---
name: theseus-orchestrator
version: 0.9.29
description: theseus-harness 의 15 페이즈 자율 driver — entry point. 페이즈 04 인터뷰 후 인터럽트 0. 본 entry skill = 순서 + 인터럽트 정책 + 그레이드 라우팅 단일 책임. 산출물 내용 컨벤션은 ../theseus-harness/conventions/ 단일 source — 페이즈 진입 시 매핑된 본문만 lookup.
---

# theseus-orchestrator — 사용자 entry skill

## 한 줄 요약

**본 스킬은 사용자 entry point.** 콘텐츠 source 는 [`../theseus-harness/`](../theseus-harness/) 동반 필수. 호출되면 14 페이즈를 자율 driver 로 진행 — 페이즈 04 인터뷰 1회 후 인터럽트 0.

## HARD-RULE — 본 스킬 호출 직후 첫 동작 (위반 시 즉시 정지)

> 본 스킬이 호출되면 당신의 *첫 동작* 은 다음이다 — 다른 어떤 작업도 우선 안 됨:
>
> 1- `.ShipofTheseus/<프로젝트>/timing/start.json` 작성 (시작 시각).
> 2- 페이즈 00 (G3+) 또는 페이즈 01 (G2) 의 산출물 작성 — `.ShipofTheseus/<프로젝트>/{naming/00-naming.md | intent/01-intent.md}`.
> 3- 그 *다음* 에 grade_assess + 페이즈 04 인터뷰 + 후속 페이즈 진행.
>
> **금지 (자동 거부 — 실행 에이전트 의 첫 동작이 다음이면 본 스킬 위반):**
>
> a- 사용자 요구를 받자마자 *직접* 코드 (Go / Python / TS / etc.) 작성 — 페이즈 산출물 우회.
> b- `.ShipofTheseus/<프로젝트>/_tools/` 또는 `code/` 디렉터리에 *retroactive* 페이즈 frontmatter 생성 스크립트 (`build_artifacts.py` 등) 작성. **하네스의 frontmatter 는 페이즈가 *진행되며 박는 것* 이지 사후 일괄 생성 대상이 아님.**
> c- "out-of-sandbox" / "cannot invoke harness scripts" 등의 사유로 자체 emulator 작성 — sandbox 친화 fallback 은 [`../theseus-harness/scoring/`](../theseus-harness/scoring/) 의 도구를 *직접 import* 하거나 사용자에게 명시적 ack 요청.
> d- 페이즈 04 인터뷰의 "사전 박힌 답" 지시를 *페이즈 04 자체 생략* 으로 해석. 사전 답은 *질의 답안 자동 매핑* 일 뿐 페이즈 자체는 진행되어야 함 (`intent/04-questions.md` + `04-answers.md` 산출물 의무).
>
> **위반 시 처리** — 실행 에이전트 가 위 a-d 중 어느 하나라도 시작하면 본 스킬은 즉시 정지 + `intent/00-violation.md` 에 위반 사유 기록 + 페이즈 01 부터 정상 진행 재시작.
>
> **HARD-RULE 8 — 그레이드별 의무 산출물 (모든 페이즈 완주 강제):**
>
> 본 스킬 호출 후 종료 시 다음 산출물이 *모두* `.ShipofTheseus/<프로젝트>/` 에 박혀 있어야 함. 누락 = 본 스킬 미완. budget cap 도달 시에도 *최소한 frontmatter 만이라도* 박고 `(budget-truncated)` 표시.
>
> | Grade | 의무 산출물 |
> | ----- | ---------- |
> | **G1** Trivial | `timing/start.json` + `intent/01-intent.md` + `handoff/14-handoff.md` (3개) |
> | **G2** Simple | G1 + `intent/04-{questions,answers,autonomy,stack,verification,runtime-prereq}.md` + `plan/06-plan.md` + `impl/08-impl-log.md` + `quality/09-quality-gate.md` (총 11개) |
> | **G3** Standard | G2 + `naming/00-naming.md` + `intent/{02,03,05}*.md` + **refresh 1**: `intent/01-{1,2,3,4}-intent.md` + `intent/01-additional.md` + **refresh 2**: `intent/01-{1,2,3,4}-intent.v2.md` + `intent/04-refreshed.md` + `intent/05-refreshed.md` + `plan/{tournament-NN.md (≥ 2), candidates/universe-{1,2}/{meta,06-plan,07-cold-read}.md, 07-plan-review.md, dacapo-rerun-NN.md (≥ 1), dacapo-flow.md, shadow-grade-NN.json}` (plan body 8 항목 의무 — implementation guidance 포함, sprint-21 정공) + `impl/{candidates/universe-N/실 코드 + tests, tournament-impl-NN.md (≥ 1), shadow-grade-impl-NN.json, dacapo-rerun-impl-NN.md (≥ 1), dacapo-flow.md, 08-impl-log.md (canonical, ≥ winner 80% inline 또는 shared schema)}` + `sprints/01..03/{inputs,report}.json` + `webview/` (8 탭) (총 45+) |
> | **G4** Complex | G3 + `intent/05-decisions.md` + `plan/candidates/universe-3*` + `sprints/NN/bisect.md` (회귀 발생 시) + 임계 0.999 도달까지 무한 sprint |
> | **G5** Critical | G4 + `plan/candidates/universe-{1..5}/children/...` (깊이 2) + 멀티버스 강제 + 빡빡 모드 가드 |
>
> **자발적 조기 종료 금지** — 실행 에이전트 가 페이즈 06 까지만 만들고 "끝" 으로 보고하면 본 스킬 위반. 위 표의 의무 산출물을 *모두* 박아야 정상 종료.
>
> **부분 채움 OK** — 본문이 한 줄이라도 frontmatter (skill_name / skill_version / phase / fingerprint / prev_fingerprint / created_at) 는 박혀야 함. 본문 truncated 시 마지막 줄에 `<!-- budget-truncated -->` 명시.
>
> **HARD-RULE 9 — 산출물 *내용* 컨벤션 (페이즈별 lookup 인덱스, 본문은 [`../theseus-harness/conventions/`](../theseus-harness/conventions/) 단일 source):**
>
> 본 entry skill 의 책임은 *순서 + 인터럽트 + 그레이드 라우팅* (HARD-RULE 1, 8). 산출물 *내용* 컨벤션은 본 prompt 안에서 *전부 읽지 않음* — 페이즈 진입 시 매핑된 컨벤션 본문만 lookup. 본 prompt context 에서 27 항목 prose 가 빠져 HARD-RULE 1 (페이즈 순서) 의 cognitive bandwidth 가 회복됨. self_lint.py 가 페이즈 exit 시 모두 검증.
>
> | 페이즈 | 컨벤션 (lookup) |
> | --- | --- |
> | 01 의도 | mindmap-richness-default · deep-semantic-intent · domain-model-completeness · intent-completeness · mindmap-centrality |
> | 04 인터뷰 | commentary-policy · runtime-prereq · interview |
> | 04 → 05 (refresh 1) | **intent-refresh-post-interview** (sprint-17 by, 01-{1..4}-intent + 01-additional 의무) |
> | 05 → 06 (refresh 2) | **intent-refresh-post-critique** (sprint-19 ci, **HARD-RULE 9.kk**, 01-{1..4}-intent.v2 + 04-refreshed + 05-refreshed 의무, 사용자 ack 없음 자율) |
> | 05 비평 | directional-simplification · premortem-friction · domain-failure-patterns · parallel-cold-review |
> | 06 계획 | per-module-diagram-fan-out · multiverse-width-default-bump · contested-decision-multiverse · measurement-contract · rubric-driven-doc-skeleton · intra-phase-dacapo-loop · dacapo-enforcement (**HARD-RULE 9.p**) · dacapo-frontmatter-schema · shadow-grader-zero-context · dacapo-skip-sentinel · dacapo-flow-trace · data-structure-invariants · plan-tree · tournament-blind-rerun · interface-first-parallel-impl · **dacapo-mandatory-rerun (HARD-RULE 9.gg)** · **plan-tournament-scoring-strict (9.hh)** · **canonical-not-stub (9.ii)** · **cross-phase-shared-context (9.ll)** |
> | 08 구현 | intra-phase-dacapo-loop · simulation-physical-invariants · idiomatic-code-quality · experimental-control-protocol · deliverable-hurdle-supremacy · multiverse-impl-fan-out · **impl-multiverse-strict (HARD-RULE 9.jj, 7 조건 게이트)** · **dacapo-mandatory-rerun (9.gg)** · **canonical-not-stub (9.ii)** · dead-code-zero · magic-number-traceability · submission-portability · reproducibility-doublecheck |
> | 09 게이트 | rubric-targeted-quality-gates · score-rubric-objectivity · test-invariants · nfr-derivation · readme-numbers-from-summary (**HARD-RULE 9.bb**) · reproducibility-doublecheck (**9.cc**) · magic-number-traceability (**9.dd**) · dead-code-zero (**9.ee**) · submission-portability (**9.ff**) |
> | 10 스프린트 | intent-plan-impl-sprint-trinity · grader-in-sprint · sprint-regression-loop · budget-saturation-loop · sprint-score-delta-tracking · evidence-driven-sprint-planning · cross-universe-lesson-distillation |
> | 14 핸드오프 | results-decision-mapping · phase-lineage-viewer · decision-support-framing |
>
> **9.a~c 본문 의무 (페이즈 06/08 산출물 구조)** — 본 entry skill 에 직접 박힘 (실 코드 외부 repo 따라 구현 가능 의무):
> - 9.a `plan/06-plan.md` 본문 8 항목 의무 (별도 impl-design.md 안 만듦, plan 단일 source — plan + impl-log 응집 보존):
>   1. 파일 경로 ≥ 5
>   2. **Mermaid sequenceDiagram ≥ 1 AND Mermaid usecase/graph ≥ 1 AND 인터페이스 정의 ≥ 3** (셋 다 의무)
>   3. TODO DAG (T-NNN ID + 의존 + 완료 조건)
>   4. 모듈 의존 다이어그램 (per-module sequenceDiagram ≥ 모듈 수)
>   5. Data structure invariants 표 (Invariants/Topology/Access/Bounds 4 항)
>   6. Test surface mapping (invariant ↔ test signature 1:1)
>   7. Error handling / fallback policy (모듈별)
>   8. Implementation guidance per TODO (알고리즘 / DS / 라이브러리 / pseudo-code — implementer 가 따라가는 디자인)
> - 9.b `impl/08-impl-log.md`: TODO ID 매핑 ≥ 3 / 모듈명 명시 / 인터페이스 노출
> - 9.c G3+ universe N `06-plan.md`: 시드별 의미 분기 ≥ 20 diff 라인 (universe-1 vs universe-2 동일 ≠ 형식적 분기)
>
> **위반 처리** — 컨벤션 미달 = self_lint 페이즈 exit fail → 페이즈 재진입 (자율, ≥ 3 회 위반 시만 ack). cold session evidence (sprint-17 슬림화 도입 동기 — v0.9.18~v0.9.22 동안 본 영역이 118 → 287 lines 비대화 + 신규 컨벤션 fabrication 표적화 사고) → `intent/00-violation.md` 추적.

## 15 페이즈 진행

상세는 [`../theseus-harness/SKILL.md`](../theseus-harness/SKILL.md) 의 15 페이즈 표 + [`../theseus-harness/phases/`](../theseus-harness/phases/) 의 페이즈 문서. 본 entry skill 은 그 표를 따라 sub-agent 호출 + frontmatter chain + 산출물 의무 + autonomy 정책을 강제할 뿐, 룰 본문은 한 곳 (theseus-harness) 에 있다.

| # | 페이즈 | 그레이드 활성 (그레이드 매트릭스: [`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md)) |
| --- | --- | --- |
| 00 | 명명 | G3+ |
| 01 | 의도 + 마인드맵 | G2+ (모든 그레이드) |
| 02 | 의도 리뷰 | G3+ |
| 03 | 콜드 재이해 | G3+ |
| 04 | 사용자 질의 | G2+ (모든 그레이드, *유일한 인터럽트*) |
| 05 | 비평 | G3+ |
| 06 | 계획 (G3+ AIDE 트리) | G2+ |
| 07 | 계획 재이해 | G4+ |
| 08 | 구현 (5 서브페이즈 TDD) | G2+ |
| 09 | 게이트 (7 게이트) | G2+ |
| 10 | 스프린트 루프 | G3+ |
| 11 | 회귀 바이섹트 | G4+ |
| 12 | theseus-view (스킬 진행 추적) | G3+ (G2 단순) |
| 13 | interactive-viewer (프로젝트 output observability) | G3+ (G2 옵션, G5 강제) |
| 14 | 핸드오프 | G2+ |

## 그레이드 처리 (호출 직후 첫 동작 후)

```
1. grade_assess.py 자동 추정 (사용자 원문)
2. 페이즈 04 의 Q-G1 객관식 → 사용자 그레이드 확정
3. 그레이드별 매트릭스 활성 페이즈만 진행 (모든 그레이드 진행 — 그레이드는 *내부 모듈레이션만*):
   - Grade 1 (Trivial): mini_harness_tbd 모드 — 최소 페이즈 (모듈레이션 정의 진행 중)
   - Grade 2 (Simple):  intent + plan + implement + quality + handoff (5 페이즈)
   - Grade 3 (Standard): naming + intent + plan-tree + implement(5 sub-phase TDD) + quality + sprint(3 cap) + theseus-view + interactive-viewer + handoff (13 페이즈)
   - Grade 4 (Complex): 15 페이즈 풀 (default)
   - Grade 5 (Critical): 15 페이즈 풀 + 빡빡 모드 (DIP 0.4 / 회귀 0.02 / 멀티버스 강제 5 / 깊이 2 + interactive-viewer 강제)
```

자세한 그레이드 매트릭스는 [`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md).

## 단일 source of truth — theseus-harness 동반 필수

> **본 스킬 단독 설치 시 동작 안 함.** 본 저장소의 [`../theseus-harness/`](../theseus-harness/) 가 모든 룰 본문 source. 본 스킬은:
> - HARD-RULE entry 룰 (위)
> - harness 의존 명시
> - 사용자 마켓플레이스 namespace (`/shipoftheseus:theseus-orchestrator`)
> - 그레이드 처리 흐름 인덱스 (위)

## 자율 결정 (인터럽트 0)

페이즈 04 외 인터럽트 절대 없음. 모든 자율 결정은 산출물 frontmatter + `intent/04-autonomy.md` 의 Q-D1 ~ Q-D9 답에 기록되어 사후 회수 가능. 보안 가드 (실 secret 의 git 커밋 감지) 만 *유일한* 인터럽트 추가 예외 — [`../theseus-harness/conventions/runtime-prereq.md`](../theseus-harness/conventions/runtime-prereq.md).

## 안전 보장

a- **HARD-RULE 양쪽** — 본 SKILL.md + [`../theseus-harness/SKILL.md`](../theseus-harness/SKILL.md) 모두 HARD-RULE 명시. self_lint C-OD 가 양쪽 keyword 일치 검증.
b- **single source of truth** — 콘텐츠는 [`../theseus-harness/`](../theseus-harness/) 한 곳. self_lint C28 검증.
c- **fingerprint 체인** — 각 페이즈 산출물이 직전 산출물의 fingerprint 를 prev_fingerprint 로. 체인 끊기면 다음 페이즈 진입 거부. [`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md).
