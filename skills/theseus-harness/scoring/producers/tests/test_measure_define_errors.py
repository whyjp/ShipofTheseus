"""measure_define_errors.py(증거 조립기) 테스트 — WP5 promote.

요구 매핑:
  (1) producer 가 module_count/raised_type_count/unhandled_type_count/
      bare_except_vacuous_flag 만 raw 값으로 emit — verdict/pass/raise_catalog 류
      원본 스크립트의 판정 문자열이 measured 에 안 섞인다.
  (2) 실 CheckSpec(checks/quality.define_errors.json) 으로 커널이 재판정 — handle
      누락/ vacuous bare-except 는 FAIL.
  (3) 회귀 가드: module_count==0(no-work) 이 unhandled_type_count==0 을 vacuous 하게
      만족해 buffer PASS 로 새지 않고, module_count>0 guard 로 FAIL.
  (4) producer_cmd 패턴 정합 + 결정성.

실행: python -m pytest skills/theseus-harness/scoring/producers -q
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import checkspec
import evidence as evidence_mod
import kernel
import measure_define_errors as producer

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "quality.define_errors"
FIXED_TS = "2026-07-04T00:00:00+00:00"

HANDLED_SRC = '''
def f():
    raise ValueError("bad")

def g():
    try:
        f()
    except ValueError:
        return 0
'''

UNHANDLED_SRC = '''
def h():
    raise RuntimeError("nobody catches this")
'''

BARE_EXCEPT_ONLY_SRC = '''
def k():
    raise ValueError("bad")

def caller():
    try:
        k()
    except Exception:
        pass
'''


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run(code_root: Path, out_dir: Path, **over):
    argv = ["--code-root", str(code_root), "--out-dir", str(out_dir), "--measured-at", FIXED_TS]
    for k, v in over.items():
        argv += [f"--{k.replace('_', '-')}", str(v)]
    args = producer.build_parser().parse_args(argv)
    return producer.run(args)


def test_producer_emits_raw_values_no_verdict_mixed_in(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", HANDLED_SRC)
    summary = _run(src, run_root / "evidence")
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run"
    assert ev.self_reported is False
    assert set(ev.measured.keys()) == {
        "module_count", "raised_type_count", "unhandled_type_count", "bare_except_vacuous_flag",
    }
    assert ev.measured["raised_type_count"]["value"] == 1
    assert ev.measured["unhandled_type_count"]["value"] == 0
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    dumped = json.dumps(ev.to_dict())
    assert "verdict" not in dumped
    assert '"pass"' not in dumped
    assert "raise_catalog" not in dumped  # 원본의 dict 판정 산출물이 measured 에 안 섞임


def test_kernel_passes_when_all_raises_handled(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", HANDLED_SRC)
    _run(src, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons


def test_kernel_fails_on_unhandled_raise(tmp_path):
    """요구(2): handle 0 인 예외 종류 → 커널 FAIL."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", UNHANDLED_SRC)
    summary = _run(src, run_root / "evidence")
    assert summary["unhandled_type_count"] == 1

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("unhandled_type_count" in r or "handle" in r for r in v.reasons)


def test_kernel_fails_on_vacuous_bare_except(tmp_path):
    """bare/Exception 절만으로 handle 처리 → vacuous handle 의심 → 커널 FAIL."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", BARE_EXCEPT_ONLY_SRC)
    summary = _run(src, run_root / "evidence")
    assert summary["bare_except_vacuous_flag"] is True

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"


def test_empty_code_root_fails_not_vacuous_pass(tmp_path):
    """요구(3): module_count==0 이 unhandled_type_count==0(vacuous)을 만족해 버퍼 PASS
    로 새지 않고 module_count>0 guard 로 FAIL."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    src.mkdir(parents=True)
    summary = _run(src, run_root / "evidence")
    assert summary["module_count"] == 0
    assert summary["unhandled_type_count"] == 0  # vacuous — 이래서 guard 가 필요

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("no .py modules found" in r for r in v.reasons)


def test_cli_subprocess_matches_checkspec_pattern(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", HANDLED_SRC)
    script = Path(producer.__file__)
    proc = subprocess.run(
        [sys.executable, str(script),
         "--code-root", str(src),
         "--measured-at", FIXED_TS,
         "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)


def test_deterministic_across_runs(tmp_path):
    a_root, b_root = tmp_path / "a", tmp_path / "b"
    for root in (a_root, b_root):
        _write(root / "src" / "a.py", HANDLED_SRC)
        _run(root / "src", root / "evidence")
    a = json.loads((a_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    b = json.loads((b_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    assert a["measured"] == b["measured"]
