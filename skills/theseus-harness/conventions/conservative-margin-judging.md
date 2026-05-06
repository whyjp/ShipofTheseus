---
id: conservative-margin-judging
category: meta
applies-to-phases: '[06,08,09,10]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'any tournament / shadow grader / sprint stop scoring'
indexed-in: conventions/INDEX.md
---

# Conservative margin judging (`conservative-margin-judging`) — 모든 judge 보수적 채점 + 0.999 마진 보존 (sprint-30, cf 보강)

## 한 줄 요약

**모든 내부 judge (plan tournament / impl tournament / shadow grader / sprint stop / phase exit gate) 는 *보수적 prior* 로 채점 — 더 개선 여지가 있다고 가정.** 0.999 임계값까지 *마진 보존* → mandatory rerun (ce) + Da Capo loop (bl) 가 *임계 도달까지 무한 회귀* (sprint-28 j 정합) 작동. 1st pass 에서 0.95+ 쉽게 도달 시 polishing 0 → 본 컨벤션이 차단.

## 결손 진단

| 결손 | 증거 |
|---|---|
| 1st pass optimistic scoring | cold session attempt-2 의 `tournament-01` u1 score 18/20 = 0.90 (1st rerun) → mandatory rerun 1 회 후 즉시 종료 |
| judge 가 "winner clear" / "no further improvement" 자신감 표현 | "Implementation passes regressed-then-fixed test. No further sprints required" — sprint-28 j 안티 패턴 정합 |
| improvement_axes_remaining frontmatter 부재 | judge 가 *남은 개선 차원* 명시 안 함 → polishing 동력 0 |

→ judge 가 *낙관적* 으로 채점하면 mandatory rerun + 무한 회귀 의도 무력화. 보수적 prior 강제로 polishing 동력 보존.

## 룰 — rerun-별 score cap (0.999 마진 보존)

```
rerun = 0           : cap = 0.90    (1st pass — 항상 개선 여지 가정)
rerun = 1           : cap = 0.95    (lesson 1 적용 후)
rerun = 2           : cap = 0.99    (lesson 2 적용 후)
rerun >= 3 AND budget_used >= 0.80 : 0.999 허용 (최종 polishing 마진 도달 후만)

# 0.99999 (G5) 는 rerun >= 5 + budget >= 0.95 시만 허용
```

cap 초과 점수 박힘 시 self_lint reject + judge 재채점 강제. universe 별 weighted total 적용 (per-dim sub_score 도 동일 cap 적용 권장).

## 룰 — improvement_axes_remaining frontmatter 의무

각 tournament-NN.md / shadow-grade-NN.json frontmatter :

```yaml
improvement_axes_remaining: <int>           # 0 = fully converged (rerun >= 3 시만 허용)
                                            # >= 1 = 더 개선 가능 (rerun < 3 시 의무)
improvement_axes_detail:                    # 각 axis 의 weakness + lesson candidate
  - dim: <차원명>
    current_score: <0.0-1.0>
    weakness: "<1 줄 weakness>"
    lesson_candidate: "<적용 가능한 lesson>"
```

rerun < 3 시 `improvement_axes_remaining: 0` 박으면 self_lint C-CMJ-AXES fail (반드시 ≥ 1 개선 차원 명시).

## 룰 — judge 자신감 sentinel

다음 confident first-pass language regex detect 시 reject (sentinel C 정합 — bp 정합):

- "winner clear"
- "no further improvement"
- "no further sprints required"
- "clearly best"
- "obvious winner"
- "definitive"
- "first execution passed" / "passed on first execution"

이 표현이 rerun=0 산출물에 박혀 있으면 → judge 가 보수적 prior 위반. 자동 회귀 + judge 재채점.

## 적용 layer

| Layer | 적용 산출물 | cap 강제 |
|---|---|---|
| **plan tournament** (phase 06) | `plan/tournament-NN.md` | winner_score / sub_scores |
| **impl tournament** (phase 08) | `impl/tournament-impl-NN.md` | 동일 |
| **shadow grader** (zero-context, phase 06/08) | `*/shadow-grade-NN.json` | predicted_score |
| **sprint stop judge** (phase 10) | `sprints/NN/report.json` | sprint score |
| **phase exit gate** (phase 09) | `quality/09-quality-gate.md` | category scores |

본 cap 은 모든 judge 에 *동일 적용*. agent 가 phase 별로 다르게 적용 금지.

## self_lint C-CMJ

컨벤션 파일 존재 + 본문 keyword (rerun-별 score cap / improvement_axes_remaining / judge 자신감 sentinel / 보수적 prior / 0.999 마진).

## 안티 패턴

a- **1st pass score 0.95+** → cap 0.90 위반. judge 재채점 강제.
b- **improvement_axes_remaining: 0 (rerun=0)** → 본 룰 위반. ≥ 1 명시 의무.
c- **shadow grader 가 confident pass** ("predicted_score: 100" type) → bo zero-context 무결성 + 본 룰 cap 동시 위반. 0.95 cap 강제.
d- **sprint stop 즉시 종료** ("first-try PASS, sprint loop 종료") → an budget-saturation-loop 위반 + 본 룰 cap 위반.
e- **judge 가 weakness 0 명시** → 보수적 prior 위반. universe 별 ≥ 1 weakness 의무.

## 호환성

- [`plan-tournament-scoring-strict.md`](plan-tournament-scoring-strict.md) (cf) — 6-dim weighted scoring 위에 cap layer 추가
- [`shadow-grader-zero-context.md`](shadow-grader-zero-context.md) (bo) — zero-context + 본 룰 cap 결합
- [`score-rubric-objectivity.md`](score-rubric-objectivity.md) (ao) — strict checklist 의 *보수적 prior* version
- [`dacapo-mandatory-rerun.md`](dacapo-mandatory-rerun.md) (ce) — mandatory ≥ 1 rerun + 본 룰 cap = polishing 동력 보존
- [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) — sprint-28 j (무한 회귀) + 본 룰 cap = 0.999 도달까지 무한 polishing

## cold session 검증 (sprint-30 도입 동기)

attempt-2 v0.9.33 :
- `tournament-01` u1 = 18/20 = 0.90 (rerun=0) — cap 0.90 정합 (경계선)
- `tournament-02` u1 = 19.5 (재가중) — cap 0.95 위반 (sprint-28 g survivors rerun + 본 룰 cap 동시 위반)
- `dacapo-rerun-impl-01` 본문 "No further sprints required" — sentinel 위반
- 외부 채점 92/100 — internal judge 가 92~95 range 자가추정 시 0.999 cap 미적용 → polishing 0

→ sprint-30 cap 적용 시 universe 별 weakness 명시 + rerun ≥ 3 까지 polishing → 외부 채점 95+ 도달 가능성 ↑.
