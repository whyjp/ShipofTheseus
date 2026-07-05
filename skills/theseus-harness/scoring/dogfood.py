#!/usr/bin/env python3
"""dogfood.py — 검증 커널을 harness 자기 `scoring/` 코드에 적용하는 얇은 wrapper.

이 스크립트는 오케스트레이션 로직을 **소유하지 않는다** — B1(§2.5)에서 junit→quality→
gates→submission→cold→meta_audit 오케스트레이션은 전부 `run_gate.py` 로 이동했다. dogfood
는 그 라이브러리 API(`run_gate.run_gate`)를 *dogfood 특수성* 만 입혀 부르는 wrapper 다:
  (a) 기본값 — scoring/ 자기 디렉터리·dogfood_inputs/·v0919 cold 쌍,
  (b) exit-0-on-FAIL 의미론(실행 성공 = 'verdict 를 냈다', pass 여부 아님),
  (c) plan/sprint 단계 비활성 + gate_history 아카이브 비활성(dogfood 특수),
  (d) PASS/FAIL/NA/ADVISORY/deficit 세분류 보고 + dogfood_summary.json.
verdict 자체는 여전히 커널(meta_audit)이 소유하고, run_gate 가 그것을 오케스트레이션한다 —
dogfood 는 값을 만들지 않는다(WP4a/WP8 규율 계승).

정직한 범위(과장 금지 — 이 환경에서 측정 가능한 것만 측정한다):
  - 실측 backing 되는 차원: quality.deep_module / quality.dry / quality.define_errors +
    scoring 테스트 카운트 + cold.isolation 의 computed_overlap + (JW5) scoring.correctness/
    scope_fit/solid — 참인 claim 선언(scoring/dogfood_inputs/)을 producer 가 디스크
    재검사해 emit 한 실측값(PASS 또는 실 assertion FAIL 로 관측).
  - deficit 로 남는 차원: artifact 가 없는 프로세스 게이트(coverage/e2e/dacapo/tournament/
    regression) — evidence 부재라 커널 법칙1(evidence_missing) FAIL. '측정 안 함'이 통과가
    아니라 실패다(§2 원칙2). 이 FAIL 은 결함이 아니라 정직한 결손이다.
  - NA(비게이팅): cold.isolation(dispatch_log_present=0) / scoring.coverage/fe_be_parity
    (단일 사이드).
  - ADVISORY(비게이팅): frozen.* 동결 체크(§8) — 편익 A/B 미실증이라 종료를 막지 않는다.

실행 성공 = 'pipeline 이 끝까지 돌아 verdict 를 냈다'이지 'verdict 가 pass 다'가 아니다.
그래서 meta_audit verdict 가 FAIL 이어도 dogfood 자체는 exit 0 으로 끝난다(run_gate 의
exit=verdict 의미론과 다른 dogfood 특수성 — 이 환경에서 FAIL 은 예상되는 정직한 관측).

CLI:
    python dogfood.py [--run-root DIR] [--grade G3] [--code-root DIR] \
        [--test-target DIR] [--junit PATH] [--submission DIR] [--git-base HEAD] \
        [--cold-reunderstanding PATH] [--cold-reference PATH] \
        [--intent-criteria PATH] [--plan-todos PATH] [--solid-contract PATH] \
        [--measured-at ISO8601] [--verified-at ISO8601]

저장소 self_lint C35 — 모든 open/subprocess encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import run_gate

_SCORING_DIR = Path(__file__).resolve().parent
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


# --- 분류(dogfood 특수 보고 레이어) --------------------------------------------


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


# --- 오케스트레이션 위임(run_gate 흡수, §2.5) ---------------------------------


def run(args: argparse.Namespace) -> dict[str, Any]:
    """dogfood 기본값·특수성으로 run_gate 오케스트레이션을 호출하고 dogfood 요약을 낸다.

    오케스트레이션(junit/quality/gates/submission/cold/meta_audit) 자체는 run_gate 가
    소유한다 — 여기엔 남은 오케스트레이션 코드가 없다(DRY, 순감 정신). dogfood 는 자기
    기본값을 전부 명시로 넘겨 run_gate 의 관례 경로 유도를 우회하고, plan/sprint/archive 를
    비활성화한다(dogfood 특수성). meta_audit 는 phase_upto 없이(전 체크 게이팅) 호출되므로
    verdict/gate_meta_audit.json 은 흡수 전과 값·바이트가 동일하다(behavior-preserving).
    """
    result = run_gate.run_gate(
        project_root=args.run_root,
        grade=args.grade,
        submission=args.submission,
        test_target=args.test_target,
        code_root=args.code_root,
        git_base=args.git_base,
        junit=args.junit,
        intent_criteria=args.intent_criteria,
        plan_todos=args.plan_todos,
        solid_contract=args.solid_contract,
        cold_reunderstanding=args.cold_reunderstanding,
        cold_reference=args.cold_reference,
        phase_upto=None,          # dogfood 는 전 체크 게이팅(흡수 전 동작 보존)
        enable_plan=False,        # dogfood 특수성 — plan/sprint 미호출
        enable_sprint=False,
        enable_archive=False,     # dogfood run dir 에 gate_history 누적 없음
        measured_at=args.measured_at,
        verified_at=args.verified_at,
    )

    report = result["report"] or {}
    classification = classify(report)

    summary = {
        "dogfood_schema_version": "1.0",
        "run_root": result["run_root"],
        "grade": result["grade"],
        "measured_at": result["measured_at"],
        "verified_at": result["verified_at"],
        "code_root": result["code_root"],
        "verdict": classification["verdict"],
        "counts": classification["counts"],
        "checks": classification["rows"],
        "emitted_evidence": result["emitted_evidence"],
        "steps": result["steps"],
    }
    (Path(result["run_root"]) / "dogfood_summary.json").write_text(
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
        description="dogfood — 검증 커널을 harness 자기 scoring/ 코드에 적용(run_gate wrapper, §2.5)"
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
    run_gate.force_utf8_stdio()  # cp949 등 로캘 콘솔에서 분류표 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)
    summary = run(args)
    _print_human(summary)
    # 실행 성공 = pipeline 이 verdict 를 냈다. verdict 자체(FAIL 가능)는 정직한 관측 결과라
    # dogfood exit code 로 승격하지 않는다(위 docstring). verdict 미산출만 비정상(exit 1).
    return 0 if summary["verdict"] is not None else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
