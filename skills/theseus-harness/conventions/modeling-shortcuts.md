---
id: modeling-shortcuts
category: planning
applies-to-phases: '[02,03,05,06,09]'
applies-to-grades: '[all]'
trigger-when: 'heuristic / approximation / coarse model 사용 시'
indexed-in: conventions/INDEX.md
---

# Modeling Shortcuts — 휴리스틱/근사 분류 강제 (sprint-40 PR-F 신규)

## 한 줄 요약

**도메인 모델링의 모든 *수학적 단축* (휴리스틱 / 근사 / coarse model) 을 4-tier 로 분류 + plan/impl 본문에서 직접 참조 의무.** simulation-bench 001 v0.9.44 g4-v2 회차의 -2pt Sim correctness (dispatcher queue=`len()+busy` 휴리스틱 + travel-noise per-edge 1 draw) 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| Phase 02 cold-reread / Phase 07 plan review 가 *동작 여부* 만 검사 | "이 산식이 휴리스틱인가, 측정값인가, defensible coarse 인가, gold-standard 인가" 분류 0 |
| 메모리 [`feedback_premortem_not_pause.md`] 의 *forward simulation + derived_improvements* 가 *프로세스 깨짐* axis 만 커버 | 도메인 모델링의 *수학적 깊이* axis 미커버 |
| Tournament 6-dim 중 *heuristic-vs-optimal* 차원 부재 | sim correctness 가 binary ("공식 맞나?") 로만 채점 |
| Plan implementation guidance 에 *anti-pattern explicit ban* 미의무 | dispatcher / queue / wait / noise / sample 결정에 대한 alternative 미명시 |

## 4-tier 분류

| Tier | 정의 | 점수 영향 (도메인 expert) |
|---|---|---|
| **gold-standard** | 학계/업계 합의된 optimal solution. 측정값 또는 analytically optimal. | 0 cap |
| **defensible-coarse** | 알려진 fidelity 손실, 그러나 데이터/시간 제약 내 reasonable. alternative + 기각 사유 명시. | -0.5pt cap (Sim correctness 차원) |
| **heuristic** | 빠른 근사, fidelity 검증 0. alternative + expected-loss-vs-optimal 추정 1줄 의무. | -1pt cap |
| **placeholder** | 단순 채움, 실 작동성 0. plan 단계에서만 허용, impl 단계에서 0. | phase 09 진입 거부 |

## 산출물 — `intent/modeling_shortcuts.json` (phase 02/03 산출 의무)

```json
{
  "schema_version": "0.9.45",
  "domain": "DES",
  "shortcuts": [
    {
      "id": "MS-001",
      "location": "src/mine_sim/dispatcher.py:choose_loader",
      "current_form": "queue = len(res.queue) + (1 if res.count > 0 else 0)",
      "classification": "heuristic",
      "alternative_gold_standard": "expected wait = sum(remaining_service_time for truck in queue) + mean_residual(busy_truck)",
      "expected_loss_vs_optimal_pct": 5.0,
      "why_chosen": "implementation cost / data availability — full M/M/c upper bound 솔버 미가용",
      "phase_decided_at": "phase 06 plan tournament round-2",
      "decision_id": "Q-D11"
    },
    {
      "id": "MS-002",
      "location": "src/mine_sim/simulation.py:248",
      "current_form": "edge_time *= lognormal_noise(rng, cv)",
      "classification": "defensible-coarse",
      "alternative_gold_standard": "per-metre noise: edge_time = sum(deterministic_metre * lognormal_noise(rng, cv) for metre in edge_metres)",
      "expected_loss_vs_optimal_pct": 2.0,
      "why_chosen": "long-edge under-disperse 영향 minor (CV=0.1, edge_length 평균 200m)",
      "phase_decided_at": "phase 02 cold-reread",
      "decision_id": "Q-D3"
    }
  ],
  "verdict": "pass"
}
```

## 게이트 룰

- **phase 02 (cold-reread) entry** — `intent/modeling_shortcuts.json` 골격 emit 의무 (cold reviewer 가 후보 추출).
- **phase 06 (plan) exit** — 모든 shortcut 의 classification 확정 + alternative + expected_loss_vs_optimal_pct 명시 의무.
- **phase 08 (impl) entry** — `placeholder` tier 0 건 의무. 발견 시 phase 06 재진입.
- **phase 09 (gate) §Modeling-Shortcuts** (신규) — JSON evidence verdict 검증.
- **plan implementation guidance per TODO** — 각 shortcut 의 *anti-pattern explicit ban* 의무 (예: "do not use Python `hash()` for seed", "do not use `len(queue)` as expected wait estimator").

## 4-tier 결정 트리 (cold reviewer 매뉴얼)

```
Q1: 학계/업계 표준 optimal solver 가 직접 사용 가능한가?
    Yes → gold-standard
    No  → Q2

Q2: alternative gold-standard 가 *명시* + 기각 사유 *데이터/시간 제약* 으로 명시되었는가?
    Yes → defensible-coarse
    No  → Q3

Q3: expected_loss_vs_optimal_pct 추정값이 명시되어 있는가?
    Yes → heuristic
    No  → placeholder
```

## C-MSC (self_lint 미등록 — sprint-40 PR-F 신규)

phase 02 종료 시:
- `intent/modeling_shortcuts.json` 존재 확인
- 모든 shortcut 에 `classification` + `alternative_gold_standard` + `expected_loss_vs_optimal_pct` 명시 확인
- `placeholder` tier 0 건 (phase 08 진입 시점)

phase 09 entry:
- 본 JSON 의 verdict == "pass" 확인
- 미달 시 phase 09 진입 거부

## 도메인 어댑터 매핑

| 도메인 | 의무 shortcut 카테고리 (premortem 자동 검사) |
|---|---|
| **DES** | dispatch policy fidelity, noise distribution scaling, warmup justification, queue depth estimator |
| **ML** | optimization stopping criterion, validation split strategy, loss function approximation, regularization choice |
| **API** | retry policy, timeout default, rate limiting heuristic, cache TTL choice |
| **데이터 ETL** | batch size choice, dedup strategy, schema validation strictness |

각 도메인의 표준 shortcut 카테고리는 [`domain-pack.md`](domain-pack.md) 의 도메인 어댑터에 박힘 — 본 컨벤션이 phase 02/05 cold reviewer 가 자동 attach.

## simulation-bench 001 v0.9.44 g4-v2 검증 (sprint-40 PR-F 직접 대응)

### Reviewer 인용
- (a) `Dispatcher.choose_loader` queue=`len(queue)+busy_flag` — *defensible but coarse* (Sim correctness -1pt)
- (b) `simulation.py:248` travel-noise = `lognormal_noise(rng, cv)` *1 draw per edge* — *under-disperses for long edges* (-1pt)

### sprint-40 PR-F 적용 시 차단 흐름

1. Phase 02 cold-reread 가 `dispatcher.py` + `simulation.py` 자동 grep → modeling_shortcuts.json 골격에 (a), (b) 후보 추출.
2. Phase 05 critique cold reviewer (DES sub-deck) 가 두 shortcut 의 *alternative gold-standard* + *expected_loss_vs_optimal* 강제.
3. Phase 06 plan tournament 의 6-dim 에 *heuristic-fidelity* 차원 추가 (DES 도메인 자동 expansion) — universe 분기 시 두 shortcut 에 대한 다른 선택 의무 비교.
4. Phase 09 §Modeling-Shortcuts gate 가 verdict == "pass" 확인.

**효과 추정**: Sim correctness 18/20 → 19~20/20 (직접 +1~2pt).

## 안티 패턴

a- **classification 모호 ("approximate" 라고만 적음)** — 4-tier 중 하나 정확히 선택 의무. 모호 = phase 02 재진입.
b- **alternative_gold_standard 미명시** — heuristic / defensible-coarse tier 의 *비교 기준* 없으면 분류 자체 무효.
c- **expected_loss_vs_optimal_pct 추정 skip** — heuristic tier 의 의무 필드. skip 시 phase 09 fail.
d- **placeholder 가 impl 단계까지 잔존** — 0 tolerance. phase 08 진입 시 자동 차단.
e- **shortcut 발견 후 plan implementation guidance 에 anti-pattern ban 미반영** — guidance 가 *그 shortcut 을 다시 쓰게* 둠. v0.9.44 회차의 D-6 (`SeedSequence(hash())`) 사례 = T-002 distributions.py 가이드에 "do not use Python hash() for seed" 가 박혀 있었어야.

## 메모리 정합

- [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md) — 6pt 질적 layer 갭의 *Sim correctness* 차원 직접 보강.
- [`feedback_premortem_not_pause.md`](../../../memory/feedback_premortem_not_pause.md) — premortem 의 *수학 axis* 확장.
- [`project_bench_001_v0944.md`](../../../memory/project_bench_001_v0944.md) — 두 휴리스틱 (queue + noise) flag 직접 대응.
