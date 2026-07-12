#!/usr/bin/env python3
"""measure_tournament_argmax.py — plan.tournament_winner_argmax 증거 조립기 (병합/승자 소유).

멀티버스 tournament 의 *승자 선택*(argmax)과 *승격*(promotion)을 모델재량이 아니라 코드가
소유하는 조건으로 만든다. B1(multiverse.fan_out_width)이 fan-out *폭*을 강제했다면, 본
producer 는 그 짝인 *병합*을 소유한다 — 사용자 논지 "폭 강제 + 병합을 코드로 소유".

오늘까지 승자 선택은 모델 서술이었다: 모델이 sub-score 를 쓰고 winner 를 선언하고 canonical
아티팩트로 복사한다. 아무도 선언 winner 가 *선언된 sub-score 의 argmax* 인지, 승격된 canonical
이 *실제 winner 아티팩트*인지 재계산하지 않았다. 본 producer 가 최종 라운드 tournament 를
디스크에서 파싱해 emit:
  - winner_in_table          : frontmatter winner_id 가 채점된 표 행에 실재(1/0)
  - winner_argmax_match       : winner 총점 >= 전 universe 최대 총점(1/0) — 병합 소유 핵심
  - score_margin              : winner 총점 − 차점 총점(0=동률, 음수=불일치; value)
  - argmax_tie_count          : 최대점과 동률(≤eps) 행 수(동률=competition.md 머지 영역, info)
  - universes_scored          : 총점 파싱된 universe- 행 수
  - malformed_rows            : universe- 행이지만 총점 미파싱 수(무결성)
  - scores_out_of_range       : 총점이 [0,1] 밖인 행 수(1-5 coarse 채점 자동 reject 정합)
  - winner_row_delta          : |frontmatter winner_score − winner 행 총점|(서술 일관성)
  - canonical_exists          : plan/06-plan.md 존재(1/0)
  - winner_dir_exists         : plan/candidates/<winner_id>/06-plan.md 존재(1/0)
  - promotion_policy_copy     : 승격 정책 == copy(1/0; frontmatter 미기재 → copy 기본)
  - canonical_digest_match    : sha256(canonical) == sha256(winner 후보)(1/0) — 복사=기계적 복사
  - merge_sources_include_winner : merge 정책 시 winner_id ∈ merge_sources(1/0)

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다 — 판정은 커널이 CheckSpec
plan.tournament_winner_argmax.json 의 assertion 으로 내린다. 모든 수치는 로그 자기 신고가
아니라 producer 가 디스크의 tournament frontmatter·본문 표를 다시 파싱해 낸 값이다(상상값
주입 0). weight-free: universe 별 총점(본문 표 `weighted` 열)의 argmax 는 가중치가 필요 없다
(컨벤션에 6-dim 스키마가 둘 충돌하므로 가중치를 재계산하지 않는다 — plan-tournament-scoring-
strict.md vs intra-phase-dacapo-loop.md).

승격 정책(copy vs merge): competition.md 는 Δ<0.05/0.02 시 *머지* 승격을 허용한다. canonical 이
winner 와 byte-동일이 아닐 정당한 경로가 있으므로, frontmatter `promotion_policy: copy|merge`
+ `merge_sources` 를 읽는다(미기재 → copy 기본: copy 가 의사코드 계약, merge 는 선언 의무인
예외). copy 면 canonical==winner 복사를 digest 로 증명하고, merge 면 winner 가 선언된 merge
base 인지 확인한다(머지 내용 파생은 digest 로 증명 불가 — 정직 고지).

정직 고지: 본 게이트는 "선언 winner 가 선언 sub-score 의 argmax 다 + 승격이 기계적이다"를
증명하지 계획 품질을 증명하지 않는다 — sub-score 는 LLM 판단이고 모델은 자기 선호 universe 가
이기는 *일관된* 점수표를 위조할 수 있다(본 체크가 재심사하지 않는다). 그 위조 압력은
plan.tournament_independence shadow 변량·zero-context shadow grading·monotonicity 가 좁힌다
(review.context_minimality 가 순도의 궁극 증명 대신 무결성으로 조이는 것과 같은 전제).

플래그: 최종 tournament md 부재 또는 frontmatter winner_id 부재면 evidence 를 emit 하지 않는다
(승자를 상상하지 않는다) — G3+ 는 absence_policy FAIL(비휴면), G2 는 tournament 없음이라
체크 맵 제외(비게이팅).

CLI:
    python measure_tournament_argmax.py [--phase 06] [--project-run <name>] \\
        [--measured-at <ISO8601>] --out-dir <project_root>/evidence

저장소 self_lint C35 — 모든 open encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_SCORING_DIR = Path(__file__).resolve().parents[1]
if str(_SCORING_DIR) not in sys.path:
    sys.path.insert(0, str(_SCORING_DIR))

import _evidence_common as ec  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "plan.tournament_winner_argmax"
DEFAULT_PHASE = "06"
_EPS = 1e-9

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
# 본문 표의 universe 행 라벨(winner_id 규약과 동일: universe-N / universe-anon-rerun-01-a).
_UNIVERSE_LABEL_RE = re.compile(r"^universe-[0-9A-Za-z][0-9A-Za-z-]*$")
_TOURNAMENT_RE = re.compile(r"^tournament-(\d+)\.md$")


def _parse_frontmatter(text: str) -> dict[str, str]:
    """최상위 key: value 만 파싱(중첩 블록은 건너뜀). winner_id/winner_score/promotion_policy/
    merge_sources 는 전부 최상위 스칼라라 nested winner_sub_scores 평탄화 오염을 피한다."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        if line[:1] in (" ", "\t"):
            continue  # 들여쓴 중첩(예: winner_sub_scores 하위) 무시
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        key, _, val = s.partition(":")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def _parse_list(val: str) -> list[str]:
    """`[a, b]` 또는 `a, b` → [a, b]. 단순 프론트매터 리스트."""
    v = val.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [x.strip().strip('"').strip("'") for x in v.split(",") if x.strip()]


def _parse_num(s: str) -> float | None:
    """`0.913` / `**0.913**` / `57/60`(비율) → float. 미파싱 None."""
    s = s.strip().strip("*").strip()
    if not s:
        return None
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)", s)
    if m:
        num, den = float(m.group(1)), float(m.group(2))
        return (num / den) if den else None
    try:
        return float(s)
    except ValueError:
        return None


def _final_tournament_md(plan_dir: Path) -> Path | None:
    """최종 라운드 tournament md(승격은 최종 라운드 winner 에서 일어난다 — B1 round-0 의 역).

    tournament-NN.md 중 최대 NN, 또는 무번호 tournament.md(round 0). 최대 round = 최종."""
    if not plan_dir.is_dir():
        return None
    cand: list[tuple[int, str, Path]] = []
    for md in plan_dir.glob("tournament-*.md"):
        m = _TOURNAMENT_RE.match(md.name)
        if m:
            cand.append((int(m.group(1)), md.name, md))
    bare = plan_dir / "tournament.md"
    if bare.is_file():
        cand.append((0, bare.name, bare))
    if not cand:
        return None
    cand.sort(key=lambda t: (t[0], t[1]))
    return cand[-1][2]


def _parse_universe_rows(text: str) -> list[tuple[str, float | None]]:
    """본문 표에서 universe- 행 → (label, total). total None = 총점 미파싱(malformed).

    라벨은 첫 열, 총점은 마지막 숫자 셀. header(`| Universe | ... |`)·separator(`|---|`)·
    비-universe 라벨 행은 건너뛴다(universes_scored 로 잡힘)."""
    body = _FRONTMATTER_RE.sub("", text, count=1)
    rows: list[tuple[str, float | None]] = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        label = cells[0].strip("*").strip()
        if not _UNIVERSE_LABEL_RE.match(label):
            continue
        total: float | None = None
        for c in reversed(cells[1:]):
            v = _parse_num(c)
            if v is not None:
                total = v
                break
        rows.append((label, total))
    return rows


def _build_report(run_root: Path, text: str, fm: dict[str, str]) -> dict[str, Any]:
    """tournament frontmatter + 본문 표 + 승격 아티팩트를 디스크에서 파싱 → 관측 리포트."""
    winner_id = fm.get("winner_id", "").strip()
    winner_score_fm = _parse_num(fm.get("winner_score", "")) if fm.get("winner_score") else None

    rows = _parse_universe_rows(text)
    scored = [(lbl, t) for lbl, t in rows if t is not None]
    totals = [t for _, t in scored]
    max_total = max(totals) if totals else None

    winner_total = next((t for lbl, t in scored if lbl == winner_id), None)
    winner_in_table = 1 if winner_total is not None else 0

    if winner_total is not None and max_total is not None:
        winner_argmax_match = 1 if winner_total >= max_total - _EPS else 0
        rivals = [t for lbl, t in scored if lbl != winner_id]
        best_rival = max(rivals) if rivals else 0.0
        score_margin = round(winner_total - best_rival, 6)
        argmax_tie_count = sum(1 for t in totals if t >= max_total - _EPS)
    else:
        winner_argmax_match = 0
        score_margin = 0.0
        argmax_tie_count = 0

    if winner_total is not None and winner_score_fm is not None:
        winner_row_delta = round(abs(winner_score_fm - winner_total), 6)
    else:
        winner_row_delta = 1.0

    canonical = run_root / "plan" / "06-plan.md"
    winner_cand = run_root / "plan" / "candidates" / winner_id / "06-plan.md"
    canonical_exists = 1 if canonical.is_file() else 0
    winner_dir_exists = 1 if winner_cand.is_file() else 0
    if canonical_exists and winner_dir_exists:
        canonical_digest_match = 1 if ec.sha256_of_file(canonical) == ec.sha256_of_file(winner_cand) else 0
    else:
        canonical_digest_match = 0

    policy = (fm.get("promotion_policy") or "copy").strip().lower()
    promotion_policy_copy = 1 if policy == "copy" else 0
    merge_sources = _parse_list(fm.get("merge_sources", ""))
    merge_sources_include_winner = 1 if winner_id in merge_sources else 0

    return {
        "winner_id": winner_id,
        "winner_in_table": winner_in_table,
        "winner_argmax_match": winner_argmax_match,
        "score_margin": score_margin,
        "argmax_tie_count": argmax_tie_count,
        "universes_scored": len(scored),
        "malformed_rows": sum(1 for _, t in rows if t is None),
        "scores_out_of_range": sum(1 for t in totals if t < -_EPS or t > 1.0 + _EPS),
        "winner_row_delta": winner_row_delta,
        "canonical_exists": canonical_exists,
        "winner_dir_exists": winner_dir_exists,
        "promotion_policy_copy": promotion_policy_copy,
        "canonical_digest_match": canonical_digest_match,
        "merge_sources_include_winner": merge_sources_include_winner,
    }


_MEASURED_KEYS = (
    "winner_in_table",
    "winner_argmax_match",
    "score_margin",
    "argmax_tie_count",
    "universes_scored",
    "malformed_rows",
    "scores_out_of_range",
    "winner_row_delta",
    "canonical_exists",
    "winner_dir_exists",
    "promotion_policy_copy",
    "canonical_digest_match",
    "merge_sources_include_winner",
)


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 재구성 — CheckSpec cmd_pattern `^python .*measure_tournament_argmax\\.py`
    과 정합. 설정 override 인자가 없다(승자·점수는 전부 디스크 tournament 아티팩트에서)."""
    return " ".join(["python", str(Path(__file__).resolve()), "--out-dir", args.out_dir])


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    plan_dir = run_root / "plan"
    final_md = _final_tournament_md(plan_dir)
    if final_md is None:
        # tournament 미발생 → 승자를 상상하지 않는다. G3+ 는 absence_policy FAIL(비휴면).
        return {
            "emitted": False,
            "reason": "최종 tournament md 부재 — 멀티버스 tournament 미발생(evidence_missing FAIL 로 강제)",
        }
    text = final_md.read_text(encoding="utf-8", errors="ignore")
    fm = _parse_frontmatter(text)
    if not fm.get("winner_id", "").strip():
        return {
            "emitted": False,
            "reason": "tournament frontmatter winner_id 부재 — 승격 대상 불명(evidence 미기록)",
        }

    report = _build_report(run_root, text, fm)
    report["tournament_md"] = ec.relpath(final_md, run_root)

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    report_rel = ec.relpath(report_path, run_root)
    report_digest = ec.sha256_of_file(report_path)

    src = "tournament_argmax_scan"
    measured = {k: ec.build_measured(report[k], src, report_rel) for k in _MEASURED_KEYS}
    artifact_digests = {report_rel: report_digest}
    record = ec.assemble_record(
        check_id=CHECK_ID,
        phase=args.phase,
        project_run=project_run,
        producer_cmd=producer_cmd,
        measured=measured,
        artifact_digests=artifact_digests,
        measured_at=measured_at,
    )
    path = ec.write_evidence(out_dir, CHECK_ID, record)
    summary = {"emitted": True, "evidence_path": str(path)}
    summary.update({k: report[k] for k in _MEASURED_KEYS})
    return summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_tournament_argmax — plan.tournament_winner_argmax 증거 조립기 (verdict 없음)"
    )
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
    p.add_argument("--project-run", default=None, help="project_run 이름(기본: run_root.name)")
    p.add_argument("--measured-at", default=None, help="measured_at 주입(결정성 테스트용)")
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<project_root>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)
    summary = run(args)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
