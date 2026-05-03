#!/usr/bin/env python3
"""
리줌 도구 — resume.md 의 알고리즘 구현.

state.json + 인덱싱된 산출물을 읽어 현재 진행 상태 보고, 재개 진입점 결정,
무결성 검증.

명령:
    resume.py state    --root .ShipofTheseus/<프로젝트>/
    resume.py next     --root .ShipofTheseus/<프로젝트>/
    resume.py validate --root .ShipofTheseus/<프로젝트>/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# 페이즈 → 다음 페이즈 매핑 (선형 14 페이즈 default)
PHASE_ORDER = [
    "00-naming", "01-intent", "02-document", "03-independent-comprehension",
    "04-clarify", "05-critique", "06-plan", "07-plan-recursion",
    "08-implement", "09-quality-gates", "10-test-loop",
    "11-regression-bisect", "12-webview-assembly", "13-handoff",
]

# 페이즈 → 스킬 매핑 (v0.9.0 sprint-03-b — 7 phase 분해 stub 제거 후 모든 페이즈가
# theseus-orchestrator 단일 entry 로 resume).
PHASE_TO_SKILL = {p: "theseus-orchestrator" for p in PHASE_ORDER}


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.lower() in ("null", "none", "~", ""):
            v = None
        elif v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        out[k.strip()] = v
    return out


def _next_phase_after(phase: str | None) -> str | None:
    if phase is None:
        return PHASE_ORDER[0]
    if phase not in PHASE_ORDER:
        return None
    idx = PHASE_ORDER.index(phase)
    if idx + 1 >= len(PHASE_ORDER):
        return None   # 14 끝
    return PHASE_ORDER[idx + 1]


def _phase_to_skill(phase: str | None) -> str | None:
    if phase is None:
        return None
    return PHASE_TO_SKILL.get(phase)


def _scan_artifacts(root: Path) -> list[dict]:
    """모든 *.md 의 frontmatter 만 가볍게 스캔 — index_builder 와 일관."""
    out = []
    for p in sorted(root.rglob("*.md")):
        if "INDEX.md" in p.name:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        fm = _parse_frontmatter(text)
        if not fm.get("fingerprint"):
            continue
        out.append({
            "path": str(p.relative_to(root)),
            "phase": fm.get("phase"),
            "fingerprint": fm.get("fingerprint"),
            "prev_fingerprint": fm.get("prev_fingerprint"),
            "produced_at": fm.get("produced_at"),
        })
    return out


def _integrity(artifacts: list[dict]) -> dict:
    by_fp = {a["fingerprint"]: a for a in artifacts if a["fingerprint"]}
    breaks = []
    for a in artifacts:
        prev = a.get("prev_fingerprint")
        if prev and prev not in by_fp:
            breaks.append(a["path"])
    return {
        "fingerprint_chain": "ok" if not breaks else f"break: {breaks[:3]}",
        "total_artifacts": len(artifacts),
    }


def _detect_pending_partial(root: Path, state: dict) -> list[str]:
    incomplete = []
    for entry in state.get("pending_artifacts", []) or []:
        # entry 형식: "impl/T-020/sub/A.1/code.go (in_progress)"
        path_part = entry.split(" (")[0]
        full = root / path_part
        if not full.exists():
            continue
        try:
            text = full.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            incomplete.append(path_part)
            continue
        fm = _parse_frontmatter(text)
        if not fm.get("fingerprint"):
            incomplete.append(path_part)
    return incomplete


def cmd_state(args) -> int:
    root = Path(args.root)
    state = _read_json(root / "state.json")
    if state is None:
        out = {
            "ok": False,
            "reason": "state.json 없음 — 본 프로젝트가 아직 시작 안 됐거나 자동 갱신 누락",
        }
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 1
    json.dump(state, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_validate(args) -> int:
    root = Path(args.root)
    state = _read_json(root / "state.json")
    artifacts = _scan_artifacts(root)
    integrity = _integrity(artifacts)
    incomplete = _detect_pending_partial(root, state or {})

    ok = (
        state is not None
        and integrity["fingerprint_chain"] == "ok"
        and not incomplete
    )
    out = {
        "ok": ok,
        "state_present": state is not None,
        "integrity": integrity,
        "incomplete_pending": incomplete,
        "discard_recommended": incomplete,   # resume.md §"부분 산출물 처리"
        "artifact_count": len(artifacts),
    }
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if ok else 1


def cmd_next(args) -> int:
    root = Path(args.root)
    state = _read_json(root / "state.json")
    artifacts = _scan_artifacts(root)
    integrity = _integrity(artifacts)

    if state is None:
        out = {
            "ok": True,
            "action": "fresh_start",
            "reason": "state.json 없음 — 처음부터 시작",
            "entry_skill": "theseus-orchestrator",
            "entry_input": "<사용자 원문>",
        }
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    if integrity["fingerprint_chain"].startswith("break"):
        out = {
            "ok": False,
            "action": "repair_required",
            "reason": "fingerprint 체인 끊김 — 사용자 ack 필요 (인터럽트 0 의 유일 추가 예외)",
            "integrity": integrity,
        }
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 1

    incomplete = _detect_pending_partial(root, state)
    if incomplete:
        last_completed = state.get("last_completed_artifact")
        active_skill = state.get("active_skill") or _phase_to_skill(state.get("current_phase"))
        out = {
            "ok": True,
            "action": "discard_incomplete_then_resume",
            "discard_files": incomplete,
            "entry_skill": active_skill,
            "entry_input": last_completed,
            "current_phase_retry": state.get("current_phase"),
            "reason": f"부분 산출물 {len(incomplete)} 개 폐기 후 {active_skill} 재시작",
        }
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    last_phase = state.get("last_completed_phase")
    next_phase = _next_phase_after(last_phase)
    if next_phase is None:
        out = {
            "ok": True,
            "action": "already_complete",
            "reason": "모든 페이즈 완료 — 핸드오프까지 끝남. resume 불필요.",
        }
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    out = {
        "ok": True,
        "action": "resume_next_phase",
        "entry_skill": _phase_to_skill(next_phase),
        "entry_input": state.get("last_completed_artifact"),
        "next_phase": next_phase,
        "last_completed_phase": last_phase,
        "reason": f"마지막 완료 페이즈 {last_phase} → 다음 {next_phase}",
        "resume_command": (
            f"/{_phase_to_skill(next_phase)} --from {root}/"
        ),
    }
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("state", "validate", "next"):
        sp = sub.add_parser(name)
        sp.add_argument("--root", required=True)
        sp.set_defaults(func=globals()[f"cmd_{name}"])
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
