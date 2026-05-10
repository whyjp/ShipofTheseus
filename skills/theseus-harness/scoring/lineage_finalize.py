#!/usr/bin/env python3
"""lineage_finalize.py — Viewer Finalization Closure CLI (sprint-52 PR-B v0.9.52).

phase 14-handoff 진입 후 호출되어 cold session 의 viewer 3 종을 *실 데이터* 로 refresh:

1. `<root>/lineage.json` — phases / fingerprint_chain / mermaid_flowchart / mermaid_gantt /
   project_run / final_outcome / duration_seconds / phases_completed / winner
2. `<root>/interactive-viewer/dashboard.json` — current_phase / final_phase
3. `<root>/webview/data/webview.json` — final_phase / timing.duration_seconds /
   timing.phases_completed

본 CLI 는 `pre_bootup.py` 가 시작 시 박은 *빈 골격* (mermaid="cold session 미시작" /
fingerprint_chain=[] / project_run="pending") 의 sink 페이즈 책임자.

설계:
- `.ShipofTheseus/` 재귀 스캔, 모든 *.md 의 frontmatter 추출
- created_at None / 정시 stub (T..:00:00Z) 감지 → mtime fallback (WARN 카운트)
- fingerprint PENDING 인 파일은 chain 재계산 (fingerprint.py compute 동등 로직)
- 도메인 무관 — 모든 cold session 적용

명령:
    lineage_finalize.py refresh --root <project_dir> [--dry-run] [--strict]

옵션:
    --dry-run : 변경 미적용 — 변경 사항 JSON 출력만
    --strict  : created_at stub / fingerprint PENDING 잔존 시 exit 1

Exit codes:
    0 — refresh 성공 (또는 --dry-run report)
    1 — strict 모드에서 stub/PENDING 잔존 / 의무 입력 부재 / IO 오류
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# fingerprint.py 와 같은 디렉토리에서 import
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from fingerprint import compute_fingerprint, parse_frontmatter  # noqa: E402

SCHEMA_VERSION = "0.9.52"

# 정시 stub (created_at 끝이 :00:00Z 또는 :00Z) — 분/초 단위까지 정시
STUB_TS_RE = re.compile(r":00:00Z?$|T\d{2}:00Z?$")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _is_stub_ts(ts: str | None) -> bool:
    if ts is None:
        return True
    return bool(STUB_TS_RE.search(ts))


def _file_mtime_iso(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def _phase_label(fm: dict, file_rel: str) -> str:
    """frontmatter phase + universe 결합 라벨."""
    phase = fm.get("phase") or "<unknown>"
    universe = fm.get("universe")
    if universe and "candidate" in phase or universe and "cold-read" in phase:
        return f"{phase}@{universe}"
    return phase


def scan_phase_files(root: Path) -> list[dict]:
    """`<root>/.ShipofTheseus/` 재귀 스캔 — *.md frontmatter + 본문 추출."""
    sot = root / ".ShipofTheseus"
    if not sot.is_dir():
        return []
    rows = []
    for p in sorted(sot.rglob("*.md")):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception as exc:
            rows.append({
                "file": str(p.relative_to(root)).replace("\\", "/"),
                "error": f"read failed: {exc}",
            })
            continue
        fm, body = parse_frontmatter(text)
        rel = str(p.relative_to(root)).replace("\\", "/")
        rows.append({
            "file": rel,
            "abs": p,
            "fm": fm,
            "body": body,
            "mtime_iso": _file_mtime_iso(p),
        })
    return rows


def _coerce_created_at(row: dict, warn_counter: list[int]) -> str:
    fm = row.get("fm") or {}
    ca = fm.get("created_at")
    if not _is_stub_ts(ca):
        return ca  # 실제 timestamp
    warn_counter[0] += 1
    return row["mtime_iso"]  # fallback


def build_phase_entry(row: dict, prev_fp: str, warn_counter: list[int]) -> dict:
    """row → lineage.json phases[] entry."""
    fm = row.get("fm") or {}
    body = row.get("body") or ""
    phase_label = _phase_label(fm, row["file"])
    created_at = _coerce_created_at(row, warn_counter)
    fp = fm.get("fingerprint")
    if not fp or fp == "PENDING":
        # chain 재계산 — fingerprint.py 의 compute_fingerprint 사용
        # prev_fingerprint 는 chain 위치 기반
        cf_fm = dict(fm)
        cf_fm["prev_fingerprint"] = prev_fp
        fp = compute_fingerprint(cf_fm, body)[: len("sha256:") + 16]  # 16자 prefix
    return {
        "phase": phase_label,
        "file": row["file"],
        "fingerprint": fp,
        "prev_fingerprint": prev_fp,
        "created_at": created_at,
        "status": fm.get("status") or "complete",
        "universe": fm.get("universe"),
    }


def render_mermaid_flowchart(phases: list[dict]) -> str:
    nodes = []
    edges = []
    for i, ph in enumerate(phases):
        label = ph["phase"].replace('"', "'")
        nodes.append(f'  P{i}["{label}"]')
    for i in range(1, len(phases)):
        edges.append(f"  P{i-1} --> P{i}")
    return "flowchart TB\n" + "\n".join(nodes + edges)


def render_mermaid_gantt(phases: list[dict]) -> str:
    lines = [
        "gantt",
        "  title Phase Lineage — completed",
        "  dateFormat YYYY-MM-DD HH:mm:ss",
        "  axisFormat %H:%M",
        "  section phases",
    ]
    for i, ph in enumerate(phases):
        ts = (ph["created_at"] or "").replace("T", " ").replace("Z", "")
        safe = ph["phase"].replace(":", "_").replace("@", "-")
        lines.append(f"  {safe} :p{i}, {ts}, 30s")
    return "\n".join(lines)


def find_winner(rows: list[dict]) -> dict | None:
    """tournament-NN.md frontmatter 에서 winner 추출.

    검색 키 (sprint-50/51 frontmatter 정합): winner_universe / winner_id / winner.
    score 키: winner_score_ratio / winner_ratio / ratio.
    """
    for row in rows:
        rel = row.get("file", "")
        if "/plan/tournament-" not in rel:
            continue
        fm = row.get("fm") or {}
        wid = fm.get("winner_universe") or fm.get("winner_id") or fm.get("winner")
        if not wid:
            continue
        return {
            "source": Path(rel).stem,
            "universe": wid,
            "philosophy": fm.get("winner_philosophy") or fm.get("philosophy"),
            "ratio": fm.get("winner_score_ratio") or fm.get("winner_ratio") or fm.get("ratio"),
        }
    return None


def refresh_lineage(root: Path, dry_run: bool, strict: bool) -> dict:
    lineage_path = root / "lineage.json"
    if not lineage_path.exists():
        raise SystemExit(f"lineage.json not found: {lineage_path}")
    lin = json.loads(lineage_path.read_text(encoding="utf-8"))

    rows = scan_phase_files(root)
    if not rows:
        raise SystemExit(f".ShipofTheseus/ phase artifacts not found under {root}")

    warn = [0]  # created_at stub fallback 카운트
    rows_sorted = sorted(rows, key=lambda r: _coerce_created_at(r, [0]))
    phases: list[dict] = []
    prev_fp = "GENESIS"
    for row in rows_sorted:
        if "error" in row:
            continue
        entry = build_phase_entry(row, prev_fp, warn)
        phases.append(entry)
        prev_fp = entry["fingerprint"]

    chain = [
        {"phase": p["phase"], "fingerprint": p["fingerprint"], "prev_fingerprint": p["prev_fingerprint"]}
        for p in phases
    ]

    started = lin.get("started_at_iso")
    ended = lin.get("ended_at_iso")
    if started and ended:
        duration = round((_parse_iso(ended) - _parse_iso(started)).total_seconds(), 2)
    else:
        duration = lin.get("duration_seconds", 0.0)

    lin["project_run"] = "completed"
    lin["final_outcome"] = "DONE"
    lin["duration_seconds"] = duration
    lin["phases_completed"] = len(phases)
    lin["phases"] = phases
    lin["fingerprint_chain"] = chain
    lin["mermaid_flowchart"] = render_mermaid_flowchart(phases)
    lin["mermaid_gantt"] = render_mermaid_gantt(phases)
    if lin.get("winner") in (None, ""):
        winner = find_winner(rows)
        if winner:
            lin["winner"] = winner

    final_phase = lin.get("final_phase") or (phases[-1]["phase"] if phases else None)
    lin["final_phase"] = final_phase

    if not dry_run:
        lineage_path.write_text(json.dumps(lin, indent=2, ensure_ascii=False), encoding="utf-8")

    report = {
        "lineage_path": str(lineage_path),
        "phases_completed": len(phases),
        "duration_seconds": duration,
        "final_phase": final_phase,
        "winner": lin.get("winner"),
        "created_at_fallback_count": warn[0],
        "dry_run": dry_run,
    }

    if strict and warn[0] > 0:
        report["strict_violation"] = f"{warn[0]} phase 의 created_at 이 stub/None"
    return report


def refresh_dashboard(root: Path, final_phase: str, dry_run: bool) -> dict | None:
    p = root / "interactive-viewer" / "dashboard.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text(encoding="utf-8"))
    d["current_phase"] = final_phase
    d["final_phase"] = final_phase
    if not dry_run:
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"dashboard_path": str(p), "final_phase": final_phase}


def refresh_webview(root: Path, final_phase: str, phases_completed: int, dry_run: bool) -> dict | None:
    p = root / "webview" / "data" / "webview.json"
    if not p.exists():
        return None
    w = json.loads(p.read_text(encoding="utf-8"))
    timing = w.setdefault("timing", {})
    started = timing.get("started_at")
    ended = timing.get("ended_at")
    if started and ended:
        timing["duration_seconds"] = round(
            (_parse_iso(ended) - _parse_iso(started)).total_seconds(), 2
        )
    timing["phases_completed"] = phases_completed
    w["final_phase"] = final_phase
    if not dry_run:
        p.write_text(json.dumps(w, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "webview_path": str(p),
        "final_phase": final_phase,
        "duration_seconds": timing.get("duration_seconds"),
        "phases_completed": phases_completed,
    }


def cmd_refresh(args) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"root not a dir: {root}"}, ensure_ascii=False))
        return 1
    lin_report = refresh_lineage(root, args.dry_run, args.strict)
    final_phase = lin_report["final_phase"]
    dash_report = refresh_dashboard(root, final_phase, args.dry_run)
    wv_report = refresh_webview(root, final_phase, lin_report["phases_completed"], args.dry_run)

    out = {
        "schema_version": SCHEMA_VERSION,
        "lineage": lin_report,
        "dashboard": dash_report,
        "webview": wv_report,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))

    if args.strict and lin_report.get("strict_violation"):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lineage_finalize.py")
    sub = parser.add_subparsers(dest="cmd", required=True)
    pr = sub.add_parser("refresh", help="lineage / dashboard / webview JSON refresh")
    pr.add_argument("--root", required=True, help="project / submission root dir")
    pr.add_argument("--dry-run", action="store_true")
    pr.add_argument("--strict", action="store_true",
                    help="created_at stub 또는 fingerprint PENDING 잔존 시 exit 1")
    pr.set_defaults(func=cmd_refresh)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
