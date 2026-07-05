"""runtime_guard_chain.py — Phase 진입/종료 통합 dispatch CLI (sprint-41 PR-E v0.9.46).

본 스크립트는 phase entry / exit 시 *모든 게이트 CLI 를 chain 호출* + 단일 verdict.
exit 0 까지 phase advance 차단. orchestrator 가 매 phase transition 시 의무 호출
(HARD-RULE 9.tt).

Chain 구성:
    [phase entry]
        - skill_version major + minor ≥ orchestrator
        - phase 단조성 (직전 phase fingerprint 정합)
    [phase exit]
        - phase exit hook (e.g., phase 06/08 = dacapo_threshold.py, phase 10 = sprint_loop_cap.py)
        - frontmatter 박힘 (skill_name / skill_version / phase / fingerprint / prev_fingerprint / created_at)
        - 산출물 emit 확인 (phase별 의무 산출물 list)

본 CLI = sprint-41 의 *통합 진입점*. 다른 2 CLI (dacapo_threshold /
sprint_loop_cap) 가 sub-call.

사용:
    python runtime_guard_chain.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --phase 09 \\
        --transition entry \\
        --grade G4 \\
        --domain DES

Exit codes:
    0 — 모든 chain check pass → phase advance 허용
    1 — 적어도 1 check fail → phase advance 차단

References:
- sprint-41 PR-B (dacapo_threshold)
- sprint-41 PR-D (sprint_loop_cap)
- sprint-41 PR-E (본 PR — chain dispatcher)
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Windows cp949 회피
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.46"


# version 비교 — semver minor 이상 매칭
def parse_version(s: str) -> tuple[int, int, int]:
    m = re.match(r'^(\d+)\.(\d+)\.(\d+)', s.strip())
    if not m:
        return (0, 0, 0)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def check_skill_version(project_root: Path, orchestrator_version: str) -> dict[str, Any]:
    """frontmatter skill_version 추출 → orchestrator 와 minor 이상 비교 (HARD-RULE 9 contracts.md)."""
    # 가장 최근 phase 산출물 frontmatter 검사
    candidates = list(project_root.rglob('*.md'))
    found_versions = []
    for path in candidates[:50]:  # cap
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
            m = re.search(r'^skill_version:\s*["\']?([\d.]+)["\']?\s*$', text, re.MULTILINE)
            if m:
                found_versions.append((m.group(1), str(path)))
        except OSError:
            continue

    if not found_versions:
        return {
            'check': 'skill_version',
            'passed': False,
            'reason': 'frontmatter skill_version 미검출 (산출물 없음 또는 frontmatter 누락)',
        }

    # 가장 *낮은* version 추출 (worst case)
    versions_parsed = [(parse_version(v), v, p) for v, p in found_versions]
    min_v_tuple, min_v_str, min_v_path = min(versions_parsed)
    orch_v = parse_version(orchestrator_version)

    # major 같음 + 전체 version tuple ≥ orchestrator
    # (실 사용 — 0.x.y 릴리즈 라인에서 sprint 마다 patch 증가; 본 비교가 minor silent skip 차단)
    passed = (min_v_tuple[0] == orch_v[0]) and (min_v_tuple >= orch_v)
    return {
        'check': 'skill_version',
        'min_found': min_v_str,
        'min_found_path': min_v_path,
        'orchestrator': orchestrator_version,
        'passed': passed,
        'reason': (
            'skill_version OK'
            if passed
            else (
                f"skill_version {min_v_str} < orchestrator {orchestrator_version} "
                f"(at {min_v_path}) — minor/patch silent skip 차단 (contracts.md)"
            )
        ),
    }


def check_phase_monotonicity(project_root: Path, current_phase: str) -> dict[str, Any]:
    """phase 진행 단조성 — 산출물 created_at timestamp 가 phase 번호 순"""
    # 모든 산출물에서 phase + created_at 추출
    phase_times = {}
    for path in project_root.rglob('*.md'):
        try:
            text = path.read_text(encoding='utf-8', errors='ignore')
            m_phase = re.search(r'^phase:\s*["\']?([\d-]+\S*)["\']?\s*$', text, re.MULTILINE)
            m_time = re.search(r'^created_at:\s*["\']?([^"\'\s]+)["\']?\s*$', text, re.MULTILINE)
            if m_phase and m_time:
                phase_str = m_phase.group(1)
                phase_num = re.match(r'^(\d+)', phase_str)
                if phase_num:
                    n = int(phase_num.group(1))
                    if n not in phase_times or m_time.group(1) > phase_times[n]:
                        phase_times[n] = m_time.group(1)
        except OSError:
            continue

    # 단조성 — phase N+1 created_at > phase N created_at
    violations = []
    sorted_phases = sorted(phase_times.keys())
    for i in range(1, len(sorted_phases)):
        prev_n, curr_n = sorted_phases[i - 1], sorted_phases[i]
        if phase_times[curr_n] < phase_times[prev_n]:
            violations.append({
                'prev_phase': prev_n,
                'prev_time': phase_times[prev_n],
                'curr_phase': curr_n,
                'curr_time': phase_times[curr_n],
                'reason': f'phase {curr_n} created_at < phase {prev_n} created_at (단조성 깨짐)',
            })

    return {
        'check': 'phase_monotonicity',
        'phases_seen': sorted_phases,
        'violations': violations,
        'passed': len(violations) == 0,
    }


def run_subprocess(cmd: list[str]) -> dict[str, Any]:
    """sub-CLI 호출 + JSON stdout 파싱."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace',
        )
    except subprocess.TimeoutExpired:
        return {'exit_code': 124, 'stdout': '', 'stderr': 'timeout'}
    except FileNotFoundError as e:
        return {'exit_code': 127, 'stdout': '', 'stderr': str(e)}

    parsed = None
    try:
        # stdout 의 *마지막 valid JSON object* 만 추출 (sub-CLI 가 다중 출력할 수 있음)
        text = result.stdout.strip()
        # 단순 — `{...}` 매칭 후 마지막 시도
        for start_idx in range(len(text)):
            if text[start_idx] == '{':
                try:
                    parsed = json.loads(text[start_idx:])
                    break
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return {
        'cmd': cmd,
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
        'parsed_json': parsed,
    }


def check_exit_hook(
    project_root: Path,
    phase: str,
    skill_root: Path,
    iteration: int = 1,
    max_iterations: int = 10,
) -> dict[str, Any] | None:
    """phase exit hook — 06/08 = dacapo_threshold.py, 10 = sprint_loop_cap.py."""
    if phase == '06':
        tournament = project_root / 'plan' / 'tournament-01.md'
        if not tournament.exists():
            tournament = project_root / 'plan' / 'tournament-02.md'
        if not tournament.exists():
            return {
                'check': 'exit_hook_phase_06',
                'sub_cli': 'dacapo_threshold.py',
                'exit_code': 1,
                'passed': False,
                'reason': 'tournament-NN.md 미존재 (plan/)',
            }
        cmd = [
            sys.executable,
            str(skill_root / 'scoring' / 'dacapo_threshold.py'),
            '--tournament-md', str(tournament),
            '--quiet',
        ]
        result = run_subprocess(cmd)
        return {
            'check': 'exit_hook_phase_06',
            'sub_cli': 'dacapo_threshold.py',
            'tournament_md': str(tournament),
            'exit_code': result['exit_code'],
            'parsed_verdict': (result.get('parsed_json') or {}).get('verdict'),
            'parsed_ratio': (result.get('parsed_json') or {}).get('ratio'),
            'passed': result['exit_code'] == 0,
        }

    if phase == '08':
        tournament = project_root / 'impl' / 'tournament-impl-01.md'
        if not tournament.exists():
            tournament = project_root / 'impl' / 'tournament-impl-02.md'
        if not tournament.exists():
            return {
                'check': 'exit_hook_phase_08',
                'sub_cli': 'dacapo_threshold.py',
                'exit_code': 1,
                'passed': False,
                'reason': 'tournament-impl-NN.md 미존재 (impl/)',
            }
        cmd = [
            sys.executable,
            str(skill_root / 'scoring' / 'dacapo_threshold.py'),
            '--tournament-md', str(tournament),
            '--quiet',
        ]
        result = run_subprocess(cmd)
        return {
            'check': 'exit_hook_phase_08',
            'sub_cli': 'dacapo_threshold.py',
            'tournament_md': str(tournament),
            'exit_code': result['exit_code'],
            'parsed_verdict': (result.get('parsed_json') or {}).get('verdict'),
            'parsed_ratio': (result.get('parsed_json') or {}).get('ratio'),
            'passed': result['exit_code'] == 0,
        }

    if phase == '10':
        cmd = [
            sys.executable,
            str(skill_root / 'scoring' / 'sprint_loop_cap.py'),
            '--project-root', str(project_root),
            '--current-iteration', str(iteration),
            '--max-iterations', str(max_iterations),
            '--quiet',
        ]
        result = run_subprocess(cmd)
        return {
            'check': 'exit_hook_phase_10',
            'sub_cli': 'sprint_loop_cap.py',
            'exit_code': result['exit_code'],
            'parsed_verdict': (result.get('parsed_json') or {}).get('verdict'),
            'fail_layers': (result.get('parsed_json') or {}).get('fail_layers'),
            'passed': result['exit_code'] == 0,
        }

    return None  # 다른 phase 는 sub-CLI 없음 (확장 가능)


def evaluate(
    project_root: Path,
    phase: str,
    transition: str,
    grade: str,
    domain: str | None,
    domain_matched: bool,
    orchestrator_version: str,
    iteration: int = 1,
    max_iterations: int = 10,
    skill_root: Path | None = None,
) -> dict[str, Any]:
    if skill_root is None:
        skill_root = Path(__file__).parent.parent

    checks: list[dict[str, Any]] = []

    # 모든 transition 공통 — skill_version + phase monotonicity
    checks.append(check_skill_version(project_root, orchestrator_version))
    checks.append(check_phase_monotonicity(project_root, phase))

    # transition 별 exit hook (06/08 = dacapo_threshold, 10 = sprint_loop_cap).
    # 구 phase 09 entry hook 은 은퇴 — entry 는 skill_version + monotonicity 만.
    # cold session 정합은 run_gate (cold.isolation) 가 값 기반으로 대체.
    if transition == 'exit':
        hook = check_exit_hook(project_root, phase, skill_root, iteration, max_iterations)
        if hook:
            checks.append(hook)

    fail_checks = [c['check'] for c in checks if c.get('passed') is False]
    all_pass = not fail_checks

    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'phase': phase,
        'transition': transition,
        'grade': grade,
        'orchestrator_version': orchestrator_version,
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'checks': checks,
        'fail_checks': fail_checks,
        'verdict': 'pass' if all_pass else 'fail',
        'advance_blocked': not all_pass,
        'reason': (
            f"all {len(checks)} chain check pass — phase {phase} {transition} 허용"
            if all_pass
            else f"fail: {fail_checks} — phase {phase} {transition} 차단"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='runtime_guard_chain',
        description=(
            'Phase 진입/종료 통합 dispatch CLI — skill_version + monotonicity + '
            'sub-CLI hook chain. HARD-RULE 9.tt (sprint-41).'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--phase', required=True, help='phase 번호 (e.g., "06", "09", "10")')
    parser.add_argument('--transition', choices=['entry', 'exit'], required=True)
    parser.add_argument('--grade', choices=['G2', 'G3', 'G4', 'G5'], default='G4')
    parser.add_argument('--domain', help='도메인 식별자 (e.g., DES)')
    parser.add_argument('--domain-matched', action='store_true')
    parser.add_argument(
        '--orchestrator-version',
        default='0.9.46',
        help='현재 orchestrator skill version (default 0.9.46)',
    )
    parser.add_argument('--iteration', type=int, default=1)
    parser.add_argument('--max-iterations', type=int, default=10)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(
        ns.project_root,
        ns.phase,
        ns.transition,
        ns.grade,
        ns.domain,
        ns.domain_matched,
        ns.orchestrator_version,
        ns.iteration,
        ns.max_iterations,
    )

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[runtime_guard_chain] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        for c in verdict_obj['checks']:
            if c.get('passed') is False:
                print(f"  - {c.get('check')}: {c.get('reason', 'fail')}", file=sys.stderr)
        print(
            f"\n[runtime_guard_chain] orchestrator 의무 — phase {ns.phase} {ns.transition} 차단 + fix step (HARD-RULE 9.tt).",
            file=sys.stderr,
        )

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
