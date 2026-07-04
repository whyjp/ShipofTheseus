"""score.aggregate_scores / aggregate_from_meta_audit 단위 테스트 (WP4a 집계 경로).

요구: 6 차원 value → rubric 가중 총점; N/A(None) 차원 제외+재정규화; DIP 위반 시 총점
hard cap 0.6.
"""
from __future__ import annotations

import pytest

import score


def _all(v: float) -> dict:
    return {"correctness": v, "scope_fit": v, "solid": v, "coverage": v, "fe_be_parity": v, "e2e_pass": v}


def test_six_dims_full_marks_weighted_total_is_one():
    agg = score.aggregate_scores(_all(1.0), dip_violation=False)
    assert agg["score"] == 1.0
    assert agg["weight_sum"] == 1.0
    assert agg["na_dimensions"] == []
    assert agg["dip_capped"] is False


def test_weighted_average_matches_rubric_weights():
    dims = _all(1.0)
    dims["correctness"] = 0.0  # 가중치 0.25 만큼 손실
    agg = score.aggregate_scores(dims, dip_violation=False)
    # raw = (0.25*0 + 나머지 0.75*1) / 1.0 = 0.75
    assert abs(agg["raw_score"] - 0.75) < 1e-9
    assert abs(agg["score"] - 0.75) < 1e-9


def test_dip_violation_caps_total_at_06():
    """요구(집계): DIP 위반 시 총점 ≤ 0.6 (rubric hard cap, 이중 방어)."""
    agg = score.aggregate_scores(_all(1.0), dip_violation=True)
    assert agg["score"] == 0.6
    assert agg["dip_capped"] is True
    assert agg["raw_score"] == 1.0


def test_dip_cap_does_not_raise_low_score():
    """DIP cap 은 상한일 뿐 — 이미 0.6 미만이면 그대로."""
    agg = score.aggregate_scores(_all(0.4), dip_violation=True)
    assert agg["score"] == 0.4
    assert agg["dip_capped"] is False


def test_na_dimensions_excluded_and_weights_renormalized():
    """요구(N/A): None 차원은 active 셋에서 제외하고 가중치를 재정규화."""
    dims = _all(1.0)
    dims["coverage"] = None
    dims["fe_be_parity"] = None
    agg = score.aggregate_scores(dims, dip_violation=False)
    # active weight = 1.0 - 0.15(coverage) - 0.10(parity) = 0.75
    assert agg["weight_sum"] == 0.75
    assert agg["score"] == 1.0  # 나머지 전부 1.0 → 재정규화 후도 1.0
    assert agg["na_dimensions"] == ["coverage", "fe_be_parity"]


def test_unknown_dimension_raises():
    with pytest.raises(ValueError):
        score.aggregate_scores({"bogus": 1.0}, dip_violation=False)


def test_all_na_raises():
    dims = {k: None for k in _all(1.0)}
    with pytest.raises(ValueError):
        score.aggregate_scores(dims, dip_violation=False)


def test_aggregate_from_meta_audit_maps_pass_na_and_rejects_fail():
    report = {
        "results": {
            "scoring.correctness": {"result": "PASS", "value": 1.0},
            "scoring.scope_fit": {"result": "PASS", "value": 1.0},
            "scoring.solid": {"result": "PASS", "value": 1.0},
            "scoring.e2e": {"result": "PASS", "value": 1.0},
            "scoring.coverage": {"result": "NA", "value": None},
            "scoring.fe_be_parity": {"result": "NA", "value": None},
        }
    }
    agg = score.aggregate_from_meta_audit(report, dip_violation=False)
    assert agg["na_dimensions"] == ["coverage", "fe_be_parity"]
    assert agg["score"] == 1.0

    report["results"]["scoring.solid"] = {"result": "FAIL", "value": None}
    with pytest.raises(ValueError):
        score.aggregate_from_meta_audit(report, dip_violation=False)
