"""resume.py 테스트 — 중단/재개 시나리오 검증."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

RESUME = Path(__file__).parent / "resume.py"


def _make_artifact(root: Path, rel: str, fp: str, prev: str | None, phase: str = "01-intent") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = "\n".join([
        "---",
        "skill_name: theseus-harness",
        "skill_version: 0.2.0",
        f"phase: {phase}",
        f"fingerprint: {fp}",
        f"prev_fingerprint: {prev or 'null'}",
        "produced_at: 2026-05-01T00:00:00Z",
        "---",
        "",
        "# Test artifact",
    ])
    p.write_text(fm + "\n", encoding="utf-8")
    return p


def _write_state(root: Path, **fields) -> None:
    default = {
        "project_id": "test",
        "project_run": "20260501-000000",
        "started_at": "2026-05-01T00:00:00Z",
        "last_updated_at": "2026-05-01T01:00:00Z",
        "status": "in_progress",
    }
    default.update(fields)
    (root / "state.json").write_text(json.dumps(default, ensure_ascii=False), encoding="utf-8")


def _run(cmd: str, root: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(RESUME), cmd, "--root", str(root)],
        capture_output=True, text=True,
    )
    return proc.returncode, json.loads(proc.stdout)


def test_no_state_returns_fresh_start_for_next():
    root = Path(tempfile.mkdtemp())
    rc, out = _run("next", root)
    assert rc == 0
    assert out["action"] == "fresh_start"
    assert out["entry_skill"] == "theseus-orchestrator"


def test_state_returns_state_json_contents():
    root = Path(tempfile.mkdtemp())
    _write_state(root, current_phase="06-plan", current_universe="a")
    rc, out = _run("state", root)
    assert rc == 0
    assert out["current_phase"] == "06-plan"
    assert out["current_universe"] == "a"


def test_state_missing_returns_error_for_state_command():
    root = Path(tempfile.mkdtemp())
    rc, out = _run("state", root)
    assert rc == 1
    assert out["ok"] is False
    assert "state.json 없음" in out["reason"]


def test_next_after_completed_phase_routes_to_next_skill():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "intent/01-intent.md", "sha256:a1", None, phase="01-intent")
    _write_state(
        root,
        last_completed_phase="01-intent",
        last_completed_artifact="intent/01-intent.md",
    )
    rc, out = _run("next", root)
    assert rc == 0
    assert out["action"] == "resume_next_phase"
    assert out["next_phase"] == "02-document"
    assert out["entry_skill"] == "theseus-intent"


def test_next_after_phase_07_routes_to_implement():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "plan/07-plan-review.md", "sha256:p7", None, phase="07-plan-recursion")
    _write_state(
        root,
        last_completed_phase="07-plan-recursion",
        last_completed_artifact="plan/07-plan-review.md",
    )
    rc, out = _run("next", root)
    assert rc == 0
    assert out["next_phase"] == "08-implement"
    assert out["entry_skill"] == "theseus-implement"


def test_validate_passes_for_clean_chain():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "intent/01-intent.md", "sha256:a1", None)
    _make_artifact(root, "intent/02-intent-review.md", "sha256:b1", "sha256:a1", phase="02-document")
    _write_state(root, last_completed_phase="02-document")
    rc, out = _run("validate", root)
    assert rc == 0
    assert out["ok"] is True
    assert out["integrity"]["fingerprint_chain"] == "ok"


def test_validate_detects_chain_break():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "intent/01-intent.md", "sha256:a1", None)
    # 다음 산출물의 prev 가 존재 안 함 — 체인 끊김
    _make_artifact(root, "plan/06-plan.md", "sha256:c1", "sha256:MISSING", phase="06-plan")
    _write_state(root, last_completed_phase="06-plan")
    rc, out = _run("validate", root)
    assert rc == 1
    assert out["ok"] is False
    assert "break" in out["integrity"]["fingerprint_chain"]


def test_next_with_chain_break_requires_repair():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "plan/06-plan.md", "sha256:c1", "sha256:MISSING", phase="06-plan")
    _write_state(root, last_completed_phase="06-plan")
    rc, out = _run("next", root)
    assert rc == 1
    assert out["action"] == "repair_required"
    assert "유일 추가 예외" in out["reason"]


def test_next_with_incomplete_pending_discards_then_resumes():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "impl/08-impl-log.md", "sha256:i1", None, phase="08-implement")
    # 부분 산출물 — frontmatter 없음
    partial = root / "impl/T-020/sub/A.1/code.go"
    partial.parent.mkdir(parents=True, exist_ok=True)
    partial.write_text("// incomplete code, no frontmatter\n", encoding="utf-8")
    _write_state(
        root,
        last_completed_phase="08-implement",
        last_completed_artifact="impl/08-impl-log.md",
        active_skill="theseus-implement",
        current_phase="08-implement",
        pending_artifacts=["impl/T-020/sub/A.1/code.go (in_progress)"],
    )
    rc, out = _run("next", root)
    assert rc == 0
    assert out["action"] == "discard_incomplete_then_resume"
    assert "impl/T-020/sub/A.1/code.go" in out["discard_files"]
    assert out["entry_skill"] == "theseus-implement"


def test_next_after_phase_13_returns_already_complete():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "handoff/13-handoff.md", "sha256:h1", None, phase="13-handoff")
    _write_state(
        root,
        last_completed_phase="13-handoff",
        last_completed_artifact="handoff/13-handoff.md",
    )
    rc, out = _run("next", root)
    assert rc == 0
    assert out["action"] == "already_complete"
