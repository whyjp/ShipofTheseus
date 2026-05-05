---
name: theseus-harness
version: 0.9.24
description: 재귀 멀티 에이전트 코딩 하네스 — 15 페이즈 / 74 컨벤션. AIDE 멀티버스 G3-5/G4-7/G5-9 + v0.9.23 sprint-17+18 (orchestrator 슬림화 + intent-refresh 4 framing + dacapo cap 측정-only + 다이어그램 AND + runtime enforcement 5 신규).
---

# 테세우스 하네스

## 한 줄 요약
**한 요구를 처음 의도한 타이틀로 끝까지 부를 자격을 만들기 위한 재귀 코딩 하네스.** 당신(메인 에이전트)은 *지휘자* — 직접 작업하지 않고, 페이즈마다 정해진 서브 에이전트를 띄워 산출물을 받아 다음 페이즈로 넘긴다. 본 SKILL.md 는 *인덱스* 다 — 상세는 컨벤션·페이즈·에이전트 문서로 위임. 설계 철학·도자기 장인·AIDE 멀티버스: [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md).

## HARD-RULE — 첫 동작 + 페이즈 완주 강제

본 스킬 호출 직후 *첫 동작* = `timing/start.json` + 페이즈 00 (G3+) 또는 01 (G2) 산출물 작성. 직접 코드 작성 / `_tools/build_artifacts.py` 등 retroactive frontmatter generator / out-of-sandbox harness emulator / 페이즈 04 생략은 모두 위반 → `intent/00-violation.md` 기록 + 정상 재시작. **종료 시 그레이드별 의무 산출물 (G2: 11개 / G3: 30+ / G4-5: 풀) 모두 박혀야 정상 완주** — 페이즈 06 까지만 만들고 자발적 조기 종료 금지. **`plan/06-plan.md` 본문 의무**: 파일 경로 ≥ 5 / Mermaid 시퀀스 ≥ 1 또는 인터페이스 정의 ≥ 3 / TODO DAG. **`impl/08-impl-log.md` 본문 의무**: TODO ID 매핑 ≥ 3 / 모듈명 명시 / 인터페이스 노출. 풀 룰: [`../theseus-orchestrator/SKILL.md`](../theseus-orchestrator/SKILL.md) §HARD-RULE 8/9.

## 컨벤션 카탈로그 (70)

본 표 = *어떤 컨벤션이 어디 있는지 가리키는 색인*. 모두 미리 읽지 않는다 — 각 페이즈 문서가 *자기 페이즈에 필요한 컨벤션* 을 [`phases/`](phases/) 안에서 인용한다. 룰 본문 / 도입 배경 / cross-reference 는 각 컨벤션 파일에.

### 핵심 (a~v)

| ID | 컨벤션 | 핵심 |
|:-:|---|---|
| a | [`conventions/interview.md`](conventions/interview.md) | 두괄식·1 질의·숫자 5개·확증 회귀·PRD 처리 허들 |
| b | [`conventions/timing.md`](conventions/timing.md) | 산출물 헤더 시간 메타·라이브 보고 |
| c | [`conventions/diagrams.md`](conventions/diagrams.md) | 마인드맵→유즈케이스→시퀀스 진화 |
| d | [`conventions/stack.md`](conventions/stack.md) | 언어/컴파일러/패키지 매니저 사전 점검·자율 업데이트 |
| e | [`conventions/build-and-config.md`](conventions/build-and-config.md) | sh+bat·TOML·docs/·폐기·병렬·메모리 |
| f | [`conventions/contracts.md`](conventions/contracts.md) | frontmatter·재진입·핑거프린트 체인 |
| g | [`conventions/models.md`](conventions/models.md) | 역할별 Opus/Sonnet/Haiku 매핑 |
| h | [`conventions/competition.md`](conventions/competition.md) | 격리 병렬 경쟁 + 자동 resolve |
| i | [`conventions/autonomy.md`](conventions/autonomy.md) | 페이즈 04 외 자율 결정 |
| j | [`conventions/lessons.md`](conventions/lessons.md) | 정체 감지·레슨팩·통째 재작성 |
| k | [`conventions/spec-catalog.md`](conventions/spec-catalog.md) | 도메인별 NFR 자동 카탈로그 |
| l | [`conventions/resources.md`](conventions/resources.md) | 리소스 기반 임계 + 천정 자동 조정 |
| m | [`conventions/checkpoints.md`](conventions/checkpoints.md) | 체크포인트·멀티버스 (닥터 스트레인지) |
| n | [`conventions/test-invariants.md`](conventions/test-invariants.md) | 불변 조건·Phase V 유효성 |
| o | [`conventions/dacapo.md`](conventions/dacapo.md) | Da Capo 루프·AIDE × LLM Wiki 결합 |
| p | [`conventions/fragmentation.md`](conventions/fragmentation.md) | 파편화 우선·단일 헤비 스킬 금지 |
| q | [`conventions/grades.md`](conventions/grades.md) | 그레이드 (G1~G5) — 내부 모듈레이션만 |
| r | [`conventions/sub-agents.md`](conventions/sub-agents.md) | 서브에이전트 재귀 분해 |
| s | [`conventions/indexing.md`](conventions/indexing.md) | 산출물 = DB·비직렬성 트리 인덱싱 |
| t | [`conventions/resume.md`](conventions/resume.md) | 리줌·state.json·라이브 진행 추적 |
| u | [`conventions/plan-tree.md`](conventions/plan-tree.md) | **AIDE 플랜 트리** — N 우주 격리 + 토너먼트 |
| v | [`conventions/runtime-prereq.md`](conventions/runtime-prereq.md) | Q-D9 + 게이트 7 (실 부팅 검증) |

### v0.9.6~v0.9.16 신규 (w~au)

| ID | 컨벤션 | 핵심 | v |
|:-:|---|---|:-:|
| w | [`conventions/nfr-derivation.md`](conventions/nfr-derivation.md) | prompt 형용사 → NFR + derived 게이트 | 0.9.6 |
| x | [`conventions/premortem-friction.md`](conventions/premortem-friction.md) | 콜드리뷰 한 번 더 고민 + 미래 회고 | 0.9.7 |
| y | [`conventions/sprint-regression-loop.md`](conventions/sprint-regression-loop.md) | self-polishing 임계 도달까지 반복 | 0.9.8 |
| z | [`conventions/parallel-cold-review.md`](conventions/parallel-cold-review.md) | N framing fan-out 페이즈 03 다양성 | 0.9.8 |
| aa | [`conventions/mindmap-centrality.md`](conventions/mindmap-centrality.md) | canonical concept graph 모든 페이즈 backbone | 0.9.9 |
| ab | [`conventions/aide-tree-symmetry.md`](conventions/aide-tree-symmetry.md) | universe candidate sequenceDiagram 강제 | 0.9.10 |
| ac | [`conventions/aide-tree-multi-phase.md`](conventions/aide-tree-multi-phase.md) | 02/05/08/11/13 페이즈 multiverse 확장 | 0.9.10 |
| ad | [`conventions/tournament-blind-rerun.md`](conventions/tournament-blind-rerun.md) | 임계 미달 시 anonymize previous winner 재경합 | 0.9.10 |
| ae | [`conventions/interface-first-parallel-impl.md`](conventions/interface-first-parallel-impl.md) | 페이즈 06 인터페이스 + 페이즈 08 fan-out | 0.9.11 |
| af | [`conventions/analytical-bound-cross-validation.md`](conventions/analytical-bound-cross-validation.md) | closed-form 상한 vs simulated | 0.9.12 |
| ag | [`conventions/multiverse-impl-fan-out.md`](conventions/multiverse-impl-fan-out.md) | universe N 모두 실 코드 의무 | 0.9.12 |
| ah | [`conventions/budget-aware-fallback.md`](conventions/budget-aware-fallback.md) | silent fallback 금지, `fallback_reason` 명시 | 0.9.12 |
| ai | [`conventions/deep-semantic-intent.md`](conventions/deep-semantic-intent.md) | adjective + noun → implied framing | 0.9.13 |
| aj | [`conventions/domain-research-stacking.md`](conventions/domain-research-stacking.md) + [`conventions/domain-adapters/`](conventions/domain-adapters/) | 마인드맵 noun → domain adapter stack | 0.9.13 |
| ak | [`conventions/mindmap-quality-gardening.md`](conventions/mindmap-quality-gardening.md) | Mermaid + 4 axis × ≥3 sub-node + ≥15 노드 | 0.9.13 |
| al | [`conventions/ensemble-synthesis-default.md`](conventions/ensemble-synthesis-default.md) | G4+ tournament 결과 algorithmic union default | 0.9.13 |
| am | [`conventions/deliverable-hurdle-supremacy.md`](conventions/deliverable-hurdle-supremacy.md) | **Layer 3 결과물 허들** — 메모리/컨벤션 override 불가 | 0.9.14 |
| an | [`conventions/budget-saturation-loop.md`](conventions/budget-saturation-loop.md) | sprint loop budget 끝까지 사용 + content depth lesson | 0.9.15 |
| ao | [`conventions/score-rubric-objectivity.md`](conventions/score-rubric-objectivity.md) | strict checklist self-rating, evidence 1:1 | 0.9.15 |
| ap | [`conventions/convention-traceability.md`](conventions/convention-traceability.md) | 산출물 frontmatter `applied_conventions` 의무 | 0.9.16 |
| aq | [`conventions/sprint-score-delta-tracking.md`](conventions/sprint-score-delta-tracking.md) | sprint NN+1 점수 변화 + lesson type honesty | 0.9.16 |
| ar | [`conventions/evidence-driven-sprint-planning.md`](conventions/evidence-driven-sprint-planning.md) | `evidence_missing` → 다음 sprint lesson 자동 매핑 | 0.9.16 |
| as | [`conventions/cross-universe-lesson-distillation.md`](conventions/cross-universe-lesson-distillation.md) | 패배 universe 약점 우승 본문 흡수 (차이집합) | 0.9.16 |
| at | [`conventions/regression-derived-lint-rule-autogen.md`](conventions/regression-derived-lint-rule-autogen.md) | 회귀 정정 후 self_lint 룰 자동 신규 (우로보로스) | 0.9.16 |
| au | [`conventions/polyglot-code-quality.md`](conventions/polyglot-code-quality.md) | 9 언어 표준 도구 + 6 언어 무관 메트릭 | 0.9.16 |
| av | [`conventions/anti-patterns.md`](conventions/anti-patterns.md) | A1~A10 공통 안티 패턴 | 0.9.16 |
| aw | [`conventions/intent-completeness.md`](conventions/intent-completeness.md) | 페이즈 01 §k 9 sub | 0.9.18 |
| ax | [`conventions/process-flow-coherence.md`](conventions/process-flow-coherence.md) | 페이즈 09 게이트 8 cycle | 0.9.18 |
| ay | [`conventions/domain-failure-patterns.md`](conventions/domain-failure-patterns.md) | 페이즈 09 게이트 9 failure | 0.9.18 |
| az | [`conventions/decision-support-framing.md`](conventions/decision-support-framing.md) | 페이즈 14 Q 답 framing | 0.9.18 |

### v0.9.19 신규 (ba~bd) — sprint-13 깊이 강화 + 발현 빈도 격상

| ID | 컨벤션 | 핵심 | v |
|:-:|---|---|:-:|
| ba | [`conventions/mindmap-richness-default.md`](conventions/mindmap-richness-default.md) | 마인드맵 A 등급 default 격상 (≥25 노드 / 4 axis × ≥4 sub / sub-sub-sub 1+) + intent-extractor templated stub + B fallback with lesson | 0.9.19 |
| bb | [`conventions/per-module-diagram-fan-out.md`](conventions/per-module-diagram-fan-out.md) | use-case / sequence 모듈별 분할 default — 모듈 ≥ 4 OR consumer-producer 페어 ≥ 6 트리거 + C-PMDF self_lint | 0.9.19 |
| bc | [`conventions/multiverse-width-default-bump.md`](conventions/multiverse-width-default-bump.md) | 폭 default 격상 G2=2 / G3=5 / G4=7 / G5=9 + 옵션 default G3=10/G4=12/G5=16 + budget profile cap 동기 + fallback_reason 의무 | 0.9.19 |
| bd | [`conventions/intent-plan-impl-sprint-trinity.md`](conventions/intent-plan-impl-sprint-trinity.md) | sprint loop 3 axis (intent / plan / impl) × ≥ 2 회 + budget 분배 default (20/30/50%) + early stop violation 강화 + C-IPI self_lint | 0.9.19 |

### v0.9.20 신규 (be~bk) — sprint-14 cold evaluator feedback (94→97 plateau 돌파)

| ID | 컨벤션 | 핵심 | v |
|:-:|---|---|:-:|
| be | [`conventions/grader-in-sprint.md`](conventions/grader-in-sprint.md) | sprint stop = `auto_pass AND shadow_pass AND axis_pass AND budget_pass` (4 conjunction). Zero-context shadow grader sprint 마다 1 회 호출 + lesson source 격상 + C-GIS self_lint | 0.9.20 |
| bf | [`conventions/contested-decision-multiverse.md`](conventions/contested-decision-multiverse.md) | tournament axis = paradigm → contested decisions (prompt explicit / cold-read implicit / critique potential) + per-universe code spike (≤50 LOC) + decision_coverage 채점 차원 0.20 가중 + C-CDM self_lint | 0.9.20 |
| bg | [`conventions/directional-simplification.md`](conventions/directional-simplification.md) | 페이즈 05 critique 의 simplification 표 의무 (direction ↑/↓/? + magnitude ±% + reason 1 줄) + frontmatter sync + 게이트 1 강화 + C-DS self_lint | 0.9.20 |
| bh | [`conventions/commentary-policy.md`](conventions/commentary-policy.md) | 페이즈 04 Q-D-AUDIENCE flag (internal-self / external-reviewer / mixed) → 페이즈 08 implementer 의 주석 density 매트릭스 swap. CLAUDE.md global default 컨텍스트 충돌 명시 정정 + C-CP self_lint | 0.9.20 |
| bi | [`conventions/measurement-contract.md`](conventions/measurement-contract.md) | 페이즈 06 plan 의 metric method 의무 (sample / accumulate / reconstruct + 정당화) + frontmatter sync + 게이트 6 강화 + 페이즈 11 plan_method vs impl 분류 입력 + C-MC self_lint | 0.9.20 |
| bj | [`conventions/rubric-driven-doc-skeleton.md`](conventions/rubric-driven-doc-skeleton.md) | 페이즈 04 stack-lock 직후 RubricAdapter (yaml/markdown/openapi 3 built-in) → 빈 헤더 skeleton (rubric line 인용) + fallback generic ToC + C-RDS self_lint | 0.9.20 |
| bk | [`conventions/rubric-targeted-quality-gates.md`](conventions/rubric-targeted-quality-gates.md) | 페이즈 09 RTG-* gates (rubric bullet → yes/no 체크) + bj 와 같은 adapter 공유 + 종합 판정 (proceed / remediate / halt) + fail RTG → sprint NN+1 lesson 매핑 + C-RTG self_lint | 0.9.20 |

### v0.9.21 신규 (bl) — sprint-15 intra-phase Da Capo Loop

| ID | 컨벤션 | 핵심 | v |
|:-:|---|---|:-:|
| bl | [`conventions/intra-phase-dacapo-loop.md`](conventions/intra-phase-dacapo-loop.md) | phase 06 (plan) + phase 08 (impl) 안의 통합 의사코드 loop — multiverse fan-out → tournament → shadow grade (be) → 4 conjunction AND threshold → 미달 시 lesson 적용 + 처음 (Step A) 으로 돌아감 (다카포). G3+ default 활성. ad v0.9.10 + be v0.9.20 + bd v0.9.19 + ar v0.9.16 통합. C-DCL-WIN-THRESHOLD / C-DCL-RERUN-LOG / C-DCL-ANON self_lint 3 룰. 06/08 phase hook 에 *그대로 박힌 의사코드*. cold session winner=0.853 재경합 0 회 회귀 직접 정정. | 0.9.21 |

### v0.9.22 신규 (bm~bq) — sprint-16 의사코드 → runtime guard 변환

bl v0.9.21 의 의사코드를 *runtime guard* 로 격상 + 가시화 layer. 외부 cold session `2026-05-05__001_mine_g4` winner=0.892 (G4 임계 미달) + rerun=0 + fallback="" 회귀 직접 정정.

| ID | 컨벤션 | 핵심 | v |
|:-:|---|---|:-:|
| bm | [`conventions/dacapo-enforcement.md`](conventions/dacapo-enforcement.md) | phase 06/08 → 07/09 핸드오프 6 조건 의무 게이트 (frontmatter 검증 + force_re_enter_phase). HARD-RULE 9.p. 의사코드 (bl) = agent guide / 본 룰 = orchestrator runtime guard. C-DCL-GATE self_lint. | 0.9.22 |
| bn | [`conventions/dacapo-frontmatter-schema.md`](conventions/dacapo-frontmatter-schema.md) | tournament-NN.md / shadow-grade-NN.json / dacapo-rerun-NN.md 의무 frontmatter 필드 정의 + cross-validation 5 룰 (산술 + 파일시스템). HARD-RULE 9.q. C-DCL-FRONTMATTER self_lint. | 0.9.22 |
| bo | [`conventions/shadow-grader-zero-context.md`](conventions/shadow-grader-zero-context.md) | Step C shadow grader 무결성 5 룰 — prior_context_token_count: 0, agent_call_id 유니크, loaded_artifacts ≥ 1, generic rubric, 점수 차이 ≥ 3pt 권장. HARD-RULE 9.r. cold session 92 vs 89.2 = 2.8pt 복사 의심 자동 detect. C-DCL-SHADOW-CONTEXT self_lint. | 0.9.22 |
| bp | [`conventions/dacapo-skip-sentinel.md`](conventions/dacapo-skip-sentinel.md) | 3 sentinel 자동 회귀 — A frontmatter 모순 / B 디렉터리 카운트 (universe / sprint skip) / C 로그 패턴 ("Winner clear" / "skip dacapo" / "0회 충분" / "단일 탑" 등). HARD-RULE 9.s. force_re_enter_phase + intent/00-violation.md + violation count ≥ 3 만 ack. C-DCL-SENTINEL self_lint. | 0.9.22 |
| bq | [`conventions/dacapo-flow-trace.md`](conventions/dacapo-flow-trace.md) | plan/dacapo-flow.md / impl/dacapo-flow.md 단일 마크다운 누적 갱신 — Mermaid flowchart (rerun 별 subgraph + universe 노드 + Step A~G 엣지 + ★ SENTINEL_REGRESSION 노드) + timeline 표. HARD-RULE 9.t. 5 산출물 cross-reference 0 — 한 파일에서 흐름 + 사유 즉시 재구성. C-DCL-FLOW-LOG self_lint. | 0.9.22 |
| br | [`conventions/phase-lineage-viewer.md`](conventions/phase-lineage-viewer.md) | 프로젝트 루트 `lineage.md` 단일 마크다운 — phase 00~14 전체 흐름 + universe 분기 + dacapo loop 요약 + sentinel 위반 이벤트 + fingerprint chain 표 + 페이즈 04 답안 매핑. bq 가 *per-phase*, 본 컨벤션이 *project-wide* 상위 view. HARD-RULE 9.u. C-PLV self_lint. | 0.9.22 |

### v0.9.22 phase 2 신규 (bs~bx) — sprint-16 7 차원 만점 push (91→100)

cold session 91/100 → 100/100. v0.9.21 대비 6 차원 갭 정정 (Traceability 5/5 만점 유지).

| ID | 컨벤션 | 차원 | gap |
|:-:|---|---|:-:|
| bs | [`conventions/domain-model-completeness.md`](conventions/domain-model-completeness.md) | Conceptual modelling — entity / state / transition / invariant / boundary 5 차원 + intent §m | -2 |
| bt | [`conventions/data-structure-invariants.md`](conventions/data-structure-invariants.md) | Data & topology — Invariants/Topology/Access/Bounds 4 항목 docstring + plan 표 의무 | -1 |
| bu | [`conventions/simulation-physical-invariants.md`](conventions/simulation-physical-invariants.md) | Sim correctness — 5 invariant 런타임 assert (mass/resource/time/queue/deadlock) + bs §D4 1:1 매핑 | -2 |
| bv | [`conventions/experimental-control-protocol.md`](conventions/experimental-control-protocol.md) | Experimental design — IV/DV/CV/N/seed 5 항목 의무 + N≥30 + reproducibility | -1 |
| bw | [`conventions/results-decision-mapping.md`](conventions/results-decision-mapping.md) | Results & interpretation — 결과 → 결정 1:1 매핑 (owner/deadline) + negative finding 도 결정 의무 | -2 |
| bx | [`conventions/idiomatic-code-quality.md`](conventions/idiomatic-code-quality.md) | Code quality — naming / preferred construct / stdlib first / readability 4 차원 (au 6 메트릭 위) | -1 |

self_lint C-DMC / C-DSI / C-SPI / C-ECP / C-RDM / C-ICQ 6 룰. HARD-RULE 9.v~aa.

### sprint-19 신규 (ce~cj) — Da Capo runtime polishing + plan/impl richness + 2nd refresh cycle (90/100 plateau 돌파)

cold session 003 (v0.9.23) 90/100 plateau 의 5 갭 정정. **mandatory ≥ 1 rerun** (점수 임계 도달해도 polishing 강제) + plan tournament 6-dim weighted (1-5 coarse reject) + canonical 산출물 stub 금지 + phase 08 multiverse 강제 + post-critique 2nd refresh cycle + cross-phase shared context.

| ID | 컨벤션 | 핵심 | v |
|:-:|---|---|:-:|
| ce | [`conventions/dacapo-mandatory-rerun.md`](conventions/dacapo-mandatory-rerun.md) | winner score 임계 도달해도 무조건 ≥ 1 rerun (Step D AND threshold pass 후에도 mandatory_first_rerun_satisfied: true 의무) — high score promote 우회 차단. C-DCMR self_lint. | 0.9.24 |
| cf | [`conventions/plan-tournament-scoring-strict.md`](conventions/plan-tournament-scoring-strict.md) | tournament.md frontmatter 6-dim weighted (be grader-in-sprint 정합 — feasibility/invariant/decision_coverage/modular/determinism/measurement) 의무. 1-5 cold-read coarse 자동 reject. C-PTSS self_lint. | 0.9.24 |
| cg | [`conventions/canonical-not-stub.md`](conventions/canonical-not-stub.md) | canonical 06-plan.md / 08-impl-log.md / 14-handoff.md 가 ≥ winner universe 본문 80% (inline mode) 또는 shared schema + integration decisions + cross-phase reference 3 섹션 (shared-schema mode) 의무. 위임 stub 금지. C-CNS self_lint. | 0.9.24 |
| ch | [`conventions/impl-multiverse-strict.md`](conventions/impl-multiverse-strict.md) | phase 08 G4+ → impl/candidates/universe-N/ + impl/tournament-impl-NN.md + impl/dacapo-flow.md + 5 sub-phase TDD 본문 (skip 자백 regex reject) 7 조건 게이트. ag + bl phase 08 부분의 runtime gate. C-IMS self_lint. | 0.9.24 |
| ci | [`conventions/intent-refresh-post-critique.md`](conventions/intent-refresh-post-critique.md) | phase 05 critique 후 ~ phase 06 plan 진입 전 2nd intent refresh (사용자 ack 없음, 자율). 6 신규 산출물 (01-{1..4}-intent.v2.md + 04-refreshed.md + 05-refreshed.md). by sprint-17 의 1st refresh 와 cascade. C-IRPC self_lint. | 0.9.24 |
| cj | [`conventions/cross-phase-shared-context.md`](conventions/cross-phase-shared-context.md) | shared 정보 (entity catalog / interface / invariants / TODO DAG / decisions / NFR) 단일 위치 + 양쪽 phase 산출물 인용 의무. asof_fingerprint 의무 (drift 차단). 사용자 메타 원칙 직접 정합. C-CPSC self_lint. | 0.9.24 |

self_lint C-DCMR / C-PTSS / C-CNS / C-IMS / C-IRPC / C-CPSC 6 룰. HARD-RULE 9.gg~ll. **sprint-19 = sprint-15~18 enforcement 의 마지막 빈 구멍 (high-score promote bypass + canonical stub + impl multiverse skip + critique→plan stale-input + 정보 isolation) 동시 닫음.**

### sprint-18 신규 (bz~cd) — runtime enforcement 5 (90→100 cap 풀기, 도메인-무관 한정)

cold session 003 grader 의 89/100 / "Outstanding" 지적 5 차원 갭을 *runtime 게이트* 로 닫음. **도메인 종속 (e.g., DES sim warmup) 개선안은 본 sprint 에서 의도적 제외 — 본 하네스는 벤치마크를 어뷰징하지 않음 (case-specific 룰 금지).**

| ID | 컨벤션 | 차원 | gap |
|:-:|---|---|:-:|
| bz | [`conventions/readme-numbers-from-summary.md`](conventions/readme-numbers-from-summary.md) | Results & interpretation — doc 숫자 vs measurement artifact ±0.01% 일치 (page 09 grep + drift detect) | -3 |
| ca | [`conventions/reproducibility-doublecheck.md`](conventions/reproducibility-doublecheck.md) | Reproducibility — entry script 2회 실행 + summary.json sha256 byte-equal (PYTHONHASHSEED 등 결정성 회귀 차단) | (root with bz) |
| cb | [`conventions/magic-number-traceability.md`](conventions/magic-number-traceability.md) | Conceptual modelling — 코드 literal → A_i 가정 또는 데이터 파일 출처 1:1 매핑 | -2 |
| cc | [`conventions/dead-code-zero.md`](conventions/dead-code-zero.md) | Sim correctness — 언어별 dead-code analyzer (ruff F,ARG,SIM / vulture / 동등) 위반 0 강제 | -2 |
| cd | [`conventions/submission-portability.md`](conventions/submission-portability.md) | Code quality — entry script `--data-dir` CLI flag + `DATA_DIR` env var fallback 의무 (path 하드코딩 차단) | -1 |

self_lint C-RNFS / C-RDC / C-MNT / C-DCZ / C-SPB 5 룰. HARD-RULE 9.bb~ff. **bs/bt/bu/bv/bw/bx (HARD-RULE 9.v~aa) 가 *내용 의무* layer, 본 sprint 가 *runtime 검증* layer — 두 layer 합쳐져야 enforcement 닫힘.**

### sprint-17 신규 (by) — orchestrator 슬림화 + 페이즈 04+ refresh + cap 측정-only

orchestrator SKILL.md 287 → 121 lines (-58%) — HARD-RULE 9.a~aa prose 를 conventions/ 단일 source 로 분리, 페이즈별 lookup index 만 entry skill 에 박힘. cold session 두 회귀 동시 정정: (1) 다카포 cap forward time projection 우회 (`step_e_cap_reached: false + rerun_count: 0 + budget_used_total: 0.20` 인데 promote) → 측정 only + min loop attempt 강제 / (2) HARD-RULE 9.a OR 절 (interface ≥ 3 만으로 sequence diagram skip 가능) → AND 셋 다 의무 / (3) 페이즈 04 → 05 직진으로 refresh 부재 → 04+ phase refresh 4 universe + 01-additional 의무.

| ID | 컨벤션 | 핵심 | v |
|:-:|---|---|:-:|
| by | [`conventions/intent-refresh-post-interview.md`](conventions/intent-refresh-post-interview.md) | 페이즈 04 → 05 사이 의도 refresh 4 framing universe (domain / constraint / risk / outcome) + 01-additional.md (인터뷰가 새로 드러낸 요구·비목표·제약). 페이즈 05 critique 의 입력 = refresh 4 + 01-additional (stale 01-intent.md 직접 입력 폐기). C-IRPI-COUNT/FRAMING/CHAIN/CONSUMED/CONTRADICTION 5 self_lint. | 0.9.23 |

추가 컨벤션 본문 갱신 (sprint-17, ID 변경 없음):
- [`conventions/dacapo-enforcement.md`](conventions/dacapo-enforcement.md) (bm) — 시간 cap = 측정 only (LLM forward projection 자동 reject regex). min loop attempt (rerun ≥ 1) 강제. self_lint C-DCL-NO-FORWARD-PROJECT / C-DCL-MIN-LOOP-ATTEMPT / C-DCL-CAP-MEASURED 3 룰 신규.
- [`conventions/diagrams.md`](conventions/diagrams.md) (c) — HARD-RULE 9.a OR → AND. sequence + usecase + interface 셋 다 의무. self_lint C-DIAG-AND-COVERAGE 신규.

## 산출물 트리

```
.ShipofTheseus/<프로젝트명>/
├── timing/start.json
├── naming/{00-candidates.md, 00-naming.md}
├── intent/{01-intent.md, 02-..05-decisions.md, 04-stack.md, 04-verification.md, 04-runtime-prereq.md}
├── plan/{06-plan.md, 07-plan-review.md, tournament.md, candidates/universe-N/...}  # G3+ AIDE 트리
├── impl/08-impl-log.md
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, unit.json, e2e.json}
├── webview/                     # 페이즈 12 — theseus-view (스킬 진행 추적, bun + hono + react)
├── interactive-viewer/          # 페이즈 13 — 프로젝트 output observability (도메인별 dashboard)
└── handoff/14-handoff.md
```

## 페이즈 (15)

각 페이즈 산출물은 [`conventions/contracts.md`](conventions/contracts.md) frontmatter (skill_name / skill_version / phase / project_id / fingerprint / prev_fingerprint / produced_at) 포함. 각 페이즈 문서가 자기 페이즈에 필요한 컨벤션 + 서브에이전트를 인용 (본 표는 페이즈 문서 위치 + 모델 인덱스만).

| # | 페이즈 | 모델 | 페이즈 문서 | 산출 |
|:-:|---|:-:|---|---|
| 00 | 프로젝트/모듈 명명 (G3+) | Haiku | [`phases/00-naming.md`](phases/00-naming.md) | `naming/` |
| 01 | 의도 + 마인드맵 | **Opus** | [`phases/01-intent.md`](phases/01-intent.md) | `intent/01-intent.md` |
| 02 | 의도 리뷰 | Sonnet | [`phases/02-document.md`](phases/02-document.md) | `intent/02-review.md` |
| 03 | 콜드 재이해 | Sonnet | [`phases/03-independent-comprehension.md`](phases/03-independent-comprehension.md) | `intent/03-comprehension.md` |
| 04 | 사용자 질의 + Q-D + Q-D-MODE | Sonnet | [`phases/04-clarify.md`](phases/04-clarify.md) | `intent/04-*.md` |
| 05 | 비평 | **Opus** | [`phases/05-critique.md`](phases/05-critique.md) | `intent/05-*.md` |
| 06 | 계획 + AIDE 트리 | **Opus** | [`phases/06-plan.md`](phases/06-plan.md) | `plan/{06-plan,tournament,candidates/}` |
| 07 | 계획 재이해 | Sonnet | [`phases/07-plan-recursion.md`](phases/07-plan-recursion.md) | `plan/07-review.md` |
| 08 | 구현 (5 서브 TDD: α/β/γ/δ/ε) | Sonnet/Opus | [`phases/08-implement.md`](phases/08-implement.md) | `impl/` |
| 09 | 9 게이트 + Gate 0 허들 | Sonnet | [`phases/09-quality-gates.md`](phases/09-quality-gates.md) | `quality/09-quality-gate.md` |
| 10 | 무한 스프린트 (임계 0.999) | Haiku | [`phases/10-test-loop.md`](phases/10-test-loop.md) | `sprints/NN/` |
| 11 | 회귀 바이섹트 | **Opus** | [`phases/11-regression-bisect.md`](phases/11-regression-bisect.md) | `sprints/NN/bisect` |
| 12 | theseus-view (스킬 추적) | Sonnet | [`phases/12-webview-assembly.md`](phases/12-webview-assembly.md) | `webview/` |
| 13 | interactive-viewer (output observability) | Sonnet | [`phases/13-interactive-viewer.md`](phases/13-interactive-viewer.md) | `interactive-viewer/` |
| 14 | 핸드오프 | — | [`phases/14-handoff.md`](phases/14-handoff.md) | `handoff/14-handoff.md` |

## 단계별 진입 (재진입)

페이즈 N 산출물 (frontmatter + fingerprint chain valid, semver major 호환) 을 들고 오면 페이즈 N+1 부터 진입. 호환 안 되면 거부 + 사용자 객관식 (재실행 / 무시 / 디버깅). 자세히: [`conventions/contracts.md`](conventions/contracts.md).

## 자율성 우선

페이즈 04 외 사용자 인터럽트 절대 없음. 모든 결정 (경쟁 머지 / 회귀 권고 / 스택 업데이트) 은 산출물 frontmatter + 본문 기록되어 사후 리뷰 가능. 자세히: [`conventions/autonomy.md`](conventions/autonomy.md).

<!-- HARD-RULE: 본 절의 a-~l- 항목은 본 하네스 호출 시 *예외 없이* 적용. 위반은 즉시 게이트 fail. -->

## 하드 룰 (요약)

a- 페이즈 생략 불가. 불필요해 보여도 실행하고 "발견 없음" 으로 기록.
b- 페이즈 03/07 은 *fresh* `Agent` 호출 — 컨텍스트 공유 금지.
c- 페이즈 04 는 *유일한* 사용자 인터럽트 지점. 사전 위임 카탈로그(Q-D1~D6) 답 누락 시 페이즈 05 진입 불가. **페이즈 05~13 동안 사용자 인터럽트 절대 없음** — 모든 ack 는 페이즈 04 답 자동 매핑 ([`conventions/autonomy.md`](conventions/autonomy.md)).
d- **임계 점수 0.999** — 임계 미달 시 무한 스프린트, 캡 없음. 회귀 시에만 사용자 ack.
e- **DIP 가 SOLID 중 최우선** — 위반 단독 hard cap 0.6.
e-1 **깨고 다시 빚기 트리거 = 모든 깊은 품질 위반** — DIP 위반만이 아니라 1- 코드 오류 누적 2- 기획-구현 갭 (스펙 누락) 3- 성능/NFR 미달 4- 의도 표류 5- 정체/회귀 누적 중 *어느 차원* 이라도 깊이가 임계를 넘으면 부분 수정 금지 → 페이즈 06 부터 통째 재빚기 (`re-architect`). 차원별 트리거·매핑은 [`conventions/lessons.md`](conventions/lessons.md) + [`conventions/checkpoints.md`](conventions/checkpoints.md).
f- 백엔드 기본 Go, FE 기본 bun + React + TS.
g- 모든 모듈은 sh + bat 스크립트, TOML 설정 + `.example` 동행, `docs/` 폴더.
h- 수정·리팩터링 시 기존 코드 폐기 우선. 라이브 전 중간 산출물 보존.
i- 병렬 서브에이전트 환영 — RAM 50% / 동시 E2E 2개 / 같은 파일 직렬 가드.
i-1 페이즈 06/08/11 에서 명확한 단일안이 보이지 않으면 **2~3 후보 격리 병렬 경쟁** → 점수 비교 → 우승자 또는 머지 ([`conventions/competition.md`](conventions/competition.md)). LLM 비결정성을 분기·경쟁·합병으로 정공법 극복. **resolve 는 점수 차/차원별 분석으로 자율 결정** — 사용자 ack 는 비즈니스 함의가 명시된 경쟁만.
i-2 **자율성 우선** — 페이즈 04 (초기 사용자 질의) 이외의 모든 결정은 자율 진행 ([`conventions/autonomy.md`](conventions/autonomy.md)). 모든 자율 결정은 산출물 frontmatter + 본문 기록 → 사후 리뷰 가능.
j- 사용자 진행 보고에 누적 경과 시간 1줄 항상 포함.
k- **모든 산출물에 frontmatter (skill_name, skill_version, phase, project_id, fingerprint, prev_fingerprint, produced_at) 필수.**
l- 페이즈 산출 파일을 지휘자가 손대지 않는다 — 잘못되면 페이즈 재실행.

## 호출 그레이드 — [`conventions/grades.md`](conventions/grades.md) 의 허들

**호출 직후 첫 동작 = `scoring/grade_assess.py` 자동 추정 + 페이즈 04 의 Q-G1 객관식 확정.** 그레이드별 페이즈/컨벤션 활성화로 단순 작업 over-engineering 차단.

| Grade | 호출 시점 | 본 하네스 동작 |
| ----- | -------- | ------------ |
| **Grade 1** Trivial | 한 줄 수정 / 리네임 / typo / throwaway | mini_harness_tbd (모듈레이션 정의 진행 중) |
| **Grade 2** Simple | 단일 모듈 작은 기능 (~100 LOC) | 미니 (5 페이즈 / 7 컨벤션 / 임계 0.95) |
| **Grade 3** Standard | 다중 모듈 단일 사이드 | 12 페이즈 / 12 컨벤션 / 임계 0.97 |
| **Grade 4** Complex | FE+BE / 새 도메인 / SOLID 리팩터 (default) | 14 페이즈 풀 / 26 컨벤션 / 임계 0.999 |
| **Grade 5** Mission Critical | 결제 / 금융 / 안전 시스템 | 14 풀 + 빡빡 모드 / 임계 0.99999 |

## 에이전트 (18)

페이즈 문서가 자기 페이즈에 필요한 에이전트를 인용 — 본 카탈로그는 색인.

[`agents/clarifier.md`](agents/clarifier.md) · [`agents/critic.md`](agents/critic.md) · [`agents/doc-reviewer.md`](agents/doc-reviewer.md) · [`agents/implementer.md`](agents/implementer.md) · [`agents/independent-comprehender.md`](agents/independent-comprehender.md) · [`agents/intent-extractor.md`](agents/intent-extractor.md) · [`agents/interactive-viewer-builder.md`](agents/interactive-viewer-builder.md) · [`agents/plan-reviewer.md`](agents/plan-reviewer.md) · [`agents/planner.md`](agents/planner.md) · [`agents/project-namer.md`](agents/project-namer.md) · [`agents/quality-gate.md`](agents/quality-gate.md) · [`agents/refactorer.md`](agents/refactorer.md) · [`agents/regression-analyst.md`](agents/regression-analyst.md) · [`agents/runtime-detector.md`](agents/runtime-detector.md) · [`agents/test-architect.md`](agents/test-architect.md) · [`agents/test-writer.md`](agents/test-writer.md) · [`agents/tester.md`](agents/tester.md) · [`agents/webview-builder.md`](agents/webview-builder.md)

## 안티 패턴 통합 카탈로그

공통 안티 패턴 (A1~A10): [`conventions/anti-patterns.md`](conventions/anti-patterns.md). 페이즈별 *고유* 안티 패턴은 [`phases/`](phases/) 본문에 잔존. self_lint C40 가 통합 정합 검증.
