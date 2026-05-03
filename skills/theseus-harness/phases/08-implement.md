# Phase 08 — 구현 (모듈별)

## 한 줄 요약
**계획의 TODO DAG 를 따라 한 TODO 당 한 구현 에이전트를 띄운다.** 각 에이전트는 코드 + 테스트 + 목 표면을 한 호출에 함께 출하 — 분리 출하 금지.

## 입력
- `plan/06-plan.md`
- `plan/07-plan-review.md`

## 서브에이전트
TODO 마다 [`../agents/implementer.md`](../agents/implementer.md) 로 `Agent(subagent_type="general-purpose")`. 프롬프트에 다음을 포함:

a- TODO 풀텍스트.
b- `의존` TODO 들의 `완료 조건` (의존 가능한 표면 알 수 있게).
c- `intent/01-intent.md` + `intent/04-answers.md` + `intent/05-decisions.md` 경로 (마이크로 모호함 자가 해소).
d- "코드 + 테스트 + 목 표면을 한 번에 출하, 못하면 명시 실패" 라는 강제.

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
