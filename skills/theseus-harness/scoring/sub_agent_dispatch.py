#!/usr/bin/env python3
"""
서브에이전트 재귀 분해 디스패처 — sub-agents.md 의 알고리즘 구현.

부모 모듈이 하위 모듈 N 개를 parallel/sequential/competition 모드로
디스패치하고 결과를 머지. 깊이 2 한도, RAM 5 동시 한도, Opus 3 동시 한도.

sprint-34 / v0.9.39 — analyze-todos 추가. plan/06-plan.md 의 TODO DAG 를
파싱해 *sub-todo level* 병렬 그룹을 자동 도출. 모듈 단위 should_subdivide
와 직교 — TODO 단위 fine-grained 트리거.

사용:
    sub_agent_dispatch.py decide --module-spec spec.json
    sub_agent_dispatch.py merge --results results.json --mode parallel
    sub_agent_dispatch.py analyze-todos --plan-md plan/06-plan.md [--grade G4]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Windows console cp949 → 한글 stderr mojibake 방지
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

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


TODO_HEADER_RE = re.compile(r"^[\-\*]\s*\*\*\s*(T-\d{3,})\s*[—\-:]\s*(.+?)\*\*", re.M)
DEPENDS_RE = re.compile(r"^\s*[\-\*]?\s*의존\s*:\s*\[(.*?)\]", re.M)
DEPENDS_EN_RE = re.compile(r"^\s*[\-\*]?\s*depends\s*:\s*\[(.*?)\]", re.M | re.I)


def parse_todos(plan_text: str) -> list[dict]:
    """plan/06-plan.md 본문에서 TODO 항목을 파싱.

    각 TODO = `**T-NNN — title**` 헤더 + 그 다음 항목까지 본문에서 `의존: [T-XXX, ...]`
    추출. ID 가 발견되지 않은 의존은 무시.
    """
    todos: list[dict] = []
    matches = list(TODO_HEADER_RE.finditer(plan_text))
    for i, m in enumerate(matches):
        tid = m.group(1)
        title = m.group(2).strip().rstrip("`")
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(plan_text)
        body = plan_text[body_start:body_end]
        deps_match = DEPENDS_RE.search(body) or DEPENDS_EN_RE.search(body)
        deps_raw = deps_match.group(1) if deps_match else ""
        deps = [d.strip().strip("`'\"") for d in deps_raw.split(",") if d.strip()]
        deps = [d for d in deps if re.match(r"^T-\d{3,}$", d)]
        todos.append({"id": tid, "title": title, "deps": deps})
    return todos


def topological_levels(todos: list[dict]) -> dict:
    """Kahn 알고리즘 — 의존 없는 노드부터 level 단위로 그룹화.

    같은 level = 병렬 가능. 다음 level 은 직전 level 종료 후.
    cycle 검출 시 잔여 노드를 'cyclic' 그룹으로 별도 반환.
    """
    by_id = {t["id"]: t for t in todos}
    indeg = {t["id"]: 0 for t in todos}
    rev = {t["id"]: [] for t in todos}
    for t in todos:
        for d in t["deps"]:
            if d in by_id:
                indeg[t["id"]] += 1
                rev[d].append(t["id"])

    levels: list[list[str]] = []
    remaining = set(by_id)
    while remaining:
        layer = sorted(t for t in remaining if indeg[t] == 0)
        if not layer:
            break   # cycle
        levels.append(layer)
        for t in layer:
            remaining.discard(t)
            for s in rev[t]:
                indeg[s] -= 1

    return {
        "levels": levels,
        "cyclic": sorted(remaining),
    }


def analyze_todos(plan_text: str, grade: int = 4) -> dict:
    """plan/06-plan.md 텍스트 → 병렬 그룹 + 디스패치 모드 추천.

    output:
      {
        "total_todos": N,
        "groups": [["T-001"], ["T-010", "T-011"], ...],   # 같은 sublist = 병렬
        "max_parallel": M,
        "levels": K,
        "cyclic": [],
        "recommended_mode": "parallel" | "sequential" | "competition",
        "fan_out_recommendation": "...",
      }
    """
    todos = parse_todos(plan_text)
    if not todos:
        return {
            "total_todos": 0,
            "groups": [],
            "max_parallel": 0,
            "levels": 0,
            "cyclic": [],
            "recommended_mode": "sequential",
            "fan_out_recommendation": "no todos parsed — plan/06-plan.md 본문에 TODO DAG 부재 또는 형식 비정합",
        }

    layered = topological_levels(todos)
    groups = layered["levels"]
    max_par = max((len(g) for g in groups), default=0)
    cyclic = layered["cyclic"]

    if grade <= 2:
        mode = "sequential"
    elif grade == 3:
        mode = "sequential" if max_par <= 2 else "parallel"
    elif grade == 4:
        mode = "parallel" if max_par >= 2 else "sequential"
    else:   # G5
        mode = "competition" if max_par >= 3 else "parallel"

    if max_par > PARALLEL_FAN_OUT_LIMIT:
        rec = (
            f"max_parallel={max_par} > {PARALLEL_FAN_OUT_LIMIT} 한도 — "
            f"각 level 을 {PARALLEL_FAN_OUT_LIMIT} 단위 chunk 로 분할 dispatch"
        )
    elif max_par == 0:
        rec = "TODO 0 — TODO DAG 작성 필요"
    elif max_par == 1:
        rec = "병렬 가능 TODO 부재 — 순차 dispatch (의존 chain)"
    else:
        rec = (
            f"level {len(groups)} 단계, 최대 {max_par} 병렬 — "
            f"{mode} 모드 dispatch 권장"
        )
    if cyclic:
        rec = f"⚠ cyclic 의존 {cyclic} — 페이즈 06 회귀 후 재계획. " + rec

    return {
        "total_todos": len(todos),
        "groups": groups,
        "max_parallel": max_par,
        "levels": len(groups),
        "cyclic": cyclic,
        "recommended_mode": mode,
        "fan_out_recommendation": rec,
    }


def cmd_analyze_todos(args) -> int:
    plan = Path(args.plan_md)
    if not plan.exists():
        print(f"plan 파일 부재: {plan}", file=sys.stderr)
        return 1
    out = analyze_todos(plan.read_text(encoding="utf-8"), grade=args.grade)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    # cyclic 또는 0 todos = 비정상
    return 0 if (out["total_todos"] > 0 and not out["cyclic"]) else 1


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

    a = sub.add_parser(
        "analyze-todos",
        help="plan/06-plan.md TODO DAG → 병렬 그룹 + 디스패치 모드 (sprint-34 / v0.9.39)",
    )
    a.add_argument("--plan-md", required=True, help="plan/06-plan.md 경로")
    a.add_argument("--grade", type=int, default=4, choices=[1, 2, 3, 4, 5])
    a.set_defaults(func=cmd_analyze_todos)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
