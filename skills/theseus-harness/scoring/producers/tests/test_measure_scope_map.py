"""measure_scope_map.py(gate.scope_map 증거 조립기) 테스트 — JW3.

요구 매핑(계획 문서 JW3 절 테스트 매트릭스 13케이스):
  1-3  매칭 정확도 + match_glob 의미론(파일 단위 계수, 중첩 경로, 무매칭 제외)
  4-5  전 파일 무매칭 / 빈 diff → value==0 이 실패가 아니라 emit 임을 확인
  6-8  결손(no-emit, exit 0) 3종: todos 0개, plan-todos 파일 부재, git diff 실패
  7    저작 오류(exit 2) 3종: JSON 깨짐 / paths 빈 리스트 / 판정 필드
  9    evidence 무판정 가드 + measured 키 집합
  10   커널 왕복 PASS — scoring.scope_fit
  11   커널 왕복 FAIL(빈 diff → files_touched=0)
  12   결손 유지 왕복(producer 미실행 → measure_submission skipped)
  13   결정성 (a)(b) + CLI subprocess exit 0/2

실행: python -m pytest skills/theseus-harness/scoring/producers/tests/test_measure_scope_map.py -q
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import checkspec
import evidence as evidence_mod
import kernel
import measure_scope_map as producer
import measure_submission

REAL_CHECKS_DIR = Path(__file__).resolve().parents[3] / "checks"
CHECK_ID = "gate.scope_map"
FIXED_TS = "2026-07-05T00:00:00+00:00"


def _spec():
    return checkspec.load_checkspec(REAL_CHECKS_DIR / "scoring.scope_fit.json")


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


def _repo_with_changes(root: Path, changed: dict[str, str]) -> None:
    """`_make_repo` 래퍼(헬퍼 자체는 무수정) — git 은 미추적(untracked) 신규 파일을
    `git diff --name-only HEAD` 에 절대 노출하지 않는다(add 없이는 diff 대상이 아님).
    `changed` 의 각 경로를 placeholder 로 먼저 base 커밋에 실어 '추적된 파일의 워킹
    트리 수정'으로 만들어야 diff 가 실제로 그 경로들을 낸다. 빈 diff 를 의도적으로
    검사하는 테스트는 이 래퍼 대신 `_make_repo(..., changed={})` 를 직접 쓴다."""
    base = {"README.md": "base\n", **{p: "placeholder\n" for p in changed}}
    _make_repo(root, base=base, changed=changed)


def _write_todos(path: Path, todos: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"todos": todos}, ensure_ascii=False), encoding="utf-8")
    return path


def _write_junit(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        '<testsuite tests="1" failures="0" errors="0"></testsuite>\n', encoding="utf-8"
    )
    return path


def _run(plan_todos: Path, submission: Path, out_dir: Path, **over):
    argv = [
        "--plan-todos", str(plan_todos),
        "--submission", str(submission),
        "--out-dir", str(out_dir),
        "--measured-at", FIXED_TS,
    ]
    for k, v in over.items():
        argv += [f"--{k.replace('_', '-')}", str(v)]
    args = producer.build_parser().parse_args(argv)
    return producer.run(args)


# --- 1-3: 매칭 정확도 + match_glob 의미론 ---------------------------------------


def test_matching_count_and_report_per_file(tmp_path):
    """#1: changed 4파일 중 2개가 todo glob 에 매칭 → value==2, 리포트 per-file 정확."""
    root = tmp_path / "repo"
    _repo_with_changes(
        root,
        changed={
            "src/auth/login.py": "x\n",
            "db/schema/init.sql": "y\n",
            "docs/readme.md": "z\n",
            "scripts/deploy.sh": "w\n",
        },
    )
    todos = [
        {"id": "t1", "paths": ["src/auth/**"]},
        {"id": "t2", "paths": ["db/schema/**"]},
    ]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, out_dir)
    assert summary["emitted"] is True
    assert summary["value"] == 2

    report = json.loads((out_dir / f"{CHECK_ID}.report.json").read_text(encoding="utf-8"))
    by_path = {f["path"]: f["matched_todos"] for f in report["files"]}
    assert by_path["src/auth/login.py"] == ["t1"]
    assert by_path["db/schema/init.sql"] == ["t2"]
    assert by_path["docs/readme.md"] == []
    assert by_path["scripts/deploy.sh"] == []
    assert report["files_touched_observed"] == 4
    assert report["value"] == 2


def test_file_matching_two_todos_counts_once(tmp_path):
    """#2: 한 파일이 두 todo 에 매칭되어도 파일 단위로 1만 계수."""
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"src/auth/login.py": "x\n"})
    todos = [
        {"id": "t1", "paths": ["src/auth/**"]},
        {"id": "t2", "paths": ["src/auth/login.py"]},
    ]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, out_dir)
    assert summary["value"] == 1

    report = json.loads((out_dir / f"{CHECK_ID}.report.json").read_text(encoding="utf-8"))
    assert sorted(report["files"][0]["matched_todos"]) == ["t1", "t2"]


def test_glob_semantics_nested_and_exclusion(tmp_path):
    """#3: `src/auth/**` 가 중첩 경로에 매칭, `db/schema/**` 는 무관 파일을 배제."""
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"src/auth/x/y.py": "x\n", "docs/other.md": "y\n"})
    todos = [
        {"id": "t1", "paths": ["src/auth/**"]},
        {"id": "t2", "paths": ["db/schema/**"]},
    ]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, out_dir)
    assert summary["value"] == 1

    report = json.loads((out_dir / f"{CHECK_ID}.report.json").read_text(encoding="utf-8"))
    by_path = {f["path"]: f["matched_todos"] for f in report["files"]}
    assert by_path["src/auth/x/y.py"] == ["t1"]
    assert by_path["docs/other.md"] == []


# --- 4-5: value==0 이 실패가 아님을 확인 -----------------------------------------


def test_all_files_unmatched_emits_zero(tmp_path):
    """#4: 전 파일 무매칭 → value==0, 그래도 emit 됨."""
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"unrelated/a.py": "x\n"})
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, out_dir)
    assert summary["emitted"] is True
    assert summary["value"] == 0
    assert (out_dir / f"{CHECK_ID}.json").exists()


def test_empty_diff_emits_zero_not_failure(tmp_path):
    """#5: 빈 diff(변경 없음) → value==0 emit(실패 아님, no-emit 결손과 구분)."""
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={})
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, out_dir)
    assert summary["emitted"] is True
    assert summary["value"] == 0
    assert summary["files_touched_observed"] == 0


# --- 6, 8: 결손(no-emit, exit 0) -------------------------------------------------


def test_no_emit_on_missing_plan_todos_file(tmp_path):
    """#6a: plan-todos 파일 부재 → emit 안 함, exit 0."""
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={"a.py": "x\n"})
    missing = tmp_path / "absent-plan-todos.json"
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(missing, root, out_dir)
    assert summary["emitted"] is False
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_no_emit_on_zero_todos(tmp_path):
    """#6b: todos 0개 → emit 안 함, exit 0."""
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={"a.py": "x\n"})
    plan_todos = _write_todos(tmp_path / "empty-todos.json", [])
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, out_dir)
    assert summary["emitted"] is False
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_no_emit_on_git_diff_failure(tmp_path):
    """#8: 비-git 디렉터리(diff 실패) → emit 안 함, exit 0, summary 에 git_error."""
    non_git = tmp_path / "not_a_repo"
    non_git.mkdir()
    todos = [{"id": "t1", "paths": ["a.py"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, non_git, out_dir)
    assert summary["emitted"] is False
    assert summary.get("git_error")
    assert not (out_dir / f"{CHECK_ID}.json").exists()


# --- 7: 저작 오류(exit 2) --------------------------------------------------------


def test_schema_error_on_malformed_json(tmp_path):
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={"a.py": "x\n"})
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    out_dir = tmp_path / "run" / "evidence"
    with pytest.raises(producer.ScopeMapSchemaError):
        _run(broken, root, out_dir)
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_schema_error_on_empty_paths(tmp_path):
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={"a.py": "x\n"})
    plan_todos = _write_todos(tmp_path / "empty-paths.json", [{"id": "t1", "paths": []}])
    out_dir = tmp_path / "run" / "evidence"
    with pytest.raises(producer.ScopeMapSchemaError):
        _run(plan_todos, root, out_dir)
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_schema_error_on_verdict_field(tmp_path):
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={"a.py": "x\n"})
    plan_todos = _write_todos(
        tmp_path / "verdict.json", [{"id": "t1", "paths": ["a.py"], "verified": True}]
    )
    out_dir = tmp_path / "run" / "evidence"
    with pytest.raises(producer.ScopeMapSchemaError):
        _run(plan_todos, root, out_dir)
    assert not (out_dir / f"{CHECK_ID}.json").exists()


def test_cli_exit_code_2_on_schema_violation(tmp_path):
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={"a.py": "x\n"})
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    script = Path(producer.__file__)
    out_dir = tmp_path / "run" / "evidence"
    proc = subprocess.run(
        [
            sys.executable, str(script),
            "--plan-todos", str(broken),
            "--submission", str(root),
            "--measured-at", FIXED_TS,
            "--out-dir", str(out_dir),
        ],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 2
    assert not (out_dir / f"{CHECK_ID}.json").exists()


# --- 9: evidence 무판정 가드 ------------------------------------------------------


def test_evidence_no_verdict_and_measured_keys(tmp_path):
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"src/auth/a.py": "x\n"})
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, out_dir)
    assert summary["emitted"] is True

    ev = evidence_mod.load_evidence(out_dir / f"{CHECK_ID}.json")
    assert ev.produced_by == "run"
    assert ev.self_reported is False
    assert set(ev.measured.keys()) == {"files_mapped_to_todos"}
    dumped = json.dumps(ev.to_dict())
    assert '"verdict"' not in dumped
    assert '"pass"' not in dumped


# --- 10-12: 커널 왕복 ------------------------------------------------------------


def test_kernel_round_trip_pass(tmp_path):
    """#10: 같은 --git-base 로 producer+measure_submission → scoring.scope_fit PASS,
    value==mapped/touched, 승계값 <= files_touched."""
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"src/auth/login.py": "x\n", "docs/other.md": "y\n"})
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    evidence_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, evidence_dir)
    assert summary["value"] == 1

    junit = _write_junit(tmp_path / "run" / "results" / "junit.xml")
    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(root),
        "--test-junit", str(junit),
        "--from-evidence", str(evidence_dir),
        "--measured-at", FIXED_TS,
        "--out-dir", str(tmp_path / "run" / "sub_evidence"),
    ])
    measure_submission.run(sub_args)

    ev = evidence_mod.load_evidence(tmp_path / "run" / "sub_evidence" / "scoring.scope_fit.json")
    v = kernel.verify(_spec(), ev, artifact_root=tmp_path / "run", verified_at=FIXED_TS)
    assert v.result == "PASS", v.reasons
    assert v.value == pytest.approx(1 / 2)
    assert ev.measured["files_mapped_to_todos"]["value"] <= ev.measured["files_touched"]["value"]


def test_kernel_round_trip_fail_empty_diff(tmp_path):
    """#11: 빈 diff → mapped 0 emit + measure_submission files_touched 0 →
    scoring.scope_fit FAIL, reasons 에 "no files touched"."""
    root = tmp_path / "repo"
    _make_repo(root, base={"README.md": "base\n"}, changed={})
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    evidence_dir = tmp_path / "run" / "evidence"
    summary = _run(plan_todos, root, evidence_dir)
    assert summary["value"] == 0

    junit = _write_junit(tmp_path / "run" / "results" / "junit.xml")
    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(root),
        "--test-junit", str(junit),
        "--from-evidence", str(evidence_dir),
        "--measured-at", FIXED_TS,
        "--out-dir", str(tmp_path / "run" / "sub_evidence"),
    ])
    measure_submission.run(sub_args)

    ev = evidence_mod.load_evidence(tmp_path / "run" / "sub_evidence" / "scoring.scope_fit.json")
    v = kernel.verify(_spec(), ev, artifact_root=tmp_path / "run", verified_at=FIXED_TS)
    assert v.result == "FAIL"
    assert any("no files touched" in r for r in v.reasons)


def test_deficit_maintained_without_producer(tmp_path):
    """#12: producer 미실행 → measure_submission skipped["scoring.scope_fit"] 에
    "files_mapped_to_todos" 포함, scoring.scope_fit 미emit."""
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"a.py": "x\n"})
    junit = _write_junit(tmp_path / "run" / "results" / "junit.xml")

    sub_args = measure_submission.build_parser().parse_args([
        "--submission", str(root),
        "--test-junit", str(junit),
        "--measured-at", FIXED_TS,
        "--out-dir", str(tmp_path / "run" / "sub_evidence"),
    ])
    summary = measure_submission.run(sub_args)
    assert "files_mapped_to_todos" in summary["skipped"].get("scoring.scope_fit", [])
    assert "scoring.scope_fit" not in summary["emitted"]


# --- 13: 결정성 + CLI ------------------------------------------------------------


def test_deterministic_bytes_same_root(tmp_path):
    """#13a: 같은 fixture·같은 --measured-at 2회 실행 → evidence/리포트 바이트 동일."""
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"src/auth/a.py": "x\n"})
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    out_dir = tmp_path / "run" / "evidence"

    first_summary = _run(plan_todos, root, out_dir)
    assert first_summary["value"] == 1  # 실제 매칭이 일어남을 확인(우연한 0 아님)
    first_ev = (out_dir / f"{CHECK_ID}.json").read_bytes()
    first_report = (out_dir / f"{CHECK_ID}.report.json").read_bytes()

    _run(plan_todos, root, out_dir)
    second_ev = (out_dir / f"{CHECK_ID}.json").read_bytes()
    second_report = (out_dir / f"{CHECK_ID}.report.json").read_bytes()

    assert first_ev == second_ev
    assert first_report == second_report


def test_deterministic_measured_across_roots(tmp_path):
    """#13b: 서로 다른 tmp 루트 2곳에 동일 fixture → 두 evidence 의 measured dict 동일."""
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    results = []
    for label in ("a", "b"):
        root_base = tmp_path / label
        repo = root_base / "repo"
        _repo_with_changes(repo, changed={"src/auth/a.py": "x\n"})
        plan_todos = _write_todos(root_base / "plan-todos.json", todos)
        out_dir = root_base / "run" / "evidence"
        summary = _run(plan_todos, repo, out_dir)
        assert summary["value"] == 1
        results.append(json.loads((out_dir / f"{CHECK_ID}.json").read_text(encoding="utf-8")))
    assert results[0]["measured"] == results[1]["measured"]


def test_cli_subprocess_exit_zero(tmp_path):
    root = tmp_path / "repo"
    _repo_with_changes(root, changed={"src/auth/a.py": "x\n"})
    todos = [{"id": "t1", "paths": ["src/auth/**"]}]
    plan_todos = _write_todos(tmp_path / "plan-todos.json", todos)
    script = Path(producer.__file__)
    out_dir = tmp_path / "run" / "evidence"
    proc = subprocess.run(
        [
            sys.executable, str(script),
            "--plan-todos", str(plan_todos),
            "--submission", str(root),
            "--measured-at", FIXED_TS,
            "--out-dir", str(out_dir),
        ],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr
    ev = evidence_mod.load_evidence(out_dir / f"{CHECK_ID}.json")
    assert re.search(r"measure_scope_map\.py", ev.producer_cmd)
