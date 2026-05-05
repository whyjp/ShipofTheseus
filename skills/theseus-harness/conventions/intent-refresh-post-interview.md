# Intent refresh post-interview — 사용자 질의 후 의도 4-멀티버스 재구성

## 한 줄 요약

**페이즈 04 인터뷰는 "초기 의도가 안고 있던 모호함" 을 드러낸다 — 그러나 페이즈 05 비평은 *모호함이 정정된 의도* 위에서 작동해야 한다.** 본 컨벤션은 페이즈 04 종료 직후 ~ 페이즈 05 진입 *전* 에 의도를 4 universe 로 *재* 구성 + 인터뷰가 새로 드러낸 요구·비목표·제약을 별도 산출물로 박아, 비평이 *stale 의도* 가 아닌 *refreshed 의도* 위에서 동작하도록 강제.

## 1. 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| 페이즈 01 의도 = *인터뷰 이전* 추측 | `intent/01-intent.md` 가 사용자 질의 전 에이전트 framing 으로 작성됨. 이후 04 답이 그 framing 을 부정해도 본문 갱신 없음 |
| 페이즈 04 답 → 페이즈 05 비평 직진 | 비평이 *원본 stale 의도* 를 친 결과 → simplification, alternative 가 outdated context 위에서 도출 |
| 인터뷰가 새로 드러낸 *비요구·비목표·제약* 산출물 부재 | 답 본문에 묻혀 phase 06 plan 이 다시 그 제약 누락 |
| 단일 universe refresh = 또 다른 stale | 4 framing (도메인 / 제약 / 위험 / 결과) multiverse 로 재구성해야 framing-bias 분산 |

→ 페이즈 04 와 페이즈 05 사이 *공식 refresh 단계* 부재가 본 컨벤션 도입 동기.

## 2. 트리거

페이즈 04 종료 (`intent/04-{questions,answers,autonomy,stack,verification,runtime-prereq}.md` 6 산출물 + frontmatter chain 완성) 직후, 페이즈 05 critique 진입 *전*. 자동 — 사용자 ack 없이 자율 (페이즈 04 외 인터럽트 0 정합).

## 3. 산출물 (의무 5)

```
intent/
├─ 01-1-intent.md       universe-1 — domain-paradigm framing
├─ 01-2-intent.md       universe-2 — constraint-paradigm framing
├─ 01-3-intent.md       universe-3 — risk-paradigm framing
├─ 01-4-intent.md       universe-4 — outcome-paradigm framing
└─ 01-additional.md     인터뷰가 새로 드러낸 요구 / 비목표 / 제약 (single doc)
```

각 산출물 frontmatter 의무:

```yaml
---
skill_name: shipoftheseus:theseus-orchestrator
phase: "04+"                                  # phase 04 와 05 사이
phase_name: intent-refresh
universe: 1                                   # 01-1=1, 01-2=2, 01-3=3, 01-4=4
framing: domain-paradigm                      # constraint / risk / outcome
fingerprint: "P04R-uniN-..."
prev_fingerprint: "P04-decisions-..."         # 04-answers 등의 fingerprint
created_at: "..."
interview_answers_consumed: ["04-answers.md", "04-autonomy.md", "04-stack.md", "04-verification.md", "04-runtime-prereq.md"]
---
```

`01-additional.md` frontmatter 의무 추가:

```yaml
new_requirements_count: <int>            # 인터뷰가 드러낸 신규 요구
new_non_goals_count: <int>
new_constraints_count: <int>
contradicts_initial_intent: <bool>       # 초기 01-intent 와 모순 여부
contradiction_dims: [...]                # 모순 차원 (있을 시)
```

## 4. 4 framing universe 가이드

본 컨벤션의 4 universe 는 멀티버스 폭 default 와 *다름* — 본 단계는 *framing 분산* 만이 목적, full plan-tree 가 아님.

| Universe | Framing | 강조 | 약점 (비평 입력) |
|---|---|---|---|
| **01-1** | domain-paradigm | 도메인 핵심 명사 / 동사 / 엣지 — *무엇을 모델링하는가* | 제약/리스크 underweight 가능 |
| **01-2** | constraint-paradigm | NFR / 시간 / 메모리 / API 한도 — *무엇이 가능한가* | 도메인 풍성도 underweight 가능 |
| **01-3** | risk-paradigm | 실패 시나리오 / 엣지 / 예외 — *무엇이 깨질 수 있는가* | 정상 흐름 underweight 가능 |
| **01-4** | outcome-paradigm | 사용자 결정 매핑 / 측정 지표 / 의사결정 — *무엇을 답해야 하는가* | 구현 가능성 underweight 가능 |

각 universe 가 *서로 다른 framing 으로* 인터뷰 답을 흡수 — 동일 답이라도 다른 strong-point + weak-point 를 노출. 페이즈 05 비평은 4 universe 의 weak-point 합집합을 친다.

## 5. 페이즈 05 입력 갱신

기존 phase 05 input :
- `intent/01-intent.md`
- `intent/04-answers.md`

→ sprint-17 변경 :
- `intent/01-{1,2,3,4}-intent.md` (4 refreshed universes)
- `intent/01-additional.md`
- `intent/04-answers.md` (참조 보존)
- `intent/04-autonomy.md` Q-D1~Q-D9 사전 위임
- `intent/04-verification.md` 진입 게이트

원본 `intent/01-intent.md` 는 *stale source* 로 표시 — 비평 직접 입력에서 제외, 단 contradicts 추적용 원본 보존.

## 6. self_lint — C-IRPI

| Lint ID | 검증 | PASS | FAIL |
|---|---|---|---|
| **C-IRPI-COUNT** | 5 산출물 (01-1, 01-2, 01-3, 01-4, 01-additional) 모두 존재 | 5/5 | 누락 |
| **C-IRPI-FRAMING** | 각 universe frontmatter `framing` ∈ {domain, constraint, risk, outcome} 유니크 | 4 유니크 | 중복 또는 누락 |
| **C-IRPI-CHAIN** | prev_fingerprint chain (04-* → 01-N → 05-*) 정합 | 체인 완성 | 끊김 |
| **C-IRPI-CONSUMED** | `interview_answers_consumed` 가 04-* 5 파일 모두 인용 | 5/5 | 누락 |
| **C-IRPI-CONTRADICTION** | `01-additional.md` frontmatter `contradicts_initial_intent: true` 시 본문 §contradiction-detail 존재 | true 시 본문 ≥ 1 항목 | 본문 부재 |

## 7. 안티 패턴

a- **refresh skip** — phase 04 직후 phase 05 직진. 본 5 산출물 부재 → C-IRPI-COUNT fail → phase 05 진입 자동 거부.
b- **single-universe refresh** — 01-1 만 작성하고 02/03/04 생략 → framing-bias 그대로. 4 universe 의무.
c- **framing 중복** — 4 universe 가 모두 domain-paradigm 등 동일 framing → multiverse 무력화. C-IRPI-FRAMING 강제.
d- **interview 답 미흡수** — refresh 산출물에 `interview_answers_consumed` 부재 또는 04-* 일부만 인용 → refresh 가짜.
e- **01-additional 빈 본문** — `new_requirements_count: 0 + new_non_goals_count: 0 + new_constraints_count: 0` → 인터뷰가 *아무것도 새로 드러내지 못했다* 는 주장. 가능하나 frontmatter `interview_was_redundant: true` + 본문 § 사유 ≥ 1 줄 의무 (정직 박스).
f- **stale 01-intent.md 비평 직접 입력** — phase 05 critique 가 원본 stale 의도 본문을 입력으로 사용. refresh 4 universes 로 교체 의무.

## 8. 호환성

- [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) — 본 컨벤션의 4 universe = phase 04+ 범위 *축소* multiverse. phase 06 plan-tree 의 광폭 multiverse (G4=7 등) 와 별개 layer.
- [`autonomy.md`](autonomy.md) — 페이즈 04 외 인터럽트 0 정합 (refresh 진행 자동, 사용자 ack 없음).
- [`contracts.md`](contracts.md) — fingerprint chain 정합 (04 → 04+ → 05).
- [`mindmap-richness-default.md`](mindmap-richness-default.md) (ba) — 각 refresh universe 가 자체 mindmap 갱신 의무 (initial 01-intent.md 의 mindmap 그대로 복사 금지 — refresh 의미 0).

## 9. cold session 검증 (sprint-17 도입 동기)

`2026-05-05__001_mine_g4_theseus` 의 phase 04 → phase 05 직진 실측:
- phase 04 답: "G4 forced", "45 min", "no internet", "0 intervention"
- phase 04 가 새로 드러낸 *비요구* (e.g., "real-time animation 불요", "cost modelling 불요") 별도 산출물 없이 04-answers.md 본문에 묻힘
- phase 05 critique 의 simplification 표가 04 답을 *부분만* 반영 — 4 framing 분산 부재로 outcome-paradigm weak-point (decision 매핑 누락) 미발견
- → phase 06 plan 의 winner_score 0.9132 < 0.999 의 weakest_dim = `decision_coverage` 0.85 (results-decision-mapping 갭) 으로 직결

본 컨벤션 적용 시 `01-4-intent.md` (outcome-paradigm) 가 phase 04 단계에서 decision_coverage 갭을 사전 노출 → phase 05 critique 가 그 갭을 직접 침 → phase 06 plan 의 weakest_dim 사전 정정.
