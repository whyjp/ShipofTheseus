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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(payload, f)
        path = Path(f.name)
    proc = subprocess.run(
        [sys.executable, str(CEILING), "--measurements", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
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


def test_policy_actions_mapped_when_ceiling():
    """천정 도달 시 user_options(인터럽트) 대신 policy_actions(autonomy.md Q-D3 매핑) 반환."""
    rc, out = _run([340, 342, 341], threshold=200, ceiling=350, metric="p99_ms")
    assert rc == 1
    assert "policy_actions" in out
    # 4 정책 모두 포함 (default 1, 업그레이드 2, 단순화 3, 정체 수용 4)
    assert set(out["policy_actions"].keys()) == {"1", "2", "3", "4"}
    assert out["policy_actions"]["1"]["action"] == "set_threshold"
    assert out["policy_actions"]["1"]["value"] == out["recommended_threshold"]
    # 인터럽트 없음 — user_options 키는 없어야 함 (인터뷰 후 ack 금지)
    assert "user_options" not in out
