#!/usr/bin/env python3
"""measure_context_minimality.py — review.context_minimality 증거 조립기 (pure-review 순도).

pure-review(페이즈 03 콜드 재이해 / 06·08 shadow grader)가 *필요한 것만 주입해* 리뷰했는지를
값으로 게이팅할 수 있게, 리뷰 디스패치 로그를 스캔해 다음을 emit 한다:
  - calls_total              : 로그에 기록된 리뷰 호출 수
  - malformed_calls          : 필수 필드 결손/타입오류 호출 수 (무결성)
  - prior_context_max        : 호출들의 prior_context_token_count 최대 (0 이어야 진짜 콜드)
  - duplicate_call_ids       : agent_call_id 중복 수 (fresh 재호출 위반)
  - loaded_artifacts_missing : 로그가 선언한 주입 파일 중 디스크 부재 수 (무결성)
  - loaded_tokens_max        : 호출별 주입 파일 토큰 합의 최대 (producer 가 디스크에서 *재계산*)

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다 — '순도/최소성' 판정은 커널이
CheckSpec `checks/review.context_minimality.json` 으로 내린다. loaded_tokens_max 는 로그의
자기 신고 수치를 신뢰하지 않고, 로그가 가리키는 실제 파일을 producer 가 다시 읽어
\\w+ 토큰으로 재계산한 값이다(상상값 주입 0). 마찬가지로 loaded_artifacts_missing 은
로그의 주장이 아니라 producer 의 디스크 stat 결과다.

정직 고지: prior_context_token_count 는 디스패치 계층이 기록한 관측값이다(producer 가
sub-agent conversation 을 직접 못 본다 — shadow-grader-zero-context.md 와 동일 전제). 대신
loaded_artifacts 의 *실재*와 *토큰 수*는 producer 가 디스크에서 재검증하고 agent_call_id
중복은 로그에서 값으로 잡는다 — 순도의 자기 신고 여지를 무결성·freshness 값 검사로 조인다.
cold.isolation 이 dispatch_log_present==1 applicability 뒤에서 휴면(비게이팅)이던 것과 달리
본 체크는 applicability 없이 항상 게이팅한다 — 로그 부재는 NA 가 아니라 evidence_missing FAIL.

리뷰 디스패치 로그 스키마(유연): 최상위 list 또는 {"calls"|"review_calls"|"dispatch_calls": [...]}.
각 호출 = {agent_call_id: str, prior_context_token_count: int, loaded_artifacts: [상대경로,...]}.
loaded_artifacts 경로는 --artifacts-root(기본: project_root = out_dir 의 부모) 기준 해석.

CLI 에 raw 숫자 주입 인자는 없다(손 넣기 봉쇄).

CLI:
    python measure_context_minimality.py --dispatch-log <log.json> \\
        [--artifacts-root <dir>] [--phase 03] [--project-run <name>] \\
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

import _evidence_common as ec  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "review.context_minimality"
DEFAULT_PHASE = "03"

# 로그 최상위에서 호출 배열이 실릴 수 있는 키(우선순위).
_CALLS_KEYS = ("calls", "review_calls", "dispatch_calls")

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _token_count(text: str) -> int:
    """유니코드 \\w+ 토큰 수. 언어 무관(한국어 포함)."""
    return len(_TOKEN_RE.findall(text))


def _extract_calls(data: Any) -> list[Any] | None:
    """로그에서 호출 배열을 뽑는다. list 면 그대로, dict 면 알려진 키. 아니면 None."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in _CALLS_KEYS:
            v = data.get(key)
            if isinstance(v, list):
                return v
    return None


def _valid_call(call: Any) -> bool:
    """호출이 필수 필드(agent_call_id str + prior int + loaded_artifacts list)를 갖췄나."""
    if not isinstance(call, dict):
        return False
    cid = call.get("agent_call_id")
    if not isinstance(cid, str) or not cid.strip():
        return False
    prior = call.get("prior_context_token_count")
    # bool 은 int 서브타입이라 명시 배제 — True/False 를 토큰 수로 오인하지 않는다.
    if isinstance(prior, bool) or not isinstance(prior, int):
        return False
    if not isinstance(call.get("loaded_artifacts"), list):
        return False
    return True


def _build_report(calls: list[Any], artifacts_root: Path) -> dict[str, Any]:
    """호출 배열 스캔 → 원시 관측 리포트(verdict 없음).

    loaded_artifacts 토큰 수와 부재 여부는 로그의 자기 신고가 아니라 producer 가
    artifacts_root 기준으로 디스크를 직접 stat/재계산한 값이다(상상 금지). 이 리포트
    자체가 measured 값들의 backing artifact 가 된다."""
    calls_total = len(calls)
    malformed = 0
    priors: list[int] = []
    call_ids: list[str] = []
    missing = 0
    tokens_per_call: list[int] = []
    per_call: list[dict[str, Any]] = []

    for idx, call in enumerate(calls):
        if not _valid_call(call):
            malformed += 1
            per_call.append({"index": idx, "malformed": True})
            continue
        cid = call["agent_call_id"]
        prior = call["prior_context_token_count"]
        call_ids.append(cid)
        priors.append(prior)

        loaded = [a for a in call["loaded_artifacts"] if isinstance(a, str)]
        call_missing = 0
        call_tokens = 0
        resolved: list[dict[str, Any]] = []
        for rel in loaded:
            fpath = artifacts_root / rel
            exists = fpath.is_file()
            tok = _token_count(fpath.read_text(encoding="utf-8", errors="ignore")) if exists else 0
            if not exists:
                call_missing += 1
            call_tokens += tok
            resolved.append({"path": rel, "exists": exists, "token_count": tok})
        missing += call_missing
        tokens_per_call.append(call_tokens)
        per_call.append({
            "index": idx,
            "agent_call_id": cid,
            "prior_context_token_count": prior,
            "loaded_artifacts": resolved,
            "loaded_tokens": call_tokens,
            "missing_count": call_missing,
        })

    duplicate_call_ids = len(call_ids) - len(set(call_ids))
    return {
        "artifacts_root": artifacts_root.as_posix(),
        "calls_total": calls_total,
        "malformed_calls": malformed,
        "prior_context_max": max(priors) if priors else 0,
        "duplicate_call_ids": duplicate_call_ids,
        "loaded_artifacts_missing": missing,
        "loaded_tokens_max": max(tokens_per_call) if tokens_per_call else 0,
        "calls": per_call,
    }


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 재구성 — CheckSpec cmd_pattern `^python .*measure_context_minimality\\.py`
    과 정합."""
    parts = ["python", str(Path(__file__).resolve()), "--dispatch-log", args.dispatch_log]
    if args.artifacts_root:
        parts += ["--artifacts-root", args.artifacts_root]
    parts += ["--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    dispatch_log = Path(args.dispatch_log).resolve()
    if not dispatch_log.is_file():
        # 로그 부재 → evidence 미기록 → 커널 법칙1 FAIL(비휴면: NA 아님). 상상 0.
        return {
            "emitted": False,
            "reason": "review dispatch 로그 부재 — measure_context_minimality 미실행(evidence_missing FAIL)",
            "dispatch_log_exists": False,
        }
    try:
        data = json.loads(dispatch_log.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "emitted": False,
            "reason": "review dispatch 로그 파싱 불가 — evidence 미기록(법칙1 FAIL)",
        }
    calls = _extract_calls(data)
    if calls is None:
        return {
            "emitted": False,
            "reason": "review dispatch 로그에 호출 배열 부재 — evidence 미기록(법칙1 FAIL)",
        }

    artifacts_root = Path(args.artifacts_root).resolve() if args.artifacts_root else run_root
    report = _build_report(calls, artifacts_root)

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    report_rel = ec.relpath(report_path, run_root)
    report_digest = ec.sha256_of_file(report_path)

    src = "context_minimality_scan"
    measured = {
        key: ec.build_measured(report[key], src, report_rel)
        for key in (
            "calls_total",
            "malformed_calls",
            "prior_context_max",
            "duplicate_call_ids",
            "loaded_artifacts_missing",
            "loaded_tokens_max",
        )
    }
    # 리포트(producer 재계산)와 디스패치 로그(원 입력) 둘 다 digest 체인에 건다.
    artifact_digests = {
        report_rel: report_digest,
        ec.relpath(dispatch_log, run_root): ec.sha256_of_file(dispatch_log),
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
        "calls_total": report["calls_total"],
        "prior_context_max": report["prior_context_max"],
        "loaded_artifacts_missing": report["loaded_artifacts_missing"],
        "duplicate_call_ids": report["duplicate_call_ids"],
        "malformed_calls": report["malformed_calls"],
        "loaded_tokens_max": report["loaded_tokens_max"],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_context_minimality — review.context_minimality 증거 조립기 (verdict 없음)"
    )
    p.add_argument(
        "--dispatch-log", required=True,
        help="리뷰 디스패치 로그 JSON (호출별 agent_call_id·prior_context_token_count·loaded_artifacts). "
             "부재/파싱불가 시 evidence 미기록 — 상상하지 않는다(evidence_missing FAIL).",
    )
    p.add_argument(
        "--artifacts-root", default=None,
        help="loaded_artifacts 상대경로 해석 기준(기본: project_root = out-dir 의 부모)",
    )
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
    p.add_argument("--project-run", default=None, help="project_run 이름(기본: run_root.name)")
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
