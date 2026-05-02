# Phase 06 — 계획 (TODO 형)

## 한 줄 요약
**TODO 단위의 평탄한 구현 계획을 만든다.** 각 TODO 는 한 번의 서브에이전트 호출로 끝낼 수 있을 만큼 작고, 명확한 "완료 조건" 을 갖는다.

## 입력
- `intent/01-intent.md`, `intent/04-answers.md`, `intent/05-critique.md`, `intent/05-decisions.md`
- `naming/00-naming.md` (모듈명 확정본)

## 서브에이전트
[`../agents/planner.md`](../agents/planner.md) 로 `Agent(subagent_type="Plan")`.

## 산출물
`plan/06-plan.md` — [`../templates/plan.template.md`](../templates/plan.template.md) 의 7개 필드를 모든 TODO 에 채움:

| 필드 | 의미 |
| ---- | ---- |
| `ID` | `T-001`, `T-002`, … |
| `제목` | 명령형 한 줄 |
| `모듈` | 명명 페이즈에서 정해진 모듈명 (`be4fe/auth`, `fe/login` 등) |
| `레이어` | `domain` / `application` / `adapter` / `ui` / `infra` / `test` |
| `의존` | 다른 TODO ID 목록 |
| `완료 조건` | 외부 관찰·테스트 가능 |
| `테스트` | 단위·통합·E2E 어느 것을 같이 출하 |
| `목 표면` | 노출하는 포트/페이크 |

## 시퀀스 다이어그램 동봉 (필수)

[`../conventions/diagrams.md`](../conventions/diagrams.md) §3 에 따라 `plan/06-plan.md` 에 두 종류의 Mermaid 시퀀스 다이어그램을 코드 펜스로 동봉:

ⓐ **모듈 내부 시퀀스** — 도메인 ↔ 어댑터 ↔ 포트 호출 흐름.
ⓑ **모듈 외부 시퀀스** — FE ↔ BE ↔ DB ↔ 외부 API.

각 화살표에 호출 함수명·요청/응답 페이로드 키 표기. PlantUML 도 허용하지만 프로젝트 시작 시 형식 하나로 고정.

## 경쟁 컨벤션 트리거 (페이즈 06 적용)

[`../conventions/competition.md`](../conventions/competition.md) 의 트리거 조건 ⓑ ("두 모듈 분할안의 장단점이 길항") 가 본 페이즈에서 충족되면, 단일 계획 대신 2~3 후보 계획을 격리 병렬 생성 후 점수 비교 → 우승자 채택 또는 머지. 경쟁 모드 진입 결정은 planner, 후보별 콜드 리딩 비교는 plan-reviewer (페이즈 07).

## 필수 섹션

ⓐ **스캐폴딩** — 모듈 경계, 포트 인터페이스, 패키지 레이아웃. 로직 전.
ⓑ **테스트 인프라** — 단위·통합·E2E 하네스 셋업. 첫 기능 TODO 전.
ⓒ **백엔드 기능 TODO** — 의존에 따라 프론트와 교차 배치.
ⓓ **프론트엔드 기능 TODO** — 동일.
ⓔ **연결 TODO** — 모듈 간 e2e 연결.
ⓕ **하드닝 TODO** — 에러 경로, 엣지, 옵저버빌리티.

## 기본 스택

사용자가 다른 스택을 명시하지 않으면:

ⓐ **백엔드 / API / 엔진** — Go (`net/http`, `chi` 또는 `echo`, 표준 라이브러리 우선).
ⓑ **프론트엔드** — bun + React (Phase 12 의 웹뷰와 같은 런타임 패밀리, 빌드 도구 통일).
ⓒ **테스트 — Go** — 표준 `testing` + `testify`. 통합은 `httptest`.
ⓓ **테스트 — FE** — `bun test` + `playwright` (E2E).

다른 스택 결정이 있다면 `intent/05-decisions.md` 또는 `intent/04-answers.md` 에 명시되어 있어야 한다.

## TODO 사이즈 룰

ⓐ 한 서브에이전트 호출에 끝낼 수 있을 것 (대략 < 200 LOC 변경).
ⓑ 단일 외부 관찰 가능한 "완료 조건".
ⓒ 테스트 같은 줄에 명시 — "테스트는 T-099 에서" 금지.

## 성공 기준

ⓐ `의존` 그래프가 acyclic — 본인이 검증.
ⓑ 모든 leaf TODO 아래에 테스트 TODO 가 최소 하나.
ⓒ 모든 TODO 제목에 "and" 없음 — 있으면 분할 신호.
