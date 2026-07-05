#!/usr/bin/env python3
"""measure_intent_fidelity.py — gate.intent_fidelity 증거 조립기 (판단-게이트 스펙 §3.2).

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다. 상류 선언 아티팩트
(`intent-criteria.json`, phase 01/04 저작)는 "무엇을 볼지"(backing.ref)만 담고,
판정 필드(verified/score/pass/passed/result/verdict)를 담으면 그 자체가 계약 위반이라
거부한다(exit 2) — producer 는 아티팩트의 판정을 절대 신뢰하지 않고 `claims.py` 로
디스크에서 재검사한다.

측정값 `intent_fidelity` 는 검증된 claim 집합의 결정 함수일 뿐이다(§2 원칙2):
  - required criterion 이 하나라도 미검증 → 0.0
  - required 전부 검증 + optional 중 하나 이상 미검증 → 0.7
  - 전 criterion 검증 → 1.0
criteria 0개 또는 required criterion 0개는 반증 불가능한 측정이라 emit 하지 않는다
(결손 → 커널 법칙1이 FAIL) — optional 만으로 0.7 바닥을 확보하는 경로를 봉쇄한다.

exit code 정책(스펙 §스펙과의 차이 6): 0 = 정상 실행(emit 됐거나 정직한 결손) /
2 = 선언 아티팩트 저작 오류(JSON 파싱 불가·스키마 위반·화이트리스트 밖 backing kind·
판정 필드 포함). "선언이 없어서 못 잰다"(결손)와 "선언이 틀렸다"(저작 오류)를 구분한다.

CLI:
    python measure_intent_fidelity.py --criteria <intent-criteria.json> \
        --submission <dir> [--test-junit <path>] [--git-base HEAD] [--phase 09] \
        [--project-run <name>] [--measured-at <ISO8601>] --out-dir <run>/evidence

저장소 self_lint C35 — 모든 open/subprocess `encoding="utf-8"`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import claims
import parsers

import _evidence_common as ec  # noqa: E402
from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "gate.intent_fidelity"
DEFAULT_PHASE = "09"
MEASURED_SOURCE = "claims_backing"

# 선언 아티팩트에 있으면 계약 위반인 판정 필드 — criterion 엔트리·backing 양쪽 검사.
_JUDGMENT_FIELDS = frozenset({"verified", "score", "pass", "passed", "result", "verdict"})


class CriteriaSchemaError(ValueError):
    """intent-criteria.json 저작 오류 — JSON 파싱 불가/스키마 위반/판정 필드 포함/id 중복.
    exit 2(스펙 §3.2 결정5) — 아티팩트가 없어서 못 재는 것(결손)과 구분한다."""


def _reject_judgment_fields(d: dict, where: str) -> None:
    present = sorted(_JUDGMENT_FIELDS & d.keys())
    if present:
        raise CriteriaSchemaError(f"{where} contains judgment field(s): {present}")


def _load_criteria(path: Path) -> list[dict]:
    """intent-criteria.json 로드 + 구조 검증(스펙 §3.2 알고리즘 3단계). 위반 시
    CriteriaSchemaError(화이트리스트 밖 backing.kind 는 여기서 안 걸린다 — 그건 claims.verify
    시점(6단계)의 몫)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CriteriaSchemaError(f"criteria file unreadable: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CriteriaSchemaError(f"criteria file not valid JSON: {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("criteria"), list):
        raise CriteriaSchemaError('criteria file must be a JSON object with a "criteria" list')

    criteria = data["criteria"]
    seen_ids: set[str] = set()
    for i, c in enumerate(criteria):
        if not isinstance(c, dict):
            raise CriteriaSchemaError(f"criteria[{i}] must be an object")
        _reject_judgment_fields(c, f"criteria[{i}]")
        cid = c.get("id")
        if not isinstance(cid, str):
            raise CriteriaSchemaError(f"criteria[{i}].id must be a string")
        if cid in seen_ids:
            raise CriteriaSchemaError(f"duplicate criteria id: {cid!r}")
        seen_ids.add(cid)
        if not isinstance(c.get("required"), bool):
            raise CriteriaSchemaError(f"criteria[{i}].required must be a bool")
        backing = c.get("backing")
        if not isinstance(backing, dict):
            raise CriteriaSchemaError(f"criteria[{i}].backing must be an object")
        _reject_judgment_fields(backing, f"criteria[{i}].backing")
        if not isinstance(backing.get("kind"), str):
            raise CriteriaSchemaError(f"criteria[{i}].backing.kind must be a string")
        if "ref" not in backing:
            raise CriteriaSchemaError(f"criteria[{i}].backing.ref missing")
    return criteria


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    parts = ["python", str(Path(__file__).resolve())]
    parts += ["--criteria", args.criteria, "--submission", args.submission]
    if args.test_junit:
        parts += ["--test-junit", args.test_junit]
    parts += ["--git-base", args.git_base, "--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    """스펙 §3.2 알고리즘 9단계. 스키마/화이트리스트 위반은 예외로 전파(exit 2 는
    main() 이 매김) — 그 외는 항상 exit 0(emit 됐거나 정직한 결손)."""
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    criteria_path = Path(args.criteria)
    if not criteria_path.exists():
        return {"emitted": False, "reason": "criteria file absent"}

    criteria = _load_criteria(criteria_path)  # CriteriaSchemaError → 저작 오류(exit 2)

    required_total = sum(1 for c in criteria if c["required"])
    if not criteria or required_total == 0:
        return {
            "emitted": False,
            "reason": "no required criteria - refusing vacuous measurement",
        }

    submission = Path(args.submission).resolve()
    git_files, git_error = claims.git_diff_files(submission, args.git_base)
    # git 실패는 no-emit 사유가 아니다 — symbol/diff claim 이 ctx 결손으로 False 될 뿐.

    junit_map: dict[str, str] | None = None
    junit_error: str | None = None
    if args.test_junit:
        try:
            junit_map = parsers.parse_junit_cases(args.test_junit)
        except parsers.ArtifactParseError as exc:
            junit_map = None
            junit_error = str(exc)

    ctx = claims.Context(submission=submission, git_files=git_files, junit=junit_map)

    criteria_report: list[dict[str, Any]] = []
    required_verified = 0
    optional_total = 0
    optional_verified = 0
    for c in criteria:
        backing = c["backing"]
        ok, detail = claims.verify(backing, ctx)  # UnknownBackingKind → 저작 오류(exit 2)
        criteria_report.append(
            {
                "id": c["id"],
                "required": c["required"],
                "kind": backing["kind"],
                "ref": backing["ref"],
                "verified": ok,
                "detail": detail,
            }
        )
        if c["required"]:
            if ok:
                required_verified += 1
        else:
            optional_total += 1
            if ok:
                optional_verified += 1

    # 이산화(커널 assertion intent_fidelity ∈ {1.0,0.7,0.0}).
    if required_verified < required_total:
        value = 0.0
    elif optional_total > 0 and optional_verified < optional_total:
        value = 0.7
    else:
        value = 1.0

    report = {
        "criteria": criteria_report,
        "counts": {
            "required_total": required_total,
            "required_verified": required_verified,
            "optional_total": optional_total,
            "optional_verified": optional_verified,
        },
        "git_base": args.git_base,
        "git_files_count": len(git_files) if git_files is not None else None,
        "git_error": git_error,
        "junit_provided": bool(args.test_junit),
        "junit_error": junit_error,
        "value": value,
    }

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    rel = ec.relpath(report_path, run_root)
    digest = ec.sha256_of_file(report_path)

    measured = {
        "intent_fidelity": ec.build_measured(value, MEASURED_SOURCE, rel),
    }
    record = ec.assemble_record(
        check_id=CHECK_ID,
        phase=args.phase,
        project_run=project_run,
        producer_cmd=producer_cmd,
        measured=measured,
        artifact_digests={rel: digest},
        measured_at=measured_at,
    )
    evidence_path = ec.write_evidence(out_dir, CHECK_ID, record)
    return {
        "emitted": True,
        "value": value,
        "evidence_path": str(evidence_path),
        "report_path": str(report_path),
        "counts": report["counts"],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_intent_fidelity — gate.intent_fidelity 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument("--criteria", required=True, help="intent-criteria.json 경로")
    p.add_argument("--submission", required=True, help="제출물 디렉터리 (file/symbol/git diff 대상)")
    p.add_argument(
        "--test-junit", default=None, help="test kind backing 용 junit XML 경로(optional)"
    )
    p.add_argument("--git-base", default="HEAD", help="git diff base ref (기본 HEAD)")
    p.add_argument(
        "--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다."
    )
    p.add_argument("--project-run", default=None, help="project_run 이름 (기본: run_root.name)")
    p.add_argument("--measured-at", default=None, help="measured_at 주입(결정성 테스트용)")
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<run>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)
    try:
        summary = run(args)
    except (CriteriaSchemaError, claims.UnknownBackingKind) as exc:
        print(f"measure_intent_fidelity: {exc}", file=sys.stderr)
        return 2
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
