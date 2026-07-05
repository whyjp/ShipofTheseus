"""fingerprint backing-evidence 검증 (§10, WP7) + base 3서브커맨드 회귀 0.

핵심 증명:
  - 위조: self-hash 만 있고 backing evidence 없는 frontmatter → backed=False (P4).
  - 정상: 디스크 artifact digest 가 일치하는 통과 Evidence Record → backed=True.
  - 재서명 무력화: compute 로 body 를 바꿔 재서명해도 backing 없으면 여전히 backed=False.
  - compute --with-evidence: 같은 body 여도 artifact 가 다르면 지문이 다름(실행에 묶임).
  - 기존 compute/verify/chain 회귀 0.

실행: python -m pytest skills/theseus-harness/scoring/kernel/tests/test_fingerprint_backed.py -q
"""
from __future__ import annotations

import json
import os
import sys

# 이 테스트는 kernel/ (evidence 등) 와 scoring/ (fingerprint, fingerprint_backed) 양쪽의
# 평면 모듈을 쓴다 — conftest 유무와 무관하게 자족하도록 두 경로를 직접 삽입한다.
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_KERNEL_DIR = os.path.dirname(_TESTS_DIR)          # .../scoring/kernel
_SCORING_DIR = os.path.dirname(_KERNEL_DIR)        # .../scoring
for _d in (_KERNEL_DIR, _SCORING_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

import evidence  # noqa: E402
import fingerprint  # noqa: E402
import fingerprint_backed  # noqa: E402

_PRODUCER_CMD = "python scoring/producers/measure_tests.py --suite tests/ --junit results/junit.xml"


# --- 픽스처 헬퍼 (tmp_path 자족) ----------------------------------------------


def _write_artifact_md(
    tmp_path, name="phase-09-artifact.md", phase="09", project_run="run_001",
    prev=None, body="# 산출물\n\n원본 내용\n",
):
    """페이즈 산출물 .md 를 fingerprint compute 로 self-hash 서명해 생성."""
    md = tmp_path / name
    fm = [
        "---",
        "skill_name: theseus-harness",
        "skill_version: 0.9.52",
        f"phase: {phase}",
        "project_id: proj_x",
        f"project_run: {project_run}",
        "---",
        "",
    ]
    md.write_text("\n".join(fm) + body, encoding="utf-8")
    prev_arg = str(prev) if prev is not None else "none"
    fingerprint.main(["compute", "--file", str(md), "--prev", prev_arg])
    return md


def _evidence_dict(art_rel="results/junit.xml", digest="deadbeef", **over):
    data = {
        "evidence_schema_version": "1.0",
        "check_id": "scoring.correctness",
        "phase": "09",
        "project_run": "run_001",
        "produced_by": "run",
        "producer_cmd": _PRODUCER_CMD,
        "producer_exit_code": 0,
        "measured": {
            "tests_total": {"value": 42, "source": "pytest_junit_xml", "artifact_path": art_rel},
            "tests_passed": {"value": 42, "source": "pytest_junit_xml", "artifact_path": art_rel},
            "tests_failed": {"value": 0, "source": "pytest_junit_xml", "artifact_path": art_rel},
        },
        "artifact_digests": {art_rel: "sha256:" + digest},
        "measured_at": "2026-07-04T10:00:00Z",
        "self_reported": False,
    }
    data.update(over)
    return data


def _make_evidence(
    evidence_dir, *, check_id="scoring.correctness", art_rel="results/junit.xml",
    art_content="<junit tests='42' failures='0'/>", corrupt_digest=False, **over,
):
    """evidence-dir 안에 실제 artifact + 그 digest 를 참조하는 Evidence Record 를 생성.

    artifact 는 evidence-dir 아래 두어 verify_backed 의 기본 artifact_root(=evidence-dir)
    로 해석되게 한다."""
    evidence_dir.mkdir(parents=True, exist_ok=True)
    art = evidence_dir / art_rel
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_text(art_content, encoding="utf-8")
    digest = "0" * 64 if corrupt_digest else evidence.sha256_of_file(art)
    data = _evidence_dict(art_rel=art_rel, digest=digest, check_id=check_id, **over)
    ev_path = evidence_dir / (check_id + ".json")
    ev_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return ev_path


def _make_checkspec(checks_dir, check_id="scoring.correctness"):
    checks_dir.mkdir(parents=True, exist_ok=True)
    spec = {
        "check_id": check_id,
        "phase": "09",
        "grades": ["G2", "G3", "G4", "G5"],
        "status": "active",
        "producer": {"cmd_pattern": r"^python scoring/producers/measure_tests\.py ", "must_exit_zero": True},
        "provenance_required": ["tests_total", "tests_passed", "tests_failed"],
        "assertions": [
            {"expr": "tests_total > 0", "on_fail": "no tests executed"},
            {"expr": "tests_failed == 0", "on_fail": "failing tests present"},
        ],
        "value": "tests_passed / tests_total",
        "absence_policy": "FAIL",
    }
    p = checks_dir / (check_id + ".json")
    p.write_text(json.dumps(spec), encoding="utf-8")
    return p


# --- 위조 시나리오 (P4 핵심): self-hash 만 있고 backing 없으면 backed=False --------


def test_forgery_selfhash_only_is_not_backed(tmp_path):
    md = _write_artifact_md(tmp_path)
    # self-hash 자체는 valid — 그러나 그것만으로는 아무것도 보증하지 않는다.
    assert fingerprint.main(["verify", "--file", str(md)]) == 0
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    result = fingerprint_backed.verify_backed(str(md), str(evidence_dir))
    assert result["backed"] is False
    assert any("Evidence Record 없음" in r or "backing 부재" in r for r in result["reasons"])


# --- 정상: 통과한 Evidence Record(디스크 digest 일치) → backed=True ----------------


def test_backed_when_evidence_digest_matches_disk(tmp_path):
    md = _write_artifact_md(tmp_path)
    evidence_dir = tmp_path / "evidence"
    _make_evidence(evidence_dir)
    result = fingerprint_backed.verify_backed(str(md), str(evidence_dir))
    assert result["backed"] is True
    assert any("backed by scoring.correctness" in r for r in result["reasons"])


def test_backed_via_kernel_when_checkspec_present(tmp_path):
    md = _write_artifact_md(tmp_path)
    evidence_dir = tmp_path / "evidence"
    checks_dir = tmp_path / "checks"
    _make_evidence(evidence_dir)
    _make_checkspec(checks_dir)
    result = fingerprint_backed.verify_backed(
        str(md), str(evidence_dir), checks_dir=str(checks_dir)
    )
    assert result["backed"] is True
    assert any("kernel PASS" in r for r in result["reasons"])


def test_kernel_fail_evidence_is_not_backed(tmp_path):
    # 커널 경로에서 assertion 위반(tests_failed != 0) 이면 backing 성립 안 함.
    md = _write_artifact_md(tmp_path)
    evidence_dir = tmp_path / "evidence"
    checks_dir = tmp_path / "checks"
    _make_evidence(
        evidence_dir,
        art_content="<junit tests='42' failures='3'/>",
        measured={
            "tests_total": {"value": 42, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml"},
            "tests_passed": {"value": 39, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml"},
            "tests_failed": {"value": 3, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml"},
        },
    )
    _make_checkspec(checks_dir)
    result = fingerprint_backed.verify_backed(
        str(md), str(evidence_dir), checks_dir=str(checks_dir)
    )
    assert result["backed"] is False
    assert any("kernel FAIL" in r for r in result["reasons"])


# --- 위조: evidence 는 있으나 artifact digest 가 상상값(디스크 불일치) → backed=False -


def test_evidence_with_imagined_digest_is_not_backed(tmp_path):
    md = _write_artifact_md(tmp_path)
    evidence_dir = tmp_path / "evidence"
    _make_evidence(evidence_dir, corrupt_digest=True)
    result = fingerprint_backed.verify_backed(str(md), str(evidence_dir))
    assert result["backed"] is False
    assert any("digest mismatch" in r for r in result["reasons"])


def test_evidence_missing_artifact_on_disk_is_not_backed(tmp_path):
    md = _write_artifact_md(tmp_path)
    evidence_dir = tmp_path / "evidence"
    _make_evidence(evidence_dir)
    (evidence_dir / "results" / "junit.xml").unlink()
    result = fingerprint_backed.verify_backed(str(md), str(evidence_dir))
    assert result["backed"] is False
    assert any("artifact missing on disk" in r for r in result["reasons"])


# --- 재서명 무력화 증명 (P4): body 바꿔 재서명해도 backing 없으면 backed=False -------


def test_resign_after_tamper_still_not_backed(tmp_path):
    md = _write_artifact_md(tmp_path, body="# 산출물\n\n원본 내용\n")
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()

    # 위조자: body 를 조작하고 compute 로 재서명 — self-hash 는 새 본문과 여전히 valid.
    text = md.read_text(encoding="utf-8")
    md.write_text(text.replace("원본 내용", "조작된 내용"), encoding="utf-8")
    fingerprint.main(["compute", "--file", str(md), "--prev", "none"])
    # 재서명이 self-hash verify 는 통과시킨다 — 자기 해시가 위조에 무력함을 직접 보인다.
    assert fingerprint.main(["verify", "--file", str(md)]) == 0

    # 그러나 backing Evidence Record 가 없으므로 verify-backed 는 여전히 위조로 판정.
    result = fingerprint_backed.verify_backed(str(md), str(evidence_dir))
    assert result["backed"] is False


# --- compute --with-evidence: 지문을 실행 artifact 에 묶음 --------------------------


def _plain_md(tmp_path, name, body="# 산출물\n\n동일 본문\n"):
    md = tmp_path / name
    fm = [
        "---",
        "skill_name: theseus-harness",
        "skill_version: 0.9.52",
        "phase: 09",
        "project_id: proj_x",
        "project_run: run_001",
        "---",
        "",
    ]
    md.write_text("\n".join(fm) + body, encoding="utf-8")
    return md


def _fp_of(md):
    fm, _ = fingerprint.parse_frontmatter(md.read_text(encoding="utf-8"))
    return fm["fingerprint"]


def test_with_evidence_binds_same_body_to_different_artifacts(tmp_path):
    # 같은 스키마, 다른 artifact digest 를 선언한 두 Evidence Record.
    ev_a = tmp_path / "ev_a.json"
    ev_b = tmp_path / "ev_b.json"
    ev_a.write_text(json.dumps(_evidence_dict(digest="a" * 64)), encoding="utf-8")
    ev_b.write_text(json.dumps(_evidence_dict(digest="b" * 64)), encoding="utf-8")

    md_a = _plain_md(tmp_path, "a.md")
    md_b = _plain_md(tmp_path, "b.md")  # md_a 와 body·frontmatter 동일
    fingerprint.main(["compute", "--file", str(md_a), "--prev", "none", "--with-evidence", str(ev_a)])
    fingerprint.main(["compute", "--file", str(md_b), "--prev", "none", "--with-evidence", str(ev_b)])

    # 같은 body 여도 backing artifact 가 다르면 지문이 다르다 → 지문이 실행에 묶임(§10).
    assert _fp_of(md_a) != _fp_of(md_b)


def test_with_evidence_is_deterministic_and_differs_from_plain(tmp_path):
    ev = tmp_path / "ev.json"
    ev.write_text(json.dumps(_evidence_dict(digest="c" * 64)), encoding="utf-8")

    md1 = _plain_md(tmp_path, "d1.md")
    md2 = _plain_md(tmp_path, "d2.md")
    md_plain = _plain_md(tmp_path, "d3.md")
    fingerprint.main(["compute", "--file", str(md1), "--prev", "none", "--with-evidence", str(ev)])
    fingerprint.main(["compute", "--file", str(md2), "--prev", "none", "--with-evidence", str(ev)])
    fingerprint.main(["compute", "--file", str(md_plain), "--prev", "none"])

    # 같은 body + 같은 evidence → 같은 지문 (결정성).
    assert _fp_of(md1) == _fp_of(md2)
    # evidence 를 섞은 지문은 self-hash 단독 지문과 다르다 (뿌리가 이동했다).
    assert _fp_of(md1) != _fp_of(md_plain)


def test_compute_fingerprint_none_path_is_backward_compatible():
    # 옵션 인자를 None 으로 둔 경로는 evidence 파트를 붙이지 않아 기존 7-파트와 동일.
    fm = {
        "skill_name": "theseus-harness",
        "skill_version": "0.9.52",
        "phase": "09",
        "project_id": "proj_x",
        "project_run": "run_001",
        "prev_fingerprint": None,
    }
    body = "# 산출물\n\n내용\n"
    assert fingerprint.compute_fingerprint(fm, body) == fingerprint.compute_fingerprint(fm, body, None)
    # 무언가 섞으면 반드시 달라진다.
    assert fingerprint.compute_fingerprint(fm, body) != fingerprint.compute_fingerprint(fm, body, "x")


# --- CLI 배선 + exit code ------------------------------------------------------


def test_cli_verify_backed_exit_codes(tmp_path):
    md = _write_artifact_md(tmp_path)
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    # backing 없음 → exit 1 (fingerprint.py 의 verify-backed 지연 import 경로도 함께 검증).
    assert fingerprint.main(["verify-backed", "--file", str(md), "--evidence-dir", str(evidence_dir)]) == 1
    # 통과 evidence 추가 → exit 0.
    _make_evidence(evidence_dir)
    assert fingerprint.main(["verify-backed", "--file", str(md), "--evidence-dir", str(evidence_dir)]) == 0


# --- 기존 3서브커맨드 회귀 0 ---------------------------------------------------


def test_base_compute_verify_chain_regression(tmp_path):
    chain_dir = tmp_path / "chain"
    chain_dir.mkdir()
    p0 = _write_artifact_md(chain_dir, name="00-naming.md", phase="00", body="# 00\n\n네이밍\n")
    p1 = _write_artifact_md(chain_dir, name="01-intent.md", phase="01", prev=p0, body="# 01\n\n의도\n")

    # verify: 각 산출물 self-hash 통과.
    assert fingerprint.main(["verify", "--file", str(p0)]) == 0
    assert fingerprint.main(["verify", "--file", str(p1)]) == 0

    # p1 의 prev_fingerprint 가 p0 의 fingerprint 를 가리킨다.
    fm1, _ = fingerprint.parse_frontmatter(p1.read_text(encoding="utf-8"))
    fm0, _ = fingerprint.parse_frontmatter(p0.read_text(encoding="utf-8"))
    assert fm1["prev_fingerprint"] == fm0["fingerprint"]

    # chain: 디렉터리 전체 체인 무결성 통과.
    assert fingerprint.main(["chain", "--dir", str(chain_dir)]) == 0

    # 본문 변조 → self-hash verify 실패 (base verify 여전히 민감).
    p0.write_text(p0.read_text(encoding="utf-8").replace("네이밍", "변조"), encoding="utf-8")
    assert fingerprint.main(["verify", "--file", str(p0)]) == 1
