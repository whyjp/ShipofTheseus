#!/usr/bin/env python3
"""
pre-cold-session bootup — phase 00 enter 직전 (sprint-36 v0.9.41 신규).

orchestrator 가 cold session 시작 *전* 호출 :
1. `templates/{lineage-viewer,webview,interactive-viewer}/dist/*` 를 project root 로 복사
2. 각 viewer 의 빈 골격 JSON emit (의무 키 모두 박힘, 값 null/empty)
3. `templates/viewer-runtime/*` 를 project/viewer-runtime/ 로 복사
4. `viewer_runtime.py up --root <project>` 호출 → HTTP server + lock file
5. 사용자에게 viewer URL 출력

이렇게 하면 cold session 진행 중 viewer 가 *항상 떠 있고*, JSON 갱신 시 5초 polling 으로 자동 반영. file:// 환경에선 수동 새로고침 button 으로 갱신.

종료는 `pre_bootup.py teardown --root <project>` 또는 `viewer_runtime.py down`.

명령:
    pre_bootup.py bootstrap --root <project> [--port 18080] [--skip-server]
    pre_bootup.py teardown  --root <project>
    pre_bootup.py emit-skeleton --root <project> --kind lineage|webview|interactive
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


SCHEMA_VERSION = "0.9.41"

# templates/ root 자동 탐색 (이 파일 기준 ../templates/)
HARNESS_ROOT = Path(__file__).resolve().parent.parent  # skills/theseus-harness/
TEMPLATES_ROOT = HARNESS_ROOT / "templates"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ─────────────────────────────────────────────────────────────────────
# 빈 골격 JSON
# ─────────────────────────────────────────────────────────────────────


def lineage_skeleton(project_id: str | None = None, project_run: str | None = None, grade: str = "G4") -> dict:
    """phase 00 미진입 상태의 lineage.json — emit_fidelity 의 *skeleton* 모드 통과용."""
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id or "pending",
        "project_run": project_run or "pending",
        "started_at_iso": _utcnow_iso(),
        "ended_at_iso": None,
        "duration_seconds": 0,
        "grade": grade,
        "final_phase": None,
        "phases_completed": 0,
        "violations_count": 0,
        "dacapo_count": 0,
        "final_outcome": "IN_PROGRESS",
        "mermaid_flowchart": "flowchart TB\n  Empty[\"cold session 미시작\"]\n  classDef pending fill:#f5f0e6,stroke:#b8ad9c,stroke-dasharray:4 4\n  class Empty pending",
        "mermaid_gantt": "gantt\n  title Phase Lineage — pending\n  dateFormat YYYY-MM-DD HH:mm\n  axisFormat %H:%M\n  section Pending\n  대기 :p0, 2000-01-01 00:00, 1m",
        "fingerprint_chain": [],
        "dacapo_summary": [],
        "phase04_answers": [],
        "sentinel_events": [],
        "winner": None,
    }


def webview_skeleton(project_id: str | None = None) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "emit_mode": "prebuilt",
        "project_id": project_id or "pending",
        "final_phase": None,
        "timing": {"started_at_iso": _utcnow_iso(), "ended_at_iso": None, "duration_seconds": 0},
        "state": {
            "status": "waiting",
            "current_phase": None,
            "active_skill": None,
            "active_agent": None,
            "current_universe": None,
            "current_module": None,
            "current_sub_depth": 0,
            "last_completed_phase": None,
            "completed_count": 0,
            "total_estimated": 15,
            "pending_artifacts": [],
        },
        "plan": {"module_graph_mermaid": ""},
        "intent": {},
        "impl": {},
        "quality": "",
        "tests": {"unit": [], "e2e": []},
        "sprints": [],
        "runtime": {"prereq": {}, "boot_result": {}},
    }


def interactive_skeleton(project_id: str | None = None) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id or "pending",
        "current_phase": "pre-bootup",
        "final_phase": None,
        "status": "waiting",
        "domain": None,
        "domain_label": "도메인 미매칭 (cold session 미시작)",
        "matched": False,
        "skip": False,
        "skip_reason": None,
        "summary_kpis": [],
        "scenarios": [],
        "widgets": [],
        "raw_artifacts": [],
        "narrative": "# 대기 중\n\ncold session 이 시작되면 phase 별 산출이 본 viewer 에 자동 반영됩니다.\n",
    }


# ─────────────────────────────────────────────────────────────────────
# bootstrap / teardown
# ─────────────────────────────────────────────────────────────────────


def _copy_dist(src_dir: Path, dst_dir: Path, rename_index: str | None = None) -> None:
    """templates/<viewer>/dist/* 를 dst_dir/ 로 복사. rename_index 가 있으면 index.html → 그 이름."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    for item in src_dir.iterdir():
        target_name = rename_index if (rename_index and item.name == "index.html") else item.name
        target = dst_dir / target_name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def cmd_bootstrap(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    project_id = args.project_id or root.name
    grade = (args.grade or "G4").upper()

    # 1. lineage shell
    lineage_dist = TEMPLATES_ROOT / "lineage-viewer" / "dist"
    if lineage_dist.exists():
        # lineage shell → root 직접 복사. index.html → lineage.html
        _copy_dist(lineage_dist, root, rename_index="lineage.html")
        # 빈 골격 emit
        (root / "lineage.json").write_text(
            json.dumps(lineage_skeleton(project_id=project_id, grade=grade), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[pre-bootup] lineage → {root}/lineage.html + lineage.json", file=sys.stderr)
    else:
        print(f"[pre-bootup] WARN — {lineage_dist} 부재, skip", file=sys.stderr)

    # 2. webview shell
    webview_dist = TEMPLATES_ROOT / "webview" / "dist"
    if webview_dist.exists():
        webview_dst = root / "webview"
        _copy_dist(webview_dist, webview_dst)
        data_dir = webview_dst / "data"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "webview.json").write_text(
            json.dumps(webview_skeleton(project_id=project_id), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[pre-bootup] webview → {webview_dst}/index.html + data/webview.json", file=sys.stderr)
    else:
        print(f"[pre-bootup] WARN — {webview_dist} 부재, skip", file=sys.stderr)

    # 3. interactive-viewer shell
    iv_dist = TEMPLATES_ROOT / "interactive-viewer" / "dist"
    if iv_dist.exists():
        iv_dst = root / "interactive-viewer"
        _copy_dist(iv_dist, iv_dst)
        (iv_dst / "dashboard.json").write_text(
            json.dumps(interactive_skeleton(project_id=project_id), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[pre-bootup] interactive-viewer → {iv_dst}/index.html + dashboard.json", file=sys.stderr)
    else:
        print(f"[pre-bootup] WARN — {iv_dist} 부재, skip", file=sys.stderr)

    # 4. viewer-runtime scripts
    runtime_src = TEMPLATES_ROOT / "viewer-runtime"
    runtime_dst = root / "viewer-runtime"
    if runtime_src.exists():
        runtime_dst.mkdir(exist_ok=True)
        for f in runtime_src.iterdir():
            if f.is_file():
                shutil.copy2(f, runtime_dst / f.name)
        print(f"[pre-bootup] viewer-runtime/ scripts → {runtime_dst}/", file=sys.stderr)

    # 5. HTTP server 시작 (옵션)
    if not args.skip_server:
        cli = HARNESS_ROOT / "scoring" / "viewer_runtime.py"
        cmd = [sys.executable, str(cli), "up", "--root", str(root)]
        if args.port:
            cmd += ["--port", str(args.port)]
        if args.host:
            cmd += ["--host", args.host]
        subprocess.run(cmd, check=False)

    return 0


def cmd_teardown(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    cli = HARNESS_ROOT / "scoring" / "viewer_runtime.py"
    return subprocess.call([sys.executable, str(cli), "down", "--root", str(root)])


def cmd_emit_skeleton(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    kind = args.kind
    if kind == "lineage":
        out = root / "lineage.json"
        out.write_text(json.dumps(lineage_skeleton(project_id=root.name, grade=args.grade or "G4"), ensure_ascii=False, indent=2), encoding="utf-8")
    elif kind == "webview":
        out = root / "webview" / "data" / "webview.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(webview_skeleton(project_id=root.name), ensure_ascii=False, indent=2), encoding="utf-8")
    elif kind == "interactive":
        out = root / "interactive-viewer" / "dashboard.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(interactive_skeleton(project_id=root.name), ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(f"unknown kind: {kind}", file=sys.stderr)
        return 1
    print(f"[pre-bootup] skeleton emitted → {out}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="pre-cold-session bootup — phase 00 이전 viewer 부팅")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("bootstrap", help="dist 복사 + 빈 골격 JSON + viewer_runtime up")
    pb.add_argument("--root", required=True)
    pb.add_argument("--project-id", default=None)
    pb.add_argument("--grade", default="G4")
    pb.add_argument("--port", type=int, default=None)
    pb.add_argument("--host", default=None)
    pb.add_argument("--skip-server", action="store_true", help="HTTP server 시작 생략 (file:// 만 사용 시)")
    pb.set_defaults(func=cmd_bootstrap)

    pt = sub.add_parser("teardown", help="viewer_runtime down")
    pt.add_argument("--root", required=True)
    pt.set_defaults(func=cmd_teardown)

    pe = sub.add_parser("emit-skeleton", help="개별 viewer 의 빈 골격 JSON emit")
    pe.add_argument("--root", required=True)
    pe.add_argument("--kind", required=True, choices=["lineage", "webview", "interactive"])
    pe.add_argument("--grade", default="G4")
    pe.set_defaults(func=cmd_emit_skeleton)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
