# theseus-harness 웹뷰 (be4fe + fe)

## 한 줄 요약
**`.ShipofTheseus/<프로젝트>/` 산출물을 모듈 구성도·설계 의도·구현 의도·단위 테스트·E2E·스프린트 6 탭으로 인터랙티브 시각화하는 bun 기반 웹뷰.** 하네스 매 실행마다 페이즈 12 가 자동 생성한다.

## 구성

```
webview/
├── package.json          # bun 런타임, hono + react + vite
├── server.ts             # be4fe — 산출물 → JSON API
├── vite.config.ts        # fe 빌드 + /api 프록시
├── tsconfig.json
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx           # 6 탭 컨테이너
    ├── styles.css
    ├── lib/api.ts        # fetch 래퍼
    ├── components/
    │   ├── TimingHeader.tsx   # 시작/누적/현재 시각 라이브
    │   └── EmptyState.tsx
    └── tabs/
        ├── ModuleMap.tsx
        ├── DesignIntent.tsx
        ├── ImplIntent.tsx
        ├── UnitTests.tsx
        ├── E2ETests.tsx
        └── Sprints.tsx
```

## 실행

```bash
cd .ShipofTheseus/<프로젝트>/webview
bun install
bun run dev
# fe: http://localhost:5173 (vite)
# be4fe: http://localhost:5174 (hono, /api/* 프록시 대상)
```

## 환경 변수

| 변수 | 의미 | 기본값 |
| ---- | ---- | ----- |
| `THESEUS_ROOT` | 프로젝트 산출물 루트 | webview 의 부모 디렉터리 |
| `PORT` | be4fe 포트 | 5174 |

## be4fe API 표

| 엔드포인트 | 산출물 |
| --------- | ----- |
| `GET /api/timing` | `timing/start.json` + 현재 시각 + 누적 경과 |
| `GET /api/naming` | `naming/*.md` |
| `GET /api/intent` | `intent/*.md` (의도/리뷰/재이해/질문/답/비평/결정) |
| `GET /api/plan` | `plan/*.md` (계획/계획 리뷰) |
| `GET /api/impl` | `impl/08-impl-log.md` + `quality/09-quality-gate.md` |
| `GET /api/sprints` | 모든 `sprints/NN/{report.md, inputs.json, bisect.md}` |
| `GET /api/tests/unit` | `sprints/NN/unit.json` 합본 |
| `GET /api/tests/e2e` | `sprints/NN/e2e.json` 합본 |
| `GET /api/events` | SSE — 산출 디렉터리 변경 푸시 |

## 6 탭 강제

본 스캐폴드는 페이즈 12 의 강제 6 탭 룰에 맞춰 설계됨. 데이터가 없는 탭은 빈 상태 안내를 보여주되 **숨기지 않는다.**

| 탭 | 데이터 소스 | 인터랙션 |
| -- | --------- | ------- |
| 모듈 구성도 | `/api/plan` | 마크다운 + (후속) react-flow DAG |
| 설계 의도 | `/api/intent` | 섹션 접기/펼치기 |
| 구현 의도 | `/api/impl` | 게이트 위반 라인 클릭 |
| 단위 테스트 | `/api/tests/unit` | 실패 트레이스 드릴다운 |
| E2E 테스트 | `/api/tests/e2e` | 시나리오 → 스텝 → 스크린샷 |
| 스프린트 | `/api/sprints` | 점수 차트 + 스프린트 상세 |

## 확장

ⓐ `tabs/ModuleMap.tsx` 를 react-flow 기반 DAG 시각화로 교체 — 계획의 TODO·의존을 노드/엣지로.
ⓑ `lib/api.ts` 에 SSE 구독 추가 — `/api/events` 로 산출물 변경 라이브 갱신.
ⓒ 테스터 에이전트가 `sprints/NN/unit.json`, `e2e.json` 표준 형식으로 결과를 떨어뜨리도록 지시 — 위 탭들이 그대로 소비.

## 한국어 폰트

`styles.css` 에 `Apple SD Gothic Neo`, `Noto Sans KR` 폴백 포함. 추가 폰트 필요 시 `index.html` 에 `<link rel="stylesheet">` 로.
