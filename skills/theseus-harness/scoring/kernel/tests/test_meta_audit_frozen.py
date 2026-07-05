"""meta_audit frozen/advisory 정책 단위 테스트 (WP6, 설계 §8 동결).

자족 fixture(demo.* 네임스페이스)로 정책만 검증한다 — 실 scoring 레지스트리와 분리.
kernel.verify 는 이 WP 에서도 순수 PASS/FAIL 을 유지한다(수정 금지 대상, 읽기만).
frozen 분류(ADVISORY)는 meta_audit._evaluate_check 정책 레이어가 소유하며, NA 와
마찬가지로 커널 판정 자체를 바꾸지 않고 '그 판정을 게이팅에 쓰지 않는다'만 바꾼다.

실행: python -m pytest skills/theseus-harness/scoring/kernel/tests/test_meta_audit*.py -q
"""
from __future__ import annotations

import json
from pathlib import Path

import evidence as evidence_mod
import kernel
import meta_audit

FIXED_TS = "2026-07-04T00:00:00+00:00"

# 이 파일: .../scoring/kernel/tests/test_meta_audit_frozen.py
# parents[3] == skills/theseus-harness (meta_audit.py 의 parents[2] 규약과 동일 기준,
# 이 파일이 tests/ 한 단계 아래에 있는 만큼 +1).
_THESEUS_HARNESS_DIR = Path(__file__).resolve().parents[3]
# frozen 예시 스펙은 평면 레지스트리(checks/ top-level)에 산다 — meta_audit 의 flat
# 로드(checks_dir/<id>.json)와 drift_check 의 비재귀 glob 이 찾을 수 있어야 실 파이프라인이
# 이들을 ADVISORY 로 인식한다(오케스트레이터 통합 시 서브디렉터리→top-level 이동).
_REAL_CHECKS_DIR = _THESEUS_HARNESS_DIR / "checks"


# --- 자족 fixture 빌더 (test_meta_audit_applicability.py 관례를 따름) -----------


def _active_spec_dict(check_id: str) -> dict:
    """적용성 없는 평범한 active 체크 — 대조군."""
    return {
        "check_id": check_id,
        "phase": "09",
        "grades": ["G3"],
        "status": "active",
        "producer": {"cmd_pattern": r"^python .*measure_demo\.py", "must_exit_zero": True},
        "provenance_required": ["value_a"],
        "assertions": [{"expr": "value_a > 0", "on_fail": "value_a must be positive"}],
        "value": "value_a",
        "absence_policy": "FAIL",
    }


def _na_capable_spec_dict(check_id: str) -> dict:
    """적용성 있는 active 체크 — side_flag==1 일 때만 게이팅(NA 대조군)."""
    d = _active_spec_dict(check_id)
    d["provenance_required"] = ["side_flag"]
    d["applicability"] = "side_flag == 1"
    return d


def _frozen_spec_dict(check_id: str, *, with_applicability: bool = False) -> dict:
    """status:frozen 체크. with_applicability=True 면 적용성 필드도 같이 둬서
    우선순위(frozen 이 applicability 를 가림)를 시험한다."""
    d = _active_spec_dict(check_id)
    d["status"] = "frozen"
    if with_applicability:
        d["provenance_required"] = ["side_flag"]
        d["applicability"] = "side_flag == 1"
    return d


def _write_spec(checks_dir, check_id: str, spec: dict) -> None:
    checks_dir.mkdir(parents=True, exist_ok=True)
    (checks_dir / f"{check_id}.json").write_text(json.dumps(spec), encoding="utf-8")


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


def _write_evidence(run_root, check_id: str, *, value_a=None, side_flag=None) -> None:
    art_rel = f"results/{check_id}.txt"
    art = run_root / art_rel
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_text(f"value_a={value_a} side_flag={side_flag}", encoding="utf-8")
    digest = evidence_mod.sha256_of_file(art)

    measured = {}
    if value_a is not None:
        measured["value_a"] = {"value": value_a, "source": "demo", "artifact_path": art_rel}
    if side_flag is not None:
        measured["side_flag"] = {"value": side_flag, "source": "demo", "artifact_path": art_rel}

    data = {
        "evidence_schema_version": "1.0",
        "check_id": check_id,
        "phase": "09",
        "project_run": "run_001",
        "produced_by": "run",
        "producer_cmd": "python scoring/producers/measure_demo.py --check " + check_id,
        "producer_exit_code": 0,
        "measured": measured,
        "artifact_digests": {art_rel: "sha256:" + digest},
        "measured_at": "2026-07-04T10:00:00Z",
        "self_reported": False,
    }
    ev_dir = run_root / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    (ev_dir / f"{check_id}.json").write_text(json.dumps(data), encoding="utf-8")


def _audit(tmp_path, run_root, ids, checks_dir=None):
    return meta_audit.run_meta_audit(
        run_root, "G3",
        manifest_path=_write_manifest(tmp_path, ids),
        checks_dir=checks_dir or (tmp_path / "checks"),
        verified_at=FIXED_TS,
    )


# --- (1) frozen + evidence 완전 부재 → ADVISORY, verdict pass -------------------


def test_frozen_check_with_no_evidence_is_advisory_and_does_not_block_verdict(tmp_path):
    """§8 동결의 핵심 증명: A/B measurer 가 아직 없어 evidence 가 아예 없어도
    (실 frozen.* 예시가 처한 상황과 동일) frozen 체크는 종료를 막지 않는다."""
    _write_spec(tmp_path / "checks", "demo.frozen_check", _frozen_spec_dict("demo.frozen_check"))
    run_root = tmp_path / "run"
    (run_root / "evidence").mkdir(parents=True)  # evidence 자체를 안 씀

    report = _audit(tmp_path, run_root, ["demo.frozen_check"])

    assert report["verdict"] == "pass"
    assert report["failed"] == []
    assert report["advisory"] == ["demo.frozen_check"]
    outcome = report["results"]["demo.frozen_check"]
    assert outcome["result"] == "ADVISORY"
    # 정보 보존: 커널이 실제로 낸 판정(FAIL, evidence_missing)은 값으로 남는다.
    assert outcome["kernel_result"] == "FAIL"
    assert any("evidence_missing" in r for r in outcome["reasons"])


# --- (2) frozen + evidence 있음 + assertion 위반(커널 FAIL) → 그래도 ADVISORY --


def test_frozen_check_kernel_fail_is_recorded_but_nongating(tmp_path):
    _write_spec(tmp_path / "checks", "demo.frozen_check", _frozen_spec_dict("demo.frozen_check"))
    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.frozen_check", value_a=0)  # value_a>0 위반

    report = _audit(tmp_path, run_root, ["demo.frozen_check"])

    assert report["verdict"] == "pass"
    assert report["failed"] == []
    assert report["advisory"] == ["demo.frozen_check"]
    outcome = report["results"]["demo.frozen_check"]
    assert outcome["result"] == "ADVISORY"
    assert outcome["kernel_result"] == "FAIL"
    assert outcome["reasons"] == ["value_a must be positive"]


# --- (3) frozen 우선순위 — applicability 필드가 있어도 frozen 이 가린다 --------


def test_frozen_takes_priority_over_applicability_even_when_applicability_false(tmp_path):
    """side_flag=0 이면 applicability(side_flag==1) 은 거짓이라, 이 체크가 active 였다면
    NA 가 됐을 상황(test_meta_audit_applicability.py 의 대조군과 동일 조건)이다. 그러나
    status:frozen 이면 적용성 판정 자체에 도달하지 않고 곧장 ADVISORY 여야 한다."""
    spec = _frozen_spec_dict("demo.frozen_appl", with_applicability=True)
    _write_spec(tmp_path / "checks", "demo.frozen_appl", spec)
    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.frozen_appl", side_flag=0, value_a=5)

    report = _audit(tmp_path, run_root, ["demo.frozen_appl"])

    assert report["na"] == []  # NA 로 새지 않는다 — frozen 이 우선
    assert report["advisory"] == ["demo.frozen_appl"]
    outcome = report["results"]["demo.frozen_appl"]
    assert outcome["result"] == "ADVISORY"
    # kernel 은 applicability 를 모른다 — assertions(value_a>0)만 평가해 PASS.
    assert outcome["kernel_result"] == "PASS"


# --- (4) active/na/advisory/failed 4 집합 상호 배타성 --------------------------


def test_active_na_advisory_failed_are_mutually_exclusive(tmp_path):
    checks_dir = tmp_path / "checks"
    _write_spec(checks_dir, "demo.active_pass", _active_spec_dict("demo.active_pass"))
    _write_spec(checks_dir, "demo.active_fail", _active_spec_dict("demo.active_fail"))
    _write_spec(checks_dir, "demo.na_check", _na_capable_spec_dict("demo.na_check"))
    _write_spec(checks_dir, "demo.frozen_check", _frozen_spec_dict("demo.frozen_check"))

    run_root = tmp_path / "run"
    _write_evidence(run_root, "demo.active_pass", value_a=5)
    _write_evidence(run_root, "demo.active_fail", value_a=0)  # assertion 위반 → FAIL
    _write_evidence(run_root, "demo.na_check", side_flag=0)  # 적용 안 됨 → NA
    # demo.frozen_check 는 evidence 미기록 — ADVISORY(1)과 동일 상황.

    ids = ["demo.active_pass", "demo.active_fail", "demo.na_check", "demo.frozen_check"]
    report = _audit(tmp_path, run_root, ids)

    assert report["failed"] == ["demo.active_fail"]
    assert report["na"] == ["demo.na_check"]
    assert report["advisory"] == ["demo.frozen_check"]
    # 배타성: 네 집합 어디에도 겹치는 check_id 가 없다.
    failed_s, na_s, adv_s = set(report["failed"]), set(report["na"]), set(report["advisory"])
    assert failed_s.isdisjoint(na_s)
    assert failed_s.isdisjoint(adv_s)
    assert na_s.isdisjoint(adv_s)
    # demo.active_pass 는 어느 특수 집합에도 없다(암묵적 PASS/게이팅 통과) — 그러면서도
    # active_checks(전체 열거) 에는 포함된다.
    assert "demo.active_pass" not in failed_s | na_s | adv_s
    assert set(report["active_checks"]) == set(ids)
    # FAIL 이 하나 있으므로 전체 verdict 는 fail — NA/ADVISORY 는 게이팅에 무관함을
    # active_fail 하나만으로도 verdict 가 이미 흔들린다는 사실이 대조 증명한다.
    assert report["verdict"] == "fail"
    assert report["results"]["demo.active_pass"]["result"] == "PASS"


# --- (5) 실 frozen 예시 CheckSpec (checks/frozen/) 자체가 유효하고 ADVISORY 산출 --


def test_real_frozen_example_checkspecs_are_valid_and_advisory(tmp_path):
    """이 WP 가 만든 실 예시 파일(frozen.multiverse_width_benefit / frozen.viewer_mandatory)이
    checkspec 로 로드 가능하고 status:frozen 이며, 아직 A/B measurer 가 없어 evidence 가
    없는 상태에서도(오늘의 현실) meta_audit 가 이들을 ADVISORY 로 분류해 verdict 를
    막지 않음을 실 파일로 증명한다."""
    ids = ["frozen.multiverse_width_benefit", "frozen.viewer_mandatory"]
    report = meta_audit.run_meta_audit(
        tmp_path / "empty_run", "G3",
        manifest_path=_write_manifest(tmp_path, ids),
        checks_dir=_REAL_CHECKS_DIR,
        verified_at=FIXED_TS,
    )
    assert report["verdict"] == "pass"
    assert report["failed"] == []
    assert set(report["advisory"]) == set(ids)
    for check_id in ids:
        assert report["results"][check_id]["result"] == "ADVISORY"
        assert report["results"][check_id]["kernel_result"] == "FAIL"
        assert any("evidence_missing" in r for r in report["results"][check_id]["reasons"])
