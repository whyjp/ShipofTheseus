"""sprint_loop_cap.py — Sprint loop 4-layer 종료 조건 CLI (sprint-41 PR-D v0.9.46).

본 스크립트는 phase 10 sprint loop 의 *종료 조건* 을 검사한다 — *단순 iteration count cap*
아닌 *4 layer 모두 ≥ threshold* 일 때만 stop. 어떤 layer 라도 미달 시 exit 1
(continue 의무).

4 layer:
    Auto       — evaluation_report.json:automated_checks.pass_rate ≥ 0.999
    Internal   — quality/09-quality-gate.md 9 정적 + N derived + R RTG 모두 pass
    Tournament — plan/dacapo_threshold.json + impl/dacapo_threshold.json 모두 pass
    External   — (있을 경우) results/zero_context_review.md total/100 ≥ 0.95

HARD-RULE 9.ss (sprint-41 신규).

사용:
    python sprint_loop_cap.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --current-iteration 1 \\
        --max-iterations 10 \\
        --output sprints/01/sprint_loop_cap.json

보고 모드(설계 B2 §2.3, default) — exit 0. 도달 불가 임계(≥0.999) layer 게이트를
해제한다. layer 별 score/verdict 는 여전히 측정·보고되지만 CLI 가 게이팅하지 않는다.
종료 판정의 유일 권위는 manifest `stop_policy`(§2.2) — meta_audit verdict pass +
sprint.regression 무회귀 + plateau/budget cap. 점수 절대값은 어디서도 게이트가 아니다.

--gate 를 명시하면(능력 보존) 예전 4-layer 차단 동작 복원.

Exit codes:
    default(보고 모드): 항상 0 (verdict/fail_layers 는 stdout JSON 으로 보고)
    --gate 지정 시:
        0 — 모든 layer ≥ threshold OR max_iterations 도달 (stop 허용)
        1 — 적어도 1 layer 미달 + iter < max (continue — opt-in 강제)

증거 회피 사례 (0510 회차):
    quality/09-quality-gate.md 마지막 절 — *"Given 100% on evaluator, sprint cap = 1
    (re-validation only)"* 자율 결정. 그러나:
    - Auto 100% ✓
    - Tournament 0.95 ✗ (winner 57/60)
    - External 90/100 = 0.90 ✗
    Sprint cap = 1 자율 stop 은 *Auto layer only* 시각. 본 CLI = 4 layer 종합.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Windows cp949 회피 — stdout/stderr UTF-8 강제 (한글 출력)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.46"
DEFAULT_THRESHOLD = 0.999
EXTERNAL_THRESHOLD_AUTO_STOP = 0.95
EXTERNAL_THRESHOLD_FORCE_STOP = 0.99


def check_auto_layer(project_root: Path) -> dict[str, Any]:
    """evaluation_report.json:automated_checks.pass_rate ≥ 0.999."""
    candidates = [
        project_root.parent / 'results' / 'evaluation_report.json',
        project_root / 'results' / 'evaluation_report.json',
        project_root / 'evaluation_report.json',
    ]
    for path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding='utf-8'))
                pass_rate = data.get('automated_checks', {}).get('pass_rate')
                if pass_rate is None:
                    continue
                return {
                    'layer': 'auto',
                    'source': str(path),
                    'score': float(pass_rate),
                    'threshold': DEFAULT_THRESHOLD,
                    'passed': float(pass_rate) >= DEFAULT_THRESHOLD,
                }
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
    return {
        'layer': 'auto',
        'source': None,
        'score': None,
        'threshold': DEFAULT_THRESHOLD,
        'passed': None,
        'note': 'evaluation_report.json 미존재 또는 invalid',
    }


def check_internal_layer(project_root: Path) -> dict[str, Any]:
    """quality/09-quality-gate.md frontmatter 또는 본문 grep — 모든 정적/derived/RTG pass."""
    qg = project_root / 'quality' / '09-quality-gate.md'
    if not qg.exists():
        return {
            'layer': 'internal',
            'source': None,
            'score': None,
            'passed': None,
            'note': 'quality/09-quality-gate.md 미존재',
        }
    text = qg.read_text(encoding='utf-8', errors='ignore')

    # 본문 안의 PASS / FAIL 카운트 — `**PASS` 또는 `**FAIL` 또는 `:white_check_mark:` / `❌`
    pass_count = len(re.findall(r'\bPASS\b|✅|:white_check_mark:|✓\s', text))
    fail_count = len(re.findall(r'\bFAIL\b|❌|:x:', text))

    # 종합 verdict 행 — `proceed` | `remediate-then-proceed` | `halt`
    verdict = 'unknown'
    for v in ['proceed', 'remediate-then-proceed', 'halt']:
        if re.search(rf'\b{re.escape(v)}\b', text, re.IGNORECASE):
            verdict = v
            break

    # internal layer pass 조건: verdict == 'proceed' AND fail_count == 0
    passed = (verdict == 'proceed') and (fail_count == 0)

    score = 1.0 if passed else (pass_count / max(pass_count + fail_count, 1))

    return {
        'layer': 'internal',
        'source': str(qg),
        'score': round(score, 4),
        'pass_count': pass_count,
        'fail_count': fail_count,
        'verdict_text': verdict,
        'threshold': DEFAULT_THRESHOLD,
        'passed': passed,
    }


def check_tournament_layer(project_root: Path) -> dict[str, Any]:
    """plan/dacapo_threshold.json + impl/dacapo_threshold.json 모두 verdict pass."""
    paths = [
        project_root / 'plan' / 'dacapo_threshold.json',
        project_root / 'impl' / 'dacapo_threshold.json',
    ]
    statuses = []
    min_ratio = 1.0
    all_present = True
    for path in paths:
        if not path.exists():
            statuses.append({'path': str(path), 'exists': False})
            all_present = False
            continue
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            statuses.append({
                'path': str(path),
                'exists': True,
                'verdict': data.get('verdict'),
                'ratio': data.get('ratio'),
            })
            if data.get('ratio') is not None:
                min_ratio = min(min_ratio, float(data['ratio']))
        except json.JSONDecodeError:
            statuses.append({'path': str(path), 'exists': True, 'invalid': True})
            all_present = False

    if not all_present:
        return {
            'layer': 'tournament',
            'sources': statuses,
            'score': None,
            'passed': False,
            'note': 'plan/impl dacapo_threshold.json 미존재 또는 invalid (sprint-41 PR-B 산출물)',
        }

    all_pass = all(s.get('verdict') == 'pass' for s in statuses)
    return {
        'layer': 'tournament',
        'sources': statuses,
        'score': round(min_ratio, 4),
        'threshold': DEFAULT_THRESHOLD,
        'passed': all_pass,
    }


def check_external_layer(project_root: Path) -> dict[str, Any]:
    """results/zero_context_review.md 또는 zero_context_review.json 의 total/100."""
    candidates = [
        project_root.parent / 'results' / 'zero_context_review.md',
        project_root / 'results' / 'zero_context_review.md',
    ]
    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding='utf-8', errors='ignore')
        # `**Total** | **N** |` 또는 `Total\s*\|\s*\d+\s*\|\s*N` 또는 `N/100` 단순 패턴
        m = re.search(r'\*\*Total\*\*\s*\|\s*\*?\*?(\d+)\*?\*?\s*\|\s*\*?\*?(\d+)', text)
        if m:
            total_max = int(m.group(1))
            score = int(m.group(2))
        else:
            m = re.search(r'(\d+)\s*/\s*100\b', text)
            if m:
                score = int(m.group(1))
                total_max = 100
            else:
                continue
        ratio = score / max(total_max, 1)
        return {
            'layer': 'external',
            'source': str(path),
            'score': round(ratio, 4),
            'auto_stop_threshold': EXTERNAL_THRESHOLD_AUTO_STOP,
            'force_stop_threshold': EXTERNAL_THRESHOLD_FORCE_STOP,
            'passed': ratio >= EXTERNAL_THRESHOLD_AUTO_STOP,  # auto stop 허용 임계
            'force_stop': ratio >= EXTERNAL_THRESHOLD_FORCE_STOP,
        }
    return {
        'layer': 'external',
        'source': None,
        'score': None,
        'passed': None,
        'note': 'zero_context_review.md 미존재 (외부 평가 전 — auto/internal/tournament 만 검사)',
    }


def evaluate(
    project_root: Path,
    current_iteration: int,
    max_iterations: int,
) -> dict[str, Any]:
    auto = check_auto_layer(project_root)
    internal = check_internal_layer(project_root)
    tournament = check_tournament_layer(project_root)
    external = check_external_layer(project_root)

    layers = {
        'auto': auto,
        'internal': internal,
        'tournament': tournament,
        'external': external,
    }

    # external is None (외부 평가 전) → 3 layer 만 종합
    # external 있으면 4 layer
    required_layers = ['auto', 'internal', 'tournament']
    if external.get('passed') is not None:
        required_layers.append('external')

    fail_layers = [
        name for name in required_layers
        if layers[name].get('passed') is False
    ]

    pending_layers = [
        name for name in required_layers
        if layers[name].get('passed') is None
    ]

    all_pass = not fail_layers and not pending_layers
    iter_exhausted = current_iteration >= max_iterations

    if all_pass:
        verdict = 'stop'
        reason = f"all {len(required_layers)} layer ≥ threshold"
    elif iter_exhausted:
        verdict = 'stop'
        reason = (
            f"max_iterations ({max_iterations}) 도달 — fail layer "
            f"{fail_layers} pending {pending_layers} 정직 기록 후 진행"
        )
    else:
        verdict = 'continue'
        reason = (
            f"fail layer {fail_layers} pending {pending_layers} — iteration {current_iteration} → {current_iteration+1}"
        )

    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'iteration': current_iteration,
        'max_iterations': max_iterations,
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'layers': layers,
        'fail_layers': fail_layers,
        'pending_layers': pending_layers,
        'verdict': verdict,
        'reason': reason,
        'sprint_loop_terminated_by_max_iter': iter_exhausted and not all_pass,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='sprint_loop_cap',
        description=(
            'Sprint loop 4-layer 종료 조건 CLI — auto+internal+tournament+external '
            '모두 ≥ threshold 일 때만 stop. HARD-RULE 9.ss (sprint-41).'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--current-iteration', type=int, default=1)
    parser.add_argument('--max-iterations', type=int, default=10)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument(
        '--gate',
        action='store_true',
        help=(
            '예전 4-layer 차단 동작 복원(능력 보존, opt-in) — verdict continue 시 exit 1. '
            '기본은 보고 모드(비게이팅, 설계 B2 §2.3).'
        ),
    )

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(ns.project_root, ns.current_iteration, ns.max_iterations)

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'continue':
        print(
            f"\n[sprint_loop_cap] verdict=continue(보고): {verdict_obj['reason']}",
            file=sys.stderr,
        )
        if ns.gate:
            print(
                f"[sprint_loop_cap] --gate opt-in — sprint iteration "
                f"{ns.current_iteration} → {ns.current_iteration+1}.",
                file=sys.stderr,
            )

    # 보고 모드(default) — 점수 절대값은 게이트가 아니다. --gate opt-in 시에만 차단.
    if ns.gate:
        return 0 if verdict_obj['verdict'] == 'stop' else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
