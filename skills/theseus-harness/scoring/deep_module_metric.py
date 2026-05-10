"""deep_module_metric.py — Deep-Module 강제 CLI (sprint-50 PR-D v0.9.50).

본 스크립트는 Ousterhout, *A Philosophy of Software Design*, Ch.4 — *"Modules Should
Be Deep"* 의 enforcement. 각 모듈의 (public interface 줄 수) / (내부 functional 줄 수)
비율이 ≤ τ 의무. 비율이 높으면 *얕은 모듈* (interface ≈ implementation).

Python 한정 1 차 휴리스틱 (다른 언어는 다음 sprint 확장):
- public interface 줄 = `def <name>(...)` (private `_` prefix 제외) + `class <Name>(...)` +
  module-level `__all__` 항목 + module-level 상수 (UPPER_SNAKE) 의 합.
- 내부 functional 줄 = 전체 code line 수 - blank - comment - docstring - import.
- 비율 = interface / functional.

vacuous PASS 차단 (premortem §3-3):
- 모듈 수 = 1 (단일 파일) = automatic fail. *전부 1 파일* 우회 차단.
- 모듈 수 < ⌈sqrt(LOC/100)⌉ = warning (LOC 1000 → 모듈 ≥ 4 권장).

격언:
    Ousterhout — "A deep module is one that has a lot of functionality hidden
    behind a simple interface. A shallow module is one whose interface is
    relatively complex compared to the functionality it provides."

사용:
    python deep_module_metric.py \\
        --code-root <submission>/src/ \\
        --max-ratio 0.4 \\
        --min-modules 2

Exit codes:
    0 — 모든 모듈의 interface/functional 비율 ≤ τ + 모듈 수 충족
    1 — 미달 (얕은 모듈 list / 모듈 수 부족)
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


PUBLIC_DEF_RE = re.compile(r'^\s*def\s+([A-Za-z][A-Za-z0-9_]*)\s*\(', re.MULTILINE)
PUBLIC_CLASS_RE = re.compile(r'^\s*class\s+([A-Z][A-Za-z0-9_]*)\b', re.MULTILINE)
ALL_RE = re.compile(r"^__all__\s*=\s*\[(.*?)\]", re.MULTILINE | re.DOTALL)
CONST_RE = re.compile(r'^([A-Z][A-Z0-9_]{2,})\s*=', re.MULTILINE)
IMPORT_RE = re.compile(r'^\s*(?:from\s+\S+\s+)?import\s+', re.MULTILINE)
COMMENT_RE = re.compile(r'^\s*#', re.MULTILINE)
DOCSTRING_RE = re.compile(r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'', re.MULTILINE)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return ''


def _is_public(name: str) -> bool:
    return not name.startswith('_')


def analyze_module(path: Path) -> dict:
    body = _read(path)
    if not body:
        return {'path': str(path), 'interface_lines': 0, 'functional_lines': 0,
                'ratio': 0.0, 'total_lines': 0}

    public_defs = [n for n in PUBLIC_DEF_RE.findall(body) if _is_public(n)]
    public_classes = [n for n in PUBLIC_CLASS_RE.findall(body) if _is_public(n)]
    all_match = ALL_RE.search(body)
    all_count = 0
    if all_match:
        all_body = all_match.group(1)
        all_count = len([s for s in re.findall(r"'([^']+)'|\"([^\"]+)\"", all_body)
                         if s[0] or s[1]])
    consts = CONST_RE.findall(body)

    interface_lines = (
        len(public_defs) + len(public_classes) + all_count + len(consts)
    )

    body_no_doc = DOCSTRING_RE.sub('', body)
    raw_lines = body_no_doc.splitlines()
    code_lines = 0
    for line in raw_lines:
        s = line.strip()
        if not s:
            continue
        if s.startswith('#'):
            continue
        if IMPORT_RE.match(line):
            continue
        code_lines += 1

    functional_lines = max(0, code_lines - interface_lines)
    ratio = interface_lines / functional_lines if functional_lines else (
        1.0 if interface_lines else 0.0
    )

    return {
        'path': str(path),
        'interface_lines': interface_lines,
        'functional_lines': functional_lines,
        'ratio': round(ratio, 3),
        'total_lines': len(raw_lines),
        'public_defs': len(public_defs),
        'public_classes': len(public_classes),
        'all_count': all_count,
        'consts': len(consts),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--code-root', type=Path, default=None)
    parser.add_argument('--max-ratio', type=float, default=0.4,
                        help='public interface / internal functional 비율 상한 — '
                             '비율 큰 모듈 = 얕은 모듈 = fail')
    parser.add_argument('--min-modules', type=int, default=2,
                        help='모듈 수 (= .py 파일 수) 최소 — vacuous PASS 차단')
    parser.add_argument('--ignore-tests', action='store_true', default=True,
                        help='tests/ 디렉토리 + test_*.py / *_test.py 제외 (default ON)')
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
    files = [f for f in files if f.name != '__init__.py' or f.stat().st_size > 100]

    if not files:
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': [f'no .py modules found in {args.code_root}']}
        _emit(report, args.json_out)
        print(f'FAIL: {args.code_root} 에 모듈 0', file=sys.stderr)
        return 1

    if len(files) < args.min_modules:
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'module_count': len(files),
                  'failures': [f'module count {len(files)} < min {args.min_modules}']}
        _emit(report, args.json_out)
        print(f'FAIL: 모듈 수 {len(files)} < {args.min_modules}', file=sys.stderr)
        return 1

    results = [analyze_module(f) for f in files]
    total_loc = sum(r['total_lines'] for r in results)
    recommended_modules = max(2, math.ceil(math.sqrt(total_loc / 100))) if total_loc else 2

    failures: list[str] = []
    warnings: list[str] = []
    shallow_modules = []
    for r in results:
        if r['functional_lines'] >= 5 and r['ratio'] > args.max_ratio:
            shallow_modules.append((r['path'], r['ratio']))
            failures.append(
                f'{Path(r["path"]).name}: ratio {r["ratio"]} > max {args.max_ratio} '
                f'(interface={r["interface_lines"]} / functional={r["functional_lines"]})'
            )

    if len(files) < recommended_modules:
        warnings.append(
            f'module count {len(files)} < recommended ⌈sqrt(LOC/100)⌉={recommended_modules} '
            f'(LOC={total_loc})'
        )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'module_count': len(files),
        'recommended_modules': recommended_modules,
        'total_loc': total_loc,
        'shallow_modules': [m[0] for m in shallow_modules],
        'per_module': results,
        'failures': failures,
        'warnings': warnings,
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: deep-module ({len(failures)} 얕은 모듈)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: deep-module (modules={len(files)} '
        f'recommended={recommended_modules} loc={total_loc})'
    )
    if warnings:
        for w in warnings:
            print(f'  WARN: {w}')
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    deep_module_src = '''"""Deep module — small interface, lots of internal logic."""

def process(data):
    # internal logic — long
    x = 0
    for d in data:
        x += d * 2
    y = x * x
    z = []
    for i in range(y):
        z.append(i % 7)
    out = sum(z)
    if out > 100:
        out = out % 100
    if out < 0:
        out = -out
    if out == 0:
        out = 1
    return out
'''

    shallow_module_src = '''"""Shallow module — many small public functions."""

def add(a, b): return a + b
def sub(a, b): return a - b
def mul(a, b): return a * b
def div(a, b): return a / b
def mod(a, b): return a % b
def neg(a): return -a
def abs_(a): return a if a >= 0 else -a
def double(a): return a * 2
def triple(a): return a * 3
def quad(a): return a * 4
'''

    import tempfile
    with tempfile.TemporaryDirectory() as d:
        deep_p = Path(d) / 'deep.py'
        shallow_p = Path(d) / 'shallow.py'
        deep_p.write_text(deep_module_src, encoding='utf-8')
        shallow_p.write_text(shallow_module_src, encoding='utf-8')

        deep_r = analyze_module(deep_p)
        shallow_r = analyze_module(shallow_p)

        assert deep_r['ratio'] < shallow_r['ratio'], (
            f'deep ratio {deep_r["ratio"]} should be < shallow {shallow_r["ratio"]}'
        )
        assert shallow_r['ratio'] > 0.4, (
            f'shallow ratio {shallow_r["ratio"]} should be > 0.4'
        )

    print(
        f'SELF-TEST PASS — deep ratio={deep_r["ratio"]} '
        f'shallow ratio={shallow_r["ratio"]}'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
