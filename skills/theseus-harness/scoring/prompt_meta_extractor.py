"""prompt_meta_extractor.py — Prompt-driven harness 의 *seed* CLI (sprint-51 PR-A v0.9.51).

본 스크립트는 cold session 의 prompt.md (또는 user 메시지 dump) 를 *구조 markdown
parse* 로 8 메타-카탈로그 자동 추출. agent 가 *프롬프트 너머* 사고를 자력 발굴할
필요 없이, 본 추출 결과가 Phase 1.5 hidden intent / placeholder grep / default
justification / anti-pattern 모두의 입력.

격언 (사용자 직접 인용, 2026-05-10):
    "이 자체가 우리 intent 가 회귀하며 숨은 의도를 모두 채우는 방식의 이유야"

회귀 cycle 의 seed: prompt.md → intent/00-prompt-meta.json → 후속 페이즈 입력.

8 카탈로그:

1. output_schemas — code block 의 file column list (results.csv / summary.json / event_log.csv 등)
2. readme_required_items — `## README` 섹션 직후 numbered list
3. decision_questions — `## Operational decision questions` 또는 유사 §의 numbered list
4. evaluation_dimensions — `## Evaluation criteria` 또는 유사 §의 sub-bullet
5. anti_patterns — 부정 표현 grep (not / avoid / instead of / rather than / not sufficient
                                       / silently / not manually fabricated)
6. explicit_constraints — numeric + unit grep (8-hour / 30 replications / 95%)
7. default_warnings — "Use ... rather than zero" / "meaningful values" / "non-trivial" 등 패턴
8. conditional_obligations — "where applicable" / "where measurable" / "if appropriate" 패턴

본 CLI 는 *벤치 무관* — markdown 의 공통 패턴만 추출. domain knowledge 0.

사용:
    python prompt_meta_extractor.py \\
        --prompt-file benchmarks/<id>/prompt.md \\
        --output intent/00-prompt-meta.json

Exit codes:
    0 — 추출 성공 + 모든 카탈로그 emit (빈 list 도 OK, list 자체 없음 = fail)
    1 — prompt 파일 부재 / parse 실패 / 추출 결과 비정합
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


HEADER_RE = re.compile(r'^(#{1,4})\s+(.+?)\s*$', re.MULTILINE)
CODE_BLOCK_RE = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)
NUMBERED_LIST_RE = re.compile(r'^\s*(\d+)\.\s+(.+?)\s*$', re.MULTILINE)
BULLET_LIST_RE = re.compile(r'^\s*[-*]\s+(.+?)\s*$', re.MULTILINE)
BACKTICK_FILE_RE = re.compile(r'`([A-Za-z0-9_./-]+\.(?:csv|json|md|yaml|yml|py|txt|html|png|gif|mp4))`')


# Anti-pattern phrases — 부정 표현 catalog (확장 가능, 도메인 무관)
ANTI_PATTERN_TRIGGERS = [
    (r'\bnot\s+sufficient\b', 'not_sufficient'),
    (r'\bnot\s+manually\s+fabricated\b', 'not_fabricated'),
    (r'\bsilently\s+(?:producing|fail|skip)', 'silent_failure'),
    (r'\binstead\s+of\b', 'instead_of'),
    (r'\brather\s+than\b', 'rather_than'),
    (r'\bavoid\b', 'avoid'),
    (r'\bshould\s+fail\b', 'should_fail'),
    (r'\bmust\s+not\b', 'must_not'),
    (r'\bnot\s+at\s+the\s+expense\s+of\b', 'not_at_expense_of'),
]


# Default warnings — "use meaningful values rather than zeros" 류
DEFAULT_WARNING_TRIGGERS = [
    (r'use\s+meaningful\s+values\s+rather\s+than\s+zeros?', 'meaningful_not_zero'),
    (r'use\s+meaningful\s+values?', 'meaningful_values'),
    (r'avoid\s+placeholders?', 'avoid_placeholder'),
    (r'do\s+not\s+leave\s+(?:as\s+)?(?:null|empty|placeholder)', 'no_null'),
    (r'fill\s+in\s+all\s+fields?', 'fill_all'),
    (r'must\s+be\s+(?:non-empty|populated|set)', 'must_populate'),
]


# Conditional obligations — 조건부 의무 catalog
CONDITIONAL_TRIGGERS = [
    (r'where\s+applicable', 'where_applicable'),
    (r'where\s+measurable', 'where_measurable'),
    (r'where\s+appropriate', 'where_appropriate'),
    (r'if\s+appropriate', 'if_appropriate'),
    (r'if\s+useful', 'if_useful'),
    (r'where\s+possible', 'where_possible'),
]


# Numeric + unit constraint — explicit constraint catalog
CONSTRAINT_RE = re.compile(
    r'\b(\d+(?:\.\d+)?)\s*'
    r'(hour|hours|h|min|minutes|sec|seconds|s|'
    r'replication|replications|reps|'
    r'%|percent|'
    r'CI|confidence|'
    r'truck|trucks|loaders?|nodes?|edges?|'
    r'kph|mph|m\b|metres?|meters?)',
    re.IGNORECASE,
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return ''


def _sections(body: str) -> list[dict]:
    """body 를 §-level 으로 split — 각 section 의 (level, title, content)."""
    headers = list(HEADER_RE.finditer(body))
    out = []
    for i, m in enumerate(headers):
        level = len(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(body)
        out.append({
            'level': level,
            'title': title,
            'title_lower': title.lower().strip('`').strip(),
            'content': body[start:end].strip(),
            'span': (m.start(), end),
        })
    return out


def _extract_output_schemas(body: str, sections: list[dict]) -> list[dict]:
    """code block 또는 backtick file 에서 output schema 추출."""
    schemas = []
    seen = set()

    # Pattern 1: ## `<filename>` 형식의 §-header (e.g. ## `summary.json`)
    for sec in sections:
        m = re.match(r'^[`]?([A-Za-z0-9_./-]+\.(?:csv|json|md|yaml|yml))[`]?$', sec['title'])
        if not m:
            continue
        fn = m.group(1)
        if fn in seen:
            continue
        # 본 §의 code block (json) 또는 bullet list 에서 field 추출
        fields = _fields_from_section(sec['content'], fn)
        if fields:
            schemas.append({
                'file': fn,
                'fields': fields,
                'field_count': len(fields),
                'required': True,
                'extraction_marker': f'## `{fn}`',
            })
            seen.add(fn)

    return schemas


def _fields_from_section(content: str, filename: str) -> list[str]:
    """section content 에서 schema field 추출 — code block (json/yaml) 또는 bullet list."""
    fields = []

    # code block from json / yaml
    for m in CODE_BLOCK_RE.finditer(content):
        lang = (m.group(1) or '').lower()
        block = m.group(2)
        if filename.endswith('.json') or lang == 'json':
            for kmatch in re.finditer(r'^\s*"([A-Za-z_][A-Za-z_0-9]*)"\s*:', block, re.MULTILINE):
                key = kmatch.group(1)
                if key not in fields:
                    fields.append(key)
        elif filename.endswith(('.csv',)) or lang in ('text', '', 'csv'):
            # text block — line-per-field 패턴
            for line in block.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # 단순 identifier
                if re.match(r'^[A-Za-z_][A-Za-z_0-9]*$', line):
                    if line not in fields:
                        fields.append(line)

    # bullet list 의 backtick identifier (code/csv 유사)
    if not fields:
        for m in BULLET_LIST_RE.finditer(content):
            txt = m.group(1)
            ident = re.match(r'^`([A-Za-z_][A-Za-z_0-9]*)`', txt)
            if ident:
                key = ident.group(1)
                if key not in fields:
                    fields.append(key)

    return fields


def _extract_readme_items(sections: list[dict]) -> list[str]:
    """## README 또는 README.md 섹션의 numbered list."""
    for sec in sections:
        if 'readme' in sec['title_lower']:
            items = [m.group(2).strip()
                     for m in NUMBERED_LIST_RE.finditer(sec['content'])]
            if items:
                return items
    return []


def _extract_decision_questions(sections: list[dict]) -> list[str]:
    """decision question / 운영 결정 질문 섹션."""
    keywords = ['decision question', 'decision questions', 'questions to answer',
                'operational question', '결정 질문', '의사결정 질문']
    for sec in sections:
        if any(kw in sec['title_lower'] for kw in keywords):
            items = [m.group(2).strip()
                     for m in NUMBERED_LIST_RE.finditer(sec['content'])]
            if items:
                return items
    return []


def _extract_evaluation_dimensions(sections: list[dict]) -> list[dict]:
    """evaluation criteria / rubric 섹션 — 다음 same-or-higher level 헤더 까지의 sub-section 수집."""
    keywords = ['evaluation criteria', 'evaluation', 'rubric', 'scoring',
                '평가 기준', '평가 차원']
    eval_idx = None
    for i, sec in enumerate(sections):
        if sec['title_lower'] in keywords or any(kw in sec['title_lower'] for kw in keywords):
            eval_idx = i
            break
    if eval_idx is None:
        return []

    eval_sec = sections[eval_idx]
    dims = []
    for j in range(eval_idx + 1, len(sections)):
        s = sections[j]
        if s['level'] <= eval_sec['level']:
            break  # next same-or-higher level header — eval section 끝
        criteria = [m.group(1).strip() for m in BULLET_LIST_RE.finditer(s['content'])]
        clean_title = re.sub(r'^\d+\.\s+', '', s['title'])
        dims.append({
            'name': clean_title,
            'criteria': criteria,
            'criteria_count': len(criteria),
        })
    return dims


def _extract_anti_patterns(body: str) -> list[dict]:
    """부정 표현 grep — 도메인 무관."""
    out = []
    seen = set()
    for pattern, category in ANTI_PATTERN_TRIGGERS:
        for m in re.finditer(pattern, body, re.IGNORECASE):
            ctx_start = max(0, m.start() - 60)
            ctx_end = min(len(body), m.end() + 60)
            ctx = body[ctx_start:ctx_end].replace('\n', ' ').strip()
            key = (category, m.group(0).lower())
            if key in seen:
                continue
            seen.add(key)
            out.append({
                'phrase': m.group(0),
                'context': ctx,
                'category': category,
            })
    return out


def _extract_default_warnings(body: str) -> list[dict]:
    out = []
    for pattern, category in DEFAULT_WARNING_TRIGGERS:
        for m in re.finditer(pattern, body, re.IGNORECASE):
            ctx_start = max(0, m.start() - 80)
            ctx_end = min(len(body), m.end() + 80)
            ctx = body[ctx_start:ctx_end].replace('\n', ' ').strip()
            out.append({
                'phrase': m.group(0),
                'context': ctx,
                'category': category,
            })
    return out


def _extract_conditional_obligations(body: str) -> list[dict]:
    out = []
    seen = set()
    for pattern, category in CONDITIONAL_TRIGGERS:
        for m in re.finditer(pattern, body, re.IGNORECASE):
            ctx_start = max(0, m.start() - 60)
            ctx_end = min(len(body), m.end() + 60)
            ctx = body[ctx_start:ctx_end].replace('\n', ' ').strip()
            key = (category, ctx[:80])
            if key in seen:
                continue
            seen.add(key)
            out.append({
                'phrase': m.group(0),
                'context': ctx,
                'category': category,
            })
    return out


def _extract_explicit_constraints(body: str) -> list[dict]:
    out = []
    seen = set()
    for m in CONSTRAINT_RE.finditer(body):
        text = m.group(0)
        if text.lower() in seen:
            continue
        seen.add(text.lower())
        out.append({
            'text': text,
            'value': m.group(1),
            'unit': m.group(2),
        })
    return out


def extract_meta(body: str, prompt_path: str) -> dict:
    sections = _sections(body)
    return {
        'schema_version': SCHEMA_VERSION,
        'prompt_path': prompt_path,
        'output_schemas': _extract_output_schemas(body, sections),
        'readme_required_items': _extract_readme_items(sections),
        'decision_questions': _extract_decision_questions(sections),
        'evaluation_dimensions': _extract_evaluation_dimensions(sections),
        'anti_patterns': _extract_anti_patterns(body),
        'explicit_constraints': _extract_explicit_constraints(body),
        'default_warnings': _extract_default_warnings(body),
        'conditional_obligations': _extract_conditional_obligations(body),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--prompt-file', type=Path, default=None)
    parser.add_argument('--output', type=Path, default=None,
                        help='emit json path (default: print to stdout)')
    parser.add_argument('--summary', action='store_true', default=False,
                        help='print one-line summary to stdout')
    parser.add_argument('--self-test', action='store_true', default=False)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.prompt_file is None:
        parser.error('--prompt-file required when not --self-test')

    if not args.prompt_file.exists():
        print(f'FAIL: {args.prompt_file} 부재', file=sys.stderr)
        return 1

    body = _read(args.prompt_file)
    if not body:
        print(f'FAIL: {args.prompt_file} 빈 파일', file=sys.stderr)
        return 1

    meta = extract_meta(body, str(args.prompt_file))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(meta, indent=2, ensure_ascii=False),
                               encoding='utf-8')

    schema_count = sum(s['field_count'] for s in meta['output_schemas'])
    summary = (
        f"PASS: prompt_meta_extractor "
        f"(schemas={len(meta['output_schemas'])}/{schema_count} fields, "
        f"readme={len(meta['readme_required_items'])}, "
        f"decisions={len(meta['decision_questions'])}, "
        f"eval_dims={len(meta['evaluation_dimensions'])}, "
        f"anti={len(meta['anti_patterns'])}, "
        f"defaults={len(meta['default_warnings'])}, "
        f"conditionals={len(meta['conditional_obligations'])}, "
        f"constraints={len(meta['explicit_constraints'])})"
    )
    print(summary)

    if not args.output and not args.summary:
        print(json.dumps(meta, indent=2, ensure_ascii=False))

    return 0


def _self_test() -> int:
    sample = '''# Task: Sample Benchmark

## Operational decision questions

1. What is the expected throughput?
2. What are the bottlenecks?
3. Does adding more workers help?

## Required outputs

```text
results.csv
summary.json
README.md
```

## `summary.json`

```json
{
  "benchmark_id": "x",
  "scenarios": {},
  "key_assumptions": []
}
```

Use meaningful values rather than zeros.

## `results.csv`

It should include:

- `scenario_id`
- `replication`
- `random_seed`

## README.md

The README should explain:

1. How to install dependencies.
2. How to run the simulation.
3. The conceptual model.

## Evaluation criteria

### 1. Conceptual modelling

- clear system boundary
- sensible assumptions

### 2. Code quality

- clear structure
- readable code

A static calculation is not sufficient.
The model should fail clearly rather than silently producing misleading results.
Token usage where measurable.
Run at least 30 replications.
'''
    meta = extract_meta(sample, '<self-test>')
    assert len(meta['decision_questions']) == 3, f"decisions: {meta['decision_questions']}"
    assert len(meta['readme_required_items']) == 3, f"readme: {meta['readme_required_items']}"
    assert len(meta['output_schemas']) >= 2, f"schemas: {meta['output_schemas']}"
    assert any('summary.json' == s['file'] for s in meta['output_schemas'])
    assert any('benchmark_id' in s['fields'] for s in meta['output_schemas'])
    assert len(meta['evaluation_dimensions']) >= 2, f"eval_dims: {meta['evaluation_dimensions']}"
    assert len(meta['anti_patterns']) >= 2, f"anti: {meta['anti_patterns']}"
    assert len(meta['default_warnings']) >= 1, f"defaults: {meta['default_warnings']}"
    assert len(meta['conditional_obligations']) >= 1, f"cond: {meta['conditional_obligations']}"
    assert len(meta['explicit_constraints']) >= 1, f"constraints: {meta['explicit_constraints']}"
    print(
        f"SELF-TEST PASS — prompt_meta_extractor "
        f"(decisions={len(meta['decision_questions'])} "
        f"readme={len(meta['readme_required_items'])} "
        f"schemas={len(meta['output_schemas'])} "
        f"anti={len(meta['anti_patterns'])} "
        f"defaults={len(meta['default_warnings'])})"
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
