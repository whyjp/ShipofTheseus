"""lineage_finalize.py 테스트 — sprint-52 PR-B v0.9.52.

3 fixture:
- empty: lineage.json placeholder + .ShipofTheseus 빈 → SystemExit (실 산출물 부재).
- partial: 몇 phase .md + fingerprint PENDING + created_at 정시 stub → refresh 후 chain 채워짐 + warn count > 0.
- complete: 정상 phase .md + 실 fingerprint + 실 created_at → refresh 후 lineage.json 의 placeholder 모두 제거.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCORING_DIR = Path(__file__).parent
sys.path.insert(0, str(SCORING_DIR))

import lineage_finalize as lf  # noqa: E402

LF = SCORING_DIR / "lineage_finalize.py"


# ─── fixture helpers ─────────────────────────────────────────────────────


def _write_phase(
    sot_dir: Path,
    rel: str,
    phase: str,
    created_at: str | None = "2026-05-10T11:00:00Z",
    fingerprint: str = "PENDING",
    prev_fingerprint: str = "PENDING_FROM_NULL",
    body: str = "# placeholder body\n",
    universe: str | None = None,
) -> Path:
    p = sot_dir / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    fm_lines = [
        "---",
        "skill_name: shipoftheseus:theseus-orchestrator",
        "skill_version: 0.9.52",
        f"phase: {phase}",
        f"created_at: {created_at if created_at else 'null'}",
        f"fingerprint: {fingerprint}",
        f"prev_fingerprint: {prev_fingerprint}",
    ]
    if universe:
        fm_lines.append(f"universe: {universe}")
    fm_lines.append("---")
    p.write_text("\n".join(fm_lines) + "\n\n" + body, encoding="utf-8")
    return p


def _make_skeleton_lineage(root: Path) -> Path:
    p = root / "lineage.json"
    p.write_text(
        json.dumps({
            "schema_version": "0.9.41",
            "project_id": "test-project",
            "project_run": "pending",
            "started_at_iso": "2026-05-10T11:00:00Z",
            "ended_at_iso": "2026-05-10T11:30:00Z",
            "duration_seconds": 4.35,
            "grade": "G4",
            "final_phase": None,
            "phases_completed": 0,
            "violations_count": 0,
            "dacapo_count": 0,
            "final_outcome": "IN_PROGRESS",
            "mermaid_flowchart": "flowchart TB\n  Empty[\"cold session 미시작\"]",
            "mermaid_gantt": "gantt\n  title Phase Lineage — pending\n  section Pending\n  대기 :p0, 2000-01-01 00:00, 1m",
            "fingerprint_chain": [],
            "phases": [],
            "winner": None,
        }, indent=2),
        encoding="utf-8",
    )
    return p


# ─── tests ───────────────────────────────────────────────────────────────


def test_empty_root_raises_systemexit(tmp_path: Path):
    """`.ShipofTheseus/` 가 없으면 SystemExit (실 산출물 부재)."""
    _make_skeleton_lineage(tmp_path)
    with pytest.raises(SystemExit):
        lf.refresh_lineage(tmp_path, dry_run=False, strict=False)


def test_partial_with_stub_created_at_triggers_warn(tmp_path: Path):
    """부분 산출 + created_at 정시 stub → fallback warn count > 0."""
    _make_skeleton_lineage(tmp_path)
    sot = tmp_path / ".ShipofTheseus"
    _write_phase(sot, "intent/01-intent.md", "01-intent", "2026-05-10T11:00:00Z")
    _write_phase(sot, "plan/06-plan.md", "06-plan", "2026-05-10T11:00:00Z")
    _write_phase(sot, "handoff/14-handoff.md", "14-handoff", "2026-05-10T11:00:00Z")

    report = lf.refresh_lineage(tmp_path, dry_run=False, strict=False)
    assert report["created_at_fallback_count"] >= 3
    assert report["phases_completed"] == 3

    lin = json.loads((tmp_path / "lineage.json").read_text(encoding="utf-8"))
    assert lin["project_run"] == "completed"
    assert lin["final_outcome"] == "DONE"
    assert len(lin["fingerprint_chain"]) == 3
    assert all(c["fingerprint"].startswith("sha256:") for c in lin["fingerprint_chain"])
    assert "Empty" not in lin["mermaid_flowchart"]
    assert "미시작" not in lin["mermaid_flowchart"]
    assert "Pending" not in lin["mermaid_gantt"]


def test_strict_mode_fails_on_stub(tmp_path: Path):
    """strict 모드 + created_at 정시 stub 잔존 → strict_violation report."""
    _make_skeleton_lineage(tmp_path)
    sot = tmp_path / ".ShipofTheseus"
    _write_phase(sot, "intent/01-intent.md", "01-intent", "2026-05-10T11:00:00Z")
    _write_phase(sot, "handoff/14-handoff.md", "14-handoff", "2026-05-10T11:00:00Z")

    report = lf.refresh_lineage(tmp_path, dry_run=False, strict=True)
    assert "strict_violation" in report


def test_complete_phases_no_fallback(tmp_path: Path):
    """완전 산출 (실 timestamp + 실 fingerprint) → fallback warn 0."""
    _make_skeleton_lineage(tmp_path)
    sot = tmp_path / ".ShipofTheseus"
    _write_phase(sot, "intent/01-intent.md", "01-intent", "2026-05-10T11:05:23Z",
                 fingerprint="sha256:abc123", prev_fingerprint="GENESIS")
    _write_phase(sot, "plan/06-plan.md", "06-plan", "2026-05-10T11:08:45Z",
                 fingerprint="sha256:def456", prev_fingerprint="sha256:abc123")
    _write_phase(sot, "handoff/14-handoff.md", "14-handoff", "2026-05-10T11:14:12Z",
                 fingerprint="sha256:ghi789", prev_fingerprint="sha256:def456")

    report = lf.refresh_lineage(tmp_path, dry_run=False, strict=True)
    assert report["created_at_fallback_count"] == 0
    assert "strict_violation" not in report
    assert report["phases_completed"] == 3


def test_dry_run_does_not_write(tmp_path: Path):
    """--dry-run → lineage.json 변경 없음."""
    p = _make_skeleton_lineage(tmp_path)
    original = p.read_text(encoding="utf-8")
    sot = tmp_path / ".ShipofTheseus"
    _write_phase(sot, "intent/01-intent.md", "01-intent")

    lf.refresh_lineage(tmp_path, dry_run=True, strict=False)
    after = p.read_text(encoding="utf-8")
    assert original == after


def test_dashboard_and_webview_refresh(tmp_path: Path):
    """dashboard.json / webview/data/webview.json 동시 refresh."""
    _make_skeleton_lineage(tmp_path)
    sot = tmp_path / ".ShipofTheseus"
    _write_phase(sot, "handoff/14-handoff.md", "14-handoff", "2026-05-10T11:14:12Z")

    iv = tmp_path / "interactive-viewer"
    iv.mkdir()
    (iv / "dashboard.json").write_text(json.dumps({
        "schema_version": "0.9.41",
        "current_phase": "pre-bootup",
        "final_phase": None,
        "status": "complete",
    }, indent=2), encoding="utf-8")

    wv_dir = tmp_path / "webview" / "data"
    wv_dir.mkdir(parents=True)
    (wv_dir / "webview.json").write_text(json.dumps({
        "schema_version": "0.9.41",
        "final_phase": None,
        "timing": {
            "started_at": "2026-05-10T11:00:00Z",
            "ended_at": "2026-05-10T11:30:00Z",
            "duration_seconds": 4.35,
            "phases_completed": 0,
        },
    }, indent=2), encoding="utf-8")

    rc = lf.cmd_refresh(type("A", (), {
        "root": str(tmp_path), "dry_run": False, "strict": False,
    })())
    assert rc == 0

    dash = json.loads((iv / "dashboard.json").read_text(encoding="utf-8"))
    assert dash["current_phase"] == "14-handoff"
    assert dash["final_phase"] == "14-handoff"

    wv = json.loads((wv_dir / "webview.json").read_text(encoding="utf-8"))
    assert wv["final_phase"] == "14-handoff"
    assert wv["timing"]["duration_seconds"] >= 60  # 1800s 정도여야


def test_universe_candidate_phase_label(tmp_path: Path):
    """universe candidate phase 는 phase@universe 라벨로."""
    _make_skeleton_lineage(tmp_path)
    sot = tmp_path / ".ShipofTheseus"
    _write_phase(sot, "plan/candidates/universe-1/06-plan.md", "06-plan-candidate",
                 created_at="2026-05-10T11:08:30Z", universe="universe-1")
    _write_phase(sot, "plan/candidates/universe-2/06-plan.md", "06-plan-candidate",
                 created_at="2026-05-10T11:08:35Z", universe="universe-2")
    _write_phase(sot, "handoff/14-handoff.md", "14-handoff", "2026-05-10T11:14:12Z")

    lf.refresh_lineage(tmp_path, dry_run=False, strict=False)
    lin = json.loads((tmp_path / "lineage.json").read_text(encoding="utf-8"))
    labels = [p["phase"] for p in lin["phases"]]
    assert "06-plan-candidate@universe-1" in labels
    assert "06-plan-candidate@universe-2" in labels


def test_cli_invocation_smoke(tmp_path: Path):
    """`python lineage_finalize.py refresh --root <dir>` smoke."""
    _make_skeleton_lineage(tmp_path)
    sot = tmp_path / ".ShipofTheseus"
    _write_phase(sot, "handoff/14-handoff.md", "14-handoff", "2026-05-10T11:14:12Z")
    proc = subprocess.run(
        [sys.executable, str(LF), "refresh", "--root", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["lineage"]["phases_completed"] == 1
