# Phase 07 — 계획 재이해 (콜드)

## 한 줄 요약
**계획 자체에 페이즈 03 와 같은 콜드 리딩을 적용한다.** 의도 문서, 비평, 사용자 답을 본 적 없는 fresh 에이전트가 계획만 읽고 무엇을 만들 것인지 거꾸로 추론한다. 의도와 어긋나면 계획이 잘못된 것.

## 입력
- `plan/06-plan.md` 만.

## 서브에이전트
**fresh `Agent(subagent_type="general-purpose")`**, [`../agents/plan-reviewer.md`](../agents/plan-reviewer.md) 의 self-contained 프롬프트.

## 답해야 할 4 질문 + premortem

1- 이 계획만 보면 어떤 기능을 만드는 것인가? (한 문단, 자기 말)
2- 어떤 TODO 부터 시작하겠는가? 이유는?
3- 과소 명세·과대 사이즈·순서 어긋남이 보이는 TODO 는?
4- 누락·잘못된 의존은?
5- **premortem** ([`../conventions/premortem-friction.md`](../conventions/premortem-friction.md), v0.9.7) — "이 플랜이 *수정 0* 으로 페이즈 08 진입 시, sprint 01 의 회귀 발생 위치 ≥ 3 곳?" 격언 prepend (F5 *知之為知之 不知為不知 是知也* / F2 *de omnibus dubitandum est*) + `derived_improvements ≥ 1` 의무. 0 면 self_lint C-PM fail.

## 산출물
`plan/07-plan-review.md` — 4 답 + premortem 절 + 판정 (`accept` | `revise` | `reject`).

## 지휘자 후속

a- 1- 답을 `intent/01-intent.md` 의 "무엇을" 과 diff. 의미상 어긋나면 → 계획이 의도를 인코딩하지 못함 → 페이즈 06 재실행.
b- `revise` → 리뷰 첨부해 페이즈 06 재실행. 시도 3 회 캡.
c- `accept` → 페이즈 08.

## v0.9.22 진입 의무 — Da Capo enforcement gate (HARD-RULE 9.p)

본 페이즈 진입 *전* orchestrator 가 [`../conventions/dacapo-enforcement.md`](../conventions/dacapo-enforcement.md) (bm) 의 `gate_phase06_to_07()` 자동 호출 — 6 조건 검증 :

1- `plan/tournament-NN.md` frontmatter 에 `dacapo_loop_executed: true`
2- `step_d_tournament_pass` + `step_d_shadow_pass` + `step_d_converged` 3종 명시
3- (step_d_converged=true) → CONVERGED OR (rerun_count >= max_rerun OR budget >= 0.95) AND `plan/fallback-reason.md` 본문 ≥ 1 줄 → BUDGET_BOUND
4- rerun_count >= 1 시 `dacapo-rerun-NN.md` 갯수 == rerun_count + `shadow-grade-NN.json` 갯수 == rerun_count+1
5- rerun_count >= 1 시 anonymized previous winner 존재 (ad C-TBR-ANON)
6- `plan/dacapo-flow.md` Mermaid + timeline 의무 (at 가시화)

미달 시 본 페이즈 진입 *자동 거부* + phase 06 Step A 재진입 + `intent/00-violation.md` 기록. 위반 ≥ 3회 시만 페이즈 04 사전 답안 매핑 escalation ([`../conventions/autonomy.md`](../conventions/autonomy.md) 정합 — 자율 회귀 default).

또한 [`../conventions/dacapo-skip-sentinel.md`](../conventions/dacapo-skip-sentinel.md) (bp) 의 3 sentinel (frontmatter 모순 / 디렉터리 카운트 / 로그 패턴) 매치 시도 자동 회귀.

## 왜 필요한가

대부분의 코딩 하네스는 계획 리뷰를 건너뛰고 구현 도중 "당연한" 단계가 사실은 미명세 인프라를 요구한다는 사실을 알게 된다. 여기서 한 번의 에이전트 호출로 잡으면 스프린트 4 회분의 바이섹트 비용을 아낀다.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).
