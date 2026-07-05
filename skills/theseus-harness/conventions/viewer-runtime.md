---
id: viewer-runtime
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'advisory, §8 동결 — 3 viewer 공통 (auto-refresh) / cold session start/end (lifecycle), 산출 시'
indexed-in: conventions/INDEX.md
---

# Viewer Runtime — frontend 폴링 (auto-refresh) + backend lifecycle (lock + scripts, how-to)

## 한 줄 요약

**3 viewer (lineage / webview / interactive) 의 runtime 두 layer 단일 컨벤션 — 생산 의무는 §8 동결(B2-F3)로 해제, 본 how-to 는 viewer 를 산출하는 경우에 적용.** ① **frontend** — JSON 파일 변경 자동 감지 + 5초 polling + Page Visibility + 수동 button + ETag 304. ② **backend** — `viewer-up/down.{sh,ps1}` + `viewer.lock.json` (PID/port/URL) + cross-platform PID kill (SIGTERM grace → SIGKILL). 두 layer 결합 = "사용자가 *체감* 하는 갱신 + PID 누수 차단" — observability 본질 상승.

## 1. 동기 — sprint-36 변경

cold session 진행 중 viewer 가 떠 있어도 :
- JSON 갱신이 화면에 반영되지 않으면 *static viewer* 와 다를 바 없다 (frontend 결손)
- HTTP server 안 끄면 PID/port 누수 (backend 결손)

사용자 명시 요구 :
> "뷰어 시작용 스크립트와 뷰어 프로세스/포트를 기재한 파일을 명확히 남기며 시작 하도록 설계되어야 하며 이 파일을 기반으로 종료하는 스크립트가 명확히 존재해야 릭이없다"

→ frontend (auto-refresh) + backend (lifecycle) 두 layer 모두 박혀야 본질적 observability.

## 2. Frontend — auto-refresh (3 viewer 공통)

### 2.1 polling 메커니즘 (HTTP server 환경)

```javascript
setInterval(function () {
  if (document.hidden) return;     // 탭 숨김 시 skip
  pollOnce();
}, 5000);

function pollOnce() {
  var headers = {};
  if (lastEtag)     headers['If-None-Match']     = lastEtag;
  if (lastModified) headers['If-Modified-Since'] = lastModified;
  fetch('./<viewer>.json?_t=' + Date.now(), { cache: 'no-store', headers: headers })
    .then(function (r) {
      if (r.status === 304) return;   // 변경 없음
      // ... fetch + render
    });
}
```

핵심:
- **ETag / Last-Modified** — 변경 없을 때 304 반환 → 페이로드 0, 자원 효율.
- **`?_t=<ts>`** — 일부 프록시/브라우저 캐시 우회.
- **`document.hidden` 체크** — 백그라운드 탭에서 폴링 안 함.
- **5초** interval — file 변경 감지 + 자원 균형. 단축 시 부하 / 연장 시 체감 저하.

### 2.2 Page Visibility API

탭 포커스 돌아올 때 즉시 fetch :

```javascript
document.addEventListener('visibilitychange', function () {
  if (!document.hidden && pollTimer) pollOnce();
});
```

5초 polling 보다 *체감 속도* 향상. 탭 전환 직후 화면 = 최신.

### 2.3 manual refresh button

`[data-action="manual-refresh"]` 클릭 → `loadHttp({ skipInline: true })` → 즉시 fetch + render. 폴링 + 수동 둘 다 같은 파이프라인 사용.

### 2.4 status pill UX

3 viewer 모두 헤더에 `data-state` 4 종 :

| state | 표시 | 의미 |
|---|---|---|
| `idle` | 회색 dot | 부팅 직전 |
| `live` | 초록 dot + pulse | polling 활성 |
| `updating` | 파란 dot | 현재 fetch 중 |
| `offline` | 빨간 dot | fetch 실패 → F5 안내 |

manual refresh button 도 동일 state 반영.

### 2.5 file:// 환경 fallback

브라우저가 `file://` 에서 fetch 차단 (CORS) → polling 자동 fail → status='offline'. 사용자에게 "F5 또는 새로고침 button" 안내. inline 주입 패턴 (`window.__LINEAGE__` 등) 시 *초기* 로드는 inline 데이터, 갱신은 manual.

### 2.6 적용 대상

| viewer | data source | binding |
|---|---|---|
| lineage-viewer | `./lineage.json` | `window.__LINEAGE__` |
| webview | `./data/webview.json` | `window.__WEBVIEW__` |
| interactive-viewer | `./dashboard.json` | `window.__DASHBOARD__` |

3 viewer 모두 동일 *폴링 + visibility + manual* 패턴 박힘.

## 3. Backend — lifecycle (start/stop + lock)

### 3.1 산출물 — `<project>/viewer-runtime/`

```
viewer-runtime/
├── viewer-up.sh          # bash / git-bash
├── viewer-up.ps1         # Windows PowerShell
├── viewer-down.sh
├── viewer-down.ps1
├── README.md             # 사용법
├── viewer.lock.json      # PID/port/URL 추적 (실행 시 자동 생성)
└── server.log            # HTTP server stdout/stderr (자동)
```

스크립트 자체는 본 하네스 `templates/viewer-runtime/` 에서 복사 (pre-bootup 시점).

### 3.2 lock file 스키마 — `viewer.lock.json`

```json
{
  "schema_version": "0.9.41",
  "project_root": "/path/to/.ShipofTheseus/<proj>",
  "host": "127.0.0.1",
  "port": 18080,
  "pid": 12345,
  "started_at_iso": "2026-05-09T13:00:00Z",
  "viewers": [
    { "type": "lineage",     "url": "http://127.0.0.1:18080/lineage.html" },
    { "type": "webview",     "url": "http://127.0.0.1:18080/webview/" },
    { "type": "interactive", "url": "http://127.0.0.1:18080/interactive-viewer/" }
  ],
  "log_file": "/path/to/viewer-runtime/server.log"
}
```

### 3.3 수명 주기 (up / status / down)

a- **up** — `viewer-up.{sh,ps1}` → `python viewer_runtime.py up --root <proj>` :
   1. 기존 lock 확인 — alive 시 idempotent (재시작 안 함, URL 만 출력)
   2. 가용 port 탐색 (기본 18080 시작, 점유 시 +1)
   3. `python -m http.server <port> --bind 127.0.0.1 --directory <proj>` 백그라운드 실행
   4. 0.5초 대기 후 PID alive check
   5. lock file 작성 + URL 출력

b- **status** — `python viewer_runtime.py status --root <proj>` :
   - lock 읽기 + PID alive check + URL 덤프 (JSON)
   - stale lock 감지 (lock 있으나 PID 죽음)

c- **down** — `viewer-down.{sh,ps1}` → `python viewer_runtime.py down --root <proj>` :
   1. lock 읽기 → PID 추출
   2. PID 살아있으면 SIGTERM (POSIX) / `taskkill /PID` (Windows)
   3. 1.5초 grace 대기
   4. 여전히 살아있으면 SIGKILL / `taskkill /F /PID`
   5. lock file 삭제

### 3.4 cross-platform 고려

| OS | PID kill | 백그라운드 spawn |
|---|---|---|
| POSIX (Linux/Mac) | `os.kill(pid, SIGTERM)` → `SIGKILL` | `subprocess.Popen(start_new_session=True)` |
| Windows | `taskkill /PID /T` → `/F` | `subprocess.Popen(creationflags=CREATE_NEW_PROCESS_GROUP)` |

`viewer_runtime.py` 가 `os.name` 분기로 자동 선택.

## 4. self_lint

### 4.1 C-VAR (frontend 폴링)

```python
def check_viewer_auto_refresh(skill_root: Path) -> list[str]:
    # 컨벤션 본문 + 3 viewer app.js 폴링 패턴 검증
    for kw in ['polling', 'Page Visibility', 'manual-refresh',
               'If-None-Match', 'If-Modified-Since', '5초', 'status pill']:
        if kw not in conv_body: issues.append(...)
    for viewer, app_path in [
        ('lineage-viewer', 'templates/lineage-viewer/dist/assets/app.js'),
        ('webview',        'templates/webview/dist/assets/app.js'),
        ('interactive-viewer', 'templates/interactive-viewer/dist/assets/app.js'),
    ]:
        for kw in ['POLL_INTERVAL_MS', 'pollOnce', 'visibilitychange',
                   'manual-refresh', 'If-None-Match']:
            if kw not in body: issues.append(...)
```

### 4.2 C-VRL (backend lifecycle)

```python
def check_viewer_runtime_lifecycle(skill_root: Path) -> list[str]:
    # 컨벤션 본문 + scoring/viewer_runtime.py 함수 + templates/viewer-runtime/ 스크립트 검증
    for kw in ['viewer.lock.json', 'PID', 'SIGTERM', 'SIGKILL', 'stale lock']:
        if kw not in conv_body: issues.append(...)
    for fn in ['cmd_up', 'cmd_down', 'cmd_status', '_is_pid_alive',
               '_kill_pid', '_find_free_port']:
        if f'def {fn}' not in viewer_runtime_py: issues.append(...)
    for f in ['viewer-up.sh', 'viewer-up.ps1', 'viewer-down.sh', 'viewer-down.ps1', 'README.md']:
        if not (templates/viewer-runtime / f).exists(): issues.append(...)
```

## 5. 안티 패턴

### 5.1 Frontend 안티 패턴

a- **fetch 캐시 미off** — `cache: 'no-store'` 누락 시 브라우저가 stale 반환. 의무.
b- **ETag 무시** — 매 폴링마다 풀 페이로드. 304 활용 의무.
c- **document.hidden 체크 누락** — 백그라운드 탭이 자원 잡아먹음.
d- **status pill 부재** — 사용자가 polling 활성 여부 알 수 없음.
e- **폴링 5초가 너무 빠름/느림** — 5초 = file 변경 감지 + 자원 균형.

### 5.2 Backend 안티 패턴

f- **viewer-up 만 호출, viewer-down 미호출** — PID 누수. orchestrator 가 cold session 종료/Ctrl+C 시 의무 호출.
g- **lock file 수동 삭제** — 살아있는 PID 추적 불가.
h- **port hardcode** — 18080 점유 시 fail. 자동 +1 탐색 의무.
i- **log file 미수집** — server.log 에 stdout/stderr redirect 의무.

### 5.3 산출물 file-existence 안티 패턴 (sprint-40 PR-C 신규)

j- **`webview/index.md` 마크다운으로 `webview/index.html` 우회** — v0.9.44 g4-v2 회차 직접 사례. phase 12 종료 게이트 (`webview/index.html` + `data/webview.json` + `assets/app.js` 등) file-existence 강제 차단.
k- **`interactive-viewer/` 디렉터리 자체 부재 + phase 13 종료 marker** — G4 강제 unwiring. phase 13 종료 게이트가 `interactive-viewer/{index.html, dashboard.json, assets/app.js}` 강제.
l- **prebuilt shell 복사 단계 skip 후 자체 HTML 작성** — vendored UMD (mermaid.min.js / marked.min.js) 누락 → offline 동작 깨짐. 산출물 검사가 vendored UMD 파일 존재 의무.
m- **dashboard.json widget 0 또는 1 (G4+)** — phase 13 종료 게이트의 G4+ 룰 (widgets ≥ 3, kpi_grid + topology + metric_chart 의무) 위반.

## 5.4 산출물 file-existence 게이트 일람 (sprint-40 PR-C 추가)

| phase | 게이트 위치 | 검사 산출물 | self_lint |
|---|---|---|---|
| 09 entry | [`../phases/09-quality-gates.md`](../phases/09-quality-gates.md) §V8 | webview/ + interactive-viewer/ 디렉터리 외피 | C-VEX |
| 12 exit | [`../phases/12-webview-assembly.md`](../phases/12-webview-assembly.md) §종료 게이트 | webview/{index.html, data/webview.json, assets/*.{js,css}} | C-VEX |
| 13 exit | [`../phases/13-interactive-viewer.md`](../phases/13-interactive-viewer.md) §종료 게이트 | interactive-viewer/{index.html, dashboard.json, assets/app.js} + widgets ≥ 1 (G3+) / ≥ 3 (G4+) | C-VEX |

## 6. 호환성

- [`pre-cold-session-bootup.md`](pre-cold-session-bootup.md) — bootstrap step 5 = 본 lifecycle up. 빈 골격이 polling 으로 자동 갱신.
- [`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) — server 가 서빙하는 산출물 + emit 프로토콜 정합.

## 7. 통합 history (sprint-37 PR-AC)

본 컨벤션은 sprint-37 PR-AC (다이어트) 에서 **`viewer-auto-refresh`** (sprint-36, frontend 폴링) + **`viewer-runtime-lifecycle`** (sprint-36, backend lifecycle) 두 컨벤션을 단일 컨벤션의 §2/§3 두 layer 로 통합. 책임 = "viewer runtime" 단일, 두 layer = frontend (auto-refresh) / backend (lifecycle). 각 layer 의 self_lint 룰 (C-VAR / C-VRL) 은 독립 함수 유지 (infra 파일 검사 분리 — app.js vs viewer_runtime.py). 매핑은 [`MIGRATION.md`](MIGRATION.md) 단일 source.
