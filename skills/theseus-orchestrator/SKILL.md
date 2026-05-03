---
name: theseus-orchestrator
version: 0.9.2
description: theseus-harness 의 15 페이즈 자율 driver — entry point. 페이즈 04 인터뷰 후 인터럽트 0. 멀티버스 폭 G3-3/G4-4/G5-6 + TDD 5 서브 + 자동 머지 + universe 별 head-to-head. 모든 그레이드 진행 — 내부 모듈레이션만.
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
> | **G3** Standard | G2 + `naming/00-naming.md` + `intent/{02,03,05}*.md` + `plan/{tournament.md, candidates/universe-{1,2}/{meta,06-plan,07-cold-read}.md, 07-plan-review.md}` + `sprints/01..03/{inputs,report}.json` + `webview/` (8 탭) (총 30+) |
> | **G4** Complex | G3 + `intent/05-decisions.md` + `plan/candidates/universe-3*` + `sprints/NN/bisect.md` (회귀 발생 시) + 임계 0.999 도달까지 무한 sprint |
> | **G5** Critical | G4 + `plan/candidates/universe-{1..5}/children/...` (깊이 2) + 멀티버스 강제 + 빡빡 모드 가드 |
>
> **자발적 조기 종료 금지** — 실행 에이전트 가 페이즈 06 까지만 만들고 "끝" 으로 보고하면 본 스킬 위반. 위 표의 의무 산출물을 *모두* 박아야 정상 종료.
>
> **부분 채움 OK** — 본문이 한 줄이라도 frontmatter (skill_name / skill_version / phase / fingerprint / prev_fingerprint / created_at) 는 박혀야 함. 본문 truncated 시 마지막 줄에 `<!-- budget-truncated -->` 명시.
>
> **HARD-RULE 9 — 산출물 *내용* 의무 (설계 품질, 실 코드 외부 repo 책임):**
>
> 본 하네스의 책임은 *설계 + 구현 가이드 문서* 까지 — 실 코드 빌드/테스트/부팅은 외부 프로젝트 repo 책임. 다만 산출물 *내용* 이 다음을 만족해야 외부 repo 가 따라 구현 가능:
>
> a- **`plan/06-plan.md` 의무 본문**:
>    - 모듈 분할 + 파일 배치 + 폴더 배치 (디렉터리 트리 또는 파일 경로 ≥ 5 개 명시)
>    - 모듈간 인터페이스 — Mermaid 시퀀스 다이어그램 ≥ 1 개 *또는* `interface` / `port` / `type ... interface` 정의 ≥ 3 개
>    - TODO DAG (T-001, T-002, ... ID + 의존 + 완료 조건)
>
> b- **`impl/08-impl-log.md` 의무 본문**:
>    - 페이즈 06 의 TODO ID 매핑 — 각 TODO 별 항목 (T-001 / T-002 / ...) ≥ 3 개
>    - 항목별 (a) 생성/수정 파일 경로, (b) 추가 테스트 명세, (c) 노출한 인터페이스 / 포트
>    - 모듈명 명시 (internal/X, src/Y 등)
>
> c- **G3+ `plan/candidates/universe-N/06-plan.md` 의무 본문**:
>    - 우주마다 *시드별* 의미 차이 — universe-1 (domain-first) vs universe-2 (adapter-first) 의 06-plan.md 가 동일 ≠ 형식적 분기. 의미 분기 ≥ 20 diff 라인.
>
> 위 산출물 본문이 의무를 미달해도 frontmatter 만 박혀있으면 본 스킬은 "정상 완주" 로 종료하나, *설계 품질 부족* 시 외부 repo 의 구현이 모호해짐. verify 의 i/j/k 체크가 본 의무 검증.

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
