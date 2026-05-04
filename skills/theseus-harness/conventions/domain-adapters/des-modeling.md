---
name: des-modeling
description: Discrete-event simulation 도메인 어댑터 — SimPy / event-driven / process / resource 패턴
triggers:
  - regex: "discrete[-_ ]event|DES|simpy|simulation"
    weight: 0.4
  - regex: "process|resource|event[-_ ]driven|env\\.|env\\s*="
    weight: 0.3
  - regex: "replication|reps|seed|stochastic"
    weight: 0.3
match_threshold: 0.5
authority: "academic + best-practice (Banks/Carson/Nelson DES textbook + SimPy docs)"
references:
  - "Banks, Carson, Nelson, Nicol — Discrete-Event System Simulation (5th ed.)"
  - "SimPy 4.x official documentation — Resource / Process / Container patterns"
  - "Law — Simulation Modeling and Analysis (5th ed.)"
---

# DES Modeling Adapter

## §i-additions (NFR 추가)

| NFR | 설명 |
|---|---|
| **determinism** | 동일 (seed, scenario) → byte-identical 결과. simpy 의 _Process queue stable order 의존 회피 (single mutation point 패턴). |
| **byte_repro** | results.csv + event_log.csv SHA256 동일 across runs. dict 직렬화 시 sorted key 의무. |
| **convergence_diagnostic** | 30 reps 외 *수렴 검증* — sliding-window 95% CI width 가 mean 의 ≤2% 면 converged. 미달 시 reps 증가 권고. |
| **warmup_handling** | 8h shift 의 cold start bias 명시 (~1% downward). warmup window cut 옵션. |
| **stochastic_independence** | 트럭별 / event 별 RNG 분리 (per-stream RNG). 전역 random 0. |

## §architecture-patterns

a- **Single mutation point** — 모든 entity state 변경이 단일 `_dispatch_event(ev)` 함수에서. race condition 0.
b- **FIFO Resource** — simpy.Resource(capacity=N) + FIFO native queue. starvation 0.
c- **Bidirectional cap-1 segment** — 단일 lane 양방향 = 단일 `simpy.Resource(capacity=1)` + 방향 토큰. *per-direction Resource × 2 = unphysical 인플레*.
d- **Pure Dijkstra** — networkx 의존 0, edge_id alphabetical tie-break for byte-repro.
e- **numpy structured array event log** — pre-allocated MAX_EVENTS_PER_REP, mass-emit at rep end. CSV 직렬화 비용 감소.
f- **Per-rep RNG** — `np.random.default_rng(base_seed + rep_idx)` 만. 전역 random / threading RNG 0.

## §limitations (도메인 known limitations)

- **Single 8h shift** — multi-shift effects (driver fatigue, shift change overhead) 미모델
- **No warm-up window** — t=0 cold start, ~1% downward bias on total throughput
- **No breakdown / availability < 1.0** — entity availability fixed at 1.0
- **Hard cutoff** — shift end 시 in-flight events 누락 (small symmetric bias across scenarios)
- **Static dispatch** — dynamic re-balancing 미모델 (loader 고장 시 적응 X)

## §decision-templates

DES 도메인의 6 결정 질문 답 형식 :

```
Q: <decision question>
A: <primary metric value> <unit> (95% CI [<low>, <high>], n=<reps>)
   ratio_to_baseline: <delta %>
   confidence: <high|medium|low>  ← uncertainty quantification
   robustness: <decision flips when <assumption changes>?>
   recommendation: <action> ← risk-adjusted
```

confidence band + robustness sensitivity 강제 (deep-semantic-intent.md 의 decision-support framing 정합).

## §verification-hooks

- analytical_bound_cross_validation (loader-bound / crusher-bound / fleet-bound) — v0.9.12 컨벤션 직접 활용
- byte_repro_test — 동일 seed 두 회 실행 + SHA256 비교
- sanity_4 patterns — scenario 간 monotonic 관계 검증 (예: trucks_12 > trucks_4)
- convergence_check — 30 reps CI width 임계

## §code-organization (DDD)

```
mine_sim/                       (또는 도메인-specific 패키지)
├── topology/                   (graph + routing)
├── model/                      (entities + dataclasses)
├── experiment/                 (runner + scenario + replication)
├── analysis/                   (aggregator + bottleneck + decision)
└── report/                     (summary + narrative)
```

DDD layer 분리 — interface-first-parallel-impl §3 의 sub-agent fan-out 단위 정합.
