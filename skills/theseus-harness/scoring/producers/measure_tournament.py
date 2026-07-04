#!/usr/bin/env python3
"""measure_tournament.py — plan.tournament_independence 증거 조립기 (설계 §7.2, WP4b).

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다. shadow-grade 산출물(각 grading
이 낳은 JSON)을 파싱해 grader 패널의 *계산 가능한 속성* 만 emit 한다 — LLM 이 내린
'누가 이겼나 / 진짜 독립이었나' 판단을 재판단하지 않고, 그 판단 산출물의 계산량만
측정한다:
  - winner_ratio      = grader 패널의 평균 정규 점수(합의 추정; value=정보용)
  - grader_score_variance = grader 간 정규 점수의 모분산(독립성 지표; 게이트 대상)
  - grader_count      = 파싱된 shadow-grade 수(no-work / applicability 근거)

독립성을 *퍼포먼스적 불일치 강제*(3pt 차 의무 등)로 만들지 않는다 — grader 점수의
분산이라는 *관측된 계산량* 으로 측정한다. 분산 0(=2인 이상 패널이 완전 동일 점수)만
copy 의심 신호로 삼아 CheckSpec 이 게이트한다(정직한 수렴 자체를 재판단하지 않는다,
설계 §7.2).

plan.dacapo_threshold 와의 차원 구분: dacapo 는 tournament-md 의 winner_score/winner_max
로 '품질 plateau 도달(≥0.999)' 을 게이트한다(다른 artifact·다른 차원). 여기 winner_ratio
는 shadow grader 패널 평균이며 gating assertion 대상이 아니라 value 일 뿐 — 0.999 임계와
중복/충돌하지 않는다.

CLI 에 raw 점수를 주입하는 인자는 없다(손 넣기 봉쇄, WP4a 규율) — 입력은 shadow-grade
파일 경로(디렉터리 glob 또는 명시 목록)뿐이고, 모든 measured 값은 그 파일들을 파싱해
얻어 producer 가 직접 기록한 scan 리포트로 backing 된다. shadow-grade 를 하나도 못
파싱하면 evidence 를 안 쓴다 — 커널 법칙1(evidence_missing)이 FAIL 시킨다.

CLI:
    python measure_tournament.py --shadow-grades-dir <dir> [--score-max 100] \\
        [--phase 06] [--project-run <name>] [--measured-at <ISO8601>] \\
        --out-dir <project_root>/evidence
  또는 --shadow-grade <f1> --shadow-grade <f2> ... 로 파일을 명시.

저장소 self_lint C35 — 모든 open encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import _evidence_common as ec  # noqa: E402

CHECK_ID = "plan.tournament_independence"
DEFAULT_PHASE = "06"

# shadow-grade 점수가 실릴 수 있는 키(우선순위) — dacapo-frontmatter-schema.md /
# shadow-grader-zero-context.md 의 실 필드명. 첫 발견 키의 값만 쓴다(결정성).
_SCORE_KEYS = ("predicted_score", "score_total_weighted", "winner_score")


def _normalize_score(raw: Any, score_max: float) -> float | None:
    """shadow-grade 원시 점수를 [0,1] 정규값으로. 스키마상 0-100(predicted_score) 과
    0-1(winner_score) 이 혼재하므로, >1 이면 score_max 로 나누고 ≤1 이면 이미 정규로
    본다. 숫자 아님/음수/비정상은 None(무효 — 상상 없이 결손)."""
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        return None
    val = float(raw)
    if val < 0:
        return None
    if val > 1:
        if score_max <= 0:
            return None
        return val / score_max
    return val


def _extract_score(data: Any, score_max: float) -> tuple[float | None, str | None]:
    """shadow-grade dict 에서 정규 점수 + 어떤 키에서 왔는지. 값 없음 → (None, None)."""
    if not isinstance(data, dict):
        return None, None
    for key in _SCORE_KEYS:
        if key in data:
            norm = _normalize_score(data[key], score_max)
            if norm is not None:
                return norm, key
    return None, None


def _population_variance(values: list[float]) -> float:
    """모분산 Σ(x-μ)²/N. 단일 값이면 0(분산 없음). 정규화 규약(§2 원칙5)상 결정적."""
    n = len(values)
    if n == 0:
        return 0.0
    mean = sum(values) / n
    return sum((v - mean) ** 2 for v in values) / n


def _collect_shadow_grades(args: argparse.Namespace) -> list[Path]:
    """--shadow-grades-dir glob + --shadow-grade 명시 목록을 합쳐 정렬(결정성)."""
    paths: list[Path] = []
    if args.shadow_grades_dir:
        d = Path(args.shadow_grades_dir).resolve()
        if d.is_dir():
            paths += sorted(d.glob("shadow-grade-*.json"))
    for f in args.shadow_grade or []:
        paths.append(Path(f).resolve())
    # 중복 제거하되 정렬 순서 보존.
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in sorted(paths, key=lambda x: x.as_posix()):
        key = p.as_posix()
        if key not in seen:
            seen.add(key)
            uniq.append(p)
    return uniq


def _build_report(shadow_files: list[Path], score_max: float) -> dict[str, Any]:
    """shadow-grade 파일들 → 원시 관측 리포트(verdict 없음). 각 파일의 정규 점수 + 원본
    digest 를 기록해, 이 리포트 자체가 '이 실행이 실제로 무엇을 파싱했나'의 backing 이
    되게 한다(measure_dry_violation 의 scan 리포트 패턴). 정규 점수를 못 뽑은 파일은
    graders 에서 제외하고 unparseable 에 사유를 남긴다 — 상상 값을 만들지 않는다."""
    graders: list[dict[str, Any]] = []
    unparseable: list[dict[str, str]] = []
    for p in shadow_files:
        if not p.exists():
            unparseable.append({"path": p.as_posix(), "reason": "file not found"})
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            unparseable.append({"path": p.as_posix(), "reason": f"unparseable json: {exc}"})
            continue
        norm, key = _extract_score(data, score_max)
        if norm is None:
            unparseable.append(
                {"path": p.as_posix(), "reason": "no normalizable score key present"}
            )
            continue
        graders.append(
            {
                "path": p.as_posix(),
                "score_key": key,
                "normalized_score": norm,
                "source_digest": ec.sha256_of_file(p),
            }
        )
    scores = [g["normalized_score"] for g in graders]
    grader_count = len(scores)
    variance = _population_variance(scores)
    # winner_ratio = 패널 평균(합의 추정). grader 0 이면 0.0 — no-work 을 winner_ratio>0
    # assertion 이 잡는다(0 이면 FAIL).
    winner_ratio = sum(scores) / grader_count if grader_count else 0.0
    return {
        "score_max": score_max,
        "grader_count": grader_count,
        "grader_score_variance": variance,
        "winner_ratio": winner_ratio,
        "graders": graders,
        "unparseable": unparseable,
    }


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 재구성 — CheckSpec cmd_pattern `^python .*measure_tournament\\.py`
    과 정합. 실 호출을 충실히 반영한다."""
    parts = ["python", str(Path(__file__).resolve())]
    if args.shadow_grades_dir:
        parts += ["--shadow-grades-dir", args.shadow_grades_dir]
    for f in args.shadow_grade or []:
        parts += ["--shadow-grade", f]
    parts += ["--score-max", str(args.score_max), "--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    shadow_files = _collect_shadow_grades(args)
    report = _build_report(shadow_files, args.score_max)

    if report["grader_count"] == 0:
        # 파싱 가능한 shadow-grade 0 — 상상하지 않는다. evidence 를 안 쓴다(법칙1 FAIL).
        return {
            "emitted": False,
            "reason": "no parseable shadow-grade score (all inputs missing/unparseable)",
            "unparseable": report["unparseable"],
        }

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    rel = ec.relpath(report_path, run_root)
    digest = ec.sha256_of_file(report_path)

    src = "tournament_shadow_grade_scan"
    measured = {
        "grader_count": ec.build_measured(report["grader_count"], src, rel),
        "grader_score_variance": ec.build_measured(report["grader_score_variance"], src, rel),
        "winner_ratio": ec.build_measured(report["winner_ratio"], src, rel),
    }
    record = ec.assemble_record(
        check_id=CHECK_ID,
        phase=args.phase,
        project_run=project_run,
        producer_cmd=producer_cmd,
        measured=measured,
        artifact_digests={rel: digest},
        measured_at=measured_at,
    )
    path = ec.write_evidence(out_dir, CHECK_ID, record)
    return {
        "emitted": True,
        "evidence_path": str(path),
        "grader_count": report["grader_count"],
        "grader_score_variance": report["grader_score_variance"],
        "winner_ratio": report["winner_ratio"],
        "unparseable": report["unparseable"],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_tournament — plan.tournament_independence 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument(
        "--shadow-grades-dir", default=None,
        help="shadow-grade-*.json 이 있는 디렉터리(glob). --shadow-grade 와 병용 가능.",
    )
    p.add_argument(
        "--shadow-grade", action="append", default=None,
        help="shadow-grade JSON 파일 명시(반복 가능).",
    )
    p.add_argument(
        "--score-max", type=float, default=100.0,
        help="원시 점수(>1)의 정규화 분모. predicted_score 0-100 스키마 기본 100.",
    )
    p.add_argument(
        "--phase", default=DEFAULT_PHASE,
        help="이 측정이 속한 페이즈(06 plan / 08 impl tournament). 정보용 — 게이팅 무관.",
    )
    p.add_argument("--project-run", default=None, help="project_run 이름 (기본: run_root.name)")
    p.add_argument("--measured-at", default=None, help="measured_at 주입(결정성 테스트용)")
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<project_root>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run(args)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
