# 페이즈 13 — Interactive Viewer (프로젝트 output observability)

## 한 줄 요약
**프로젝트 결과 시각화 + observability 통합 viewer — 도메인별 dashboard 를 자동 emit 한다.** 페이즈 08 산출물 + Q-D4 답을 바탕으로 도메인을 식별하고, 해당 도메인의 default plot/dashboard 를 `.ShipofTheseus/<프로젝트>/interactive-viewer/` 에 생성한다. **sprint-36 / v0.9.41 — prebuilt shell + schema-driven widget renderer 로 전환** (build 0). cold session 은 `templates/interactive-viewer/dist/*` 복사 + `dashboard.json` emit 만. dashboard.json schema = widget array (kpi_grid / topology / metric_chart / table / markdown). [`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §3.4 정합.

## 페이즈 12 와의 분리

| | 페이즈 12 (theseus-view) | 페이즈 13 (interactive-viewer) |
|---|---|---|
| **목적** | 메타-스킬 진행 추적 | 프로젝트 결과 시각화 |
| **무엇을 보여주는가** | 페이즈 진행도, 게이트 결과, 스프린트 점수 | 프로젝트 output observability (도메인별 plot/dashboard) |
| **산출물 위치** | `webview/` | `interactive-viewer/` |
| **담당 에이전트** | `agents/webview-builder.md` | `agents/interactive-viewer-builder.md` |
| **항상 생성 여부** | 항상 | 도메인 매칭 시 / 미매칭 시 skip 가능 |

## 도메인별 dashboard 카탈로그

도메인을 식별(페이즈 01 의도 + Q-D4 답 기준)하고 아래 매트릭스에서 default dashboard 를 선택한다.

| 도메인 | default dashboard |
|---|---|
| DES (시뮬레이션) | scenario throughput bar + bottleneck heatmap + truck cycle gantt |
| 데이터 ETL/스트리밍 | flow diagram + batch progress + record count over time + schema drift |
| ML | metric curves (loss/accuracy) + confusion matrix + feature importance + sample drift |
| 분석 | key metric dashboard + drill-down view + cohort comparison |
| REST API | endpoint latency p50/p95/p99 + error rate + RPS over time + status code distribution |
| Frontend | screen tree + component metric + Lighthouse score + bundle size |
| (도메인 미매칭) | 단순 결과 JSON pretty + 1 summary plot |

각 도메인의 dashboard 는 `dashboard.json` (메타데이터 + plot 정의) + `plots/*.png` (정적 이미지 또는 인터랙티브 HTML) 로 구성된다.

## 산출물 (sprint-36 v0.9.41 — prebuilt shell)

```
.ShipofTheseus/<프로젝트>/interactive-viewer/
├── index.html          # ← templates/interactive-viewer/dist/index.html 복사 (shell)
├── dashboard.json      # ← cold session emit (도메인 widget array 합본)
├── assets/
│   ├── styles.css
│   ├── app.js          # schema-driven widget renderer + auto-refresh
│   ├── mermaid.min.js  # vendored UMD
│   └── marked.min.js   # vendored UMD
└── plots/              # 정적 plot (옵션) — raw_artifacts 키로 dashboard.json 에서 참조
    ├── *.png
    └── *.html
```

`index.html` 은 *prebuilt* — CDN 링크 0, build 0, bun/npm 의존 0. 복사 + JSON emit 만. 자동 새로고침 (5초 polling) 으로 cold session 진행 시 즉시 반영.

## dashboard.json schema (sprint-36 신규)

```json
{
  "schema_version": "0.9.41",
  "project_id": "...",
  "current_phase": "...",
  "status": "complete | in_progress | waiting",
  "domain": "DES | ML | API | ...",
  "domain_label": "...",
  "matched": true,
  "skip": false,
  "skip_reason": null,
  "summary_kpis": [{"label": "Throughput", "value": "850 t/h", "trend": "+5%", "direction": "up"}],
  "scenarios": [{"name": "baseline", "status": "pass", "key_metric": "...", "note": "..."}],
  "widgets": [
    {"id": "topology", "type": "topology", "title": "Mine Layout", "mermaid": "flowchart LR..."},
    {"id": "throughput", "type": "metric_chart", "title": "Scenario Throughput", "kind": "bar", "data": [{"label": "...", "value": 850}], "x_label": "...", "y_label": "..."},
    {"id": "queue", "type": "metric_chart", "title": "Queue over Time", "kind": "line", "data": [...]},
    {"id": "bottleneck", "type": "table", "title": "Bottleneck", "columns": ["Edge", "Util %"], "rows": [["pit→hauler", "78.2%"]]},
    {"id": "summary", "type": "markdown", "title": "발견 요약", "body": "## 핵심 발견\n..."}
  ],
  "raw_artifacts": [{"name": "topology.png", "path": "plots/topology.png", "type": "image"}],
  "narrative": "# 결과 해석\n..."
}
```

widget 타입은 viewer 가 *모르는 도메인* — DES/ML/API 모두 동일 5 종 (`kpi_grid` / `topology` / `metric_chart` / `table` / `markdown`) 으로 표현. 도메인 카탈로그 = 어느 widget 을 어떤 데이터로 채울지 결정.

## 자율 결정

- Q-D4 (도메인 선택) 답이 **"Skip"** 이더라도, 도메인이 카탈로그에 *매칭되는 경우* **최소 1 결과 plot 자동 emit 의무** — 사용자가 skip 을 선택했다는 것은 개입을 원하지 않는다는 뜻이지, 결과 없음이 아님.
- 도메인이 카탈로그에 완전히 **미매칭** 이면 본 페이즈 자체를 skip 할 수 있다 (HARD-RULE a). 단 산출물에 **"발견 없음 — 도메인 미매칭으로 페이즈 13 skip"** 으로 기록해야 한다.
- 도메인 미매칭에도 프로젝트 결과가 JSON/CSV 등으로 존재하면 "단순 결과 JSON pretty + 1 summary plot" 을 최소 산출한다.

**HARD-RULE a** — 도메인 미매칭 skip 은 허용이지만, skip 시 반드시 handoff 문서(페이즈 14) 에 사유 한 줄 기록 의무.

## 에이전트

[`../agents/interactive-viewer-builder.md`](../agents/interactive-viewer-builder.md) — 권장 모델: Sonnet.

도메인별 dashboard 자동 emit, frontend 코드 작성, plot 생성을 담당한다. 입력 계약:

- 페이즈 01 산출물 (`intent/01-intent.md`) — 프로젝트 의도 + 도메인 키워드
- 페이즈 08 결과 (`impl/08-impl-log.md`) — 실제 산출물 목록
- Q-D4 답 — 도메인 확정값

## 그레이드 매트릭스

| 그레이드 | interactive-viewer 동작 |
|---|---|
| G2 | 도메인 매칭 시 최소 1 plot emit (옵션) |
| G3+ | 도메인별 default dashboard 전체 emit (권고) |
| G5 | 도메인별 dashboard + 인터랙티브 drill-down + observability 메트릭 라이브 연동 (강제) |

## 안티 패턴

a- 도메인 미매칭인데 강제로 dashboard 를 만들어 빈 plot 노출 — HARD-RULE a 위반 (skip + 기록이 정답).
b- Q-D4 "Skip" 을 "산출물 없음" 으로 해석 — 도메인 매칭이 있으면 최소 1 plot 의무.
c- CDN 링크 의존 — 오프라인 동작 불가, fail.
d- `plots/` 하위에 PNG 만 있고 `index.html` 누락 — 뷰어 없음, 관측 불가.
e- `dashboard.json` 에 도메인 매칭 결과 미기록 — 다음 페이즈(14 handoff) 가 참조 불가.
f- **`bun install && bun run build` cold session 실행** (sprint-36) — prebuilt shell 우회. 의무 = dist 복사 + JSON emit 만.
g- **dashboard.json widget 카탈로그 외 type** — 5 종 (kpi_grid/topology/metric_chart/table/markdown) 만 허용. 신규 추가 시 shell + lint 동시 갱신.

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.

## 결과 프로덕트 only — 하네스 메타 emit 금지 (sprint-05-d 정정)

본 페이즈의 *유일한* 책임 = **결과 프로덕트** (프로젝트의 시뮬레이션/데이터/모델 출력) 의 viewer/dashboard. 하네스 내부 메타 (universe 비교, plan-tree, sprint metric, head-to-head 점수) 는 페이즈 12 theseus-view 책임 — **본 페이즈 산출물에 박으면 위반**.

### DES 도메인 (광산/queueing/manufacturing) 의 결과 프로덕트

a- **topology** : 시스템 토폴로지 그래프 시각화 (networkx draw → topology.png). cap-1 edges 강조, 시나리오별 변경 (ramp_closed 시 폐쇄 edge 빨강, bypass 노랑).
b- **animation** : event_log 시간축 replay (matplotlib FuncAnimation → animation.gif/mp4). 시뮬레이션 시간 → 가속 재생, entity (truck) 가 노드/엣지 이동.
c- **scenario drill-down** : HTML time slider, 시점별 entity 상태 / queue 길이 / resource 사용률 표시.
d- **결과 metric chart** : throughput bar (CI 포함) + bottleneck heatmap.

### 분리 검증 (self_lint C-IV1 강제)

본 페이즈 산출물 (`interactive-viewer/{*.png, *.gif, *.html, *.json}`) 본문에 다음 *하네스 내부 어휘* 등장 금지 :
- `universe-N`, `universe_comparison`, `multiverse`, `plan-tree`, `tournament`
- `sprint metric`, `head-to-head sub-score`
- `phase 06`, `08-α`, `08-β` 등 본 하네스 페이즈 내부 명칭

위 어휘는 **페이즈 12 theseus-view** 의 책임 — 그쪽에 박을 것.

### sprint-05-c 회고 — 페이즈 13 첫 시연의 결함

v0.9.3 첫 시연 시 `interactive-viewer/plots/universe_comparison.png` (3 universe sub-score 비교) 가 박혔는데 = *하네스 메타*, 페이즈 13 위반. sprint-05-d 가 본 룰을 self_lint C-IV1 으로 강제 — 회귀 방지.
