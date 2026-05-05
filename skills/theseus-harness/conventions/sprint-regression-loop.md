---
id: sprint-regression-loop
category: sprint
applies-to-phases: '[10]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Sprint Regression Loop — *self-polishing* 임계 도달까지 반복

## 한 줄 요약

**페이즈 10 sprint = *임계 도달까지 무한 반복*** — 단일 통과로 종료 금지. 매 sprint 가 *전 sprint 의 dimension 별 gap* 을 입력으로 *가장 약한 dimension 의 lesson* 을 적용 + 재실행 + 재측정. 임계 도달 또는 budget 소진 시까지. 본 컨벤션이 본 하네스의 *self-polishing 의지* 의 운영 형태.

## 1. 결손 진단 — 본 컨벤션 도입 전

페이즈 10 ([`../phases/10-test-loop.md`](../phases/10-test-loop.md)) 의 SKILL.md 인덱스가 "무한 스프린트 (임계 0.999)" 로 명시되어 있으나, *실 운영에서 단일 sprint 통과 후 정상 종료* 케이스 발생. v0.9.7 cold 회차 (`synthetic_mine_throughput_cold`) 에서 sprint-01 의 자체 추정 92-95 / 100 이 임계 (0.97 G3 / 0.999 G4) 미달임에도 *재실행 0 회* — 본 스킬의 self-polishing 의도 누락.

## 2. 운영 룰

### Step 1 — score-per-dimension (sprint 출력)

매 sprint 종료 시 산출물 `sprints/NN/report.json` 에 *bench rubric (또는 일반 success criteria) 차원별 점수* 의무 :

```yaml
self_estimate:
  per_dimension:
    Conceptual_modelling: {score: 18, max: 20, gap: 2}
    Sim_correctness: {score: 19, max: 20, gap: 1}
    ...
  total: 94
  threshold_target: 97   # G4 = 0.97 × 100
  weakest_dimension: "Conceptual_modelling"
  weakest_gap: 2
```

### Step 2 — gap-from-threshold 검사

- 모든 dimension `score / max ≥ threshold` → **CONVERGED** (sprint 종료, phase 14 진입).
- 어느 한 dimension `score / max < threshold` → **REGRESS** (sprint NN+1 진입).

threshold 는 grade 별 (G3=0.97 / G4=0.999 / G5=0.99999) — [`grades.md`](grades.md) 정합.

### Step 3 — weakest-dimension lesson 적용

REGRESS 시 :

a- weakest_dimension 의 *원인 lesson* 식별 ([`lessons.md`](lessons.md) 의 차원 5 매핑 참조).
b- 해당 lesson 의 *수정 범위* 결정 :
   - 단순 narrative 보강 → outputs/ 재생성 (페이즈 08-ε log 만 재진입)
   - 모듈 결손 → 페이즈 06 plan 부분 재진입
   - 기획-구현 갭 → 페이즈 06 부터 통째 re-architect (HARD-RULE e-1)
c- 수정 적용 후 sprint NN+1 재실행 + Step 1 재측정.

### Step 4 — budget cap

- 정해진 budget (페이즈 04 Q-D6 답) 내에서 *무한 반복*.
- budget 초과 시 *최선 sprint* 로 phase 14 진입 + handoff 에 *gap 명시*.

본 룰이 단순히 "임계 미달 시 정지" 가 아닌 *budget 내 최대 폴리싱* 보장.

## 3. Lesson dimension 매핑 (의미군 단위, 케이스 종속 0)

매 dimension 의 weakest 시 *어떤 lesson 의 수정* 을 할 것인가 — 케이스가 아닌 의미군 별 :

| Dimension 약점 | Lesson 의미군 | 적용 페이즈 |
|---|---|---|
| Conceptual / clarity | narrative 분량/깊이 + assumption 분리 | 페이즈 08-ε log (outputs/ regen) |
| Sim correctness / accuracy | 모델 결손 — analytical bound mismatch / sanity 차원 추가 | 페이즈 06 plan 부분 재진입 |
| Experimental / reproducibility | seed 분리 / determinism / 더 많은 reps | 페이즈 06/08 |
| Results / interpretability | 운영 권고 깊이 (ROI, sensitivity matrix) | 페이즈 08-ε |
| Code quality / maintainability | DIP 위반 / cyclomatic | 페이즈 06 re-architect (HARD-RULE e-1) |
| Traceability | event log 컬럼 추가 / 결정 추적표 | 페이즈 08 |
| Completeness | optional scope 활용 / requirement coverage | 페이즈 06 plan 추가 |
| Efficiency | wall clock / LOC | 페이즈 08 refactor |

본 표는 *씨앗* — 새 dimension 의 의미군 매핑은 추가 가능, 케이스별 추가 X.

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- trigger = *sprint 종료 시 dimension gap* — 도메인 무관. simulation-bench 든 결제 시스템이든 같은 룰.
b- lesson 매핑 = 의미군 단위, 케이스별 X.
c- iteration 종료 조건 = 임계 또는 budget — 외부 답안 visit 0.

## 5. v0.9.6/v0.9.7 와의 직교성

| 컨벤션 | trigger | output |
|---|---|---|
| v0.9.6 nfr-derivation | prompt 형용사 | derived gate 자동 생성 |
| v0.9.7 premortem-friction | 콜드리뷰 페이즈 진입 | derived improvements 도출 |
| **v0.9.8 sprint-regression-loop** | **sprint 종료 시 dimension gap** | **다음 sprint 의 lesson 적용** |

세 컨벤션이 다른 axis — 함께 적용 가능. 본 cold 회차 sprint-02 가 본 컨벤션 + v0.9.7 premortem 함께 적용.

## 6. 안티 패턴

a- **Single-sprint 종료** — sprint-01 통과로 phase 14 진입 = 본 컨벤션 위반. 임계 도달 명시 의무.
b- **Theatrical regression** — 매 sprint 가 *형식적 score increment* 만 (예: assumption 표 row 1개 추가 = +0pt) → C-SR self_lint fail 후보. lesson 의 *실 effect* 측정 의무.
c- **Lesson dimension mismatch** — weakest 가 Conceptual 인데 Code quality lesson 적용. 위 §3 표 참조 강제.
d- **Budget 초과 후 gap 은닉** — handoff 에 *gap 명시* 의무. 임계 미달도 *최선 결과 보존* 으로 종료.

## 7. 자기 검증 (메타)

본 컨벤션 자체에 sprint loop 적용 :
- sprint-01 = 본 v0.9.8 도입 후 첫 cold 회차 sprint
- sprint-02 = sprint-01 의 weakest dim (예: Conceptual narrative) 보강 후 재측정
- ...
- 임계 도달 시 phase 14 진입.

본 회차 결과 (sprints/NN/report.json) 가 본 컨벤션 자체의 evidence.
