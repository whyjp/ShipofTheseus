#!/usr/bin/env python3
"""
그레이드 추정 — 페이즈 01 의도 *전체* 신호 기반 (v0.9.17 sprint-11).

v0.9.16 까지의 *키워드 매칭* 알고리즘은 폐기 — 키워드는 도메인 어휘를 추적하지
못해 (예: simulation-bench 작업 = G3 default 으로 떨어짐) 잘못된 분류의 직접 원인.

페이즈 01 (의도 + 마인드맵) 자체가 그레이드 분류와 *강결합*. 본 함수는 의도
문서의 §a~§i 모든 섹션 + 마인드맵 복잡도를 *다중 신호 카탈로그* 로 받아 그레이드
추정. 마인드맵 복잡도는 *한 차원* 일 뿐 — 의도 §d 제약 수 / §f 스테이크홀더 /
§g 성공 지표 / §h 열린 질문 / §i Derived NFR 등 의도 페이즈 *전체* 신호 활용.

핵심 원칙:
  - **default = G4** (본 하네스 호출 자체가 G4+ 의도 신호)
  - **G5 상향** = 사용자 *명시 ack* 의무 (safety_critical / irreversible_change) — 자율 키워드 매칭 0
  - **G3 하향** = 마인드맵 *실재 단순* (positive evidence) + 모든 escalation trigger negative
  - **G2 하향** = G3 + 단일 모듈 + 단일 도메인 용어 + 마인드맵 nodes ≤ 5
  - **no signals (default 호출)** = G4 보존 — 데이터 없음 ≠ 단순함

호출 시점은 페이즈 04 Q-G1 직전 (페이즈 01 의도 + 마인드맵 완성 후).

사용:
    grade_assess.py --mindmap-json <path> --intent-json <path>
    grade_assess.py --signals '<json>'   # 직접 신호 입력 (테스트용)

stdout JSON, exit 0 항상 (그레이드는 내부 모듈레이션만, 진행/거부에 관여 X).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path


# ──────────────────────────────────────────────────────────────
# 신호 모델 — 페이즈 01 의도 §a~§i + 마인드맵 + 의도 외부 신호
# ──────────────────────────────────────────────────────────────


@dataclass
class GradeSignals:
    """페이즈 01 의도 + 마인드맵에서 추출한 18+ 차원 신호.

    intent-extractor 에이전트가 페이즈 01 산출물 (`intent/01-intent.md`) 작성 시
    부산물로 본 신호 dict 를 별도 산출 (예: `intent/01-grade-signals.json`).
    페이즈 04 직전에 본 함수가 이를 입력으로 받아 그레이드 추정.
    """

    # ── 마인드맵 복잡도 (하나의 차원, 전부 아님) ─────────────
    mindmap_node_count: int = 0          # 마인드맵 노드 수 (≥15 = mindmap-quality §3 B 임계, ≥25 = §4 A 임계)
    mindmap_axis_count: int = 0          # axis 수 (≥4 axis = G4 정합)
    mindmap_max_depth: int = 0           # 최대 깊이
    mindmap_external_systems: int = 0    # 외부 시스템 / dependency 수
    mindmap_domain_nouns: list[str] = field(default_factory=list)   # 도메인 어댑터 후보 noun

    # ── 의도 §a 무엇을 — 외부 관찰 가능 결과 ────────────────
    observable_results_count: int = 0    # 관찰 가능 결과 수

    # ── 의도 §c 비목표 — 명시 범위 ──────────────────────────
    explicit_non_goals_count: int = 0    # 명시 비목표 수 (많을수록 경계 명확 + 복잡)

    # ── 의도 §d 제약 — 성능/호환/보안/운영/마감 ─────────────
    constraint_count: int = 0            # 명시 제약 수 (5 카테고리 합)
    explicit_thresholds_count: int = 0   # numeric 임계 (200ms / 99.9% / 1k RPS 등)

    # ── 의도 §e 유비쿼터스 언어 ─────────────────────────────
    domain_term_count: int = 0           # 도메인 용어 수 (≥5 = 도메인 깊이)

    # ── 의도 §f 스테이크홀더 ────────────────────────────────
    stakeholder_count: int = 0           # 결과 소비자 수 (≥3 = G4+ 정합)

    # ── 의도 §g 성공 지표 ──────────────────────────────────
    success_metric_count: int = 0        # 외부 관찰 가능 지표 수
    measured_metrics_count: int = 0      # numeric 만 (성공 지표 부분집합)

    # ── 의도 §h 열린 질문 ──────────────────────────────────
    open_question_count: int = 0         # 모호함 수 (≥3 = 다중 결정 지점)

    # ── 의도 §i Derived NFRs (v0.9.6 nfr-derivation) ────────
    derived_nfr_count: int = 0           # qualitative NFR 수
    qualitative_adjective_count: int = 0 # 매핑된 형용사 수

    # ── 외부 evaluator / multi-scenario ────────────────────
    multi_scenario: bool = False         # multi-scenario 또는 sensitivity matrix 의무
    external_evaluator: bool = False     # bench / leaderboard / submission / external review

    # ── 인터페이스 / 리팩터 ────────────────────────────────
    fe_be_split: bool = False            # FE + BE 동시 (마인드맵에 frontend/backend axis 둘 다)
    refactor_scope_module_count: int = 0 # 리팩터 시 영향 모듈 수

    # ── 미션 크리티컬 신호 — 사용자 *명시 ack* 의무 ────────
    safety_critical: bool = False        # 결제/금융/의료/안전 — 사용자 *명시* (자율 키워드 매칭 X)
    irreversible_change: bool = False    # 데이터 마이그레이션 / 외부 거래 / 회복 불가 액션


# ──────────────────────────────────────────────────────────────
# Trigger 카탈로그 — 모두 generic 메트릭 (도메인 X)
# ──────────────────────────────────────────────────────────────


# G3 → G4 escalation 신호 (1+ 매칭 시 G4 강화). 5 차원.
ESCALATION_TRIGGERS = {
    "external_evaluator": "외부 evaluator (bench / leaderboard / submission / external review)",
    "measured_value_obligation": "measured value 의무 (numeric metric ≥ 1)",
    "multi_scenario": "multi-scenario 또는 sensitivity matrix",
    "domain_adapter_stack": "도메인 어댑터 stack 가능성 (마인드맵 도메인 noun ≥ 1)",
    "fe_be_split": "FE + BE 동시 진행",
}


# G4 → G3 하향 trigger — 다음 *모두 negative* 일 때만 단순 증명
PROVEN_SIMPLE_REQUIREMENTS = {
    # 의도 §d / §g — numeric 지표 0
    "no_explicit_thresholds": "explicit_thresholds_count == 0",
    "no_measured_metrics": "measured_metrics_count == 0",
    "no_multi_scenario": "multi_scenario == False",
    "no_external_evaluator": "external_evaluator == False",
    # 의도 §i — qualitative NFR 미적용
    "no_derived_nfr": "derived_nfr_count == 0",
    # 의도 §f / §h — stakeholder + open question 단순
    "single_stakeholder": "stakeholder_count <= 1",
    "few_open_questions": "open_question_count <= 1",
    # 마인드맵 — 실재 단순 (positive evidence, 0 ≠ 단순)
    "mindmap_present": "mindmap_node_count >= 1",       # 데이터 없으면 simple 증명 불가
    "mindmap_small": "mindmap_node_count <= 10",
    "mindmap_few_axes": "mindmap_axis_count <= 2",
    "no_domain_stack": "len(mindmap_domain_nouns) <= 1",
    # 인터페이스
    "no_fe_be": "fe_be_split == False",
}


# ──────────────────────────────────────────────────────────────
# 평가 함수
# ──────────────────────────────────────────────────────────────


def _check_escalation_triggers(s: GradeSignals) -> list[str]:
    matched: list[str] = []
    if s.external_evaluator:
        matched.append(ESCALATION_TRIGGERS["external_evaluator"])
    if s.measured_metrics_count >= 1:
        matched.append(ESCALATION_TRIGGERS["measured_value_obligation"])
    if s.multi_scenario:
        matched.append(ESCALATION_TRIGGERS["multi_scenario"])
    if s.mindmap_domain_nouns:
        matched.append(ESCALATION_TRIGGERS["domain_adapter_stack"])
    if s.fe_be_split:
        matched.append(ESCALATION_TRIGGERS["fe_be_split"])
    return matched


def _is_proven_simple(s: GradeSignals) -> tuple[bool, list[str], list[str]]:
    """단순함 *positive 증명*. 데이터 부재 (no signals) ≠ 단순.

    반환: (proven, satisfied_reasons, missing_reasons)
    """
    checks = {
        "no_explicit_thresholds": s.explicit_thresholds_count == 0,
        "no_measured_metrics": s.measured_metrics_count == 0,
        "no_multi_scenario": not s.multi_scenario,
        "no_external_evaluator": not s.external_evaluator,
        "no_derived_nfr": s.derived_nfr_count == 0,
        "single_stakeholder": s.stakeholder_count <= 1,
        "few_open_questions": s.open_question_count <= 1,
        "mindmap_present": s.mindmap_node_count >= 1,        # ← 데이터 없으면 단순 증명 불가
        "mindmap_small": 1 <= s.mindmap_node_count <= 10,
        "mindmap_few_axes": s.mindmap_axis_count <= 2,
        "no_domain_stack": len(s.mindmap_domain_nouns) <= 1,
        "no_fe_be": not s.fe_be_split,
    }
    satisfied = [k for k, v in checks.items() if v]
    missing = [k for k, v in checks.items() if not v]
    return (len(missing) == 0, satisfied, missing)


def _is_proven_trivial(s: GradeSignals) -> bool:
    """G3 → G2 — G3 단순 증명 + 매우 작은 마인드맵 + 단일 모듈."""
    proven, _, _ = _is_proven_simple(s)
    if not proven:
        return False
    if s.mindmap_node_count > 5:
        return False
    if s.refactor_scope_module_count > 1:
        return False
    if s.domain_term_count > 1:
        return False
    return True


def assess_grade(s: GradeSignals) -> dict:
    """페이즈 01 의도 + 마인드맵 신호 기반 그레이드 추정.

    default = G4. G5 상향은 사용자 명시 ack. G3·G2 하향은 단순함 *증명*.
    """
    # G5 — 사용자 명시 mission-critical (자율 키워드 매칭 0)
    if s.safety_critical or s.irreversible_change:
        reasons = []
        if s.safety_critical:
            reasons.append("safety_critical 사용자 명시")
        if s.irreversible_change:
            reasons.append("irreversible_change 사용자 명시")
        return {
            "primary_grade": 5,
            "primary_reason": " + ".join(reasons) + " (페이즈 01 의도 §b/§d)",
            "default_was": 4,
            "escalation_triggers_matched": _check_escalation_triggers(s),
            "require_user_confirmation": True,
            "recommendation": "tight_mode",
            "user_question_options": _grade_options(5),
        }

    # G3 / G2 하향 — 단순함 positive 증명 + 사용자 ack 의무
    proven_simple, satisfied, missing = _is_proven_simple(s)

    if proven_simple and _is_proven_trivial(s):
        return {
            "primary_grade": 2,
            "primary_reason": "마인드맵 단순함 증명 + 단일 모듈 + 단일 도메인 용어 — 사용자 ack 의무 (default 는 G4)",
            "default_was": 4,
            "escalation_triggers_matched": [],
            "deescalation_proven": True,
            "deescalation_satisfied": satisfied,
            "require_user_confirmation": True,
            "recommendation": "mini_harness",
            "user_question_options": _grade_options(2),
        }

    if proven_simple:
        return {
            "primary_grade": 3,
            "primary_reason": "단순함 12 차원 모두 negative — 사용자 ack 의무 (default 는 G4)",
            "default_was": 4,
            "escalation_triggers_matched": [],
            "deescalation_proven": True,
            "deescalation_satisfied": satisfied,
            "require_user_confirmation": True,
            "recommendation": "full_or_standard",
            "user_question_options": _grade_options(3),
        }

    # default G4 — 본 하네스 호출 자체가 G4+ 의도 신호
    triggers = _check_escalation_triggers(s)
    if triggers:
        reason = f"default G4 — escalation triggers 매칭: {triggers}"
    elif missing:
        reason = (
            "default G4 — 단순함 증명 미달 (다음 차원에서 단순 미증명: "
            + ", ".join(missing[:5])
            + ")"
        )
    else:
        reason = "default G4 — 본 하네스 호출 자체가 G4+ 의도 신호 (no signals fallback)"

    return {
        "primary_grade": 4,
        "primary_reason": reason,
        "default_was": 4,
        "escalation_triggers_matched": triggers,
        "deescalation_proven": False,
        "deescalation_missing": missing,
        "require_user_confirmation": True,
        "recommendation": "full_or_standard",
        "user_question_options": _grade_options(4),
    }


def _grade_options(primary: int) -> list[str]:
    return [
        f"1. Grade 1 (Trivial) — TBD (v0.5.x 후속){' (자동 추정)' if primary == 1 else ''}",
        f"2. Grade 2 (Simple) — 5 페이즈 / 7 컨벤션 / 임계 0.95{' (자동 추정)' if primary == 2 else ''}",
        f"3. Grade 3 (Standard) — 12 페이즈 / 12 컨벤션 / 임계 0.999{' (자동 추정)' if primary == 3 else ''}",
        f"4. Grade 4 (Complex, default) — 15 페이즈 풀 / 47 컨벤션 / 임계 0.999{' (자동 추정)' if primary == 4 else ''}",
        f"5. Grade 5 (Mission Critical) — 빡빡 모드 / 임계 0.99999{' (자동 추정)' if primary == 5 else ''}",
    ]


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────


def _load_signals(args: argparse.Namespace) -> GradeSignals:
    if args.signals:
        data = json.loads(args.signals)
        return GradeSignals(**data)
    data: dict = {}
    if args.mindmap_json:
        m = json.loads(Path(args.mindmap_json).read_text(encoding="utf-8"))
        data.update({
            "mindmap_node_count": int(m.get("node_count", 0)),
            "mindmap_axis_count": int(m.get("axis_count", 0)),
            "mindmap_max_depth": int(m.get("max_depth", 0)),
            "mindmap_external_systems": int(m.get("external_systems", 0)),
            "mindmap_domain_nouns": m.get("domain_nouns") or [],
        })
    if args.intent_json:
        i = json.loads(Path(args.intent_json).read_text(encoding="utf-8"))
        data.update({
            "observable_results_count": int(i.get("observable_results_count", 0)),
            "explicit_non_goals_count": int(i.get("explicit_non_goals_count", 0)),
            "constraint_count": int(i.get("constraint_count", 0)),
            "explicit_thresholds_count": int(i.get("explicit_thresholds_count", 0)),
            "domain_term_count": int(i.get("domain_term_count", 0)),
            "stakeholder_count": int(i.get("stakeholder_count", 0)),
            "success_metric_count": int(i.get("success_metric_count", 0)),
            "measured_metrics_count": int(i.get("measured_metrics_count", 0)),
            "open_question_count": int(i.get("open_question_count", 0)),
            "derived_nfr_count": int(i.get("derived_nfr_count", 0)),
            "qualitative_adjective_count": int(i.get("qualitative_adjective_count", 0)),
            "multi_scenario": bool(i.get("multi_scenario", False)),
            "external_evaluator": bool(i.get("external_evaluator", False)),
            "fe_be_split": bool(i.get("fe_be_split", False)),
            "refactor_scope_module_count": int(i.get("refactor_scope_module_count", 0)),
            "safety_critical": bool(i.get("safety_critical", False)),
            "irreversible_change": bool(i.get("irreversible_change", False)),
        })
    return GradeSignals(**data)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--mindmap-json", help="페이즈 01 마인드맵 신호 JSON")
    p.add_argument("--intent-json", help="페이즈 01 의도 신호 JSON")
    p.add_argument("--signals", help="GradeSignals JSON (직접 입력)")
    args = p.parse_args(argv)
    if not (args.mindmap_json or args.intent_json or args.signals):
        # no-data fallback — default G4 (본 하네스 호출 자체가 G4+)
        signals = GradeSignals()
    else:
        signals = _load_signals(args)
    out = assess_grade(signals)
    out["signals_used"] = asdict(signals)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
