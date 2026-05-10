"""placeholder_grep.py — Placeholder sentinel detector CLI (sprint-51 PR-D v0.9.51).

본 스크립트는 산출물 본문 / frontmatter / YAML / JSON 에서 *placeholder sentinel*
catalog 를 grep. 도메인 무관, 모든 cold session 적용.

surrender_phrase_grep.py 의 sister CLI — *agent 자백 어휘* 와 *placeholder 미채움*
은 같은 클래스의 회피 패턴.

증거 회피 사례 (g4-v4 96 회차 reviewer 약점):
- token_usage.json 의 모든 numeric field = `null` + token_count_method = "unknown"
- submission.yaml 의 intervention.category = "unrecorded"
- 본 CLI 가 *벤치 무관* 으로 위 패턴 모두 catch.

Sentinel catalog (도메인 무관):
- 명시적 placeholder: TBD / TODO / FIXME / XXX / placeholder / pending / unrecorded
- 알수없음 표기: unknown / N/A / n/a / undefined / undetermined / not specified
- 빈 값: null / None / "" (단, prompt-meta 의 output_schemas field 인 경우만)
- ???? / ??? / <insert> / <replace> / <fill> 류 angle bracket placeholder

vacuous PASS 차단:
- 코멘트/문서 본문에 *legitimate* "TODO" 사용 (예: 다음 sprint 의제) → escape
  comment `# placeholder-ok:` prefix 또는 frontmatter 의 명시 ack.
- escape 비율 ≥ 50% = 의심 fail (escape 만 사용 우회 차단).

prompt-meta 입력 옵션 (--prompt-meta-file):
- `output_schemas` 의 모든 field → null/missing 검사 *target*. (필드별 must-be-non-null)
- 즉 prompt 가 직접 명시한 schema field 가 산출물 에서 placeholder/null 이면 fail.
- 도메인 무관 — prompt 가 어떤 도메인이든 *prompt 가 명시한 schema* 가 입력.

사용:
    python placeholder_grep.py \\
        --target-root <project-or-submission> \\
        --prompt-meta-file <path-to-00-prompt-meta.json> \\
        --max-violation-count 0

Exit codes:
    0 — 모든 sentinel 매치가 escape 되어 있음 + prompt-meta schema fields 모두 non-null
    1 — sentinel violation 잔존 / schema field null
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


SCHEMA_VERSION = "0.9.51"


# Sentinel catalog (도메인 무관, 일반 placeholder 패턴).
#
# 전략 — *value context* 만 매치 (key 또는 prose 본문 에서의 합법 사용 제외):
# - YAML/JSON value: `field: <SENTINEL>` 또는 `"field": "<SENTINEL>"`
# - bare placeholder marker: TBD / FIXME / XXX (코드 코멘트 외 본문 등장 시)
# - bracket placeholder: <insert>, <fill>, ???
#
# pending 은 phase state machine value (status: pending) 등 legit 사용 다수 →
# 일반 SENTINEL 카탈로그에서 *제외*. 필요 시 prompt-meta 의 default_warnings
# 에 등록된 경우만 grep (도메인 의존 escape).
SENTINEL_PATTERNS = [
    # 명시적 placeholder marker — 어디든 매치 (의도적)
    (r'\bTBD\b', 'TBD'),
    (r'\bFIXME\b', 'FIXME'),
    (r'\bXXX\b', 'XXX'),
    # value-context 로만 매치 (key / prose 의 단어 사용은 OK)
    (r'(?:^|[:=]\s+|"\s*:\s*"?)(placeholder)\b', 'placeholder_value'),
    (r'(?:^|[:=]\s+|"\s*:\s*"?)(unrecorded)\b', 'unrecorded_value'),
    (r'(?:^|[:=]\s+|"\s*:\s*"?)(undetermined)\b', 'undetermined_value'),
    (r'(?:^|[:=]\s+|"\s*:\s*"?)(undefined)\b(?![()])', 'undefined_value'),  # JS/code "undefined()" 제외
    (r'(?:^|[:=]\s+|"\s*:\s*"?)(unknown)\b', 'unknown_value'),
    # NOTE: TODO 는 코드 base 의 normal annotation — 전체 카운트에서 제외 (--include-todo flag 로 opt-in)
    # NOTE: pending 은 phase state value 에 legit 사용 다수 — 제외
    # 알수없음 표기
    (r'\bN/A\b|\bn/a\b', 'na'),
    (r'\bnot\s+specified\b', 'not_specified'),
    # angle bracket placeholder
    (r'<insert>', 'insert'),
    (r'<replace>', 'replace'),
    (r'<fill>', 'fill'),
    (r'<your\s+\w+>', 'your_x'),
    (r'(?<![?\w])\?{3,}(?![?\w])', 'qmark3'),  # ??? 단독, ???? 같은 5+개도 catch
]


# TODO 패턴 (opt-in via --include-todo)
TODO_PATTERN = (r'\bTODO\b', 'TODO')


# escape sentinel — line 내 또는 직전/직후 line 에 prefix 있으면 OK
ESCAPE_PREFIX_RE = re.compile(
    r'(?:#|//|/\*)\s*(?:placeholder-ok|sentinel-ok|legitimate-placeholder)\s*[:.]',
    re.IGNORECASE,
)


# 산출물 file extension catalog
TARGET_SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.txt', '.py', '.ts', '.go', '.rs',
                   '.js', '.tsx', '.jsx', '.cpp', '.c', '.h', '.java'}


# 제외 path 패턴 — 본 CLI 자체 / 테스트 fixture / venv / vendored library 등
EXCLUDE_PATH_PATTERNS = [
    r'\.git[/\\]',
    r'__pycache__',
    r'node_modules',
    r'venv[/\\]',
    r'\.venv[/\\]',
    r'placeholder_grep\.py$',  # 본 CLI 자기 자신 (sentinel catalog 정의 자체)
    r'surrender_phrase_grep\.py$',  # sister CLI
    # vendored libraries (sprint-35 prebuilt shell + 3rd-party UMD)
    r'\.min\.js$',  # minified JS library
    r'mermaid\.[a-z\.]*\.js$',
    r'marked\.[a-z\.]*\.js$',
    # prebuilt shell 의 templates / viewer-runtime / assets js (cold session 산출 X)
    r'(?:^|[/\\])templates[/\\]',
    r'(?:^|[/\\])viewer-runtime[/\\]',
    r'(?:^|[/\\])assets[/\\][^/\\]+\.(?:js|css)$',  # submission/assets/*.js, *.css
    r'(?:^|[/\\])dist[/\\]',
]


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return ''


def _is_excluded(path: Path) -> bool:
    s = str(path).replace('\\', '/')
    return any(re.search(p, s) for p in EXCLUDE_PATH_PATTERNS)


def grep_sentinels(body: str, patterns: list[tuple[str, str]] | None = None) -> list[dict]:
    """본문에서 sentinel 매치 list — escape 표기 제외."""
    if patterns is None:
        patterns = SENTINEL_PATTERNS
    lines = body.splitlines()
    matches = []
    for lineno, line in enumerate(lines, start=1):
        # escape line 자체는 skip
        if ESCAPE_PREFIX_RE.search(line):
            continue
        # 직전/직후 line 에 escape 있으면 본 line 도 escape (1-line context)
        prev_esc = lineno >= 2 and ESCAPE_PREFIX_RE.search(lines[lineno - 2])
        next_esc = lineno < len(lines) and ESCAPE_PREFIX_RE.search(lines[lineno])
        for pattern, kind in patterns:
            for m in re.finditer(pattern, line, re.IGNORECASE):
                if prev_esc or next_esc:
                    matches.append({
                        'lineno': lineno,
                        'kind': kind,
                        'matched': m.group(0),
                        'line': line.strip()[:120],
                        'escaped': True,
                    })
                else:
                    matches.append({
                        'lineno': lineno,
                        'kind': kind,
                        'matched': m.group(0),
                        'line': line.strip()[:120],
                        'escaped': False,
                    })
    return matches


def check_schema_fields(submission_root: Path,
                        prompt_meta: dict) -> list[dict]:
    """prompt-meta 의 output_schemas field 가 산출물에서 *non-null* 인지 검사."""
    violations = []
    for sch in prompt_meta.get('output_schemas', []):
        fn = sch.get('file', '')
        fields = sch.get('fields', [])
        if not fn or not fields:
            continue

        # submission_root 에서 file 검색
        candidates = list(submission_root.rglob(fn))
        if not candidates:
            violations.append({
                'kind': 'missing_file',
                'file': fn,
                'detail': f'{fn} not found in {submission_root}',
            })
            continue

        for fp in candidates[:3]:  # 후보 ≤3 제한
            body = _read(fp)
            if not body:
                continue
            # JSON 인 경우 — null / empty 직접 검사
            if fn.endswith('.json'):
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    violations.append({
                        'kind': 'invalid_json',
                        'file': str(fp),
                        'detail': 'JSON parse failed',
                    })
                    continue
                _check_null_recursive(data, fields, str(fp), violations)
            elif fn.endswith(('.yaml', '.yml')):
                # YAML — null 표기 검사 (간이)
                for field in fields:
                    pattern = rf'^\s*{re.escape(field)}\s*:\s*(null|~|""|\'\')\s*$'
                    if re.search(pattern, body, re.MULTILINE):
                        violations.append({
                            'kind': 'null_field',
                            'file': str(fp),
                            'field': field,
                            'detail': f'{field}: null/empty in YAML',
                        })
            elif fn.endswith('.csv'):
                # CSV — header 줄에 모든 field 존재 + 본문 row 가 빈 cell 0
                first_line = body.split('\n', 1)[0] if body else ''
                missing = [f for f in fields
                           if f not in first_line.split(',')]
                if missing:
                    violations.append({
                        'kind': 'missing_csv_columns',
                        'file': str(fp),
                        'detail': f'missing columns: {missing}',
                    })
    return violations


def _check_null_recursive(data, fields: list[str], file_path: str,
                          violations: list[dict]) -> None:
    """JSON 객체 재귀 — `fields` 의 key 가 null 인지 검사."""
    if isinstance(data, dict):
        for k, v in data.items():
            if k in fields and v is None:
                violations.append({
                    'kind': 'null_field',
                    'file': file_path,
                    'field': k,
                    'detail': f'{k}: null in JSON',
                })
            _check_null_recursive(v, fields, file_path, violations)
    elif isinstance(data, list):
        for item in data:
            _check_null_recursive(item, fields, file_path, violations)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--target-root', type=Path, default=None,
                        help='산출물 root (project-root 또는 submission-root)')
    parser.add_argument('--prompt-meta-file', type=Path, default=None,
                        help='prompt_meta_extractor 산출물 (intent/00-prompt-meta.json)')
    parser.add_argument('--max-violation-count', type=int, default=0,
                        help='non-escape sentinel 매치 + null field 합계 상한')
    parser.add_argument('--max-escape-ratio', type=float, default=0.5,
                        help='escape 비율 상한 (escape 만 사용 우회 차단)')
    parser.add_argument('--include-todo', action='store_true', default=False,
                        help='TODO 도 sentinel 로 검사 (default OFF — 코드 base 의 normal annotation 으로 false positive 多)')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.target_root is None:
        parser.error('--target-root required when not --self-test')

    # opt-in TODO 추가
    active_patterns = list(SENTINEL_PATTERNS)
    if args.include_todo:
        active_patterns.append(TODO_PATTERN)

    # 1) sentinel grep — 모든 산출물 검사
    files = []
    for fp in args.target_root.rglob('*'):
        if not fp.is_file():
            continue
        if fp.suffix not in TARGET_SUFFIXES:
            continue
        if _is_excluded(fp):
            continue
        files.append(fp)

    all_matches = []
    for fp in files:
        body = _read(fp)
        if not body:
            continue
        matches = grep_sentinels(body, active_patterns)
        for m in matches:
            m['file'] = str(fp)
            all_matches.append(m)

    non_escape = [m for m in all_matches if not m['escaped']]
    escape = [m for m in all_matches if m['escaped']]
    total = len(all_matches)
    escape_ratio = len(escape) / total if total else 0.0

    # 2) prompt-meta schema field null 검사
    schema_violations = []
    if args.prompt_meta_file and args.prompt_meta_file.exists():
        try:
            meta = json.loads(args.prompt_meta_file.read_text(encoding='utf-8'))
            schema_violations = check_schema_fields(args.target_root, meta)
        except json.JSONDecodeError as e:
            schema_violations.append({
                'kind': 'meta_parse_failed',
                'detail': str(e),
            })

    failures: list[str] = []

    if len(non_escape) > args.max_violation_count:
        failures.append(
            f'sentinel non-escape violations {len(non_escape)} > max '
            f'{args.max_violation_count}'
        )

    if escape_ratio > args.max_escape_ratio:
        failures.append(
            f'escape ratio {escape_ratio:.3f} > max {args.max_escape_ratio} '
            f'(escape={len(escape)}/{total})'
        )

    if schema_violations:
        failures.append(
            f'prompt-meta schema field violations: {len(schema_violations)}'
        )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'total_files_scanned': len(files),
        'sentinel_matches': len(all_matches),
        'non_escape_count': len(non_escape),
        'escape_count': len(escape),
        'escape_ratio': round(escape_ratio, 3),
        'schema_violations': schema_violations[:20],
        'top_non_escape': non_escape[:10],
        'failures': failures,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                 encoding='utf-8')

    if failures:
        print(f'FAIL: placeholder_grep ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        for m in non_escape[:5]:
            print(f'  - {m["file"]}:{m["lineno"]} [{m["kind"]}] {m["matched"]}',
                  file=sys.stderr)
        for v in schema_violations[:5]:
            print(f'  - {v}', file=sys.stderr)
        return 1
    print(
        f'PASS: placeholder_grep '
        f'(files={len(files)} sentinels={len(all_matches)} '
        f'non_escape={len(non_escape)} schema_viols={len(schema_violations)})'
    )
    return 0


def _self_test() -> int:
    bad_text = '''# Sample doc

field_a: TBD
field_b: unknown
intervention.category: unrecorded
some_value: ???
notes: undetermined
'''
    matches = grep_sentinels(bad_text)
    non_esc = [m for m in matches if not m['escaped']]
    assert len(non_esc) >= 4, f'expected ≥4 non-escape, got {len(non_esc)}: {matches}'

    good_text = '''# Sample doc

# placeholder-ok: 다음 sprint 의제 — TBD 는 의도적
field_a: TBD

field_b: actual_value
'''
    matches = grep_sentinels(good_text)
    non_esc = [m for m in matches if not m['escaped']]
    assert len(non_esc) == 0, f'expected 0 non-escape, got {len(non_esc)}: {matches}'

    # phase status legit 사용 — pending/Pending 은 sentinel 카탈로그에서 제거됐으므로 매치 안 됨
    legit_phase_text = '''{
  "phase": "06",
  "status": "pending",
  "state": "Pending"
}'''
    matches = grep_sentinels(legit_phase_text)
    pending_matches = [m for m in matches if 'pending' in m['matched'].lower()]
    assert not pending_matches, f'pending should NOT be sentinel: {pending_matches}'

    # JSON null field 검사
    sample_meta = {
        'output_schemas': [{
            'file': 'token_usage.json',
            'fields': ['total_tokens', 'input_tokens', 'output_tokens'],
        }],
    }
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        sub = Path(d)
        (sub / 'token_usage.json').write_text(
            json.dumps({
                'total_tokens': None,
                'input_tokens': None,
                'output_tokens': 12345,
                'token_count_method': 'unknown',
            }), encoding='utf-8')
        viols = check_schema_fields(sub, sample_meta)
        # total_tokens, input_tokens null = 2 violations
        null_viols = [v for v in viols if v['kind'] == 'null_field']
        assert len(null_viols) == 2, f'expected 2 null violations, got {viols}'

    print('SELF-TEST PASS — placeholder_grep '
          f'(grep + escape + schema null 모두 검증)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
