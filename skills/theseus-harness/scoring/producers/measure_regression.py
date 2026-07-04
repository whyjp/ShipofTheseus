#!/usr/bin/env python3
"""measure_regression.py — sprint.regression 증거 조립기 (설계 §7.3, WP4b).

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다. 두 score 산출물(prior/current)
의 *커널 검증된 value* 를 읽어 그 delta 라는 계산량만 emit 한다 — '회귀인가'라는 판단은
재판단하지 않고, 두 값의 차이(계산 속성)를 측정한다. delta >= -0.05 판정(하락 임계,
§7.3)은 커널이 CheckSpec `checks/sprint.regression.json` 으로 내린다.

입력은 두 JSON 파일(각각 kernel Verdict 또는 score Evidence Record)뿐 — CLI 로 raw 숫자
delta 를 주입하는 인자는 없다(손 넣기 봉쇄, WP4a 규율). score 추출은
regression_check.extract_score(스크립트가 노출한 순수 seam)가 담당한다. 둘 중 하나라도
score 를 못 뽑으면 evidence 를 안 쓴다 — 커널 법칙1(evidence_missing)이 FAIL 시킨다
(skipped==FAIL 규율, §2 원칙2: 측정 안 하면 통과가 아니라 실패).

provenance 사슬: prior_score → prior 파일, current_score → current 파일, score_delta →
producer 가 직접 기록한 scan 리포트. 세 backing 파일 모두 digest 로 pin 되어 커널 법칙3
이 디스크와 대조하므로, 상상한 delta 는 backing 없이 계약을 통과할 수 없다.

CLI:
    python measure_regression.py --prior <verdict_or_evidence.json> \\
        --current <verdict_or_evidence.json> [--score-key score_total_weighted] \\
        [--phase 10] [--project-run <name>] [--measured-at <ISO8601>] \\
        --out-dir <project_root>/evidence

저장소 self_lint C35 — 모든 open encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCORING_DIR = Path(__file__).resolve().parents[1]
if str(_SCORING_DIR) not in sys.path:
    sys.path.insert(0, str(_SCORING_DIR))
import regression_check  # noqa: E402

import _evidence_common as ec  # noqa: E402

CHECK_ID = "sprint.regression"
DEFAULT_PHASE = "10"


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 재구성 — CheckSpec cmd_pattern `^python .*measure_regression\\.py`
    과 정합."""
    parts = ["python", str(Path(__file__).resolve()),
             "--prior", args.prior, "--current", args.current]
    if args.score_key:
        parts += ["--score-key", args.score_key]
    parts += ["--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    prior_path = Path(args.prior).resolve()
    current_path = Path(args.current).resolve()
    prior_score = regression_check.extract_score(_load_json(prior_path), args.score_key)
    current_score = regression_check.extract_score(_load_json(current_path), args.score_key)

    if prior_score is None or current_score is None:
        # score 미추출 — 상상하지 않는다. evidence 를 안 쓴다(법칙1 FAIL, skipped==FAIL).
        return {
            "emitted": False,
            "reason": "prior/current score 미추출 (value/measured 스칼라 부재 또는 파일 파싱불가)",
            "prior_score": prior_score,
            "current_score": current_score,
        }

    report = regression_check.build_delta_report(prior_score, current_score)
    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    report_rel = ec.relpath(report_path, run_root)
    report_digest = ec.sha256_of_file(report_path)

    prior_rel = ec.relpath(prior_path, run_root)
    current_rel = ec.relpath(current_path, run_root)
    measured = {
        "prior_score": ec.build_measured(prior_score, "kernel_verdict_or_evidence", prior_rel),
        "current_score": ec.build_measured(current_score, "kernel_verdict_or_evidence", current_rel),
        "score_delta": ec.build_measured(report["score_delta"], "regression_delta_scan", report_rel),
    }
    artifact_digests = {
        prior_rel: ec.sha256_of_file(prior_path),
        current_rel: ec.sha256_of_file(current_path),
        report_rel: report_digest,
    }
    record = ec.assemble_record(
        check_id=CHECK_ID,
        phase=args.phase,
        project_run=project_run,
        producer_cmd=producer_cmd,
        measured=measured,
        artifact_digests=artifact_digests,
        measured_at=measured_at,
    )
    path = ec.write_evidence(out_dir, CHECK_ID, record)
    return {
        "emitted": True,
        "evidence_path": str(path),
        "prior_score": prior_score,
        "current_score": current_score,
        "score_delta": report["score_delta"],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_regression — sprint.regression 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument(
        "--prior", required=True,
        help="이전 score 산출물 (kernel Verdict 또는 score Evidence Record JSON)",
    )
    p.add_argument(
        "--current", required=True,
        help="현재 score 산출물 (kernel Verdict 또는 score Evidence Record JSON)",
    )
    p.add_argument(
        "--score-key", default=None,
        help="Verdict.value 가 아니라 Evidence measured 스칼라에서 뽑을 때의 키 이름",
    )
    p.add_argument(
        "--phase", default=DEFAULT_PHASE,
        help="이 측정이 속한 페이즈(10 sprint loop / 11 regression). 정보용 — 게이팅 무관.",
    )
    p.add_argument("--project-run", default=None, help="project_run 이름 (기본: run_root.name)")
    p.add_argument("--measured-at", default=None, help="measured_at 주입(결정성 테스트용)")
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<project_root>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run(args)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
