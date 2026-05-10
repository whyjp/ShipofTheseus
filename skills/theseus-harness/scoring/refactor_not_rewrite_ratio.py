"""refactor_not_rewrite_ratio.py — Refactor-not-Rewrite ratio CLI (sprint-50 PR-F v0.9.50).

본 스크립트는 Hunt & Thomas, *The Pragmatic Programmer*, Ch.6 — *"Refactoring"*
의 enforcement. sprint loop 의 *개선* 이 *기존 함수/모듈 변경* 비율 ≥ 신규 추가 의무.
*전부 추가만* 하는 sprint = 진짜 refactoring 아님.

측정: git diff --stat <baseline>..HEAD 의 +/- 카운트.
- additions: 새로 추가된 줄
- deletions: 제거된 줄 = *변경* 의 일부 (replace = delete + add)
- modified ratio = deletions / (deletions + additions)

vacuous PASS 차단 (premortem §3-5):
- additions = 0 AND deletions = 0 = vacuous PASS = automatic fail (sprint 변화 0).
- 임계: modified ratio ≥ 0.3 (즉 변경:추가 ≈ 1:3 이상).

격언:
    Hunt & Thomas: "Refactoring is not the same as writing new code—you have a
    rhythm of small, behavior-preserving changes."

사용:
    python refactor_not_rewrite_ratio.py \\
        --git-root <repo> \\
        --baseline <commit-sha-or-ref> \\
        --min-modified-ratio 0.3

Exit codes:
    0 — modified ratio ≥ τ AND total diff > 0
    1 — 미달 (전부 신규 추가 또는 변화 0)
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
from pathlib import Path


if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.50"


# git diff --shortstat 형식: " 5 files changed, 23 insertions(+), 8 deletions(-)"
SHORTSTAT_RE = re.compile(
    r'(\d+)\s+insertions?\(\+\).*?(\d+)\s+deletions?\(-\)'
    r'|(\d+)\s+insertions?\(\+\)'
    r'|(\d+)\s+deletions?\(-\)',
    re.DOTALL,
)


def get_diff_stats(git_root: Path, baseline: str, head: str = 'HEAD') -> dict:
    try:
        result = subprocess.run(
            ['git', '-C', str(git_root), 'diff', '--shortstat',
             f'{baseline}..{head}'],
            capture_output=True, text=True, timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {'error': str(e), 'additions': 0, 'deletions': 0}

    out = result.stdout.strip()
    if not out:
        return {'additions': 0, 'deletions': 0, 'raw': ''}

    additions = 0
    deletions = 0
    insert_m = re.search(r'(\d+)\s+insertions?\(\+\)', out)
    delete_m = re.search(r'(\d+)\s+deletions?\(-\)', out)
    if insert_m:
        additions = int(insert_m.group(1))
    if delete_m:
        deletions = int(delete_m.group(1))

    return {'additions': additions, 'deletions': deletions, 'raw': out}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--git-root', type=Path, default=None)
    parser.add_argument('--baseline', type=str, default=None,
                        help='baseline commit/ref (e.g. sprint-loop-start commit)')
    parser.add_argument('--head', type=str, default='HEAD')
    parser.add_argument('--min-modified-ratio', type=float, default=0.3,
                        help='deletions / (deletions + additions) ≥ τ')
    parser.add_argument('--allow-zero-diff', action='store_true', default=False,
                        help='additions=deletions=0 도 PASS (default OFF — vacuous 차단)')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.git_root is None:
        parser.error('--git-root required when not --self-test')
    if args.baseline is None:
        parser.error('--baseline required when not --self-test')

    stats = get_diff_stats(args.git_root, args.baseline, args.head)
    additions = stats.get('additions', 0)
    deletions = stats.get('deletions', 0)
    total = additions + deletions

    failures: list[str] = []

    if total == 0 and not args.allow_zero_diff:
        failures.append('zero diff — vacuous PASS 차단 (sprint 변화 0)')

    modified_ratio = deletions / total if total else 0.0
    if total > 0 and modified_ratio < args.min_modified_ratio:
        failures.append(
            f'modified ratio {modified_ratio:.3f} < min '
            f'{args.min_modified_ratio} '
            f'(additions={additions}, deletions={deletions})'
        )

    report = {
        'schema_version': SCHEMA_VERSION,
        'pass': not failures,
        'baseline': args.baseline,
        'head': args.head,
        'additions': additions,
        'deletions': deletions,
        'modified_ratio': round(modified_ratio, 3),
        'failures': failures,
        'raw': stats.get('raw', ''),
        'error': stats.get('error'),
    }
    _emit(report, args.json_out)

    if failures:
        print(f'FAIL: refactor-not-rewrite ({len(failures)} 결손)', file=sys.stderr)
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    print(
        f'PASS: refactor-not-rewrite '
        f'(additions={additions} deletions={deletions} ratio={modified_ratio:.3f})'
    )
    return 0


def _emit(report: dict, out: Path | None) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')


def _self_test() -> int:
    sample = ' 5 files changed, 23 insertions(+), 8 deletions(-)'
    insert_m = re.search(r'(\d+)\s+insertions?\(\+\)', sample)
    delete_m = re.search(r'(\d+)\s+deletions?\(-\)', sample)
    assert insert_m and int(insert_m.group(1)) == 23
    assert delete_m and int(delete_m.group(1)) == 8
    ratio = 8 / (8 + 23)
    assert 0.2 < ratio < 0.3, f'expected ~0.258, got {ratio}'
    print(f'SELF-TEST PASS — refactor-not-rewrite parser (ratio={ratio:.3f})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
