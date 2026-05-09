---
id: prebuilt-shell-runtime-json
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'observability HTML emit'
indexed-in: conventions/INDEX.md
---

# Prebuilt Shell + Runtime JSON Injection — observability viewer 표준

## 한 줄 요약

**cold session 은 webview / lineage 의 HTML/JS/CSS shell 을 *빌드하지 않는다*.** 본 하네스가 패키징한 prebuilt shell (`templates/lineage-viewer/dist/`, `templates/webview/dist/`) 을 산출 디렉토리로 *복사* + 데이터 JSON 만 emit. shell 은 `window.__LINEAGE__` / `window.__WEBVIEW__` inline 주입 또는 `fetch('./lineage.json')` / `fetch('./data/webview.json')` fallback 으로 로드. cold session 부팅 시간 대폭 감소 + bun/npm 의존 제거. **다만 *옵션 dev mode* (`bun run dev` + `server.ts`) 는 보존** — 라이브 폴링/SSE 가 필요한 contributor 시나리오용.

## 1. 동기 — sprint-35 / v0.9.40 변경

**v0.9.39 까지의 문제**:

a- 매 cold session 마다 `bun install && bun run build` 의 5~30 초 오버헤드 (cold start + node_modules 캐시 미스).
b- `bun` 미설치 환경에서 phase 12 산출물이 *static HTML 만* 출력되거나 fail (HARD-CORE Layer 3 H1~H5 위반 가능).
c- 산출물 일관성 — 같은 하네스 버전인데 cold session 마다 빌드 결과 hash 가 달라질 가능성 (mermaid/react minor 차이 등).
d- `lineage.md` (Mermaid 코드 펜스만) 은 *마크다운 viewer 가 있어야* 가독 — standalone HTML 이 없어 cold session 결과 공유 / 디버깅 시 항상 별도 도구 (VSCode preview / Github render) 의존.

**v0.9.40 변경**:

a- `templates/lineage-viewer/dist/` + `templates/webview/dist/` 를 본 하네스가 *prebuild 해서 커밋*. cold session 은 dist 복사만.
b- 데이터는 `lineage.json` / `data/webview.json` 으로 emit — shell 이 fetch.
c- bun/npm 의존 = optional dev mode 만. cold session 자체는 외부 런타임 0.
d- `lineage.md` (markdown) + `lineage.html` (standalone) 이중 emit — debug 편의성.

## 2. shell 위치 + 콘텐츠

```
templates/
├── lineage-viewer/
│   ├── dist/                          # ← cold session 이 복사하는 root
│   │   ├── index.html                 # shell (lineage.html 로 rename 후 복사)
│   │   ├── lineage.json               # data (cold session 이 emit, dist 자체엔 없음)
│   │   └── assets/
│   │       ├── styles.css
│   │       ├── app.js
│   │       └── mermaid.min.js         # vendored UMD (CDN 금지)
│   └── sample/                        # 검증용 샘플 데이터 + smoke-test HTML
│       ├── lineage.json
│       ├── inline-data.js
│       └── lineage.html
└── webview/
    ├── dist/                          # ← cold session 이 복사하는 root (`.ShipofTheseus/<proj>/webview/`)
    │   ├── index.html                 # 8 탭 shell
    │   ├── data/
    │   │   └── webview.json           # cold session emit
    │   └── assets/
    │       ├── styles.css
    │       ├── app.js
    │       ├── mermaid.min.js         # vendored UMD
    │       └── marked.min.js          # vendored UMD (markdown 렌더)
    ├── sample/
    │   └── webview.json               # 검증용 샘플
    └── (기존 src/, server.ts, package.json 보존 — dev mode 전용)
```

dist 사이즈 (참고) :
- lineage-viewer/dist : 약 3.4 MB (mermaid 3.3 MB + shell 50 KB)
- webview/dist : 약 3.4 MB (mermaid 3.3 MB + marked 40 KB + shell 60 KB + 데이터 ≤ 100 KB)

## 3. emit 프로토콜 (cold session 측 의무)

### 3.1 lineage (phase exit 트리거 — phase-lineage-viewer 컨벤션 br)

매 phase exit 시 `update_phase_lineage` 호출 + 다음 *2 산출* :

a- `lineage.md` — 기존대로 마크다운 (Mermaid flowchart + gantt + 표) 누적 갱신.
b- `lineage.html` + `lineage.json` + `assets/` — 신규.

`lineage.html` emit 패턴 (택 1):

**패턴 A — 단일 파일 inline 주입** (권장, file:// 환경 지원) :
1. `cp -r templates/lineage-viewer/dist/* <project>/`
2. `<project>/index.html` → `<project>/lineage.html` rename
3. `<script src="./assets/app.js"></script>` *직전* 에 `<script>window.__LINEAGE__ = <JSON>;</script>` inline 주입.
4. (옵션) `lineage.json` 별도 emit 안 해도 됨 — inline 주입이 우선.

**패턴 B — 별도 JSON 파일** (HTTP server 환경) :
1. `cp -r templates/lineage-viewer/dist/* <project>/`
2. `<project>/index.html` → `<project>/lineage.html` rename
3. `<project>/lineage.json` 별도 emit.
4. shell 의 `fetch('./lineage.json')` fallback 작동.

`lineage.json` 스키마 (필수 키) :
```json
{
  "schema_version": "0.9.40",
  "project_id": "...",
  "project_run": "...",
  "started_at_iso": "...",
  "ended_at_iso": "...",
  "duration_seconds": 0,
  "grade": "G4",
  "final_phase": 14,
  "phases_completed": 15,
  "violations_count": 0,
  "dacapo_count": 3,
  "final_outcome": "HANDOFF",
  "mermaid_flowchart": "flowchart TB\n  ...",
  "mermaid_gantt": "gantt\n  title ...\n  ...",
  "fingerprint_chain": [{"phase": "00", "name": "naming", "start": "...", "end": "...", "fingerprint": "sha256:...", "match": true}],
  "dacapo_summary": [{"phase": "06 plan", "rerun_count": 2, "final_winner": "...", "final_score": 0.967, "shadow": 96, "outcome": "...", "budget": 0.89}],
  "phase04_answers": [{"question": "Q-G1", "label": "grade", "answer": "G4", "phase_impact": "..."}],
  "sentinel_events": []
}
```

### 3.2 webview (phase 12 — phase 본문 12-webview-assembly.md)

phase 12 진입 시 :

1. `cp -r templates/webview/dist/* <project>/webview/`
2. `<project>/webview/data/webview.json` emit (8 탭 데이터 합본).
3. (옵션) inline 주입 — 단일 파일 시 `webview/index.html` 의 app.js script 직전에 `<script>window.__WEBVIEW__ = <JSON>;</script>`.
4. dev mode 가 필요한 경우 `templates/webview/src/` + `server.ts` + `package.json` 도 함께 복사 → 사용자가 `bun install && bun run dev` 로 라이브 폴링.

`webview.json` 스키마 (필수 키) :
```json
{
  "schema_version": "0.9.40",
  "emit_mode": "prebuilt",
  "project_id": "...",
  "final_phase": 14,
  "timing": { "started_at_iso": "...", "duration_seconds": 0 },
  "state": { "status": "complete | in_progress | interrupted | user_paused", "current_phase": null, "..." },
  "plan": { "module_graph_mermaid": "flowchart ..." },
  "intent": { "01-intent.md": "...", "04-questions.md": "..." },
  "impl": { "08-impl-log.md": "..." },
  "quality": "...",
  "tests": {
    "unit": [{"sprint": "01", "total": 24, "pass": 24, "fail": 0, "failures": []}],
    "e2e": [{"sprint": "03", "scenarios": [{"name": "...", "status": "pass", "steps": 12, "note": "..."}]}]
  },
  "sprints": [{"sprint": "01", "score": 0.832, "outcome": "PASS", "bisect": null}],
  "runtime": {
    "prereq": { "mode": "real", "secrets_count": 0, "boot_command": "...", "env_hash": "sha256:..." },
    "boot_result": { "boot_exit": 0, "healthz_status": 200, "elapsed_ms": 1240 }
  }
}
```

### 3.3 emit fidelity — 의무 키 + 빈값 sentinel (sprint-35-extra)

shell 복사 + JSON 파일 *생성* 만으로는 부족하다. **각 의무 키가 *실제 데이터로 채워져야* 디버깅 가능한 산출** — 빈 list / null / dummy "데이터 미주입" 문자열은 fail. 본 절이 cold session 측 emit step 의 *완전성* 강제.

**lineage.json 의무 키** (모두 G3+, †=G1/G2 옵션) :

| 키 | 출처 | 빈값 정책 |
|---|---|---|
| `schema_version` | 컨벤션 본문 = "0.9.40" | 비어있을 시 fail |
| `project_id` / `project_run` | phase 00 naming + state.json | 빈 문자열 fail |
| `started_at_iso` / `ended_at_iso` / `duration_seconds` | phase_state.json | null fail (phase 14 진입 후) |
| `grade` | phase 01 frontmatter | "G1"~"G5" 외 fail |
| `final_phase` / `phases_completed` | state.json | 0 fail |
| `violations_count` / `dacapo_count` | aggregate over phases | int 의무 |
| `final_outcome` | {HANDOFF, IN_PROGRESS, BUDGET_BOUND} | enum 외 fail |
| `mermaid_flowchart` | lineage.md `flowchart` 코드 펜스 그대로 | "flowchart" 미포함 fail. G4+ 면 `subgraph` (multiverse / dacapo) ≥ 2 의무 |
| `mermaid_gantt` | lineage.md `gantt` 코드 펜스 그대로 | "gantt" + "dateFormat" 미포함 fail. G4+ 면 `★` ≥ 1 (hotspot) + 동일 start 의 다수 row ≥ 2 (parallel sub-agent) 의무 |
| `fingerprint_chain` | scoring/phase_state.py 의 phase 별 fingerprint | `len = phases_completed` 정합 의무. 0 행 fail |
| `dacapo_summary` | phase 06 + 08 dacapo trace | dacapo 발생 phase 갯수 = `len`. 발생 0 시 빈 list 허용 (G2 minimal) |
| `phase04_answers` | intent/04-questions.md + 04-autonomy.md | Q-G1 + Q-D1~D9 모두 row 의무 (G2+) |
| `sentinel_events` | dacapo-skip-sentinel + log pattern + forgery 감지 | 0 건 시 `[]` 허용 (정상 lineage) |
| `winner` | phase 06/08 final winner (universe + score) | dacapo 발생 시 의무 |

**webview.json 의무 키** (8 탭, [`../phases/12-webview-assembly.md`](../phases/12-webview-assembly.md) 와 정합) :

| 키 | 비어있을 때 fallback | 빈값 정책 |
|---|---|---|
| `state` | "데이터 미주입" 표시 가능, 단 키는 의무 | object 자체 부재 fail |
| `plan.module_graph_mermaid` | flowchart 본문 의무 | "flowchart" 미포함 fail (G2+) |
| `intent` | dict[markdown 파일명 → 본문] | `01-intent.md` 키 의무 |
| `impl` | dict[markdown 파일명 → 본문] | `08-impl-log.md` 키 의무 (phase 08 진입 시) |
| `quality` | string (markdown) | phase 09 진입 시 빈 string fail |
| `tests.unit` / `tests.e2e` | sprint 별 list | phase 10 진입 시 빈 list fail. 회귀 발생 시 `bisect` 키 채워짐 |
| `sprints` | sprint 별 score + outcome | phase 10 진입 시 빈 list fail |
| `runtime.prereq` / `runtime.boot_result` | Q-D9 + 게이트 7 결과 | phase 09 진입 시 부재 fail |

**검증 의사코드** (orchestrator 가 phase 12 exit / phase 14 진입 시 호출) :

```python
def check_emit_fidelity(artifact_dir: Path) -> list[str]:
    errors = []
    lineage = json.loads((artifact_dir / 'lineage.json').read_text())
    grade = lineage.get('grade', 'G4')

    # 1. enum / int 검증
    if lineage.get('final_outcome') not in ['HANDOFF', 'IN_PROGRESS', 'BUDGET_BOUND']:
        errors.append('lineage.json final_outcome enum 외')
    if lineage.get('phases_completed', 0) == 0:
        errors.append('lineage.json phases_completed = 0')

    # 2. mermaid 본문 룰
    gantt = lineage.get('mermaid_gantt', '')
    if 'gantt' not in gantt or 'dateFormat' not in gantt:
        errors.append('lineage.json mermaid_gantt 본문 미작성')
    if grade in ('G4', 'G5'):
        # hotspot ★ ≥ 1 + 병렬 row (동일 start 시각의 task ≥ 2)
        if '★' not in gantt:
            errors.append('lineage.json mermaid_gantt hotspot ★ marker 부재 (G4+)')
        # 동일 시각으로 시작하는 task 가 2 개 이상인지 정규식
        if not _has_parallel_rows(gantt, min_count=2):
            errors.append('lineage.json mermaid_gantt 병렬 sub-agent row 부재 (G4+, phase 08 multiverse 시연)')

    # 3. fingerprint chain 길이 정합
    chain = lineage.get('fingerprint_chain', [])
    if len(chain) != lineage.get('phases_completed', 0):
        errors.append(f'fingerprint_chain 길이 ≠ phases_completed ({len(chain)} vs {lineage.get("phases_completed")})')

    # 4. webview.json 8 탭
    webview = json.loads((artifact_dir / 'webview' / 'data' / 'webview.json').read_text())
    for k in ['state', 'plan', 'intent', 'impl', 'quality', 'tests', 'sprints', 'runtime']:
        if k not in webview:
            errors.append(f'webview.json: 의무 키 {k} 부재')
    return errors
```

**dummy filler 금지** — `"데이터 미주입"` / `"TODO"` / `"-"` 문자열을 진짜 데이터로 박는 것 fail. shell 측이 *키 부재 시* fallback 으로 표시하는 건 OK.

## 4. self_lint C-PSR (Prebuilt Shell Runtime)

```python
def check_prebuilt_shell_runtime(artifact_dir: Path) -> list[str]:
    """sprint-35 / v0.9.40 — prebuilt shell + JSON 산출 검증."""
    errors = []

    # ── lineage HTML ──
    lineage_html = artifact_dir / 'lineage.html'
    lineage_md   = artifact_dir / 'lineage.md'

    if lineage_md.exists() and not lineage_html.exists():
        errors.append('lineage.html 부재 (sprint-35 / v0.9.40 의무 — md/html 이중 emit)')

    if lineage_html.exists():
        text = lineage_html.read_text(encoding='utf-8')
        # 데이터 주입 채널 ≥ 1 (inline window.__LINEAGE__ OR sibling lineage.json)
        has_inline = 'window.__LINEAGE__' in text
        has_json   = (artifact_dir / 'lineage.json').exists()
        if not (has_inline or has_json):
            errors.append('lineage.html 데이터 채널 부재 (window.__LINEAGE__ inline 또는 lineage.json fetch 중 하나 필수)')
        # CDN 금지
        if 'unpkg.com' in text or 'cdn.jsdelivr.net' in text or 'cdnjs.cloudflare' in text:
            errors.append('lineage.html CDN 링크 사용 — 오프라인 동작 위반')
        # build-time fs bake 금지 (script 본문에 산출물 경로 박힘)
        if '.ShipofTheseus/' in text:
            errors.append('lineage.html 본문에 산출물 절대경로 박힘 — build-time fs bake 위반')

    # ── webview ──
    webview_dir = artifact_dir / 'webview'
    if webview_dir.is_dir():
        idx = webview_dir / 'index.html'
        if not idx.exists():
            errors.append('webview/index.html 부재 (prebuilt shell copy 누락)')
        # 데이터 채널
        data_json = webview_dir / 'data' / 'webview.json'
        if idx.exists():
            text = idx.read_text(encoding='utf-8')
            has_inline = 'window.__WEBVIEW__' in text
            if not (has_inline or data_json.exists()):
                errors.append('webview/index.html 데이터 채널 부재 (window.__WEBVIEW__ inline 또는 data/webview.json fetch 중 하나 필수)')
            if 'unpkg.com' in text or 'cdn.jsdelivr.net' in text or 'cdnjs.cloudflare' in text:
                errors.append('webview/index.html CDN 링크 사용')
        # vendored bundle
        for asset in ['assets/mermaid.min.js']:
            if not (webview_dir / asset).exists():
                errors.append(f'webview/{asset} 벤더링 부재')

    return errors
```

`self_lint` 실행 :
- phase 12 exit 시 webview/ 검증
- phase 14 (handoff) 진입 시 lineage 최종 검증

## 5. dev mode 보존 — contributor 친화

prebuild 가 *기본* 이지만, 다음 케이스에서 dev mode 가 필요 :

a- 새 산출물이 들어올 때 마다 *라이브* 갱신 보고 싶은 contributor (intent/05-decisions.md 작성 중 등).
b- shell 자체를 수정 / 디버그 (templates/webview/src/ 의 React 컴포넌트 갱신).
c- SSE 이벤트 스트림 검증.

dev mode 진입 :
```bash
cd <project>/webview
bun install
bun run dev              # be4fe (5174) + vite (5173) 동시 기동
```

dev mode 의 React 빌드는 production 산출이 *아님* — 산출물은 `templates/webview/dist/` 의 prebuilt shell 만이 source of truth.

## 6. shell 갱신 절차 (하네스 contributor 전용)

shell HTML/CSS/JS 또는 mermaid 버전을 올릴 때 :

a- `templates/lineage-viewer/dist/` 또는 `templates/webview/dist/` 직접 수정 (소스가 곧 산출).
b- `templates/{lineage-viewer,webview}/sample/` 의 sample 데이터로 브라우저 검증.
c- self_lint 통과.
d- CHANGELOG 에 shell 버전 변경 기록.

별도 build step 없음 — vanilla JS + vendored UMD 가 곧 dist.

mermaid 등 vendored UMD 업데이트 시 :
```bash
curl -sL -o templates/lineage-viewer/dist/assets/mermaid.min.js https://unpkg.com/mermaid@<NEW>/dist/mermaid.min.js
cp templates/lineage-viewer/dist/assets/mermaid.min.js templates/webview/dist/assets/mermaid.min.js
```

## 7. 안티 패턴

a- **cold session 이 `bun run build` 실행** — 본 컨벤션 위반. dist 복사만 의무.
b- **shell 본문에 산출물 절대경로 박음** — build-time fs bake. 데이터는 항상 fetch / inline.
c- **CDN 링크 (unpkg.com 등) 사용** — 오프라인 동작 위반.
d- **`lineage.md` 만 emit, `lineage.html` 누락** — debug 편의성 위반 (sprint-35 의무).
e- **dev mode 산출물을 cold session 결과로 출하** — `templates/webview/dist/` 가 단일 source.

## 8. 호환성

- [`phase-lineage-viewer.md`](phase-lineage-viewer.md) (br) — `lineage.{md,html}` 이중 emit 의무는 본 컨벤션 patterns A/B 채택.
- phase 12 [`../phases/12-webview-assembly.md`](../phases/12-webview-assembly.md) — 본 컨벤션이 *기본 emit 경로*. server.ts dev mode 는 옵션.
- [`build-and-config.md`](build-and-config.md) — `.gitattributes` text=auto / vendored bundle commit 룰 정합.
- [`indexing.md`](indexing.md) — INDEX.md 등록.

## 9. 케이스 종속이 아닌 이유

a- 모든 도메인의 cold session 이 동일 emit 프로토콜 사용 — 도메인 X.
b- 데이터 스키마 (lineage.json / webview.json) 가 *하네스 자체* 의 phase 흐름 + 산출물에 매핑 — 프로젝트 내용 X.
c- prebuild + JSON injection 패턴은 SSR 의 표준 escape hatch — 어떤 일반 도구든 채택 가능.
