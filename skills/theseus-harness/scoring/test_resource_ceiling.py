"""resource_ceiling.py 테스트 — 천정 감지 + 자동 조정 권고 검증."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

CEILING = Path(__file__).parent / "resource_ceiling.py"


def _run(meas: list[float], threshold: float, ceiling: float, metric: str = "p99_ms") -> tuple[int, dict]:
    payload = {
        "measurements": meas,
        "current_threshold": threshold,
        "estimated_ceiling": ceiling,
        "metric": metric,
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        path = Path(f.name)
    proc = subprocess.run(
        [sys.executable, str(CEILING), "--measurements", str(path)],
        capture_output=True,
        text=True,
    )
    return proc.returncode, json.loads(proc.stdout)


def test_latency_ceiling_reached_recommends_adjustment():
    rc, out = _run([340, 342, 341], threshold=200, ceiling=350, metric="p99_ms")
    assert rc == 1
    assert out["near_ceiling"] is True
    assert out["recommended_threshold"] >= 340
    assert out["recommended_threshold"] <= 360
    assert out["ceiling_pct_actual"] >= 0.95


def test_latency_well_below_ceiling_no_adjustment():
    rc, out = _run([100, 105, 110], threshold=80, ceiling=350, metric="p99_ms")
    assert rc == 0
    assert out["near_ceiling"] is False


def test_high_variance_no_judgment():
    rc, out = _run([200, 350, 250], threshold=200, ceiling=350, metric="p99_ms")
    assert rc == 0
    assert out["near_ceiling"] is False
    assert "변동" in out["reason"]


def test_threshold_already_met_no_adjustment():
    rc, out = _run([180, 185, 182], threshold=200, ceiling=350, metric="p99_ms")
    assert rc == 0
    assert out["near_ceiling"] is False


def test_short_history_returns_false():
    rc, out = _run([340, 342], threshold=200, ceiling=350, metric="p99_ms")
    assert rc == 0
    assert out["near_ceiling"] is False


def test_throughput_metric_supported():
    # RPS 천정 700, 측정 ~640 이면 천정의 91% — 근접
    rc, out = _run([640, 642, 638], threshold=800, ceiling=700, metric="rps")
    assert rc == 1
    assert out["near_ceiling"] is True
    # throughput 권고는 측정의 95% (안전 하향)
    assert 600 <= out["recommended_threshold"] <= 640


def test_user_options_included_when_ceiling():
    rc, out = _run([340, 342, 341], threshold=200, ceiling=350, metric="p99_ms")
    assert rc == 1
    assert "user_options" in out
    assert len(out["user_options"]) == 4
    assert any("리소스 업그레이드" in o for o in out["user_options"])
