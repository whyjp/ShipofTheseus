#!/usr/bin/env python3
"""measure_multiverse_width.py — multiverse.fan_out_width 증거 조립기 (폭 강제 primitive).

멀티버스 fan-out(페이즈 06 plan)의 *초기 폭*이 grade 별 활성 폭(manifest multiverse_widths)
바닥을 채웠는지를 값으로 게이팅할 수 있게, plan 산출물을 디스크에서 세어 emit 한다:
  - plan_round0_tournament_width : 최저 라운드 tournament md 의 universe 표 행 수 — *초기 폭*의
                                    권위 신호(다카포 라운드 0 = 초기 fan-out).
  - plan_candidates_width        : plan/candidates/universe-N/ 디렉터리 실측 수(game-proof). 단
                                    다카포 rerun 마다 fresh universe 가 누적돼 *초기 폭이 아니라
                                    누적 폭*이다(anti-pattern g: round N+1 = width-1 NEW ID).
  - round0_rows_without_dirs     : round0 표가 인용한 universe ID 중 디렉터리 부재 수(phantom 방어).
  - plan_observed_width          : max(round0, candidates) — 관측용 "최선 폭" 정보값(게이팅 아님).
  - impl_candidates_width        : impl/candidates/universe-N/ 실측 수(관측용, 게이팅 안 함).
  - width_floor                  : manifest multiverse_widths[grade](활성 폭 단일 소스).

왜 필요한가: dacapo fan-out(활성 폭 G3=3/G4=4/G5=6)이 컨벤션 의사코드·모델재량이라 모델이
폭을 skip 할 수 있었다(cold session winner 0.853 재경합 0 회 = universe 3 < G4 폭 4 회귀).
universe_count_monotonicity.py 는 라운드 간 단조성(N+1 ≥ N)만 사후 검사할 뿐 *초기 폭 바닥*은
강제하지 않는다(라운드 0 에서 width=1 이어도 단조성 통과). 본 producer + CheckSpec
multiverse.fan_out_width.json 이 그 구멍을 커널 게이트로 닫는다 — 폭이 모델재량이 아니라
코드가 소유하는 조건이 된다.

*초기 폭*을 왜 round0 표를 권위로 삼는가: candidates 디렉터리는 rerun 누적이라 초기 2 폭 +
rerun 3 fresh = 5 dir 로 floor 4 를 통과시킬 수 있다(초기 폭은 2인데). 따라서 게이트 assertion 은
plan_round0_tournament_width 를 우선하고, 그 표가 파싱 불가(=0)일 때만 candidates 로 폴백한다
(CheckSpec assertion 참조). plan_observed_width(max)는 정보값일 뿐 assertion 대상이 아니다.

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다 — 폭 판정은 커널이 CheckSpec assertion
으로 내린다. 모든 수치는 로그의 자기 신고가 아니라 producer 가 디스크의 실제 universe-N
디렉터리와 tournament 표 행을 다시 세어 낸 값이다(상상값 주입 0). width_floor 는 하드코딩이
아니라 manifest multiverse_widths[grade] 를 읽은 활성 폭 단일 소스로, backing report 에 함께
기록돼 digest 체인에 실린다.

정직 고지(§5 한계 정합): round0 표만 쓰고 dir 을 비운 위조(phantom 행)는 커널 assertion
round0_rows_without_dirs==0 이 잡는다. 그러나 표를 아예 파싱 불가로 쓰고(=0) 폭을 줄인 뒤
rerun 으로 dir 을 누적시키는 잔여 우회는 본 체크 단독이 아니라 생태계가 좁힌다 —
universe_count_monotonicity(오케스트레이터 CLI, *비-커널*)의 단조성/mismatch 와
plan.tournament_independence 의 shadow 변량. 순도의 궁극 증명이 불가한 것과 같은 전제
(review.context_minimality 참조).

플래그: plan 디렉터리 자체가 없으면(멀티버스 미발생) evidence 를 emit 하지 않는다 — 폭을
상상하지 않는다. G3+ run 이 페이즈 09 게이트까지 plan fan-out 없이 왔다면 evidence 부재가
absence_policy FAIL 로 강제된다(비휴면). G2 는 멀티버스 없음(multiverse_widths=1)이며 체크
맵에서 제외라 emit 되어도 게이팅되지 않는다.

CLI:
    python measure_multiverse_width.py --grade G4 \\
        [--manifest <pipeline.manifest.json>] [--phase 06] [--project-run <name>] \\
        [--measured-at <ISO8601>] --out-dir <project_root>/evidence
    (커널 게이팅 경로는 --manifest override 를 금지한다 — CheckSpec cmd_pattern 이 canonical
     form 만 수용해 floor 몰래 낮추기 채널을 봉쇄. --manifest 는 producer 단위 테스트 전용.)

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

CHECK_ID = "multiverse.fan_out_width"
DEFAULT_PHASE = "06"

# 활성 폭 단일 소스(manifest). 이 파일 기준 producers -> scoring -> theseus-harness.
_DEFAULT_MANIFEST = Path(__file__).resolve().parents[2] / "pipeline.manifest.json"

# universe-N 디렉터리 / tournament 표 행 패턴(universe_count_monotonicity 와 동일 규약).
_UNIVERSE_DIR_RE = re.compile(r"^universe-(\d+)$")
_TOURNAMENT_RE = re.compile(r"^tournament-(\d+)\.md$")
_UNIVERSE_ROW_RE = re.compile(r"^\|\s*(?:\*\*)?universe-(\d+)(?:\*\*)?\s*\|", re.MULTILINE)


def _universe_dir_ids(candidates_dir: Path) -> set[int]:
    """candidates/ 아래 universe-N 디렉터리 ID 집합. 부재면 빈 집합."""
    ids: set[int] = set()
    if candidates_dir.is_dir():
        for sub in candidates_dir.iterdir():
            if sub.is_dir():
                m = _UNIVERSE_DIR_RE.match(sub.name)
                if m:
                    ids.add(int(m.group(1)))
    return ids


def _round0_tournament_ids(plan_dir: Path) -> set[int]:
    """최저 라운드 tournament md(초기 fan-out)의 universe 표 행 ID 집합. 부재/미파싱이면 빈 집합.

    tournament-NN.md 중 최소 NN, 또는 무번호 tournament.md 를 라운드 0 으로 본다. 둘이 공존하면
    (round 키 동률) 파일명 사전순 tie-break — '-'(0x2D) < '.'(0x2E) 라 tournament-00.md 가
    tournament.md 를 이긴다(결정적). 표 행은 universe_count_monotonicity 인용 규약과 동일하게
    `| universe-N |` 패턴으로 센다(U1 같은 비표준 라벨은 매칭 안 됨 → 빈 집합 → candidates 폴백)."""
    if not plan_dir.is_dir():
        return set()
    rounds: list[tuple[int, str, Path]] = []
    for md in plan_dir.glob("tournament-*.md"):
        m = _TOURNAMENT_RE.match(md.name)
        if m:
            rounds.append((int(m.group(1)), md.name, md))
    bare = plan_dir / "tournament.md"
    if bare.is_file():
        rounds.append((0, bare.name, bare))  # 무번호 = 라운드 0(초기 fan-out)
    if not rounds:
        return set()
    rounds.sort(key=lambda t: (t[0], t[1]))
    md0 = rounds[0][2]
    text = md0.read_text(encoding="utf-8", errors="ignore")
    return {int(m.group(1)) for m in _UNIVERSE_ROW_RE.finditer(text)}


def _load_width_floor(manifest_path: Path, grade: str) -> int | None:
    """manifest multiverse_widths[grade] — 활성 폭 단일 소스. 없으면 None(상상 금지)."""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    widths = data.get("multiverse_widths")
    if not isinstance(widths, dict):
        return None
    v = widths.get(grade)
    # bool 은 int 서브타입이라 명시 배제.
    if isinstance(v, bool) or not isinstance(v, int):
        return None
    return v


def _build_report(run_root: Path, grade: str, width_floor: int) -> dict[str, Any]:
    """plan/impl 디스크 스캔 → 원시 관측 리포트(verdict 없음).

    round0 표 ID 와 candidates 디렉터리 ID 를 각각 집합으로 구해:
      - plan_round0_tournament_width : 초기 폭의 권위 신호(게이트 assertion 우선)
      - round0_rows_without_dirs     : round0 표가 인용했으나 디렉터리 없는 phantom 수(커널 방어)
      - plan_observed_width          : max(둘) — 정보값(게이팅 아님)
    이 리포트 자체가 measured 값들의 backing artifact."""
    plan_dir = run_root / "plan"
    impl_dir = run_root / "impl"
    round0_ids = _round0_tournament_ids(plan_dir)
    dir_ids = _universe_dir_ids(plan_dir / "candidates")
    plan_round0 = len(round0_ids)
    plan_candidates = len(dir_ids)
    return {
        "grade": grade,
        "plan_round0_tournament_width": plan_round0,
        "plan_candidates_width": plan_candidates,
        "round0_rows_without_dirs": len(round0_ids - dir_ids),
        "plan_observed_width": max(plan_round0, plan_candidates),
        "impl_candidates_width": len(_universe_dir_ids(impl_dir / "candidates")),
        "width_floor": width_floor,
    }


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 재구성. canonical form(--manifest override 없음)은 CheckSpec cmd_pattern
    `^python (?!.*--manifest).*measure_multiverse_width\\.py` 에 매칭된다. --manifest 를 쓰면
    cmd 에 그 토큰이 실려 pattern 이 거부 → 커널 법칙3 FAIL(floor 몰래 낮추기 봉쇄)."""
    parts = ["python", str(Path(__file__).resolve()), "--grade", args.grade]
    if args.manifest:
        parts += ["--manifest", args.manifest]
    parts += ["--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    manifest_path = Path(args.manifest).resolve() if args.manifest else _DEFAULT_MANIFEST
    width_floor = _load_width_floor(manifest_path, args.grade)
    if width_floor is None:
        # 활성 폭을 못 구함(미지의 grade/manifest 결손) → evidence 미기록(상상 0). G3+ 는
        # 이 경로에 오지 않아야 하며, 오면 absence_policy FAIL 로 정직하게 잡힌다.
        return {
            "emitted": False,
            "reason": f"manifest multiverse_widths[{args.grade}] 미존재 — measure_multiverse_width 미실행",
        }

    plan_dir = run_root / "plan"
    if not plan_dir.is_dir():
        # 멀티버스 미발생(plan 산출물 부재) → 폭을 상상하지 않는다. G3+ 는 evidence 부재로
        # absence_policy FAIL(비휴면), G2 는 체크 맵 제외라 무영향.
        return {
            "emitted": False,
            "reason": "plan 디렉터리 부재 — 멀티버스 fan-out 미발생(evidence_missing FAIL 로 강제)",
            "plan_dir_exists": False,
        }

    report = _build_report(run_root, args.grade, width_floor)

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    report_rel = ec.relpath(report_path, run_root)
    report_digest = ec.sha256_of_file(report_path)

    src = "multiverse_width_scan"
    measured = {
        key: ec.build_measured(report[key], src, report_rel)
        for key in (
            "plan_round0_tournament_width",
            "plan_candidates_width",
            "round0_rows_without_dirs",
            "plan_observed_width",
            "impl_candidates_width",
            "width_floor",
        )
    }
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
    return {
        "emitted": True,
        "evidence_path": str(path),
        "grade": args.grade,
        "plan_round0_tournament_width": report["plan_round0_tournament_width"],
        "plan_candidates_width": report["plan_candidates_width"],
        "round0_rows_without_dirs": report["round0_rows_without_dirs"],
        "plan_observed_width": report["plan_observed_width"],
        "impl_candidates_width": report["impl_candidates_width"],
        "width_floor": width_floor,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_multiverse_width — multiverse.fan_out_width 증거 조립기 (verdict 없음)"
    )
    p.add_argument(
        "--grade", required=True,
        help="폭 바닥 조회용 grade(G2|G3|G4|G5). manifest multiverse_widths[grade] 를 width_floor 로 읽는다.",
    )
    p.add_argument(
        "--manifest", default=None,
        help="활성 폭 소스 override(기본: skills/theseus-harness/pipeline.manifest.json). "
             "커널 게이팅 경로에선 금지 — producer 단위 테스트 전용(CheckSpec cmd_pattern 이 거부).",
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
