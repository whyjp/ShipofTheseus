#!/usr/bin/env python3
"""
점수 정체(stagnation) 감지기 — 무한 재귀 함정의 객관 측정 도구.

스프린트 점수 시계열과 차원별 sub-score 시계열을 받아, 정체 여부와
정체 차원, 권장 행동 (rewrite vs extend) 을 판단한다. lessons.md 의
정의에 1:1 매핑.

사용:
    stagnation.py --history sprints-history.json [--window 3] [--eps 0.005]

입력 JSON 예:
    {
      "sprint_scores": [0.910, 0.912, 0.913],
      "dim_history": {
        "correctness": [0.95, 0.95, 0.95],
        "coverage":    [0.85, 0.86, 0.86],
        "e2e_pass":    [0.90, 0.90, 0.91],
        ...
      },
      "threshold": 0.999
    }

stdout JSON, exit 0 = 건강, 1 = 정체 감지 (rewrite 권고).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def detect(
    sprint_scores: list[float],
    dim_history: dict[str, list[float]],
    threshold: float = 0.999,
    window: int = 3,
    score_eps: float = 0.005,
    dim_eps: float = 0.005,
    dim_threshold: float = 0.95,
) -> dict:
    """lessons.md 의 정체 감지 알고리즘 — 종합 + 차원별."""
    n = len(sprint_scores)
    overall = False
    overall_recent: list[float] = []
    if n >= window:
        overall_recent = sprint_scores[-window:]
        if (max(overall_recent) - min(overall_recent)) < score_eps and overall_recent[-1] < threshold:
            overall = True

    stagnant_dims: list[dict] = []
    for dim, hist in dim_history.items():
        if len(hist) < window:
            continue
        rec = hist[-window:]
        spread = max(rec) - min(rec)
        if spread < dim_eps and rec[-1] < dim_threshold:
            stagnant_dims.append(
                {
                    "dim": dim,
                    "recent": rec,
                    "spread": round(spread, 6),
                    "last": rec[-1],
                }
            )

    if overall:
        action = "rewrite_full"
        reason = (
            f"종합 점수가 {window} 스프린트 동안 {score_eps} 이내 변동 + "
            f"마지막 점수 {overall_recent[-1]:.4f} 가 임계 {threshold} 미달 → "
            "페이즈 06 (계획) 부터 재시작 권고"
        )
    elif stagnant_dims:
        action = "rewrite_module"
        names = ", ".join(d["dim"] for d in stagnant_dims)
        reason = (
            f"차원 정체 ({names}) — 해당 차원에 영향 주는 모듈을 "
            "통째 재작성 권고 (preserve=false). 부분 수정 금지."
        )
    else:
        action = "extend"
        reason = "정체 신호 없음 — 일반 다음 스프린트 진행 (이어서 보강)."

    return {
        "stagnation_overall": overall,
        "stagnant_dims": stagnant_dims,
        "recommended_action": action,
        "reason": reason,
        "params": {
            "window": window,
            "score_eps": score_eps,
            "dim_eps": dim_eps,
            "dim_threshold": dim_threshold,
            "threshold": threshold,
        },
    }


def build_lesson_pack(
    sprint: int,
    history: list[dict],
    stagnation_report: dict,
    prior_attempts: list[dict] | None = None,
    forbidden: list[str] | None = None,
    autonomy_level: int = 1,
) -> dict:
    """
    lessons.md 의 lesson_pack 구조를 만들어 반환.
    implementer/planner 호출 시 프롬프트에 첨부.
    """
    last_score = history[-1]["score"] if history else None
    threshold = stagnation_report["params"]["threshold"]
    rewrite = stagnation_report["recommended_action"].startswith("rewrite")
    pack = {
        "current_sprint": sprint,
        "current_score": last_score,
        "threshold": threshold,
        "delta_to_threshold": (
            round(threshold - last_score, 4) if last_score is not None else None
        ),
        "history": history,
        "stagnation": {
            "overall": stagnation_report["stagnation_overall"],
            "stagnant_dims": [d["dim"] for d in stagnation_report["stagnant_dims"]],
            "window": stagnation_report["params"]["window"],
        },
        "prior_attempts": prior_attempts or [],
        "forbidden_strategies": forbidden or [],
        "recommended_action": stagnation_report["recommended_action"],
        "rewrite_rule": (
            {"preserve": False, "start_from": "phase-06-replan"}
            if stagnation_report["stagnation_overall"]
            else (
                {"preserve": False, "start_from": "fresh-impl"}
                if rewrite
                else {"preserve": True, "start_from": "extend"}
            )
        ),
        "autonomy_level": autonomy_level,
    }
    return pack


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--history", required=True, help="sprints-history.json 경로")
    p.add_argument("--window", type=int, default=3)
    p.add_argument("--score-eps", type=float, default=0.005)
    p.add_argument("--dim-eps", type=float, default=0.005)
    p.add_argument("--dim-threshold", type=float, default=0.95)
    p.add_argument("--threshold", type=float, default=0.999)
    p.add_argument("--lesson-pack", action="store_true", help="lesson_pack 도 함께 출력")
    args = p.parse_args(argv)

    data = json.loads(Path(args.history).read_text(encoding="utf-8"))
    report = detect(
        data["sprint_scores"],
        data["dim_history"],
        threshold=data.get("threshold", args.threshold),
        window=args.window,
        score_eps=args.score_eps,
        dim_eps=args.dim_eps,
        dim_threshold=args.dim_threshold,
    )
    out: dict = {"report": report}
    if args.lesson_pack:
        history_records = [
            {"sprint": i + 1, "score": s} for i, s in enumerate(data["sprint_scores"])
        ]
        out["lesson_pack"] = build_lesson_pack(
            sprint=len(data["sprint_scores"]),
            history=history_records,
            stagnation_report=report,
        )
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 1 if report["stagnation_overall"] or report["stagnant_dims"] else 0


if __name__ == "__main__":
    sys.exit(main())
