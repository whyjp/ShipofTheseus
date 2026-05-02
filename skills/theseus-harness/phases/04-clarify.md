# Phase 04 — 사용자 질의

## 한 줄 요약
**의도 문서의 모호함을 사용자와 직접 해소하는 유일한 페이즈.** [`../conventions/interview.md`](../conventions/interview.md) 컨벤션을 예외 없이 따른다 — 두괄식·1회 1질의·숫자 객관식 5개 이하.

## 입력
- `intent/01-intent.md`
- `intent/03-comprehension.md` (재이해에서 표류한 지점)

## 서브에이전트
[`../agents/clarifier.md`](../agents/clarifier.md). 이 에이전트는 *질의 목록만 작성* 한다 — 사용자에게 직접 묻지 않음. 묻는 사람은 지휘자.

## 산출물

ⓐ `intent/04-questions.md` — 질의 리스트. 각 항목: 질문 텍스트, 왜 중요한지, 보기 후보(객관식이면).
ⓑ `intent/04-answers.md` — 사용자 답을 시각과 함께 기록.
ⓒ `intent/04-resource-profile.md` — 리소스 프로파일 합의 + 추정 천정. [`../conventions/resources.md`](../conventions/resources.md).
ⓓ `intent/04-stack.md` — 언어/컴파일러/패키지 매니저 합의. [`../conventions/stack.md`](../conventions/stack.md).
ⓔ NFR 임계 확정값은 `intent/01-intent.md` 의 "성능/스펙" 표를 in-place 갱신 (`proposed: true` → 사용자 답).
ⓕ `intent/04-autonomy.md` — [`../conventions/autonomy.md`](../conventions/autonomy.md) 의 사전 위임 카탈로그 Q-D1 ~ Q-D6 답 6 줄. **이게 페이즈 05 진입 조건** — 답이 빠지면 페이즈 05 시작 불가.

## 지휘자 동작 (강제)

각 질문마다:

① 두괄식 한 줄 요약을 먼저 출력.
② 다음 문단에 배경·트레이드오프.
③ 객관식이면 숫자 5개 이하로 — `AskUserQuestion` 의 `options` 배열에 라벨 `"1"` … `"4"`. 5번째 옵션이 필요하면 별도 자유 응답 후속으로 분리.
④ 자유 응답이 본질이면 도구 없이 평문으로 질의.
⑤ 답을 받기 전에는 다음 질문으로 넘어가지 않는다 — 사용자가 답할 때까지 다른 페이즈 호출 금지.

## 첫 질의 — Q-G1 그레이드 확정 ([`../conventions/grades.md`](../conventions/grades.md))

본 페이즈의 **가장 첫 질의**. `scoring/grade_assess.py` 의 자동 추정을 두괄식으로 보여주고 5 보기 객관식으로 사용자 확정. Grade 1 (Trivial) 답이면 본 하네스 즉시 종료 + 단순 응답 권고.

## PRD 입력 처리 — 인터뷰 스킵 금지 ([`../conventions/prd-handling.md`](../conventions/prd-handling.md))

사용자가 PRD/스펙 문서를 첨부했어도 본 페이즈의 *모든 인터뷰 항목* 은 생략 안 됨. PRD 추출값은 객관식의 1번 보기로 제안되고, 사용자가 빠르게 1 클릭 확정. 각 답에 `user_explicit_confirmation: true` + `confirmed_at` timestamp 필수. self_lint C33 이 누락된 항목 자동 검출 → 페이즈 05 진입 거부.

## 사전 위임 카탈로그 (페이즈 04 의 마지막 6 질의)

본 페이즈가 *유일한* 사용자 인터럽트 지점이므로, 후속 페이즈(05~13) 의 모든 자율 결정 정책을 *여기서* 한 번에 결정한다. [`../conventions/autonomy.md`](../conventions/autonomy.md) 의 Q-D1 ~ Q-D6 6 질의를 Q-G1 + 일반 질의 *뒤에* 차례로 진행:

ⓐ Q-D1 — 회귀 권고 자동 적용 정책 (페이즈 11)
ⓑ Q-D2 — 경쟁 resolve 자동 적용 정책 (competition.md)
ⓒ Q-D3 — 천정 도달 시 자동 임계 조정 정책 (resources.md)
ⓓ Q-D4 — 정체 누적 시 정책 (lessons.md)
ⓔ Q-D5 — 자율 패키지 업데이트 정책 (stack.md)
ⓕ Q-D6 — 자율 결정 보고 빈도

답을 `intent/04-autonomy.md` 에 기록. **이 6 답이 빠지면 페이즈 05 진입 불가** — 페이즈 04 가 마지막 인터럽트이므로 사전 위임 답 없이는 후속 자율 진행이 정의 안 된다.

## 성공 기준

ⓐ `04-answers.md` 가 `04-questions.md` 의 모든 항목을 커버. `TBD` 또는 `?` 표시 없음.
ⓑ "사용자가 결정 보류" 같은 응답도 명시적으로 기록 (페이즈 05 비평이 이를 다시 다룸).

## 흔한 실패

ⓐ 질문 6개 이상 — 차원이 섞임. clarifier 재실행해 차원별로 재구성.
ⓑ 객관식인데 알파벳 라벨 — 컨벤션 위반. 수정 후 재질의.
ⓒ 두괄식 누락 — 사용자가 끝까지 읽어야 핵심이 나오는 질문은 무효.
