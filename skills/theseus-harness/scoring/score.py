#!/usr/bin/env python3
"""
theseus-harness 스프린트 채점기.

**1차 경로(설계 §5, §7.1, WP4a)**: producer(measure_submission.py) → Evidence Record →
kernel.verify(scoring.* CheckSpec) → `aggregate_scores(dim_values, dip_violation)`.
즉 score.py 는 *커널/집계가 호출하는 순수 함수* 다 — 6 차원 커널 verdict 의 value 를
rubric 가중치로 가중평균하고 DIP 총점 hard cap 0.6 을 적용한다. N/A(None) 차원은 active
셋에서 제외하고 가중치를 재정규화한다(rubric "active dimensions").

**DEPRECATED**: 아래 `--inputs sprint-inputs.json` 직접 채점 경로는 손으로 쓴 자기 신고
값을 받는다(설계 P1). 하위호환·자기점검(self_lint --score) 용도로만 유지하며, 새 채점은
1차 경로를 쓴다. compute_sub_scores/overall_score/apply_caps/main 은 그 얇은 shim 이다.

사용법(deprecated shim):
    score.py --inputs sprint-inputs.json [--prior prior.json] [--regression-threshold 0.05]

inputs JSON 형식 (모든 필드 필수, 명시 표시 외):

{
  "test_pass_rate": 0.0..1.0,
  "intent_fidelity": 1.0 | 0.7 | 0.0,        # 페이즈 09 게이트 1 결과
  "files_mapped_to_todos": int,
  "files_touched": int,
  "modules_passing_solid": int,
  "modules_total": int,
  "dip_violation": bool,                       # 페이즈 09 게이트 3 의 DIP 항목
  "be_coverage": 0.0..1.0,
  "fe_coverage": 0.0..1.0 | null,              # 단일 사이드면 null
  "fe_be_parity": "full" | "missing_one" | "missing_two" | "smoke_only" | "n/a",
  "e2e_passing": int,
  "e2e_total": int,
  "hard_exit_flags": {                         # optional
    "skipped_or_only_tests": bool,
    "debug_prints": bool,
    "lint_errors": bool,
    "type_errors": bool
  }
}

stdout 으로 결과 JSON, exit code:
  0  = 임계 통과 (기본 임계 0.999 — 자율 최대 결과 지향)
  1  = 임계 미달
  2  = 회귀 트리거 (--prior 비교)
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

# kernel/_stdio 의 공유 UTF-8 강제 헬퍼 — argparse 한글 help/에러 등 자기 출력도
# cp949 콘솔에서 크래시하지 않도록. kernel/ 을 sys.path 에 올려 import.
_KERNEL_DIR = Path(__file__).resolve().parent / "kernel"
if str(_KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(_KERNEL_DIR))
from _stdio import force_utf8_stdio  # noqa: E402

WEIGHTS = {
    "correctness": 0.25,
    "scope_fit": 0.10,
    "solid": 0.20,
    "coverage": 0.15,
    "fe_be_parity": 0.10,
    "e2e_pass": 0.20,
}

PARITY_SCORES = {
    "full": 1.0,
    "missing_one": 0.7,
    "missing_two": 0.4,
    "smoke_only": 0.0,
    "n/a": None,
}

DIP_SOLID_CAP = 0.5
DIP_TOTAL_CAP = 0.6


@dataclass
class SubScores:
    correctness: float
    scope_fit: float
    solid: float
    coverage: float
    fe_be_parity: float | None
    e2e_pass: float


def _safe_div(a: float, b: float, default: float = 1.0) -> float:
    return a / b if b else default


def compute_sub_scores(d: dict) -> SubScores:
    correctness = d["test_pass_rate"] * d["intent_fidelity"]
    scope_fit = _safe_div(d["files_mapped_to_todos"], d["files_touched"])

    solid_raw = _safe_div(d["modules_passing_solid"], d["modules_total"])
    solid = min(solid_raw, DIP_SOLID_CAP) if d.get("dip_violation") else solid_raw

    fe_cov = d.get("fe_coverage")
    coverage = d["be_coverage"] if fe_cov is None else min(d["be_coverage"], fe_cov)

    parity = PARITY_SCORES[d["fe_be_parity"]]

    e2e_pass = _safe_div(d["e2e_passing"], d["e2e_total"], default=0.0)

    return SubScores(correctness, scope_fit, solid, coverage, parity, e2e_pass)


def overall_score(sub: SubScores) -> float:
    contribs = {
        "correctness": sub.correctness,
        "scope_fit": sub.scope_fit,
        "solid": sub.solid,
        "coverage": sub.coverage,
        "fe_be_parity": sub.fe_be_parity,
        "e2e_pass": sub.e2e_pass,
    }
    active = {k: v for k, v in contribs.items() if v is not None}
    weight_sum = sum(WEIGHTS[k] for k in active)
    return sum(WEIGHTS[k] * v for k, v in active.items()) / weight_sum


# scoring CheckSpec id → rubric 차원명(WEIGHTS 키). 커널 verdict(check_id 별)를 집계
# 입력(차원명별)으로 옮기는 유일 매핑. e2e 는 rubric 상 'e2e_pass'.
CHECK_ID_TO_DIM = {
    "scoring.correctness": "correctness",
    "scoring.scope_fit": "scope_fit",
    "scoring.solid": "solid",
    "scoring.coverage": "coverage",
    "scoring.fe_be_parity": "fe_be_parity",
    "scoring.e2e": "e2e_pass",
}


def aggregate_scores(dim_values: dict[str, float | None], dip_violation: bool) -> dict:
    """1차 경로 집계 — 6 차원 커널 verdict value → rubric 가중 총점 + DIP 총점 cap.

    dim_values 는 WEIGHTS 키(correctness/scope_fit/solid/coverage/fe_be_parity/e2e_pass)
    별 값. None 인 차원은 N/A(적용성 미충족)로 active 셋에서 제외하고 가중치를 active
    위에서 재정규화한다. DIP 위반 시 총점을 hard cap 0.6 으로 누른다(rubric 문면).

    WHY dip_violation 을 별도 인자로 받나: solid 차원 자체는 WP3 대로 DIP 위반 시 게이트
    FAIL(scoring.solid CheckSpec)이라 verdict pass 인 run 에서는 DIP=0 이다. 총점 0.6
    cap 은 그 위의 *이중 방어* — solid 게이트가 어떤 이유로 뚫려도 총점이 0.6 을 넘지
    못하게 한다(rubric.md "DIP 위반 = solid 게이트 FAIL + 총점 0.6 cap").
    """
    active = {k: v for k, v in dim_values.items() if v is not None}
    unknown = set(active) - set(WEIGHTS)
    if unknown:
        raise ValueError(f"unknown scoring dimensions: {sorted(unknown)}")
    weight_sum = sum(WEIGHTS[k] for k in active)
    if weight_sum == 0:
        raise ValueError("no active dimensions to aggregate (all N/A?)")
    raw = sum(WEIGHTS[k] * v for k, v in active.items()) / weight_sum
    capped = bool(dip_violation) and raw > DIP_TOTAL_CAP
    score = DIP_TOTAL_CAP if capped else raw
    return {
        "score": round(score, 4),
        "raw_score": round(raw, 4),
        "active_dimensions": sorted(active),
        "na_dimensions": sorted(k for k, v in dim_values.items() if v is None),
        "weight_sum": round(weight_sum, 4),
        "dip_violation": bool(dip_violation),
        "dip_capped": capped,
    }


def aggregate_from_meta_audit(report: dict, *, dip_violation: bool) -> dict:
    """meta_audit report → aggregate_scores. PASS=value, NA=None(제외). FAIL 은 집계
    대상이 아니다(게이트 실패한 run 의 총점은 무의미) — ValueError 로 크게 실패시킨다.

    이 어댑터가 1차 경로의 '커널 verdict → 총점' 연결부다. dip_violation 은 solid 측정에서
    이미 아는 값이라 명시로 받는다(evidence 내부를 다시 뜯지 않는다 — 결합도 최소).
    """
    results = report.get("results", {})
    dim_values: dict[str, float | None] = {}
    failed_gating: list[str] = []
    for check_id, dim in CHECK_ID_TO_DIM.items():
        outcome = results.get(check_id)
        if outcome is None:
            continue
        result = outcome.get("result")
        if result == "PASS":
            dim_values[dim] = outcome.get("value")
        elif result == "NA":
            dim_values[dim] = None
        else:  # FAIL
            failed_gating.append(check_id)
    if failed_gating:
        raise ValueError(
            f"cannot aggregate: gating checks failed: {sorted(failed_gating)}"
        )
    return aggregate_scores(dim_values, dip_violation)


def apply_caps(score: float, inputs: dict) -> tuple[float, list[str]]:
    flags = inputs.get("hard_exit_flags") or {}
    caps: list[tuple[str, float]] = []
    if flags.get("skipped_or_only_tests"):
        caps.append(("skipped_or_only_tests", 0.5))
    if flags.get("debug_prints"):
        caps.append(("debug_prints", 0.85))
    if flags.get("lint_errors"):
        caps.append(("lint_errors", 0.85))
    if flags.get("type_errors"):
        caps.append(("type_errors", 0.7))
    if inputs.get("dip_violation"):
        caps.append(("dip_violation", DIP_TOTAL_CAP))

    applied: list[str] = []
    for name, cap in caps:
        if score > cap:
            score = cap
            applied.append(f"{name} -> capped at {cap}")
    return score, applied


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", required=True, help="sprint-inputs.json 경로")
    p.add_argument("--prior", help="이전 스프린트 score 출력 경로 (회귀 판정용)")
    p.add_argument("--threshold", type=float, default=0.999)
    p.add_argument("--regression-threshold", type=float, default=0.05)
    p.add_argument(
        "--out",
        help=(
            "score 출력 JSON 을 파일로도 저장 (예: sprints/NN/score.json). "
            "stdout 은 그대로 유지 — webview/be4fe 가 score.json 을 직접 로드해 "
            "Sprints 차트의 데이터 소스로 사용 (v0.2.1 회귀 수정)."
        ),
    )
    args = p.parse_args(argv)

    with open(args.inputs, encoding="utf-8") as f:
        inputs = json.load(f)

    sub = compute_sub_scores(inputs)
    raw = overall_score(sub)
    score, caps_applied = apply_caps(raw, inputs)

    prior_score = None
    regression = False
    if args.prior:
        with open(args.prior, encoding="utf-8") as f:
            prior_score = json.load(f).get("score")
        if prior_score is not None and score < prior_score - args.regression_threshold:
            regression = True

    output = {
        "score": round(score, 4),
        "raw_score": round(raw, 4),
        "sub_scores": {
            "correctness": round(sub.correctness, 4),
            "scope_fit": round(sub.scope_fit, 4),
            "solid": round(sub.solid, 4),
            "coverage": round(sub.coverage, 4),
            "fe_be_parity": (
                None if sub.fe_be_parity is None else round(sub.fe_be_parity, 4)
            ),
            "e2e_pass": round(sub.e2e_pass, 4),
        },
        "caps_applied": caps_applied,
        "dip_violation": bool(inputs.get("dip_violation")),
        "prior_score": prior_score,
        "regression_triggered": regression,
        "passes_threshold": score >= args.threshold,
    }
    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")

    if args.out:
        # webview/be4fe 가 score.json 을 직접 로드 — Sprints 차트의 데이터 소스.
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
            f.write("\n")

    if regression:
        return 2
    return 0 if output["passes_threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
