#!/usr/bin/env python3
"""measure_dry_violation.py — quality.dry 증거 조립기 (설계 §8 promote, WP5).

dry_violation_count.py 의 `build_report()`(WP5 리팩터로 main() 에서 추출된 순수 계산
함수 — CLI 동작은 그대로 보존)를 호출해 total_ngrams/violation_count/
scanned_line_count/n_gram 을 얻고, raw 값 + provenance(artifact_path=이 실행이 직접
기록한 raw scan 리포트 json)만 Evidence Record 로 emit 한다. violation ratio ≤0.05
판정(Pragmatic Programmer Tip 11)은 커널이 CheckSpec `checks/quality.dry.json` 으로
내린다 — 이 스크립트는 verdict 를 내지 않는다.

소규모 코드베이스(scanned_line_count < n_gram+10) 처리: 원본 스크립트는 이 경우를
'skip=pass'(exit 0, pass:true)로 처리했다 — 측정을 안 했는데 통과 취급하는 것은 설계
원칙2("skipped==pass 를 skipped==FAIL 로 뒤집는다")가 경계하는 패턴이다. 그러나 이
경우는 '측정 실패'가 아니라 '표본이 n-gram 추출에 못 미친다는 실제 관측 사실'이므로,
CheckSpec 의 `applicability: "scanned_line_count >= n_gram + 10"` 으로 옮겼다 —
meta_audit 가 이를 evidence 로 입증된 NA(비게이팅)로 처리한다(침묵 pass 아님, 값으로
입증된 NA). evidence 는 이 경우에도 정상 emit 된다(scanned_line_count/n_gram 은 여전히
실측값).

CLI:
    python measure_dry_violation.py --code-root <dir> [--n-gram 8] [--min-repeat 2] \\
        [--max-violation-ratio 0.05] [--project-run <name>] [--measured-at <ISO8601>] \\
        --out-dir <project_root>/evidence

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
import dry_violation_count  # noqa: E402

import _evidence_common as ec  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "quality.dry"
DEFAULT_PHASE = "08"


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    return " ".join([
        "python", str(Path(__file__).resolve()),
        "--code-root", args.code_root,
        "--n-gram", str(args.n_gram),
        "--min-repeat", str(args.min_repeat),
        "--max-violation-ratio", str(args.max_violation_ratio),
        "--out-dir", args.out_dir,
    ])


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    code_root = Path(args.code_root).resolve()
    report = dry_violation_count.build_report(
        code_root,
        n_gram=args.n_gram,
        min_repeat=args.min_repeat,
        max_violation_ratio=args.max_violation_ratio,
    )

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    rel = ec.relpath(report_path, run_root)
    digest = ec.sha256_of_file(report_path)

    module_count = report.get("module_count", 0)
    total_ngrams = report.get("total_ngrams", 0)
    violation_count = report.get("violation_count", 0)
    scanned_line_count = report.get("scanned_line_count", 0)
    measured = {
        # applicability 가 "module_count==0 or scanned_line_count>=n_gram+10" 이라
        # module_count 없이는 0-모듈 코드베이스가 NA(비게이팅)로 새 버린다(원본 스크립트는
        # 이 경우 exit 1) — 이 값이 그 구멍을 막는다(no-work guard, applicability 안이 아닌
        # 강제 통과 경로로).
        "module_count": ec.build_measured(module_count, "dry_violation_report", rel),
        "total_ngrams": ec.build_measured(total_ngrams, "dry_violation_report", rel),
        "violation_count": ec.build_measured(violation_count, "dry_violation_report", rel),
        "scanned_line_count": ec.build_measured(scanned_line_count, "dry_violation_report", rel),
        # applicability("module_count==0 or scanned_line_count>=n_gram+10")가 참조하는
        # 설정값 — 실행 파라미터도 이 실행의 관측 가능한 사실이라 provenance 붙여 둔다.
        "n_gram": ec.build_measured(args.n_gram, "dry_violation_report", rel),
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
        "total_ngrams": total_ngrams,
        "violation_count": violation_count,
        "scanned_line_count": scanned_line_count,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_dry_violation — quality.dry 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument("--code-root", required=True, help="분석 대상 코드 루트 디렉터리")
    p.add_argument("--n-gram", type=int, default=8)
    p.add_argument("--min-repeat", type=int, default=2)
    p.add_argument("--max-violation-ratio", type=float, default=0.05)
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
    p.add_argument("--project-run", default=None)
    p.add_argument("--measured-at", default=None)
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<project_root>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)
    summary = run(args)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
