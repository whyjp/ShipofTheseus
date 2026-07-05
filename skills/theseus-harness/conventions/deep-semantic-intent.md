---
id: deep-semantic-intent
category: interview
applies-to-phases: '[01,04]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Deep Semantic Intent — adjective 너머 *implied operational framing* 추출

## 한 줄 요약

**페이즈 01 §i 가 prompt 의 *qualitative adjectives* 만 NFR 로 추출하던 v0.9.6 패턴을 확장 — *adjective + 도메인 noun* 결합 패턴으로 *implied operational framing* (operator decision-support / uncertainty quantification / risk-adjusted recommendation 등) 도 동시 추출.** v0.9.6-12 의 self-estimate 97 plateau 의 진짜 원인 = 의도 확장 미달. 본 컨벤션이 ceiling-breaking 1순위.

## 1. 결손 진단

v0.9.6 [`nfr-derivation.md`](nfr-derivation.md) 의 §i =adjective 추출만 (clear / reproducible / interpretable 등). prompt 의 다음 implied semantic 미추출 :

| Surface (현재 §i) | Implied (현재 미추출) | 영향 |
|---|---|---|
| "answer the following questions" | **decision-support framing** — 답이 yes/no 가 아닌 *risk-adjusted action* + confidence band | Results 14→15 (1pt) |
| "operator" / "decision" 명사 | **uncertainty quantification depth** — CI95 외 robustness sensitivity (가정 변경 시 결정 변하는가) | Sim correctness 19→20 (1pt) |
| "scenarios" 복수 | **integrated narrative across scenarios** — per-scenario 답 아닌 *capex sequence under uncertainty* | Conceptual 19→20 (1pt) |
| "additional scenario" optional | **opportunity cost framing** — 본 모델 외 대안 인식 | Results +0~1pt |

→ self-estimate 97 plateau 의 결손 1-3pt 가 이 차원에서. 현재 §i 의 *1차 추출* 만으로는 도달 불가.

## 2. 운영 룰 — 2nd-order extraction

페이즈 01 의 intent-extractor.md step 4-bis 확장 :

### Step A — Surface (1차, v0.9.6 carry)

prompt 의 *qualitative adjectives* → §i NFR 후보 (Q1~Q10).

### Step B — Combined (2차, v0.9.13 신규)

prompt 의 *adjective × 도메인 noun* 결합 패턴 → *implied operational framing* :

```python
def extract_implied_framings(prompt: str) -> list[ImpliedFraming]:
    framings = []

    # Decision-support framing
    if matches(prompt, [r"answer.*questions", r"operator.*decision", r"decision.*support"]):
        framings.append(ImpliedFraming(
            id="decision-support",
            evidence=quote_lines(...),
            verification="recommendations include risk-adjusted action + confidence band, NOT just yes/no",
        ))

    # Uncertainty quantification depth
    if matches(prompt, [r"95%\s*CI", r"reproducible", r"sensitivity"]):
        framings.append(ImpliedFraming(
            id="uncertainty-depth",
            evidence=...,
            verification="propagation: CI95 + sensitivity-of-decision (가정 변경 시 결정 flip 여부)",
        ))

    # Integrated narrative
    if matches(prompt, [r"scenarios", r"\b6\b.*scenario", r"trade-?off"]):
        framings.append(ImpliedFraming(
            id="integrated-narrative",
            evidence=...,
            verification="capex sequence + conditional dependency (R1→R2 when, R2 alone when)",
        ))

    # Opportunity cost
    if matches(prompt, [r"additional scenario", r"alternative", r"trade-?off"]):
        framings.append(ImpliedFraming(
            id="opportunity-cost",
            evidence=...,
            verification="외부 대안 (해당 capex 대신 다른 투자) 명시",
        ))

    return framings
```

매칭 0개 = "본 prompt 는 functional-only" 명시 (drift 가드).

### Step C — implied framing → derived gate

페이즈 09 derived gate 자동 추가 — 각 implied framing 의 verification protocol 그대로.

예 : "decision-support" → DG-DS-1 = `outputs/operational_recommendations.txt` 의 R1~R5 모두 *confidence band 명시* + *risk-adjusted phrasing* (예: "high confidence, recommend pilot" / "low confidence, hold").

## 3. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- adjective + noun 결합 카탈로그 = 의미군 단위 (decision-support / uncertainty / integrated-narrative / opportunity-cost), 도메인 X.
b- regex 패턴 = generic, 도메인 X.
c- verification protocol = 의미군 단위, 케이스 X.

## 4. 안티 패턴

a- **Surface 만 적용 (v0.9.6 한정)** — adjective 추출하고 implied framing 추출 0. §i 절에 *adjective + implied 두 절 분리* 검증 의무 (주의: self_lint 의 `C-DSI` 는 data-structure-invariants.md 룰과 동명이인 — 미등록).
b- **Implied framing 매칭 0인데 functional-only 명시 누락** — 본 컨벤션의 drift 가드 위반.
c- **Verification protocol 이 surface 와 동일** — 형식적 implied 박힘, *질적 차이 0*. 텍스트 차이 ≥ 50% 검증 의무 (C-DSI-VERIFY, 미등록).

## 5. v0.9.13 효과 추정

v01_cold (v0.9.9, self-estimate 97) retroactive 적용 :
- decision-support framing 적용 → operational_recommendations.txt 의 R1~R5 에 *confidence band* 추가 → +1pt (Results)
- uncertainty-depth framing → conceptual_model.md 에 sensitivity-of-decision 절 추가 → +1pt (Sim correctness)
- integrated-narrative → R1→R2→R5 *조건부 sequencing* 명시 → +1pt (Conceptual)

→ 97 → 99-100 도달 가능. 천정 self-estimate 97 의 *진짜 깨기*.

## 6. 호환성

- v0.9.6 nfr-derivation = surface adjective 추출 (1차)
- 본 컨벤션 = surface + implied (2차)
- v0.9.7 premortem-friction / [`mindmap-quality.md`](mindmap-quality.md) §2 (sprint-37 PR-AD 통합) / 기타 모두 *직교* — surface NFR + implied framing 모두 §i 의 노드로 박힘.

## 7. 자기 검증

본 컨벤션 자체에 적용 시 — 본 문서의 implied framing = "derivation depth as a quality dimension" / "ceiling-breaking via semantic layer addition" / "harness self-improvement bound by extraction shallowness". §1 의 plateau 분석 = 본 컨벤션 자체의 implied framing 적용 결과.
