# Phase 08 — 구현 (모듈별)

## 한 줄 요약
**계획의 TODO DAG 를 따라 한 TODO 당 한 구현 에이전트를 띄운다.** 각 에이전트는 코드 + 테스트 + 목 표면을 한 호출에 함께 출하 — 분리 출하 금지.

## 입력
- `plan/06-plan.md`
- `plan/07-plan-review.md`

## 서브에이전트
TODO 마다 [`../agents/implementer.md`](../agents/implementer.md) 로 `Agent(subagent_type="general-purpose")`. 프롬프트에 다음을 포함:

ⓐ TODO 풀텍스트.
ⓑ `의존` TODO 들의 `완료 조건` (의존 가능한 표면 알 수 있게).
ⓒ `intent/01-intent.md` + `intent/04-answers.md` + `intent/05-decisions.md` 경로 (마이크로 모호함 자가 해소).
ⓓ "코드 + 테스트 + 목 표면을 한 번에 출하, 못하면 명시 실패" 라는 강제.

## 산출물
TODO 마다 `impl/08-impl-log.md` 에 항목 append:

ⓐ TODO ID + 제목.
ⓑ 생성/수정 파일 (경로 + 라인 수).
ⓒ 추가 테스트 (경로 + 케이스 수).
ⓓ 노출한 목 표면 (인터페이스명 + 사용 예).
ⓔ 계획 대비 일탈 (한 줄 사유).

## 병렬화

공유 의존이 없는 TODO 는 한 메시지에 다중 `Agent` 호출로 동시 디스패치. DAG 엣지 가로지를 때만 직렬.

## 기본 스택 (재확인)

명시 없으면:

ⓐ **백엔드 / API / 엔진** — Go. `internal/` 패키지 분리, 도메인은 외부 의존 import 금지.
ⓑ **프론트엔드** — bun + React + TypeScript.
ⓒ **각 모듈은 포트 인터페이스를 노출** — `type AuthService interface { ... }` (Go) / `interface AuthService { ... }` (TS).

## 성공 기준

ⓐ 모든 TODO 가 `impl-log` 에 항목.
ⓑ 코드만 있고 테스트 없음 = fail.
ⓒ 테스트만 있고 외부 의존 목 표면 없음 = fail.

## 구현 에이전트 실패 처리

① 출력을 직접 Read — 요약만 믿지 않음 (CLAUDE.md "trust but verify").
② 환경 문제(누락 dep) → 고치고 재디스패치.
③ 개념 문제(TODO 너무 큼, 의존 잘못됨) → 페이즈 06 으로 돌아가 분할. 무리하게 덮지 않음.
