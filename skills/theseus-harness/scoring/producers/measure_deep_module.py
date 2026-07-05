#!/usr/bin/env python3
"""measure_deep_module.py — quality.deep_module 증거 조립기 (설계 §8 promote, WP5).

deep_module_metric.py 의 `build_report()`(WP5 리팩터로 main() 에서 추출된 순수 계산
함수 — CLI 동작은 그대로 보존)를 호출해 module_count/max_shallow_ratio 를 얻고, 그
raw 값 + provenance(artifact_path=이 실행이 직접 기록한 raw scan 리포트 json)만
Evidence Record 로 emit 한다. 얕은 모듈 판정(비율 ≤0.4, Ousterhout Ch.4)은 커널이
CheckSpec `checks/quality.deep_module.json` 으로 내린다 — 이 스크립트는 verdict 를
내지 않는다.

deep_module → scoring.solid backing 브릿지(설계 §12 WP5 지시 사항, 정직 고지):
  - `module_count` 를 measure_submission.py 의 `--from-evidence` 가 읽는
    `modules_total` 키 shape 로도 병기한다 — '모듈 개수'는 deep_module_metric 이
    실제로 세는 것과 scoring.solid 가 기대하는 것이 같은 개념이라 겹침이 정직하다.
  - `modules_passing_solid` 와 `dip_violation` 은 **의도적으로 emit 하지 않는다**.
    deep-module 비율(정보 은닉 깊이 — public interface 줄 / 내부 functional 줄)은
    SOLID 5원칙(SRP/OCP/LSP/ISP/DIP) 준수와 다른 차원이다. '비율이 낮은(얕지 않은)
    모듈 수'를 'SOLID 통과 모듈 수'로 세는 것은 억지 매핑이라 하지 않는다.
    DIP(의존성 역전 — 고수준 모듈이 구체 구현이 아니라 추상에 의존하는가)는 이
    스크립트가 애초에 측정하는 개념이 아니다(의존 방향/주입 여부를 전혀 보지
    않는다) — 그래서 더더욱 승계 불가능하다. 이 두 값이 없으면 measure_submission
    은 여전히 그 키들을 결손 처리하고, scoring.solid 는 이 브릿지만으로는
    unblock 되지 않는다. 이것은 결함이 아니라 정직한 결손이다(§12 요구).

CLI:
    python measure_deep_module.py --code-root <dir> [--max-ratio 0.4] [--min-modules 2] \\
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
import deep_module_metric  # noqa: E402

import _evidence_common as ec  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "quality.deep_module"
DEFAULT_PHASE = "08"

# scoring.solid backing 브릿지가 넘겨줄 수 있는 키 — module_count 뿐(위 docstring).
SOLID_BRIDGE_DEFICITS = ("modules_passing_solid", "dip_violation")


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    return " ".join([
        "python", str(Path(__file__).resolve()),
        "--code-root", args.code_root,
        "--max-ratio", str(args.max_ratio),
        "--min-modules", str(args.min_modules),
        "--out-dir", args.out_dir,
    ])


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    code_root = Path(args.code_root).resolve()
    report = deep_module_metric.build_report(
        code_root, max_ratio=args.max_ratio, min_modules=args.min_modules,
    )

    # raw scan 리포트(per_module 상세 포함)를 backing artifact 로 기록.
    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    rel = ec.relpath(report_path, run_root)
    digest = ec.sha256_of_file(report_path)

    max_shallow_ratio = report.get("max_shallow_ratio", 0.0)
    measured = {
        "module_count": ec.build_measured(report["module_count"], "deep_module_report", rel),
        "max_shallow_ratio": ec.build_measured(max_shallow_ratio, "deep_module_report", rel),
        # 브릿지 — modules_total shape 로 병기(모듈 카운트는 정직하게 겹치는 개념).
        # modules_passing_solid/dip_violation 은 의도적 결손(위 docstring) — emit 안 함.
        "modules_total": ec.build_measured(report["module_count"], "deep_module_report", rel),
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
        "module_count": report["module_count"],
        "max_shallow_ratio": max_shallow_ratio,
        "solid_bridge_provided": ["modules_total"],
        "solid_bridge_deficits": list(SOLID_BRIDGE_DEFICITS),
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_deep_module — quality.deep_module 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument("--code-root", required=True, help="분석 대상 코드 루트 디렉터리")
    p.add_argument("--max-ratio", type=float, default=0.4)
    p.add_argument("--min-modules", type=int, default=2)
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
