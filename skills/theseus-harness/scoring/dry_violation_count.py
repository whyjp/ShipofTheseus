"""dry_violation_count.py — DRY (Don't Repeat Yourself) 휴리스틱 CLI (sprint-50 PR-D v0.9.50).

본 스크립트는 Hunt & Thomas, *The Pragmatic Programmer*, Tip 11 — *"DRY"* 의
enforcement. 코드 token n-gram (n=8) 중복 발견. 동일 n-gram 이 ≥ k 번 등장 = violation.
violation 비율 ≥ τ = exit 1.

token = code line 의 normalize 형태 (whitespace 정규화 + 변수명 placeholder X 보존
— 단순 token list 비교).

vacuous PASS 차단:
- frame imports / decorators / class header / `if __name__` 같은 *boilerplate* n-gram
  은 catalog 로 제외 (`--no-boilerplate-skip` 으로 비활성화 가능).
- 너무 짧은 모듈 (token 수 < 50) 은 검사 skip — n-gram 부족.

격언:
    Hunt & Thomas, Pragmatic Programmer Tip 11 — "Every piece of knowledge must
    have a single, unambiguous, authoritative representation within a system."

사용:
    python dry_violation_count.py \\
        --code-root <submission>/src/ \\
        --n-gram 8 \\
        --max-violation-ratio 0.05

Exit codes:
    0 — violation 비율 ≤ τ
    1 — 비율 초과 (top-N 중복 n-gram + 위치)
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.50"


# Boilerplate n-gram 시드 (n-gram 안에 이 패턴이 들어 있으면 제외)
BOILERPLATE_PATTERNS = [
    r'^from\s+\S+\s+import\s',
    r'^import\s+\S+',
    r'^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:',
    r'^def\s+__init__\s*\(',
    r'^def\s+__repr__\s*\(',
    r'^def\s+__str__\s*\(',
    r'^@\w+',
    r'^class\s+\w+',
    r'^\s*pass\s*$',
    r'^\s*return\s*$',
]
BOILERPLATE_RE = [re.compile(p) for p in BOILERPLATE_PATTERNS]


# token = code line normalize. comment / blank 제외.
def _normalize_line(line: str) -> str | None:
    s = line.strip()
    if not s or s.startswith('#'):
        return None
    s = re.sub(r'\s+', ' ', s)
    return s


def _is_boilerplate(line: str) -> bool:
    return any(p.match(line) for p in BOILERPLATE_RE)


def extract_ngrams(lines: list[str], n: int) -> list[tuple[str, ...]]:
    if len(lines) < n:
        return []
    grams = []
    for i in range(len(lines) - n + 1):
        gram = tuple(lines[i:i + n])
        if any(_is_boilerplate(g) for g in gram):
            continue
        grams.append(gram)
    return grams


def build_report(
    code_root: Path,
    n_gram: int = 8,
    min_repeat: int = 2,
    max_violation_ratio: float = 0.05,
    no_boilerplate_skip: bool = False,
    ignore_tests: bool = True,
    top_n: int = 10,
) -> dict:
    """code_root 스캔 → DRY 리포트(raw counts + ratio). verdict 는 안 낸다.

    main()(CLI, 하위호환 유지)과 producers/measure_dry_violation.py(evidence 조립기)가
    공유하는 단일 계산 경로. `module_count`/`scanned_line_count`/`total_ngrams`/
    `violation_count` 는 모든 분기에 present(0 포함) — 호출자가 string-match 없이
    분기(모듈 0 / 소규모 skip / 정상측정)를 구분하도록.
    """
    files = sorted(code_root.rglob('*.py'))
    if ignore_tests:
        files = [
            f for f in files
            if 'tests' not in f.parts
            and not f.name.startswith('test_')
            and not f.name.endswith('_test.py')
            and not f.name.startswith('conftest')
        ]
    if not files:
        return {
            'schema_version': SCHEMA_VERSION, 'pass': False, 'module_count': 0,
            'scanned_line_count': 0, 'total_ngrams': 0, 'violation_count': 0,
            'failures': [f'no .py modules found in {code_root}'],
        }

    if no_boilerplate_skip:
        BOILERPLATE_RE.clear()

    all_lines: list[tuple[str, str, int]] = []  # (line, file, lineno)
    for fp in files:
        try:
            body = fp.read_text(encoding='utf-8', errors='replace')
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            continue
        for lineno, line in enumerate(body.splitlines(), start=1):
            normalized = _normalize_line(line)
            if normalized is None:
                continue
            all_lines.append((normalized, str(fp), lineno))

    if len(all_lines) < n_gram + 10:
        return {
            'schema_version': SCHEMA_VERSION, 'pass': True,
            'note': 'token count < n-gram + 10, skipped',
            'module_count': len(files), 'scanned_line_count': len(all_lines),
            'total_ngrams': 0, 'violation_count': 0,
        }

    line_strs = [l[0] for l in all_lines]
    grams = extract_ngrams(line_strs, n_gram)

    counter = Counter(grams)
    violations = [(gram, count) for gram, count in counter.most_common()
                  if count >= min_repeat]

    total_grams = len(grams)
    violation_count = sum(c for _g, c in violations) - len(violations)  # 첫 등장 제외
    ratio = violation_count / total_grams if total_grams else 0.0

    failures: list[str] = []
    if ratio > max_violation_ratio:
        failures.append(
            f'DRY violation ratio {ratio:.4f} > max {max_violation_ratio} '
            f'(violations={violation_count}/{total_grams})'
        )

    return {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'module_count': len(files),
        'scanned_line_count': len(all_lines),
        'n_gram': n_gram,
        'total_ngrams': total_grams,
        'violation_count': violation_count,
        'violation_ratio': round(ratio, 4),
        'top_violations': [
            {'count': c, 'preview': ' / '.join(g[:3]) + '...'}
            for g, c in violations[:top_n]
        ],
        'failures': failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--code-root', type=Path, default=None)
    parser.add_argument('--n-gram', type=int, default=8)
    parser.add_argument('--min-repeat', type=int, default=2,
                        help='same n-gram 등장 ≥ k 번 = violation (default 2)')
    parser.add_argument('--max-violation-ratio', type=float, default=0.05,
                        help='violation n-gram 수 / 전체 n-gram 수 상한')
    parser.add_argument('--no-boilerplate-skip', action='store_true', default=False)
    parser.add_argument('--ignore-tests', action='store_true', default=True)
    parser.add_argument('--top-n', type=int, default=10,
                        help='리포트 상위 N 위반 표시')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.code_root is None:
        parser.error('--code-root required when not --self-test')

    report = build_report(
        args.code_root,
        n_gram=args.n_gram,
        min_repeat=args.min_repeat,
        max_violation_ratio=args.max_violation_ratio,
        no_boilerplate_skip=args.no_boilerplate_skip,
        ignore_tests=args.ignore_tests,
        top_n=args.top_n,
    )
    _emit(report, args.json_out)

    if report['module_count'] == 0:
        print(f'FAIL: {args.code_root} 에 모듈 0', file=sys.stderr)
        return 1
    if report.get('note') == 'token count < n-gram + 10, skipped':
        print(f'PASS: dry skipped (small codebase, lines={report["scanned_line_count"]})')
        return 0
    if not report['pass']:
        print(f'FAIL: dry violation ({len(report["failures"])} fail)', file=sys.stderr)
        for f in report['failures']:
            print(f'  - {f}', file=sys.stderr)
        for v in report.get('top_violations', []):
            print(f'  - x{v["count"]}: {v["preview"]}', file=sys.stderr)
        return 1
    print(f'PASS: dry (ratio={report["violation_ratio"]:.4f} grams={report["total_ngrams"]})')
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    no_dup = ['line one', 'line two', 'line three', 'line four',
              'line five', 'line six', 'line seven', 'line eight',
              'line nine', 'line ten', 'line eleven', 'line twelve']
    grams_no = extract_ngrams(no_dup, 4)
    counter = Counter(grams_no)
    assert all(c == 1 for c in counter.values()), 'no_dup should have no repeats'

    dup = no_dup + no_dup
    grams_dup = extract_ngrams(dup, 4)
    counter_dup = Counter(grams_dup)
    assert any(c >= 2 for c in counter_dup.values()), 'dup should detect repeats'

    print('SELF-TEST PASS — dry_violation_count')
    return 0


if __name__ == '__main__':
    sys.exit(main())
