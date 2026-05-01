#!/usr/bin/env python3
"""Score a theseus-harness sprint against the rubric.

Usage:
    score.py --inputs sprint-inputs.json [--prior prior.json] [--regression-threshold 0.05]

Inputs JSON shape (all fields required unless marked optional):

{
  "test_pass_rate": 0.0..1.0,           # all suites combined
  "intent_fidelity": 1.0 | 0.7 | 0.0,   # from Phase 9 Gate 1
  "files_mapped_to_todos": int,
  "files_touched": int,
  "modules_passing_solid": int,
  "modules_total": int,
  "be_coverage": 0.0..1.0,
  "fe_coverage": 0.0..1.0,              # null if single-side feature
  "fe_be_parity": "full" | "missing_one" | "missing_two" | "smoke_only" | "n/a",
  "e2e_passing": int,
  "e2e_total": int,
  "hard_exit_flags": {                  # optional
    "skipped_or_only_tests": bool,
    "debug_prints": bool,
    "lint_errors": bool,
    "type_errors": bool
  }
}

Outputs JSON to stdout; non-zero exit if score < threshold (default 0.9).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

WEIGHTS = {
    "correctness": 0.25,
    "scope_fit": 0.10,
    "solid": 0.15,
    "coverage": 0.20,
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
    solid = _safe_div(d["modules_passing_solid"], d["modules_total"])

    fe_cov = d.get("fe_coverage")
    coverage = d["be_coverage"] if fe_cov is None else min(d["be_coverage"], fe_cov)

    parity = PARITY_SCORES[d["fe_be_parity"]]

    e2e_pass = _safe_div(d["e2e_passing"], d["e2e_total"], default=0.0)

    return SubScores(correctness, scope_fit, solid, coverage, parity, e2e_pass)


def overall_score(sub: SubScores) -> float:
    contributions = {
        "correctness": sub.correctness,
        "scope_fit": sub.scope_fit,
        "solid": sub.solid,
        "coverage": sub.coverage,
        "fe_be_parity": sub.fe_be_parity,
        "e2e_pass": sub.e2e_pass,
    }
    active = {k: v for k, v in contributions.items() if v is not None}
    weight_sum = sum(WEIGHTS[k] for k in active)
    return sum(WEIGHTS[k] * v for k, v in active.items()) / weight_sum


def apply_hard_caps(score: float, flags: dict | None) -> tuple[float, list[str]]:
    flags = flags or {}
    caps = []
    if flags.get("skipped_or_only_tests"):
        caps.append(("skipped_or_only_tests", 0.5))
    if flags.get("debug_prints"):
        caps.append(("debug_prints", 0.85))
    if flags.get("lint_errors"):
        caps.append(("lint_errors", 0.85))
    if flags.get("type_errors"):
        caps.append(("type_errors", 0.7))

    applied = []
    for name, cap in caps:
        if score > cap:
            score = cap
            applied.append(f"{name} -> capped at {cap}")
    return score, applied


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--inputs", required=True, help="path to sprint-inputs.json")
    p.add_argument("--prior", help="path to prior sprint's score output (for regression flag)")
    p.add_argument("--threshold", type=float, default=0.9)
    p.add_argument("--regression-threshold", type=float, default=0.05)
    args = p.parse_args(argv)

    with open(args.inputs) as f:
        inputs = json.load(f)

    sub = compute_sub_scores(inputs)
    raw = overall_score(sub)
    score, caps_applied = apply_hard_caps(raw, inputs.get("hard_exit_flags"))

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
        "prior_score": prior_score,
        "regression_triggered": regression,
        "passes_threshold": score >= args.threshold,
    }
    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")

    if regression:
        return 2
    return 0 if output["passes_threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
