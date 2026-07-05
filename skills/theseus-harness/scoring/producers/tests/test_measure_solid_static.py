"""measure_solid_static.py(scoring.solid 증거 조립기) 테스트 — JW4.

요구 매핑(스펙 §3.4 / 계획 JW4 테스트 매트릭스 14케이스):
  (1)  enumerate_modules 필터 정확 + build_report 동작 불변.
  (2)  통과 카운트(전 claim 충족 vs SRP 위반), dip_violation.
  (3~4) DIP 위반/충족 케이스.
  (5)  enumeration 밖 모듈은 통과 불가 + passing <= total 유지.
  (6)  contract 미제공 → modules_total 하나만.
  (7)  판정 필드/깨진 JSON/화이트리스트 밖 kind → exit 2, emit 없음.
  (8)  modules_total 브릿지 정합(deep_module 과 값 동일 + 사전순 승자).
  (9)  결손 유지 왕복(contract 없이 → scoring.solid 미emit).
  (10) 커널 왕복 PASS. (11) 커널 왕복 FAIL(DIP). (12) evidence 무판정.
  (13) 결정성 (a)(b) + CLI subprocess. (14) modules_total==0.

실행: python -m pytest skills/theseus-harness/scoring/producers/tests/test_measure_solid_static.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import checkspec
import claims
import deep_module_metric
import evidence as evidence_mod
import kernel
import measure_deep_module
import measure_solid_static as producer
import measure_submission

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "gate.solid_static"
FIXED_TS = "2026-07-05T00:00:00+00:00"


# --- fixture 모듈 소스 ---------------------------------------------------------

GOOD_SRC = '''"""Good module — abstract dependency, single public class."""
from repo import Repository


class Service:
    def run(self):
        return Repository()
'''

SRP_VIOLATION_SRC = '''"""SRP violation — two public classes."""


class Alpha:
    def a(self):
        return 1


class Beta:
    def b(self):
        return 2
'''

DIP_VIOLATION_SRC = '''"""DIP violation — concrete sqlite3 import."""
import sqlite3


def connect():
    return sqlite3.connect(":memory:")
'''


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _contract(path: Path, modules: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"modules": modules}, ensure_ascii=False), encoding="utf-8")
    return path


def _run(code_root: Path, out_dir: Path, contract: Path | None = None, **over):
    argv = ["--code-root", str(code_root), "--out-dir", str(out_dir), "--measured-at", FIXED_TS]
    if contract is not None:
        argv += ["--solid-contract", str(contract)]
    for k, v in over.items():
        argv += [f"--{k.replace('_', '-')}", str(v)]
    args = producer.build_parser().parse_args(argv)
    return producer.run(args)


def _solid_spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / "scoring.solid.json")


def _load_ev(evidence_dir: Path):
    return evidence_mod.load_evidence(evidence_dir / f"{CHECK_ID}.json")


def _measure_submission_roundtrip(run_root: Path, upstream_dir: Path):
    """upstream evidence(gate.solid_static.json 등)를 measure_submission 이 승계하도록
    git repo + junit 를 놓고 --from-evidence 로 돌린다 — deep_module 브릿지 테스트 패턴."""
    junit = run_root / "results" / "junit.xml"
    junit.parent.mkdir(parents=True, exist_ok=True)
    junit.write_text('<testsuite tests="1" failures="0" errors="0"></testsuite>\n', encoding="utf-8")
    subprocess.run(["git", "-C", str(run_root), "init", "-q"], check=True)
    (run_root / "a.txt").write_text("x", encoding="utf-8")
    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(run_root),
        "--test-junit", str(junit),
        "--from-evidence", str(upstream_dir),
        "--measured-at", FIXED_TS,
        "--out-dir", str(run_root / "sub_evidence"),
    ])
    return measure_submission.run(sub_args), run_root / "sub_evidence"


# --- #1 enumerate_modules 필터 + build_report 동작 불변 --------------------------


def test_enumerate_modules_filters_and_build_report_unchanged(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "pkg.py", "x = 1\n")
    _write(cr / "tests" / "helper.py", "y = 2\n")             # tests/ 제외
    _write(cr / "test_foo.py", "z = 3\n")                     # test_ 제외
    _write(cr / "foo_test.py", "z = 4\n")                     # _test.py 제외
    _write(cr / "conftest.py", "z = 5\n")                     # conftest 제외
    _write(cr / "sub" / "__init__.py", "")                    # 빈 __init__ 제외(<=100B)
    _write(cr / "big" / "__init__.py", "# " + "a" * 120 + "\n")  # 큰 __init__ 계수

    mods = deep_module_metric.enumerate_modules(cr)
    rels = sorted(Path(m).relative_to(cr).as_posix() for m in mods)
    assert rels == ["big/__init__.py", "pkg.py"]

    # 동작 불변 — build_report 가 같은 enumeration 을 쓴다.
    report = deep_module_metric.build_report(cr, min_modules=1)
    assert report["module_count"] == len(mods) == 2


# --- #2 통과 카운트 + dip_violation(SRP 실패는 DIP 아님) --------------------------


def test_passing_count_srp_violation(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "good.py", GOOD_SRC)
    _write(cr / "bad_srp.py", SRP_VIOLATION_SRC)
    contract = _contract(tmp_path / "c.json", [
        {"module": "good.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
            {"principle": "SRP", "backing": {"kind": "symbol_count_max",
                                             "ref": {"symbol": "public_class", "max": 1}}},
        ]},
        {"module": "bad_srp.py", "claims": [
            {"principle": "SRP", "backing": {"kind": "symbol_count_max",
                                             "ref": {"symbol": "public_class", "max": 1}}},
        ]},
    ])
    summary = _run(cr, tmp_path / "run" / "evidence", contract)
    assert summary["modules_passing_solid"] == 1
    assert summary["modules_total"] == 2
    assert summary["dip_violation"] == 0  # SRP 위반은 DIP 아님


# --- #3 DIP 위반 감지 ----------------------------------------------------------


def test_dip_violation_concrete_import(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "bad_dip.py", DIP_VIOLATION_SRC)
    _write(cr / "filler.py", "v = 1\n")
    contract = _contract(tmp_path / "c.json", [
        {"module": "bad_dip.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
        ]},
    ])
    summary = _run(cr, tmp_path / "run" / "evidence", contract)
    assert summary["dip_violation"] == 1


# --- #4 DIP 충족 → 그 모듈 passed, dip_violation 0 ------------------------------


def test_dip_satisfied_module_passes(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "good.py", GOOD_SRC)
    contract = _contract(tmp_path / "c.json", [
        {"module": "good.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
        ]},
    ])
    out = tmp_path / "run" / "evidence"
    summary = _run(cr, out, contract)
    assert summary["dip_violation"] == 0
    assert summary["modules_passing_solid"] == 1
    report = json.loads((out / f"{CHECK_ID}.report.json").read_text(encoding="utf-8"))
    good = next(m for m in report["modules"] if m["module"] == "good.py")
    assert good["passed"] is True


# --- #5 enumeration 밖 모듈 → 통과 불가, passing <= total -------------------------


def test_module_outside_enumeration_not_counted(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "good.py", GOOD_SRC)
    contract = _contract(tmp_path / "c.json", [
        {"module": "good.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
        ]},
        {"module": "ghost.py", "claims": [   # 비존재 → enumeration 밖
            {"principle": "SRP", "backing": {"kind": "symbol_count_max",
                                             "ref": {"symbol": "public_class", "max": 5}}},
        ]},
    ])
    out = tmp_path / "run" / "evidence"
    summary = _run(cr, out, contract)
    assert summary["modules_passing_solid"] == 1
    assert summary["modules_total"] == 1
    assert summary["modules_passing_solid"] <= summary["modules_total"]
    report = json.loads((out / f"{CHECK_ID}.report.json").read_text(encoding="utf-8"))
    ghost = next(m for m in report["modules"] if m["module"] == "ghost.py")
    assert ghost["in_enumeration"] is False
    assert ghost["passed"] is False
    assert ghost["reason"] == "module not in enumeration"


# --- #6 contract 미제공 → modules_total 하나만 ----------------------------------


def test_no_contract_emits_only_modules_total(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "a.py", GOOD_SRC)
    _write(cr / "b.py", GOOD_SRC)
    out = tmp_path / "run" / "evidence"
    summary = _run(cr, out, contract=None)
    assert summary["emitted_keys"] == ["modules_total"]
    ev = _load_ev(out)
    assert set(ev.measured.keys()) == {"modules_total"}
    assert ev.measured["modules_total"]["value"] == 2


def test_missing_contract_file_treated_as_deficit(tmp_path):
    """--solid-contract 이 주어졌으나 파일 부재 → 결손 경로(exit 0), modules_total 만."""
    cr = tmp_path / "code"
    _write(cr / "a.py", GOOD_SRC)
    _write(cr / "b.py", GOOD_SRC)
    out = tmp_path / "run" / "evidence"
    rc = producer.main([
        "--code-root", str(cr), "--out-dir", str(out),
        "--solid-contract", str(tmp_path / "nope.json"), "--measured-at", FIXED_TS,
    ])
    assert rc == 0
    ev = _load_ev(out)
    assert set(ev.measured.keys()) == {"modules_total"}


# --- #7 저작 오류 → exit 2, emit 없음 ------------------------------------------


def test_judgment_field_exits_2(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "a.py", GOOD_SRC)
    out = tmp_path / "run" / "evidence"
    contract = _contract(tmp_path / "c.json", [
        {"module": "a.py", "verified": True, "claims": [
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
        ]},
    ])
    rc = producer.main(["--code-root", str(cr), "--out-dir", str(out),
                        "--solid-contract", str(contract), "--measured-at", FIXED_TS])
    assert rc == 2
    assert not (out / f"{CHECK_ID}.json").exists()


def test_broken_json_exits_2(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "a.py", GOOD_SRC)
    out = tmp_path / "run" / "evidence"
    bad = tmp_path / "c.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    rc = producer.main(["--code-root", str(cr), "--out-dir", str(out),
                        "--solid-contract", str(bad), "--measured-at", FIXED_TS])
    assert rc == 2
    assert not (out / f"{CHECK_ID}.json").exists()


def test_unknown_backing_kind_exits_2(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "a.py", GOOD_SRC)
    out = tmp_path / "run" / "evidence"
    contract = _contract(tmp_path / "c.json", [
        {"module": "a.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "grep", "ref": "sqlite3"}},
        ]},
    ])
    rc = producer.main(["--code-root", str(cr), "--out-dir", str(out),
                        "--solid-contract", str(contract), "--measured-at", FIXED_TS])
    assert rc == 2
    assert not (out / f"{CHECK_ID}.json").exists()


# --- #8 modules_total 브릿지 정합 -----------------------------------------------


def test_modules_total_bridge_parity_with_deep_module(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "a.py", GOOD_SRC)
    _write(cr / "b.py", DIP_VIOLATION_SRC)
    run_root = tmp_path / "run"
    evidence_dir = run_root / "evidence"

    contract = _contract(tmp_path / "c.json", [
        {"module": "a.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
        ]},
    ])
    _run(cr, evidence_dir, contract)

    # 같은 code_root 로 deep_module 도 같은 evidence 디렉터리에 emit.
    dm_args = measure_deep_module.build_parser().parse_args([
        "--code-root", str(cr), "--out-dir", str(evidence_dir), "--measured-at", FIXED_TS,
    ])
    measure_deep_module.run(dm_args)

    solid_ev = _load_ev(evidence_dir)
    dm_ev = evidence_mod.load_evidence(evidence_dir / "quality.deep_module.json")
    assert solid_ev.measured["modules_total"]["value"] == dm_ev.measured["modules_total"]["value"] == 2

    # measure_submission 승계 — 사전순 승자 = gate.solid_static.json.
    summary, sub_dir = _measure_submission_roundtrip(run_root, evidence_dir)
    assert "scoring.solid" in summary["emitted"]
    sub_solid = evidence_mod.load_evidence(sub_dir / "scoring.solid.json")
    assert sub_solid.measured["modules_total"]["source"] == "from_evidence:gate.solid_static.json"


# --- #9 결손 유지 왕복 ---------------------------------------------------------


def test_deficit_roundtrip_keeps_solid_unmeasured(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "a.py", GOOD_SRC)
    _write(cr / "b.py", GOOD_SRC)
    run_root = tmp_path / "run"
    evidence_dir = run_root / "evidence"
    _run(cr, evidence_dir, contract=None)  # modules_total 만

    summary, _ = _measure_submission_roundtrip(run_root, evidence_dir)
    assert "modules_total" not in summary["skipped"].get("scoring.solid", [])
    assert "modules_passing_solid" in summary["skipped"].get("scoring.solid", [])
    assert "dip_violation" in summary["skipped"].get("scoring.solid", [])
    assert "scoring.solid" not in summary["emitted"]


# --- #10 커널 왕복 PASS --------------------------------------------------------


def test_kernel_roundtrip_pass(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "svc_a.py", GOOD_SRC)
    _write(cr / "svc_b.py", GOOD_SRC)
    run_root = tmp_path / "run"
    evidence_dir = run_root / "evidence"
    contract = _contract(tmp_path / "c.json", [
        {"module": "svc_a.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
            {"principle": "SRP", "backing": {"kind": "symbol_count_max",
                                             "ref": {"symbol": "public_class", "max": 1}}},
        ]},
        {"module": "svc_b.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
        ]},
    ])
    _run(cr, evidence_dir, contract)

    _, sub_dir = _measure_submission_roundtrip(run_root, evidence_dir)
    ev = evidence_mod.load_evidence(sub_dir / "scoring.solid.json")
    v = kernel.verify(_solid_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert v.value == 1.0  # passing 2 / total 2


# --- #11 커널 왕복 FAIL(DIP) ----------------------------------------------------


def test_kernel_roundtrip_fail_dip(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "svc_a.py", GOOD_SRC)
    _write(cr / "leaky.py", DIP_VIOLATION_SRC)
    run_root = tmp_path / "run"
    evidence_dir = run_root / "evidence"
    contract = _contract(tmp_path / "c.json", [
        {"module": "svc_a.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
        ]},
        {"module": "leaky.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
        ]},
    ])
    summary = _run(cr, evidence_dir, contract)
    assert summary["dip_violation"] == 1

    _, sub_dir = _measure_submission_roundtrip(run_root, evidence_dir)
    ev = evidence_mod.load_evidence(sub_dir / "scoring.solid.json")
    v = kernel.verify(_solid_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("DIP violation present" in r for r in v.reasons)


# --- #12 evidence 무판정 -------------------------------------------------------


def test_evidence_raw_values_only(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "good.py", GOOD_SRC)
    _write(cr / "bad_srp.py", SRP_VIOLATION_SRC)
    out = tmp_path / "run" / "evidence"
    contract = _contract(tmp_path / "c.json", [
        {"module": "good.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
        ]},
        {"module": "bad_srp.py", "claims": [
            {"principle": "SRP", "backing": {"kind": "symbol_count_max",
                                             "ref": {"symbol": "public_class", "max": 1}}},
        ]},
    ])
    _run(cr, out, contract)
    ev = _load_ev(out)
    assert ev.produced_by == "run"
    assert ev.self_reported is False
    assert set(ev.measured.keys()) == {"modules_passing_solid", "modules_total", "dip_violation"}
    dumped = json.dumps(ev.to_dict())
    assert "verdict" not in dumped
    assert '"pass"' not in dumped
    assert '"passed"' not in dumped  # 리포트 전용 필드는 evidence 레코드에 없다


# --- #13 결정성 + CLI subprocess -----------------------------------------------


def test_deterministic_same_path_byte_identical(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "good.py", GOOD_SRC)
    _write(cr / "b.py", GOOD_SRC)
    out = tmp_path / "run" / "evidence"
    contract = _contract(tmp_path / "c.json", [
        {"module": "good.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
        ]},
    ])
    _run(cr, out, contract)
    ev_bytes_1 = (out / f"{CHECK_ID}.json").read_bytes()
    rep_bytes_1 = (out / f"{CHECK_ID}.report.json").read_bytes()
    _run(cr, out, contract)  # 덮어씀
    assert (out / f"{CHECK_ID}.json").read_bytes() == ev_bytes_1
    assert (out / f"{CHECK_ID}.report.json").read_bytes() == rep_bytes_1


def test_deterministic_across_roots(tmp_path):
    contract_modules = [
        {"module": "good.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
        ]},
    ]
    measured = []
    for name in ("a", "b"):
        root = tmp_path / name
        cr = root / "code"
        _write(cr / "good.py", GOOD_SRC)
        _write(cr / "x.py", GOOD_SRC)
        contract = _contract(root / "c.json", contract_modules)
        _run(cr, root / "evidence", contract)
        measured.append(_load_ev(root / "evidence").measured)
    assert measured[0] == measured[1]


def test_cli_subprocess_exit_zero(tmp_path):
    cr = tmp_path / "code"
    _write(cr / "good.py", GOOD_SRC)
    _write(cr / "b.py", GOOD_SRC)
    contract = _contract(tmp_path / "c.json", [
        {"module": "good.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "import_of", "ref": "Repository"}},
        ]},
    ])
    out = tmp_path / "run" / "evidence"
    proc = subprocess.run(
        [sys.executable, str(Path(producer.__file__)),
         "--code-root", str(cr),
         "--solid-contract", str(contract),
         "--measured-at", FIXED_TS,
         "--out-dir", str(out)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = _load_ev(out)  # 스키마 로드 가능
    assert ev.measured["modules_total"]["value"] == 2


# --- #14 modules_total == 0 ----------------------------------------------------


def test_empty_code_root_fails_kernel_no_modules(tmp_path):
    cr = tmp_path / "code"
    cr.mkdir(parents=True)
    run_root = tmp_path / "run"
    evidence_dir = run_root / "evidence"
    contract = _contract(tmp_path / "c.json", [])  # 빈 contract → 3키 emit
    summary = _run(cr, evidence_dir, contract)
    assert summary["modules_total"] == 0
    assert summary["emitted_keys"] == ["modules_passing_solid", "modules_total", "dip_violation"]

    _, sub_dir = _measure_submission_roundtrip(run_root, evidence_dir)
    ev = evidence_mod.load_evidence(sub_dir / "scoring.solid.json")
    v = kernel.verify(_solid_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("no modules measured" in r for r in v.reasons)
