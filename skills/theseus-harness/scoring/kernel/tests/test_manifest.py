"""manifest.py 단위 테스트 — 로더 + 질의 API + 드리프트 체크.

실제 저장소 checks/ 에 의존하지 않고 tmp_path fixture 로 자족적으로 검증한다
(WP3 가 아직 checks/ 레지스트리를 만들지 않았다).

실행: python -m pytest skills/theseus-harness/scoring/kernel -q
"""
from __future__ import annotations

import json

import manifest as manifest_mod
import pytest
from manifest import (
    ManifestError,
    active_checks,
    drift_check,
    load_manifest,
    multiverse_width,
    phases_for_grade,
    stop_policy,
)


def _manifest_dict() -> dict:
    """자족 fixture — 실제 매니페스트 구조를 축약하되 01.5·메타 키·checks 를 포함."""
    return {
        "manifest_schema_version": "1.0",
        "_authority": "메타 키는 그레이드 맵에서 걸러져야 한다.",
        "phases": [
            {"id": "00", "name": "naming", "active_grades": ["G3", "G4", "G5"]},
            {"id": "01", "name": "intent", "active_grades": ["G2", "G3", "G4", "G5"]},
            {"id": "04", "name": "clarify", "active_grades": ["G2", "G3", "G4", "G5"]},
            {"id": "01.5", "name": "hidden-intent", "active_grades": ["G3", "G4", "G5"]},
            {"id": "07", "name": "plan-recursion", "active_grades": ["G4", "G5"]},
        ],
        "multiverse_widths": {
            "G2": 1, "G3": 3, "G4": 4, "G5": 6,
            "_note": "메타 키 — 그레이드가 아니다.",
        },
        "frozen_widths": {"G3": 5, "G4": 7, "G5": 9, "_note": "동결 폭."},
        "checks": {
            "G2": [],
            "G3": ["scoring.correctness"],
            "G4": ["scoring.correctness", "scoring.solid"],
            "G5": ["scoring.correctness", "scoring.solid"],
            "_note": "메타 키 — 그레이드가 아니다.",
        },
    }


def _write_manifest(tmp_path, data=None) -> object:
    p = tmp_path / "pipeline.manifest.json"
    p.write_text(json.dumps(data or _manifest_dict()), encoding="utf-8")
    return p


def _write_registry(checks_dir, check_ids) -> None:
    checks_dir.mkdir(parents=True, exist_ok=True)
    for cid in check_ids:
        (checks_dir / f"{cid}.json").write_text(
            json.dumps({"check_id": cid}), encoding="utf-8"
        )


# --- 로더 ----------------------------------------------------------------------


def test_load_parses_phases_widths_checks(tmp_path):
    m = load_manifest(_write_manifest(tmp_path))
    assert m.manifest_schema_version == "1.0"
    assert len(m.phases) == 5
    # '_' 메타 키가 그레이드 맵에서 걸러졌는가.
    assert set(m.multiverse_widths) == {"G2", "G3", "G4", "G5"}
    assert set(m.frozen_widths) == {"G3", "G4", "G5"}
    assert set(m.checks) == {"G2", "G3", "G4", "G5"}
    assert m.frozen_widths["G5"] == 9


def test_load_missing_field_raises(tmp_path):
    bad = _manifest_dict()
    del bad["multiverse_widths"]
    with pytest.raises(ManifestError):
        load_manifest(_write_manifest(tmp_path, bad))


def test_load_absent_file_raises(tmp_path):
    with pytest.raises(ManifestError):
        load_manifest(tmp_path / "nope.json")


# --- 질의 API — 그레이드별 정확한 값 -------------------------------------------


def test_active_checks_per_grade(tmp_path):
    m = load_manifest(_write_manifest(tmp_path))
    assert active_checks(m, "G2") == []
    assert active_checks(m, "G3") == ["scoring.correctness"]
    assert active_checks(m, "G4") == ["scoring.correctness", "scoring.solid"]
    # 미정의 그레이드는 빈 리스트.
    assert active_checks(m, "G9") == []


def test_multiverse_width_per_grade(tmp_path):
    m = load_manifest(_write_manifest(tmp_path))
    assert multiverse_width(m, "G2") == 1
    assert multiverse_width(m, "G3") == 3
    assert multiverse_width(m, "G4") == 4
    assert multiverse_width(m, "G5") == 6


def test_multiverse_width_unknown_grade_raises(tmp_path):
    # 조용한 default 금지 — 미정의 그레이드는 loud fail(설계 P1 silent-default 배제).
    m = load_manifest(_write_manifest(tmp_path))
    with pytest.raises(ManifestError):
        multiverse_width(m, "G9")


def test_phases_for_grade(tmp_path):
    m = load_manifest(_write_manifest(tmp_path))
    # G2 는 00(G3+)·01.5(G3+)·07(G4+) 비활성 → intent + clarify 만.
    g2_ids = [p["id"] for p in phases_for_grade(m, "G2")]
    assert g2_ids == ["01", "04"]
    # G4 는 전 페이즈 활성(fixture 기준).
    g4_ids = [p["id"] for p in phases_for_grade(m, "G4")]
    assert g4_ids == ["00", "01", "04", "01.5", "07"]


# --- 스칼라 count 부재 보증 — 01.5 가 phases 에 실재 ---------------------------


def test_no_scalar_phase_count_and_01_5_present(tmp_path):
    """페이즈 수는 리스트 길이로만 존재 — 별도 count 스칼라가 없어야 드리프트 불가."""
    m = load_manifest(_write_manifest(tmp_path))
    assert "phase_count" not in m.raw
    assert "phases_count" not in m.raw
    ids = [p["id"] for p in m.phases]
    assert "01.5" in ids  # hidden-intent 가 열거에 실재
    # 개수는 리스트 길이 그 자체.
    assert len(m.phases) == len(ids)


# --- drift_check — 세 시나리오 -------------------------------------------------


def test_drift_check_consistent_when_all_present(tmp_path):
    m = load_manifest(_write_manifest(tmp_path))
    checks_dir = tmp_path / "checks"
    _write_registry(checks_dir, ["scoring.correctness", "scoring.solid"])
    assert drift_check(m, checks_dir) == []


def test_drift_check_reports_missing_registry_file(tmp_path):
    m = load_manifest(_write_manifest(tmp_path))
    checks_dir = tmp_path / "checks"
    # solid 를 누락 → 매니페스트가 참조하나 파일 없음.
    _write_registry(checks_dir, ["scoring.correctness"])
    problems = drift_check(m, checks_dir)
    assert len(problems) == 1
    assert "scoring.solid" in problems[0]
    assert "missing registry file" in problems[0]


def test_drift_check_detects_orphan_file(tmp_path):
    m = load_manifest(_write_manifest(tmp_path))
    checks_dir = tmp_path / "checks"
    # 매니페스트에 없는 orphan 파일 추가.
    _write_registry(
        checks_dir, ["scoring.correctness", "scoring.solid", "scoring.orphan"]
    )
    problems = drift_check(m, checks_dir)
    assert len(problems) == 1
    assert "orphan" in problems[0]
    assert "scoring.orphan.json" in problems[0]


def test_drift_check_empty_checks_dir_with_no_refs(tmp_path):
    # checks 가 전부 빈 배열(현재 매니페스트 상태)이면 빈 레지스트리와도 정합.
    data = _manifest_dict()
    data["checks"] = {"G2": [], "G3": [], "G4": [], "G5": []}
    m = load_manifest(_write_manifest(tmp_path, data))
    checks_dir = tmp_path / "checks"
    checks_dir.mkdir()
    assert drift_check(m, checks_dir) == []


# --- CLI -----------------------------------------------------------------------


def test_cli_drift_check_exit_codes(tmp_path):
    """CLI: 정합 → exit 0, 드리프트 → exit 1, stdout 은 문제 JSON."""
    import subprocess
    import sys
    from pathlib import Path

    manifest_py = Path(manifest_mod.__file__)
    manifest_path = _write_manifest(tmp_path)
    checks_dir = tmp_path / "checks"
    _write_registry(checks_dir, ["scoring.correctness", "scoring.solid"])

    proc = subprocess.run(
        [sys.executable, str(manifest_py), "drift-check",
         "--manifest", str(manifest_path), "--checks-dir", str(checks_dir)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["ok"] is True

    # solid 파일 제거 → 드리프트 → exit 1.
    (checks_dir / "scoring.solid.json").unlink()
    proc2 = subprocess.run(
        [sys.executable, str(manifest_py), "drift-check",
         "--manifest", str(manifest_path), "--checks-dir", str(checks_dir)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc2.returncode == 1
    out = json.loads(proc2.stdout)
    assert out["ok"] is False
    assert any("scoring.solid" in p for p in out["problems"])


# --- stop_policy 블록 (설계 B2 §2.2 종료 단일 권위, additive) -------------------


def test_stop_policy_absent_defaults_empty(tmp_path):
    """fixture 에 stop_policy 없으면 빈 dict — 선택 필드(하위호환)."""
    m = load_manifest(_write_manifest(tmp_path))
    assert m.stop_policy == {}
    assert stop_policy(m) == {}


def test_stop_policy_loaded_and_exposed_when_present(tmp_path):
    """stop_policy 블록이 있으면 로드·노출 — _note·plateau_window 중첩 구조 보존."""
    data = _manifest_dict()
    data["stop_policy"] = {
        "gate": "meta_audit_verdict_pass",
        "no_regression": True,
        "plateau_eps": 0.005,
        "plateau_window": {"G3": 2, "G4": 2, "G5": 3},
        "budget_hard_cap": 0.95,
        "_note": "종료 단일 권위.",
    }
    m = load_manifest(_write_manifest(tmp_path, data))
    sp = stop_policy(m)
    assert sp["gate"] == "meta_audit_verdict_pass"
    assert sp["budget_hard_cap"] == 0.95
    # 그레이드 맵 아님 — _note·중첩 window 를 필터하지 않고 그대로 노출.
    assert sp["plateau_window"] == {"G3": 2, "G4": 2, "G5": 3}
    assert "_note" in sp


def test_stop_policy_non_object_raises(tmp_path):
    data = _manifest_dict()
    data["stop_policy"] = ["not", "an", "object"]
    with pytest.raises(ManifestError):
        load_manifest(_write_manifest(tmp_path, data))


def test_stop_policy_does_not_affect_drift_check(tmp_path):
    """stop_policy 는 additive — drift-check(manifest↔checks 정합)에 무영향."""
    data = _manifest_dict()
    data["stop_policy"] = {"gate": "meta_audit_verdict_pass", "budget_hard_cap": 0.95}
    m = load_manifest(_write_manifest(tmp_path, data))
    checks_dir = tmp_path / "checks"
    _write_registry(checks_dir, ["scoring.correctness", "scoring.solid"])
    assert drift_check(m, checks_dir) == []


# --- 실제 저장소 매니페스트 정합 (드리프트 판정 근거 회귀 가드) ----------------


def test_real_manifest_loads_and_enumerates_16_phases():
    """저장소 pipeline.manifest.json 이 16 페이즈(00-14 + 01.5)를 열거하는지 회귀 가드."""
    from pathlib import Path

    repo_manifest = (
        Path(manifest_mod.__file__).resolve().parents[2] / "pipeline.manifest.json"
    )
    m = load_manifest(repo_manifest)
    ids = [p["id"] for p in m.phases]
    assert len(ids) == 16
    assert "01.5" in ids
    assert ids[-1] == "14"  # handoff 가 마지막
    assert multiverse_width(m, "G3") == 3
    assert multiverse_width(m, "G5") == 6
    assert m.frozen_widths == {"G3": 5, "G4": 7, "G5": 9}
    # stop_policy 종료 단일 권위 블록(B2 §2.2) 이 실 매니페스트에 존재.
    sp = stop_policy(m)
    assert sp.get("gate") == "meta_audit_verdict_pass"
    assert sp.get("budget_hard_cap") == 0.95
    assert sp.get("plateau_window", {}).get("G5") == 3
