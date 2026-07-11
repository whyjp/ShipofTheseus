"""test_should_stop.py — 루프 정지조건 단일 진입점 검증 (P1, manifest stop_policy 합성).

stop = gate(meta_audit verdict pass) AND no_regression AND (plateau OR budget≥cap).
라이브러리 순수 함수 6종 + 실 manifest 로 CLI exit code(0=stop / 1=continue).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import should_stop

# 실 manifest 의 stop_policy 와 동일 구조(단위 테스트 자족 fixture).
_STOP_POLICY = {
    "gate": "meta_audit_verdict_pass",
    "no_regression": True,
    "plateau_eps": 0.005,
    "plateau_window": {"G3": 2, "G4": 2, "G5": 3},
    "budget_hard_cap": 0.95,
}


def _gate(verdict="pass", sprint_regression="PASS"):
    return {"verdict": verdict, "results": {"sprint.regression": {"result": sprint_regression}}}


def _call(gate, scores, grade="G4", budget=0.3, policy=None):
    return should_stop.should_stop(
        gate_report=gate, sprint_scores=scores, grade=grade,
        budget_used_ratio=budget, stop_policy=policy or _STOP_POLICY,
    )


def test_stop_when_gate_pass_no_regression_plateau():
    """gate pass ∧ 무회귀 ∧ plateau(spread<eps) → 정지."""
    r = _call(_gate("pass", "PASS"), [0.90, 0.901])   # spread 0.001 < 0.005
    assert r["stop"] is True
    assert r["components"] == {
        "gate_pass": True, "no_regression": True, "plateau": True, "budget_bound": False,
    }


def test_continue_when_gate_fails():
    """gate FAIL → plateau 여도 계속(수렴 아님, 게이트 미충족)."""
    r = _call(_gate("fail", "PASS"), [0.90, 0.901])
    assert r["stop"] is False
    assert r["components"]["gate_pass"] is False


def test_continue_on_regression():
    """sprint.regression FAIL(회귀) → plateau 여도 계속(회귀 먼저 해소)."""
    r = _call(_gate("fail", "FAIL"), [0.90, 0.901])
    assert r["stop"] is False
    assert r["components"]["no_regression"] is False


def test_continue_when_not_converged():
    """gate pass ∧ 무회귀지만 개선 진행 중(no plateau) ∧ budget<cap → 계속."""
    r = _call(_gate("pass", "PASS"), [0.80, 0.90])   # spread 0.10 > eps
    assert r["stop"] is False
    assert r["components"]["plateau"] is False
    assert r["components"]["budget_bound"] is False


def test_stop_on_budget_cap_without_plateau():
    """plateau 아니어도 budget≥hard_cap 이면 정지(over-budget 방지 상한)."""
    r = _call(_gate("pass", "PASS"), [0.80, 0.90], budget=0.96)
    assert r["stop"] is True
    assert r["components"]["budget_bound"] is True
    assert r["components"]["plateau"] is False


def test_no_regression_policy_false_ignores_regression():
    """stop_policy.no_regression=false → 회귀 무시(정책 존중)."""
    policy = dict(_STOP_POLICY, no_regression=False)
    r = _call(_gate("pass", "FAIL"), [0.90, 0.901], policy=policy)
    assert r["components"]["no_regression"] is True
    assert r["stop"] is True


def test_cli_exit_codes(tmp_path):
    """실 manifest stop_policy 로 CLI: 정지→exit 0, 계속→exit 1."""
    gate = tmp_path / "gate.json"
    gate.write_text(json.dumps(_gate("pass", "PASS")), encoding="utf-8")

    def _run(scores):
        hist = tmp_path / "hist.json"
        hist.write_text(json.dumps({"sprint_scores": scores}), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(Path(should_stop.__file__)),
             "--gate-report", str(gate), "--score-history", str(hist),
             "--grade", "G4", "--budget-used", "0.3"],
            capture_output=True, text=True, encoding="utf-8",
        )

    stop = _run([0.90, 0.901])     # plateau → stop
    assert stop.returncode == 0, stop.stderr
    assert json.loads(stop.stdout)["stop"] is True

    cont = _run([0.80, 0.90])      # no plateau, budget<cap → continue
    assert cont.returncode == 1
    assert json.loads(cont.stdout)["stop"] is False
