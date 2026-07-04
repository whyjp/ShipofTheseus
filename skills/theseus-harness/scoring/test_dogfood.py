#!/usr/bin/env python3
"""test_dogfood.py — WP8 dogfood runner 검증.

두 층으로 나눈다:
  1. classify() 순수 함수 — 합성 meta_audit 리포트로 PASS/FAIL/NA/ADVISORY/deficit
     5분류와 measured_backed 카운트를 검증(외부 실행 없이 결정적).
  2. 미니 end-to-end — 픽스처 코드/junit/cold 쌍으로 파이프라인을 끝까지 돌려
     run dir 구조·verdict 산출·evidence emit 을 검증. --junit 재사용으로
     pytest-in-pytest 재귀를 피한다(dogfood 의 seam).

저장소 self_lint C35 — 모든 open encoding="utf-8".
"""
from __future__ import annotations

import json
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
    """픽스처로 전체 파이프라인 실행 → run dir + verdict + evidence + gate 산출 검증."""
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
    # 결손 차원은 evidence_missing FAIL 로 deficit 분류(상상 값 주입 0).
    assert by_id["scoring.correctness"]["classification"] == "deficit"

    # 요약 JSON 이 utf-8 로 재로딩 가능(직렬화 왕복).
    reloaded = json.loads((run_root / "dogfood_summary.json").read_text(encoding="utf-8"))
    assert reloaded["counts"]["ADVISORY"] == 2
