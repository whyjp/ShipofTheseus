"""measure_deep_module.py(증거 조립기) 테스트 — WP5 promote.

요구 매핑:
  (1) producer 가 code_root 를 스캔해 module_count/max_shallow_ratio(+modules_total
      브릿지)만 raw 값으로 emit — verdict/pass/failures 문자열이 measured 에 안 섞인다.
  (2) 실 CheckSpec(checks/quality.deep_module.json) 으로 커널이 재판정 — 얕은 모듈 존재
      시 FAIL, min_modules 미달 시 FAIL(둘 다 evidence 는 정상 emit — 판정만 커널 몫).
  (3) deep_module → scoring.solid backing 브릿지: modules_total 은 measure_submission
      의 --from-evidence 로 실제 승계되지만, modules_passing_solid/dip_violation 은
      결손으로 남아 scoring.solid 차원 자체는 여전히 emit 안 됨(정직한 부분 브릿지).
  (4) producer_cmd 가 CheckSpec pattern 과 정합 + 결정성.

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
import measure_deep_module as producer
import measure_submission

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "quality.deep_module"
FIXED_TS = "2026-07-04T00:00:00+00:00"

DEEP_MODULE_SRC = '''"""Deep module — small interface, lots of internal logic."""

def process(data):
    x = 0
    for d in data:
        x += d * 2
    y = x * x
    z = []
    for i in range(y):
        z.append(i % 7)
    out = sum(z)
    if out > 100:
        out = out % 100
    if out < 0:
        out = -out
    return out
'''

#  functional_lines>=5 가드(build_report)를 통과하면서 ratio>0.4 이 되도록 구성 —
#  단순 one-liner def 뭉치는 interface_lines==code_lines 라 functional_lines=0 이 되어
#  build_report 의 얕은-모듈 후보에서 아예 제외된다(별도 확인, 실측으로 조정됨).
SHALLOW_MODULE_SRC = '''class Widget:
    def render(self):
        raise ValueError("bad widget")

def use_widget(w):
    try:
        w.render()
    except ValueError:
        return None
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
    """요구(1): measured 에 module_count/max_shallow_ratio/modules_total 만, verdict 없음."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "deep.py", DEEP_MODULE_SRC)
    _write(src / "other_deep.py", DEEP_MODULE_SRC)
    summary = _run(src, run_root / "evidence")
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run"
    assert ev.self_reported is False
    assert set(ev.measured.keys()) == {"module_count", "max_shallow_ratio", "modules_total"}
    assert ev.measured["module_count"]["value"] == 2
    assert ev.measured["modules_total"]["value"] == 2  # 브릿지 — 같은 값
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    dumped = json.dumps(ev.to_dict())
    assert "verdict" not in dumped
    assert '"pass"' not in dumped
    assert '"failures"' not in dumped


def test_kernel_passes_all_deep_modules(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", DEEP_MODULE_SRC)
    _write(src / "b.py", DEEP_MODULE_SRC)
    _run(src, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons


def test_kernel_fails_on_shallow_module(tmp_path):
    """요구(2): 얕은 모듈(ratio>0.4) 존재 → 커널 FAIL. producer 는 정상 evidence 를 냄."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "deep.py", DEEP_MODULE_SRC)
    _write(src / "shallow.py", SHALLOW_MODULE_SRC)
    summary = _run(src, run_root / "evidence")
    assert summary["emitted"] is True
    assert summary["max_shallow_ratio"] > 0.4

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("0.4" in r for r in v.reasons)


def test_kernel_fails_below_min_modules(tmp_path):
    """min_modules(2) 미달 → module_count=1 → 커널 FAIL(assertion), evidence 는 정상."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "only.py", DEEP_MODULE_SRC)
    summary = _run(src, run_root / "evidence")
    assert summary["module_count"] == 1

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("module count" in r for r in v.reasons)


def test_solid_bridge_modules_total_survives_from_evidence_but_solid_stays_deficit(tmp_path):
    """요구(3): modules_total 은 measure_submission --from-evidence 로 실제 승계되지만,
    modules_passing_solid/dip_violation 결손 때문에 scoring.solid 자체는 여전히 결손
    (억지 매핑 없이, 정직한 부분 브릿지)."""
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", DEEP_MODULE_SRC)
    _write(src / "b.py", DEEP_MODULE_SRC)
    _run(src, run_root / "evidence")

    # deep_module evidence 를 measure_submission 의 from-evidence 입력으로 사용.
    upstream_dir = run_root / "evidence"
    junit = run_root / "results" / "junit.xml"
    junit.parent.mkdir(parents=True, exist_ok=True)
    junit.write_text('<testsuite tests="1" failures="0" errors="0"></testsuite>\n', encoding="utf-8")

    subprocess.run(  # git repo 필요 — measure_submission 이 git diff 를 부른다
        ["git", "-C", str(run_root), "init", "-q"], check=True,
    )
    (run_root / "a.txt").write_text("x", encoding="utf-8")

    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(run_root),
        "--test-junit", str(junit),
        "--from-evidence", str(upstream_dir),
        "--measured-at", FIXED_TS,
        "--out-dir", str(run_root / "sub_evidence"),
    ])
    summary = measure_submission.run(sub_args)

    # modules_total 은 승계됐으나 modules_passing_solid/dip_violation 결손 → solid 미emit.
    assert "modules_total" not in summary["skipped"].get("scoring.solid", [])
    assert "modules_passing_solid" in summary["skipped"].get("scoring.solid", [])
    assert "dip_violation" in summary["skipped"].get("scoring.solid", [])
    assert "scoring.solid" not in summary["emitted"]


def test_cli_subprocess_matches_checkspec_pattern(tmp_path):
    run_root = tmp_path / "run"
    src = run_root / "src"
    _write(src / "a.py", DEEP_MODULE_SRC)
    _write(src / "b.py", DEEP_MODULE_SRC)
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
        _write(root / "src" / "a.py", DEEP_MODULE_SRC)
        _write(root / "src" / "b.py", DEEP_MODULE_SRC)
        _run(root / "src", root / "evidence")
    a = json.loads((a_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    b = json.loads((b_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    assert a["measured"] == b["measured"]
