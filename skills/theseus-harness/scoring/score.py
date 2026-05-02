#!/usr/bin/env python3
"""
theseus-harness 스프린트 채점기.

사용법:
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
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", required=True, help="sprint-inputs.json 경로")
    p.add_argument("--prior", help="이전 스프린트 score 출력 경로 (회귀 판정용)")
    p.add_argument("--threshold", type=float, default=0.999)
    p.add_argument("--regression-threshold", type=float, default=0.05)
    args = p.parse_args(argv)

    with open(args.inputs) as f:
        inputs = json.load(f)

    sub = compute_sub_scores(inputs)
    raw = overall_score(sub)
    score, caps_applied = apply_caps(raw, inputs)

    prior_score = None
    regression = False
    if args.prior:
        with open(args.prior) as f:
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

    if regression:
        return 2
    return 0 if output["passes_threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
