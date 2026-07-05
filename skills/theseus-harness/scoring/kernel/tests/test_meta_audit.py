"""meta_audit.py 단위 테스트 — 생성형 메타 감사 + P5(하드코딩 사각) 구조적 제거 증명.

실제 저장소 checks/ 나 pipeline.manifest.json 에 의존하지 않고 tmp_path fixture 로
자족적으로 검증한다(test_manifest.py 관례를 그대로 따른다) — 단, 회귀 테스트
(test_real_manifest_checks_registry_has_six_scoring_dimensions) 만 예외적으로 실제
저장소 산출물을 읽어 WP3 완료 상태를 값으로 확인한다.

실행: python -m pytest skills/theseus-harness/scoring/kernel -q
"""
from __future__ import annotations

import json

import evidence as evidence_mod
import manifest as manifest_mod
import meta_audit

FIXED_TS = "2026-07-04T00:00:00+00:00"


# --- 자족 fixture 빌더 ----------------------------------------------------------


def _spec_dict(check_id: str) -> dict:
    """단일 measured 키(value_a)만 갖는 최소 CheckSpec — meta_audit 배관 검증용.

    demo.* 네임스페이스를 써서 실제 scoring.* 레지스트리와 완전히 분리한다.
    """
    return {
        "check_id": check_id,
        "phase": "09",
        "grades": ["G3"],
        "status": "active",
        "producer": {
            "cmd_pattern": r"^python .*measure_demo\.py",
            "must_exit_zero": True,
        },
        "provenance_required": ["value_a"],
        "assertions": [{"expr": "value_a > 0", "on_fail": "value_a must be positive"}],
        "value": "value_a",
        "absence_policy": "FAIL",
    }


def _write_spec(checks_dir, check_id: str) -> None:
    checks_dir.mkdir(parents=True, exist_ok=True)
    (checks_dir / f"{check_id}.json").write_text(
        json.dumps(_spec_dict(check_id)), encoding="utf-8"
    )


def _write_artifact(run_root, rel: str, content: str):
    p = run_root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _write_passing_evidence(run_root, check_id: str, value: int = 5) -> None:
    """이 check_id 의 evidence + 그 evidence 가 참조하는 artifact 를 함께 기록."""
    art_rel = f"results/{check_id}.txt"
    art = _write_artifact(run_root, art_rel, f"value_a={value}")
    digest = evidence_mod.sha256_of_file(art)
    data = {
        "evidence_schema_version": "1.0",
        "check_id": check_id,
        "phase": "09",
        "project_run": "run_001",
        "produced_by": "run",
        "producer_cmd": "python scoring/producers/measure_demo.py --check " + check_id,
        "producer_exit_code": 0,
        "measured": {
            "value_a": {"value": value, "source": "demo", "artifact_path": art_rel},
        },
        "artifact_digests": {art_rel: "sha256:" + digest},
        "measured_at": "2026-07-04T10:00:00Z",
        "self_reported": False,
    }
    ev_dir = run_root / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    (ev_dir / f"{check_id}.json").write_text(json.dumps(data), encoding="utf-8")


def _write_manifest(tmp_path, check_ids: list[str]):
    p = tmp_path / "pipeline.manifest.json"
    data = {
        "manifest_schema_version": "1.0",
        "phases": [{"id": "09", "name": "quality-gates", "active_grades": ["G3"]}],
        "multiverse_widths": {"G3": 3},
        "frozen_widths": {"G3": 5},
        "checks": {"G3": list(check_ids)},
    }
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def _spec_dict_phase(check_id: str, phase: str) -> dict:
    """임의 페이즈를 갖는 최소 CheckSpec — --phase-upto 단계 스코프 검증용."""
    d = _spec_dict(check_id)
    d["phase"] = phase
    return d


def _write_spec_phase(checks_dir, check_id: str, phase: str) -> None:
    checks_dir.mkdir(parents=True, exist_ok=True)
    (checks_dir / f"{check_id}.json").write_text(
        json.dumps(_spec_dict_phase(check_id, phase)), encoding="utf-8"
    )


def _write_two_phase_manifest(tmp_path, check_ids: list[str]):
    """phases 순서에 09 와 10 을 둔 매니페스트 — 페이즈 이하/초과 비교의 기반."""
    p = tmp_path / "pipeline.manifest.json"
    data = {
        "manifest_schema_version": "1.0",
        "phases": [
            {"id": "09", "name": "quality-gates", "active_grades": ["G3"]},
            {"id": "10", "name": "test-loop", "active_grades": ["G3"]},
        ],
        "multiverse_widths": {"G3": 3},
        "frozen_widths": {"G3": 5},
        "checks": {"G3": list(check_ids)},
    }
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


# --- (i) 활성 체크 전부 evidence 존재 + 커널 통과 → verdict pass ----------------


def test_all_active_checks_pass_yields_verdict_pass(tmp_path):
    checks_dir = tmp_path / "checks"
    _write_spec(checks_dir, "demo.checkA")
    _write_spec(checks_dir, "demo.checkB")
    manifest_path = _write_manifest(tmp_path, ["demo.checkA", "demo.checkB"])

    run_root = tmp_path / "run"
    _write_passing_evidence(run_root, "demo.checkA")
    _write_passing_evidence(run_root, "demo.checkB")

    report = meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=manifest_path, checks_dir=checks_dir, verified_at=FIXED_TS,
    )

    assert report["verdict"] == "pass"
    assert report["failed"] == []
    assert set(report["active_checks"]) == {"demo.checkA", "demo.checkB"}
    assert report["results"]["demo.checkA"]["result"] == "PASS"
    assert report["results"]["demo.checkB"]["result"] == "PASS"


# --- (ii) 한 체크의 evidence 부재 → verdict fail, evidence_missing -------------


def test_missing_evidence_for_one_check_fails_with_evidence_missing_reason(tmp_path):
    checks_dir = tmp_path / "checks"
    _write_spec(checks_dir, "demo.checkA")
    _write_spec(checks_dir, "demo.checkB")
    manifest_path = _write_manifest(tmp_path, ["demo.checkA", "demo.checkB"])

    run_root = tmp_path / "run"
    _write_passing_evidence(run_root, "demo.checkA")
    # demo.checkB 는 evidence 를 아예 안 씀 — 부재.

    report = meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=manifest_path, checks_dir=checks_dir, verified_at=FIXED_TS,
    )

    assert report["verdict"] == "fail"
    assert report["failed"] == ["demo.checkB"]
    assert report["results"]["demo.checkA"]["result"] == "PASS"
    b = report["results"]["demo.checkB"]
    assert b["result"] == "FAIL"
    assert any("evidence_missing" in r for r in b["reasons"])
    assert b["value"] is None


# --- (iii) P5 수정 증명 — 신규 check_id 를 코드 변경 없이 자동 감사 ------------


def test_new_check_id_is_automatically_audited_without_code_change(tmp_path):
    """P5 회귀 증명(핵심).

    phase_invoke_audit.py 는 신규 CLI 를 감사하려면 사람이 `CLI_TRACE_PATHS` dict
    (파이썬 소스)에 항목을 직접 추가해야 한다 — 안 하면 `invoked: None ->
    audit_skipped` 이고 `overall_pass = len(not_invoked) == 0` 이라 사각이 FAIL 을
    유발하지 않는다(phase_invoke_audit.py 의 CLI_TRACE_PATHS/evaluate 참조).

    meta_audit.py 는 그런 매핑 dict 자체가 없다 — `run_meta_audit` 은
    `manifest.active_checks(m, grade)` 가 돌려주는 목록을 그대로 순회한다. 이 테스트는
    "코드 변경 0" 상태로(= 이 파일을 건드리지 않고) checks_dir 에 새 spec 파일을
    떨어뜨리고 매니페스트에 항목 하나를 추가하는 것만으로 그 체크가 자동으로 감사
    대상에 들어와 evidence 부재 시 FAIL 됨을 값으로 증명한다.
    """
    checks_dir = tmp_path / "checks"
    _write_spec(checks_dir, "demo.checkA")
    manifest_path = _write_manifest(tmp_path, ["demo.checkA"])

    run_root = tmp_path / "run"
    _write_passing_evidence(run_root, "demo.checkA")

    baseline = meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=manifest_path, checks_dir=checks_dir, verified_at=FIXED_TS,
    )
    assert baseline["verdict"] == "pass"
    assert baseline["active_checks"] == ["demo.checkA"]

    # --- 신규 체크 등록: 파일 + 매니페스트 항목만 추가, meta_audit.py 는 무손 ---
    _write_spec(checks_dir, "demo.checkC")  # 새 CheckSpec 파일 추가
    manifest_path = _write_manifest(tmp_path, ["demo.checkA", "demo.checkC"])  # 매니페스트 항목 추가
    # demo.checkC 의 evidence 는 의도적으로 쓰지 않는다 (아직 producer 미구현 상황 모사).

    after = meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=manifest_path, checks_dir=checks_dir, verified_at=FIXED_TS,
    )

    assert set(after["active_checks"]) == {"demo.checkA", "demo.checkC"}
    assert after["verdict"] == "fail"
    assert after["failed"] == ["demo.checkC"]
    assert any("evidence_missing" in r for r in after["results"]["demo.checkC"]["reasons"])
    # demo.checkA 는 그대로 PASS — 신규 체크 추가가 기존 체크 판정에 영향 없음.
    assert after["results"]["demo.checkA"]["result"] == "PASS"


# --- (iv) 실 매니페스트 + 실 checks/ 레지스트리 정합 회귀 ----------------------


def test_real_manifest_checks_registry_has_six_scoring_dimensions_and_no_drift():
    """WP3 산출물 회귀 가드: 실 저장소의 6 scoring CheckSpec 이 매니페스트와 정합.

    drift_check 가 두 방향(참조된 id가 파일로 실재 / orphan 파일 없음) 모두 정합임을
    값으로 확인한다. 레지스트리는 WP5(promote)/WP6(frozen) 로 성장하므로 '정확히 6개'가
    아니라 '6 scoring 차원이 존재(부분집합) + drift 0' 로 가드한다 — 성장에 견디되 핵심
    불변식(6 scoring 차원 상시 존재·drift 없음)은 유지.
    """
    manifest_path = meta_audit._DEFAULT_MANIFEST
    checks_dir = meta_audit._DEFAULT_CHECKS_DIR

    m = manifest_mod.load_manifest(manifest_path)
    problems = manifest_mod.drift_check(m, checks_dir)
    assert problems == []

    scoring_ids = {
        "scoring.correctness",
        "scoring.scope_fit",
        "scoring.solid",
        "scoring.coverage",
        "scoring.fe_be_parity",
        "scoring.e2e",
    }
    file_ids = {p.stem for p in checks_dir.glob("*.json")}
    assert scoring_ids <= file_ids

    for grade in ("G2", "G3", "G4", "G5"):
        assert scoring_ids <= set(manifest_mod.active_checks(m, grade))


def test_real_registry_meta_audit_reports_evidence_missing_for_all_six(tmp_path):
    """producer 가 없는 run 은 evidence 부재로 게이팅 체크가 FAIL 이어야 한다 — 결함이
    아니라 §2 원칙2("증거 없음=FAIL")의 올바른 동작이다. 레지스트리 성장(WP5 promote)으로
    G2 활성 체크가 6 scoring + 3 quality 로 늘었으므로 '정확히 6' 대신 '6 scoring 차원이
    전부 evidence_missing 으로 FAIL(부분집합)' 로 가드한다."""
    report = meta_audit.run_meta_audit(
        tmp_path / "empty_run", "G2",
        manifest_path=meta_audit._DEFAULT_MANIFEST,
        checks_dir=meta_audit._DEFAULT_CHECKS_DIR,
        verified_at=FIXED_TS,
    )
    assert report["verdict"] == "fail"
    scoring_ids = {
        "scoring.correctness", "scoring.scope_fit", "scoring.solid",
        "scoring.coverage", "scoring.fe_be_parity", "scoring.e2e",
    }
    assert scoring_ids <= set(report["failed"])
    for check_id in report["failed"]:
        assert any(
            "evidence_missing" in r for r in report["results"][check_id]["reasons"]
        )


# --- --phase-upto 단계 스코프(§2.4) -------------------------------------------


def test_phase_upto_defers_later_phase_check_from_verdict(tmp_path):
    """phase-10 체크가 evidence 부재로 FAIL 이어도 --phase-upto 09 지정 시 deferred(비게이팅)
    로 빠져 verdict 를 막지 않는다. 도달 가능(phase≤09) 체크의 PASS 는 그대로 산입."""
    checks_dir = tmp_path / "checks"
    _write_spec_phase(checks_dir, "demo.p09", "09")
    _write_spec_phase(checks_dir, "demo.p10", "10")  # 나중 페이즈, evidence 미저작 → FAIL
    manifest_path = _write_two_phase_manifest(tmp_path, ["demo.p09", "demo.p10"])

    run_root = tmp_path / "run"
    _write_passing_evidence(run_root, "demo.p09")
    # demo.p10 evidence 는 의도적으로 안 씀(phase-09 시점 원리상 부재 모사).

    report = meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=manifest_path, checks_dir=checks_dir,
        verified_at=FIXED_TS, phase_upto="09",
    )
    assert report["verdict"] == "pass"          # 나중 페이즈 FAIL 이 게이팅 안 함
    assert report["failed"] == []
    assert report["deferred"] == ["demo.p10"]   # 평가·기록은 하되 이 단계 게이트 아님
    # deferred 여도 결과는 results 에 여전히 기록됨(침묵 skip 아님).
    assert report["results"]["demo.p10"]["result"] == "FAIL"
    assert report["results"]["demo.p09"]["result"] == "PASS"


def test_phase_upto_still_strictly_fails_reachable_checks(tmp_path):
    """deferred 는 skipped==pass 관대함 부활이 아니다 — 도달 가능(phase≤09) 체크가
    evidence 부재면 --phase-upto 09 여도 여전히 엄격 FAIL 이다."""
    checks_dir = tmp_path / "checks"
    _write_spec_phase(checks_dir, "demo.p09", "09")
    _write_spec_phase(checks_dir, "demo.p10", "10")
    manifest_path = _write_two_phase_manifest(tmp_path, ["demo.p09", "demo.p10"])

    run_root = tmp_path / "run"
    # demo.p09 evidence 도 안 씀 — 도달 가능한 체크의 부재.
    (run_root / "evidence").mkdir(parents=True)

    report = meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=manifest_path, checks_dir=checks_dir,
        verified_at=FIXED_TS, phase_upto="09",
    )
    assert report["verdict"] == "fail"
    assert report["failed"] == ["demo.p09"]     # 도달 가능 → 엄격 FAIL
    assert report["deferred"] == ["demo.p10"]   # 나중 페이즈 → 비게이팅


def test_phase_upto_unset_is_backward_compatible_no_deferred_key(tmp_path):
    """미지정 시 나중 페이즈 체크도 전부 게이팅되고 report 에 deferred 키가 아예 없다
    (기존 동작·바이트 불변)."""
    checks_dir = tmp_path / "checks"
    _write_spec_phase(checks_dir, "demo.p09", "09")
    _write_spec_phase(checks_dir, "demo.p10", "10")
    manifest_path = _write_two_phase_manifest(tmp_path, ["demo.p09", "demo.p10"])

    run_root = tmp_path / "run"
    _write_passing_evidence(run_root, "demo.p09")
    # demo.p10 evidence 부재.

    report = meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=manifest_path, checks_dir=checks_dir, verified_at=FIXED_TS,
    )
    assert "deferred" not in report             # 미지정 → 키 자체가 없음
    assert report["verdict"] == "fail"
    assert report["failed"] == ["demo.p10"]     # 나중 페이즈도 게이팅


# --- CLI -------------------------------------------------------------------


def test_cli_exit_codes_and_output_files(tmp_path):
    import subprocess
    import sys
    from pathlib import Path

    checks_dir = tmp_path / "checks"
    _write_spec(checks_dir, "demo.checkA")
    manifest_path = _write_manifest(tmp_path, ["demo.checkA"])
    run_root = tmp_path / "run"
    _write_passing_evidence(run_root, "demo.checkA")

    meta_audit_py = Path(meta_audit.__file__)
    output_path = tmp_path / "report.json"

    proc = subprocess.run(
        [
            sys.executable, str(meta_audit_py),
            "--project-root", str(run_root),
            "--grade", "G3",
            "--manifest", str(manifest_path),
            "--checks-dir", str(checks_dir),
            "--output", str(output_path),
            "--verified-at", FIXED_TS,
        ],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["verdict"] == "pass"
    assert output_path.exists()
    assert (run_root / "quality" / "gate_meta_audit.json").exists()

    # evidence 를 지우면 exit 1.
    (run_root / "evidence" / "demo.checkA.json").unlink()
    proc2 = subprocess.run(
        [
            sys.executable, str(meta_audit_py),
            "--project-root", str(run_root),
            "--grade", "G3",
            "--manifest", str(manifest_path),
            "--checks-dir", str(checks_dir),
            "--verified-at", FIXED_TS,
        ],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc2.returncode == 1
    assert json.loads(proc2.stdout)["verdict"] == "fail"
