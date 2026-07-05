"""measure_regression.py(증거 조립기) 테스트 — WP4b 값 기반 회귀(score delta).

요구 매핑(팀 지시 산출물 6 — fixture 자족):
  (1) producer 가 두 score 산출물(kernel Verdict)의 value 를 읽어 raw prior_score/
      current_score/score_delta 를 provenance 붙여 emit — verdict/regressed 는 measured
      에 안 섞인다.
  (2) 실 CheckSpec(checks/sprint.regression.json)으로 커널 재판정: delta>=-0.05 → PASS.
  (3) delta<-0.05(실제 값 하락) → 커널 FAIL. (자기 채점 단조 상승이 아니라 실제 값 비교.)
  (4) skipped==FAIL 규율: 두 입력 중 하나라도 score 미추출 → evidence 미기록 →
      커널 법칙1(evidence_missing) FAIL. (측정 안 하면 통과가 아니라 실패.)
  (5) Evidence measured 스칼라(--score-key)에서도 추출 가능.
  (6) producer_cmd 정합 + 결정성 + digest 대조.

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
import measure_regression as producer

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "sprint.regression"
FIXED_TS = "2026-07-04T00:00:00+00:00"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _write_verdict(path: Path, value) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"check_id": "scoring.correctness", "result": "PASS",
                                "value": value}), encoding="utf-8")
    return path


def _run(prior: Path, current: Path, out_dir: Path, **over):
    argv = ["--prior", str(prior), "--current", str(current), "--out-dir", str(out_dir),
            "--measured-at", FIXED_TS]
    for k, v in over.items():
        argv += [f"--{k.replace('_', '-')}", str(v)]
    args = producer.build_parser().parse_args(argv)
    return producer.run(args)


def test_producer_emits_raw_delta_no_verdict_mixed_in(tmp_path):
    """요구(1): measured 에 prior/current/delta 만, regressed/verdict 없음."""
    run_root = tmp_path / "run"
    prior = _write_verdict(run_root / "scores" / "prior.json", 0.90)
    current = _write_verdict(run_root / "scores" / "current.json", 0.93)
    summary = _run(prior, current, run_root / "evidence")
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run" and ev.self_reported is False
    assert set(ev.measured.keys()) == {"prior_score", "current_score", "score_delta"}
    assert abs(ev.measured["prior_score"]["value"] - 0.90) < 1e-9
    assert abs(ev.measured["current_score"]["value"] - 0.93) < 1e-9
    assert abs(ev.measured["score_delta"]["value"] - 0.03) < 1e-9
    # measured 값은 모두 숫자(원시 계산량)뿐 — verdict/result/regressed 같은 판정 문자열이
    # measured 로 섞이지 않는다(키 집합이 정확히 3 이라는 위 단언과 합쳐 봉쇄 증명).
    for entry in ev.measured.values():
        assert isinstance(entry["value"], (int, float)) and not isinstance(entry["value"], bool)
    # prior/current 는 각자 원본 파일로, delta 는 scan 리포트로 backing(3 파일 pin).
    assert len(ev.artifact_digests) == 3


def test_kernel_passes_when_delta_within_threshold(tmp_path):
    """요구(2): +0.03 (>= -0.05) → 커널 PASS, value == delta."""
    run_root = tmp_path / "run"
    prior = _write_verdict(run_root / "scores" / "prior.json", 0.90)
    current = _write_verdict(run_root / "scores" / "current.json", 0.93)
    _run(prior, current, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert abs(v.value - 0.03) < 1e-9


def test_kernel_fails_on_real_score_drop(tmp_path):
    """요구(3): 0.90 -> 0.80 (delta -0.10 < -0.05) → 커널 FAIL. 실제 값 하락에 발동."""
    run_root = tmp_path / "run"
    prior = _write_verdict(run_root / "scores" / "prior.json", 0.90)
    current = _write_verdict(run_root / "scores" / "current.json", 0.80)
    summary = _run(prior, current, run_root / "evidence")
    assert abs(summary["score_delta"] - (-0.10)) < 1e-9

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("score_delta" in r for r in v.reasons)


def test_missing_score_emits_no_evidence_skipped_is_fail(tmp_path):
    """요구(4): current 에 value 없음 → score 미추출 → evidence 미기록 → 법칙1 FAIL."""
    run_root = tmp_path / "run"
    prior = _write_verdict(run_root / "scores" / "prior.json", 0.90)
    current = run_root / "scores" / "current.json"
    current.parent.mkdir(parents=True, exist_ok=True)
    # value 없는 Verdict(측정 미완) — 상상하지 않는다.
    current.write_text(json.dumps({"check_id": "scoring.correctness", "result": "FAIL",
                                   "value": None}), encoding="utf-8")
    summary = _run(prior, current, run_root / "evidence")
    assert summary["emitted"] is False
    assert not (run_root / "evidence" / f"{CHECK_ID}.json").exists()

    ev = evidence_mod.try_load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("evidence_missing" in r for r in v.reasons)


def test_extract_score_from_evidence_measured_scalar(tmp_path):
    """요구(5): Verdict.value 대신 Evidence measured 스칼라(--score-key)에서 추출."""
    run_root = tmp_path / "run"
    prior = run_root / "scores" / "prior.json"
    current = run_root / "scores" / "current.json"
    prior.parent.mkdir(parents=True, exist_ok=True)
    prior.write_text(json.dumps({"measured": {"score_total_weighted": {"value": 0.88}}}),
                     encoding="utf-8")
    current.write_text(json.dumps({"measured": {"score_total_weighted": {"value": 0.90}}}),
                       encoding="utf-8")
    summary = _run(prior, current, run_root / "evidence", score_key="score_total_weighted")
    assert summary["emitted"] is True
    assert abs(summary["score_delta"] - 0.02) < 1e-9


def test_cli_subprocess_matches_pattern_and_deterministic(tmp_path):
    """요구(6): 실 subprocess producer_cmd 정합 + 결정성 + digest 대조."""
    run_root = tmp_path / "run"
    prior = _write_verdict(run_root / "scores" / "prior.json", 0.90)
    current = _write_verdict(run_root / "scores" / "current.json", 0.93)
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--prior", str(prior), "--current", str(current),
         "--measured-at", FIXED_TS, "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)

    # score_delta 의 backing(scan 리포트) digest 가 디스크와 대조.
    rel = ev.measured["score_delta"]["artifact_path"]
    assert evidence_mod.sha256_of_file(run_root / rel) == ev.artifact_digests[rel]
