"""dashboard_submission_parity.py — dashboard ↔ submission disk 일치 검증 CLI (sprint-43 PR-D).

본 스크립트는 dashboard md (`dashboard/src/content/submissions/<id>.md`) 의 `files:`
항목과 submission disk 의 실 파일 list 일치 검증. dashboard 가 *과거 상태* 보존하고
disk 가 *현재 상태* 보존 — 둘이 어긋나면 *데이터 무결성 실패*.

orchestrator 가 dashboard sync *직후* 의무 호출 (HARD-RULE 9.aaa).

증거 회피 사례 (g4-v2 91 회차):
    dashboard md 가 9 source path 명시 (config.py / model.py / experiment.py 등),
    submission disk 에 0 잔존. dashboard 가 *과거 상태* 만 박혀 있음 — 본 CLI = 차단.

사용:
    python dashboard_submission_parity.py \\
        --submission-dir submissions/<id>/ \\
        --dashboard-md dashboard/src/content/submissions/<id>.md \\
        --output results/gate_dashboard_parity.json

Exit codes:
    0 — dashboard files: ↔ disk 일치
    1 — missing on disk OR untracked on dashboard
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


# dashboard md 의 `files:` 블록 안 `path: "..."` 추출
DASHBOARD_FILE_PATH_PATTERN = re.compile(
    r'^\s*-\s*path:\s*["\']([^"\']+)["\']',
    re.MULTILINE,
)

# legitimate cleanup — submission disk 에 있어도 dashboard tracked 아닌 OK
LEGITIMATE_DISK_ONLY = {
    '__pycache__',
    '.pytest_cache',
    '.ruff_cache',
}


def parse_dashboard_files(md_path: Path) -> dict[str, Any]:
    """dashboard md 의 files: 블록에서 path list 추출."""
    if not md_path.exists():
        return {'present': False, 'declared_paths': []}

    text = md_path.read_text(encoding='utf-8', errors='ignore')
    paths = DASHBOARD_FILE_PATH_PATTERN.findall(text)
    return {
        'present': True,
        'dashboard_md': str(md_path),
        'declared_paths': sorted(set(paths)),
    }


def list_submission_files(submission_dir: Path) -> list[str]:
    """submission_dir 안 모든 파일 (legitimate cleanup 제외)."""
    if not submission_dir.exists():
        return []
    files: list[str] = []
    for p in submission_dir.rglob('*'):
        if not p.is_file():
            continue
        rel = p.relative_to(submission_dir).as_posix()
        if any(part in LEGITIMATE_DISK_ONLY for part in p.parts):
            continue
        files.append(rel)
    return sorted(files)


def evaluate(
    submission_dir: Path,
    dashboard_md: Path,
) -> dict[str, Any]:
    dash_info = parse_dashboard_files(dashboard_md)

    if not dash_info['present']:
        return {
            'schema_version': SCHEMA_VERSION,
            'submission_dir': str(submission_dir),
            'dashboard_md': str(dashboard_md),
            'verdict': 'fail',
            'reason': 'dashboard md 미존재',
        }

    declared = set(dash_info['declared_paths'])
    disk = set(list_submission_files(submission_dir))

    missing_on_disk = sorted(declared - disk)
    untracked_on_dashboard = sorted(disk - declared)

    violations = []
    if missing_on_disk:
        violations.append({
            'kind': 'missing_on_disk',
            'count': len(missing_on_disk),
            'paths': missing_on_disk[:20],  # cap
            'reason': f"dashboard 에 declared, submission disk 에 부재: {len(missing_on_disk)} 파일",
        })
    if untracked_on_dashboard:
        # untracked 는 less critical — warning 등급 (별 violation 분리 가능, 본 버전은 violation 으로 처리)
        violations.append({
            'kind': 'untracked_on_dashboard',
            'count': len(untracked_on_dashboard),
            'paths': untracked_on_dashboard[:20],
            'reason': f"submission disk 에 존재, dashboard 미tracked: {len(untracked_on_dashboard)} 파일",
        })

    overall_pass = len(missing_on_disk) == 0  # untracked 는 warning 만, fail 안함

    return {
        'schema_version': SCHEMA_VERSION,
        'submission_dir': str(submission_dir),
        'dashboard_md': str(dashboard_md),
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'declared_count': len(declared),
        'disk_count': len(disk),
        'missing_on_disk_count': len(missing_on_disk),
        'untracked_on_dashboard_count': len(untracked_on_dashboard),
        'missing_on_disk': missing_on_disk,
        'untracked_on_dashboard': untracked_on_dashboard,
        'violations': violations,
        'verdict': 'pass' if overall_pass else 'fail',
        'reason': (
            'dashboard ↔ disk parity OK (untracked warning 가능)'
            if overall_pass
            else f"dashboard 에 declared {len(declared)} 파일 중 {len(missing_on_disk)} 가 disk 에 부재"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='dashboard_submission_parity',
        description=(
            'dashboard ↔ submission disk 일치 검증 CLI — missing on disk 차단. '
            'HARD-RULE 9.aaa (sprint-43).'
        ),
    )
    parser.add_argument('--submission-dir', type=Path, required=True)
    parser.add_argument('--dashboard-md', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--quiet', action='store_true')

    ns = parser.parse_args(argv)

    verdict_obj = evaluate(ns.submission_dir, ns.dashboard_md)

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[dashboard_submission_parity] FAIL: {verdict_obj['reason']}",
            file=sys.stderr,
        )
        for v in verdict_obj.get('violations', []):
            if v['kind'] == 'missing_on_disk':
                print(f"  - missing on disk ({v['count']}):", file=sys.stderr)
                for p in v['paths']:
                    print(f"      - {p}", file=sys.stderr)

    return 0 if verdict_obj['verdict'] == 'pass' else 1


if __name__ == '__main__':
    sys.exit(main())
