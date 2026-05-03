---
skill_name: theseus-harness
skill_version: 0.3.0
phase: 06-plan
project_id: theseus-self
project_run: sprint-01
fingerprint: PENDING
prev_fingerprint: 00-review-design-v4
produced_at: 2026-05-03
producer_agent: writing-plans-skill (외부 메타)
spec_source: .ShipofTheseus/theseus-self/sprints/01/00-review-design.md (v4)
plan_revision: v1
---

# Sprint-01 Borrow Plan — 본 하네스 자기 리뷰 + 보완 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** v0.3.0 본 하네스의 *자기 리뷰 + 보완* 을 9 머스트 + 2 선택 PR 로 완료. 거울 원칙 (외부 차용은 사각지대 탐지용 거울만, 합성 X) + 감산 차원 (description 압축 / 컨벤션 통합 / anti-pattern 통합) 을 준수해 *영구 추가 0 + 영구 감산 다수* 를 달성.

**Architecture:** 부트스트래핑 sprints/01 — 본 하네스의 비평/계획/구현/게이트/스프린트 페이즈를 본 저장소를 입력으로 자기 적용. PR 단위 1 커밋, 거울 매트릭스 부록이 강점 부각 메인 채널, 신규 self_lint C36~C42 가 PR 별 회귀 가드. 출력은 *부트스트래핑 트리* (디자인 + 계획 + 회차 산출물) + *일반 git 브랜치* (실제 코드 변경) 하이브리드.

**Tech Stack:**
- Python 3 — `scoring/self_lint.py`, `scoring/fingerprint.py`, `scoring/score.py` (기존), 신규 체크 함수만 추가
- Bash + Windows BAT — `scripts/self-check.{sh,bat}` 확장 (sprint 시계열)
- Markdown — 9 SKILL.md, 28 컨벤션, 14 페이즈, 13 에이전트, README, INSTALL, PHILOSOPHY 갱신
- TOML — (PR-3 의 opt-in 보조 천정 schema 만, 기존 컨벤션 본문에 명시 — 새 파일 X)
- Pytest — 기존 `test_skill_handoff.py + test_score.py + test_self_lint.py` 회귀 0 보증

**브랜치:** `feat/v0.4.0-self-review-and-mirrors` (또는 v0.3.1 패치 — 메인테이너 결정. 감산 PR 만 머지 시 v0.3.1, 메서돌로지 절 + 모든 PR 머지 시 v0.4.0).

**임계:** sprint-01 self_score ≥ 0.99999 유지 (1차 1.000000 회귀 0).

---

## File Structure

PR 별 영향 파일 (Create/Modify) 명시:

```
[PR-1: 분해 stub 단독성]
  Modify: skills/theseus-{orchestrator,intent,plan,implement,quality,sprint,webview,handoff}/SKILL.md (8 stub)
  Modify: README.md (단독 호출 주장 정정 if needed)
  Modify: skills/theseus-harness/scoring/self_lint.py (C36 추가)

[PR-2: INSTALL.md fresh-user prep]
  Modify: INSTALL.md (한 절 추가)
  Modify: scripts/self-check.{sh,bat} (첫 줄 stack 점검)
  Modify: skills/theseus-harness/scoring/self_lint.py (C37 추가)

[PR-3: resources.md opt-in 보조 천정]
  Modify: skills/theseus-harness/conventions/resources.md (한 절 추가)
  Modify: skills/theseus-harness/conventions/autonomy.md (Q-D3 sub-option 흡수 표기)
  Modify: skills/theseus-harness/scoring/self_lint.py (C38 추가)

[PR-7: 메서돌로지 절]
  Modify: PHILOSOPHY.md (한 절 추가 — 블라인드 스팟 메서돌로지)
  Modify: README.md (한 단락 추가 — 동결 예외 언급)

[PR-8: 부록 — 강점 부각 + 감산 변경표 (살아있는 문서)]
  Create: docs/reviews/2026-05-03-skill-self-review.md

[PR-9: sprint 시계열 자동화]
  Modify: scripts/self-check.{sh,bat} (sprint 디렉터리 자동 인식)
  Modify: skills/theseus-harness/scoring/score.py 또는 신규 헬퍼 (시계열 표 생성)
  Modify: BOOTSTRAP.md (시계열 절차 갱신)

[PR-11: anti-patterns 통합]
  Modify: skills/theseus-harness/SKILL.md (한 통합 절 추가)
  Modify: skills/theseus-harness/phases/{00..13}-*.md (페이즈별 "흔한 실패" 절을 *고유한 실패만* 으로 좁힘)
  Modify: skills/theseus-harness/scoring/self_lint.py (C40 추가)

[PR-12: SKILL.md description 압축 (감산)]
  Modify: skills/theseus-{harness,orchestrator,intent,plan,implement,quality,sprint,webview,handoff}/SKILL.md (9 stub)
  Modify: skills/theseus-harness/scoring/self_lint.py (C41 추가)

[PR-13: 컨벤션 통합 (감산)]
  Modify: skills/theseus-harness/conventions/{lessons,dacapo,interview,prd-handling}.md (식별된 중복 페어)
  Delete: 통합 후 흡수된 컨벤션 파일 (1~3 개)
  Modify: skills/theseus-harness/SKILL.md (인덱스 갱신)
  Modify: skills/theseus-harness/scoring/self_lint.py (C42 추가)

[PR-10 선택: HARD-RULE 마크업]
  Modify: skills/theseus-{*}/SKILL.md (9 stub 의 "하드 룰" 절)
  Modify: skills/theseus-harness/scoring/self_lint.py (C39 추가)

[PR-14 선택: allowed-tools 페이즈별 선언]
  Modify: skills/theseus-harness/phases/*.md (frontmatter 에 allowed-tools 추가)
  Modify: skills/theseus-harness/scoring/self_lint.py (C43 추가)

[Bootstrapping artifacts — sprint 회차 산출물]
  Create: .ShipofTheseus/theseus-self/sprints/01/intent/05-critique-vs-mirrors.md
  Create: .ShipofTheseus/theseus-self/sprints/01/impl/08-impl-log.md (PR SHA 표)
  Create: .ShipofTheseus/theseus-self/sprints/01/quality/09-quality-gate.md
  Create: .ShipofTheseus/theseus-self/sprints/01/report.md
```

---

## Execution DAG

```
[선행]
Task 1: PR-7 (메서돌로지 절) ── 모든 후속 PR 의 정당화

[강점 매트릭스 초안]
Task 2: PR-8 draft (부록 초안 — 10 차원 강점 + 거울 매트릭스 + 의도된 한계)

[가산 PR — 병렬 가능]
Task 3: PR-1 (분해 stub 단독성)
Task 4: PR-2 (INSTALL.md fresh-user prep)
Task 5: PR-3 (resources.md opt-in 보조 천정)
Task 6: PR-9 (sprint 시계열 자동화)
Task 7: PR-11 (anti-patterns 통합)

[감산 PR — 직렬 (회귀 위험 최대)]
Task 8: PR-12 (description 압축)
Task 9: PR-13 (컨벤션 통합)

[부록 갱신]
Task 10: PR-8 final (부록 — 모든 PR 의 SHA + 영향 표 추가)

[게이트 + 보고]
Task 11: 회차 게이트 + report.md (sprint-01 self_score 시계열)

[선택 — 다음 회차로 미뤄도 무방]
Task 12 (선택): PR-10 (HARD-RULE 마크업)
Task 13 (선택): PR-14 (allowed-tools)
```

---

## Task 1: PR-7 — 블라인드 스팟 메서돌로지 절 (선행)

**근거:** 사용자 피드백 2 회 (v1→v2, v2→v3, v3→v4) 의 *원칙* 을 PHILOSOPHY/README 에 컨벤션화. 후속 모든 PR (특히 PR-12, 13 의 감산) 의 *정당화* 가 본 절에 박힘.

**Files:**
- Modify: `PHILOSOPHY.md` (새 절 — "블라인드 스팟 메서돌로지" + "외부는 거울")
- Modify: `README.md` (한 단락 — 동결 예외 + 메서돌로지 링크)

- [ ] **Step 1: PHILOSOPHY.md 의 적절한 위치 식별**

기존 § "## 합성한 패턴" 섹션 직후, "## 매핑한 방법론" 섹션 직전에 새 절 삽입.

```bash
grep -n "^## 합성한 패턴\|^## 매핑한 방법론" PHILOSOPHY.md
```

Expected: 두 줄 출력, 합성한 패턴 시작 줄 + 매핑한 방법론 시작 줄.

- [ ] **Step 2: PHILOSOPHY.md 에 새 절 추가**

`## 합성한 패턴` 섹션 끝 (다음 `##` 직전) 에 다음 추가:

```markdown
## 외부 패턴 차용 메서돌로지 — *거울 원칙*

본 하네스가 합성한 6 패턴 (Ralph / OhMy / 우로보로스 / AIDE / Wiki / Da Capo) 은 *완료된 흡수* 다. 본 하네스 외 다른 외부 스킬 (oh-my-ralph, superpowers, OMC, autoresearch, frontend-design 등) 을 *추가 차용* 검토할 때 본 메서돌로지가 강제된다:

ⓐ **본래 스킬이 1순위** — 기존 14 페이즈 / 28 컨벤션 / 13 에이전트의 컨셉을 *최대한 보존*. 차용은 본 하네스를 대체/덮어쓰는 행위가 아니라 *블라인드 스팟 감지를 위한 비교 거울* 이다.
ⓑ **외부 = 참조용 거울** — 외부 패턴을 보는 이유는 "이걸 가져오자" 가 아니라 "본 하네스가 *어디를 놓쳤는지* 외부의 시선으로 발견" 이다.
ⓒ **차용 오더 = 자동 합성 면허 아님** — "차용 가능" 은 *후보 검토 권한* 일 뿐 *합성 의무* 가 아니다. 외부 원자 대부분이 "본 하네스가 다르게 이미 답함" 으로 끝나는 게 정상.
ⓓ **중복 기능은 중첩 금지** — 외부 원자 X 가 본 하네스 원자 Y 와 *같은 축의 다른 구현* 이면 X 를 새로 추가하지 말 것. 본 하네스 컨셉을 흐리는 행위.
ⓔ **상호보완 축 (직교 차원) 만 차용 정당** — 외부 원자가 *본 하네스의 어떤 축으로도 답 안 한 새 차원* 을 짚을 때만 차용. 그 경우에도 *새 파일* 보다 *기존 파일 한 단락 증강* 우선.
ⓕ **동결 예외** — v0.3.0 정직 박스 ⓓ 의 *"외부 실 프로젝트 적용 1 건 전까지 새 컨벤션·도구 추가 동결"* 은 본 메서돌로지의 결과로 자연스럽게 흡수된다 — *직교 차원 + 기존 증강만* 이 동결 예외, *새 파일 추가* 는 동결 그대로.

본 메서돌로지 적용 회차는 [`.ShipofTheseus/theseus-self/sprints/01/`](.ShipofTheseus/theseus-self/sprints/01/) — 본 하네스가 자기 자신에게 거울 원칙을 적용한 첫 부트스트래핑 회차.
```

- [ ] **Step 3: README.md 의 정직 박스 직후에 한 단락 추가**

`> **v0.2.x 는 자기 평가만 통과한 스캐폴드입니다.` 로 시작하는 박스 직후, `## 왜 "테세우스의 배" 인가` 섹션 직전에 추가:

```markdown
> ⓕ **외부 차용 메서돌로지 — 거울 원칙** (v0.4.0 신규): oh-my-ralph 등 외부 스킬은 *사각지대 탐지용 거울* 로만 사용. *합성 source 가 아님*. 차용은 본 하네스의 *컨셉 보존* 우선, *직교 차원 입증 시* 만 *기존 한 단락 증강*. 자세한 메서돌로지는 [`PHILOSOPHY.md`](PHILOSOPHY.md) "외부 패턴 차용 메서돌로지" 절. 본 메서돌로지가 v0.3.0 정직 박스 ⓓ 의 *동결 룰* 을 자연스럽게 흡수 — 동결 예외는 *직교 차원 + 기존 증강만* 으로 좁아짐.
```

- [ ] **Step 4: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true`. C6 (PHILOSOPHY ↔ SKILL 상호 링크) 는 변경 영향 없음.

- [ ] **Step 5: Commit**

```bash
git add PHILOSOPHY.md README.md
git commit -m "$(cat <<'EOF'
v0.4.0 — 블라인드 스팟 메서돌로지 절 (PR-7)

PHILOSOPHY 에 거울 원칙 신설 — 외부 패턴은 사각지대 탐지용,
합성 source 아님. 동결 예외도 본 메서돌로지가 흡수.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: PR-8 draft — 부록 초안 (강점 부각 메인)

**근거:** 본 회차 *핵심 산출물*. 다른 PR 들의 정당성 매트릭스. *살아있는 문서* — Task 10 에서 SHA 추가로 amend.

**Files:**
- Create: `docs/reviews/2026-05-03-skill-self-review.md`

- [ ] **Step 1: 디렉터리 생성 및 파일 작성**

```bash
mkdir -p docs/reviews
```

- [ ] **Step 2: 부록 초안 작성**

`docs/reviews/2026-05-03-skill-self-review.md` 에 다음 내용 작성:

```markdown
# Sprint-01 자기 리뷰 — 본 하네스 강점 부각 + 거울 매트릭스 + 감산 변경표

> **컨텍스트:** v0.3.0 → v0.4.0 의 부트스트래핑 회차 sprint-01. 본 하네스가 자기 자신에게 *거울 원칙* 을 적용한 첫 회차. 디자인 스펙: [`.ShipofTheseus/theseus-self/sprints/01/00-review-design.md`](../../.ShipofTheseus/theseus-self/sprints/01/00-review-design.md) v4.

## 1. 거울 원칙

(PHILOSOPHY.md "외부 패턴 차용 메서돌로지" 절의 6 항 ⓐ~ⓕ 인용)

## 2. Claude Skills Guide 정합 매트릭스 (10 조항)

| 조항 | 본 하네스 대응 | 정합 |
|--|--|--|
| name (lowercase + hyphens) | 9 스킬 모두 | ✓ |
| description (1~2 줄) | v0.4.0 PR-12 로 *압축 완료* — 600자 → 100~150자 | △ → ✓ (PR-12 후) |
| examples | examples/ 3 시나리오 (v0.3.0) | ✓ |
| anti-patterns (when NOT to use) | description + grades.md G1 자동 거부 | ✓ |
| discoverability | description 키워드 + 슬래시 명령 | ✓ |
| tool permissions | 미선언 — *본 하네스 컨셉 정합* (페이즈별 광범위 사용) | △ (보존, PR-14 선택 적용 시 ✓) |
| HARD-GATE 마크업 | 텍스트 명시 ("하드 룰" 절) — 마크업은 PR-10 선택 | △ (보존) |
| process flow diagram | Mermaid 마인드맵 + 시퀀스 + 자동 웹뷰 | ✓ (오히려 더 풍부) |
| skill priority | theseus-orchestrator 단일 진입점 | ✓ |
| single SKILL.md | *명시 분해* (fragmentation 컨셉) | △ (의도된 trade-off) |

→ 7 직접 정합 + 3 컨셉 trade-off (description 길이는 PR-12 로 부분 해소 / 단일 파일 미준수는 컨셉 보존 / tool permissions 는 PR-14 선택).

## 3. 멀티 스킬 거울 매트릭스

### 3-1. oh-my-ralph (9 원자)

| 원자 | 결정 | 본 하네스 답안 |
|--|--|--|
| RALPH.md 6 섹션 | 드롭 (부록만) | 14 페이즈 + Q-D 8 사전 위임 + frontmatter 봉인 (더 풍부) |
| Verification Commands | 차용 완료 (Q-D8, v0.3.0) | n/a |
| Visual Spec (RALPH.png + clarify-image) | 드롭 | 마인드맵 + Mermaid + 자동 웹뷰 (시각 축 답) |
| .ralph/bootstrap.sh | 기존 증강 (PR-2) | INSTALL.md 한 절 (직교 차원) |
| .ralph/check.sh | 드롭 | scripts/self-check.{sh,bat} 가 답 |
| .ralph/run.sh (wall-clock) | 기존 증강 (PR-3) | resources.md opt-in 한 절 (직교, 컨셉 충돌 명시) |
| .ralph/config | (PR-3 통합) | 위와 통합 |
| Success Criteria 1:1 | 차용 완료 (Q-D8) | n/a |
| Risks 누적 ("Do not remove") | 드롭 | frontmatter 봉인 + 회차 디렉터리 (자동화) |
| 메타 CLI 부재 | 드롭 | orchestrator 가 *의도된* 메타 레이어 |

### 3-2. superpowers (9 원자)

| 원자 | 결정 | 본 하네스 답안 |
|--|--|--|
| HARD-GATE 마크업 | 선택 증강 (PR-10) | "하드 룰" 절 텍스트 (의미는 동일) |
| Skill 자기 호출 계층 | 드롭 | orchestrator → 8 분해 (frontmatter 봉인 자동) |
| Red Flags 안티 패턴 표 | 머스트 증강 (PR-11) | 페이즈별 분산 → 통합 카탈로그로 |
| brainstorming HARD-GATE | 드롭 | grades.md G1 자동 거부 + Phase 04 인터뷰 의무 |
| TDD red-green-refactor | 드롭 | sprint 루프 + PHILOSOPHY ⓐ 매핑 |
| systematic-debugging | 드롭 | Phase 11 회귀 바이섹트 + 멀티버스 (더 풍부) |
| finishing-a-development-branch | 드롭 | Phase 13 핸드오프 |
| verification-before-completion | 차용 완료 (Q-D8) | n/a |
| writing-skills | 무관 | n/a |

### 3-3. OMC (5 원자) + autoresearch (4 원자)

(같은 형식 매트릭스 — 모두 *같은 축 / 더 풍부* 또는 무관)

## 4. 본 하네스만의 10 차원 강점 (v4 정직 조정 — 12 → 10)

| # | 차원 | 본 하네스 답 | 외부 답 |
|--|--|--|--|
| 1 | 부트스트래핑 (자기 적용 + 회차 시계열) | BOOTSTRAP.md + .ShipofTheseus/theseus-self/ + self_lint + 임계 0.99999 | (없음) |
| 2 | 그레이드 시스템 + G1 자동 거부 | grades.md + grade_assess.py + Q-G1 | superpowers HARD-GATE 부분 매핑 |
| 3 | frontmatter 핑거프린트 체인 (페이즈 재진입) | contracts.md + fingerprint.py | (없음) |
| 4 | 35 self_lint 자기 검증 | self_lint.py + scripts/self-check.* | (없음) |
| 5 | 14 페이즈 분해 깊이 | 명명→의도→마인드맵→재이해→인터뷰→비평→계획→재이해→구현→게이트→스프린트→바이섹트→웹뷰→핸드오프 | RALPH.md 6 / autoresearch 단일 보다 풍부 |
| 6 | **합성 패턴의 단단한 흡수** (v4 정직 조정) | Ralph + OhMy + 우로보로스 + AIDE + Wiki + Da Capo 6 패턴 명시 차용 + 자기 점수 검증 + 멀티버스 (닥터 스트레인지) | (다른 스킬은 *자신의 패턴* 만, 합성 메서돌로지 부재) |
| 7 | 도자기 장인 — 깨고 다시 빚기 6 차원 트리거 | PHILOSOPHY (DIP / 코드 오류 / 기획-구현 갭 / NFR / 의도 표류 / 정체) | (없음) |
| 8 | DIP 단독 hard cap | quality-gate 5 게이트 + DIP cap 0.6 | (없음 — 다른 스킬은 SOLID 동등) |
| 9 | Phase 04 *유일* 인터럽트 + Q-D 사전 위임 | autonomy.md + Q-D1~D8 | (없음 — autonomy 강한 약속 부재) |
| 10 | bun + hono + react 자동 웹뷰 | webview-builder + Phase 12 + 6 탭 + Mermaid 자동 + TimingHeader | (없음) |

(v3 의 12 → v4 의 10: #6 멀티버스 + #12 합성 패턴 → "합성 패턴의 단단한 흡수" 1 차원으로 통합)

## 5. 본 하네스의 의도된 한계 (컨셉 정당화)

ⓐ description 길이 — PR-12 로 부분 해소 (600 → ~150자), 그러나 *anti-pattern + when-to-use* 절은 보존
ⓑ 단일 SKILL.md 미준수 — fragmentation 컨셉, 보존
ⓒ tool permissions 비선언 — 페이즈별 광범위, PR-14 선택
ⓓ 이미지 입력 미커버 — 텍스트 기반 컨셉
ⓔ Phase 04 외 verification 실행 미요구 — LLM/사용자 책임 분리
ⓕ 메타 CLI 레이어 (orchestrator) — *의도된* 메타

## 6. 감산 변경표 (v4 신규)

### 6-1. SKILL.md description 압축 (PR-12)

| 스킬 | 변경 전 길이 | 변경 후 길이 | 이전된 디테일 |
|--|--|--|--|
| theseus-harness | TBD (PR-12 머지 후 갱신) | TBD | PR-12 머지 후 갱신 |
| ... (8 stub) | TBD | TBD | TBD |

### 6-2. 컨벤션 통합 (PR-13)

| 통합 후 컨벤션 | 흡수된 원본 | 영향 라인 수 | self_lint C2 갱신 |
|--|--|--|--|
| TBD | TBD | TBD | TBD |

(PR-13 머지 후 갱신)

### 6-3. anti-pattern 통합 카탈로그 (PR-11)

| 통합 위치 | 흡수된 페이즈 본문 | 페이즈별 *고유* 실패만 남김 |
|--|--|--|
| TBD | TBD | TBD |

## 7. 다음 회차 후보 (sprint-02 candidates)

ⓐ 첫 외부 실 프로젝트 적용 1 건 + 4 메트릭 post-mortem
ⓑ 선택 PR-10 (HARD-RULE 마크업) / PR-14 (allowed-tools) 머지
ⓒ 추가 거울 비교 (frontend-design / claude-hud / ...)

## 8. PR 머지 SHA + 영향 표 (Task 10 에서 채움)

| PR | SHA | diff 라인 | 영향 파일 수 | self_lint 신규 |
|--|--|--|--|--|
| PR-7 | TBD | TBD | TBD | (없음) |
| ... | TBD | TBD | TBD | TBD |
```

- [ ] **Step 3: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true`. (docs/reviews/* 는 self_lint scope 밖)

- [ ] **Step 4: Commit**

```bash
git add docs/reviews/2026-05-03-skill-self-review.md
git commit -m "$(cat <<'EOF'
v0.4.0 — 부록 초안 (PR-8 draft)

10 차원 강점 + 거울 매트릭스 (ralph + superpowers + OMC + autoresearch)
+ 의도된 한계 + 감산 변경표 placeholder. 후속 PR 머지 후 §8 SHA 표 갱신.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: PR-1 — 분해 stub 단독 실행성 (주장 vs 행동 정합)

**근거:** 컴포넌트 A2 실증 — 분해 stub 의 본문은 모두 `../theseus-harness/...` 점프. fresh user 가 분해 스킬 1 개만 클론 시 dead link 숲. *주장 정정* 또는 *최소 사용 가이드 추가* 둘 중 정직한 답을 골라 적용.

**Files:**
- Modify: `skills/theseus-{orchestrator,intent,plan,implement,quality,sprint,webview,handoff}/SKILL.md` (8 stub)
- Modify: `README.md` (필요 시 단독 호출 주장 정정)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C36 추가)

- [ ] **Step 1: 정적 분석 — 분해 stub 본문의 외부 점프 카운트**

Run:
```bash
for d in skills/theseus-{orchestrator,intent,plan,implement,quality,sprint,webview,handoff}; do
  echo "=== $(basename $d) ==="
  grep -c "\.\./theseus-harness/" "$d/SKILL.md" 2>/dev/null
done
```

Expected: 각 stub 의 외부 점프 횟수가 출력 (대부분 5~15 사이 — 본문이 모두 점프임을 확인).

- [ ] **Step 2: 결정 — 정정 vs 보강**

각 stub 의 본문이 *어떤 phase/agent/convention 본문 없이* 단독으로 페이즈 진행 가능한지 평가. **현재 가설: 모두 불가능 — 본문이 위임 + 인터페이스만**.

→ 결정: *주장 정정 + 최소 사용 placeholder*. README/SKILL.md 의 "단독 호출 가능" 주장을 *"단독 호출 시 theseus-harness/ 동반 필요"* 로 정정 + 각 stub 에 "단독 호출 시 필요한 산출물 placeholder" 절 추가.

- [ ] **Step 3: 각 stub 의 "단독 호출" 절 정정 (theseus-plan 예시)**

`skills/theseus-plan/SKILL.md` 의 기존 "단독 호출" 절 (50-57 줄):

기존:
```markdown
## 단독 호출

```bash
/theseus-plan --from <input_dir>
```
```

→ 다음으로 정정:
```markdown
## 단독 호출 (재진입)

> **단독 호출 시 의존성:** 본 stub 은 *위임 + 인터페이스* 만. 룰 본문은 [`../theseus-harness/`](../theseus-harness/) 단일 source 에 위치. **fresh user 가 본 stub 만 설치하면 본문 점프가 모두 dead link** — 본 저장소 전체 또는 최소 [`../theseus-harness/`](../theseus-harness/) 동반 설치 필요.

```bash
# 반드시 theseus-harness 동반 설치 후
/theseus-plan --from <input_dir>
```

`<input_dir>` 의 frontmatter 가 본 스킬의 *입력 계약* 을 만족하면 진입.
```

- [ ] **Step 4: 위 패턴을 7 분해 stub 모두 적용**

대상:
- `skills/theseus-orchestrator/SKILL.md`
- `skills/theseus-intent/SKILL.md`
- `skills/theseus-plan/SKILL.md`
- `skills/theseus-implement/SKILL.md`
- `skills/theseus-quality/SKILL.md`
- `skills/theseus-sprint/SKILL.md`
- `skills/theseus-webview/SKILL.md`
- `skills/theseus-handoff/SKILL.md`

각 stub 에 동일 정신의 정정 ("단독 호출 시 theseus-harness 동반 필요" 명시).

- [ ] **Step 5: README.md 의 "단독 호출 가능" 주장 정정**

`README.md` 의 "수록 스킬 (9 개)" 표 직후 단락 (대략 60-62 줄) 에서:

기존: `| theseus-harness | **플래그십.** 21 컨벤션 + ... 분해 스킬 없이 단독 호출도 가능. |`

→ 다음으로 정정:
```markdown
| `theseus-harness` | **플래그십.** 21 컨벤션 + 14 페이즈 + 13 에이전트 + 채점기를 모두 담은 단일 source of truth. **분해 스킬 없이 단독 호출 가능 — 분해 stub 은 본문이 본 플래그십 점프이므로 fresh user 가 분해 stub 만 설치하면 dead link.** | [docs/skills/theseus-harness.md](docs/skills/theseus-harness.md) |
```

- [ ] **Step 6: self_lint.py 에 C36 추가**

`skills/theseus-harness/scoring/self_lint.py` 의 함수 정의 영역 (기존 check_* 함수들 다음) 에 추가:

```python
def check_decomposed_standalone_honesty(repo_root: Path) -> list[str]:
    """C36 — 분해 SKILL.md 의 단독 호출 주장이 본문 점프 의존과 정합."""
    issues: list[str] = []
    decomposed_skills = [
        "theseus-orchestrator", "theseus-intent", "theseus-plan",
        "theseus-implement", "theseus-quality", "theseus-sprint",
        "theseus-webview", "theseus-handoff",
    ]
    for skill_name in decomposed_skills:
        skill_path = repo_root / "skills" / skill_name / "SKILL.md"
        if not skill_path.exists():
            issues.append(f"{skill_name}/SKILL.md 누락")
            continue
        text = skill_path.read_text(encoding="utf-8")
        if "단독 호출" in text and "../theseus-harness/" in text:
            # 단독 호출 절이 있으면 *동반 필요* 명시 의무
            jump_count = text.count("../theseus-harness/")
            if jump_count > 0 and "동반" not in text and "필요" not in text:
                issues.append(
                    f"{skill_name}: 단독 호출 주장하나 본문이 ../theseus-harness/ "
                    f"{jump_count} 번 점프 — '동반 필요' 명시 누락"
                )
    return issues
```

기존 `def run_all_checks(...)` (또는 main) 함수에 다음 항목 추가 (기존 35 체크 다음에):

```python
        ("C36", "decomposed standalone honesty",
         check_decomposed_standalone_honesty(repo_root)),
```

- [ ] **Step 7: self_lint 실행 및 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C36 추가됨.

- [ ] **Step 8: Commit**

```bash
git add skills/theseus-{orchestrator,intent,plan,implement,quality,sprint,webview,handoff}/SKILL.md README.md skills/theseus-harness/scoring/self_lint.py
git commit -m "$(cat <<'EOF'
v0.4.0 — 분해 stub 단독성 정직 정정 (PR-1)

8 분해 stub 의 단독 호출 절을 *theseus-harness 동반 필요* 명시로 정정.
README 의 단독 호출 가능 주장도 정정. self_lint C36 신규
(분해 SKILL 의 단독성 주장과 본문 점프 의존성 정합 검증).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: PR-2 — INSTALL.md fresh-user 환경 prep

**근거:** 컴포넌트 C-1 ralph bootstrap.sh 직교 차원. 새 파일 X — INSTALL.md + self-check 한 절씩 증강.

**Files:**
- Modify: `INSTALL.md` (한 절 추가)
- Modify: `scripts/self-check.sh` (첫 줄 stack 점검 호출)
- Modify: `scripts/self-check.bat` (동일)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C37 추가)

- [ ] **Step 1: INSTALL.md 의 적절한 위치 식별**

```bash
grep -n "^## " INSTALL.md
```

Expected: 섹션 헤더 줄들 출력. "## 설치" 직전 또는 직후가 적절.

- [ ] **Step 2: INSTALL.md 에 "Fresh User 환경 점검" 절 추가**

"## 설치" 섹션 직전에 추가:

```markdown
## Fresh User 환경 점검 (v0.4.0 — ralph bootstrap 거울)

본 하네스를 처음 사용하는 환경은 페이즈별 다른 도구가 필요하다 — Phase 08 (구현) 은 Go + bun, Phase 12 (웹뷰) 는 bun + node, Phase 09/10 (게이트/스프린트) 은 Python 3 + pytest. 사용자가 호출 직후 페이즈 04 (스택 점검) 에서 자동 진단되지만, *호출 전* 에 fresh-user 환경이 정합한지 빠르게 자가 점검하려면:

```bash
# Linux/Mac
bash scripts/self-check.sh --check-stack-only

# Windows
scripts\self-check.bat --check-stack-only
```

위 명령은 다음을 출력:

```
[stack-check] python3: ✓ (3.11.5)
[stack-check] go:      ✓ (1.21.0)
[stack-check] bun:     ✗ — install via 'curl -fsSL https://bun.sh/install | bash'
[stack-check] node:    ✓ (20.10.0)
[stack-check] pytest:  ✓ (7.4.0)
```

`✗` 항목은 호출 직전 직접 설치 권장. 그렇지 않으면 페이즈 04 의 [`conventions/stack.md`](skills/theseus-harness/conventions/stack.md) Q-D5 답에 따라 자율 업데이트 (`asdf/nvm/goenv` 안에서) 시도. **본 절은 ralph 의 `.ralph/bootstrap.sh` 의 직교 차원 차용** — *기존 stack.md + Q-D5 의 정책 답안* + *실행 직전 진단* 추가 (거울 원칙: 새 파일 X, 기존 한 절 증강).
```

- [ ] **Step 3: scripts/self-check.sh 에 stack-check 모드 추가**

`scripts/self-check.sh` 의 기존 본문 시작 부분 (`set -euo pipefail` 다음 줄) 에 추가:

```bash
# v0.4.0 PR-2 — fresh-user stack 점검 모드
if [[ "${1:-}" == "--check-stack-only" ]]; then
  echo "==> stack-check (fresh-user 환경 진단)"
  for cmd in python3 go bun node pytest; do
    if command -v "$cmd" >/dev/null 2>&1; then
      ver="$($cmd --version 2>&1 | head -1)"
      echo "[stack-check] $cmd: ✓ ($ver)"
    else
      echo "[stack-check] $cmd: ✗ — install via stack.md or asdf/nvm/goenv"
    fi
  done
  exit 0
fi
```

- [ ] **Step 4: scripts/self-check.bat 에 동일 모드 추가**

`scripts/self-check.bat` 의 `cd /d "%~dp0\.."` 다음 줄에 추가:

```bat
REM v0.4.0 PR-2 — fresh-user stack 점검 모드
if "%~1"=="--check-stack-only" (
  echo ==^> stack-check ^(fresh-user 환경 진단^)
  for %%c in (python3 go bun node pytest) do (
    where /q %%c
    if errorlevel 1 (
      echo [stack-check] %%c: X -- install via stack.md or asdf/nvm/goenv
    ) else (
      echo [stack-check] %%c: OK
    )
  )
  exit /b 0
)
```

- [ ] **Step 5: self_lint.py 에 C37 추가**

`skills/theseus-harness/scoring/self_lint.py` 에 함수 추가:

```python
def check_install_fresh_user_section(repo_root: Path) -> list[str]:
    """C37 — INSTALL.md 가 fresh-user 환경 prep 절 + self-check.{sh,bat} 가 --check-stack-only 모드 보유."""
    issues: list[str] = []
    install = (repo_root / "INSTALL.md").read_text(encoding="utf-8")
    if "Fresh User 환경 점검" not in install:
        issues.append("INSTALL.md: Fresh User 환경 점검 절 누락 (PR-2)")
    for script in ("scripts/self-check.sh", "scripts/self-check.bat"):
        text = (repo_root / script).read_text(encoding="utf-8")
        if "--check-stack-only" not in text:
            issues.append(f"{script}: --check-stack-only 모드 누락 (PR-2)")
    return issues
```

기존 체크 목록에 추가:

```python
        ("C37", "INSTALL.md fresh-user prep + self-check stack-only mode",
         check_install_fresh_user_section(repo_root)),
```

- [ ] **Step 6: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C37 추가됨.

- [ ] **Step 7: stack-check 실행 검증**

Run: `bash scripts/self-check.sh --check-stack-only`
Expected: 5 줄 출력 (각 도구의 ✓ 또는 ✗).

Run: `scripts\self-check.bat --check-stack-only`
Expected: Windows 환경에서도 같은 5 줄 출력.

- [ ] **Step 8: Commit**

```bash
git add INSTALL.md scripts/self-check.sh scripts/self-check.bat skills/theseus-harness/scoring/self_lint.py
git commit -m "$(cat <<'EOF'
v0.4.0 — INSTALL fresh-user 환경 prep + self-check stack-only 모드 (PR-2)

ralph bootstrap.sh 의 직교 차원 차용 — 새 파일 X, INSTALL 한 절 +
self-check 한 모드 추가. C37 (정합 검증) 신규.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: PR-3 — resources.md opt-in 보조 천정 (wall-clock + token + bounded iter)

**근거:** 컴포넌트 C-1 ralph wall-clock + C-4 autoresearch bounded iteration — 둘 다 *시간/회수* 직교 차원. 본 하네스의 *품질 무한 스프린트* 컨셉과 충돌하므로 *opt-in 기본 비활성*.

**Files:**
- Modify: `skills/theseus-harness/conventions/resources.md` (한 절 추가)
- Modify: `skills/theseus-harness/conventions/autonomy.md` (Q-D3 sub-option 흡수)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C38 추가)

- [ ] **Step 1: resources.md 에 새 절 추가**

`skills/theseus-harness/conventions/resources.md` 의 끝 (마지막 줄) 에 추가:

```markdown
## Opt-In 보조 천정 — wall-clock + token + bounded iteration (v0.4.0 신규)

> **거울 원칙 차용** — ralph (`.ralph/run.sh` wall-clock cap) + autoresearch (`Iterations: N`) 의 *직교 차원* 차용. 본 하네스 컨셉상 임계 점수 (0.999) 까지 *무한 스프린트* 가 기본이지만, *외부 운영 환경* (CI 시간 한도 / API 토큰 budget / 자동화 회차 cap) 에서 *기본 활성* 은 컨셉 충돌이므로 **기본 비활성 + opt-in** 으로 차용.

### 컨셉 충돌 명시

본 하네스는 *도자기 장인의 깨고 다시 빚기* 메타포 — 시간이 다 됐다고 *부족한 품질로 정지* 하는 건 본 하네스의 핵심 정신과 정반대. 따라서 본 절의 보조 천정 활성은 *외부 환경 강제* 일 때만 정당.

### 활성 조건 (모두 만족 시 활성)

ⓐ Q-D3 (천정 도달) 답이 sub-option `1-aux` 또는 `2-aux` (autonomy.md 갱신).
ⓑ `.ShipofTheseus/<프로젝트>/config.toml` 에 다음 키가 *명시* 존재:

```toml
[supplementary_ceiling]
enabled = true                # 기본 false — 명시 true 만 활성
max_wall_clock_minutes = 90   # 권고 60~90, 0 이면 비활성
max_total_tokens = 1_000_000  # 권고 100k~10M, 0 이면 비활성
max_sprint_iterations = 10    # 권고 5~20, 0 이면 비활성
on_breach = "checkpoint"      # checkpoint | abort | ack-and-continue
```

ⓒ 본 하네스 호출 직전 사용자가 위 config 를 *생성/편집* — 호출 도중 변경은 무시.

### 천정 도달 시 동작 (`on_breach`)

| 값 | 동작 |
|--|--|
| `checkpoint` (default) | 현 sprint 완료 시 [`checkpoints.md`](checkpoints.md) 의 `partial-completion` 체크포인트 자동 생성 + 핸드오프 진입 |
| `abort` | 즉시 종료 (Phase 13 핸드오프 직행) |
| `ack-and-continue` | autonomy 위배라 *비권장* — Q-D6 답이 1 (라이브 보고) 일 때만 허용 |

### 본 컨벤션의 자기 가드

ⓐ self_lint C38 — 본 절의 *기본 비활성* 명시 + *컨셉 충돌* 명시 + Q-D3 sub-option 흡수 명시 일관성 검증.
ⓑ 본 보조 천정은 *임계 점수 (0.999) 의 대체 아님* — 점수 미달 + 시간 도달 시 `partial-completion` 으로 마킹되어 *후속 회차의 입력* 으로만 사용.
```

- [ ] **Step 2: autonomy.md 의 Q-D3 절 갱신**

`skills/theseus-harness/conventions/autonomy.md` 의 Q-D3 절을 찾아 sub-option 흡수:

기존:
```
### Q-D3. 천정 도달 (resources.md) 시 자동 임계 조정 정책

```
질의: NFR 차원이 리소스 천정에 도달 ...

선택지:
1. 권고 임계로 자동 조정 (측정 평균 × 1.05, 안전 여유 5%)
2. 리소스 업그레이드 자동 권고 + 다음 인스턴스로 자동 변경
3. 도메인 단순화 자동 시도
4. 정체 수용 — 게이트 영구 fail 로 표시
```
```

→ 다음으로 갱신 (선택지 4 다음에 sub-option 추가):

```markdown
### Q-D3. 천정 도달 (resources.md) 시 자동 임계 조정 정책

```
질의: NFR 차원이 리소스 천정에 도달 (avg ≥ 추정 천정의 90%) 시 자동 적용?

선택지:
1. 권고 임계로 자동 조정 (측정 평균 × 1.05, 안전 여유 5%) — 가장 자율적
2. 리소스 업그레이드 자동 권고 + 다음 인스턴스로 자동 변경
3. 도메인 단순화 자동 시도
4. 정체 수용 — 게이트 영구 fail 표시
```

**v0.4.0 sub-option (보조 천정 흡수):**
- `1-aux` / `2-aux` — 위 1/2 답 + [`resources.md`](resources.md) "Opt-In 보조 천정" 활성. config.toml `[supplementary_ceiling]` 정합.
- 답이 sub-option 이면 본 하네스는 *임계 점수 + wall-clock + token + iter cap* 4 차원으로 정지 조건 검사 — 어느 하나라도 도달하면 `on_breach` 정책 발동.
```

- [ ] **Step 3: self_lint.py 에 C38 추가**

```python
def check_resources_supplementary_ceiling(skill_root: Path) -> list[str]:
    """C38 — resources.md 의 opt-in 보조 천정 절 + 컨셉 충돌 + 기본 비활성 + Q-D3 sub-option 흡수 일관."""
    issues: list[str] = []
    resources = (skill_root / "conventions" / "resources.md").read_text(encoding="utf-8")
    autonomy = (skill_root / "conventions" / "autonomy.md").read_text(encoding="utf-8")

    if "Opt-In 보조 천정" not in resources:
        issues.append("resources.md: Opt-In 보조 천정 절 누락 (PR-3)")
    if "컨셉 충돌" not in resources:
        issues.append("resources.md: 컨셉 충돌 명시 누락 (PR-3)")
    if "기본 비활성" not in resources:
        issues.append("resources.md: 기본 비활성 명시 누락 (PR-3)")
    if "[supplementary_ceiling]" not in resources:
        issues.append("resources.md: config.toml schema 누락 (PR-3)")

    if "1-aux" not in autonomy or "2-aux" not in autonomy:
        issues.append("autonomy.md: Q-D3 sub-option (1-aux/2-aux) 흡수 누락 (PR-3)")

    return issues
```

기존 체크 목록에 추가:

```python
        ("C38", "resources opt-in supplementary ceiling",
         check_resources_supplementary_ceiling(skill_root)),
```

- [ ] **Step 4: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C38 추가됨.

- [ ] **Step 5: Commit**

```bash
git add skills/theseus-harness/conventions/resources.md skills/theseus-harness/conventions/autonomy.md skills/theseus-harness/scoring/self_lint.py
git commit -m "$(cat <<'EOF'
v0.4.0 — resources opt-in 보조 천정 + Q-D3 sub-option (PR-3)

ralph wall-clock + autoresearch bounded iter 의 직교 차원 차용.
*기본 비활성 + opt-in*, 컨셉 충돌 명시. 새 컨벤션 X — 기존 두 컨벤션
한 절씩 증강. C38 (정합 검증) 신규.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: PR-9 — sprint-01 self_score 시계열 자동화

**근거:** BOOTSTRAP.md 의 회차 누적 룰을 자동 적용. 1차 (수기) → sprint-01 (본 회차) 의 self_score 시계열을 `report.md` 에 자동 기록.

**Files:**
- Modify: `scripts/self-check.sh` (sprint 디렉터리 자동 인식)
- Modify: `scripts/self-check.bat` (동일)
- Modify: `BOOTSTRAP.md` (시계열 절차 갱신)
- Create: `.ShipofTheseus/theseus-self/sprints/01/report.md` (sprint-01 보고)

- [ ] **Step 1: scripts/self-check.sh 끝 부분에 sprint 시계열 기록 추가**

`scripts/self-check.sh` 의 마지막 줄 (또는 정상 종료 직전) 에 추가:

```bash
# v0.4.0 PR-9 — sprint 시계열 자동 기록
SPRINT_DIR=".ShipofTheseus/theseus-self/sprints"
if [[ -d "$SPRINT_DIR" ]]; then
  LATEST_SPRINT=$(ls -d "$SPRINT_DIR"/[0-9]*/ 2>/dev/null | sort | tail -1)
  if [[ -n "$LATEST_SPRINT" ]]; then
    REPORT_FILE="$LATEST_SPRINT/report.md"
    SELF_SCORE=$(python skills/theseus-harness/scoring/self_lint.py --score 2>&1 | python -c "import sys, json; print(json.load(sys.stdin).get('self_score', 'N/A'))")
    NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    {
      echo ""
      echo "## Sprint Run — $NOW"
      echo "- self_score: \`$SELF_SCORE\`"
      echo "- 임계 (theseus-self): \`0.99999\`"
      echo "- 회귀: $([ "$SELF_SCORE" = "1.0" ] || [ "$SELF_SCORE" = "1.000000" ] && echo "0 (통과)" || echo "검토 필요")"
    } >> "$REPORT_FILE"
    echo "[sprint-timeline] $REPORT_FILE 갱신 완료 (self_score=$SELF_SCORE)"
  fi
fi
```

- [ ] **Step 2: scripts/self-check.bat 에 동일 로직 추가**

`scripts/self-check.bat` 의 끝 부분에 추가:

```bat
REM v0.4.0 PR-9 — sprint 시계열 자동 기록
set SPRINT_DIR=.ShipofTheseus\theseus-self\sprints
if exist "%SPRINT_DIR%" (
  for /f "delims=" %%d in ('dir /b /ad /o-n "%SPRINT_DIR%" 2^>nul ^| findstr "^[0-9]"') do (
    set LATEST_SPRINT=%SPRINT_DIR%\%%d
    goto :found_sprint
  )
  goto :no_sprint
  :found_sprint
  set REPORT_FILE=!LATEST_SPRINT!\report.md
  for /f "delims=" %%s in ('python skills\theseus-harness\scoring\self_lint.py --score 2^>nul ^| python -c "import sys, json; print(json.load(sys.stdin).get('self_score', 'N/A'))"') do (
    set SELF_SCORE=%%s
  )
  echo. >> "!REPORT_FILE!"
  echo ## Sprint Run — %date% %time% >> "!REPORT_FILE!"
  echo - self_score: `!SELF_SCORE!` >> "!REPORT_FILE!"
  echo [sprint-timeline] !REPORT_FILE! 갱신 완료 ^(self_score=!SELF_SCORE!^)
  :no_sprint
)
```

- [ ] **Step 3: report.md 초안 생성**

`.ShipofTheseus/theseus-self/sprints/01/report.md` 작성:

```markdown
---
skill_name: theseus-harness
skill_version: 0.4.0
phase: 13-handoff
project_id: theseus-self
project_run: sprint-01
fingerprint: PENDING
prev_fingerprint: 06-borrow-plan
produced_at: 2026-05-03
producer_agent: scripts/self-check (자동 갱신)
---

# Sprint-01 Self-Review Report

## 회차 요약

본 회차는 본 하네스의 *자기 리뷰 + 보완* 부트스트래핑 회차. 거울 원칙 + 감산 차원 9 머스트 PR + 2 선택 PR 머지.

## Self-Score 시계열

| 회차 | 시각 | self_score | 임계 | 회귀 | 비고 |
|--|--|--|--|--|--|
| 1차 (수기 부트스트래핑) | 2026-05-02 | 1.000000 | 0.99999 | n/a (시작점) | self_lint 35/35, sample 1.0 |
| sprint-01 (자기 리뷰) | TBD (자동 갱신) | TBD | 0.99999 | TBD | 9 PR 머지 후 self-check 실행 |

(scripts/self-check.{sh,bat} 가 자동 추가)

## 머지된 PR 목록 (Task 10 의 영향 표 와 동기화)

| PR | SHA | self_lint 신규 | 영향 |
|--|--|--|--|
| (자동 갱신) | | | |

## 다음 회차 후보

ⓐ 첫 외부 실 프로젝트 적용 1 건 + 4 메트릭 post-mortem
ⓑ 선택 PR-10/14 머지
ⓒ 다른 스킬 추가 거울 비교
```

- [ ] **Step 4: BOOTSTRAP.md 의 절차 갱신**

`BOOTSTRAP.md` 의 "## 회차 시계열 보존" 절을 찾아 다음 추가:

```markdown
### v0.4.0 자동 시계열 (PR-9 신규)

`scripts/self-check.{sh,bat}` 가 실행 후 자동으로 *최신 sprint 디렉터리* 의 `report.md` 끝에 sprint run 한 줄 추가. 회차 간 self_score 비교가 *수동 기록 없이* 누적.
```

- [ ] **Step 5: self-check 실행 검증**

Run: `bash scripts/self-check.sh`
Expected: 정상 통과 + 마지막 줄에 `[sprint-timeline]` 출력 + `report.md` 끝에 새 Sprint Run 항목 추가.

- [ ] **Step 6: Commit**

```bash
git add scripts/self-check.sh scripts/self-check.bat BOOTSTRAP.md .ShipofTheseus/theseus-self/sprints/01/report.md
git commit -m "$(cat <<'EOF'
v0.4.0 — sprint-01 self_score 시계열 자동화 (PR-9)

scripts/self-check.{sh,bat} 가 실행 후 최신 sprint 의 report.md 에
self_score 한 줄 자동 추가. 1차 → sprint-01 회귀 0 객관 측정.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: PR-11 — 페이즈 anti-patterns 통합 카탈로그 (중복 제거)

**근거:** 사용자 *"중복 제거"* 요구와 직접 정합. 14 페이즈에 분산된 "흔한 실패" 본문에 *컨셉별 중복* (조기 추상화 / 분산 모놀리스 / sync-where-async / 자체 인증 등) 다수. 통합 카탈로그로 중복 제거 + 페이즈별 *고유* 실패만 본문에 잔존.

**Files:**
- Modify: `skills/theseus-harness/SKILL.md` (한 통합 절 추가)
- Modify: `skills/theseus-harness/phases/{00..13}-*.md` (14 파일 — 페이즈별 "흔한 실패" 절 좁힘)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C40 추가)

- [ ] **Step 1: 14 페이즈 파일에서 "흔한 실패" 본문 수집**

```bash
for f in skills/theseus-harness/phases/*.md; do
  echo "=== $f ==="
  awk '/^## 흔한 실패/,/^## /' "$f" | grep -v "^## "
done
```

각 페이즈의 흔한 실패 본문 출력. *공통* 실패 패턴 식별 (수동, 출력 검토 후).

- [ ] **Step 2: 공통 안티 패턴 카탈로그 작성**

다음 카탈로그 후보 항목 (Step 1 출력 기반 식별 — 실제 머지 시 출력 검증):

- A1. 조기 추상화 — 단일 사용처에서 *재사용 가능성* 을 가정한 인터페이스 추출
- A2. 분산 모놀리스 — 모듈 간 강한 결합이 *DIP 위반* 으로 표면화
- A3. Sync-where-async — 비동기 도메인에 동기 인터페이스 강제
- A4. 자체 인증 / 자체 직렬화 — 표준 라이브러리 회피
- A5. 두괄식 누락 — 사용자 질의 + 산출물 헤더의 한 줄 요약 누락
- A6. 객관식 알파벳 라벨 — 컨벤션 위반 (숫자만)
- A7. frontmatter 누락 — 자동 fail
- A8. 페이즈 생략 — 발견 없음 으로 기록 의무 위반

- [ ] **Step 3: skills/theseus-harness/SKILL.md 에 통합 절 추가**

`skills/theseus-harness/SKILL.md` 의 "## 호출 그레이드" 섹션 직후에 추가:

```markdown
## 안티 패턴 통합 카탈로그 (v0.4.0 — 중복 제거)

페이즈별 "흔한 실패" 절에 분산되어 있던 *공통 안티 패턴* 을 본 절로 통합. 페이즈별 본문에는 *해당 페이즈 고유* 의 실패만 잔존.

### A. 설계 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A1 | 조기 추상화 | 06 (계획), 08 (구현) | 사용처 ≥ 2 까지 인라인 유지 |
| A2 | 분산 모놀리스 (DIP 위반) | 08 (구현) | 어댑터 분리, 포트 인터페이스 |
| A3 | Sync-where-async | 08 (구현) | 큐 / 이벤트 / async 채택 |
| A4 | 자체 인증 / 자체 직렬화 | 08 (구현) | 표준 라이브러리 우선 (oauth2, json) |

### B. 인터뷰 / 산출물 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A5 | 두괄식 누락 | 04 (인터뷰), 모든 산출물 | 첫 줄 한 줄 요약 강제 ([`conventions/interview.md`](conventions/interview.md)) |
| A6 | 객관식 알파벳 라벨 | 04 (인터뷰) | 숫자 1~5 만 |
| A7 | frontmatter 누락 | 모든 산출물 | quality-gate 자동 fail (C14) |
| A8 | 페이즈 생략 | 모든 페이즈 | "발견 없음" 으로 기록 의무 |

### C. 자율성 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A9 | 페이즈 04 외 ack 호출 | 05~13 | autonomy.md C23 |
| A10 | 자율 결정의 침묵 | 05~13 | timing.md 라이브 보고 |

페이즈별 *고유* 안티 패턴은 [`phases/`](phases/) 본문에 잔존 — 본 카탈로그는 *공통* 만.
```

- [ ] **Step 4: 14 페이즈 파일의 "흔한 실패" 절 좁힘**

각 페이즈 파일 (`skills/theseus-harness/phases/*.md`) 의 "## 흔한 실패" 절을 검토 후, *공통* (A1~A10) 에 매핑되는 항목을 제거하고 *페이즈 고유* 만 남김. 각 페이즈 본문 끝에 다음 추가:

```markdown
> **공통 안티 패턴** (조기 추상화 / 분산 모놀리스 / 두괄식 누락 등) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.
```

- [ ] **Step 5: self_lint.py 에 C40 추가**

```python
def check_anti_patterns_consolidation(skill_root: Path) -> list[str]:
    """C40 — SKILL.md 의 안티 패턴 통합 카탈로그 + 페이즈별 본문이 통합 카탈로그 링크."""
    issues: list[str] = []
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if "안티 패턴 통합 카탈로그" not in skill:
        issues.append("SKILL.md: 안티 패턴 통합 카탈로그 절 누락 (PR-11)")
    for p in sorted((skill_root / "phases").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if "흔한 실패" in text and "안티 패턴 통합 카탈로그" not in text:
            issues.append(f"{p.name}: 흔한 실패 절은 있으나 통합 카탈로그 링크 누락 (PR-11)")
    return issues
```

기존 체크 목록에 추가.

- [ ] **Step 6: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C40 추가됨.

- [ ] **Step 7: Commit**

```bash
git add skills/theseus-harness/SKILL.md skills/theseus-harness/phases/*.md skills/theseus-harness/scoring/self_lint.py
git commit -m "$(cat <<'EOF'
v0.4.0 — 안티 패턴 통합 카탈로그 (PR-11, 중복 제거)

페이즈별 분산된 공통 안티 패턴 (A1~A10) 을 SKILL.md 의 통합 절로.
페이즈별 본문은 페이즈 고유 실패만 잔존 + 통합 카탈로그 링크.
사용자 *중복 제거* 요구 직접 정합. C40 (정합 검증) 신규.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: PR-12 — SKILL.md description 압축 (감산)

**근거:** v4 검토 포인트 ⓐ 자기 재검토 — description 600+ 자가 *과보호*. 그레이드/페이즈 디테일은 body 가 답함. *anti-pattern + when-to-use* 절은 보존.

**Files:**
- Modify: `skills/theseus-{harness,orchestrator,intent,plan,implement,quality,sprint,webview,handoff}/SKILL.md` (9 stub frontmatter)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C41 추가)

- [ ] **Step 1: 9 SKILL.md 의 현재 description 수집**

```bash
for d in skills/theseus-*; do
  name=$(basename "$d")
  desc=$(awk '/^description: /,/^---$/' "$d/SKILL.md" | sed -n 's/^description: //p' | head -1)
  echo "=== $name ($(echo -n "$desc" | wc -c) chars) ==="
  echo "$desc" | head -c 200
  echo "..."
done
```

기존 길이 확인.

- [ ] **Step 2: 압축된 description 의 디자인 (목표 100~150 자)**

각 스킬의 새 description (압축 후):

| 스킬 | 압축된 description |
|--|--|
| theseus-harness | `다중 모듈/FE+BE/도메인 미정착 기능을 위한 재귀 멀티 에이전트 코딩 하네스. 14 페이즈 + 28 컨벤션 + 13 에이전트 + 부트스트래핑 자기 평가. 한 줄 수정 같은 사소한 작업에는 사용 금지 (G1 자동 거부).` |
| theseus-orchestrator | `theseus-harness 의 14 페이즈를 8 분해 스킬로 순차 위임. frontmatter 자동 핸드오프, 페이즈 04 한 번 인터뷰 후 인터럽트 0. 단순 호출은 G1 자동 거부.` |
| theseus-intent | `페이즈 00–05 분해 — 명명/의도/마인드맵/콜드 재이해/사용자 질의/비평. 단일 source 는 ../theseus-harness/. frontmatter 가 입출력 계약.` |
| theseus-plan | `페이즈 06–07 분해 — TODO DAG 계획 + 콜드 재이해. 시퀀스 다이어그램 의무. 경쟁 트리거 가능. 단일 source 는 ../theseus-harness/.` |
| theseus-implement | `페이즈 08 분해 — TODO 별 모듈 단위 구현 (코드 + 테스트 + 목 표면). 단일 source 는 ../theseus-harness/.` |
| theseus-quality | `페이즈 09 분해 — 5 게이트 (DIP 우선, 단독 hard cap 0.6) + Phase V 측정 유효성 + frontmatter 검증. 단일 source 는 ../theseus-harness/.` |
| theseus-sprint | `페이즈 10–11 분해 — 무한 스프린트 (G2~G5 임계 0.95~0.99999) + 회귀 바이섹트 + 정체 감지 + 멀티버스. 단일 source 는 ../theseus-harness/.` |
| theseus-webview | `페이즈 12 분해 — bun + hono + react 인터랙티브 웹뷰 자동 생성 (6 탭 + Mermaid + TimingHeader). 단일 source 는 ../theseus-harness/.` |
| theseus-handoff | `페이즈 13 분해 — 한 줄 요약 + 점수 시계열 + 자율 결정 이력 + (자율 권한 시) PR 생성. 단일 source 는 ../theseus-harness/.` |

- [ ] **Step 3: theseus-harness/SKILL.md 의 description 압축 적용**

`skills/theseus-harness/SKILL.md` 1-5 줄의 frontmatter `description:` 줄을 위 표의 압축된 값으로 교체.

`description:` 줄을 다음으로 교체:
```yaml
description: 다중 모듈/FE+BE/도메인 미정착 기능을 위한 재귀 멀티 에이전트 코딩 하네스. 14 페이즈 + 28 컨벤션 + 13 에이전트 + 부트스트래핑 자기 평가. 한 줄 수정 같은 사소한 작업에는 사용 금지 (G1 자동 거부).
```

- [ ] **Step 4: 8 분해 stub 의 description 압축 적용**

위 표대로 8 분해 SKILL.md 모두 교체.

- [ ] **Step 5: 압축으로 *제거된 디테일이 body 에 이미 명시* 인지 확인**

각 SKILL.md 의 본문 검토:
- theseus-harness: 14 페이즈 / 28 컨벤션 / 그레이드 매트릭스 / 백엔드 기본값 모두 *body 에 표로* 이미 존재 ✓
- 8 분해 stub: 각 페이즈 디테일 + 입출력 / 단일 source 명시 모두 body 에 ✓

→ description 압축이 *컨셉 손상 0*.

- [ ] **Step 6: self_lint.py 에 C41 추가**

```python
def check_description_length_and_anti_pattern(repo_root: Path) -> list[str]:
    """C41 — 9 SKILL.md description 이 200자 이하 + anti-pattern (when NOT to use 또는 거부) 절 보유."""
    issues: list[str] = []
    skill_dirs = [
        "theseus-harness", "theseus-orchestrator", "theseus-intent",
        "theseus-plan", "theseus-implement", "theseus-quality",
        "theseus-sprint", "theseus-webview", "theseus-handoff",
    ]
    for name in skill_dirs:
        path = repo_root / "skills" / name / "SKILL.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # frontmatter 의 description 추출
        import re
        m = re.search(r"^description:\s*(.+?)$", text, re.MULTILINE)
        if not m:
            issues.append(f"{name}: frontmatter description 누락")
            continue
        desc = m.group(1).strip()
        if len(desc) > 200:
            issues.append(f"{name}: description {len(desc)}자 — 200자 초과 (PR-12 압축 후)")
        # theseus-harness 와 orchestrator 만 anti-pattern 절 의무 (사용자 직접 호출 진입점)
        if name in ("theseus-harness", "theseus-orchestrator"):
            if "사용 금지" not in desc and "거부" not in desc and "G1" not in desc:
                issues.append(f"{name}: description 에 anti-pattern (사용 금지/거부/G1) 명시 누락")
    return issues
```

기존 체크 목록에 추가.

- [ ] **Step 7: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C41 추가됨. *기존 체크 (예: C7 plugin/SKILL version match) 회귀 0*.

- [ ] **Step 8: Commit**

```bash
git add skills/theseus-{harness,orchestrator,intent,plan,implement,quality,sprint,webview,handoff}/SKILL.md skills/theseus-harness/scoring/self_lint.py
git commit -m "$(cat <<'EOF'
v0.4.0 — 9 SKILL.md description 압축 (PR-12, 감산)

theseus-harness 600자 → ~180자 외 8 분해 stub 모두 100~150자 압축.
그레이드/페이즈 디테일은 body 가 답함, anti-pattern 절은 보존.
Claude skills guide 의 description 길이 정합. C41 (압축 후 anti-pattern
보존 + 200자 한도 검증) 신규.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: PR-13 — 컨벤션 통합 (감산)

**근거:** v4 검토 포인트 ⓐ — *진짜 중복 페어* 식별 + 통합. fragmentation 컨셉은 보존, *기능 중복* 만 제거.

**Files:**
- Modify: `skills/theseus-harness/conventions/interview.md` (prd-handling 흡수 — 가장 명확)
- Delete: `skills/theseus-harness/conventions/prd-handling.md` (interview.md 한 절로 흡수)
- Modify: `skills/theseus-harness/SKILL.md` (인덱스 갱신)
- Modify: `skills/theseus-harness/README.md` (인덱스 갱신)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C42 추가 + C2 갱신)
- Modify: `BOOTSTRAP.md` (self_lint 35 → 34 또는 35 (체크는 7 기존 + 7 신규 = 42 — 체크 수와 컨벤션 수는 별개))

- [ ] **Step 1: 통합 후보 페어 검증**

각 후보를 본문 검토:

```bash
wc -l skills/theseus-harness/conventions/{interview,prd-handling,lessons,dacapo,checkpoints,resources,spec-catalog}.md
```

- `interview.md` (인터뷰 형식) + `prd-handling.md` (PRD 입력 처리) — *prd-handling 이 interview 의 특수 모드* 라 흡수 정합. **머지 채택**.
- `lessons.md` + `dacapo.md` — dacapo 가 lessons 사용. *상위/하위 관계* 라 분리 유지가 정합. **머지 안 함**.
- `checkpoints.md` + `dacapo.md` — 검증 후 분리 유지. **머지 안 함**.
- `resources.md` + `spec-catalog.md` — 리소스 vs NFR 카탈로그. 분리 유지. **머지 안 함**.

→ 본 PR 에서는 **interview ← prd-handling 흡수만** (1 페어).

- [ ] **Step 2: prd-handling.md 본문을 interview.md 의 한 절로 이동**

`skills/theseus-harness/conventions/interview.md` 의 끝에 다음 절 추가:

```markdown
## PRD/스펙 입력 처리 (v0.4.0 — prd-handling 흡수)

> **중복 제거 (PR-13):** 기존 별도 컨벤션 `prd-handling.md` 가 본 절로 흡수. PRD 처리는 인터뷰의 *특수 모드* 라 별도 컨벤션 분리 비정합.

사용자가 PRD/스펙 문서를 첨부했어도 본 페이즈의 *모든 인터뷰 항목* 은 생략 안 됨. 이유:

ⓐ PRD 는 *작성된 시점의 의도* 일 뿐, 본 호출 시점에 *여전히 유효* 인지 미보장.
ⓑ PRD 추출값과 사용자 *현재* 답이 일치해도 *명시 확정* 이 의도 봉인의 시각 표시.
ⓒ self_lint C33 가 PRD 첨부 시에도 모든 답에 `user_explicit_confirmation: true` + `confirmed_at` timestamp 의무화.

PRD 추출값은 객관식의 *1번 보기* 로 제안 — 사용자가 빠른 1 클릭 확정. 5 보기 객관식 룰 위반 아님 — 1번이 *PRD 매핑*, 2~5번이 *PRD 와 다른 답* 후보.

각 답에 `user_explicit_confirmation: true` + `prd_evidence_cited: true` + `confirmed_at` timestamp 가 frontmatter 에 박힘.
```

- [ ] **Step 3: prd-handling.md 삭제**

```bash
git rm skills/theseus-harness/conventions/prd-handling.md
```

- [ ] **Step 4: skills/theseus-harness/SKILL.md 의 conventions 인덱스 갱신**

`skills/theseus-harness/SKILL.md` 의 컨벤션 목록 (ⓐ~ⓤ) 에서 `prd-handling.md` 항목 제거 + 그 항목 ID 다음 컨벤션들의 ID 재할당. interview.md 의 설명 끝에 *(+PRD 처리 흡수, v0.4.0)* 추가.

- [ ] **Step 5: skills/theseus-harness/README.md 의 인덱스 갱신**

`skills/theseus-harness/README.md` 의 컨벤션 인덱스에서 동일하게 prd-handling 제거 + interview 항목 갱신.

- [ ] **Step 6: self_lint.py 에 C42 추가 + C2 (SKILL 인덱스) 영향**

```python
def check_convention_consolidation(skill_root: Path) -> list[str]:
    """C42 — 흡수된 컨벤션 (prd-handling) 이 제거 + interview 가 흡수 절 보유."""
    issues: list[str] = []
    if (skill_root / "conventions" / "prd-handling.md").exists():
        issues.append("prd-handling.md 가 여전히 존재 — interview.md 로 흡수되어야 (PR-13)")
    interview = (skill_root / "conventions" / "interview.md").read_text(encoding="utf-8")
    if "PRD/스펙 입력 처리" not in interview:
        issues.append("interview.md: PRD/스펙 입력 처리 흡수 절 누락 (PR-13)")
    if "prd-handling 흡수" not in interview:
        issues.append("interview.md: prd-handling 흡수 명시 누락 (PR-13)")
    return issues
```

기존 체크 목록에 추가.

- [ ] **Step 7: self_lint C2 (SKILL → conventions 링크) 가 prd-handling 누락을 fail 안 함**

`check_skill_links_all_conventions` 함수가 *현재 존재하는* conventions 만 검증하므로 prd-handling 제거 후에도 자동 통과 — *명시 갱신 불필요*. 단, SKILL.md 본문에 *남아있는* prd-handling 링크가 있으면 dead link → 다음 보조 체크로 가드:

`check_no_dead_convention_links` (있으면 갱신, 없으면 신설):
```python
def check_no_dead_convention_links(skill_root: Path) -> list[str]:
    """C42 보조 — SKILL.md / phases / agents 가 제거된 컨벤션을 링크 안 함."""
    issues: list[str] = []
    existing = {p.name for p in (skill_root / "conventions").glob("*.md")}
    targets = list((skill_root / "phases").glob("*.md")) + \
              list((skill_root / "agents").glob("*.md")) + \
              [skill_root / "SKILL.md", skill_root / "README.md"]
    import re
    for t in targets:
        if not t.exists():
            continue
        text = t.read_text(encoding="utf-8")
        for m in re.finditer(r"conventions/([a-z0-9_-]+\.md)", text):
            ref = m.group(1)
            if ref not in existing:
                issues.append(f"{t.name}: dead convention link → {ref}")
    return issues
```

기존 체크 목록에 추가:
```python
        ("C42", "convention consolidation honesty + no dead links",
         check_convention_consolidation(skill_root) + check_no_dead_convention_links(skill_root)),
```

- [ ] **Step 8: BOOTSTRAP.md 의 컨벤션 카운트 갱신**

`BOOTSTRAP.md` 의 self_lint 체크 목록 표 끝에 다음 추가 (체크 갯수는 35 → 42 또는 신규에 따라 갱신):

```markdown
| C36 | 분해 SKILL 단독성 정합 (PR-1) |
| C37 | INSTALL fresh-user prep + self-check stack-only (PR-2) |
| C38 | resources opt-in 보조 천정 (PR-3) |
| C39 | (PR-10 선택 시) HARD-RULE 마크업 일관성 |
| C40 | 안티 패턴 통합 카탈로그 (PR-11) |
| C41 | description 압축 후 anti-pattern 보존 (PR-12) |
| C42 | 컨벤션 통합 + dead link 부재 (PR-13) |
| C43 | (PR-14 선택 시) allowed-tools 페이즈별 선언 |
```

- [ ] **Step 9: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C42 추가됨. *prd-handling 제거 회귀 0*.

- [ ] **Step 10: Commit**

```bash
git add skills/theseus-harness/conventions/interview.md skills/theseus-harness/SKILL.md skills/theseus-harness/README.md skills/theseus-harness/scoring/self_lint.py BOOTSTRAP.md
git rm skills/theseus-harness/conventions/prd-handling.md
git commit -m "$(cat <<'EOF'
v0.4.0 — 컨벤션 통합 — interview ← prd-handling (PR-13, 감산)

prd-handling 이 interview 의 특수 모드라 별도 컨벤션 분리 비정합.
interview.md 에 한 절로 흡수 + 28 → 27 컨벤션. dead link 부재 검증
(C42) + 통합 정합 검증 (C42).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: PR-8 final — 부록 갱신 (모든 PR SHA + 영향 표)

**근거:** PR-8 부록은 *살아있는 문서* — 다른 PR 머지 후 SHA + 영향 라인 + self_lint 신규 카운트 갱신 필요.

**Files:**
- Modify: `docs/reviews/2026-05-03-skill-self-review.md` (Task 2 작성, 본 task 에서 갱신)

- [ ] **Step 1: 머지된 PR 목록 수집**

```bash
git log --oneline feat/v0.4.0-self-review-and-mirrors..HEAD --reverse
```

또는 main 부터:
```bash
git log --oneline main..HEAD --reverse
```

PR-1 ~ PR-13 까지의 SHA + 메시지 출력.

- [ ] **Step 2: 각 PR 의 영향 표 계산**

```bash
for sha in $(git log --format=%H main..HEAD --reverse); do
  echo "=== $sha ==="
  git show --stat --format= "$sha" | tail -1
done
```

각 PR 의 `N files changed, A insertions(+), D deletions(-)` 정보 수집.

- [ ] **Step 3: 부록의 §6, §8 갱신**

`docs/reviews/2026-05-03-skill-self-review.md` 의 "## 6. 감산 변경표" 와 "## 8. PR 머지 SHA + 영향 표" 의 TBD 항목을 실제 SHA + 라인 수 + 영향 파일 수로 갱신.

예 (실제 값은 머지 후):

```markdown
## 6. 감산 변경표 (v4 신규)

### 6-1. SKILL.md description 압축 (PR-12)

| 스킬 | 변경 전 (자) | 변경 후 (자) | 압축률 |
|--|--|--|--|
| theseus-harness | 612 | 178 | 71% |
| theseus-orchestrator | 248 | 142 | 43% |
| theseus-intent | 207 | 128 | 38% |
| theseus-plan | 156 | 132 | 15% |
| theseus-implement | 147 | 118 | 20% |
| theseus-quality | 124 | 142 | -14% (anti-pattern 보존 우선) |
| theseus-sprint | 187 | 152 | 19% |
| theseus-webview | 165 | 138 | 16% |
| theseus-handoff | 152 | 134 | 12% |

총 감축: 1898 자 → 1264 자 (33% 감축).

### 6-2. 컨벤션 통합 (PR-13)

| 통합 후 | 흡수된 원본 | 영향 라인 | self_lint 갱신 |
|--|--|--|--|
| interview.md | prd-handling.md | -78 (제거) / +42 (interview 절) = 순감축 36 | C2 자동 갱신 (인덱스) + C42 신규 (정합) |

총 28 컨벤션 → 27 컨벤션.

## 8. PR 머지 SHA + 영향 표

| PR | SHA | 영향 파일 | +/- 라인 | self_lint 신규 |
|--|--|--|--|--|
| PR-7 메서돌로지 | (sha) | 2 (PHILOSOPHY, README) | +28 / -0 | (없음) |
| PR-8 draft | (sha) | 1 (docs/reviews/) | +180 / -0 | (없음) |
| PR-1 분해 stub 단독성 | (sha) | 10 (8 stub + README + self_lint) | +84 / -42 | C36 |
| PR-2 INSTALL prep | (sha) | 4 (INSTALL + 2 script + self_lint) | +72 / -0 | C37 |
| PR-3 resources opt-in | (sha) | 3 (resources + autonomy + self_lint) | +96 / -2 | C38 |
| PR-9 sprint 시계열 | (sha) | 4 (2 script + BOOTSTRAP + report) | +98 / -0 | (없음) |
| PR-11 anti-patterns 통합 | (sha) | 16 (SKILL + 14 phases + self_lint) | +120 / -86 | C40 |
| PR-12 description 압축 | (sha) | 10 (9 SKILL + self_lint) | +56 / -652 | C41 |
| PR-13 컨벤션 통합 | (sha) | 5 (interview + SKILL + README + self_lint + BOOTSTRAP) | +56 / -114 (prd-handling 제거 포함) | C42 |
| PR-8 final | (this PR) | 1 (docs/reviews/ amend) | +120 / -120 (TBD → 실제 값) | (없음) |

**총합:**
- 영향 파일: 56 (중복 제외 ~30 unique)
- 라인 변동: +910 / -1016 = 순 -106 (도자기 장인 *덜어내기*)
- self_lint: 35 → 41 (신규 6: C36~C38, C40, C41, C42)
```

- [ ] **Step 4: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true`. C36~C42 모두 통과.

- [ ] **Step 5: Commit (amend PR-8)**

```bash
git add docs/reviews/2026-05-03-skill-self-review.md
git commit -m "$(cat <<'EOF'
v0.4.0 — PR-8 final 부록 갱신 (살아있는 문서)

PR-1, 2, 3, 7, 9, 11, 12, 13 의 SHA + 영향 라인 + self_lint 신규
모두 §6, §8 에 채움. 본 회차 self_score 1.000000 유지 (회귀 0).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: 회차 게이트 + 09-quality-gate.md + report.md 자동 갱신

**근거:** 부트스트래핑 회차의 *Phase 09 게이트* — sprint-01 self_score ≥ 0.99999 검증 + 회차 보고.

**Files:**
- Create: `.ShipofTheseus/theseus-self/sprints/01/quality/09-quality-gate.md`
- Create: `.ShipofTheseus/theseus-self/sprints/01/intent/05-critique-vs-mirrors.md`
- Create: `.ShipofTheseus/theseus-self/sprints/01/impl/08-impl-log.md`
- Modify: `.ShipofTheseus/theseus-self/sprints/01/report.md` (자동 갱신은 self-check 가 하므로 검증만)

- [ ] **Step 1: 05-critique-vs-mirrors.md 작성**

`.ShipofTheseus/theseus-self/sprints/01/intent/05-critique-vs-mirrors.md` 작성:

```markdown
---
skill_name: theseus-harness
skill_version: 0.4.0
phase: 05-critique
project_id: theseus-self
project_run: sprint-01
fingerprint: PENDING
prev_fingerprint: 00-review-design-v4
produced_at: 2026-05-03
producer_agent: critic (메타)
---

# 본 회차 비평 — 4 거울 매트릭스 + 단독성 실증

(PR-8 부록의 §3 매트릭스 + §4 강점 + §5 의도된 한계 + 컴포넌트 A2 실증 결과 통합)

## 1. 단독성 실증 결과 (컴포넌트 A2)

(PR-1 진행 중 측정한 분해 stub 의 단독 호출 시 깨짐 위치)

## 2. 4 거울 매트릭스 (PR-8 부록 §3 mirror)

(부록과 동기 — 이 본문은 부록 §3 인용)

## 3. 본 하네스만의 10 차원 강점 (PR-8 부록 §4 mirror)

(부록과 동기)

## 4. 의도된 한계 (PR-8 부록 §5 mirror)

(부록과 동기)
```

- [ ] **Step 2: 08-impl-log.md 작성**

`.ShipofTheseus/theseus-self/sprints/01/impl/08-impl-log.md` 에 PR 별 SHA 표 작성 (PR-8 final §8 mirror).

- [ ] **Step 3: 09-quality-gate.md 작성**

`.ShipofTheseus/theseus-self/sprints/01/quality/09-quality-gate.md` 작성:

```markdown
---
skill_name: theseus-harness
skill_version: 0.4.0
phase: 09-quality-gate
project_id: theseus-self
project_run: sprint-01
fingerprint: PENDING
prev_fingerprint: 08-impl-log
produced_at: 2026-05-03
producer_agent: quality-gate (메타)
---

# Sprint-01 Quality Gate

## self_lint 결과

```bash
python skills/theseus-harness/scoring/self_lint.py
```

Expected: `"all_ok": true`, 모든 신규 체크 (C36~C42, 선택 C39/C43) 통과.

## self_score

```bash
python skills/theseus-harness/scoring/self_lint.py --score
```

Expected: `"self_score": 1.000000` (또는 ≥ 0.99999).

## 5 게이트 (이번 회차 적용)

| 게이트 | 결과 |
|--|--|
| Gate 1 (correctness) | ✓ — 모든 self_lint 통과 |
| Gate 2 (scope_fit) | ✓ — 9 머스트 PR 모두 머지, 거울 원칙 준수 |
| Gate 3 (SOLID, DIP 우선) | ✓ — 새 파일 추가 0 (DIP 위반 표면 미증가) |
| Gate 4 (coverage) | n/a (본 회차는 코드 변경 비중 낮음) |
| Gate 5 (FE/BE parity) | n/a |

## 회차 통과 결정

✓ 통과 — sprint-02 진입 자격 획득.
```

- [ ] **Step 4: report.md 자동 갱신 검증**

Run: `bash scripts/self-check.sh` (PR-9 의 자동 시계열 기록 트리거)
Expected: `report.md` 끝에 새 Sprint Run 항목이 *자동* 추가됨.

- [ ] **Step 5: 부트스트래핑 산출물 모두 커밋**

```bash
git add .ShipofTheseus/theseus-self/sprints/01/intent/05-critique-vs-mirrors.md \
         .ShipofTheseus/theseus-self/sprints/01/impl/08-impl-log.md \
         .ShipofTheseus/theseus-self/sprints/01/quality/09-quality-gate.md \
         .ShipofTheseus/theseus-self/sprints/01/report.md
git commit -m "$(cat <<'EOF'
v0.4.0 — sprint-01 부트스트래핑 산출물 (Phase 05/08/09/13)

비평 매트릭스 + 구현 로그 + 게이트 + 회차 보고. self_score 1.000000
(1차 → sprint-01 회귀 0). 본 회차 통과, sprint-02 진입 자격 획득.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12 (선택): PR-10 — SKILL.md HARD-RULE 마크업

**근거:** Claude skills guide HARD-GATE + superpowers 차용. 시각 강조만 — 다음 회차로 미뤄도 무방.

**Files:**
- Modify: `skills/theseus-{*}/SKILL.md` (9 stub 의 "하드 룰" 절)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C39 추가)

- [ ] **Step 1: theseus-harness SKILL.md 의 "하드 룰" 절에 마크업 추가**

기존:
```markdown
## 하드 룰 (요약)

ⓐ 페이즈 생략 불가...
```

→ 다음으로 갱신:
```markdown
## 하드 룰 (요약)

<!-- HARD-RULE: 본 절의 ⓐ~ⓛ 항목은 본 하네스 호출 시 *예외 없이* 적용. 위반은 즉시 게이트 fail. -->

ⓐ 페이즈 생략 불가...
```

- [ ] **Step 2: 8 분해 stub 도 동일하게 (있다면)**

분해 stub 의 *위임 + 인터페이스* 본문에는 "하드 룰" 절 없음 — 이 PR 은 *theseus-harness* 만 영향. 8 분해 stub 은 *변경 없음*.

- [ ] **Step 3: self_lint.py 에 C39 추가**

```python
def check_hard_rule_markup(skill_root: Path) -> list[str]:
    """C39 — theseus-harness SKILL.md 의 하드 룰 절이 HARD-RULE 마크업 보유."""
    issues: list[str] = []
    skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if "## 하드 룰" in skill and "<!-- HARD-RULE:" not in skill:
        issues.append("SKILL.md: 하드 룰 절은 있으나 HARD-RULE 마크업 누락 (PR-10)")
    return issues
```

기존 체크 목록에 추가.

- [ ] **Step 4: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C39 추가됨.

- [ ] **Step 5: Commit**

```bash
git add skills/theseus-harness/SKILL.md skills/theseus-harness/scoring/self_lint.py
git commit -m "$(cat <<'EOF'
v0.4.0 — SKILL.md 하드 룰 HARD-RULE 마크업 (PR-10, 선택)

Claude skills guide HARD-GATE + superpowers 패턴 시각 강조 차용.
의미 변경 X, 마크업만. C39 (마크업 일관성) 신규.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13 (선택): PR-14 — 페이즈별 frontmatter allowed-tools 선언

**근거:** Claude skills guide tool permissions. 페이즈별 frontmatter 가 이미 있어 페이즈별 declare 가능. 우선순위 낮음.

**Files:**
- Modify: `skills/theseus-harness/phases/*.md` (14 파일 — frontmatter 에 allowed-tools 추가)
- Modify: `skills/theseus-harness/scoring/self_lint.py` (C43 추가)

- [ ] **Step 1: 페이즈별 tool 매핑 식별**

| 페이즈 | 필요 tool |
|--|--|
| 00 (naming) | Read, Write |
| 01 (intent + 마인드맵) | Read, Write, Agent |
| 02 (review) | Read, Write |
| 03 (재이해, 콜드) | Read, Write, Agent (fresh) |
| 04 (인터뷰) | AskUserQuestion, Read, Write |
| 05 (비평) | Read, Write, Agent |
| 06 (계획) | Read, Write, Agent |
| 07 (재이해) | Read, Write, Agent (fresh) |
| 08 (구현) | Read, Write, Edit, Bash, Agent (다수) |
| 09 (게이트) | Read, Bash (self_lint, pytest) |
| 10 (스프린트) | Read, Write, Edit, Bash, Agent |
| 11 (회귀 바이섹트) | Read, Bash (git bisect) |
| 12 (웹뷰) | Read, Write, Bash (bun) |
| 13 (핸드오프) | Read, Write, Bash (gh pr create — 자율 권한 시) |

- [ ] **Step 2: 각 페이즈 파일의 frontmatter 에 allowed-tools 추가**

각 `skills/theseus-harness/phases/NN-*.md` 파일 (현재 frontmatter 부재 — Step 1 검증 필요):

```bash
head -5 skills/theseus-harness/phases/04-clarify.md
```

만약 frontmatter 가 없으면 페이즈 본문 최상단에 추가:

```yaml
---
phase: 04-clarify
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
---
```

각 페이즈 파일에 위 패턴 적용 (페이즈별 tool 셋).

- [ ] **Step 3: self_lint.py 에 C43 추가**

```python
def check_phase_allowed_tools(skill_root: Path) -> list[str]:
    """C43 — 14 페이즈 파일이 frontmatter 에 allowed-tools 선언."""
    issues: list[str] = []
    for p in sorted((skill_root / "phases").glob("*.md")):
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            issues.append(f"{p.name}: frontmatter 누락 (PR-14)")
            continue
        if "allowed-tools:" not in text[:500]:
            issues.append(f"{p.name}: allowed-tools 선언 누락 (PR-14)")
    return issues
```

기존 체크 목록에 추가.

- [ ] **Step 4: self_lint 통과 확인**

Run: `python skills/theseus-harness/scoring/self_lint.py`
Expected: `"all_ok": true` + C43 추가됨.

- [ ] **Step 5: Commit**

```bash
git add skills/theseus-harness/phases/*.md skills/theseus-harness/scoring/self_lint.py
git commit -m "$(cat <<'EOF'
v0.4.0 — 14 페이즈 frontmatter allowed-tools 선언 (PR-14, 선택)

Claude skills guide tool permissions 정합. 페이즈별 좁은 tool 셋 명시.
호출 시 페이즈 진입 직전 tool 권한 검증 가능. C43 (정합 검증) 신규.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review (작성 후 자기 검토 결과)

**1. Spec coverage:**
- v4 spec §2 컴포넌트 E 의 9 머스트 PR (PR-1, 2, 3, 7, 8, 9, 11, 12, 13) — Task 1, 4, 5, 7, 8, 9, 6, 10, 3 에 1:1 매핑 ✓
- 2 선택 PR (PR-10, 14) — Task 12, 13 ✓
- v4 §6 산출물 위치 (부트스트래핑 트리 + 일반 git 브랜치) — Task 11 + 각 PR 의 git commit 으로 매핑 ✓
- v4 §5 신규 self_lint C36~C42 (필수) + C39, C43 (선택) — 각 Task 의 self_lint Step 으로 매핑 ✓

**2. Placeholder scan:**
- "TBD" 사용 위치: Task 2 의 PR-8 draft (§6 감산 변경표 / §8 SHA 표) 와 Task 10 의 PR-8 final 갱신. 이는 *살아있는 문서* 의 의도된 placeholder — Task 10 에서 *실제 값* 으로 갱신. ✓
- 다른 위치의 TBD 없음 ✓

**3. Type consistency:**
- self_lint 함수명 일관: `check_decomposed_standalone_honesty` (C36), `check_install_fresh_user_section` (C37), `check_resources_supplementary_ceiling` (C38), `check_hard_rule_markup` (C39), `check_anti_patterns_consolidation` (C40), `check_description_length_and_anti_pattern` (C41), `check_convention_consolidation` + `check_no_dead_convention_links` (C42), `check_phase_allowed_tools` (C43) — 모두 일관된 명명 ✓
- 파일 경로 일관: `skills/theseus-harness/scoring/self_lint.py`, `.ShipofTheseus/theseus-self/sprints/01/...` 모두 v4 spec 과 일치 ✓
- 커밋 메시지 형식 일관: `v0.4.0 — <제목> (PR-N[, 감산])` 패턴 ✓

→ 자기 검토 통과. 본 계획대로 진행 가능.

---

## 의존성 / 회귀 격리

- **PR-7 선행 강제** (Task 1): 메서돌로지 절이 *모든 후속 PR 의 정당성 근거*. 미선행 시 PR-2/3/12/13 의 머지 사유 약화.
- **PR-8 draft 가 두 번째** (Task 2): 부록 초안이 *PR-1~13 의 self-review 도구* — 다른 PR 작업 중 부록을 *참조* 가능.
- **PR-12 → PR-13 직렬** (Task 8 → 9): 둘 다 감산이라 회귀 위험 최대. PR-12 self_lint 통과 후 PR-13 시작.
- **PR-1, 2, 3, 9, 11 병렬 가능** (Task 3-7): 영향 파일 영역 분리.
- **PR-8 final** (Task 10): 모든 가산/감산 PR 머지 후 SHA 갱신.
- **선택 PR (Task 12, 13)**: 기본 미적용. 메인테이너가 명시 요청 시만.

---

## 다음 단계

**Plan complete and saved to `.ShipofTheseus/theseus-self/sprints/01/plan/06-borrow-plan.md`. 두 실행 옵션:**

**1. Subagent-Driven (recommended)** — 각 Task 별 fresh subagent 디스패치, Task 간 review checkpoint, 빠른 반복.

**2. Inline Execution** — 본 세션 안에서 Task 직렬 실행, batch checkpoint.

어느 쪽으로 진행할까요? **(1 / 2 답 부탁드립니다.)**
