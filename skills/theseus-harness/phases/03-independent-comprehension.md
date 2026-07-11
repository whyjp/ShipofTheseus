# Phase 03 — 독립 재이해 (콜드)

## 한 줄 요약
**의도 문서가 의미를 전달하는지 왕복으로 검증한다.** 원문도, 리뷰 결과도, 지휘자의 추론도 본 적 없는 fresh 에이전트가 의도 문서만 읽고 자기 말로 다시 써본다. 차이가 크면 의도 문서가 잘못된 것.

## 입력
- `intent/01-intent.md` 만.

## 서브에이전트
**반드시 fresh `Agent(subagent_type="general-purpose")`** — 이전 컨텍스트를 절대 공유하지 않음. [`../agents/independent-comprehender.md`](../agents/independent-comprehender.md) 의 self-contained 프롬프트로.

## 리뷰 디스패치 로그 emit (review.context_minimality 배선, v0.9.54 P1-A)

본 페이즈의 fresh 콜드 재이해 agent(및 [`../conventions/parallel-cold-review.md`](../conventions/parallel-cold-review.md) 의 N framing)은 *pure-review 디스패치* 다 — 각 호출 직후 `state/review_dispatch_log.json` 의 `calls` 배열에 append **의무**:

```json
{"calls": [
  {"agent_call_id": "<유니크 호출 id>", "prior_context_token_count": 0,
   "loaded_artifacts": ["intent/01-intent.md"]}
]}
```

- `prior_context_token_count`: fresh sub-agent 이므로 **0**(누적 conversation 미주입 보증).
- `loaded_artifacts`: 그 호출에 *명시 주입한 파일* 만(콜드 재이해는 `intent/01-intent.md` 만) — 상대경로.
- `agent_call_id`: 호출마다 **유니크**(재호출 중복 = freshness 위반).

phase 09 게이트에서 [`../scoring/producers/measure_context_minimality.py`](../scoring/producers/measure_context_minimality.py) 가 이 로그를 스캔해 `review.context_minimality`(순도 `prior_context_max==0` + 무결성 `loaded_artifacts_missing==0` + freshness + 최소성 `loaded_tokens_max` 디스크 재계산)를 값으로 판정한다. **로그 부재 = NA 아닌 FAIL(비휴면)** — pure-review 를 안 남기면 통과가 아니라 실패(`skipped==FAIL`). 06/08 shadow grader 호출도 같은 로그에 append → [`../conventions/intra-phase-dacapo-loop.md`](../conventions/intra-phase-dacapo-loop.md) Step C.

## Premortem-Friction (v0.9.7, [`../conventions/premortem-friction.md`](../conventions/premortem-friction.md))

agent prompt 헤더에 격언 prepend + 산출물에 `premortem` 절 의무. 핵심 질문 = "이 문서를 *처음 보는 사람* 의 첫 5 질문이 자기가 답할 수 없으면 어떤 결손이 표면화될까?". 콜드 재이해의 *친숙성 자동 동의* 결손이 본 컨벤션의 1차 적용 대상. `derived_improvements ≥ 1` 의무.

## 산출물
`intent/03-comprehension.md`:

a- **내가 이해한 목표** — 한 문단, 자기 말.
b- **성공의 모습** — 외부에서 관찰 가능한 결과.
c- **나라면 어디부터** — 첫 3 단계.
d- **불확실한 점** — 사용자에게 물어야 할 항목 (반드시 1개 이상).
e- **premortem 절** — `proceed_as_is_findings ≥ 3` + `derived_improvements ≥ 1` + `accepted_silence`.

## 성공 기준

지휘자가 `01-intent.md` 의 "무엇을" 과 본 문서의 "내가 이해한 목표" 를 diff 한다. 의미상 차이가 크면 (범위·스테이크홀더·성공지표 변동) 의도 문서가 실패한 것 — 페이즈 01 재실행.

## 왜 이 페이즈가 필요한가

우로보로스의 첫 번째 자기 무는 지점. 출력(`01-intent.md`)을 다음 입력으로 흘리고, 그 결과를 원본과 대조해 표류를 잡는다. 코드 시간 들기 전에.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).
