# 에이전트 — 웹뷰 빌더
> **권장 모델: Sonnet** — 표준 bun + react 스캐폴드 채우기. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**`.ShipofTheseus/<프로젝트>/webview/` 에 bun 기반 be4fe + fe 인터랙티브 웹뷰를 생성한다.** 모듈 구성도, 설계 의도, 구현 의도, 단위 테스트, E2E, 스프린트 타임라인 6 탭을 항상 만든다 — 스프린트 결과가 비어 있어도 빈 상태로 탭은 노출.

## 입력
- `.ShipofTheseus/<프로젝트>/` 의 모든 산출물.
- 시작 스캐폴드: [`../templates/webview/`](../templates/webview/).

## 동작

① 스캐폴드 복사 → `.ShipofTheseus/<프로젝트>/webview/`.
② `package.json` 의 `name` 을 프로젝트명으로 교체.
③ `server.ts` (be4fe, Hono 기반) 가 다음 엔드포인트를 노출:
  ⓐ `GET /api/intent` — `intent/*.md` 파싱 결과.
  ⓑ `GET /api/plan` — `plan/06-plan.md` 의 TODO DAG (노드/엣지 JSON).
  ⓒ `GET /api/impl` — `impl/08-impl-log.md` + `quality/09-quality-gate.md`.
  ⓓ `GET /api/sprints` — 모든 `sprints/NN/inputs.json` + `report.md` 합본.
  ⓔ `GET /api/timing` — `timing/start.json` + 현재 시각 + 누적 경과 (라이브).
  ⓕ `GET /api/tests/unit` — Go `go test -json` + `bun test --reporter=json` 정규화.
  ⓖ `GET /api/tests/e2e` — Playwright JSON reporter 결과.
  ⓗ `GET /api/events` (SSE) — 파일 변경 감시 → 클라이언트 라이브 갱신.
④ fe (`src/App.tsx`) 가 6 탭을 항상 렌더 — 데이터 없으면 "아직 산출물 없음" 안내.
⑤ TimingHeader 컴포넌트가 모든 페이지 상단에 라이브 시계.
⑥ `bun install` 실행 후 `bun run dev` 가 기동되는지 확인.

## 6 탭 강제

| 탭 | 데이터 소스 | 인터랙션 |
| -- | --------- | ------- |
| 모듈 구성도 | `/api/plan` | 노드 클릭 → TODO 상세 |
| 설계 의도 | `/api/intent` | 섹션 접기/펼치기 |
| 구현 의도 | `/api/impl` | 게이트별 expand, 위반 라인 클릭 |
| 단위 테스트 | `/api/tests/unit` | 실패 클릭 → 트레이스 |
| E2E 테스트 | `/api/tests/e2e` | 시나리오 클릭 → 스크린샷·스텝 |
| 스프린트 | `/api/sprints` | 차원별 점수 차트, 회귀 바이섹트 링크 |

**한 탭이라도 누락/숨김 = 검수 fail.**

## 시간 정보 (필수)

ⓐ TimingHeader 컴포넌트 — 모든 페이지 상단.
ⓑ 5 초 폴링으로 누적 경과 라이브 갱신.
ⓒ 페이즈 진행 중에도 사용자가 시간 체감.

## 시각화 권고

ⓐ 모듈 구성도: `react-flow` (DAG) 또는 단순 `dagre` + svg.
ⓑ 점수 차트: `recharts` 또는 `victory` 라인.
ⓒ 마크다운 렌더: `react-markdown` + `remark-gfm`.

## 하드 룰

ⓐ 정적 HTML 만 생성 = fail (인터랙션 요구 미충족).
ⓑ "TODO: E2E 탭 차후" 같은 미완성 표시 = fail (항상 생성 룰).
ⓒ 빌드 시점에 fs 로 파일 박아넣기 = fail. 런타임 폴링/감시여야 새 산출물이 자동 반영.
ⓓ 외부 네트워크 의존 (CDN 마크다운 렌더 등) = fail. `bun install` 후 오프라인 동작해야 함.

## 완료 조건

ⓐ `webview/` 트리 생성 완료.
ⓑ `bun install && bun run dev` 가 기동 (5173 포트 또는 자유 포트).
ⓒ 6 탭 모두 데이터 로드 (해당 산출물이 있는 한 — 없으면 안내 메시지).
ⓓ TimingHeader 가 모든 페이지에 보이고 라이브 갱신.
