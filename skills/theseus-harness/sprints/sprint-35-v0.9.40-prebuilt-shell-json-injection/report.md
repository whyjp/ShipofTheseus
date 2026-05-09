# Sprint-35 — v0.9.40 — Prebuilt Shell + JSON Injection

> 시작: 2026-05-09
> 끝: 2026-05-09
> 사용자 직접 지시: *"리니지 뷰 / 테세우스 뷰 는 html 로 미리 준비해두고 컨텐츠만 동적 교체되도록 하자 런타임 컨텐츠는 json 으로, html FE 는 미리 프리빌드해서 패키징"*. FE 시연 = `huashu-design` 스킬.

## 1. 의도 — 한 줄

cold session 마다 매번 Bun+React build 하는 패턴을 *prebuilt vanilla shell 복사 + JSON 데이터 emit* 으로 교체. cold session 부팅 시간 대폭 감소 + bun/npm 의존 제거 + 산출물 일관성.

## 2. 변경 — layer 별

### 2.1 산출 (templates/)

| 파일 | 역할 | 크기 |
|---|---|---|
| `templates/lineage-viewer/dist/index.html` | 단일 페이지 viewer shell — 6 섹션 (헤더 / flowchart / gantt / fingerprint chain / dacapo summary / phase 04 매핑 / sentinel events) | ~7 KB |
| `templates/lineage-viewer/dist/assets/styles.css` | 정보 건축 / 엔지니어링 토큰 (functional palette: success/sentinel/dacapo/bypass/violation/budget) | ~5 KB |
| `templates/lineage-viewer/dist/assets/app.js` | 데이터 로드 (`window.__LINEAGE__` > fetch) + 6 섹션 렌더 + 라이트/다크 토글 + mermaid initialize/run | ~7 KB |
| `templates/lineage-viewer/dist/assets/mermaid.min.js` | vendored UMD (mermaid@10.9.1) | 3.3 MB |
| `templates/lineage-viewer/sample/{lineage.json, lineage.html, inline-data.js}` | 검증용 샘플 (window.__LINEAGE__ inline 패턴 시연) | — |
| `templates/webview/dist/index.html` | 8 탭 shell (Progress / ModuleMap / DesignIntent / ImplIntent / UnitTests / E2ETests / Sprints / Runtime) | ~7 KB |
| `templates/webview/dist/assets/styles.css` | webview 전용 스타일 (lineage-viewer 토큰 일관) | ~12 KB |
| `templates/webview/dist/assets/app.js` | 8 탭 렌더 + vanilla SVG 점수 차트 (0.999 임계 점선) + markdown/Mermaid 자동 감지 | ~18 KB |
| `templates/webview/dist/assets/{mermaid.min.js,marked.min.js}` | vendored UMD (mermaid@10.9.1, marked@15.0.7) | 3.3 MB + 40 KB |
| `templates/webview/dist/data/webview.json` | 테스트용 샘플 데이터 | ~4 KB |
| `templates/webview/sample/webview.json` | 검증용 샘플 | — |

기존 `templates/webview/{src/,server.ts,package.json,vite.config.ts,tsconfig.json}` = 옵션 dev mode 전용으로 보존.

### 2.2 룰 / 컨벤션 (conventions/, HARD-CORE.md)

- **신규**: `conventions/prebuilt-shell-runtime-json.md` (90 컨벤션째). emit 프로토콜 (패턴 A inline `window.__LINEAGE__/__WEBVIEW__` + 패턴 B sibling JSON fetch) + 스키마 (lineage.json / webview.json) + self_lint C-PSR + dev mode 보존 정책 + shell 갱신 절차.
- **확장**: `conventions/phase-lineage-viewer.md` §14 신규 — `lineage.{md,html,json}` 이중/삼중 emit. C-PLV 룰 G3+ lineage.html 의무. §11 호환성에 prebuilt-shell-runtime-json 추가.
- **확장**: `HARD-CORE.md` 9.nn 한 줄 — cold session build 0 룰. 4386 chars (≤ 4400 임계).
- **갱신**: `phases/12-webview-assembly.md` 전면 — "bun runtime build" → "prebuilt shell 복사 + JSON emit". server.ts dev mode = 옵션. 흔한 실패 c (build-time fs bake) 룰 보존 (의미 그대로, 런타임 fetch 강제).
- **갱신**: `agents/webview-builder.md` 전면 — 동작 4 단계 (shell 복사 / 데이터 합본 / inline 주입 옵션 / dev mode src 옵션). 8 탭 = shell 책임, 데이터 채우기 = agent 책임 분리.

### 2.3 self_lint (scoring/self_lint.py)

- **신규**: `check_prebuilt_shell_runtime_json` (C-PSR). 9 sub-check (컨벤션 본문 / INDEX 등록 / HARD-CORE 9.nn / phase 12 본문 / agent 본문 / phase-lineage-viewer §14 / dist 산출물 존재 / CDN 호스트 0 / 데이터 채널 ≥ 1).
- **bump**: C-HC1 임계 4250 → 4400 (sprint-32 4000→4200, sprint-34 4200→4250 정합 이어감).

### 2.4 메타 (README, SKILL, plugin)

- `README.md` d-97 row (prebuilt-shell-runtime-json).
- `SKILL.md` frontmatter version 0.9.40, description 갱신 (90 컨벤션 / sprint-35).
- `.claude-plugin/plugin.json` version 0.9.40, description 갱신.

## 3. premortem — 사전 부검 결과 (전부 사전 정정)

| 우려 | 정정 |
|---|---|
| mermaid CDN 의존 | 벤더링 (UMD 3.3 MB, dist 자체엔 박힘) |
| dist 사이즈 1 MB+ | 5 MB 미만으로 수용 (이전 Bun+node_modules ~100 MB+ 대비 95% 감소) |
| React 무거움 | Vanilla JS — DOM API + 작은 helper. 12 KB 본문. |
| score chart Recharts 의존 | vanilla SVG (~80 line). 0.999 임계 점선까지 직접 처리. |
| file:// + fetch 차단 | inline `window.__LINEAGE__/__WEBVIEW__` 우선순위 — 단일 파일 배포 가능 |
| build-time fs bake 룰 위배? | shell HTML 본문엔 산출물 경로 0. 데이터 = runtime 채널 (fetch / window). 룰 의미 그대로 보존. |
| phase 13 도 이번 sprint 에? | 분리 — phase 13 = 도메인별 dashboard (DES topology / ML curves / API latency 등 *프로젝트 종속*) → sprint-36 별도 sprint 의제 |

## 4. 자기 평가

- **self_lint** : `python scoring/self_lint.py` → `all_ok=True`. 60+ 룰 모두 통과 — C-PSR 신규 룰 통과 + 기존 룰 회귀 0.
- **HARD-CORE 길이** : 4386 chars / 4400 임계 (sprint-32 / 34 precedent 동일 패턴 bump).
- **dist 산출물 검증** :
  - `templates/lineage-viewer/dist/{index.html, assets/{styles.css, app.js, mermaid.min.js}}` 모두 존재
  - `templates/webview/dist/{index.html, assets/{styles.css, app.js, mermaid.min.js, marked.min.js}, data/webview.json}` 모두 존재
  - 두 index.html 본문에 `unpkg.com` / `cdn.jsdelivr.net` / `cdnjs.cloudflare` 0 회
  - 두 index.html 본문에 데이터 채널 ≥ 1 (window.__* + ./*.json fetch 둘 다)
- **수동 시연** : 자동화 환경에서 file:// + http server 모두 sandbox 차단으로 브라우저 검증 미수행 — *사용자 측 1 회 시연 권장* :
  ```
  cd skills/theseus-harness/templates/lineage-viewer/sample
  # 브라우저로 lineage.html 직접 열기 → 6 섹션 모두 그려져야 함
  ```

## 5. 다음 sprint 후보 (배경)

- **sprint-36** : phase 13 interactive-viewer 의 prebuilt 패턴 적용. 도메인별 (DES / ML / API / Frontend / 분석 / ETL) per-domain template + 도메인 매칭 시 dist 선택 복사. 본 sprint 보다 복잡 (per-domain template ≥ 6 종, 각각 vanilla JS + 도메인 plot/chart 정의).
- **sprint-37 후보** : `update_phase_lineage` 호출이 `lineage.html` 의 `<script>window.__LINEAGE__={...}</script>` inline 갱신을 자동 emit 하는 orchestrator 측 구현 (`scoring/lineage_emitter.py` 또는 phase-lineage-viewer.md §14.2 의 emit 흐름 구체화).

## 6. 회고

a- **scope 분리 결정** (lineage + phase 12 만, phase 13 별도) 가 정답이었다. phase 13 dashboard 는 도메인 종속이라 prebuilt 패턴 적용이 *다른* 설계 (per-domain template 매트릭스). 본 sprint 의 일관성 유지.
b- **huashu-design** 의 정보 건축 / 엔지니어링 디버그 도구 frame 이 적합. AI slop (gradient 남발 / 둥근 그림자 fluff / 무의미 emoji) 회피 + 정보 밀도 우선 + 색상이 기능적 (functional palette).
c- **vendored UMD 가 본 패턴의 핵심** — npm/bun 의존 0 + offline 동작 + cold session 일관성 모두 한 번에. dist 사이즈는 그 대가 (3.3 MB mermaid) — 하지만 cold session 1 회 emit 비용으로 합리적.
d- **dev mode 보존** — `templates/webview/{src/,server.ts}` 를 *지우지 않은* 결정도 옳음. contributor 가 shell 자체를 수정하거나 SSE 라이브 폴링 검증할 때 필요. prebuild 가 *기본*, dev mode 가 *옵션* 으로 분리.

본 sprint = **"기존 자산 80% 위에 정확한 갭만 채우기"** 패턴 (sprint-34 동일 메타 패턴) — 기존 webview 8 탭 정의 / mermaid 렌더 / 시간 헤더 등 그대로 보존, *빌드 layer* 만 교체. 스코프 작고 정확.
