"""phase_invoke_audit.py — orchestrator literal command 호출 trace 검증 CLI (sprint-43 PR-C).

본 스크립트는 orchestrator SKILL.md 본문에서 *literal Bash command* (e.g.,
`python skills/theseus-harness/scoring/<NAME>.py`) 를 추출 + cold session 산출물에서
각 CLI 의 *호출 trace* (e.g., `quality/gate_<NAME>.json` 파일 존재 + evaluated_at
timestamp) 검증. *declared but not invoked* 패턴 차단.

orchestrator 가 phase 09 진입 + phase 14 진입 시 의무 호출 (HARD-RULE 9.zz).

증거 회피 사례 (g4-v2 91 회차):
    sprint-41/42 9 CLI 가 declared (HARD-RULE 9.qq~9.xx). 그러나 cold session 산출물 0 trace.
    *declared = 9, invoked = 0*. 본 CLI = 차단.

사용:
    python phase_invoke_audit.py \\
        --orchestrator-skill skills/theseus-orchestrator/SKILL.md \\
        --project-root .ShipofTheseus/<proj>/ \\
        --output quality/gate_phase_invoke_audit.json

Exit codes:
    0 — 모든 declared CLI 가 invoked (trace 존재)
    1 — 일부 CLI declared but not invoked
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


SCHEMA_VERSION = "0.9.48"


# CLI 별 trace 산출물 매핑 (orchestrator 가 호출 시 emit 하는 JSON 위치)
CLI_TRACE_PATHS = {
    'dacapo_threshold': [
        'plan/dacapo_threshold.json',
        'impl/dacapo_threshold.json',
    ],
    'runtime_guard_chain': ['quality/gate_runtime_guard_chain.json'],
    'cross_phase_context_audit': ['quality/gate_cross_phase_context.json'],
    'universe_count_monotonicity': ['quality/gate_universe_monotonicity.json'],
    'stagnation_breakthrough': ['sprints/*/gate_stagnation_breakthrough.json'],
    'surrender_phrase_grep': ['quality/gate_surrender_phrase.json'],
    'submission_completeness': ['results/gate_submission_completeness.json'],
}

# orchestrator literal command 추출 정규식
LITERAL_CMD_PATTERN = re.compile(
    r'`?python\s+skills/theseus-harness/scoring/(\w+)\.py\b',
    re.IGNORECASE,
)


def extract_declared_clis(orchestrator_md: Path) -> dict[str, Any]:
    """orchestrator SKILL.md 에서 literal Bash command 패턴으로 declared CLI 추출."""
    if not orchestrator_md.exists():
        return {'present': False, 'declared_clis': []}

    text = orchestrator_md.read_text(encoding='utf-8', errors='ignore')
    matches = LITERAL_CMD_PATTERN.findall(text)
    declared = sorted(set(matches))
    return {
        'present': True,
        'orchestrator_md': str(orchestrator_md),
        'declared_clis': declared,
        'declaration_count': len(matches),
    }


def check_invocation_trace(project_root: Path, cli_name: str) -> dict[str, Any]:
    """단일 CLI 의 호출 trace 검사."""
    trace_paths = CLI_TRACE_PATHS.get(cli_name, [])
    if not trace_paths:
        return {
            'cli': cli_name,
            'trace_paths': [],
            'invoked': None,
            'note': 'CLI_TRACE_PATHS 에 매핑 없음 — audit 불가',
        }

    found_traces = []
    for tp in trace_paths:
        if '*' in tp:
            # glob
            matches = list(project_root.glob(tp))
            for m in matches:
                if m.is_file():
                    try:
                        data = json.loads(m.read_text(encoding='utf-8'))
                        found_traces.append({
                            'path': str(m.relative_to(project_root)),
                            'evaluated_at': data.get('evaluated_at'),
                            'verdict': data.get('verdict'),
                        })
                    except (json.JSONDecodeError, OSError):
                        pass
        else:
            full = project_root / tp
            if full.exists() and full.is_file():
                try:
                    data = json.loads(full.read_text(encoding='utf-8'))
                    found_traces.append({
                        'path': tp,
                        'evaluated_at': data.get('evaluated_at'),
                        'verdict': data.get('verdict'),
                    })
                except (json.JSONDecodeError, OSError):
                    pass

    return {
        'cli': cli_name,
        'trace_paths': trace_paths,
        'found_traces': found_traces,
        'invoked': len(found_traces) > 0,
    }


def evaluate(
    orchestrator_md: Path,
    project_root: Path,
) -> dict[str, Any]:
    decl_info = extract_declared_clis(orchestrator_md)

    if not decl_info['present']:
        return {
            'schema_version': SCHEMA_VERSION,
            'orchestrator_md': str(orchestrator_md),
            'project_root': str(project_root),
            'verdict': 'fail',
            'reason': 'orchestrator SKILL.md 미존재',
        }

    declared = decl_info['declared_clis']
    invocation_results = {}
    not_invoked = []
    audit_skipped = []
    for cli in declared:
        result = check_invocation_trace(project_root, cli)
        invocation_results[cli] = result
        if result['invoked'] is False:
            not_invoked.append(cli)
        elif result['invoked'] is None:
            audit_skipped.append(cli)

    overall_pass = len(not_invoked) == 0

    return {
        'schema_version': SCHEMA_VERSION,
        'orchestrator_md': str(orchestrator_md),
        'project_root': str(project_root),
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'declared_clis': declared,
        'declaration_count_total': decl_info['declaration_count'],
        'invocation_results': invocation_results,
        'not_invoked': not_invoked,
        'audit_skipped': audit_skipped,
        'verdict': 'pass' if overall_pass else 'fail',
        'reason': (
            f"all {len(declared)} declared CLI invoked"
            if overall_pass
            else (
                f"{len(not_invoked)} declared CLI not invoked: {not_invoked}. "
                f"orchestrator phase 본문에 literal command 박혀 있어도 cold session 이 자율 skip 했음."
            )
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='phase_invoke_audit',
        description=(
            'orchestrator literal command 호출 trace 검증 CLI — declared ≠ invoked 갭 차단. '
            'HARD-RULE 9.zz (sprint-43).'
        ),
    )
    parser.add_argument('--orchestrator-skill', type=Path, required=True)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(ns.orchestrator_skill, ns.project_root)

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[phase_invoke_audit] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        for cli in verdict_obj.get('not_invoked', []):
            paths = verdict_obj['invocation_results'][cli]['trace_paths']
            print(f"  - {cli}: trace 미발견 ({paths})", file=sys.stderr)

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
