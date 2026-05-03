# Phase 08 — 구현 (모듈별)

## 한 줄 요약
**계획의 TODO DAG 를 따라 한 TODO 당 한 구현 에이전트를 띄운다.** 5 서브페이즈 (08-α/β/γ/δ/ε) 로 분해 — test-first 원칙 강제.

## 5 서브페이즈 분해 (TDD test-first, sprint-05-a)

페이즈 08 은 *한 sub-agent 가 코드 + 테스트 + 실행을 동시 진행* 하면 test-first 위반이다. sprint-05-a 부터 다음 5 서브페이즈로 강제 분해한다.

| 서브페이즈 | 책임 | sub-agent | 산출물 | 게이트 |
|----|----|----|----|----|
| **08-α scope** | atomic / group / functional 3 계층 test scope 정의 | test-architect (Sonnet) | impl/08-test-scope.md | scope 분리 ≥ 3 계층 |
| **08-β test (RED)** | test-first writer — 테스트만 작성, 구현 0 | test-writer (Sonnet) | code/tests/* | pytest 실행 시 모든 테스트 RED (right reason) |
| **08-γ impl (GREEN)** | 테스트 통과 최소 구현 | implementer (Sonnet/Opus) | code/<modules>/*.py + 실행 + 산출물 emit | pytest 모두 GREEN |
| **08-δ refactor (REFACTOR)** | DRY / SOLID 정리 + docstring + type hint | refactorer (Sonnet) | code/* 수정 | pytest GREEN 유지 |
| **08-ε log** | impl/08-impl-log.md (TODO 매핑 + 모듈명 + 인터페이스) | implementer 본인 (마지막) | impl/08-impl-log.md | HARD-RULE 9.b 의무 본문 |

관련 에이전트: [`../agents/test-architect.md`](../agents/test-architect.md) / [`../agents/test-writer.md`](../agents/test-writer.md) / [`../agents/refactorer.md`](../agents/refactorer.md) / [`../agents/implementer.md`](../agents/implementer.md)

## universe 변경 시 재진입 룰

페이즈 06 plan-tree 의 머지 결정 변경 (universe 추가/제거/머지 변경) 발생 시 **08-α 부터 재실행**한다.

- universe 변경 → 기존 scope 무효 → 08-α (scope 재정의) 재진입
- 새 scope → 새 test → 새 impl → 새 refactor → 새 log
- 부분 재실행(08-β 만 재실행 등) 금지 — 08-α 부터 전체 재순환

키워드: `universe 변경` 감지 시 오케스트레이터는 현재 08 단계를 중단하고 08-α 로 돌아간다.

## TDD test-first 원칙 — 안티 패턴

test-first 원칙 위반은 페이즈 08 의 가장 흔한 실패 모드다. 다음은 **금지** 안티 패턴이다:

a- **test-after** — 코드 작성 후 사후 테스트 (test-after) 금지. 구현 전 반드시 RED 확인.
b- **동시 작성** — test 와 impl 한 sub-agent 가 동시 작성 금지. 08-β 와 08-γ 는 별도 에이전트, 별도 호출.
c- **GREEN 없이 REFACTOR** — 08-δ (REFACTOR) 는 반드시 08-γ (GREEN) 완료 후 진입. 테스트 통과 전 리팩터 금지.
d- **RED 확인 생략** — 08-β 완료 시 pytest 실행해 모든 신규 테스트가 RED (right reason) 임을 반드시 확인.

## 입력
- `plan/06-plan.md`
- `plan/07-plan-review.md`

## 서브에이전트

5 서브페이즈별 전담 에이전트를 순서대로 디스패치한다. 각 에이전트 프롬프트에 포함 필수:

a- TODO 풀텍스트 (ID, 제목, 모듈, 레이어, 의존, 완료 조건).
b- `의존` TODO 들의 `완료 조건` (의존 가능한 표면 알 수 있게).
c- `intent/01-intent.md` + `intent/04-answers.md` + `intent/05-decisions.md` 경로 (마이크로 모호함 자가 해소).
d- 서브페이즈 역할 명시 (08-α / 08-β / 08-γ / 08-δ / 08-ε 중 하나).

## 산출물
TODO 마다 `impl/08-impl-log.md` 에 항목 append:

a- TODO ID + 제목.
b- 생성/수정 파일 (경로 + 라인 수).
c- 추가 테스트 (경로 + 케이스 수).
d- 노출한 목 표면 (인터페이스명 + 사용 예).
e- 계획 대비 일탈 (한 줄 사유).

## 병렬화

공유 의존이 없는 TODO 는 한 메시지에 다중 `Agent` 호출로 동시 디스패치. DAG 엣지 가로지를 때만 직렬.

## 빌드 스크립트 강제 (sh + bat 양쪽)

[`../conventions/build-and-config.md`](../conventions/build-and-config.md) §1 에 따라 모든 모듈 + 루트에 다음 셋트를 *반드시* 출하:

a- `scripts/build.sh` + `scripts/build.bat` — 컴파일/번들.
b- `scripts/test.sh` + `scripts/test.bat` — 단위+통합+E2E 매트릭스.
c- `scripts/dev.sh` + `scripts/dev.bat` — 개발 모드 핫리로드.
d- `scripts/setup.sh` + `scripts/setup.bat` — 의존 설치 + 환경 점검.

한쪽(예: sh 만 있고 bat 누락) 출하 시 페이즈 09 게이트 fail. eol 정규화는 `.gitattributes` (build-and-config.md §6) 가 강제.

## TOML 설정 + .example 강제

[`../conventions/build-and-config.md`](../conventions/build-and-config.md) §2 에 따라 `config.toml` + `.env` 는 `.gitignore`, `config.toml.example` + `.env.example` 은 항상 커밋. 누락 시 게이트 9 fail.

## 경쟁 컨벤션 트리거 (페이즈 08 적용)

[`../conventions/competition.md`](../conventions/competition.md) 의 트리거 조건 c- ("두 구현 방식이 모두 SOLID/테스트 통과 가능, 미감 차이만 있음") 가 *도메인 코어 같은 복잡 모듈* 에서 충족되면 2~3 후보 구현을 격리 병렬 생성 → score.py 로 채점 → 우승자 또는 머지. 단순 어댑터까지는 비용 폭발이라 경쟁 안 함.

## 기본 스택 (재확인)

명시 없으면:

a- **백엔드 / API / 엔진** — Go. `internal/` 패키지 분리, 도메인은 외부 의존 import 금지.
b- **프론트엔드** — bun + React + TypeScript.
c- **각 모듈은 포트 인터페이스를 노출** — `type AuthService interface { ... }` (Go) / `interface AuthService { ... }` (TS).

## 성공 기준

a- 모든 TODO 가 `impl-log` 에 항목.
b- 코드만 있고 테스트 없음 = fail.
c- 테스트만 있고 외부 의존 목 표면 없음 = fail.

## 구현 에이전트 실패 처리

1- 출력을 직접 Read — 요약만 믿지 않음 (CLAUDE.md "trust but verify").
2- 환경 문제(누락 dep) → 고치고 재디스패치.
3- 개념 문제(TODO 너무 큼, 의존 잘못됨) → 페이즈 06 으로 돌아가 분할. 무리하게 덮지 않음.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).

## universe 별 5 서브페이즈 head-to-head (sprint-05-b)

페이즈 06 plan-tree 의 폭 확장 (G3 폭 3 / G4 폭 4 / G5 폭 6) 으로 N 개 universe 가 살아남으면, 페이즈 08 도 *universe 별 implementer* 가 *각각 5 서브페이즈 (08-α/β/γ/δ/ε) 를 독립 사이클* 로 진행한다. 즉 각 universe 가 자기 plan 으로 자기 코드를 써 *실 head-to-head* 비교 가능.

### universe 별 5 서브페이즈 사이클

각 universe-N 마다 :
- 08-α scope : universe-N 의 plan 의 인터페이스/모듈 분해에 맞춘 test scope
- 08-β test (RED) : universe-N 의 인터페이스 시그니처 따른 테스트
- 08-γ impl (GREEN) : universe-N 의 plan 의 디자인 결정 따른 최소 구현
- 08-δ refactor : universe-N 코드 정리 (ruff + DRY/SOLID)
- 08-ε log : `impl/08-impl-log.universe-N.md`

산출물 :
- `code/universe-1/`, `code/universe-2/`, ..., `code/universe-N/` (격리)
- 각 universe 별 `impl/08-test-scope.universe-N.md` + `impl/08-impl-log.universe-N.md`

### head-to-head 점수 비교 (페이즈 09 게이트 + 페이즈 10 sprint)

각 universe-N 의 코드를 *동일한 acceptance criteria* (Q-D8 verification) 에 통과시킨 뒤 점수 비교 :
- 각 universe 의 pytest pass rate
- 각 universe 의 sprint metric (해당 도메인의 sanity check / NFR / etc.)
- 각 universe 의 wall-clock + 토큰 + LOC + ruff 위반 수

[`../conventions/competition.md`](../conventions/competition.md) 의 자동 머지 알고리즘 (sprint-05-b 신규) 이 차원별 sub-score 로 :
a- 단일 우승자 채택 OR
b- 차원별 머지 (예: universe-1 의 Resource topology + universe-2 의 Dispatcher + universe-3 의 EventLogger) — 머지 결과를 *새 code/* 디렉터리로 emit + 페이즈 10 sprint 재진입

### universe 변경 시 재진입 (기존 룰 강화)

페이즈 06 의 머지 결정 변경 시 → 모든 활성 universe 의 08-α 부터 재실행 (test-first 위반 방지). 새 머지 결과 universe → 새 5 서브페이즈 사이클.

### 비용 가드

[`../conventions/resources.md`](../conventions/resources.md) 의 universe N 병렬 budget profile (sprint-05-b) 가 메모리/시간 가드. 초과 시 자율 폭 축소 (G4 4→3, G5 6→5) + lessons 기록.

### sprint-05-a 베이스라인 retro

sprint-05-a 의 simulation-bench 케이스는 *페이즈 06 에서 머지 결정 후 페이즈 08 단일 universe 로 진행* (G3 폭 2, 머지 fast resolve). sprint-05-b 후 동일 케이스 = 폭 3 × 5 서브페이즈 독립 → 3 후보 코드 head-to-head → 차원별 머지 → 추정 점수 92 → 95-97 lift 가능.
