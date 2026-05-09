# Convention Migration — sprint-37 다이어트 매핑 표

> sprint-37 의 컨벤션 다이어트 (`.ShipofTheseus/sprints/37/plan.md`) 매핑 표.
> 본 파일 = *단일 source*. 매 다이어트 PR 마다 1 행 추가.
> deprecated 컨벤션은 frontmatter `deprecated: true` + `successor:` 동시 박힘.

## 사용 규약

- 본 표는 **변경 history 가 아닌 *현재 활성 매핑***. deprecated 컨벤션이 *완전 제거* 된 시점에 본 행 유지 (1.0.0 까지).
- 후속 sprint 에서 추가 다이어트 시 본 표에 누적.
- INDEX.md 카운트는 본 표의 deprecated 행 수와 inverse — 매핑 동기 의무.
- self_lint C-MIGRATION (sprint-37 v0.9.42 신규, 후속 PR-AK 도입 예정) 가 매핑 무결성 검증.

## 컬럼

- **deprecated** : 삭제/통폐합 대상 컨벤션 ID (`<id>.md`)
- **successor** : 흡수 대상 — 컨벤션 ID 또는 페이즈 본문 (`phases/NN-name.md §section`)
- **introduced_in** : deprecation 도입 sprint (frontmatter `deprecated: true` 박힌 sprint)
- **removed_in** : 컨벤션 파일 *완전 삭제* sprint (도입 후 1 sprint grace 후)
- **rationale** : 다이어트 사유 (한 줄)

## 매핑

| deprecated | successor | introduced_in | removed_in | rationale |
|---|---|---|---|---|
| intent-refresh-post-interview | intent-refresh | sprint-37 PR-AA | sprint-37 PR-AA | 책임 단순 (의도 refresh 1 가지) + phase param 분기. 양쪽 본문 inline 흡수 |
| intent-refresh-post-critique | intent-refresh | sprint-37 PR-AA | sprint-37 PR-AA | 동일 — 1차/2차 refresh 단일 컨벤션 phase 분기 |
| aide-tree-multi-phase | aide-tree | sprint-37 PR-AB | sprint-37 PR-AB | breadth (multi-phase 확장) — 단일 컨벤션의 §2 축 |
| aide-tree-symmetry | aide-tree | sprint-37 PR-AB | sprint-37 PR-AB | depth (sequenceDiagram 대칭) — 단일 컨벤션의 §3 축 |

## 후속 PR 별 예상 추가 (참조 — `.ShipofTheseus/sprints/37/diet-analysis.md` §3)

| PR | deprecated 추가 | successor |
|---|---|---|
| PR-AA | intent-refresh-post-interview / intent-refresh-post-critique | intent-refresh |
| PR-AB | aide-tree-multi-phase / aide-tree-symmetry | aide-tree |
| PR-AC | viewer-auto-refresh / viewer-runtime-lifecycle | viewer-runtime |
| PR-AD | mindmap-centrality / mindmap-quality-gardening / mindmap-richness-default | mindmap-quality |
| PR-AE | regression-derived-lint-rule-autogen / sprint-regression-loop | regression |
| PR-AF | sprint-score-delta-tracking / cross-universe-lesson-distillation / lessons | sprint-narrative |
| PR-AG | domain-research-stacking / domain-failure-patterns / domain-model-completeness | domain-pack |
| PR-AH | canonical-not-stub | phases/06,08,14 §canonical |
| PR-AI | timing | phases/00,14 §timing |
| PR-AJ | stack | phases/04 §stack |

본 표는 *예상* — 실제 PR 머지 시 본 파일에 1 행 추가 + introduced_in 갱신.

## 관련

- sprint-37 plan : `.ShipofTheseus/sprints/37/plan.md`
- 다이어트 분석 : `.ShipofTheseus/sprints/37/diet-analysis.md`
- 카테고리 라우터 : [`INDEX.md`](INDEX.md)
- 변경 history : [`../../../CHANGELOG.md`](../../../CHANGELOG.md)
