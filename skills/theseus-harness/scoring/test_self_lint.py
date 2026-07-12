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


def test_self_score_reports_without_99999_gate():
    """설계 B2 §2.3 — self_score 는 보고 전용, 판정 권위는 all_ok(값 boolean).

    구 0.99999 게이트(passes_threshold_99999)는 도달 불가 임계라 perverse incentive
    (점수 인플레이션 유인)를 만들었다 — 필드째 폐지했으므로 부재를 값으로 확인한다.
    """
    out = _run_score()
    assert "passes_threshold_99999" not in out, "0.99999 게이트 필드가 잔존 — 보고모드 위반"
    assert isinstance(out["self_score"], (int, float))
    assert out["all_ok"], (
        f"all_ok=False — lint={out['lint_pass']}/{out['lint_total']}, "
        f"pytest={out['pytest_pass']}/{out['pytest_total']}, "
        f"sample={out['sample_score']}"
    )


def test_lint_score_is_perfect():
    out = _run_score()
    assert out["lint_score"] == 1.0, f"lint_score={out['lint_score']} 가 1.0 미달"


def test_review_and_should_stop_wiring_guards_bite(tmp_path):
    """C-RDL/C-SSW (v0.9.54 P1-A) 가 배선 누락 시 실제로 FAIL 하는지 — 무장 게이트 미급식 차단.

    가짜 skill_root(키워드 없는 stub)에서는 issue 반환, 실 skill_root(배선 존재)에서는 통과.
    """
    import self_lint

    (tmp_path / "phases").mkdir()
    (tmp_path / "conventions").mkdir()
    (tmp_path / "phases" / "03-independent-comprehension.md").write_text("cold reunderstanding", encoding="utf-8")
    (tmp_path / "phases" / "10-test-loop.md").write_text("sprint loop", encoding="utf-8")
    (tmp_path / "conventions" / "intra-phase-dacapo-loop.md").write_text("dacapo", encoding="utf-8")

    # 배선 부재 → 가드가 issue 반환(truthy).
    assert self_lint.check_review_dispatch_log_wired(tmp_path)
    assert self_lint.check_should_stop_wired(tmp_path)

    # 실 저장소(배선 존재) → 통과(빈 리스트).
    real = Path(self_lint.__file__).resolve().parents[1]
    assert self_lint.check_review_dispatch_log_wired(real) == []
    assert self_lint.check_should_stop_wired(real) == []


def test_multiverse_width_wiring_guard_bites(tmp_path):
    """C-MFW (B1 v0.9.56) 가 배선 누락 시 실제로 FAIL 하는지 — 무장 폭 게이트 미급식 차단.

    manifest 가 multiverse.fan_out_width 를 선언해도 run_gate 가 producer 를 안 부르면
    영구 evidence_missing FAIL 이므로, 러너 배선(declared=invoked)을 가드가 강제한다.
    """
    import self_lint

    (tmp_path / "scoring").mkdir()
    (tmp_path / "scoring" / "run_gate.py").write_text("# producer 미배선 stub\n", encoding="utf-8")

    # 배선 부재 → 가드가 issue 반환(truthy).
    assert self_lint.check_multiverse_width_wired(tmp_path)

    # 실 저장소(배선 존재) → 통과(빈 리스트).
    real = Path(self_lint.__file__).resolve().parents[1]
    assert self_lint.check_multiverse_width_wired(real) == []
