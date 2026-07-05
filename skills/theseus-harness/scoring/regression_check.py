#!/usr/bin/env python3
"""
Regression Check — 매 코드 수정/회귀 시점 TDD 재실행 게이트 (sprint-34 / v0.9.39).

orchestrator 가 phase 08 의 매 sub-impl 산출 시점 + dacapo loop step F + sprint
loop iteration 시점에 호출. 테스트 + boot_check + lint 를 *재실행* 해 회귀를
runtime 시점에 차단. 결과는 `state/regression_log.json` append-only 누적 — 직전
known-good 대비 회귀 검출.

phase 08 의 5 sub-phase TDD ([`phases/08-implement.md`](../phases/08-implement.md))
가 *페이즈 단위* 이라면, 본 모듈은 *commit-level* — 두 layer 가 상보적.

명령:
    regression_check.py run --root <proj> --module <T-NNN>
        [--test-cmd 'pytest -x'] [--boot-cmd 'npm start' --healthz <url>]
        [--lint-cmd 'ruff check .']
        # 모든 단계 실행 + state/regression_log.json 항목 append
        # exit 0 = PASS, 1 = FAIL (회귀)

    regression_check.py last --root <proj>
        # 가장 최근 항목 JSON 덤프

    regression_check.py compare --root <proj>
        # 직전 known-good vs 최신 비교 — regression 검출 시 exit 1
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows console cp949 → 한글 stderr mojibake 방지
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCHEMA_VERSION = 1
LOG_FILENAME = "regression_log.json"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log_path(root: Path) -> Path:
    return root / "state" / LOG_FILENAME


def _load_log(root: Path) -> dict:
    p = _log_path(root)
    if not p.exists():
        return {"schema_version": SCHEMA_VERSION, "entries": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _save_log(root: Path, log: dict) -> None:
    p = _log_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(log, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _run_cmd(cmd: str | None, cwd: Path | None = None, timeout: int = 300) -> dict:
    """주어진 shell 명령 실행. cmd None 또는 빈 문자열 = skipped.

    shell=True — verification cmd 는 natural shell 명령 (intent/04-verification.md
    의 verification_command 가 'pytest -x' / 'cargo test' / 'npm test' 등) 이므로
    POSIX/Windows 양쪽에서 일관된 quoting.
    """
    if not cmd or not cmd.strip():
        return {"cmd": cmd, "exit": "skipped", "stdout_tail": "", "stderr_tail": ""}
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            cwd=str(cwd) if cwd else None,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
        return {
            "cmd": cmd,
            "exit": proc.returncode,
            "stdout_tail": proc.stdout[-1000:] if proc.stdout else "",
            "stderr_tail": proc.stderr[-1000:] if proc.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "exit": "timeout", "stdout_tail": "", "stderr_tail": "timeout"}


def evaluate_entry(test_res: dict, boot_res: dict, lint_res: dict) -> tuple[bool, str]:
    """3 단계 결과 → pass 여부 + 사유."""
    reasons: list[str] = []
    if test_res["exit"] not in (0, "skipped"):
        reasons.append(f"tests fail (exit={test_res['exit']})")
    if boot_res["exit"] not in (0, "skipped"):
        reasons.append(f"boot fail (exit={boot_res['exit']})")
    if lint_res["exit"] not in (0, "skipped"):
        reasons.append(f"lint fail (exit={lint_res['exit']})")
    return (not reasons, "; ".join(reasons) or "all pass")


def cmd_run(args) -> int:
    root = Path(args.root)
    test_res = _run_cmd(args.test_cmd, cwd=root if root.exists() else None, timeout=args.test_timeout)
    boot_res = _run_cmd(args.boot_cmd, cwd=root if root.exists() else None, timeout=args.boot_timeout)
    lint_res = _run_cmd(args.lint_cmd, cwd=root if root.exists() else None, timeout=args.lint_timeout)

    pass_, reason = evaluate_entry(test_res, boot_res, lint_res)

    log = _load_log(root)
    entry = {
        "timestamp": _utcnow_iso(),
        "phase": args.phase,
        "module": args.module,
        "trigger": args.trigger,
        "test": test_res,
        "boot": boot_res,
        "lint": lint_res,
        "outcome": "ok" if pass_ else "fail",
        "reason": reason,
    }
    log["entries"].append(entry)
    _save_log(root, log)

    json.dump({
        "ok": pass_,
        "outcome": entry["outcome"],
        "reason": reason,
        "entries_total": len(log["entries"]),
    }, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if pass_ else 1


def cmd_last(args) -> int:
    log = _load_log(Path(args.root))
    if not log["entries"]:
        print("regression_log 비어 있음", file=sys.stderr)
        return 1
    json.dump(log["entries"][-1], sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def detect_regression(log: dict) -> dict:
    """직전 known-good (outcome=ok) 와 최신 entry 비교."""
    entries = log.get("entries", [])
    if len(entries) < 2:
        return {"regressed": False, "reason": "history < 2"}
    latest = entries[-1]
    if latest["outcome"] == "ok":
        return {"regressed": False, "reason": "latest ok"}
    # 직전 ok 항목 찾기
    prev_ok = next((e for e in reversed(entries[:-1]) if e["outcome"] == "ok"), None)
    if prev_ok is None:
        return {
            "regressed": False,
            "reason": "no prior known-good — first attempt fail",
            "latest": latest,
        }
    return {
        "regressed": True,
        "reason": f"regression: 직전 ok ({prev_ok['timestamp']} module={prev_ok['module']}) → 최신 fail ({latest['reason']})",
        "prev_ok": prev_ok,
        "latest": latest,
    }


def cmd_compare(args) -> int:
    out = detect_regression(_load_log(Path(args.root)))
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 1 if out["regressed"] else 0


# --- evidence-emit 경로 seam (설계 §7.3, WP4b) --------------------------------
# 아래 두 순수 함수는 producers/measure_regression.py(증거 조립기)가 import 해 쓰는
# 재사용 지점이다 — dry_violation_count.build_report ← measure_dry_violation 와 동일
# 방향(스크립트가 순수 계산을 노출, producer 가 소비). 위 CLI/subcommand/exit-code 는
# 손대지 않는다(하위호환). verdict 는 여기서도 커널 몫이라 내지 않는다 — 이 함수들은
# 원시 delta 값만 낸다.


def extract_score(data: object, score_key: str | None = None) -> float | None:
    """커널 Verdict(또는 score Evidence Record) dict 에서 정규 score 값을 뽑는다.

    우선순위:
      1. 최상위 `value` 가 숫자면 그것(kernel Verdict.value = 측정값의 결정 함수, §4.1).
      2. `measured[score_key].value` 가 숫자면 그것(score Evidence 의 measured 스칼라).
    둘 다 아니면 None — 상상하지 않는다(호출자가 결손 처리해 커널 법칙1로 FAIL).
    bool 은 int 서브클래스라 명시적으로 배제(True 를 1.0 으로 오인 금지)."""
    if not isinstance(data, dict):
        return None
    val = data.get("value")
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        return float(val)
    if score_key:
        measured = data.get("measured")
        if isinstance(measured, dict):
            entry = measured.get(score_key)
            if isinstance(entry, dict):
                mv = entry.get("value")
                if isinstance(mv, (int, float)) and not isinstance(mv, bool):
                    return float(mv)
    return None


def build_delta_report(prior_score: float, current_score: float) -> dict:
    """두 커널 검증 score → 원시 delta 리포트(verdict 없음). regression_threshold 판정
    (delta >= -0.05, §7.3)은 커널이 CheckSpec `checks/sprint.regression.json` 으로 내린다 —
    여기서는 계산량(delta)만 낸다. `regressed` 는 정보용 관측이며 measured 로 emit 되지
    않는다(게이트는 커널이 delta 로 직접)."""
    delta = current_score - prior_score
    return {
        "prior_score": prior_score,
        "current_score": current_score,
        "score_delta": delta,
        "regressed_hint": delta < -0.05,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("run", help="test + boot + lint 재실행 + log append")
    pr.add_argument("--root", required=True)
    pr.add_argument("--module", required=True, help="T-NNN 또는 sprint NN")
    pr.add_argument("--phase", default="08", help="phase 번호 (default 08)")
    pr.add_argument("--trigger", default="impl",
                    choices=["impl", "dacapo-step-f", "sprint-iter", "phase-exit"])
    pr.add_argument("--test-cmd", default=None,
                    help="테스트 명령 (intent/04-verification.md 의 verification_command)")
    pr.add_argument("--test-timeout", type=int, default=300)
    pr.add_argument("--boot-cmd", default=None, help="boot_check 대체 — boot 명령 (옵션)")
    pr.add_argument("--boot-timeout", type=int, default=60)
    pr.add_argument("--lint-cmd", default=None, help="lint 명령 (옵션)")
    pr.add_argument("--lint-timeout", type=int, default=120)
    pr.set_defaults(func=cmd_run)

    pl = sub.add_parser("last", help="가장 최근 항목 덤프")
    pl.add_argument("--root", required=True)
    pl.set_defaults(func=cmd_last)

    pc = sub.add_parser("compare", help="직전 known-good vs 최신 — regression 검출")
    pc.add_argument("--root", required=True)
    pc.set_defaults(func=cmd_compare)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
