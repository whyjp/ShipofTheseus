"""measure_dacapo_threshold.py(증거 조립기) 테스트 — WP5 promote.

요구 매핑(팀 지시 산출물 4 — fixture 자족):
  (1) producer 가 tournament-md 를 파싱해 raw winner_score/winner_max 를 provenance
      붙여 emit — verdict/ratio 문자열은 measured 에 안 섞인다.
  (2) 실 CheckSpec(checks/plan.dacapo_threshold.json) 으로 커널이 재판정 — 임계 미달은
      커널 FAIL(assertion), producer 는 여전히 정상 evidence 를 냈음(측정=측정,
      판정=판정 분리).
  (3) 추출 실패 시 evidence 자체를 안 씀 → 커널 법칙1(evidence_missing) FAIL.
  (4) producer_cmd 가 CheckSpec.producer.cmd_pattern 과 정합(subprocess 실행 경로).
  (5) 결정성 — 같은 입력 + measured_at 고정 → 같은 measured/digest.

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
import measure_dacapo_threshold as producer

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "plan.dacapo_threshold"
FIXED_TS = "2026-07-04T00:00:00+00:00"

TOURNAMENT_57_60 = """---
skill_name: theseus-orchestrator
phase: "08-impl-tournament-01"
---

# Implementation tournament — round 1

| Dim | U1 | U2 | U3 |
| --- | --- | --- | --- |
| **Total** | 50/60 | 41/60 | **57/60** |

## Winner

- Combined wins.
"""

TOURNAMENT_PERFECT = """---
skill_name: theseus-orchestrator
phase: "06-plan-tournament-02"
winner_score: 60
winner_max: 60
---

# Plan tournament — round 2

Perfect score reached.
"""

TOURNAMENT_UNPARSEABLE = """---
skill_name: theseus-orchestrator
---

# No score information anywhere in this document.
"""


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{CHECK_ID}.json")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run(tournament_md: Path, out_dir: Path, **over):
    argv = ["--tournament-md", str(tournament_md), "--out-dir", str(out_dir), "--measured-at", FIXED_TS]
    for k, v in over.items():
        argv += [f"--{k.replace('_', '-')}", str(v)]
    args = producer.build_parser().parse_args(argv)
    return producer.run(args)


def test_producer_emits_raw_values_no_verdict_mixed_in(tmp_path):
    """요구(1): measured 에 winner_score/winner_max 만 있고 verdict/ratio/pass 류가 없다."""
    run_root = tmp_path / "run"
    tmd = _write(run_root / "plan" / "tournament-01.md", TOURNAMENT_57_60)
    summary = _run(tmd, run_root / "evidence")
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert ev.produced_by == "run"
    assert ev.self_reported is False
    assert set(ev.measured.keys()) == {"winner_score", "winner_max"}
    assert ev.measured["winner_score"]["value"] == 57
    assert ev.measured["winner_max"]["value"] == 60
    for entry in ev.measured.values():
        assert entry["source"] and entry["artifact_path"]
    # verdict 문자열이 measured 어디에도 없다 — kernel 만이 판정을 낸다.
    dumped = json.dumps(ev.to_dict())
    assert "verdict" not in dumped
    assert '"pass"' not in dumped


def test_kernel_passes_below_old_threshold_and_reports_ratio(tmp_path):
    """요구(2)[B2 §2.3 재설정]: 57/60 = 0.95 는 도달 불가 0.999 게이트가 제거돼 유효성
    assertion(winner_max>0, winner_score<=winner_max)만 통과 → 커널 PASS + ratio 를
    value 로 보고. 측정=측정(점수 절대값은 게이트 아님, 비게이팅). producer 는 정상 실행."""
    run_root = tmp_path / "run"
    tmd = _write(run_root / "impl" / "tournament-impl-01.md", TOURNAMENT_57_60)
    summary = _run(tmd, run_root / "evidence")
    assert summary["winner_score"] == 57 and summary["winner_max"] == 60

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert abs(v.value - 0.95) < 1e-9
    # 도달 불가 임계 게이트가 삭제됐으므로 어떤 사유에도 0.999 가 남지 않는다.
    assert not any("0.999" in r for r in v.reasons)


def test_kernel_passes_at_perfect_score(tmp_path):
    """60/60 → 커널 PASS, value == 1.0 (측정값의 결정 함수, ratio=winner_score/winner_max)."""
    run_root = tmp_path / "run"
    tmd = _write(run_root / "plan" / "tournament-02.md", TOURNAMENT_PERFECT)
    _run(tmd, run_root / "evidence")

    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert abs(v.value - 1.0) < 1e-9


def test_extraction_failure_emits_no_evidence_kernel_fails_missing(tmp_path):
    """요구(3): 추출 실패(패턴 미매칭) → evidence 파일 자체가 안 쓰인다 → 커널 법칙1 FAIL."""
    run_root = tmp_path / "run"
    tmd = _write(run_root / "plan" / "tournament-03.md", TOURNAMENT_UNPARSEABLE)
    summary = _run(tmd, run_root / "evidence")
    assert summary["emitted"] is False
    assert not (run_root / "evidence" / f"{CHECK_ID}.json").exists()

    ev = evidence_mod.try_load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    v = kernel.verify(_spec(), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("evidence_missing" in r for r in v.reasons)


def test_cli_subprocess_matches_checkspec_pattern(tmp_path):
    """요구(4): 실제 subprocess 로 돌린 producer_cmd 가 CheckSpec.producer.cmd_pattern 과 정합."""
    run_root = tmp_path / "run"
    tmd = _write(run_root / "plan" / "tournament-01.md", TOURNAMENT_PERFECT)
    script = Path(producer.__file__)
    proc = subprocess.run(
        [sys.executable, str(script),
         "--tournament-md", str(tmd),
         "--measured-at", FIXED_TS,
         "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    assert re.search(_spec().producer.cmd_pattern, ev.producer_cmd)


def test_deterministic_across_runs(tmp_path):
    """요구(5): measured_at 고정 시 같은 입력 → 같은 measured/digest(바이트 동일)."""
    a_root = tmp_path / "a"
    b_root = tmp_path / "b"
    _write(a_root / "plan" / "t.md", TOURNAMENT_PERFECT)
    _write(b_root / "plan" / "t.md", TOURNAMENT_PERFECT)
    _run(a_root / "plan" / "t.md", a_root / "evidence")
    _run(b_root / "plan" / "t.md", b_root / "evidence")
    a = json.loads((a_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    b = json.loads((b_root / "evidence" / f"{CHECK_ID}.json").read_text(encoding="utf-8"))
    assert a["measured"] == b["measured"]
    assert a["measured_at"] == b["measured_at"] == FIXED_TS


def test_artifact_digest_matches_disk_tournament_file(tmp_path):
    """artifact_path 가 실제 tournament_md 를 가리키고 그 sha256 이 대조 가능."""
    run_root = tmp_path / "run"
    tmd = _write(run_root / "plan" / "tournament-01.md", TOURNAMENT_PERFECT)
    _run(tmd, run_root / "evidence")
    ev = evidence_mod.load_evidence(run_root / "evidence" / f"{CHECK_ID}.json")
    rel = ev.measured["winner_score"]["artifact_path"]
    assert evidence_mod.sha256_of_file(run_root / rel) == list(ev.artifact_digests.values())[0]
