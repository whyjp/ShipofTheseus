---
name: theseus-orchestrator
version: 0.9.21
description: theseus-harness 의 15 페이즈 자율 driver — entry point. 페이즈 04 인터뷰 후 인터럽트 0. AIDE 멀티버스 (G3=5/G4=7/G5=9 폭 default) + grade_assess v2 + sprint-14 v0.9.20 (grader-in-sprint dual-objective / contested decisions axis / directional simplification / commentary policy / measurement contract / rubric skeleton + targeted gates) + sprint-15 v0.9.21 (phase 06/08 Da Capo Loop 의사코드 hook — multiverse + sprint retry 통합).
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
>
> **HARD-RULE 9.d~g — sprint-13 / v0.9.19 신규** (산출물 *발현 빈도* 강제):
>
> d- **마인드맵 풍성도** ([`../theseus-harness/conventions/mindmap-richness-default.md`](../theseus-harness/conventions/mindmap-richness-default.md), ba):
>    - frontmatter `mindmap_quality_grade ∈ [A, B]` 만 PASS (C/D fail).
>    - A 등급 default (≥25 노드 / 4 axis × ≥4 sub-node / 3 axis sub-sub + 1 axis sub-sub-sub).
>    - B 등급 fallback (≥15 노드 + Mermaid 형식) — *PASS with lesson* (sprint NN+1 의 mindmap 보강 trigger).
>    - C/D 등급 — self_lint C-MRD-A-DEFAULT fail / 페이즈 02 진입 거부.
>
> e- **per-module 다이어그램** ([`../theseus-harness/conventions/per-module-diagram-fan-out.md`](../theseus-harness/conventions/per-module-diagram-fan-out.md), bb):
>    - 페이즈 06 plan/06-plan.md 의 모듈 수 ≥ 4 OR consumer-producer 페어 ≥ 6 → per-module use-case / sequence 다이어그램 ≥ 모듈 수 의무.
>    - 모듈 ≤ 3 → 단일 통합 OK.
>    - self_lint C-PMDF 가 검증.
>
> f- **multiverse 폭 default** ([`../theseus-harness/conventions/multiverse-width-default-bump.md`](../theseus-harness/conventions/multiverse-width-default-bump.md), bc):
>    - 페이즈 06 plan-tree 폭 default G2=2 / G3=5 / G4=7 / G5=9.
>    - 사용자 명시 ack 시 옵션 default G3=10 / G4=12 / G5=16.
>    - budget tight 시 fallback 폭 + `fallback_reason` frontmatter 의무 ([`../theseus-harness/conventions/budget-aware-fallback.md`](../theseus-harness/conventions/budget-aware-fallback.md)).
>    - self_lint C-MWDB 가 검증.
>
> g- **sprint trinity** ([`../theseus-harness/conventions/intent-plan-impl-sprint-trinity.md`](../theseus-harness/conventions/intent-plan-impl-sprint-trinity.md), bd):
>    - 페이즈 10 sprint axis count: intent ≥ 2 / plan ≥ 2 / impl ≥ 2 (총 ≥ 6 sprint).
>    - 임계 0.999 default (모든 그레이드 G2~G4 / G5 = 0.99999 보존).
>    - early stop violation = (axis 별 < 2) OR (budget < 80%).
>    - budget 분배 default: intent 20% / plan 30% / impl 50%.
>    - self_lint C-IPI 가 검증.
>
> **HARD-RULE 9.h~n — sprint-14 / v0.9.20 신규** (cold evaluator feedback 7 패치, 94 plateau 돌파):
>
> h- **grader-in-sprint dual-objective** ([`../theseus-harness/conventions/grader-in-sprint.md`](../theseus-harness/conventions/grader-in-sprint.md), be):
>    - 페이즈 10 sprint stop = `auto_pass(≥0.999) AND shadow_pass(≥target) AND axis_pass(≥2) AND budget_pass(≥0.80)` (4 conjunction).
>    - target_score: G2=80 / G3=90 / **G4=95 default** / G5=98.
>    - 매 sprint 종료 *직전* zero-context shadow grader (Sonnet) 1 회 호출 — 누적 conversation 0, fresh load.
>    - sprint report.json 에 `shadow_grader_predicted_score / shadow_grader_call_id / weakest_category / lesson_candidates` 의무.
>    - self_lint C-GIS 가 검증.
>
> i- **contested decision multiverse axis** ([`../theseus-harness/conventions/contested-decision-multiverse.md`](../theseus-harness/conventions/contested-decision-multiverse.md), bf):
>    - 페이즈 06 universe axis = `prompt + cold-read + critique` 에서 추출한 contested decisions (paradigm fallback only when decisions=0).
>    - `plan/contested-decisions.md` 신규 산출물 의무 + 각 universe meta.md 의 code spike (≤50 LOC).
>    - tournament 채점 5 차원 → 6 차원 (decision_coverage 0.20 가중 신규, 가중 재분배).
>    - self_lint C-CDM 가 검증.
>
> j- **directional simplification** ([`../theseus-harness/conventions/directional-simplification.md`](../theseus-harness/conventions/directional-simplification.md), bg):
>    - 페이즈 05 critique 의 simplification 표 의무 (direction ↑/↓/? + magnitude ±% + reason 1 줄).
>    - frontmatter sync (`simplification_count / direction_known_ratio / magnitude_known_ratio`).
>    - 게이트 1 강화 (direction 명시 row ≥ 50%).
>    - self_lint C-DS 가 검증.
>
> k- **commentary policy** ([`../theseus-harness/conventions/commentary-policy.md`](../theseus-harness/conventions/commentary-policy.md), bh):
>    - 페이즈 04 Q-D-AUDIENCE 신규 (internal-self / external-reviewer (default) / mixed).
>    - audience 별 페이즈 08 implementer 주석 density 매트릭스 swap (CLAUDE.md global default 컨텍스트 충돌 명시 정정).
>    - external-reviewer 시 docstring + why-comment density ≥ 0.015 / LOC.
>    - self_lint C-CP 가 검증.
>
> l- **measurement contract** ([`../theseus-harness/conventions/measurement-contract.md`](../theseus-harness/conventions/measurement-contract.md), bi):
>    - 페이즈 06 plan 의 metric method 표 의무 (sample / accumulate / reconstruct + reconstruct 정당화).
>    - frontmatter sync (`direct_measurement_ratio / reconstruct_justified_ratio`).
>    - 게이트 6 강화 (direct_ratio < 0.7 시 cap 0.85).
>    - 페이즈 11 plan_method vs impl 분류 입력.
>    - self_lint C-MC 가 검증.
>
> m- **rubric-driven doc skeleton** ([`../theseus-harness/conventions/rubric-driven-doc-skeleton.md`](../theseus-harness/conventions/rubric-driven-doc-skeleton.md), bj):
>    - 페이즈 04 stack-lock 직후 RubricAdapter (yaml / markdown / openapi 3 built-in) → `_skeleton/` 빈 헤더 (rubric line 인용).
>    - rubric 미노출 시 fallback generic ToC (intent / plan / handoff 기본 헤더).
>    - 페이즈 08 산출물 헤더가 skeleton 와 1:1 매핑 의무.
>    - self_lint C-RDS 가 검증.
>
> n- **rubric-targeted quality gates** ([`../theseus-harness/conventions/rubric-targeted-quality-gates.md`](../theseus-harness/conventions/rubric-targeted-quality-gates.md), bk):
>    - 페이즈 09 정적 9 + derived N + RTG-* (rubric bullet → yes/no 체크) 통합.
>    - bj 와 같은 RubricAdapter 1 회 파싱, skeleton + gates 둘 다 입력.
>    - 종합 판정: proceed / remediate (RTG fail ≤30%) / halt.
>    - fail RTG → sprint NN+1 lesson 자동 매핑 (be shadow grader lesson 과 합산).
>    - self_lint C-RTG 가 검증.
>
> **HARD-RULE 9.o — sprint-15 / v0.9.21 신규** (phase 06/08 Da Capo Loop 의사코드 hook):
>
> o- **intra-phase Da Capo Loop** ([`../theseus-harness/conventions/intra-phase-dacapo-loop.md`](../theseus-harness/conventions/intra-phase-dacapo-loop.md), bl):
>    - 페이즈 06 (plan) + 페이즈 08 (impl) 안에 *통합 의사코드 loop* 박힘 — multiverse fan-out (Step A) → tournament (Step B) → shadow grade (Step C, be 재사용) → 4 conjunction AND threshold (Step D) → cap 체크 (Step E) → lesson 도출 + winner 갱신 (Step F) → **다카포: 처음 (Step A) 으로** (Step G).
>    - winner.tournament_score 와 shadow.predicted_score 둘 다 grade 임계 (G3=0.97/90, G4=0.999/95, G5=0.99999/98) 이상 의무 (4 conjunction AND).
>    - max_rerun (G3=2/G4=3/G5=5) OR budget 95% 도달 시 BUDGET_BOUND + fallback_reason 의무 (ah 정합).
>    - rerun 시 anonymized previous winner + width-1 fresh universes 재 fan-out (ad v0.9.10 룰 정합).
>    - phase 08 의 lesson 적용 시 5 서브페이즈 (08-α/β/γ/δ/ε) *전체* 재실행 의무 (universe 변경 룰 정합, 부분 재진입 금지).
>    - 산출물 의무: `tournament-NN.md` / `shadow-grade-NN.json` / `dacapo-rerun-NN.md` / (BUDGET_BOUND 시) `fallback-reason.md`.
>    - self_lint C-DCL-WIN-THRESHOLD / C-DCL-RERUN-LOG / C-DCL-ANON 가 검증.
>    - cold session `2026-05-05__001_synthetic_mine_throughput__theseus-shipoftheseus__claude-opus-4-7__g4` 의 winner=0.853 (G4 임계 0.999 미달) 재경합 0 회 회귀 직접 정정.

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
