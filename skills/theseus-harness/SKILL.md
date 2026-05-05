---
name: theseus-harness
version: 0.9.21
description: 재귀 멀티 에이전트 코딩 하네스 — 15 페이즈 / 63 컨벤션 / 18 에이전트. AIDE 멀티버스 (G3=5/G4=7/G5=9 폭 default) + 발현 검증 + Layer 3 결과물 허들 + grade_assess v2 + sprint-14 v0.9.20 (grader-in-sprint dual-objective AND / contested decisions axis / directional simplification / commentary policy / measurement contract / rubric skeleton + targeted gates) + sprint-15 v0.9.21 (intra-phase Da Capo Loop — phase 06/08 의사코드 hook 으로 multiverse + sprint retry 통합).
---

# 테세우스 하네스

## 한 줄 요약
**한 요구를 처음 의도한 타이틀로 끝까지 부를 자격을 만들기 위한 재귀 코딩 하네스.** 당신(메인 에이전트)은 *지휘자* — 직접 작업하지 않고, 페이즈마다 정해진 서브 에이전트를 띄워 산출물을 받아 다음 페이즈로 넘긴다. 본 SKILL.md 는 *인덱스* 다 — 상세는 컨벤션·페이즈·에이전트 문서로 위임. 설계 철학·도자기 장인·AIDE 멀티버스: [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md).

## HARD-RULE — 첫 동작 + 페이즈 완주 강제

본 스킬 호출 직후 *첫 동작* = `timing/start.json` + 페이즈 00 (G3+) 또는 01 (G2) 산출물 작성. 직접 코드 작성 / `_tools/build_artifacts.py` 등 retroactive frontmatter generator / out-of-sandbox harness emulator / 페이즈 04 생략은 모두 위반 → `intent/00-violation.md` 기록 + 정상 재시작. **종료 시 그레이드별 의무 산출물 (G2: 11개 / G3: 30+ / G4-5: 풀) 모두 박혀야 정상 완주** — 페이즈 06 까지만 만들고 자발적 조기 종료 금지. **`plan/06-plan.md` 본문 의무**: 파일 경로 ≥ 5 / Mermaid 시퀀스 ≥ 1 또는 인터페이스 정의 ≥ 3 / TODO DAG. **`impl/08-impl-log.md` 본문 의무**: TODO ID 매핑 ≥ 3 / 모듈명 명시 / 인터페이스 노출. 풀 룰: [`../theseus-orchestrator/SKILL.md`](../theseus-orchestrator/SKILL.md) §HARD-RULE 8/9.

## 컨벤션 카탈로그 (63)

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
