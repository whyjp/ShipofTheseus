"""evidence.py 단위 테스트 — 스키마 로드/형태검증/artifact 해시/정규화 직렬화.

실행: python -m pytest skills/theseus-harness/scoring/kernel -q
"""
from __future__ import annotations

import hashlib
import json

import evidence
import pytest


def _valid_dict() -> dict:
    return {
        "evidence_schema_version": "1.0",
        "check_id": "scoring.correctness",
        "phase": "09",
        "project_run": "run_001",
        "produced_by": "run",
        "producer_cmd": "python scoring/producers/measure_tests.py --suite tests/",
        "producer_exit_code": 0,
        "measured": {
            "tests_total": {
                "value": 42,
                "source": "pytest_junit_xml",
                "artifact_path": "results/junit.xml",
            }
        },
        "artifact_digests": {"results/junit.xml": "sha256:deadbeef"},
        "measured_at": "2026-07-04T10:00:00Z",
        "self_reported": False,
    }


def test_load_absent_empty_and_unparseable_raise(tmp_path):
    assert not (tmp_path / "nope.json").exists()
    with pytest.raises(evidence.EvidenceParseError):
        evidence.load_evidence(tmp_path / "nope.json")

    blank = tmp_path / "blank.json"
    blank.write_text("   \n\t", encoding="utf-8")
    with pytest.raises(evidence.EvidenceParseError):
        evidence.load_evidence(blank)

    bad = tmp_path / "bad.json"
    bad.write_text("{ this is not json", encoding="utf-8")
    with pytest.raises(evidence.EvidenceParseError):
        evidence.load_evidence(bad)


def test_try_load_absorbs_failures_to_none(tmp_path):
    assert evidence.try_load_evidence(tmp_path / "nope.json") is None


def test_validate_shape_flags_missing_fields():
    d = _valid_dict()
    del d["measured"]
    problems = evidence.validate_shape(d)
    assert any("measured" in p for p in problems)


def test_validate_shape_flags_type_errors():
    d = _valid_dict()
    d["producer_exit_code"] = "0"
    d["self_reported"] = "false"
    problems = evidence.validate_shape(d)
    assert any("producer_exit_code" in p for p in problems)
    assert any("self_reported" in p for p in problems)


def test_sha256_of_file_matches_hashlib(tmp_path):
    art = tmp_path / "artifact.bin"
    content = "값이 있는 산출물\n".encode("utf-8")
    art.write_bytes(content)
    assert evidence.sha256_of_file(art) == hashlib.sha256(content).hexdigest()


def test_normalize_digest_strips_prefix_and_lowercases():
    assert evidence.normalize_digest("sha256:ABC123") == "abc123"
    assert evidence.normalize_digest("  DEADbeef  ") == "deadbeef"


def test_digest_is_deterministic_and_order_independent():
    a = evidence.from_dict(_valid_dict())
    # 키 순서만 다르게 재구성한 동일 내용 — 정규화 직렬화라 digest 동일해야 한다.
    d = _valid_dict()
    reordered = dict(reversed(list(d.items())))
    b = evidence.from_dict(reordered)
    assert a.digest() == b.digest()
    # canonical_json 은 유효 JSON 이고 키가 정렬돼 있다.
    parsed = json.loads(a.canonical_json())
    assert parsed["check_id"] == "scoring.correctness"


def test_provenance_gaps_detects_missing_source_and_path():
    d = _valid_dict()
    d["measured"]["tests_total"].pop("artifact_path")
    d["measured"]["tests_passed"] = {"value": 40, "source": "", "artifact_path": "x"}
    rec = evidence.from_dict(d)
    gaps = rec.provenance_gaps()
    assert any("tests_total" in g and "artifact_path" in g for g in gaps)
    assert any("tests_passed" in g and "source" in g for g in gaps)


def test_measured_values_exposes_only_raw_values():
    rec = evidence.from_dict(_valid_dict())
    assert rec.measured_values() == {"tests_total": 42}
