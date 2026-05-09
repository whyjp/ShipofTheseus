"""generate_sprint40_artefacts.py — sprint-40 13 산출물 *빈 골격* 자동 emit (sprint-41 PR-F).

본 스크립트는 phase 00 (pre-cold-session-bootup) 직후 호출되어 sprint-40 의 13 의무 산출물의
*빈 골격* 을 자동 emit. cold session 이 phase 진행 중 verdict 갱신.

cold_session_artefacts.py (PR-C) 가 *부재 시 차단*, 본 PR-F 가 *부재 시 골격 emit 후
cold session 채움 유도*. 두 CLI 페어 = pre-emit + check 패턴.

사용:
    python generate_sprint40_artefacts.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --grade G4 \\
        --domain DES

Exit codes:
    0 — 13 골격 emit 성공 (또는 이미 존재 — overwrite 안 함)
    1 — emit 실패 (디스크 / 권한 등)

본 CLI = sprint-40 컨벤션 본문 의 *runtime emit 메커니즘*. agent 가 cold session 진행
중 의무 산출물을 *발견* → *채움* 의 pre-condition.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Windows cp949 회피
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.46"


# 13 산출물 골격 — verdict: "pending" (cold session 이 phase 진행 시 갱신)
SKELETONS = {
    'quality/gate_v6_reproducibility.json': {
        'schema_version': SCHEMA_VERSION,
        'intra_process': {'test_id': None, 'passed': None},
        'cross_process': {
            'pythonhashseed': '0',
            'invoke_1': {'stdout_sha256': None, 'summary_sha256': None, 'summary_path': None},
            'invoke_2': {'stdout_sha256': None, 'summary_sha256': None, 'summary_path': None},
            'summary_byte_equal': None,
        },
        'anti_pattern_grep': {
            'scanned_globs': ['src/**/*.py'],
            'patterns_checked': 0,
            'violations': [],
        },
        'verdict': 'pending',
    },
    'quality/gate_v8_viewer_readiness.json': {
        'schema_version': SCHEMA_VERSION,
        'grade': None,
        'domain_matched': None,
        'checks': [],
        'missing': [],
        'verdict': 'pending',
    },
    'quality/gate_readme_summary_consistency.json': {
        'schema_version': SCHEMA_VERSION,
        'atomic_regen_block': {
            'measure_run_started_at': None,
            'summary_emitted_at': None,
            'readme_regenerated_at': None,
            'atomic': None,
            'phases_between': [],
        },
        'scanned': {
            'files': ['README.md', 'outputs/README.md', 'handoff/14-handoff.md'],
            'numbers_total': 0,
            'numbers_mapped': 0,
            'numbers_external_source': 0,
        },
        'drift': {
            'tolerance_pct': 0.01,
            'violations': [],
            'max_observed_drift_pct': 0.0,
        },
        'verdict': 'pending',
    },
    'quality/gate_methodology_completeness.json': {
        'schema_version': SCHEMA_VERSION,
        'domain': None,
        'domain_matched': None,
        'skeleton_checks': {
            'transient_classification': {'verdict': 'pending', 'evidence_path': None},
            'sample_size_power': {'verdict': 'pending', 'evidence_path': None},
            'determinism_protocol': {'verdict': 'pending', 'evidence_path': None},
            'horizon_classification': {'verdict': 'pending', 'evidence_path': None},
        },
        'verdict': 'pending',
    },
    'quality/gate_pnc.json': {
        'schema_version': SCHEMA_VERSION,
        'fields_total': 0,
        'fields_consumed': 0,
        'fields_orphan': 0,
        'violations': [],
        'verdict': 'pending',
    },
    'quality/gate_mirror.json': {
        'schema_version': SCHEMA_VERSION,
        'internal_facts_total': 0,
        'mirrored_count': 0,
        'unmirrored_count': 0,
        'violations': [],
        'verdict': 'pending',
    },
    'quality/gate_primary.json': {
        'schema_version': SCHEMA_VERSION,
        'primary_directives_total': 0,
        'direct_measured': 0,
        'proxy_via_sibling': 0,
        'violations': [],
        'verdict': 'pending',
    },
    'quality/gate_literal.json': {
        'schema_version': SCHEMA_VERSION,
        'avoid_directives_total': 0,
        'regex_patterns': [],
        'violations': [],
        'verdict': 'pending',
    },
    'intent/modeling_shortcuts.json': {
        'schema_version': SCHEMA_VERSION,
        'domain': None,
        'shortcuts': [],
        'verdict': 'pending',
    },
    'webview/exit_gate.json': {
        'schema_version': SCHEMA_VERSION,
        'checked_at': None,
        'required_files': [],
        'missing': [],
        'verdict': 'pending',
    },
    'interactive-viewer/exit_gate.json': {
        'schema_version': SCHEMA_VERSION,
        'grade': None,
        'domain_matched': None,
        'checked_at': None,
        'widget_count': 0,
        'widget_types': [],
        'g4_widget_types_satisfied': None,
        'missing': [],
        'verdict': 'pending',
    },
    'interactive-viewer/dashboard.json': {
        'schema_version': SCHEMA_VERSION,
        'project_id': None,
        'current_phase': 'pending',
        'status': 'waiting',
        'domain': None,
        'matched': None,
        'skip': False,
        'summary_kpis': [],
        'scenarios': [],
        'widgets': [],
        'raw_artifacts': [],
        'narrative': '',
    },
}

# 마크다운 골격 — cascaded sub-Q
CASCADED_SUBQ_SKELETON = """---
skill_name: theseus-harness
skill_version: 0.9.46
phase: 04-cascaded-subq
generated_from: []
created_at: {iso}
---

# Phase 04 cascaded sub-Q — 자동 파생 (sprint-40 PR-F + sprint-41 PR-F skeleton)

> 본 파일은 phase 04 인터뷰 종료 후 keyword 매칭 sub-Q 답을 박는 자리. 빈 골격 — cold
> session 이 진행 중 채움.

## (cascading sub-Q 가 없는 경우)

phase 04 의 Q-D 답에 cascading keyword (noise / dispatch / seed / aggregation / warmup /
tolerance) 매칭 0 — 본 파일은 *명시 빈* 으로 유지.

## (cascading sub-Q 가 있는 경우 — cold session 이 추가)

```yaml
- parent_qd: Q-D3
  keyword_matched: lognormal
  sub_qs:
    - id: Q-D3.1
      question: noise per atomic event 또는 per duration unit?
      answer: <pending>
    - id: Q-D3.2
      question: distribution truncation policy?
      answer: <pending>
```
"""


def emit_skeleton(
    project_root: Path,
    rel_path: str,
    skeleton: dict[str, Any] | str,
    overwrite: bool = False,
) -> dict[str, Any]:
    """단일 산출물 골격 emit. 이미 존재 + not overwrite 시 skip."""
    path = project_root / rel_path
    if path.exists() and not overwrite:
        return {'path': rel_path, 'status': 'exists_skip', 'size': path.stat().st_size}

    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(skeleton, dict):
        path.write_text(json.dumps(skeleton, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    else:
        path.write_text(skeleton, encoding='utf-8')
    return {'path': rel_path, 'status': 'emitted', 'size': path.stat().st_size}


def emit_all(
    project_root: Path,
    overwrite: bool = False,
) -> dict[str, Any]:
    """13 산출물 골격 일괄 emit."""
    iso = datetime.now(timezone.utc).isoformat()
    results = []

    # JSON 골격 12 종
    for rel, skel in SKELETONS.items():
        results.append(emit_skeleton(project_root, rel, skel, overwrite))

    # markdown 골격 1 종
    cascaded_text = CASCADED_SUBQ_SKELETON.format(iso=iso)
    results.append(emit_skeleton(project_root, 'intent/04-cascaded-subq.md', cascaded_text, overwrite))

    emitted_count = sum(1 for r in results if r['status'] == 'emitted')
    skip_count = sum(1 for r in results if r['status'] == 'exists_skip')

    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'evaluated_at': iso,
        'total': len(results),
        'emitted': emitted_count,
        'skipped': skip_count,
        'results': results,
        'verdict': 'pass' if (emitted_count + skip_count) == len(results) else 'fail',
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='generate_sprint40_artefacts',
        description=(
            'Sprint-40 13 신규 산출물 빈 골격 자동 emit — phase 00 직후 호출. '
            'cold_session_artefacts.py (PR-C) 의 페어.'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='기존 파일 덮어쓰기 (default: skip).',
    )
    parser.add_argument('--output', type=Path, help='산출 결과 JSON 경로')
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        ns.project_root.mkdir(parents=True, exist_ok=True)

    verdict_obj = emit_all(ns.project_root, overwrite=ns.overwrite)

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet:
        print(
            f"\n[generate_sprint40_artefacts] {verdict_obj['emitted']} 신규 emit + "
            f"{verdict_obj['skipped']} skip (이미 존재). cold session 이 verdict 'pending' → 'pass' 갱신.",
            file=sys.stderr,
        )

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
