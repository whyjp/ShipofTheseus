# 2026-05-09 — Bench 001 Synthetic Mine Throughput · v0.9.44 · 95/100 (94 plateau 돌파)

> **컨텍스트:** [`CHANGELOG.md`](../../CHANGELOG.md) v0.9.44 후속 절에 명시한 sprint-40 외부 적용 = simulation-bench 001 (synthetic_mine_throughput) 재제출. *sprint-37 (다이어트) → sprint-38 (깊이) → sprint-39 (4 패턴 inline)* 3 단계 누적 효과를 zero-context Opus 리뷰어 (분리 Agent + evaluate-submission 스킬) 의 100pt 휴먼-퀄리티 루브릭으로 측정. 결과 **95/100 — 94 plateau 첫 돌파 (+1pt).**
>
> 메모리 정합: [`project_simulation_bench_001_cold01.md`](../../../memory/project_simulation_bench_001_cold01.md) (94), [`project_simulation_bench_003.md`](../../../memory/project_simulation_bench_003.md) (94), [`project_v0914_cold01.md`](../../../memory/project_v0914_cold01.md) (94), [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md) (천정 분석).

## 1. 정량 결과

### 1-1. 시뮬레이션 산출 (53/53 자동 체크 = 100%)

| 시나리오 | tonnes mean | CI95 | t/h | Crusher util | Narrow ramp util |
|---|---:|---|---:|---:|---:|
| baseline | 12 086.7 | [12 018.2, 12 155.1] | 1 510.8 | 0.886 | 0.052 |
| trucks_4 | 7 836.7 | [7 793.4, 7 880.0] | 979.6 | 0.576 | 0.026 |
| trucks_12 | 12 713.3 | [12 615.4, 12 811.3] | 1 589.2 | 0.929 | 0.079 |
| ramp_upgrade | 12 136.7 | [12 069.1, 12 204.2] | 1 517.1 | 0.884 | 0.000 |
| crusher_slowdown | 6 506.7 | [6 452.1, 6 561.2] | 813.3 | 0.953 | 0.052 |
| ramp_closed | 12 040.0 | [11 989.4, 12 090.6] | 1 505.0 | 0.879 | 0.000 |

행동 sanity 6/6 PASS · 자동 체크 53/53 PASS · 런타임 9.03 sec · 18 .py 파일 / 1 426 코드 줄.

### 1-2. 휴먼-퀄리티 루브릭 (95/100)

| 카테고리 | Max | 점수 | 손실 | 리뷰어 사유 |
|---|---:|---:|---:|---|
| Conceptual modelling | 20 | **19** | -1 | 잔여 (사유 미명시 — 천정 6pt 갭의 일부) |
| Data and topology handling | 15 | **15** | 0 | 만점 |
| Simulation correctness | 20 | **18** | -2 | dispatcher queue=`len(queue)+busy` 휴리스틱 (실제 wait 미측정) + travel-noise 1 draw / edge (per-metre 분산 부족) |
| Experimental design | 15 | **14** | -1 | warmup_minutes=0 정당화 thin (cold-start transient 정량화 부재) |
| Results and interpretation | 15 | **14** | -1 | README §7 표 ↔ summary.json 수치 드리프트 (~0.08%) |
| Code quality and reproducibility | 10 | **10** | 0 | 만점 |
| Traceability and auditability | 5 | **5** | 0 | 13 386 row event_log + topology.png CSV 자동 생성 |
| **합계** | **100** | **95** | **-5** | |

리뷰어 *Final judgement*: "**Yes** — would trust this model as a first-pass decision-support artefact." 운영 결론 (crusher dominance · 8→12 saturation · ramp 비-병목 · ramp_closed 견고) 모두 물리적으로 defensible.

## 2. 점수 손실 5pt — 본 하네스 단점 매핑

리뷰어가 깐 4 weakness + 잔여 1pt = **5 gap**. 각각 *현재 게이트 / 누락 차원 / sprint-40+ 개선 후보* 3 항으로 추적.

### G-1. Cross-process 재현성 게이트 = 텍스트-only · -2pt 직접 (리뷰어가 D-6/V6 버그 발견)

**증상.** 리뷰어가 README baseline=12 126.7 vs `summary.json`=12 116.7 (~0.08% drift) 발견 → 비-결정성 가설 → bisect 결과 `src/mine_sim/distributions.py::replication_rng` 가 Python `hash(scenario_id)` 를 `numpy.random.SeedSequence` 안에 사용. Python `hash()` 는 *프로세스 시작마다 salt 랜덤화* — 같은 입력이 다른 process invocation 에서 다른 hash → 다른 SeedSequence → 다른 출력.

**현재 게이트.** [`.ShipofTheseus/mine-throughput-g4-v2/quality/09-quality-gate.md`](../../../.../mine-throughput-g4-v2/quality/09-quality-gate.md) §V6 *Reproducibility ✅* — "Two consecutive `python run_experiment.py` invocations produce bit-identical `summary.json` aggregates" *라고 텍스트로 주장만* 한 채 PASS 마크. 실제 두 번 invoke 한 stdout 캡처 0.

**누락.** V6 = 텍스트 self-attestation 만으로 PASS 가능. *증거 1:1* 정합 [`feedback_score_rubric_objectivity`](../../../memory/MEMORY.md) 위반.

**Sprint-40+ 후보.**
- HARD-RULE: V6 evidence-bound — `sprints/<n>/v6/stdout1.txt` + `stdout2.txt` 의 *별도 process invocation* 산출물 필수, `sha256(stdout1) == sha256(stdout2)` 게이트.
- `gate_v6_reproducibility.json` 산출물 (file_a / file_b / digest_a / digest_b / equal). [v0.9.44 sprint-39 4 패턴 게이트 산출물 (gate_pnc/mirror/primary/literal.json) 와 동일 ABI](../../CHANGELOG.md#v0944--2026-05-09).
- self_lint: `grep -E 'SeedSequence\([^)]*hash\(' src/` 빈 결과 강제 (이번 사건의 auto-derived lint rule, [`bisect.md:53`](../../../.../mine-throughput-g4-v2/sprints/04/bisect.md)).

### G-2. README ↔ summary.json 수치 드리프트 게이트 부재 · -1pt (Results 14/15)

**증상.** README §7 표 baseline 12 126.7 t / ramp_closed 12 050.0 t. `summary.json` 12 116.7 / 12 023.3. 리뷰어 *"a reader trusting the README without cross-checking the JSON would cite the wrong numbers."*

**현재 게이트.** Phase 09 V5 (Output schema) 가 *summary.json 의 키 존재* 만 검사 — 마크다운 deliverable 본문의 수치 ↔ JSON 의 수치 *cross-reference* 미실시.

**누락.** 본 하네스의 *deliverable-internal-consistency* 차원 부재. 메모리 [`feedback_dual_pressure_json_schema.md`](../../../memory/feedback_dual_pressure_json_schema.md) 의 *이중 압력 (게이트 + viewer source)* 패러다임을 README ↔ summary 축으로 확장하지 못한 단계.

**Sprint-40+ 후보.**
- 신규 게이트 (phase 09 sub-gate) — README 마크다운 표 파싱 (regex `\|\s*[\w_]+\s*\|.*\d+(\.\d+)?`) → summary.json scenario fields 와 numerical equality (tol=0).
- 산출물: `gate_readme_summary_consistency.json` — table_rows / mismatches / max_relative_diff.
- self_lint: 새 README 추가 시 자동 잠금 (markdown table → JSON path mapping table 필수).

### G-3. 휴리스틱 vs 측정값 분류 게이트 부재 · -2pt 의 일부 (Sim correctness 18/20)

**증상.** 리뷰어 두 항목 *"defensible but coarse"* 플래그:
- `Dispatcher.choose_loader` queue depth = `len(queue) + (1 if busy else 0)` — currently-loading 트럭의 *남은 service time* 무시. true expected wait (mean residual service time) 가 한 단계 위.
- `simulation.py:248` travel-noise = `lognormal_noise(rng, cv)` *1 draw per edge* — long edge 에서 per-metre 모델 대비 under-disperses.

**현재 게이트.** Phase 02 cold-reread + Phase 07 plan review + Phase 09 V3 single-rep smoke 모두 *동작 여부* 만 확인. *"이 산식이 휴리스틱인가, 측정값인가, defensible coarse 인가, gold-standard 인가"* 4-tier 분류 미실시.

**누락.** 메모리 [`feedback_premortem_not_pause.md`](../../../memory/feedback_premortem_not_pause.md) 가 *forward simulation + derived_improvements* 를 의무화했지만 해당 derived 의 *대상 axis* 가 *프로세스 깨짐* 위주 — 도메인 모델링의 *수학적 깊이 axis* 미커버.

**Sprint-40+ 후보.**
- Phase 02/03 추가 산출물 `modeling_shortcuts.json` — (location, current_form, classification ∈ {gold-standard, defensible-coarse, heuristic, placeholder}, alternative_form, why_chosen) 5-필드 테이블.
- Phase 09 신규 sub-gate "domain depth" — `modeling_shortcuts.json` 의 `defensible-coarse / heuristic` 항목이 plan/impl-log 에 명시 reference 갖는지 검증.
- self_lint: dispatcher / queue / wait / noise / sample 키워드를 src/ 에서 grep → modeling_shortcuts.json 카탈로그와 1:1 매칭.

### G-4. Warmup 정량화 게이트 부재 · -1pt (Experimental design 14/15)

**증상.** `baseline.yaml` warmup_minutes=0. 리뷰어 *"correctly note this is a transient inclusion but neither quantifies it (e.g. by reporting throughput in the second half of the shift) nor justifies the choice on first principles for an 8 h shift."*

**현재 게이트.** Phase 09 V4 행동 sanity 6 항 *결과 평균* 만 검사. 같은 shift 안의 first-half vs second-half throughput delta 비교 0.

**누락.** 본 하네스의 *실험 설계 깊이* 가 reps × scenarios × CI95 까지만 — *정상 상태 진입* 검증 미커버. 메모리 [`feedback_analytical_bound_validation.md`](../../../memory/feedback_analytical_bound_validation.md) 의 cross-validation (잘못된 가정 자동 발견) 패러다임을 시간 차원으로 확장 미완.

**Sprint-40+ 후보.**
- Phase 09 신규 sub-gate "warmup quantification" — `summary.json` 의 각 scenario 에 `tonnes_first_half_mean` + `tonnes_second_half_mean` + `relative_delta` 필드 의무. delta > 5% 시 warmup_minutes 정당화 evidence (decision-ID Q-D? 와 1:1 reference) 강제.
- 산출물: `gate_warmup.json` — scenario × delta × verdict (steady / transient_acknowledged_with_evidence / transient_unjustified).
- self_lint: warmup_minutes=0 인 모든 scenario yaml 이 위 evidence reference 를 갖는지 grep.

### G-5. Conceptual 19/20 잔여 -1pt — 천정 갭 (사유 미명시)

**증상.** 리뷰어가 본 항목 *"Crisp boundary, entities, resources, events, state vars, assumptions, limitations, performance measures all present and well-organised"* 라고 평했지만 점수는 19. 명시 weakness 없음.

**해석.** 메모리 [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md) 의 *천정 6pt 갭 — Conceptual / Sim / Results 차원 질적 layer* 분석 정합. *enforcement 만으로 도달 불가* 의 직접 evidence — 본 회차는 enforcement 트랙 (sprint-37/38/39) 을 이미 풀로 적용한 산출물.

**누락.** *질적 깊이* 게이트 — literature reference / competing-mode analysis (e.g., FIFO 외 SRPT/EDD 비교) / 시스템 식별 / sensitivity-of-bottleneck (analytical bound vs simulation cross-check) — 본 하네스 0 지원.

**Sprint-40+ 후보.**
- Phase 03 cold-reread 추가 산출물 `conceptual_depth.json` — (boundary, alternative_modeling_choices, literature_or_first_principles_anchor, competing_dispatch_policies_considered, analytical_bound_vs_simulation).
- Phase 06 (인터뷰 후 첫 plan) 신규 *모델링 결정 분기 트리* — 각 *defensible-coarse* 항목당 *gold-standard alternative* 1 안 + *기각 사유* 의무.
- 단, 본 게이트는 sprint-40 이후 점진 도입 — 직접 1pt 회수 보장 X (천정 차원 = 비단조).

## 3. 점수 부재 추적 — 94 plateau → 95 break

| 회차 | 버전 | 점수 | 비고 |
|---|---|---:|---|
| 002 | v0.9.5 (sprint-02-e) | 92 | narrative-first 도입 전 |
| 003 | v0.9.6 (sprint-03) | 94 | nfr-derivation 도입 |
| v01_cold | v0.9.6 | 94 | fresh cold 첫 외부 적용 |
| v091_cold01 | v0.9.12 | 94 | analytical bound cross-validation 도입 |
| v0913_cold01 | v0.9.13 | **0** | scope-bench-aware 룰 충돌, design-only 산출 |
| v0914_cold01 | v0.9.14 | 94 | DG-DELIVERABLES-COUNT 강제 후 회복 |
| 본 회차 (g4-v2) | **v0.9.44** | **95** | **+1pt — 95 plateau 첫 돌파** |

**해석.** v0.9.6 → v0.9.14 9 sprint *enforcement-trail* 만으로 94 고정. v0.9.42-44 (sprint-37/38/39) 의 다이어트 + 본체 강화 + 4 패턴 inline 누적 후 +1pt. **이는 enforcement layer 의 마지막 1pt 까지 회수한 신호** — *그 위 5pt (G-3/G-4/G-5)* 는 *질적 깊이* axis. enforcement 가 아니라 *모델링 사고 depth* 의무화로만 도달 가능.

## 4. 분석 — 본 하네스의 식별 가능한 단점 5 카테고리

위 G-1~5 를 메타-분류:

| 카테고리 | gap | 본 하네스 차원 | sprint-40+ 후보 |
|---|---|---|---|
| **A. 자기-증거 (self-evidence)** | G-1 V6 | 텍스트 attestation → evidence 1:1 미정착 area | gate_v6_reproducibility.json + sha256 게이트 |
| **B. deliverable-internal 정합** | G-2 README↔JSON | dual-pressure JSON schema 의 *마크다운 본문* 미적용 | gate_readme_summary_consistency.json |
| **C. 도메인 깊이 분류** | G-3 휴리스틱 | premortem 의 *수학 axis* 미커버 | modeling_shortcuts.json + 09 domain-depth gate |
| **D. 시간 차원 검증** | G-4 warmup | analytical-bound cross-validation 의 *시간 축* 확장 미완 | gate_warmup.json + first/second-half delta |
| **E. 천정 차원 (질적 layer)** | G-5 conceptual | enforcement 외 *모델링 사고 depth* 의무화 미존재 | conceptual_depth.json + 모델링 결정 분기 트리 |

**카테고리 A·B 는 sprint-39 *4 패턴 inline* 의 직접 확장** — phase 09 §PNC/Mirror/Primary/Literal 옆에 §V6-Evidence / §README-Mirror 추가가 자연스럽다. **C·D 는 sprint-38 의 깊이 트랙 확장**. **E 는 신규 axis** — sprint-37/38/39 의 enforcement 패러다임 안에서는 마무리가 어렵고, *질적 게이트* 라는 새 패러다임이 필요.

## 5. sprint-40 권고

본 회차 (95/100) 는 v0.9.44 외부 검증의 *primary success signal*. **그러나 5 gap 모두 본 하네스 직접 책임** — 두 손에 있는 1pt 가 아니라 *천정* 5pt. CHANGELOG v0.9.44 §후속 절의 *"94 plateau 극복 검증"* 은 **수치적 만족** (+1pt) 이지만 *구조적 만족* 은 sprint-40 의 G-1 ~ G-4 4 게이트 도입 필요.

**구체 제안 — sprint-40 PR 분할:**

- PR-A · plan.md (sprint-40)
- PR-B · G-1 V6 evidence-bound + gate_v6_reproducibility.json + self_lint SeedSequence(hash()) 금지 — *직접 1pt 회수*
- PR-C · G-2 gate_readme_summary_consistency.json + phase 09 §README-Mirror — *직접 1pt 회수*
- PR-D · G-3 modeling_shortcuts.json + phase 09 §Domain-Depth — *간접 0.5–1pt*
- PR-E · G-4 gate_warmup.json + first/second-half 의무 — *직접 1pt 회수*
- PR-F · sprint 마감 (v0.9.45 + CHANGELOG)
- (G-5 = sprint-41+ 신규 패러다임 — *질적 게이트* — 별 sprint)

**예상 효과.** PR-B/C/E 직접 3pt + PR-D 간접 0.5–1pt → 98–99/100 도달 가능. 단, *본 회차의 95 는 enforcement 마지막 1pt* 관찰 정합 — sprint-40 의 +3 ~ +4pt 회수는 *증거-bound + 도메인-classification* 2 신축에 의존, sprint-37/38/39 패러다임의 *직접* 연장.

---

## Appendix — 원자료 위치 (참조 stable)

- 제출 폴더: `D:/github/simulation-bench/submissions/2026-05-09__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4-v2/`
- 거버넌스 trail (15-phase + 4 sprint): `D:/github/simulation-bench/.ShipofTheseus/mine-throughput-g4-v2/`
- 자동 평가 보고: `<제출 폴더>/results/evaluation_report.json` (53/53)
- 휴먼-퀄리티 리뷰: `<제출 폴더>/results/zero_context_review.md` (95/100)
- bisect 기록 (D-6/V6 reproducibility 버그): `<거버넌스>/sprints/04/bisect.md`
- 본 하네스 메모리 (천정 분석): [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md)
- 본 하네스 메모리 (해당 회차 — sprint-40 후 신규 후보): `project_bench_001_v0944.md` (미생성)
