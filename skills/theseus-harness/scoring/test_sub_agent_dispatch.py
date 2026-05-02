"""sub_agent_dispatch.py 테스트 — 하위 분해 결정 + 머지 검증."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

DISPATCH = Path(__file__).parent / "sub_agent_dispatch.py"


def _run_decide(module_spec: dict, grade: int = 4) -> tuple[int, dict]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(module_spec, f)
        path = Path(f.name)
    proc = subprocess.run(
        [sys.executable, str(DISPATCH), "decide", "--module-spec", str(path), "--grade", str(grade)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.returncode, json.loads(proc.stdout)


def _run_merge(results: list[dict], mode: str = "parallel") -> tuple[int, dict]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(results, f)
        path = Path(f.name)
    proc = subprocess.run(
        [sys.executable, str(DISPATCH), "merge", "--results", str(path), "--mode", mode],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.returncode, json.loads(proc.stdout)


# ─── decide 테스트 ─────────────────────────────────────

def test_grade_2_never_subdivides():
    rc, out = _run_decide({"title": "auth and payment", "estimated_loc": 500}, grade=2)
    assert out["subdivide"] is False


def test_loc_over_threshold_triggers_subdivide():
    rc, out = _run_decide({"title": "auth", "estimated_loc": 250}, grade=4)
    assert rc == 0
    assert out["subdivide"] is True
    assert any("LOC 250" in t for t in out["triggers"])


def test_compound_responsibility_triggers():
    rc, out = _run_decide({"title": "user 인증 and 결제 처리", "estimated_loc": 100}, grade=4)
    assert out["subdivide"] is True
    assert any("복합 책임" in t for t in out["triggers"])


def test_multi_language_triggers():
    rc, out = _run_decide({"title": "auth", "estimated_loc": 100, "languages": ["go", "ts"]}, grade=4)
    assert out["subdivide"] is True
    assert any("다중 스택" in t for t in out["triggers"])


def test_depth_limit_triggers_regression_to_plan():
    rc, out = _run_decide({"title": "x and y", "estimated_loc": 250, "depth": 2}, grade=4)
    assert out["subdivide"] is False
    assert out["regress_to_plan"] is True
    assert "한도" in out["reason"]


def test_rewrite_streak_triggers_subdivide():
    rc, out = _run_decide({"title": "x", "estimated_loc": 100, "rewrite_streak": 3}, grade=4)
    assert out["subdivide"] is True
    assert any("회귀 누적" in t for t in out["triggers"])


def test_grade_5_recommends_competition_mode():
    rc, out = _run_decide({"title": "auth and pay", "estimated_loc": 250}, grade=5)
    assert out["subdivide"] is True
    assert out["recommended_mode"] == "competition"


# ─── merge 테스트 ─────────────────────────────────────

def test_merge_parallel_accept_all():
    results = [
        {"id": "A.1", "score": 0.95, "files_written": ["a.go"]},
        {"id": "A.2", "score": 0.93, "files_written": ["b.go"]},
    ]
    rc, out = _run_merge(results, mode="parallel")
    assert rc == 0
    assert out["verdict"] == "accept_all"
    assert set(out["ids"]) == {"A.1", "A.2"}


def test_merge_same_file_conflict_violates_guard():
    results = [
        {"id": "A.1", "score": 0.95, "files_written": ["shared.go"]},
        {"id": "A.2", "score": 0.93, "files_written": ["shared.go"]},   # 충돌
    ]
    rc, out = _run_merge(results, mode="parallel")
    assert rc != 0
    assert out["guard_violation"] is True


def test_merge_competition_select_dominant():
    results = [
        {"id": "A.1", "score": 0.97, "dip_violation": False, "loc": 100},
        {"id": "A.2", "score": 0.90, "dip_violation": False, "loc": 80},
    ]
    rc, out = _run_merge(results, mode="competition")
    assert rc == 0
    assert out["verdict"] == "select"
    assert out["winner"] == "A.1"


def test_merge_competition_dip_eliminated():
    results = [
        {"id": "A.1", "score": 0.99, "dip_violation": True, "loc": 50},
        {"id": "A.2", "score": 0.90, "dip_violation": False, "loc": 100},
    ]
    rc, out = _run_merge(results, mode="competition")
    assert out["winner"] == "A.2"   # DIP 위반 우주 탈락


def test_merge_all_dip_violation_halts():
    results = [
        {"id": "A.1", "score": 0.99, "dip_violation": True},
        {"id": "A.2", "score": 0.95, "dip_violation": True},
    ]
    rc, out = _run_merge(results, mode="competition")
    assert rc != 0
    assert out.get("halt") is True
