"""placeholder_grep.py viewer JSON 검증 — sprint-52 PR-E v0.9.52.

`--include-viewer-json` opt-in 시 lineage.json / dashboard.json / webview/data/webview.json
의 cold session 마감 후 placeholder 잔존 catch.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCORING_DIR = Path(__file__).parent
sys.path.insert(0, str(SCORING_DIR))

import placeholder_grep as pg  # noqa: E402


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def test_lineage_pending_caught(tmp_path: Path):
    _write(tmp_path / "lineage.json", {
        "project_run": "pending",
        "final_outcome": "IN_PROGRESS",
        "winner": None,
        "fingerprint_chain": [],
        "mermaid_flowchart": "flowchart TB\n  Empty[\"cold session 미시작\"]",
        "mermaid_gantt": "gantt\n  title Phase Lineage — pending",
        "phases": [],
    })
    v = pg.check_viewer_json_placeholders(tmp_path)
    fields = {item.get("field") for item in v}
    assert "project_run" in fields
    assert "final_outcome" in fields
    assert "winner" in fields
    assert "fingerprint_chain" in fields
    assert "mermaid_flowchart" in fields


def test_lineage_completed_passes(tmp_path: Path):
    _write(tmp_path / "lineage.json", {
        "project_run": "completed",
        "final_outcome": "DONE",
        "winner": {"universe": "universe-1"},
        "fingerprint_chain": [{"phase": "p", "fingerprint": "sha256:abc"}],
        "mermaid_flowchart": "flowchart TB\n  P0[\"00-naming\"]",
        "mermaid_gantt": "gantt\n  title Phase Lineage — completed\n  section phases\n  p0 :2026-05-10 11:00:00, 30s",
        "phases": [
            {"phase": "00-naming", "fingerprint": "sha256:abc",
             "created_at": "2026-05-10T11:05:23Z"},
        ],
    })
    v = pg.check_viewer_json_placeholders(tmp_path)
    assert v == []


def test_lineage_phase_pending_caught(tmp_path: Path):
    _write(tmp_path / "lineage.json", {
        "project_run": "completed", "final_outcome": "DONE",
        "winner": {"x": 1}, "fingerprint_chain": [{"f": 1}],
        "mermaid_flowchart": "flowchart TB",
        "mermaid_gantt": "gantt",
        "phases": [
            {"phase": "01-intent", "fingerprint": "PENDING",
             "created_at": "2026-05-10T11:00:00Z"},
        ],
    })
    v = pg.check_viewer_json_placeholders(tmp_path)
    msgs = [(item["field"], item["detail"]) for item in v]
    assert any("phases[01-intent].fingerprint" == f for f, _ in msgs)
    assert any("phases[01-intent].created_at" == f for f, _ in msgs)


def test_dashboard_status_complete_but_null_final_phase(tmp_path: Path):
    iv = tmp_path / "interactive-viewer"
    _write(iv / "dashboard.json", {
        "status": "complete",
        "current_phase": "pre-bootup",
        "final_phase": None,
    })
    v = pg.check_viewer_json_placeholders(tmp_path)
    fields = {item["field"] for item in v}
    assert "final_phase" in fields
    assert "current_phase" in fields


def test_webview_duration_stub_caught(tmp_path: Path):
    wv = tmp_path / "webview" / "data"
    _write(wv / "webview.json", {
        "final_phase": None,
        "timing": {
            "started_at": "2026-05-10T11:00:00Z",
            "duration_seconds": 4.35,  # 실험 wall-time 만, cold session 전체 아님
            "phases_completed": 43,
        },
    })
    v = pg.check_viewer_json_placeholders(tmp_path)
    fields = {item["field"] for item in v}
    assert "final_phase" in fields
    assert "timing.duration_seconds" in fields


def test_no_viewer_files_no_violations(tmp_path: Path):
    """3 viewer JSON 모두 부재 — pass (옵션은 viewer 환경에서만 의미)."""
    v = pg.check_viewer_json_placeholders(tmp_path)
    assert v == []
