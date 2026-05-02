---
skill_name: theseus-harness
skill_version: 0.3.0
phase: review-design
project_id: theseus-self
project_run: sprint-01
fingerprint: PENDING
prev_fingerprint: theseus-self-bootstrap-1차
produced_at: 2026-05-03
producer_agent: brainstorming-skill (외부 메타)
sprint_target: skill-self-review + claude-skills-guide compliance + multi-skill-mirror
revision: v4 (검토 포인트 자기 재검토 + 감산 차원 신규 — 제거/압축/중복 제거)
session_decisions:
  Q1: 2  # 보고서 + 구체 PR 후보
  Q2: 4  # 모든 후보 commit-ready
  Q3: 4  # 정적 분석 → 가설 → 실증
  Q4: 4  # 하이브리드 (디자인은 부트스트래핑, 코드는 일반 git)
  Q5: 2  # ralph 우선 → v3 에서 멀티 스킬로 확장
  Q6_borrow_principle: mirror  # 외부는 사각지대 탐지용 거울. 본래 스킬 1순위.
  Q7_review_target: self  # v3: 리뷰 = 본 하네스 자체 (ralph 비교는 거울로만)
---

> **프로젝트:** `theseus-self` · **회차:** `sprints/01` · **목적:** `00-review-design (v3)`
> **시작:** `2026-05-03` · **선행:** v0.3.0 머지 직후 (`997fd60`)

# 본 회차 디자인 v4 — 본 하네스 5 차원 자기 리뷰 (가산 + 감산)

## v1 → v2 → v3 → v4 진화 (사용자 피드백 흡수 누적)

ⓐ **v1 → v2** (1차 정정): ralph atomic feature 1:1 합성 시도 → *거울 원칙* 도입. 외부는 사각지대 탐지용 거울일 뿐, 합성 source 아님.

ⓑ **v2 → v3** (2차 정정): 리뷰 *대상* 정정. *본 하네스 자체 리뷰 + 보완* 이 메인 — ralph 는 *여러 거울 중 하나*. Claude skills guide + 멀티 스킬 (superpowers + OMC + autoresearch) 거울로 확장.

ⓒ **v3 → v4** (3차 정정): *감산 차원* 신규. 사용자 원문:

> *"좋아 이대로 진행해도 좋은데 추가로 검토 포인트들의 a-b-c-d 도 검토해야해 한번더 검토 해보자. 이 작업에서는 기존 스킬이나 description 을 제거하거나 압축하는것 중복제거하는것도 포함해작업 해야해."*

v3 가 *가산 차원* (새 추가는 거울 원칙으로 0) 만 다뤘음. v3 의 검토 포인트 ⓐ 자기 재검토 결과 — Claude skills guide 의 3 trade-off 중 *description 길이* 는 컨셉 정당화로 과보호됐음. v4 에서 *감산 PR* 신규: PR-12 (description 압축) / PR-13 (컨벤션 중복 통합) / PR-14 (tool permissions 페이즈별 선언) + PR-11 머스트 격상 (anti-patterns 통합 = 중복 제거).

→ **5 차원 자기 리뷰** (v4):
- ⓐ Claude skills guide 정합 (10 조항 audit)
- ⓑ 멀티 스킬 거울 (~30 원자, 거울 원칙 적용)
- ⓒ 본 하네스만의 장점 카탈로그 (10 차원 — v3 의 12 에서 정직 조정)
- ⓓ 놓친 가드라인 → 거울 원칙 *기존 증강만* 차용
- ⓔ **감산 차원 (v4 신규)** — 기존 스킬/description/컨벤션의 *제거/압축/중복 제거*

## 한 줄 요약

**본 회차는 본 하네스의 자기 리뷰 sprints/01 — 5 차원 (Claude skills guide + 멀티 스킬 거울 + 강점 카탈로그 + 놓친 차원 + 감산) 으로 ⓐ 이미 구현된 가드라인 ⓑ 본 하네스만의 강점 ⓒ 놓친 직교 차원 ⓓ *과잉 보호된 부분 (description / 중복 컨벤션)* 을 분리. 가산은 *기존 1 단락 증강만*, 감산은 *압축/통합/중복 제거*. 새 파일/컨벤션/에이전트 영구 추가 X, 영구 *감산* O. 핵심 산출물은 본 하네스 *10 차원 강점 + 거울 매트릭스 + 감산 변경 표* 가 담긴 부록 (`docs/reviews/...`) — 외부 독자에게 본 하네스 강점 부각의 메인 채널.**

## 비목표

ⓐ ralph (또는 어떤 단일 외부 스킬) 의 1:1 차용 — *명시 거부*. 거울로만 사용.
ⓑ 새 컨벤션 / 새 에이전트 / 새 스킬 *영구 추가* — 거울 원칙상 원칙적 거부. 직교 차원 입증 시만 *기존 한 단락 증강*.
ⓒ 본 하네스 *핵심 컨셉* 의 변경 — 14 페이즈 / DIP 우선 / 부트스트래핑 / 도자기 장인 비유 / 그레이드 시스템 / Phase 04 *유일* 인터럽트 — 모두 *보존*.
ⓓ Claude skills guide 의 *조항별 강압 적용*. 그러나 v4 에서 — *컨셉 정당화로 과보호된 부분* 은 압축 가능 (description 길이). 진짜 컨셉 trade-off 만 보존.
ⓔ 첫 외부 실 프로젝트 적용 1 건 — 본 리뷰가 그것을 *enable* 만.
ⓕ 영문 번역.
ⓖ *기능적으로 의미 있는* 컨벤션의 통합/제거 — 28 컨벤션 중 *진짜 중복* 만 PR-13 으로. 컨벤션 갯수 자체를 줄이는 건 *비목표*. 의도된 분산 (fragmentation 컨셉) 은 보존.

---

## 1. 아키텍처 — 4 차원 자기 리뷰

본 리뷰는 본 하네스 14 페이즈 중 *재이해 → 비평 → 계획 → 구현 → 게이트 → 스프린트* 6 페이즈를 본 저장소를 입력으로 자기 적용. 비평 페이즈 (05) 의 도구가 *멀티 스킬 거울 + Claude skills guide* 로 확장.

```
[입력]
  본 저장소 (skills/, docs/, examples/, scripts/, conventions/, phases/, agents/)
  Claude skills guide (Anthropic 공식 — SKILL.md frontmatter 룰, description 형식, examples 패턴)
  멀티 스킬 거울:
    - oh-my-ralph (RALPH.md, .ralph/, .claude/skills/clarify-image)
    - superpowers (브레인스토밍, TDD, executing-plans, writing-plans, debugging,
                  finishing-a-development-branch, verification-before-completion,
                  receiving/requesting-code-review, writing-skills 등)
    - OMC (agent 카탈로그, 모델 라우팅, autopilot/ultrawork/ralph/team)
    - autoresearch (Iterations: N 의 bounded iteration 계약)

[페이즈]
  03 (재이해, 콜드)  → 9 SKILL.md 의 단독 실행 의존성 + Claude skills guide 정합 audit
  05 (비평)          → 4 차원 거울 매트릭스 + 본 하네스 고유 장점 카탈로그
  06 (계획)          → 직교 차원만 *기존 증강* PR + 부록 PR (강점 부각 메인 채널)
  08 (구현)          → 실 PR (resources.md, INSTALL.md/self-check 증강) + 부록 PR + 메타 PR
  09 (게이트)        → 신규 self_lint C36~C39 (확장) + Claude skills guide 정합 체크
  10 (스프린트)      → self_score 회귀 부재 (1차 1.000000 → sprint-01 ≥ 0.99999)

[산출물]
  `.ShipofTheseus/theseus-self/sprints/01/`
  ├── 00-review-design.md (v3)            ← 본 문서
  ├── timing/start.json
  ├── intent/05-critique-vs-mirrors.md    ← 4 차원 거울 매트릭스
  ├── plan/06-borrow-plan.md              ← 6~7 PR DAG
  ├── impl/08-impl-log.md                 ← 각 PR git SHA
  ├── quality/09-quality-gate.md          ← C1~C35 + 신규 C36~C39 통과
  └── report.md                            ← self_score 시계열
```

## 2. 컴포넌트

### 컴포넌트 A — 단독 실행 가능성 프로브 (변경 없음, v2 동일)

**A1. 정적 의존성 그래프 (가설 단계)**

7 분해 stub (`theseus-{intent,plan,implement,quality,sprint,webview,handoff}`) 본문이 *위임 + 인터페이스* 만이고 룰 본문은 모두 `../theseus-harness/...` 점프 — fresh user 가 분해 스킬 1 개만 클론 시 dead link 숲 (가설).

**A2. 실증 (구현 페이즈)**: 빈 worktree + 분해 스킬 1 개 → 깨짐 위치 기록.

**산출 → `intent/05-critique-vs-mirrors.md` §1**.

### 컴포넌트 B — Claude Skills Guide 정합 audit (v3 신규)

Anthropic Claude Code skills guide 의 *조항별* 본 하네스 정합 검사:

| Claude skills guide 조항 | 본 하네스 대응 | 정합 상태 | 본 하네스 컨셉 정당화 (있다면) | 결정 |
|--|--|--|--|--|
| **frontmatter `name` (lowercase + hyphens)** | `theseus-harness`, `theseus-orchestrator` 등 9 스킬 모두 정합 | ✓ | n/a | 통과 |
| **frontmatter `description` (1~2 줄, when to invoke)** | 600+ 자 한국어 description (full pipeline 요약 + "한 줄 수정 사용 금지" 명시) | △ — 길이는 가이드 전형 초과, 그러나 *언제 사용 / 언제 거부* 가 명시되어 *기능적으로 정합* | 본 하네스 컨셉상 *그레이드 시스템 (G1 자동 거부)* 과 사전 위임 8 항이 description 에 박혀야 자동 트리거 시 잘못된 호출 방지. 압축은 *컨셉 손상*. | **컨셉 정합 — 보존**. 부록 §6 "본 하네스의 의도된 한계" 에 명시. |
| **examples (use cases)** | `examples/{evolving-spec,frozen-spec,fix-bug}.md` 3 개 (v0.3.0 신규) | ✓ | n/a | 통과 |
| **anti-patterns (when NOT to use)** | description 의 "한 줄 수정 같은 사소한 작업에는 사용 금지" + grades.md 의 G1 자동 거부 | ✓ | n/a | 통과 |
| **discoverability (자동 트리거 키워드)** | `theseus-harness` 외 슬래시 명령 명시. 키워드 매칭은 description 에 *14 페이즈 / 그레이드 / 의존 역전 / 부트스트래핑* 다수. | ✓ (다소 과잉이지만 정확) | n/a | 통과 |
| **tool permissions (`allowed-tools` frontmatter)** | 미선언 — Claude Code skills 는 의무 아님. | △ | 본 하네스는 모든 페이즈에서 다양한 tool 사용 (Read/Write/Bash/Agent/WebFetch). 제한 시 페이즈 일부 깨짐. | **명시 비선언이 정합** — 부록 §6 에 명시. |
| **HARD-GATE 마크업 (superpowers 패턴)** | "하드 룰" 절 (SKILL.md ⓐ~ⓛ) 텍스트 — 마크업 없음 | △ — 의미는 명시, 마크업은 부재 | superpowers 의 `<HARD-GATE>` 가 *시각적 강조* 효과. 본 하네스의 "하드 룰" 도 같은 의미. | **기존 증강 후보** — `<!-- HARD-RULE -->` 마크업 한 줄 추가 (선택). |
| **process flow diagram** | 14 페이즈 표 + 마인드맵 + 시퀀스 다이어그램 (Mermaid) + 페이즈 12 자동 웹뷰 | ✓ — superpowers 의 dot graph 보다 *더 풍부* | n/a | 통과 (오히려 본 하네스가 더 정교) |
| **skill priority (process vs implementation)** | 단일 진입점 (`theseus-orchestrator`) + 그레이드 라우팅 | ✓ | n/a | 통과 |
| **single-file vs deeply-fragmented** | *명시 분해* (단일 source of truth 룰) — Claude skills guide 의 "single SKILL.md" 권장과 trade-off | △ | 본 하네스 컨셉상 *파편화 우선* (`fragmentation.md`) — 28 컨벤션이 한 파일에 박히면 가독성/PR 회귀 표면 악화. *의도된 trade-off*. | **컨셉 정합 — 보존**. 부록 §6 명시. |

**산출 → `intent/05-critique-vs-mirrors.md` §2**.

**Claude skills guide 결산:**
- 직접 정합: 7 / 10 조항 ✓
- 컨셉 trade-off (의도된 비정합): 3 조항 — description 길이, 단일 파일 미준수, tool permissions 비선언
- *기존 증강 후보 1 개*: HARD-GATE 마크업 (superpowers 패턴 차용 — 시각적 강조만)

### 컴포넌트 C — 멀티 스킬 거울 매트릭스 (v3 확장)

ralph 9 원자 + superpowers 의 가드라인 + OMC 의 라우팅 + autoresearch 의 bounded iteration 을 본 하네스 거울로 사용. **결정 칸 대부분이 "이미 답함 (드롭, 부록만)" 이 정상.**

#### C-1. ralph (이미 v2 에서 다룬 9 원자 — 요약만)

| ralph 원자 | 결정 | 사유 |
|--|--|--|
| RALPH.md 6 섹션 | 드롭 (부록만) | 본 하네스가 14 페이즈 + Q-D 8 사전 위임 + frontmatter 봉인으로 더 풍부 답함 |
| Verification Commands 게이트 | 이미 차용 (v0.3.0 Q-D8) | n/a |
| Visual Spec (RALPH.png + clarify-image) | 드롭 (부록만) | 마인드맵 + Mermaid + 웹뷰가 시각 축 답. 이미지 입력은 텍스트 컨셉의 의도된 한계 |
| `.ralph/bootstrap.sh` | **기존 증강** | 직교 차원 — 본 하네스 *의도-기반 stack 점검* + ralph *실행-기반 환경 prep*. INSTALL.md 한 절. |
| `.ralph/check.sh` | 드롭 (부록만) | self-check.{sh,bat} 가 답 |
| `.ralph/run.sh` (wall-clock cap) | **기존 증강** | 직교 차원 — 품질/회수 vs 시간/토큰. resources.md opt-in 절. 컨셉 충돌 명시. |
| `.ralph/config` | 위와 통합 | 위와 통합 |
| Success Criteria + Verification 1:1 | 이미 차용 (Q-D8) | n/a |
| Risks 누적 ("Do not remove") | 드롭 (부록만) | frontmatter 봉인 + 회차 디렉터리가 자동화 |
| 메타 CLI 부재 | 드롭 (부록만) | orchestrator 가 *의도된 메타 레이어* — 컨셉 차이 |

#### C-2. superpowers — 메서돌로지 가드라인 (v3 신규)

| superpowers 원자 | 본 하네스 기존 동등 원자 | 같은 축 / 직교 | 놓친 차원? | 결정 |
|--|--|--|--|--|
| **`<HARD-GATE>` 마크업 (강조 표기)** | "하드 룰" 절 텍스트 (의미는 동일) | 같은 축 (의미는 정합) | △ 시각 강조만 미흡 | **기존 증강 후보 (선택)** — SKILL.md 의 "하드 룰" 절에 마크업 한 줄. PR 우선순위 낮음. |
| **Skill 자기 호출 계층 (using-superpowers → brainstorming → writing-plans)** | theseus-orchestrator → 8 분해 스킬 (frontmatter 자동 핸드오프) | 같은 축 (둘 다 stage gate 자동 진행) | ✗ — 본 하네스가 더 명시적 (frontmatter 봉인 + 핑거프린트 체인) | 드롭 (부록만) — *본 하네스가 더 단단* 명시 |
| **Red Flags (안티 패턴 표 — "이런 생각 STOP")** | 각 페이즈 본문의 "흔한 실패" 절 + grades.md 의 over-engineering 거부 | 같은 축 | △ — 본 하네스의 "흔한 실패" 가 페이즈 별 분산. 통합 카탈로그 부재. | **기존 증강 후보 (선택)** — `conventions/anti-patterns.md` 또는 SKILL.md 한 절로 통합 카탈로그. PR 우선순위 중간. |
| **brainstorming 의 HARD-GATE ("Do NOT invoke implementation skill until design approved")** | grades.md 의 G1 자동 거부 + Phase 04 의 인터뷰 의무 | 같은 축 (둘 다 단계 진입 hard gate) | ✗ | 드롭 (부록만) |
| **TDD red-green-refactor 명시 단계** | sprint 루프 (Phase 10) 의 무한 RGR + PHILOSOPHY ⓐ 매핑 | 같은 축 | ✗ — 본 하네스가 PHILOSOPHY 에 명시 매핑 | 드롭 (부록만) — *본 하네스가 더 명시* |
| **systematic-debugging (hypothesis tree, evidence-based)** | Phase 11 회귀 바이섹트 + AIDE Tree Search 차용 (PHILOSOPHY ⓓ) | 같은 축 | ✗ — 본 하네스가 더 풍부 (멀티버스 + 6 차원 트리거) | 드롭 (부록만) |
| **finishing-a-development-branch (merge/PR/cleanup 옵션)** | Phase 13 핸드오프 (자동 PR 생성, autonomy 권한 시) | 같은 축 | ✗ | 드롭 (부록만) |
| **verification-before-completion** | Q-D8 (v0.3.0) | 같은 축 | ✗ — 이미 차용 | n/a |
| **writing-skills (skill 작성 메타 스킬)** | (해당 영역 무관) | 무관 | n/a | 드롭 (관련 없음) |
| **using-git-worktrees (격리 작업)** | (해당 영역 무관 — 본 하네스는 산출물 디렉터리로 격리) | 직교? | △ — 멀티버스 (`checkpoints.md`) 가 디렉터리 분기로 답. worktree 는 git 레이어. | 드롭 (부록만) — 컨셉 차이 |

#### C-3. OMC (oh-my-claudecode) — 에이전트/모델 라우팅 (v3 신규)

| OMC 원자 | 본 하네스 기존 동등 원자 | 같은 축 / 직교 | 놓친 차원? | 결정 |
|--|--|--|--|--|
| **agent 카탈로그 (executor/explore/planner/architect/...)** | `agents/` 13 에이전트 (페이즈별) | 같은 축 (둘 다 역할 분리) | ✗ — 본 하네스는 페이즈 매핑이 더 명시 | 드롭 (부록만) |
| **모델 라우팅 (Opus/Sonnet/Haiku)** | `conventions/models.md` (페이즈별 모델 명시) | 같은 축 | ✗ — 이미 답함 | 드롭 (부록만) |
| **OMC tier-0 워크플로 (autopilot/ralph/ultrawork/team)** | theseus-orchestrator 자동 진행 | 같은 축 | ✗ — 본 하네스가 더 *컨셉 명확* (그레이드별 활성) | 드롭 (부록만) |
| **Hooks와 system reminder** | (Claude Code 레이어) | 무관 | n/a | 드롭 (관련 없음) |
| **Worktree 격리** | 산출물 디렉터리 + 멀티버스 분기 | 직교? | △ — 본 하네스는 git worktree 미사용 (산출물 디렉터리만) | 드롭 (부록만) — 컨셉 차이 명시 |

#### C-4. autoresearch — bounded iteration 계약 (v3 신규)

| autoresearch 원자 | 본 하네스 기존 동등 원자 | 같은 축 / 직교 | 놓친 차원? | 결정 |
|--|--|--|--|--|
| **`Iterations: N` inline config (회수 cap)** | grades.md sprint cap (G3=3) + 무한 스프린트 (G4/G5) | 직교 축 (회수 vs 품질) | △ — ralph wall-clock 과 같은 축 (기존 증강 후보로 통합) | (PR-3 에 통합) |
| **strict evaluator contract** | rubric.md 6 차원 + DIP hard cap + self_lint | 같은 축 (둘 다 객관 평가) | ✗ — 본 하네스가 더 풍부 | 드롭 (부록만) |
| **markdown decision logs** | `intent/05-decisions.md` + sprint 디렉터리 누적 + frontmatter 봉인 | 같은 축 | ✗ | 드롭 (부록만) |
| **max-runtime stop behavior** | resources.md 천정 자동 조정 + lessons.md 정체 카운터 | 직교 (시간 vs 자원) | △ — wall-clock 과 통합 | (PR-3 에 통합) |

**결산 (멀티 스킬):**
- 4 거울 (ralph + superpowers + OMC + autoresearch) 의 ~30 원자 중:
  - 이미 차용: 1 (Q-D8)
  - 같은 축 / 더 풍부 답함 (드롭, 부록만): ~22
  - 직교 차원 (기존 증강): 2 (bootstrap → INSTALL.md, wall-clock + bounded iter → resources.md)
  - 시각 강조만 미흡 (기존 증강 선택): 1 (HARD-GATE 마크업)
  - 통합 카탈로그 부재 (기존 증강 선택): 1 (anti-patterns 통합)

→ **6 PR + 부록**: PR-1 (분해 stub 단독성, 내부) / PR-2 (INSTALL.md 환경 prep) / PR-3 (resources.md opt-in 보조 천정) / PR-7 (메서돌로지 절) / PR-8 (부록 — 본 하네스 강점 + 거울 매트릭스) / PR-9 (sprint 시계열) + *선택 PR-10/11* (HARD-GATE 마크업 / anti-patterns 통합 — 우선순위 낮음).

### 컴포넌트 D — 본 하네스만의 장점 카탈로그 (v3 신규 — 부각 메인)

본 하네스가 **어떤 외부 스킬도 답 안 한 (또는 더 단단히 답한) 12 차원**:

| # | 차원 | 본 하네스 답 | 외부 스킬의 답 | 부각 채널 |
|--|--|--|--|--|
| 1 | **부트스트래핑** (자기 적용 + 회차 시계열) | BOOTSTRAP.md + `.ShipofTheseus/theseus-self/` + 35 self_lint + 임계 0.99999 | (없음 — 어떤 스킬도 자기 자신을 같은 게이트로 평가하지 않음) | PR-8 부록 §4-1 |
| 2 | **그레이드 시스템 + G1 자동 거부** | grades.md (G1~G5) + grade_assess.py 자동 추정 + Q-G1 사용자 확정 | superpowers brainstorming HARD-GATE 와 부분 매핑, ralph 무관 | PR-8 부록 §4-2 |
| 3 | **frontmatter 핑거프린트 체인 (페이즈 재진입)** | contracts.md + fingerprint.py + 단계별 진입 가드 | (없음 — 다른 스킬은 stage gate 가 명시 frontmatter 계약 부재) | PR-8 부록 §4-3 |
| 4 | **35 self_lint 객관 자기 검증** | self_lint.py + scripts/self-check.{sh,bat} + CI 역할 | (없음 — superpowers/OMC 도 lint 자동화 없음) | PR-8 부록 §4-4 |
| 5 | **14 페이즈 분해 깊이** | 명명 → 의도 → 마인드맵 → 콜드 재이해 → 인터뷰 → 비평 → 계획 → 재이해 → 구현 → 게이트 → 스프린트 → 바이섹트 → 웹뷰 → 핸드오프 | RALPH.md 6 섹션 / autoresearch 단일 mission 보다 *더 풍부* | PR-8 부록 §4-5 |
| 6 | **Da Capo + AIDE 멀티버스 + 닥터 스트레인지** | checkpoints.md + dacapo.md + AIDE Tree Search 차용 | superpowers systematic-debugging 보다 *더 풍부* | PR-8 부록 §4-6 |
| 7 | **도자기 장인 비유 — 깨고 다시 빚기 6 차원 트리거** | PHILOSOPHY (DIP / 코드 오류 / 기획-구현 갭 / NFR / 의도 표류 / 정체) → 페이즈 06 부터 통째 재빚기 | (없음 — 부분 수정 vs 통째 재빚기 트리거가 명시된 스킬 없음) | PR-8 부록 §4-7 |
| 8 | **DIP 단독 hard cap + SOLID 위계 명시** | quality-gate.md 의 5 게이트 + DIP cap 0.6 | (없음 — 다른 스킬은 SOLID 다섯 동등) | PR-8 부록 §4-8 |
| 9 | **Phase 04 의 *유일* 인터럽트 + Q-D 사전 위임 카탈로그** | autonomy.md + phases/04-clarify.md + Q-D1~D8 (오토노미 약속) | (없음 — autonomy 의 강한 약속이 명시된 스킬 없음) | PR-8 부록 §4-9 |
| 10 | **bun + hono + react 자동 웹뷰** | webview-builder.md + Phase 12 + 6 탭 + Mermaid 자동 렌더 + TimingHeader 라이브 | (없음 — 시각화 자동 생성 트랙 부재) | PR-8 부록 §4-10 |
| 11 | **6 차원 rubric 객관 점수 + 임계 0.999 / 자기 0.99999** | rubric.md + score.py + grades.md 임계 매트릭스 | autoresearch evaluator 와 같은 축, 더 풍부 | PR-8 부록 §4-11 |
| 12 | **합성 패턴 6 (Ralph + OhMy + 우로보로스 + AIDE + Wiki + Da Capo)** | PHILOSOPHY 명시 차용 + 자기 점수로 검증 | (없음 — 다른 스킬은 *자신의 패턴* 만) | PR-8 부록 §4-12 |

이 표가 **PR-8 부록의 메인 콘텐츠** — 본 하네스 강점이 외부 독자에게 한눈에 보이게.

### 컴포넌트 E — PR 후보 (commit-ready 9 머스트 + 1 선택, v4)

**가산 PR (변경 없음 — v3 와 동일):**

| PR | 제목 | 변경 유형 | 근거 | 신규 self_lint |
|--|--|--|--|--|
| PR-1 | 분해 stub 단독성 — 주장 vs 행동 정합 | 보강 또는 정정 | 컴포넌트 A2 실증 | C36 |
| PR-2 | INSTALL.md + self-check 의 fresh-user 환경 prep | 기존 증강 (1 절) | 컴포넌트 C-1 ralph bootstrap 직교 | C37 |
| PR-3 | resources.md 의 *opt-in 보조 천정* (wall-clock + token + bounded iter) | 기존 증강 (1 절) | C-1 ralph wall-clock + C-4 autoresearch 통합 | C38 |
| PR-7 | PHILOSOPHY/README 의 *블라인드 스팟 메서돌로지* 절 | 메타 (텍스트만) | v2/v3 피드백 컨벤션화 | (없음) |
| PR-8 | `docs/reviews/2026-05-03-skill-self-review.md` — *부각 부록 (메인)* | 신규 문서 (본 회차 핵심, *살아있는 문서* — 다른 PR 머지 후 SHA 갱신) | 컴포넌트 D 의 10 차원 강점 + B/C 거울 매트릭스 + 신규 §X 감산 변경표 | (없음) |
| PR-9 | sprint-01 self_score 시계열 자동화 | 메타 (self-check 확장) | BOOTSTRAP.md 회차 누적 룰 | (없음) |

**가산 PR (v3 선택 → v4 머스트 격상):**

| PR | 제목 | 변경 유형 | 근거 (v4 격상 사유) | 신규 self_lint |
|--|--|--|--|--|
| PR-11 | 페이즈별 "흔한 실패" → 통합 anti-patterns 카탈로그 | 기존 증강 (SKILL.md 한 절) + **중복 제거** | 사용자 *"중복 제거"* 요구와 직접 정합. 14 페이즈에 분산된 "흔한 실패" 본문이 *컨셉별 중복* 다수. | C40 |

**감산 PR (v4 신규 — 사용자 새 요구):**

| PR | 제목 | 변경 유형 | 근거 | 신규 self_lint |
|--|--|--|--|--|
| **PR-12** | 9 SKILL.md description 압축 (600+ → 100~150 자) | **감산 (영구 압축)** | v3 검토 포인트 ⓐ 자기 재검토. description 의 그레이드/페이즈 디테일은 *body 가 답함* — 자동 트리거 메타데이터 한도 초과 부분 압축. *컨셉 손상 X*. | C41 (description 길이 + when-not-to-use 절 보유 검사) |
| **PR-13** | 28 컨벤션 중 *진짜 중복/과잉 분산* 식별 + 통합 | **감산 (영구 통합)** | C-2 결과로 *fragmentation 컨셉* 은 보존 정당, 그러나 *컨셉별 중복* 가능 (예: lessons.md + dacapo.md 가 정체 누적 학습이라는 같은 영역 — 흡수 가능?) | C42 (통합 후 self_lint C2 인덱스 정합 유지) |

**가산 PR (v4 선택 유지):**

| PR | 제목 | 변경 유형 | 근거 | 신규 self_lint |
|--|--|--|--|--|
| PR-10 (선택) | SKILL.md "하드 룰" 절 `<!-- HARD-RULE -->` 마크업 | 기존 증강 (마크업만) | C-2 superpowers HARD-GATE 시각 강조 | C39 (마크업 일관성) |
| PR-14 (선택) | 페이즈별 frontmatter 의 `allowed-tools` 선언 | 기존 증강 (frontmatter 한 줄씩) | C-1 Claude skills guide tool permissions | (선택 시 C43) |

**우선순위 (v4 갱신):**
- **머스트 (9)**: PR-1, 2, 3, 7, 8, 9, 11, 12, 13 — 자기 일관성 + 강점 부각 + *영구 감산*.
- **선택 (2)**: PR-10, PR-14 — 시각/정합 강화. 다음 회차 가능.

**PR 의존 DAG (v4):**
```
PR-7 (메서돌로지 절) ── 모든 PR 의 정당화 선행
  ↓
PR-8 (부록 초안) ── 가장 먼저 머지 권장 — 강점 매트릭스가 다른 PR 의 정당성 근거
  ↓
가산 (병렬):  PR-1, PR-2, PR-3, PR-9, PR-11
감산 (직렬):  PR-12 (description 압축) → PR-13 (컨벤션 통합)
              ※ 감산은 self_lint 회귀 위험이 가장 커 *직렬*. PR-12 통과 후 PR-13.
  ↓
PR-8 (부록 갱신) ── 모든 PR 머지 후 SHA + 영향 표 추가
  ↓
PR-10, PR-14 (선택) ── 다음 회차 가능
```

**감산 PR (PR-12, 13) 의 회귀 가드:**
- PR-12: 9 SKILL.md description 압축 후 *각 SKILL.md 의 본문 (body) 에 그레이드/페이즈/거부 시점이 명시* 인지 C41 가 검사. description 만 짧아지면 본 하네스의 *기능적 정합* 깨지므로 — body 보강이 필수 동반.
- PR-13: 통합 후보 컨벤션 (예: lessons + dacapo) 의 *링크가 모든 페이즈/에이전트/SKILL.md 에서 갱신* 인지 C42 가 검사. self_lint C2/C3/C4 (인덱스 정합) 회귀 0 보증.

**v1 → v2 → v3 → v4 PR 변동 요약:**
- v1: 9 PR (강압 합성)
- v2: 6 PR (거울 원칙)
- v3: 6 머스트 + 2 선택 (멀티 스킬 거울)
- **v4: 9 머스트 + 2 선택** (감산 차원 신규: PR-12, PR-13 + PR-11 선택→머스트 격상)

### 컴포넌트 F-감산 — *제거/압축/중복 제거* 후보 매트릭스 (v4 신규)

본 회차의 *영구 감산* 후보. 사용자 새 요구: *"이 작업에서는 기존 스킬이나 description 을 제거하거나 압축하는것 중복제거하는것도 포함해작업"*.

#### F-1. SKILL.md description 압축 (PR-12)

| 스킬 | 현재 description 길이 | 압축 후 (목표) | 이전될 디테일 → body 위치 |
|--|--|--|--|
| theseus-harness | 600+ 자 | ~150 자 | 14 페이즈 / 그레이드 / 백엔드 기본 / 사전 위임 → SKILL.md body (이미 있음) |
| theseus-orchestrator | ~250 자 | ~120 자 | 분해 호출 순서 → body |
| theseus-intent | ~100 자 | ~80 자 | 페이즈 00–05 디테일 → body (이미 있음) |
| theseus-plan | ~100 자 | ~80 자 | 시퀀스 다이어그램 동봉 등 → body |
| theseus-implement | ~80 자 | ~70 자 | (현재도 짧음 — 미세 압축만) |
| theseus-quality | ~70 자 | ~60 자 | (현재도 짧음) |
| theseus-sprint | ~80 자 | ~70 자 | (현재도 짧음) |
| theseus-webview | ~80 자 | ~70 자 | (현재도 짧음) |
| theseus-handoff | ~80 자 | ~70 자 | (현재도 짧음) |

**압축 원칙:**
- ⓐ description 은 *자동 트리거* 용 *언제 쓸지 / 언제 거부할지* 만 1~2 줄.
- ⓑ "한 줄 수정 같은 사소한 작업에는 사용 금지" 같은 anti-pattern 절은 *유지* (Claude skills guide 권장).
- ⓒ 페이즈 디테일 / 그레이드 매트릭스 / 사전 위임 카탈로그 / 백엔드 기본값 등은 모두 *body 가 답함* — description 에 *중복 박힐* 필요 없음.
- ⓓ C41 (신규) 가 압축 후에도 *anti-pattern 절 보유* + *body 의 디테일 명시* 검사.

#### F-2. 28 컨벤션 중 *진짜 중복* 식별 (PR-13)

본 회차에서 *식별만* 하고 통합은 PR-13 안에서 수행. 후보 (가설 — 컴포넌트 A2 실증 단계 검증):

| 통합 후보 쌍 | 같은 영역? | 통합 정합? | 결정 후보 |
|--|--|--|--|
| `lessons.md` + `dacapo.md` | 정체 학습 누적 (lessons) + 자기 강화 회귀 (dacapo) — 부분 겹침 | △ — dacapo 가 lessons 의 *상위 메타* 일 가능성 | 검증 필요 (PR-13 내) |
| `checkpoints.md` + `dacapo.md` | 멀티버스 분기 (checkpoints) + 자기 강화 (dacapo) | △ — dacapo 가 checkpoints 사용 | 검증 필요 |
| `interview.md` + `prd-handling.md` | 인터뷰 형식 (interview) + PRD 입력 처리 (prd-handling) | ✗ — prd-handling 이 interview 의 *특수 모드* | 통합 정합 (prd-handling 을 interview.md 의 한 절로) |
| `sub-agents.md` + `competition.md` | 재귀 분해 (sub-agents) + 격리 경쟁 (competition) | ✗ — 다른 축 (분해 vs 경쟁) | 분리 유지 |
| `resources.md` + `spec-catalog.md` | 리소스 천정 + NFR 카탈로그 — 부분 겹침 | △ | 검증 필요 |

**통합 원칙:**
- ⓐ *기능적으로 진짜 중복* 만 통합. 컨셉이 다르면 (다른 추상 차원) 분리 유지.
- ⓑ 통합 시 *self_lint C1~C4 인덱스 정합* 유지 — 모든 SKILL.md/phase/agent 링크 갱신.
- ⓒ C42 (신규) 가 통합 후 cross-link 무결성 검사.
- ⓓ *fragmentation 컨셉 보존* 이 우선 — 의도된 분산 (페이즈 별 / 도메인 별) 은 통합 금지.

#### F-3. 페이즈별 "흔한 실패" 중복 통합 (PR-11)

각 페이즈 파일에 분산된 "흔한 실패" 절을 SKILL.md 한 절로 통합 — *anti-pattern 통합 카탈로그*. 페이즈별 *고유한 실패* 만 페이즈 본문에 남기고, *공통 안티 패턴* (조기 추상화 / 분산 모놀리스 / sync-where-async / 자체 인증 등) 은 통합. C40 가 통합 후 페이즈별 본문이 *고유 실패만 보유* 검사.

### 컴포넌트 G — 부록 PR-8 의 구조 (v4 강점 부각 메인 + 감산 변경표 신규)

`docs/reviews/2026-05-03-skill-self-review.md`:

```
1. 거울 원칙 — 외부 스킬은 사각지대 탐지용, 합성 source 아님.

2. Claude skills guide 정합 매트릭스 (10 조항, 7 직접 정합 + 3 컨셉 trade-off)

3. 멀티 스킬 거울 매트릭스:
   3-1. ralph 9 원자 (이미 답함 6 / 차용 완료 1 / 기존 증강 2)
   3-2. superpowers 가드라인 (9 원자, 모두 같은 축 또는 시각 강조만 미흡)
   3-3. OMC 라우팅 (5 원자, 모두 같은 축 또는 무관)
   3-4. autoresearch bounded iter (4 원자, 1 직교 — wall-clock 과 통합)

4. **본 하네스만의 12 차원 강점** (컴포넌트 D — 부각 메인):
   부트스트래핑 / 그레이드 G1 거부 / 핑거프린트 체인 / self_lint /
   14 페이즈 / 멀티버스 / 도자기 장인 / DIP 위계 /
   Phase 04 *유일* 인터럽트 / 자동 웹뷰 / 6 차원 rubric / 합성 패턴 6

5. **본 하네스의 의도된 한계** (컨셉 정당화):
   ⓐ description 길이 — 그레이드 + 사전 위임 명시 필요
   ⓑ 단일 SKILL.md 미준수 — fragmentation.md 컨셉
   ⓒ tool permissions 비선언 — 페이즈별 광범위 사용
   ⓓ 이미지 입력 미커버 — 텍스트 기반 컨셉
   ⓔ Phase 04 외 verification 실행 미요구 — LLM/사용자 책임 분리
   ⓕ 메타 CLI 레이어 (orchestrator) — *의도된 메타*

6. **감산 변경표 (v4 신규)**:
   ⓐ description 압축 — 9 SKILL.md 의 변경 전/후 길이 + 이전된 디테일 위치
   ⓑ 컨벤션 통합 — 진짜 중복 페어 + 통합 후 인덱스 갱신 표
   ⓒ anti-pattern 통합 — 페이즈별 분산 → SKILL.md 통합 카탈로그

7. 다음 회차 후보 (sprint-02 candidates):
   ⓐ 첫 외부 실 프로젝트 적용 1 건 + 4 메트릭 post-mortem (정직 박스 ⓓ)
   ⓑ 선택 PR-10, PR-14 머지
   ⓒ 다른 스킬 추가 거울 비교 (frontend-design, claude-hud 등)
```

이 부록이 **본 회차의 가장 가치 있는 산출물** — *외부 독자가 본 하네스의 본질적 강점을 한눈에 인지*.

## 3. 데이터 흐름 (v3 — 4 차원 자기 리뷰)

```
[입력 수집]
  본 저장소 (v0.3.0)
  Claude skills guide (Anthropic 공식 SKILL.md spec)
  멀티 스킬:
    - oh-my-ralph (WebFetch — RALPH.md + .ralph/* + clarify-image)
    - superpowers (브레인스토밍 자체 + 시스템 reminder 의 9+ 스킬)
    - OMC (CLAUDE.md 시스템 프롬프트 + omc-reference)
    - autoresearch (시스템 reminder 의 7 변종)

[정적 분석]
  ↓
  standalone_breakage_map.json    (컴포넌트 A1)
  claude_skills_guide_audit.md    (컴포넌트 B)

[거울 비교]
  ↓
  multi_skill_mirror_matrix.md    (컴포넌트 C)

[강점 카탈로그]
  ↓
  unique_strengths_12.md          (컴포넌트 D)

[실증]
  ↓
  empirical_breakage_log.md       (컴포넌트 A2)

[비평 → 계획]
  ↓
  intent/05-critique-vs-mirrors.md (위 5 산출물 통합)
  plan/06-borrow-plan.md           (PR-1, 2, 3, 7, 8, 9, [10, 11] DAG)

[구현 — 별도 git 브랜치]
  ↓
  feat/v0.4.0-self-review-and-mirrors  (또는 v0.3.1 — 메인테이너 결정)
  6 (또는 8) PR 각각 1 커밋

[게이트]
  ↓
  scripts\self-check.bat
  C1~C35 + 신규 C36~C39 (또는 ~C40) 통과 + self_score ≥ 0.99999

[스프린트 보고]
  ↓
  report.md — 1차 self_score 1.000000 → sprint-01 self_score ≥ 0.99999
```

## 4. 에러 처리 (v3)

| 상황 | 행동 |
|--|--|
| A2 실증에서 분해 stub 가 어떤 PR-1 보강으로도 단독 실행 불가 | PR-1 철회 + README 의 "단독 호출 가능" 주장 *제거* (정직). |
| Claude skills guide 정합 검사에서 의도된 trade-off 외에 *진짜 위반* 발견 | 즉시 새 PR 후보로 추가, 그 결과 v3 의 PR 리스트 갱신. |
| 컴포넌트 D 의 12 차원 강점 중 외부 거울에 의해 *이미 다른 스킬이 답한* 것 발견 | 12 → N 으로 축소. *정직한 강점 카탈로그* 유지. |
| PR-2/3 가 self_lint 회귀 발생 | 해당 PR 안에서 신규 절 위치 재배치. 그래도 회귀면 PR 철회. |
| PR-7 (메서돌로지 절) 가 PR 리뷰에서 거부 | PR-2/3/10/11 도 보류. PR-1, 8, 9 만 머지 (자기 일관성 유지). |
| 본 회차 self_score < 0.99999 | 부트스트래핑 정의상 *허용 안 됨*. 깨진 PR revert. report.md 에 fail 보고 후 재진입. |

## 5. 테스트 / 검증 (v3)

**기존 self_lint 35 + 신규 (3~5):**

ⓐ **C36** — 분해 SKILL.md 의 "단독 호출" 주장과 본문이 점프하는 외부 경로의 절대성 일치.
ⓑ **C37** — `INSTALL.md` 가 fresh-user 환경 prep 절 보유 + `scripts/self-check.{sh,bat}` 가 첫 줄 stack 점검 호출.
ⓒ **C38** — `conventions/resources.md` 가 *opt-in 보조 천정* 절 + 기본 비활성 + 컨셉 충돌 명시 + Q-D3 sub-option 흡수.
ⓓ **C39 (PR-10 선택 시)** — 모든 SKILL.md 의 "하드 룰" 절이 `<!-- HARD-RULE -->` 마크업.
ⓔ **C40 (PR-11 선택 시)** — `conventions/anti-patterns.md` (또는 통합 SKILL.md 절) 가 모든 페이즈 "흔한 실패" 인덱싱.

**Claude skills guide 정합 자동 검사 (PR-8 부록과 함께 1 회 실행):**
ⓕ 9 SKILL.md 의 frontmatter 가 `name`, `description`, `version` 필드 보유 — *현재 통과* (수동 확인).
ⓖ description 의 *anti-pattern 절* 명시 — 본 하네스는 모두 통과.

**self_score 회귀 부재:** 1차 1.000000 → sprint-01 ≥ 0.99999 유지.

## 6. 산출물 위치 (Q4=4 하이브리드, 변경 없음)

부트스트래핑 트리: `.ShipofTheseus/theseus-self/sprints/01/`.
일반 git 브랜치: `feat/v0.4.0-self-review-and-mirrors` 또는 `feat/v0.3.1-self-review-and-mirrors`.
부록 (PR-8): `docs/reviews/2026-05-03-skill-self-review.md` (일반 git 트리, 외부 독자 친화).

## 7. 그레이드 자기 추정

본 회차 작업 그레이드:
- `grade_assess.py` 추정: G2 (단일 사이드 — conventions/INSTALL/docs 만 변경, 새 파일 X).
- 자기 확정: **G2 — Simple**.
- 부트스트래핑 임계 0.99999 강제 — 그레이드 무관 한 단계 빡빡 적용.

## 8. 자율성 정책 (Q-D 답)

(v2 와 동일)

## 9. 단위 분리

- PR 한 단위 = *한 직교 차원* 또는 *한 메타* 또는 *한 부록*.
- 부록 (PR-8) 가 본 회차 메인 — 코드 PR 보다 *먼저 머지 권장* (강점 매트릭스가 PR-2/3 정당성 근거).

## 10. 본 디자인의 자기 모순 검사 (v4 — 검토 포인트 a-b-c-d 자기 재검토 결과)

### 10-1. 일반 자기 모순 검사

ⓐ **placeholder:** A1, B 는 가설/정합 단계. 명시 ✓.
ⓑ **내부 정합:** 컴포넌트 B/C 의 *기존 증강* 결정과 §2 컴포넌트 E PR-2/3 매핑 1:1 ✓. 신규 self_lint (C36~C42 머스트 + C39/C43 선택) 와 §5 매핑 1:1 ✓.
ⓒ **거울 원칙:** v4 의 *가산 PR* 모두 *내부 fix* 또는 *기존 한 단락 증강* 또는 *부록 문서* — 새 컨벤션/에이전트/스킬 *영구 추가 0*. *감산 PR* 은 거울 원칙과 직교 (외부 차용 아닌 내부 정합 강화). ✓
ⓓ **부각 채널:** 컴포넌트 D 의 10 차원 강점이 PR-8 부록 §4 로 직접 매핑 + 감산 변경표 (PR-12, 13) 도 부록 §6 에 — 외부 독자에게 강점 + 정합 둘 다 부각. ✓
ⓔ **컨셉 보존:** 14 페이즈 / DIP 우선 / 부트스트래핑 / 도자기 장인 / 그레이드 / Phase 04 *유일* 인터럽트 — 모두 보존. description 압축은 *컨셉 손상 X* (디테일이 body 로 이전, anti-pattern 절은 유지). ✓
ⓕ **모호성:** "v0.4.0 vs v0.3.1" §6 메인테이너 위임 ✓. 감산 PR (PR-12, 13) 은 *컨셉 변경* 이 아닌 *과보호 해소* 라 v0.3.1 패치 가능, PR-3 (resources opt-in) + PR-7 (메서돌로지 절) 만 v0.4.0 마이너 점프 트리거.

### 10-2. 검토 포인트 a-b-c-d 자기 재검토 (v4 신규)

v3 메시지 끝의 4 검토 포인트를 *한 번 더* 자기 답:

**검토 포인트 ⓐ — Claude skills guide 의 3 trade-off 보존 결정 — 컨셉 정당화 충분한가?**

| trade-off | v3 결정 | v4 자기 재검토 결과 |
|--|--|--|
| description 600+ 자 | 컨셉 정당화로 보존 | **부분 부정** — 그레이드/페이즈 디테일은 *body 가 답함*. 600+ 자는 *과보호*. anti-pattern 절은 보존, 디테일은 압축. → **PR-12 신규 (감산)** |
| 단일 파일 미준수 (28 컨벤션) | fragmentation 컨셉 정당 보존 | **유지** — 컨셉은 정당. 다만 *진짜 중복 페어* (lessons + dacapo 등) 검증 필요. → **PR-13 신규 (감산, 식별 + 통합)** |
| tool permissions 비선언 | 페이즈별 광범위 사용 정당 | **부분 부정** — 페이즈별 frontmatter 가 이미 있어 페이즈별 declare 가능. 우선순위 낮음. → **PR-14 선택 (감산)** |

→ 결론: 3 trade-off 중 *2 개가 과보호*. v4 에서 PR-12, 13 머스트, PR-14 선택으로 해소.

**검토 포인트 ⓑ — 12 차원 강점 카탈로그 — 빠진 / 과장된 차원 있나?**

| 차원 | v3 평가 | v4 자기 재검토 |
|--|--|--|
| #6 멀티버스 / Da Capo | unique 강점 | **과장** — AIDE 차용 + Da Capo (사용자 이전 연구). *합성* 이 unique, *원자* 는 차용. *합성 자체* 를 강조. |
| #12 합성 패턴 6 | unique 강점 | **과장** — 차용 자기 정당화이지 *기능* 은 아님. *#6 의 합성 강조* 와 합쳐 1 차원으로. |
| 다른 10 차원 (1, 2, 3, 4, 5, 7, 8, 9, 10, 11) | unique | **유지** ✓ |

→ 결론: 12 → **10 차원** 으로 정직 조정 (#6 + #12 → "합성 패턴의 단단한 흡수" 1 차원으로). PR-8 부록 §4 갱신.

**검토 포인트 ⓒ — PR-10/11 (선택) 을 이번 회차 포함 vs 다음 회차?**

| PR | v3 | v4 결정 | 사유 |
|--|--|--|--|
| PR-10 (HARD-RULE 마크업) | 선택 | **선택 유지** — 시각 강조만, 다음 회차 가능 | 효과 낮음, 회귀 표면도 낮음. 본 회차 핵심과 분리 가능. |
| PR-11 (anti-patterns 통합) | 선택 | **머스트 격상** | *중복 제거* 사용자 요구와 직접 정합. 페이즈별 분산 통합은 *영구 감산* 의 일부. |

→ 결론: PR-11 머스트 격상 (감산 차원 PR 군에 합류).

**검토 포인트 ⓓ — PR-8 부록 우선 머지 전략 — 강점 매트릭스가 PR-2/3 정당성 근거 흐름 정합?**

| 검토 | 결과 |
|--|--|
| PR-8 부록이 PR-2/3 (직교 차원 차용) 의 정당성 매트릭스 | ✓ 정합 |
| PR-8 이 PR-12/13 (감산) 의 정당성 매트릭스도 되어야 함 | **부분 부족** — v3 의 PR-8 구조는 *가산만*. v4 에서 §6 *감산 변경표* 신규 (컴포넌트 G 갱신). |
| PR-8 이 *살아있는 문서* (다른 PR 머지 후 SHA + 영향 표 갱신) | **명시 추가** — DAG 의 *마지막* 에 PR-8 갱신 단계 박힘. |

→ 결론: PR-8 의 *초안* 이 가장 먼저 머지 + *완성판* 이 모든 PR 머지 후 마지막에 SHA 갱신 PR (또는 부록 PR 자체 amend). DAG 갱신.

## 11. 다음 단계

본 디자인 v3 를 메인테이너가 승인하면:

ⓐ writing-plans 스킬로 *PR-1, 2, 3, 7, 8, 9 (+ 선택 10, 11) 각각의 step-by-step 구현 계획* 생성.
ⓑ 그 계획이 곧 `plan/06-borrow-plan.md` 본문.
ⓒ 구현은 별도 git 브랜치, PR 단위 커밋.
ⓓ **PR-8 (부록) 을 가장 먼저 머지 권장** — 12 차원 강점 카탈로그가 외부 독자에게 본 하네스 본질을 즉시 전달하는 메인 채널.

---

## Appendix v1 → v2 → v3 → v4 PR 변동표

| PR | v1 | v2 | v3 | v4 | 사유 |
|--|--|--|--|--|--|
| PR-1 분해 stub 단독성 | 유지 | 유지 | 유지 | 유지 | 본 하네스 self-discovery |
| PR-2 bootstrap | 새 파일 | 재프레이밍 (INSTALL/self-check 증강) | 유지 | 유지 | 직교 차원 |
| PR-3 wall-clock cap | 새 파일 | 재프레이밍 (resources opt-in) | 확장 (+autoresearch 통합) | 유지 | 직교 차원 |
| PR-4 Q-D8 실행 게이트 | 신규 | 드롭 | 드롭 | 드롭 | 코드 부재 시점 실행 무의미 |
| PR-5 RALPH 변환기 | 신규 | 드롭 | 드롭 | 드롭 | 같은 축, 부록으로 충분 |
| PR-6 시각 입력 에이전트 | 신규 | 드롭 | 드롭 | 드롭 | 컨셉 정합 보호 |
| PR-7 동결 예외 절 | 신규 | 재프레이밍 (메서돌로지) | 유지 | 유지 | 메서돌로지 컨벤션화 |
| PR-8 부록 | 부록 옵션 | 격상 | 재격상 (12 차원) | **재재격상** — 10 차원 + 감산 변경표 + 살아있는 문서 | 강점 부각 메인 + 감산 정합 |
| PR-9 sprint 시계열 | 신규 | 유지 | 유지 | 유지 | BOOTSTRAP 회차 룰 |
| PR-10 HARD-RULE 마크업 | n/a | n/a | 선택 | **선택 유지** | 시각 강조 |
| PR-11 anti-patterns 통합 | n/a | n/a | 선택 | **머스트 격상** (중복 제거) | 사용자 *중복 제거* 요구 정합 |
| **PR-12 description 압축** | n/a | n/a | n/a | **신규 머스트 (감산)** | v4 검토 포인트 ⓐ — description 과보호 해소 |
| **PR-13 컨벤션 통합 (lessons+dacapo 등)** | n/a | n/a | n/a | **신규 머스트 (감산)** | v4 검토 포인트 ⓐ — 진짜 중복 페어 식별 + 통합 |
| **PR-14 allowed-tools 페이즈별 선언** | n/a | n/a | n/a | **신규 선택 (감산)** | v4 검토 포인트 ⓐ — Claude skills guide 정합 |

**총합 변천:**
- v1: 9 PR (강압 합성)
- v2: 6 PR (거울 원칙)
- v3: 6 머스트 + 2 선택 (멀티 스킬 거울)
- **v4: 9 머스트 + 2 선택** (감산 차원 신규: PR-11 격상 + PR-12, 13 머스트 + PR-14 선택)

**새 파일/컨벤션 영구 *추가*:** v1 다수 → v2/v3/v4 *0*.
**새 *감산* (영구 압축/통합):** v1/v2/v3 *0* → v4 — 9 SKILL.md description 압축 + 컨벤션 통합 ~1~3 페어 + 페이즈 anti-pattern 통합 + (선택) tool permissions 정합.

이게 v4 의 핵심 차이: *가산은 거울 원칙으로 0 유지, 감산은 사용자 새 요구로 신규*. 본 하네스가 *더 단단해지면서 더 가벼워짐* — 도자기 장인이 *덜어내는* 단계.
