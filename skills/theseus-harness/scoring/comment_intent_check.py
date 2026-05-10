"""comment_intent_check.py — Comments-Why-Not-What enforcement CLI (sprint-50 PR-E v0.9.50).

본 스크립트는 Ousterhout, *A Philosophy of Software Design*, Ch.13 — *"Comments
Should Describe Things That Are Not Obvious from the Code"* 의 휴리스틱 enforcement.

comment 와 *바로 다음 코드 줄* 의 token Jaccard overlap 이 높으면 *paraphrase*
(코드를 재서술하는 무가치한 comment) 의심. 비율 ≤ τ 의무.

vacuous PASS 차단 (premortem §3-4):
- sentinel marker (`# why:` / `// why:` / `# 이유:`) 가 prefix 인 comment 는
  자동 OK (의도 명시).
- *그러나* 전체 comment 중 sentinel escape ≥80% = 의심 fail (escape 만 사용 우회).
- comment 수가 적은 (< 5) 경우 — 검사 skip (small codebase).

격언:
    Ousterhout: "Comments augment the code by providing information at a
    different level of detail. ... Some comments provide information that is
    *lower-level* than the code (precision); other comments provide
    *higher-level* information (intuition, why)."

사용:
    python comment_intent_check.py \\
        --code-root <submission>/src/ \\
        --max-paraphrase-ratio 0.5 \\
        --max-escape-ratio 0.8

Exit codes:
    0 — paraphrase 비율 ≤ τ + escape ratio ≤ τ
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


COMMENT_RE = re.compile(r'^(\s*)#\s*(.+?)\s*$')
WHY_PREFIX_RE = re.compile(
    r'^(?:why|이유|why:)\s*[:：]?\s*',
    re.IGNORECASE,
)


TOKEN_RE = re.compile(r'[A-Za-z가-힣]{3,}')

# Python keyword + 자주 쓰이는 token — comment-vs-code overlap 카운트에서 제외.
STOPWORDS = {
    'def', 'class', 'self', 'return', 'import', 'from', 'as', 'with',
    'for', 'while', 'if', 'else', 'elif', 'try', 'except', 'pass',
    'lambda', 'yield', 'and', 'or', 'not', 'true', 'false', 'none',
    'the', 'and', 'for', 'with', 'this', 'that', 'are', 'has', 'have',
}


def _tokens(s: str) -> set[str]:
    raw = (t.lower() for t in TOKEN_RE.findall(s or ''))
    return {t for t in raw if t not in STOPWORDS and len(t) >= 3}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def analyze_file(path: Path) -> dict:
    """파일 단위 comment-vs-next-code overlap 분석."""
    try:
        body = path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return {
            'path': str(path), 'comment_count': 0, 'paraphrase_count': 0,
            'escape_count': 0, 'paraphrase_examples': [],
        }

    lines = body.splitlines()
    comment_count = 0
    paraphrase_count = 0
    escape_count = 0
    paraphrase_examples = []

    for i, line in enumerate(lines):
        m = COMMENT_RE.match(line)
        if not m:
            continue
        # docstring fragments 등 (이미 strip 됐어야 하지만 안전)
        text = m.group(2)
        if text.startswith('!') or text.startswith('-'):
            # shebang / dash separator skip
            continue
        comment_count += 1

        # sentinel escape
        if WHY_PREFIX_RE.match(text):
            escape_count += 1
            continue

        # 다음 코드 줄 (skip blank / next comment)
        next_code = None
        for j in range(i + 1, min(i + 6, len(lines))):
            cand = lines[j].strip()
            if not cand:
                continue
            if cand.startswith('#'):
                continue
            next_code = cand
            break

        if next_code is None:
            continue

        com_t = _tokens(text)
        code_t = _tokens(next_code)
        if not com_t or not code_t:
            continue

        ov = jaccard(com_t, code_t)
        if ov >= 0.5:
            paraphrase_count += 1
            if len(paraphrase_examples) < 5:
                paraphrase_examples.append({
                    'lineno': i + 1,
                    'comment': text[:60],
                    'code': next_code[:60],
                    'overlap': round(ov, 2),
                })

    return {
        'path': str(path),
        'comment_count': comment_count,
        'paraphrase_count': paraphrase_count,
        'escape_count': escape_count,
        'paraphrase_examples': paraphrase_examples,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--code-root', type=Path, default=None)
    parser.add_argument('--max-paraphrase-ratio', type=float, default=0.5,
                        help='paraphrase / total comment 비율 상한')
    parser.add_argument('--max-escape-ratio', type=float, default=0.8,
                        help='# why: sentinel / total comment 비율 상한 — 우회 차단')
    parser.add_argument('--min-comments-for-check', type=int, default=5,
                        help='comment 수가 이 미만이면 검사 skip (small codebase)')
    parser.add_argument('--ignore-tests', action='store_true', default=True)
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.code_root is None:
        parser.error('--code-root required when not --self-test')

    files = sorted(args.code_root.rglob('*.py'))
    if args.ignore_tests:
        files = [
            f for f in files
            if 'tests' not in f.parts
            and not f.name.startswith('test_')
            and not f.name.endswith('_test.py')
            and not f.name.startswith('conftest')
        ]
    if not files:
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': [f'no .py modules found in {args.code_root}']}
        _emit(report, args.json_out)
        print(f'FAIL: {args.code_root} 에 모듈 0', file=sys.stderr)
        return 1

    results = [analyze_file(f) for f in files]
    total_comments = sum(r['comment_count'] for r in results)
    total_paraphrase = sum(r['paraphrase_count'] for r in results)
    total_escape = sum(r['escape_count'] for r in results)

    if total_comments < args.min_comments_for_check:
        report = {'schema_version': SCHEMA_VERSION, 'pass': True,
                  'note': f'total comments {total_comments} < min '
                          f'{args.min_comments_for_check}, skipped',
                  'total_comments': total_comments}
        _emit(report, args.json_out)
        print(f'PASS: comment-intent skipped (small codebase, comments={total_comments})')
        return 0

    paraphrase_ratio = total_paraphrase / total_comments
    escape_ratio = total_escape / total_comments

    failures: list[str] = []

    if paraphrase_ratio > args.max_paraphrase_ratio:
        failures.append(
            f'paraphrase ratio {paraphrase_ratio:.3f} > max '
            f'{args.max_paraphrase_ratio} '
            f'({total_paraphrase}/{total_comments} comments)'
        )

    if escape_ratio > args.max_escape_ratio:
        failures.append(
            f'sentinel escape ratio {escape_ratio:.3f} > max '
            f'{args.max_escape_ratio} — escape only 의심 '
            f'({total_escape}/{total_comments} comments)'
        )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'total_comments': total_comments,
        'paraphrase_count': total_paraphrase,
        'paraphrase_ratio': round(paraphrase_ratio, 3),
        'escape_count': total_escape,
        'escape_ratio': round(escape_ratio, 3),
        'failures': failures,
        'examples': [r for r in results if r['paraphrase_examples']][:5],
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: comment-intent ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: comment-intent '
        f'(comments={total_comments} paraphrase_ratio={paraphrase_ratio:.3f})'
    )
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    paraphrase_src = '''# Calculate total quantity by summing entries
total_quantity = sum(entries)

# why: edge case for empty input data
if not data:
    return None

# Compute average rating from feedback values
average_rating = compute_average(feedback_values)
'''
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'sample.py'
        p.write_text(paraphrase_src, encoding='utf-8')
        r = analyze_file(p)
        assert r['comment_count'] == 3, f'expected 3, got {r["comment_count"]}'
        assert r['escape_count'] == 1, f'escape expected 1, got {r["escape_count"]}'
        # 두 paraphrase comment 가 코드 paraphrase 이므로 ≥1
        assert r['paraphrase_count'] >= 1, (
            f'paraphrase ≥ 1 expected, got {r["paraphrase_count"]} '
            f'(examples: {r["paraphrase_examples"]})'
        )

    print(
        f'SELF-TEST PASS — comments={r["comment_count"]} '
        f'paraphrase={r["paraphrase_count"]} escape={r["escape_count"]}'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
