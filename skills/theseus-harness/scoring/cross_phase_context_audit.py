"""cross_phase_context_audit.py — Cross-phase 컨텍스트 전달 audit CLI (sprint-42 PR-B v0.9.47).

본 스크립트는 phase N 산출물 본문에 *직전 phase + 1단계 이상 과거 phase* 인용 ≥ 2 (총합)
의무 검증. 부재 시 exit 1. orchestrator 가 phase exit 시 의무 호출 (HARD-RULE 9.uu).

증거 회피 사례 (0510-2 회차):
    `tournament-impl-01.md` 본문 = 7-condition 체크리스트만 박힘. phase 02 cold-reread /
    phase 04 답안 / phase 05 critique 인용 0. `prev_fingerprint` chain 1 단계만.

사용:
    python cross_phase_context_audit.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --phase 09 \\
        --min-immediate 1 \\
        --min-distant 1

Exit codes:
    0 — phase N 본문에 직전 phase + 과거 phase 인용 ≥ 1 each
    1 — 미달 (결손 phase list)
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


# Phase N 산출물 위치 매핑 — 본문 인용 검사 시 phase 추출
PHASE_DIRS = {
    '00': ('naming', 'naming/'),
    '01': ('intent', 'intent/01-'),
    '02': ('intent', 'intent/02-'),
    '03': ('intent', 'intent/03-'),
    '04': ('intent', 'intent/04-'),
    '05': ('intent', 'intent/05-'),
    '06': ('plan', 'plan/'),
    '07': ('plan', 'plan/07-'),
    '08': ('impl', 'impl/'),
    '09': ('quality', 'quality/'),
    '10': ('sprints', 'sprints/'),
    '11': ('sprints', 'sprints/.*/bisect'),
    '12': ('webview', 'webview/'),
    '13': ('interactive-viewer', 'interactive-viewer/'),
    '14': ('handoff', 'handoff/'),
}


# Cross-phase 인용 keyword 카탈로그 — 본문에 다음 패턴 등장 시 phase 인용으로 카운트
PHASE_REFERENCE_PATTERNS = {
    # decision IDs — phase 04/05 답안 인용 신호
    'Q-D': re.compile(r'\bQ-D\d+(?:\.\d+)?\b'),
    'DEC-': re.compile(r'\bDEC-\d+\b'),
    # phase 명칭 직접 인용
    'phase_label': re.compile(r'\bphase\s*(\d{1,2})\b', re.IGNORECASE),
    # 산출물 path 인용
    'intent_path': re.compile(r'(?:intent/0[1-5][^.\s]*\.md)|(?:`?intent/\d{2}-[^`\s]+`?)'),
    'plan_path': re.compile(r'(?:plan/(?:06-plan|07-plan-review|tournament-\d+|dacapo-rerun-\d+|candidates/universe-\d+)[^\s]*)'),
    'impl_path': re.compile(r'(?:impl/(?:08-impl-log|tournament-impl-\d+|dacapo-rerun-impl-\d+|candidates/universe-\d+)[^\s]*)'),
    'quality_path': re.compile(r'(?:quality/(?:09-quality-gate|gate_[a-z_]+)[^\s]*)'),
    'sprint_path': re.compile(r'(?:sprints/\d+/(?:report|inputs|bisect)[^\s]*)'),
}


def _phase_num(s: str) -> int | None:
    m = re.match(r'^0*(\d{1,2})', s)
    return int(m.group(1)) if m else None


def find_phase_artefacts(project_root: Path, phase: str) -> list[Path]:
    """phase N 의 산출물 파일 list 반환."""
    n = _phase_num(phase)
    if n is None:
        return []

    candidates: list[Path] = []
    if 1 <= n <= 5:
        candidates.extend((project_root / 'intent').glob(f'{phase.zfill(2)}-*.md'))
        candidates.extend((project_root / 'intent').glob(f'{phase.zfill(2)}-*.v2.md'))
    elif n == 6:
        candidates.extend((project_root / 'plan').glob('06-*.md'))
        candidates.extend((project_root / 'plan').glob('tournament-*.md'))
        candidates.extend((project_root / 'plan').glob('dacapo-rerun-*.md'))
    elif n == 7:
        candidates.extend((project_root / 'plan').glob('07-*.md'))
    elif n == 8:
        candidates.extend((project_root / 'impl').glob('08-*.md'))
        candidates.extend((project_root / 'impl').glob('tournament-impl-*.md'))
        candidates.extend((project_root / 'impl').glob('dacapo-rerun-impl-*.md'))
    elif n == 9:
        candidates.extend((project_root / 'quality').glob('09-*.md'))
    elif n == 10:
        # sprint reports
        sprints = project_root / 'sprints'
        if sprints.exists():
            for sub in sprints.iterdir():
                if sub.is_dir():
                    candidates.extend(sub.glob('report.*'))
                    candidates.extend(sub.glob('inputs.*'))
    elif n == 11:
        sprints = project_root / 'sprints'
        if sprints.exists():
            for sub in sprints.iterdir():
                if sub.is_dir():
                    candidates.extend(sub.glob('bisect.*'))
    elif n == 12:
        candidates.extend((project_root / 'webview').glob('*.md'))
    elif n == 13:
        candidates.extend((project_root / 'interactive-viewer').glob('*.md'))
    elif n == 14:
        candidates.extend((project_root / 'handoff').glob('14-*.md'))
    return [p for p in candidates if p.is_file()]


def count_references(text: str, target_phase_num: int) -> dict[str, int]:
    """본문에서 target phase 인용 카운트."""
    counts: dict[str, int] = {}
    # phase_label
    for m in PHASE_REFERENCE_PATTERNS['phase_label'].finditer(text):
        try:
            n = int(m.group(1))
            if n == target_phase_num:
                counts['phase_label'] = counts.get('phase_label', 0) + 1
        except ValueError:
            pass
    # path 인용 (phase 별 path pattern)
    if target_phase_num <= 5:
        path_pattern = PHASE_REFERENCE_PATTERNS['intent_path']
        prefix = f'intent/{target_phase_num:02d}-'
        for m in path_pattern.finditer(text):
            if prefix in m.group(0):
                counts['intent_path'] = counts.get('intent_path', 0) + 1
    elif target_phase_num == 6:
        for m in PHASE_REFERENCE_PATTERNS['plan_path'].finditer(text):
            if any(k in m.group(0) for k in ['06-plan', 'tournament', 'dacapo-rerun', 'candidates/universe']):
                counts['plan_path'] = counts.get('plan_path', 0) + 1
    elif target_phase_num == 7:
        for m in PHASE_REFERENCE_PATTERNS['plan_path'].finditer(text):
            if '07-plan-review' in m.group(0):
                counts['plan_path'] = counts.get('plan_path', 0) + 1
    elif target_phase_num == 8:
        for m in PHASE_REFERENCE_PATTERNS['impl_path'].finditer(text):
            counts['impl_path'] = counts.get('impl_path', 0) + 1
    elif target_phase_num == 9:
        for m in PHASE_REFERENCE_PATTERNS['quality_path'].finditer(text):
            counts['quality_path'] = counts.get('quality_path', 0) + 1
    elif target_phase_num == 10:
        for m in PHASE_REFERENCE_PATTERNS['sprint_path'].finditer(text):
            if '/report' in m.group(0) or '/inputs' in m.group(0):
                counts['sprint_path'] = counts.get('sprint_path', 0) + 1

    # decision IDs (phase 04/05 인용 강 신호)
    if target_phase_num in (4, 5):
        for m in PHASE_REFERENCE_PATTERNS['Q-D'].finditer(text):
            counts['Q-D'] = counts.get('Q-D', 0) + 1
        for m in PHASE_REFERENCE_PATTERNS['DEC-'].finditer(text):
            counts['DEC-'] = counts.get('DEC-', 0) + 1

    return counts


def evaluate_phase(
    project_root: Path,
    phase: str,
    min_immediate: int,
    min_distant: int,
) -> dict[str, Any]:
    n = _phase_num(phase)
    if n is None:
        return {'phase': phase, 'error': 'invalid phase number'}

    artefacts = find_phase_artefacts(project_root, phase)
    if not artefacts:
        return {
            'phase': phase,
            'artefacts_found': 0,
            'verdict': 'skip',
            'reason': f'phase {phase} 산출물 없음',
        }

    # phase N 본문 모두 합쳐 인용 카운트
    combined = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in artefacts)

    immediate_phase = n - 1
    distant_phases = list(range(0, n - 1))

    immediate_counts = count_references(combined, immediate_phase) if immediate_phase >= 0 else {}
    distant_counts: dict[int, dict[str, int]] = {}
    for dp in distant_phases:
        distant_counts[dp] = count_references(combined, dp)

    immediate_total = sum(immediate_counts.values())
    distant_total = sum(sum(c.values()) for c in distant_counts.values())

    immediate_pass = immediate_total >= min_immediate
    distant_pass = distant_total >= min_distant or len(distant_phases) == 0

    return {
        'phase': phase,
        'artefacts_found': len(artefacts),
        'artefact_paths': [str(p.relative_to(project_root)) for p in artefacts],
        'immediate_phase': immediate_phase if immediate_phase >= 0 else None,
        'immediate_references': immediate_counts,
        'immediate_total': immediate_total,
        'immediate_min': min_immediate,
        'immediate_pass': immediate_pass,
        'distant_phases': distant_phases,
        'distant_references': {str(k): v for k, v in distant_counts.items()},
        'distant_total': distant_total,
        'distant_min': min_distant,
        'distant_pass': distant_pass,
        'verdict': 'pass' if (immediate_pass and distant_pass) else 'fail',
    }


def evaluate(
    project_root: Path,
    phases: list[str] | None,
    min_immediate: int,
    min_distant: int,
) -> dict[str, Any]:
    if phases is None:
        phases = ['02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14']

    per_phase = []
    fail_phases: list[str] = []
    for ph in phases:
        result = evaluate_phase(project_root, ph, min_immediate, min_distant)
        per_phase.append(result)
        if result.get('verdict') == 'fail':
            fail_phases.append(ph)

    overall_pass = not fail_phases

    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'phases_audited': phases,
        'per_phase': per_phase,
        'fail_phases': fail_phases,
        'verdict': 'pass' if overall_pass else 'fail',
        'reason': (
            f"all audited phases context 전달 OK"
            if overall_pass
            else f"{len(fail_phases)} phase 미달: {fail_phases}"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='cross_phase_context_audit',
        description=(
            'Cross-phase 컨텍스트 전달 audit — 본문에 직전 phase + 1단계 이상 과거 phase 인용 ≥ 1 each. '
            'HARD-RULE 9.uu (sprint-42).'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument(
        '--phase',
        action='append',
        help='특정 phase 만 audit (반복 지정 가능, default: 02-14 모두)',
    )
    parser.add_argument('--min-immediate', type=int, default=1)
    parser.add_argument('--min-distant', type=int, default=1)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(
        ns.project_root,
        ns.phase,
        ns.min_immediate,
        ns.min_distant,
    )

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[cross_phase_context_audit] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        for p in verdict_obj['per_phase']:
            if p.get('verdict') == 'fail':
                print(
                    f"  - phase {p['phase']}: immediate {p['immediate_total']}/{p['immediate_min']}, "
                    f"distant {p['distant_total']}/{p['distant_min']}",
                    file=sys.stderr,
                )

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
