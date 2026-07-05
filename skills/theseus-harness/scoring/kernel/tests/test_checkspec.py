"""checkspec.py 단위 테스트 — 로더 + 안전 평가기 (테스트 (j) 포함).

실행: python -m pytest skills/theseus-harness/scoring/kernel -q
"""
from __future__ import annotations

import checkspec
import pytest
from checkspec import UnsafeExpressionError, safe_eval


def test_load_requires_producer_cmd_pattern():
    with pytest.raises(checkspec.CheckSpecError):
        checkspec.from_dict({"check_id": "x", "phase": "09", "producer": {}})


def test_from_dict_defaults():
    spec = checkspec.from_dict(
        {"check_id": "x", "phase": "09", "producer": {"cmd_pattern": "^python "}}
    )
    assert spec.status == "active"
    assert spec.absence_policy == "FAIL"
    assert spec.producer.must_exit_zero is True
    assert spec.value is None


def test_safe_eval_arithmetic_and_comparison():
    assert safe_eval("a + b * 2", {"a": 1, "b": 3}) == 7
    assert safe_eval("a / b", {"a": 40, "b": 42}) == 40 / 42
    assert safe_eval("a // b", {"a": 7, "b": 2}) == 3
    assert safe_eval("a % b", {"a": 7, "b": 2}) == 1
    assert safe_eval("tests_total > 0", {"tests_total": 42}) is True
    assert safe_eval("tests_failed == 0", {"tests_failed": 2}) is False


def test_safe_eval_boolean_and_chained():
    assert safe_eval("a and b", {"a": True, "b": False}) is False
    assert safe_eval("not flag", {"flag": False}) is True
    assert safe_eval("0 < x and x <= 1", {"x": 0.5}) is True
    # 체인 비교
    assert safe_eval("0 < x < 1", {"x": 0.5}) is True
    assert safe_eval("0 < x < 1", {"x": 5}) is False


def test_safe_eval_string_equality():
    assert safe_eval("parity == 'full'", {"parity": "full"}) is True
    assert safe_eval("parity == 'full'", {"parity": "smoke_only"}) is False


# --- 테스트 (j): 위험 식은 평가에 도달하지 못한다 ------------------------------


def test_safe_eval_rejects_import_and_calls():
    # __import__(...) 는 Call 노드 — 화이트리스트 밖이라 실행 전 거부.
    with pytest.raises(UnsafeExpressionError):
        safe_eval("__import__('os').system('echo pwned')", {})


def test_safe_eval_rejects_attribute_access():
    with pytest.raises(UnsafeExpressionError):
        safe_eval("x.__class__", {"x": 1})
    with pytest.raises(UnsafeExpressionError):
        safe_eval("().__class__.__bases__", {})


def test_safe_eval_rejects_subscript_and_lambda():
    with pytest.raises(UnsafeExpressionError):
        safe_eval("x[0]", {"x": [1, 2]})
    with pytest.raises(UnsafeExpressionError):
        safe_eval("(lambda: 1)()", {})


def test_safe_eval_rejects_unknown_name():
    # measured 키가 아닌 이름은 값이 아니라 거부 — 임의 전역 접근 차단.
    with pytest.raises(UnsafeExpressionError):
        safe_eval("secret + 1", {})
