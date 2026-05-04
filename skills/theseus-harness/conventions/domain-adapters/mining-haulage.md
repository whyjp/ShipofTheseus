---
name: mining-haulage
description: 광산 haulage 도메인 어댑터 — truck / loader / crusher / ramp / shift 패턴
triggers:
  - regex: "truck|haul|haulage|fleet"
    weight: 0.3
  - regex: "loader|crush|crusher|dump"
    weight: 0.3
  - regex: "ore|mining|pit|mine|shift|ramp"
    weight: 0.4
match_threshold: 0.5
authority: "industry-standard (AusIMM Mine Manager's Handbook + open-pit haul truck operating data)"
references:
  - "AusIMM Mine Manager's Handbook — haulage cycle modeling"
  - "Caterpillar Performance Handbook — haul truck cycle time + payload patterns"
  - "Open-pit mining: empirical MTBF / availability data (industry typical 0.85-0.95)"
failure_patterns:
  - id: DFP-MH-1
    name: "No saturation analysis"
    detection: "fleet sweep (trucks_4 / baseline / trucks_12) 미진행 또는 saturation point 식별 부재"
    severity: cap_results
    remediation: "fleet sweep + saturation point 식별 + Δ(N→N+4) plot"
  - id: DFP-MH-2
    name: "Bottleneck claim without composite score"
    detection: "bottleneck 결론이 utilization 만 또는 queue 만 — composite (util × wait) 부재"
    severity: cap_results
    remediation: "composite bottleneck score (utilisation × queue_wait) 계산"
  - id: DFP-MH-3
    name: "No capex / payback in fleet recommendation"
    detection: "R1 fleet sizing 답에 truck capex / payback 본문 부재"
    severity: cap_results
    remediation: "capex per truck (typical $750K-1.2M) + payback estimate 의무"
  - id: DFP-MH-4
    name: "Per-direction ramp Resource"
    detection: "단일 ramp 양방향에 Resource × 2 → throughput inflation"
    severity: cap_correctness
    remediation: "단일 Resource(capacity=1) + 방향 토큰 또는 passing bay 명시"
  - id: DFP-MH-5
    name: "Availability = 1.0 without limitation note"
    detection: "MTBF / availability 모델링 0 + limitations 절에 명시 부재"
    severity: warning
    remediation: "limitations 절에 'no breakdown / availability=1.0' 명시 + bias 추정 (~10% upward)"
---

# Mining Haulage Adapter

## §i-additions (NFR 추가)

| NFR | 설명 |
|---|---|
| **MTBF_modeling** | 트럭 / 로더 / 크러셔 평균 고장 간격. 일반 open-pit data: trucks ~150-300 hr MTBF, loaders ~300-500 hr, crushers ~500-1000 hr. *현재 모델은 MTBF 미반영* — limitation 명시 의무. |
| **availability_lt_1.0** | 산업 typical 0.85-0.95. 본 모델 1.0 가정 = ~10% upward bias. *limitation 명시* 의무. |
| **grade_variation** | 광석 품위 변동 (g/t Au, % Cu 등) → 처리량 외 *품질 metric* 추가 가능. 본 task 는 단일 ore type 가정 — 명시 의무. |
| **shift_handover** | 8h shift 시작/종료 의 *부분 사이클* 처리 (현재 model = hard cutoff). |
| **ramp_capacity_physics** | 단일 lane bidirectional ramp = single shared simpy.Resource(cap=1). per-direction × 2 = ~30% throughput inflation (unphysical). |

## §architecture-patterns

a- **Truck cycle** — PARK → loader → CRUSHER → PARK 반복. cycle_time = mean ~30-60 min depending on haul distance.
b- **Loader-truck balance** — fleet sizing rule: trucks ≈ 4-6 × loaders for typical 30-60 min cycle. saturation 신호 = trucks_n / trucks_n+1 throughput delta < 5%.
c- **Crusher-bound vs ramp-bound vs loader-bound** — bottleneck 식별 = composite (utilization × queue_wait). DES community standard.
d- **Static dispatch (nearest-loader / inverse-mean-load-time)** — typical baseline. *dynamic re-balancing* (queue length 기반) = capex 0 의 throughput +5-10%.
e- **Bidirectional ramp single-pool** — single-lane physics 정합. *passing bay* 가 있으면 cap=2 가능 (산업 fact, 본 데이터 명시 안 됨).

## §limitations

- **No truck breakdown** — availability = 1.0. 산업 typical 0.85-0.95 (-5~15% bias on absolute throughput).
- **No driver heterogeneity** — 모든 driver 동일 + rule-following 가정. real spread 10-20% (CI95 +5-8% wider 가능).
- **No grade variation** — 단일 ore type. 실 광산 grade variation +/- 30% per truck load.
- **No shift handover overhead** — 8h fully productive 가정. 산업 typical ~6.5-7h productive (-15-20% bias).
- **No ramp passing bay** — single-lane assumption. 일부 ramp 는 passing bay 보유.

## §decision-templates

Mining capex 결정 패턴 :

```
R1 Fleet sizing
  trucks_4 vs baseline vs trucks_12 throughput delta
  capex per truck (typical $750K-1.2M USD for 100t haul truck)
  payback = capex / (annual_revenue_delta) — typical 12-36 months at $18-25/t ore @ 6-7t/cycle effective grade
  recommendation: pilot (10 trucks mid-step) | hold | recommend

R2 Ramp upgrade
  ramp_upgrade vs baseline throughput delta
  capex (typical $3-6M for ramp widening + speed improvement)
  payback = capex / annual_revenue_delta
  recommendation: justified | not justified without complementary fleet

R3 Crusher reliability
  crusher_slowdown sensitivity — typical 1pp/pp meaning crusher is primary risk
  redundancy capex = $5-15M for second crusher line
  recommendation: invest_redundancy | monitor PM cycles only

R4 Route resilience
  ramp_closed bypass capability
  per-shift loss during forced closure (typical $5K-50K/shift at $18-25/t ore)
  recommendation: bypass adequate (off-shift maintenance) | major loss (avoid concurrent)

R5 Schedule / replication
  baseline absolute (typical 600-2000 t/h for open-pit operations)
  reps cost-benefit (60 vs 30 narrows CI ~30%)
  recommendation: capex-grade analysis cost trivial vs operational use
```

각 R1-R5 는 confidence band + robustness sensitivity 의무 (deep-semantic-intent.md decision-support 정합).

## §verification-hooks

- **analytical_bound_cross_validation** (loader-rate × N + crusher-rate + ramp-capacity) — payload assumption 검증 의무
- **sanity_4 mining-specific** :
  - trucks_12 > trucks_4 (fleet monotonic)
  - ramp_upgrade ≥ 0.95 × baseline (upgrade 비역효과 0)
  - crusher_slowdown < baseline (crusher 영향)
  - ramp_closed ≤ 1.05 × baseline (ramp 닫혀 throughput 증가는 모델 오류)

## §typical-input-parameters

mining bench 의 *typical 데이터* (어댑터의 expected ranges) :
- payload: 50-200 t (open-pit haul truck class 240E 100t 대표)
- truck_speed: 30-60 kph empty / 25-50 kph loaded
- loader service time: 3-8 min mean
- crusher service time: 2-5 min mean (dump cycle)
- shift length: 8h or 12h
- replications standard: 30+

trucks.csv / nodes.csv 의 *실 값* 이 위 typical range 외이면 *입력 가정 재검증* 트리거 (analytical-bound 의 80% 임계 fail 와 동일 메커니즘).
