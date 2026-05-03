#!/usr/bin/env python3
"""
Plan tree tournament — 우주별 점수 + auto_resolve 헬퍼.

[`../conventions/plan-tree.md`](../conventions/plan-tree.md) 의 자율 결정 룰 +
[`../conventions/competition.md`](../conventions/competition.md) 의 auto_resolve
알고리즘을 그대로 재사용:

  - Δ ≥ 0.05            → SELECT  (top 우주 채택, 패자는 losers/ 로)
  - 0.02 ≤ Δ < 0.05     → 차원별 분석 → 모든 차원 우위면 SELECT, 분점이면 MERGE_BY_DIMENSION
  - Δ < 0.02            → AUTO_MERGE (simplicity 우위 base, 다른 우주의 차별 강점 머지)
  - 모든 우주 cold_recall < 0.6 → HALT_AND_ASK_USER (의도 자체 모호 → 페이즈 04 회귀)

cold_recall < 0.6 인 우주는 점수 무관 즉시 탈락.

산출물:
  - .ShipofTheseus/<프로젝트>/plan/tournament.md  (사용자 대면 단일 audit)
  - 각 우주 meta.md 의 status 필드 갱신 (winner / runner_up / loser / merged)

사용법:
    tournament.py resolve --plan-root <path>
    tournament.py score --universe <path>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# 5 차원 가중치 (plan-tree.md §토너먼트 채점)
WEIGHTS: dict[str, float] = {
    "cold_recall": 0.30,
    "dip_strictness": 0.25,
    "simplicity": 0.20,
    "test_topology": 0.15,
    "fe_be_parity": 0.10,
}

COLD_RECALL_DISQUALIFY = 0.6  # plan-tree.md §"cold_recall < 0.6 즉시 탈락"
DELTA_SELECT = 0.05           # SELECT 임계
DELTA_AUTO_MERGE = 0.02       # AUTO_MERGE 임계


@dataclass
class UniverseScore:
    universe_id: str
    seed: str
    cold_recall: float
    dip_strictness: float
    simplicity: float
    test_topology: float
    fe_be_parity: float
    path: Path

    @property
    def overall(self) -> float:
        return sum(getattr(self, dim) * w for dim, w in WEIGHTS.items())

    @property
    def disqualified(self) -> bool:
        return self.cold_recall < COLD_RECALL_DISQUALIFY


@dataclass
class Resolution:
    kind: str  # SELECT / MERGE_BY_DIMENSION / AUTO_MERGE / HALT_AND_ASK_USER
    winner: UniverseScore | None = None
    runner_up: UniverseScore | None = None
    losers: list[UniverseScore] = field(default_factory=list)
    delta: float = 0.0
    rule: str = ""  # 어떤 룰이 적용됐는지 한 줄
    merge_dims: dict[str, str] = field(default_factory=dict)  # dim → universe_id


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_frontmatter(text: str) -> dict[str, str]:
    """간단한 YAML frontmatter 추출 — score 의 5 차원 + universe_id + seed."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    body = text[3:end]
    out: dict[str, str] = {}
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip().strip('"\'')
    return out


def load_universe(meta_path: Path) -> UniverseScore:
    """우주의 meta.md 에서 score 를 로드."""
    if not meta_path.exists():
        raise FileNotFoundError(f"{meta_path} 누락 — 우주 meta.md 가 없음")
    text = _read(meta_path)

    # frontmatter 와 별개로 score: 블록 (들여쓴 multi-line) 도 파싱
    fm = _parse_frontmatter(text)
    universe_id = fm.get("universe_id", meta_path.parent.name)
    seed = fm.get("seed", "unknown")

    score: dict[str, float] = {}
    in_score_block = False
    for line in text.splitlines():
        if line.startswith("score:"):
            in_score_block = True
            continue
        if in_score_block:
            if not line.startswith(("  ", "\t")) or ":" not in line:
                in_score_block = False
                continue
            key, _, val = line.strip().partition(":")
            try:
                score[key.strip()] = float(val.strip())
            except ValueError:
                continue

    def _g(name: str) -> float:
        v = score.get(name, fm.get(name, "0"))
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    return UniverseScore(
        universe_id=universe_id,
        seed=seed,
        cold_recall=_g("cold_recall"),
        dip_strictness=_g("dip_strictness"),
        simplicity=_g("simplicity"),
        test_topology=_g("test_topology"),
        fe_be_parity=_g("fe_be_parity"),
        path=meta_path.parent,
    )


def load_all_universes(plan_root: Path) -> list[UniverseScore]:
    """plan/candidates/universe-*/meta.md 모두 로드 (자식 우주 children/ 제외)."""
    candidates = plan_root / "candidates"
    if not candidates.exists():
        return []
    universes: list[UniverseScore] = []
    for u_dir in sorted(candidates.iterdir()):
        if not u_dir.is_dir() or u_dir.name == "losers":
            continue
        meta = u_dir / "meta.md"
        if meta.exists():
            universes.append(load_universe(meta))
    return universes


def resolve(universes: list[UniverseScore]) -> Resolution:
    """auto_resolve 알고리즘 — competition.md §자동 resolve 와 동일."""
    qualified = [u for u in universes if not u.disqualified]
    if not qualified:
        return Resolution(
            kind="HALT_AND_ASK_USER",
            rule="모든 우주 cold_recall < 0.6 — 의도 자체 모호 → 페이즈 04 회귀",
            losers=universes,
        )

    qualified.sort(key=lambda u: u.overall, reverse=True)
    top = qualified[0]
    if len(qualified) == 1:
        return Resolution(
            kind="SELECT",
            winner=top,
            losers=[u for u in universes if u is not top],
            delta=1.0,
            rule="단일 우주 자격 — 자동 채택",
        )

    runner = qualified[1]
    delta = top.overall - runner.overall

    # 압도적 우위 — SELECT
    if delta >= DELTA_SELECT:
        return Resolution(
            kind="SELECT",
            winner=top,
            runner_up=runner,
            losers=[u for u in universes if u is not top],
            delta=delta,
            rule=f"Δ {delta:.3f} ≥ {DELTA_SELECT} — SELECT (top 채택, 나머지 losers/ 로)",
        )

    # 사실상 동등 — AUTO_MERGE
    if delta < DELTA_AUTO_MERGE:
        # simplicity 우위 우주를 base 로
        simpler = max((top, runner), key=lambda u: u.simplicity)
        merge_from = top if simpler is runner else runner
        return Resolution(
            kind="AUTO_MERGE",
            winner=simpler,
            runner_up=merge_from,
            losers=[u for u in universes if u not in (simpler, merge_from)],
            delta=delta,
            rule=f"Δ {delta:.3f} < {DELTA_AUTO_MERGE} — AUTO_MERGE (simplicity 우위 base)",
        )

    # 중간 영역 — 차원별 분석
    dims = list(WEIGHTS.keys())
    dim_winners = {d: max(qualified, key=lambda u: getattr(u, d)) for d in dims}
    if all(w is top for w in dim_winners.values()):
        return Resolution(
            kind="SELECT",
            winner=top,
            runner_up=runner,
            losers=[u for u in universes if u is not top],
            delta=delta,
            rule=f"Δ {delta:.3f} 중간이지만 모든 차원 top 우위 — SELECT",
        )
    return Resolution(
        kind="MERGE_BY_DIMENSION",
        winner=top,
        runner_up=runner,
        losers=[u for u in universes if u is not top],
        delta=delta,
        rule=f"Δ {delta:.3f} 중간 + 차원 분점 — MERGE_BY_DIMENSION",
        merge_dims={d: u.universe_id for d, u in dim_winners.items()},
    )


def render_tournament_md(universes: list[UniverseScore], resolution: Resolution) -> str:
    """plan/tournament.md 본문 생성."""
    lines: list[str] = []
    lines.append("# 플랜 토너먼트")
    lines.append("")
    lines.append("## 우주 카탈로그")
    lines.append("")
    header = "| 우주 | 시드 | cold_recall | dip_strictness | simplicity | test_topology | fe_be_parity | 종합 | 자격 |"
    sep = "|---|---|---:|---:|---:|---:|---:|---:|:-:|"
    lines.extend([header, sep])
    for u in sorted(universes, key=lambda x: x.overall, reverse=True):
        ok = "✗" if u.disqualified else "✓"
        lines.append(
            f"| {u.universe_id} | {u.seed} | {u.cold_recall:.3f} | {u.dip_strictness:.3f} | "
            f"{u.simplicity:.3f} | {u.test_topology:.3f} | {u.fe_be_parity:.3f} | "
            f"**{u.overall:.3f}** | {ok} |"
        )
    lines.append("")
    lines.append(f"## 결정: {resolution.kind}")
    lines.append("")
    lines.append(f"- **룰**: {resolution.rule}")
    lines.append(f"- **Δ**: {resolution.delta:.4f}")
    if resolution.winner:
        lines.append(f"- **우승**: {resolution.winner.universe_id} (시드 {resolution.winner.seed}, 종합 {resolution.winner.overall:.3f})")
    if resolution.runner_up:
        lines.append(f"- **차점**: {resolution.runner_up.universe_id} (종합 {resolution.runner_up.overall:.3f})")
    if resolution.merge_dims:
        lines.append("")
        lines.append("### 차원별 우위 (MERGE_BY_DIMENSION)")
        for d, uid in resolution.merge_dims.items():
            lines.append(f"- {d}: {uid}")
    if resolution.losers:
        lines.append("")
        lines.append("### 패자 우주")
        for u in resolution.losers:
            reason = "cold_recall < 0.6 (자격 미달)" if u.disqualified else "Δ 차이"
            lines.append(f"- {u.universe_id} — {reason}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_resolve = sub.add_parser("resolve", help="모든 우주 로드 + auto_resolve + tournament.md 작성")
    p_resolve.add_argument("--plan-root", type=Path, required=True, help=".ShipofTheseus/<프로젝트>/plan/")
    p_resolve.add_argument("--out", type=Path, default=None, help="기본: <plan-root>/tournament.md")

    p_score = sub.add_parser("score", help="단일 우주 score 계산 (디버깅용)")
    p_score.add_argument("--universe", type=Path, required=True, help="universe-N/ 디렉터리")

    args = parser.parse_args(argv)

    if args.cmd == "resolve":
        universes = load_all_universes(args.plan_root)
        if not universes:
            print(json.dumps({"error": "no universes found", "plan_root": str(args.plan_root)}, ensure_ascii=False))
            return 2
        resolution = resolve(universes)
        out = args.out or (args.plan_root / "tournament.md")
        out.write_text(render_tournament_md(universes, resolution), encoding="utf-8")
        print(json.dumps({
            "kind": resolution.kind,
            "winner": resolution.winner.universe_id if resolution.winner else None,
            "delta": resolution.delta,
            "out": str(out),
        }, ensure_ascii=False))
        return 0

    if args.cmd == "score":
        u = load_universe(args.universe / "meta.md")
        print(json.dumps({
            "universe_id": u.universe_id,
            "seed": u.seed,
            "overall": u.overall,
            "disqualified": u.disqualified,
            "scores": {d: getattr(u, d) for d in WEIGHTS},
        }, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
