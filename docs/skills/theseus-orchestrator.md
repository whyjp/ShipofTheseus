# theseus-orchestrator 가이드

## 한 줄 요약

**15 페이즈 자율 driver — 사용자 entry point.** 페이즈 04 인터뷰 1회 후 인터럽트 0. 본 스킬은 HARD-RULE (호출 직후 첫 동작 강제 + 그레이드별 의무 산출물) + 그레이드 처리 인덱스만 자체 보유 — 콘텐츠 source 는 [`theseus-harness`](theseus-harness.md) 동반 필수.

## 언제 호출하는가

ⓐ 다중 모듈 / FE+BE 동시 / 도메인 미정착 신규 기능 / 외부 evaluator 가 채점하는 bench 작업 (G4 자동 escalation).
ⓑ 사용자 인터뷰 인터럽트는 페이즈 04 한 번만 받고 이후는 자율 진행을 원할 때.
ⓒ AIDE multiverse 의 *유일한 차별 강점* (N 우주 토너먼트 + 5+ 페이즈 multi-phase 확장 + ensemble synthesis + blind rerun) 을 그대로 활용하고 싶을 때.

## 호출 형식

```
/shipoftheseus:theseus-orchestrator <요구사항>
```

요구사항이 단순하면(G1) 본 스킬 내부의 grade-assess 가 mini_harness_tbd 모드로 처리. **G2~G5 모두 진행 — 그레이드는 *내부 모듈레이션만* 결정 (복잡도 / 페이즈 수 / 컨벤션 / 임계 / 멀티버스 폭).**

## 진행 흐름 (15 페이즈)

| # | 페이즈 | 그레이드 활성 |
| --- | --- | --- |
| 00 | 명명 | G3+ |
| 01 | 의도 + 마인드맵 | G2+ |
| 02 | 의도 리뷰 (multi-reviewer multi-phase 옵션, v0.9.10) | G3+ |
| 03 | 콜드 재이해 (parallel cold review, v0.9.8) | G3+ |
| 04 | 사용자 질의 + 스택 + Q-D9 + Q-D-DELIVERABLE-MODE + Q-D-BUDGET-MODE | G2+ (*유일한 인터럽트*) |
| 05 | 비평 (multi-critic multi-phase 옵션) | G3+ |
| 06 | **AIDE Plan-Tree** — N 우주 토너먼트 (G3-3 / G4-4 / G5-6 + 깊이 1-2 + sequenceDiagram per-universe + ensemble synthesis default) | G2+ |
| 07 | 계획 재이해 | G4+ |
| 08 | 구현 (5 서브페이즈 TDD + multiverse impl fan-out) | G2+ |
| 09 | 7 게이트 + Gate 0 결과물 허들 (H1-H5) supremacy | G2+ |
| 10 | 무한 스프린트 (budget-saturation-loop ≥80% 사용 강제) | G3+ |
| 11 | 회귀 바이섹트 (4 분류 + multi-hypothesis multi-phase 옵션) | G4+ |
| 12 | theseus-view (스킬 진행 추적) | G3+ (G2 단순) |
| 13 | interactive-viewer (프로젝트 output observability + multi-framing 옵션) | G3+ (G2 옵션, G5 강제) |
| 14 | 핸드오프 (score-rubric-objectivity self-estimate) | G2+ |

자세한 그레이드 매트릭스는 [`../../skills/theseus-harness/conventions/grades.md`](../../skills/theseus-harness/conventions/grades.md).

## 입출력

- **입력**: 사용자 자연어 요청 + 레포 컨텍스트.
- **출력**: 15 페이즈 산출물 모두 + (standalone 시) 코드 + theseus-view 웹뷰 + interactive-viewer + 핸드오프 메시지.

산출물 위치: `.ShipofTheseus/<프로젝트명>/`.

## HARD-RULE 요약

| # | 룰 |
|---|---|
| HARD-RULE 1~7 | 호출 직후 첫 동작 = `timing/start.json` + 페이즈 00/01 산출물 작성. 코드 직접 작성 / retroactive frontmatter generator / harness emulator / 페이즈 04 생략 모두 위반 |
| HARD-RULE 8 | 그레이드별 의무 산출물 (G1 3개 / G2 11개 / G3 30+ / G4-5 풀) 모두 박혀야 정상 완주 |
| HARD-RULE 9 | 산출물 *내용* 의무 — `plan/06-plan.md` (파일 경로 ≥ 5 / Mermaid 시퀀스 ≥ 1 또는 인터페이스 ≥ 3 / TODO DAG) + `impl/08-impl-log.md` (TODO ID 매핑 ≥ 3 / 모듈명 / 인터페이스 노출) |

전체 룰: [`../../skills/theseus-orchestrator/SKILL.md`](../../skills/theseus-orchestrator/SKILL.md) §HARD-RULE.

## Layer 3 결과물 허들 supremacy (v0.9.14)

본 스킬 종료 시 *standalone 컨텍스트* (= bench / 단독 진행) 면 5 hurdle 의무:

- H1 Code Existence (≥ 5 모듈)
- H2 Code Execution (verification command exit 0)
- H3 Test Suite (실 측정 통과 수 0 금지)
- H4 Bench-Required Outputs (file existence + size > 0 + schema 정합)
- H5 Executed Values Recording (placeholder 금지)

실패 시 자동 retry sprint. 사용자 명시 ack (Q-D-DELIVERABLE-MODE = 3 design-only) 만 면제.

## 자주 묻는 질문

**Q. orchestrator 와 theseus-harness 단독 호출의 차이는?**
A. orchestrator 는 *사용자 entry point* — HARD-RULE entry 룰 + 그레이드 처리 흐름 인덱스만 자체 보유. 콘텐츠는 모두 [`theseus-harness/`](theseus-harness.md) 의 47 컨벤션 + 18 에이전트 + 채점기. 두 스킬 모두 설치 필수 (orchestrator 단독 설치 시 본문 링크 깨짐).

**Q. 페이즈 04 외에 사용자 인터럽트가 발생하는가?**
A. 페이즈 04 답안 매핑이 모든 후속 결정을 자율 처리. 보안 가드 (실 secret 의 git 커밋 감지) 만 *유일한* 인터럽트 추가 예외 — [`../../skills/theseus-harness/conventions/runtime-prereq.md`](../../skills/theseus-harness/conventions/runtime-prereq.md). 페이즈 11 회귀 바이섹트 / 페이즈 13 PR 권한 / 멀티버스 머지 결정 모두 Q-D 사전 위임 자동 매핑.

**Q. 중간에 끊어지면?**
A. `state.json` 이 자동 기록되어 다음 호출 시 마지막 valid 페이즈 다음부터 재개. 자세한 절차는 [`../../skills/theseus-harness/conventions/resume.md`](../../skills/theseus-harness/conventions/resume.md).

**Q. budget 80% 강제는 무엇인가?**
A. v0.9.15 budget-saturation-loop — 페이즈 10 sprint loop 가 임계 first-try PASS 해도 budget ≥ 80% 사용까지 sprint 추가. 추가 sprint 의 lesson type = *content depth* (enforcement 아님). 94 plateau 돌파 룰. 페이즈 04 Q-D-BUDGET-MODE 답 2 (Quick-stop) 로 사용자 명시 ack 시 fast-stop.

## 더 읽을거리

- [`../../skills/theseus-orchestrator/SKILL.md`](../../skills/theseus-orchestrator/SKILL.md) — 기계 진입점 (LLM 이 읽음).
- [`../../skills/theseus-harness/SKILL.md`](../../skills/theseus-harness/SKILL.md) — 콘텐츠 source of truth.
- [`../../skills/theseus-harness/conventions/contracts.md`](../../skills/theseus-harness/conventions/contracts.md) — 스킬 간 frontmatter 계약.
- [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — AIDE 멀티버스 (진짜 차별 동력) + 도자기 장인 비유.
