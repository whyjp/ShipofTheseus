"""measure_cold_isolation.py(증거 조립기) 테스트 — WP4b 콜드 격리(overlap + 격리).

요구 매핑(팀 지시 산출물 6 — fixture 자족):
  (1) producer 가 두 텍스트의 계산된 overlap + (있으면)dispatch 로그의 실 관측값을
      provenance 붙여 emit — verdict 는 measured 에 안 섞인다.
  (2) 실 CheckSpec(checks/cold.isolation.json)으로 커널 재판정: 로그 present + overlap<=0.6
      + prior==0 + allowed>=1 → PASS.
  (3) prior_context_token_count != 0 → 커널 FAIL(격리 위반).
  (4) overlap > 0.6(하류 누출/오염) → 커널 FAIL.
  (5) 정직 고지: dispatch 로그 부재 → dispatch_log_present=0, 격리 키는 deficit(상상 0) →
      applicability(dispatch_log_present==1) false → meta_audit NA(비게이팅).
  (6) 두 텍스트 중 하나라도 부재 → computed_overlap 계산 불가 → evidence 미기록 → 법칙1 FAIL.
  (7) 언어 무관(한국어 토큰 overlap) + producer_cmd 정합 + 결정성 + digest 대조.

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
import measure_cold_isolation as producer
import meta_audit

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "cold.isolation"
FIXED_TS = "2026-07-04T00:00:00+00:00"

# 부분 겹침(overlap <= 0.6) 텍스트 쌍 — 공통 어휘 있으나 동일하지 않다.
REUNDERSTANDING = "mine throughput system extracts ore hauls surface conveyor\n광석 채굴 처리량\n"
INTENT = "build a mine throughput system extracting ore upward\n처리량 광석 시스템\n"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _dispatch(path: Path, prior: int, allowed: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"prior_context_token_count": prior,
                                "loaded_artifacts": allowed}), encoding="utf-8")
    return path


def _run(ru: Path, ref: Path, out_dir: Path, dispatch=None, cold_session=None):
    argv = ["--reunderstanding", str(ru), "--reference", str(ref),
            "--out-dir", str(out_dir), "--measured-at", FIXED_TS]
    if dispatch is not None:
        argv += ["--dispatch-log", str(dispatch)]
    if cold_session is not None:
        argv += ["--cold-session", str(cold_session)]
    return producer.run(producer.build_parser().parse_args(argv))


def test_producer_emits_raw_overlap_and_isolation_no_verdict(tmp_path):
    """요구(1): measured 에 overlap/present(+격리 키) 만, verdict 없음."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "reunderstanding.md", REUNDERSTANDING)
    ref = _write(run_root / "cold" / "intent.md", INTENT)
    disp = _dispatch(run_root / "cold" / "dispatch.json", 0, ["intent.md", "meta.md"])
    summary = _run(ru, ref, run_root / "evidence", dispatch=disp)
    assert summary["emitted"] is True and summary["dispatch_log_present"] == 1

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run" and ev.self_reported is False
    assert set(ev.measured.keys()) == {
        "computed_overlap", "dispatch_log_present",
        "prior_context_token_count", "allowed_file_count",
    }
    assert ev.measured["prior_context_token_count"]["value"] == 0
    assert ev.measured["allowed_file_count"]["value"] == 2
    assert 0.0 < ev.measured["computed_overlap"]["value"] <= 0.6
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    assert "verdict" not in json.dumps(ev.to_dict())


def test_kernel_passes_when_isolated_and_low_overlap(tmp_path):
    """요구(2): present + overlap<=0.6 + prior==0 + allowed>=1 → 커널 PASS."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "r.md", REUNDERSTANDING)
    ref = _write(run_root / "cold" / "i.md", INTENT)
    disp = _dispatch(run_root / "cold" / "d.json", 0, ["i.md"])
    _run(ru, ref, run_root / "evidence", dispatch=disp)
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons


def test_kernel_fails_on_nonzero_prior_context(tmp_path):
    """요구(3): prior_context_token_count != 0 → 커널 FAIL(격리 위반)."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "r.md", REUNDERSTANDING)
    ref = _write(run_root / "cold" / "i.md", INTENT)
    disp = _dispatch(run_root / "cold" / "d.json", 4823, ["i.md"])
    _run(ru, ref, run_root / "evidence", dispatch=disp)
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("prior_context_token_count" in r for r in v.reasons)


def test_kernel_fails_on_high_overlap_leak(tmp_path):
    """요구(4): reunderstanding == reference (overlap 1.0 > 0.6) → 커널 FAIL(오염/누출)."""
    run_root = tmp_path / "run"
    same = "identical text shared between cold output and reference downstream artifact"
    ru = _write(run_root / "cold" / "r.md", same)
    ref = _write(run_root / "cold" / "i.md", same)
    disp = _dispatch(run_root / "cold" / "d.json", 0, ["i.md"])
    summary = _run(ru, ref, run_root / "evidence", dispatch=disp)
    assert abs(summary["computed_overlap"] - 1.0) < 1e-9

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("computed_overlap" in r for r in v.reasons)


def test_no_dispatch_log_is_na_and_isolation_keys_deficit(tmp_path):
    """요구(5): 로그 부재 → present=0, 격리 키 deficit(상상 0) → meta_audit NA(비게이팅)."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "r.md", REUNDERSTANDING)
    ref = _write(run_root / "cold" / "i.md", INTENT)
    summary = _run(ru, ref, run_root / "evidence")  # dispatch 로그 없음
    assert summary["emitted"] is True and summary["dispatch_log_present"] == 0
    assert summary["deficits"] == ["prior_context_token_count", "allowed_file_count"]

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    # 격리 키는 measured 에 없다 — 상상하지 않는다.
    assert "prior_context_token_count" not in ev.measured
    assert "allowed_file_count" not in ev.measured

    manifest_path = tmp_path / "pipeline.manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "03", "name": "independent-comprehension", "active_grades": ["G3"]}],
        "multiverse_widths": {"G3": 3},
        "frozen_widths": {"G3": 5},
        "checks": {"G3": [CHECK_ID]},
    }), encoding="utf-8")
    report = meta_audit.run_meta_audit(
        run_root, "G3", manifest_path=manifest_path,
        checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "NA"
    assert CHECK_ID in report["na"] and report["verdict"] == "pass"


def test_missing_text_emits_no_evidence_kernel_missing(tmp_path):
    """요구(6): reference 텍스트 부재 → overlap 계산 불가 → evidence 미기록 → 법칙1 FAIL."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "r.md", REUNDERSTANDING)
    ref = run_root / "cold" / "missing.md"  # 존재하지 않음
    summary = _run(ru, ref, run_root / "evidence")
    assert summary["emitted"] is False
    assert not (run_root / "evidence" / f"{CHECK_ID}.json").exists()

    ev = evidence_mod.try_load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("evidence_missing" in r for r in v.reasons)


def test_language_agnostic_korean_overlap(tmp_path):
    """요구(7a): 한국어 전용 텍스트도 토큰 overlap 이 계산된다(영어 sentinel 회귀 없음)."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "r.md", "광석 채굴 처리량 시스템 갱도 컨베이어")
    ref = _write(run_root / "cold" / "i.md", "광석 채굴 처리량 상향 이송")
    summary = _run(ru, ref, run_root / "evidence")
    # 공통 어휘(광석/채굴/처리량) 있으므로 overlap > 0.
    assert summary["computed_overlap"] > 0.0


def test_cold_session_report_folded_for_traceability(tmp_path):
    """--cold-session 시 check_cold_session.build_report 결과가 scan 리포트에 첨부(추적)."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "r.md", REUNDERSTANDING)
    ref = _write(run_root / "cold" / "i.md", INTENT)
    cs = run_root / "session"
    (cs / "plan").mkdir(parents=True)
    _run(ru, ref, run_root / "evidence", cold_session=cs)
    report = json.loads((run_root / "evidence" / f"{CHECK_ID}.report.json").read_text(encoding="utf-8"))
    assert "cold_session_artifact_report" in report
    assert "violation_count" in report["cold_session_artifact_report"]


def test_cli_subprocess_matches_pattern_and_deterministic(tmp_path):
    """요구(7b): 실 subprocess producer_cmd 정합 + 결정성 + digest 대조."""
    run_root = tmp_path / "run"
    ru = _write(run_root / "cold" / "r.md", REUNDERSTANDING)
    ref = _write(run_root / "cold" / "i.md", INTENT)
    disp = _dispatch(run_root / "cold" / "d.json", 0, ["i.md"])
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--reunderstanding", str(ru), "--reference", str(ref),
         "--dispatch-log", str(disp), "--measured-at", FIXED_TS,
         "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)
    rel = ev.measured["computed_overlap"]["artifact_path"]
    assert evidence_mod.sha256_of_file(run_root / rel) == ev.artifact_digests[rel]
