# Phase 12 — theseus-view (prebuilt shell + JSON emit)

## 한 줄 요약
**theseus-view — 메타-스킬 진행 추적 전용 prebuilt HTML viewer + JSON 데이터 emit.** v0.9.40 부터 cold session 은 `templates/webview/dist/` 의 prebuilt shell 을 *복사* + 8 탭 데이터를 단일 `data/webview.json` 으로 emit — bun/npm 의존 0, build step 0. 라이브 폴링/SSE 가 필요한 contributor 시나리오는 *옵션 dev mode* (`bun run dev` + `server.ts`) 로 분리.

본 페이즈는 [`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) 의 **§3.2 webview emit 프로토콜** 을 phase 12 trigger 에 매핑한 본문.

## 책임 범위 — theseus-view (스킬 진행 추적)

본 페이즈(12)의 산출물 **theseus-view** 는 *메타-스킬 대시보드* — 페이즈 진행도, 산출물 트리, 게이트 결과 등 하네스 자체의 실행 상태를 시각화. 책임 범위 :

- 페이즈 진행 상태 (state.json snapshot — cold session 종료 시점)
- 모듈 구성도 DAG / 설계·구현 의도 / 단위·E2E 테스트 탭
- 스프린트 타임라인 + 점수 차트 (SVG, vanilla)
- Runtime 탭 (Q-D9 사전조건 + 게이트 7 부팅 결과)

**프로젝트 결과 시각화 (output observability) 는 본 페이즈의 책임이 아니다 — 페이즈 13 (interactive-viewer) 에 위임.**

## 입력
- `.ShipofTheseus/<프로젝트명>/` 의 모든 산출물.

## 서브에이전트
[`../agents/webview-builder.md`](../agents/webview-builder.md). 시작 스캐폴드 (prebuilt shell) = [`../templates/webview/dist/`](../templates/webview/dist/), dev mode 옵션 src = [`../templates/webview/`](../templates/webview/) (server.ts 등 기존 보존).

## 산출물 (`webview/`)

```
.ShipofTheseus/<proj>/webview/
├── index.html                # ← templates/webview/dist/index.html 복사 (shell)
├── data/
│   └── webview.json          # ← cold session emit (8 탭 합본)
└── assets/
    ├── styles.css            # ← templates/webview/dist/assets/* 복사
    ├── app.js
    ├── mermaid.min.js        # vendored UMD
    └── marked.min.js         # vendored UMD
```

옵션 dev mode (필요 시 contributor 가 추가) :
```
.ShipofTheseus/<proj>/webview/
├── package.json              # ← templates/webview/package.json 복사
├── server.ts                 # ← templates/webview/server.ts 복사 (be4fe Hono)
├── tsconfig.json
├── vite.config.ts
└── src/                      # ← templates/webview/src/ 복사 (React 원본)
```

## 필수 탭 (8 탭, 모두 항상 생성)

| 탭 | 무엇을 보여주는가 | 데이터 source |
| -- | --------------- | ----------- |
| 진행 상태 | `state.json` snapshot — status / current_phase / active_skill / pending_artifacts | `webview.json:state` |
| 모듈 구성도 | 계획의 DAG (TODO 의존, 모듈 경계, 포트) — Mermaid flowchart | `webview.json:plan.module_graph_mermaid` |
| 설계 의도 | `intent/01-intent.md` + `04-questions.md` + `05-decisions.md` 렌더 (markdown + Mermaid 자동 감지) | `webview.json:intent` |
| 구현 의도 | `impl/08-impl-log.md` + `quality/09-quality-gate.md` 렌더 | `webview.json:impl,quality` |
| 단위 테스트 | 모든 스프린트의 단위 결과 (sprint / total / pass / fail / pass-rate / failures) | `webview.json:tests.unit` |
| E2E 테스트 | E2E 시나리오·스텝·상태 (스프린트별) | `webview.json:tests.e2e` |
| 스프린트 | 점수 차트 (vanilla SVG, 0.999 임계 점선) + 타임라인 + 회귀 바이섹트 링크 | `webview.json:sprints` |
| Runtime | Q-D9 사전조건 + 게이트 7 부팅 검증 (boot_check.py 결과) — [`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md) 의 사용자 대면 표면 | `webview.json:runtime` |

## emit 프로토콜 (cold session 측 의무)

[`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §3.2 본문 발췌 :

1. **shell 복사** — `cp -r templates/webview/dist/* <project>/webview/`
2. **데이터 합본 emit** — `webview.json` 을 `<project>/webview/data/` 에 작성. 스키마 = 컨벤션 §3.2 표.
3. **inline 주입 (옵션)** — file:// 환경 / 단일 파일 배포가 필요하면 `webview/index.html` 의 `<script src="./assets/app.js"></script>` *직전* 에 `<script>window.__WEBVIEW__ = <JSON>;</script>` 박음. shell 의 우선순위 = window > fetch.
4. **CDN 링크 / 산출물 절대경로 / build-time fs bake 금지** — self_lint C-PSR 가 검증.

## 시간 정보 표시

shell 헤더가 `webview.json:timing` 의 `started_at_iso` + `duration_seconds` 를 표시. cold session 종료 시점의 *snapshot* 이므로 라이브 폴링 없음 — 라이브가 필요하면 dev mode.

## 실행 (cold session 결과 열람)

```
# 단순 — 브라우저로 직접 열기 (inline 주입 패턴 시)
open .ShipofTheseus/<proj>/webview/index.html

# HTTP server 패턴 (sibling JSON fetch 시)
python -m http.server --directory .ShipofTheseus/<proj>/webview 8000
# → http://localhost:8000
```

## 옵션 dev mode (contributor 친화)

shell 자체를 수정하거나 라이브 폴링이 필요한 경우만 :

```
cd .ShipofTheseus/<proj>/webview
bun install
bun run dev          # be4fe (5174) + vite (5173)
```

dev mode 산출은 *cold session 결과 아님* — production 산출은 prebuilt shell 만이 source of truth ([`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §5).

## 성공 기준

a- `webview/index.html` + `webview/data/webview.json` (또는 inline 주입) 둘 다 산출.
b- 8 탭 데이터 로드 (해당 산출물이 있는 한). 빈 탭은 "데이터 미주입" 안내 — 단 *키 자체는 의무*.
c- 헤더 timing 정보 표시.
d- 단위·E2E 탭이 인터랙티브 — 실패 항목 클릭 시 트레이스 / 노트 표시.
e- self_lint C-PSR + C-EFS 통과.
f- **emit fidelity** — `emit_fidelity.py check --root <proj>` 통과 (8 탭 키 enumeration + 빈값/dummy 금지). [`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §3.3 정합. cold session 이 fail 시 phase 12 exit 차단.

## emit fidelity — 8 탭 의무 키 + 빈값 정책

8 탭은 *모두 webview.json 키 enumeration 의무* (해당 산출이 있든 없든). 빈값 정책 :

| 탭 / 키 | 키 필요 시점 | 빈값 정책 |
|---|---|---|
| `state` | 항상 | object 자체 부재 fail. 진행중이면 `current_phase` 채움, 종료면 `status: complete` |
| `timing` | 항상 | `started_at_iso` 의무. duration 은 종료 후 |
| `plan.module_graph_mermaid` | phase 06 진입 후 (G2+) | G1 = 옵션. G2+ 면 "flowchart" 키워드 의무 |
| `intent` | phase 01 종료 후 | `01-intent.md` 키 의무. 04/05 는 G2+ |
| `impl` | phase 08 진입 후 (G2+) | `08-impl-log.md` 키 의무 |
| `quality` | phase 09 종료 후 | string. dummy filler 금지 |
| `tests.unit` | phase 10 진입 후 (G2+) | sprint 별 record. 빈 list = phase 미도달 |
| `tests.e2e` | phase 10 진입 후 (G3+) | scenario 별 record |
| `sprints` | phase 10 진입 후 (G2+) | sprint 별 score+outcome |
| `runtime.prereq` / `runtime.boot_result` | phase 04-runtime + phase 09 게이트 7 | 모두 객체 의무. boot_exit 정합 |

빈 list / null 은 *그 phase 미도달 시* OK. *진입했는데 빈 list* = fail. shell 의 "데이터 미주입" fallback 은 *키 자체가 부재* 일 때만 표시 — 키 있으면서 빈값 = fail.

## 종료 게이트 — 산출물 파일 존재 강제 (sprint-40 PR-C 신규)

phase 12 *종료 직전* 다음 파일 *디스크 존재* 강제 — fail 시 phase 12 미완 (종료 marker 박지 못함):

| 파일 | 검사 | fail 시 |
|---|---|---|
| `<project>/webview/index.html` | `os.path.exists()` + size > 0 | webview-builder agent 재실행 |
| `<project>/webview/data/webview.json` | `os.path.exists()` + valid JSON parse | 동일 |
| `<project>/webview/assets/app.js` | exists | shell 복사 단계 재실행 |
| `<project>/webview/assets/mermaid.min.js` | exists (vendored UMD) | 동일 |
| `<project>/webview/assets/marked.min.js` | exists (vendored UMD) | 동일 |
| `<project>/webview/assets/styles.css` | exists | 동일 |

**증거 회피 사례.** simulation-bench 001 v0.9.44 g4-v2 회차 — `webview/index.md` 8-tab 마크다운 표 만 박힘, 위 6 파일 *전부 부재*. 그럼에도 phase 12 종료 marker (`webview/index.md` frontmatter `phase: 12-theseus-view`) 자동 진행. **본 게이트 = 그 silent skip 차단.**

### 검사 알고리즘 (orchestrator phase 12 exit)

```python
import json, pathlib

REQUIRED_FILES = [
    'webview/index.html',
    'webview/data/webview.json',
    'webview/assets/app.js',
    'webview/assets/mermaid.min.js',
    'webview/assets/marked.min.js',
    'webview/assets/styles.css',
]

def check_phase12_exit(project_root: pathlib.Path) -> tuple[bool, list[str]]:
    missing = []
    for rel in REQUIRED_FILES:
        path = project_root / rel
        if not path.exists() or path.stat().st_size == 0:
            missing.append(rel)
    # webview.json valid JSON 확인
    wj = project_root / 'webview' / 'data' / 'webview.json'
    if wj.exists():
        try:
            json.loads(wj.read_text())
        except json.JSONDecodeError as e:
            missing.append(f'webview/data/webview.json (invalid JSON: {e})')
    return (len(missing) == 0, missing)
```

### 산출물 — `webview/exit_gate.json`

```json
{
  "schema_version": "0.9.45",
  "checked_at": "2026-05-..T..:..:..+09:00",
  "required_files": [
    {"path": "webview/index.html", "exists": true, "size": 2451},
    {"path": "webview/data/webview.json", "exists": true, "size": 12482, "valid_json": true},
    ...
  ],
  "missing": [],
  "verdict": "pass"
}
```

### self_lint C-VEX (sprint-40 PR-C 신규)

phase 12 종료 marker 박힘 직전 `webview/exit_gate.json` 의 `verdict == "pass"` + `missing == []` 검증. fail 시 phase 12 종료 거부.

### 메모리 정합

- [`feedback_convention_runtime_gap.md`](../../../memory/feedback_convention_runtime_gap.md) — 컨벤션 선언 ≠ 런타임 집행. 본 게이트 = 런타임 집행.
- [`feedback_dual_pressure_json_schema.md`](../../../memory/feedback_dual_pressure_json_schema.md) — 이중 압력 (게이트 + viewer source). 본 게이트가 *파일 존재* 압력, viewer 자체가 *빈 화면* 압력.

## 흔한 실패

a- 정적 HTML 만 출력 + 8 탭 누락 — 인터랙티브 요구 미충족, fail.
b- E2E 탭이 숨겨져 있거나 "차후 구현" 표시 — 항상 생성 룰 위반.
c- shell 본문에 산출물 절대경로 박음 (build-time fs bake) — 런타임 fetch / inline 만 허용. C-PSR 위반.
d- CDN 링크 사용 (`https://unpkg.com/...`) — 오프라인 동작 위반. C-PSR 위반.
e- `bun install && bun run build` 를 cold session 안에서 실행 — prebuilt shell 우회. 본 컨벤션 위반.
f- **(sprint-40 PR-C)** `webview/index.md` 마크다운 표만 박고 `webview/index.html` + viewer 산출 0 — 종료 게이트 차단 대상. silent skip 시 v0.9.44 회차 회귀.

> **공통 안티 패턴** (조기 추상화 / 분산 모놀리스 / 두괄식 누락 / 객관식 라벨 등) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.
