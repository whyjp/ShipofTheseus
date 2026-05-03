"""tournament.py — 5 차원 점수 + auto_resolve 룰 검증."""

from __future__ import annotations

from pathlib import Path

import pytest

from tournament import (
    DELTA_AUTO_MERGE,
    DELTA_SELECT,
    UniverseScore,
    load_all_universes,
    load_universe,
    render_tournament_md,
    resolve,
)


def _u(uid: str, seed: str, **scores: float) -> UniverseScore:
    """테스트용 우주 — path 는 dummy, 점수는 키워드 인자."""
    defaults = {
        "cold_recall": 0.9,
        "dip_strictness": 0.9,
        "simplicity": 0.9,
        "test_topology": 0.9,
        "fe_be_parity": 0.9,
    }
    defaults.update(scores)
    return UniverseScore(
        universe_id=uid,
        seed=seed,
        path=Path("/tmp/dummy"),
        **defaults,
    )


def test_overall_uses_weights():
    u = _u("a", "domain-first")  # 모든 차원 0.9 → overall 0.9
    assert abs(u.overall - 0.9) < 1e-9


def test_disqualify_low_cold_recall():
    u = _u("a", "domain-first", cold_recall=0.5)
    assert u.disqualified

    u2 = _u("a", "domain-first", cold_recall=0.6)
    assert not u2.disqualified


def test_resolve_select_when_delta_large():
    a = _u("a", "domain-first", cold_recall=0.95, dip_strictness=0.95)
    b = _u("b", "adapter-first", cold_recall=0.7, simplicity=0.7)
    res = resolve([a, b])
    assert res.kind == "SELECT"
    assert res.winner.universe_id == "a"
    assert res.delta >= DELTA_SELECT


def test_resolve_auto_merge_when_delta_tiny():
    # 두 우주 동등 (Δ < 0.02), simplicity 만 살짝 다르게
    # simplicity 가중치 0.20 이므로 (0.95-0.90)*0.20 = 0.01 = Δ
    a = _u("a", "domain-first", simplicity=0.90)
    b = _u("b", "adapter-first", simplicity=0.95)
    res = resolve([a, b])
    assert res.kind == "AUTO_MERGE", f"expected AUTO_MERGE, got {res.kind} (Δ={res.delta:.4f})"
    # simplicity 우위 = b 가 base
    assert res.winner.universe_id == "b"
    assert res.delta < DELTA_AUTO_MERGE


def test_resolve_halt_when_all_disqualified():
    a = _u("a", "domain-first", cold_recall=0.4)
    b = _u("b", "adapter-first", cold_recall=0.5)
    res = resolve([a, b])
    assert res.kind == "HALT_AND_ASK_USER"
    assert res.winner is None


def test_resolve_merge_by_dimension_in_middle_zone():
    # Δ 중간 영역 (0.02 ≤ Δ < 0.05) + 차원 분점
    # a 가 cold_recall 우위, b 가 simplicity + test_topology 우위
    a = _u("a", "domain-first",
           cold_recall=0.99, dip_strictness=0.95, simplicity=0.7,
           test_topology=0.7, fe_be_parity=0.85)
    b = _u("b", "adapter-first",
           cold_recall=0.85, dip_strictness=0.93, simplicity=0.95,
           test_topology=0.92, fe_be_parity=0.85)
    res = resolve([a, b])
    # Δ 중간 — 차원 분점이면 MERGE_BY_DIMENSION, 아니면 SELECT
    assert res.kind in ("MERGE_BY_DIMENSION", "SELECT")
    if res.kind == "MERGE_BY_DIMENSION":
        assert "cold_recall" in res.merge_dims


def test_resolve_single_qualified():
    a = _u("a", "domain-first")
    b = _u("b", "adapter-first", cold_recall=0.4)  # disqualified
    res = resolve([a, b])
    assert res.kind == "SELECT"
    assert res.winner.universe_id == "a"
    # b 는 losers 에 포함
    assert any(u.universe_id == "b" for u in res.losers)


def test_render_tournament_md_basic_structure():
    a = _u("a", "domain-first")
    b = _u("b", "adapter-first", simplicity=0.95)
    res = resolve([a, b])
    md = render_tournament_md([a, b], res)
    assert "# 플랜 토너먼트" in md
    assert "우주 카탈로그" in md
    assert "결정: " + res.kind in md
    assert "domain-first" in md
    assert "adapter-first" in md


def test_load_universe_from_meta(tmp_path: Path):
    u_dir = tmp_path / "universe-1-domain-first"
    u_dir.mkdir()
    meta = u_dir / "meta.md"
    meta.write_text(
        "---\n"
        "universe_id: 1-domain-first\n"
        "seed: domain-first\n"
        "depth: 1\n"
        "score:\n"
        "  cold_recall: 0.92\n"
        "  dip_strictness: 0.95\n"
        "  simplicity: 0.78\n"
        "  test_topology: 0.90\n"
        "  fe_be_parity: 0.85\n"
        "  overall: 0.892\n"
        "---\n",
        encoding="utf-8",
    )
    u = load_universe(meta)
    assert u.universe_id == "1-domain-first"
    assert u.seed == "domain-first"
    assert abs(u.cold_recall - 0.92) < 1e-9
    assert abs(u.dip_strictness - 0.95) < 1e-9


def test_load_all_universes_skips_losers(tmp_path: Path):
    plan = tmp_path / "plan"
    cands = plan / "candidates"
    cands.mkdir(parents=True)

    # Active universe
    u1 = cands / "universe-1"
    u1.mkdir()
    (u1 / "meta.md").write_text(
        "---\nuniverse_id: 1\nseed: domain-first\nscore:\n"
        "  cold_recall: 0.9\n  dip_strictness: 0.9\n"
        "  simplicity: 0.9\n  test_topology: 0.9\n  fe_be_parity: 0.9\n---\n",
        encoding="utf-8",
    )

    # losers/ — 무시되어야 함
    losers = cands / "losers"
    losers.mkdir()
    (losers / "old.md").write_text("---\n---\n", encoding="utf-8")

    universes = load_all_universes(plan)
    assert len(universes) == 1
    assert universes[0].universe_id == "1"
