"""grade_assess.py 테스트 — v0.9.17 sprint-11: 키워드 매칭 폐기 + 페이즈 01 다중 신호 + default G4."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

GRADE = Path(__file__).parent / "grade_assess.py"


def _run(signals: dict | None = None) -> tuple[int, dict]:
    args = [sys.executable, str(GRADE)]
    if signals is not None:
        args += ["--signals", json.dumps(signals)]
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, json.loads(proc.stdout)


# ── default G4 (v0.9.17 핵심) ─────────────────────────


def test_no_signals_defaults_to_g4():
    """no signals (CLI 인자 없음) = default G4 — 본 하네스 호출 자체가 G4+ 의도 신호."""
    rc, out = _run()
    assert rc == 0
    assert out["primary_grade"] == 4
    assert out["default_was"] == 4


def test_empty_signals_defaults_to_g4():
    rc, out = _run({})
    assert rc == 0
    assert out["primary_grade"] == 4


# ── G5 상향 — 사용자 명시 ack 만 ─────────────────────


def test_safety_critical_routes_to_g5():
    rc, out = _run({"safety_critical": True})
    assert rc == 0
    assert out["primary_grade"] == 5
    assert out["recommendation"] == "tight_mode"


def test_irreversible_change_routes_to_g5():
    rc, out = _run({"irreversible_change": True})
    assert out["primary_grade"] == 5


# ── G3 하향 — 단순함 positive 증명 ───────────────────


def test_proven_simple_routes_to_g3():
    """12 차원 모두 negative + mindmap 실재 작음 → G3 단순 증명."""
    rc, out = _run({"mindmap_node_count": 8, "mindmap_axis_count": 2, "stakeholder_count": 1})
    assert rc == 0
    assert out["primary_grade"] == 3
    assert out["deescalation_proven"] is True


def test_proven_trivial_routes_to_g2():
    """G3 단순 증명 + nodes ≤5 + 단일 모듈 + 단일 도메인 용어 → G2."""
    rc, out = _run({
        "mindmap_node_count": 5,
        "mindmap_axis_count": 1,
        "stakeholder_count": 1,
        "refactor_scope_module_count": 1,
        "domain_term_count": 1,
    })
    assert out["primary_grade"] == 2


# ── escalation triggers ─────────────────────────────


def test_external_evaluator_keeps_g4():
    """external_evaluator + measured metrics + multi-scenario → default G4 유지 + triggers list 명시."""
    rc, out = _run({
        "external_evaluator": True,
        "measured_metrics_count": 5,
        "multi_scenario": True,
    })
    assert out["primary_grade"] == 4
    triggers = out["escalation_triggers_matched"]
    assert any("evaluator" in t.lower() for t in triggers)
    assert any("measured value" in t.lower() for t in triggers)
    assert any("multi-scenario" in t.lower() for t in triggers)


def test_fe_be_split_keeps_g4():
    rc, out = _run({"fe_be_split": True})
    assert out["primary_grade"] == 4


def test_domain_adapter_stack_keeps_g4():
    rc, out = _run({"mindmap_domain_nouns": ["mining", "DES"]})
    assert out["primary_grade"] == 4


# ── 키워드 매칭 폐기 검증 ────────────────────────────


def test_signal_only_no_keyword_matching():
    """v0.9.17: 키워드 (결제 / payment / FE+BE) 매칭 없음 — signals 만으로 결정."""
    # signals 0 → default G4. 사용자 텍스트와 무관.
    rc, out = _run({})
    assert out["primary_grade"] == 4
    # 신호 하나라도 negative-direction 이면 단순 증명 미달
    rc, out = _run({"external_evaluator": True})
    assert out["primary_grade"] == 4   # G3 으로 떨어지지 않음


# ── 사용자 확정 의무 ────────────────────────────────


def test_user_confirmation_always_required():
    for signals in [{}, {"safety_critical": True}, {"mindmap_node_count": 5}]:
        _, out = _run(signals)
        assert out["require_user_confirmation"] is True


def test_all_5_options_in_user_question():
    _, out = _run()
    assert len(out["user_question_options"]) == 5
    assert "Grade 1" in out["user_question_options"][0]
    assert "Grade 5" in out["user_question_options"][4]


# ── G1 진행 보존 (v0.5.0 룰 정합) ────────────────────


def test_g1_no_longer_rejects_harness_call():
    """G1 추정도 진행 — reject_harness_call recommendation 부재."""
    rc, out = _run({})
    assert rc == 0
    assert out["recommendation"] != "reject_harness_call"


def test_signals_used_echoed():
    """추정 결과에 입력 signals 가 echo 되어 사후 audit 가능."""
    _, out = _run({"safety_critical": True, "mindmap_node_count": 7})
    assert "signals_used" in out
    assert out["signals_used"]["safety_critical"] is True
    assert out["signals_used"]["mindmap_node_count"] == 7
