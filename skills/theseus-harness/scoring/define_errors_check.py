"""define_errors_check.py — Define-Errors-Out enforcement CLI (sprint-50 PR-E v0.9.50).

본 스크립트는 Ousterhout, *A Philosophy of Software Design*, Ch.10 —
*"Define Errors Out of Existence"* 의 *역방향* enforcement.

Ousterhout 의 원 권고는 "예외를 줄여 errors-out-of-existence 화" 지만, 본 CLI 는
*반대 시그널* 검출:
- raise 된 예외 종류가 catalog ≥ N (≥1 종류) — 단일 종류만 쓰는 코드 의심
- 각 raise 가 *어딘가에서* handle (try/except 또는 caller catch comment) 됨 —
  정의만 하고 처리 0 = 진짜로 *errors-out-of-existence* 한 것이 아닌, *handle 누락*.

본 CLI 의 vacuous PASS 차단:
- 0 raise = automatic warning ("진짜 errors-out vs implicit propagation 어느 쪽?").
- raise + bare except (`except:` 또는 `except Exception:`) only = vacuous handle 의심 fail
  (Effective Python Item 87 *"Defining a Root Exception"* 정합 — 광역 catch 는 정의 회피).

Python 한정 1 차 (다른 언어 다음 sprint).

격언:
    Ousterhout: "Exceptions are one of the worst sources of complexity in software
    systems." → 따라서 *예외를 정의했다면 반드시 처리하라* (handle 0 인 raise = 잘못).

사용:
    python define_errors_check.py \\
        --code-root <submission>/src/ \\
        --min-exception-types 1 \\
        --require-handle

Exit codes:
    0 — raise 된 예외 catalog 가 모두 어딘가 handle (try/except 또는 sentinel comment)
    1 — handle 0 인 raise 발견 / bare except only / 카탈로그 부족
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


# raise <ExceptionName>(...) 또는 raise <Name> from <source>
RAISE_RE = re.compile(
    r'^\s*raise\s+([A-Z][A-Za-z0-9_]*)\s*(?:\(|from|$)',
    re.MULTILINE,
)

# except <Name>: 또는 except (Name1, Name2): / except Name as e:
EXCEPT_RE = re.compile(
    r'^\s*except\s+([^:]+?)\s*(?:as\s+\w+\s*)?:',
    re.MULTILINE,
)

# bare except: 또는 except Exception:
BARE_EXCEPT_RE = re.compile(
    r'^\s*except\s*(?:Exception\s*)?(?:as\s+\w+\s*)?\s*:',
    re.MULTILINE,
)

# sentinel comment — caller catches 명시 (escape)
CALLER_CATCH_RE = re.compile(
    r'#\s*(?:caller catches?|caller handles?|propagated to|raised to)',
    re.IGNORECASE,
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return ''


def _split_except_clause(clause: str) -> list[str]:
    """except (Name1, Name2): → [Name1, Name2]."""
    s = clause.strip().strip('()')
    out = []
    for part in s.split(','):
        name = part.strip()
        m = re.match(r'([A-Z][A-Za-z0-9_]*)', name)
        if m:
            out.append(m.group(1))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--code-root', type=Path, default=None)
    parser.add_argument('--min-exception-types', type=int, default=1,
                        help='raise 된 예외 종류 catalog ≥ N')
    parser.add_argument('--require-handle', action='store_true', default=True,
                        help='raise 된 모든 예외가 어딘가 handle 의무')
    parser.add_argument('--allow-bare-except', action='store_true', default=False,
                        help='bare except / except Exception only 도 handle 로 카운트 '
                             '(default OFF — Effective Python Item 87 정합)')
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

    raise_catalog = Counter()
    handled_catalog = Counter()
    bare_except_count = 0
    caller_catch_marker = 0
    raise_locations = []

    for fp in files:
        body = _read(fp)
        if not body:
            continue
        for m in RAISE_RE.finditer(body):
            name = m.group(1)
            raise_catalog[name] += 1
            raise_locations.append({'file': str(fp), 'name': name})
        for m in EXCEPT_RE.finditer(body):
            for name in _split_except_clause(m.group(1)):
                handled_catalog[name] += 1
        for _m in BARE_EXCEPT_RE.finditer(body):
            bare_except_count += 1
        for _m in CALLER_CATCH_RE.finditer(body):
            caller_catch_marker += 1

    failures: list[str] = []
    warnings: list[str] = []

    if len(raise_catalog) < args.min_exception_types:
        warnings.append(
            f'exception types catalog {len(raise_catalog)} < min '
            f'{args.min_exception_types} — implicit propagation only?'
        )

    # require-handle: raise 된 각 종류가 handle 또는 sentinel 마커
    handled_set = set(handled_catalog.keys())
    if not args.allow_bare_except:
        # bare except / Exception 광역 catch 는 handle 카운트에서 제외
        handled_set = {n for n in handled_set
                       if n not in ('Exception', 'BaseException')}

    if args.require_handle:
        unhandled = []
        for name in raise_catalog:
            if name not in handled_set and caller_catch_marker == 0:
                unhandled.append(name)
        if unhandled:
            failures.append(
                f'raise 후 handle 0 인 예외 종류: {unhandled} '
                f'(or use `# caller catches` sentinel comment)'
            )

    # bare except only = vacuous handle 의심
    if (bare_except_count > 0 and not handled_set
            and not args.allow_bare_except and raise_catalog):
        failures.append(
            f'except 절 모두 bare/Exception only ({bare_except_count} 회) — '
            f'specific exception type 이 handle 0. (use --allow-bare-except 우회)'
        )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'raise_catalog': dict(raise_catalog),
        'handled_catalog': dict(handled_catalog),
        'bare_except_count': bare_except_count,
        'caller_catch_marker': caller_catch_marker,
        'raise_locations': raise_locations[:20],
        'failures': failures,
        'warnings': warnings,
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: define-errors-out ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    msg = (
        f'PASS: define-errors-out (raised={dict(raise_catalog)} '
        f'handled={list(handled_set)})'
    )
    print(msg)
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
    src = '''
def f():
    raise ValueError("bad")

def g():
    try:
        f()
    except ValueError:
        return 0
    except KeyError:
        return -1

def h():
    raise RuntimeError("unhandled")
'''
    raises = list(RAISE_RE.finditer(src))
    excepts = list(EXCEPT_RE.finditer(src))
    raise_names = [r.group(1) for r in raises]
    handled = []
    for m in excepts:
        handled.extend(_split_except_clause(m.group(1)))
    assert 'ValueError' in raise_names
    assert 'RuntimeError' in raise_names
    assert 'ValueError' in handled
    assert 'KeyError' in handled
    assert 'RuntimeError' not in handled
    print(f'SELF-TEST PASS — raises={raise_names} handled={handled}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
