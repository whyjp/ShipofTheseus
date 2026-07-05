#!/usr/bin/env python3
"""test_dogfood.py — WP8 dogfood runner 검증 (+ JW5 gate producer 단계 검증).

세 층으로 나눈다:
  1. classify() 순수 함수 — 합성 meta_audit 리포트로 PASS/FAIL/NA/ADVISORY/deficit
     5분류와 measured_backed 카운트를 검증(외부 실행 없이 결정적).
  2. 미니 end-to-end — 픽스처 코드/junit/cold 쌍으로 파이프라인을 끝까지 돌려
     run dir 구조·verdict 산출·evidence emit 을 검증. --junit 재사용으로
     pytest-in-pytest 재귀를 피한다(dogfood 의 seam). 이 테스트는 gate 선언
     아티팩트를 존재하지 않는 경로로 명시해 실 저장소의 `scoring/dogfood_inputs/`
     기본값과 완전히 분리한다(hermetic) — gate producer 는 스킵되고 그 사유가
     `steps["gates"]`에 기록되는 것만 검증한다.
  3. gate producer 단계(JW5) — 자체 hermetic git fixture 에 참인 criteria/todos/
     contract 를 저작해 `_gate_producers` 가 scoring.correctness/scope_fit/solid 를
     결손에서 실측 backing(PASS/FAIL 값)으로 전환하는 것을 값으로 확인한다.

저장소 self_lint C35 — 모든 open/subprocess encoding="utf-8".
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import dogfood


def test_classify_five_buckets() -> None:
    """FAIL 중 evidence_missing 은 deficit 로 세분류되고, 실 assertion FAIL 과 구분된다."""
    report = {
        "active_checks": ["a", "b", "c", "d", "e"],
        "results": {
            "a": {"result": "PASS", "value": 0.9, "reasons": []},
            "b": {"result": "FAIL", "value": None, "reasons": ["evidence_missing (absence_policy=FAIL)"]},
            "c": {"result": "FAIL", "value": None, "reasons": ["failing tests present"]},
            "d": {"result": "NA", "value": None, "reasons": ["not applicable"]},
            "e": {"result": "ADVISORY", "value": None, "kernel_result": "FAIL", "reasons": ["evidence_missing"]},
        },
        "verdict": "fail",
    }
    out = dogfood.classify(report)
    counts = out["counts"]
    assert counts["PASS"] == 1
    assert counts["FAIL"] == 1  # 실 assertion FAIL (c) 만 — deficit(b)는 제외
    assert counts["deficit"] == 1  # evidence_missing FAIL (b)
    assert counts["NA"] == 1
    assert counts["ADVISORY"] == 1
    # measured_backed = 커널이 evidence 를 실제 로드해 평가한 것(PASS + 실FAIL + NA).
    assert counts["measured_backed"] == 3
    assert out["verdict"] == "fail"


def test_classify_empty_report() -> None:
    """리포트가 비어도(파싱 실패 fallback) 크래시 없이 빈 분류를 낸다."""
    out = dogfood.classify({})
    assert out["rows"] == []
    assert out["verdict"] is None


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_junit(path: Path) -> None:
    """재사용용 최소 junit — pytest 를 돌리지 않고 tests_* provenance 를 backing."""
    _write(
        path,
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<testsuite name="fx" tests="3" failures="0" errors="0" skipped="0">\n'
        '<testcase classname="t" name="t1"/><testcase classname="t" name="t2"/>'
        '<testcase classname="t" name="t3"/></testsuite>\n',
    )


def test_dogfood_end_to_end(tmp_path: Path) -> None:
    """픽스처로 전체 파이프라인 실행 → run dir + verdict + evidence + gate 산출 검증.

    gate 선언 아티팩트(intent-criteria/plan-todos/solid-contract)는 존재하지 않는
    tmp_path 경로로 명시한다 — 실 저장소의 `scoring/dogfood_inputs/` 기본값이 이
    hermetic 픽스처에 새지 않게 하기 위함(JW5). 그래서 gate producer 3종은 모두
    스킵되고, scoring.correctness 등은 여전히 결손(evidence_missing)으로 관측된다 —
    이 테스트는 "선언 아티팩트가 없을 때" 정직한 결손 경로가 보존됨을 검증한다.
    """
    code_root = tmp_path / "code"
    _write(code_root / "mod_a.py", "def add(a, b):\n    return a + b\n")
    _write(code_root / "mod_b.py", "def sub(a, b):\n    return a - b\n")

    junit = tmp_path / "fixture-junit.xml"
    _fixture_junit(junit)

    cold_ru = tmp_path / "reread.md"
    cold_ref = tmp_path / "source.md"
    _write(cold_ru, "cold reunderstanding text about modules and errors\n")
    _write(cold_ref, "source plan text describing modules\n")

    run_root = tmp_path / "run"
    args = dogfood.build_parser().parse_args(
        [
            "--run-root", str(run_root),
            "--grade", "G3",
            "--code-root", str(code_root),
            "--junit", str(junit),
            "--submission", str(code_root),  # non-git → files_touched deficit(정상 graceful 경로)
            "--cold-reunderstanding", str(cold_ru),
            "--cold-reference", str(cold_ref),
            # 존재하지 않는 경로 — 실 dogfood_inputs 기본값과 분리(hermetic, JW5).
            "--intent-criteria", str(tmp_path / "no-such-intent-criteria.json"),
            "--plan-todos", str(tmp_path / "no-such-plan-todos.json"),
            "--solid-contract", str(tmp_path / "no-such-solid-contract.json"),
            "--measured-at", "2026-07-04T00:00:00+00:00",
        ]
    )
    summary = dogfood.run(args)

    # pipeline 이 끝까지 돌아 verdict 를 냈다(성공 기준 — pass 여부가 아님).
    assert summary["verdict"] in {"pass", "fail"}
    assert (run_root / "quality" / "gate_meta_audit.json").exists()
    assert (run_root / "dogfood_summary.json").exists()
    assert (run_root / "results" / "junit.xml").exists()

    # quality 3종 + cold 는 실 evidence 를 emit 한다(scoring.* 대부분은 결손).
    emitted = set(summary["emitted_evidence"])
    for expected in (
        "quality.deep_module.json",
        "quality.dry.json",
        "quality.define_errors.json",
        "cold.isolation.json",
    ):
        assert expected in emitted, f"{expected} not emitted: {emitted}"

    by_id = {row["check_id"]: row for row in summary["checks"]}
    # frozen 2종은 언제나 비게이팅 ADVISORY.
    assert by_id["frozen.multiverse_width_benefit"]["classification"] == "ADVISORY"
    assert by_id["frozen.viewer_mandatory"]["classification"] == "ADVISORY"
    # dispatch 로그 부재 → cold.isolation 은 NA(§7.4 정직 고지).
    assert by_id["cold.isolation"]["classification"] == "NA"
    # gate 선언 아티팩트 부재 → 결손 유지(evidence_missing FAIL, 상상 값 주입 0).
    assert by_id["scoring.correctness"]["classification"] == "deficit"
    assert by_id["scoring.scope_fit"]["classification"] == "deficit"
    assert by_id["scoring.solid"]["classification"] == "deficit"

    # gate 단계 자체는 존재하고, 부재 사유를 정직하게 기록한다(§ _cold_producer 동형).
    gates = summary["steps"]["gates"]
    assert set(gates.keys()) == {"intent_fidelity", "scope_map", "solid_static"}
    for name in ("intent_fidelity", "scope_map", "solid_static"):
        assert gates[name]["returncode"] is None
        assert gates[name]["summary"]["emitted"] is False
        assert "파일 부재" in gates[name]["summary"]["reason"]
    assert "gate.intent_fidelity.json" not in emitted
    assert "gate.scope_map.json" not in emitted
    assert "gate.solid_static.json" not in emitted

    # 요약 JSON 이 utf-8 로 재로딩 가능(직렬화 왕복).
    reloaded = json.loads((run_root / "dogfood_summary.json").read_text(encoding="utf-8"))
    assert reloaded["counts"]["ADVISORY"] == 2


def _init_git_repo(root: Path) -> None:
    run = lambda *a: subprocess.run(
        ["git", "-C", str(root), *a],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")
    run("add", "-A")
    run("commit", "-q", "-m", "base")


def test_dogfood_gate_producers_convert_deficit_to_measured(tmp_path: Path) -> None:
    """JW5 — 참인 declarative 아티팩트(criteria/todos/contract)가 존재하면 `_gate_producers`
    가 scoring.correctness/scope_fit/solid 를 결손(evidence_missing)에서 실측 backing
    (PASS/FAIL 값)으로 전환한다(판단-게이트 스펙 §6.5). 자체 hermetic git fixture 로
    왕복시켜 실 저장소 상태와 무관하게 결정적으로 확인한다.
    """
    code_root = tmp_path / "repo"
    _write(code_root / "mod_a.py", "def add(a, b):\n    return a + b\n")
    _write(code_root / "mod_b.py", "import sqlite3\n\n\ndef use():\n    return sqlite3.connect(':memory:')\n")
    _init_git_repo(code_root)
    # working-tree 변경 — git diff --name-only HEAD 가 비지 않도록.
    _write(code_root / "mod_a.py", "def add(a, b):\n    return a + b\n\n\ndef sub(a, b):\n    return a - b\n")

    junit = tmp_path / "fixture-junit.xml"
    _fixture_junit(junit)  # t1/t2/t3 전부 passed

    criteria = tmp_path / "intent-criteria.json"
    _write(
        criteria,
        json.dumps(
            {
                "criteria": [
                    {"id": "c1", "required": True, "backing": {"kind": "file", "ref": "mod_a.py"}},
                    {"id": "c2", "required": True, "backing": {"kind": "test", "ref": "t1"}},
                ]
            }
        ),
    )
    plan_todos = tmp_path / "plan-todos.json"
    _write(
        plan_todos,
        json.dumps({"todos": [{"id": "t1", "paths": ["mod_a.py"]}]}),
    )
    solid_contract = tmp_path / "solid-contract.json"
    _write(
        solid_contract,
        json.dumps(
            {
                "modules": [
                    {
                        "module": "mod_b.py",
                        "claims": [
                            {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "requests"}}
                        ],
                    }
                ]
            }
        ),
    )

    run_root = tmp_path / "run"
    args = dogfood.build_parser().parse_args(
        [
            "--run-root", str(run_root),
            "--grade", "G3",
            "--code-root", str(code_root),
            "--junit", str(junit),
            "--submission", str(code_root),
            "--git-base", "HEAD",
            "--intent-criteria", str(criteria),
            "--plan-todos", str(plan_todos),
            "--solid-contract", str(solid_contract),
            "--measured-at", "2026-07-05T00:00:00+00:00",
        ]
    )
    summary = dogfood.run(args)

    emitted = set(summary["emitted_evidence"])
    for expected in (
        "gate.intent_fidelity.json",
        "gate.scope_map.json",
        "gate.solid_static.json",
    ):
        assert expected in emitted, f"{expected} not emitted: {emitted}"

    gates = summary["steps"]["gates"]
    assert gates["intent_fidelity"]["summary"]["value"] == 1.0
    assert gates["scope_map"]["summary"]["value"] == 1
    assert gates["solid_static"]["summary"]["dip_violation"] == 0

    by_id = {row["check_id"]: row for row in summary["checks"]}
    # 결손이 아니라 커널이 evidence 를 로드해 실제로 평가한 것(PASS 또는 실 FAIL) —
    # 어느 쪽이든 "deficit"이면 안 된다(이게 이 WP 의 핵심 전환).
    for check_id in ("scoring.correctness", "scoring.scope_fit", "scoring.solid"):
        assert by_id[check_id]["classification"] in {"PASS", "FAIL"}, by_id[check_id]
        assert by_id[check_id]["value"] is not None
