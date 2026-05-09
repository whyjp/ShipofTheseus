#!/usr/bin/env python3
"""
viewer 라이프사이클 — start / stop / status (sprint-36 v0.9.41 신규).

cold session 의 prebuilt viewer 들 (lineage / webview / interactive) 을 단일 HTTP server
로 띄우고, PID + port 를 lock file 에 박아 종료 시 누수 없이 정리.

설계:
- 단일 HTTP server (Python `http.server`) 가 `<project root>` 에 root → 모든 viewer 를
  하나의 포트로 서빙. 첫 동작 cost 최소화 + URL 명확화.
- lock file `<project>/viewer-runtime/viewer.lock.json` 에 PID/port/URL 박힘.
- cross-platform — POSIX `os.kill(SIGTERM)` + Windows `taskkill /F /PID` fallback.
- pre-cold-session bootup 시점에 호출 — phase 00 enter 직전. cold session 종료 시 down.

명령:
    viewer_runtime.py up     --root <project_dir> [--port 18080] [--host 127.0.0.1]
    viewer_runtime.py down   --root <project_dir>
    viewer_runtime.py status --root <project_dir>
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


SCHEMA_VERSION = "0.9.41"
LOCK_DIRNAME = "viewer-runtime"
LOCK_FILENAME = "viewer.lock.json"
LOG_FILENAME = "server.log"
DEFAULT_PORT = 18080
DEFAULT_HOST = "127.0.0.1"

# 어떤 viewer 가 어디 산출되는지 — pre-bootup 시 모두 빈 골격으로 박힘.
VIEWERS = [
    {"type": "lineage",     "rel_url": "lineage.html"},
    {"type": "webview",     "rel_url": "webview/"},
    {"type": "interactive", "rel_url": "interactive-viewer/"},
]


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _lock_path(root: Path) -> Path:
    return root / LOCK_DIRNAME / LOCK_FILENAME


def _log_path(root: Path) -> Path:
    return root / LOCK_DIRNAME / LOG_FILENAME


def _is_pid_alive(pid: int) -> bool:
    """PID 가 살아있는지 — POSIX + Windows 둘 다 동작."""
    try:
        if os.name == "nt":
            # Windows — tasklist 결과 파싱
            out = subprocess.check_output(
                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                stderr=subprocess.DEVNULL, encoding="utf-8", errors="replace",
            )
            return str(pid) in out
        else:
            os.kill(pid, 0)
            return True
    except Exception:
        return False


def _kill_pid(pid: int, force: bool = False) -> bool:
    """PID 종료. 성공 시 True."""
    try:
        if os.name == "nt":
            cmd = ["taskkill", "/PID", str(pid)]
            if force:
                cmd.append("/F")
            cmd.append("/T")  # 자식 프로세스도 같이
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            os.kill(pid, signal.SIGTERM if not force else signal.SIGKILL)
        return True
    except Exception as e:
        print(f"[viewer_runtime] kill PID {pid} fail: {e}", file=sys.stderr)
        return False


def _port_available(host: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        s.bind((host, port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def _find_free_port(host: str, start: int, max_tries: int = 20) -> int:
    for i in range(max_tries):
        p = start + i
        if _port_available(host, p):
            return p
    raise RuntimeError(f"포트 {start}~{start + max_tries - 1} 모두 점유됨")


# ─────────────────────────────────────────────────────────────────────
# up / down / status
# ─────────────────────────────────────────────────────────────────────


def cmd_up(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"root 디렉토리 부재: {root}", file=sys.stderr)
        return 1

    runtime_dir = root / LOCK_DIRNAME
    runtime_dir.mkdir(parents=True, exist_ok=True)

    lock = _lock_path(root)
    if lock.exists():
        try:
            data = json.loads(lock.read_text(encoding="utf-8"))
            if data.get("pid") and _is_pid_alive(data["pid"]):
                print(f"[viewer_runtime] 이미 실행 중 — PID {data['pid']} on port {data.get('port')}", file=sys.stderr)
                print(f"  URL: http://{data.get('host', DEFAULT_HOST)}:{data.get('port')}/", file=sys.stderr)
                return 0
        except Exception:
            pass  # stale lock — overwrite

    host = args.host or DEFAULT_HOST
    port = args.port or _find_free_port(host, DEFAULT_PORT)

    # background HTTP server
    log_file = _log_path(root)
    log_fh = open(log_file, "a", encoding="utf-8")
    log_fh.write(f"\n--- viewer_runtime up at {_utcnow_iso()} ---\n")
    log_fh.flush()

    cmd = [sys.executable, "-m", "http.server", str(port), "--bind", host, "--directory", str(root)]
    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP") else 0

    proc = subprocess.Popen(
        cmd,
        stdout=log_fh, stderr=log_fh,
        creationflags=creationflags if os.name == "nt" else 0,
        start_new_session=(os.name != "nt"),
        cwd=str(root),
    )

    # 부팅 확인 — 0.5초 대기 후 alive check
    time.sleep(0.5)
    if not _is_pid_alive(proc.pid):
        log_fh.close()
        try:
            tail = log_file.read_text(encoding="utf-8", errors="replace").splitlines()[-10:]
            print(f"[viewer_runtime] HTTP server 시작 실패. log tail:\n  " + "\n  ".join(tail), file=sys.stderr)
        except Exception:
            print(f"[viewer_runtime] HTTP server 시작 실패", file=sys.stderr)
        return 1

    lock_data = {
        "schema_version": SCHEMA_VERSION,
        "project_root": str(root),
        "host": host,
        "port": port,
        "pid": proc.pid,
        "started_at_iso": _utcnow_iso(),
        "viewers": [
            {
                "type": v["type"],
                "url": f"http://{host}:{port}/{v['rel_url']}",
            }
            for v in VIEWERS
        ],
        "log_file": str(log_file),
    }
    lock.write_text(json.dumps(lock_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[viewer_runtime] up — PID {proc.pid}, port {port}", file=sys.stderr)
    for v in lock_data["viewers"]:
        print(f"  {v['type']:>11s} → {v['url']}", file=sys.stderr)
    print(f"  lock: {lock}", file=sys.stderr)
    print(f"  log:  {log_file}", file=sys.stderr)
    return 0


def cmd_down(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    lock = _lock_path(root)
    if not lock.exists():
        print(f"[viewer_runtime] lock file 부재: {lock} (이미 정리됨)", file=sys.stderr)
        return 0

    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[viewer_runtime] lock 파싱 실패 — 강제 삭제: {e}", file=sys.stderr)
        lock.unlink(missing_ok=True)
        return 1

    pid = data.get("pid")
    if pid is None:
        print(f"[viewer_runtime] lock 에 pid 부재 — 정리만", file=sys.stderr)
        lock.unlink(missing_ok=True)
        return 0

    if not _is_pid_alive(pid):
        print(f"[viewer_runtime] PID {pid} 이미 종료됨 — lock 정리만", file=sys.stderr)
        lock.unlink(missing_ok=True)
        return 0

    print(f"[viewer_runtime] PID {pid} 종료 시도 (SIGTERM)...", file=sys.stderr)
    _kill_pid(pid, force=False)

    # grace period 1.5초
    for _ in range(15):
        if not _is_pid_alive(pid):
            break
        time.sleep(0.1)

    if _is_pid_alive(pid):
        print(f"[viewer_runtime] grace 만료 — SIGKILL", file=sys.stderr)
        _kill_pid(pid, force=True)
        time.sleep(0.3)

    lock.unlink(missing_ok=True)
    if _is_pid_alive(pid):
        print(f"[viewer_runtime] PID {pid} 종료 실패 — 수동 확인 필요", file=sys.stderr)
        return 1

    print(f"[viewer_runtime] down — PID {pid} 종료, lock 정리", file=sys.stderr)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    lock = _lock_path(root)
    if not lock.exists():
        print(json.dumps({"running": False, "reason": "lock 부재"}, ensure_ascii=False, indent=2))
        return 1

    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except Exception as e:
        print(json.dumps({"running": False, "reason": f"lock 파싱 실패: {e}"}, ensure_ascii=False, indent=2))
        return 1

    pid = data.get("pid")
    alive = _is_pid_alive(pid) if pid else False
    out = {
        "running": alive,
        "stale_lock": (pid is not None and not alive),
        "pid": pid,
        "port": data.get("port"),
        "host": data.get("host"),
        "started_at_iso": data.get("started_at_iso"),
        "viewers": data.get("viewers", []),
        "lock_path": str(lock),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if alive else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="viewer 라이프사이클 — start/stop/status (sprint-36)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_up = sub.add_parser("up", help="HTTP server 시작 + lock 박음")
    p_up.add_argument("--root", required=True, help=".ShipofTheseus/<proj> 디렉토리")
    p_up.add_argument("--port", type=int, default=None, help="port (기본 18080, 점유 시 자동 +1)")
    p_up.add_argument("--host", default=None, help="host (기본 127.0.0.1)")
    p_up.set_defaults(func=cmd_up)

    p_down = sub.add_parser("down", help="lock 의 PID 종료 + lock 정리")
    p_down.add_argument("--root", required=True)
    p_down.set_defaults(func=cmd_down)

    p_status = sub.add_parser("status", help="lock + PID alive check + URL 덤프")
    p_status.add_argument("--root", required=True)
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
