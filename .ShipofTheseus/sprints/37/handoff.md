# Sprint-37 Handoff — 다음 세션 cold-start 가이드

> 작성: 2026-05-09 (sprint-37 PR-A 마감 시점)
> 다음 세션 = **PR-AA — intent-refresh 2→1**
> 본 문서 + `plan.md` + `diet-analysis.md` 만 읽으면 cold start 가능.

---

## 0. 현재 상태 (2026-05-09 마감)

| PR | 브랜치 | scope | 상태 |
|---|---|---|---|
| #61 | `docs/sprint-37-plan` | plan.md (방향 + 트랙) | open, 사용자 머지 대기 |
| #62 | `feat/sprint-37-diet-analysis` | 분석 + MIGRATION 골격 + self_lint exception + handoff (본 문서) | open, base=`docs/sprint-37-plan` |

**머지 가정** : 다음 세션 시작 전 PR #61 + #62 가 main 으로 머지된 상태 가정. 미머지 시 `feat/sprint-37-diet-analysis` 위에 stack.

**커밋 0 인 변경** :
- repo root 의 untracked PNG 15개 (`hotspot-*.png`, `lineage-*.png`, `linear-*.png`, `review-*.png`, `sprint36-iv-*.png`) — 이전 sprint 시연용. 본 sprint scope 외, 별도 turn 처리.

---

## 1. 다음 작업 = PR-AA — intent-refresh 2→1

**대상** :
- `skills/theseus-harness/conventions/intent-refresh-post-interview.md` (by, sprint-17, 130 라인) — phase 04 → 05 사이 1차 refresh
- `skills/theseus-harness/conventions/intent-refresh-post-critique.md` (ci, sprint-19, 102 라인) — phase 05 → 06 사이 2차 refresh

**통합 후** : `intent-refresh.md` (~200 라인 예상, phase param 분기)

**선정 사유** (`diet-analysis.md` §7) :
- 책임 단순 (의도 refresh 1 가지) + phase param 으로 명확 분기
- 의존 최소 (autonomy / contracts / cross-phase-shared-context 만)
- runtime infra 0 (별도 .py 없음)
- self_lint 룰 2 (C-IRPI / C-IRPC) — 통합 컨벤션 한 파일에서 reference 가능

---

## 2. 통합본 골격 (`intent-refresh.md`)

```markdown
---
id: intent-refresh
category: interview
applies-to-phases: '[04,05]'
applies-to-grades: '[all]'
trigger-when: 'phase 04 종료 / phase 05 종료'
indexed-in: conventions/INDEX.md
---

# Intent Refresh — phase 04 / 05 종료 후 의도 재구성

## 한 줄 요약
**페이즈 04 종료 (1차) + 페이즈 05 종료 (2차) 두 시점에 의도를 4 universe + cascade refresh 로 재구성.**
1차 = 인터뷰 답 흡수해 stale 01-intent 교체.
2차 = critique 인사이트 흡수해 v2 cascade.

## 1. 결손 진단 (공통)
- phase 01 의도 = 인터뷰 이전 추측 → stale
- phase 04 답 / phase 05 critique 가 드러낸 갭이 plan 으로 흐르지 못함
- single refresh = framing-bias 잔존 → 4 universe multiverse 로 분산 의무

## 2. 트리거 — phase param 분기

### 2.1 Phase 04 종료 (1차 refresh, sprint-17 by)
- 산출: 5 (4 universe v1 + 01-additional)
- 트리거: phase 04 6 산출물 완성 직후, phase 05 진입 *전*
- 자동 — 사용자 ack 0 (페이즈 04 외 인터럽트 0 정합)

### 2.2 Phase 05 종료 (2차 refresh, sprint-19 ci)
- 산출: 6 (4 universe v2 + 04-refreshed + 05-refreshed)
- 트리거: phase 05 critique + decisions 완성 직후, phase 06 진입 *전*
- 자동 — 사용자 ack 0

## 3. 산출물

### 3.1 1차 refresh — 5 산출물
[intent-refresh-post-interview.md §3 본문 그대로 흡수]

### 3.2 2차 refresh — 6 산출물
[intent-refresh-post-critique.md "의무 산출물" 본문 그대로 흡수]

## 4. 4 framing universe (공통)
[intent-refresh-post-interview.md §4 표 그대로 흡수 — domain / constraint / risk / outcome paradigm]

## 5. self_lint

### 5.1 C-IRPI (1차)
[intent-refresh-post-interview.md §6 표 5 룰 그대로]

### 5.2 C-IRPC (2차)
[intent-refresh-post-critique.md self_lint 본문 그대로]

## 6. phase 06 plan 진입 게이트
[intent-refresh-post-critique.md §"phase 06 plan 진입 게이트 갱신" 본문 그대로]

## 7. 안티 패턴
[양쪽 §"안티 패턴" 통합 — 1차/2차 분기 표시]

## 8. 호환성
[양쪽 §"호환성" 통합 — 중복 제거]

## 9. cold session 검증
[양쪽 §"cold session 검증" 통합 — 1차/2차 분기]
```

**예상 라인** : ~200 (현 232 라인 합계 → -32 라인 감소).

---

## 3. PR-AA 작업 절차 (8 단계)

### 단계 1 — 브랜치 생성

```bash
# main 머지 후 가정
git checkout main && git pull
git checkout -b feat/sprint-37-pr-aa-intent-refresh

# 머지 안 됐으면 stack
# git checkout feat/sprint-37-diet-analysis && git pull
# git checkout -b feat/sprint-37-pr-aa-intent-refresh
```

### 단계 2 — 통합본 작성
- `skills/theseus-harness/conventions/intent-refresh.md` 신규 (위 §2 골격 따라 작성)
- 양쪽 본문 통합 시 *공통* 부분은 한 번만 박음, *분기* 부분은 §2.1 / §2.2 등으로 명확 라벨

### 단계 3 — 페이즈 04, 05 본문 cross-ref 갱신

```bash
grep -rn "intent-refresh-post-interview\|intent-refresh-post-critique" \
  skills/theseus-harness/phases/ skills/theseus-harness/HARD-CORE.md \
  skills/theseus-harness/SKILL.md skills/theseus-harness/README.md
```

발견되는 모든 reference 를 `intent-refresh.md` 로 갱신. 특히 :
- `phases/04-clarify.md` (post-interview reference)
- `phases/05-critique.md` (post-critique reference)
- `HARD-CORE.md` 9.kk 등 (sprint-19 도입 룰)
- 기존 컨벤션의 cross-link (`mindmap-richness-default.md`, `cross-phase-shared-context.md` 등)

### 단계 4 — 2 컨벤션 파일 삭제

```bash
git rm skills/theseus-harness/conventions/intent-refresh-post-interview.md
git rm skills/theseus-harness/conventions/intent-refresh-post-critique.md
```

(plan.md §3.1.2 의 1 sprint grace 는 본 sprint 안에서 즉시 제거 — sprint-37 자체가 다이어트 sprint, grace 의미 약함. MIGRATION.md 매핑은 보존.)

### 단계 5 — INDEX.md 갱신

- 2 행 삭제 : `intent-refresh-post-interview` / `intent-refresh-post-critique`
- 1 행 신규 : `intent-refresh | interview | [04,05] | [all] | always`
- 카운트 갱신 : `**90 컨벤션**` → `**89 컨벤션**` (라인 117 부근 + 라인 3 부근 narrative)

### 단계 6 — MIGRATION.md 매핑 추가

```markdown
| intent-refresh-post-interview | intent-refresh | sprint-37 PR-AA | sprint-37 PR-AA | 책임 단순, phase param 통합 |
| intent-refresh-post-critique | intent-refresh | sprint-37 PR-AA | sprint-37 PR-AA | 동일 |
```

`(현재 비어 있음)` 행 삭제 + 위 2 행 추가.

### 단계 7 — self_lint 검증

```bash
python skills/theseus-harness/scoring/self_lint.py 2>&1 | python -c "import sys,json; d=json.loads(sys.stdin.read()); failed=[c for c in d['checks'] if not c['ok']]; print(f'all_ok={d[\"all_ok\"]} failed={len(failed)}/{len(d[\"checks\"])}'); [print(f'  {c[\"code\"]}: {c[\"issues\"][:1]}') for c in failed]"
```

기대 : `all_ok=True 0/114` (또는 신규 self_lint 룰 추가 시 0/116 등).

C-IRPI / C-IRPC 룰이 *컨벤션 파일 키워드 검사* 를 한다면 통합본에 키워드 모두 박혔는지 검증. self_lint 본문 grep:

```bash
grep -n "C-IRPI\|C-IRPC\|intent-refresh-post" skills/theseus-harness/scoring/self_lint.py
```

self_lint 본문이 컨벤션 파일명을 hardcode 한다면 self_lint 도 동시 갱신 필요.

### 단계 8 — commit + push + PR

```bash
git add -A
git commit -m "$(cat <<'COMMIT'
feat(sprint-37): PR-AA — intent-refresh 2→1 통합

- intent-refresh-post-interview (sprint-17 by, 130) + intent-refresh-post-critique (sprint-19 ci, 102) → intent-refresh (~200, phase param 분기)
- 페이즈 04/05 본문 cross-ref 갱신
- HARD-CORE 9.kk reference 갱신
- INDEX.md 2 행 → 1 행, 카운트 90 → 89
- MIGRATION.md 2 행 추가
- self_lint: all_ok=True

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
COMMIT
)"
git push -u origin feat/sprint-37-pr-aa-intent-refresh

"/c/Program Files/GitHub CLI/gh.exe" pr create \
  --title "feat(sprint-37): PR-AA — intent-refresh 2→1" \
  --body "..." # 본 handoff 의 §1, §2 인용
```

---

## 4. 위험 신호 + 처리

| 신호 | 처리 |
|---|---|
| 통합본이 ~250 라인 초과 (현 232 라인 합계 못 줄임) | 1차/2차 책임 분기가 너무 넓음 → PR-AA 보류, 다음 묶음 (PR-AB aide-tree) 으로 진행 |
| self_lint 의 C-IRPI / C-IRPC 가 hardcode 컨벤션 파일명 검사 | self_lint 갱신 (PR scope 확장 합리) — `_CONVENTION_META_FILES` 패턴 따라 통합 처리 |
| HARD-CORE.md 의 9.kk 룰이 직접 본문 reference (e.g., `intent-refresh-post-critique 의 6 산출물`) | reference 갱신 + HARD-CORE 길이 임계 4400 chars 정합 확인 |
| 페이즈 04, 05 외 다른 페이즈 (06, 07 등) 가 cross-ref | grep 결과 모두 갱신, 누락 시 self_lint C-CT (convention-traceability) fail |
| C-IRPI 와 C-IRPC self_lint 룰이 *별도 함수* 로 정의 | 두 함수 보존 + 통합 컨벤션 파일에서 둘 다 키워드 검출되도록 작성 (가장 안전) |

---

## 5. 후속 PR 시리즈 (참고 — `plan.md` §8)

| PR | scope | 추정 변경량 |
|---|---|---|
| **PR-AA** ★ 본 핸드오프 | intent-refresh 2→1 | 작음 (-32 라인, 1 self_lint 갱신 가능) |
| PR-AB | aide-tree 2→1 | 작음 (-100, 본문 작음) |
| PR-AC | viewer-auto-refresh + viewer-runtime-lifecycle 2→1 | 중간 (runtime infra 검토 필요) |
| PR-AD | mindmap 3→1 | 큼 (3 컨벤션 + 페이즈 01/06 본문) |
| PR-AE | regression 2→1 | 중간 |
| PR-AF | sprint-narrative 3→1 (lessons 포함) | 큼 (lessons 228 라인) |
| PR-AG | domain 3→1 | 큼 (도메인 어댑터 영향) |
| PR-AH | canonical-not-stub inline → phases/06,08,14 | 작음 (페이즈 본문 +80 라인) |
| PR-AI | timing inline → phases/00,14 | 작음 (-75) |
| PR-AJ | stack inline → phases/04 | 작음 (-100) |
| PR-AK | self_lint 통합 + version bump v0.9.42 | 마감 PR |

각 PR 마다 본 handoff.md 를 *템플릿* 으로 사용 — "intent-refresh" → 대상 컨벤션 치환 + 본문 분석 추가.

---

## 6. 본 세션 마감 요약 (2026-05-09)

### 본 세션 진행
- PR #61 plan.md (sprint-37 방향 + 3 트랙 + 4 축)
- PR #62 다이어트 분석 + MIGRATION 골격 + self_lint exception (META_FILES 상수)

### 발견 사실
- **plan.md §3.1.4 의 inline 4 후보 과소평가** : subagent-trigger / phase-state-machine / canonical-not-stub / runtime-prereq 중 3개가 self_lint 룰 + runtime infra 동반 → inline 단순 흡수 불가. *카테고리 C* 로 재분류 (분리 유지).
- **PR scope 1 회 = 1 묶음** : 단일 PR 검증 부담 회피. 후속 PR-AA~AJ 11 분할.

### 메모리 신규 (영구화)
- `feedback_convention_diet_paradigm.md` — 누적 패치 → 다이어트+본체 패러다임 전환
- `feedback_deliverable_path_user_confirm.md` — 산출물 경로 + user-confirm 게이트

### 메모리 미저장 (sprint 산출물로 trace)
- sprint-37 PR-A 진행 사실 = 본 handoff.md + plan.md + diet-analysis.md = 영구 trace
- sprint 마감 후 `project_sprint37_v0942.md` 메모리 신규 (PR-AK 머지 시점)

---

## 7. 다음 세션 시작 트리거

다음 세션이 본 sprint 이어가려면 :

1. 본 디렉토리 (`.ShipofTheseus/sprints/37/`) 의 3 파일 read :
   - `plan.md` (방향)
   - `diet-analysis.md` (분석 + 후속 PR 분할안)
   - `handoff.md` (본 문서, 다음 작업 가이드)
2. `git log --oneline main..HEAD` 로 PR #61, #62 머지 상태 확인
3. §3 단계 1 부터 진행

본 세션 컨텍스트 손실 시에도 위 3 파일 + 메모리 (`feedback_convention_diet_paradigm` + `feedback_deliverable_path_user_confirm`) 만으로 정합 진행 가능.
