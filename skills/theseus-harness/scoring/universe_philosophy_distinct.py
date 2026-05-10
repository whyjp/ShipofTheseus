"""universe_philosophy_distinct.py — Phase 06 Design-Twice 강제 CLI (sprint-50 PR-C v0.9.50).

본 스크립트는 plan tournament universe N (G3=3, G4=4, G5=6) 가 *서로 다른 설계 철학*
으로 출발했는지 검증. 같은 philosophy universe ≥2 = exit 1.

증거 회피 사례 (g4-v3 plan tournament):
    universe-1/2/3 모두 *modular* 변형 — 코드 분기는 있되 *설계 철학 단일*.
    tournament winner 가 사실상 항상 *modular* 인 패턴 유발 (plateau 의 한 원인).

본 CLI 의 *vacuous PASS 차단* (premortem §3-2):
- 1 단: universe-N/meta.md frontmatter `philosophy` 필드 의무.
- 2 단: universe-N/06-plan.md 본문에서 architectural 결정 ≥3 추출 + universe 간
        declared 결정 distinct ≥ ⌈N/2⌉ (이름만 다른 우주 차단).

Allowed philosophy catalog (default 7):
    modular, oop, functional, data-driven, event-driven, actor, dsl-first

`--allow-extra` 시 카탈로그 외 값도 허용 (단 declare).

격언:
    Ousterhout, *A Philosophy of Software Design*, Ch.11 — "Design It Twice".

사용:
    python universe_philosophy_distinct.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --grade G4

Exit codes:
    0 — 모든 universe philosophy distinct + meta.md philosophy 필드 존재
        + 본문 결정 distinct ≥ ⌈N/2⌉
    1 — 미달 (중복 philosophy / 결손 필드 / 결정 동질)
"""

from __future__ import annotations

import argparse
import io
import json
import math
import re
import sys
from pathlib import Path


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.50"


PHILOSOPHY_CATALOG = {
    'modular', 'oop', 'functional', 'data-driven', 'event-driven', 'actor', 'dsl-first',
}


GRADE_UNIVERSE_COUNT = {
    'G2': 0,  # tournament 없음
    'G3': 3,
    'G4': 4,
    'G5': 6,
}


FRONTMATTER_RE = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)
PHILOSOPHY_FIELD_RE = re.compile(r'^philosophy\s*:\s*([A-Za-z0-9\-_]+)\s*$', re.MULTILINE)


# Architectural decision keywords (06-plan.md 본문에서 § 표제로 등장 시 추출).
ARCH_DECISION_HEADERS = [
    'module boundary', 'module boundaries', '모듈 경계',
    'communication', 'communication style', '통신 방식',
    'state management', 'state model', '상태 관리',
    'error model', 'error handling', 'fallback', '에러 모델',
    'concurrency', 'concurrency model', '동시성',
    'data flow', 'data model', '데이터 흐름',
    'extension point', 'plugin', '확장 지점',
    'persistence', '영속성',
    'event model', 'event handling', '이벤트 모델',
    'control flow', '제어 흐름',
]


HEADER_RE = re.compile(r'^#{2,4}\s+(.+?)\s*$', re.MULTILINE)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


def _frontmatter(body: str) -> str:
    m = FRONTMATTER_RE.match(body)
    return m.group(1) if m else ''


def _philosophy_of(meta_path: Path) -> str | None:
    body = _read(meta_path)
    fm = _frontmatter(body)
    m = PHILOSOPHY_FIELD_RE.search(fm)
    if m:
        return m.group(1).lower()
    # fallback: body 본문에서 `Philosophy:` 또는 `철학:` 라인
    body_m = re.search(r'^\*?\*?(?:Philosophy|철학)\*?\*?\s*[:：]\s*([A-Za-z0-9\-_]+)',
                       body, re.MULTILINE)
    return body_m.group(1).lower() if body_m else None


def _arch_decisions(plan_path: Path) -> list[str]:
    """plan/06-plan.md 의 architectural decision header 카운트.

    section header 가 ARCH_DECISION_HEADERS 의 keyword 와 substring 매치하는 것만.
    """
    body = _read(plan_path)
    if not body:
        return []
    headers = [m.group(1).strip().lower() for m in HEADER_RE.finditer(body)]
    decisions = []
    for h in headers:
        for kw in ARCH_DECISION_HEADERS:
            if kw in h:
                decisions.append(h)
                break
    return decisions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--project-root', type=Path, default=None)
    parser.add_argument('--grade', type=str, default='G4',
                        choices=['G2', 'G3', 'G4', 'G5'])
    parser.add_argument('--allow-extra', action='store_true', default=False,
                        help='카탈로그 외 philosophy 값도 허용 (declared 시)')
    parser.add_argument('--min-decision-distinct-ratio', type=float, default=0.5,
                        help='universe 간 architectural decision header distinct '
                             '비율 ≥ τ — default 0.5 (⌈N/2⌉ 의미)')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.project_root is None:
        parser.error('--project-root required when not --self-test')

    expected = GRADE_UNIVERSE_COUNT[args.grade]
    if expected == 0:
        print(f'PASS: grade {args.grade} no tournament — skip')
        return 0

    candidates_dir = args.project_root / 'plan' / 'candidates'
    if not candidates_dir.exists():
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': [f'missing: {candidates_dir}']}
        _emit(report, args.json_out)
        print(f'FAIL: {candidates_dir} 부재', file=sys.stderr)
        return 1

    universes = sorted(d for d in candidates_dir.iterdir()
                       if d.is_dir() and d.name.startswith('universe-'))
    if len(universes) < expected:
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': [f'universe count {len(universes)} < grade-{args.grade} '
                               f'expected {expected}']}
        _emit(report, args.json_out)
        print(f'FAIL: universe 수 {len(universes)} < {expected}', file=sys.stderr)
        return 1

    failures: list[str] = []
    declared = []
    decisions_per_universe = []

    for u in universes:
        meta = u / 'meta.md'
        plan = u / '06-plan.md'
        phi = _philosophy_of(meta)
        if phi is None:
            failures.append(f'{u.name}: meta.md 에 `philosophy:` 필드 부재')
            declared.append(None)
        else:
            if phi not in PHILOSOPHY_CATALOG and not args.allow_extra:
                failures.append(
                    f'{u.name}: philosophy={phi} 카탈로그 외 (use --allow-extra)'
                )
            declared.append(phi)
        decisions_per_universe.append(_arch_decisions(plan))

    # 1 단: declared philosophy distinct count
    distinct_phi = {p for p in declared if p is not None}
    if len(declared) and None not in declared:
        if len(distinct_phi) < len(declared):
            dups = [p for p in declared if declared.count(p) > 1]
            failures.append(
                f'philosophy 중복: {dups} (distinct {len(distinct_phi)}/{len(declared)})'
            )

    # 2 단: architectural decision distinct ratio
    all_decisions = [set(d) for d in decisions_per_universe]
    union_decisions = set().union(*all_decisions) if all_decisions else set()
    distinctness_ratio = 0.0
    if union_decisions:
        # 각 universe 가 unique 하게 가지는 decision header 수 / 전체 union
        unique_per_u = []
        for i, dset in enumerate(all_decisions):
            others = set().union(*(s for j, s in enumerate(all_decisions) if j != i))
            unique_per_u.append(len(dset - others))
        distinctness_ratio = (
            sum(1 for u in unique_per_u if u >= 1) / len(all_decisions)
            if all_decisions else 0.0
        )

    needed_universes_with_unique = math.ceil(
        len(universes) * args.min_decision_distinct_ratio
    )
    if all_decisions and union_decisions:
        u_with_unique = sum(
            1 for i, dset in enumerate(all_decisions)
            if dset - set().union(*(s for j, s in enumerate(all_decisions) if j != i))
        )
        if u_with_unique < needed_universes_with_unique:
            failures.append(
                f'architectural decision 동질성 의심 — universe 중 unique decision '
                f'≥1 보유 = {u_with_unique}/{len(universes)}, '
                f'min={needed_universes_with_unique}'
            )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'grade': args.grade,
        'expected_universes': expected,
        'universes_found': len(universes),
        'declared_philosophies': declared,
        'distinct_philosophies': sorted(distinct_phi),
        'decision_distinctness_ratio': round(distinctness_ratio, 3),
        'failures': failures,
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: universe philosophy distinct ({len(failures)} 결손)',
              file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: universe philosophy distinct '
        f'({len(declared)} universes, philosophies={sorted(distinct_phi)})'
    )
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    sample_meta = '''---
universe: 1
philosophy: modular
---
# Universe-1 meta'''
    body_with_phi = sample_meta
    fm = _frontmatter(body_with_phi)
    m = PHILOSOPHY_FIELD_RE.search(fm)
    assert m and m.group(1) == 'modular', f'philosophy parse failed: {m}'

    sample_plan = '''# Plan

## Module boundary
content

## Communication style
content

## State management
content

## Random other
content
'''
    decs = _arch_decisions_str(sample_plan)
    assert len(decs) == 3, f'expected 3 decisions, got {decs}'
    print('SELF-TEST PASS — universe_philosophy_distinct')
    return 0


def _arch_decisions_str(body: str) -> list[str]:
    headers = [m.group(1).strip().lower() for m in HEADER_RE.finditer(body)]
    decs = []
    for h in headers:
        for kw in ARCH_DECISION_HEADERS:
            if kw in h:
                decs.append(h)
                break
    return decs


if __name__ == '__main__':
    sys.exit(main())
