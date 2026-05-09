# Convention Router — 단일 진실 원천

**93 컨벤션 router.** 페이즈 본문 cross-ref / [`grades.md`](grades.md) 매트릭스 / 컨벤션 frontmatter `applies-to` 모두 본 표 참조. drift 시 self_lint C-IDX-1 fail. sprint-34 / v0.9.39 신규 4 (phase-state-machine, subagent-trigger, regression-tdd-gate, intent-optional-disambiguation) + phase-lineage-viewer 확장 (gantt + 모든 그레이드).

본 표는 *현재* 활성 컨벤션의 라우팅 정보 (sprint/version history → [`../../../CHANGELOG.md`](../../../CHANGELOG.md) 단일 위치).

## 컬럼

- **id**: 컨벤션 파일명 (`<id>.md`)
- **cat**: category — {core / interview / mindmap / domain / planning / multiverse / tournament / impl / quality / sprint / meta}
- **phases**: applies-to-phases — phase 번호 list 또는 `[all]`
- **grades**: applies-to-grades — `[G2..G5]` subset 또는 `[all]`
- **trigger**: 활성 조건 — `always` 또는 specific

## Router

| id | cat | phases | grades | trigger |
|---|---|---|---|---|
| aide-tree | multiverse | [02,05,06,08,11,13] | [G3,G4,G5] | always (multi-phase) / universe candidate (symmetry) |
| analytical-bound-cross-validation | quality | [09,11] | [all] | analytical bound 가능 |
| anti-patterns | meta | [all] | [all] | always |
| autonomy | core | [all] | [all] | always |
| budget-aware-fallback | sprint | [10] | [G3,G4,G5] | budget tight |
| budget-saturation-loop | sprint | [10] | [G3,G4,G5] | always |
| build-and-config | core | [08] | [all] | always |
| checkpoints | core | [10,11] | [G3,G4,G5] | sprint loop |
| commentary-policy | interview | [04,08] | [all] | always |
| competition | meta | [06,08,11] | [G3,G4,G5] | universe 단일안 부재 |
| conservative-margin-judging | meta | [06,08,09,10] | [G3,G4,G5] | any tournament/shadow/sprint scoring |
| contested-decision-multiverse | planning | [06] | [G3,G4,G5] | universe axis 부재 |
| contracts | core | [all] | [all] | always |
| convention-traceability | meta | [all] | [G3,G4,G5] | always |
| cross-phase-shared-context | meta | [06,08,09,14] | [all] | shared 정보 인용 |
| sprint-narrative | sprint | [06,10,11] | [all] | always (lessons / stagnation) / sprint NN+1 (delta) / universe 패배 (cross-universe) |
| dacapo | tournament | [06,08] | [G3,G4,G5] | always |
| dacapo-enforcement | tournament | [06,08] | [G3,G4,G5] | phase exit |
| dacapo-flow-trace | tournament | [06,08] | [G3,G4,G5] | dacapo step |
| dacapo-frontmatter-schema | tournament | [06,08] | [G3,G4,G5] | tournament 산출 |
| dacapo-mandatory-rerun | tournament | [06,08] | [G3,G4,G5] | step D AND pass |
| dacapo-skip-sentinel | tournament | [06,08] | [G3,G4,G5] | sentinel 매치 |
| data-structure-invariants | planning | [06] | [all] | data 구조 ≥ 1 |
| dead-code-zero | quality | [09] | [all] | code present |
| decision-support-framing | meta | [14] | [G3,G4,G5] | handoff Q 답 |
| deep-semantic-intent | interview | [01,04] | [all] | always |
| deliverable-hurdle-supremacy | meta | [all] | [G3,G4,G5] | standalone |
| diagrams | mindmap | [01,04,06] | [all] | always |
| directional-simplification | interview | [05] | [G3,G4,G5] | critique 본문 |
| domain-pack | domain | [01,09] | [all] | always (model completeness) / 사용자 어댑터 매칭 (research stacking + failure patterns) |
| ensemble-synthesis-default | tournament | [06,11] | [G4,G5] | 점수차 < 0.05 |
| evidence-driven-sprint-planning | sprint | [10] | [G3,G4,G5] | always |
| experimental-control-protocol | quality | [09] | [all] | 실험 산출 |
| fragmentation | meta | [all] | [all] | always |
| grader-in-sprint | sprint | [10] | [all] | sprint stop |
| grades | core | [all] | [all] | always |
| idiomatic-code-quality | quality | [09] | [all] | code present |
| impl-multiverse-strict | impl | [08,09] | [G4,G5] | phase 09 진입 |
| indexing | core | [all] | [all] | always |
| intent-completeness | interview | [01] | [all] | always |
| intent-optional-disambiguation | interview | [01,04] | [all] | optional marker 검출 |
| intent-plan-impl-sprint-trinity | sprint | [10] | [G3,G4,G5] | always |
| intent-refresh | interview | [04,05] | [all] | phase 04 종료 / phase 05 종료 |
| interface-first-parallel-impl | impl | [06,08] | [all] | always |
| interview | interview | [04] | [all] | always |
| intra-phase-dacapo-loop | tournament | [06,08] | [G3,G4,G5] | always |
| magic-number-traceability | quality | [09] | [all] | code present |
| measurement-contract | planning | [06,11] | [all] | metric ≥ 1 |
| mindmap-quality | mindmap | [all] | [all] | always |
| models | core | [all] | [all] | always |
| multiverse-impl-fan-out | impl | [08] | [G3,G4,G5] | always |
| multiverse-width-default-bump | planning | [06,08] | [G3,G4,G5] | always |
| nfr-derivation | quality | [01,09] | [all] | NFR derived |
| parallel-cold-review | interview | [03] | [G3,G4,G5] | always |
| per-module-diagram-fan-out | mindmap | [06,08] | [all] | 모듈 ≥ 4 |
| phase-lineage-viewer | meta | [all] | [all] | phase exit |
| phase-state-machine | core | [all] | [all] | phase enter / phase exit |
| plan-tournament-scoring-strict | tournament | [06] | [all] | tournament 산출 |
| plan-tree | planning | [06] | [G3,G4,G5] | always |
| polyglot-code-quality | quality | [09] | [all] | always |
| prebuilt-shell-runtime-json | meta | [all] | [all] | observability HTML emit |
| pre-cold-session-bootup | meta | [all] | [all] | phase 00 enter 직전 |
| viewer-runtime | meta | [all] | [all] | 3 viewer 공통 (auto-refresh) / cold session start/end (lifecycle) |
| premortem-friction | interview | [02,03,07] | [G3,G4,G5] | always |
| process-flow-coherence | quality | [09] | [all] | process 차원 |
| readme-numbers-from-summary | quality | [09,14] | [all] | doc + summary |
| regression | meta | [10,11] | [G3,G4,G5] | always (sprint loop) / 회귀 정정 (lint autogen) |
| regression-tdd-gate | quality | [08,10,11] | [all] | every code change / dacapo step F / sprint iteration |
| reproducibility-doublecheck | quality | [09] | [all] | entry script |
| resources | core | [10] | [all] | always |
| results-decision-mapping | quality | [14] | [all] | always |
| resume | core | [all] | [all] | resume |
| rubric-driven-doc-skeleton | planning | [04] | [all] | rubric ≥ 1 |
| rubric-targeted-quality-gates | quality | [09] | [all] | rubric ≥ 1 |
| runtime-prereq | core | [04,09] | [all] | always |
| score-rubric-objectivity | quality | [09,14] | [all] | self-rating |
| shadow-grader-zero-context | tournament | [06,08] | [G3,G4,G5] | step C |
| simulation-physical-invariants | quality | [09] | [all] | sim domain |
| spec-catalog | quality | [01,09] | [all] | always |
| stack | core | [04] | [all] | always |
| sub-agents | core | [all] | [all] | always |
| subagent-trigger | core | [06,08] | [G3,G4,G5] | phase 06 exit / phase 08 enter |
| submission-portability | quality | [09] | [all] | entry script |
| test-invariants | quality | [09,10] | [all] | always |
| tournament-blind-rerun | tournament | [06,08,11] | [G3,G4,G5] | 임계 미달 |

총 **78 컨벤션**. self_lint C-IDX-1 가 `conventions/*.md` ↔ INDEX row 1:1 매칭 검증.

## 사용 규약

- **단일 진실 원천**: 본 표만 수정. 컨벤션 frontmatter router 메타 + 페이즈 본문 cross-ref + grades.md 매트릭스가 본 표 참조.
- **history narration 금지**: "removed in vNN" / "이전에는" / "sprint-NN 신규" 류 historical narrative 본 표 + 컨벤션 본문 모두 금지. 변경 history 는 [`../../../CHANGELOG.md`](../../../CHANGELOG.md) 단일 위치.
- **frontmatter backfill**: 각 컨벤션 본문 frontmatter 에 `id` / `category` / `applies-to-phases` / `applies-to-grades` / `trigger-when` / `indexed-in: conventions/INDEX.md` 박힘 (후속 sprint).
