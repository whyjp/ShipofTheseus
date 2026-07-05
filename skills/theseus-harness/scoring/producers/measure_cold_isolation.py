#!/usr/bin/env python3
"""measure_cold_isolation.py — cold.isolation 증거 조립기 (설계 §7.4, WP4b).

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다. 콜드 재이해 산출물과 참조
텍스트(원문/하류 artifact) 사이의 *계산된 어휘 overlap*, 그리고 (있으면) dispatch 로그의
*실제* prior_context_token_count·허용 파일 수만 emit 한다 — '격리됐나 / 오염됐나'라는
판단은 재판단하지 않고, 두 텍스트의 token 집합 overlap(계산량)과 로그의 관측값만 측정한다.
overlap <= 임계, prior_context_token_count == 0 판정은 커널이 CheckSpec
`checks/cold.isolation.json` 으로 내린다.

overlap 은 Jaccard token 집합 비율 — `\\w+`(유니코드) 토큰이라 영어 sentinel 정규식이
한국어 산출물을 놓치던 회귀(설계 P3)를 없앤 *언어 무관* 값 검사다.

정직 고지(설계 §7.4 반영): 이 저장소의 콜드 세션은 LLM 주도라 *구조화된 dispatch 로그가
아직 없다*. 그래서:
  - computed_overlap: 두 텍스트 파일이 주어지면 *항상 실측*(실 backing).
  - dispatch_log_present: 파싱 가능한 dispatch 로그가 동반됐는지의 *실 관측*(0/1).
  - prior_context_token_count / allowed_file_count: dispatch 로그가 실재할 때만 emit.
    로그 부재 시 이 키들은 *deficit* 로 두고 상상하지 않는다 — CheckSpec 의
    applicability=dispatch_log_present==1 이 이를 '증거로 입증된 NA'(비게이팅)로 처리한다
    (침묵 skip 아님, meta_audit 정책).

CLI 에 raw 숫자 주입 인자는 없다(손 넣기 봉쇄, WP4a 규율).

CLI:
    python measure_cold_isolation.py --reunderstanding <cold_output.md> \\
        --reference <intent_or_downstream.md> [--dispatch-log <log.json>] \\
        [--cold-session <path>] [--phase 03] [--project-run <name>] \\
        [--measured-at <ISO8601>] --out-dir <project_root>/evidence

저장소 self_lint C35 — 모든 open encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_SCORING_DIR = Path(__file__).resolve().parents[1]
if str(_SCORING_DIR) not in sys.path:
    sys.path.insert(0, str(_SCORING_DIR))
import check_cold_session  # noqa: E402

import _evidence_common as ec  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "cold.isolation"
DEFAULT_PHASE = "03"

# dispatch 로그에서 허용 파일 목록이 실릴 수 있는 키(우선순위) — shadow-grade 스키마의
# loaded_artifacts, sub-agent dispatch 의 allowed_files 등 실 필드명 후보.
_ALLOWED_FILE_KEYS = ("allowed_files", "loaded_artifacts", "allowed_file_list", "access_allowed")

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokens(text: str) -> set[str]:
    """유니코드 \\w+ 토큰 집합(소문자). 언어 무관(한국어 포함) — 영어 정규식 sentinel 의
    한국어 미매치 회귀(P3)를 없앤다."""
    return {t.lower() for t in _TOKEN_RE.findall(text)}


def _jaccard(a: set[str], b: set[str]) -> float:
    """|A∩B| / |A∪B|. 합집합이 비면 0.0(공통 어휘 없음). 결정적."""
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _parse_dispatch_log(path: Path) -> dict[str, Any] | None:
    """dispatch 로그에서 prior_context_token_count(int) + 허용 파일 수를 뽑는다.

    prior_context_token_count 가 정수로 실재해야 '로그 있음'으로 인정한다 — 그 필드가
    없으면(격리 증거 자체가 없으면) None 을 반환해 producer 가 deficit 처리하게 한다
    (상상 금지). 허용 파일 목록은 여러 후보 키를 순서대로 시도하고, 없으면 0."""
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    prior = data.get("prior_context_token_count")
    if isinstance(prior, bool) or not isinstance(prior, int):
        return None
    allowed_count = 0
    for key in _ALLOWED_FILE_KEYS:
        v = data.get(key)
        if isinstance(v, list):
            allowed_count = len(v)
            break
    return {"prior_context_token_count": prior, "allowed_file_count": allowed_count}


def _build_report(
    reunderstanding: Path,
    reference: Path,
    dispatch_log: Path | None,
    cold_session: Path | None,
) -> dict[str, Any]:
    """콜드 산출물·참조·(있으면)dispatch 로그를 스캔 → 원시 관측 리포트(verdict 없음).

    이 리포트 자체가 measured 값들의 backing 이 된다(measure_dry_violation scan 패턴).
    reunderstanding/reference 실 텍스트, 토큰 수, overlap, dispatch 로그 관측, 그리고
    (--cold-session 시)check_cold_session.build_report 결과까지 담아 감사 가능하게 한다."""
    ru_text = reunderstanding.read_text(encoding="utf-8", errors="ignore")
    ref_text = reference.read_text(encoding="utf-8", errors="ignore")
    ru_tokens = _tokens(ru_text)
    ref_tokens = _tokens(ref_text)
    overlap = _jaccard(ru_tokens, ref_tokens)

    dispatch: dict[str, Any] | None = None
    if dispatch_log is not None:
        dispatch = _parse_dispatch_log(dispatch_log)

    report: dict[str, Any] = {
        "reunderstanding_path": reunderstanding.as_posix(),
        "reunderstanding_digest": ec.sha256_of_file(reunderstanding),
        "reunderstanding_token_count": len(ru_tokens),
        "reference_path": reference.as_posix(),
        "reference_digest": ec.sha256_of_file(reference),
        "reference_token_count": len(ref_tokens),
        "computed_overlap": overlap,
        "dispatch_log_present": 1 if dispatch is not None else 0,
    }
    if dispatch is not None:
        report["prior_context_token_count"] = dispatch["prior_context_token_count"]
        report["allowed_file_count"] = dispatch["allowed_file_count"]
    if cold_session is not None:
        # 콜드 세션 artifact 정합(check_cold_session)도 이 실행의 관측 사실 — 추적용으로
        # 리포트에 담는다(assertion 대상은 아님; 별도 차원이라 cold.isolation 을 오염 안 함).
        report["cold_session_artifact_report"] = check_cold_session.build_report(cold_session)
    return report


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 재구성 — CheckSpec cmd_pattern `^python .*measure_cold_isolation\\.py`
    과 정합."""
    parts = ["python", str(Path(__file__).resolve()),
             "--reunderstanding", args.reunderstanding, "--reference", args.reference]
    if args.dispatch_log:
        parts += ["--dispatch-log", args.dispatch_log]
    if args.cold_session:
        parts += ["--cold-session", args.cold_session]
    parts += ["--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    reunderstanding = Path(args.reunderstanding).resolve()
    reference = Path(args.reference).resolve()
    if not (reunderstanding.exists() and reference.exists()):
        # overlap 을 낼 두 텍스트 중 하나라도 없으면 computed_overlap deficit — evidence 를
        # 안 쓴다(법칙1 FAIL). 상상하지 않는다.
        return {
            "emitted": False,
            "reason": "reunderstanding/reference 텍스트 부재 — computed_overlap 계산 불가",
            "reunderstanding_exists": reunderstanding.exists(),
            "reference_exists": reference.exists(),
        }

    dispatch_log = Path(args.dispatch_log).resolve() if args.dispatch_log else None
    cold_session = Path(args.cold_session).resolve() if args.cold_session else None
    report = _build_report(reunderstanding, reference, dispatch_log, cold_session)

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    report_rel = ec.relpath(report_path, run_root)
    report_digest = ec.sha256_of_file(report_path)

    src = "cold_isolation_scan"
    measured = {
        "computed_overlap": ec.build_measured(report["computed_overlap"], src, report_rel),
        "dispatch_log_present": ec.build_measured(report["dispatch_log_present"], src, report_rel),
    }
    if report["dispatch_log_present"] == 1:
        # dispatch 로그 실재 시에만 격리 키를 emit — 부재 시 deficit(상상 금지). backing 은
        # dispatch 로그 파일 자신(값의 provenance 사슬).
        dispatch_rel = ec.relpath(dispatch_log, run_root)  # type: ignore[arg-type]
        measured["prior_context_token_count"] = ec.build_measured(
            report["prior_context_token_count"], "dispatch_log", dispatch_rel
        )
        measured["allowed_file_count"] = ec.build_measured(
            report["allowed_file_count"], "dispatch_log", dispatch_rel
        )

    artifact_digests = {report_rel: report_digest}
    if report["dispatch_log_present"] == 1:
        artifact_digests[ec.relpath(dispatch_log, run_root)] = ec.sha256_of_file(dispatch_log)  # type: ignore[arg-type]

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
        "computed_overlap": report["computed_overlap"],
        "dispatch_log_present": report["dispatch_log_present"],
        "prior_context_token_count": report.get("prior_context_token_count"),
        "allowed_file_count": report.get("allowed_file_count"),
        "deficits": (
            []
            if report["dispatch_log_present"] == 1
            else ["prior_context_token_count", "allowed_file_count"]
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_cold_isolation — cold.isolation 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument(
        "--reunderstanding", required=True,
        help="콜드 재이해 산출물 텍스트 (03 cold re-read / 07 plan re-read)",
    )
    p.add_argument(
        "--reference", required=True,
        help="overlap 대조 참조 텍스트 (원문 intent 또는 하류 artifact)",
    )
    p.add_argument(
        "--dispatch-log", default=None,
        help="sub-agent dispatch 로그 JSON (prior_context_token_count·허용 파일 목록). "
             "없으면 격리 키 deficit — 상상하지 않는다.",
    )
    p.add_argument(
        "--cold-session", default=None,
        help="cold session 경로 — check_cold_session artifact 정합을 추적용으로 리포트에 첨부",
    )
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
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
