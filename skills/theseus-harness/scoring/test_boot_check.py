"""boot_check.py — frontmatter 파싱 + mode=none + spawn-error 시나리오 검증."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from boot_check import (
    BootResult,
    parse_runtime_prereq,
    run_boot_check,
)


def test_mode_none_skips_boot():
    """mode=none → 부팅 시도 없이 pass."""
    r = run_boot_check(
        boot_command="should-not-run",
        healthz_url=None,
        mode="none",
    )
    assert r.pass_ is True
    assert r.boot_exit == "no-runtime"
    assert r.healthz_status == "skipped"
    assert r.mode == "none"


def test_spawn_error_does_not_crash():
    """존재 안 하는 명령 → spawn-error 산출, BootResult 반환 (예외 X)."""
    # cmd /c 같은 셸 wrapper 가 없는 짧은 invalid command
    r = run_boot_check(
        boot_command="this-command-cannot-exist-anywhere-x9z7q",
        healthz_url=None,
        mode="real",
        timeout_s=2.0,
    )
    # shell=True 라 보통 exit code 127/-1/1 — pass_ False 면 OK
    assert r.pass_ is False or isinstance(r.boot_exit, str)


def test_healthz_unreachable_returns_error_status():
    """healthz URL 이 연결 불가 → 'error: ...' 반환, pass=False."""
    r = run_boot_check(
        boot_command="python -c \"import time; time.sleep(2)\"",
        healthz_url="http://127.0.0.1:1/healthz",  # port 1 = 미사용 보장
        mode="real",
        timeout_s=2.0,
    )
    assert r.pass_ is False
    # healthz 결과가 200 이 아닌 무엇 (연결 거부 / timeout / etc)
    assert r.healthz_status != 200


def test_parse_runtime_prereq_extracts_keys(tmp_path: Path):
    prereq = tmp_path / "04-runtime-prereq.md"
    prereq.write_text(
        "---\n"
        "skill_name: theseus-harness\n"
        "phase: 04-clarify\n"
        "mode: real\n"
        "boot_command: npm start\n"
        "healthz_url: http://localhost:3000/healthz\n"
        "secrets_count: 4\n"
        "entry_blocked: false\n"
        "---\n"
        "# Body\n",
        encoding="utf-8",
    )
    fm = parse_runtime_prereq(prereq)
    assert fm["mode"] == "real"
    assert fm["boot_command"] == "npm start"
    assert fm["healthz_url"] == "http://localhost:3000/healthz"
    assert fm["entry_blocked"] == "false"


def test_parse_runtime_prereq_missing_frontmatter(tmp_path: Path):
    prereq = tmp_path / "no-frontmatter.md"
    prereq.write_text("# Just a markdown\n\nNo frontmatter.\n", encoding="utf-8")
    fm = parse_runtime_prereq(prereq)
    assert fm == {}


def test_boot_result_dataclass_serializable():
    r = BootResult(
        boot_command="echo hi",
        mode="real",
        healthz_url=None,
        boot_exit=0,
        healthz_status="skipped",
        elapsed_s=0.5,
        pass_=True,
    )
    # dataclass.asdict 가 JSON 직렬화 OK 임을 간접 검증
    from dataclasses import asdict
    d = asdict(r)
    assert d["boot_exit"] == 0
    assert d["pass_"] is True
