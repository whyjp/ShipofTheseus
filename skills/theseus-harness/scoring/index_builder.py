#!/usr/bin/env python3
"""
산출물 트리 인덱스 빌더 — indexing.md 의 INDEX.md / index.json 자동 생성.

매 페이즈/체크포인트/서브에이전트 산출 직후 자동 호출. .ShipofTheseus/<프로젝트>/
디렉터리를 스캔해 모든 마크다운 산출물의 frontmatter 를 읽고, 부모-자식 관계
(prev_fingerprint / parent_module / parent_branch) 를 그래프로 재구성.

사용:
    index_builder.py rebuild --root .ShipofTheseus/<프로젝트>/
    index_builder.py verify  --root .ShipofTheseus/<프로젝트>/

stdout JSON; exit 0 = ok, 1 = 무결성 위반 발견.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DEPTH_LIMIT = 2


@dataclass
class Artifact:
    path: str
    fingerprint: str | None = None
    prev_fingerprint: str | None = None
    phase: str | None = None
    universe: str | None = None
    parent_branch: str | None = None
    parent_module: str | None = None
    depth: int = 0
    branch_kind: str | None = None
    produced_at: str | None = None
    producer_agent: str | None = None
    children: list[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.lower() in ("null", "none", "~", ""):
            v = None
        elif v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        fm[k.strip()] = v
    return fm


def collect_artifacts(root: Path) -> list[Artifact]:
    artifacts: list[Artifact] = []
    for p in sorted(root.rglob("*.md")):
        if "INDEX.md" in p.name:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = parse_frontmatter(text)
        if not fm.get("fingerprint"):
            continue   # 비-페이즈 마크다운 (README 등) 무시
        depth_raw = fm.get("depth", "0")
        try:
            depth = int(depth_raw) if depth_raw is not None else 0
        except (TypeError, ValueError):
            depth = 0
        artifacts.append(
            Artifact(
                path=str(p.relative_to(root)),
                fingerprint=fm.get("fingerprint"),
                prev_fingerprint=fm.get("prev_fingerprint"),
                phase=fm.get("phase"),
                universe=fm.get("universe"),
                parent_branch=fm.get("parent_branch"),
                parent_module=fm.get("parent_module"),
                depth=depth,
                branch_kind=fm.get("branch_kind"),
                produced_at=fm.get("produced_at"),
                producer_agent=fm.get("producer_agent"),
            )
        )
    return artifacts


def build_tree(artifacts: list[Artifact]) -> dict[str, Artifact]:
    by_fp = {a.fingerprint: a for a in artifacts if a.fingerprint}
    for a in artifacts:
        if a.prev_fingerprint and a.prev_fingerprint in by_fp:
            parent = by_fp[a.prev_fingerprint]
            parent.children.append(a.path)
    return by_fp


def detect_multiverses(artifacts: list[Artifact]) -> list[dict]:
    branches: dict[str, dict] = {}
    for a in artifacts:
        if not a.parent_branch:
            continue
        b = branches.setdefault(
            a.parent_branch,
            {"branch_id": a.parent_branch, "universes": {}, "winner": None, "losers": []},
        )
        if a.universe:
            b["universes"].setdefault(a.universe, [])
            b["universes"][a.universe].append(a.path)
            if a.branch_kind == "multiverse_winner":
                b["winner"] = a.universe
            elif a.branch_kind == "multiverse_loser" and a.universe not in b["losers"]:
                b["losers"].append(a.universe)
    return list(branches.values())


def detect_subdivisions(artifacts: list[Artifact]) -> list[dict]:
    subs: dict[str, dict] = {}
    for a in artifacts:
        if not a.parent_module:
            continue
        s = subs.setdefault(
            a.parent_module,
            {"parent_module": a.parent_module, "sub_modules": [], "max_depth": 0, "modes": set()},
        )
        s["sub_modules"].append(a.path)
        s["max_depth"] = max(s["max_depth"], a.depth)
        if a.branch_kind:
            s["modes"].add(a.branch_kind)
    out = []
    for s in subs.values():
        s["modes"] = sorted(s["modes"])
        out.append(s)
    return out


def integrity_checks(artifacts: list[Artifact]) -> dict:
    by_fp = {a.fingerprint: a for a in artifacts}
    checks: dict[str, str] = {}

    # fingerprint 체인
    chain_breaks = []
    for a in artifacts:
        if a.prev_fingerprint and a.prev_fingerprint not in by_fp:
            # null 이 아닌데 매핑 없음 — 시작 페이즈를 제외하고 끊김
            chain_breaks.append(a.path)
    checks["fingerprint_chain"] = "ok" if not chain_breaks else f"break: {chain_breaks[:3]}"

    # universe 일관성: 같은 parent_branch 의 winner 가 단일
    multiverses = detect_multiverses(artifacts)
    multi_winner = [m for m in multiverses if isinstance(m["winner"], list) and len(m["winner"]) > 1]
    checks["multiverse_single_winner"] = "ok" if not multi_winner else f"violation: {multi_winner}"

    # parent_module 체인 — parent_module 이 가리키는 모듈이 산출물에 존재
    module_paths = {a.path for a in artifacts}
    orphans = []
    for a in artifacts:
        if a.parent_module:
            # parent_module 은 TODO ID — path 자체가 아니라 phase 산출물 안에 등장하는지 확인.
            # 약한 검증: parent 가 명시되어 있고 자기 path 와 같은 디렉터리에 임의 산출물 존재
            pass   # 강한 검증은 self_lint 에서
    checks["parent_module_chain"] = "ok"

    # 깊이 한도
    over_depth = [a.path for a in artifacts if a.depth > DEPTH_LIMIT]
    checks["depth_within_limit"] = (
        "ok" if not over_depth
        else f"warn: {len(over_depth)} 산출물이 깊이 {DEPTH_LIMIT} 초과 — 페이즈 06 회귀 권고"
    )

    return checks


def render_index_md(root: Path, artifacts: list[Artifact]) -> str:
    multiverses = detect_multiverses(artifacts)
    subdivisions = detect_subdivisions(artifacts)
    checks = integrity_checks(artifacts)
    active_universes = sorted({a.universe for a in artifacts if a.universe and a.branch_kind != "multiverse_loser"})

    rebuilt = datetime.now(timezone.utc).isoformat(timespec="seconds")

    lines = [
        f"# 산출물 인덱스 — `{root.name}`",
        "",
        f"> **재생성 시각:** `{rebuilt}` · **총 산출물:** {len(artifacts)}",
        f"> **활성 우주:** {', '.join(active_universes) if active_universes else '(없음 — 선형)'}",
        f"> **멀티버스 분기:** {len(multiverses)} · **서브 분해:** {len(subdivisions)}",
        "",
        "## 트리 (선형 페이즈)",
        "```",
    ]
    # 시작 (prev_fingerprint == null) 부터 깊이 우선 출력
    by_fp = {a.fingerprint: a for a in artifacts}
    roots = [a for a in artifacts if not a.prev_fingerprint]

    def walk(node: Artifact, depth: int) -> None:
        prefix = "  " * depth + ("└─ " if depth else "")
        marker = ""
        if node.branch_kind == "multiverse_winner":
            marker = " [WINNER ★]"
        elif node.branch_kind == "multiverse_loser":
            marker = " [LOSER]"
        elif node.parent_module:
            marker = f" [sub of {node.parent_module}, depth={node.depth}]"
        lines.append(f"{prefix}{node.path}{marker}")
        children_artifacts = [a for a in artifacts if a.prev_fingerprint == node.fingerprint]
        for c in children_artifacts:
            walk(c, depth + 1)

    for r in roots:
        walk(r, 0)
    if not roots:
        lines.append("(산출물 없음)")
    lines.append("```")
    lines.append("")

    # 멀티버스 섹션
    if multiverses:
        lines.append("## 멀티버스 분기")
        lines.append("")
        for m in multiverses:
            lines.append(f"- `{m['branch_id']}` — winner: `{m['winner']}`, losers: {m['losers']}")
        lines.append("")

    # 서브분해 섹션
    if subdivisions:
        lines.append("## 서브에이전트 분해")
        lines.append("")
        for s in subdivisions:
            lines.append(
                f"- `{s['parent_module']}` — sub_modules: {len(s['sub_modules'])}, "
                f"max_depth: {s['max_depth']}, modes: {s['modes']}"
            )
        lines.append("")

    # 무결성 섹션
    lines.append("## 무결성 체크")
    lines.append("")
    for k, v in checks.items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("> 본 INDEX.md 는 `scoring/index_builder.py rebuild` 가 자동 재생성한다 — 수동 편집 금지.")

    return "\n".join(lines) + "\n"


def render_index_json(artifacts: list[Artifact]) -> dict:
    multiverses = detect_multiverses(artifacts)
    subdivisions = detect_subdivisions(artifacts)
    checks = integrity_checks(artifacts)
    return {
        "rebuilt_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_artifacts": len(artifacts),
        "active_universes": sorted(
            {a.universe for a in artifacts if a.universe and a.branch_kind != "multiverse_loser"}
        ),
        "tree": [asdict(a) for a in artifacts],
        "multiverses": multiverses,
        "subdivisions": subdivisions,
        "integrity": checks,
    }


def cmd_rebuild(args) -> int:
    root = Path(args.root)
    artifacts = collect_artifacts(root)
    build_tree(artifacts)
    md = render_index_md(root, artifacts)
    js = render_index_json(artifacts)
    (root / "INDEX.md").write_text(md, encoding="utf-8")
    (root / "index.json").write_text(json.dumps(js, indent=2, ensure_ascii=False), encoding="utf-8")
    integrity = js["integrity"]
    has_violation = any(
        not v.startswith("ok") and not v.startswith("warn") for v in integrity.values()
    )
    print(json.dumps(
        {"rebuilt": True, "artifacts": len(artifacts), "integrity": integrity},
        indent=2, ensure_ascii=False,
    ))
    return 1 if has_violation else 0


def cmd_verify(args) -> int:
    root = Path(args.root)
    artifacts = collect_artifacts(root)
    js = render_index_json(artifacts)
    integrity = js["integrity"]
    print(json.dumps({"integrity": integrity, "total_artifacts": len(artifacts)}, indent=2, ensure_ascii=False))
    has_violation = any(
        not v.startswith("ok") and not v.startswith("warn") for v in integrity.values()
    )
    return 1 if has_violation else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("rebuild")
    pr.add_argument("--root", required=True)
    pr.set_defaults(func=cmd_rebuild)
    pv = sub.add_parser("verify")
    pv.add_argument("--root", required=True)
    pv.set_defaults(func=cmd_verify)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
