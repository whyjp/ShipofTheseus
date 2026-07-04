#!/usr/bin/env python3
"""measure_define_errors.py — quality.define_errors 증거 조립기 (설계 §8 promote, WP5).

define_errors_check.py 의 `build_report()`(WP5 리팩터로 main() 에서 추출된 순수 계산
함수 — CLI 동작은 그대로 보존)를 호출해 raised_type_count/unhandled_type_count/
bare_except_vacuous_flag 를 얻고, raw 값 + provenance(artifact_path=이 실행이 직접
기록한 raw scan 리포트 json)만 Evidence Record 로 emit 한다. handle-누락/vacuous
bare-except 판정(Ousterhout Ch.10, Effective Python Item 87)은 커널이 CheckSpec
`checks/quality.define_errors.json` 으로 내린다 — 이 스크립트는 verdict 를 내지 않는다.

CLI:
    python measure_define_errors.py --code-root <dir> [--min-exception-types 1] \\
        [--project-run <name>] [--measured-at <ISO8601>] --out-dir <project_root>/evidence

저장소 self_lint C35 — 모든 open/subprocess encoding="utf-8".
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
import define_errors_check  # noqa: E402

import _evidence_common as ec  # noqa: E402

CHECK_ID = "quality.define_errors"
DEFAULT_PHASE = "08"


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    return " ".join([
        "python", str(Path(__file__).resolve()),
        "--code-root", args.code_root,
        "--min-exception-types", str(args.min_exception_types),
        "--out-dir", args.out_dir,
    ])


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    code_root = Path(args.code_root).resolve()
    report = define_errors_check.build_report(
        code_root, min_exception_types=args.min_exception_types,
    )

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    rel = ec.relpath(report_path, run_root)
    digest = ec.sha256_of_file(report_path)

    module_count = report["module_count"]
    raised_type_count = report["raised_type_count"]
    unhandled_type_count = report["unhandled_type_count"]
    bare_except_vacuous_flag = report["bare_except_vacuous_flag"]
    measured = {
        # module_count 없이는 0-모듈 코드베이스가 unhandled_type_count==0 을 vacuous 하게
        # 만족해 buffer PASS 로 새는 구멍이 생긴다(원본 스크립트는 이 경우 exit 1) —
        # CheckSpec 의 no-work guard 가 이 값을 assert 해서 그 구멍을 막는다.
        "module_count": ec.build_measured(module_count, "define_errors_report", rel),
        "raised_type_count": ec.build_measured(raised_type_count, "define_errors_report", rel),
        "unhandled_type_count": ec.build_measured(unhandled_type_count, "define_errors_report", rel),
        "bare_except_vacuous_flag": ec.build_measured(bare_except_vacuous_flag, "define_errors_report", rel),
    }
    record = ec.assemble_record(
        check_id=CHECK_ID,
        phase=args.phase,
        project_run=project_run,
        producer_cmd=producer_cmd,
        measured=measured,
        artifact_digests={rel: digest},
        measured_at=measured_at,
    )
    path = ec.write_evidence(out_dir, CHECK_ID, record)
    return {
        "emitted": True,
        "evidence_path": str(path),
        "module_count": module_count,
        "raised_type_count": raised_type_count,
        "unhandled_type_count": unhandled_type_count,
        "bare_except_vacuous_flag": bare_except_vacuous_flag,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_define_errors — quality.define_errors 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument("--code-root", required=True, help="분석 대상 코드 루트 디렉터리")
    p.add_argument("--min-exception-types", type=int, default=1)
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
    p.add_argument("--project-run", default=None)
    p.add_argument("--measured-at", default=None)
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
