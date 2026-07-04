"""refactor_not_rewrite_ratio.py — Refactor-not-Rewrite ratio CLI (sprint-50 PR-F v0.9.50, sprint-51 PR-F sprint_type 확장).

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

sprint-51 PR-F 확장 — sprint_type frontmatter 인식:
sprint plan / report frontmatter 의 `sprint_type` 필드 자동 검출 → type 별 적용 여부:
- `sprint_type: rule-addition` → skip (적용 대상 외, 본 sprint 50/51 같은 룰 추가 sprint)
- `sprint_type: refactoring` / `feature` / `bug-fix` → modified ratio ≥ τ 적용
- frontmatter 부재 또는 unknown type → 보수적 적용 (기본 동작)

격언:
    Hunt & Thomas: "Refactoring is not the same as writing new code—you have a
    rhythm of small, behavior-preserving changes."

사용:
    python refactor_not_rewrite_ratio.py \\
        --git-root <repo> \\
        --baseline <commit-sha-or-ref> \\
        --sprint-plan-file <sprint-N/plan.md>  (optional, sprint_type 자동 검출)
        --min-modified-ratio 0.3

Exit codes:
    0 — modified ratio ≥ τ AND total diff > 0 / OR sprint_type=rule-addition skip
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


SCHEMA_VERSION = "0.9.51"


# git diff --shortstat 형식: " 5 files changed, 23 insertions(+), 8 deletions(-)"
SHORTSTAT_RE = re.compile(
    r'(\d+)\s+insertions?\(\+\).*?(\d+)\s+deletions?\(-\)'
    r'|(\d+)\s+insertions?\(\+\)'
    r'|(\d+)\s+deletions?\(-\)',
    re.DOTALL,
)


# sprint plan / report frontmatter 의 sprint_type 검출
SPRINT_TYPE_RE = re.compile(
    r'^sprint_type\s*:\s*(rule-addition|refactoring|feature|bug-fix|docs|chore)\s*$',
    re.MULTILINE | re.IGNORECASE,
)


# Allowed sprint_type catalog
ALLOWED_SPRINT_TYPES = {
    'rule-addition',  # 본 CLI skip 대상 (sprint-50/51 같은 컨벤션/CLI 추가 sprint)
    'refactoring',    # 본 CLI 적용
    'feature',        # 본 CLI 적용
    'bug-fix',        # 본 CLI 적용
    'docs',           # 보수적 — modified 검사 skip 가능
    'chore',          # 보수적
}


# Skip 대상 — 본 CLI 가 적용되지 않는 sprint type
SKIP_SPRINT_TYPES = {'rule-addition', 'docs', 'chore'}


def detect_sprint_type(plan_path: Path | None) -> str | None:
    """sprint plan / report frontmatter 에서 sprint_type 검출.

    plan_path 가 dir 인 경우 plan.md / report.md 자동 검색.
    """
    if plan_path is None or not plan_path.exists():
        return None
    if plan_path.is_dir():
        for fname in ('plan.md', 'report.md', 'sprint.md'):
            candidate = plan_path / fname
            if candidate.exists():
                plan_path = candidate
                break
        else:
            return None
    try:
        body = plan_path.read_text(encoding='utf-8', errors='replace')
    except (FileNotFoundError, IsADirectoryError, PermissionError):
        return None
    m = SPRINT_TYPE_RE.search(body)
    if m:
        return m.group(1).lower()
    return None


def get_diff_stats(git_root: Path, baseline: str, head: str = 'HEAD') -> dict:
    try:
        result = subprocess.run(
            ['git', '-C', str(git_root), 'diff', '--shortstat',
             f'{baseline}..{head}'],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
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
    parser.add_argument('--sprint-plan-file', type=Path, default=None,
                        help='sprint plan / report 또는 sprint dir — frontmatter 의 '
                             'sprint_type 자동 검출. rule-addition / docs / chore = skip')
    parser.add_argument('--sprint-type', type=str, default=None,
                        choices=sorted(ALLOWED_SPRINT_TYPES),
                        help='sprint_type 직접 명시 (--sprint-plan-file 보다 우선)')
    parser.add_argument('--self-test', action='store_true', default=False)
    parser.add_argument('--json-out', type=Path, default=None)
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.git_root is None:
        parser.error('--git-root required when not --self-test')
    if args.baseline is None:
        parser.error('--baseline required when not --self-test')

    # sprint_type 결정 — flag > frontmatter > None
    sprint_type = args.sprint_type or detect_sprint_type(args.sprint_plan_file)

    if sprint_type and sprint_type in SKIP_SPRINT_TYPES:
        report = {
            'schema_version': SCHEMA_VERSION,
            'pass': True,
            'sprint_type': sprint_type,
            'note': f'sprint_type={sprint_type} — refactor ratio 적용 대상 외 (skip)',
        }
        _emit(report, args.json_out)
        print(f'PASS: refactor-not-rewrite (sprint_type={sprint_type} — skip)')
        return 0

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
        'sprint_type': sprint_type,
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
        f'(sprint_type={sprint_type or "unknown"} '
        f'additions={additions} deletions={deletions} ratio={modified_ratio:.3f})'
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

    # sprint_type frontmatter 검출
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        plan = Path(d) / 'plan.md'
        plan.write_text('---\nname: Sprint-50\nsprint_type: rule-addition\n---\n# x',
                        encoding='utf-8')
        st = detect_sprint_type(plan)
        assert st == 'rule-addition', f'expected rule-addition, got {st}'

        plan2 = Path(d) / 'plan2.md'
        plan2.write_text('---\nname: Sprint-N\nsprint_type: refactoring\n---\n# x',
                        encoding='utf-8')
        st2 = detect_sprint_type(plan2)
        assert st2 == 'refactoring', f'expected refactoring, got {st2}'

        plan3 = Path(d) / 'plan3.md'
        plan3.write_text('---\nname: Sprint-N\n---\n# no sprint_type',
                        encoding='utf-8')
        st3 = detect_sprint_type(plan3)
        assert st3 is None, f'expected None, got {st3}'

    print(f'SELF-TEST PASS — refactor-not-rewrite '
          f'(parser ratio={ratio:.3f}, sprint_type detection ✅)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
