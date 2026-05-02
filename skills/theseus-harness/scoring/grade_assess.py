#!/usr/bin/env python3
"""
그레이드 자동 추정 — 작업 원문에서 G1~G5 후보 산출.

grades.md 의 알고리즘을 코드로 구현. 페이즈 01 의 intent-extractor 가
호출해 자동 추정 그레이드를 intent/01-intent.md "스택 가정" 섹션에 기록,
페이즈 04 의 Q-G1 이 사용자 객관식으로 확정.

사용:
    grade_assess.py --request "작업 원문" [--repo-root <path>]

stdout JSON, exit 0 = G2~G5 (진행 가능), 1 = G1 (호출 거부 권고).
"""
from __future__ import annotations

import argparse
import json
import sys


# 키워드 카탈로그 (grades.md 와 일치)
TRIGGERS_G5 = ["결제", "금융", "payment", "billing", "안전", "safety", "의료", "medical", "암호화폐", "crypto"]
TRIGGERS_G4 = [
    "FE+BE", "프론트엔드", "백엔드", "frontend", "backend",
    "신규 도메인", "새 도메인", "리팩터", "refactor",
    "다중 모듈", "multi-module", "multiple modules",
]
TRIGGERS_G2 = [
    "단일 모듈", "single module", "작은 기능", "small feature",
    "추가", "add a", "add an", "한 함수", "one function",
]
TRIGGERS_G1 = [
    "한 줄", "oneline", "one line", "one-line",
    "rename", "리네임", "이름 변경",
    "typo", "오타",
    "버그 수정", "bug fix",
    "throwaway", "버릴", "스파이크", "spike",
]


def assess_grade(request_text: str) -> dict:
    """원문에서 후보 그레이드 산출. 가장 높은 후보가 primary (보수적)."""
    lower = request_text.lower()

    candidates: list[tuple[int, str]] = []

    if any(t in request_text or t in lower for t in TRIGGERS_G5):
        matched = [t for t in TRIGGERS_G5 if t in request_text or t in lower]
        candidates.append((5, f"Mission Critical 키워드 일치: {matched[:3]}"))

    if any(t in request_text or t in lower for t in TRIGGERS_G4):
        matched = [t for t in TRIGGERS_G4 if t in request_text or t in lower]
        candidates.append((4, f"Complex 키워드 (FE+BE / 새 도메인 / 리팩터): {matched[:3]}"))

    if any(t in request_text or t in lower for t in TRIGGERS_G2):
        matched = [t for t in TRIGGERS_G2 if t in request_text or t in lower]
        candidates.append((2, f"Simple 키워드 (단일 모듈 작은 기능): {matched[:3]}"))

    if any(t in request_text or t in lower for t in TRIGGERS_G1):
        matched = [t for t in TRIGGERS_G1 if t in request_text or t in lower]
        candidates.append((1, f"Trivial 키워드 — 호출 거부 권고: {matched[:3]}"))

    if not candidates:
        candidates.append((3, "키워드 매칭 없음 — Standard default"))

    # 가장 높은 그레이드 = primary (보수적)
    candidates.sort(key=lambda x: -x[0])
    primary_grade, primary_reason = candidates[0]

    # G1 만 단독 후보면 호출 거부 권고
    g1_only = len(candidates) == 1 and primary_grade == 1
    # G1 과 다른 후보가 같이 있으면 다른 후보 채택 (G2 이상)
    if g1_only:
        recommendation = "reject_harness_call"
    elif primary_grade == 5:
        recommendation = "tight_mode"
    elif primary_grade >= 3:
        recommendation = "full_or_standard"
    else:
        recommendation = "mini_harness"

    return {
        "primary_grade": primary_grade,
        "primary_reason": primary_reason,
        "all_candidates": [{"grade": g, "reason": r} for g, r in candidates],
        "require_user_confirmation": True,   # 항상 페이즈 04 Q-G1 으로 확정
        "recommendation": recommendation,
        "user_question_options": [
            "1. Grade 1 (Trivial) — 본 하네스 호출 거부",
            "2. Grade 2 (Simple) — 5 페이즈 / 7 컨벤션 / 임계 0.95",
            "3. Grade 3 (Standard) — 12 페이즈 / 12 컨벤션 / 임계 0.97",
            f"4. Grade 4 (Complex) — 14 페이즈 풀 / 26 컨벤션 / 임계 0.999{' (자동 추정)' if primary_grade == 4 else ''}",
            f"5. Grade 5 (Mission Critical) — 빡빡 모드 / 임계 0.99999{' (자동 추정)' if primary_grade == 5 else ''}",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--request", required=True, help="작업 원문 텍스트")
    args = p.parse_args(argv)
    out = assess_grade(args.request)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 1 if out["recommendation"] == "reject_harness_call" else 0


if __name__ == "__main__":
    sys.exit(main())
