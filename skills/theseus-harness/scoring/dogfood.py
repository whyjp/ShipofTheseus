#!/usr/bin/env python3
"""dogfood.py — WP8: 검증 커널을 harness 자기 `scoring/` 코드에 실제로 적용하는 runner.

이 스크립트는 새 측정 로직을 만들지 않는다 — 이미 완성된 도구(pytest, producers/*,
kernel/meta_audit.py)를 *호출*해 harness 자기 코드에서 실측 값으로 verdict 를 낸다.
설계 §12 WP8("커널을 theseus-self 에 적용")의 실행체다. 상상값 주입 0(WP4a 규율 계승):
이 runner 는 어떤 measured 값도 스스로 만들지 않고, producer 가 파일을 파싱해 emit 한
Evidence 만 커널에 태운다.

정직한 범위(과장 금지 — 이 환경에서 측정 가능한 것만 측정한다):
  - 실측 backing 되는 차원: quality.deep_module / quality.dry / quality.define_errors
    (measure_deep_*/dry/define 가 scoring/ 코드를 실제로 스캔) + scoring 테스트 카운트
    (harness 자기 pytest junit) + cold.isolation 의 computed_overlap(실 파일 Jaccard) +
    (JW5) scoring.correctness/scope_fit/solid — `_gate_producers` 가 scoring/dogfood_inputs/
    의 참인 claim 선언을 `gate.intent_fidelity`/`gate.scope_map`/`gate.solid_static`
    producer 로 디스크 재검사해 emit 한 실측값(PASS 또는 실 assertion FAIL 로 관측된다 —
    clean tree 라 scope_fit 은 files_touched=0 실 FAIL 이 정직한 결과다).
  - deficit 로 남는 차원: 이 dogfood 에 artifact 가 없는 프로세스 게이트
    (coverage/e2e/dacapo/tournament/regression) — 도구·fixture 부재이지 판단 producer
    부재가 아니다(§8 비목표). evidence 부재라 커널 법칙1(evidence_missing)이 FAIL —
    '측정 안 함'이 통과가 아니라 실패다(§2 원칙2). 이 FAIL 은 결함이 아니라 정직한 결손이다.
  - NA(비게이팅): cold.isolation 은 이 저장소에 구조화된 dispatch 로그가 없어
    dispatch_log_present=0 → 적용성 false → NA(§7.4 정직 고지). scoring.coverage/
    fe_be_parity 는 단일 사이드(fe 부재)라 NA.
  - ADVISORY(비게이팅): frozen.* 동결 체크(§8) — 편익 A/B 미실증이라 종료를 막지 않는다.

실행 성공 = 'pipeline 이 끝까지 돌아 verdict 를 냈다'이지 'verdict 가 pass 다'가 아니다.
그래서 meta_audit verdict 가 FAIL 이어도 dogfood 자체는 exit 0 으로 끝난다(FAIL 은 이
환경에서 예상되는 정직한 관측 결과). verdict 는 요약 JSON·stdout 으로 보고한다.

CLI:
    python dogfood.py [--run-root DIR] [--grade G3] [--code-root DIR] \
        [--test-target DIR] [--junit PATH] [--submission DIR] [--git-base HEAD] \
        [--cold-reunderstanding PATH] [--cold-reference PATH] \
        [--intent-criteria PATH] [--plan-todos PATH] [--solid-contract PATH] \
        [--measured-at ISO8601] [--verified-at ISO8601]

저장소 self_lint C35 — 모든 open/subprocess encoding="utf-8".

JW5 갱신(2026-07-05): 판단-게이트 producer 3종(gate.intent_fidelity/gate.scope_map/
gate.solid_static, JW1~JW4 머지)을 `_gate_producers` 단계로 적용해 scoring.correctness/
scope_fit/solid 3개 deficit 을 실측 backing(PASS 또는 실 assertion FAIL)으로 전환한다
(`docs/design/2026-07-05-judgment-gate-producers-design.md` §6.5). 선언 아티팩트
(criteria/todos/contract)는 `scoring/dogfood_inputs/`에 저작되며 참인 claim 만 담는다 —
이 runner 는 여전히 어떤 measured 값도 스스로 만들지 않는다.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SCORING_DIR = Path(__file__).resolve().parent
_PRODUCERS_DIR = _SCORING_DIR / "producers"
_KERNEL_DIR = _SCORING_DIR / "kernel"
# scoring -> theseus-harness -> skills -> <repo root>.
_REPO_ROOT = _SCORING_DIR.parents[2]

# 이 저장소에 실재하는 유일한 genuine cold-read/source 쌍(v0919 self-run 의 phase-07 계획
# 재이해 vs 그 원본 계획). scoring 코드 자체의 cold re-read 는 없으므로, cold.isolation
# producer 를 실 파일로 end-to-end 돌려 NA 경로(§7.4)를 실증하기 위한 기본 입력이다.
_DEFAULT_COLD_DIR = (
    _REPO_ROOT
    / ".ShipofTheseus"
    / "theseus_self_v0919"
    / "plan"
    / "candidates"
    / "universe-1-convention-first"
)
_DEFAULT_COLD_RU = _DEFAULT_COLD_DIR / "07-cold-read.md"
_DEFAULT_COLD_REF = _DEFAULT_COLD_DIR / "06-plan.md"

_DEFAULT_RUN_BASE = _REPO_ROOT / ".ShipofTheseus" / "theseus-self-kernel-dogfood"

# JW5 — scoring 자기 코드에 대한 판단-게이트 선언 아티팩트(참인 claim 만 저작, §6.5).
_DOGFOOD_INPUTS_DIR = _SCORING_DIR / "dogfood_inputs"
_DEFAULT_INTENT_CRITERIA = _DOGFOOD_INPUTS_DIR / "intent-criteria.json"
_DEFAULT_PLAN_TODOS = _DOGFOOD_INPUTS_DIR / "plan-todos.json"
_DEFAULT_SOLID_CONTRACT = _DOGFOOD_INPUTS_DIR / "solid-contract.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    """subprocess 한 번 실행 → {cmd, returncode, stdout, stderr}. text/utf-8 고정(C35).

    producer/meta_audit 는 __file__ 로 자기 위치를 잡으므로 cwd 는 무관하지만, pytest 의
    상대 경로 해석과 git 호출을 위해 repo root 로 고정한다.
    """
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _parse_json_stdout(step: dict[str, Any]) -> dict[str, Any] | None:
    """producer 는 요약 JSON 을 stdout 으로 낸다 — 파싱 실패는 None(감사 추적용)."""
    try:
        return json.loads(step["stdout"])
    except (json.JSONDecodeError, TypeError):
        return None


# --- pytest (harness 자기 테스트 실행 → junit) ---------------------------------


def _produce_junit(
    test_target: Path, junit_path: Path, reuse_junit: Path | None, cwd: Path
) -> dict[str, Any]:
    """harness 자기 테스트를 junit 으로 실행. --junit 재사용 시 pytest 를 돌리지 않고 복사
    (테스트 안에서 pytest-in-pytest 재귀를 피하는 seam). 반환에 pytest exit 를 담아
    tests_failed 의 실측 근거가 감사 가능하게 한다."""
    junit_path.parent.mkdir(parents=True, exist_ok=True)
    if reuse_junit is not None:
        shutil.copyfile(reuse_junit, junit_path)
        return {"ran_pytest": False, "reused": str(reuse_junit), "junit": str(junit_path)}
    step = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_target),
            "-q",
            f"--junitxml={junit_path}",
        ],
        cwd,
    )
    return {
        "ran_pytest": True,
        "pytest_returncode": step["returncode"],
        "junit": str(junit_path),
        "tail": step["stdout"].splitlines()[-3:] if step["stdout"] else [],
    }


# --- producer 호출 -------------------------------------------------------------


def _quality_producers(
    code_root: Path, evidence_dir: Path, measured_at: str, cwd: Path
) -> dict[str, Any]:
    """WP5 승격군 producer 3종을 scoring/ 코드에 돌려 quality.* evidence 조립."""
    out: dict[str, Any] = {}
    specs = [
        ("deep_module", _PRODUCERS_DIR / "measure_deep_module.py"),
        ("dry", _PRODUCERS_DIR / "measure_dry_violation.py"),
        ("define_errors", _PRODUCERS_DIR / "measure_define_errors.py"),
    ]
    for name, script in specs:
        step = _run(
            [
                sys.executable,
                str(script),
                "--code-root",
                str(code_root),
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out[name] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    return out


def _gate_producers(
    submission: Path,
    code_root: Path,
    junit_path: Path,
    evidence_dir: Path,
    git_base: str,
    intent_criteria: Path,
    plan_todos: Path,
    solid_contract: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """판단-게이트 producer 3종(JW1~JW4 머지 완료)을 scoring 자기 코드에 적용해
    `intent_fidelity`/`files_mapped_to_todos`/`modules_passing_solid`+`dip_violation`
    을 실측 backing 으로 emit 한다(설계 §6.5, JW5). `_quality_producers` 뒤·
    `_submission_producer` 앞에서 호출돼야 measure_submission 의 `--from-evidence` 가
    이 세 evidence 파일을 함께 승계한다.

    선언 아티팩트(criteria/todos/contract)가 디스크에 없으면 그 producer 는 아예 부르지
    않고 사유만 기록한다 — 기존 `_cold_producer` 의 부재 처리와 동형(정직한 결손 경로
    보존). 존재하면 producer 를 실제로 돌려 리포트로 자기 확인된 값을 그대로 emit 한다
    (이 runner 는 값을 만들지 않는다 — WP8 규율 계승)."""
    out: dict[str, Any] = {}

    if intent_criteria.is_file():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_intent_fidelity.py"),
                "--criteria",
                str(intent_criteria),
                "--submission",
                str(submission),
                "--test-junit",
                str(junit_path),
                "--git-base",
                git_base,
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["intent_fidelity"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["intent_fidelity"] = {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "intent-criteria 파일 부재 — measure_intent_fidelity 미실행",
            },
        }

    if plan_todos.is_file():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_scope_map.py"),
                "--plan-todos",
                str(plan_todos),
                "--submission",
                str(submission),
                "--git-base",
                git_base,
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["scope_map"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["scope_map"] = {
            "returncode": None,
            "summary": {"emitted": False, "reason": "plan-todos 파일 부재 — measure_scope_map 미실행"},
        }

    if solid_contract.is_file():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_solid_static.py"),
                "--code-root",
                str(code_root),
                "--solid-contract",
                str(solid_contract),
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["solid_static"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["solid_static"] = {
            "returncode": None,
            "summary": {"emitted": False, "reason": "solid-contract 파일 부재 — measure_solid_static 미실행"},
        }

    return out


def _submission_producer(
    submission: Path,
    junit_path: Path,
    evidence_dir: Path,
    git_base: str,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """measure_submission 으로 scoring.* evidence 조립. --from-evidence 로 quality evidence
    를 가리켜 modules_total 브릿지를 승계(나머지 분석 파생 값은 backing 부재 → 결손)."""
    step = _run(
        [
            sys.executable,
            str(_PRODUCERS_DIR / "measure_submission.py"),
            "--submission",
            str(submission),
            "--test-junit",
            str(junit_path),
            "--from-evidence",
            str(evidence_dir),
            "--git-base",
            git_base,
            "--measured-at",
            measured_at,
            "--out-dir",
            str(evidence_dir),
        ],
        cwd,
    )
    return {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}


def _cold_producer(
    reunderstanding: Path,
    reference: Path,
    evidence_dir: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """measure_cold_isolation 으로 cold.isolation evidence 조립. dispatch 로그를 주지
    않으므로 dispatch_log_present=0 → meta_audit 가 NA(§7.4). 두 텍스트가 없으면 producer
    가 emit:false 를 내고 evidence 부재 → 커널 법칙1 FAIL(정직한 결손)."""
    if not (reunderstanding.exists() and reference.exists()):
        return {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "cold-read/reference 파일 부재 — cold.isolation producer 미실행",
            },
        }
    step = _run(
        [
            sys.executable,
            str(_PRODUCERS_DIR / "measure_cold_isolation.py"),
            "--reunderstanding",
            str(reunderstanding),
            "--reference",
            str(reference),
            "--measured-at",
            measured_at,
            "--out-dir",
            str(evidence_dir),
        ],
        cwd,
    )
    return {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}


# --- meta_audit + 분류 ---------------------------------------------------------


def _meta_audit(
    run_root: Path, grade: str, verified_at: str, cwd: Path
) -> dict[str, Any]:
    """생성형 meta_audit 를 레지스트리 열거로 실행 → run verdict + gate_meta_audit.json.
    보고는 stdout JSON 을 신뢰하되, 파싱 실패 시 gate 파일을 fallback 으로 읽는다."""
    gate_path = run_root / "quality" / "gate_meta_audit.json"
    step = _run(
        [
            sys.executable,
            str(_KERNEL_DIR / "meta_audit.py"),
            "--project-root",
            str(run_root),
            "--grade",
            grade,
            "--output",
            str(gate_path),
            "--verified-at",
            verified_at,
        ],
        cwd,
    )
    report = _parse_json_stdout(step)
    if report is None and gate_path.exists():
        report = json.loads(gate_path.read_text(encoding="utf-8"))
    return {"returncode": step["returncode"], "gate_path": str(gate_path), "report": report}


def _is_deficit(reasons: list[str]) -> bool:
    """FAIL 사유가 evidence 부재(=측정 자체가 없음)인지 — 실 assertion 실패와 구분."""
    return any("evidence_missing" in str(r) for r in reasons)


def classify(report: dict[str, Any]) -> dict[str, Any]:
    """meta_audit 결과를 PASS/FAIL/NA/ADVISORY/deficit 로 분류하고 실측 값을 붙인다.

    deficit 는 커널이 아는 상태가 아니라(커널은 PASS/FAIL 만) 보고 레이어의 세분류다 —
    'FAIL 이지만 사유가 evidence_missing'을 '실 assertion FAIL'과 나눠, 몇 개가 실측
    backing 됐고 몇 개가 결손인지 정직하게 세기 위함이다.
    """
    rows: list[dict[str, Any]] = []
    counts = {"PASS": 0, "FAIL": 0, "NA": 0, "ADVISORY": 0, "deficit": 0}
    for check_id in report.get("active_checks", []):
        outcome = report.get("results", {}).get(check_id, {})
        result = outcome.get("result")
        reasons = outcome.get("reasons", [])
        display = result
        if result == "FAIL" and _is_deficit(reasons):
            display = "deficit"
        rows.append(
            {
                "check_id": check_id,
                "classification": display,
                "value": outcome.get("value"),
                "kernel_result": outcome.get("kernel_result"),
                "reasons": reasons,
            }
        )
        counts[display] = counts.get(display, 0) + 1
    # 실측 backing = 커널이 evidence 를 실제로 로드해 assertion/적용성까지 평가한 체크
    # (PASS + 실 FAIL + evidence 로 입증된 NA). deficit/advisory 는 evidence 부재.
    counts["measured_backed"] = counts["PASS"] + counts["FAIL"] + counts["NA"]
    return {"rows": rows, "counts": counts, "verdict": report.get("verdict")}


# --- 오케스트레이션 ------------------------------------------------------------


def run(args: argparse.Namespace) -> dict[str, Any]:
    measured_at = args.measured_at or _now_iso()
    verified_at = args.verified_at or measured_at

    run_root = Path(args.run_root).resolve()
    evidence_dir = run_root / "evidence"
    junit_path = run_root / "results" / "junit.xml"
    for d in (run_root, evidence_dir, run_root / "results", run_root / "quality"):
        d.mkdir(parents=True, exist_ok=True)

    cwd = _REPO_ROOT
    code_root = Path(args.code_root).resolve()
    submission = Path(args.submission).resolve()
    reuse_junit = Path(args.junit).resolve() if args.junit else None

    steps: dict[str, Any] = {}
    steps["junit"] = _produce_junit(
        Path(args.test_target).resolve(), junit_path, reuse_junit, cwd
    )
    # quality 를 먼저 조립해야 measure_submission --from-evidence 가 modules_total 브릿지를
    # 승계할 수 있다(순서 의존).
    steps["quality"] = _quality_producers(code_root, evidence_dir, measured_at, cwd)
    # gate producer 3종(JW1~JW4) — quality 뒤·submission 앞이어야 --from-evidence 가
    # gate.intent_fidelity/gate.scope_map/gate.solid_static 를 함께 승계한다(§4.1 사전순
    # 승자 규칙과 무관하게 파일이 먼저 디스크에 있어야 색인된다).
    steps["gates"] = _gate_producers(
        submission=submission,
        code_root=code_root,
        junit_path=junit_path,
        evidence_dir=evidence_dir,
        git_base=args.git_base,
        intent_criteria=Path(args.intent_criteria).resolve(),
        plan_todos=Path(args.plan_todos).resolve(),
        solid_contract=Path(args.solid_contract).resolve(),
        measured_at=measured_at,
        cwd=cwd,
    )
    steps["submission"] = _submission_producer(
        submission, junit_path, evidence_dir, args.git_base, measured_at, cwd
    )
    steps["cold"] = _cold_producer(
        Path(args.cold_reunderstanding).resolve(),
        Path(args.cold_reference).resolve(),
        evidence_dir,
        measured_at,
        cwd,
    )
    audit = _meta_audit(run_root, args.grade, verified_at, cwd)
    steps["meta_audit"] = {"returncode": audit["returncode"], "gate_path": audit["gate_path"]}

    report = audit["report"] or {}
    classification = classify(report)

    summary = {
        "dogfood_schema_version": "1.0",
        "run_root": str(run_root),
        "grade": args.grade,
        "measured_at": measured_at,
        "verified_at": verified_at,
        "code_root": str(code_root),
        "verdict": classification["verdict"],
        "counts": classification["counts"],
        "checks": classification["rows"],
        "emitted_evidence": sorted(p.name for p in evidence_dir.glob("*.json")),
        "steps": steps,
    }
    (run_root / "dogfood_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def _print_human(summary: dict[str, Any]) -> None:
    c = summary["counts"]
    print(f"dogfood verdict: {summary['verdict']}  (grade {summary['grade']})")
    print(
        "  PASS={PASS} FAIL={FAIL} NA={NA} ADVISORY={ADVISORY} "
        "(deficit-of-FAIL={deficit}, measured_backed={measured_backed})".format(**c)
    )
    for row in summary["checks"]:
        val = "" if row["value"] is None else f" value={row['value']}"
        extra = f" kernel={row['kernel_result']}" if row.get("kernel_result") else ""
        print(f"  [{row['classification']:>8}] {row['check_id']}{val}{extra}")
    print(f"  run_root: {summary['run_root']}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="dogfood — 검증 커널을 harness 자기 scoring/ 코드에 적용(WP8, §12)"
    )
    p.add_argument(
        "--run-root",
        default=str(_DEFAULT_RUN_BASE / "run"),
        help="run 산출물 루트(evidence/, results/, quality/). 기본: .ShipofTheseus/theseus-self-kernel-dogfood/run",
    )
    p.add_argument("--grade", default="G3", help="감사 그레이드 (기본 G3)")
    p.add_argument(
        "--code-root",
        default=str(_SCORING_DIR),
        help="quality.* 스캔 + submission 대상 코드 루트 (기본: 이 scoring/ 디렉터리)",
    )
    p.add_argument(
        "--test-target",
        default=str(_SCORING_DIR),
        help="pytest 대상 (기본: 이 scoring/ 디렉터리)",
    )
    p.add_argument(
        "--junit",
        default=None,
        help="기존 junit XML 재사용(pytest 미실행). 테스트가 pytest-in-pytest 재귀를 피하는 seam.",
    )
    p.add_argument(
        "--submission",
        default=str(_REPO_ROOT),
        help="git diff 대상 제출물 디렉터리 (기본: repo root)",
    )
    p.add_argument("--git-base", default="HEAD", help="git diff base ref (기본 HEAD)")
    p.add_argument(
        "--cold-reunderstanding",
        default=str(_DEFAULT_COLD_RU),
        help="cold.isolation 재이해 텍스트 (기본: v0919 universe-1 07-cold-read.md)",
    )
    p.add_argument(
        "--cold-reference",
        default=str(_DEFAULT_COLD_REF),
        help="cold.isolation 참조 텍스트 (기본: v0919 universe-1 06-plan.md)",
    )
    p.add_argument(
        "--intent-criteria",
        default=str(_DEFAULT_INTENT_CRITERIA),
        help="gate.intent_fidelity 선언 아티팩트 (기본: scoring/dogfood_inputs/intent-criteria.json)",
    )
    p.add_argument(
        "--plan-todos",
        default=str(_DEFAULT_PLAN_TODOS),
        help="gate.scope_map 선언 아티팩트 (기본: scoring/dogfood_inputs/plan-todos.json)",
    )
    p.add_argument(
        "--solid-contract",
        default=str(_DEFAULT_SOLID_CONTRACT),
        help="gate.solid_static 선언 아티팩트 (기본: scoring/dogfood_inputs/solid-contract.json)",
    )
    p.add_argument("--measured-at", default=None, help="모든 producer 에 주입할 measured_at(결정성)")
    p.add_argument("--verified-at", default=None, help="meta_audit 에 주입할 verified_at(기본: measured_at)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run(args)
    _print_human(summary)
    # 실행 성공 = pipeline 이 verdict 를 냈다. verdict 자체(FAIL 가능)는 정직한 관측 결과라
    # dogfood exit code 로 승격하지 않는다(위 docstring). verdict 미산출만 비정상(exit 1).
    return 0 if summary["verdict"] is not None else 1


if __name__ == "__main__":
    sys.exit(main())
