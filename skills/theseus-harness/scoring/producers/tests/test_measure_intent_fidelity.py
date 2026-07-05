"""measure_intent_fidelity.py(증거 조립기) 테스트 — JW2 (판단-게이트 스펙 §3.2).

요구 매핑:
  (1) parsers.parse_junit_cases: 케이스별 상태 맵 + classname::name 병기 +
      worst-status-wins(동명 케이스 여러 개일 때 가장 나쁜 상태).
  (2) producer 가 criteria 를 claims.py 로 재검사해 intent_fidelity 를 3케이스로
      이산화 — measured 에 verdict/pass 문자열이 섞이지 않는다(가드1).
  (3) 저작 오류(JSON 깨짐/화이트리스트 밖 kind/판정 필드/id 중복)는 exit 2, 결손
      (파일 부재/criteria 0개/required 0개)은 exit 0 no-emit — 둘을 구분한다.
  (4) 실 CheckSpec(scoring.correctness)으로 커널이 실제로 재판정 — PASS 시 value 반영,
      producer 미실행 시 scoring.correctness 결손 유지(skipped). intent_fidelity < 0.7
      (required 미충족) 은 phase-09 hard gate assertion(intent_fidelity >= 0.7)을 어겨
      법칙4에서 FAIL(value=None) — 0.7 은 커널 레벨로 고정된 PASS/FAIL 경계.
  (5) 결정성(바이트 동일 + 서로 다른 루트 measured 동일) + CLI subprocess.

실행: python -m pytest skills/theseus-harness/scoring/producers/tests/test_measure_intent_fidelity.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import checkspec
import evidence as evidence_mod
import kernel
import measure_intent_fidelity as producer
import measure_submission
import parsers

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "gate.intent_fidelity"
FIXED_TS = "2026-07-05T00:00:00+00:00"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / "scoring.correctness.json")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _make_repo(root: Path, base: dict[str, str], changed: dict[str, str]) -> None:
    """base 파일들을 커밋한 뒤 changed 파일들을 워킹트리에만 반영 —
    `git diff --name-only HEAD` 가 changed 키 목록을 내도록 만든다."""
    root.mkdir(parents=True, exist_ok=True)
    run = lambda *a: subprocess.run(
        ["git", "-C", str(root), *a], check=True, capture_output=True,
        text=True, encoding="utf-8")
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    for rel, text in base.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    run("add", "-A")
    run("commit", "-q", "-m", "base")
    for rel, text in changed.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def _junit(path: Path, cases: list[tuple[str, str | None, str]]) -> Path:
    """cases: (name, classname|None, status). status ∈ passed/failed/error/skipped."""
    parts = [f'<testsuite tests="{len(cases)}">']
    for name, classname, status in cases:
        attrs = f'name="{name}"'
        if classname:
            attrs += f' classname="{classname}"'
        if status == "failed":
            parts.append(f'<testcase {attrs}><failure message="x"/></testcase>')
        elif status == "error":
            parts.append(f'<testcase {attrs}><error message="x"/></testcase>')
        elif status == "skipped":
            parts.append(f"<testcase {attrs}><skipped/></testcase>")
        else:
            parts.append(f"<testcase {attrs}></testcase>")
    parts.append("</testsuite>")
    return _write(path, "\n".join(parts))


def _criteria(path: Path, entries: list[dict]) -> Path:
    return _write(path, json.dumps({"criteria": entries}, ensure_ascii=False))


def _argv(**kwargs) -> list[str]:
    argv = ["--measured-at", FIXED_TS]
    for k, v in kwargs.items():
        if v is None:
            continue
        argv += [f"--{k.replace('_', '-')}", str(v)]
    return argv


def _run(**kwargs) -> dict:
    args = producer.build_parser().parse_args(_argv(**kwargs))
    return producer.run(args)


def _main(**kwargs) -> int:
    return producer.main(_argv(**kwargs))


# --- (1) parse_junit_cases ------------------------------------------------------


def test_parse_junit_cases_states_and_classname_key(tmp_path):
    junit = _junit(tmp_path / "junit.xml", [
        ("test_a", "pkg.ClassA", "passed"),
        ("test_b", "pkg.ClassB", "failed"),
        ("test_c", "pkg.ClassC", "error"),
        ("test_d", "pkg.ClassD", "skipped"),
    ])
    cases = parsers.parse_junit_cases(junit)
    assert cases["test_a"] == "passed"
    assert cases["pkg.ClassA::test_a"] == "passed"
    assert cases["test_b"] == "failed"
    assert cases["pkg.ClassB::test_b"] == "failed"
    assert cases["test_c"] == "error"
    assert cases["pkg.ClassC::test_c"] == "error"
    assert cases["test_d"] == "skipped"
    assert cases["pkg.ClassD::test_d"] == "skipped"


def test_parse_junit_cases_worst_status_wins(tmp_path):
    junit = _junit(tmp_path / "junit.xml", [
        ("test_dup", "pkg.ClassA", "passed"),
        ("test_dup", "pkg.ClassB", "failed"),
    ])
    cases = parsers.parse_junit_cases(junit)
    assert cases["test_dup"] == "failed"  # bare name merges across classes, worst-wins
    assert cases["pkg.ClassA::test_dup"] == "passed"
    assert cases["pkg.ClassB::test_dup"] == "failed"


def test_parse_junit_cases_file_absent_raises(tmp_path):
    with pytest.raises(parsers.ArtifactParseError):
        parsers.parse_junit_cases(tmp_path / "nope.xml")


# --- (2) 이산화 3케이스 ------------------------------------------------------------


def test_discretize_all_verified_yields_one(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    _write(sub / "b.txt", "y")
    _write(sub / "c.txt", "z")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
        {"id": "c2", "required": True, "backing": {"kind": "file", "ref": "b.txt"}},
        {"id": "c3", "required": False, "backing": {"kind": "file", "ref": "c.txt"}},
    ])
    summary = _run(criteria=criteria, submission=sub, out_dir=tmp_path / "evidence")
    assert summary["emitted"] is True
    assert summary["value"] == 1.0


def test_discretize_required_ok_optional_missing_yields_zero_point_seven(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    _write(sub / "b.txt", "y")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
        {"id": "c2", "required": True, "backing": {"kind": "file", "ref": "b.txt"}},
        {"id": "c3", "required": False, "backing": {"kind": "file", "ref": "missing.txt"}},
    ])
    summary = _run(criteria=criteria, submission=sub, out_dir=tmp_path / "evidence")
    assert summary["value"] == 0.7


def test_discretize_required_missing_yields_zero(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    _write(sub / "c.txt", "z")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
        {"id": "c2", "required": True, "backing": {"kind": "file", "ref": "missing.txt"}},
        {"id": "c3", "required": False, "backing": {"kind": "file", "ref": "c.txt"}},
    ])
    summary = _run(criteria=criteria, submission=sub, out_dir=tmp_path / "evidence")
    assert summary["value"] == 0.0


# --- (3) 결손 vs 저작 오류 --------------------------------------------------------


def test_zero_criteria_no_emit(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    criteria = _criteria(tmp_path / "criteria.json", [])
    out_dir = tmp_path / "evidence"
    summary = _run(criteria=criteria, submission=sub, out_dir=out_dir)
    assert summary["emitted"] is False
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_zero_required_criteria_no_emit(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": False, "backing": {"kind": "file", "ref": "a.txt"}},
    ])
    out_dir = tmp_path / "evidence"
    summary = _run(criteria=criteria, submission=sub, out_dir=out_dir)
    assert summary["emitted"] is False
    assert "no required criteria" in summary["reason"]
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_criteria_file_absent_no_emit(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    out_dir = tmp_path / "evidence"
    summary = _run(criteria=tmp_path / "nope.json", submission=sub, out_dir=out_dir)
    assert summary["emitted"] is False
    assert summary["reason"] == "criteria file absent"
    # exit code 0 (결손, 저작 오류 아님) — main() 경유로 명시 확인.
    rc = _main(criteria=tmp_path / "nope.json", submission=sub, out_dir=out_dir)
    assert rc == 0


def test_broken_json_exit_2_no_emit(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    criteria_path = _write(tmp_path / "criteria.json", "{not valid json")
    out_dir = tmp_path / "evidence"
    rc = _main(criteria=criteria_path, submission=sub, out_dir=out_dir)
    assert rc == 2
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_unknown_backing_kind_exit_2_no_emit(tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "grep", "ref": "x"}},
    ])
    out_dir = tmp_path / "evidence"
    rc = _main(criteria=criteria, submission=sub, out_dir=out_dir)
    assert rc == 2
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_judgment_field_in_entry_exit_2_no_emit(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "verified": True,
         "backing": {"kind": "file", "ref": "a.txt"}},
    ])
    out_dir = tmp_path / "evidence"
    rc = _main(criteria=criteria, submission=sub, out_dir=out_dir)
    assert rc == 2
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_judgment_field_in_backing_exit_2_no_emit(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True,
         "backing": {"kind": "file", "ref": "a.txt", "pass": True}},
    ])
    out_dir = tmp_path / "evidence"
    rc = _main(criteria=criteria, submission=sub, out_dir=out_dir)
    assert rc == 2
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_duplicate_id_exit_2_no_emit(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
        {"id": "c1", "required": False, "backing": {"kind": "file", "ref": "a.txt"}},
    ])
    out_dir = tmp_path / "evidence"
    rc = _main(criteria=criteria, submission=sub, out_dir=out_dir)
    assert rc == 2
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_missing_test_junit_yields_ctx_deficit_false_and_zero(tmp_path):
    """--test-junit 미제공 + required test claim → ctx 결손으로 False → value 0.0."""
    sub = tmp_path / "sub"
    sub.mkdir()
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "test", "ref": "test_x"}},
    ])
    out_dir = tmp_path / "evidence"
    summary = _run(criteria=criteria, submission=sub, out_dir=out_dir)
    assert summary["emitted"] is True
    assert summary["value"] == 0.0
    report = json.loads(Path(summary["report_path"]).read_text(encoding="utf-8"))
    assert report["criteria"][0]["verified"] is False
    assert "not provided" in report["criteria"][0]["detail"]["reason"]
    assert report["junit_provided"] is False


# --- (4) 무판정 가드 + measured 스키마 --------------------------------------------


def test_evidence_has_no_verdict_keys_and_correct_shape(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
    ])
    out_dir = tmp_path / "evidence"
    summary = _run(criteria=criteria, submission=sub, out_dir=out_dir)
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(out_dir / f"{CHECK_ID}.json")
    assert ev.produced_by == "run"
    assert ev.self_reported is False
    assert set(ev.measured.keys()) == {"intent_fidelity"}
    dumped = json.dumps(ev.to_dict())
    assert '"verdict"' not in dumped
    assert '"pass"' not in dumped


# --- 커널 왕복 --------------------------------------------------------------------


def test_kernel_round_trip_pass_with_all_three_kinds(tmp_path):
    run_root = tmp_path / "run"
    _make_repo(
        run_root,
        base={
            "src/auth/service.py": "# placeholder\n",
            "src/auth/reset_pw.py": "# placeholder\n",
        },
        changed={
            "src/auth/service.py": "class AuthService:\n    pass\n",
            "src/auth/reset_pw.py": "def reset():\n    pass\n",
        },
    )
    junit = _junit(run_root / "junit.xml", [("test_login_ok", None, "passed")])
    criteria = _criteria(run_root / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "test", "ref": "test_login_ok"}},
        {"id": "c2", "required": True, "backing": {"kind": "symbol", "ref": "AuthService"}},
        {"id": "c3", "required": False, "backing": {"kind": "diff", "ref": "src/auth/reset*.py"}},
    ])
    evidence_dir = run_root / "evidence"
    summary = _run(
        criteria=criteria, submission=run_root, out_dir=evidence_dir,
        test_junit=junit, git_base="HEAD",
    )
    assert summary["emitted"] is True
    assert summary["value"] == 1.0

    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(run_root),
        "--test-junit", str(junit),
        "--from-evidence", str(evidence_dir),
        "--git-base", "HEAD",
        "--measured-at", FIXED_TS,
        "--out-dir", str(run_root / "sub_evidence"),
    ])
    sub_summary = measure_submission.run(sub_args)
    assert "scoring.correctness" in sub_summary["emitted"]

    ev = evidence_mod.load_evidence(run_root / "sub_evidence" / "scoring.correctness.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert v.value == pytest.approx(1.0)  # (tests_passed/tests_total) * intent_fidelity


def test_kernel_round_trip_zero_intent_fails_hard(tmp_path):
    """intent_fidelity=0.0(required 미충족) 은 discretization 이산 화이트리스트에는
    들지만 phase-09 하드 게이트(intent_fidelity >= 0.7)를 어겨 커널이 FAIL 시켜야
    한다 — 법칙4 위반이므로 value 는 계산되지 않고 None(법칙5 미도달)."""
    run_root = tmp_path / "run"
    _make_repo(run_root, base={"a.txt": "x"}, changed={})
    junit = _junit(run_root / "junit.xml", [("test_login_ok", None, "passed")])
    criteria = _criteria(run_root / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "test", "ref": "test_missing"}},
    ])
    evidence_dir = run_root / "evidence"
    summary = _run(
        criteria=criteria, submission=run_root, out_dir=evidence_dir,
        test_junit=junit, git_base="HEAD",
    )
    assert summary["emitted"] is True
    assert summary["value"] == 0.0

    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(run_root),
        "--test-junit", str(junit),
        "--from-evidence", str(evidence_dir),
        "--git-base", "HEAD",
        "--measured-at", FIXED_TS,
        "--out-dir", str(run_root / "sub_evidence"),
    ])
    sub_summary = measure_submission.run(sub_args)
    assert "scoring.correctness" in sub_summary["emitted"]

    ev = evidence_mod.load_evidence(run_root / "sub_evidence" / "scoring.correctness.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"  # hard gate: intent_fidelity >= 0.7 (법칙4)
    assert any("intent_fidelity < 0.7" in r for r in v.reasons), v.reasons
    assert v.value is None  # 법칙4 FAIL 시 법칙5(value) 미도달


def test_kernel_round_trip_optional_missing_still_passes_at_boundary(tmp_path):
    """required 전부 충족 + optional 미충족 → intent_fidelity=0.7(경계) 은
    hard gate(>= 0.7) 를 통과해야 한다 — 0.7 이 PASS/FAIL 경계임을 커널 레벨로 고정."""
    run_root = tmp_path / "run"
    _make_repo(
        run_root,
        base={"src/auth/service.py": "# placeholder\n"},
        changed={"src/auth/service.py": "class AuthService:\n    pass\n"},
    )
    junit = _junit(run_root / "junit.xml", [("test_login_ok", None, "passed")])
    criteria = _criteria(run_root / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "symbol", "ref": "AuthService"}},
        {"id": "c2", "required": False, "backing": {"kind": "test", "ref": "test_missing_optional"}},
    ])
    evidence_dir = run_root / "evidence"
    summary = _run(
        criteria=criteria, submission=run_root, out_dir=evidence_dir,
        test_junit=junit, git_base="HEAD",
    )
    assert summary["emitted"] is True
    assert summary["value"] == 0.7

    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(run_root),
        "--test-junit", str(junit),
        "--from-evidence", str(evidence_dir),
        "--git-base", "HEAD",
        "--measured-at", FIXED_TS,
        "--out-dir", str(run_root / "sub_evidence"),
    ])
    sub_summary = measure_submission.run(sub_args)
    assert "scoring.correctness" in sub_summary["emitted"]

    ev = evidence_mod.load_evidence(run_root / "sub_evidence" / "scoring.correctness.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert v.value == pytest.approx(1.0 * 0.7)  # (tests_passed/tests_total) * intent_fidelity


def test_kernel_deficit_preserved_when_producer_not_run(tmp_path):
    run_root = tmp_path / "run"
    _make_repo(run_root, base={"a.txt": "x"}, changed={})
    junit = _junit(run_root / "junit.xml", [("test_login_ok", None, "passed")])
    evidence_dir = run_root / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)  # producer never ran — dir empty

    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(run_root),
        "--test-junit", str(junit),
        "--from-evidence", str(evidence_dir),
        "--git-base", "HEAD",
        "--measured-at", FIXED_TS,
        "--out-dir", str(run_root / "sub_evidence"),
    ])
    sub_summary = measure_submission.run(sub_args)
    assert "intent_fidelity" in sub_summary["skipped"].get("scoring.correctness", [])
    assert "scoring.correctness" not in sub_summary["emitted"]


# --- 결정성 + CLI ------------------------------------------------------------------


def test_deterministic_same_path_twice_byte_identical(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
    ])
    out_dir = tmp_path / "evidence"
    _run(criteria=criteria, submission=sub, out_dir=out_dir)
    first_ev = (out_dir / f"{CHECK_ID}.json").read_bytes()
    first_report = (out_dir / f"{CHECK_ID}.report.json").read_bytes()
    _run(criteria=criteria, submission=sub, out_dir=out_dir)
    second_ev = (out_dir / f"{CHECK_ID}.json").read_bytes()
    second_report = (out_dir / f"{CHECK_ID}.report.json").read_bytes()
    assert first_ev == second_ev
    assert first_report == second_report


def test_deterministic_across_roots_measured_identical(tmp_path):
    a_root, b_root = tmp_path / "a", tmp_path / "b"
    for root in (a_root, b_root):
        sub = root / "sub"
        _write(sub / "a.txt", "x")
        criteria = _criteria(root / "criteria.json", [
            {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
        ])
        _run(criteria=criteria, submission=sub, out_dir=root / "evidence")
    a = json.loads((a_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    b = json.loads((b_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    assert a["measured"] == b["measured"]


def test_cli_subprocess_exit_zero_and_schema_loadable(tmp_path):
    sub = tmp_path / "sub"
    _write(sub / "a.txt", "x")
    criteria = _criteria(tmp_path / "criteria.json", [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "a.txt"}},
    ])
    out_dir = tmp_path / "evidence"
    script = Path(producer.__file__)
    proc = subprocess.run(
        [sys.executable, str(script),
         "--criteria", str(criteria),
         "--submission", str(sub),
         "--measured-at", FIXED_TS,
         "--out-dir", str(out_dir)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(out_dir / f"{CHECK_ID}.json")
    assert ev.check_id == CHECK_ID
