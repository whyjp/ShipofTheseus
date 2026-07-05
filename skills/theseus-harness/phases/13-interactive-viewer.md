# 페이즈 13 — Interactive Viewer (프로젝트 output observability, 옵션 페이즈 — advisory, §8 동결 B2-F3)

## 한 줄 요약
**프로젝트 결과 시각화 + observability 통합 viewer — 도메인별 dashboard 를 emit *가능*.** 생산 의무는 §8 동결로 해제됐다(`frozen.viewer_mandatory` A/B 재승격 대기) — 실행하면 페이즈 08 산출물 + Q-D4 답을 바탕으로 도메인을 식별하고 default plot/dashboard 를 `.ShipofTheseus/<프로젝트>/interactive-viewer/` 에 생성한다. prebuilt shell + schema-driven widget renderer(build 0) — cold session 은 `templates/interactive-viewer/dist/*` 복사 + `dashboard.json` emit 만. [`../conventions/prebuilt-shell-runtime-json.md`](../conventions/prebuilt-shell-runtime-json.md) §3.4 how-to 참조.

## 페이즈 12 와의 분리

| | 페이즈 12 (theseus-view) | 페이즈 13 (interactive-viewer) |
|---|---|---|
| **목적** | 메타-스킬 진행 추적 | 프로젝트 결과 시각화 |
| **무엇을 보여주는가** | 페이즈 진행도, 게이트 결과, 스프린트 점수 | 프로젝트 output observability (도메인별 plot/dashboard) |
| **산출물 위치** | `webview/` | `interactive-viewer/` |
| **담당 에이전트** | `agents/webview-builder.md` | `agents/interactive-viewer-builder.md` |
| **생성 여부** | 옵션(advisory) | 옵션(도메인 매칭 시 권장, advisory) |

## 도메인별 dashboard 카탈로그 (how-to)

도메인을 식별(페이즈 01 의도 + Q-D4 답 기준)하면 아래 매트릭스에서 default dashboard 선택 가능:

| 도메인 | default dashboard |
|---|---|
| DES (시뮬레이션) | scenario throughput bar + bottleneck heatmap + truck cycle gantt |
| 데이터 ETL/스트리밍 | flow diagram + batch progress + record count over time + schema drift |
| ML | metric curves (loss/accuracy) + confusion matrix + feature importance + sample drift |
| 분석 | key metric dashboard + drill-down view + cohort comparison |
| REST API | endpoint latency p50/p95/p99 + error rate + RPS over time + status code distribution |
| Frontend | screen tree + component metric + Lighthouse score + bundle size |
| (도메인 미매칭) | 단순 결과 JSON pretty + 1 summary plot |

각 도메인의 dashboard 는 `dashboard.json`(메타데이터 + plot 정의) + `plots/*.png`(정적 이미지 또는 인터랙티브 HTML)로 구성.

## 산출물 (실행하는 경우)

```
.ShipofTheseus/<프로젝트>/interactive-viewer/
├── index.html          # ← templates/interactive-viewer/dist/index.html 복사 (shell)
├── dashboard.json      # ← cold session emit (도메인 widget array 합본)
├── assets/              # styles.css, app.js(schema-driven renderer), mermaid.min.js, marked.min.js
└── plots/               # 정적 plot (옵션) — raw_artifacts 키로 dashboard.json 에서 참조
```

`index.html` 은 prebuilt — CDN 링크 0, build 0, bun/npm 의존 0.

## dashboard.json schema (how-to, 산출하는 경우)

```json
{
  "schema_version": "0.9.41", "project_id": "...", "current_phase": "...",
  "status": "complete | in_progress | waiting", "domain": "DES | ML | API | ...",
  "matched": true, "skip": false, "skip_reason": null,
  "summary_kpis": [{"label": "Throughput", "value": "850 t/h", "trend": "+5%", "direction": "up"}],
  "scenarios": [{"name": "baseline", "status": "pass", "key_metric": "...", "note": "..."}],
  "widgets": [
    {"id": "topology", "type": "topology", "title": "Mine Layout", "mermaid": "flowchart LR..."},
    {"id": "throughput", "type": "metric_chart", "title": "Scenario Throughput", "kind": "bar", "data": [{"label": "...", "value": 850}]},
    {"id": "bottleneck", "type": "table", "title": "Bottleneck", "columns": ["Edge", "Util %"], "rows": [["pit→hauler", "78.2%"]]},
    {"id": "summary", "type": "markdown", "title": "발견 요약", "body": "## 핵심 발견\n..."}
  ],
  "raw_artifacts": [{"name": "topology.png", "path": "plots/topology.png", "type": "image"}],
  "narrative": "# 결과 해석\n..."
}
```

widget 타입은 도메인 무관 5 종 카탈로그(`kpi_grid`/`topology`/`metric_chart`/`table`/`markdown`) — 도메인 카탈로그는 어느 widget 을 어떤 데이터로 채울지의 매핑일 뿐.

## 자율 결정 (advisory)

- 도메인이 카탈로그에 매칭되면 최소 1 결과 plot emit *권장*.
- 도메인 미매칭이면 본 페이즈 전체를 skip *가능* — skip 시 handoff(페이즈 14) 에 사유 한 줄 기록 *권장*(silent skip 은 지양하되 강제 게이트는 없음).

## 에이전트 (실행하는 경우)

[`../agents/interactive-viewer-builder.md`](../agents/interactive-viewer-builder.md) — 권장 모델: Sonnet. 입력: `intent/01-intent.md`(도메인 키워드) · `impl/08-impl-log.md`(산출물 목록) · Q-D4 답.

## 그레이드별 권장 (강제 아님 — 활성 폭·존치 게이트와 별개)

| 그레이드 | interactive-viewer 권장 동작 |
|---|---|
| G2 | 도메인 매칭 시 최소 1 plot emit (옵션) |
| G3+ | 도메인별 default dashboard 전체 emit (권장) |
| G4+ | dashboard.json widgets 다양화(kpi_grid+topology+metric_chart 권장) — 하한 강제·invoke 강제·종료 게이트는 해제(§8 동결) |
| G5 | 도메인별 dashboard + drill-down + observability 라이브 연동 (권장, 강제 아님) |

## 안티 패턴 (실행하는 경우에 한함)

a- 도메인 미매칭인데 강제로 dashboard 를 만들어 빈 plot 노출 — skip + 기록이 정답.
b- CDN 링크 의존 — 오프라인 동작 불가.
c- `plots/` 하위에 PNG 만 있고 `index.html` 누락 — 뷰어 없음, 관측 불가.
d- **`bun install && bun run build` cold session 실행** — prebuilt shell 우회, dist 복사 + JSON emit 만 사용.
e- dashboard.json widget 카탈로그 외 type 사용 — 5 종만 허용.

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.

## 결과 프로덕트 only — 하네스 메타 emit 금지 (조건부 존치, 산출하는 경우)

본 페이즈를 실행하는 경우 유일한 책임 = **결과 프로덕트**(프로젝트의 시뮬레이션/데이터/모델 출력)의 viewer/dashboard. 하네스 내부 메타(universe 비교, plan-tree, sprint metric, head-to-head 점수)는 페이즈 12 theseus-view 책임 — 본 페이즈 산출물에 박으면 진실성 위반(원칙 2, self_lint C-IV1).

### DES 도메인 (광산/queueing/manufacturing) 의 결과 프로덕트 예시

a- **topology** : 시스템 토폴로지 그래프 시각화 (networkx draw → topology.png).
b- **animation** : event_log 시간축 replay (matplotlib FuncAnimation → animation.gif/mp4).
c- **scenario drill-down** : HTML time slider, 시점별 entity 상태/queue 길이/resource 사용률 표시.
d- 결과 metric chart : throughput bar + bottleneck heatmap.

### 분리 검증 (산출한 경우, self_lint C-IV1)

산출물(`interactive-viewer/{*.png, *.gif, *.html, *.json}`) 본문에 하네스 내부 어휘(`universe-N`/`multiverse`/`plan-tree`/`tournament`/`sprint metric`/`head-to-head sub-score`/`phase 06`/`08-α`/`08-β` 등) 등장 금지 — 그 어휘는 페이즈 12 theseus-view 책임.

## 재승격 경로

`frozen.viewer_mandatory` CheckSpec 의 A/B 실증(편익 확인 시 phase 13 을 다시 의무 phase 로, G4+ 하한·종료 게이트 복원 검토).
