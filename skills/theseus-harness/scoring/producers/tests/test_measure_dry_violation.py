"""measure_dry_violation.py(증거 조립기) 테스트 — WP5 promote.

요구 매핑:
  (1) producer 가 total_ngrams/violation_count/scanned_line_count/n_gram 만 raw 값으로
      emit — verdict/pass/failures 문자열이 measured 에 안 섞인다.
  (2) 실 CheckSpec(checks/quality.dry.json) 으로 커널이 재판정 — 중복 많은 코드는 FAIL.
  (3) 소규모 코드베이스(scanned_line_count < n_gram+10): evidence 는 정상 emit 되지만
      meta_audit 의 applicability 가 NA(비게이팅)로 처리 — 침묵 pass 가 아니라 증거로
      입증된 NA(원본 스크립트의 'skip=pass' 를 대체).
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
import measure_dry_violation as producer
import meta_audit

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
REAL_MANIFEST = meta_audit._DEFAULT_MANIFEST
CHECK_ID = "quality.dry"
FIXED_TS = "2026-07-04T00:00:00+00:00"


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


def _unique_lines_src(n: int) -> str:
    return "\n".join(f"v{i} = {i}" for i in range(n)) + "\n"


def _repeated_block_src(repeats: int) -> str:
    block = [f"r{i} = {i}" for i in range(8)]
    return "\n".join(block * repeats) + "\n"


def test_producer_emits_raw_values_no_verdict_mixed_in(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", _unique_lines_src(30))
    summary = _run(src, run_root / "evidence")
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run"
    assert ev.self_reported is False
    assert set(ev.measured.keys()) == {
        "module_count", "total_ngrams", "violation_count", "scanned_line_count", "n_gram",
    }
    assert ev.measured["scanned_line_count"]["value"] == 30
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    dumped = json.dumps(ev.to_dict())
    assert "verdict" not in dumped
    assert '"pass"' not in dumped


def test_kernel_passes_no_duplication(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", _unique_lines_src(30))
    _run(src, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert v.value == 0.0


def test_kernel_fails_on_heavy_duplication(tmp_path):
    """요구(2): 8줄 블록 반복(실측 violation_ratio ≈0.80) → 커널 FAIL."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", _repeated_block_src(6))
    summary = _run(src, run_root / "evidence")
    assert summary["violation_count"] / summary["total_ngrams"] > 0.05

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("0.05" in r for r in v.reasons)


def test_small_codebase_is_evidenced_na_not_silent_pass(tmp_path):
    """요구(3): scanned_line_count(10) < n_gram+10(18) → meta_audit 가 NA(비게이팅).
    evidence 자체는 정상 emit(값이 진짜 관측됨) — 침묵 skip 이 아니다."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", _unique_lines_src(10))
    summary = _run(src, run_root / "evidence")
    assert summary["emitted"] is True
    assert summary["scanned_line_count"] == 10
    assert summary["total_ngrams"] == 0

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev is not None  # evidence 는 있다 — 부재가 아니다

    report = meta_audit.run_meta_audit(
        run_root, "G2",
        manifest_path=_write_minimal_manifest(tmp_path),
        checks_dir=REAL_CHECKS_DIR,
        verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "NA"
    assert CHECK_ID in report["na"]


def test_empty_code_root_fails_not_na(tmp_path):
    """회귀 가드: applicability("module_count==0 or scanned_line_count>=n_gram+10")가
    없으면 0-모듈 코드베이스가 scanned_line_count=0 <18 로 NA(비게이팅) 처리돼 원본
    스크립트의 명시적 exit-1(FAIL)이 새 커널 하에서 무해화될 뻔했다. module_count==0
    은 applicability 를 강제로 참으로 만들어 NA 가 아니라 assertion FAIL 로 잡는다."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    src.mkdir(parents=True)  # .py 파일 0개
    summary = _run(src, run_root / "evidence")
    assert summary["module_count"] == 0

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("no .py modules found" in r for r in v.reasons)

    report = meta_audit.run_meta_audit(
        run_root, "G2",
        manifest_path=_write_minimal_manifest(tmp_path),
        checks_dir=REAL_CHECKS_DIR,
        verified_at=FIXED_TS,
    )
    assert report["results"][CHECK_ID]["result"] == "FAIL"
    assert CHECK_ID not in report["na"]


def _write_minimal_manifest(tmp_path: Path) -> Path:
    """quality.dry 만 활성인 최소 매니페스트 — 실 매니페스트에는 아직 이 check_id 가
    없으므로(오케스트레이터가 추가할 몫), meta_audit NA 동작 자체만 독립적으로 검증."""
    data = {
        "manifest_schema_version": "1.0",
        "phases": [{"id": "08", "name": "implement", "active_grades": ["G2"]}],
        "multiverse_widths": {"G2": 1},
        "frozen_widths": {},
        "checks": {"G2": [CHECK_ID]},
    }
    p = tmp_path / "min_manifest.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def test_cli_subprocess_matches_checkspec_pattern(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", _unique_lines_src(30))
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
        _write(root / "src" / "a.py", _unique_lines_src(30))
        _run(root / "src", root / "evidence")
    a = json.loads((a_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    b = json.loads((b_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    assert a["measured"] == b["measured"]
