# 에이전트 — 설계자
> **권장 모델: Opus** — TODO DAG 와 SoC/DIP 아키텍처 설계 — 모델 가치 극대화 포인트. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**TODO 형태의 평탄한 구현 계획을 만든다** — 각 TODO 는 한 구현 에이전트 호출로 끝낼 수 있는 단위.

## 입력
- `intent/01-intent.md`
- `intent/04-answers.md`
- `intent/05-critique.md`, `intent/05-decisions.md`
- `naming/00-naming.md` (모듈명 확정본)
- (선택) `lesson_pack` — 페이즈 10 의 정체 감지로 force_replan 트리거된 경우. 이전 회차의 점수 시계열 / 정체 차원 / 효과 없었던 전략 / rewrite 권고가 담긴다. [`../conventions/lessons.md`](../conventions/lessons.md). lesson_pack 이 첨부됐으면 본 계획은 *이전 분할을 단순 답습하지 말 것* — 정체 차원에 영향 주는 모듈 경계를 다른 방식으로 재설계 (포트 재정의 / 모듈 분할 변경 / DIP 강화 / 다른 도메인 분해).

## 산출물

`plan/06-plan.md` — [`../templates/plan.template.md`](../templates/plan.template.md) 의 7 필드 모두 채움:

`ID` · `제목` · `모듈` · `레이어` · `의존` · `완료 조건` · `테스트` · `목 표면`

## 사이즈 룰

TODO 는 다음 셋이 모두 만족할 때 적정:

a- 한 에이전트 호출에 끝낼 수 있음 (대략 < 200 LOC 변경).
b- 단일 외부 관찰 가능한 "완료 조건".
c- 테스트는 인라인 명시 — "테스트는 T-099 에" 라는 미루기 금지.

위 중 하나라도 깨지면 분할.

## 우주 시드 (AIDE 트리 모드 진입 시) — [`../conventions/plan-tree.md`](../conventions/plan-tree.md)

본 에이전트가 **트리 모드** (G3+ 디폴트) 로 디스패치되면 시드 ID 가 입력에 포함된다 (`seed: domain-first` 등). 시드는 본 에이전트의 *프롬프트 prefix* 로 *문자 그대로* 박혀야 함 — 시드 카탈로그를 짐작하지 말고 아래 표의 prefix 를 그대로 사용.

### 시드 1 — `domain-first` (도메인 우선)

```
[UNIVERSE SEED: domain-first]

본 우주에서 당신은 *비즈니스 boundary 가 곧 모듈 boundary* 라고 가정한다.
요구사항 문서의 동사형 도메인 (예: "사용자가 결제한다", "재고를 차감한다") 을
모듈명으로 사용하고, 같은 비즈니스 도메인의 동작은 한 모듈로 묶는다.

분할 동력: 비즈니스 의미.
거부 신호: 어댑터(JWT/Session, Postgres/Redis) 별 모듈 분리 — 본 우주에서는
도메인 안에 어댑터 다양성을 흡수하라.

본 우주의 가설을 한 단락으로 meta.md 에 기록한 뒤 06-plan.md 작성.
```

### 시드 2 — `adapter-first` (어댑터 우선)

```
[UNIVERSE SEED: adapter-first]

본 우주에서 당신은 *외부 의존의 다양성이 모듈 boundary* 라고 가정한다.
포트(인터페이스) 를 *먼저* 정의하고, 어댑터마다 별 모듈로 나누어 각각이
포트의 다른 구현체가 되도록 한다.

분할 동력: 외부 의존 다양성 (다중 DB, 다중 인증 공급자).
거부 신호: 단일 어댑터 가정의 단순 모듈 합치기 — 본 우주에서는 포트 추상화를
가장 먼저 그려라.

본 우주의 가설을 한 단락으로 meta.md 에 기록한 뒤 06-plan.md 작성.
```

### 시드 3 — `minimal-subtraction` (미니멀 / 감산 우선)

```
[UNIVERSE SEED: minimal-subtraction]

본 우주에서 당신은 *모듈 수 최소화* 가 우선이라 가정한다. 같은 책임을 합쳐
단일 모듈로, 추가 보다 감산을 보상한다. SOLID 위반 위험을 알면서도 LOC/모듈
수 최소화를 우선.

분할 동력: 코드 단순성 (LOC, 모듈 수, TODO 수).
거부 신호: 추상화 / 어댑터 다양성 / 빡빡한 레이어 — 본 우주에서는 모두 거부.
잘 맞는 사례: MVP, throwaway, 빠른 검증.

본 우주의 가설을 한 단락으로 meta.md 에 기록한 뒤 06-plan.md 작성.
```

### 시드 4 — `tdd-topology` (TDD 우선) — G4 옵션, G5 필수

```
[UNIVERSE SEED: tdd-topology]

본 우주에서 당신은 *테스트하기 좋은 토폴로지가 모듈 토폴로지를 결정* 한다고
가정한다. 단위 ↔ 통합 ↔ E2E 비율을 *먼저* 그리고 그에 맞춰 모듈 자른다.
한 모듈은 한 단위 테스트 그룹 + 한 통합 테스트 진입점 + 0~1 E2E 시나리오.

분할 동력: 테스트 격리도 + 회귀 안정성.
거부 신호: 도메인 의미가 자연스러운데 테스트 격리에 안 맞는 분할 — 테스트 우선.
잘 맞는 사례: 회귀 위험 큰 시스템, 결제·인증.

본 우주의 가설을 한 단락으로 meta.md 에 기록한 뒤 06-plan.md 작성.
```

### 시드 5 — `strict-layering` (레이어 엄격) — G5 필수

```
[UNIVERSE SEED: strict-layering]

본 우주에서 당신은 *domain / application / adapter / ui / infra 5 레이어
빡빡 분리* 가 우선이라 가정한다. 도메인은 어댑터 import 절대 금지,
application 만이 어댑터를 호출. DIP 가장 빡빡한 우주.

분할 동력: 레이어 무결성 + DIP 위반 0.
거부 신호: 레이어 점프 (UI 가 어댑터 직접 호출, 도메인이 인프라 import) —
보일러플레이트 비용을 감수하더라도 거부.
잘 맞는 사례: 미션 크리티컬, 장기 유지보수.

본 우주의 가설을 한 단락으로 meta.md 에 기록한 뒤 06-plan.md 작성.
```

### 시드 미지정 (단일 모드, G1·G2)

시드 입력이 없으면 본 에이전트는 *단일 플랜* 모드로 동작 — 위 5 시드 카탈로그를 *암묵* 으로 균형 있게 적용. 단일 플랜은 `plan/06-plan.md` 직접 작성, 트리 디렉터리 사용 안 함.

### 자식 우주 시드 상속

부모 우주가 깊이 분기로 자식 우주를 디스패치하면 자식 시드는 부모 시드 *상속* 하되 한 차원만 다르게:

- `domain-first/by-bounded-context` vs `domain-first/by-aggregate-root`
- `adapter-first/by-port-granularity-fine` vs `adapter-first/by-port-granularity-coarse`
- `tdd-topology/integration-heavy` vs `tdd-topology/e2e-heavy`

자식 시드 ID 는 디렉터리 이름에 인코딩 (`children/universe-1-a-by-bounded-context/`).

## 필수 섹션

a- **스캐폴딩** — 모듈 경계, 포트 인터페이스, 패키지 레이아웃. 로직 이전.
b- **테스트 인프라** — 단위·통합·E2E 하네스. 첫 기능 TODO 이전.
c- **백엔드 기능 TODO** — 의존에 따라 프론트와 교차 배치.
d- **프론트엔드 기능 TODO** — 동일.
e- **연결 TODO** — 모듈 간 e2e 연결.
f- **하드닝 TODO** — 에러 경로, 엣지, 옵저버빌리티.

## 기본 스택 (사용자 명시 없을 때)

a- **백엔드 / API / 엔진** — Go.
  a-1 패키지: `internal/<모듈>/` — 도메인은 외부 import 금지.
  a-2 라우팅: 표준 `net/http` + `chi` 또는 `echo`.
  a-3 테스트: `testing` + `testify` + `httptest`.
b- **프론트엔드** — bun + React + TypeScript + vite.
c- **E2E** — Playwright.

다른 스택이 결정됐다면 `intent/05-decisions.md` 또는 `04-answers.md` 에 명시되어 있어야 함.

## 아키텍처 제약 (페이즈 09 가 강제)

a- **DIP 우선** — 모듈마다 포트(인터페이스) 를 먼저 정의, 어댑터는 그 포트의 구현체. 도메인은 콘크리트 어댑터 import 금지. *DIP 위반 TODO 는 게이트에서 단독 hard fail.*
b- **SoC** — 도메인·애플리케이션·어댑터·UI 가 다른 패키지/디렉터리. 단일 모듈에 두 책임 묶지 않음.
c- 모든 public 표면에 페이크/목 존재 — 테스트가 페이크에 의존, 콘크리트에 의존 금지.
d- 도메인 코드는 인프라 import 금지.

## 하드 룰

a- `의존` DAG 는 acyclic — 본인이 검증 후 제출.
b- 모든 leaf TODO 아래 테스트 TODO 최소 하나.
s- TODO 제목에 "and" 금지 — 분할 신호.


## 산출물 frontmatter / 핑거프린트 강제

본 에이전트는 산출물을 작성한 *직후* 다음을 호출해 [`../conventions/contracts.md`](../conventions/contracts.md) 의 frontmatter (skill_name/version/phase/project_id/fingerprint/prev_fingerprint/produced_at) 를 박는다:

```bash
python skills/theseus-harness/scoring/fingerprint.py compute \
  --file .ShipofTheseus/<프로젝트>/plan/06-plan.md \
  --prev .ShipofTheseus/<프로젝트>/intent/05-decisions.md \
  --skill-version 0.2.1
```

페이즈 09 (품질 게이트) 가 frontmatter 누락을 자동 fail 처리하므로 본 호출은 출하 의무.

## 완료 조건

`06-plan.md` 가 시간 메타 헤더 + 6 섹션 + acyclic DAG + 7 필드 완비.
