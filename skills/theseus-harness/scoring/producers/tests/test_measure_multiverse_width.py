"""measure_multiverse_width.py(증거 조립기) 테스트 — 멀티버스 폭 강제 primitive.

요구 매핑(fixture 자족):
  (1) producer 가 plan 디스크(candidates 디렉터리 + round0 tournament 표)를 스캔해 measured
      (폭 신호)만 provenance 붙여 emit — verdict 는 measured 에 안 섞인다.
  (2) round0 폭 >= 활성 폭 바닥 + phantom 없음 → 커널 PASS.
  (3) round0 폭 < 바닥 → 커널 FAIL(초기 폭 skip).
  (4) *핵심 회귀 방어* under-width-then-rerun: round0=2(바닥 4), candidates=5(rerun 누적) →
      max() 였다면 5>=4 PASS 였을 것을 round0-primary 가 FAIL 로 잡는다(우회 차단).
  (5) round0 표 파싱 불가(=0)면 candidates 로 폴백 → PASS(비표준 라벨 레이아웃 구제).
  (6) round0 표가 인용한 universe 의 디렉터리 부재(phantom) → 커널 FAIL(무결성).
  (7) candidates collapse(디렉터리 삭제, round0 표만) → phantom 검사 면제 → PASS.
  (8) 비휴면: plan 부재 → evidence 미기록 → meta_audit 가 NA 아니라 FAIL.
  (9) width_floor 는 manifest multiverse_widths[grade] 단일 소스.
  (10) 실 subprocess producer_cmd(canonical) 정합 + digest 대조.
  (11) cmd_pattern 이 --manifest override 를 거부(floor 몰래 낮추기 봉쇄).

실행: python -m pytest skills/theseus-harness/scoring/producers -q
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import checkspec
import evidence as evidence_mod
import kernel
import measure_multiverse_width as producer
import meta_audit

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "multiverse.fan_out_width"
FIXED_TS = "2026-07-12T00:00:00+00:00"

# 활성 폭 바닥은 실 manifest 단일 소스에서 읽는다 — 폭 변경 시 테스트가 자동 추종.
FLOOR_G4 = producer._load_width_floor(Path(producer._DEFAULT_MANIFEST), "G4")


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _mk_universes(plan_dir: Path, ids) -> None:
    for i in ids:
        d = plan_dir / "candidates" / f"universe-{i}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "06-plan.md").write_text(f"universe {i} plan", encoding="utf-8")


def _mk_round0(plan_dir: Path, ids, name: str = "tournament-00.md") -> None:
    plan_dir.mkdir(parents=True, exist_ok=True)
    lines = ["| universe | score |", "|---|---|"]
    lines += [f"| universe-{i} | 0.9 |" for i in ids]
    (plan_dir / name).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run(run_root: Path, grade: str = "G4"):
    argv = ["--grade", grade, "--out-dir", str(run_root / "evidence"), "--measured-at", FIXED_TS]
    return producer.run(producer.build_parser().parse_args(argv))


def _ev(run_root: Path):
    return evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")


def test_producer_emits_measured_no_verdict(tmp_path):
    """요구(1): measured 폭 키만, verdict 없음, provenance 완전."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _mk_round0(plan, [1, 2, 3, 4])
    _mk_universes(plan, [1, 2, 3, 4])
    summary = _run(run_root)
    assert summary["emitted"] is True

    ev = _ev(run_root)
    assert ev.produced_by == "run" and ev.self_reported is False
    assert set(ev.measured.keys()) == {
        "plan_round0_tournament_width", "plan_candidates_width",
        "round0_rows_without_dirs", "plan_observed_width",
        "impl_candidates_width", "width_floor",
    }
    assert ev.measured["plan_round0_tournament_width"]["value"] == 4
    assert ev.measured["plan_candidates_width"]["value"] == 4
    assert ev.measured["round0_rows_without_dirs"]["value"] == 0
    assert ev.measured["width_floor"]["value"] == FLOOR_G4
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    import json
    assert "verdict" not in json.dumps(ev.to_dict())


def test_kernel_passes_when_round0_meets_floor(tmp_path):
    """요구(2): round0 >= floor + phantom 0 → PASS."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _mk_round0(plan, range(1, FLOOR_G4 + 1))
    _mk_universes(plan, range(1, FLOOR_G4 + 1))
    _run(run_root)
    v = kernel.verify(_spec(), _ev(run_root), artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert v.value == FLOOR_G4   # plan_observed_width


def test_kernel_fails_when_round0_below_floor(tmp_path):
    """요구(3): round0 < floor → 초기 폭 skip FAIL."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _mk_round0(plan, range(1, FLOOR_G4))          # floor-1 개
    _mk_universes(plan, range(1, FLOOR_G4))
    _run(run_root)
    v = kernel.verify(_spec(), _ev(run_root), artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"


def test_under_width_then_rerun_still_fails(tmp_path):
    """요구(4) 핵심: 초기 폭 2(바닥 4) + rerun 누적 candidates 5 → round0-primary FAIL.

    max(dirs, round0)=5>=4 로 게이팅했다면 PASS 였을 우회를, round0 우선 assertion 이 차단한다."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    under = max(1, FLOOR_G4 - 2)
    _mk_round0(plan, range(1, under + 1))                 # round0 = under(<floor)
    _mk_universes(plan, range(1, FLOOR_G4 + 2))           # candidates = floor+1(누적)
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["plan_round0_tournament_width"]["value"] == under
    assert ev.measured["plan_candidates_width"]["value"] == FLOOR_G4 + 1
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL", "round0<floor 인데 누적 candidates 로 통과되면 우회"


def test_fallback_to_candidates_when_rows_unparseable(tmp_path):
    """요구(5): round0 표가 비표준 라벨(U1)이라 파싱 0 → candidates 폴백 PASS."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    plan.mkdir(parents=True, exist_ok=True)
    # universe-N 패턴이 아닌 라벨 → round0 파싱 0
    (plan / "tournament-00.md").write_text(
        "| U1 | 0.9 |\n| U2 | 0.8 |\n| U3 | 0.7 |\n| U4 | 0.6 |\n", encoding="utf-8"
    )
    _mk_universes(plan, range(1, FLOOR_G4 + 1))
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["plan_round0_tournament_width"]["value"] == 0
    assert ev.measured["plan_candidates_width"]["value"] == FLOOR_G4
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons


def test_phantom_rows_without_dirs_fail(tmp_path):
    """요구(6): round0 표가 인용한 universe 의 디렉터리 부재 → phantom FAIL."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _mk_round0(plan, range(1, FLOOR_G4 + 1))   # 표는 floor 개 인용
    _mk_universes(plan, range(1, FLOOR_G4 - 1))  # 디렉터리는 floor-2 개
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["round0_rows_without_dirs"]["value"] == 2
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("round0_rows_without_dirs" in r for r in v.reasons)


def test_post_collapse_dirs_deleted_passes(tmp_path):
    """요구(7): candidates collapse(디렉터리 0) + round0 표 >= floor → phantom 면제 PASS."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _mk_round0(plan, range(1, FLOOR_G4 + 1))   # round0 = floor
    # candidates 디렉터리 없음(collapse)
    _run(run_root)
    ev = _ev(run_root)
    assert ev.measured["plan_candidates_width"]["value"] == 0
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons


def test_absent_plan_is_fail_not_na(tmp_path):
    """요구(8) 비휴면: plan 부재 → evidence 미기록 → meta_audit FAIL(NA 아님)."""
    import json
    run_root = tmp_path / "run"
    summary = _run(run_root)   # plan 디렉터리 없음
    assert summary["emitted"] is False
    assert not (run_root / "evidence" / f"{CHECK_ID}.json").exists()

    manifest_path = tmp_path / "pipeline.manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "06", "name": "plan", "active_grades": ["G4"]}],
        "multiverse_widths": {"G4": FLOOR_G4},
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


def test_meta_audit_passes_when_width_clean(tmp_path):
    """요구(2') 게이트가 실제로 '열린다': round0 >= floor 깨끗 → meta_audit PASS."""
    import json
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _mk_round0(plan, range(1, FLOOR_G4 + 1))
    _mk_universes(plan, range(1, FLOOR_G4 + 1))
    _run(run_root)
    manifest_path = tmp_path / "pipeline.manifest.json"
    manifest_path.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "06", "name": "plan", "active_grades": ["G4"]}],
        "multiverse_widths": {"G4": FLOOR_G4},
        "frozen_widths": {"G4": 7},
        "checks": {"G4": [CHECK_ID]},
    }), encoding="utf-8")
    report = meta_audit.run_meta_audit(
        run_root, "G4", manifest_path=manifest_path,
        checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "PASS", report["results"][CHECK_ID]["reasons"]
    assert report["verdict"] == "pass"


def test_width_floor_from_manifest_by_grade():
    """요구(9): width_floor 는 manifest multiverse_widths[grade] 단일 소스."""
    m = Path(producer._DEFAULT_MANIFEST)
    assert producer._load_width_floor(m, "G2") == 1
    assert producer._load_width_floor(m, "G3") == 3
    assert producer._load_width_floor(m, "G4") == 4
    assert producer._load_width_floor(m, "G5") == 6
    assert producer._load_width_floor(m, "G9") is None   # 미지의 grade → 상상 금지


def test_cli_subprocess_matches_pattern_and_deterministic(tmp_path):
    """요구(10): 실 subprocess canonical producer_cmd 정합 + digest 대조."""
    run_root = tmp_path / "run"
    plan = run_root / "plan"
    _mk_round0(plan, range(1, FLOOR_G4 + 1))
    _mk_universes(plan, range(1, FLOOR_G4 + 1))
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--grade", "G4", "--measured-at", FIXED_TS,
         "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = _ev(run_root)
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)
    rel = ev.measured["plan_round0_tournament_width"]["artifact_path"]
    assert evidence_mod.sha256_of_file(run_root / rel) == ev.artifact_digests[rel]


def test_cmd_pattern_rejects_manifest_override():
    """요구(11): cmd_pattern 이 --manifest override 를 거부(floor 몰래 낮추기 봉쇄)."""
    pat = _spec().producer.cmd_pattern
    canonical = "python /x/producers/measure_multiverse_width.py --grade G4 --out-dir /r/evidence"
    doctored = "python /x/producers/measure_multiverse_width.py --grade G4 --manifest /bad.json --out-dir /r/evidence"
    assert re.search(pat, canonical)
    assert not re.search(pat, doctored)
