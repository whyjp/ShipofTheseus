"""stagnation_breakthrough.py — Stagnation 후 자율 종료 차단 CLI (sprint-42 PR-D v0.9.47).

본 스크립트는 sprints/N/report.json 의 `stagnation_detected: true` + `score < 0.999` 시
*exit_sprint_loop 자율 결정 차단*. 다음 4 시도 evidence ≥ 1 의무:
    ① 새 universe (multiverse-width-default-bump 정합)
    ② lateral think (ouroboros:unstuck 정합)
    ③ ensemble synthesis (ensemble-synthesis-default 정합)
    ④ phase 회귀 (phase 06 plan 다른 universe 시도)

orchestrator 가 phase 10 sprint iteration 종료 시 의무 호출 (HARD-RULE 9.ww).

증거 회피 사례 (0510-2 회차):
    `sprints/03/report.json` =
        score: 0.97
        stagnation_detected: true
        decision: exit_sprint_loop_per_DEC-autonomy
    lateral / 새 universe / ensemble / phase 회귀 시도 0 — 본 CLI 가 차단.

사용:
    python stagnation_breakthrough.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --current-iteration 3 \\
        --output sprints/03/gate_stagnation_breakthrough.json

보고 모드(설계 B2 §2.2-4, default) — exit 0. plateau(정직한 수렴)를 절대 점수 미달로
벌하고 breakthrough 를 강제하던 게이트를 해제한다. verdict('pass'/'fail')는 여전히
측정·보고되지만 CLI 가 게이팅하지 않는다. breakthrough 는 budget 여유 + 사용자 opt-in
시에만 옵션이며, 종료 판정 권위는 manifest `stop_policy`(§2.2)다.

--gate 를 명시하면(능력 보존) 예전 차단 동작 복원 — verdict fail 시 exit 1.

Exit codes:
    default(보고 모드): 항상 0 (verdict 는 stdout JSON 으로 보고)
    --gate 지정 시:
        0 — stagnation 미감지 OR 4 시도 evidence ≥ 1
        1 — stagnation + 0 시도 evidence (자율 종료 차단 — opt-in 강제)
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


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.47"
DEFAULT_THRESHOLD = 0.999


# 4 breakthrough 시도 evidence 패턴
BREAKTHROUGH_PATTERNS = {
    'new_universe': [
        re.compile(r'\bnew\s+universe[s]?\b', re.IGNORECASE),
        re.compile(r'\buniverse[-_\s]*([4-9]|[1-9]\d+)\b', re.IGNORECASE),  # universe-4+
        re.compile(r'\bspawn(?:ed|ing)\s+universe[s]?\b', re.IGNORECASE),
        re.compile(r'\bmultiverse[-_]width[-_]bump\b', re.IGNORECASE),
    ],
    'lateral_think': [
        re.compile(r'\blateral\s+think(?:ing)?\b', re.IGNORECASE),
        re.compile(r'\balternative\s+hypothesis\b', re.IGNORECASE),
        re.compile(r'\bouroboros[:\.\s]+unstuck\b', re.IGNORECASE),
        re.compile(r'\breframe(?:d|ing)?\s+the\s+problem\b', re.IGNORECASE),
    ],
    'ensemble_synthesis': [
        re.compile(r'\bensemble\s+synthesis\b', re.IGNORECASE),
        re.compile(r'\bsynth(?:esis|esize|esized)\s+(?:from|of)\s+universes?\b', re.IGNORECASE),
        re.compile(r'\bensemble[-_]synthesis[-_]default\b', re.IGNORECASE),
        re.compile(r'\bcombine(?:d)?\s+universe[-_\s]\d+', re.IGNORECASE),
    ],
    'phase_regression': [
        re.compile(r'\bphase\s+(?:06|08)\s+(?:re|regression|retry)\b', re.IGNORECASE),
        re.compile(r'\brewind(?:ed|ing)?\s+to\s+phase\s+\d+\b', re.IGNORECASE),
        re.compile(r'\b(?:plan|impl)\s+(?:retry|redo|regression)\b', re.IGNORECASE),
        re.compile(r'\bbranch\s+to\s+different\s+universe\b', re.IGNORECASE),
    ],
}


def find_sprint_report(project_root: Path, iteration: int) -> Path | None:
    """sprints/<iteration>/report.json or report.md 찾기."""
    candidates = [
        project_root / 'sprints' / str(iteration).zfill(2) / 'report.json',
        project_root / 'sprints' / str(iteration) / 'report.json',
        project_root / 'sprints' / str(iteration).zfill(2) / 'report.md',
        project_root / 'sprints' / str(iteration) / 'report.md',
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def parse_sprint_report(path: Path) -> dict[str, Any]:
    """sprint report 의 stagnation_detected + score 추출."""
    text = path.read_text(encoding='utf-8', errors='ignore')
    if path.suffix == '.json':
        try:
            data = json.loads(text)
            return {
                'stagnation_detected': bool(data.get('stagnation_detected', False)),
                'score': float(data['score']) if 'score' in data else None,
                'decision': data.get('decision'),
                'lessons_outbound': data.get('lessons_outbound', []),
                'parse_source': 'json',
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    # markdown / fallback grep
    stag = bool(re.search(r'stagnation_detected\s*[:=]\s*(?:true|yes|✓)', text, re.IGNORECASE))
    score_m = re.search(r'(?:score|trinity[-_\s]*score)\s*[:=]\s*(0?\.\d+|\d+\.\d+)', text, re.IGNORECASE)
    return {
        'stagnation_detected': stag,
        'score': float(score_m.group(1)) if score_m else None,
        'decision': None,
        'lessons_outbound': [],
        'parse_source': 'grep',
    }


def detect_breakthrough_attempts(project_root: Path, iteration: int) -> dict[str, Any]:
    """sprints/iteration 안 + plan/impl 산출물 본문에서 4 breakthrough 시도 evidence grep."""
    # 본 sprint iteration 의 report + inputs + 직전 sprint dir 의 산출물 모두 검사
    search_paths: list[Path] = []
    sprints_dir = project_root / 'sprints'
    if sprints_dir.exists():
        for sub in sprints_dir.iterdir():
            if sub.is_dir():
                search_paths.extend(sub.glob('*'))
    # plan / impl 의 dacapo + tournament 도 검사 (fresh universe 등 evidence)
    for sub in (project_root / 'plan', project_root / 'impl'):
        if sub.exists():
            search_paths.extend(sub.glob('*.md'))
            search_paths.extend(sub.glob('*.json'))

    combined = '\n'.join(
        p.read_text(encoding='utf-8', errors='ignore')
        for p in search_paths
        if p.is_file()
    )

    found: dict[str, list[str]] = {}
    for kind, patterns in BREAKTHROUGH_PATTERNS.items():
        matches = []
        for pat in patterns:
            for m in pat.finditer(combined):
                matches.append(m.group(0))
        if matches:
            found[kind] = matches

    return {
        'attempts_found': found,
        'attempt_kinds_present': list(found.keys()),
        'attempt_count': len(found),
    }


def evaluate(
    project_root: Path,
    current_iteration: int,
    threshold: float = DEFAULT_THRESHOLD,
) -> dict[str, Any]:
    report_path = find_sprint_report(project_root, current_iteration)
    if not report_path:
        return {
            'schema_version': SCHEMA_VERSION,
            'project_root': str(project_root),
            'iteration': current_iteration,
            'sprint_report': None,
            'verdict': 'pass',
            'reason': f'sprints/{current_iteration} report 미존재 — skip (sprint loop 미시작 또는 다른 iteration)',
        }

    parsed = parse_sprint_report(report_path)
    stagnation = parsed['stagnation_detected']
    score = parsed['score']

    # stagnation 미감지 OR score ≥ threshold → pass
    if not stagnation:
        return {
            'schema_version': SCHEMA_VERSION,
            'project_root': str(project_root),
            'iteration': current_iteration,
            'sprint_report': str(report_path),
            'parsed': parsed,
            'threshold': threshold,
            'verdict': 'pass',
            'reason': 'stagnation 미감지',
        }

    if score is not None and score >= threshold:
        return {
            'schema_version': SCHEMA_VERSION,
            'project_root': str(project_root),
            'iteration': current_iteration,
            'sprint_report': str(report_path),
            'parsed': parsed,
            'threshold': threshold,
            'verdict': 'pass',
            'reason': f"score {score:.4f} ≥ threshold {threshold} (stagnation 무관 stop OK)",
        }

    # stagnation + score < threshold → 4 시도 evidence 검사
    attempts = detect_breakthrough_attempts(project_root, current_iteration)

    has_attempt = attempts['attempt_count'] >= 1
    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'iteration': current_iteration,
        'sprint_report': str(report_path),
        'parsed': parsed,
        'threshold': threshold,
        'breakthrough_attempts': attempts,
        'verdict': 'pass' if has_attempt else 'fail',
        'reason': (
            f"stagnation + score {score} < {threshold} 인데 breakthrough 시도 ≥ 1 발견 ({attempts['attempt_kinds_present']})"
            if has_attempt
            else (
                f"stagnation_detected=true + score {score} < {threshold} + breakthrough 시도 0 — "
                f"exit_sprint_loop 자율 결정 차단. 4 시도 (new_universe / lateral_think / "
                f"ensemble_synthesis / phase_regression) 중 ≥ 1 evidence 의무."
            )
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='stagnation_breakthrough',
        description=(
            'Stagnation 후 자율 종료 차단 CLI — exit_loop 차단 + 4 breakthrough 시도 evidence. '
            'HARD-RULE 9.ww (sprint-42).'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--current-iteration', type=int, required=True)
    parser.add_argument('--threshold', type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument(
        '--gate',
        action='store_true',
        help=(
            '예전 차단 동작 복원(능력 보존, opt-in) — verdict fail 시 exit 1. '
            '기본은 보고 모드(비게이팅, 설계 B2 §2.2-4).'
        ),
    )

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(ns.project_root, ns.current_iteration, ns.threshold)

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[stagnation_breakthrough] verdict=fail(보고): {verdict_obj['reason']}",
            file=sys.stderr,
        )
        if ns.gate:
            print(
                "[stagnation_breakthrough] --gate opt-in — exit_loop 차단 + 4 시도 ≥ 1.",
                file=sys.stderr,
            )

    # 보고 모드(default) — 점수 절대값은 게이트가 아니다. --gate opt-in 시에만 차단.
    if ns.gate:
        return 0 if verdict_obj['verdict'] == 'pass' else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
