---
id: plan-tournament-scoring-strict
category: tournament
applies-to-phases: '[06]'
applies-to-grades: '[all]'
trigger-when: 'tournament 산출'
indexed-in: conventions/INDEX.md
---

# Plan tournament scoring strict (`plan-tournament-scoring-strict`) — 6-dim weighted 의무 (sprint-19, cf, HARD-RULE 9.hh)

## 한 줄 요약

**Phase 06 plan tournament.md 의 winner_sub_scores 는 [`grader-in-sprint.md`](grader-in-sprint.md) (be) 의 6-dim weighted 스키마 의무 — 1-5 coarse cold-read scoring 자동 reject.** 점수 체계가 coarse 일수록 dacapo lesson polishing 이 무력화 (1-5 × 4 dim = max 20, 임계 0.999 와 산술 매핑 불가). cold session 003 의 1-5 × 4 cold-read 19/20 promote 우회 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| 1-5 × N dim coarse scoring | cold 003 의 4 universe 점수 19 / 16 / 16 / 15 — 1pt 단위 너무 굵어 dacapo Step D AND threshold 정상 작동 안 함 |
| max 20 vs 0.999 임계 산술 매핑 부재 | 19/20 = 0.95 ≠ G4 임계 0.999. Step D `tournament_pass: 0.95 >= 0.999` ❌ 무시한 채 promote |
| be (grader-in-sprint) 6-dim weighted 우회 | bf (contested-decision-multiverse) 의 6 차원 (decision_coverage 0.20 가중 포함) 가 강제 안 됨 |

## 의무 — winner_sub_scores 6 차원 weighted

```yaml
winner_sub_scores:
  feasibility_in_45min: <0.0~1.0>      # weight 0.20
  invariant_robustness: <0.0~1.0>      # weight 0.20
  decision_coverage: <0.0~1.0>         # weight 0.20  (bf contested-decision-multiverse)
  modular_clarity: <0.0~1.0>           # weight 0.15
  determinism: <0.0~1.0>               # weight 0.15
  measurement_directness: <0.0~1.0>    # weight 0.10
winner_score: <weighted total, 0.0~1.0>
```

산식:
`winner_score = 0.20·feasibility + 0.20·invariant + 0.20·decision_coverage + 0.15·modular + 0.15·determinism + 0.10·measurement`

### Step D 매핑 (sprint-19, 설계 B2 §2.3 재정정)

`winner_score`/`shadow_grade-NN.json.predicted_score` 는 6-dim weighted 측정값으로 계속 emit 된다 — 단 절대 임계(구 G4=0.999/G5=0.99999) 는 게이트가 아니다. 정지 판정 권위는 manifest `stop_policy`(gate AND no_regression AND (plateau OR budget≥95%)) 이며, 본 표는 값의 *참고 target* 으로만 남는다 (G2=0.85/G3=0.97, G4/G5 의 도달 불가 임계는 폐지).

## 의무 — universe table 6-dim

`tournament-NN.md` 본문에 다음 표 의무 (universe 별 6 차원 sub-score):

| Universe | feasibility | invariant | decision_coverage | modular | determinism | measurement | weighted |
| --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | 0.95 | 0.92 | 0.85 | 0.93 | 0.95 | 0.88 | **0.913** |
| U2 | ... | ... | ... | ... | ... | ... | ... |

## 자동 reject 패턴

다음 패턴 detect 시 fail (특히 **1-5 cold-read** coarse scoring 패턴 자동 reject):
1. universe sub-score 정수 1-5 사용 (0.0~1.0 연속값 의무) — `1-5 cold-read` 임시 채점 자동 reject
2. `winner_score` 가 단순 합산 (Σ sub-scores) 가중치 미적용
3. 6 dim 중 ≥ 1 누락
4. `decision_coverage` 차원 부재 (bf contested-decision-multiverse 정합)

## self_lint C-PTSS

컨벤션 파일 존재 + 페이즈 06 본문 "plan-tournament-scoring-strict" + "6-dim weighted" + "decision_coverage" + "1-5 coarse cold-read" reject 명시.

## 안티 패턴

a- "1-5 × N dim cold-read 임시 채점" — sprint-19 차단. be 6-dim weighted 만 인정.
b- weighted total 박지만 sub_scores 부재 — agent 가 숫자 fabricate 가능. 6 sub_scores frontmatter 의무.
c- decision_coverage 누락 — bf contested-decision-multiverse 0.20 가중치 무시.

## cold session 003 검증

`plan/tournament.md`:
- "Cold-read scoring (zero-context judge persona, 1-5 each)" — 1-5 × 4 dim
- U1 19/20 = 0.95 < 0.999 → `tournament_pass: false` 의무인데 promote
- decision_coverage 차원 부재
- → sprint-19 게이트 적용 시 1-5 coarse 패턴 detect → reject + 6-dim weighted 재채점 강제. 재채점 결과가 0.999 미달 시 mandatory rerun (ce) 와 결합.

## 호환성

- [`grader-in-sprint.md`](grader-in-sprint.md) (be) — 6-dim weighted 의무의 source.
- [`contested-decision-multiverse.md`](contested-decision-multiverse.md) (bf) — decision_coverage 0.20 가중.
- [`dacapo-mandatory-rerun.md`](dacapo-mandatory-rerun.md) (ce) — 본 룰 적용 후 winner_score 가 임계 도달해도 sprint-19 mandatory ≥ 1 rerun.
