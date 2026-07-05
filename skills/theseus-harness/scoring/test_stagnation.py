"""stagnation.py 테스트 — 정체 감지 알고리즘의 객관 검증."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

STAG = Path(__file__).parent / "stagnation.py"


def _run(history: dict, **flags) -> tuple[int, dict]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(history, f)
        path = Path(f.name)
    args = [sys.executable, str(STAG), "--history", str(path)]
    for k, v in flags.items():
        if isinstance(v, bool):
            if v:
                args.append(f"--{k.replace('_', '-')}")
        else:
            args += [f"--{k.replace('_', '-')}", str(v)]
    proc = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, json.loads(proc.stdout)


def _hist(scores: list[float], **dims) -> dict:
    return {"sprint_scores": scores, "dim_history": dict(dims), "threshold": 0.999}


def test_no_stagnation_when_steady_climb():
    rc, out = _run(_hist([0.85, 0.90, 0.95], correctness=[0.8, 0.9, 1.0]))
    assert rc == 0
    assert out["report"]["recommended_action"] == "extend"
    assert out["report"]["stagnation_overall"] is False


def test_overall_plateau_is_stop_signal_non_gating():
    # 설계 B2 §2.2-4 — plateau 는 정지 신호(비게이팅). exit 0, stop_signal True.
    rc, out = _run(_hist([0.910, 0.912, 0.913], correctness=[0.95, 0.95, 0.95]))
    assert rc == 0  # 보고 모드 — 점수 절대값은 게이트가 아니다
    assert out["report"]["stagnation_overall"] is True
    assert out["report"]["stop_signal"] is True
    assert out["report"]["last_delta"] is not None
    assert out["report"]["recommended_action"] == "rewrite_full"


def test_plateau_decoupled_from_absolute_score():
    """절대 점수가 낮아도(0.999 미달) plateau 판정은 delta 만으로 — 임계 분리(§2.2-4)."""
    # 점수가 0.999 훨씬 미달(0.60 대)이라도 delta<eps 면 plateau=정지 신호.
    rc, out = _run(_hist([0.601, 0.602, 0.603], correctness=[0.60, 0.60, 0.60]))
    assert rc == 0
    assert out["report"]["stagnation_overall"] is True
    assert out["report"]["stop_signal"] is True


def test_dim_stagnation_reports_module_advice_non_gating():
    rc, out = _run(
        _hist(
            [0.95, 0.96, 0.97],
            correctness=[0.99, 0.99, 0.99],
            coverage=[0.85, 0.85, 0.85],   # 정체 + < 0.95
            e2e_pass=[0.90, 0.95, 1.0],    # 건강
        )
    )
    assert rc == 0  # 보고 모드(비게이팅) — 차원 정체는 조언 데이터
    assert out["report"]["stagnation_overall"] is False
    assert any(d["dim"] == "coverage" for d in out["report"]["stagnant_dims"])
    assert out["report"]["recommended_action"] == "rewrite_module"


def test_high_score_microvariation_not_stagnation():
    """0.95 이상 미세 변동은 정체로 판정 안 함 — 마지막 미세 조정 단계."""
    rc, out = _run(
        _hist(
            [0.96, 0.961, 0.962],
            correctness=[0.97, 0.97, 0.97],     # > 0.95 → 정체 아님
            coverage=[0.97, 0.97, 0.97],
        )
    )
    # 종합 점수가 0.999 미달이므로 종합 정체는 트리거 가능
    # 단 차원 정체는 < 0.95 임계 미적용
    assert all(d["dim"] not in {"correctness", "coverage"}
               for d in out["report"]["stagnant_dims"])


def test_short_history_no_stagnation():
    """window 미달 (2 스프린트) 이면 정체 판단 안 함."""
    rc, out = _run(_hist([0.91, 0.91], correctness=[0.95, 0.95]))
    assert rc == 0
    assert out["report"]["stagnation_overall"] is False


def test_lesson_pack_includes_rewrite_rule():
    rc, out = _run(
        _hist([0.910, 0.912, 0.913], correctness=[0.95, 0.95, 0.95]),
        lesson_pack=True,
    )
    assert rc == 0  # 보고 모드(비게이팅)
    pack = out["lesson_pack"]
    assert pack["recommended_action"] == "rewrite_full"
    assert pack["rewrite_rule"]["preserve"] is False
    assert pack["rewrite_rule"]["start_from"] == "phase-06-replan"
    # delta_to_threshold(도달 불가 임계 거리)는 last_delta(직전 대비 실측)로 교체됨.
    assert "last_delta" in pack
    assert "delta_to_threshold" not in pack


def test_lesson_pack_module_rewrite():
    rc, out = _run(
        _hist(
            [0.95, 0.96, 0.97],
            correctness=[0.99, 0.99, 0.99],
            coverage=[0.85, 0.85, 0.85],
        ),
        lesson_pack=True,
    )
    assert rc == 0  # 보고 모드(비게이팅)
    pack = out["lesson_pack"]
    assert pack["recommended_action"] == "rewrite_module"
    assert pack["rewrite_rule"]["preserve"] is False
    assert pack["rewrite_rule"]["start_from"] == "fresh-impl"
    assert "coverage" in pack["stagnation"]["stagnant_dims"]
