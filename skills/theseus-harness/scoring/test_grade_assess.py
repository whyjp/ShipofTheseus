"""grade_assess.py 테스트 — 자동 그레이드 추정 검증."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

GRADE = Path(__file__).parent / "grade_assess.py"


def _run(request: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(GRADE), "--request", request],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.returncode, json.loads(proc.stdout)


def test_oneline_typo_routes_to_g1_tbd():
    rc, out = _run("typo 수정")
    assert rc == 0
    assert out["primary_grade"] == 1
    assert out["recommendation"] == "mini_harness_tbd"


def test_rename_routes_to_g1():
    rc, out = _run("이 함수 이름 rename 좀 해줘")
    assert rc == 0
    assert out["primary_grade"] == 1


def test_payment_routes_to_g5_critical():
    rc, out = _run("결제 시스템 추가")
    # 결제(G5) + 추가(G2) 가 함께 매칭되지만 보수적 = G5
    assert rc == 0
    assert out["primary_grade"] == 5
    assert out["recommendation"] == "tight_mode"


def test_fe_be_routes_to_g4_complex():
    rc, out = _run("FE+BE 다중 모듈로 새 도메인 추가")
    assert rc == 0
    assert out["primary_grade"] == 4


def test_simple_single_module_routes_to_g2():
    rc, out = _run("단일 모듈에 작은 기능 추가")
    assert rc == 0
    assert out["primary_grade"] == 2
    assert out["recommendation"] == "mini_harness"


def test_no_keywords_default_g3_standard():
    rc, out = _run("이 시스템 개선 작업")
    assert rc == 0
    assert out["primary_grade"] == 3


def test_all_5_options_in_user_question():
    """페이즈 04 Q-G1 의 5 보기 객관식이 항상 포함."""
    _, out = _run("아무거나")
    assert len(out["user_question_options"]) == 5
    assert "Grade 1" in out["user_question_options"][0]
    assert "Grade 5" in out["user_question_options"][4]


def test_higher_grade_wins_when_multiple_match():
    """G5 키워드 + G2 키워드 동시 매칭 → 보수적 G5 채택."""
    rc, out = _run("결제 단일 모듈 작은 기능")
    assert out["primary_grade"] == 5   # 보수적 = 가장 높은 그레이드


def test_report_includes_all_candidates():
    rc, out = _run("결제 FE+BE 작은 기능")
    grades_in_candidates = {c["grade"] for c in out["all_candidates"]}
    assert 5 in grades_in_candidates
    assert 4 in grades_in_candidates
    assert 2 in grades_in_candidates


def test_user_confirmation_always_required():
    _, out = _run("결제")
    assert out["require_user_confirmation"] is True


def test_g1_no_longer_rejects_harness_call():
    """v0.5.0 sprint-02-a — G1 도 진행. reject_harness_call recommendation 자체가 사라짐."""
    rc, out = _run("typo 한 줄 수정")
    assert rc == 0   # exit code 1 (거부) 더 이상 없음
    assert out["recommendation"] != "reject_harness_call"
    assert out["recommendation"] == "mini_harness_tbd"
