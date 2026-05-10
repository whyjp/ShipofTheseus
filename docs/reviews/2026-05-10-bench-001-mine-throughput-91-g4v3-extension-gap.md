# 2026-05-10 — Bench 001 g4-v3 91/100 — Extension Gap 진단 + sprint-50 design rationale

> **회차:** `2026-05-10__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4-v3`
> **공식 점수:** 91 / 100, SHIP (Opus zero-context reviewer)
> **자동 평가:** 53 / 53 = 1.000
> **검증 일시:** 2026-05-10 (sprint-50 진단 시점)
> **위치:** `D:\github\simulation-bench\submissions\2026-05-10__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4-v3`

## 0. TL;DR — 3 결론

1. **91 plateau 의 본질 = *프롬프트 너머의 사고 부재***. 페이즈 01–05 의 모든 산출물이 *프롬프트 충실 이행* 패턴. *확장 사고 (Extension Thinking)* 단계가 부재.
2. **6 차원 손실 중 *최소 3 차원* (Experimental / Results / Conceptual 일부) 은 코드 디테일이 아니라 *"프롬프트가 묻지 않은 것을 제안 + 실행"* 으로만 채워지는 영역**. 즉 본 갭은 enforcement 룰 하나로 닫히지 않음 — *전 페이즈 사고 패턴 변경* 필요.
3. **sprint-50 (v0.9.50) 진행 결정** — 16 phases (1.5 신설) + 9 신규 HARD-RULE + 10 신규 CLI. Pragmatic Programmer + A Philosophy of Software Design 인사이트 enforcement 화.

## 1. 점수 분포 — 91 / 100

| Category | Max | Score | 손실 | 손실 성격 |
|---|---:|---:|---:|---|
| Conceptual modelling | 20 | **18** | -2 | 모델이 프롬프트 그대로 / 이론 framing 부재 |
| Data + topology | 15 | **14** | -1 | topology 단순 따라하기 |
| Simulation correctness | 20 | **18** | -2 | `node_overrides` dead-path |
| **Experimental design** | 15 | **13** | **-2** | **시나리오 6 개만 / sensitivity sweep · DoE 부재** ← extension 영역 |
| **Results + interpretation** | 15 | **14** | **-1** | **해석이 표층 머무름** ← extension 영역 |
| Code quality | 10 | **9** | -1 | `_choose_loader` realtime queue 무시 |
| Traceability | 5 | **5** | 0 | — |

자동 53/53 (1.000) vs 외부 91/100 의 갭은 *코드 디테일* (#3 Simulation / #6 Code quality) 이 일부, *extension 영역* (#4 Experimental / #5 Results / #1 Conceptual 일부) 이 더 큰 부분.

## 2. 산출물 직접 증거 — *extension supplement 의 빈약함*

### 2-1. `intent/01-additional.md` (refresh-1 supplement)

```
단 17 줄.
설계 결정 1 개 ("ramp_closed bypass 가 ~3500 m → throughput 70-80% baseline 예상").
+ 캐싱 권고 1 ("shortest-time paths 캐시 by (origin, dest, loaded_state)").
```

이건 *extension 이 아니라 supplement*. 페이즈 04 답안 직접 follow-up 일 뿐, *프롬프트가 묻지 않은 영역* 0.

### 2-2. `intent/05-decisions.md` DEC-10 (7th scenario)

```
DEC-10: 7th proposed scenario = `loader_balance` (LOAD_N service rate matched to LOAD_S)
```

7th 시나리오 1 개 추가 — Q-OPT-3 답안 follow-up. 시나리오 sweep / sensitivity DoE / parameter range 탐색 0.

### 2-3. 외부 reviewer 가 직접 짚은 *extension 부재*:

> *"#2: node_overrides 가 로드되지만 experiment.py:69-79 에서 무시 — crusher_slowdown 시나리오는 dump_point_overrides 에 같은 값을 중복 선언해서 우연히 동작 (히든 dead-path)"*
>
> *"#3: _choose_loader 가 Resource.count 만 보고 실시간 큐 길이는 무시"*

코드 디테일이지만, *둘 다 sensitivity / observability 차원의 사고가 사전에 있었으면 catch* 가능. 즉 *extension 페이즈의 사전 발굴* 이 누락되어 *코드 작성 후 reviewer 가 발견*.

## 3. 본 하네스의 구조적 진단

### 3-1. 91 plateau — 95 첫 돌파 후 회귀

| 회차 | 일자 | 점수 | 비고 |
|---|---|---:|---|
| v0.9.44 | 2026-05-09 | **95** | 94 plateau 첫 돌파 (역대 최고) |
| v0.9.45 (1차) | 2026-05-10 | 90 | 회귀 |
| v0.9.45 (2차) | 2026-05-10 | 87 | universe 감소 + 자율 종료 |
| v0.9.47 g4-v2 | 2026-05-10 | 91 | sandbox 검증 |
| **v0.9.49 g4-v3** | **2026-05-10** | **91** | **본 review 대상** |

95 첫 돌파 *이후* 93~91 plateau. sprint-37~49 의 enforcement 누적은 *기존 차원* 에 한해 효과 — *프롬프트 너머* 차원은 부재.

### 3-2. 사용자 직접 진단 (2026-05-10)

> *"의도를 이해하고 프롬프트에 적혀있는 이상의 처리를 해야 한다. 이해 만으로 멈춰서 그런데 성찰-상상력을 덧대서 추가하면 좋은 작업이나 더 설계를 확장하거나 프롬프트보다 더 확장된 제안을 intent 이후 단계에 추가하는 건 어떨까. 지금 남은 점수들 그 이상을 하려면 프롬프트를 지키는 것 이상으로 프롬프트를 실행하고 숨겨진 의도를 파악하는 것이다."*
>
> *"plan/impl 에서도 확장 된 사고를 지시해야 한다. 실용주의 프로그래밍 이펙티브 소픝크웨어 설계의 인사이트들을 실제 반영해야 한다. 요구사항이해와 설계 구현 유지보수 -테스트 들에 대한 바이블이다."*

본 review 가 사용자 진단을 *직접 trace* — 본 sprint 의 모든 PR 본문은 위 인용을 출처로.

## 4. sprint-50 design rationale

### 4-1. 페이즈 1.5 신설 — *intent 단계 의 확장 분리*

페이즈 04 (Q&A) 직후, 페이즈 05 (Critique) 직전 *별도 단계*. 페이즈 05 가 본 페이즈 1.5 의 hidden-intent 까지 비판. 페이즈 06 plan 이 *채택* extension 을 직접 다룸.

3 산출물:
- `01-hidden-intent.md` — ≥5 항목, 10 카테고리 catalog 중 distinct ≥3
- `01-extension-scope.md` — must/should/could 분류, should ≥1 채택
- `01-extension-trace.md` — 채택 항목 후속 페이즈 explicit pointer

### 4-2. 페이즈 06 Design-Twice — *plan 단계 의 사고 확장*

기존 multiverse 는 *코드 분기* 만. sprint-50 부터 universe 별 *설계 철학* distinct 의무 — modular / oop / functional / data-driven / event-driven / actor / dsl-first 7 카탈로그.

### 4-3. 페이즈 08 Deep-Module + DRY — *impl 단계 의 사고 확장*

Ousterhout Ch.4 + Pragmatic Tip 11. 코드 작성 시 *얕은 모듈* / *반복 패턴* 자동 검출 → implementer 재진입 강제.

### 4-4. 페이즈 09 Define-Errors-Out + Comments-Why — *quality 단계 의 사고 확장*

Ousterhout Ch.10 + Ch.13. 예외 정의/처리 catalog + comment 의도 검증.

### 4-5. 페이즈 10/14 Refactor-not-Rewrite + Knowledge Portfolio — *유지보수 + 회고 단계*

Pragmatic Ch.6 + Ch.1. sprint loop 의 변경 비율 + handoff 의 *통찰* 의무.

## 5. 본 review 의 자기 정합

본 review 는 sprint-50 의 *진단 source*. sprint-50 마감 후 *g4-v4 cold session 결과* 가 본 review 의 진단 정확성을 검증한다 (dogfood 한계 — `feedback_self_eating_dogfood.md` 정합).

본 review 는 *점수 회복 targeting* 으로 작성되지 않았다 (`feedback_score_targeting_taboo.md` 정합) — 91 plateau 의 *구조적* 원인 진단이 본 review 의 단일 책임.

## 6. 후속 추적 (sprint-51 의제 후보)

- g4-v4 cold session 결과 (외부 평가)
- 본 sprint 의 어느 PR 이 실제로 외부 평가 차원을 끌어올렸는지 attribution 분석
- 끌어올리지 못한 차원 → 다음 sprint enforcement 보강 또는 pollutant 제거
