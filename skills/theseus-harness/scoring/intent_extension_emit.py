"""intent_extension_emit.py — Phase 1.5 Hidden Intent 산출물 emit 검증 CLI (sprint-50 PR-B v0.9.50).

본 스크립트는 페이즈 1.5 의 3 산출물 (`intent/01-hidden-intent.md` /
`intent/01-extension-scope.md` / `intent/01-extension-trace.md`) 존재 + 항목 ≥5
+ 카테고리 distinct ≥3 + should 채택 ≥1 검증. 부재 / 미달 시 exit 1.

본 CLI 의 *vacuous PASS 차단* — `feedback_score_targeting_taboo.md` 정합:
- 항목 ≥5 만 보지 않고 카테고리 distinct ≥3 의무 (= 같은 카테고리만 5 개로 우회 차단).
- *should* 채택 ≥1 의무 (= 전부 *could* 보류로 우회 차단).
- 항목 본문이 ≥80 chars (vacuous 한 줄 우회 차단).

증거 회피 사례 (g4-v3 산출물 분석):
    `intent/01-additional.md` = refresh-1 supplement 17 줄. 이건 *extension 이 아니라 supplement*.
    extension 은 별도 페이즈 (1.5) 의무.

사용:
    python intent_extension_emit.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --min-items 5 \\
        --min-categories 3 \\
        --require-should-adoption

Exit codes:
    0 — 3 산출물 모두 emit + 항목 ≥5 + 카테고리 distinct ≥3 + should 채택 ≥1
    1 — 미달 (결손 항목 list)
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.50"


CATEGORY_CATALOG = {
    'validation', 'sensitivity', 'non-functional', 'domain-modeling', 'risk',
    'observability', 'scalability', 'accessibility', 'maintainability', 'reproducibility',
}


HI_HEADER_RE = re.compile(r'^##\s+HI-(\d+)\b', re.MULTILINE)
CATEGORY_RE = re.compile(r'\*\*카테고리\*\*\s*[:\-]?\s*([a-z\-]+)', re.IGNORECASE)
REACH_RE = re.compile(r'\*\*(?:본\s*회차\s*)?reach(?:\s*의향)?\*\*\s*[:\-]?\s*(must|should|could)', re.IGNORECASE)
SCOPE_TABLE_ROW_RE = re.compile(
    r'^\|\s*HI-(\d+)\s*\|[^|]*\|\s*([a-z\-]+)\s*\|\s*(must|should|could)\s*\|',
    re.IGNORECASE | re.MULTILINE,
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


def parse_hidden_intent(body: str) -> list[dict]:
    """`intent/01-hidden-intent.md` 본문 parse — HI-NN 항목 list."""
    items = []
    headers = list(HI_HEADER_RE.finditer(body))
    for idx, m in enumerate(headers):
        start = m.start()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(body)
        chunk = body[start:end]
        category_match = CATEGORY_RE.search(chunk)
        reach_match = REACH_RE.search(chunk)
        items.append({
            'id': f'HI-{m.group(1).zfill(2)}',
            'category': category_match.group(1).lower() if category_match else None,
            'reach': reach_match.group(1).lower() if reach_match else None,
            'body_chars': len(chunk.strip()),
        })
    return items


def parse_extension_scope(body: str) -> list[dict]:
    """`intent/01-extension-scope.md` 본문 parse — 표에서 (id, category, reach) 추출."""
    items = []
    for m in SCOPE_TABLE_ROW_RE.finditer(body):
        items.append({
            'id': f'HI-{m.group(1).zfill(2)}',
            'category': m.group(2).lower(),
            'reach': m.group(3).lower(),
        })
    return items


def parse_extension_trace(body: str) -> list[str]:
    """`intent/01-extension-trace.md` 본문 parse — `## HI-NN` 헤더 list."""
    return [f'HI-{m.group(1).zfill(2)}' for m in HI_HEADER_RE.finditer(body)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--project-root', type=Path, default=None)
    parser.add_argument('--min-items', type=int, default=5)
    parser.add_argument('--min-categories', type=int, default=3)
    parser.add_argument('--min-body-chars', type=int, default=80,
                        help='항목별 최소 본문 길이 (vacuous 차단)')
    parser.add_argument('--require-should-adoption', action='store_true', default=False)
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.project_root is None:
        parser.error('--project-root required when not --self-test')
    root = args.project_root
    intent_dir = root / 'intent'
    p_hi = intent_dir / '01-hidden-intent.md'
    p_scope = intent_dir / '01-extension-scope.md'
    p_trace = intent_dir / '01-extension-trace.md'

    failures: list[str] = []

    if not p_hi.exists():
        failures.append(f'missing: {p_hi}')
    if not p_scope.exists():
        failures.append(f'missing: {p_scope}')
    if not p_trace.exists():
        failures.append(f'missing: {p_trace}')

    if failures:
        report = {
            'schema_version': SCHEMA_VERSION,
            'pass': False,
            'failures': failures,
        }
        _emit(report, args.json_out)
        print('FAIL: hidden intent 3 산출물 부재', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1

    hi_items = parse_hidden_intent(_read(p_hi))
    scope_items = parse_extension_scope(_read(p_scope))
    trace_items = parse_extension_trace(_read(p_trace))

    if len(hi_items) < args.min_items:
        failures.append(f'item count {len(hi_items)} < min {args.min_items}')

    cats = {it['category'] for it in hi_items if it['category'] in CATEGORY_CATALOG}
    if len(cats) < args.min_categories:
        failures.append(
            f'distinct category count {len(cats)} < min {args.min_categories} '
            f'(found: {sorted(cats)})'
        )

    short = [it['id'] for it in hi_items if it['body_chars'] < args.min_body_chars]
    if short:
        failures.append(f'vacuous items (body < {args.min_body_chars} chars): {short}')

    if args.require_should_adoption:
        should_in_scope = [it for it in scope_items if it['reach'] == 'should']
        if not should_in_scope:
            failures.append('no `should` adoption in extension-scope (require-should-adoption)')

    # cross-file id consistency
    hi_ids = {it['id'] for it in hi_items}
    scope_ids = {it['id'] for it in scope_items}
    trace_ids = set(trace_items)
    adopted_ids = {it['id'] for it in scope_items if it['reach'] in ('must', 'should')}
    missing_trace = adopted_ids - trace_ids
    if missing_trace:
        failures.append(f'adopted (must/should) items without trace doc entry: {sorted(missing_trace)}')

    orphan_in_scope = scope_ids - hi_ids
    if orphan_in_scope:
        failures.append(f'scope references unknown HI ids: {sorted(orphan_in_scope)}')

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'failures': failures,
        'metrics': {
            'item_count': len(hi_items),
            'distinct_categories': sorted(cats),
            'scope_count': len(scope_items),
            'trace_count': len(trace_items),
            'adopted_count': len(adopted_ids),
        },
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: hidden intent emit ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: hidden intent emit '
        f'(items={len(hi_items)} cats={len(cats)} adopted={len(adopted_ids)})'
    )
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    """Self-test fixture — embedded sample doc로 parser 동작 검증."""
    sample_hi = '''# 01-hidden-intent.md

## HI-01 — 입력 데이터 sanity 검증 부재

- **카테고리**: validation
- **prompt 직접 인용 여부**: NO
- **합리적 평가자 expectation 근거**: 평가자는 input topology / scenario.yaml 의 결손 / 음수 / 일관성 위반에 대한 명시적 검증을 기대한다. prompt 는 *결과* 만 묻고 *입력 검증* 안 묻음.
- **impact 추정**: medium
- **본 회차 reach 의향**: should

## HI-02 — Truck inter-arrival sensitivity sweep

- **카테고리**: sensitivity
- **prompt 직접 인용 여부**: NO
- **합리적 평가자 expectation 근거**: prompt 는 trucks_4 / trucks_12 만 sweep. inter-arrival 분포 sweep 은 prompt 외 차원. 평가자는 robust DoE 를 기대.
- **impact 추정**: high
- **본 회차 reach 의향**: should

## HI-03 — Replication seed determinism 명시

- **카테고리**: reproducibility
- **prompt 직접 인용 여부**: NO
- **합리적 평가자 expectation 근거**: prompt 는 random_seed column 만 요구. seed → reproducibility 보장 절차 (e.g. all RNG sources lockdown) 는 prompt 외.
- **impact 추정**: medium
- **본 회차 reach 의향**: must

## HI-04 — Queueing theory framing in Conceptual model

- **카테고리**: domain-modeling
- **prompt 직접 인용 여부**: NO
- **합리적 평가자 expectation 근거**: prompt 는 *모델* 만 묻고 *이론 framing* 안 묻음. queueing theory M/G/c bounds 와의 비교가 평가에 가치.
- **impact 추정**: high
- **본 회차 reach 의향**: should

## HI-05 — Memory ceiling under trucks_12 + long shift

- **카테고리**: scalability
- **prompt 직접 인용 여부**: NO
- **합리적 평가자 expectation 근거**: 시나리오 sweep 시 메모리 가 어떻게 거동하는지 prompt 외. event_log.csv 가 unbounded 일 가능성.
- **impact 추정**: low
- **본 회차 reach 의향**: could
'''
    sample_scope = '''# 01-extension-scope.md

| ID | 진술 (단축) | 카테고리 | reach | trace 대상 페이즈 |
|---|---|---|---|---|
| HI-01 | 입력 sanity 검증 | validation | should | impl |
| HI-02 | inter-arrival sweep | sensitivity | should | plan / impl |
| HI-03 | seed determinism | reproducibility | must | impl |
| HI-04 | queueing framing | domain-modeling | should | plan |
| HI-05 | memory ceiling | scalability | could | (보류) |
'''
    sample_trace = '''# 01-extension-trace.md

## HI-01 (should)
- trace: impl/08-impl-log.md §X

## HI-02 (should)
- trace: plan/06-plan.md §Y, impl §Z

## HI-03 (must)
- trace: impl/08-impl-log.md §W

## HI-04 (should)
- trace: plan/06-plan.md §V
'''

    items = parse_hidden_intent(sample_hi)
    assert len(items) == 5, f'expected 5 items, got {len(items)}'
    assert {it['category'] for it in items} == {
        'validation', 'sensitivity', 'reproducibility', 'domain-modeling', 'scalability'
    }, f'category mismatch: {[it["category"] for it in items]}'
    assert sum(1 for it in items if it['reach'] == 'should') == 3

    scope = parse_extension_scope(sample_scope)
    assert len(scope) == 5, f'expected 5 scope rows, got {len(scope)}'

    trace = parse_extension_trace(sample_trace)
    assert set(trace) == {'HI-01', 'HI-02', 'HI-03', 'HI-04'}, f'trace mismatch: {trace}'

    print('SELF-TEST PASS — intent_extension_emit')
    return 0


if __name__ == '__main__':
    sys.exit(main())
