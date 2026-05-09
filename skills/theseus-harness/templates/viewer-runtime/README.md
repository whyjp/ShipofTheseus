# viewer-runtime — sprint-36 viewer 라이프사이클

본 디렉토리의 스크립트는 cold session 의 prebuilt viewer 들 (lineage / webview / interactive) 을 단일 HTTP server 로 띄우고 누수 없이 정리한다.

## 산출 파일

`.ShipofTheseus/<proj>/viewer-runtime/` 에 다음이 박힘 (orchestrator 가 pre-bootup 시 본 디렉토리 복사) :

```
viewer-runtime/
├── viewer-up.sh        # bash / zsh / git-bash
├── viewer-up.ps1       # Windows PowerShell
├── viewer-down.sh
├── viewer-down.ps1
├── viewer.lock.json    # PID/port/URL 추적 (실행 시 자동 생성)
└── server.log          # HTTP server stdout/stderr (자동)
```

## 사용

```bash
# 시작
bash viewer-runtime/viewer-up.sh             # bash
powershell -File viewer-runtime\viewer-up.ps1 # Windows PowerShell

# 종료
bash viewer-runtime/viewer-down.sh
powershell -File viewer-runtime\viewer-down.ps1
```

`THESEUS_HARNESS_ROOT` 환경변수가 있으면 그 위치의 `scoring/viewer_runtime.py` 사용. 없으면 상대 경로 자동 탐색 (`../../skills/theseus-harness` 등 3 단계).

## 라이프사이클 — 누수 방지

a- **시작**: `viewer-up` → Python `http.server` 백그라운드 실행 → PID/port 를 `viewer.lock.json` 에 박음.
b- **상태**: `python <harness>/scoring/viewer_runtime.py status --root <project>` 로 alive check.
c- **종료**: `viewer-down` → lock 의 PID 에 SIGTERM, 1.5초 grace 후 SIGKILL → lock 정리.

비정상 종료 (Ctrl+C / 시스템 리부트 등) 로 lock 만 남고 PID 죽었어도 `viewer-down` 이 stale lock 자동 정리. orchestrator 가 cold session 시작 시 `up` 호출, 종료 시 `down` 호출 의무.

## URL

기본 host:port = `127.0.0.1:18080` (점유 시 자동 +1). 같은 server 가 모든 viewer 서빙 :

- `http://127.0.0.1:18080/lineage.html`
- `http://127.0.0.1:18080/webview/`
- `http://127.0.0.1:18080/interactive-viewer/`

## 안티 패턴

a- **`viewer-up` 만 호출하고 `viewer-down` 미호출** — PID 누수. orchestrator 가 cold session 종료 또는 ctrl+C 시 항상 down 호출.
b- **lock file 수동 삭제** — 살아있는 PID 추적 불가. 종료 못 하면 OS 도구로 `kill <pid>`.
c- **동일 root 에 두 번 up** — 첫 PID alive 시 idempotent (재시작 안 함). lock 의 URL 만 다시 출력.
