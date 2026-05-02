#!/usr/bin/env python3
"""
서브에이전트 재귀 분해 디스패처 — sub-agents.md 의 알고리즘 구현.

부모 모듈이 하위 모듈 N 개를 parallel/sequential/competition 모드로
디스패치하고 결과를 머지. 깊이 2 한도, RAM 5 동시 한도, Opus 3 동시 한도.

사용:
    sub_agent_dispatch.py decide --module-spec spec.json
    sub_agent_dispatch.py merge --results results.json --mode parallel
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEPTH_LIMIT = 2
PARALLEL_FAN_OUT_LIMIT = 5
OPUS_PARALLEL_LIMIT = 3


def should_subdivide(module: dict, grade: int = 4) -> dict:
    """sub-agents.md §"트리거 조건" — 하위 분해 필요 여부 판단."""
    title = module.get("title", "")
    estimated_loc = module.get("estimated_loc", 0)
    languages = set(module.get("languages") or [])
    explicit = module.get("subdivide", False)
    rewrite_streak = module.get("rewrite_streak", 0)

    if grade <= 2:
        return {"subdivide": False, "reason": "Grade 2 이하 — 분해 안 함"}

    triggers: list[str] = []

    threshold_loc = 300 if grade == 3 else 200
    if estimated_loc > threshold_loc:
        triggers.append(f"LOC {estimated_loc} > {threshold_loc}")

    if " and " in title.lower() or " 및 " in title or " + " in title:
        triggers.append("복합 책임 키워드 (and/및/+)")

    if len(languages) >= 2:
        triggers.append(f"다중 스택: {sorted(languages)}")

    if explicit:
        triggers.append("planner 가 subdivide:true 명시")

    if rewrite_streak >= 3:
        triggers.append(f"회귀 누적 {rewrite_streak} 회 → 분해로 전환")

    if not triggers:
        return {"subdivide": False, "reason": "트리거 신호 없음"}

    # 깊이 한도
    depth = module.get("depth", 0)
    if depth >= DEPTH_LIMIT:
        return {
            "subdivide": False,
            "regress_to_plan": True,
            "reason": f"깊이 {depth} ≥ 한도 {DEPTH_LIMIT} → 페이즈 06 자동 회귀",
        }

    return {
        "subdivide": True,
        "triggers": triggers,
        "next_depth": depth + 1,
        "recommended_mode": _recommend_mode(grade, len(triggers)),
    }


def _recommend_mode(grade: int, signal_count: int) -> str:
    """그레이드 + 신호 수에 따라 디스패치 모드 추천."""
    if grade == 5:
        return "competition"
    if grade == 4 and signal_count >= 2:
        return "parallel"
    return "sequential"   # G3 default


def merge_sub_results(results: list[dict], mode: str) -> dict:
    """
    하위 결과 머지 — sub-agents.md §"머지 룰".
    competition 모드는 checkpoint.py 의 select_universe 와 같은 알고리즘.
    """
    if not results:
        return {"merged": False, "reason": "결과 없음"}

    # 같은 파일 직렬 가드 (build-and-config.md §7)
    file_writers: dict[str, list[str]] = {}
    for r in results:
        for f in r.get("files_written", []):
            file_writers.setdefault(f, []).append(r["id"])
    conflicts = {f: ids for f, ids in file_writers.items() if len(ids) > 1}
    if conflicts and mode in {"parallel", "sequential"}:
        return {
            "merged": False,
            "reason": f"같은 파일 직렬 가드 위반: {conflicts}",
            "guard_violation": True,
        }

    if mode == "competition":
        # DIP 위반 탈락
        alive = [r for r in results if not r.get("dip_violation", False)]
        if not alive:
            return {"merged": False, "reason": "모든 하위 DIP 위반 — halt", "halt": True}
        alive.sort(key=lambda r: r.get("score", 0.0), reverse=True)
        top = alive[0]
        runner = alive[1] if len(alive) > 1 else None
        if runner is None or top["score"] - runner["score"] >= 0.05:
            return {
                "merged": True,
                "verdict": "select",
                "winner": top["id"],
                "winner_score": top["score"],
                "losers": [r["id"] for r in alive[1:]],
                "mode": mode,
            }
        # 점수 근접 — LOC 단순성 우선 머지
        loc_a = top.get("loc", float("inf"))
        loc_b = runner.get("loc", float("inf"))
        base = top if loc_a <= loc_b else runner
        return {
            "merged": True,
            "verdict": "auto_merge",
            "base": base["id"],
            "merge_from": (runner if base is top else top)["id"],
            "mode": mode,
        }

    # parallel / sequential — 모두 채택
    return {
        "merged": True,
        "verdict": "accept_all",
        "ids": [r["id"] for r in results],
        "total_score": sum(r.get("score", 0.0) for r in results) / len(results),
        "mode": mode,
    }


def cmd_decide(args) -> int:
    spec = json.loads(Path(args.module_spec).read_text(encoding="utf-8"))
    out = should_subdivide(spec, grade=args.grade)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if out.get("subdivide") else 1


def cmd_merge(args) -> int:
    results = json.loads(Path(args.results).read_text(encoding="utf-8"))
    out = merge_sub_results(results, mode=args.mode)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if out.get("merged") else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("decide", help="하위 분해 필요 여부 판단")
    d.add_argument("--module-spec", required=True)
    d.add_argument("--grade", type=int, default=4)
    d.set_defaults(func=cmd_decide)

    m = sub.add_parser("merge", help="하위 결과 머지")
    m.add_argument("--results", required=True)
    m.add_argument("--mode", choices=["parallel", "sequential", "competition"], default="parallel")
    m.set_defaults(func=cmd_merge)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
