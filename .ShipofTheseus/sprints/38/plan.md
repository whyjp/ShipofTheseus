# Sprint-38 — 본체 강화 + 구현-층 깊이 (트랙 2)

> 시작: 2026-05-09 (sprint-37 12 PR 마감 직후)
> 직전: sprint-37 다이어트 마감 (90 → 84 컨벤션, -13 net, 14 통합 + 3 inline, MIGRATION.md 14 행)
> 우선순위 (사용자): **트랙 2 → 트랙 3 → 외부 적용 (sprint-39, sprint-40)**

본 sprint = sprint-37 plan.md §3.2 의 **트랙 2 (본체 강화 + 구현-층 깊이)** 의 정식 진행.

---

## 0. 배경 — sprint-37 마감 결과 + 트랙 2 도입

sprint-37 트랙 1 (다이어트) 마감 :

- 90 → 84 컨벤션 (-13 net), 본문 -470 라인
- 7 신규 통합본 + 3 inline + MIGRATION.md 단일 source
- self_lint 10 함수 통합본 path 갱신, all_ok=True 0/114
- 패러다임 전환 = 누적 패치 → 다이어트+본체 강화

**메모리** :
- `feedback_convention_diet_paradigm` — 신규 컨벤션은 통폐합/inline 검토 후 최후 수단
- `feedback_deliverable_path_user_confirm` — 산출물 경로 user-confirm 게이트

**남은 결손** (sprint-37 가 답하지 못한 것):

| 결손 | 영향 |
|---|---|
| 페이즈 06 monolithic 단일 파일 | 의도→계획→구현 사이 *intent 해석 + classification + sub-tree TODO* 가 plan 본문에 모두 묶임. cold session 마다 *직진 작성* 으로 깊이 부족 |
| Path-policy 권고 단계만 | sprint-37 plan/handoff 가 본 룰 시범 적용했으나 페이즈 본문 enforcement 0 |
| 페이즈 본문 길이 제어 0 | sprint-37 통합본 일부 (mindmap-quality 288, sprint-narrative 370) 가 이전 250 권고 초과 |
| Prompt-trace 부재 | 산출물 → prompt directive 역추적 메커니즘 없음 (deliverable 가 prompt 의 어느 directive 충족인지 추적 불가) |

---

## 1. 의도 — 한 줄

페이즈 06 monolithic 을 **6 sub-phase (06.a Research / 06.b Intent-decoding / 06.c Classification / 06.d Sub-tree TODO / 06.e Post-decision premortem / 06.f Path-policy + user-confirm gate)** 로 분해 + 페이즈 07/08 강화 + path-policy 정식 enforcement + 프롬프트 trace 의무화.

---

## 2. 4 축 진단 (sprint-37 plan.md §2 의 트랙 2 부분 재확인)

| 축 | sprint-37 후 상태 | sprint-38 변화 |
|---|---|---|
| α 컨벤션 | 84개 (sprint-37 -13 net) | 변경 0 (트랙 2 = 페이즈/agent 구조 변경) |
| β 본체 | 페이즈 06 monolithic, intent 해석 빈약 | **페이즈 06 6 sub-phase 분해** |
| γ 구현-층 | 06-08 monolithic, sub-tree TODO 부재 | **페이즈 06.d sub-tree + 페이즈 07 dispatch + 페이즈 08.f prompt-trace** |
| δ 산출물 | 권고 단계 (path-policy / prompt-trace 미적용) | **path-policy enforcement (06.f) + prompt-trace lint (08.f)** |

---

## 3. Phase 06 분해 — 6 sub-phase

### 3.1 sub-phase 정의

```
Phase 06 (현 monolithic) → 6 sub-phase 분해

06.a  Research-injection
  - 외부 ref / 도구 / 라이브러리 / 도큐 (context7 / web fetch)
  - 산출: research.md (인용 ≥3, 결론 ≤3)
  - 의무: 모든 인용에 source URL/제목 + 추출 결론 1 줄
  - skip 조건: prompt 가 명시 외부 ref 0 + cold session full-context

06.b  Intent-decoding
  - 프롬프트 directive 매트릭스 추출
  - 명시 (must/should/avoid) + 묵시 (primary/canonical/no-proxy) + rubric 채점항
  - 산출: directives.json — {id, type, source_quote, layers:[def/exec/visibility]}
  - 의무: 모든 directive 가 prompt source quote + 3 layer 매핑 (def/exec/visibility)

06.c  Classification
  - 모듈/관심사/책임 분할 (구현 분류 트리)
  - 산출: classification.md (≥3 layer)
  - 의무: 모든 모듈이 ≥1 directive 매핑 (orphan 모듈 0)

06.d  Sub-tree TODO
  - 분류 노드별 TODO, 깊이 ≥3
  - subagent dispatch 단위와 1:1 일치
  - 산출: TaskCreate 호출 tree (또는 todo-tree.md)
  - 의무: 모든 leaf TODO 가 ≥1 module + ≥1 directive 매핑

06.e  Post-decision premortem
  - 결정 후 재고민 (격언 동·서 1개)
  - 미래 회고 시뮬레이션
  - 산출: premortem.md (derived improvements ≥1)
  - 의무: ≥1 derived improvement → plan 본문 갱신

06.f  Path-policy + user-confirm gate
  - 산출물 경로 후보 ≥2 제시
  - 내용 줄거리 압축 제시
  - AskUserQuestion 또는 인터뷰
  - 승인 후 작성
  - 의무: 본 sub-phase 가 phase 06 의 *마지막* — 출력 산출물 (06.a-06.e 산출 전체 + 06-plan.md 자체) 의 경로 사용자 ack
  - 사용자 ack 0 = phase 07 진입 거부
```

### 3.2 sub-phase 간 의존

```
06.a Research → 06.b Intent-decoding → 06.c Classification → 06.d Sub-tree TODO
                                                                   ↓
                                                           06.e Premortem
                                                                   ↓
                                                           06.f Path-policy ack
                                                                   ↓
                                                       phase 07 진입
```

각 sub-phase 가 직전 sub-phase 의 산출물을 frontmatter `prev_fingerprint` 로 인용 (contracts.md fingerprint chain 정합).

### 3.3 sub-phase 산출물 위치

`.ShipofTheseus/<프로젝트>/plan/`:

```
plan/
├── 06-research.md              # 06.a
├── 06-directives.json          # 06.b
├── 06-classification.md        # 06.c
├── 06-todo-tree.md             # 06.d (또는 TaskCreate trace)
├── 06-premortem.md             # 06.e
├── 06-path-policy.md           # 06.f (사용자 ack 산출물)
└── 06-plan.md                  # 통합 canonical (모든 sub-phase 산출 흡수)
```

phase 06 canonical = sub-phase 6 산출물 *통합* (각 sub-phase 본문 inline + cross-link).

### 3.4 phases/06-plan.md 본문 변화

기존 monolithic phase 06 본문을 6 sub-phase 섹션 분할 :

```markdown
# Phase 06 — 계획 (6 sub-phase)

## 06.a Research-injection (sub-phase 1/6)
- 트리거 / 산출 / 의무 / skip 조건
- subagent 호출 형식

## 06.b Intent-decoding (sub-phase 2/6)
...

## 06.c Classification (sub-phase 3/6)
...

## 06.d Sub-tree TODO (sub-phase 4/6)
...

## 06.e Post-decision premortem (sub-phase 5/6)
...

## 06.f Path-policy + user-confirm gate (sub-phase 6/6)
...
```

기존 본문의 plan-tree / multiverse / dacapo 룰은 06.d ~ 06.e 영역 통합 (의도: 6 sub-phase 가 multiverse 와 *직교* — sub-phase 각각이 N universe 분기 가능).

---

## 4. Phase 07 강화 — subagent dispatch

### 4.1 sub-phase 정의

```
Phase 07 (현 단순 dispatch) → 3 sub-phase

07.a  Dispatch table
  - 06.d sub-tree 노드 → agent role 매핑
  - 산출: 07-dispatch-table.md
  - 의무: 모든 leaf TODO 에 agent role 명시

07.b  Dispatch trace
  - agent 실행/산출 추적 manifest
  - 산출: 07-dispatch-trace.json
  - 의무: 매 agent 호출의 시작/종료 timestamp + 산출 파일 list

07.c  Cross-agent invariant
  - agent 간 산출 정합성 lint
  - 산출: 07-cross-agent-lint.md
  - 의무: agent A 의 output 이 agent B 의 input 정합 (interface drift 0)
```

### 4.2 산출물 위치

`.ShipofTheseus/<프로젝트>/dispatch/`:

```
dispatch/
├── 07-dispatch-table.md
├── 07-dispatch-trace.json
└── 07-cross-agent-lint.md
```

---

## 5. Phase 08 강화 — prompt-trace lint

### 5.1 신규 sub-phase 08.f

```
Phase 08 기존 5 sub-phase (08-α / β / γ / δ / ε) 유지 + 추가

08.f  Prompt-trace lint
  - 모든 deliverable 산출물 → originating directive 역추적
  - 미추적 산출물 = warn or fail
  - 산출: 08-prompt-trace.md (deliverable → directive 매핑 표)
  - 의무: 모든 deliverable 이 ≥1 directive (06.b directives.json) 매핑
```

### 5.2 self_lint 신규 — C-PT (prompt-trace)

```python
def check_prompt_trace(skill_root: Path, project_root: Path) -> list[str]:
    issues = []
    directives = json.loads((project_root / "plan" / "06-directives.json").read_text())
    trace = parse_md(project_root / "impl" / "08-prompt-trace.md")
    for deliverable in scan_deliverables(project_root):
        if deliverable not in trace:
            issues.append(f"{deliverable}: prompt-trace 누락")
            continue
        mapped_directives = trace[deliverable]
        for did in mapped_directives:
            if did not in directives:
                issues.append(f"{deliverable}: directive {did} 부재 (06-directives.json)")
    return issues
```

---

## 6. self_lint 변경 (sprint-37 plan §6 잔여 + 트랙 2 신규)

| 룰 ID | 변경 | 내용 |
|---|---|---|
| C-IDX-1 | 갱신 | 카운트 narrative 84 정합 (sprint-37 fix #74 후속) |
| C-DIET | 신규 | deprecated 컨벤션 grace 1 sprint 후 자동 삭제 검증 — sprint-37 MIGRATION.md 의 introduced/removed_in 정합 |
| C-PHASE-LEN | 신규 | 페이즈 본문 길이 임계 (4500 chars 권고, 5000 chars 강제) |
| C-MIGRATION | 신규 | MIGRATION.md 매핑 무결성 — 삭제 컨벤션 모두 successor 매핑 |
| C-PT | 신규 | prompt-trace (08.f) — deliverable ↔ directive 매핑 |
| C-IDC | 신규 | intent-decoding (06.b) — directives.json schema + 모든 directive source quote 의무 |
| C-PPC | 신규 | path-policy + user-confirm (06.f) — 산출물 경로 후보 ≥2 + 사용자 ack frontmatter |
| C-RES | 신규 | research-injection (06.a) — research.md 인용 ≥3 + 결론 ≤3 |
| C-CLS | 신규 | classification (06.c) — ≥3 layer + orphan 모듈 0 |
| C-STT | 신규 | sub-tree TODO (06.d) — leaf TODO module + directive 매핑 의무 |
| C-PMT | 신규 | premortem (06.e) — derived improvements ≥1 |

---

## 7. PR 분할안

| PR | scope | 산출 | 위험 |
|---|---|---|---|
| **PR-A** ★ 본 PR | sprint-38 plan.md (본 문서) | 0 (계획만) | 0 |
| PR-B | path-policy (06.f) 정식 enforcement + self_lint C-PPC | phases/06.f boilerplate + AskUserQuestion 호출 패턴 + frontmatter `path_policy_acked: true` 의무 | 낮음 (단일 sub-phase) |
| PR-C | 06.a Research-injection sub-phase 도입 | phases/06.a + research.md template + self_lint C-RES | 낮음 (skip 조건 명확) |
| PR-D | 06.b Intent-decoding sub-phase + directives.json schema | phases/06.b + directives.json template + self_lint C-IDC | **중간** (모든 후속 sub-phase 의 source) |
| PR-E | 06.c Classification sub-phase | phases/06.c + classification.md template + self_lint C-CLS | 낮음 |
| PR-F | 06.d Sub-tree TODO sub-phase | phases/06.d + 06-todo-tree.md template + self_lint C-STT | 중간 (TaskCreate 통합) |
| PR-G | 06.e Post-decision premortem sub-phase | phases/06.e + premortem.md template + self_lint C-PMT | 낮음 |
| PR-H | 06 통합 — 6 sub-phase 본문 phases/06-plan.md 재구성 + canonical 흡수 룰 | phases/06-plan.md major 재작성 | **큼** (기존 본문 보존 + 6 sub-phase 흡수) |
| PR-I | Phase 07 dispatch table + trace + invariant 3 sub-phase | phases/07-* + 3 self_lint 신규 | 중간 |
| PR-J | Phase 08.f prompt-trace lint sub-phase | phases/08.f + 08-prompt-trace.md template + self_lint C-PT | 중간 |
| PR-K | self_lint 신규 (C-DIET, C-PHASE-LEN, C-MIGRATION) + INDEX 정합 | scoring/self_lint.py 3 함수 신규 + MIGRATION.md schema 갱신 | 중간 |
| PR-L | sprint 마감 — version bump v0.9.43 + CHANGELOG | SKILL.md / plugin.json / CHANGELOG | 낮음 |

**누적 예상 효과** (PR-B~K):
- phase 06 monolithic → 6 sub-phase 분해
- phase 07 단순 → 3 sub-phase
- phase 08 5 sub → 6 sub (08.f 추가)
- self_lint +9 신규 룰 (114 → 123)
- 신규 산출물 8 종 (research.md / directives.json / classification.md / todo-tree.md / premortem.md / path-policy.md / dispatch-table.md / dispatch-trace.json / cross-agent-lint.md / prompt-trace.md)

---

## 8. 산출물 경로 정책 (sprint-38 본 sprint 부터 정식 enforcement)

```
산출물 생성 전 :
  ① 경로 후보 ≥2 제시
  ② 내용 줄거리 압축 제시
  ③ AskUserQuestion / 인터뷰
  ④ 승인 후 작성
```

**본 plan.md 자체가 본 sprint 의 첫 적용** :
- 후보: `.ShipofTheseus/sprints/38/plan.md` / `skills/theseus-harness/sprints/38/` / mirror 양쪽
- 사용자 결정 (2026-05-09 본 sprint 시작 turn): `.ShipofTheseus/sprints/38/plan.md` (sprint-37 동일 패턴)

---

## 9. premortem — 사전 부검

| 우려 | 사전 정정 |
|---|---|
| phase 06 6 sub-phase 분해 시 기존 plan-tree / multiverse 룰 흡수 어려움 | sub-phase 6 (06.d) 가 multiverse fan-out 위치, sub-phase 5 (06.e) 가 dacapo loop 위치. plan-tree 본문 보존, sub-phase 흐름 안에 *위치* 만 명시 |
| Sub-phase 마다 산출물 추가 = 시간 비용 ↑ | skip 조건 명확화 (06.a research = 외부 ref 0 시 skip / 06.f path-policy = 본 룰 자체 skip 불가, 항상 사용자 ack 의무) |
| cold agent 가 6 sub-phase 의 일부만 진행 | self_lint (C-IDC, C-CLS, C-STT, C-PMT, C-PPC) 가 각 sub-phase 산출물 부재 시 fail. orchestrator runtime guard 도 매 sub-phase 진입 검사 |
| 페이즈 본문 길이 5000 chars 강제 (C-PHASE-LEN) | sub-phase 별 별도 파일 분리 가능 (phases/06.a-research.md / phases/06.b-intent-decoding.md / 등). 또는 phases/06-plan.md 안에 §섹션 |
| 6 sub-phase 흡수 후 단일 phases/06-plan.md = 본문 비대 | 옵션 A: phases/06.a / 06.b / ... 별도 파일 분리. 옵션 B: phases/06-plan.md §섹션 통합. PR-H 진입 전 사용자 결정 의무 (path-policy 정합) |

격언 (동·서 1개):

- **동**: 「磨刀不誤砍柴工 (마도불오감시공)」 — 칼 가는 시간이 나무 베는 시간을 늦추지 않는다. 본 sprint 의 6 sub-phase 분해는 *직진 plan 작성* 보다 *느려 보이지만* 결과 깊이가 늘어 전체 효율은 상승.
- **서**: 「Slow down to speed up.」 — 본 sprint 의 다이어트 (sprint-37) + 본체 강화 (sprint-38) 패러다임 정합.

---

## 10. 후속 sprint 후보

| sprint | 트랙 | spec |
|---|---|---|
| sprint-39 | 트랙 3 | 페이즈 09 4 패턴 (PNC / Mirror / Primary / Literal) inline |
| sprint-40 | 외부 적용 | simulation-bench 재제출 — 본 sprint 효과 검증 (94 plateau 극복 목표) |

---

## 11. 본 sprint 의 의미 — 메타

본 sprint = **sprint-37 다이어트 (트랙 1) → sprint-38 본체 강화 (트랙 2)** 의 패러다임 전환 두 번째 단계 :

- sprint-01~36 = 추가 패러다임 (기능 + 컨벤션 누적)
- **sprint-37 = 정리 패러다임** (다이어트 + 본체 흡수, *완료*)
- **sprint-38 = 깊이 패러다임** (구현-층 sub-phase + path-policy + prompt-trace, *진행*)
- sprint-39 = 통합 패턴 (4 패턴 inline)
- sprint-40 = 외부 검증

3 단계 패러다임 전환 (정리 → 깊이 → 외부 검증) 은 본 하네스가 1.0.0 도달 전 자체 ship-of-theseus 가설 검증 — *기능 누적만으로는 천정 못 깸. 본체 정리 + 깊이 + 외부 검증 모두 필요*.

메모리 후속 갱신 :

- `feedback_phase06_sub_phase_decomposition.md` (PR-H 머지 후 신규) — 6 sub-phase 분해의 결정 + 효과 영구화
- `project_sprint38_v0943.md` (sprint 마감 후, PR-L 머지 시점)
