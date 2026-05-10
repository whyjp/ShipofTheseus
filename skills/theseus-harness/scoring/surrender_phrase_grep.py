"""surrender_phrase_grep.py — Agent 자율 종료 자백 어휘 차단 CLI (sprint-42 PR-E v0.9.47).

본 스크립트는 cold session 산출물 본문에 *agent 가 책임 회피 / 자율 종료 / 외부 위임* 류
어휘 등장 시 차단. orchestrator 가 phase 10 / phase 14 exit 시 의무 호출 (HARD-RULE 9.xx).

증거 회피 사례 (0510-2 회차):
    `sprints/03/report.json:lessons_outbound[1]` =
    "0.97 < 0.999 G4 asymptote; defer to opus-reviewer scoring as final ground truth"
    이 직접 자백 어휘 — *defer to* / *asymptote* — 본 CLI 가 차단.

사용:
    python surrender_phrase_grep.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --output quality/gate_surrender_phrase.json

Exit codes:
    0 — 자백 어휘 0 매치 OR 모든 매치에 override 명시
    1 — 자백 어휘 매치 + override 부재 (자율 종료 자백 차단)

본 CLI = ouroboros 보다 *더 깊은* enforcement — 점수 / 산출물 / 단조성 외에
*agent 의 자백 어휘* 자체를 차단. 메모리 [`feedback_hurdle_as_cli_paradigm.md`] 정합.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.47"


# Surrender 어휘 카탈로그 — 8 패턴 (conventions/surrender-phrase-forbid.md 정합)
SURRENDER_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    (
        'defer_to_external',
        re.compile(r'\bdefer(?:s|red|ring)?\s+to\s+(?!self|the\s+(?:plan|impl|test|code))(?:opus[-_]reviewer|human|external|reviewer|grader|judge|user)\b', re.IGNORECASE),
        '외부 위임 — 본 하네스 책임 회피',
    ),
    (
        'plateaued',
        re.compile(r'\bplateau(?:ed|ing)\b', re.IGNORECASE),
        '정체 인정 (verb form — agent 자가 진단) — stagnation 후 노력 종료 신호. *명사 plateau* 는 neutral observation 으로 허용.',
    ),
    (
        'asymptote',
        re.compile(r'\basymptot(?:e|ic|ically)\b', re.IGNORECASE),
        '점근선 인정 — 임계 미달 + 종료 정당화',
    ),
    (
        'good_enough',
        re.compile(r"\bgood\s+enough\b", re.IGNORECASE),
        '"이쯤이면 충분해" 직접 어휘',
    ),
    (
        'sufficient',
        re.compile(r"\b(?:considered|deemed|judged|is)\s+sufficient\b", re.IGNORECASE),
        '충분함 인정 — context 의존 (override 가능)',
    ),
    (
        'fine_tune_narrative',
        re.compile(r'\bfine[-_\s]?tune\s+(?:the\s+)?(?:narrative|wording|prose|text)\b', re.IGNORECASE),
        '서술만 다듬음 — 실 개선 회피',
    ),
    (
        'would_only',
        re.compile(r'\bwould\s+only\s+(?:fine[-_\s]?tune|polish|tweak|adjust)\b', re.IGNORECASE),
        '더 시도 무의미 — exit 자율 결정 정당화',
    ),
    (
        'final_ground_truth_external',
        re.compile(r'\b(?:final|definitive)\s+ground\s+truth\b', re.IGNORECASE),
        '외부에 진실 위임 — 본 하네스 결정 회피',
    ),
]


# Override 메커니즘 — frontmatter `surrender_override: true` + reason 검사
OVERRIDE_PATTERN = re.compile(
    r'^surrender_override:\s*(?:true|yes)\b',
    re.MULTILINE | re.IGNORECASE,
)
OVERRIDE_REASON_PATTERN = re.compile(
    r'^surrender_override_reason:\s*[\'"]?[^\s\'"]+',
    re.MULTILINE | re.IGNORECASE,
)


def file_has_override(text: str) -> bool:
    return bool(OVERRIDE_PATTERN.search(text)) and bool(OVERRIDE_REASON_PATTERN.search(text))


def scan_file(path: Path) -> list[dict[str, Any]]:
    """단일 파일 surrender 어휘 매치 list."""
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except OSError:
        return []

    has_override = file_has_override(text)
    matches: list[dict[str, Any]] = []
    for kind, pat, why in SURRENDER_PATTERNS:
        for m in pat.finditer(text):
            matches.append({
                'kind': kind,
                'match': m.group(0),
                'why': why,
                'overridden': has_override,
                'span_start': m.start(),
            })
    return matches


def evaluate(project_root: Path, scan_globs: list[str] | None = None) -> dict[str, Any]:
    if scan_globs is None:
        scan_globs = ['**/*.md', '**/*.json']

    seen_paths: set[Path] = set()
    files: list[Path] = []
    for glob in scan_globs:
        for p in project_root.rglob(glob.replace('**/', '')):
            if p.is_file() and p not in seen_paths:
                seen_paths.add(p)
                files.append(p)

    per_file: list[dict[str, Any]] = []
    total_violations = 0
    overridden_count = 0
    for path in files:
        matches = scan_file(path)
        if not matches:
            continue
        non_override = [m for m in matches if not m['overridden']]
        per_file.append({
            'path': str(path.relative_to(project_root)),
            'matches': matches,
            'match_count': len(matches),
            'non_override_count': len(non_override),
        })
        total_violations += len(non_override)
        overridden_count += len([m for m in matches if m['overridden']])

    overall_pass = total_violations == 0

    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'files_scanned': len(files),
        'files_with_match': len(per_file),
        'total_violations': total_violations,
        'overridden_count': overridden_count,
        'per_file': per_file,
        'patterns_checked': [p[0] for p in SURRENDER_PATTERNS],
        'verdict': 'pass' if overall_pass else 'fail',
        'reason': (
            'surrender 어휘 0 매치 (또는 모두 override)'
            if overall_pass
            else f"{total_violations} surrender 매치 (override 부재)"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='surrender_phrase_grep',
        description=(
            'Agent 자율 종료 자백 어휘 차단 CLI — 8 패턴 grep + override 검사. '
            'HARD-RULE 9.xx (sprint-42).'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument(
        '--scan-glob',
        action='append',
        help='스캔할 glob 패턴 (반복 가능, default: **/*.md, **/*.json)',
    )
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(ns.project_root, ns.scan_glob)

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[surrender_phrase_grep] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        for f in verdict_obj['per_file']:
            if f['non_override_count'] > 0:
                print(f"  - {f['path']} ({f['non_override_count']}):", file=sys.stderr)
                for m in f['matches']:
                    if not m['overridden']:
                        print(f"      [{m['kind']}] {m['match']!r} — {m['why']}", file=sys.stderr)

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
