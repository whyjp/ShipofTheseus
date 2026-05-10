"""universe_count_monotonicity.py — Universe 단조성 강제 CLI (sprint-42 PR-C v0.9.47).

본 스크립트는 다카포 round N+1 의 universe 수가 round N 보다 *작지 않음* 검증 +
impl universe 수가 plan universe 수의 합리적 비율 (단일 winner only 시 7-condition 명시)
검증. exit 1 시 round N+1 강제. orchestrator 가 phase 06/08 exit 시 의무 호출
(HARD-RULE 9.vv).

증거 회피 사례 (0510-2 회차):
    plan round 1: universe-{1,2,3} (3 universe)
    plan round 2: same 3 re-rate (NEW = 0) — dacapo-skip-sentinel 위반
    impl: 1 universe only ("Single-universe implementation") — multiverse-impl-fan-out 약화

사용:
    python universe_count_monotonicity.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --output quality/gate_universe_monotonicity.json

Exit codes:
    0 — round N+1 ≥ N AND impl universe 수 합리적
    1 — universe 감소 OR impl 단일 universe + 7-condition 미명시
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


# universe-N 디렉터리 패턴
UNIVERSE_DIR_PATTERN = re.compile(r'^universe-(\d+)$')

# tournament-NN.md 안의 universe 인용 (sub-score 표 행)
UNIVERSE_TABLE_ROW = re.compile(
    r'^\|\s*(?:\*\*)?universe-(\d+)(?:\*\*)?\s*\|',
    re.MULTILINE,
)


def list_universes_in_dir(root: Path) -> set[int]:
    """plan/candidates/ 또는 impl/candidates/ 안의 universe-N 카운트."""
    if not root.exists():
        return set()
    universes = set()
    for sub in root.iterdir():
        if sub.is_dir():
            m = UNIVERSE_DIR_PATTERN.match(sub.name)
            if m:
                universes.add(int(m.group(1)))
    return universes


def list_universes_in_tournament(md_path: Path) -> set[int]:
    """tournament-NN.md 본문 sub-score 표 행에서 universe 카운트."""
    if not md_path.exists():
        return set()
    text = md_path.read_text(encoding='utf-8', errors='ignore')
    return {int(m.group(1)) for m in UNIVERSE_TABLE_ROW.finditer(text)}


def check_seven_condition_explicit(md_path: Path) -> bool:
    """impl-multiverse-strict 7-condition 명시 여부."""
    if not md_path.exists():
        return False
    text = md_path.read_text(encoding='utf-8', errors='ignore')
    # impl-multiverse-strict 본문 의 7 condition 의 *각각이 명시* 되어야
    # 단순 "7-condition was assessed" 한 줄 ≠ 명시 — 7 행 표 또는 ≥ 5 condition keyword 매칭
    keywords = [
        '2 plan universes scored',
        'tournament re-rerun',
        'da capo step',
        'reproducibility',
        'capacity-1 edges',
        'wall-clock',
        'tests green',
    ]
    matches = sum(1 for kw in keywords if kw.lower() in text.lower())
    # 7 의무 중 ≥ 5 명시 시 통과 (단순 referencing 차단)
    return matches >= 5


def evaluate(project_root: Path) -> dict[str, Any]:
    plan_dir = project_root / 'plan'
    impl_dir = project_root / 'impl'

    # plan tournament rounds
    plan_rounds: dict[int, dict[str, Any]] = {}
    if plan_dir.exists():
        for md in plan_dir.glob('tournament-*.md'):
            m = re.match(r'^tournament-(\d+)\.md$', md.name)
            if m:
                round_n = int(m.group(1))
                universes = list_universes_in_tournament(md)
                plan_rounds[round_n] = {
                    'tournament_md': str(md.relative_to(project_root)),
                    'universes': sorted(universes),
                    'count': len(universes),
                }

    # impl tournament rounds
    impl_rounds: dict[int, dict[str, Any]] = {}
    if impl_dir.exists():
        for md in impl_dir.glob('tournament-impl-*.md'):
            m = re.match(r'^tournament-impl-(\d+)\.md$', md.name)
            if m:
                round_n = int(m.group(1))
                universes = list_universes_in_tournament(md)
                impl_rounds[round_n] = {
                    'tournament_md': str(md.relative_to(project_root)),
                    'universes': sorted(universes),
                    'count': len(universes),
                    'seven_condition_explicit': check_seven_condition_explicit(md),
                }

    # plan candidates 디렉터리
    plan_candidates_universes = list_universes_in_dir(plan_dir / 'candidates')
    impl_candidates_universes = list_universes_in_dir(impl_dir / 'candidates')

    violations: list[dict[str, Any]] = []

    # plan round monotonicity
    sorted_plan_rounds = sorted(plan_rounds.keys())
    for i in range(1, len(sorted_plan_rounds)):
        prev = sorted_plan_rounds[i - 1]
        curr = sorted_plan_rounds[i]
        prev_set = set(plan_rounds[prev]['universes'])
        curr_set = set(plan_rounds[curr]['universes'])
        new_universes = curr_set - prev_set
        if len(curr_set) < len(prev_set):
            violations.append({
                'kind': 'plan_round_decrease',
                'prev_round': prev,
                'prev_count': len(prev_set),
                'curr_round': curr,
                'curr_count': len(curr_set),
                'reason': f"plan round {curr} ({len(curr_set)}) < round {prev} ({len(prev_set)})",
            })
        elif len(new_universes) == 0:
            violations.append({
                'kind': 'plan_round_zero_new_universe',
                'prev_round': prev,
                'curr_round': curr,
                'count': len(curr_set),
                'reason': (
                    f"plan round {curr} 가 round {prev} 의 universe 와 동일 (NEW universe = 0). "
                    f"dacapo-skip-sentinel 위반 — re-rate 만으로는 불충분."
                ),
            })

    # impl round monotonicity (between impl rounds)
    sorted_impl_rounds = sorted(impl_rounds.keys())
    for i in range(1, len(sorted_impl_rounds)):
        prev = sorted_impl_rounds[i - 1]
        curr = sorted_impl_rounds[i]
        if impl_rounds[curr]['count'] < impl_rounds[prev]['count']:
            violations.append({
                'kind': 'impl_round_decrease',
                'prev_round': prev,
                'curr_round': curr,
                'reason': f"impl round {curr} count < round {prev}",
            })

    # plan -> impl bridge (single universe 차단)
    if plan_rounds and impl_rounds:
        last_plan_round = max(plan_rounds.keys())
        first_impl_round = min(impl_rounds.keys())
        plan_count = plan_rounds[last_plan_round]['count']
        impl_count = impl_rounds[first_impl_round]['count']
        # impl-multiverse-strict — single universe = 7-condition 명시 필요
        if impl_count == 1 and plan_count > 1:
            if not impl_rounds[first_impl_round].get('seven_condition_explicit'):
                violations.append({
                    'kind': 'impl_single_universe_without_seven_condition',
                    'plan_count': plan_count,
                    'impl_count': impl_count,
                    'impl_md': impl_rounds[first_impl_round]['tournament_md'],
                    'reason': (
                        f"impl 단일 universe (plan {plan_count} → impl 1) 인데 "
                        f"impl-multiverse-strict 7-condition ≥ 5 키워드 명시 부족."
                    ),
                })

    # plan candidates dir 검증 — tournament 와 일관성
    if plan_rounds:
        last_plan_round = max(plan_rounds.keys())
        tournament_universes = set(plan_rounds[last_plan_round]['universes'])
        if plan_candidates_universes and plan_candidates_universes != tournament_universes:
            violations.append({
                'kind': 'plan_candidates_mismatch',
                'tournament': sorted(tournament_universes),
                'candidates_dir': sorted(plan_candidates_universes),
                'reason': "plan/candidates/ universe 디렉터리와 tournament 본문 universe 인용 불일치",
            })

    overall_pass = len(violations) == 0

    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'plan_rounds': plan_rounds,
        'impl_rounds': impl_rounds,
        'plan_candidates_universes': sorted(plan_candidates_universes),
        'impl_candidates_universes': sorted(impl_candidates_universes),
        'violations': violations,
        'verdict': 'pass' if overall_pass else 'fail',
        'reason': (
            'universe 단조성 OK'
            if overall_pass
            else f"{len(violations)} violation"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='universe_count_monotonicity',
        description=(
            'Universe 단조성 강제 CLI — round N+1 ≥ N + impl single universe + '
            '7-condition 명시 검증. HARD-RULE 9.vv (sprint-42).'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(ns.project_root)

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[universe_count_monotonicity] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        for v in verdict_obj['violations']:
            print(f"  - [{v['kind']}] {v.get('reason', '')}", file=sys.stderr)

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
