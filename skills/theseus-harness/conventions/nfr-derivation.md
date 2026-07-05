---
id: nfr-derivation
category: quality
applies-to-phases: '[01,09]'
applies-to-grades: '[all]'
trigger-when: 'NFR derived'
indexed-in: conventions/INDEX.md
---

# NFR Derivation — Prompt 형용사로부터의 비기능 요구 자동 도출

## 한 줄 요약

**Prompt 본문의 *qualitative 형용사군* 을 NFR 후보로 자동 변환한다.** 페이즈 01 의 *fixed list* (도메인 카탈로그 매칭) 와 별개의 channel — *fixed list* 는 도메인 사전 지식 의존이라 prompt 의 *명시 의도* 를 놓친다. 본 컨벤션이 그 결손을 메우는 *도메인 독립 룰*.

## 왜 이 컨벤션이 필요한가

`spec-catalog.md` 의 도메인 카탈로그 (결제·검색·로그인·...) 는 *명사 (도메인) → NFR* 매칭 — *형용사 (품질) → NFR* 은 누락. Prompt 가 "**clear, reproducible, interpretable** modelling-and-simulation" 처럼 *형용사군* 으로 의도의 본질을 표현할 때, 명사 카탈로그는 본 의도를 잡을 수 없다. simulation-bench 외부 적용 (synthetic_mine_throughput_003 sprint-01) 에서 본 결손이 객관 노출 — ouroboros 97 vs 003 sprint-01 94 의 3pt 차이의 *진짜 메커니즘*.

## Qualitative 어휘 카탈로그 (도메인 독립, 의미군 단위)

본 카탈로그는 *씨앗* — 사용자 prompt 의 한 형용사가 본 표의 한 행에 매칭되면 해당 NFR 후보가 자동 산출. 외래 어휘는 의미적 동의어로 재맵 (LLM-driven semantic match — 정확 문자열 매칭만 아님).

| ID | 의미군 (영/한 동의어) | NFR 후보 | derive 기준 verification 후보 |
|----|----|----|----|
| Q1 | clear / clean / explicit / transparent / 명확한 / 투명한 | clarity | (a) 산출물의 정량 vs 정성 분리 (b) assumption 표 의무 (c) decision 추적표 |
| Q2 | reproducible / deterministic / idempotent / replayable / 결정적 / 재현 가능 | reproducibility | (a) seed 명시 + log (b) byte-hash 매치 across re-run (c) pinned dep version |
| Q3 | interpretable / auditable / decision-ready / traceable / 해석 가능 / 의사결정 가능 / 추적 가능 | interpretability | (a) 결정 질문별 정량 답 (b) sensitivity 매트릭스 (c) 운영 권고 ROI |
| Q4 | realtime / responsive / low-latency / 실시간 / 응답성 | latency | (a) p99 측정 (b) SLO 명시 (c) percentile 게이트 |
| Q5 | safe / secure / private / confidential / 안전 / 보안 / 프라이버시 | security | (a) secret 0개 git 검출 (b) auth 명시 (c) 위협 모델 |
| Q6 | resilient / fault-tolerant / graceful / 복원력 / 결함 허용 | resilience | (a) failure injection (b) retry 정책 (c) degraded mode |
| Q7 | accurate / precise / 정확한 / 정밀한 | accuracy | (a) ground truth 비교 (b) 분석적 상한 vs 측정값 (c) confusion matrix |
| Q8 | scalable / horizontal / 확장 가능 / 수평 확장 | scalability | (a) load curve (b) p99 vs throughput (c) shard 룰 |
| Q9 | maintainable / readable / refactorable / 유지보수 가능 | maintainability | (a) DIP score (b) cyclomatic complexity (c) doc coverage |
| Q10 | comprehensive / complete / exhaustive / 포괄적 / 완비 | completeness | (a) requirement coverage (b) edge case 카탈로그 (c) optional scope 활용 |

이 표는 *씨앗* 이지 *닫힌 카탈로그* 가 아님 — 새 의미군이 prompt 에 등장하면 LLM 이 *유사 의미군* 매칭 후 본 표에 *neighbor 로 등록*. 본 컨벤션의 본질은 "prompt 의 형용사 → NFR" 의 *derivation rule* 자체이지 표의 *행 갯수* 가 아님.

## Derivation Rule (intent-extractor 호출 시점)

페이즈 01 의 의도 추출 단계에서 `agents/intent-extractor.md` 가 다음 호출:

```
1- prompt 본문에서 qualitative 형용사 어휘 스캔
   - 명사구 수식어, 부사구, 등위 접속절의 형용사 모두 후보
2- 본 표의 의미군 매칭 (LLM-driven semantic — 정확 문자열만 아님)
   - "lucid" / "self-explanatory" → Q1 clarity
   - "deterministic across runs" → Q2 reproducibility
3- 매칭된 의미군마다 NFR 후보 + verification method 후보 list 작성
4- intent/01-intent.md 의 §i "Derived NFRs from prompt qualitative adjectives" 절에 자동 채움
```

매칭 0개 = "본 prompt 는 qualitative NFR 명시 0 — functional only" 명시 (drift 가드).

## Phase 04 후속 질의 매핑

페이즈 04 (clarify) 가 *각 derived NFR 마다* 후속 질의 1건 생성:

```
질의 (NFR-derived, NFR=Q2 reproducibility):
재현 가능성 검증 방법은?

선택지:
1. seed 로그 + per-rep RNG 분리 (verification.a)
2. byte-hash SHA256 매치 across 2회 실행 (verification.b)
3. pinned dep version + lockfile 봉인 (verification.c)
4. N/A — 본 NFR 은 본 작업에선 비활성
```

페이즈 04 의 누적 질의 수 무한 룰 ([`interview.md`](interview.md) §3) 정합 — derived NFR 갯수만큼 질의 추가.

## Phase 09 게이트 동적 생성

페이즈 09 의 `gate_set = static_gates_7 ∪ derived_gates(NFR_answers)`:

```python
def derived_gates(nfr_answers: list[NFRAnswer]) -> list[Gate]:
    gates = []
    for ans in nfr_answers:
        if ans.option == 4:  # N/A
            continue
        verification_id = ans.option  # 1, 2, 3
        gate = Gate(
            id=f"DG-{ans.nfr_id}-{verification_id}",
            check=ans.verification_protocol,
            on_fail="auto_fix_trigger" if ans.auto_fix else "truthful_record",
        )
        gates.append(gate)
    return gates
```

NFR 0 = derived gate 0 = static 7 만. NFR 5 = derived gate 5 추가 = 12 게이트.

각 derived gate 의 fail 처리는 *본 컨벤션이 결정 안 함* — 페이즈 04 의 사용자 답안에 따라 (a) auto-fix trigger 또는 (b) truthful record. 003 sprint-01 의 byte-repro fail 이 "truthful record" 로 처리된 것은 정합 — 사용자 Q-D2 답이 "회귀 자율" 이었으면 auto-fix 가 옳음.

## 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 본 컨벤션은 *형용사 → NFR → verification* 의 *3단 derivation* 만 정의. 어떤 도메인이든 prompt 의 형용사를 입력으로 받음.
b- 본 표의 행은 *씨앗* — 닫힌 카탈로그 아님. 새 의미군은 LLM-driven semantic match 로 흡수.
c- 게이트는 *fixed list* 아님 — NFR 답안에 따라 동적 생성. 본 케이스의 byte-repro 게이트는 prompt 가 "reproducible" 을 안 썼으면 *자동 비활성*.

## Anti-pattern (본 컨벤션 위반)

a- *spec-catalog.md 의 도메인 카탈로그를 본 컨벤션의 대체로* — 도메인 카탈로그는 *명사*, 본 컨벤션은 *형용사*. 둘은 *직교* 채널.
b- *Qualitative 어휘 카탈로그 의 행을 케이스별로 add* — 본 표는 *씨앗*. 행 추가는 의미군 단위만, 케이스 단위 X.
c- *NFR 도출 후 사용자 확인 생략* — 페이즈 04 의 후속 질의는 *의무*. 자동 도출 + 사용자 확정의 2 stage.

## 자기 검증 (sprint-01 003 회귀 검증)

본 컨벤션이 v0.9.5 이전에 있었다면 003 sprint-01 의 페이즈 01 산출물에 "Derived NFRs: clarity, reproducibility, interpretability" 가 자동 채워졌을 것. 페이즈 04 가 각 NFR 마다 verification method 질의 → 페이즈 09 가 byte-hash gate + reachability gate + ROI gate 자동 생성 → sprint-01 의 자체 추정 점수가 94 가 아닌 ≥97 도달. 본 컨벤션의 도입은 simulation-bench 외부 적용의 *구조적 처치* 이지 *케이스 패치* 아님.

## 외부 참조

- [`spec-catalog.md`](spec-catalog.md) — 도메인 (명사) NFR 카탈로그. 본 컨벤션과 직교.
- [`interview.md`](interview.md) — 페이즈 04 인터뷰 룰 + 누적 질의 무한 한도.
- [`autonomy.md`](autonomy.md) — Q-D1~D9 사전 위임. derived NFR 의 fail 처리 정책 결정.
- [`test-invariants.md`](test-invariants.md) — derived gate 의 *invariant 형 check* 의 위치.

## 도메인 sub-checklist (sprint-40 PR-G 신규 — methodology completeness)

본 컨벤션의 *형용사 → NFR* 채널과 별개로, 도메인 매칭 시 *methodology* 차원의 sub-checklist 를 phase 01 intent 에 자동 inject. simulation-bench 001 v0.9.44 g4-v2 회차의 -1pt Experimental design (warmup_minutes=0 정당화 thin) 직접 정정.

### DES 도메인 의무 methodology 항목

| 항목 | derive 기준 verification 후보 |
|---|---|
| **warmup justification** (quantitative) | (a) first-half / second-half throughput delta 측정 (b) delta > 5% 시 warmup_minutes 정당화 evidence 박힘 (c) batch-means 또는 학계 휴리스틱 reference |
| **replication count power analysis** | (a) target CI half-width 명시 (b) 30 reps 가 그 width 도달 evidence (c) variance pilot estimate |
| **common-random-numbers protocol** | (a) seed derivation source (paired across scenarios) (b) reproducibility byte-equal (PR-B G-RDC 정합) |
| **terminating vs steady-state 분류** | (a) shift_min 이 finite horizon (terminating) 또는 long-run mean (steady-state)? (b) 분류 명시 + 그에 따른 반복/warmup 정책 |

### ML 도메인 의무 methodology 항목

| 항목 | verification |
|---|---|
| **train/val/test split independence** | (a) leakage check (b) temporal split for time-series (c) stratification verification |
| **early stopping protocol** | (a) patience parameter justified (b) val metric monotonic check |
| **regularization choice rationale** | (a) L1/L2/dropout choice + 기각 사유 (b) cross-val 결과 |

### API 도메인 의무 methodology 항목

| 항목 | verification |
|---|---|
| **load test design** | (a) traffic pattern (smooth / spike / chaos) (b) duration justified (c) cold-start vs warm 분리 |
| **error budget** | (a) SLO target (b) MTBF estimate (c) graceful degradation 정책 |

### 산출물 — `quality/gate_warmup.json` (DES 시 의무, sprint-40 PR-G 신규)

```json
{
  "schema_version": "0.9.45",
  "domain": "DES",
  "methodology_checklist": {
    "warmup_justification": {
      "warmup_minutes_value": 0,
      "first_half_throughput_mean": 12086.7,
      "second_half_throughput_mean": 12087.2,
      "delta_pct": 0.004,
      "delta_threshold_pct": 5.0,
      "evidence_path": "outputs/half_split_analysis.csv",
      "verdict": "pass"
    },
    "replication_count_power": {
      "target_ci_half_width_pct": 0.5,
      "observed_ci_half_width_pct": 0.28,
      "reps": 30,
      "verdict": "pass"
    },
    "common_random_numbers": {
      "seed_derivation": "SeedSequence([base, _stable_hash(scenario_id), rep])",
      "reproducibility_evidence": "quality/gate_v6_reproducibility.json",
      "verdict": "pass"
    },
    "terminating_vs_steady_state": {
      "classification": "terminating",
      "rationale": "shift_min = 480 (finite 8h shift) — terminating simulation",
      "evidence_path": "conceptual_model.md#L42",
      "verdict": "pass"
    }
  },
  "verdict": "pass"
}
```

### 게이트 룰

- `domain == "DES"` 면 4 항목 모두 `verdict == "pass"` 의무
- `warmup_minutes == 0` 인데 `delta_pct > delta_threshold_pct` (5%) → warmup_minutes 증가 또는 first-half 데이터 분리 의무
- `terminating_vs_steady_state.classification` 이 `"unspecified"` 면 phase 09 진입 거부

### C-WUP (self_lint 미등록 — sprint-40 PR-G 신규, Warmup Quantification)

phase 09 진입 시 (도메인이 DES 일 때):
- `quality/gate_warmup.json` 존재 확인
- 4 methodology 항목 모두 verdict == "pass" 확인
- `warmup_justification.evidence_path` 가 실제 존재하는 파일인지 확인 (regex 0 매치 = 빈 evidence)
- 미달 시 phase 09 진입 거부

### simulation-bench 001 v0.9.44 g4-v2 검증 (sprint-40 PR-G 직접 대응)

`baseline.yaml: warmup_minutes: 0`. 회차 산출물에 first-half/second-half throughput 분리 0. reviewer *"correctly note this is a transient inclusion but neither quantifies it nor justifies the choice on first principles for an 8 h shift"* — Experimental design -1pt.

**sprint-40 PR-G 적용 시 차단 흐름**:
1. Phase 01 intent extraction 시 `domain: DES` 자동 검출 → DES sub-checklist 자동 inject.
2. Phase 04 인터뷰가 4 methodology 항목 사용자 확정 (또는 자율 결정 default).
3. Phase 09 §Warmup-Quantification (신규 sub-gate) 가 `gate_warmup.json` verdict 검증.
4. `delta_pct = 0.004` (0.4%, 5% 임계 < 충분히 작음) → "warmup 0 OK" 의 evidence-bound 정당화.

**효과 추정**: Experimental design 14/15 → 15/15 (직접 +1pt).

### 메모리 정합

- [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md) — 6pt 질적 layer 의 *Experimental methodology* 차원 직접 보강.
- [`feedback_analytical_bound_validation.md`](../../../memory/feedback_analytical_bound_validation.md) — analytical bound cross-validation 의 *시간 차원* 확장.
- [`project_bench_001_v0944.md`](../../../memory/project_bench_001_v0944.md) — warmup justification thin 직접 대응.
