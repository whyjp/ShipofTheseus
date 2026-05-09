"""cold_session_artefacts.py — Sprint-40 13 신규 산출물 file-existence 강제 CLI (sprint-41 PR-C).

본 스크립트는 *cold session* (`.ShipofTheseus/<project>/`) 안의 sprint-40 의무 산출물
13 종 (gate JSONs + intent 산출물 + viewer exit_gate / dashboard) 을 *존재 + valid +
verdict pass* 검증한다. 부재/invalid 시 exit 1 + stderr 결손 list. orchestrator 가
phase 09 진입 직전 의무 호출 (HARD-RULE 9.rr, sprint-41 신규).

자동 평가 (`evaluation_report.json:automated_checks.pass_rate == 1.0`) ≠ 산출물 통과
명확 분리 — phase 09 진입 *전* 의 게이트.

사용:
    python cold_session_artefacts.py \\
        --project-root .ShipofTheseus/<proj>/ \\
        --grade G4 \\
        --domain DES \\
        --output .ShipofTheseus/<proj>/quality/gate_cold_session_artefacts.json

Exit codes:
    0 — 13 모두 존재 + valid + verdict pass
    1 — missing OR invalid OR verdict fail (stderr 결손 list)

증거 회피 사례 (0510 회차):
    skill_version 0.9.45 frontmatter 박힘에도 13 산출물 모두 부재. 그러나 phase 09
    GREEN 자율 통과. 본 CLI 활성 시 phase 09 진입 거부 → 결손 산출물 emit 강제.

References:
- sprint-40 PR-B/C/E/F/G (13 산출물 도입)
- sprint-39 4 패턴 게이트 (gate_pnc/mirror/primary/literal.json)
- sprint-41 PR-C (본 PR, runtime guard CLI)
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Windows cp949 회피 — stdout/stderr UTF-8 강제 (한글 출력)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.46"


# 산출물 명세 — 13 항목
#   path: project_root 기준 상대 경로
#   kind: file | dir
#   require_grades: 의무 grade list (subset 매칭 시 의무, 미매칭 = skip 허용)
#   require_domains: 의무 domain list (None = all)
#   verdict_field: JSON 안의 verdict path (dotted, None = file 존재만)
#   require_verdict_pass: True 시 verdict == "pass" 의무
ARTEFACTS = [
    # sprint-40 PR-B G-1 (V6 cross-process evidence)
    {
        'id': 'gate_v6_reproducibility',
        'path': 'quality/gate_v6_reproducibility.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    # sprint-40 PR-C M-2 (viewer-readiness 사전)
    {
        'id': 'gate_v8_viewer_readiness',
        'path': 'quality/gate_v8_viewer_readiness.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    # sprint-40 PR-E G-2 (numeric drift atomic)
    {
        'id': 'gate_readme_summary_consistency',
        'path': 'quality/gate_readme_summary_consistency.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    # sprint-40 PR-G G-4 (methodology completeness, 도메인 매칭 시 활성)
    {
        'id': 'gate_methodology_completeness',
        'path': 'quality/gate_methodology_completeness.json',
        'kind': 'file',
        'require_grades': ['G3', 'G4', 'G5'],
        'require_domains': None,  # 도메인 매칭 여부는 본 JSON 안의 domain_matched 가 결정
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
        'allow_skip_when': 'domain_matched',  # 본 JSON 안 domain_matched=false 시 skip 허용
    },
    # sprint-39 4 패턴 게이트 + sprint-40 PR-E auto-emit
    {
        'id': 'gate_pnc',
        'path': 'quality/gate_pnc.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    {
        'id': 'gate_mirror',
        'path': 'quality/gate_mirror.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    {
        'id': 'gate_primary',
        'path': 'quality/gate_primary.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    {
        'id': 'gate_literal',
        'path': 'quality/gate_literal.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    # sprint-40 PR-F G-3 (modeling shortcuts)
    {
        'id': 'modeling_shortcuts',
        'path': 'intent/modeling_shortcuts.json',
        'kind': 'file',
        'require_grades': ['G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    {
        'id': 'cascaded_subq',
        'path': 'intent/04-cascaded-subq.md',
        'kind': 'file',
        'require_grades': ['G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': None,  # markdown — 존재만 검사
        'require_verdict_pass': False,
    },
    # sprint-40 PR-C M-2 (phase 12 종료 게이트)
    {
        'id': 'webview_exit_gate',
        'path': 'webview/exit_gate.json',
        'kind': 'file',
        'require_grades': ['G2', 'G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
    },
    # sprint-40 PR-C M-2 (phase 13 종료 게이트, G3+ 의무)
    {
        'id': 'interactive_viewer_exit_gate',
        'path': 'interactive-viewer/exit_gate.json',
        'kind': 'file',
        'require_grades': ['G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': 'verdict',
        'require_verdict_pass': True,
        'allow_skip_when': 'g2_domain_unmatched',  # G2 + 도메인 미매칭 시 skip
    },
    # sprint-36 v0.9.41 (interactive-viewer dashboard)
    {
        'id': 'interactive_viewer_dashboard',
        'path': 'interactive-viewer/dashboard.json',
        'kind': 'file',
        'require_grades': ['G3', 'G4', 'G5'],
        'require_domains': None,
        'verdict_field': None,  # schema valid 만 검사 (별도 함수)
        'require_verdict_pass': False,
        'allow_skip_when': 'g2_domain_unmatched',
    },
]


def get_dotted(obj: Any, path: str) -> Any:
    """obj 의 'a.b.c' 경로 값 추출. 부재 시 sentinel _MISSING."""
    cur = obj
    for key in path.split('.'):
        if isinstance(cur, dict) and key in cur:
            cur = cur[key]
        else:
            return None
    return cur


def check_artefact(
    project_root: Path,
    spec: dict[str, Any],
    grade: str,
    domain_matched: bool,
) -> dict[str, Any]:
    """단일 산출물 검사."""
    path = project_root / spec['path']
    require_grades = spec.get('require_grades', ['G2', 'G3', 'G4', 'G5'])

    # grade 필터
    if grade not in require_grades:
        return {
            'id': spec['id'],
            'path': spec['path'],
            'required': False,
            'skipped': True,
            'skip_reason': f"grade {grade} not in {require_grades}",
        }

    # allow_skip_when 처리
    skip_marker = spec.get('allow_skip_when')
    if skip_marker == 'g2_domain_unmatched' and grade == 'G2' and not domain_matched:
        return {
            'id': spec['id'],
            'path': spec['path'],
            'required': False,
            'skipped': True,
            'skip_reason': 'G2 + domain unmatched',
        }

    base = {
        'id': spec['id'],
        'path': spec['path'],
        'required': True,
        'skipped': False,
        'exists': path.exists(),
        'size': path.stat().st_size if path.exists() else 0,
    }

    if not path.exists():
        return {**base, 'verdict': 'fail', 'reason': 'file 부재'}

    if path.stat().st_size == 0:
        return {**base, 'verdict': 'fail', 'reason': 'file size 0'}

    # JSON valid 검사
    if path.suffix == '.json':
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
            base['valid_json'] = True
        except json.JSONDecodeError as e:
            return {**base, 'valid_json': False, 'verdict': 'fail', 'reason': f'invalid JSON: {e}'}
    else:
        data = None
        base['valid_json'] = None

    # allow_skip_when=domain_matched (gate_methodology_completeness) — 본 JSON 안 domain_matched=false 시 skip 허용
    if skip_marker == 'domain_matched' and data is not None:
        if data.get('domain_matched') is False:
            return {**base, 'verdict': 'skip', 'skip_reason': 'JSON domain_matched=false'}

    # verdict_field 검사
    verdict_field = spec.get('verdict_field')
    if verdict_field and data is not None:
        verdict_val = get_dotted(data, verdict_field)
        base['verdict_value'] = verdict_val
        if spec.get('require_verdict_pass') and verdict_val != 'pass':
            return {
                **base,
                'verdict': 'fail',
                'reason': f"verdict='{verdict_val}' != 'pass'",
            }

    return {**base, 'verdict': 'pass'}


def evaluate(
    project_root: Path,
    grade: str,
    domain: str | None,
    domain_matched: bool,
) -> dict[str, Any]:
    """13 산출물 종합 검사."""
    checks = []
    missing = []
    invalid = []
    verdict_fail = []

    for spec in ARTEFACTS:
        result = check_artefact(project_root, spec, grade, domain_matched)
        checks.append(result)
        if result.get('skipped'):
            continue
        if not result.get('exists'):
            missing.append(spec['path'])
        elif result.get('valid_json') is False:
            invalid.append(spec['path'])
        elif result.get('verdict') == 'fail':
            verdict_fail.append(spec['path'])

    overall_pass = not missing and not invalid and not verdict_fail

    return {
        'schema_version': SCHEMA_VERSION,
        'project_root': str(project_root),
        'grade': grade,
        'domain': domain,
        'domain_matched': domain_matched,
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'checks': checks,
        'missing': missing,
        'invalid': invalid,
        'verdict_fail': verdict_fail,
        'verdict': 'pass' if overall_pass else 'fail',
        'reason': (
            f"all 13 sprint-40 산출물 통과"
            if overall_pass
            else (
                f"missing: {len(missing)} / invalid: {len(invalid)} / verdict fail: {len(verdict_fail)}"
            )
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='cold_session_artefacts',
        description=(
            'Sprint-40 13 신규 산출물 file-existence 강제 CLI — phase 09 진입 직전 '
            '의무 호출. HARD-RULE 9.rr (sprint-41).'
        ),
    )
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument(
        '--grade',
        choices=['G2', 'G3', 'G4', 'G5'],
        required=True,
    )
    parser.add_argument(
        '--domain',
        help='도메인 식별자 (e.g., DES / ML / API / ETL). default: None',
    )
    parser.add_argument(
        '--domain-matched',
        action='store_true',
        help='domain 이 도메인 카탈로그와 매칭 (G2 + 미매칭 시 viewer skip 허용)',
    )
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    if not ns.project_root.exists():
        print(f'ERROR: project-root 미존재: {ns.project_root}', file=sys.stderr)
        return 2

    verdict_obj = evaluate(
        ns.project_root,
        ns.grade,
        ns.domain,
        ns.domain_matched,
    )

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[cold_session_artefacts] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        if verdict_obj['missing']:
            print(f"  missing 산출물 ({len(verdict_obj['missing'])}):", file=sys.stderr)
            for p in verdict_obj['missing']:
                print(f"    - {p}", file=sys.stderr)
        if verdict_obj['invalid']:
            print(f"  invalid JSON ({len(verdict_obj['invalid'])}):", file=sys.stderr)
            for p in verdict_obj['invalid']:
                print(f"    - {p}", file=sys.stderr)
        if verdict_obj['verdict_fail']:
            print(f"  verdict fail ({len(verdict_obj['verdict_fail'])}):", file=sys.stderr)
            for p in verdict_obj['verdict_fail']:
                print(f"    - {p}", file=sys.stderr)
        print(
            f"\n[cold_session_artefacts] orchestrator 의무 — 결손 emit 후 phase 09 재진입 (HARD-RULE 9.rr).",
            file=sys.stderr,
        )

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
