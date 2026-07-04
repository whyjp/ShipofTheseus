"""measure_tournament.py(증거 조립기) 테스트 — WP4b 판단성(독립성/변량).

요구 매핑(팀 지시 산출물 6 — fixture 자족):
  (1) producer 가 shadow-grade 파일들을 파싱해 raw grader_count/grader_score_variance/
      winner_ratio 를 provenance 붙여 emit — verdict/pass 류는 measured 에 안 섞인다.
  (2) 실 CheckSpec(checks/plan.tournament_independence.json)으로 커널 재판정:
      2인 이상 + 변량>0 → PASS(value=winner_ratio).
  (3) 변량 0(동일 점수 2 grader) → 커널 FAIL(grader_score_variance>0 assertion).
  (4) 단일 grader → applicability(grader_count>=2) false → meta_audit NA(비게이팅).
  (5) 파싱 가능 shadow-grade 0 → evidence 미기록 → 커널 법칙1(evidence_missing) FAIL.
  (6) producer_cmd 가 CheckSpec.producer.cmd_pattern 과 정합(subprocess 경로).
  (7) 결정성 + artifact digest 가 디스크 scan 리포트와 대조.

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
import manifest as manifest_mod
import measure_tournament as producer
import meta_audit

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "plan.tournament_independence"
FIXED_TS = "2026-07-04T00:00:00+00:00"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _write_grade(path: Path, score) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"predicted_score": score}), encoding="utf-8")
    return path


def _run(shadow_dir: Path, out_dir: Path, **over):
    argv = ["--shadow-grades-dir", str(shadow_dir), "--out-dir", str(out_dir),
            "--measured-at", FIXED_TS]
    for k, v in over.items():
        argv += [f"--{k.replace('_', '-')}", str(v)]
    args = producer.build_parser().parse_args(argv)
    return producer.run(args)


def test_producer_emits_raw_values_no_verdict_mixed_in(tmp_path):
    """요구(1): measured 에 grader_count/variance/winner_ratio 만, verdict/pass 없음."""
    run_root = tmp_path / "run"
    sg = run_root / "plan"
    _write_grade(sg / "shadow-grade-00.json", 92)
    _write_grade(sg / "shadow-grade-01.json", 86)
    summary = _run(sg, run_root / "evidence")
    assert summary["emitted"] is True and summary["grader_count"] == 2

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run" and ev.self_reported is False
    assert set(ev.measured.keys()) == {"grader_count", "grader_score_variance", "winner_ratio"}
    assert ev.measured["grader_count"]["value"] == 2
    # winner_ratio = 패널 평균 = (0.92+0.86)/2 = 0.89
    assert abs(ev.measured["winner_ratio"]["value"] - 0.89) < 1e-9
    assert ev.measured["grader_score_variance"]["value"] > 0
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    dumped = json.dumps(ev.to_dict())
    assert "verdict" not in dumped and '"pass"' not in dumped


def test_kernel_passes_when_variance_positive(tmp_path):
    """요구(2): 2 grader + 변량>0 → 커널 PASS, value == winner_ratio."""
    run_root = tmp_path / "run"
    sg = run_root / "plan"
    _write_grade(sg / "shadow-grade-00.json", 92)
    _write_grade(sg / "shadow-grade-01.json", 86)
    _run(sg, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert abs(v.value - 0.89) < 1e-9


def test_kernel_fails_on_zero_variance_identical_graders(tmp_path):
    """요구(3): 2 grader 동일 점수(변량 0) → 커널 FAIL(zero-context 위반/복사 의심)."""
    run_root = tmp_path / "run"
    sg = run_root / "plan"
    _write_grade(sg / "shadow-grade-00.json", 90)
    _write_grade(sg / "shadow-grade-01.json", 90)
    summary = _run(sg, run_root / "evidence")
    # 측정 자체는 성공 — variance==0 은 실측된 값이지 측정 실패가 아니다.
    assert summary["emitted"] is True and summary["grader_score_variance"] == 0.0

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("grader_score_variance" in r for r in v.reasons)


def test_single_grader_is_na_via_applicability(tmp_path):
    """요구(4): 단일 grader → grader_count<2 → applicability false → meta_audit NA.

    실 CheckSpec 을 쓰되(REAL_CHECKS_DIR), 이 체크만 활성인 최소 매니페스트로 meta_audit
    정책 레이어를 태워 '침묵 skip 이 아니라 증거로 입증된 NA(비게이팅)'임을 값으로 확인.
    """
    run_root = tmp_path / "run"
    sg = run_root / "plan"
    _write_grade(sg / "shadow-grade-00.json", 88)
    _run(sg, run_root / "evidence")

    manifest_path = tmp_path / "pipeline.manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "06", "name": "plan", "active_grades": ["G3"]}],
        "multiverse_widths": {"G3": 3},
        "frozen_widths": {"G3": 5},
        "checks": {"G3": [CHECK_ID]},
    }), encoding="utf-8")

    report = meta_audit.run_meta_audit(
        run_root, "G3", manifest_path=manifest_path,
        checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "NA"
    assert CHECK_ID in report["na"]
    # NA 는 비게이팅 — verdict pass(회귀 트리거 아님).
    assert report["verdict"] == "pass"


def test_no_shadow_grades_emits_no_evidence_kernel_missing(tmp_path):
    """요구(5): 파싱 가능 shadow-grade 0 → evidence 미기록 → 커널 법칙1 FAIL."""
    run_root = tmp_path / "run"
    empty = run_root / "plan"
    empty.mkdir(parents=True)
    summary = _run(empty, run_root / "evidence")
    assert summary["emitted"] is False
    assert not (run_root / "evidence" / f"{CHECK_ID}.json").exists()

    ev = evidence_mod.try_load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("evidence_missing" in r for r in v.reasons)


def test_unparseable_grades_are_deficit_not_invented(tmp_path):
    """점수 키 없는 shadow-grade 는 graders 에서 제외되고 unparseable 로 기록 — 상상값 0."""
    run_root = tmp_path / "run"
    sg = run_root / "plan"
    (sg).mkdir(parents=True)
    (sg / "shadow-grade-00.json").write_text(json.dumps({"note": "no score here"}), encoding="utf-8")
    _write_grade(sg / "shadow-grade-01.json", 91)
    summary = _run(sg, run_root / "evidence")
    # 유효 grader 1 개만 — 상상으로 채우지 않는다.
    assert summary["grader_count"] == 1
    assert any("no normalizable score" in u["reason"] for u in summary["unparseable"])


def test_cli_subprocess_matches_checkspec_pattern(tmp_path):
    """요구(6): 실 subprocess producer_cmd 가 CheckSpec.producer.cmd_pattern 과 정합."""
    run_root = tmp_path / "run"
    sg = run_root / "plan"
    _write_grade(sg / "shadow-grade-00.json", 92)
    _write_grade(sg / "shadow-grade-01.json", 80)
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--shadow-grades-dir", str(sg), "--measured-at", FIXED_TS,
         "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)


def test_deterministic_and_digest_matches_disk(tmp_path):
    """요구(7): 결정성(같은 입력 → 같은 measured) + scan 리포트 digest 가 디스크와 대조."""
    a = tmp_path / "a"
    b = tmp_path / "b"
    for root in (a, b):
        _write_grade(root / "plan" / "shadow-grade-00.json", 92)
        _write_grade(root / "plan" / "shadow-grade-01.json", 86)
        _run(root / "plan", root / "evidence")
    da = json.loads((a / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    db = json.loads((b / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    assert da["measured"] == db["measured"]

    ev = evidence_mod.load_evidence(a / "evidence" / f"{CHECK_ID}.json")
    rel = ev.measured["winner_ratio"]["artifact_path"]
    assert evidence_mod.sha256_of_file(a / rel) == ev.artifact_digests[rel]
