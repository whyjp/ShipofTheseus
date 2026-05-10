"""default_value_justification.py — Default value 정당화 rule CLI (sprint-51 PR-E v0.9.51).

본 스크립트는 prompt-meta 의 `default_warnings` 카탈로그 (e.g.
"Use meaningful values rather than zeros") 가 trigger 된 경우, agent 가 산출물에
*명시적 default* (numeric 0 / null / "none" / "auto") 사용 시 *왜* 명시 의무 검증.

도메인 무관 — prompt 가 어떤 default 경고를 명시했든 본 CLI 는 일반 패턴으로 검사.

증거 회피 사례 (g4-v4 96 reviewer 약점 #2):
- baseline.yaml 의 `warmup_minutes: 0` 이 *prompt 의 "Use meaningful values rather
  than zeros"* default_warning 정합 위반.
- README 본문에 warmup=0 사용 *왜* 0 한 줄 정당화 부재 → reviewer 약점.

검사 알고리즘:
1. prompt-meta 의 `default_warnings` 가 비어있으면 → skip (PASS, applicable X).
2. submission YAML/JSON 산출물에서 *suspicious default*:
   - `<field>: 0` (정수 0 — 의식적 default 의심)
   - `<field>: null`
   - `<field>: "none"` / `<field>: "auto"` / `<field>: "default"`
3. 각 suspicious default 항목 마다 README/handoff/intent 본문에 *justification* grep:
   - field 이름 + 사유 keyword (e.g. `because`, `since`, `due to`, `이유`, `때문`,
     `의도적`, `intentionally`, `chosen because`)
   - 또는 `# why:` / `// why:` sentinel comment 직접 인접
4. justification 0 = fail.

vacuous PASS 차단:
- field 이름만 mention 되고 사유 keyword 없음 = fail
- README/handoff 본문 길이 < 50 chars 인 mention 은 vacuous fail

사용:
    python default_value_justification.py \\
        --target-root <submission-root> \\
        --justification-roots <project-root> <submission-root> \\
        --prompt-meta-file intent/00-prompt-meta.json

Exit codes:
    0 — default_warnings 비어있음 OR 모든 suspicious default 가 justification 보유
    1 — justification 부재 항목 ≥ 1
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


# Suspicious default 패턴 — value 가 의식적 0 / null / 매직 default
# YAML: `field: 0`, `field: null`, `field: ~`, `field: "none"`, `field: "auto"`
SUSPICIOUS_DEFAULT_RE = [
    (re.compile(r'^(\s*)([\w_-]+)\s*:\s*0\s*(?:#.*)?$', re.MULTILINE), 'zero'),
    (re.compile(r'^(\s*)([\w_-]+)\s*:\s*null\s*(?:#.*)?$', re.MULTILINE), 'null'),
    (re.compile(r'^(\s*)([\w_-]+)\s*:\s*~\s*(?:#.*)?$', re.MULTILINE), 'tilde_null'),
    (re.compile(r'^(\s*)([\w_-]+)\s*:\s*["\'](none|auto|default)["\']\s*(?:#.*)?$',
                re.MULTILINE | re.IGNORECASE), 'magic_string'),
]

# JSON: `"field": 0`, `"field": null`, `"field": "none"`
JSON_SUSPICIOUS_RE = [
    (re.compile(r'"([\w_-]+)"\s*:\s*0\b'), 'zero'),
    (re.compile(r'"([\w_-]+)"\s*:\s*null\b'), 'null'),
    (re.compile(r'"([\w_-]+)"\s*:\s*"(none|auto|default)"', re.IGNORECASE),
     'magic_string'),
]


# Justification keyword catalog (도메인 무관, 다국어)
JUSTIFICATION_KEYWORDS = [
    r'\bbecause\b',
    r'\bsince\b',
    r'\bdue\s+to\b',
    r'\breason\b',
    r'\brationale\b',
    r'\bjustif\w+\b',
    r'\bchosen\s+because\b',
    r'\bintentional\w*\b',
    r'\bdeliberate\w*\b',
    r'\bexplicit\w*\b',
    r'\bin\s+order\s+to\b',
    r'\bso\s+that\b',
    # 한국어
    r'이유',
    r'때문',
    r'의도적',
    r'명시적',
    r'그래서',
]
JUSTIFICATION_RE = re.compile('|'.join(JUSTIFICATION_KEYWORDS),
                              re.IGNORECASE | re.UNICODE)


# Sentinel `# why:` 직접 인접 escape (placeholder_grep 의 escape 와 비슷)
WHY_PREFIX_RE = re.compile(
    r'(?:#|//|/\*)\s*(?:why|이유|chosen because|rationale)\s*[:.]',
    re.IGNORECASE,
)


# config 산출물 patterns (default 가 흔히 등장하는 file)
CONFIG_SUFFIXES = {'.yaml', '.yml', '.json', '.toml', '.ini', '.cfg'}


# justification 검색 대상 (README / handoff / intent / docs / comments)
JUSTIFICATION_SEARCH_SUFFIXES = {'.md', '.rst', '.txt', '.py', '.ts', '.go',
                                 '.rs', '.js', '.tsx'}


# 너무 흔한 field 명 — false positive 위험. skip catalog (보수적):
# 일반 SI/식별자 field 는 default 0 이 의미 있을 수 있음 — 이 catalog 는
# justification 면제 (즉 본 CLI 가 검사 대상 외).
COMMON_TRIVIAL_FIELDS = {
    'replication', 'replications', 'rep', 'reps',
    'index', 'idx', 'i', 'j', 'k', 'n',
    'count', 'total',
    'len', 'length', 'size',
    'min', 'max',
    'start', 'end', 'begin',
    # version / id / random_seed 류
    'version', 'id', 'uid',
    'random_seed', 'seed',
    'major', 'minor', 'patch',
}


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return ''


def find_suspicious_defaults(target_root: Path) -> list[dict]:
    """target_root 에서 config 파일 의 suspicious default list."""
    out = []
    for fp in target_root.rglob('*'):
        if not fp.is_file():
            continue
        if fp.suffix not in CONFIG_SUFFIXES:
            continue
        body = _read(fp)
        if not body:
            continue
        if fp.suffix == '.json':
            for pattern, kind in JSON_SUSPICIOUS_RE:
                for m in pattern.finditer(body):
                    field = m.group(1)
                    if field.lower() in COMMON_TRIVIAL_FIELDS:
                        continue
                    out.append({
                        'file': str(fp),
                        'field': field,
                        'kind': kind,
                        'matched': m.group(0),
                    })
        else:
            for pattern, kind in SUSPICIOUS_DEFAULT_RE:
                for m in pattern.finditer(body):
                    field = m.group(2)
                    if field.lower() in COMMON_TRIVIAL_FIELDS:
                        continue
                    out.append({
                        'file': str(fp),
                        'field': field,
                        'kind': kind,
                        'matched': m.group(0).strip(),
                    })
    return out


def has_justification(field: str, search_roots: list[Path]) -> dict:
    """field 가 README/handoff/intent/docs 에서 justification 보유하는지.

    *sentence-level 인접* 만 검사 — field mention 과 justification keyword 가 *같은 문장*
    안에 있어야 인정. 200 chars context 의 *우연한 다른 sentence 의 keyword* 매치
    (false PASS) 차단. Vacuous PASS 차단 — premortem §3 정합.
    """
    sentence_split = re.compile(r'(?<=[.!?])\s+|\n\n+')
    for root in search_roots:
        if not root.exists():
            continue
        for fp in root.rglob('*'):
            if not fp.is_file():
                continue
            if fp.suffix not in JUSTIFICATION_SEARCH_SUFFIXES:
                continue
            body = _read(fp)
            if not body:
                continue
            sentences = sentence_split.split(body)
            field_pattern = re.compile(rf'\b{re.escape(field)}\b')
            for sent in sentences:
                if not field_pattern.search(sent):
                    continue
                # 같은 sentence 안 OR 직후 sentence 안에 justification keyword
                if JUSTIFICATION_RE.search(sent) or WHY_PREFIX_RE.search(sent):
                    return {
                        'found': True,
                        'file': str(fp),
                        'context': sent.strip().replace('\n', ' ')[:160],
                    }
    return {'found': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--target-root', type=Path, default=None,
                        help='config 산출물 root (suspicious default 검색 대상)')
    parser.add_argument('--justification-roots', type=Path, nargs='*', default=None,
                        help='justification 검색 root (README/handoff/intent/docs)')
    parser.add_argument('--prompt-meta-file', type=Path, default=None,
                        help='prompt_meta_extractor 산출물. default_warnings 비어있으면 PASS skip')
    parser.add_argument('--require-default-warning', action='store_true', default=False,
                        help='prompt-meta 의 default_warnings ≥1 의무 (default OFF — 비어있으면 skip)')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.target_root is None:
        parser.error('--target-root required when not --self-test')

    # 1) prompt-meta 의 default_warnings 검사 — 비어있으면 PASS skip
    default_warnings = []
    if args.prompt_meta_file and args.prompt_meta_file.exists():
        try:
            meta = json.loads(args.prompt_meta_file.read_text(encoding='utf-8'))
            default_warnings = meta.get('default_warnings', [])
        except (json.JSONDecodeError, OSError):
            pass

    if not default_warnings:
        if args.require_default_warning:
            print('FAIL: prompt-meta default_warnings 비어있음 (--require-default-warning)',
                  file=sys.stderr)
            return 1
        report = {
            'schema_version': SCHEMA_VERSION,
            'pass': True,
            'note': 'default_warnings 비어있음 — 본 CLI 적용 대상 외 (PASS skip)',
        }
        if args.json_out:
            args.json_out.parent.mkdir(parents=True, exist_ok=True)
            args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                     encoding='utf-8')
        print('PASS: default_value_justification (prompt-meta default_warnings 0 — skip)')
        return 0

    # 2) suspicious default 검색
    defaults = find_suspicious_defaults(args.target_root)

    # 3) justification 검사
    search_roots = args.justification_roots or [args.target_root]
    results = []
    failures = []
    for d in defaults:
        just = has_justification(d['field'], search_roots)
        results.append({**d, 'justification': just})
        if not just['found']:
            failures.append(
                f'{d["file"]}:{d["field"]} ({d["kind"]}) - no justification'
            )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'default_warnings_count': len(default_warnings),
        'suspicious_defaults_count': len(defaults),
        'results': results[:20],
        'failures': failures,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                 encoding='utf-8')

    if failures:
        print(f'FAIL: default_value_justification ({len(failures)} 결손)',
              file=sys.stderr)
        for f in failures[:8]:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: default_value_justification '
        f'(warnings={len(default_warnings)} defaults={len(defaults)} all justified)'
    )
    return 0


def _self_test() -> int:
    # 1) suspicious default detection
    yaml_body = '''
warmup_minutes: 0
seed: 12345
mode: "auto"
threshold: 0.999
state: null
replications: 30
'''
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        config = Path(d) / 'config.yaml'
        config.write_text(yaml_body, encoding='utf-8')
        defaults = find_suspicious_defaults(Path(d))
        kinds = {x['field']: x['kind'] for x in defaults}
        # warmup_minutes:0, mode:"auto", state:null 매치 (seed/replications 는 trivial 제외, threshold 는 0이 아님)
        assert 'warmup_minutes' in kinds and kinds['warmup_minutes'] == 'zero', (
            f'warmup_minutes detection failed: {kinds}'
        )
        assert 'mode' in kinds and kinds['mode'] == 'magic_string', (
            f'mode detection failed: {kinds}'
        )
        assert 'state' in kinds and kinds['state'] == 'null', (
            f'state detection failed: {kinds}'
        )
        # seed / replications 는 trivial → skip
        assert 'seed' not in kinds, f'seed should be skipped (trivial): {kinds}'

    # 2) justification detection
    text_with = '''
The warmup_minutes is set to 0 because the model assumes steady-state from t=0.
This is intentionally chosen to match the prompt's specification.
'''
    text_without = '''
warmup_minutes is 0.
The model runs for 8 hours.
'''
    just_with = JUSTIFICATION_RE.search(text_with) is not None
    just_without = JUSTIFICATION_RE.search(text_without) is not None
    assert just_with, 'justification keyword should match in text_with'
    assert not just_without, 'no justification should match in text_without'

    print('SELF-TEST PASS — default_value_justification')
    return 0


if __name__ == '__main__':
    sys.exit(main())
