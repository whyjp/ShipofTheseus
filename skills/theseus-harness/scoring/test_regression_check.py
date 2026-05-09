"""regression_check.py 테스트 — TDD + boot + lint 재실행 게이트 + 회귀 검출."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

RC = Path(__file__).parent / "regression_check.py"


def _run(*args: str) -> tuple[int, dict | None, str]:
    proc = subprocess.run(
        [sys.executable, str(RC), *args],
        capture_output=True, text=True, encoding="utf-8",
    )
    out = None
    if proc.stdout.strip():
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            pass
    return proc.returncode, out, proc.stderr


def _root() -> Path:
    return Path(tempfile.mkdtemp())


# 크로스플랫폼 — shell=True 사용. Windows cmd / POSIX sh 모두 `exit 0` / `exit 1` 지원.
TRUE_CMD = "exit 0"
FALSE_CMD = "exit 1"


# ─── run — 단순 케이스 ────────────────────────────

def test_run_all_pass_writes_log_entry():
    r = _root()
    rc, out, _ = _run("run", "--root", str(r), "--module", "T-001",
                      "--test-cmd", TRUE_CMD,
                      "--lint-cmd", TRUE_CMD)
    assert rc == 0
    assert out["ok"] is True
    assert out["outcome"] == "ok"
    log = json.loads((r / "state" / "regression_log.json").read_text(encoding="utf-8"))
    assert len(log["entries"]) == 1
    assert log["entries"][0]["module"] == "T-001"
    assert log["entries"][0]["test"]["exit"] == 0


def test_run_test_fail_returns_1():
    r = _root()
    rc, out, _ = _run("run", "--root", str(r), "--module", "T-001",
                      "--test-cmd", FALSE_CMD)
    assert rc == 1
    assert out["ok"] is False
    assert "tests fail" in out["reason"]


def test_run_skipped_when_no_cmd():
    r = _root()
    # 모든 cmd 생략 — 모두 skipped, pass
    rc, out, _ = _run("run", "--root", str(r), "--module", "T-001")
    assert rc == 0
    log = json.loads((r / "state" / "regression_log.json").read_text(encoding="utf-8"))
    e = log["entries"][0]
    assert e["test"]["exit"] == "skipped"
    assert e["boot"]["exit"] == "skipped"
    assert e["lint"]["exit"] == "skipped"


# ─── last ─────────────────────────────────────────

def test_last_returns_most_recent_entry():
    r = _root()
    _run("run", "--root", str(r), "--module", "T-001", "--test-cmd", TRUE_CMD)
    _run("run", "--root", str(r), "--module", "T-002", "--test-cmd", TRUE_CMD)
    rc, out, _ = _run("last", "--root", str(r))
    assert rc == 0
    assert out["module"] == "T-002"


def test_last_empty_log_returns_1():
    r = _root()
    rc, _, err = _run("last", "--root", str(r))
    assert rc == 1
    assert "비어" in err


# ─── compare — 회귀 검출 ──────────────────────────

def test_compare_detects_regression():
    r = _root()
    # 1 회 ok → 1 회 fail = regression
    _run("run", "--root", str(r), "--module", "T-001", "--test-cmd", TRUE_CMD)
    _run("run", "--root", str(r), "--module", "T-002", "--test-cmd", FALSE_CMD)
    rc, out, _ = _run("compare", "--root", str(r))
    assert rc == 1
    assert out["regressed"] is True
    assert out["prev_ok"]["module"] == "T-001"
    assert out["latest"]["module"] == "T-002"


def test_compare_no_regression_when_latest_ok():
    r = _root()
    _run("run", "--root", str(r), "--module", "T-001", "--test-cmd", FALSE_CMD)
    _run("run", "--root", str(r), "--module", "T-002", "--test-cmd", TRUE_CMD)
    rc, out, _ = _run("compare", "--root", str(r))
    assert rc == 0
    assert out["regressed"] is False


def test_compare_no_prior_ok_treats_first_fail_as_baseline():
    r = _root()
    _run("run", "--root", str(r), "--module", "T-001", "--test-cmd", FALSE_CMD)
    _run("run", "--root", str(r), "--module", "T-002", "--test-cmd", FALSE_CMD)
    rc, out, _ = _run("compare", "--root", str(r))
    # 둘 다 fail — regression 으로 보지 않음 (prior known-good 부재)
    assert rc == 0
    assert out["regressed"] is False
    assert "no prior known-good" in out["reason"]
