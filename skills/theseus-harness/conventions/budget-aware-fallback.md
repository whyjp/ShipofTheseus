---
id: budget-aware-fallback
category: sprint
applies-to-phases: '[10]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'budget tight'
indexed-in: conventions/INDEX.md
---

# Budget-Aware Fallback — silent fallback 금지, 명시적 1 단계 다운그레이드

## 한 줄 요약

**budget (wall clock / token / 자원) 압박 시 컨벤션 활성도 (G4 → G3 fallback 등) 의 *silent fallback 금지* — 모든 fallback 은 산출물 frontmatter `fallback_reason` 박힘 의무.** v01_cold (v0.9.9) 가 60min budget 압박으로 parallel-cold-review G4 (4 framing) → G3 (3 framing) silent fallback 한 사례를 enforce.

## 1. 결손 진단

기존 컨벤션들이 *strict 활성* (예: G4 = 4 framing) 만 명시, *budget-pressure 시 fallback* 룰 미정 → silent fallback 발생.

v01_cold 사례 :
- v0.9.10 [`parallel-cold-review.md`](parallel-cold-review.md) §7 그레이드별 활성 = G4 → 4 framings (skeptic / domain / outsider / pessimist)
- 실제 v01_cold 결과 = 3 framings (skeptic / domain / pessimist) — F-outsider skip
- 산출물 frontmatter `framings_run: [F-skeptic, F-domain, F-pessimist]` + `grade_active: G4_with_3_framing_due_to_budget_60min`
- → fallback *evidence* 는 frontmatter 안에 박혔으나, 본 룰이 *컨벤션 강제* 가 아닌 *agent 자율 판단*

→ 다른 페이즈 / 다른 컨벤션의 fallback 은 *전혀 명시 없이* silent 발생 가능. enforcement 0.

## 2. 운영 룰

### Step 1 — fallback 카탈로그 (의미군 단위)

각 컨벤션이 *budget-pressure 시 fallback 1 단계* 명시 의무. 본 컨벤션 §3 의 표 = 씨앗.

### Step 2 — fallback 발생 시 frontmatter 의무

```yaml
fallback:
  trigger: "budget_60min" | "token_pressure" | "wall_clock_warning"
  from: G4_4_framing
  to: G3_3_framing
  reason: "budget_used 60% at phase 03 entry — 1 framing skip required"
  skip_choice: "F-outsider (least diverse w.r.t. F-skeptic per pre-scan)"
  skip_at_utc: 2026-05-04T05:46:00Z
```

`fallback` 필드 = 산출물 frontmatter 의 **별개 키** (universe / mindmap_revision 와 동일 level).

### Step 3 — self_lint C-BAF (budget-aware fallback) 검증

agent 가 G4 컨벤션 default 미준수 + frontmatter `fallback` 미박힘 → C-BAF auto-fail.

## 3. Fallback 카탈로그 (씨앗, 컨벤션별 1 단계)

| 컨벤션 | strict (G4) | fallback (1 단계) | 추가 fallback (G3 → G2) |
|---|---|---|---|
| parallel-cold-review.md | 4 framing | 3 framing | 2 framing |
| plan-tree.md | 3-4 universes | 2-3 universes | 1 universe |
| multiverse-impl-fan-out.md | code/universe-N/ all | winner only + plan-only others | single universe |
| regression.md (§2 sprint loop) | 무한 sprint until threshold | 3 sprint cap | 1 sprint cap |
| aide-tree.md (§2 multi-phase) | 06+02+05+08+11+13 multiverse | 06 only | n/a |
| interface-first-parallel-impl.md | sub-agent per module | single agent + module structure | single agent flat |

각 컨벤션이 자기 *fallback 카탈로그* 를 본 컨벤션 reference 로 추가 의무.

## 4. Fallback 트리거 정의

| Trigger | 임계 |
|---|---|
| `budget_60min` | wall clock 사용량 ≥ 50% (cold MVP) 또는 ≥ 75% (full G4) |
| `token_pressure` | context window ≥ 80% |
| `wall_clock_warning` | 현재 phase 의 예상 시간 + 누적 ≥ budget |
| `cost_pressure` | API 비용 budget cap (옵션) |

## 5. 그레이드별 활성

| Grade | fallback 활성 | self_lint C-BAF |
|---|:-:|:-:|
| G2 Simple | n/a | n/a |
| G3 Standard | optional | optional |
| **G4 Complex** | **의무** | **의무** |
| G5 Critical | 의무 + *fallback 자체 사용자 ack* (G5 의 빡빡 모드 룰) | 의무 |

## 6. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- fallback trigger = generic (budget / token / wall clock), 도메인 X.
b- fallback 카탈로그 = 컨벤션별 의미군 단위, 케이스 X.
c- frontmatter `fallback` 키 = 일반 schema, 도메인 X.

## 7. 안티 패턴

a- **silent fallback** — fallback frontmatter 박지 않고 1 단계 다운그레이드. 본 컨벤션 핵심 위반. C-BAF auto-fail.
b- **budget cap 없이 fallback** — budget 정의 없으면 fallback 자체가 임의 결정. 페이즈 04 Q-D6 답에 budget 정의 의무 (기존 룰).
c- **fallback 후 *복구 시도 0*** — budget 풀렸을 때 strict 복구 없음. fallback frontmatter 의 `recover_attempted` 키 (옵션) 로 복구 시도 기록.
d- **G5 빡빡 모드에서 silent fallback** — G5 는 사용자 ack 강제 (페이즈 04 외 인터럽트 0 룰의 예외). `fallback_user_ack_required: true` G5 강제.

## 8. v0.9.10/0.9.11 와의 직교성

기존 컨벤션들이 *strict 활성도* 만 명시 → 본 컨벤션이 *fallback 룰* 추가. 직교 axis :

| 컨벤션 | strict | fallback (본 컨벤션) |
|---|---|---|
| parallel-cold-review | 4 framing G4 | 3 / 2 framing |
| multiverse-impl-fan-out | code/universe-N/ all | winner only |
| ... | ... | ... |

## 9. 자기 검증 (메타)

본 컨벤션 자체가 *fallback* 가능 — 본 컨벤션 작성 시 budget 압박 시 §3 fallback 카탈로그 의 행 수 1-2 fallback. 본 회차 = budget 충분 → strict 적용 (6 행 모두 박음).
