"""measure_context_minimality.py(증거 조립기) 테스트 — pure-review 순도(순도+무결성+최소성).

요구 매핑(fixture 자족):
  (1) producer 가 리뷰 디스패치 로그를 스캔해 measured(순도/무결성/freshness/최소성)만
      provenance 붙여 emit — verdict 는 measured 에 안 섞인다.
  (2) 실 CheckSpec(checks/review.context_minimality.json)으로 커널 재판정:
      calls>=1 + malformed==0 + prior==0 + missing==0 + dup==0 → PASS.
  (3) prior_context_max != 0 → 커널 FAIL(생성 컨텍스트 누출 = 순도 위반).
  (4) loaded_artifacts_missing > 0 → 커널 FAIL(실재하지 않는 컨텍스트 신고 = 무결성).
  (5) duplicate_call_ids > 0 → 커널 FAIL(fresh 재호출 위반).
  (6) malformed_calls > 0 → 커널 FAIL(순도 검증 불가).
  (7) calls_total == 0 → 커널 FAIL(no-work guard).
  (8) 비휴면: 로그 부재 → evidence 미기록 → meta_audit 가 NA 아니라 FAIL(cold.isolation 대비).
  (9) loaded_tokens_max 는 로그 자기 신고가 아니라 producer 의 디스크 재계산값(game 불가).
  (10) producer_cmd 정합 + digest 대조.

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
import measure_context_minimality as producer
import meta_audit

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "review.context_minimality"
FIXED_TS = "2026-07-04T00:00:00+00:00"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _log(path: Path, calls) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"calls": calls}), encoding="utf-8")
    return path


def _run(dispatch: Path, out_dir: Path):
    argv = ["--dispatch-log", str(dispatch), "--out-dir", str(out_dir), "--measured-at", FIXED_TS]
    return producer.run(producer.build_parser().parse_args(argv))


def _clean_fixture(run_root: Path):
    """3 토큰·5 토큰 아티팩트 2개 + 순수 로그(2 호출, prior 0, 유니크 id)."""
    _write(run_root / "plan" / "a.md", "alpha beta gamma")            # \w+ = 3
    _write(run_root / "plan" / "b.md", "one two three four five")     # \w+ = 5
    return _log(run_root / "state" / "log.json", [
        {"agent_call_id": "call-1", "prior_context_token_count": 0,
         "loaded_artifacts": ["plan/a.md"]},
        {"agent_call_id": "call-2", "prior_context_token_count": 0,
         "loaded_artifacts": ["plan/a.md", "plan/b.md"]},   # 3+5 = 8 토큰
    ])


def test_producer_emits_measured_no_verdict(tmp_path):
    """요구(1): measured 6키만, verdict 없음, provenance 완전."""
    run_root = tmp_path / "run"
    disp = _clean_fixture(run_root)
    summary = _run(disp, run_root / "evidence")
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run" and ev.self_reported is False
    assert set(ev.measured.keys()) == {
        "calls_total", "malformed_calls", "prior_context_max",
        "duplicate_call_ids", "loaded_artifacts_missing", "loaded_tokens_max",
    }
    assert ev.measured["calls_total"]["value"] == 2
    assert ev.measured["prior_context_max"]["value"] == 0
    assert ev.measured["loaded_artifacts_missing"]["value"] == 0
    assert ev.measured["loaded_tokens_max"]["value"] == 8   # max(3, 3+5)
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    assert "verdict" not in json.dumps(ev.to_dict())


def test_kernel_passes_when_pure_and_bounded(tmp_path):
    """요구(2): 순수(prior 0)·무결(missing 0)·fresh(dup 0)·well-formed → 커널 PASS."""
    run_root = tmp_path / "run"
    disp = _clean_fixture(run_root)
    _run(disp, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert v.value == 8   # loaded_tokens_max


def test_kernel_fails_on_nonzero_prior(tmp_path):
    """요구(3): 한 호출이 prior_context_token_count!=0 → 순도 위반 FAIL."""
    run_root = tmp_path / "run"
    _write(run_root / "plan" / "a.md", "alpha beta gamma")
    disp = _log(run_root / "state" / "log.json", [
        {"agent_call_id": "c1", "prior_context_token_count": 1500,
         "loaded_artifacts": ["plan/a.md"]},
    ])
    _run(disp, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("prior_context_max" in r for r in v.reasons)


def test_kernel_fails_on_missing_loaded_artifact(tmp_path):
    """요구(4): 로그가 선언한 주입 파일이 디스크 부재 → 무결성 FAIL."""
    run_root = tmp_path / "run"
    _write(run_root / "plan" / "a.md", "alpha beta gamma")
    disp = _log(run_root / "state" / "log.json", [
        {"agent_call_id": "c1", "prior_context_token_count": 0,
         "loaded_artifacts": ["plan/a.md", "plan/does-not-exist.md"]},
    ])
    _run(disp, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.measured["loaded_artifacts_missing"]["value"] == 1
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("loaded_artifacts_missing" in r for r in v.reasons)


def test_kernel_fails_on_duplicate_call_id(tmp_path):
    """요구(5): agent_call_id 중복 → fresh 재호출 위반 FAIL."""
    run_root = tmp_path / "run"
    _write(run_root / "plan" / "a.md", "alpha beta gamma")
    disp = _log(run_root / "state" / "log.json", [
        {"agent_call_id": "dup", "prior_context_token_count": 0, "loaded_artifacts": ["plan/a.md"]},
        {"agent_call_id": "dup", "prior_context_token_count": 0, "loaded_artifacts": ["plan/a.md"]},
    ])
    _run(disp, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.measured["duplicate_call_ids"]["value"] == 1
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("duplicate_call_ids" in r for r in v.reasons)


def test_kernel_fails_on_malformed_call(tmp_path):
    """요구(6): prior 필드 결손 호출 → malformed FAIL(순도 검증 불가)."""
    run_root = tmp_path / "run"
    _write(run_root / "plan" / "a.md", "alpha beta gamma")
    disp = _log(run_root / "state" / "log.json", [
        {"agent_call_id": "c1", "loaded_artifacts": ["plan/a.md"]},  # prior 없음
    ])
    _run(disp, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.measured["malformed_calls"]["value"] == 1
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("malformed_calls" in r for r in v.reasons)


def test_kernel_fails_on_zero_calls(tmp_path):
    """요구(7): 빈 호출 배열 → calls_total 0 → no-work FAIL."""
    run_root = tmp_path / "run"
    disp = _log(run_root / "state" / "log.json", [])
    _run(disp, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.measured["calls_total"]["value"] == 0
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("calls_total" in r for r in v.reasons)


def test_absent_log_is_fail_not_na(tmp_path):
    """요구(8) 비휴면: 로그 부재 → evidence 미기록 → meta_audit FAIL(NA 아님).

    cold.isolation 은 applicability=dispatch_log_present==1 뒤에서 로그 부재 시 NA(휴면)이지만,
    본 체크는 applicability 없음 → 부재가 absence_policy FAIL 로 강제된다(pure-review 로깅 의무)."""
    run_root = tmp_path / "run"
    summary = _run(run_root / "state" / "nope.json", run_root / "evidence")  # 로그 없음
    assert summary["emitted"] is False
    assert not (run_root / "evidence" / f"{CHECK_ID}.json").exists()

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
    assert report["results"][CHECK_ID]["result"] == "FAIL"     # NA 아님(비휴면)
    assert CHECK_ID in report["failed"]
    assert CHECK_ID not in report.get("na", [])
    assert report["verdict"] == "fail"


def test_meta_audit_passes_when_log_clean(tmp_path):
    """요구(2') 게이트가 실제로 '열린다': 순수 로그 evidence → meta_audit PASS."""
    run_root = tmp_path / "run"
    disp = _clean_fixture(run_root)
    _run(disp, run_root / "evidence")
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
    assert report["results"][CHECK_ID]["result"] == "PASS", report["results"][CHECK_ID]["reasons"]
    assert report["verdict"] == "pass"


def test_loaded_tokens_recomputed_from_disk_not_log(tmp_path):
    """요구(9): loaded_tokens_max 는 로그의 자기 신고가 아니라 producer 의 디스크 재계산.

    로그에 거짓 토큰 수를 박아도 producer 는 실제 파일을 다시 읽어 \\w+ 로 센다(game 불가)."""
    run_root = tmp_path / "run"
    _write(run_root / "plan" / "a.md", "alpha beta gamma")   # 실제 3 토큰
    disp = _log(run_root / "state" / "log.json", [
        {"agent_call_id": "c1", "prior_context_token_count": 0,
         "loaded_artifacts": ["plan/a.md"],
         "loaded_artifacts_token_count": 999999},   # 거짓 자기 신고 — 무시돼야 함
    ])
    summary = _run(disp, run_root / "evidence")
    assert summary["loaded_tokens_max"] == 3   # 거짓 999999 아님 — 디스크 재계산


def test_cli_subprocess_matches_pattern_and_deterministic(tmp_path):
    """요구(10): 실 subprocess producer_cmd 정합 + digest 대조."""
    run_root = tmp_path / "run"
    disp = _clean_fixture(run_root)
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--dispatch-log", str(disp), "--measured-at", FIXED_TS,
         "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)
    rel = ev.measured["calls_total"]["artifact_path"]
    assert evidence_mod.sha256_of_file(run_root / rel) == ev.artifact_digests[rel]
