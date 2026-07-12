"""measure_tournament_argmax.py(증거 조립기) 테스트 — 병합/승자 소유(merge-ownership).

요구 매핑(fixture 자족):
  (1) producer 가 최종 tournament frontmatter + 본문 표 + 승격 아티팩트를 디스크에서 파싱해
      measured 만 provenance 붙여 emit — verdict 없음.
  (2) winner==argmax + copy digest 매칭 + 정상 → 커널 PASS.
  (3) *핵심* 선언 winner 가 argmax 아님 → 커널 FAIL(선택을 코드가 소유).
  (4) malformed_rows > 0(universe 행 총점 미파싱) → FAIL.
  (5) universes_scored < 2(단일 universe) → FAIL.
  (6) scores_out_of_range > 0(1-5 coarse 총점) → FAIL.
  (7) winner_row_delta > 0.005(frontmatter winner_score ≠ 표 총점) → FAIL.
  (8) copy 인데 canonical ≠ winner(digest 불일치) → FAIL(조용한 재작성).
  (9) merge + winner ∈ merge_sources → digest 불일치여도 PASS(선언 머지 허용).
  (10) merge 인데 winner ∉ merge_sources → FAIL.
  (11) 동률(winner 총점 == 최대) → PASS(argmax_tie_count 보고, 머지 영역).
  (12) 비휴면: tournament/winner_id 부재 → evidence 미기록 → meta_audit FAIL(NA 아님).
  (13) 게이트가 실제 열림: 정상 → meta_audit PASS.
  (14) 실 subprocess producer_cmd 정합 + digest 대조.

실행: python -m pytest skills/theseus-harness/scoring/producers -q
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import checkspec
import evidence as evidence_mod
import kernel
import measure_tournament_argmax as producer
import meta_audit

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "plan.tournament_winner_argmax"
FIXED_TS = "2026-07-12T00:00:00+00:00"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _row(lbl, tot) -> str:
    if tot is None:
        return f"| {lbl} | n/a | pending |"       # 총점 미파싱 → malformed
    return f"| {lbl} | 0.50 | {tot} |"


def _tournament(plan_dir: Path, winner_id, winner_score, rows,
                policy=None, merge_sources=None, name="tournament-00.md") -> None:
    fm = ["---", "phase: 06-tournament",
          f"winner_id: {winner_id}", f"winner_score: {winner_score}"]
    if policy is not None:
        fm.append(f"promotion_policy: {policy}")
    if merge_sources is not None:
        fm.append(f"merge_sources: [{', '.join(merge_sources)}]")
    fm.append("---")
    body = ["", "| Universe | feasibility | weighted |", "| --- | --- | --- |"]
    body += [_row(lbl, tot) for lbl, tot in rows]
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / name).write_text("\n".join(fm + body) + "\n", encoding="utf-8")


def _promote(plan_dir: Path, winner_id, content="WINNER PLAN BODY", canonical_same=True) -> None:
    cand = plan_dir / "candidates" / winner_id
    cand.mkdir(parents=True, exist_ok=True)
    (cand / "06-plan.md").write_text(content, encoding="utf-8")
    (plan_dir / "06-plan.md").write_text(
        content if canonical_same else content + "\nREWRITTEN", encoding="utf-8"
    )


def _clean(run_root: Path):
    """winner=universe-1(argmax 0.913), copy, digest 매칭."""
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.913",
                [("universe-1", "0.913"), ("universe-2", "0.802")], policy="copy")
    _promote(plan, "universe-1")


def _run(run_root: Path):
    argv = ["--out-dir", str(run_root / "evidence"), "--measured-at", FIXED_TS]
    return producer.run(producer.build_parser().parse_args(argv))


def _ev(run_root: Path):
    return evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")


def _verify(run_root: Path):
    return kernel.verify(_spec(), _ev(run_root), artifact_root=run_root, verified_at=FIXED_TS)


def test_producer_emits_measured_no_verdict(tmp_path):
    run_root = tmp_path / "run"
    _clean(run_root)
    summary = _run(run_root)
    assert summary["emitted"] is True
    ev = _ev(run_root)
    assert ev.produced_by == "run" and ev.self_reported is False
    assert ev.measured["winner_argmax_match"]["value"] == 1
    assert ev.measured["universes_scored"]["value"] == 2
    assert ev.measured["canonical_digest_match"]["value"] == 1
    assert ev.measured["promotion_policy_copy"]["value"] == 1
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    assert "verdict" not in json.dumps(ev.to_dict())


def test_kernel_passes_when_winner_is_argmax_and_copy_matches(tmp_path):
    run_root = tmp_path / "run"
    _clean(run_root)
    _run(run_root)
    v = _verify(run_root)
    assert v.result == "PASS", v.reasons


def test_kernel_fails_when_winner_not_argmax(tmp_path):
    """핵심: 선언 winner(0.802) < 다른 universe(0.913) → argmax 아님 FAIL."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.802",
                [("universe-1", "0.802"), ("universe-2", "0.913")], policy="copy")
    _promote(plan, "universe-1")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["winner_argmax_match"]["value"] == 0
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("winner_argmax_match" in r for r in v.reasons)


def test_kernel_fails_on_malformed_row(tmp_path):
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.913",
                [("universe-1", "0.913"), ("universe-2", "0.80"), ("universe-3", None)], policy="copy")
    _promote(plan, "universe-1")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["malformed_rows"]["value"] == 1
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("malformed_rows" in r for r in v.reasons)


def test_kernel_fails_on_single_universe(tmp_path):
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.913", [("universe-1", "0.913")], policy="copy")
    _promote(plan, "universe-1")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["universes_scored"]["value"] == 1
    assert _verify(run_root).result == "FAIL"


def test_kernel_fails_on_out_of_range_score(tmp_path):
    """1-5 coarse 총점(4/3) → [0,1] 밖."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "4",
                [("universe-1", "4"), ("universe-2", "3")], policy="copy")
    _promote(plan, "universe-1")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["scores_out_of_range"]["value"] >= 1
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("scores_out_of_range" in r for r in v.reasons)


def test_kernel_fails_on_winner_row_delta(tmp_path):
    """frontmatter winner_score(0.913) ≠ winner 표 총점(0.700)."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.913",
                [("universe-1", "0.700"), ("universe-2", "0.60")], policy="copy")
    _promote(plan, "universe-1")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["winner_row_delta"]["value"] > 0.005
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("winner_row_delta" in r for r in v.reasons)


def test_kernel_fails_on_copy_digest_mismatch(tmp_path):
    """copy 인데 canonical ≠ winner 후보(조용한 재작성)."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.913",
                [("universe-1", "0.913"), ("universe-2", "0.80")], policy="copy")
    _promote(plan, "universe-1", canonical_same=False)
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["canonical_digest_match"]["value"] == 0
    assert _verify(run_root).result == "FAIL"


def test_kernel_passes_on_declared_merge(tmp_path):
    """merge + winner ∈ merge_sources → digest 불일치여도 PASS(선언 머지 허용)."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.913",
                [("universe-1", "0.913"), ("universe-2", "0.90")],
                policy="merge", merge_sources=["universe-1", "universe-2"])
    _promote(plan, "universe-1", canonical_same=False)   # 머지라 canonical ≠ winner OK
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["promotion_policy_copy"]["value"] == 0
    assert ev.measured["merge_sources_include_winner"]["value"] == 1
    v = _verify(run_root)
    assert v.result == "PASS", v.reasons


def test_kernel_fails_on_merge_excluding_winner(tmp_path):
    """merge 인데 winner ∉ merge_sources."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.913",
                [("universe-1", "0.913"), ("universe-2", "0.90")],
                policy="merge", merge_sources=["universe-2"])
    _promote(plan, "universe-1", canonical_same=False)
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["merge_sources_include_winner"]["value"] == 0
    assert _verify(run_root).result == "FAIL"


def test_tie_at_max_passes(tmp_path):
    """동률(winner 총점 == 최대) → argmax_tie_count 보고하되 PASS."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _tournament(plan, "universe-1", "0.900",
                [("universe-1", "0.900"), ("universe-2", "0.900")], policy="copy")
    _promote(plan, "universe-1")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["winner_argmax_match"]["value"] == 1
    assert ev.measured["argmax_tie_count"]["value"] == 2
    assert _verify(run_root).result == "PASS"


def test_absent_tournament_is_fail_not_na(tmp_path):
    """비휴면: tournament 부재 → evidence 미기록 → meta_audit FAIL(NA 아님)."""
    run_root = tmp_path / "run"
    summary = _run(run_root)
    assert summary["emitted"] is False
    assert not (run_root / "evidence" / f"{CHECK_ID}.json").exists()

    manifest_path = tmp_path / "pipeline.manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "06", "name": "plan", "active_grades": ["G4"]}],
        "multiverse_widths": {"G4": 4},
        "frozen_widths": {"G4": 7},
        "checks": {"G4": [CHECK_ID]},
    }), encoding="utf-8")
    report = meta_audit.run_meta_audit(
        run_root, "G4", manifest_path=manifest_path,
        checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "FAIL"
    assert CHECK_ID in report["failed"]
    assert CHECK_ID not in report.get("na", [])


def test_missing_winner_id_is_not_emitted(tmp_path):
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    plan.mkdir(parents=True, exist_ok=True)
    (plan / "tournament-00.md").write_text(
        "---\nphase: 06-tournament\n---\n\n| Universe | weighted |\n| universe-1 | 0.9 |\n",
        encoding="utf-8",
    )
    summary = _run(run_root)
    assert summary["emitted"] is False


def test_meta_audit_passes_when_clean(tmp_path):
    run_root = tmp_path / "run"
    _clean(run_root)
    _run(run_root)
    manifest_path = tmp_path / "pipeline.manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "06", "name": "plan", "active_grades": ["G4"]}],
        "multiverse_widths": {"G4": 4},
        "frozen_widths": {"G4": 7},
        "checks": {"G4": [CHECK_ID]},
    }), encoding="utf-8")
    report = meta_audit.run_meta_audit(
        run_root, "G4", manifest_path=manifest_path,
        checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "PASS", report["results"][CHECK_ID]["reasons"]
    assert report["verdict"] == "pass"


def test_cli_subprocess_matches_pattern_and_deterministic(tmp_path):
    run_root = tmp_path / "run"
    _clean(run_root)
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--measured-at", FIXED_TS, "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = _ev(run_root)
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)
    rel = ev.measured["winner_argmax_match"]["artifact_path"]
    assert evidence_mod.sha256_of_file(run_root / rel) == ev.artifact_digests[rel]
