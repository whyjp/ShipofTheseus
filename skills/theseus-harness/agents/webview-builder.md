# 에이전트 — 웹뷰 빌더 (theseus-view)
> **권장 모델: Sonnet** — 표준 prebuilt shell 복사 + JSON 합본 산출. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**theseus-view (스킬 진행 추적) 만 책임 — `templates/webview/dist/` 의 prebuilt shell 을 `.ShipofTheseus/<프로젝트>/webview/` 로 *복사* + 8 탭 데이터를 단일 `data/webview.json` 으로 emit.** v0.9.40 부터 cold session 안에서 build 하지 않는다 ([`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md)).

**프로젝트 결과 시각화는 페이즈 13 의 interactive-viewer-builder 에 위임** — 본 에이전트는 메타-스킬 대시보드 (페이즈 진행도, 산출물 트리, 게이트 결과) 만 담당.

## 입력
- `.ShipofTheseus/<프로젝트>/` 의 모든 산출물.
- prebuilt shell : [`../templates/webview/dist/`](../templates/webview/dist/).
- (옵션) dev mode src : [`../templates/webview/`](../templates/webview/) 의 `src/`, `server.ts`, `package.json`, `vite.config.ts`.

## 동작

1- **shell 복사** — `cp -r ../templates/webview/dist/* .ShipofTheseus/<proj>/webview/`. 결과:
   ```
   webview/
   ├── index.html
   ├── data/             # ← 비어 있음, 단계 2 에서 채움
   └── assets/
       ├── styles.css
       ├── app.js
       ├── mermaid.min.js
       └── marked.min.js
   ```
2- **데이터 합본 작성** — `webview/data/webview.json` 에 8 탭 데이터를 단일 객체로 emit. 스키마 :
   - `schema_version`, `emit_mode: "prebuilt"`, `project_id`, `final_phase`, `timing`
   - `state` — `state.json` snapshot (status / current_phase / pending_artifacts / ...)
   - `plan.module_graph_mermaid` — `plan/06-plan.md` 의 모듈 의존 flowchart Mermaid 본문
   - `intent` — `intent/{01-intent, 04-questions, 05-decisions}.md` 의 path → 본문 dict
   - `impl` + `quality` — `impl/08-impl-log.md` + `quality/09-quality-gate.md` 본문
   - `tests.unit` — sprints/NN/unit.json 정규화 (sprint / total / pass / fail / failures)
   - `tests.e2e` — sprints/NN/e2e.json 정규화 (sprint / scenarios[name, status, steps, note])
   - `sprints` — sprints/NN/{report, inputs, score}.{md,json} 합본 (sprint / score / outcome / bisect)
   - `runtime.prereq` + `runtime.boot_result` — `intent/04-runtime-prereq.md` + boot_check.py 결과
   상세 스키마 = [`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §3.2.
3- **inline 주입 (옵션)** — file:// 환경 / 단일 파일 배포 시 `webview/index.html` 의 `<script src="./assets/app.js"></script>` *직전* 에 `<script>window.__WEBVIEW__ = <JSON>;</script>` 박음. 이 경우 `data/webview.json` 은 별도 emit 안 해도 됨 (shell 의 우선순위 = window > fetch).
4- **dev mode src 복사 (옵션)** — contributor 가 라이브 폴링/SSE 가 필요한 경우만 :
   ```
   cp ../templates/webview/{package.json,server.ts,tsconfig.json,vite.config.ts} webview/
   cp -r ../templates/webview/src webview/src
   ```
   사용자가 `bun install && bun run dev` 직접 기동.

## 8 탭 강제 (shell 이 prebuilt 이므로 데이터만 책임)

shell `index.html` 에 8 탭이 *이미 박혀* 있다 — 본 에이전트는 데이터 채우기만 책임.

| 탭 | 데이터 키 | 빈 상태 표시 |
| -- | -------- | ----------- |
| 진행 상태 | `state` | "—" + "데이터 미주입" |
| 모듈 구성도 | `plan.module_graph_mermaid` | "데이터 미주입" placeholder |
| 설계 의도 | `intent` (file → markdown) | "데이터 없음" |
| 구현 의도 | `impl` + `quality` | "데이터 없음" |
| 단위 테스트 | `tests.unit` | "데이터 미주입" 행 |
| E2E 테스트 | `tests.e2e` | "데이터 미주입" 행 |
| 스프린트 | `sprints` | "데이터 미주입" 행 + 빈 SVG |
| Runtime | `runtime` | "—" |

**한 탭이라도 데이터 키 누락 = self_lint C-PSR fail.** 산출물 자체가 없으면 빈 list / null 로라도 채워야 한다 ("아직 산출물 없음" 안내가 그려짐).

## Mermaid + Markdown 자동 렌더 (shell 책임)

shell 은 :
- `data.plan.module_graph_mermaid` 를 모듈 구성도 탭의 `<pre class="mermaid">` 에 주입 후 `mermaid.run()`.
- `data.intent` / `data.impl` / `data.quality` 의 markdown 을 `marked.parse()` 로 HTML 변환 + ```mermaid` 코드 펜스 자동 감지 → `<pre class="mermaid">` 로 변환 후 `mermaid.run()`.

본 에이전트는 *원본 markdown / Mermaid 본문 그대로* 데이터에 박는다 — 렌더 변환은 shell 의 책임.

오프라인 동작 강제 — `mermaid.min.js` + `marked.min.js` 가 `assets/` 에 vendored. CDN 링크 금지 ([`../conventions/build-and-config.md`](../conventions/build-and-config.md) §6 의 .gitattributes 와 정합).

## 하드 룰

a- 정적 HTML 만 생성 = fail. shell 복사 + JSON emit 둘 다 의무.
b- "TODO: E2E 탭 차후" 같은 미완성 표시 = fail (항상 생성 룰).
c- shell 본문에 산출물 절대경로 박아넣기 = fail. 데이터는 항상 fetch / inline.
d- 외부 네트워크 의존 (CDN 마크다운 렌더 등) = fail. dist 의 vendored UMD 만.
e- cold session 안에서 `bun run build` 실행 = fail ([`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §1 의 핵심 변경).

## 완료 조건

a- `webview/index.html` + `webview/data/webview.json` (또는 inline 주입) 둘 다 산출.
b- `webview/assets/` 에 mermaid.min.js + marked.min.js + styles.css + app.js 4 파일 존재.
c- 8 탭 데이터 키 모두 존재 (해당 산출물이 없으면 빈 list / null).
d- `webview/index.html` 본문에 `unpkg.com` / `cdn.jsdelivr.net` / `cdnjs.cloudflare` 0 회.
e- self_lint C-PSR 통과.
