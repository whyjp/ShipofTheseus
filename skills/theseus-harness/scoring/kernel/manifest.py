#!/usr/bin/env python3
"""Pipeline Manifest — 파이프라인 스펙의 유일 권위 소스 로더 (설계 §6, §11.3).

`pipeline.manifest.json` 하나가 페이즈 열거·그레이드별 활성 폭·그레이드별 활성
CheckSpec ID 를 정의하고, 러너·메타 감사·문서가 *같은 파일* 을 읽는다. 스펙이 두
곳에 있으면 그것은 스펙이 아니라 드리프트다(§2 원칙3).

WHY 스칼라 '페이즈 수'가 없나: 페이즈는 phases 리스트로 *열거* 된다 — 리스트 길이가
곧 개수다. 별도 count 필드를 두면 리스트와 어긋나 14/15/16 드리프트가 재발한다.

`drift_check` 는 매니페스트가 참조하는 모든 check_id 가 레지스트리 파일로 실재하는지,
그리고 레지스트리에 있으나 매니페스트에 없는 orphan 이 없는지를 값으로 판정한다 —
WP3 의 meta_audit 가 이 결과 위에서 '선언되고 감사 안 되는 체크는 존재 불가'를 세운다.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# 맵(widths/checks)에서 '_' 로 시작하는 키는 인라인 주석·메타데이터 — 그레이드가 아니다.
# JSON 이 문서를 품되 그레이드 맵을 오염시키지 않도록 로드 시 걸러낸다.
_META_PREFIX = "_"

_REQUIRED_TOP_FIELDS = (
    "manifest_schema_version",
    "phases",
    "multiverse_widths",
    "frozen_widths",
    "checks",
)


class ManifestError(ValueError):
    """매니페스트 로드/형태 검증 실패."""


@dataclass
class Manifest:
    """`pipeline.manifest.json` 의 기계 판독 캐리어.

    widths/checks 맵은 '_' 접두 메타 키를 제거한 순수 그레이드→값 맵으로 정규화한다.
    phases 는 원본 dict 리스트를 그대로 보존한다(id/name/active_grades) — 소비자가
    위치가 아니라 id 로 키잉하도록.
    """

    manifest_schema_version: str
    phases: list[dict[str, Any]]
    multiverse_widths: dict[str, int]
    frozen_widths: dict[str, int]
    checks: dict[str, list[str]]
    raw: dict[str, Any] = field(default_factory=dict, repr=False)


def _grade_map(raw: Any, field_name: str) -> dict[str, Any]:
    """widths/checks 맵을 dict 로 검증하고 '_' 메타 키를 제거."""
    if not isinstance(raw, dict):
        raise ManifestError(f"{field_name} must be an object")
    return {k: v for k, v in raw.items() if not k.startswith(_META_PREFIX)}


def from_dict(data: Any) -> Manifest:
    """dict → Manifest. 필수 필드 결손·타입오류 시 ManifestError."""
    if not isinstance(data, dict):
        raise ManifestError("manifest root is not a JSON object")
    for fname in _REQUIRED_TOP_FIELDS:
        if fname not in data:
            raise ManifestError(f"missing field: {fname}")

    phases_raw = data["phases"]
    if not isinstance(phases_raw, list):
        raise ManifestError("phases must be an array")
    phases: list[dict[str, Any]] = []
    for i, p in enumerate(phases_raw):
        if not isinstance(p, dict):
            raise ManifestError(f"phases[{i}] is not an object")
        for key in ("id", "name", "active_grades"):
            if key not in p:
                raise ManifestError(f"phases[{i}] missing '{key}'")
        if not isinstance(p["active_grades"], list):
            raise ManifestError(f"phases[{i}].active_grades must be an array")
        phases.append(p)

    widths = _grade_map(data["multiverse_widths"], "multiverse_widths")
    frozen = _grade_map(data["frozen_widths"], "frozen_widths")
    checks_raw = _grade_map(data["checks"], "checks")
    checks: dict[str, list[str]] = {}
    for grade, ids in checks_raw.items():
        if not isinstance(ids, list):
            raise ManifestError(f"checks[{grade}] must be an array")
        checks[grade] = list(ids)

    return Manifest(
        manifest_schema_version=data["manifest_schema_version"],
        phases=phases,
        multiverse_widths={k: int(v) for k, v in widths.items()},
        frozen_widths={k: int(v) for k, v in frozen.items()},
        checks=checks,
        raw=data,
    )


def load_manifest(path: str | Path) -> Manifest:
    """경로에서 매니페스트 로드. 부재/파싱불가/구조결손 → ManifestError."""
    p = Path(path)
    if not p.exists():
        raise ManifestError(f"manifest file not found: {p}")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifestError(f"manifest not parseable JSON: {p}: {exc}") from exc
    return from_dict(data)


# --- 질의 API (WP3 meta_audit 가 이 이름들을 import 한다) -----------------------


def active_checks(manifest: Manifest, grade: str) -> list[str]:
    """해당 그레이드에서 활성인 CheckSpec ID 목록. 미정의 그레이드는 빈 리스트."""
    return list(manifest.checks.get(grade, []))


def phases_for_grade(manifest: Manifest, grade: str) -> list[dict[str, Any]]:
    """해당 그레이드가 active_grades 에 포함된 페이즈만, 매니페스트 순서대로."""
    return [p for p in manifest.phases if grade in p["active_grades"]]


def multiverse_width(manifest: Manifest, grade: str) -> int:
    """해당 그레이드의 실제 강제 멀티버스 폭.

    미정의 그레이드는 조용한 default 를 내지 않고 ManifestError — '무노동 만점'류
    silent default(설계 P1)를 폭 질의에서도 구조적으로 배제한다.
    """
    if grade not in manifest.multiverse_widths:
        raise ManifestError(f"no multiverse width defined for grade: {grade!r}")
    return manifest.multiverse_widths[grade]


def _referenced_check_ids(manifest: Manifest) -> set[str]:
    """매니페스트가 모든 그레이드에 걸쳐 참조하는 check_id 합집합."""
    refs: set[str] = set()
    for ids in manifest.checks.values():
        refs.update(ids)
    return refs


def drift_check(manifest: Manifest, checks_dir: str | Path) -> list[str]:
    """매니페스트 ↔ 레지스트리 정합 검사. 문제 목록 반환(빈 리스트 = 정합).

    두 방향을 값으로 판정한다:
      - 매니페스트가 참조하는 모든 check_id 가 `checks_dir/<id>.json` 파일로 실재하는가.
      - 레지스트리 파일 중 매니페스트가 참조하지 않는 orphan 이 있는가.
    결정성(§2 원칙5)을 위해 문제를 정렬해 반환한다.
    """
    problems: list[str] = []
    checks_root = Path(checks_dir)
    referenced = _referenced_check_ids(manifest)

    # 방향1 — 참조된 check_id 가 파일로 실재?
    for check_id in referenced:
        spec_path = checks_root / f"{check_id}.json"
        if not spec_path.exists():
            problems.append(
                f"missing registry file for check '{check_id}': {spec_path}"
            )

    # 방향2 — orphan(파일은 있으나 매니페스트가 참조 안 함) 탐지.
    if checks_root.is_dir():
        for spec_file in checks_root.glob("*.json"):
            file_id = spec_file.stem
            if file_id not in referenced:
                problems.append(
                    f"orphan registry file not referenced in manifest: {spec_file.name}"
                )

    return sorted(problems)


# --- CLI -----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline Manifest — 로더 + 매니페스트↔레지스트리 드리프트 체크"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    d = sub.add_parser("drift-check", help="매니페스트 ↔ checks/ 레지스트리 정합")
    d.add_argument("--manifest", required=True, help="pipeline.manifest.json 경로")
    d.add_argument("--checks-dir", required=True, help="CheckSpec 레지스트리 디렉터리")
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    problems = drift_check(manifest, args.checks_dir)
    json.dump(
        {"ok": not problems, "problems": problems},
        sys.stdout,
        indent=2,
        ensure_ascii=False,
    )
    sys.stdout.write("\n")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
