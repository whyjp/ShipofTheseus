"""checkpoint.py 테스트 — 회귀 매핑 + 멀티버스 선택 검증."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHK = Path(__file__).parent / "checkpoint.py"


def _project_with_checkpoints(checkpoints: dict[str, list[tuple[str, str]]]) -> Path:
    """
    임시 .ShipofTheseus 트리 생성.
    checkpoints = {"08": [("08.001", "module: auth"), ("08.002", "module: payment")]}
    """
    root = Path(tempfile.mkdtemp())
    for phase, ids in checkpoints.items():
        for cid, meta_text in ids:
            d = root / "checkpoints" / phase / cid
            d.mkdir(parents=True)
            (d / "meta.md").write_text(meta_text, encoding="utf-8")
    return root


def _run_find(root: Path, failure_kind: str, module: str | None = None, sprint: int | None = None) -> tuple[int, dict]:
    args = [sys.executable, str(CHK), "find-target", "--root", str(root), "--failure-kind", failure_kind]
    if module:
        args += ["--module", module]
    if sprint is not None:
        args += ["--sprint", str(sprint)]
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, json.loads(proc.stdout)


def _run_select(universes: list[dict]) -> tuple[int, dict]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(universes, f)
        path = Path(f.name)
    proc = subprocess.run(
        [sys.executable, str(CHK), "select-universe", "--universes-json", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.returncode, json.loads(proc.stdout)


# ─── 회귀 매핑 테스트 ─────────────────────────────────────────

def test_intent_mismatch_routes_to_phase_01():
    root = _project_with_checkpoints({"01": [("01.001", "intent v1")]})
    rc, out = _run_find(root, "intent_mismatch")
    assert rc == 0
    assert out["target_phase"] == "01"
    assert out["checkpoint"] == "01.001"


def test_module_violation_finds_module_checkpoint():
    root = _project_with_checkpoints(
        {"08": [("08.001", "module: auth"), ("08.002", "module: payment"), ("08.003", "module: notify")]}
    )
    rc, out = _run_find(root, "module_impl_violation", module="payment")
    assert rc == 0
    assert out["checkpoint"] == "08.002"
    assert out["lesson_seed"]["module"] == "payment"


def test_test_regression_finds_prior_sprint_checkpoint():
    root = _project_with_checkpoints(
        {"10": [("10.01", "sprint 1"), ("10.02", "sprint 2"), ("10.03", "sprint 3")]}
    )
    # sprint 3 에서 회귀 → sprint 2 (10.02) 로
    rc, out = _run_find(root, "test_regression", sprint=3)
    assert rc == 0
    assert out["checkpoint"].startswith("10.02")


def test_resource_ceiling_routes_to_phase_04():
    root = _project_with_checkpoints({"04": [("04.001", "nfr profile")]})
    rc, out = _run_find(root, "resource_ceiling")
    assert rc == 0
    assert out["target_phase"] == "04"


def test_unknown_failure_kind_rejected():
    # argparse choices 가 막아 별도 검증 — 직접 호출 시 0 반환되는 경로 없음
    proc = subprocess.run(
        [sys.executable, str(CHK), "find-target", "--root", "/tmp", "--failure-kind", "alien"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode != 0


def test_missing_checkpoint_dir_returns_action():
    root = Path(tempfile.mkdtemp())  # 빈 트리
    rc, out = _run_find(root, "intent_mismatch")
    assert rc == 1
    assert out["ok"] is False
    assert out["action"].startswith("rerun_phase_")


# ─── 멀티버스 선택 테스트 ──────────────────────────────────────

def test_select_universe_dominant_winner():
    rc, out = _run_select(
        [
            {"id": "a", "score": 0.97, "dip_violation": False},
            {"id": "b", "score": 0.90, "dip_violation": False},
        ]
    )
    assert rc == 0
    assert out["verdict"] == "select"
    assert out["winner"] == "a"
    assert out["archive_to_losers"] == ["b"]


def test_select_universe_dip_violation_eliminated():
    rc, out = _run_select(
        [
            {"id": "a", "score": 0.99, "dip_violation": True},   # 탈락
            {"id": "b", "score": 0.90, "dip_violation": False},  # 우승
        ]
    )
    assert rc == 0
    assert out["winner"] == "b"


def test_all_universes_dip_violation_halts():
    rc, out = _run_select(
        [
            {"id": "a", "score": 0.99, "dip_violation": True},
            {"id": "b", "score": 0.95, "dip_violation": True},
        ]
    )
    assert rc != 0
    assert out["verdict"] == "halt_for_intent_mismatch"


def test_close_scores_with_loc_auto_merge():
    rc, out = _run_select(
        [
            {"id": "a", "score": 0.951, "dip_violation": False, "loc": 1200},
            {"id": "b", "score": 0.950, "dip_violation": False, "loc": 800},   # 더 단순
        ]
    )
    assert rc == 0
    assert out["verdict"] == "auto_merge"
    assert out["base_universe"] == "b"   # LOC 더 적음
