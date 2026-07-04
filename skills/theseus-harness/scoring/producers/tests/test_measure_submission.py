"""measure_submission.py (증거 조립기) 통합 테스트 — 측정 = 실행 산물, 손 넣기 봉쇄.

실 저장소 checks/ 레지스트리 + pipeline.manifest.json 으로 end-to-end 를 돈다:
producer 가 fixture junit/coverage 에서 원시 값을 파싱해 Evidence Record 를 emit →
kernel.verify / meta_audit 가 판정. 요구↔테스트 매핑은 각 테스트 docstring 에 명시.

실행: python -m pytest skills/theseus-harness/scoring/producers -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import checkspec
import evidence as evidence_mod
import kernel
import measure_submission
import meta_audit

REAL_CHECKS_DIR = meta_audit._DEFAULT_CHECKS_DIR
REAL_MANIFEST = meta_audit._DEFAULT_MANIFEST
FIXED_TS = "2026-07-04T00:00:00+00:00"


# --- fixture 빌더 --------------------------------------------------------------


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _junit(path: Path, total: int, failures: int = 0, errors: int = 0, skipped: int = 0) -> Path:
    return _write(
        path,
        f'<testsuite name="s" tests="{total}" failures="{failures}" '
        f'errors="{errors}" skipped="{skipped}"></testsuite>\n',
    )


def _coverage(path: Path, rate: float) -> Path:
    return _write(path, f'<coverage line-rate="{rate}" branch-rate="{rate}"></coverage>\n')


def _from_evidence(dir_path: Path, values: dict) -> Path:
    """상류 분석 Evidence Record — measured 형태로 파생 값을 제공."""
    measured = {
        k: {"value": v, "source": "upstream_analysis", "artifact_path": f"analysis/{k}"}
        for k, v in values.items()
    }
    record = {"measured": measured}
    return _write(dir_path / "analysis.json", json.dumps(record, ensure_ascii=False))


def _git_repo(repo: Path, files: dict[str, str], modify: list[str]) -> None:
    """git repo 초기화 → files 커밋 → modify 파일들을 변경. `git diff --name-only HEAD`
    가 modify 목록을 그대로 돌려주도록(files_touched 측정 대상)."""
    repo.mkdir(parents=True, exist_ok=True)
    run = lambda *a: subprocess.run(
        ["git", "-C", str(repo), *a], capture_output=True, text=True, encoding="utf-8", check=True
    )
    run("init", "-q")
    run("config", "user.email", "t@t.t")
    run("config", "user.name", "t")
    for name, content in files.items():
        _write(repo / name, content)
    run("add", "-A")
    run("commit", "-q", "-m", "base")
    for name in modify:
        _write(repo / name, files[name] + "\n// changed")


def _load_evidence(out_dir: Path, check_id: str):
    return evidence_mod.try_load_evidence(out_dir / f"{check_id}.json")


def _spec(check_id: str):
    return checkspec.load_checkspec(REAL_CHECKS_DIR / f"{check_id}.json")


def _run_producer(**over) -> tuple[dict, Path]:
    """producer 를 실 인자로 돌리고 (summary, out_dir) 반환."""
    argv: list[str] = []
    for k, v in over.items():
        if v is None:
            continue
        argv += [f"--{k.replace('_', '-')}", str(v)]
    args = measure_submission.build_parser().parse_args(argv)
    summary = measure_submission.run(args)
    return summary, Path(summary["out_dir"])


def _full_run(tmp_path: Path, *, total=5, dual_side=True, derived=None) -> tuple[dict, Path, Path]:
    """전 차원 측정에 필요한 fixture 를 깔고 producer 실행. (summary, out_dir, run_root)."""
    run_root = tmp_path / "run"
    res = run_root / "results"
    _junit(res / "junit.xml", total)
    _coverage(res / "coverage.xml", 0.9)
    _junit(res / "e2e.xml", 3)
    if dual_side:
        _coverage(res / "fe-coverage.xml", 0.9)
    derived = derived if derived is not None else {
        "intent_fidelity": 1.0,
        "files_mapped_to_todos": 2,
        "modules_passing_solid": 4,
        "modules_total": 4,
        "dip_violation": 0,
        "parity_category": "full",
    }
    _from_evidence(run_root / "from_evidence", derived)
    _git_repo(run_root / "repo", {"a.py": "x", "b.py": "y"}, ["a.py", "b.py"])
    summary, out_dir = _run_producer(
        submission=run_root / "repo",
        test_junit=res / "junit.xml",
        coverage=res / "coverage.xml",
        fe_coverage=(res / "fe-coverage.xml") if dual_side else None,
        e2e_junit=res / "e2e.xml",
        from_evidence=run_root / "from_evidence",
        measured_at=FIXED_TS,
        out_dir=run_root / "evidence",
    )
    return summary, out_dir, run_root


# --- (1) producer 가 fixture 에서 원시 값을 파싱해 올바른 Evidence Record emit -----


def test_producer_parses_and_emits_kernel_valid_records(tmp_path):
    """요구: '측정 = 실행 산물'. junit/coverage 를 파싱해 provenance 붙은 Evidence
    Record 를 emit 하고, 실 CheckSpec 으로 커널이 통과시킨다(dual-side 전부 PASS)."""
    _, out_dir, run_root = _full_run(tmp_path, total=5, dual_side=True)

    ev = _load_evidence(out_dir, "scoring.correctness")
    assert ev is not None
    assert ev.produced_by == "run"
    assert ev.producer_exit_code == 0
    assert ev.self_reported is False
    # junit 에서 실제로 파싱된 원시 값.
    assert ev.measured["tests_total"]["value"] == 5
    assert ev.measured["tests_passed"]["value"] == 5
    assert ev.measured["tests_failed"]["value"] == 0
    # provenance 3필드 완전.
    for entry in ev.measured.values():
        assert entry["value"] is not None or entry["value"] == 0
        assert entry["source"] and entry["artifact_path"]

    # 커널이 실 spec 으로 재판정 — artifact digest 를 run_root 기준으로 대조.
    for cid in ("scoring.correctness", "scoring.scope_fit", "scoring.solid", "scoring.e2e",
                "scoring.coverage", "scoring.fe_be_parity"):
        v = kernel.verify(_spec(cid), _load_evidence(out_dir, cid),
                          artifact_root=run_root, verified_at=FIXED_TS)
        assert v.result == "PASS", (cid, v.reasons)


def test_coverage_value_is_min_of_be_and_fe(tmp_path):
    """요구: coverage = min(be, fe). producer 가 dual-side 를 emit 하면 커널 value 가
    두 값의 min 이다(rubric.md)."""
    run_root = tmp_path / "run"
    res = run_root / "results"
    _junit(res / "junit.xml", 5)
    _coverage(res / "coverage.xml", 0.9)
    _coverage(res / "fe-coverage.xml", 0.4)
    _from_evidence(run_root / "from_evidence", {"parity_category": "full"})
    _git_repo(run_root / "repo", {"a.py": "x"}, ["a.py"])
    _, out_dir = _run_producer(
        submission=run_root / "repo", test_junit=res / "junit.xml",
        coverage=res / "coverage.xml", fe_coverage=res / "fe-coverage.xml",
        from_evidence=run_root / "from_evidence", measured_at=FIXED_TS,
        out_dir=run_root / "evidence",
    )
    v = kernel.verify(_spec("scoring.coverage"), _load_evidence(out_dir, "scoring.coverage"),
                      artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "PASS"
    assert abs(v.value - 0.4) < 1e-9  # min(0.9, 0.4)


# --- (2) 측정 회귀: 테스트 0개 → 침묵 만점 아님, 커널 FAIL ----------------------


def test_zero_tests_junit_makes_correctness_fail_not_silent_max(tmp_path):
    """요구(측정 회귀): 0-test junit → tests_total=0 → scoring.correctness 가 커널 FAIL.
    설계 P1 `_safe_div(default=1.0)` 무노동 만점 회귀 봉쇄."""
    run_root = tmp_path / "run"
    res = run_root / "results"
    _junit(res / "junit.xml", 0)  # 테스트 0개
    _from_evidence(run_root / "from_evidence", {"intent_fidelity": 1.0})
    _git_repo(run_root / "repo", {"a.py": "x"}, ["a.py"])
    _, out_dir = _run_producer(
        submission=run_root / "repo", test_junit=res / "junit.xml",
        from_evidence=run_root / "from_evidence", measured_at=FIXED_TS,
        out_dir=run_root / "evidence",
    )
    ev = _load_evidence(out_dir, "scoring.correctness")
    assert ev is not None  # evidence 는 emit 됨(intent_fidelity backing 있음)
    assert ev.measured["tests_total"]["value"] == 0
    v = kernel.verify(_spec("scoring.correctness"), ev, artifact_root=run_root, verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("no tests executed" in r for r in v.reasons)


# --- (3) 손 넣기 봉쇄: backing 없는 파생 값은 emit 안 됨 → 차원 결손 → FAIL -------


def test_derived_values_without_backing_evidence_are_deficit(tmp_path):
    """요구(손 넣기 봉쇄): --from-evidence 없이 돌리면 분석 파생 값(intent_fidelity/
    files_mapped_to_todos/modules_*)이 backing artifact 부재로 emit 되지 않는다.
    그 차원 evidence 자체가 안 쓰여 커널 법칙1(evidence_missing)로 FAIL.
    직접 측정 차원(e2e)만 살아남는다 — 값의 출처가 구조적으로 강제됨을 증명."""
    run_root = tmp_path / "run"
    res = run_root / "results"
    _junit(res / "junit.xml", 5)
    _coverage(res / "coverage.xml", 0.9)
    _junit(res / "e2e.xml", 3)
    _git_repo(run_root / "repo", {"a.py": "x"}, ["a.py"])
    summary, out_dir = _run_producer(
        submission=run_root / "repo", test_junit=res / "junit.xml",
        coverage=res / "coverage.xml", e2e_junit=res / "e2e.xml",
        # --from-evidence 의도적 생략
        measured_at=FIXED_TS, out_dir=run_root / "evidence",
    )
    # 파생 값 필요한 차원은 evidence 파일이 아예 없다.
    assert not (out_dir / "scoring.correctness.json").exists()
    assert not (out_dir / "scoring.scope_fit.json").exists()
    assert not (out_dir / "scoring.solid.json").exists()
    assert "scoring.correctness" in summary["skipped"]
    assert "intent_fidelity" in summary["skipped"]["scoring.correctness"]
    assert "files_mapped_to_todos" in summary["skipped"]["scoring.scope_fit"]
    # 직접 측정 차원은 emit 됨.
    assert (out_dir / "scoring.e2e.json").exists()
    assert "scoring.e2e" in summary["emitted"]

    # meta_audit(정책): 파생 차원은 evidence_missing 으로 FAIL.
    report = meta_audit.run_meta_audit(
        run_root, "G2", manifest_path=REAL_MANIFEST, checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS
    )
    for cid in ("scoring.correctness", "scoring.scope_fit", "scoring.solid"):
        assert report["results"][cid]["result"] == "FAIL"
        assert any("evidence_missing" in r for r in report["results"][cid]["reasons"])


def test_no_cli_path_injects_raw_numbers():
    """요구(손 넣기 봉쇄, 구조적): CLI 에 어떤 measured 값도 raw 숫자로 주입하는 인자가
    없다. 파생 값은 오직 --from-evidence 승계, 나머지는 artifact 경로 파싱뿐."""
    parser = measure_submission.build_parser()
    dests = {a.dest for a in parser._actions}
    forbidden = {
        "intent_fidelity", "files_mapped_to_todos", "modules_passing_solid",
        "modules_total", "dip_violation", "parity_category",
        "tests_total", "be_coverage", "files_touched",
    }
    assert forbidden.isdisjoint(dests)
    assert "from_evidence" in dests  # 파생 값의 유일 입구


# --- (4) N/A: 단일 사이드 → coverage/fe_be_parity NA(비게이팅), 나머지 통과 → pass --


def test_single_side_marks_coverage_and_parity_na_overall_pass(tmp_path):
    """요구(N/A): fe_side_exists=false → scoring.coverage/fe_be_parity 가 meta_audit 에서
    NA(비게이팅). 나머지 4 차원이 통과하면 overall verdict=pass. NA 는 producer 가 emit
    한 fe_side_exists=0 으로 *입증* 됨(침묵 skip 아님)."""
    _, out_dir, run_root = _full_run(tmp_path, total=5, dual_side=False)

    # 단일 사이드: fe_coverage 없음, fe_side_exists=0 이 evidence 에 들어간다.
    cov_ev = _load_evidence(out_dir, "scoring.coverage")
    assert cov_ev.measured["fe_side_exists"]["value"] == 0
    assert "fe_coverage" not in cov_ev.measured

    # 이 테스트의 의도는 'NA 가 게이팅을 막지 않는다'는 N/A 메커니즘 자체다. 실 매니페스트에는
    # WP5 promote 체크(quality.*)가 G2 에 함께 활성이라, scoring evidence 만 준 run 은 그것들의
    # evidence_missing 으로 overall FAIL 하는 게 올바른 동작이다(불완전 run). N/A 불변식만
    # 격리 검증하려고 scoring 6 차원으로 스코프한 fixture 매니페스트를 쓴다(checks_dir 는 실 파일).
    scoped_manifest = tmp_path / "scoped.manifest.json"
    scoped_manifest.write_text(
        json.dumps({
            "manifest_schema_version": "1.0",
            "phases": [],
            "multiverse_widths": {"G2": 1},
            "frozen_widths": {},
            "checks": {"G2": [
                "scoring.correctness", "scoring.scope_fit", "scoring.solid",
                "scoring.coverage", "scoring.fe_be_parity", "scoring.e2e",
            ]},
        }),
        encoding="utf-8",
    )
    report = meta_audit.run_meta_audit(
        run_root, "G2", manifest_path=scoped_manifest, checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS
    )
    assert set(report["na"]) == {"scoring.coverage", "scoring.fe_be_parity"}
    assert report["failed"] == []
    assert report["verdict"] == "pass"
    for cid in ("scoring.correctness", "scoring.scope_fit", "scoring.solid", "scoring.e2e"):
        assert report["results"][cid]["result"] == "PASS"

    # 집계: NA 차원 제외 후 가중 재정규화 → 만점 통과 가능.
    import score
    agg = score.aggregate_from_meta_audit(report, dip_violation=False)
    assert agg["na_dimensions"] == ["coverage", "fe_be_parity"]
    assert abs(agg["score"] - 1.0) < 1e-9


def test_na_requires_genuine_evidence_absence_still_fails(tmp_path):
    """요구(NA도 증거로 입증): coverage evidence 가 아예 없으면(단일 사이드라도) NA 가
    아니라 FAIL(evidence_missing). 적용성은 부재를 구할 수 없다."""
    run_root = tmp_path / "run"
    (run_root / "evidence").mkdir(parents=True)
    # coverage evidence 를 안 쓴 상태로 감사.
    report = meta_audit.run_meta_audit(
        run_root, "G2", manifest_path=REAL_MANIFEST, checks_dir=REAL_CHECKS_DIR, verified_at=FIXED_TS
    )
    assert "scoring.coverage" not in report["na"]
    assert "scoring.coverage" in report["failed"]
    assert any("evidence_missing" in r for r in report["results"]["scoring.coverage"]["reasons"])


# --- 결정성 회귀: 같은 입력·measured_at → 같은 evidence digest -------------------


def test_emitted_evidence_is_deterministic(tmp_path):
    """measured_at 을 고정하면 producer 가 두 번 돌아도 같은 evidence(바이트 동일)를 낸다
    — 결정성(§2 원칙5). CLI 도 subprocess 로 한 번 태워 스크립트 경로 정합 확인."""
    _, out_dir_a, _ = _full_run(tmp_path / "a", total=5, dual_side=True)
    _, out_dir_b, _ = _full_run(tmp_path / "b", total=5, dual_side=True)
    # project_run(run_root.name)만 다르므로 그 필드를 빼고 measured/digests 비교.
    a = json.loads((out_dir_a / "scoring.correctness.json").read_text(encoding="utf-8"))
    b = json.loads((out_dir_b / "scoring.correctness.json").read_text(encoding="utf-8"))
    assert a["measured"] == b["measured"]
    assert a["measured_at"] == b["measured_at"] == FIXED_TS


def test_cli_subprocess_runs_and_matches_pattern(tmp_path):
    """CLI 경로가 실제로 돌고, 기록된 producer_cmd 가 CheckSpec cmd_pattern 과 정합."""
    run_root = tmp_path / "run"
    res = run_root / "results"
    _junit(res / "junit.xml", 5)
    _coverage(res / "coverage.xml", 0.9)
    _from_evidence(run_root / "from_evidence", {"intent_fidelity": 1.0})
    _git_repo(run_root / "repo", {"a.py": "x"}, ["a.py"])
    script = Path(measure_submission.__file__)
    proc = subprocess.run(
        [sys.executable, str(script),
         "--submission", str(run_root / "repo"),
         "--test-junit", str(res / "junit.xml"),
         "--coverage", str(res / "coverage.xml"),
         "--from-evidence", str(run_root / "from_evidence"),
         "--measured-at", FIXED_TS,
         "--out-dir", str(run_root / "evidence")],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = _load_evidence(run_root / "evidence", "scoring.correctness")
    spec = _spec("scoring.correctness")
    import re
    assert re.search(spec.producer.cmd_pattern, ev.producer_cmd)
