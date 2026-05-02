"""index_builder.py 테스트 — 산출물 트리 인덱스 + 비직렬성 메타 검증."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

BUILDER = Path(__file__).parent / "index_builder.py"


def _make_artifact(root: Path, rel: str, fp: str, prev: str | None, **extra) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    fm_lines = ["---", "skill_name: theseus-harness", "skill_version: 0.2.0",
                f"phase: {extra.get('phase', '01-intent')}",
                f"fingerprint: {fp}",
                f"prev_fingerprint: {prev or 'null'}",
                f"produced_at: 2026-05-01T00:00:00Z"]
    for k in ("universe", "parent_branch", "parent_module", "branch_kind", "depth"):
        if k in extra:
            fm_lines.append(f"{k}: {extra[k] if extra[k] is not None else 'null'}")
    fm_lines.append("---")
    body = "\n".join(fm_lines) + "\n\n# Test artifact\n\nbody\n"
    p.write_text(body, encoding="utf-8")
    return p


def _run(cmd: str, root: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(BUILDER), cmd, "--root", str(root)],
        capture_output=True, text=True,
    )
    return proc.returncode, json.loads(proc.stdout)


def test_linear_chain_builds_index():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "naming/00-naming.md", "sha256:a1", None, phase="00-naming")
    _make_artifact(root, "intent/01-intent.md", "sha256:b1", "sha256:a1", phase="01-intent")
    _make_artifact(root, "plan/06-plan.md", "sha256:c1", "sha256:b1", phase="06-plan")

    rc, out = _run("rebuild", root)
    assert rc == 0
    assert out["artifacts"] == 3
    # INDEX.md 와 index.json 생성됨
    assert (root / "INDEX.md").exists()
    assert (root / "index.json").exists()
    # 무결성 ok
    integrity = json.loads((root / "index.json").read_text())["integrity"]
    assert integrity["fingerprint_chain"] == "ok"


def test_multiverse_branch_with_winner_loser():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "intent/01-intent.md", "sha256:a1", None, phase="01-intent")
    _make_artifact(root, "plan/06-plan.md", "sha256:b1", "sha256:a1", phase="06-plan")
    # 3 우주 분기
    _make_artifact(root, "multiverse/06-plan/universe-a/plan.md", "sha256:wa",
                   "sha256:b1", phase="06-plan",
                   universe="a", parent_branch="06-plan", branch_kind="multiverse_winner")
    _make_artifact(root, "multiverse/06-plan/universe-b/plan.md", "sha256:wb",
                   "sha256:b1", phase="06-plan",
                   universe="b", parent_branch="06-plan", branch_kind="multiverse_loser")
    _make_artifact(root, "multiverse/06-plan/universe-c/plan.md", "sha256:wc",
                   "sha256:b1", phase="06-plan",
                   universe="c", parent_branch="06-plan", branch_kind="multiverse_loser")

    rc, out = _run("rebuild", root)
    assert rc == 0
    js = json.loads((root / "index.json").read_text())
    assert len(js["multiverses"]) == 1
    mv = js["multiverses"][0]
    assert mv["winner"] == "a"
    assert sorted(mv["losers"]) == ["b", "c"]
    assert "a" in js["active_universes"]
    assert "b" not in js["active_universes"]   # loser 는 활성 아님


def test_subdivision_tree_recorded():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "impl/08-impl-log.md", "sha256:i1", None, phase="08-implement")
    _make_artifact(root, "impl/T-020/sub/A.1/code.md", "sha256:s1",
                   "sha256:i1", phase="08-implement",
                   parent_module="T-020", depth=1, branch_kind="sub_parallel")
    _make_artifact(root, "impl/T-020/sub/A.2/code.md", "sha256:s2",
                   "sha256:i1", phase="08-implement",
                   parent_module="T-020", depth=1, branch_kind="sub_parallel")

    rc, out = _run("rebuild", root)
    assert rc == 0
    js = json.loads((root / "index.json").read_text())
    assert len(js["subdivisions"]) == 1
    sd = js["subdivisions"][0]
    assert sd["parent_module"] == "T-020"
    assert sd["max_depth"] == 1
    assert "sub_parallel" in sd["modes"]


def test_depth_over_limit_warns():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "impl/08-impl-log.md", "sha256:i1", None, phase="08-implement")
    _make_artifact(root, "impl/T-020/sub/A/sub/B/code.md", "sha256:d3",
                   "sha256:i1", phase="08-implement",
                   parent_module="T-020", depth=3, branch_kind="sub_parallel")

    rc, out = _run("rebuild", root)
    js = json.loads((root / "index.json").read_text())
    assert "warn" in js["integrity"]["depth_within_limit"]


def test_chain_break_detected():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "intent/01-intent.md", "sha256:a1", None, phase="01-intent")
    # prev 가 존재 안 하는 fingerprint 가리킴
    _make_artifact(root, "plan/06-plan.md", "sha256:c1", "sha256:MISSING", phase="06-plan")

    rc, out = _run("rebuild", root)
    js = json.loads((root / "index.json").read_text())
    assert js["integrity"]["fingerprint_chain"].startswith("break")


def test_index_md_contains_tree_and_multiverse():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "intent/01-intent.md", "sha256:a1", None, phase="01-intent")
    _make_artifact(root, "multiverse/06/universe-a/plan.md", "sha256:wa", "sha256:a1",
                   phase="06-plan", universe="a", parent_branch="06",
                   branch_kind="multiverse_winner")

    rc, out = _run("rebuild", root)
    md = (root / "INDEX.md").read_text(encoding="utf-8")
    assert "## 트리" in md
    assert "WINNER" in md
    assert "## 멀티버스 분기" in md
    assert "## 무결성 체크" in md


def test_verify_command_does_not_write_index():
    root = Path(tempfile.mkdtemp())
    _make_artifact(root, "intent/01-intent.md", "sha256:a1", None, phase="01-intent")
    rc, out = _run("verify", root)
    assert rc == 0
    # verify 는 INDEX.md 를 *쓰지* 않음 — 검증만
    assert not (root / "INDEX.md").exists()
    assert "integrity" in out


def test_no_artifacts_returns_empty_tree():
    root = Path(tempfile.mkdtemp())
    rc, out = _run("rebuild", root)
    assert rc == 0
    assert out["artifacts"] == 0
    md = (root / "INDEX.md").read_text(encoding="utf-8")
    assert "(산출물 없음)" in md or "총 산출물:** 0" in md
