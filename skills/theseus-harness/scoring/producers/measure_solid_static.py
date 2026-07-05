#!/usr/bin/env python3
"""measure_solid_static.py — scoring.solid 증거 조립기 (판단-게이트 스펙 §3.4).

`--solid-contract`(phase 08 저작, optional)의 모듈별 SOLID/DIP claim 을 claims.py 로
디스크에서 재검사해 raw 값(`modules_passing_solid`/`modules_total`/`dip_violation`)만
Evidence Record 로 emit 한다. verdict/score 는 내지 않는다 — 얕은 모듈 판정과 마찬가지로
`scoring.solid` CheckSpec 이 커널로 내린다(§5 producer/kernel 분리).

핵심 불변식(스펙 §2·§3.4):
  - producer 는 verdict/score 를 emit 하지 않는다 — measured 는 원시 측정값만.
  - `modules_total` 은 deep_module_metric.enumerate_modules 단일 소스를 재사용한다 —
    measure_deep_module 과 값이 동일해야 브릿지 정합(§4.1)이 성립한다.
  - 모듈 통과 = enumeration 안 ∧ 전 claim 검증. enumeration 밖 모듈은 claim 검증은
    하되 통과 계수에서 제외 → `modules_passing_solid <= modules_total` 구조적 충족.
  - dip_violation = principle=="DIP" claim 중 하나라도 미검증이면 1.
  - contract 미제공/파일 부재 → `modules_total` 하나만 emit(결손 유지, zero-config
    AST 휴리스틱 금지). 판정 필드/깨진 JSON/화이트리스트 밖 kind → exit 2.
  - 결정성: 시간/난수 없음, `--measured-at` 주입 가능, 정렬 고정, 리포트 절대경로 금지.

CLI:
    python measure_solid_static.py --code-root <dir> [--solid-contract <json>] \\
        [--phase 08] [--project-run <name>] [--measured-at <ISO8601>] \\
        --out-dir <run>/evidence

저장소 self_lint C35 — 모든 open/read_text/write_text encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path, PurePosixPath
from typing import Any

_PRODUCERS_DIR = Path(__file__).resolve().parent
_SCORING_DIR = _PRODUCERS_DIR.parent
for _d in (_PRODUCERS_DIR, _SCORING_DIR):
    if str(_d) not in sys.path:
        sys.path.insert(0, str(_d))

import deep_module_metric  # noqa: E402

import _evidence_common as ec  # noqa: E402
import claims  # noqa: E402

CHECK_ID = "gate.solid_static"
DEFAULT_PHASE = "08"
SOURCE = "solid_static_report"

# 선언 아티팩트가 담으면 즉시 거부하는 판정 필드(스펙 §2 불변식1, 구체화 결정 5).
_JUDGMENT_FIELDS = frozenset({"verified", "score", "pass", "passed", "result", "verdict"})


class ContractError(Exception):
    """선언 아티팩트 저작 오류 — emit 없이 exit 2 (스펙 §2 불변식, 구체화 결정 5·6).

    "선언 자체가 없어서 못 잰다"(결손, exit 0)와 구분되는 "선언이 틀렸다"(저작 오류).
    """


def _reject_judgment_fields(obj: dict, where: str) -> None:
    for k in _JUDGMENT_FIELDS:
        if k in obj:
            raise ContractError(f"judgment field {k!r} present in {where} (구체화 결정 5)")


def _load_contract(path: Path) -> list[dict]:
    """solid-contract.json 로드 + 스키마 검증. 위반 시 ContractError(→ exit 2).

    반환: 모듈별 정규화 엔트리 리스트 — 같은 module 경로는 claim 을 병합(첫 등장 순서
    보존). 각 엔트리 {"module": <posix str>, "claims": [{"principle","backing"} ...]}.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        raise ContractError(f"solid-contract JSON unparseable: {exc}")
    if not isinstance(data, dict) or not isinstance(data.get("modules"), list):
        raise ContractError("solid-contract must be an object with a 'modules' list")

    merged: dict[str, dict] = {}
    order: list[str] = []
    for i, entry in enumerate(data["modules"]):
        if not isinstance(entry, dict):
            raise ContractError(f"module entry #{i} is not an object")
        _reject_judgment_fields(entry, f"module entry #{i}")
        module = entry.get("module")
        if not isinstance(module, str):
            raise ContractError(f"module entry #{i} missing string 'module'")
        raw_claims = entry.get("claims")
        if not isinstance(raw_claims, list):
            raise ContractError(f"module {module!r} missing 'claims' list")
        mrel = PurePosixPath(module).as_posix()
        norm_claims: list[dict] = []
        for j, claim in enumerate(raw_claims):
            if not isinstance(claim, dict):
                raise ContractError(f"module {module!r} claim #{j} is not an object")
            _reject_judgment_fields(claim, f"module {module!r} claim #{j}")
            principle = claim.get("principle")
            if not isinstance(principle, str):
                raise ContractError(f"module {module!r} claim #{j} missing string 'principle'")
            backing = claim.get("backing")
            if not isinstance(backing, dict):
                raise ContractError(f"module {module!r} claim #{j} missing 'backing' object")
            _reject_judgment_fields(backing, f"module {module!r} claim #{j} backing")
            norm_claims.append({"principle": principle, "backing": backing})
        if mrel not in merged:
            merged[mrel] = {"module": mrel, "claims": []}
            order.append(mrel)
        merged[mrel]["claims"].extend(norm_claims)
    return [merged[m] for m in order]


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    parts = ["python", str(Path(__file__).resolve()), "--code-root", args.code_root]
    if args.solid_contract:
        parts += ["--solid-contract", args.solid_contract]
    parts += ["--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    code_root = Path(args.code_root).resolve()

    # modules_total 의 단일 소스 — deep_module 과 동일 enumeration(브릿지 정합, §4.1).
    modules = deep_module_metric.enumerate_modules(code_root)
    enum_rel = [Path(os.path.relpath(m, code_root)).as_posix() for m in modules]
    enum_set = set(enum_rel)
    modules_total = len(modules)

    contract_path = Path(args.solid_contract).resolve() if args.solid_contract else None
    contract_provided = contract_path is not None and contract_path.is_file()

    report: dict[str, Any] = {
        "modules_total": modules_total,
        "enumeration": enum_rel,
        "contract_provided": contract_provided,
        "modules": [],
        "dip_claims_total": 0,
        "dip_claims_unverified": 0,
    }

    if not contract_provided:
        # 결손 유지 — modules_total 만 emit. zero-config 휴리스틱 금지(스펙 §3.4).
        report_path = out_dir / f"{CHECK_ID}.report.json"
        ec.write_json_artifact(report_path, report)
        rel = ec.relpath(report_path, run_root)
        measured = {"modules_total": ec.build_measured(modules_total, SOURCE, rel)}
        record = ec.assemble_record(
            check_id=CHECK_ID, phase=args.phase, project_run=project_run,
            producer_cmd=producer_cmd, measured=measured,
            artifact_digests={rel: ec.sha256_of_file(report_path)}, measured_at=measured_at,
        )
        path = ec.write_evidence(out_dir, CHECK_ID, record)
        return {
            "emitted": True,
            "evidence_path": str(path),
            "report_path": str(report_path),
            "modules_total": modules_total,
            "emitted_keys": ["modules_total"],
            "solid_claims": "deficit (no contract)",
        }

    contract = _load_contract(contract_path)

    modules_passing = 0
    dip_total = 0
    dip_unverified = 0
    report_modules: list[dict] = []
    for entry in contract:
        mrel = entry["module"]
        in_enum = mrel in enum_set
        ctx = claims.Context(code_root=code_root, module=mrel)
        claim_reports: list[dict] = []
        all_verified = True
        for claim in entry["claims"]:
            backing = claim["backing"]
            try:
                ok, detail = claims.verify(backing, ctx)
            except claims.UnknownBackingKind as exc:
                raise ContractError(
                    f"unknown backing kind in module {mrel!r}: {exc} "
                    f"(화이트리스트 밖 — 임의 검사 표면 차단, 스펙 §3.1)"
                )
            if not ok:
                all_verified = False
            if claim["principle"] == "DIP":
                dip_total += 1
                if not ok:
                    dip_unverified += 1
            claim_reports.append({
                "principle": claim["principle"],
                "kind": backing.get("kind"),
                "ref": backing.get("ref"),
                "verified": ok,
                "detail": detail,
            })
        passed = in_enum and all_verified
        if passed:
            modules_passing += 1
        entry_report = {
            "module": mrel,
            "in_enumeration": in_enum,
            "passed": passed,
            "claims": claim_reports,
        }
        if not in_enum:
            entry_report["reason"] = "module not in enumeration"
        report_modules.append(entry_report)

    report["modules"] = sorted(report_modules, key=lambda m: m["module"])
    report["dip_claims_total"] = dip_total
    report["dip_claims_unverified"] = dip_unverified
    dip_violation = 1 if dip_unverified > 0 else 0

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    rel = ec.relpath(report_path, run_root)
    digest = ec.sha256_of_file(report_path)
    measured = {
        "modules_passing_solid": ec.build_measured(modules_passing, SOURCE, rel),
        "modules_total": ec.build_measured(modules_total, SOURCE, rel),
        "dip_violation": ec.build_measured(dip_violation, SOURCE, rel),
    }
    record = ec.assemble_record(
        check_id=CHECK_ID, phase=args.phase, project_run=project_run,
        producer_cmd=producer_cmd, measured=measured,
        artifact_digests={rel: digest}, measured_at=measured_at,
    )
    path = ec.write_evidence(out_dir, CHECK_ID, record)
    return {
        "emitted": True,
        "evidence_path": str(path),
        "report_path": str(report_path),
        "modules_total": modules_total,
        "modules_passing_solid": modules_passing,
        "dip_violation": dip_violation,
        "emitted_keys": ["modules_passing_solid", "modules_total", "dip_violation"],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_solid_static — scoring.solid 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument("--code-root", required=True, help="분석 대상 코드 루트 디렉터리")
    p.add_argument("--solid-contract", default=None, help="solid-contract.json (optional, phase 08 저작)")
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
    p.add_argument("--project-run", default=None)
    p.add_argument("--measured-at", default=None, help="결정성 주입 — 기본 ec.now_iso()")
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<run>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        summary = run(args)
    except ContractError as exc:
        print(f"measure_solid_static: contract authoring error — {exc}", file=sys.stderr)
        return 2
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
