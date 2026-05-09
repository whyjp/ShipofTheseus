"""phase_state.py 테스트 — runtime 단조성 게이트 + frontmatter forgery 차단."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PS = Path(__file__).parent / "phase_state.py"


def _run(*cmd_args: str) -> tuple[int, dict | None, str]:
    proc = subprocess.run(
        [sys.executable, str(PS), *cmd_args],
        capture_output=True, text=True, encoding="utf-8",
    )
    out = None
    if proc.stdout.strip():
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            out = None
    return proc.returncode, out, proc.stderr


def _root() -> Path:
    return Path(tempfile.mkdtemp())


# ─── init ─────────────────────────────────────────

def test_init_creates_state_file():
    r = _root()
    rc, out, _ = _run("init", "--root", str(r), "--grade", "G4", "--project-id", "proj-x")
    assert rc == 0
    state = json.loads((r / "state" / "phase_state.json").read_text(encoding="utf-8"))
    assert state["schema_version"] == 1
    assert state["project_id"] == "proj-x"
    assert state["grade"] == "G4"
    assert state["phases"] == []
    assert state["current_status"] == "idle"


def test_init_rejects_duplicate():
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    rc, _, err = _run("init", "--root", str(r), "--grade", "G4")
    assert rc == 1
    assert "이미 존재" in err


# ─── enter / exit happy path ───────────────────────

def test_enter_then_exit_records_phase():
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    rc, _, _ = _run("enter", "--root", str(r), "--phase", "00", "--producer", "project-namer")
    assert rc == 0
    time.sleep(1)   # ensure exited_at strictly > entered_at (1s granularity)
    rc, _, _ = _run("exit", "--root", str(r), "--phase", "00",
                    "--fingerprint", "sha256:abc", "--outcome", "ok")
    assert rc == 0
    state = json.loads((r / "state" / "phase_state.json").read_text(encoding="utf-8"))
    assert len(state["phases"]) == 1
    p0 = state["phases"][0]
    assert p0["status"] == "completed"
    assert p0["fingerprint"] == "sha256:abc"
    assert p0["duration_seconds"] >= 1


def test_validate_passes_for_clean_chain():
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    _run("enter", "--root", str(r), "--phase", "00", "--producer", "project-namer")
    time.sleep(1)
    _run("exit", "--root", str(r), "--phase", "00", "--fingerprint", "sha256:a", "--outcome", "ok")
    time.sleep(1)
    _run("enter", "--root", str(r), "--phase", "01", "--producer", "intent-extractor")
    time.sleep(1)
    _run("exit", "--root", str(r), "--phase", "01", "--fingerprint", "sha256:b", "--outcome", "ok")

    rc, _, _ = _run("validate", "--root", str(r))
    assert rc == 0


# ─── 단조성 위반 ──────────────────────────────────

def test_enter_rejects_when_already_in_progress():
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    _run("enter", "--root", str(r), "--phase", "00", "--producer", "namer")
    rc, _, err = _run("enter", "--root", str(r), "--phase", "01", "--producer", "intent")
    assert rc == 1
    assert "in_progress" in err


def test_validate_detects_manual_backfill():
    """수동으로 phase_state.json 을 편집해 단조성을 깬 경우 — sprint-17 forgery 패턴."""
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    sp = r / "state" / "phase_state.json"
    state = json.loads(sp.read_text(encoding="utf-8"))
    # 인위적으로 단조성 깨기 — phase 00 의 exited_at 보다 phase 01 entered_at 이 더 이전
    state["phases"] = [
        {"phase": "00", "status": "completed",
         "entered_at": "2026-05-09T13:00:00Z", "exited_at": "2026-05-09T13:10:00Z",
         "duration_seconds": 600, "fingerprint": "sha256:a", "producer": "n",
         "outcome": "ok", "artifact_path": None, "frontmatter_created_at": None},
        {"phase": "01", "status": "completed",
         "entered_at": "2026-05-09T13:05:00Z",   # ← 위반: 직전 exited_at 보다 이전
         "exited_at": "2026-05-09T13:15:00Z",
         "duration_seconds": 600, "fingerprint": "sha256:b", "producer": "i",
         "outcome": "ok", "artifact_path": None, "frontmatter_created_at": None},
    ]
    sp.write_text(json.dumps(state, indent=2), encoding="utf-8")

    rc, _, err = _run("validate", "--root", str(r))
    assert rc == 1
    assert "단조성 위반" in err


# ─── frontmatter forgery cross-check ──────────────

def test_exit_detects_frontmatter_forgery():
    """v0.9.22 사건 — 산출물 frontmatter created_at 이 phase 진입 *이전* 시각."""
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    _run("enter", "--root", str(r), "--phase", "00", "--producer", "namer")
    # 위조된 산출물 — frontmatter created_at 이 페이즈 진입보다 1 시간 *이전*
    art = r / "naming" / "00-naming.md"
    art.parent.mkdir(parents=True)
    art.write_text(
        "---\n"
        "skill_name: theseus-harness\n"
        "phase: '00'\n"
        "created_at: '2020-01-01T00:00:00Z'\n"   # ← 위조
        "---\n# naming\n",
        encoding="utf-8",
    )
    time.sleep(1)
    rc, _, err = _run("exit", "--root", str(r), "--phase", "00",
                      "--fingerprint", "sha256:a", "--outcome", "ok",
                      "--artifact-path", "naming/00-naming.md")
    assert rc == 1
    assert "forgery" in err


def test_exit_accepts_frontmatter_within_window():
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    _run("enter", "--root", str(r), "--phase", "00", "--producer", "namer")
    # 산출물 frontmatter created_at = 정상 (페이즈 진입 직후 — exit 호출 시점 1초 이내)
    art = r / "naming" / "00-naming.md"
    art.parent.mkdir(parents=True)
    # state 의 entered_at 을 읽어 그 이후 시각으로 박음
    state = json.loads((r / "state" / "phase_state.json").read_text(encoding="utf-8"))
    entered = state["phases"][-1]["entered_at"]
    art.write_text(
        f"---\nskill_name: theseus-harness\nphase: '00'\ncreated_at: '{entered}'\n---\n# naming\n",
        encoding="utf-8",
    )
    time.sleep(1)
    rc, _, _ = _run("exit", "--root", str(r), "--phase", "00",
                    "--fingerprint", "sha256:a", "--outcome", "ok",
                    "--artifact-path", "naming/00-naming.md")
    assert rc == 0


# ─── status ───────────────────────────────────────

def test_status_dumps_state_json():
    r = _root()
    _run("init", "--root", str(r), "--grade", "G4")
    rc, out, _ = _run("status", "--root", str(r))
    assert rc == 0
    assert out["schema_version"] == 1
    assert out["grade"] == "G4"
