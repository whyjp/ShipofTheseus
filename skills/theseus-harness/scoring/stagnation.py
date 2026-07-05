#!/usr/bin/env python3
"""
점수 정체(stagnation) 감지기 — 무한 재귀 함정의 객관 측정 도구.

스프린트 점수 시계열과 차원별 sub-score 시계열을 받아, 정체 여부와
정체 차원, 권장 행동 (rewrite vs extend) 을 판단한다. sprint-narrative.md §4 의
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

stdout JSON. exit 는 항상 0 — 보고 모드(설계 B2 §2.2-4, 비게이팅).

의미 반전(§2.2-4): plateau(개선 정지) 는 이제 *정지 신호* 다 — 절대 점수가 낮아서
벌하는 것이 아니라, 실측 delta 가 0 에 수렴하면 "정직하게 수렴했다"는 종료 신호로 읽는다.
plateau 검출은 절대 임계(0.999)와 **완전히 분리**된다(delta 만으로 판정). 점수 절대값은
어디서도 종료·차단 게이트가 아니다. recommended_action 은 오케스트레이터가 소비하는 조언
필드일 뿐 CLI 자체가 게이팅하지 않으며, 종료 판정 권위는 manifest `stop_policy`(§2.2)다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def detect(
    sprint_scores: list[float],
    dim_history: dict[str, list[float]],
    threshold: float | None = None,
    window: int = 3,
    score_eps: float = 0.005,
    dim_eps: float = 0.005,
    dim_threshold: float = 0.95,
) -> dict:
    """정체(plateau) 감지 — 종합 + 차원별. 절대 임계와 분리(설계 B2 §2.2-4).

    plateau 는 delta 만으로 판정한다: 직전 `window` 스프린트 점수 spread < score_eps 면
    개선이 멈춘 것(=정직한 수렴 신호). 예전의 `and last < threshold`(0.999 floor) 결합을
    제거해, 절대 점수가 어디에도 게이트로 들어가지 않게 한다. plateau 는 이제 *정지 신호*
    이지 벌 대상이 아니다. threshold 인자는 하위호환·보고용으로만 params 에 남는다(비게이팅).
    """
    n = len(sprint_scores)
    overall = False
    overall_recent: list[float] = []
    if n >= window:
        overall_recent = sprint_scores[-window:]
        # 절대 점수 결합 제거 — plateau = 개선 정지(delta<eps), 점수 높낮이 무관.
        if (max(overall_recent) - min(overall_recent)) < score_eps:
            overall = True

    last_delta = (
        round(sprint_scores[-1] - sprint_scores[-2], 6) if n >= 2 else None
    )

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
            f"종합 점수가 {window} 스프린트 동안 {score_eps} 이내 변동(plateau, last_delta="
            f"{last_delta}) — 개선 정지 = 정직한 수렴 *정지 신호*(벌 아님). 최종 실측 점수를"
            " 정직 보고하고 종료 가능. rewrite/breakthrough 는 budget 여유 + opt-in 시 옵션."
        )
    elif stagnant_dims:
        action = "rewrite_module"
        names = ", ".join(d["dim"] for d in stagnant_dims)
        reason = (
            f"차원 정체 ({names}) — 해당 차원 보강 대상(조언). 종합 plateau 는 아니라 "
            "다음 스프린트에서 해당 차원을 targeted 보강 권장(비게이팅)."
        )
    else:
        action = "extend"
        reason = "plateau 아님(개선 진행 중) — 일반 다음 스프린트 진행 (이어서 보강)."

    return {
        # stagnation_overall = plateau(개선 정지) = 정지 신호. 이름은 하위호환 유지.
        "stagnation_overall": overall,
        "stop_signal": overall,
        "last_delta": last_delta,
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
    sprint-narrative.md §4 의 lesson_pack 구조를 만들어 반환.
    implementer/planner 호출 시 프롬프트에 첨부.
    """
    last_score = history[-1]["score"] if history else None
    threshold = stagnation_report["params"]["threshold"]
    rewrite = stagnation_report["recommended_action"].startswith("rewrite")
    pack = {
        "current_sprint": sprint,
        "current_score": last_score,
        "threshold": threshold,
        # delta_to_threshold(도달 불가 임계와의 거리)를 last_delta(직전 대비 실측 변화량)로
        # 교체 — 설계 B2 §2.3. 정지 신호는 절대 점수가 아니라 delta 다.
        "last_delta": stagnation_report.get("last_delta"),
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
    p.add_argument(
        "--threshold",
        type=float,
        default=None,
        help=(
            "하위호환·보고용 참조 임계 (default 없음 = 비게이팅). 설계 B2 §2.2-4 — plateau "
            "검출은 절대 임계와 분리되며 점수 절대값은 게이트가 아니다."
        ),
    )
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
    # 항상 exit 0 — 보고 모드(설계 B2 §2.2-4). plateau/차원정체는 조언 데이터일 뿐
    # CLI 가 게이팅하지 않는다. 점수 절대값은 어디서도 종료·차단 게이트가 아니다.
    return 0


if __name__ == "__main__":
    sys.exit(main())
