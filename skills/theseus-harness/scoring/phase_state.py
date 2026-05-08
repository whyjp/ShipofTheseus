#!/usr/bin/env python3
"""
페이즈 진행 상태 머신 — runtime 단조성 게이트 (sprint-34 / v0.9.39).

orchestrator 가 매 페이즈 enter/exit 시점에 호출. `.ShipofTheseus/<proj>/state/phase_state.json`
에 페이즈 진입/종료 시각 + 산출물 frontmatter `created_at` + fingerprint 를 누적.
이후 페이즈 진입 시 단조성 (entered_at strict-monotonic) + frontmatter cross-check
를 검증해 v0.9.22 의 백필/위조 (페이즈 01-06 사후 frontmatter 9-12 분 위조) 를
runtime 시점에 차단한다.

`check_cold_session.py` 가 *post-hoc* artifact 검사를 한다면, 본 모듈은 *runtime
entry-time* gate — 두 layer 가 상보적.

명령:
    phase_state.py init --root <proj> --grade G [--project-id ID]
    phase_state.py enter --root <proj> --phase NN --producer <agent>
    phase_state.py exit  --root <proj> --phase NN --fingerprint sha256:<hex>
                         --outcome ok|fail [--artifact-path naming/00-naming.md]
    phase_state.py validate --root <proj>
        # 단조성 + frontmatter created_at cross-check + chain 검증
        # exit 0 = PASS, exit 1 = violations (stderr 에 위반 목록)
    phase_state.py status --root <proj>
        # 현재 상태 JSON 덤프
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Windows console cp949 → 한글 stderr mojibake 방지 (subprocess UTF-8 capture 정합)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SCHEMA_VERSION = 1
STATE_FILENAME = "phase_state.json"
KNOWN_PHASES = [f"{i:02d}" for i in range(0, 15)]   # 00..14


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _state_path(root: Path) -> Path:
    return root / "state" / STATE_FILENAME


def _load(root: Path) -> dict:
    p = _state_path(root)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _save(root: Path, state: dict) -> None:
    p = _state_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def cmd_init(args) -> int:
    root = Path(args.root)
    if _state_path(root).exists():
        print(f"phase_state.json 이미 존재: {_state_path(root)}", file=sys.stderr)
        return 1
    state = {
        "schema_version": SCHEMA_VERSION,
        "project_id": args.project_id or root.name,
        "grade": args.grade,
        "started_at": _utcnow_iso(),
        "current_phase": None,
        "current_status": "idle",
        "phases": [],
    }
    _save(root, state)
    json.dump({"ok": True, "state_path": str(_state_path(root))}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_enter(args) -> int:
    root = Path(args.root)
    state = _load(root)
    if not state:
        print("phase_state.json 부재 — init 먼저 호출", file=sys.stderr)
        return 1

    phase = args.phase
    if phase not in KNOWN_PHASES:
        print(f"unknown phase: {phase} (allowed: {KNOWN_PHASES})", file=sys.stderr)
        return 1

    # 진행 중 페이즈 동시 1 개 — 새 enter 호출 시 직전이 in_progress 면 fail (단조성 검증보다 먼저)
    if state.get("current_status") == "in_progress":
        print(
            f"이전 페이즈 ({state['current_phase']}) in_progress — exit 후 enter (current_status=in_progress)",
            file=sys.stderr,
        )
        return 1

    now = _utcnow_iso()
    now_dt = _parse_iso(now)

    # 단조성 — entered_at 가 직전 모든 항목 entered_at/exited_at 보다 strict-greater
    for prev in state["phases"]:
        for key in ("entered_at", "exited_at"):
            if prev.get(key):
                prev_dt = _parse_iso(prev[key])
                if not (now_dt > prev_dt):
                    print(
                        f"단조성 위반: phase {phase} entered_at {now} ≤ phase {prev['phase']} {key}={prev[key]}",
                        file=sys.stderr,
                    )
                    return 1

    state["phases"].append({
        "phase": phase,
        "status": "in_progress",
        "entered_at": now,
        "exited_at": None,
        "duration_seconds": None,
        "fingerprint": None,
        "producer": args.producer,
        "outcome": None,
        "artifact_path": None,
        "frontmatter_created_at": None,
    })
    state["current_phase"] = phase
    state["current_status"] = "in_progress"
    _save(root, state)

    json.dump({"ok": True, "phase": phase, "entered_at": now}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def _read_frontmatter_created_at(artifact: Path) -> str | None:
    if not artifact.exists():
        return None
    text = artifact.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fm = text[4:end]
    m = re.search(r"^created_at:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", fm, re.M)
    if not m:
        # 일부 산출물은 produced_at 사용
        m = re.search(r"^produced_at:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", fm, re.M)
    return m.group(1).strip() if m else None


def cmd_exit(args) -> int:
    root = Path(args.root)
    state = _load(root)
    if not state:
        print("phase_state.json 부재", file=sys.stderr)
        return 1

    phase = args.phase
    # 가장 최근 in_progress 항목 찾기
    target = None
    for p in reversed(state["phases"]):
        if p["phase"] == phase and p["status"] == "in_progress":
            target = p
            break
    if target is None:
        print(f"phase {phase} in_progress 항목 부재", file=sys.stderr)
        return 1

    now = _utcnow_iso()
    now_dt = _parse_iso(now)
    entered_dt = _parse_iso(target["entered_at"])
    if not (now_dt > entered_dt):
        # 시계 역행 등 비정상
        print(f"exit_at {now} ≤ entered_at {target['entered_at']}", file=sys.stderr)
        return 1

    target["status"] = "completed" if args.outcome == "ok" else "failed"
    target["exited_at"] = now
    target["duration_seconds"] = int((now_dt - entered_dt).total_seconds())
    target["fingerprint"] = args.fingerprint
    target["outcome"] = args.outcome
    target["artifact_path"] = args.artifact_path

    # frontmatter created_at cross-check
    if args.artifact_path:
        ap = root / args.artifact_path
        fm_created = _read_frontmatter_created_at(ap)
        target["frontmatter_created_at"] = fm_created
        if fm_created:
            try:
                fm_dt = _parse_iso(fm_created)
                # frontmatter created_at 은 [entered_at, exited_at] 안이어야 정상.
                # 외부 = forgery (사후 백필) 또는 시계 drift.
                if not (entered_dt <= fm_dt <= now_dt):
                    print(
                        f"frontmatter forgery 의심: {args.artifact_path} "
                        f"created_at={fm_created} 가 [{target['entered_at']}, {now}] 범위 밖",
                        file=sys.stderr,
                    )
                    return 1
            except ValueError:
                # 비표준 시각 포맷 — 경고만
                pass

    state["current_phase"] = phase
    state["current_status"] = "idle"
    _save(root, state)

    json.dump({"ok": True, "phase": phase, "exited_at": now, "duration_seconds": target["duration_seconds"]},
              sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def validate_state(root: Path) -> list[str]:
    """단조성 + frontmatter cross-check + chain 검증. 위반 목록 반환 (빈 리스트 = PASS)."""
    state = _load(root)
    if not state:
        return ["phase_state.json 부재"]

    issues: list[str] = []
    last_dt: datetime | None = None
    for p in state["phases"]:
        ph = p["phase"]
        ent = p.get("entered_at")
        exi = p.get("exited_at")

        if ent is None:
            issues.append(f"phase {ph}: entered_at 누락")
            continue

        try:
            ent_dt = _parse_iso(ent)
        except ValueError:
            issues.append(f"phase {ph}: entered_at 비표준 포맷 ({ent})")
            continue

        if last_dt is not None and not (ent_dt > last_dt):
            issues.append(
                f"단조성 위반: phase {ph} entered_at {ent} ≤ 직전 timestamp {last_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            )

        if exi:
            try:
                exi_dt = _parse_iso(exi)
            except ValueError:
                issues.append(f"phase {ph}: exited_at 비표준 포맷 ({exi})")
                continue
            if not (exi_dt > ent_dt):
                issues.append(f"phase {ph}: exited_at {exi} ≤ entered_at {ent}")
            last_dt = exi_dt
        else:
            last_dt = ent_dt

        # frontmatter created_at cross-check
        ap_str = p.get("artifact_path")
        fm = p.get("frontmatter_created_at")
        if ap_str and fm:
            try:
                fm_dt = _parse_iso(fm)
                ub = _parse_iso(exi) if exi else None
                if ub is not None:
                    if not (ent_dt <= fm_dt <= ub):
                        issues.append(
                            f"phase {ph}: frontmatter forgery 의심 — "
                            f"{ap_str} created_at={fm} not in [{ent}, {exi}]"
                        )
            except ValueError:
                pass

    # current_status 일관성
    cur_status = state.get("current_status")
    if cur_status == "in_progress":
        last = state["phases"][-1] if state["phases"] else None
        if not last or last.get("status") != "in_progress":
            issues.append("current_status=in_progress 인데 마지막 phase 가 in_progress 아님")

    return issues


def cmd_validate(args) -> int:
    issues = validate_state(Path(args.root))
    if issues:
        print(f"FAIL — {len(issues)} phase_state violation(s):", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)
        return 1
    json.dump({"ok": True, "violations": []}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_status(args) -> int:
    state = _load(Path(args.root))
    json.dump(state, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pi = sub.add_parser("init", help="phase_state.json 초기화")
    pi.add_argument("--root", required=True)
    pi.add_argument("--grade", required=True, choices=["G1", "G2", "G3", "G4", "G5"])
    pi.add_argument("--project-id", default=None)
    pi.set_defaults(func=cmd_init)

    pe = sub.add_parser("enter", help="페이즈 진입 기록")
    pe.add_argument("--root", required=True)
    pe.add_argument("--phase", required=True)
    pe.add_argument("--producer", required=True)
    pe.set_defaults(func=cmd_enter)

    px = sub.add_parser("exit", help="페이즈 종료 기록 + frontmatter cross-check")
    px.add_argument("--root", required=True)
    px.add_argument("--phase", required=True)
    px.add_argument("--fingerprint", required=True)
    px.add_argument("--outcome", required=True, choices=["ok", "fail"])
    px.add_argument("--artifact-path", default=None)
    px.set_defaults(func=cmd_exit)

    pv = sub.add_parser("validate", help="단조성 + cross-check 전체 검증")
    pv.add_argument("--root", required=True)
    pv.set_defaults(func=cmd_validate)

    ps = sub.add_parser("status", help="현재 상태 덤프")
    ps.add_argument("--root", required=True)
    ps.set_defaults(func=cmd_status)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
