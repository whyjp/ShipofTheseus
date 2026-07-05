# Phase 12 — theseus-view (prebuilt shell + JSON emit, 옵션 페이즈 — advisory, §8 동결 B2-F3)

## 한 줄 요약
**theseus-view — 메타-스킬 진행 추적용 prebuilt HTML viewer + JSON 데이터 emit.** 생산 의무는 §8 동결로 해제됐다(편익 미실증, `frozen.viewer_mandatory` A/B 재승격 대기) — 실행 *가능*하며, 실행하면 `templates/webview/dist/` prebuilt shell 복사 + 탭 데이터를 단일 `data/webview.json` 으로 emit(bun/npm 의존 0, build step 0). 라이브 폴링이 필요한 contributor 시나리오는 옵션 dev mode(`bun run dev`).

본 페이즈는 [`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) 의 prebuilt shell + `data/webview.json` emit 프로토콜(§3.2)을 참조하는 how-to 다.

## 책임 범위 (실행하는 경우)

theseus-view = 메타-스킬 대시보드 — 페이즈 진행도, 산출물 트리, 게이트 결과 시각화. 프로젝트 결과 시각화(output observability)는 phase 13(interactive-viewer)의 책임.

## 입력
- `.ShipofTheseus/<프로젝트명>/` 의 모든 산출물.

## 서브에이전트 (실행하는 경우)
[`../agents/webview-builder.md`](../agents/webview-builder.md). prebuilt shell = [`../templates/webview/dist/`](../templates/webview/dist/), dev mode 옵션 src = [`../templates/webview/`](../templates/webview/).

## 산출물 (`webview/`, 실행하는 경우)

```
.ShipofTheseus/<proj>/webview/
├── index.html                # ← templates/webview/dist/index.html 복사 (shell)
├── data/
│   └── webview.json          # ← cold session emit
└── assets/                   # styles.css, app.js, mermaid.min.js, marked.min.js (vendored)
```

## 탭 카탈로그 (how-to — 산출 가능, 강제 아님)

| 탭 | 무엇을 보여주는가 | 데이터 source |
| -- | --------------- | ----------- |
| 진행 상태 | `state.json` snapshot | `webview.json:state` |
| 모듈 구성도 | 계획 DAG (Mermaid flowchart) | `webview.json:plan.module_graph_mermaid` |
| 설계 의도 | intent 문서 렌더 | `webview.json:intent` |
| 구현 의도 | impl/quality 문서 렌더 | `webview.json:impl,quality` |
| 단위 테스트 | 스프린트별 단위 결과 | `webview.json:tests.unit` |
| E2E 테스트 | 시나리오·스텝·상태 | `webview.json:tests.e2e` |
| 스프린트 | 점수 차트 + 타임라인 | `webview.json:sprints` |
| Runtime | Q-D9 사전조건 + 게이트 7 부팅 검증 — [`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md) | `webview.json:runtime` |

산출하는 경우, 8 탭 모두 키 enumeration *권장*(값 없으면 "데이터 미주입" fallback) — 강제 게이트는 해제됐다.

## emit 프로토콜 (실행하는 경우, how-to)

[`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §3.2 요약:

1. **shell 복사** — `cp -r templates/webview/dist/* <project>/webview/`
2. **데이터 emit** — `webview.json` 을 `<project>/webview/data/` 에 작성.
3. **inline 주입(옵션)** — file:// 배포 시 `<script>window.__WEBVIEW__ = <JSON>;</script>` 주입 가능.
4. CDN 링크 / 절대경로 build-time bake 는 지양(C-PSR 검증 대상).

## 키 정직성 (emit 하는 경우, 조건부 진실성 — 9.oo)

**산출물을 실제로 emit 하는 경우에 한해** 빈 탭에 dummy filler("TODO" 등)를 채워 넣지 않는다 — 값 없으면 null/empty 그대로, 있는 척하지 않는다. `emit_fidelity.py check --root <proj>` 로 검증 가능(옵션). 이 진실성 규칙은 *산출 의무* 가 아니라 *산출한 결과가 거짓말하지 않게* 하는 규칙이다.

## 실행 (cold session 결과 열람, 산출한 경우)

```
open .ShipofTheseus/<proj>/webview/index.html
# 또는 HTTP server: python -m http.server --directory .ShipofTheseus/<proj>/webview 8000
```

## 옵션 dev mode (contributor 친화)

```
cd .ShipofTheseus/<proj>/webview && bun install && bun run dev   # be4fe (5174) + vite (5173)
```

dev mode 산출은 cold session 결과가 아니다 — production 산출은 prebuilt shell.

## 흔한 실패 (실행하는 경우에 한함)

a- shell 본문에 산출물 절대경로 박음(build-time fs bake) — 런타임 fetch/inline 만 허용.
b- CDN 링크 사용 — 오프라인 동작 위반.
c- 빈 탭에 dummy filler — 진실성 위반(위 절 참조).

> **공통 안티 패턴** (조기 추상화 / 분산 모놀리스 / 두괄식 누락 / 객관식 라벨 등) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.

## 재승격 경로

`frozen.viewer_mandatory` CheckSpec 의 A/B 실증(편익 확인 시 phase 12 를 다시 의무 phase 로).
