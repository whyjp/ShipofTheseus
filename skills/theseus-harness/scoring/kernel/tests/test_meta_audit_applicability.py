"""meta_audit 적용성(NA) 정책 단위 테스트 (WP4a) — '증거로 입증된 NA', 침묵 skip 아님.

자족 fixture(demo.* 네임스페이스)로 정책만 검증한다 — 실 scoring 레지스트리와 분리.
kernel.verify 는 순수 PASS/FAIL 을 유지하고, NA 판정은 meta_audit(정책)이 소유함을 확인.

실행: python -m pytest skills/theseus-harness/scoring/kernel -q
"""
from __future__ import annotations

import json

import evidence as evidence_mod
import meta_audit

FIXED_TS = "2026-07-04T00:00:00+00:00"


def _spec_dict(check_id: str) -> dict:
    """side_flag 로 적용성을 가르는 demo spec. 적용될 때만 value_a 술어를 본다."""
    return {
        "check_id": check_id,
        "phase": "09",
        "grades": ["G3"],
        "status": "active",
        "producer": {"cmd_pattern": r"^python .*measure_demo\.py", "must_exit_zero": True},
        "provenance_required": ["side_flag"],
        "applicability": "side_flag == 1",
        "assertions": [{"expr": "value_a > 0", "on_fail": "value_a must be positive"}],
        "value": "value_a",
        "absence_policy": "FAIL",
    }


def _plain_spec_dict(check_id: str) -> dict:
    """적용성 없는 demo spec — 항상 게이팅(대조군)."""
    d = _spec_dict(check_id)
    d.pop("applicability")
    d["provenance_required"] = ["value_a"]
    return d


def _write_spec(checks_dir, check_id, spec):
    checks_dir.mkdir(parents=True, exist_ok=True)
    (checks_dir / f"{check_id}.json").write_text(json.dumps(spec), encoding="utf-8")


def _write_manifest(tmp_path, ids):
    p = tmp_path / "pipeline.manifest.json"
    p.write_text(json.dumps({
        "manifest_schema_version": "1.0",
        "phases": [{"id": "09", "name": "quality-gates", "active_grades": ["G3"]}],
        "multiverse_widths": {"G3": 3},
        "frozen_widths": {"G3": 5},
        "checks": {"G3": list(ids)},
    }), encoding="utf-8")
    return p


def _write_evidence(run_root, check_id, side_flag, value_a=None, *, tamper=False, produced_by="run"):
    """demo evidence + backing artifact. tamper=True 면 artifact_digests 를 위조."""
    art_rel = f"results/{check_id}.txt"
    art = run_root / art_rel
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_text(f"side_flag={side_flag} value_a={value_a}", encoding="utf-8")
    digest = "sha256:" + ("0" * 64 if tamper else evidence_mod.sha256_of_file(art))

    measured = {"side_flag": {"value": side_flag, "source": "demo", "artifact_path": art_rel}}
    if value_a is not None:
        measured["value_a"] = {"value": value_a, "source": "demo", "artifact_path": art_rel}

    data = {
        "evidence_schema_version": "1.0",
        "check_id": check_id,
        "phase": "09",
        "project_run": "run_001",
        "produced_by": produced_by,
        "producer_cmd": "python scoring/producers/measure_demo.py --check " + check_id,
        "producer_exit_code": 0,
        "measured": measured,
        "artifact_digests": {art_rel: digest},
        "measured_at": "2026-07-04T10:00:00Z",
        "self_reported": False,
    }
    ev_dir = run_root / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    (ev_dir / f"{check_id}.json").write_text(json.dumps(data), encoding="utf-8")


def _audit(tmp_path, run_root, ids):
    return meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=_write_manifest(tmp_path, ids),
        checks_dir=tmp_path / "checks",
        verified_at=FIXED_TS,
    )


# --- 적용성 false + 유효 evidence → NA(비게이팅) --------------------------------


def test_applicability_false_yields_na_nongating(tmp_path):
    _write_spec(tmp_path / "checks", "demo.appl", _spec_dict("demo.appl"))
    _write_spec(tmp_path / "checks", "demo.plain", _plain_spec_dict("demo.plain"))
    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.appl", side_flag=0)          # 단일 사이드
    _write_evidence(run_root, "demo.plain", side_flag=1, value_a=5)

    report = _audit(tmp_path, run_root, ["demo.appl", "demo.plain"])
    assert report["results"]["demo.appl"]["result"] == "NA"
    assert report["na"] == ["demo.appl"]
    assert report["failed"] == []
    assert report["verdict"] == "pass"  # NA 는 verdict 를 막지 않는다


# --- 적용성 true → 커널 완전 판정(PASS/FAIL) ------------------------------------


def test_applicability_true_gates_pass(tmp_path):
    _write_spec(tmp_path / "checks", "demo.appl", _spec_dict("demo.appl"))
    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.appl", side_flag=1, value_a=5)
    report = _audit(tmp_path, run_root, ["demo.appl"])
    assert report["results"]["demo.appl"]["result"] == "PASS"
    assert report["na"] == []


def test_applicability_true_gates_fail_on_assertion(tmp_path):
    _write_spec(tmp_path / "checks", "demo.appl", _spec_dict("demo.appl"))
    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.appl", side_flag=1, value_a=0)  # value_a>0 위반
    report = _audit(tmp_path, run_root, ["demo.appl"])
    assert report["results"]["demo.appl"]["result"] == "FAIL"
    assert any("value_a must be positive" in r for r in report["results"]["demo.appl"]["reasons"])


# --- NA 도 증거로 입증: 부재/위조는 NA 가 아니라 FAIL --------------------------


def test_absent_evidence_is_fail_not_na(tmp_path):
    """적용성 있는 체크라도 evidence 부재면 FAIL(evidence_missing) — 적용성은 부재를
    구할 수 없다."""
    _write_spec(tmp_path / "checks", "demo.appl", _spec_dict("demo.appl"))
    run_root = tmp_path / "run"
    (run_root / "evidence").mkdir(parents=True)  # evidence 안 씀
    report = _audit(tmp_path, run_root, ["demo.appl"])
    assert report["results"]["demo.appl"]["result"] == "FAIL"
    assert report["na"] == []
    assert any("evidence_missing" in r for r in report["results"]["demo.appl"]["reasons"])


def test_tampered_digest_cannot_claim_na(tmp_path):
    """핵심: 적용성 false 를 주장하는 evidence 라도 artifact digest 가 위조면 무결성
    검사(법칙3)에서 걸려 NA 가 아니라 FAIL. 가짜 evidence 로 게이트를 NA 로 회피 불가."""
    _write_spec(tmp_path / "checks", "demo.appl", _spec_dict("demo.appl"))
    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.appl", side_flag=0, tamper=True)
    report = _audit(tmp_path, run_root, ["demo.appl"])
    assert report["results"]["demo.appl"]["result"] == "FAIL"
    assert "demo.appl" not in report["na"]
    assert any("digest mismatch" in r for r in report["results"]["demo.appl"]["reasons"])


def test_self_reported_evidence_cannot_claim_na(tmp_path):
    """produced_by 가 'run' 이 아니면(자기 신고) 무결성 실패 → NA 아님 FAIL."""
    _write_spec(tmp_path / "checks", "demo.appl", _spec_dict("demo.appl"))
    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.appl", side_flag=0, produced_by="assert")
    report = _audit(tmp_path, run_root, ["demo.appl"])
    assert report["results"]["demo.appl"]["result"] == "FAIL"
    assert "demo.appl" not in report["na"]
