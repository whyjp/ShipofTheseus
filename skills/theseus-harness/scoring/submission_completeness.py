"""submission_completeness.py — 평가 직후 산출물 disk 잔존 검증 CLI (sprint-43 PR-B v0.9.48).

본 스크립트는 *evaluation_report.json* 의 `automated_checks.checks` 안 `output_exists_*` 가
true 인 모든 파일이 *현재* disk 에 잔존 검증. `.pyc-only` 패턴 (cache 만 남고 source 삭제)
차단. orchestrator 가 phase 14 handoff *직후* 의무 호출 (HARD-RULE 9.yy).

증거 회피 사례 (g4-v2 91 회차):
    submissions/.../theseus-orchestrator-g4-v2/ = 10 .pyc 파일만 (README/submission.yaml/
    conceptual_model/run_experiment/outputs/.ShipofTheseus 모두 부재). 평가 시점 (output_exists_*
    pass) 후 *대량 삭제*. 본 CLI = 차단.

사용:
    python submission_completeness.py \\
        --submission-dir submissions/<id>/ \\
        --eval-report submissions/<id>/results/evaluation_report.json \\
        --grade G4 \\
        --output submissions/<id>/results/gate_submission_completeness.json

Exit codes:
    0 — 평가 시 존재했던 모든 산출물이 *현재* disk 잔존
    1 — 일부 missing OR `.pyc-only` 패턴 OR governance trail 부재 (G3+)
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.48"


# evaluation_report.json 의 output_exists_<NAME> 체크 → 실 disk 경로 매핑
# 본 매핑은 simulation-bench 001 류 일반 패턴 — 도메인 차이 시 override 가능
OUTPUT_EXISTS_MAPPINGS = {
    'output_exists_conceptual_model.md': 'conceptual_model.md',
    'output_exists_README.md': 'README.md',
    'output_exists_results.csv': 'outputs/results.csv',
    'output_exists_summary.json': 'outputs/summary.json',
    'output_exists_event_log.csv': 'outputs/event_log.csv',
}


def parse_eval_report(path: Path) -> dict[str, Any]:
    """evaluation_report.json 파싱 + output_exists checks 추출."""
    if not path.exists():
        return {'eval_report_present': False, 'output_exists_checks': []}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        return {'eval_report_present': False, 'parse_error': str(e), 'output_exists_checks': []}

    checks = data.get('automated_checks', {}).get('checks', [])
    output_exists = [c for c in checks if c.get('name', '').startswith('output_exists_')]
    return {
        'eval_report_present': True,
        'eval_report_passed': data.get('automated_checks', {}).get('passed'),
        'eval_report_total': data.get('automated_checks', {}).get('total'),
        'output_exists_checks': output_exists,
    }


def list_disk_files(submission_dir: Path) -> dict[str, Any]:
    """submission_dir 안의 파일 분류."""
    if not submission_dir.exists():
        return {
            'dir_exists': False,
            'total_files': 0,
            'pyc_count': 0,
            'py_count': 0,
            'md_count': 0,
            'json_count': 0,
            'yaml_count': 0,
            'other_count': 0,
        }

    counts = {'pyc': 0, 'py': 0, 'md': 0, 'json': 0, 'yaml': 0, 'other': 0}
    for p in submission_dir.rglob('*'):
        if not p.is_file():
            continue
        suffix = p.suffix.lower().lstrip('.')
        if suffix == 'pyc':
            counts['pyc'] += 1
        elif suffix == 'py':
            counts['py'] += 1
        elif suffix == 'md':
            counts['md'] += 1
        elif suffix == 'json':
            counts['json'] += 1
        elif suffix in ('yaml', 'yml'):
            counts['yaml'] += 1
        else:
            counts['other'] += 1

    return {
        'dir_exists': True,
        'total_files': sum(counts.values()),
        'pyc_count': counts['pyc'],
        'py_count': counts['py'],
        'md_count': counts['md'],
        'json_count': counts['json'],
        'yaml_count': counts['yaml'],
        'other_count': counts['other'],
    }


def evaluate(
    submission_dir: Path,
    eval_report_path: Path,
    grade: str = 'G4',
    survival_threshold: float = 0.5,
) -> dict[str, Any]:
    eval_info = parse_eval_report(eval_report_path)
    disk_info = list_disk_files(submission_dir)

    # 1. .pyc-only 패턴 — pyc > 0 + (py + md + yaml) == 0
    # (eval_report.json 같은 .json 은 허용 — source 부재 만 차단)
    pyc_only = (
        disk_info['pyc_count'] > 0
        and (disk_info['py_count'] + disk_info['md_count']
             + disk_info['yaml_count']) == 0
    )

    # 2. 평가 시 존재했던 산출물 잔존 검증
    output_exists_checks = eval_info.get('output_exists_checks', [])
    survival_results = []
    for c in output_exists_checks:
        if not c.get('passed'):
            continue  # 평가 시에도 부재 — skip
        rel_path = OUTPUT_EXISTS_MAPPINGS.get(c['name'])
        if rel_path is None:
            continue  # mapping 없음
        full_path = submission_dir / rel_path
        survival_results.append({
            'check_name': c['name'],
            'rel_path': rel_path,
            'eval_passed': True,
            'currently_exists': full_path.exists(),
        })

    eval_pass_count = len(survival_results)
    currently_exists_count = sum(1 for r in survival_results if r['currently_exists'])
    survival_ratio = (
        currently_exists_count / eval_pass_count if eval_pass_count > 0 else 1.0
    )
    missing_after_eval = [r for r in survival_results if not r['currently_exists']]

    # 3. governance trail (G3+)
    governance_dir = submission_dir / '.ShipofTheseus'
    governance_present = governance_dir.exists() and any(governance_dir.iterdir())
    governance_violation = grade in ('G3', 'G4', 'G5') and not governance_present

    violations = []
    if pyc_only:
        violations.append({
            'kind': 'pyc_only',
            'reason': f"submission disk 에 .pyc {disk_info['pyc_count']} 만 존재. .py/.md/.json/.yaml 0 — 평가 후 대량 삭제 또는 cache cleanup 결손",
        })
    if eval_pass_count > 0 and survival_ratio < survival_threshold:
        violations.append({
            'kind': 'low_survival_ratio',
            'reason': f"eval 시 존재했던 산출물 잔존 ratio {survival_ratio:.2%} < {survival_threshold:.0%}",
            'missing': [r['rel_path'] for r in missing_after_eval],
        })
    if governance_violation:
        violations.append({
            'kind': 'governance_trail_missing',
            'reason': f"grade {grade} 의무 governance trail (.ShipofTheseus/) 부재",
        })

    overall_pass = len(violations) == 0

    return {
        'schema_version': SCHEMA_VERSION,
        'submission_dir': str(submission_dir),
        'eval_report': str(eval_report_path),
        'grade': grade,
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'eval_info': eval_info,
        'disk_info': disk_info,
        'survival_check': {
            'eval_passed_outputs': eval_pass_count,
            'currently_present': currently_exists_count,
            'survival_ratio': round(survival_ratio, 4),
            'threshold': survival_threshold,
            'missing_after_eval': [r['rel_path'] for r in missing_after_eval],
        },
        'governance_trail_present': governance_present,
        'pyc_only_pattern': pyc_only,
        'violations': violations,
        'verdict': 'pass' if overall_pass else 'fail',
        'reason': (
            'submission completeness OK'
            if overall_pass
            else f"{len(violations)} violation"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='submission_completeness',
        description=(
            '평가 직후 산출물 disk 잔존 검증 CLI — .pyc-only 패턴 + 산출물 대량 삭제 차단. '
            'HARD-RULE 9.yy (sprint-43).'
        ),
    )
    parser.add_argument('--submission-dir', type=Path, required=True)
    parser.add_argument('--eval-report', type=Path, required=True)
    parser.add_argument('--grade', choices=['G2', 'G3', 'G4', 'G5'], default='G4')
    parser.add_argument('--survival-threshold', type=float, default=0.5)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    verdict_obj = evaluate(
        ns.submission_dir,
        ns.eval_report,
        ns.grade,
        ns.survival_threshold,
    )

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[submission_completeness] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        for v in verdict_obj['violations']:
            print(f"  - [{v['kind']}] {v['reason']}", file=sys.stderr)

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
