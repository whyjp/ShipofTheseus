---
id: viewer-runtime-lifecycle
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'cold session start/end'
indexed-in: conventions/INDEX.md
---

# Viewer Runtime Lifecycle — start/stop script + lock file (PID/port 추적)

## 한 줄 요약

**HTTP server 의 PID + port + URL 을 lock file 에 박아 누수 없이 시작/종료.** `viewer-up.{sh,ps1}` 시작 → `viewer.lock.json` 자동 생성 → `viewer-down.{sh,ps1}` 가 lock 의 PID 에 SIGTERM (1.5초 grace) → SIGKILL → lock 정리. cross-platform (POSIX + Windows). cold session 비정상 종료에도 stale lock 자동 감지.

## 1. 동기 — sprint-36 변경

`pre-cold-session-bootup` 가 phase 00 *이전* HTTP server 띄움 → cold session 끝나도 server 안 끄면 PID 누수. 본 컨벤션이 lifecycle 명확화.

사용자 명시 요구 (sprint-36 v0.9.41) :
> "뷰어 시작용 스크립트와 뷰어 프로세스/포트를 기재한 파일을 명확히 남기며 시작 하도록 설계되어야 하며 이 파일을 기반으로 종료하는 스크립트가 명확히 존재해야 릭이없다"

## 2. 산출물 — `<project>/viewer-runtime/`

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

## 3. lock file 스키마

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

## 4. 수명 주기

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

## 5. cross-platform 고려

| OS | PID kill | 백그라운드 spawn |
|---|---|---|
| POSIX (Linux/Mac) | `os.kill(pid, SIGTERM)` → `SIGKILL` | `subprocess.Popen(start_new_session=True)` |
| Windows | `taskkill /PID /T` → `/F` | `subprocess.Popen(creationflags=CREATE_NEW_PROCESS_GROUP)` |

`viewer_runtime.py` 가 `os.name` 분기로 자동 선택.

## 6. self_lint C-VRL

```python
def check_viewer_runtime_lifecycle(skill_root: Path) -> list[str]:
    issues = []
    cli = skill_root / 'scoring' / 'viewer_runtime.py'
    if not cli.exists():
        return ['scoring/viewer_runtime.py 부재 (sprint-36)']
    body = _read(cli)
    for fn in ['cmd_up', 'cmd_down', 'cmd_status', '_is_pid_alive', '_kill_pid', '_find_free_port']:
        if f'def {fn}' not in body:
            issues.append(f'viewer_runtime.py 함수 {fn} 부재')
    rt = skill_root / 'templates' / 'viewer-runtime'
    for f in ['viewer-up.sh', 'viewer-up.ps1', 'viewer-down.sh', 'viewer-down.ps1', 'README.md']:
        if not (rt / f).exists():
            issues.append(f'templates/viewer-runtime/{f} 부재')
    return issues
```

## 7. 안티 패턴

a- **viewer-up 만 호출, viewer-down 미호출** — PID 누수. orchestrator 가 cold session 종료/Ctrl+C 시 의무 호출.
b- **lock file 수동 삭제** — 살아있는 PID 추적 불가. 종료 안 되면 OS 도구 사용.
c- **port hardcode** — 18080 점유 시 fail. 자동 +1 탐색 의무.
d- **log file 미수집** — 디버깅 불가. server.log 에 stdout/stderr redirect 의무.

## 8. 호환성

- [`pre-cold-session-bootup.md`](pre-cold-session-bootup.md) — bootstrap step 5 = 본 lifecycle up.
- [`viewer-auto-refresh.md`](viewer-auto-refresh.md) — HTTP server 가 polling 의 전제.
- [`prebuilt-shell-runtime-json.md`](prebuilt-shell-runtime-json.md) — server 가 서빙하는 산출물.
