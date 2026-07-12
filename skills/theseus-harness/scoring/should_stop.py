#!/usr/bin/env python3
"""should_stop.py — 루프 정지조건 단일 코드 진입점 (manifest stop_policy 유일 권위, 설계 B2 §2.2).

phase 10 sprint loop 의 정지 판정을 manifest `stop_policy` 블록을 *유일 권위* 로 읽어 단일
boolean 으로 합성한다:

    stop = gate(meta_audit verdict pass) AND no_regression AND (plateau OR budget ≥ hard_cap)

기존 갭(하네스 리뷰 P1): stop_policy 는 manifest 에 *선언* 됐으나 이 합성식을 평가하는 코드
진입점이 없었다 — `manifest.stop_policy()` 는 dict 만 반환했고, 구 4-layer 보고모드 종료-조건
CLI(C1 에서 폐기)는 manifest 권위를 소비하지 않았으며, 합성 AND 는 오케스트레이터(LLM)가 세
산출물을 읽어 머릿속으로 조립했다. 본 모듈이 그 합성을 코드로 소유해 *루프 정지의 유일 권위*
가 됐고(폐기된 옛 CLI 를 대체), phase 09 게이트(meta_audit)와 *같은 커널 권위* 로 루프 제어
흐름을 돌린다(다이나믹 워크플로우의 코드기반 조건 검사).

producer/kernel 분리 유지: 값을 만들지 않는다. 이미 산출된 gate_meta_audit.json(verdict +
sprint.regression 결과) + sprint score 시계열 + budget 사용률 + manifest stop_policy 를 읽어
*합성만* 한다. plateau 는 stagnation.detect 재사용(DRY — 중복 구현 안 함).

호출자 규약: gate_report 는 phase-10 시점의 *전체* verdict(phase_upto 로 sprint.regression 을
deferred 시키지 않은 것)여야 한다 — sprint.regression 은 phase-10 체크라 루프 정지 판정의
직접 입력이다.

exit: 0 = stop(수렴/종료), 1 = continue(다음 sprint), 2 = 입력 오류.

저장소 self_lint C35 — 모든 open encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCORING_DIR = Path(__file__).resolve().parent
_KERNEL_DIR = _SCORING_DIR / "kernel"
for _p in (_SCORING_DIR, _KERNEL_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import stagnation  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402


def should_stop(
    *,
    gate_report: dict[str, Any],
    sprint_scores: list[float],
    grade: str,
    budget_used_ratio: float,
    stop_policy: dict[str, Any],
) -> dict[str, Any]:
    """manifest stop_policy 를 유일 권위로 정지 여부 합성. verdict/값 안 만들고 읽어서 AND 만.

    stop = gate_pass AND no_regression AND (plateau OR budget_bound).
    반환은 최종 boolean 뿐 아니라 각 성분과 사유를 담아 결정을 감사 가능하게 한다.
    """
    # 1. gate — meta_audit verdict pass (stop_policy.gate == "meta_audit_verdict_pass" 규약).
    gate_pass = gate_report.get("verdict") == "pass"

    # 2. no_regression — sprint.regression 이 *명시 FAIL* 일 때만 회귀. PASS/NA/부재 = 무회귀.
    #    stop_policy.no_regression=false 면 이 게이트를 요구하지 않는다(정책 존중).
    require_no_reg = bool(stop_policy.get("no_regression", True))
    sr = gate_report.get("results", {}).get("sprint.regression", {})
    observed_no_regression = sr.get("result") != "FAIL"
    no_regression = observed_no_regression if require_no_reg else True

    # 3. plateau — stagnation.detect 재사용(delta<eps, 절대점수 무관). window/eps 는 stop_policy.
    window = stop_policy.get("plateau_window", {}).get(grade)
    eps = float(stop_policy.get("plateau_eps", 0.005))
    plateau = False
    if window is not None and len(sprint_scores) >= int(window):
        plateau = bool(
            stagnation.detect(sprint_scores, {}, window=int(window), score_eps=eps)["stop_signal"]
        )

    # 4. budget — hard_cap 이상이면 정지(over-budget 방지 상한이지 소진 의무 아님).
    budget_cap = float(stop_policy.get("budget_hard_cap", 0.95))
    budget_bound = budget_used_ratio >= budget_cap

    stop = gate_pass and no_regression and (plateau or budget_bound)

    if stop:
        if plateau and budget_bound:
            trig = "plateau+budget≥cap"
        elif plateau:
            trig = "plateau"
        else:
            trig = "budget≥cap"
        reason = f"정지: gate_pass ∧ no_regression ∧ ({trig})."
    else:
        blockers: list[str] = []
        if not gate_pass:
            blockers.append("gate FAIL(meta_audit verdict≠pass)")
        if not no_regression:
            blockers.append("회귀(sprint.regression FAIL)")
        if not (plateau or budget_bound):
            blockers.append("미수렴(plateau 아님 ∧ budget<cap)")
        reason = "계속: " + " + ".join(blockers)

    return {
        "stop": stop,
        "verdict": "stop" if stop else "continue",
        "components": {
            "gate_pass": gate_pass,
            "no_regression": no_regression,
            "plateau": plateau,
            "budget_bound": budget_bound,
        },
        "budget_used_ratio": budget_used_ratio,
        "budget_hard_cap": budget_cap,
        "plateau_window": window,
        "reason": reason,
        "authority": "manifest.stop_policy",
    }


def _load_stop_policy(manifest_path: Path) -> dict[str, Any]:
    """manifest 에서 stop_policy 블록만 뽑는다(유일 권위 소스)."""
    import manifest as manifest_mod  # kernel/ (위에서 path 삽입)

    m = manifest_mod.load_manifest(manifest_path)
    return manifest_mod.stop_policy(m)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="should_stop — 루프 정지조건 단일 진입점(manifest stop_policy 합성, 설계 B2 §2.2)"
    )
    p.add_argument("--gate-report", required=True, help="gate_meta_audit.json (phase-10 전체 verdict)")
    p.add_argument(
        "--score-history", required=True,
        help='sprint 점수 시계열 JSON — {"sprint_scores": [...]} 또는 [...] (stagnation 포맷)',
    )
    p.add_argument("--grade", required=True, help="G2|G3|G4|G5 (plateau_window 선택)")
    p.add_argument("--budget-used", type=float, default=0.0, help="budget 사용률 0..1 (기본 0)")
    p.add_argument(
        "--manifest", default=None,
        help="pipeline.manifest.json (기본 관례: skills/theseus-harness/pipeline.manifest.json)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)

    try:
        gate_report = json.loads(Path(args.gate_report).read_text(encoding="utf-8"))
        hist = json.loads(Path(args.score_history).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: 입력 로드 실패: {exc}", file=sys.stderr)
        return 2
    sprint_scores = hist["sprint_scores"] if isinstance(hist, dict) else hist

    manifest_path = Path(args.manifest) if args.manifest else (_SCORING_DIR.parent / "pipeline.manifest.json")
    stop_policy = _load_stop_policy(manifest_path)

    result = should_stop(
        gate_report=gate_report,
        sprint_scores=sprint_scores,
        grade=args.grade,
        budget_used_ratio=args.budget_used,
        stop_policy=stop_policy,
    )
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    # exit = 정지 판정: 0 = stop(수렴), 1 = continue. `while ! should_stop; do sprint; done` 정합.
    return 0 if result["stop"] else 1


if __name__ == "__main__":
    sys.exit(main())
