#!/usr/bin/env python3
"""
emit fidelity 검증 CLI — sprint-35 v0.9.40 신규.

prebuilt-shell-runtime-json 컨벤션 §3.3 의 의무 키 enumeration 을 *runnable* 게이트로 박음.
cold session 측 산출물 (`.ShipofTheseus/<proj>/lineage.json` + `webview/data/webview.json`) 의
*키 완전성* + *룰 적용 (hotspot ★ / parallel rows / multiverse subgraph)* 을 검증.

이중 책무 (lineage.json/webview.json 이 *진행 게이트* + *FE source* 동시 만족) 의 게이트 측면을
runnable 형태로 강제하여, prompt 만의 권고가 아닌 *체감 압력* 으로 만든다.

명령:
    emit_fidelity.py check --root <project_dir> [--grade G4]
        exit 0 = PASS, exit 1 = violations (stderr 에 위반 목록)

    emit_fidelity.py report --root <project_dir>
        JSON 으로 모든 의무 키의 fill 상태 dump (디버깅용)

    emit_fidelity.py samples
        skills/theseus-harness/templates/{lineage-viewer,webview}/sample/ 자체 검증
        (하네스 contributor 자기 점검용 — self_lint C-EFS 와 동일 로직)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ─────────────────────────────────────────────────────────────────────
# lineage.json 의무 키 (컨벤션 §3.3)
# ─────────────────────────────────────────────────────────────────────

LINEAGE_REQUIRED_TOP = [
    "schema_version", "project_id", "project_run",
    "started_at_iso", "ended_at_iso", "duration_seconds",
    "grade", "final_phase", "phases_completed",
    "violations_count", "dacapo_count", "final_outcome",
    "mermaid_flowchart", "mermaid_gantt",
    "fingerprint_chain", "dacapo_summary", "phase04_answers", "sentinel_events",
]

FINAL_OUTCOME_ENUM = {"HANDOFF", "IN_PROGRESS", "BUDGET_BOUND"}
GRADE_ENUM = {"G1", "G2", "G3", "G4", "G5"}

# dummy filler 금지 — 진짜 데이터 위치에 박히면 fail
DUMMY_FILLERS = {"데이터 미주입", "TODO", "TBD", "-", "FIXME", "..."}


def _is_dummy(value: str) -> bool:
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    return stripped in DUMMY_FILLERS or stripped == ""


def _has_parallel_rows(gantt_text: str, min_count: int = 3) -> bool:
    """동일 시각으로 시작하는 task 가 ≥ min_count 인가.

    Mermaid gantt 행 형식 :
        <label> :<class?>, <id>, <YYYY-MM-DD HH:mm>, <duration>
    또는
        <label> :<id>, <YYYY-MM-DD HH:mm>, <duration>

    min_count 3 — G3+ multiverse 폭 ≥3 정합. 2 로 낮추면 back-to-back phase
    (1 분 bypass + 다음 phase 동일 시각 시작) 의 false-pass 발생.
    """
    pattern = re.compile(r",\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s*,")
    starts = pattern.findall(gantt_text)
    if not starts:
        return False
    counts: dict[str, int] = {}
    for s in starts:
        counts[s] = counts.get(s, 0) + 1
    return any(c >= min_count for c in counts.values())


def _count_subgraphs(flowchart_text: str) -> int:
    return len(re.findall(r"\bsubgraph\s+\w+", flowchart_text))


def check_lineage_json(path: Path, grade: str | None = None, mode: str = "filled") -> list[str]:
    """lineage.json 의무 키 + 본문 룰 검증.

    grade 미지정 시 lineage.json 의 grade 필드 사용. 둘 다 없으면 G4 fallback.
    mode = "filled" (기본, cold session 진행/종료 후) | "skeleton" (pre-bootup 시점, 빈값 허용).
    """
    errors: list[str] = []
    if not path.exists():
        return [f"lineage.json 부재: {path}"]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"lineage.json 파싱 실패: {e}"]

    # 1. top-level 의무 키 enumeration — skeleton 도 모든 키 *enumeration* 의무
    for key in LINEAGE_REQUIRED_TOP:
        if key not in data:
            errors.append(f"lineage.json: 의무 키 '{key}' 부재")

    g = (grade or data.get("grade") or "G4").upper()
    if g not in GRADE_ENUM:
        errors.append(f"lineage.json grade '{g}' enum 외 ({GRADE_ENUM})")

    if mode == "skeleton":
        # skeleton: 빈값/dummy 허용. enum 만 약하게 검증 + flowchart/gantt 코드 펜스 골격은 필요.
        flow = data.get("mermaid_flowchart", "")
        gantt = data.get("mermaid_gantt", "")
        if "flowchart" not in flow:
            errors.append("lineage.json (skeleton) mermaid_flowchart 'flowchart' 키워드 부재")
        if "gantt" not in gantt or "dateFormat" not in gantt:
            errors.append("lineage.json (skeleton) mermaid_gantt 'gantt' + 'dateFormat' 부재")
        return errors

    # filled mode 이하 — sprint-35 정책 그대로
    fo = data.get("final_outcome")
    if fo not in FINAL_OUTCOME_ENUM:
        errors.append(f"lineage.json final_outcome '{fo}' enum 외 ({FINAL_OUTCOME_ENUM})")

    for k in ["project_id", "project_run", "started_at_iso", "ended_at_iso"]:
        v = data.get(k)
        if not v or _is_dummy(v):
            errors.append(f"lineage.json '{k}' 빈값/dummy")

    if data.get("phases_completed", 0) == 0:
        errors.append("lineage.json phases_completed = 0 (cold session 미진행)")

    # 3. mermaid_flowchart 본문 룰
    flow = data.get("mermaid_flowchart", "")
    if "flowchart" not in flow:
        errors.append("lineage.json mermaid_flowchart 'flowchart' 키워드 부재")
    if g in ("G4", "G5"):
        if _count_subgraphs(flow) < 2:
            errors.append(
                f"lineage.json mermaid_flowchart subgraph < 2 ({_count_subgraphs(flow)}) — "
                f"G4+ 는 multiverse + dacapo subgraph ≥ 2 의무"
            )

    # 4. mermaid_gantt 본문 룰
    gantt = data.get("mermaid_gantt", "")
    if "gantt" not in gantt or "dateFormat" not in gantt:
        errors.append("lineage.json mermaid_gantt 'gantt' + 'dateFormat' 부재")
    if g in ("G4", "G5"):
        if "★" not in gantt:
            errors.append("lineage.json mermaid_gantt hotspot ★ marker 부재 (G4+, sprint-35-extra)")
        if not _has_parallel_rows(gantt, min_count=3):
            errors.append(
                "lineage.json mermaid_gantt 병렬 sub-agent row 부재 — "
                "동일 start 의 task ≥ 3 의무 (G4+, phase 08 multiverse 폭 ≥3)"
            )
        # bypass = :crit 금지
        for line in gantt.splitlines():
            if "bypass" in line and ":crit" in line:
                errors.append(f"lineage.json mermaid_gantt bypass 행에 :crit 사용 금지 — '{line.strip()}'")

    # 5. fingerprint_chain 정합
    chain = data.get("fingerprint_chain", [])
    pc = data.get("phases_completed", 0)
    if isinstance(chain, list) and isinstance(pc, int) and pc > 0:
        if len(chain) != pc:
            errors.append(f"fingerprint_chain 길이({len(chain)}) ≠ phases_completed({pc})")
    if isinstance(chain, list):
        for i, row in enumerate(chain):
            for k in ["phase", "name", "fingerprint", "match"]:
                if k not in row:
                    errors.append(f"fingerprint_chain[{i}] '{k}' 부재")
            fp = row.get("fingerprint", "")
            if isinstance(fp, str) and not fp.startswith("sha256:"):
                errors.append(f"fingerprint_chain[{i}] fingerprint 'sha256:' prefix 부재 ('{fp}')")

    # 6. phase04_answers — Q-G1 의무 (G2+)
    if g != "G1":
        answers = data.get("phase04_answers", [])
        if not isinstance(answers, list) or len(answers) == 0:
            errors.append("phase04_answers 빈 list — Q-G1 + Q-D1~D9 row 의무 (G2+)")
        else:
            qs = {a.get("question") for a in answers if isinstance(a, dict)}
            if "Q-G1" not in qs:
                errors.append("phase04_answers Q-G1 row 부재")

    # 7. dacapo_summary — winner score / outcome 채워짐
    dacapo = data.get("dacapo_summary", [])
    if isinstance(dacapo, list):
        for i, row in enumerate(dacapo):
            for k in ["phase", "rerun_count", "final_winner", "final_score", "outcome"]:
                if k not in row:
                    errors.append(f"dacapo_summary[{i}] '{k}' 부재")
            if _is_dummy(str(row.get("final_winner", ""))):
                errors.append(f"dacapo_summary[{i}] final_winner dummy")

    return errors


# ─────────────────────────────────────────────────────────────────────
# webview.json 의무 키 (컨벤션 §3.3 + phase 12 표)
# ─────────────────────────────────────────────────────────────────────

WEBVIEW_REQUIRED_TOP = [
    "schema_version", "project_id", "final_phase",
    "timing", "state", "plan", "intent", "impl",
    "quality", "tests", "sprints", "runtime",
]


# ─────────────────────────────────────────────────────────────────────
# dashboard.json (interactive-viewer) 의무 키 (sprint-36)
# ─────────────────────────────────────────────────────────────────────

DASHBOARD_REQUIRED_TOP = [
    "schema_version", "project_id", "current_phase",
    "domain", "domain_label", "matched", "skip",
    "summary_kpis", "scenarios", "widgets", "raw_artifacts", "narrative",
]
WIDGET_TYPES = {"kpi_grid", "topology", "metric_chart", "table", "markdown"}


def check_dashboard_json(path: Path, mode: str = "filled") -> list[str]:
    """dashboard.json (interactive-viewer) 검증. sprint-36 신규.

    mode = "skeleton" 일 때는 빈 list / 도메인 미매칭 모두 허용.
    """
    errors: list[str] = []
    if not path.exists():
        return [f"dashboard.json 부재: {path}"]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"dashboard.json 파싱 실패: {e}"]

    # 1. enumeration
    for key in DASHBOARD_REQUIRED_TOP:
        if key not in data:
            errors.append(f"dashboard.json: 의무 키 '{key}' 부재")

    if mode == "skeleton":
        # skeleton: 모든 list 비어있어도 됨, domain null 허용
        return errors

    # filled mode
    if data.get("skip"):
        # skip 시 skip_reason 필수
        if not data.get("skip_reason"):
            errors.append("dashboard.json skip=true 인데 skip_reason 부재")
        return errors

    # 비-skip = 도메인 매칭됨 → 산출 의무
    if not data.get("widgets"):
        errors.append("dashboard.json widgets 빈 list (skip 도 아님)")
    else:
        for i, w in enumerate(data["widgets"]):
            if not isinstance(w, dict):
                errors.append(f"dashboard.json widgets[{i}] dict 아님")
                continue
            if "type" not in w:
                errors.append(f"dashboard.json widgets[{i}] type 부재")
            elif w["type"] not in WIDGET_TYPES:
                errors.append(f"dashboard.json widgets[{i}] type '{w['type']}' 카탈로그 외 ({WIDGET_TYPES})")
            if not w.get("title"):
                errors.append(f"dashboard.json widgets[{i}] title 부재")

    if not data.get("summary_kpis"):
        errors.append("dashboard.json summary_kpis 빈 list (도메인 매칭 시 ≥ 1 의무)")

    return errors


def check_webview_json(path: Path, grade: str | None = None, mode: str = "filled") -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"webview.json 부재: {path}"]

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"webview.json 파싱 실패: {e}"]

    g = (grade or "G4").upper()

    # 1. 8 탭 키 enumeration — skeleton 도 enumeration 의무
    for key in WEBVIEW_REQUIRED_TOP:
        if key not in data:
            errors.append(f"webview.json: 의무 키 '{key}' 부재")

    if mode == "skeleton":
        # skeleton: 빈 list/null 허용. timing.started_at_iso 만 의무 (pre-bootup 시각).
        timing = data.get("timing", {})
        if not isinstance(timing, dict) or not timing.get("started_at_iso"):
            errors.append("webview.json (skeleton) timing.started_at_iso 부재")
        return errors

    # 2. timing
    timing = data.get("timing", {})
    if not isinstance(timing, dict) or not timing.get("started_at_iso"):
        errors.append("webview.json timing.started_at_iso 부재")

    # 3. plan.module_graph_mermaid (G2+)
    if g != "G1":
        plan = data.get("plan", {})
        mg = plan.get("module_graph_mermaid", "") if isinstance(plan, dict) else ""
        if "flowchart" not in mg:
            errors.append("webview.json plan.module_graph_mermaid 'flowchart' 부재 (G2+)")

    # 4. intent — 01-intent.md 키 의무
    intent = data.get("intent", {})
    if isinstance(intent, dict) and "01-intent.md" not in intent:
        errors.append("webview.json intent['01-intent.md'] 부재")

    # 5. impl — 08-impl-log.md (phase 08 진입 시 = G2+)
    if g != "G1":
        impl = data.get("impl", {})
        if isinstance(impl, dict) and "08-impl-log.md" not in impl:
            errors.append("webview.json impl['08-impl-log.md'] 부재 (G2+)")

    # 6. quality (phase 09 진입 후)
    quality = data.get("quality")
    if quality is not None and isinstance(quality, str) and _is_dummy(quality):
        errors.append("webview.json quality dummy filler")

    # 7. tests / sprints — phase 10 진입 후 빈 list 금지 (G2+)
    if g not in ("G1",):
        tests = data.get("tests", {})
        if isinstance(tests, dict):
            if not tests.get("unit"):
                errors.append("webview.json tests.unit 빈 list (G2+, phase 10 진입 후)")
            # e2e 는 G3+ 의무
            if g not in ("G2",) and not tests.get("e2e"):
                errors.append("webview.json tests.e2e 빈 list (G3+, phase 10 진입 후)")

        if not data.get("sprints"):
            errors.append("webview.json sprints 빈 list (G2+, phase 10 진입 후)")

    # 8. runtime.prereq + boot_result (phase 09 진입 후)
    rt = data.get("runtime", {})
    if isinstance(rt, dict):
        if "prereq" not in rt:
            errors.append("webview.json runtime.prereq 부재")
        if "boot_result" not in rt:
            errors.append("webview.json runtime.boot_result 부재")

    return errors


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────


def cmd_check(args: argparse.Namespace) -> int:
    root = Path(args.root)
    grade = args.grade
    mode = args.mode or "filled"

    errors: list[str] = []
    lineage_path = root / "lineage.json"
    webview_path = root / "webview" / "data" / "webview.json"
    dashboard_path = root / "interactive-viewer" / "dashboard.json"

    if lineage_path.exists():
        errors.extend(check_lineage_json(lineage_path, grade=grade, mode=mode))
    else:
        errors.append(f"lineage.json 부재: {lineage_path}")

    if webview_path.exists():
        errors.extend(check_webview_json(webview_path, grade=grade, mode=mode))
    else:
        errors.append(f"webview/data/webview.json 부재: {webview_path}")

    if dashboard_path.exists():
        errors.extend(check_dashboard_json(dashboard_path, mode=mode))
    else:
        # dashboard 는 phase 13 산출이라 phase 13 이전 미존재 허용. skeleton 모드면 의무.
        if mode == "skeleton":
            errors.append(f"interactive-viewer/dashboard.json 부재 (skeleton 의무): {dashboard_path}")

    if errors:
        print(f"emit fidelity FAIL ({mode}) — {len(errors)} 위반:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"emit fidelity PASS ({mode})", file=sys.stderr)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    root = Path(args.root)
    lineage_path = root / "lineage.json"
    webview_path = root / "webview" / "data" / "webview.json"
    dashboard_path = root / "interactive-viewer" / "dashboard.json"
    mode = args.mode or "filled"

    report = {
        "mode": mode,
        "lineage": {
            "path": str(lineage_path),
            "exists": lineage_path.exists(),
            "errors": check_lineage_json(lineage_path, grade=args.grade, mode=mode) if lineage_path.exists() else ["부재"],
        },
        "webview": {
            "path": str(webview_path),
            "exists": webview_path.exists(),
            "errors": check_webview_json(webview_path, grade=args.grade, mode=mode) if webview_path.exists() else ["부재"],
        },
        "dashboard": {
            "path": str(dashboard_path),
            "exists": dashboard_path.exists(),
            "errors": check_dashboard_json(dashboard_path, mode=mode) if dashboard_path.exists() else ["부재"],
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def cmd_samples(args: argparse.Namespace) -> int:
    here = Path(__file__).resolve().parent.parent
    lineage_sample = here / "templates" / "lineage-viewer" / "sample" / "lineage.json"
    webview_sample = here / "templates" / "webview" / "sample" / "webview.json"
    dashboard_sample = here / "templates" / "interactive-viewer" / "sample" / "dashboard.json"

    errors: list[str] = []
    le = check_lineage_json(lineage_sample)
    we = check_webview_json(webview_sample)
    errors.extend([f"lineage sample: {e}" for e in le])
    errors.extend([f"webview sample: {e}" for e in we])
    if dashboard_sample.exists():
        de = check_dashboard_json(dashboard_sample)
        errors.extend([f"dashboard sample: {e}" for e in de])

    if errors:
        print(f"sample fidelity FAIL — {len(errors)} 위반:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("sample fidelity PASS (lineage + webview + dashboard)", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="emit fidelity 검증 — lineage.json + webview.json")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check", help="cold session 산출물 검증")
    p_check.add_argument("--root", required=True, help=".ShipofTheseus/<proj> 디렉토리")
    p_check.add_argument("--grade", default=None, help="G1~G5 (lineage.json 의 grade 필드 우선)")
    p_check.add_argument("--mode", default="filled", choices=["filled", "skeleton"], help="filled (기본, cold session 진행 후) | skeleton (pre-bootup, 빈값 허용)")
    p_check.set_defaults(func=cmd_check)

    p_report = sub.add_parser("report", help="JSON report 덤프")
    p_report.add_argument("--root", required=True)
    p_report.add_argument("--grade", default=None)
    p_report.add_argument("--mode", default="filled", choices=["filled", "skeleton"])
    p_report.set_defaults(func=cmd_report)

    p_samples = sub.add_parser("samples", help="하네스 sample/ 자체 검증")
    p_samples.set_defaults(func=cmd_samples)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
