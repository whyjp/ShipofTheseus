"""dacapo_threshold.py — Tournament 다카포 임계 강제 CLI (sprint-41 PR-B v0.9.46).

본 스크립트는 *cold session* 의 tournament 산출물 (`plan/tournament-NN.md`,
`impl/tournament-impl-NN.md`) 의 winner 점수를 추출 → ratio 계산 → < 0.999 임계 시
exit 1 + stderr "round N+1 강제" 메시지. orchestrator 가 phase 06/08 종료 직전
의무 호출 (HARD-RULE 9.qq, sprint-41 신규).

사용:
    # phase 06 plan tournament 후
    python dacapo_threshold.py \\
        --tournament-md .ShipofTheseus/<proj>/plan/tournament-01.md \\
        --threshold 0.999 \\
        --output .ShipofTheseus/<proj>/plan/dacapo_threshold.json

    # phase 08 impl tournament 후
    python dacapo_threshold.py \\
        --tournament-md .ShipofTheseus/<proj>/impl/tournament-impl-01.md \\
        --threshold 0.999

보고 모드(설계 B2 §2.3, default) — `--threshold` 미지정 시 exit 0 + ratio 보고(비게이팅).
도달 불가 임계(0.999)를 종료 게이트로 두던 perverse incentive 를 제거한다. winner ratio 는
계속 측정·보고되지만 절대값이 종료·차단 게이트가 아니다. 재경합 결정은 delta 룰(직전 라운드
대비 개선 실측) + budget cap 으로 이동하며, 종료 판정 권위는 manifest `stop_policy`(§2.2)다.
`--threshold` 를 명시하면(능력 보존) 예전 게이팅 동작(ratio<threshold → exit 1) 복원.

Exit codes:
    default(보고 모드, --threshold 미지정): 항상 0 (ratio 는 stdout JSON 으로 보고)
    --threshold 지정 시(gating opt-in):
        0 — winner ratio ≥ threshold
        1 — winner ratio < threshold

본 CLI 가 컨벤션 [`intra-phase-dacapo-loop.md`](../conventions/intra-phase-dacapo-loop.md)
의 *임계 0.999 까지 재경합* 룰의 *런타임 집행* 메커니즘. 컨벤션 본문 = 명세, 본 CLI
= 집행. agent 자율 skip 불가.

증거 회피 사례 (0510 회차):
    impl/tournament-impl-01.md winner 57/60 = 0.95 < 0.999 임계 → round 2 = 0
    자율 종료. 본 CLI 활성 시 exit 1 → orchestrator 가 round 2 자동 진행.

References:
- sprint-15 (intra-phase-dacapo-loop bl)
- sprint-16 (HARD-RULE 9.o, 임계 0.999)
- sprint-41 (본 PR-B, runtime guard CLI)
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


# Windows cp949 회피 — stdout/stderr UTF-8 강제 (한글 출력)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


SCHEMA_VERSION = "0.9.46"
DEFAULT_THRESHOLD = 0.999


# Tournament 본문 winner 추출 패턴 — 3 source priority
#   1. frontmatter `winner_score` + `winner_max`
#   2. 본문 `| **Total** | ... | **N/M** |` 또는 유사 표 행
#   3. 본문 `## Winner` 절 안의 "Combined ... wins" 류 + 인접 표 행
WINNER_TOTAL_ROW = re.compile(
    r'^\s*\|\s*\*?\*?Total\*?\*?\s*\|.*?\|\s*\*?\*?(\d+)\s*/\s*(\d+)\*?\*?\s*\|',
    re.MULTILINE,
)

# fallback: 본문 어디든 "winner ... N/M" 패턴 (최대값)
WINNER_NM_PATTERN = re.compile(
    r'(?:winner|combined|wins|final|locked)[\s\S]{0,200}?(\d+)\s*/\s*(\d+)',
    re.IGNORECASE,
)

FRONTMATTER_PATTERN = re.compile(
    r'^---\s*\n(.*?)\n---\s*\n',
    re.DOTALL,
)


def parse_frontmatter(text: str) -> dict[str, str]:
    """frontmatter 의 단순 key: value 파싱 (yaml 의존 회피)."""
    m = FRONTMATTER_PATTERN.match(text)
    if not m:
        return {}
    body = m.group(1)
    out = {}
    for line in body.split('\n'):
        line = line.strip()
        if ':' not in line or line.startswith('#'):
            continue
        key, _, val = line.partition(':')
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def extract_winner_score(text: str) -> tuple[int, int, str] | None:
    """본문에서 winner score / max 추출. (score, max, source) 반환 또는 None.

    Priority:
        1. frontmatter `winner_score` + `winner_max`
        2. `| **Total** | ... | **57/60** |` 표 행 — 마지막 row 의 *최대* N/M
        3. fallback: "winner ... wins" 인접 N/M 패턴
    """
    fm = parse_frontmatter(text)
    if 'winner_score' in fm and 'winner_max' in fm:
        try:
            return int(fm['winner_score']), int(fm['winner_max']), 'frontmatter'
        except ValueError:
            pass

    # Priority 2 — Total row (winner column = max N/M in row)
    rows = WINNER_TOTAL_ROW.findall(text)
    if rows:
        # 모든 Total row 의 (N, M) 중 *최대 N/M ratio* 인 것 (winner column)
        # 단순화: 각 Total row 의 마지막 N/M 만 추출 (winner column 가장 오른쪽 가정)
        # → 정규식이 첫 N/M 만 잡으므로, line 별 모든 N/M 재추출
        for line_match in re.finditer(r'^\s*\|\s*\*?\*?Total\*?\*?\s*\|.*$', text, re.MULTILINE):
            line = line_match.group(0)
            nm_pairs = re.findall(r'(\d+)\s*/\s*(\d+)', line)
            if nm_pairs:
                # winner = 가장 오른쪽 N/M (cross-universe combined column 가정)
                # 또는 가장 큰 ratio
                best = max(nm_pairs, key=lambda nm: int(nm[0]) / max(int(nm[1]), 1))
                return int(best[0]), int(best[1]), 'total_row_max_ratio'

    # Priority 3 — fallback "winner ... N/M"
    fb = WINNER_NM_PATTERN.search(text)
    if fb:
        return int(fb.group(1)), int(fb.group(2)), 'fallback_winner_pattern'

    return None


def evaluate(
    tournament_md: Path,
    threshold: float | None = None,
    score_text_override: str | None = None,
) -> dict[str, Any]:
    """tournament-NN.md 본문 → verdict JSON.

    threshold 가 None(default)이면 보고 모드 — ratio 를 측정·보고하되 verdict='report'
    (비게이팅). threshold 를 명시하면 예전 gating(ratio<threshold → verdict 'fail') 복원.
    """
    reporting = threshold is None
    if score_text_override:
        m = re.match(r'^(\d+)\s*/\s*(\d+)\s*$', score_text_override.strip())
        if not m:
            raise ValueError(
                f"--score-text 형식 오류: {score_text_override!r} (예: '57/60')"
            )
        winner_score, winner_max, source = int(m.group(1)), int(m.group(2)), 'cli_override'
        text = ''
    else:
        text = tournament_md.read_text(encoding='utf-8', errors='ignore')
        result = extract_winner_score(text)
        if result is None:
            return {
                'schema_version': SCHEMA_VERSION,
                'tournament_md': str(tournament_md),
                'extraction_failed': True,
                'reason': 'winner score/max 추출 실패 (frontmatter / Total row / winner pattern 모두 미매칭)',
                # 보고 모드는 추출 실패도 비게이팅(exit 0) — 실제 종료 게이트는 커널
                # producer(measure_dacapo_threshold, 법칙1 evidence_missing)가 소유.
                'verdict': 'report' if reporting else 'fail',
                'next_round_required': not reporting,
                'threshold': threshold,
            }
        winner_score, winner_max, source = result

    if winner_max == 0:
        ratio = 0.0
    else:
        ratio = winner_score / winner_max

    if reporting:
        passed = None
        verdict = 'report'
        next_round = False
        reason = (
            f"winner ratio {ratio:.4f} 보고(비게이팅, 보고 모드) — 절대값은 종료 게이트가 "
            f"아니다. 재경합 결정은 delta 룰 + budget cap(stop_policy §2.2)."
        )
    else:
        passed = ratio >= threshold
        verdict = 'pass' if passed else 'fail'
        next_round = not passed
        reason = (
            f"winner ratio {ratio:.4f} ≥ threshold {threshold} (round N+1 불필요)"
            if passed
            else f"winner ratio {ratio:.4f} < threshold {threshold} (round N+1 강제)"
        )

    return {
        'schema_version': SCHEMA_VERSION,
        'tournament_md': str(tournament_md),
        'evaluated_at': datetime.now(timezone.utc).isoformat(),
        'winner_score': winner_score,
        'winner_max': winner_max,
        'ratio': round(ratio, 6),
        'threshold': threshold,
        'extraction_source': source,
        'verdict': verdict,
        'next_round_required': next_round,
        'reason': reason,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='dacapo_threshold',
        description=(
            'Tournament 다카포 임계 강제 CLI — winner ratio < threshold 시 exit 1 '
            '(round N+1 강제). HARD-RULE 9.qq (sprint-41).'
        ),
    )
    parser.add_argument(
        '--tournament-md',
        type=Path,
        help='tournament-NN.md 또는 tournament-impl-NN.md 경로',
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=None,
        help=(
            '다카포 임계. 미지정(default)이면 보고 모드(비게이팅, exit 0 + ratio 보고, '
            f'설계 B2 §2.3). 명시하면 예전 gating 복원(ratio<threshold → exit 1). '
            f'예전 값은 {DEFAULT_THRESHOLD}.'
        ),
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='산출 JSON 경로 (없으면 stdout 만)',
    )
    parser.add_argument(
        '--score-text',
        help='tournament-md 대신 직접 score 입력 (예: "57/60")',
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='stderr 메시지 억제 (exit code 만 사용)',
    )

    ns = parser.parse_args(argv)

    if not ns.score_text and not ns.tournament_md:
        parser.error('--tournament-md 또는 --score-text 필수')

    if ns.tournament_md and not ns.tournament_md.exists() and not ns.score_text:
        print(
            f'ERROR: tournament-md 미존재: {ns.tournament_md}',
            file=sys.stderr,
        )
        return 2

    try:
        verdict_obj = evaluate(
            ns.tournament_md or Path('<score-text>'),
            ns.threshold,
            ns.score_text,
        )
    except ValueError as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2

    out_text = json.dumps(verdict_obj, indent=2, ensure_ascii=False)
    print(out_text)

    if ns.output:
        ns.output.parent.mkdir(parents=True, exist_ok=True)
        ns.output.write_text(out_text + '\n', encoding='utf-8')

    if not ns.quiet and verdict_obj['verdict'] == 'fail':
        print(
            f"\n[dacapo_threshold] FAIL(--threshold gating): {verdict_obj.get('reason', 'verdict=fail')}",
            file=sys.stderr,
        )
        print(
            f"[dacapo_threshold] --threshold opt-in — round N+1 자동 진행.",
            file=sys.stderr,
        )

    # 보고 모드(verdict=='report') 는 exit 0. gating opt-in(--threshold) 시에만 fail→exit 1.
    return 1 if verdict_obj['verdict'] == 'fail' else 0


if __name__ == '__main__':
    sys.exit(main())
