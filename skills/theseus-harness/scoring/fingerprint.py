#!/usr/bin/env python3
"""
산출물 핑거프린트 계산·검증.

frontmatter 스펙은 conventions/contracts.md 참조.

사용법:
    fingerprint.py compute --file <md> --prev <prev-md|none> --skill-version <semver>
        # frontmatter 의 fingerprint 와 prev_fingerprint 를 채워 in-place 저장.
    fingerprint.py verify --file <md>
        # 저장된 fingerprint 가 본문과 일치하는지 검증. 일치 시 exit 0, 아니면 1.
    fingerprint.py chain --dir <dir>
        # 디렉터리의 모든 마크다운에 대해 prev_fingerprint 체인 무결성 검증.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TIMING_HEADER_RE = re.compile(r"\A>\s*\*\*시작:\*\*.*?\n(>.*\n)*", re.MULTILINE)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """미니멀 YAML 파싱 — `key: value` 한 줄짜리만 처리. 본 스킬 내부 용도."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end() :]
    fm: dict = {}
    for line in raw.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.lower() in ("null", "none", "~"):
            v = None
        elif v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        fm[k.strip()] = v
    return fm, body


def render_frontmatter(fm: dict) -> str:
    lines = ["---"]
    for k in [
        "skill_name",
        "skill_version",
        "phase",
        "project_id",
        "project_run",
        "fingerprint",
        "prev_fingerprint",
        "produced_at",
        "producer_agent",
    ]:
        if k in fm:
            v = fm[k]
            if v is None:
                lines.append(f"{k}: null")
            else:
                lines.append(f"{k}: {v}")
    # 표준 외 키 보존
    for k, v in fm.items():
        if k in {
            "skill_name",
            "skill_version",
            "phase",
            "project_id",
            "project_run",
            "fingerprint",
            "prev_fingerprint",
            "produced_at",
            "producer_agent",
        }:
            continue
        lines.append(f"{k}: {v if v is not None else 'null'}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def canonical_body(body: str) -> str:
    """timing 헤더와 후행 공백 제거, 행 끝 정규화."""
    body = TIMING_HEADER_RE.sub("", body, count=1)
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in body.split("\n")).strip() + "\n"


def major_of(version: str) -> str:
    return version.split(".", 1)[0]


def compute_fingerprint(fm: dict, body: str) -> str:
    payload = "\n".join(
        [
            fm.get("skill_name", ""),
            major_of(fm.get("skill_version", "0")),
            fm.get("phase", ""),
            fm.get("project_id", ""),
            fm.get("project_run", ""),
            fm.get("prev_fingerprint") or "null",
            canonical_body(body),
        ]
    )
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def cmd_compute(args) -> int:
    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    if args.skill_version:
        fm["skill_version"] = args.skill_version
    if args.prev and args.prev.lower() != "none":
        prev_fm, _ = parse_frontmatter(Path(args.prev).read_text(encoding="utf-8"))
        fm["prev_fingerprint"] = prev_fm.get("fingerprint")
    elif args.prev and args.prev.lower() == "none":
        fm["prev_fingerprint"] = None
    fm["fingerprint"] = compute_fingerprint(fm, body)
    path.write_text(render_frontmatter(fm) + body, encoding="utf-8")
    print(json.dumps({"file": str(path), "fingerprint": fm["fingerprint"]}, ensure_ascii=False))
    return 0


def cmd_verify(args) -> int:
    path = Path(args.file)
    text = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)
    expected = fm.get("fingerprint")
    if not expected:
        print(json.dumps({"file": str(path), "ok": False, "reason": "fingerprint 없음"}, ensure_ascii=False))
        return 1
    actual = compute_fingerprint({**fm, "fingerprint": None}, body)
    ok = actual == expected
    print(
        json.dumps(
            {"file": str(path), "ok": ok, "expected": expected, "actual": actual},
            ensure_ascii=False,
        )
    )
    return 0 if ok else 1


def cmd_chain(args) -> int:
    root = Path(args.dir)
    files = sorted(root.rglob("*.md"))
    by_fp: dict[str, dict] = {}
    issues: list[str] = []
    for p in files:
        fm, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        fp = fm.get("fingerprint")
        if not fp:
            continue  # 비-페이즈 마크다운(README 등) 은 무시
        by_fp[fp] = {"path": str(p), "prev": fm.get("prev_fingerprint")}
    for fp, info in by_fp.items():
        prev = info["prev"]
        if prev is None or prev == "null":
            continue
        if prev not in by_fp:
            issues.append(f"{info['path']} 의 prev_fingerprint {prev} 매칭 산출물 없음 (체인 끊김)")
    print(json.dumps({"files": len(by_fp), "issues": issues}, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("compute")
    pc.add_argument("--file", required=True)
    pc.add_argument("--prev", default=None, help="직전 페이즈 산출물 경로 또는 'none'")
    pc.add_argument("--skill-version", default=None)
    pc.set_defaults(func=cmd_compute)

    pv = sub.add_parser("verify")
    pv.add_argument("--file", required=True)
    pv.set_defaults(func=cmd_verify)

    pch = sub.add_parser("chain")
    pch.add_argument("--dir", required=True)
    pch.set_defaults(func=cmd_chain)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
