---
id: intent-refresh
category: interview
applies-to-phases: '[04,05]'
applies-to-grades: '[all]'
trigger-when: 'phase 04 종료 / phase 05 종료'
indexed-in: conventions/INDEX.md
---

# Intent Refresh — phase 04 / 05 종료 후 의도 재구성 (1차 + 2차)

## 한 줄 요약

**페이즈 04 종료 (1차 refresh) + 페이즈 05 종료 (2차 refresh) 두 시점에 의도를 4 framing universe + cascade re-write 로 재구성.** 1차 = 인터뷰 답을 흡수해 stale 01-intent 를 4 framing 으로 교체 + 새로 드러난 요구·비목표·제약을 별도 산출물로 박음. 2차 = critique 인사이트를 흡수해 v2 cascade + 04/05 doc 재작성 (사용자 ack 없음 자율). 둘 다 페이즈 04 외 인터럽트 0 정합 — clarifier 가 답을 받은 직후, 또는 critique decisions 완성 직후, 다음 페이즈 진입 *전* 자동 진행.

## 1. 결손 진단 (공통)

| 결손 | 증거 / 영향 |
|---|---|
| 페이즈 01 의도 = *인터뷰 이전* 추측 | `intent/01-intent.md` 가 사용자 질의 전 에이전트 framing 으로 작성됨. 04 답이 framing 을 부정해도 본문 갱신 없음 |
| 페이즈 04 답 → 페이즈 05 비평 직진 | 비평이 *원본 stale 의도* 위에서 작동 → simplification, alternative 가 outdated context 위에서 도출 |
| 페이즈 05 critique → 페이즈 06 plan 직진 | critique 가 드러낸 갭 (예: decision_coverage) 이 plan 진입 전 흡수 안 됨 → plan winner_score 의 weakest_dim 으로 직결 |
| 단일 universe refresh = 또 다른 stale | 4 framing (도메인 / 제약 / 위험 / 결과) multiverse 로 재구성해야 framing-bias 분산 |
| 04/05 doc 가 *최초 작성* 그대로 | refresh 후 04 답변 / 05 결정 의 framing 갱신 부재 → 후속 페이즈가 stale 입력 위 동작 |
| 인터뷰가 새로 드러낸 *비요구·비목표·제약* 산출물 부재 | 답 본문에 묻혀 phase 06 plan 이 다시 그 제약 누락 |

→ 페이즈 04 ↔ 05 ↔ 06 사이 *공식 refresh 단계 2 회* 부재가 본 컨벤션 도입 동기.

## 2. 트리거 — phase 분기 (자동, 사용자 ack 없음)

본 컨벤션은 **두 시점** 에 발동 — 페이즈 04 종료 (1차) + 페이즈 05 종료 (2차). 둘 다 페이즈 04 외 인터럽트 0 정합 ([`autonomy.md`](autonomy.md)) — clarifier 가 답을 받은 직후 또는 critique decisions 완성 직후 자율 진행.

### 2.1 1차 refresh — phase 04 종료 직후 (post-interview)

페이즈 04 종료 (`intent/04-{questions,answers,autonomy,stack,verification,runtime-prereq}.md` 6 산출물 + frontmatter chain 완성) 직후, 페이즈 05 critique 진입 *전*. 자동 — 사용자 ack 없음.

### 2.2 2차 refresh — phase 05 종료 직후 (post-critique)

페이즈 05 critique 산출물 (`intent/05-critique.md` + `intent/05-decisions.md`) 완성 직후, 페이즈 06 plan 진입 *전*. **자동 — 사용자 ack 없음** (페이즈 04 외 인터럽트 0 정합).

## 3. 산출물 — phase 분기

### 3.1 1차 refresh — 5 산출물 (post-interview)

```
intent/
├─ 01-1-intent.md       universe-1 — domain-paradigm framing
├─ 01-2-intent.md       universe-2 — constraint-paradigm framing
├─ 01-3-intent.md       universe-3 — risk-paradigm framing
├─ 01-4-intent.md       universe-4 — outcome-paradigm framing
└─ 01-additional.md     인터뷰가 새로 드러낸 요구 / 비목표 / 제약 (single doc)
```

각 universe frontmatter 의무:

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

### 3.2 2차 refresh — 6 산출물 (post-critique)

```
intent/
├─ 01-1-intent.v2.md       universe-1 v2 — domain-paradigm + critique-absorbed
├─ 01-2-intent.v2.md       universe-2 v2 — constraint-paradigm + critique-absorbed
├─ 01-3-intent.v2.md       universe-3 v2 — risk-paradigm + critique-absorbed
├─ 01-4-intent.v2.md       universe-4 v2 — outcome-paradigm + critique-absorbed
├─ 04-refreshed.md         04 answers / decisions / autonomy / stack 통합 v2 (critique-absorbed cascade)
└─ 05-refreshed.md         05 critique / decisions 통합 v2 (mismatch resolved against v2 framing)
```

각 v2 universe frontmatter:

```yaml
---
phase: "05+"                                  # phase 05 와 06 사이
phase_name: intent-refresh
universe: 1                                   # 01-{1..4}-intent.v2.md 만
framing: domain-paradigm                      # 01-{1..4} 만
fingerprint: "P05R-uniN-..."
prev_fingerprint: "P05-decisions-..."
created_at: "..."
critique_findings_consumed: ["05-critique.md", "05-decisions.md"]
intent_v1_supersedes: ["01-1-intent.md", ..., "01-additional.md"]
contradicts_v1: <bool>                        # v1 의도와 모순 여부
contradiction_dims: [...]                     # 모순 차원
---
```

## 4. 4 framing universe 가이드 (공통)

본 컨벤션의 4 universe 는 멀티버스 폭 default 와 *다름* — 본 단계는 *framing 분산* 만이 목적, full plan-tree 가 아님.

| Universe | Framing | 강조 | 약점 (비평/cascade 입력) |
|---|---|---|---|
| **01-1** | domain-paradigm | 도메인 핵심 명사 / 동사 / 엣지 — *무엇을 모델링하는가* | 제약/리스크 underweight 가능 |
| **01-2** | constraint-paradigm | NFR / 시간 / 메모리 / API 한도 — *무엇이 가능한가* | 도메인 풍성도 underweight 가능 |
| **01-3** | risk-paradigm | 실패 시나리오 / 엣지 / 예외 — *무엇이 깨질 수 있는가* | 정상 흐름 underweight 가능 |
| **01-4** | outcome-paradigm | 사용자 결정 매핑 / 측정 지표 / 의사결정 — *무엇을 답해야 하는가* | 구현 가능성 underweight 가능 |

각 universe 가 *서로 다른 framing 으로* 입력을 흡수 — 동일 입력이라도 다른 strong-point + weak-point 노출. 페이즈 05 비평은 1차 universes 의 weak-point 합집합을 친다. 2차 cascade 는 critique 인사이트를 4 framing 모두에 흡수.

## 5. 페이즈 입력 갱신

### 5.1 페이즈 05 critique 입력 (1차 refresh 후)

기존 phase 05 input :
- `intent/01-intent.md`
- `intent/04-answers.md`

→ 1차 refresh 적용 후 :
- `intent/01-{1,2,3,4}-intent.md` (4 refreshed universes)
- `intent/01-additional.md`
- `intent/04-answers.md` (참조 보존)
- `intent/04-autonomy.md` Q-D1~Q-D9 사전 위임
- `intent/04-verification.md` 진입 게이트

원본 `intent/01-intent.md` 는 *stale source* 로 표시 — 비평 직접 입력에서 제외, 단 contradicts 추적용 원본 보존.

### 5.2 페이즈 06 plan 진입 게이트 (2차 refresh 후)

```python
for u in [1, 2, 3, 4]:
    if not (intent_dir / f"01-{u}-intent.v2.md").exists():
        raise SkillEntryError(f"intent/01-{u}-intent.v2.md 부재 — phase 05+ refresh 미완료. intent-refresh.md 의무.")
if not (intent_dir / "04-refreshed.md").exists():
    raise SkillEntryError("intent/04-refreshed.md 부재 — phase 05+ cascade re-write 미완료.")
if not (intent_dir / "05-refreshed.md").exists():
    raise SkillEntryError("intent/05-refreshed.md 부재 — phase 05+ cascade re-write 미완료.")
```

phase 06 plan 의 `prev_fingerprint` 는 `P05R-*` (v2 universe) 인용 의무 (v1 `P05-decisions-*` 직접 인용 금지).

## 6. self_lint

### 6.1 C-IRPI (1차 refresh)

| Lint ID | 검증 | PASS | FAIL |
|---|---|---|---|
| **C-IRPI-COUNT** | 5 산출물 (01-1, 01-2, 01-3, 01-4, 01-additional) 모두 존재 | 5/5 | 누락 |
| **C-IRPI-FRAMING** | 각 universe frontmatter `framing` ∈ {domain, constraint, risk, outcome} 유니크 | 4 유니크 | 중복 또는 누락 |
| **C-IRPI-CHAIN** | prev_fingerprint chain (04-* → 01-N → 05-*) 정합 | 체인 완성 | 끊김 |
| **C-IRPI-CONSUMED** | `interview_answers_consumed` 가 04-* 5 파일 모두 인용 | 5/5 | 누락 |
| **C-IRPI-CONTRADICTION** | `01-additional.md` frontmatter `contradicts_initial_intent: true` 시 본문 §contradiction-detail 존재 | true 시 본문 ≥ 1 항목 | 본문 부재 |

### 6.2 C-IRPC (2차 refresh)

컨벤션 파일 존재 + 페이즈 05 본문 "intent-refresh" 인용 + 6 산출물 명시 + 페이즈 06 plan 진입 게이트 갱신 명시.

자동 reject 패턴:
- 6 산출물 (01-{1..4}-intent.v2 + 04-refreshed + 05-refreshed) 중 ≥ 1 누락
- v2 본문이 v1 본문 그대로 복붙 (diff < 50 byte)
- `critique_findings_consumed` frontmatter 부재 또는 05-* 미인용
- `intent_v1_supersedes` 부재 → cascade 추적 불가
- phase 06 plan 의 `prev_fingerprint` 가 `P05-decisions-*` 직접 인용 (`P05R-*` 인용 의무)

## 7. 안티 패턴

### 7.1 1차 refresh 안티 패턴

a- **refresh skip** — phase 04 직후 phase 05 직진. 5 산출물 부재 → C-IRPI-COUNT fail → phase 05 진입 자동 거부.
b- **single-universe refresh** — 01-1 만 작성하고 02/03/04 생략 → framing-bias 그대로. 4 universe 의무.
c- **framing 중복** — 4 universe 가 모두 domain-paradigm 등 동일 framing → multiverse 무력화. C-IRPI-FRAMING 강제.
d- **interview 답 미흡수** — refresh 산출물에 `interview_answers_consumed` 부재 또는 04-* 일부만 인용 → refresh 가짜.
e- **01-additional 빈 본문** — `new_requirements_count: 0 + new_non_goals_count: 0 + new_constraints_count: 0` → 인터뷰가 *아무것도 새로 드러내지 못했다* 는 주장. 가능하나 frontmatter `interview_was_redundant: true` + 본문 § 사유 ≥ 1 줄 의무 (정직 박스).
f- **stale 01-intent.md 비평 직접 입력** — phase 05 critique 가 원본 stale 의도 본문을 입력으로 사용. refresh 4 universes 로 교체 의무.

### 7.2 2차 refresh 안티 패턴

g- 1차 refresh 만으로 충분하다 가정 — sprint-19 차단. critique 가 드러낸 갭은 *post-05 cascade* 로만 흡수 가능.
h- v2 산출물 본문이 v1 본문 그대로 복붙 — diff threshold (≥ 50 byte 또는 ≥ 5% 변경) 강제.
i- `intent_v1_supersedes` 부재 → cascade 추적 불가.
j- 사용자 ack 시도 — 페이즈 04 외 인터럽트 0 정합. 자율로만 진행.

## 8. 호환성

- [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) — 본 컨벤션의 4 universe = phase 04+ / 05+ 범위 *축소* multiverse. phase 06 plan-tree 의 광폭 multiverse (G4=7 등) 와 별개 layer.
- [`autonomy.md`](autonomy.md) — 페이즈 04 외 인터럽트 0 정합 (1차/2차 refresh 모두 진행 자동, 사용자 ack 없음).
- [`contracts.md`](contracts.md) — fingerprint chain (04 → 04+ → 05 → 05+ → 06) 정합.
- [`mindmap-richness-default.md`](mindmap-richness-default.md) (ba) — 각 refresh universe (1차/2차 모두) 가 자체 mindmap 갱신 의무 (initial 01-intent.md 의 mindmap 그대로 복사 금지 — refresh 의미 0).
- [`cross-phase-shared-context.md`](cross-phase-shared-context.md) (cj) — 04-refreshed.md / 05-refreshed.md 가 phase 06 plan 의 입력 source.

## 9. cold session 검증

### 9.1 1차 refresh 검증 (sprint-17 도입 동기)

`2026-05-05__001_mine_g4_theseus` 의 phase 04 → phase 05 직진 실측:
- phase 04 답: "G4 forced", "45 min", "no internet", "0 intervention"
- phase 04 가 새로 드러낸 *비요구* (e.g., "real-time animation 불요", "cost modelling 불요") 별도 산출물 없이 04-answers.md 본문에 묻힘
- phase 05 critique 의 simplification 표가 04 답을 *부분만* 반영 — 4 framing 분산 부재로 outcome-paradigm weak-point (decision 매핑 누락) 미발견
- → phase 06 plan 의 winner_score 0.9132 < 0.999 의 weakest_dim = `decision_coverage` 0.85 (results-decision-mapping 갭) 으로 직결

본 컨벤션 적용 시 `01-4-intent.md` (outcome-paradigm) 가 phase 04 단계에서 decision_coverage 갭을 사전 노출 → phase 05 critique 가 그 갭을 직접 침 → phase 06 plan 의 weakest_dim 사전 정정.

### 9.2 2차 refresh 검증 (sprint-19 도입 동기)

cold 003 의 `intent/05-decisions.md` (2393 byte) 직후 `plan/tournament.md` 진입:
- 04-05 사이 1차 refresh 완료
- 05 → 06 사이 2차 refresh 부재 (sprint-19 본 룰 부재로 자연 skip)
- critique 가 드러낸 "ramp_upgrade vs baseline 1% 미만" 같은 outcome-paradigm 인사이트 → 06 plan 의 decision_coverage 차원 sub_score 0.85 (gap)
→ sprint-19 게이트 적용 시 6 산출물 강제 → critique 인사이트 흡수 → plan decision_coverage 차원 사전 보강.

## 10. 통합 history (sprint-37 PR-AA)

본 컨벤션은 sprint-37 PR-AA (다이어트) 에서 **`intent-refresh-post-interview`** (sprint-17 by, 1차) + **`intent-refresh-post-critique`** (sprint-19 ci, 2차) 두 컨벤션을 phase param 분기 단일 컨벤션으로 통합. 책임 = "의도 refresh" 단일, 트리거 = phase 04 종료 / 05 종료 분기. 매핑은 [`MIGRATION.md`](MIGRATION.md) 단일 source.
