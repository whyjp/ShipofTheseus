"""knowledge_portfolio_check.py — Knowledge Portfolio refresh CLI (sprint-50 PR-F v0.9.50).

본 스크립트는 Hunt & Thomas, *The Pragmatic Programmer*, Ch.1 — *"A Pragmatic
Philosophy"*, "Your Knowledge Portfolio" 의 enforcement.

페이즈 14 handoff 산출물 (`handoff/14-handoff.md`) 본문이 *본 회차에서 학습한 통찰
≥ 3* 명시 의무. 단순 산출물 list 가 아니라 *insight*.

heuristic — handoff 본문의 §-level header 중 다음 keyword 매치:
- 'lesson', 'learned', 'insight', 'finding', 'takeaway', 'observation',
  'discovery', '학습', '교훈', '발견', '관찰', '통찰'

해당 § 본문이 ≥80 chars (vacuous 한 줄 차단) 의무.

vacuous PASS 차단:
- header 만 있고 본문 0 = fail.
- 같은 keyword section 이 ≥3 개 = false positive — distinct *주제* (header text 자체)
  ≥3 의무.

격언:
    Hunt & Thomas: "Treat your knowledge as an investment portfolio. Diversify.
    Take risks. ... Review and rebalance periodically."

사용:
    python knowledge_portfolio_check.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --min-insights 3

Exit codes:
    0 — handoff 본문에 ≥3 distinct insight section + 각 ≥80 chars
    1 — 미달
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


INSIGHT_KEYWORDS = [
    'lesson', 'learned', 'insight', 'finding', 'takeaway',
    'observation', 'discovery',
    '학습', '교훈', '발견', '관찰', '통찰', '시사점',
]


HEADER_RE = re.compile(r'^(#{2,4})\s+(.+?)\s*$', re.MULTILINE)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


def find_insight_sections(body: str) -> list[dict]:
    """handoff body 의 keyword-매치 섹션 list — (header, body_chars)."""
    headers = list(HEADER_RE.finditer(body))
    matched = []
    for idx, m in enumerate(headers):
        header_text = m.group(2).strip().lower()
        if any(kw in header_text for kw in INSIGHT_KEYWORDS):
            start = m.end()
            end = headers[idx + 1].start() if idx + 1 < len(headers) else len(body)
            section_body = body[start:end].strip()
            matched.append({
                'header': m.group(2).strip(),
                'header_lower': header_text,
                'body_chars': len(section_body),
            })
    return matched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--project-root', type=Path, default=None)
    parser.add_argument('--min-insights', type=int, default=3)
    parser.add_argument('--min-body-chars', type=int, default=80,
                        help='insight section 별 최소 본문 길이 (vacuous 차단)')
    parser.add_argument('--handoff-path', type=Path, default=None,
                        help='override handoff path (default: <root>/handoff/14-handoff.md)')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.project_root is None and args.handoff_path is None:
        parser.error('--project-root or --handoff-path required when not --self-test')

    handoff = args.handoff_path or (args.project_root / 'handoff' / '14-handoff.md')
    if not handoff.exists():
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': [f'missing: {handoff}']}
        _emit(report, args.json_out)
        print(f'FAIL: {handoff} 부재', file=sys.stderr)
        return 1

    body = _read(handoff)
    sections = find_insight_sections(body)

    failures: list[str] = []

    valid_sections = [
        s for s in sections if s['body_chars'] >= args.min_body_chars
    ]

    if len(valid_sections) < args.min_insights:
        failures.append(
            f'insight section count {len(valid_sections)} < min '
            f'{args.min_insights} '
            f'(found {len(sections)} headers; '
            f'{len(sections) - len(valid_sections)} vacuous)'
        )

    # distinct topic — header text (not lower) 가 모두 다름
    distinct_headers = {s['header'] for s in valid_sections}
    if len(distinct_headers) < min(args.min_insights, len(valid_sections)):
        failures.append(
            f'duplicate insight headers — distinct {len(distinct_headers)} '
            f'< {len(valid_sections)} sections'
        )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'handoff_path': str(handoff),
        'sections_found': len(sections),
        'valid_sections': len(valid_sections),
        'distinct_headers': sorted(distinct_headers),
        'failures': failures,
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: knowledge-portfolio ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: knowledge-portfolio '
        f'(insights={len(valid_sections)} distinct={len(distinct_headers)})'
    )
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    sample_handoff = '''# 14 — Handoff

## Project files

- src/...
- tests/...

## Lessons learned — universe-2 modular won

본 회차에서 universe-2 modular philosophy 가 plan tournament winner 가 된 것은
4-truck under-saturation 시 graph traversal 비용 vs context switch overhead 의
교환점이 universe-3 actor 모델보다 명시적이었기 때문. 80 chars 충족.

## Key finding — crusher binding 91%

baseline crusher utilization 91% 가 장기 distribution 임을 30 replication CI95 로
확인. ramp_upgrade 에서 +0.9% 만 상승한 이유 = crusher binding (ramp 비-병목) 의 직접 증거. 80 chars 충족.

## 학습 — sensitivity sweep 부재의 결손

본 회차는 truck count sweep 만 진행. inter-arrival 분포 sweep 은 phase 1.5 에서
should 채택 됐으나 본 회차 reach 안 함 — 다음 회차 인계. 80 chars 충족.

## Random other section

irrelevant.
'''
    sections = find_insight_sections(sample_handoff)
    assert len(sections) == 3, f'expected 3 sections, got {len(sections)}: {sections}'
    valid = [s for s in sections if s['body_chars'] >= 80]
    assert len(valid) == 3, f'expected 3 valid, got {len(valid)}'
    print(f'SELF-TEST PASS — knowledge-portfolio (sections={len(sections)})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
