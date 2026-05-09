# Sprint-37 다이어트 분석 — 90 컨벤션 본문 길이 + 통폐합 판정 + 후속 PR 분할안

> 작성: 2026-05-09 (sprint-37 PR-A)
> base: PR #61 plan.md 의 §3.1 트랙 1
> 본 보고서 = 다이어트 작업의 *기준선*. 후속 PR (PR-AA, PR-AB, ...) 이 1-2 컨벤션 단위 매핑 누적.

## 0. 본 PR 의 scope 결정 회고

PR-A 의 초기 scope 는 plan.md §3.1.3 "dacapo 군 7→2" 였으나, 본문 분석 결과 **dacapo 군 7개가 각각 다른 책임 layer 로 분리** :

| 컨벤션 | 책임 | 라인 |
|---|---|---|
| dacapo | 얇은 인덱스 + 신규 2 개념 (defense_test / contradiction) | 121 |
| dacapo-enforcement | runtime gate + HARD-RULE 9.o + self_lint 7 신규 | 229 |
| dacapo-flow-trace | flow trace artifact | 321 |
| dacapo-frontmatter-schema | frontmatter 스키마 + 검증 | 229 |
| dacapo-mandatory-rerun | mandatory rerun 룰 | 90 |
| dacapo-skip-sentinel | skip sentinel + bypass 룰 | 332 |
| intra-phase-dacapo-loop | 페이즈 06/08 의사코드 7 step | 366 |
| **합** | **7 컨벤션** | **1688** |

7→2 통합 시 단일 컨벤션 ~1500+ 라인 → **사용자의 "비대화 회피" 의도와 충돌**.

다음 후보 = plan.md §3.1.4 "기타 inline 후보 4" (subagent-trigger / phase-state-machine / canonical-not-stub / runtime-prereq) 였으나 본문 분석 결과 :

| 컨벤션 | self_lint 룰 | runtime infra | 라인 |
|---|---|---|---|
| subagent-trigger | C-STT (본문 키워드 검사) | scoring/sub_agent_dispatch.py | 153 |
| phase-state-machine | C-PSM | scoring/phase_state.py | 181 |
| canonical-not-stub | (없음) | (없음) | 80 |
| runtime-prereq | (있음) | (있음) | 173 |

**inline 흡수 시 *self_lint 룰* + *runtime infra reference* 도 동시 변경** → 단일 PR 검증 부담 초과.

→ **PR-A scope 재조정 (2번째)** : 실제 다이어트 대신 **분석 보고서 + MIGRATION.md 골격**. 후속 PR-AA/AB/... 가 컨벤션 1-2개 단위로 다이어트 진행.

본 결정 정합 :
- plan.md §6 premortem "다이어트로 룰 의미 손실" → MIGRATION.md 매핑 의무 (본 PR 골격)
- 메모리 `feedback_pseudocode_to_enforcement` → self_lint 룰 + 페이즈 본문 동시 갱신 단일 PR 부담 (본 PR 회피)
- 메모리 `feedback_premortem_not_pause` → "결정 후 재고민" — PR-A scope 2회 재조정이 본 룰 시범 적용

---

## 1. 90 컨벤션 본문 분포 (라인 기준)

| 분위 | 라인 범위 | 컨벤션 수 | 비고 |
|---|---|---|---|
| 가장 짧음 | 40-100 | 12 | 단순 룰, 통폐합 후보 (책임 단순) |
| 짧음 | 100-150 | 25 | 표준 룰 |
| 중간 | 150-220 | 25 | runtime infra 포함 가능 |
| 김 | 220-300 | 16 | 큰 모듈 (checkpoint / lessons / spec-catalog 등) |
| 매우 김 | 300-515 | 12 | 대형 산출물 (dacapo-skip-sentinel / intra-phase-dacapo-loop / phase-lineage-viewer 등) |

**총 15,289 라인** (90 컨벤션 + INDEX.md 123 라인).

다이어트 후보의 ***우선순위*** 는 라인 수 ≠ 책임 단순도. 책임 단순 = 통폐합 가능. 책임 분기 = 분리 유지.

---

## 2. 통폐합 후보 재분류 (책임 단순도 기준)

### 카테고리 A — 즉시 통폐합 가능 (책임 단순 + 의존 적음)

| 묶음 | 현 | 통폐합 후 | 라인 절감 (추정) | 위험 |
|---|---|---|---|---|
| **intent-refresh** | post-interview (130) + post-critique (102) | 1 (`intent-refresh`, phase param) | -100 | 낮음 |
| **mindmap 메타** | mindmap-centrality (114) + mindmap-quality-gardening (151) + mindmap-richness-default (179) | 1 (`mindmap-quality`) | -300 | 중간 (3 컨벤션 본문 통합) |
| **viewer 보조** | viewer-auto-refresh (120) + viewer-runtime-lifecycle (116) | 1 (`viewer-runtime`) | -100 | 낮음 |
| **regression** | regression-derived-lint-rule-autogen (147) + sprint-regression-loop (111) | 1 (`regression`) — regression-tdd-gate 별도 유지 | -150 | 중간 |
| **sprint-narrative** | sprint-score-delta-tracking (131) + cross-universe-lesson-distillation (120) + lessons (228) | 1 (`sprint-narrative`) | -300 | 중간 |
| **domain** | domain-research-stacking (128) + domain-failure-patterns (128) + domain-model-completeness (139) | 1 (`domain-pack`) | -250 | 중간 (도메인 어댑터 영향) |
| **aide-tree** | aide-tree-multi-phase (105) + aide-tree-symmetry (77) | 1 (`aide-tree`) | -100 | 낮음 |

**카테고리 A 합** : 7 묶음 → **17 컨벤션 → 7 (-10)**, **약 -1,300 라인**.

### 카테고리 B — 페이즈 inline 흡수 후보 (자주 invoke + 책임 단순)

| 컨벤션 | 흡수 페이즈 | 라인 | 위험 |
|---|---|---|---|
| canonical-not-stub | phases/06, 08, 14 boilerplate | 80 | 낮음 |
| stack | phases/04 §stack | 102 | 낮음 |
| timing | phases/00 + 14 §timing | 75 | 낮음 |
| anti-patterns | (이미 카탈로그 컨벤션, 별도 유지) | 43 | 통합 유지 |

**카테고리 B 합** : 3 컨벤션 inline 가능 (canonical-not-stub / stack / timing), **-257 라인**.

### 카테고리 C — runtime infra 동반 (분리 유지 권장)

| 컨벤션 | 사유 |
|---|---|
| subagent-trigger | self_lint C-STT + scoring/sub_agent_dispatch.py |
| phase-state-machine | self_lint C-PSM + scoring/phase_state.py |
| runtime-prereq | self_lint + scoring infra |
| dacapo-enforcement | self_lint 7 신규 + runtime gate |
| dacapo-flow-trace | trace artifact |
| dacapo-skip-sentinel | sentinel matching infra |
| phase-lineage-viewer | lineage.json/md/html emit infra |
| prebuilt-shell-runtime-json | dist/ infra |
| viewer-runtime-lifecycle (★) | PID/port lock infra (카테고리 A 통합 시 검토 필요) |
| pre-cold-session-bootup | bootup script |

**카테고리 C 합** : 10 컨벤션, **분리 유지**. 통폐합 시 self_lint 룰 + runtime infra 동시 변경 단일 PR 부담 초과.

### 카테고리 D — 핵심 유지 (변경 안 함)

| 컨벤션 | 사유 |
|---|---|
| autonomy / contracts / grades / models / indexing | core 룰, 변경 시 전체 영향 |
| HARD-CORE.md (별도) | 본 hardener |
| interview / commentary-policy | 인터뷰 골격 |
| dacapo (얇은 인덱스) | dacapo 군의 mapping doc 역할 — 본문 통합 시 의미 손실 |

---

## 3. 후속 PR 분할안 (sprint-37 본 sprint 내)

| PR | scope | 컨벤션 변경 | self_lint | 라인 절감 |
|---|---|---|---|---|
| **PR-A** ★ 본 PR | 분석 보고서 + MIGRATION.md 골격 | 0 | 0 | 0 (기준선 산출) |
| PR-AA | intent-refresh 2→1 | 2 삭제 + 1 신규 | C-IDX-1 카운트 갱신 | ~-100 |
| PR-AB | aide-tree 2→1 | 2 삭제 + 1 신규 | C-IDX-1 갱신 | ~-100 |
| PR-AC | viewer-auto-refresh + viewer-runtime-lifecycle 2→1 | 2 삭제 + 1 신규 | C-IDX-1 갱신 | ~-100 |
| PR-AD | mindmap 3→1 | 3 삭제 + 1 신규 + 페이즈 01/06 본문 갱신 | C-IDX-1 갱신 | ~-300 |
| PR-AE | regression 2→1 | 2 삭제 + 1 신규 | C-IDX-1 갱신 | ~-150 |
| PR-AF | sprint-narrative 3→1 | 3 삭제 + 1 신규 | C-IDX-1 갱신 | ~-300 |
| PR-AG | domain 3→1 | 3 삭제 + 1 신규 | C-IDX-1 갱신 | ~-250 |
| PR-AH | canonical-not-stub inline | 1 삭제 + phases/06,08,14 본문 갱신 | C-IDX-1 갱신 | -80 |
| PR-AI | timing inline | 1 삭제 + phases/00,14 본문 갱신 | C-IDX-1 갱신 | -75 |
| PR-AJ | stack inline | 1 삭제 + phases/04 본문 갱신 | C-IDX-1 갱신 | -100 |

**누적 효과** :
- 카테고리 A 7 묶음 = 17 → 7 (-10), -1,300 라인
- 카테고리 B 3 inline = -3, -255 라인
- **합 -13 컨벤션 + -1,555 라인** → **90 → 77** (목표 90→55-60 의 절반).

추가 다이어트는 sprint-38 / sprint-39 (트랙 2, 3) 작업 시 발견되는 새로운 통폐합 기회로 누적.

---

## 4. PR 분할 원칙 (본 sprint-37 한정)

1. **1 PR = 1 묶음 단위** : intent-refresh 2→1 = 1 PR. 다른 묶음 동시 작업 금지 — 검증 부담 회피.
2. **self_lint 회귀 0** : 매 PR 마다 `python skills/theseus-harness/scoring/self_lint.py` 통과 필수.
3. **MIGRATION.md 매핑 의무** : 매 PR 가 본 파일에 1 행 추가 (deprecated → successor 매핑).
4. **카테고리 C / D 변경 금지** : 본 sprint 범위 외.
5. **후속 sprint 와의 중복 회피** : sprint-38 (페이즈 06-08 sub-phase) 변경 영역 (페이즈 06/07/08 본문) 은 본 sprint-37 다이어트 대상에서 제외.

---

## 5. 본 PR-A 의 산출물

| 파일 | 위치 | 역할 |
|---|---|---|
| diet-analysis.md (본 파일) | `.ShipofTheseus/sprints/37/` | 다이어트 기준선 + 후속 PR 분할안 |
| MIGRATION.md 골격 | `skills/theseus-harness/conventions/` | 매핑 표 (현 시점 0 행, 후속 PR 마다 누적) |

**self_lint / INDEX.md / 페이즈 본문 / HARD-CORE.md 변경 0** — 본 PR 은 *기준선 산출물* 만.

---

## 6. 메모리 / 메타 갱신

본 PR 의 **재조정 사실** 은 메모리 `feedback_premortem_not_pause` 의 *결정 후 재고민* 정합 — *플로우 자체로 누적*. 메모리 신규 저장 0.

---

## 7. 다음 PR 우선순위 권고

가장 *안전* 한 첫 다이어트 PR :

> **PR-AA — intent-refresh 2→1**
> - 이유 : 책임 단순 (post-interview / post-critique 두 phase 만), 의존 최소, runtime infra 0, self_lint 룰 0.
> - 변경 : 2 컨벤션 본문 통합 + INDEX.md 1 행 갱신 + frontmatter `phase` param 추가.
> - 검증 : self_lint 회귀 0 + 페이즈 04/05 본문 cross-ref 갱신 (양쪽 컨벤션 → 단일 컨벤션).

권고 = PR-AA 부터 시작.
