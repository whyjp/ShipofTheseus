"""kernel.py 단위 테스트 — 5법칙 (a)~(i) + 결정성 + '무노동 만점' 회귀.

각 법칙이 명시 순서대로 게이트를 태우는지, 그리고 같은 증거가 비트 재현되는지를
독립 테스트로 증명한다.

실행: python -m pytest skills/theseus-harness/scoring/kernel -q
"""
from __future__ import annotations

import copy

import evidence
import kernel
from checkspec import from_dict as spec_from_dict

# 결정성 검증용 고정 타임스탬프 — verified_at 주입으로 비트 재현을 가능케 한다.
FIXED_TS = "2026-07-04T00:00:00+00:00"

_CMD = "python scoring/producers/measure_tests.py --suite tests/ --junit results/junit.xml"


def _artifact(tmp_path, rel="results/junit.xml", content="<junit tests='42' failures='0'/>"):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _good_evidence_dict(tmp_path) -> dict:
    """디스크 artifact 와 정합하는 유효 Evidence dict (happy path 는 PASS)."""
    art = _artifact(tmp_path)
    digest = evidence.sha256_of_file(art)
    return {
        "evidence_schema_version": "1.0",
        "check_id": "scoring.correctness",
        "phase": "09",
        "project_run": "run_001",
        "produced_by": "run",
        "producer_cmd": _CMD,
        "producer_exit_code": 0,
        "measured": {
            "tests_total": {"value": 42, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml"},
            "tests_passed": {"value": 40, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml"},
            "tests_failed": {"value": 0, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml"},
        },
        "artifact_digests": {"results/junit.xml": "sha256:" + digest},
        "measured_at": "2026-07-04T10:00:00Z",
        "self_reported": False,
    }


def _spec(**over):
    base = {
        "check_id": "scoring.correctness",
        "phase": "09",
        "grades": ["G2", "G3", "G4", "G5"],
        "status": "active",
        "producer": {
            "cmd_pattern": r"^python scoring/producers/measure_tests\.py ",
            "must_exit_zero": True,
        },
        "provenance_required": ["tests_total", "tests_passed", "tests_failed"],
        "assertions": [
            {"expr": "tests_total > 0", "on_fail": "no tests executed"},
            {"expr": "tests_failed == 0", "on_fail": "failing tests present"},
        ],
        "value": "tests_passed / tests_total",
        "absence_policy": "FAIL",
    }
    base.update(over)
    return spec_from_dict(base)


def _verify(tmp_path, data, spec=None):
    ev = evidence.from_dict(data)
    return kernel.verify(
        spec or _spec(), ev, artifact_root=tmp_path, verified_at=FIXED_TS
    )


def test_happy_path_passes(tmp_path):
    v = _verify(tmp_path, _good_evidence_dict(tmp_path))
    assert v.result == "PASS"
    assert v.reasons == []


# --- (a) 법칙1: 증거 부재/공백/파싱불가 → FAIL(evidence_missing) ---------------


def test_a_law1_missing_evidence_fails(tmp_path):
    # 부재/공백/파싱불가 세 경우 모두 로더가 None 을 돌려주고, verify(None) 은 FAIL.
    assert evidence.try_load_evidence(tmp_path / "absent.json") is None
    (tmp_path / "blank.json").write_text("   ", encoding="utf-8")
    assert evidence.try_load_evidence(tmp_path / "blank.json") is None
    (tmp_path / "bad.json").write_text("{oops", encoding="utf-8")
    assert evidence.try_load_evidence(tmp_path / "bad.json") is None

    v = kernel.verify(_spec(), None, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("evidence_missing" in r for r in v.reasons)
    assert v.evidence_digest == ""  # 증거 없음 → 추적할 digest 도 없음


# --- (b) 법칙2: self_reported:true (비화이트리스트) → FAIL ---------------------


def test_b_law2_self_reported_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    data["self_reported"] = True
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("self_reported" in r for r in v.reasons)


def test_b_law2_produced_by_assert_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    data["produced_by"] = "assert"
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("produced_by" in r for r in v.reasons)


# --- (c) 법칙2: measured 값 provenance 결손 → FAIL -----------------------------


def test_c_law2_provenance_gap_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    del data["measured"]["tests_total"]["artifact_path"]
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("tests_total" in r and "artifact_path" in r for r in v.reasons)


def test_c_law2_required_key_absent_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    del data["measured"]["tests_failed"]
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("tests_failed" in r for r in v.reasons)


# --- (d) 법칙3: producer_cmd 가 cmd_pattern 불일치 → FAIL ----------------------


def test_d_law3_cmd_pattern_mismatch_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    data["producer_cmd"] = "python scoring/producers/measure_something_else.py"
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("cmd_pattern" in r for r in v.reasons)


# --- (e) 법칙3: producer_exit_code != 0 → FAIL --------------------------------


def test_e_law3_nonzero_exit_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    data["producer_exit_code"] = 1
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("producer_exit_code" in r for r in v.reasons)


# --- (f) 법칙3: artifact_digests 가 디스크 실파일 hash 와 불일치 → FAIL --------


def test_f_law3_artifact_digest_mismatch_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    # 증거는 원본 content 의 hash 를 선언했으나, 디스크 파일을 바꿔 hash 를 어긋나게 한다.
    # → 커널이 상상이 아니라 '디스크 실파일'을 읽어 대조함을 증명.
    _artifact(tmp_path, content="<junit tests='999' failures='7'/>")
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("digest mismatch" in r for r in v.reasons)


def test_f_law3_artifact_missing_on_disk_fails(tmp_path):
    data = _good_evidence_dict(tmp_path)
    (tmp_path / "results" / "junit.xml").unlink()
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert any("artifact missing on disk" in r for r in v.reasons)


# --- (g) 법칙4: assertion AND — 한 술어 거짓 → FAIL(on_fail), 전부 참 → PASS --


def test_g_law4_false_assertion_fails_with_on_fail(tmp_path):
    data = _good_evidence_dict(tmp_path)
    data["measured"]["tests_failed"]["value"] = 3  # tests_failed == 0 이 거짓
    v = _verify(tmp_path, data)
    assert v.result == "FAIL"
    assert v.reasons == ["failing tests present"]  # 첫 거짓 술어의 on_fail 만


def test_g_law4_all_true_assertions_pass(tmp_path):
    v = _verify(tmp_path, _good_evidence_dict(tmp_path))
    assert v.result == "PASS"


def test_g_law4_unsafe_assertion_fails_safely(tmp_path):
    # CheckSpec 에 위험 식이 들어와도 임의 실행 없이 FAIL 로 안전 처리.
    data = _good_evidence_dict(tmp_path)
    spec = _spec(assertions=[{"expr": "__import__('os').system('echo x') == 0", "on_fail": "x"}])
    v = _verify(tmp_path, data, spec=spec)
    assert v.result == "FAIL"
    assert any("unsafe" in r for r in v.reasons)


# --- (h) 법칙5: value 는 measured 값의 함수 ------------------------------------


def test_h_law5_value_is_function_of_measured(tmp_path):
    data = _good_evidence_dict(tmp_path)
    v = _verify(tmp_path, data)
    assert v.result == "PASS"
    assert v.value == 40 / 42

    data2 = _good_evidence_dict(tmp_path)
    data2["measured"]["tests_passed"]["value"] = 21
    v2 = _verify(tmp_path, data2)
    assert v2.value == 21 / 42 == 0.5


# --- (i) 결정성 / 비트 재현 ---------------------------------------------------


def test_i_determinism_bit_reproducible(tmp_path):
    data = _good_evidence_dict(tmp_path)
    ev = evidence.from_dict(data)
    v1 = kernel.verify(_spec(), ev, artifact_root=tmp_path, verified_at=FIXED_TS)
    v2 = kernel.verify(_spec(), ev, artifact_root=tmp_path, verified_at=FIXED_TS)
    # 판정 내용 완전 동일 (verified_at 은 compare=False 라 동등성에서 제외).
    assert v1 == v2
    assert v1.to_dict() == v2.to_dict()
    assert v1.evidence_digest == v2.evidence_digest

    # verified_at 이 달라도 Verdict 동등성은 유지 — 결정성이 시각에 의존하지 않음.
    v3 = kernel.verify(_spec(), ev, artifact_root=tmp_path, verified_at="9999-01-01T00:00:00+00:00")
    assert v1 == v3
    assert v3.verified_at != v1.verified_at
    assert v3.evidence_digest == v1.evidence_digest


def test_i_evidence_digest_matches_record_digest(tmp_path):
    data = _good_evidence_dict(tmp_path)
    ev = evidence.from_dict(data)
    v = kernel.verify(_spec(), ev, artifact_root=tmp_path, verified_at=FIXED_TS)
    assert v.evidence_digest == ev.digest()


# --- '무노동 만점' 방지 회귀 (files_touched==0 이면 만점 아니라 FAIL) ----------


def test_no_work_no_perfect_score(tmp_path):
    """P1 회귀 가드: 아무것도 안 건드렸는데(files_touched==0) scope_fit 가 만점이 되면 안 된다.

    _safe_div(default=1.0) 스타일의 '무노동 만점'을 CheckSpec 술어(files_touched > 0)로
    구조적으로 봉쇄한다 — 0 이면 value(만점) 계산에 도달하기 전에 FAIL.
    """
    art = _artifact(tmp_path, rel="diff/summary.txt", content="0 files changed")
    digest = evidence.sha256_of_file(art)
    data = {
        "evidence_schema_version": "1.0",
        "check_id": "scoring.scope_fit",
        "phase": "09",
        "project_run": "run_001",
        "produced_by": "run",
        "producer_cmd": "python scoring/producers/measure_scope.py --diff diff/summary.txt",
        "producer_exit_code": 0,
        "measured": {
            "files_touched": {"value": 0, "source": "git_diff", "artifact_path": "diff/summary.txt"},
            "files_mapped_to_todos": {"value": 0, "source": "git_diff", "artifact_path": "diff/summary.txt"},
        },
        "artifact_digests": {"diff/summary.txt": "sha256:" + digest},
        "measured_at": "2026-07-04T10:00:00Z",
        "self_reported": False,
    }
    spec = spec_from_dict({
        "check_id": "scoring.scope_fit",
        "phase": "09",
        "grades": ["G2"],
        "status": "active",
        "producer": {"cmd_pattern": r"^python scoring/producers/measure_scope\.py ", "must_exit_zero": True},
        "provenance_required": ["files_touched", "files_mapped_to_todos"],
        "assertions": [{"expr": "files_touched > 0", "on_fail": "no files touched (no-work perfect-score guard)"}],
        "value": "files_mapped_to_todos / files_touched",
        "absence_policy": "FAIL",
    })
    v = kernel.verify(spec, evidence.from_dict(data), artifact_root=tmp_path, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert v.reasons == ["no files touched (no-work perfect-score guard)"]
    # 만점은커녕 value 계산(0으로 나눗셈)에 도달조차 하지 않는다.
    assert v.value is None


def test_cli_verify_pass_and_fail(tmp_path):
    """CLI 진입점: PASS → exit 0, FAIL → exit 1, stdout 은 Verdict JSON."""
    import json
    import subprocess
    import sys
    from pathlib import Path

    kernel_py = Path(kernel.__file__)
    data = _good_evidence_dict(tmp_path)
    ev_path = tmp_path / "evidence.json"
    ev_path.write_text(json.dumps(data), encoding="utf-8")
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps({
        "check_id": "scoring.correctness",
        "phase": "09",
        "producer": {"cmd_pattern": r"^python scoring/producers/measure_tests\.py ", "must_exit_zero": True},
        "provenance_required": ["tests_total", "tests_passed", "tests_failed"],
        "assertions": [{"expr": "tests_failed == 0", "on_fail": "failing tests present"}],
        "value": "tests_passed / tests_total",
    }), encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, str(kernel_py), "verify", "--spec", str(spec_path),
         "--evidence", str(ev_path), "--verified-at", FIXED_TS, "--artifact-root", str(tmp_path)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["result"] == "PASS"

    # exit 1 경로: 증거 파일을 지우면 evidence_missing FAIL.
    ev_path.unlink()
    proc2 = subprocess.run(
        [sys.executable, str(kernel_py), "verify", "--spec", str(spec_path),
         "--evidence", str(ev_path), "--verified-at", FIXED_TS],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc2.returncode == 1
    assert json.loads(proc2.stdout)["result"] == "FAIL"
