# Budget Saturation Loop — sprint loop budget 끝까지 사용 + deeper improvement

## 한 줄 요약

**페이즈 10 sprint loop 의 default 임계 = 0.999** (모든 그레이드). 조기 종료 금지 — minimum budget 사용률 ≥ 80% 강제. 매 sprint 의 lesson = weakest dim 의 *content depth* 추가 (단순 enforcement 아닌). v0.9.8 sprint-regression-loop 의 *조기 종료 회피* 룰 + 임계 정정.

## 1. 결손 진단

v0.9.8 [`sprint-regression-loop.md`](sprint-regression-loop.md) 의 룰 :
- 모든 dim `score/max ≥ threshold` → CONVERGED, 종료
- threshold = grades.md 의 0.97 (G3) / 0.999 (G4) / 0.99999 (G5)

cold session 결과 :

| 회차 | budget | 사용 | sprint | 종료 |
|---|---|:---:|:---:|---|
| v091_cold01 (v0.9.12) | 90 min | 28% (25 min) | 1 | 0.97 first-try PASS → 종료 |
| v0913_cold01 (v0.9.13) | 90 min | 69% (62 min) | 3 | 0.999 도달 → 종료 |
| v0914_cold01 (v0.9.14) | 90 min | **21% (18.5 min)** | 1-2 | 0.97 PASS → 종료 |

**78% budget 미사용** (cold avg). 이게 *score plateau 의 직접 원인* — sprint 추가 시 weakest dim 보강으로 점수 향상 가능했음에도 *조기 종료*.

## 2. 운영 룰

### Step 1 — 임계 통일 0.999

기존 :
- G3 = 0.97
- G4 = 0.999
- G5 = 0.99999

본 컨벤션 적용 후 :
- **default = 0.999** (G3/G4 모두)
- G5 = 0.99999 (변경 없음)

### Step 2 — Budget 사용률 ≥ 80% 강제 + (v0.9.19) axis 별 sprint ≥ 2 강제

페이즈 10 sprint loop 종료 조건 :

```python
def should_continue_sprint(state) -> bool:
    # v0.9.19 sprint-13: axis 별 min 2 sprint 강제 (intent-plan-impl-sprint-trinity bd)
    if state.intent_sprint_count < 2 OR state.plan_sprint_count < 2 OR state.impl_sprint_count < 2:
        return True  # 어느 axis 라도 < 2 면 무조건 추가
    if state.budget_used_ratio < 0.80:
        return True  # 무조건 sprint 추가, 임계 도달 무관
    if state.all_dimensions_above_threshold():
        return False  # 80% 사용 + 임계 도달 + axis 별 ≥ 2 → soft-converge
    if state.budget_used_ratio >= 0.95:
        return False  # 95% 임박 → 종료 (over-budget 회피)
    return True  # 80-95% 구간 + 임계 미달 → 계속
```

**80% 미달 또는 axis 별 sprint < 2 시 임계 도달해도 sprint 강제 추가**. 추가 sprint 의 lesson = *next weakest dim* (axis 우선 순서: intent → plan → impl).

### Step 3 — Lesson type = *content depth* (enforcement 아닌)

매 추가 sprint 의 lesson 분류 :

| Lesson type | 효과 |
|---|---|
| **content depth** (예: Conceptual narrative +sub-section) | self-estimate +0.5-1pt 가능 |
| ~~enforcement structure~~ (예: schema 추가) | self-estimate +0pt (이미 PASS) |
| **content evidence** (예: analytical bound 정량 cross-check) | self-estimate +0.5pt |
| **integrated insight** (예: scenario cross-reference 추가) | self-estimate +0.5pt |

→ 추가 sprint 가 *enforcement* 가 아닌 *content* 차원의 lesson 적용 의무. v0.9.8 sprint-regression-loop §3 의 lesson dimension 매핑 강화.

### Step 4 — Soft-converge handoff (v0.9.19: axis 별 sprint ≥ 2 추가)

budget 80% 사용 + 임계 도달 + **axis 별 sprint ≥ 2** 시 :
- handoff status = "PASS_AT_BUDGET_THRESHOLD"
- handoff frontmatter 의 `budget_saturation: <ratio>` + `sprint_axis_counts: {intent: N, plan: N, impl: N}` 명시
- 80% 미달 종료 OR 어느 axis 라도 < 2 = handoff status = "EARLY_STOP_VIOLATION" (self_lint C-BSL + C-IPI fail)

### Step 5 — 사용자 명시 ack 예외

페이즈 04 Q-D 답안 `Q-D-BUDGET-MODE` :
1. **Saturation (default — ≥80% 사용 강제)**
2. Quick-stop (임계 first-try 도달 시 종료, budget 절약)
3. Custom budget cap (사용자 명시)

답 1 default. 답 2 = 사용자 명시 ack 만 fast-stop.

## 3. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- budget % 임계 (80%) = generic 정량.
b- sprint 추가 룰 = sprint-regression-loop 의 일반 메커니즘 활용.
c- lesson type 분류 = 의미군 단위, 도메인 X.

## 4. 안티 패턴

a- **임계 first-try PASS 후 즉시 종료** — v0.9.12-14 default 패턴. 본 컨벤션 핵심 위반. self_lint C-BSL.
b- **추가 sprint 의 lesson 이 enforcement** — 점수 +0pt sprint 반복. content depth lesson 의무.
c- **80% 사용 후 임계 미달 종료** — handoff 의 `EARLY_STOP_VIOLATION` 마킹.
d- **budget 95% 초과** — over-budget 회피 (다른 cap 위반).

## 5. 효과 추정

cold session retro 적용 시 :

| 회차 | 현재 | 추가 sprint 횟수 | 추가 lesson 효과 | 추정 self-estimate |
|---|:---:|:---:|---|:---:|
| v091_cold01 (v0.9.12) | 1 sprint, 28% | +3-4 sprint | Conceptual / Results content depth | 94 → 96-97 |
| v0913_cold01 (v0.9.13) | 3 sprint, 69% | +1-2 sprint | (별 결손, 코드 0 — supremacy 차단) | n/a |
| v0914_cold01 (v0.9.14) | 1-2 sprint, 21% | +5-6 sprint | content depth full | 94 → 97-98 |

→ **94 plateau 깨기 가능** — 단 *agent 의 honest content improvement* 의지 필요.

## 6. v0.9.15 [`score-rubric-objectivity.md`](score-rubric-objectivity.md) 와의 합성

본 컨벤션이 budget *quantity* 강제, score-rubric-objectivity.md 가 *quality* 검증. 두 합성 시 :
- saturation loop 가 더 많은 sprint 진행
- strict rubric 이 매 sprint 후 self-rating 정확화
- noise 제거 + content 강화 → 객관 점수 향상

## 7. 자기 검증

본 컨벤션 자체 = single artifact. budget 컨벤션 적용 X (메타 룰). 단 본 컨벤션 작성 자체가 *budget 사용* 측면 = 본 sprint (v0.9.15) 의 budget %.

## 8. v0.9.16 sprint-10 합성 (발현 검증 메타 룰)

본 컨벤션 (budget 강제) 만으로는 *준비-vs-동작 갭* 검출 불가. v0.9.16 sprint-10 가 보완:

- **[`sprint-score-delta-tracking.md`](sprint-score-delta-tracking.md)** — 매 sprint 의 lesson 적용 후 점수 delta 측정 + lesson type 라벨링 정직성 검증. 본 컨벤션의 lesson type 4 분류 (content_depth / enforcement / content_evidence / integrated_insight) 가 *honest* 인지 사후 측정.
- **[`evidence-driven-sprint-planning.md`](evidence-driven-sprint-planning.md)** — score-rubric-objectivity 의 `evidence_missing` 가 다음 sprint 의 lesson source 로 *자동 매핑*. budget < 80% + evidence 결손 시 sprint NN+1 진입 룰 본 컨벤션 §2 Step 1 와 합성.

세 컨벤션 합성 = 진짜 self-iterating 0.999 루프 (budget *quantity* + score *quality* + 결손 *automatic flow*).
