# Phase 12 — be4fe + bun fe 웹뷰 자동 생성

## 한 줄 요약
**모든 산출물(.ShipofTheseus/<프로젝트>/) 을 인터랙티브하게 보여주는 bun 기반 웹뷰를 생성한다.** be4fe 가 산출 파일을 읽어 API 로 노출, fe 가 모듈 구성도·설계 의도·구현 의도·단위 테스트·E2E 결과를 탭 인터페이스로 시각화. 매 실행마다 항상 생성.

## 입력
- `.ShipofTheseus/<프로젝트명>/` 의 모든 산출물.

## 서브에이전트
[`../agents/webview-builder.md`](../agents/webview-builder.md). 시작 스캐폴드는 [`../templates/webview/`](../templates/webview/).

## 산출물 (`webview/`)

```
webview/
├── package.json            # bun 런타임, hono + react + vite
├── tsconfig.json
├── server.ts               # be4fe — Hono, 산출물 파일 직읽기
├── src/
│   ├── main.tsx
│   ├── App.tsx             # 탭 컨테이너
│   ├── tabs/
│   │   ├── ModuleMap.tsx   # 모듈 구성도 (DAG 시각화)
│   │   ├── DesignIntent.tsx# 의도 문서 렌더
│   │   ├── ImplIntent.tsx  # 구현 의도(impl-log + 게이트 결과)
│   │   ├── UnitTests.tsx   # 단위 테스트 결과 인터랙티브
│   │   ├── E2ETests.tsx    # E2E 결과 인터랙티브 (스프린트별)
│   │   └── Sprints.tsx     # 스프린트 타임라인 + 점수 차트 + 회귀 바이섹트
│   └── components/
│       ├── TimingHeader.tsx# 시작/경과/현재 시각 표시 (실시간 업데이트)
│       └── ScoreBadge.tsx
├── README.md               # 빌드 + 실행 명령
└── public/
    └── index.html
```

## 필수 탭 (모두 항상 생성)

| 탭 | 무엇을 보여주는가 |
| -- | --------------- |
| 모듈 구성도 | 계획의 DAG 시각화 (TODO 의존, 모듈 경계, 포트) |
| 설계 의도 | `intent/01-intent.md` + `04-answers.md` + `05-decisions.md` 렌더 |
| 구현 의도 | `impl/08-impl-log.md` + `quality/09-quality-gate.md` 렌더 |
| 단위 테스트 | 모든 스프린트의 단위 결과, 클릭 시 실패 트레이스 표시 |
| E2E 테스트 | E2E 시나리오·스크린샷·스프린트별 상태 |
| 스프린트 | 점수 차트(차원별), 타임라인, 회귀 바이섹트 링크 |

## 시간 정보 표시

[`../conventions/timing.md`](../conventions/timing.md) 의 헤더 메타를 모든 페이지 상단 `TimingHeader` 컴포넌트에 표시: 최초 프롬프트 시각·총 누적 경과·현재 시각. 5 초 간격 폴링으로 누적 경과는 라이브 갱신 (페이즈 진행 중에도 사용자가 시간 체감 가능).

## be4fe 책임

a- `.ShipofTheseus/<프로젝트>/**/*.md` Read 후 frontmatter/섹션 파싱해 JSON 으로 노출.
b- `sprints/*/inputs.json` + `report.md` 합쳐 차트용 시계열 데이터 생성.
c- 단위/E2E 테스트 결과 (Go `go test -json`, Playwright JSON reporter) 를 정규화.
d- 파일 변경 감시 (chokidar 등) → SSE 로 fe 에 푸시.

## 실행

`webview/README.md` 에 다음 명령 명시:

```
cd webview
bun install
bun run dev          # be4fe + fe 동시 기동, http://localhost:5173
```

## 성공 기준

a- `bun install && bun run dev` 가 성공.
b- 모든 6 탭이 데이터 로드 (해당 산출물이 있는 한).
c- TimingHeader 가 모든 페이지에 보이고 라이브 업데이트.
d- 단위·E2E 탭이 인터랙티브 — 실패 항목 클릭으로 드릴다운.
e- Lighthouse 같은 외부 점검까지 강제하지는 않음 — 기능 동작만 확인.

## 흔한 실패

a- 정적 HTML 만 출력 — 인터랙티브 요구 미충족, fail.
b- E2E 탭이 숨겨져 있거나 "차후 구현" 표시 — 항상 생성 룰 위반.
c- 산출 파일을 빌드 시점에 fs 로 박아넣음 — 런타임 폴링/감시여야 의도와 코드가 변할 때 자동 반영.

> **공통 안티 패턴** (조기 추상화 / 분산 모놀리스 / 두괄식 누락 / 객관식 라벨 등) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.
