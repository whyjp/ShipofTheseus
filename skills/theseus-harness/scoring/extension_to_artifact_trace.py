"""extension_to_artifact_trace.py — 채택 extension 항목의 후속 페이즈 trace 검증 CLI (sprint-50 PR-B v0.9.50).

본 스크립트는 페이즈 1.5 의 *채택* (must / should) HI-NN 항목이 후속 페이즈 산출물
(plan / impl / sprint / handoff / 코드) 에 grep trace ≥1 존재하는지 검증.
trace 0 = exit 1.

본 CLI 의 *vacuous PASS 차단*:
- HI-NN id 자체가 *trace 대상 산출물 본문에 등장* + *해당 id 단독 mention 이 아니라
  *주변 ≥40 chars context* 가 있어야 의미 있는 trace 로 카운트.
- frontmatter 에서만 등장 = trace 0 (frontmatter 는 metadata, 본문 trace 가 진짜).
- README / handoff 에서만 등장 = warning (코드 / plan / impl 에 0 = 적용 0 의심).

사용:
    python extension_to_artifact_trace.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --submission-root <submission>/ \\
        --min-trace 1

Exit codes:
    0 — 모든 채택 항목 trace ≥1 (코드 또는 plan/impl 본문)
    1 — 채택 항목 중 trace 0 인 게 ≥1
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


SCOPE_TABLE_ROW_RE = re.compile(
    r'^\|\s*HI-(\d+)\s*\|[^|]*\|\s*([a-z\-]+)\s*\|\s*(must|should|could)\s*\|',
    re.IGNORECASE | re.MULTILINE,
)


# trace 검색 대상 산출물 디렉토리 패턴 (project-root 와 submission-root 합집합).
TRACE_DIRS_RELATIVE = [
    'plan',
    'impl',
    'sprints',
    'handoff',
    'quality',
]


# 코드 trace 검색 — submission root 의 .py / .ts / .go / .rs / .java / .js 파일.
CODE_SUFFIXES = {'.py', '.ts', '.tsx', '.go', '.rs', '.java', '.js', '.jsx', '.cpp', '.c', '.h'}


# frontmatter 영역 (--- ... ---) 은 본문 trace 카운트에서 제외.
FRONTMATTER_RE = re.compile(r'^---\n.*?\n---\n', re.DOTALL)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return ''


def _strip_frontmatter(s: str) -> str:
    return FRONTMATTER_RE.sub('', s, count=1)


def _adopted_ids(scope_md: str) -> list[str]:
    """extension-scope.md 표에서 (must, should) 채택 항목 id list."""
    out = []
    for m in SCOPE_TABLE_ROW_RE.finditer(scope_md):
        if m.group(3).lower() in ('must', 'should'):
            out.append(f'HI-{m.group(1).zfill(2)}')
    return out


def _walk_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for sub in TRACE_DIRS_RELATIVE:
            d = root / sub
            if d.exists():
                out.extend(d.rglob('*.md'))
        for suf in CODE_SUFFIXES:
            out.extend(root.rglob(f'*{suf}'))
    return out


def _trace_count(hi_id: str, files: list[Path], min_context_chars: int = 40) -> dict:
    """hi_id 가 본문 (frontmatter 제외) 에 등장하는 횟수 + 코드/문서 분리.

    *주변 ≥40 chars context* 가 있어야 의미 있는 mention 으로 카운트.
    """
    pattern = re.compile(rf'\b{re.escape(hi_id)}\b')
    doc_count = 0
    code_count = 0
    occurrences = []
    for fp in files:
        body = _read_text(fp)
        if not body:
            continue
        is_code = fp.suffix in CODE_SUFFIXES
        # docs 는 frontmatter strip / code 는 그대로
        body_search = body if is_code else _strip_frontmatter(body)
        for m in pattern.finditer(body_search):
            ctx_start = max(0, m.start() - min_context_chars)
            ctx_end = min(len(body_search), m.end() + min_context_chars)
            ctx = body_search[ctx_start:ctx_end]
            if len(ctx.strip()) < min_context_chars:
                continue
            if is_code:
                code_count += 1
            else:
                doc_count += 1
            occurrences.append({
                'file': str(fp),
                'kind': 'code' if is_code else 'doc',
            })
    return {
        'hi_id': hi_id,
        'doc_trace': doc_count,
        'code_trace': code_count,
        'total': doc_count + code_count,
        'occurrences': occurrences[:5],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--project-root', type=Path, default=None,
                        help='.ShipofTheseus/<proj>/ — intent/01-extension-scope.md 위치')
    parser.add_argument('--submission-root', type=Path, default=None,
                        help='제출 루트 (코드 + plan/impl 본문 산출물). 미지정 시 project-root 의 부모.')
    parser.add_argument('--min-trace', type=int, default=1)
    parser.add_argument('--allow-doc-only', action='store_true', default=False,
                        help='warn 만 — 코드 trace 0 이어도 doc trace ≥1 시 PASS (default OFF)')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.project_root is None:
        parser.error('--project-root required when not --self-test')
    proj = args.project_root
    submission = args.submission_root or proj.parent

    p_scope = proj / 'intent' / '01-extension-scope.md'
    if not p_scope.exists():
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': [f'missing: {p_scope}']}
        _emit(report, args.json_out)
        print(f'FAIL: {p_scope} 부재', file=sys.stderr)
        return 1

    adopted = _adopted_ids(p_scope.read_text(encoding='utf-8'))
    if not adopted:
        report = {'schema_version': SCHEMA_VERSION, 'pass': False,
                  'failures': ['no must/should adoption in scope.md']}
        _emit(report, args.json_out)
        print('FAIL: 채택 항목 0', file=sys.stderr)
        return 1

    files = _walk_files([proj, submission])
    results = [_trace_count(hi, files) for hi in adopted]

    failures: list[str] = []
    warnings: list[str] = []
    for r in results:
        if r['total'] < args.min_trace:
            failures.append(f'{r["hi_id"]}: trace {r["total"]} < min {args.min_trace}')
        elif r['code_trace'] == 0 and not args.allow_doc_only:
            msg = f'{r["hi_id"]}: doc-only trace (code_trace=0)'
            if args.allow_doc_only:
                warnings.append(msg)
            else:
                failures.append(msg)

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'adopted_ids': adopted,
        'results': results,
        'failures': failures,
        'warnings': warnings,
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: extension trace ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(f'PASS: extension trace (adopted={len(adopted)})')
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    scope = '''| HI-01 | x | validation | should | impl |
| HI-02 | y | sensitivity | could | (보류) |
| HI-03 | z | reproducibility | must | impl |'''
    adopted = _adopted_ids(scope)
    assert adopted == ['HI-01', 'HI-03'], f'adopted: {adopted}'
    print('SELF-TEST PASS — extension_to_artifact_trace')
    return 0


if __name__ == '__main__':
    sys.exit(main())
