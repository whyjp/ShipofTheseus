"""hidden_intent_originality.py — Hidden intent paraphrase 차단 휴리스틱 CLI (sprint-50 PR-B v0.9.50).

본 스크립트는 페이즈 1.5 의 hidden intent 항목이 *프롬프트 직접 paraphrase* 가 아닌지
2 단 휴리스틱으로 검증.

1 단 — token-overlap: 항목 본문 (단, prompt 인용 명시 블록은 제외) 의 token bag 과
       prompt 본문 token bag 의 Jaccard overlap ≤ τ (default 0.4).
2 단 — semantic-novelty: 항목 카테고리 카탈로그 10 종 중 *prompt 의 5 자연 카테고리
       (data / topology / scenario / metrics / constraints) 외* ≥1 개를 다룸. 즉 항목들이
       모두 prompt 의 자연 카테고리에 속해 있으면 paraphrase 의심 (false positive 일부 OK).

본 CLI 는 *worst-case metric-gaming 회피* (premortem §3-1) — agent 가 metric 만 맞추기
위해 *겉으로 다른 표현* 만 추가하는 패턴 차단.

prompt 의 5 자연 카테고리 (default — bench / project 별 override 가능):
    data, topology, scenario, metrics, constraints

확장 카테고리 catalog (intent_extension_emit.py 와 일치):
    validation, sensitivity, non-functional, domain-modeling, risk,
    observability, scalability, accessibility, maintainability, reproducibility

사용:
    python hidden_intent_originality.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --prompt-file <path-to-prompt> \\
        --max-token-overlap 0.4 \\
        --escape-categories-min 1

Exit codes:
    0 — 모든 항목이 token-overlap ≤ τ AND 카테고리가 *escape* (자연 카테고리 외) ≥1
    1 — 미달 (paraphrase 의심 항목 list)
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


HI_HEADER_RE = re.compile(r'^##\s+HI-(\d+)\b', re.MULTILINE)
CATEGORY_RE = re.compile(r'\*\*카테고리\*\*\s*[:\-]?\s*([a-z\-]+)', re.IGNORECASE)


# 항목 본문에서 prompt 인용 블록 (markdown blockquote) 은 token-overlap 계산에서 제외.
QUOTE_BLOCK_RE = re.compile(r'^>\s.*$', re.MULTILINE)


# 자연 카테고리 (prompt 가 *직접* 묻는 영역) — escape 의 *반대*.
NATURAL_CATEGORIES = {
    'data', 'topology', 'scenario', 'metrics', 'constraints',
}


# 확장 카탈로그 (escape 영역).
EXTENSION_CATEGORIES = {
    'validation', 'sensitivity', 'non-functional', 'domain-modeling', 'risk',
    'observability', 'scalability', 'accessibility', 'maintainability', 'reproducibility',
}


# token 추출 — alpha 2+ chars (한글 포함). 숫자 제외.
TOKEN_RE = re.compile(r'[A-Za-z가-힣]{2,}')

# stopwords — Jaccard 노이즈 제거 위해 자주 나오는 token.
STOPWORDS = {
    'the', 'and', 'for', 'with', 'this', 'that', 'are', 'has', 'have', 'was', 'were',
    'should', 'must', 'could', 'will', 'can', 'may', 'one', 'two', 'three', 'all', 'any',
    'not', 'but', 'or', 'as', 'is', 'be', 'an', 'in', 'of', 'on', 'to', 'by', 'at',
    'from', 'into', 'over', 'than', 'these', 'those', 'such', 'each', 'per',
    '본', '및', '와', '의', '이', '가', '은', '는', '를', '을', '에', '로', '도', '만',
    '에서', '에는', '에서는', '대한', '대해', '있는', '있다', '없는', '없다', '하는', '한다',
    '해야', '한다', '된다', '됨', '있음', '없음',
}


def _tokens(s: str) -> set[str]:
    raw = (t.lower() for t in TOKEN_RE.findall(s or ''))
    return {t for t in raw if t not in STOPWORDS and len(t) >= 3}


def _strip_quotes(body: str) -> str:
    return QUOTE_BLOCK_RE.sub('', body)


def _hi_items(body: str) -> list[tuple[str, str, str | None]]:
    """(id, body, category) tuples."""
    items = []
    headers = list(HI_HEADER_RE.finditer(body))
    for idx, m in enumerate(headers):
        start = m.start()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(body)
        chunk = body[start:end]
        cat_m = CATEGORY_RE.search(chunk)
        items.append((
            f'HI-{m.group(1).zfill(2)}',
            chunk,
            cat_m.group(1).lower() if cat_m else None,
        ))
    return items


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--project-root', type=Path, default=None)
    parser.add_argument('--prompt-file', type=Path, default=None,
                        help='원 prompt 파일. 없으면 intent/01-intent.md 의 §a 무엇을 사용')
    parser.add_argument('--max-token-overlap', type=float, default=0.4)
    parser.add_argument('--escape-categories-min', type=int, default=1,
                        help='extension 카테고리 (자연 외) 항목 ≥ N 의무')
    parser.add_argument('--natural-categories', type=str, default=None,
                        help='자연 카테고리 override (comma-separated). default: data,topology,scenario,metrics,constraints')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.project_root is None:
        parser.error('--project-root required when not --self-test')
    natural = NATURAL_CATEGORIES
    if args.natural_categories:
        natural = {c.strip().lower() for c in args.natural_categories.split(',') if c.strip()}

    proj = args.project_root
    p_hi = proj / 'intent' / '01-hidden-intent.md'
    if not p_hi.exists():
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': [f'missing: {p_hi}']}
        _emit(report, args.json_out)
        print(f'FAIL: {p_hi} 부재', file=sys.stderr)
        return 1

    if args.prompt_file and args.prompt_file.exists():
        prompt_text = args.prompt_file.read_text(encoding='utf-8')
    else:
        # fallback: intent/01-intent.md 의 §a "무엇을" 단락만 prompt 로 간주.
        p_intent = proj / 'intent' / '01-intent.md'
        prompt_text = p_intent.read_text(encoding='utf-8') if p_intent.exists() else ''

    prompt_tokens = _tokens(prompt_text)
    if not prompt_tokens:
        print('WARNING: prompt token bag 비어 있음 — token-overlap 검사 skip',
              file=sys.stderr)

    items = _hi_items(p_hi.read_text(encoding='utf-8'))
    if not items:
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': ['no HI items in 01-hidden-intent.md']}
        _emit(report, args.json_out)
        print('FAIL: HI 항목 0', file=sys.stderr)
        return 1

    failures: list[str] = []
    per_item = []

    overlaps_high = []
    for hi_id, body, _cat in items:
        item_text = _strip_quotes(body)
        item_tokens = _tokens(item_text)
        overlap = jaccard(item_tokens, prompt_tokens) if prompt_tokens else 0.0
        per_item.append({
            'hi_id': hi_id,
            'token_overlap': round(overlap, 3),
            'item_token_count': len(item_tokens),
        })
        if overlap > args.max_token_overlap:
            overlaps_high.append((hi_id, overlap))

    if overlaps_high:
        for hi_id, ov in overlaps_high:
            failures.append(
                f'{hi_id}: token-overlap {ov:.3f} > max {args.max_token_overlap}'
            )

    # 2 단: escape 카테고리 (자연 외) ≥ N
    cats = [cat for _id, _body, cat in items if cat]
    escape_cats = [c for c in cats if c in EXTENSION_CATEGORIES and c not in natural]
    if len(escape_cats) < args.escape_categories_min:
        failures.append(
            f'escape-category count {len(escape_cats)} < min '
            f'{args.escape_categories_min} (cats: {cats})'
        )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'failures': failures,
        'natural_categories': sorted(natural),
        'per_item': per_item,
        'escape_category_count': len(escape_cats),
        'item_count': len(items),
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: hidden intent originality ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: hidden intent originality '
        f'(items={len(items)} escape_cats={len(escape_cats)})'
    )
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    prompt = 'simulate mining throughput with trucks loaders and crusher topology and scenarios'
    paraphrase_body = '''## HI-01 — simulate mining throughput more carefully

- **카테고리**: data
- text body: simulate mining throughput with trucks loaders crusher topology scenarios
'''
    novel_body = '''## HI-01 — Sensitivity sweep on inter-arrival distribution

- **카테고리**: sensitivity
- text body: design of experiments factorial sweep on stochastic input distributions
'''
    p_tokens = _tokens(prompt)
    para_items = _hi_items(paraphrase_body)
    novel_items = _hi_items(novel_body)

    para_overlap = jaccard(_tokens(_strip_quotes(para_items[0][1])), p_tokens)
    novel_overlap = jaccard(_tokens(_strip_quotes(novel_items[0][1])), p_tokens)

    assert para_overlap > 0.4, f'paraphrase overlap {para_overlap}, expected > 0.4'
    assert novel_overlap < 0.4, f'novel overlap {novel_overlap}, expected < 0.4'
    print(
        f'SELF-TEST PASS — paraphrase overlap={para_overlap:.3f} '
        f'novel overlap={novel_overlap:.3f}'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
