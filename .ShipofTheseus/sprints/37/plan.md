# Sprint-37 — Convention Diet + Harness Body Strengthening + Implementation-Layer Depth

> 시작: 2026-05-09
> 사용자 직접 지시 (요약): *"구멍 메우기 식 컨벤션 누적 중지 → 다이어트 + 본체 강화 + 구현-층 깊이 + 산출물 prompt 의존 + 산출물 경로 user-confirm 게이트"*
> 직전 입력: simulation-bench review 0509-01 (94/100, 6 카테고리 1pt 감점, 4개 자동검출 가능)
> 우선순위 결정 (사용자): **트랙 1 → 트랙 2 → 트랙 3** 순차

본 sprint = 트랙 1 (다이어트) 까지. 트랙 2/3 은 sprint-38, sprint-39 분리.

---

## 0. 배경 — 94 plateau + 누적 패치 패러다임의 구조적 한계

**측정 사실**:

- simulation-bench `2026-05-09__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4` = **94/100**
- 6 카테고리 1pt 감점 (Cat 2, 3, 4, 6 자동검출 가능 / Cat 1, 5 prose anchor)
- 메모리 `feedback_94_plateau_general_harness` 의 *general harness ceiling* 재확인

**4 감점의 메타-패턴 (도메인 중립)**:

| 패턴 | 사례 | 본질 |
|---|---|---|
| A. Plumbed-Not-Consumed | warmup_minutes 필드 정의 ✓ / 사용 ✗ | 정의 layer ↔ 실효 사용 layer 비대칭 |
| B. Workspace ≠ Deliverable | 내부 ramp_closed 검증 ✓ / 외부 README 부재 | 내부 압력 강함 / 외부 압력 빈약 |
| C. Proxy-as-Primary | truck_util = 1 − queue/shift | 형제 metric reformulation 을 1차 측정으로 통과 |
| D. Letter-by-Fallback | hardcoded `/mnt/d/...` + fallback | runtime 무해, source rubric 위반 |

**현행 36 sprint 누적 결과**:

- conventions = 90 개 (`skills/theseus-harness/conventions/INDEX.md` 명시 카운트)
- phases = 14 (페이즈 본문은 대부분 컨벤션 invoke 만 수행)
- HARD-CORE.md = 4386 chars (sprint 마다 +50~+150 누적)

**진단**:

> **컨벤션 = source, 페이즈 = invoke 의 분리가 너무 깊음.**
> sprint 마다 신규 컨벤션을 페이즈 본문에서 호출하는 구조는,
> ① cold agent 가 lookup 부담으로 룰을 skip 할 가능성을 키우고
> ② 페이즈 본문이 enforcement 책임을 갖지 않는 *얇은 dispatcher* 로 남게 하며
> ③ 룰 의미 변화 시 이중 갱신 (컨벤션 본문 + 페이즈 invoke 본문) 비용이 누적된다.

메모리 `feedback_pseudocode_to_enforcement` (룰 본문이 의사코드만이면 agent skip 가능) + `feedback_dual_pressure_json_schema` (이중 압력 = 본 하네스 강점) 의 결합:

→ **enforcement = 페이즈 본문 inline + orchestrator runtime guard 동시 박힘** 이 본 하네스의 강점인데, 컨벤션 누적은 이 강점을 약화시킨다.

---

## 1. 의도 — 한 줄

컨벤션 누적 패러다임을 **다이어트 + 페이즈 본문 흡수**로 전환하고, 이후 sprint 에서 구현-층 (페이즈 06-08) 을 sub-phase 깊이로 분해하며, 산출물에 prompt-trace + 경로 정책 + user-confirm 게이트를 박는다.

본 sprint-37 = 위 3축 중 **다이어트 (트랙 1)** 까지만.

---

## 2. 4 축 진단 (사용자 시각)

| 축 | 현 상태 | 요구 변화 | 본 sprint 처리 |
|---|---|---|---|
| α 컨벤션 | 90개 누적, source 단일, 구멍 메우기 | 다이어트 + 페이즈 본문 inline 흡수 | **트랙 1 = 본 sprint** |
| β 본체 | conventions = source, phases = invoke 위주 | 페이즈 본문 룰 inline + orchestrator runtime guard 강화 | 트랙 1 의 inline 흡수로 부분 진행 |
| γ 구현-층 | 06-08 monolithic, intent 해석 빈약 | research / intent / 분류 / sub-tree todo / post-decision premortem / subagent dispatch sub-phase | sprint-38 (트랙 2) |
| δ 산출물 | 내부 풍부 / deliverable 빈약 / 경로 자유 | prompt-trace 의무 + 경로 정책 + user-confirm 게이트 | 본 sprint 부터 *룰 자체* 즉시 적용 (본 plan.md 가 첫 적용 사례) |

---

## 3. 트랙 구성

### 트랙 1 — 컨벤션 다이어트 (본 sprint 우선) ★

#### 3.1.1 카테고리별 현 분포 (90)

INDEX.md 기준:

| cat | 카운트 (대략) |
|---|---|
| core | 14 |
| interview | 9 |
| mindmap | 4 |
| domain | 2 |
| planning | 5 |
| multiverse | 2 |
| tournament | 9 |
| impl | 2 |
| quality | 16 |
| sprint | 8 |
| meta | 19 |
| **합** | **90** |

#### 3.1.2 통폐합 원칙

1. **중복 통합** : 같은 의도 다른 표현 → 단일 룰
2. **승급 흡수** : 페이즈 본문에서 매번 invoke 되는 룰 → 페이즈 본문 본문에 inline 후 컨벤션 파일 삭제
3. **deprecation grace** : 상위 룰로 대체된 하위 룰은 frontmatter `deprecated: true` + `successor: <new>` + 1 sprint grace
4. **MIGRATION.md** : 90 → N 매핑 표 의무 (convention-traceability 룰 회귀 0)

#### 3.1.3 통폐합 후보 (초안 — 실제 작업은 본 sprint 의 후속 PR)

| 묶음 | 현 | 통폐합 | 처리 |
|---|---|---|---|
| dacapo 군 | dacapo / dacapo-enforcement / dacapo-flow-trace / dacapo-frontmatter-schema / dacapo-mandatory-rerun / dacapo-skip-sentinel / intra-phase-dacapo-loop | **7 → 2** (`dacapo` 단일 + `intra-phase-dacapo-loop` 별도 유지) | 페이즈 06/08 본문 §dacapo step boilerplate 흡수 |
| aide-tree 군 | aide-tree-multi-phase / aide-tree-symmetry | **2 → 1** | 페이즈 02/05/06/08/11/13 cross-ref 단일화 |
| mindmap 군 | mindmap-centrality / mindmap-quality-gardening / mindmap-richness-default / per-module-diagram-fan-out | **4 → 2** | 페이즈 01/06 본문 §mindmap boilerplate 흡수 |
| intent-refresh 군 | intent-refresh-post-interview / intent-refresh-post-critique | **2 → 1** (`intent-refresh` + phase param) | 페이즈 04/05 본문 호출 |
| viewer 군 | viewer-auto-refresh / viewer-runtime-lifecycle / phase-lineage-viewer / prebuilt-shell-runtime-json | **4 → 2** (`phase-lineage-viewer` 통합 + `viewer-lifecycle` 별도) | 페이즈 12/13 본문 일부 흡수 |
| regression 군 | regression-derived-lint-rule-autogen / regression-tdd-gate / sprint-regression-loop | **3 → 1** (`regression`) | 페이즈 08/10/11 본문 §regression 박음 |
| sprint-narrative 군 | sprint-score-delta-tracking / cross-universe-lesson-distillation / lessons | **3 → 1** (`sprint-narrative`) | 페이즈 10/11 본문 흡수 |
| dacapo-tournament 군 | dacapo + tournament-blind-rerun + ensemble-synthesis-default + plan-tournament-scoring-strict | **4 → 2** | tournament 별 분리 유지, dacapo 만 통합 |
| 기타 inline 후보 | subagent-trigger / phase-state-machine / canonical-not-stub / runtime-prereq | **4 → 0** (모두 페이즈 본문 inline 흡수) | 각 페이즈 §enter/§exit boilerplate |
| domain-research 군 | domain-research-stacking / domain-failure-patterns / domain-model-completeness | **3 → 1** (`domain-pack`) | 페이즈 01/09 본문 흡수 |

**누적 효과**: 90 → **약 55-60** (-30~-35).

세부 매핑은 본 sprint 후속 PR 에서 `conventions/MIGRATION.md` 로 단일 산출.

#### 3.1.4 페이즈 본문 inline 흡수 boilerplate (예시)

```markdown
## phases/06-plan.md §enter (보강)

[from convention: phase-state-machine]
- 진입 전 phase 05 critique gate PASS 확인
- phase 06 산출물 manifest 검증

[from convention: subagent-trigger]
- universe candidate ≥1 시 sub-agent dispatch
- dispatch trace 의무

[from convention: canonical-not-stub]
- plan.md 산출물은 canonical (stub/placeholder 0)
- self_lint C-CANONICAL 검증
```

→ phase-state-machine, subagent-trigger, canonical-not-stub 컨벤션 파일 = 삭제.
→ 페이즈 본문이 단일 enforcement 지점.

#### 3.1.5 산출물 (본 sprint)

1. `skills/theseus-harness/conventions/MIGRATION.md` — 90 → N 매핑 표 + deprecated list
2. 통폐합 대상 컨벤션 파일 삭제 또는 frontmatter `deprecated: true` 부여
3. 페이즈 본문 inline 추가 (각 페이즈 본문 + 200~400 chars 예상)
4. `INDEX.md` 카운트 갱신 (90 → N) + 카테고리 매트릭스 갱신
5. `HARD-CORE.md` 갱신 — deprecated 룰 제거 + neutral phrasing
6. `scoring/self_lint.py` 갱신 — C-IDX-1 카운트, C-DIET 신규, C-PHASE-LEN 신규
7. `CHANGELOG.md` v0.9.42 entry
8. `SKILL.md` + `.claude-plugin/plugin.json` version bump

### 트랙 2 — 본체 강화 + 구현-층 깊이 (sprint-38)

#### 3.2.1 페이즈 06 분해

```
Phase 06 (구현 spec) 분해
├ 06.a  Research-injection
│   - 외부 ref / 도구 / 라이브러리 / 도큐 (context7 / web)
│   - 산출: research.md (인용 ≥3, 결론 ≤3)
├ 06.b  Intent-decoding
│   - 프롬프트 directive 매트릭스 추출
│   - 명시 (must/should/avoid) + 묵시 (primary/canonical/no-proxy) + rubric 채점항
│   - 산출: directives.json — {id, type, source_quote, layers:[def/exec/visibility]}
├ 06.c  Classification
│   - 모듈/관심사/책임 분할 (구현 분류 트리)
│   - 산출: classification.md (≥3 layer)
├ 06.d  Sub-tree TODO
│   - 분류 노드별 todo, 깊이 ≥3
│   - subagent dispatch 단위와 1:1 일치
│   - 산출: TaskCreate 호출 tree
├ 06.e  Post-decision premortem
│   - 결정 후 재고민 (격언 동·서 1개)
│   - 미래 회고 시뮬레이션
│   - 산출: premortem.md (derived improvements ≥1)
└ 06.f  Path-policy + user-confirm gate
    - 산출물 경로 후보 ≥2 제시
    - 내용 줄거리 압축 제시
    - 사용자 질의 (AskUserQuestion or 인터뷰)
    - 승인 후 작성
```

#### 3.2.2 페이즈 07 강화 (subagent dispatch)

```
Phase 07 (subagent dispatch) 강화
├ 07.a  Dispatch table — 06.d sub-tree 노드 → agent role 매핑
├ 07.b  Dispatch trace — agent 실행/산출 추적 manifest
└ 07.c  Cross-agent invariant — agent 간 산출 정합성 lint
```

#### 3.2.3 페이즈 08 추가 lint

```
Phase 08 (TDD 5 sub) 유지 + 추가
└ 08.f  Prompt-trace lint
    - 모든 deliverable 산출물 → originating directive 역추적
    - 미추적 산출물 = warn or fail
```

### 트랙 3 — 4 패턴 inline (sprint-39)

페이즈 09 본문 inline (컨벤션 X):

| 패턴 | 메커니즘 |
|---|---|
| **PNC** | AST 분석 — dataclass/yaml 정의 vs 실효 사용 |
| **Deliverable-Mirror** | internal verification fact ↔ deliverable mirror 매니페스트 |
| **Primary-Source** | 메트릭 source-signal manifest, sibling overlap > 50% warn |
| **Literal-Forbid** | forbid directive → regex 자동 → deliverable source 검사 |

---

## 4. 산출물 경로 정책 (즉시 적용 — 룰 시범)

```
산출물 생성 전 :
  ① 경로 후보 ≥2 제시
  ② 내용 줄거리 압축 제시
  ③ AskUserQuestion / 인터뷰
  ④ 승인 후 작성
```

**본 plan.md 자체가 첫 적용 사례** :
- 후보: `.ShipofTheseus/sprints/37/plan.md` / `skills/theseus-harness/sprints/37/` / mirror 양쪽
- 사용자 결정 (2026-05-09): `.ShipofTheseus/sprints/37/plan.md`

본 룰은 트랙 2 (sprint-38) 의 페이즈 06.f 에서 정식 enforcement. 그 전까지는 *권고* 단계.

---

## 5. premortem — 사전 부검

| 우려 | 사전 정정 |
|---|---|
| 다이어트로 룰 의미 손실 | 페이즈 본문 inline 으로 보존, MIGRATION.md 매핑 의무, frontmatter `successor:` |
| 페이즈 본문 비대화 | 신규 self_lint C-PHASE-LEN — 페이즈 본문 길이 임계 (예: 4500 chars) 추가 |
| cold agent 가 inline 룰 skip | orchestrator runtime guard inline 도 동시 추가 (트랙 2 영역) |
| sprint-36 까지 작업 호환 | 컨벤션 frontmatter `deprecated: true` + 1 sprint grace |
| convention-traceability 룰 회귀 | 통폐합 매핑 frontmatter `successor:` + MIGRATION.md cross-ref |
| C-IDX-1 회귀 | 카운트 변경 self_lint 동시 갱신 |
| 외부 cold session 영향 | 본 sprint = harness skill 변경, 외부 submission 영향 0 (호환 그대로) |

격언 (동·서 1개):

- **동**: 「過猶不及 (과유불급)」 — 누적도 부족도 균형 잃으면 약점.
- **서**: 「Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.」 (Saint-Exupéry) — 본 sprint 의 다이어트 정신.

---

## 6. self_lint 변경 (이번 sprint)

| 룰 ID | 변경 | 내용 |
|---|---|---|
| C-IDX-1 | 갱신 | 카운트 90 → N, 카테고리 매트릭스 갱신 |
| C-DIET | 신규 | deprecated 컨벤션 grace 1 sprint 후 자동 삭제 검증 |
| C-PHASE-LEN | 신규 | 페이즈 본문 길이 임계 (4500 chars 권고, 5000 chars 강제) |
| C-MIGRATION | 신규 | MIGRATION.md 매핑 무결성 — 삭제 컨벤션 모두 successor 매핑 |
| C-HC1 | 유지 | HARD-CORE 길이 임계 4400 (다이어트 후 줄어들 가능성, 임계 그대로) |
| 기존 C-PSR / C-VAR / etc | 유지 | 회귀 0 강제 |

---

## 7. 다음 sprint 후보

| sprint | 트랙 | spec |
|---|---|---|
| sprint-38 | 트랙 2 | 페이즈 06-08 sub-phase 분해 + path-policy enforcement |
| sprint-39 | 트랙 3 | 페이즈 09 4 패턴 (PNC / Mirror / Primary / Literal) inline |
| sprint-40 | 외부 적용 | simulation-bench 재제출 — 누적 효과 검증 (94 → 97+ 목표) |

각 후속 sprint = 본 plan.md 의 트랙 spec 직접 참조.

---

## 8. 진행 단계 (본 sprint)

1. ☐ MIGRATION.md 초안 — 90 → N 매핑 표
2. ☐ 통폐합 대상 컨벤션 파일 삭제 / deprecated tag
3. ☐ 페이즈 본문 inline 흡수 (각 페이즈 §enter / §exit / §subagent-dispatch / §mindmap / §dacapo / §regression boilerplate)
4. ☐ INDEX.md 갱신
5. ☐ HARD-CORE.md 갱신
6. ☐ self_lint.py 갱신 (C-IDX-1 / C-DIET / C-PHASE-LEN / C-MIGRATION)
7. ☐ CHANGELOG.md v0.9.42 entry
8. ☐ SKILL.md + plugin.json bump
9. ☐ self_lint 회귀 0 검증
10. ☐ self-eat 검증 — 본 sprint 가 본 룰 (다이어트 + 본체 흡수) 자체에 부합
11. ☐ PR 생성

---

## 9. 본 sprint 의 의미 — 메타

본 sprint = **본 하네스 자체의 중간 turn** :

- sprint-01~36 = "추가" 패러다임 (기능 + 컨벤션 누적)
- sprint-37 = "정리" 패러다임 (다이어트 + 본체 흡수)
- sprint-38~ = "깊이" 패러다임 (구현-층 sub-phase + path-policy + 4 패턴)

3 단계 패러다임 전환은 본 하네스가 1.0.0 에 도달하기 전 자체 ship-of-theseus 가설의 검증 — *기능 누적만으로는 천정 못 깸. 본체 정리 + 깊이 모두 필요.*

메모리 후속 갱신 :

- `feedback_convention_diet_paradigm.md` (신규) — 본 sprint 의 결론 영구화
- `project_sprint37_v0942.md` (sprint 마감 후) — 출하 결과 기록
