"""score.py 테스트. 실행: python -m pytest scoring/test_score.py -q"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCORE = Path(__file__).parent / "score.py"


def _run(inputs: dict, prior: dict | None = None, **flags) -> tuple[int, dict]:
    import tempfile
    # 매 호출마다 독립 임시 파일 — 여러 테스트가 같은 경로를 공유하면 race / stale 위험.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(inputs, f)
        inputs_path = Path(f.name)
    args = [sys.executable, str(SCORE), "--inputs", str(inputs_path)]
    if prior is not None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(prior, f)
            prior_path = Path(f.name)
        args += ["--prior", str(prior_path)]
    for k, v in flags.items():
        args += [f"--{k.replace('_', '-')}", str(v)]
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, json.loads(proc.stdout)


def _green_inputs() -> dict:
    """모든 차원 1.0 — 임계 0.999 자율 최대 기준 통과용."""
    return {
        "test_pass_rate": 1.0,
        "intent_fidelity": 1.0,
        "files_mapped_to_todos": 10,
        "files_touched": 10,
        "modules_passing_solid": 4,
        "modules_total": 4,
        "dip_violation": False,
        "be_coverage": 1.0,
        "fe_coverage": 1.0,
        "fe_be_parity": "full",
        "e2e_passing": 5,
        "e2e_total": 5,
    }


def test_perfect_inputs_report_high_score_exit_zero():
    # 보고 모드(default, 설계 B2 §2.3) — 점수는 측정·보고, exit 0(비게이팅).
    rc, out = _run(_green_inputs())
    assert rc == 0
    assert out["score"] >= 0.999
    assert out["passes_threshold"] is True  # default 임계 0.0 → 보고 필드 True


def test_absolute_score_never_gates_exit():
    """설계 B2 §2.3 — 점수 절대값은 exit 을 좌우하지 않는다(도달 불가 0.999 게이트 제거)."""
    inputs = _green_inputs()
    inputs["be_coverage"] = 0.95
    inputs["fe_coverage"] = 0.92
    # 보고 모드 default(임계 0.0) — passes_threshold True, exit 0.
    rc, out = _run(inputs)
    assert rc == 0
    assert out["passes_threshold"] is True
    # 명시 임계 0.999 로 보고 필드는 False 가 되지만 exit 은 여전히 0(게이트 아님).
    rc, out = _run(inputs, threshold=0.999)
    assert rc == 0
    assert out["passes_threshold"] is False


def test_failing_e2e_drops_score_but_reports_exit_zero():
    inputs = _green_inputs()
    inputs["e2e_passing"] = 0
    rc, out = _run(inputs)
    # 측정 존치 — e2e_pass 0.0 반영, 낮은 점수 보고. 그러나 exit 0(비게이팅).
    assert rc == 0
    assert out["sub_scores"]["e2e_pass"] == 0.0
    # 명시 임계 0.999 에서 보고 필드만 False, exit 은 여전히 0.
    rc2, out2 = _run(inputs, threshold=0.999)
    assert rc2 == 0
    assert out2["passes_threshold"] is False


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
    # 회귀 임계는 0.05 — prior 0.92 vs current ~0.987 → 회귀 아님. 단, 0.999 임계는 미달이므로 명시 0.9.
    rc, out = _run(inputs, prior=prior, threshold=0.9)
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
    # DIP cap(측정) 존치 — score 0.6. exit 은 비게이팅(0, 회귀 아님).
    assert rc == 0
    assert out["score"] == 0.6
    assert out["dip_violation"] is True
    assert any("dip_violation" in c for c in out["caps_applied"])


def test_delta_field_reports_change_vs_prior():
    """delta 필드(직전 대비 변화량) 보고 — 값 기반 정지/회귀 신호의 원천(설계 B2 §2.3)."""
    prior = {"score": 0.90}
    inputs = _green_inputs()
    rc, out = _run(inputs, prior=prior, threshold=0.9)
    assert out["prior_score"] == 0.90
    assert out["delta"] is not None and out["delta"] > 0  # 개선(상승)
    assert out["regression_triggered"] is False
    assert rc == 0


def test_dip_violation_caps_solid_subscore_at_05():
    inputs = _green_inputs()
    inputs["dip_violation"] = True
    inputs["modules_passing_solid"] = 4
    inputs["modules_total"] = 4
    _, out = _run(inputs)
    assert out["sub_scores"]["solid"] == 0.5
