#!/usr/bin/env python3
"""measure_dacapo_threshold.py — plan.dacapo_threshold 증거 조립기 (설계 §8 promote, WP5).

dacapo_threshold.py(수정하지 않는다 — 그대로 재사용)의 `extract_winner_score()` 를
호출해 tournament-md 의 winner_score/winner_max 를 파싱하고, 그 raw 값 + provenance
(artifact_path=tournament_md 자신)만 Evidence Record 로 emit 한다. ratio 판정(≥0.999,
HARD-RULE 9.qq)은 커널이 CheckSpec `checks/plan.dacapo_threshold.json` 으로 내린다 —
이 스크립트는 verdict 를 내지 않는다(`evaluate()` 가 아니라 `extract_winner_score()` 만
쓰는 이유 — evaluate() 는 verdict/next_round_required 까지 계산해 반환한다).

dacapo_threshold.py 자체는 수정하지 않는다 — `extract_winner_score()` 가 이미 재사용
가능한 순수 함수라 리팩터가 불필요하고, 기존 test_dacapo_threshold.py·
runtime_guard_chain.py(phase 06/08 exit hook 이 이 스크립트를 subprocess 로 호출)의
CLI/exit-code 계약을 그대로 보존한다.

`--score-text` 수동 override 는 이 producer 에 의도적으로 없다 — backing artifact(실제
tournament 파일)가 없는 값은 자기 신고와 다를 바 없어(§3 self_reported 금지) 구조적으로
배제한다. tournament-md 에서 winner score/max 추출이 실패하면(frontmatter/표/fallback
모두 미매칭) evidence 를 emit 하지 않는다 — 커널 법칙1(evidence_missing)이 FAIL 시킨다.

CLI:
    python measure_dacapo_threshold.py --tournament-md <path> [--phase 06] \\
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
import dacapo_threshold  # noqa: E402

import _evidence_common as ec  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "plan.dacapo_threshold"
DEFAULT_PHASE = "06"


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 문자열 재구성 — CheckSpec cmd_pattern
    `^python .*measure_dacapo_threshold\\.py` 과 정합하도록."""
    return " ".join([
        "python", str(Path(__file__).resolve()),
        "--tournament-md", args.tournament_md,
        "--phase", args.phase,
        "--out-dir", args.out_dir,
    ])


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    tournament_md = Path(args.tournament_md).resolve()
    text = tournament_md.read_text(encoding="utf-8", errors="ignore")
    result = dacapo_threshold.extract_winner_score(text)
    if result is None:
        # 추출 실패 — 상상하지 않는다. evidence 를 아예 안 쓴다(법칙1 FAIL 이 정확히 잡는다).
        return {
            "emitted": False,
            "reason": (
                "winner score/max extraction failed "
                "(frontmatter / total-row / fallback pattern 모두 미매칭)"
            ),
        }
    winner_score, winner_max, source = result

    rel = ec.relpath(tournament_md, run_root)
    digest = ec.sha256_of_file(tournament_md)
    measured = {
        "winner_score": ec.build_measured(winner_score, f"tournament_md:{source}", rel),
        "winner_max": ec.build_measured(winner_max, f"tournament_md:{source}", rel),
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
        "winner_score": winner_score,
        "winner_max": winner_max,
        "extraction_source": source,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_dacapo_threshold — plan.dacapo_threshold 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument(
        "--tournament-md", required=True,
        help="tournament-NN.md 또는 tournament-impl-NN.md 경로",
    )
    p.add_argument(
        "--phase", default=DEFAULT_PHASE,
        help="이 측정이 속한 페이즈(06 plan tournament / 08 impl tournament, 기본 06). "
             "정보용 — 커널 게이팅에는 쓰이지 않는다.",
    )
    p.add_argument("--project-run", default=None, help="project_run 이름 (기본: run_root.name)")
    p.add_argument("--measured-at", default=None, help="measured_at 주입(결정성 테스트용)")
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
