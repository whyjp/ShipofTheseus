"""CheckSpec — 게이트의 기계 판독 정의 + measured 값에 대한 안전 평가기 (설계 §4.2).

게이트는 prose 가 아니라 CheckSpec 하나로 정의된다. assertion.expr 와 value 는
measured 값에 대한 '값 술어/결정 함수'이며, 자연어 판단이 될 수 없다.

WHY eval 을 쓰지 않았나: `eval` 은 임의 코드 실행 표면(`__import__`, 속성 접근,
호출)을 통째로 노출한다. 대신 AST 화이트리스트 평가기를 직접 구현해 '산술 + 비교 +
and/or/not + 리터럴'만 허용하고, 이름 참조는 measured 키로만 한정한다. 허용 목록에
없는 노드(Call/Attribute/Subscript/Lambda/comprehension 등)는 즉시 거부한다 —
따라서 위험 식은 평가에 도달하지 못한다(설계 위임 요구 §4.2).
"""
from __future__ import annotations

import ast
import json
import operator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class CheckSpecError(ValueError):
    """CheckSpec 로드/형태 검증 실패."""


class UnsafeExpressionError(ValueError):
    """허용 문법 밖의 식 — 평가 거부(임의 코드 실행 불가)."""


@dataclass
class Producer:
    cmd_pattern: str
    must_exit_zero: bool = True


@dataclass
class Assertion:
    expr: str
    on_fail: str


@dataclass
class CheckSpec:
    check_id: str
    phase: str
    grades: list[str]
    status: str
    producer: Producer
    provenance_required: list[str] = field(default_factory=list)
    assertions: list[Assertion] = field(default_factory=list)
    value: str | None = None
    absence_policy: str = "FAIL"


def from_dict(data: Any) -> CheckSpec:
    """dict → CheckSpec. 필수 필드 결손·타입오류 시 CheckSpecError."""
    if not isinstance(data, dict):
        raise CheckSpecError("checkspec root is not a JSON object")
    for fname in ("check_id", "phase", "producer"):
        if fname not in data:
            raise CheckSpecError(f"missing field: {fname}")
    prod = data["producer"]
    if not isinstance(prod, dict) or "cmd_pattern" not in prod:
        raise CheckSpecError("producer.cmd_pattern required")
    assertions = []
    for a in data.get("assertions", []):
        if not isinstance(a, dict) or "expr" not in a:
            raise CheckSpecError("assertion requires expr")
        assertions.append(Assertion(expr=a["expr"], on_fail=a.get("on_fail", a["expr"])))
    return CheckSpec(
        check_id=data["check_id"],
        phase=data["phase"],
        grades=list(data.get("grades", [])),
        status=data.get("status", "active"),
        producer=Producer(
            cmd_pattern=prod["cmd_pattern"],
            must_exit_zero=bool(prod.get("must_exit_zero", True)),
        ),
        provenance_required=list(data.get("provenance_required", [])),
        assertions=assertions,
        value=data.get("value"),
        absence_policy=data.get("absence_policy", "FAIL"),
    )


def load_checkspec(path: str | Path) -> CheckSpec:
    p = Path(path)
    if not p.exists():
        raise CheckSpecError(f"checkspec file not found: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CheckSpecError(f"checkspec not parseable JSON: {p}: {exc}") from exc
    return from_dict(data)


# --- 안전 평가기 (AST 화이트리스트) -------------------------------------------

# 허용 이항 연산: 산술만. bitwise/shift 등은 의도적으로 제외.
_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

# 허용 단항 연산: 부호 + 논리 부정.
_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.Not: operator.not_,
}

# 허용 비교: 순서/동등만. is/in 계열은 제외(컨테이너·아이덴티티 판단 불필요).
_COMPARE_OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

# 리터럴로 허용할 상수 타입 — 숫자/불리언/None/문자열.
_ALLOWED_CONST = (int, float, bool, str, type(None))


def safe_eval(expr: str, variables: dict[str, Any]) -> Any:
    """measured 변수 위에서 제한된 식을 평가. 위험 식은 UnsafeExpressionError.

    허용: 산술(+,-,*,/,//,%,**), 비교(<,<=,>,>=,==,!=), and/or/not, 숫자/불리언/None/문자열
    리터럴, 그리고 `variables` 에 존재하는 이름 참조뿐. 함수 호출·속성 접근·첨자·람다·
    컴프리헨션 등은 노드 단계에서 전부 거부된다.
    """
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise UnsafeExpressionError(f"cannot parse expression: {expr!r}: {exc}") from exc
    return _eval_node(tree.body, variables)


def _eval_node(node: ast.AST, variables: dict[str, Any]) -> Any:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, _ALLOWED_CONST):
            return node.value
        raise UnsafeExpressionError(f"disallowed constant type: {type(node.value).__name__}")

    if isinstance(node, ast.Name):
        # bool 값이 아닌 임의 이름은 measured 키로만 해석 — 미정의 이름은 거부.
        if node.id in variables:
            return variables[node.id]
        raise UnsafeExpressionError(f"unknown name (not a measured key): {node.id!r}")

    if isinstance(node, ast.BinOp):
        op = _BINOPS.get(type(node.op))
        if op is None:
            raise UnsafeExpressionError(f"disallowed binary operator: {type(node.op).__name__}")
        return op(_eval_node(node.left, variables), _eval_node(node.right, variables))

    if isinstance(node, ast.UnaryOp):
        op = _UNARYOPS.get(type(node.op))
        if op is None:
            raise UnsafeExpressionError(f"disallowed unary operator: {type(node.op).__name__}")
        return op(_eval_node(node.operand, variables))

    if isinstance(node, ast.BoolOp):
        values = [_eval_node(v, variables) for v in node.values]
        if isinstance(node.op, ast.And):
            result: Any = True
            for v in values:
                result = v
                if not v:
                    break
            return result
        if isinstance(node.op, ast.Or):
            result = False
            for v in values:
                result = v
                if v:
                    break
            return result
        raise UnsafeExpressionError(f"disallowed bool operator: {type(node.op).__name__}")

    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, variables)
        for op_node, comparator in zip(node.ops, node.comparators):
            op = _COMPARE_OPS.get(type(op_node))
            if op is None:
                raise UnsafeExpressionError(f"disallowed comparison: {type(op_node).__name__}")
            right = _eval_node(comparator, variables)
            if not op(left, right):
                return False
            left = right  # 체인 비교 (a < b < c) 지원
        return True

    raise UnsafeExpressionError(f"disallowed expression node: {type(node).__name__}")
