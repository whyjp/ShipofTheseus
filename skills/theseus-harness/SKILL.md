---
name: theseus-harness
version: 0.9.52
description: 재귀 멀티 에이전트 코딩 하네스. sprint-52 = Viewer Finalization Closure — phase 14 lineage_finalize.py 가 viewer JSON placeholder 일괄 refresh + universe candidate created_at 의무. HARD-RULE 9.nnn/9.ooo/9.ppp.
---

# theseus-harness — 콘텐츠 source of truth (인덱스)

본 SKILL.md = *인덱스만*. 모든 콘텐츠는 모듈 파일 lazy-load. 페이즈 진입 시 router 가 매칭된 본문만 load. 본 파일은 *현재* 활성 룰 + 라우팅 (sprint/version history → [`../../CHANGELOG.md`](../../CHANGELOG.md) 단일 위치).

설계 철학 + AIDE 멀티버스 + 도자기 장인: [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md).

## 0. ALWAYS-LOADED → [`HARD-CORE.md`](HARD-CORE.md)

매 페이즈 본문 *상단 import* 의무. lazy 절대 금지. ≤ 4000 chars (C-HC1 lint 강제).

- **HR1** — 호출 직후 첫 동작 (timing/start.json + naming/intent + 4 금지조항 a-d)
- **HR8** — 그레이드별 의무 산출물 (G1~G5)
- **HR9.a~c** — 산출물 *내용* 본문 의무 (06-plan / 08-impl-log / universe-N)
- **HR9.d~ll** — 페이즈별 conventions/INDEX router lazy load
- **Layer 3 H1~H5** — 결과물 허들 supremacy
- **frontmatter 핑거프린트 체인** + **페이즈 04 외 인터럽트 0**

## 1. 페이즈 진입 lazy-load → 한 파일

| # | 페이즈 | 활성 | 모델 | 모듈 | 핵심 산출 |
|:-:|---|:-:|:-:|---|---|
| 00 | 명명 | G3+ | Haiku | [`phases/00-naming.md`](phases/00-naming.md) | `naming/` |
| 01 | 의도 + 마인드맵 | G2+ | Opus | [`phases/01-intent.md`](phases/01-intent.md) | `intent/01-intent.md` |
| 02 | 의도 리뷰 | G3+ | Sonnet | [`phases/02-document.md`](phases/02-document.md) | `intent/02-review.md` |
| 03 | 콜드 재이해 | G3+ | Sonnet | [`phases/03-independent-comprehension.md`](phases/03-independent-comprehension.md) | `intent/03-comprehension.md` |
| 04 | 사용자 질의 (*유일한 인터럽트*) | G2+ | Sonnet | [`phases/04-clarify.md`](phases/04-clarify.md) | `intent/04-*.md` + refresh-1 (`01-{1..4}-intent`, `01-additional`) |
| 1.5 | 확장 사고 (Hidden Intent) | G3+ | general-purpose | [`phases/01-5-hidden-intent.md`](phases/01-5-hidden-intent.md) | `intent/01-hidden-intent.md` |
| 05 | 비평 + refresh-2 | G3+ | Opus | [`phases/05-critique.md`](phases/05-critique.md) | `intent/05-*` + `01-{1..4}-intent.v2`, `04-refreshed`, `05-refreshed` |
| 06 | AIDE Plan-Tree + 다카포 | G2+ | Opus | [`phases/06-plan.md`](phases/06-plan.md) | `plan/{06-plan, tournament-NN, candidates/, dacapo-rerun-NN, dacapo-flow, shadow-grade-NN}.md` |
| 07 | 계획 재이해 | G4+ | Sonnet | [`phases/07-plan-recursion.md`](phases/07-plan-recursion.md) | `plan/07-plan-review.md` |
| 08 | 구현 (5 sub-phase TDD + multiverse + 다카포) | G2+ | Sonnet/Opus | [`phases/08-implement.md`](phases/08-implement.md) | `impl/` |
| 09 | 게이트 (의도/SOLID/테스트/NFR/runtime/dacapo/lineage 등) | G2+ | Sonnet | [`phases/09-quality-gates.md`](phases/09-quality-gates.md) | `quality/09-quality-gate.md` |
| 10 | sprint trinity (intent/plan/impl ≥ 2) | G3+ | Haiku | [`phases/10-test-loop.md`](phases/10-test-loop.md) | `sprints/NN/` |
| 11 | 회귀 바이섹트 — 코드 오류 / 기획-구현 갭 / NFR 미달 / 의도 표류 / 정체 차원 *깨고 다시 빚기* (re-architect) | G4+ | Opus | [`phases/11-regression-bisect.md`](phases/11-regression-bisect.md) | `sprints/NN/bisect.md` |
| 12 | theseus-view | G3+ | Sonnet | [`phases/12-webview-assembly.md`](phases/12-webview-assembly.md) | `webview/` |
| 13 | interactive-viewer | G3+ G2-옵션 G5-강제 | Sonnet | [`phases/13-interactive-viewer.md`](phases/13-interactive-viewer.md) | `interactive-viewer/` |
| 14 | 핸드오프 | G2+ | — | [`phases/14-handoff.md`](phases/14-handoff.md) | `handoff/14-handoff.md` |

페이즈 N 산출물 (frontmatter + fingerprint chain valid) 들고 오면 페이즈 N+1 부터 진입 (재진입). 호환 안 되면 거부 + 사용자 객관식.

## 2. 컨벤션 router-matched lazy → [`conventions/INDEX.md`](conventions/INDEX.md)

**단일 진실 원천.** 88 컨벤션 모두 INDEX row 와 1:1 매칭. 페이즈 진입 시 router 가 `applies-to-phases × applies-to-grades × trigger-when` 매칭된 본문만 lazy load. 본 SKILL.md 는 *카탈로그 나열 안 함*.

## 3. 에이전트 (18) → [`agents/`](agents/)

페이즈 본문이 호출 시점 + agent 인용. 권장 모델은 각 agent 본문 frontmatter.

[`agents/clarifier.md`](agents/clarifier.md) · [`agents/critic.md`](agents/critic.md) · [`agents/doc-reviewer.md`](agents/doc-reviewer.md) · [`agents/implementer.md`](agents/implementer.md) · [`agents/independent-comprehender.md`](agents/independent-comprehender.md) · [`agents/intent-extractor.md`](agents/intent-extractor.md) · [`agents/interactive-viewer-builder.md`](agents/interactive-viewer-builder.md) · [`agents/plan-reviewer.md`](agents/plan-reviewer.md) · [`agents/planner.md`](agents/planner.md) · [`agents/project-namer.md`](agents/project-namer.md) · [`agents/quality-gate.md`](agents/quality-gate.md) · [`agents/refactorer.md`](agents/refactorer.md) · [`agents/regression-analyst.md`](agents/regression-analyst.md) · [`agents/runtime-detector.md`](agents/runtime-detector.md) · [`agents/test-architect.md`](agents/test-architect.md) · [`agents/test-writer.md`](agents/test-writer.md) · [`agents/tester.md`](agents/tester.md) · [`agents/webview-builder.md`](agents/webview-builder.md)

## 4. 채점기 → [`scoring/`](scoring/)

- `score.py` — 6 차원 weighted, 임계 0.999, DIP hard cap 0.6
- `fingerprint.py` — frontmatter 핑거프린트 + 체인 무결성
- `self_lint.py` — 본 저장소 자기 검증 (임계 0.99999)
- `tournament.py` — universe 채점 + auto_resolve
- `grade_assess.py` — G1~G5 자동 추정 (default G4)
- `rubric.md` — 6 차원 채점 룰

## 5. 템플릿 → [`templates/`](templates/)

intent / plan / sprint-report / naming / universe-meta + bun webview 스캐폴드.

## 6. 산출물 트리

```
.ShipofTheseus/<프로젝트>/
├── timing/start.json
├── naming/                                    G3+
├── intent/{01,01-{1..4},01-additional,02,03,04-*,01-{1..4}-intent.v2,04-refreshed,05-*,05-refreshed}.md
├── plan/{06-plan, candidates/universe-{1..N}/, tournament-NN, dacapo-rerun-NN, dacapo-flow, shadow-grade-NN, contested-decisions, 07-plan-review}.md
├── impl/{08-impl-log, candidates/universe-N/, tournament-impl-NN, dacapo-flow}.md
├── quality/09-quality-gate.md
├── sprints/{01..N}/{inputs,report,bisect?}.{json,md}
├── webview/                                   G3+
├── interactive-viewer/                        G3+ G2-옵션 G5-강제
└── handoff/14-handoff.md
```

페이즈별 산출물 의무 = HARD-CORE HR8 G3 표 + conventions/INDEX router 매칭.

## 7. 호출 그레이드 → [`conventions/grades.md`](conventions/grades.md)

호출 직후 `scoring/grade_assess.py` 자동 추정 → phase 04 Q-G1 객관식 확정. **default G4** (호출 자체가 G4+ 의도 신호). G3 하향 = 12 차원 단순 증명 + 사용자 ack. G5 상향 = 명시 ack.

| Grade | 호출 시점 | 본 하네스 동작 |
|---|---|---|
| **Grade 1** Trivial | 한 줄 수정 / 리네임 | mini_harness_tbd |
| **Grade 2** Simple | 단일 모듈 작은 기능 | 5 페이즈 / 임계 0.85 |
| **Grade 3** Standard | 다중 모듈 단일 사이드 | 13 페이즈 / 임계 0.97 |
| **Grade 4** Complex (default) | FE+BE / 새 도메인 / SOLID 리팩터 | 15 페이즈 풀 / 임계 0.999 |
| **Grade 5** Mission Critical | 결제 / 금융 / 안전 | 15 풀 + 빡빡 / 임계 0.99999 |

## 안티 패턴 통합 카탈로그 (PR-11 정합)

공통 안티 패턴 (A1~A10) → [`conventions/anti-patterns.md`](conventions/anti-patterns.md). 페이즈별 *고유* 안티 패턴은 [`phases/`](phases/) 본문에 잔존. self_lint C40 통합 정합 검증.

## 8. 자가 무결성 검증 → [`scoring/self_lint.py`](scoring/self_lint.py)

본 인덱스 ↔ 모듈 파일 정합 :
- **C-HC1**: HARD-CORE.md ≤ 4000 chars 강제
- **C-IDX-1**: 모든 conventions/*.md 가 INDEX row 와 1:1 매칭 (누락/잉여 0)
- **C-IDX-2/3/4** (후속): frontmatter / 페이즈 cross-ref / grades drift 검증

self_lint 임계 0.99999 — 본 저장소가 자기 강제 룰을 100% 통과 검증.

## 9. 페이즈 04 외 인터럽트 0

모든 자율 결정은 산출물 frontmatter + `intent/04-autonomy.md` 의 Q-D1~Q-D9 답 매핑. 보안 가드 (실 secret 의 git 커밋 감지) 만 *유일한* 인터럽트 추가 예외 → [`conventions/autonomy.md`](conventions/autonomy.md), [`conventions/runtime-prereq.md`](conventions/runtime-prereq.md).

## 10. 핵심 컨벤션 cross-link (slim, full router → INDEX.md)

본 절은 lint 호환 + 자주 cross-ref 되는 컨벤션의 직접 링크만. 88 컨벤션 router = [`conventions/INDEX.md`](conventions/INDEX.md).

[`conventions/contracts.md`](conventions/contracts.md) (frontmatter 핑거프린트 체인) · [`conventions/grades.md`](conventions/grades.md) (G1~G5 매트릭스) · [`conventions/sub-agents.md`](conventions/sub-agents.md) (서브에이전트 재귀) · [`conventions/indexing.md`](conventions/indexing.md) (산출물 = DB) · [`conventions/resume.md`](conventions/resume.md) (state.json + 라이브 추적) · [`conventions/fragmentation.md`](conventions/fragmentation.md) (단일 헤비 스킬 금지) · [`conventions/anti-patterns.md`](conventions/anti-patterns.md) (A1~A10 통합 카탈로그) · [`conventions/plan-tree.md`](conventions/plan-tree.md) (plan/tournament.md AIDE 트리) · [`conventions/phase-lineage-viewer.md`](conventions/phase-lineage-viewer.md) (project-wide lineage).
