"""measure_regression_diagnosis.py(증거 조립기) 테스트 — 회귀 진단 병렬화(parallel-diagnosis).

요구 매핑(fixture 자족):
  (1) producer 가 gate_history evidence + bisect.md frontmatter + hypothesis-*.json 을 디스크에서
      파싱해 measured(12 키)만 provenance 붙여 emit — verdict 없음.
  (2) 회귀 이벤트 0 → regression_events_total==0 → meta_audit NA(applicability false, FAIL 아님).
  (3) 회귀 + corroborated 병렬 진단(K 가설, ≥2 합의, argmax==선언, 라우팅 일치, 대안 존재) → 커널 PASS.
  (4) 회귀인데 bound 진단 없음 → undiagnosed_events≥1 → FAIL.
  (5) 가설 부족(< hypo_floor) → FAIL.
  (6) agent_call_id 중복 → FAIL.
  (7) 유효 4-class 밖 defect_class → FAIL.
  (8) corroboration < min(전원 불일치) → FAIL.
  (9) 선언 class != 표결 argmax → class_argmax_match==0 → FAIL.
  (10) 라우팅(fix_target_phase) != FAILURE_TO_PHASE[class] → FAIL.
  (11) 한 가설 alternative 결손 → FAIL.
  (12) hypo_floor/corroboration_min 을 실 manifest 에서 grade 로 읽음.
  (13) 실 subprocess producer_cmd 정합 + digest 대조.
  (+) -0.05 임계 상수가 checks/sprint.regression.json 과 drift 없음.

실행: python -m pytest skills/theseus-harness/scoring/producers -q
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import checkpoint
import checkspec
import evidence as evidence_mod
import kernel
import measure_regression_diagnosis as producer
import meta_audit

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "regression.parallel_diagnosis"
FIXED_TS = "2026-07-12T00:00:00+00:00"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


# --- fixture builders ----------------------------------------------------------


def _write_regression_event(run_root: Path, idx: str, prior: float, current: float) -> float:
    """gate_history/<idx>/evidence/sprint.regression.json 을 실 Evidence Record 로 기록."""
    ev_dir = run_root / "state" / "gate_history" / idx / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    delta = round(current - prior, 6)

    def _m(v):
        return {"value": v, "source": "kernel_verdict_or_evidence", "artifact_path": "x"}

    record = {
        "evidence_schema_version": "1.0",
        "check_id": "sprint.regression",
        "phase": "10",
        "project_run": "run",
        "produced_by": "run",
        "producer_cmd": "python measure_regression.py --out-dir x",
        "producer_exit_code": 0,
        "measured": {"prior_score": _m(prior), "current_score": _m(current), "score_delta": _m(delta)},
        "artifact_digests": {},
        "measured_at": FIXED_TS,
        "self_reported": False,
    }
    (ev_dir / "sprint.regression.json").write_text(
        json.dumps(record, ensure_ascii=False), encoding="utf-8"
    )
    return delta


def _write_bisect(run_root: Path, sprint: str, *, gate_history_ref: str, prior: float,
                  current: float, regression_class: str, fix_target_phase: str) -> Path:
    d = run_root / "sprints" / sprint
    d.mkdir(parents=True, exist_ok=True)
    fm = [
        "---",
        f"gate_history_ref: {gate_history_ref}",
        f"prior_score: {prior}",
        f"current_score: {current}",
        f"regression_class: {regression_class}",
        f"fix_target_phase: {fix_target_phase}",
        "---",
        "",
        "# 스프린트 회귀 바이섹트 (body)",
    ]
    (d / "bisect.md").write_text("\n".join(fm) + "\n", encoding="utf-8")
    return d


def _write_hypothesis(sprint_dir: Path, k: int, *, agent_call_id: str, defect_class: str,
                      alternative_class: str = "impl_defect", suspect: str = "internal/auth/token.py:42",
                      omit: tuple[str, ...] = ()) -> None:
    hdir = sprint_dir / "hypotheses"
    hdir.mkdir(parents=True, exist_ok=True)
    data = {
        "agent_call_id": agent_call_id,
        "defect_class": defect_class,
        "suspect_file_or_commit": suspect,
        "failing_test": "tests/test_auth.py::test_expired",
        "alternative_class": alternative_class,
        "alternative_reason": "diff 에 fixture 변경 없음 — 덜 가능성",
    }
    for key in omit:
        data.pop(key, None)
    (hdir / f"hypothesis-{k}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _write_scope_map(run_root: Path, idx: str, paths: list[str]) -> None:
    """gate_history/<idx>/evidence/gate.scope_map.report.json — 회귀 게이트 실관측 touched 셋(앵커)."""
    ev_dir = run_root / "state" / "gate_history" / idx / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "git_base": "HEAD",
        "files_touched_observed": len(paths),
        "files": [{"path": p, "matched_todos": []} for p in paths],
    }
    (ev_dir / "gate.scope_map.report.json").write_text(
        json.dumps(report, ensure_ascii=False), encoding="utf-8"
    )


def _clean(run_root: Path) -> None:
    """회귀 이벤트 1 + bound 진단 + 3 corroborated 가설(2 plan / 1 impl) → PASS 준비(G4)."""
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="c-a", defect_class="plan_defect")
    _write_hypothesis(sprint, 1, agent_call_id="c-b", defect_class="plan_defect")
    _write_hypothesis(sprint, 2, agent_call_id="c-c", defect_class="impl_defect")


def _run(run_root: Path, grade: str = "G4"):
    argv = ["--grade", grade, "--out-dir", str(run_root / "evidence"), "--measured-at", FIXED_TS]
    return producer.run(producer.build_parser().parse_args(argv))


def _ev(run_root: Path):
    return evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")


def _verify(run_root: Path):
    return kernel.verify(_spec(), _ev(run_root), artifact_root=run_root, verified_at=FIXED_TS)


_MEASURED_KEYS = (
    "regression_events_total", "undiagnosed_events", "hypotheses_count", "malformed_hypotheses",
    "duplicate_call_ids", "invalid_class_votes", "corroboration_count", "class_argmax_match",
    "routing_matches_class", "hypotheses_without_alternative", "hypo_floor", "corroboration_min",
)


# --- (1) emit -----------------------------------------------------------------


def test_producer_emits_measured_no_verdict(tmp_path):
    run_root = tmp_path / "run"
    _clean(run_root)
    summary = _run(run_root)
    assert summary["emitted"] is True
    ev = _ev(run_root)
    assert ev.produced_by == "run" and ev.self_reported is False
    for k in _MEASURED_KEYS:
        assert k in ev.measured, f"measured 키 누락: {k}"
        assert ev.measured[k]["source"] and ev.measured[k]["artifact_path"]
    assert ev.measured["regression_events_total"]["value"] == 1
    assert ev.measured["hypotheses_count"]["value"] == 3
    assert ev.measured["corroboration_count"]["value"] == 2
    assert ev.measured["hypo_floor"]["value"] == 3
    assert ev.measured["corroboration_min"]["value"] == 2
    assert "verdict" not in json.dumps(ev.to_dict())


# --- (2) NA (applicability false) ---------------------------------------------


def _scoped_manifest(tmp_path: Path) -> Path:
    manifest_path = tmp_path / "pipeline.manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "11", "name": "regression-bisect", "active_grades": ["G4"]}],
        "multiverse_widths": {"G4": 4},
        "frozen_widths": {"G4": 7},
        "regression_diagnosis": {"min_hypotheses": {"G4": 3}, "corroboration_min": 2},
        "checks": {"G4": [CHECK_ID]},
    }), encoding="utf-8")
    return manifest_path


def test_no_regression_event_is_na_not_fail(tmp_path):
    """회귀 이벤트 0 → emit(zeros)하되 applicability(regression_events_total>=1) false → NA."""
    run_root = tmp_path / "run"
    summary = _run(run_root)
    assert summary["emitted"] is True
    assert summary["regression_events_total"] == 0

    report = meta_audit.run_meta_audit(
        run_root, "G4", manifest_path=_scoped_manifest(tmp_path),
        checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "NA", report["results"][CHECK_ID]["reasons"]
    assert CHECK_ID in report.get("na", [])
    assert CHECK_ID not in report["failed"]


# --- (3) PASS -----------------------------------------------------------------


def test_kernel_passes_when_corroborated(tmp_path):
    run_root = tmp_path / "run"
    _clean(run_root)
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["class_argmax_match"]["value"] == 1
    assert ev.measured["routing_matches_class"]["value"] == 1
    assert ev.measured["undiagnosed_events"]["value"] == 0
    v = _verify(run_root)
    assert v.result == "PASS", v.reasons


# --- (4)-(11) FAIL ------------------------------------------------------------


def test_undiagnosed_event_fails(tmp_path):
    """회귀인데 bound 진단 없음 → undiagnosed_events≥1."""
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    # bisect.md 없음(또는 gate_history_ref 불일치) → 미진단.
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["undiagnosed_events"]["value"] >= 1
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("undiagnosed_events" in r for r in v.reasons)


def test_too_few_hypotheses_fails(tmp_path):
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="c-a", defect_class="plan_defect")
    _write_hypothesis(sprint, 1, agent_call_id="c-b", defect_class="plan_defect")  # 2 < floor 3
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["hypotheses_count"]["value"] == 2
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("hypotheses_count" in r for r in v.reasons)


def test_duplicate_call_ids_fails(tmp_path):
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="dup", defect_class="plan_defect")
    _write_hypothesis(sprint, 1, agent_call_id="dup", defect_class="plan_defect")  # 중복
    _write_hypothesis(sprint, 2, agent_call_id="c-c", defect_class="plan_defect")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["duplicate_call_ids"]["value"] >= 1
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("duplicate_call_ids" in r for r in v.reasons)


def test_invalid_class_vote_fails(tmp_path):
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="c-a", defect_class="plan_defect")
    _write_hypothesis(sprint, 1, agent_call_id="c-b", defect_class="plan_defect")
    _write_hypothesis(sprint, 2, agent_call_id="c-c", defect_class="bogus_defect")  # 무효
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["invalid_class_votes"]["value"] >= 1
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("invalid_class_votes" in r for r in v.reasons)


def test_corroboration_below_min_fails(tmp_path):
    """전원 서로 다른 valid class → corroboration_count==1 < 2."""
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="c-a", defect_class="plan_defect")
    _write_hypothesis(sprint, 1, agent_call_id="c-b", defect_class="impl_defect")
    _write_hypothesis(sprint, 2, agent_call_id="c-c", defect_class="data_defect")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["corroboration_count"]["value"] == 1
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("corroboration_count" in r for r in v.reasons)


def test_declared_class_not_argmax_fails(tmp_path):
    """2 impl / 1 plan → argmax impl_defect, 선언 plan_defect → class_argmax_match==0."""
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="c-a", defect_class="impl_defect")
    _write_hypothesis(sprint, 1, agent_call_id="c-b", defect_class="impl_defect")
    _write_hypothesis(sprint, 2, agent_call_id="c-c", defect_class="plan_defect")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["class_argmax_match"]["value"] == 0
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("class_argmax_match" in r for r in v.reasons)


def test_routing_mismatch_fails(tmp_path):
    """argmax plan_defect == 선언 이지만 fix_target_phase=08 != FAILURE_TO_PHASE[plan_defect]=06."""
    assert checkpoint.FAILURE_TO_PHASE["plan_defect"] == "06"
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="08")  # 잘못된 라우팅
    for i, cid in enumerate(("c-a", "c-b", "c-c")):
        _write_hypothesis(sprint, i, agent_call_id=cid, defect_class="plan_defect")
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["class_argmax_match"]["value"] == 1
    assert ev.measured["routing_matches_class"]["value"] == 0
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("routing_matches_class" in r for r in v.reasons)


def test_missing_alternative_fails(tmp_path):
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="c-a", defect_class="plan_defect")
    _write_hypothesis(sprint, 1, agent_call_id="c-b", defect_class="plan_defect")
    _write_hypothesis(sprint, 2, agent_call_id="c-c", defect_class="plan_defect",
                      omit=("alternative_class",))  # 대안 결손
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["malformed_hypotheses"]["value"] == 0  # 대안 결손은 malformed 아님
    assert ev.measured["hypotheses_without_alternative"]["value"] == 1
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("hypotheses_without_alternative" in r for r in v.reasons)


# --- (12) manifest floors by grade --------------------------------------------


def test_floors_from_real_manifest_by_grade():
    assert producer._load_floors(producer._DEFAULT_MANIFEST, "G4") == (3, 2)
    assert producer._load_floors(producer._DEFAULT_MANIFEST, "G5") == (4, 2)
    # G2/G3 는 min_hypotheses 에 없음 → floor 미해결(상상 금지).
    assert producer._load_floors(producer._DEFAULT_MANIFEST, "G3") is None


# --- (13) CLI subprocess + digest ---------------------------------------------


def test_cli_subprocess_matches_pattern_and_deterministic(tmp_path):
    run_root = tmp_path / "run"
    _clean(run_root)
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--grade", "G4", "--measured-at", FIXED_TS, "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = _ev(run_root)
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)
    rel = ev.measured["corroboration_count"]["artifact_path"]
    assert evidence_mod.sha256_of_file(run_root / rel) == ev.artifact_digests[rel]


# --- (+) threshold drift guard ------------------------------------------------


def test_regression_threshold_matches_sprint_regression_checkspec():
    """producer -0.05 상수가 checks/sprint.regression.json assertion 임계와 drift 없음."""
    spec = json.loads((REAL_CHECKS_DIR / "sprint.regression.json").read_text(encoding="utf-8"))
    expr = spec["assertions"][0]["expr"]  # "score_delta >= -0.05 ..."
    m = re.search(r"-\d+\.\d+", expr)
    assert m is not None, expr
    assert float(m.group(0)) == producer.REGRESSION_SCORE_DELTA_THRESHOLD


# --- suspect grounding (v0.9.61) ----------------------------------------------


def test_suspect_grounded_passes(tmp_path):
    """impl 파일 suspect 가 회귀 게이트 실관측 touched 셋에 실재 → grounded ≥ 1 → PASS."""
    run_root = tmp_path / "run"
    _clean(run_root)   # impl hyp suspect = internal/auth/token.py:42
    _write_scope_map(run_root, "00", ["internal/auth/token.py", "internal/auth/session.py"])
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["suspect_anchor_present"]["value"] == 1
    assert ev.measured["file_suspect_count"]["value"] == 1     # impl_defect 만(plan 2 제외)
    assert ev.measured["grounded_file_suspects"]["value"] == 1
    assert _verify(run_root).result == "PASS", _verify(run_root).reasons


def test_fabricated_suspect_fails(tmp_path):
    """앵커 존재 + impl 파일 suspect 가 touched 셋 어디에도 없음 → 조작 → FAIL."""
    run_root = tmp_path / "run"
    _clean(run_root)
    _write_scope_map(run_root, "00", ["src/unrelated.py"])   # suspect 미포함
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["suspect_anchor_present"]["value"] == 1
    assert ev.measured["file_suspect_count"]["value"] == 1
    assert ev.measured["grounded_file_suspects"]["value"] == 0
    v = _verify(run_root)
    assert v.result == "FAIL"
    assert any("grounded_file_suspects" in r for r in v.reasons)


def test_absent_anchor_exempt_passes(tmp_path):
    """scope_map 앵커 부재(NN-아카이브 없음/빈 diff) → suspect_anchor_present==0 → exempt PASS."""
    run_root = tmp_path / "run"
    _clean(run_root)   # scope_map 안 씀
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["suspect_anchor_present"]["value"] == 0
    assert _verify(run_root).result == "PASS"


def test_sha_suspect_is_exempt(tmp_path):
    """impl suspect 가 commit SHA(파일 아님) → file_suspect_count 제외 → 앵커 있어도 exempt PASS."""
    run_root = tmp_path / "run"
    _write_regression_event(run_root, "00", 0.92, 0.78)
    sprint = _write_bisect(run_root, "01", gate_history_ref="00", prior=0.92, current=0.78,
                           regression_class="plan_defect", fix_target_phase="06")
    _write_hypothesis(sprint, 0, agent_call_id="c-a", defect_class="plan_defect")
    _write_hypothesis(sprint, 1, agent_call_id="c-b", defect_class="plan_defect")
    _write_hypothesis(sprint, 2, agent_call_id="c-c", defect_class="impl_defect",
                      suspect="a1b2c3d4e5f6")   # commit SHA — 파일 suspect 아님
    _write_scope_map(run_root, "00", ["src/unrelated.py"])
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["suspect_anchor_present"]["value"] == 1
    assert ev.measured["file_suspect_count"]["value"] == 0   # SHA 제외
    assert _verify(run_root).result == "PASS"
