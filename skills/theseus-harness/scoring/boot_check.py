#!/usr/bin/env python3
"""
Boot check — 페이즈 09 게이트 7 (env-satisfied + 실 실행 1회) 자동화 헬퍼.

[`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md) §부팅 검증
알고리즘 구현:

  - boot_command 실행 → 5 초 (default) 내 healthz 200 OK → SIGTERM
  - boot_exit 0 + healthz_status 200 둘 다이면 게이트 7 통과
  - timeout 또는 non-200 → fail (사유 산출)

Q-D9 답별 매핑:
  - 답 1·2 (real / template): 실 boot_command 사용 (env 로드)
  - 답 3 (mock):              BOOT_MODE=mock 환경변수 추가 후 boot_command
  - 답 4 (none):              부팅 무필요 — pass (no runtime)

본 모듈은 *로컬 부팅* 만 검증 — 컨테이너 / k8s 부팅은 별도 (build-and-config.md).

사용법:
    boot_check.py run --boot-command "npm start" --healthz http://localhost:3000/healthz
    boot_check.py run --runtime-prereq <path-to-intent/04-runtime-prereq.md>
"""

from __future__ import annotations

import argparse
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_TIMEOUT_S = 30.0
DEFAULT_HEALTHZ_POLL_INTERVAL_S = 0.5
DEFAULT_HEALTHZ_FIRST_DELAY_S = 0.2


@dataclass
class BootResult:
    boot_command: str
    mode: str
    healthz_url: str | None
    boot_exit: int | str           # int = exit code, str = "timeout" / "skipped" / "no-runtime"
    healthz_status: int | str      # int = HTTP status, str = "timeout" / "error: <msg>" / "skipped"
    elapsed_s: float
    pass_: bool


def _http_get_status(url: str, timeout_s: float = 2.0) -> int | str:
    """healthz GET — 200 = OK, 그 외 status 코드 또는 'error: ...' 반환."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        return f"error: {type(e).__name__}"


def _poll_healthz(url: str, deadline: float, interval: float) -> int | str:
    """healthz 가 200 반환할 때까지 polling (deadline 까지)."""
    last_status: int | str = "error: not yet started"
    while time.monotonic() < deadline:
        status = _http_get_status(url, timeout_s=2.0)
        if status == 200:
            return 200
        last_status = status
        time.sleep(interval)
    return last_status if isinstance(last_status, str) else last_status


def _terminate(proc: subprocess.Popen, grace_s: float = 3.0) -> int | str:
    """SIGTERM → grace 후에도 살아있으면 SIGKILL. 종료 코드 반환."""
    if proc.poll() is not None:
        return proc.returncode
    try:
        if os.name == "nt":
            # Windows 는 SIGTERM 유사 — taskkill 강제
            proc.terminate()
        else:
            proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=grace_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        try:
            proc.wait(timeout=grace_s)
        except subprocess.TimeoutExpired:
            return "kill-timeout"
    return proc.returncode if proc.returncode is not None else "unknown"


def run_boot_check(
    boot_command: str,
    healthz_url: str | None,
    mode: str = "real",
    timeout_s: float = DEFAULT_TIMEOUT_S,
    extra_env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> BootResult:
    """boot_command 실행 + healthz polling + SIGTERM. BootResult 반환."""
    start = time.monotonic()

    if mode == "none":
        return BootResult(
            boot_command=boot_command, mode=mode, healthz_url=healthz_url,
            boot_exit="no-runtime", healthz_status="skipped",
            elapsed_s=0.0, pass_=True,
        )

    # 환경 준비
    env = os.environ.copy()
    if mode == "mock":
        env["BOOT_MODE"] = "mock"
    if extra_env:
        env.update(extra_env)

    # boot_command 실행
    try:
        proc = subprocess.Popen(
            boot_command,
            shell=True,
            env=env,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, OSError) as e:
        return BootResult(
            boot_command=boot_command, mode=mode, healthz_url=healthz_url,
            boot_exit=f"spawn-error: {e}", healthz_status="skipped",
            elapsed_s=time.monotonic() - start, pass_=False,
        )

    # healthz polling (있을 때만)
    if healthz_url:
        time.sleep(DEFAULT_HEALTHZ_FIRST_DELAY_S)
        deadline = start + timeout_s
        healthz_status: int | str = _poll_healthz(
            healthz_url, deadline=deadline, interval=DEFAULT_HEALTHZ_POLL_INTERVAL_S,
        )
    else:
        healthz_status = "skipped"
        # boot_command 가 빨리 끝나면 (예: `node --version`) exit 코드 그대로 받음
        try:
            proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            healthz_status = "timeout"

    # 정리 — SIGTERM
    boot_exit = _terminate(proc, grace_s=3.0)
    elapsed = time.monotonic() - start

    pass_ = (healthz_status == 200) if healthz_url else (boot_exit == 0)
    return BootResult(
        boot_command=boot_command, mode=mode, healthz_url=healthz_url,
        boot_exit=boot_exit, healthz_status=healthz_status,
        elapsed_s=elapsed, pass_=pass_,
    )


def parse_runtime_prereq(prereq_path: Path) -> dict[str, str]:
    """intent/04-runtime-prereq.md frontmatter 에서 mode + boot_command + healthz 추출."""
    text = prereq_path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    if end == -1:
        return out
    body = text[3:end]
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip().strip('"\'')
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="부팅 + healthz 검증 1회")
    p_run.add_argument("--boot-command", help="부팅 명령 (예: 'npm start')")
    p_run.add_argument("--healthz", help="healthz URL (예: http://localhost:3000/healthz)")
    p_run.add_argument("--mode", default="real", choices=["real", "mock", "none"])
    p_run.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_S)
    p_run.add_argument("--cwd", type=Path, default=None)
    p_run.add_argument("--runtime-prereq", type=Path, default=None,
                       help="intent/04-runtime-prereq.md 에서 frontmatter 자동 로드")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        boot_command = args.boot_command
        healthz = args.healthz
        mode = args.mode
        if args.runtime_prereq:
            fm = parse_runtime_prereq(args.runtime_prereq)
            boot_command = boot_command or fm.get("boot_command", "")
            mode = fm.get("mode", mode)
            healthz = healthz or fm.get("healthz_url", None)
        if mode != "none" and not boot_command:
            print(json.dumps({"error": "boot_command 필요 (또는 --runtime-prereq)"}, ensure_ascii=False))
            return 2
        result = run_boot_check(
            boot_command=boot_command or "",
            healthz_url=healthz,
            mode=mode,
            timeout_s=args.timeout,
            cwd=args.cwd,
        )
        print(json.dumps(asdict(result), ensure_ascii=False))
        return 0 if result.pass_ else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
