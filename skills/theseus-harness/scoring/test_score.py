"""score.py 테스트. 실행: python -m pytest scoring/test_score.py -q"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCORE = Path(__file__).parent / "score.py"


def _run(inputs: dict, prior: dict | None = None, **flags) -> tuple[int, dict]:
    inputs_path = Path("/tmp/_score_inputs.json")
    inputs_path.write_text(json.dumps(inputs))
    args = [sys.executable, str(SCORE), "--inputs", str(inputs_path)]
    if prior is not None:
        prior_path = Path("/tmp/_score_prior.json")
        prior_path.write_text(json.dumps(prior))
        args += ["--prior", str(prior_path)]
    for k, v in flags.items():
        args += [f"--{k.replace('_', '-')}", str(v)]
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout)


def _green_inputs() -> dict:
    return {
        "test_pass_rate": 1.0,
        "intent_fidelity": 1.0,
        "files_mapped_to_todos": 10,
        "files_touched": 10,
        "modules_passing_solid": 4,
        "modules_total": 4,
        "dip_violation": False,
        "be_coverage": 0.95,
        "fe_coverage": 0.92,
        "fe_be_parity": "full",
        "e2e_passing": 5,
        "e2e_total": 5,
    }


def test_perfect_inputs_pass():
    rc, out = _run(_green_inputs())
    assert rc == 0
    assert out["passes_threshold"] is True
    assert out["score"] >= 0.9


def test_failing_e2e_drops_score_below_threshold():
    inputs = _green_inputs()
    inputs["e2e_passing"] = 0
    rc, out = _run(inputs)
    assert rc == 1
    assert out["sub_scores"]["e2e_pass"] == 0.0
    assert out["passes_threshold"] is False


def test_coverage_uses_min_of_be_and_fe():
    inputs = _green_inputs()
    inputs["be_coverage"] = 0.99
    inputs["fe_coverage"] = 0.10
    _, out = _run(inputs)
    assert out["sub_scores"]["coverage"] == 0.10


def test_skipped_tests_cap_at_05():
    inputs = _green_inputs()
    inputs["hard_exit_flags"] = {"skipped_or_only_tests": True}
    _, out = _run(inputs)
    assert out["score"] == 0.5
    assert any("skipped_or_only_tests" in c for c in out["caps_applied"])


def test_type_errors_cap_at_07():
    inputs = _green_inputs()
    inputs["hard_exit_flags"] = {"type_errors": True}
    _, out = _run(inputs)
    assert out["score"] == 0.7


def test_single_side_feature_redistributes_parity_weight():
    inputs = _green_inputs()
    inputs["fe_coverage"] = None
    inputs["fe_be_parity"] = "n/a"
    _, out = _run(inputs)
    assert out["sub_scores"]["fe_be_parity"] is None
    assert out["passes_threshold"] is True


def test_regression_triggers_exit_code_2():
    prior = {"score": 0.95}
    inputs = _green_inputs()
    inputs["test_pass_rate"] = 0.5
    rc, out = _run(inputs, prior=prior)
    assert rc == 2
    assert out["regression_triggered"] is True


def test_no_regression_when_within_threshold():
    prior = {"score": 0.92}
    inputs = _green_inputs()
    inputs["test_pass_rate"] = 0.95
    rc, out = _run(inputs, prior=prior)
    assert out["regression_triggered"] is False
    assert rc == 0


def test_zero_files_touched_does_not_divide_by_zero():
    inputs = _green_inputs()
    inputs["files_touched"] = 0
    inputs["files_mapped_to_todos"] = 0
    _, out = _run(inputs)
    assert out["sub_scores"]["scope_fit"] == 1.0


def test_dip_violation_caps_total_at_06():
    inputs = _green_inputs()
    inputs["dip_violation"] = True
    rc, out = _run(inputs)
    assert rc == 1
    assert out["score"] == 0.6
    assert out["dip_violation"] is True
    assert any("dip_violation" in c for c in out["caps_applied"])


def test_dip_violation_caps_solid_subscore_at_05():
    inputs = _green_inputs()
    inputs["dip_violation"] = True
    inputs["modules_passing_solid"] = 4
    inputs["modules_total"] = 4
    _, out = _run(inputs)
    assert out["sub_scores"]["solid"] == 0.5
