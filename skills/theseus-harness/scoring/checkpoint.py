#!/usr/bin/env python3
"""
체크포인트 + 멀티버스 도구.

checkpoints.md 의 회귀 알고리즘과 멀티버스 라우팅을 코드로 구현.

명령:
    checkpoint.py create --phase NN --sequence MMM --snapshot-from <dir>
    checkpoint.py list --root <project> [--phase NN]
    checkpoint.py find-target --root <project> --failure-kind <kind> [--module M] [--sprint N]
    checkpoint.py multiverse --root <project> --branch <id> --universes N
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 회귀 라우팅 단일 소스 (P2 통합) — 회귀 분류 → 재진입 페이즈 매핑.
# 두 라벨 계열을 한 테이블로 통합한다(이원화 제거):
#   (a) 런타임 신호 계열 — stagnation/quality 신호가 낳는 failure_kind (checkpoints.md §회귀 알고리즘).
#   (b) phase-11 bisect 계열 — bisect 가 식별하는 4 defect class
#       (phases/11-regression-bisect.md §회귀 원인 분류).
# 두 계열은 정합한다: plan_defect~plan_misfit→06, impl_defect~module_impl_violation→08,
# data_defect~resource_ceiling→04. external_defect→09(게이트 재실행)만 bisect 고유.
# phases/11-regression-bisect.md 는 이 테이블을 *유일 코드 소스* 로 참조한다(문서=설명, 코드=권위).
# 문서↔코드 drift 는 test_checkpoint 의 가드가 FAIL 로 잡는다.
FAILURE_TO_PHASE: dict[str, str] = {
    # (a) 런타임 신호 계열
    "intent_mismatch": "01",
    "plan_misfit": "06",
    "module_impl_violation": "08",
    "test_regression": "10",
    "resource_ceiling": "04",
    "stagnation": "08",
    "dip_violation": "06",
    "scope_creep": "06",
    # (b) phase-11 bisect 4 defect class (sprint-05-e Q1 / P2 단일화)
    "plan_defect": "06",       # re-plan (universe 재분기 가능)
    "impl_defect": "08",       # re-impl (08-γ, 같은 plan 유지)
    "data_defect": "04",       # re-data (04 Q-D8 재검증)
    "external_defect": "09",   # re-env (09 게이트 재실행)
}

# phase-11 bisect 가 식별하는 4 defect class 부분집합 — 문서 C-RB1 ↔ 코드 라우팅 drift 가드용.
BISECT_DEFECT_CLASSES: tuple[str, ...] = (
    "plan_defect",
    "impl_defect",
    "data_defect",
    "external_defect",
)


def find_regression_target(
    project_root: Path,
    failure_kind: str,
    module: str | None = None,
    sprint: int | None = None,
) -> dict:
    """실패 원인 → 회귀할 체크포인트 ID 결정. 인터럽트 없음."""
    target_phase = FAILURE_TO_PHASE.get(failure_kind)
    if target_phase is None:
        return {
            "ok": False,
            "reason": f"unknown failure_kind: {failure_kind}",
            "fallback": "last_known_good",
        }

    phase_dir = project_root / "checkpoints" / target_phase
    if not phase_dir.exists():
        return {
            "ok": False,
            "target_phase": target_phase,
            "reason": f"체크포인트 없음 — 페이즈 {target_phase} 산출물 자체부터 재실행",
            "action": f"rerun_phase_{target_phase}",
        }

    # 페이즈 내 체크포인트들 중 매핑 적용
    candidates = sorted(p for p in phase_dir.iterdir() if p.is_dir())
    if not candidates:
        return {
            "ok": False,
            "reason": f"페이즈 {target_phase} 디렉터리 비어 있음",
        }

    # 모듈/스프린트 명시 시 해당 체크포인트 우선
    if module:
        for c in candidates:
            meta_path = c / "meta.md"
            if meta_path.exists() and module in meta_path.read_text(encoding="utf-8"):
                return _ok_target(target_phase, c, failure_kind, lesson_seed={"module": module})
    if sprint is not None and target_phase == "10":
        # 스프린트 직전 체크포인트
        before_id = f"10.{max(0, sprint - 1):02d}"
        for c in candidates:
            if c.name.startswith(before_id):
                return _ok_target(target_phase, c, failure_kind, lesson_seed={"sprint": sprint - 1})

    # 기본 — 페이즈의 가장 최근 체크포인트
    return _ok_target(target_phase, candidates[-1], failure_kind)


def _ok_target(phase: str, checkpoint_dir: Path, failure_kind: str, lesson_seed: dict | None = None) -> dict:
    return {
        "ok": True,
        "target_phase": phase,
        "checkpoint": checkpoint_dir.name,
        "checkpoint_path": str(checkpoint_dir),
        "failure_kind": failure_kind,
        "lesson_seed": lesson_seed or {},
        "action": "regress_then_retry_with_lesson_pack",
        "note": "checkpoints.md 의 자동 회귀 — 인터뷰 후 인터럽트 없음",
    }


def select_universe(universes: list[dict]) -> dict:
    """멀티버스 우주 비교 → 최적 우주 자율 선택 (인터럽트 없음)."""
    # 1. DIP 위반 우주 탈락
    alive = [u for u in universes if not u.get("dip_violation", False)]
    if not alive:
        return {
            "verdict": "halt_for_intent_mismatch",
            "reason": "모든 우주 DIP 위반 — autonomy.md 의 유일 예외 (의도 모순)",
        }

    alive.sort(key=lambda u: u.get("score", 0.0), reverse=True)
    top = alive[0]
    runner = alive[1] if len(alive) > 1 else None

    if runner is None or top["score"] - runner["score"] >= 0.05:
        return {
            "verdict": "select",
            "winner": top["id"],
            "winner_score": top["score"],
            "delta": (top["score"] - runner["score"]) if runner else None,
            "archive_to_losers": [u["id"] for u in alive[1:]],
            "reason": (
                f"우주 {top['id']} 점수 {top['score']:.4f} — "
                + (
                    f"runner-up {runner['id']} ({runner['score']:.4f}) 대비 Δ ≥ 0.05 압도"
                    if runner
                    else "단독 후보"
                )
            ),
        }

    # 점수 근접 — 코드 단순성 (LOC) 비교 (있으면)
    if all("loc" in u for u in alive[:2]):
        if top["loc"] <= runner["loc"]:
            base = top
        else:
            base = runner
        return {
            "verdict": "auto_merge",
            "base_universe": base["id"],
            "merge_from": (runner if base is top else top)["id"],
            "reason": f"점수 근접 (Δ {top['score']-runner['score']:.4f}) — 코드 단순성 우선 머지",
            "archive_to_losers": [u["id"] for u in alive[2:]],
        }

    return {
        "verdict": "select",
        "winner": top["id"],
        "winner_score": top["score"],
        "delta": top["score"] - runner["score"],
        "archive_to_losers": [u["id"] for u in alive[1:]],
        "reason": "점수 근접 + LOC 정보 부재 — 종합 점수 우위 채택",
    }


def cmd_find_target(args) -> int:
    out = find_regression_target(
        Path(args.root), args.failure_kind, module=args.module, sprint=args.sprint
    )
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if out.get("ok") else 1


def cmd_select_universe(args) -> int:
    universes = json.loads(Path(args.universes_json).read_text(encoding="utf-8"))
    out = select_universe(universes)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if out.get("verdict") in {"select", "auto_merge"} else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("find-target", help="실패 원인 → 회귀 체크포인트")
    pf.add_argument("--root", required=True, help=".ShipofTheseus/<프로젝트>/")
    pf.add_argument("--failure-kind", required=True, choices=sorted(FAILURE_TO_PHASE))
    pf.add_argument("--module", default=None)
    pf.add_argument("--sprint", type=int, default=None)
    pf.set_defaults(func=cmd_find_target)

    ps = sub.add_parser("select-universe", help="멀티버스 우주 비교 → 최적 선택")
    ps.add_argument("--universes-json", required=True, help="우주 [{id, score, dip_violation, loc?}] 배열 JSON")
    ps.set_defaults(func=cmd_select_universe)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
