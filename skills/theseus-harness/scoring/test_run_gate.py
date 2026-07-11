#!/usr/bin/env python3
"""test_run_gate.py — phase-09 게이트 러너 검증 (WP-B1a).

층:
  1. exit 매핑 순수 함수 — verdict→exit(0/1/2) (외부 실행 없이 결정적).
  2. 미니 end-to-end — 실 git submission 왕복으로 run dir 구조·verdict 산출·evidence emit·
     gate_history 아카이브를 값으로 확인. --junit 재사용으로 pytest-in-pytest 재귀 회피.
  3. --phase-upto deferred — 실 레지스트리에서 phase-10 sprint.regression 이 --phase-upto 09
     지정 시 deferred(비게이팅)로 분류되고 failed 에서 빠지는지, 미지정 시 여전히 게이팅
     (failed)이며 report 에 deferred 키가 없는지(하위호환).
  4. gate_history prior — 두 번째 실행의 sprint 가 첫 실행이 아카이브한 correctness 를 prior
     로 실제 소비하는지.
  5. 결정성 — 같은 measured_at 2회 → gate_meta_audit.json 바이트 동일(sprint/archive off).
  6. CLI exit — subprocess 로 실제 exit code 가 verdict 매핑과 일치.

저장소 self_lint C35 — 모든 open/subprocess encoding="utf-8".
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import run_gate


# --- 공통 fixture 헬퍼 ---------------------------------------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_junit(path: Path) -> None:
    _write(
        path,
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<testsuite name="fx" tests="3" failures="0" errors="0" skipped="0">\n'
        '<testcase classname="t" name="t1"/><testcase classname="t" name="t2"/>'
        '<testcase classname="t" name="t3"/></testsuite>\n',
    )


def _init_git_repo(root: Path) -> None:
    run = lambda *a: subprocess.run(
        ["git", "-C", str(root), *a],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    run("add", "-A")
    run("commit", "-q", "-m", "base")


def _plain_submission(tmp_path: Path) -> Path:
    """gate 선언 아티팩트 없이 2 모듈 git repo — gates 스킵, scoring.* 대부분 결손."""
    code = tmp_path / "repo"
    _write(code / "mod_a.py", "def add(a, b):\n    return a + b\n")
    _write(code / "mod_b.py", "def sub(a, b):\n    return a - b\n")
    _init_git_repo(code)
    # working-tree 변경 — git diff --name-only HEAD 가 비지 않도록.
    _write(code / "mod_a.py", "def add(a, b):\n    return a + b\n\n\ndef mul(a, b):\n    return a * b\n")
    return code


def _gate_artifacts(tmp_path: Path) -> tuple[Path, Path, Path]:
    """scoring.correctness.json 이 emit 되도록 참인 criteria/todos/contract 저작."""
    criteria = tmp_path / "intent-criteria.json"
    _write(criteria, json.dumps({"criteria": [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "mod_a.py"}},
        {"id": "c2", "required": True, "backing": {"kind": "test", "ref": "t1"}},
    ]}))
    todos = tmp_path / "plan-todos.json"
    _write(todos, json.dumps({"todos": [{"id": "t1", "paths": ["mod_a.py"]}]}))
    contract = tmp_path / "solid-contract.json"
    _write(contract, json.dumps({"modules": [
        {"module": "mod_b.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "requests"}}]},
    ]}))
    return criteria, todos, contract


def _common_kwargs(tmp_path: Path, code: Path) -> dict:
    junit = tmp_path / "fixture-junit.xml"
    _fixture_junit(junit)
    return {
        "grade": "G3",
        "submission": str(code),
        "test_target": str(code),
        "code_root": str(code),
        "git_base": "HEAD",
        "junit": str(junit),
        "cold_reunderstanding": str(_cold(tmp_path)[0]),
        "cold_reference": str(_cold(tmp_path)[1]),
        "measured_at": "2026-07-05T00:00:00+00:00",
        "verified_at": "2026-07-05T00:00:00+00:00",
    }


def _cold(tmp_path: Path) -> tuple[Path, Path]:
    ru = tmp_path / "reread.md"
    ref = tmp_path / "source.md"
    if not ru.exists():
        _write(ru, "cold reunderstanding text about modules and errors\n")
        _write(ref, "source plan text describing modules\n")
    return ru, ref


# --- (1) exit 매핑 순수 함수 ---------------------------------------------------


def test_verdict_exit_mapping() -> None:
    """exit = verdict(§2.1): pass=0 / fail=1 / 미산출(크래시)=2."""
    assert run_gate._verdict_exit("pass") == 0
    assert run_gate._verdict_exit("fail") == 1
    assert run_gate._verdict_exit(None) == 2


# --- (2) 미니 end-to-end -------------------------------------------------------


def test_run_gate_end_to_end_emits_artifacts(tmp_path: Path) -> None:
    """실 submission 왕복 → run dir 구조 + verdict 산출 + evidence + gate_history."""
    code = _plain_submission(tmp_path)
    run_root = tmp_path / "run"
    result = run_gate.run_gate(
        project_root=str(run_root),
        # 존재하지 않는 gate 아티팩트 → gates 스킵(hermetic).
        intent_criteria=str(tmp_path / "nx1.json"),
        plan_todos=str(tmp_path / "nx2.json"),
        solid_contract=str(tmp_path / "nx3.json"),
        **_common_kwargs(tmp_path, code),
    )

    assert result["verdict"] in {"pass", "fail"}
    assert (run_root / "quality" / "gate_meta_audit.json").exists()
    assert (run_root / "results" / "junit.xml").exists()
    emitted = set(result["emitted_evidence"])
    for expected in ("quality.deep_module.json", "quality.dry.json",
                     "quality.define_errors.json", "cold.isolation.json"):
        assert expected in emitted, f"{expected} not emitted: {emitted}"
    # gate_history 아카이브(§2.2 단계 9) — evidence + verdict 사본.
    hist = Path(result["gate_history_dir"])
    assert hist.exists()
    assert (hist / "gate_meta_audit.json").exists()
    assert (hist / "evidence" / "cold.isolation.json").exists()


# --- (3) --phase-upto deferred (실 레지스트리) ---------------------------------


def test_phase_upto_09_defers_sprint_regression(tmp_path: Path) -> None:
    """phase-10 sprint.regression 이 --phase-upto 09 지정 시 deferred(비게이팅)로 분류되고
    failed 에서 빠진다 — phase-09 시점 evidence 원리상 부재의 영구 FAIL 해소(§2.4). frozen
    체크는 나중 페이즈여도 advisory 로 남는다('active 체크'만 defer)."""
    code = _plain_submission(tmp_path)
    run_root = tmp_path / "run"
    result = run_gate.run_gate(
        project_root=str(run_root),
        intent_criteria=str(tmp_path / "nx1.json"),
        plan_todos=str(tmp_path / "nx2.json"),
        solid_contract=str(tmp_path / "nx3.json"),
        phase_upto="09",
        **_common_kwargs(tmp_path, code),
    )
    report = result["report"]
    assert "deferred" in report  # phase_upto 지정 → deferred 키 존재
    assert "sprint.regression" in report["deferred"]
    assert "sprint.regression" not in report["failed"]
    # frozen.viewer_mandatory(phase 13)는 나중 페이즈지만 status frozen 이라 advisory 유지.
    assert "frozen.viewer_mandatory" in report["advisory"]
    assert "frozen.viewer_mandatory" not in report["deferred"]
    # 도달 가능(phase≤09) 체크는 deferred 관대함 부활이 아니다 — 여전히 엄격 게이팅.
    # gates 스킵이라 scoring.correctness 는 여전히 evidence_missing FAIL(failed 에 존재).
    assert "scoring.correctness" in report["failed"]


def test_no_phase_upto_gates_sprint_regression_and_has_no_deferred_key(tmp_path: Path) -> None:
    """미지정 시 sprint.regression 은 여전히 게이팅(failed)이며 report 에 deferred 키가
    아예 없다 — 하위호환(기존 동작·바이트 불변)."""
    code = _plain_submission(tmp_path)
    run_root = tmp_path / "run"
    result = run_gate.run_gate(
        project_root=str(run_root),
        intent_criteria=str(tmp_path / "nx1.json"),
        plan_todos=str(tmp_path / "nx2.json"),
        solid_contract=str(tmp_path / "nx3.json"),
        enable_sprint=False,   # 첫 실행 prior 부재와 무관하게 순수 미지정 경로 확인
        **_common_kwargs(tmp_path, code),
    )
    report = result["report"]
    assert "deferred" not in report
    assert "sprint.regression" in report["failed"]  # 미지정 → 전 체크 게이팅


# --- (4) gate_history prior 소비 ----------------------------------------------


def test_second_run_sprint_consumes_prior_from_history(tmp_path: Path) -> None:
    """두 번째 실행의 sprint 가 첫 실행이 아카이브한 scoring.correctness 를 prior 로 실제
    소비한다(gate_history 누적 → measure_regression 발화). 참인 gate 아티팩트로 scoring.
    correctness.json 이 emit 되어야 prior/current 가 존재한다."""
    code = _plain_submission(tmp_path)
    criteria, todos, contract = _gate_artifacts(tmp_path)
    run_root = tmp_path / "run"
    kw = dict(
        project_root=str(run_root),
        intent_criteria=str(criteria),
        plan_todos=str(todos),
        solid_contract=str(contract),
        **_common_kwargs(tmp_path, code),
    )

    first = run_gate.run_gate(**kw)
    # 첫 실행: prior 부재 → sprint 미발화, 하지만 correctness 는 아카이브됨.
    assert first["steps"]["sprint"]["summary"]["emitted"] is False
    assert "scoring.correctness.json" in set(first["emitted_evidence"])

    second = run_gate.run_gate(**kw)
    # 두 번째 실행: gate_history 최신(첫 실행)에서 prior 를 찾아 measure_regression 발화.
    assert second["steps"]["sprint"]["summary"]["emitted"] is True
    assert "sprint.regression.json" in set(second["emitted_evidence"])
    # gate_history 가 두 실행분(00, 01) 누적.
    hist_root = run_root / "state" / "gate_history"
    assert (hist_root / "00").is_dir()
    assert (hist_root / "01").is_dir()


# --- (5) 결정성 ----------------------------------------------------------------


def test_run_gate_determinism_same_measured_at(tmp_path: Path) -> None:
    """같은 measured_at 2회(sprint/archive off) → gate_meta_audit.json 바이트 동일(§2.6)."""
    code = _plain_submission(tmp_path)
    run_root = tmp_path / "run"
    kw = dict(
        project_root=str(run_root),
        intent_criteria=str(tmp_path / "nx1.json"),
        plan_todos=str(tmp_path / "nx2.json"),
        solid_contract=str(tmp_path / "nx3.json"),
        enable_sprint=False,
        enable_archive=False,
        **_common_kwargs(tmp_path, code),
    )
    run_gate.run_gate(**kw)
    first_bytes = (run_root / "quality" / "gate_meta_audit.json").read_bytes()
    run_gate.run_gate(**kw)
    second_bytes = (run_root / "quality" / "gate_meta_audit.json").read_bytes()
    assert first_bytes == second_bytes


# --- (5b) G1 병렬 producer 그룹 = 직렬 등가 --------------------------------------


def test_parallel_producer_group_equals_serial(tmp_path: Path) -> None:
    """G1: 병렬(default)과 직렬(--no-parallel)이 같은 run_root 에서 gate_meta_audit.json
    바이트 동일 + 같은 evidence emit + 같은 verdict — 독립 producer 병렬화가 verdict 를
    바꾸지 않음(behavior-preserving; 결정성은 evidence 내용에만 의존, 실행 순서 무관)."""
    code = _plain_submission(tmp_path)
    run_root = tmp_path / "run"
    kw = dict(
        project_root=str(run_root),
        intent_criteria=str(tmp_path / "nx1.json"),
        plan_todos=str(tmp_path / "nx2.json"),
        solid_contract=str(tmp_path / "nx3.json"),
        enable_archive=False,   # gate_history 누적 없이 두 실행을 독립 함수로
        **_common_kwargs(tmp_path, code),
    )
    par = run_gate.run_gate(enable_parallel=True, **kw)
    par_bytes = (run_root / "quality" / "gate_meta_audit.json").read_bytes()
    ser = run_gate.run_gate(enable_parallel=False, **kw)
    ser_bytes = (run_root / "quality" / "gate_meta_audit.json").read_bytes()

    assert par_bytes == ser_bytes
    assert set(par["emitted_evidence"]) == set(ser["emitted_evidence"])
    assert par["verdict"] == ser["verdict"]
    # 병렬 그룹의 step 결과가 모두 실렸는지(누락 없이 barrier 취합).
    for name in ("quality", "gates", "plan", "cold", "review"):
        assert name in par["steps"]


# --- (6) CLI exit code = verdict 매핑 -----------------------------------------


def test_cli_exit_code_matches_verdict(tmp_path: Path) -> None:
    """subprocess 로 run_gate.py 를 돌려 실제 exit code 가 verdict 매핑과 일치함을 확인.
    hermetic fixture 는 다수 결손이라 verdict=fail → exit 1."""
    code = _plain_submission(tmp_path)
    junit = tmp_path / "fixture-junit.xml"
    _fixture_junit(junit)
    ru, ref = _cold(tmp_path)
    run_root = tmp_path / "run"
    proc = subprocess.run(
        [
            sys.executable, str(Path(run_gate.__file__)),
            "--project-root", str(run_root),
            "--grade", "G3",
            "--submission", str(code),
            "--test-target", str(code),
            "--code-root", str(code),
            "--junit", str(junit),
            "--cold-reunderstanding", str(ru),
            "--cold-reference", str(ref),
            "--intent-criteria", str(tmp_path / "nx1.json"),
            "--plan-todos", str(tmp_path / "nx2.json"),
            "--solid-contract", str(tmp_path / "nx3.json"),
            "--phase-upto", "09",
            "--measured-at", "2026-07-05T00:00:00+00:00",
            "--verified-at", "2026-07-05T00:00:00+00:00",
        ],
        capture_output=True, text=True, encoding="utf-8",
    )
    report = json.loads((run_root / "quality" / "gate_meta_audit.json").read_text(encoding="utf-8"))
    assert proc.returncode == run_gate._verdict_exit(report["verdict"]), proc.stderr
    assert proc.returncode == 1  # 결손 다수 → fail


# --- (7) 발화 리허설 (WP-B1d — B1 완료 게이트) ----------------------------------
#
# 앞의 (2)~(6) 은 "러너가 발화하고 exit 이 verdict 를 반영한다"를 확인하지만 fixture 가
# 다수 결손이라 verdict 가 항상 fail 이다 — 즉 게이트가 *열린* 적이 없다. 이 절은
# "커널이 실제로 게이팅한다(문을 여닫는다)"를 실 submission 왕복으로 증명한다:
#
#   1. 전-녹색 baseline — 실 git repo + 실 pytest junit + 실 git diff + coverage/e2e
#      artifact + 3 선언 아티팩트(참인 claim)를 §4 관례대로 배치하면 G2 게이팅 집합이
#      전부 PASS/NA → verdict=pass → exit 0. (게이트가 열린다.)
#   2. 진짜 결함 주입 — solid-contract 가 `absent_import: sqlite3` 를 선언한 모듈에
#      `import sqlite3` 를 넣으면 producer 가 디스크 재검사에서 DIP claim 미검증을
#      관측 → dip_violation=1 → scoring.solid 의 `dip_violation == 0` assertion 이 FAIL.
#      **오직 scoring.solid 만** PASS→FAIL 로 뒤집히고 verdict=fail → exit 1. (문이 닫힌다.)
#   3. 결함 제거 — 원복하면 scoring.solid 가 PASS 로 복귀 → verdict=pass → exit 0.
#
# 옛 self-score 는 "SOLID 잘 지켰습니다" 같은 자기신고를 통과시켰지만, 커널은 선언과
# 디스크의 불일치를 값으로 잡는다 — 그 차이가 이 왕복의 0↔1 exit 뒤집힘이다.

_MOD_A_V1 = '''"""Running-total accumulator with wraparound at a fixed ceiling."""


def accumulate(values, ceiling):
    total = 0
    for value in values:
        total = total + value
        while total >= ceiling:
            total = total - ceiling
    return total
'''

# 커밋 후 working-tree 변경(diff 비지 않게) — mod_a.py 에 두 번째 deep 함수 추가.
_MOD_A_V2 = _MOD_A_V1 + '''

def scale(values, factor):
    scaled = []
    for value in values:
        scaled.append(value * factor)
    return scaled
'''

_MOD_B_CLEAN = '''"""Pick the largest element, or None when the input is empty."""


def largest(items):
    best = None
    for item in items:
        if best is None or item > best:
            best = item
    return best
'''

# 결함 주입판 — solid-contract 의 `absent_import: sqlite3` 를 위반하는 구체 import.
_MOD_B_FAULT = '''"""Pick the largest element, or None when the input is empty."""
import sqlite3


def largest(items):
    best = None
    for item in items:
        if best is None or item > best:
            best = item
    return best
'''


def _e2e_junit(path: Path) -> None:
    _write(
        path,
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<testsuite name="e2e" tests="2" failures="0" errors="0" skipped="0">\n'
        '<testcase classname="e" name="e1"/><testcase classname="e" name="e2"/></testsuite>\n',
    )


def _cobertura(path: Path) -> None:
    _write(path, '<?xml version="1.0" ?>\n<coverage branch-rate="0.85" line-rate="0.9"></coverage>\n')


def _rehearsal_fixture(tmp_path: Path) -> dict:
    """전-녹색 G2 실 submission + 3 선언 아티팩트 + 실행 산물을 조립한다.

    반환 dict 는 run_gate 인자 + `set_fault(bool)` 헬퍼를 담는다. set_fault(True) 는
    mod_b.py 에 `import sqlite3` 를 써서 solid-contract 의 DIP claim 을 실 디스크에서
    위반시키고, set_fault(False) 는 clean 판으로 원복한다(러너는 이 파일을 producer 로
    재검사하므로 git commit 불필요 — 디스크 상태만 바꾼다)."""
    code = tmp_path / "repo"
    _write(code / "mod_a.py", _MOD_A_V1)
    _write(code / "mod_b.py", _MOD_B_CLEAN)
    _init_git_repo(code)
    _write(code / "mod_a.py", _MOD_A_V2)  # working-tree diff → files_touched > 0

    criteria = tmp_path / "intent-criteria.json"
    _write(criteria, json.dumps({"criteria": [
        {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "mod_a.py"}},
        {"id": "c2", "required": True, "backing": {"kind": "diff", "ref": "mod_a.py"}},
    ]}))
    todos = tmp_path / "plan-todos.json"
    _write(todos, json.dumps({"todos": [{"id": "t1", "paths": ["mod_a.py"]}]}))
    contract = tmp_path / "solid-contract.json"
    _write(contract, json.dumps({"modules": [
        {"module": "mod_b.py", "claims": [
            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}}]},
    ]}))

    junit = tmp_path / "unit-junit.xml"
    _fixture_junit(junit)
    e2e = tmp_path / "e2e-junit.xml"
    _e2e_junit(e2e)
    coverage = tmp_path / "coverage.xml"
    _cobertura(coverage)

    def set_fault(on: bool) -> None:
        _write(code / "mod_b.py", _MOD_B_FAULT if on else _MOD_B_CLEAN)

    return {
        "kwargs": {
            "project_root": str(tmp_path / "run"),
            "grade": "G2",
            "submission": str(code),
            "test_target": str(code),
            "code_root": str(code),
            "git_base": "HEAD",
            "junit": str(junit),
            "e2e_junit": str(e2e),
            "coverage": str(coverage),
            "intent_criteria": str(criteria),
            "plan_todos": str(todos),
            "solid_contract": str(contract),
            "phase_upto": "09",
            # G2 는 plan/sprint/cold/frozen 체크가 없다 — 그 단계를 꺼 왕복을 순수
            # 디스크-상태 함수로 만든다(각 fire 는 이전 fire 와 독립).
            "enable_plan": False,
            "enable_sprint": False,
            "enable_archive": False,
            "measured_at": "2026-07-05T00:00:00+00:00",
            "verified_at": "2026-07-05T00:00:00+00:00",
        },
        "set_fault": set_fault,
    }


def _solid_result(report: dict) -> str:
    return report["results"]["scoring.solid"]["result"]


def test_rehearsal_baseline_is_green_gate_opens(tmp_path: Path) -> None:
    """리허설 baseline: 전-녹색 실 submission 에서 러너가 발화해 verdict=pass → exit 0.
    게이트가 실제로 *열린다*(앞 절 fixture 들과 달리 결손 없는 왕복의 존재 증명)."""
    fx = _rehearsal_fixture(tmp_path)
    result = run_gate.run_gate(**fx["kwargs"])
    report = result["report"]

    assert result["verdict"] == "pass", report["failed"]
    assert run_gate._verdict_exit(result["verdict"]) == 0
    assert (Path(result["run_root"]) / "quality" / "gate_meta_audit.json").exists()
    assert report["failed"] == []
    assert _solid_result(report) == "PASS"
    # 게이트가 실제 실행 산물을 소비했다는 값 증거(자기신고 아님).
    assert "scoring.solid.json" in set(result["emitted_evidence"])
    assert "scoring.correctness.json" in set(result["emitted_evidence"])


def test_rehearsal_fault_injection_flips_solid_and_exit(tmp_path: Path) -> None:
    """B1 완료 게이트: 진짜 결함(solid-contract 가 absent_import 선언한 모듈에
    import sqlite3 주입)이 **scoring.solid 만** PASS→FAIL 로 뒤집고 verdict/exit 이
    반영되며, 결함 제거 시 원복함을 실 왕복으로 단언한다."""
    fx = _rehearsal_fixture(tmp_path)
    run = lambda: run_gate.run_gate(**fx["kwargs"])

    # 1. baseline — 게이트 열림.
    fx["set_fault"](False)
    base = run()
    assert base["verdict"] == "pass"
    assert run_gate._verdict_exit(base["verdict"]) == 0
    assert _solid_result(base["report"]) == "PASS"
    assert "scoring.solid" not in base["report"]["failed"]

    # 2. 결함 주입 — dip_violation=1 → scoring.solid FAIL, exit 1. 게이트 닫힘.
    fx["set_fault"](True)
    faulted = run()
    assert faulted["verdict"] == "fail"
    assert run_gate._verdict_exit(faulted["verdict"]) == 1
    assert _solid_result(faulted["report"]) == "FAIL"
    assert faulted["report"]["failed"] == ["scoring.solid"]  # 오직 solid 만 뒤집힘

    # 3. 결함 제거 — PASS 복귀, exit 0. 게이트 다시 열림.
    fx["set_fault"](False)
    reverted = run()
    assert reverted["verdict"] == "pass"
    assert run_gate._verdict_exit(reverted["verdict"]) == 0
    assert _solid_result(reverted["report"]) == "PASS"
    assert reverted["report"]["failed"] == []


def test_rehearsal_cli_process_exit_flips_with_fault(tmp_path: Path) -> None:
    """리허설을 실제 프로세스로 발화 — run_gate.py 의 실 exit code 가 결함 주입 전후로
    0↔1 을 오간다(단언만이 아니라 OS 프로세스 반환값 관측)."""
    fx = _rehearsal_fixture(tmp_path)
    k = fx["kwargs"]

    def cli() -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable, str(Path(run_gate.__file__)),
                "--project-root", k["project_root"],
                "--grade", k["grade"],
                "--submission", k["submission"],
                "--test-target", k["test_target"],
                "--code-root", k["code_root"],
                "--junit", k["junit"],
                "--e2e-junit", k["e2e_junit"],
                "--coverage", k["coverage"],
                "--intent-criteria", k["intent_criteria"],
                "--plan-todos", k["plan_todos"],
                "--solid-contract", k["solid_contract"],
                "--phase-upto", "09",
                "--no-plan", "--no-sprint", "--no-archive",
                "--measured-at", k["measured_at"],
                "--verified-at", k["verified_at"],
            ],
            capture_output=True, text=True, encoding="utf-8",
        )

    fx["set_fault"](False)
    base = cli()
    assert base.returncode == 0, base.stderr

    fx["set_fault"](True)
    faulted = cli()
    assert faulted.returncode == 1, faulted.stderr
    # 프로세스 exit 이 gate_meta_audit.json verdict 매핑과 정확히 일치함을 재확인.
    report = json.loads(
        (Path(k["project_root"]) / "quality" / "gate_meta_audit.json").read_text(encoding="utf-8")
    )
    assert faulted.returncode == run_gate._verdict_exit(report["verdict"])
    assert report["failed"] == ["scoring.solid"]

    fx["set_fault"](False)
    reverted = cli()
    assert reverted.returncode == 0, reverted.stderr
