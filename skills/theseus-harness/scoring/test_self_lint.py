"""self_lint pytest wrap — 본 저장소가 자기 lint 를 통과하는지 매 PR 검증.

실행: python -m pytest scoring/test_self_lint.py -q
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SELF_LINT = Path(__file__).parent / "self_lint.py"


def _run_lint() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SELF_LINT)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(proc.stdout)


def _run_score() -> dict:
    proc = subprocess.run(
        [sys.executable, str(SELF_LINT), "--score"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(proc.stdout)


def test_all_lint_checks_pass():
    out = _run_lint()
    fails = [c for c in out["checks"] if not c["ok"]]
    assert out["all_ok"], f"lint fails: {fails}"


def test_lint_check_count_at_least_18():
    """체크 개수 회귀 방지 — 새 체크 추가는 가능, 제거는 사람 리뷰 필요."""
    out = _run_lint()
    assert len(out["checks"]) >= 18


def test_self_score_meets_99999():
    out = _run_score()
    assert out["passes_threshold_99999"], (
        f"self_score={out['self_score']} 가 임계 0.99999 미달. "
        f"lint={out['lint_pass']}/{out['lint_total']}, "
        f"pytest={out['pytest_pass']}/{out['pytest_total']}, "
        f"sample={out['sample_score']}"
    )


def test_lint_score_is_perfect():
    out = _run_score()
    assert out["lint_score"] == 1.0, f"lint_score={out['lint_score']} 가 1.0 미달"
