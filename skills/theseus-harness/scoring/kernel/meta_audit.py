#!/usr/bin/env python3
"""meta_audit.py — 생성형(generative) 메타 감사 (설계 §6, WP3).

phase_invoke_audit.py 의 `CLI_TRACE_PATHS` 하드코딩 10개(P5)를 레지스트리 열거로
대체한다. 이 스크립트는 어떤 check_id 도 소스에 박아 두지 않는다 — `run_meta_audit`
아래 `active = manifest.active_checks(m, grade)` 한 줄이 순회 대상 전체이고, 이는
매니페스트 파일을 읽어 얻은 목록이다. 신규 CheckSpec 은 `checks/<id>.json` 파일 +
`pipeline.manifest.json` 의 checks 맵 항목만 추가하면 다음 실행에서 곧바로 감사
대상에 들어온다(코드 변경 0줄) — phase_invoke_audit.py 는 신규 CLI 매핑이 없으면
`invoked: None → audit_skipped` 이고 `overall_pass = len(not_invoked) == 0` 이라
감사 사각이 FAIL 을 유발하지 않았지만(P5), 본 스크립트는 evidence 부재도 여전히
kernel.verify(spec, None, ...) 을 태워 FAIL 로 잡는다 — skip 이라는 제3의 상태가
존재하지 않는다(§2 원칙2 "skipped == pass 를 skipped == FAIL 로 뒤집는다").

사용:
    python meta_audit.py --project-root <run> --grade G3 \
        [--manifest pipeline.manifest.json] [--checks-dir checks/] \
        [--output report.json] [--verified-at ISO8601]

evidence 경로 규약: `<project_root>/evidence/<check_id>.json`.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# kernel/ 디렉터리 안이라 평면 import(conftest.py 가 sys.path 에 이 디렉터리를 넣는다).
import checkspec
import evidence as evidence_mod
import kernel
import manifest as manifest_mod
from checkspec import CheckSpec, UnsafeExpressionError, safe_eval

SCHEMA_VERSION = "1.0"

# 결과 상태 3종 — 커널은 PASS/FAIL 만 알지만, 정책 레이어는 NA(비게이팅)를 더한다.
NA = "NA"

# WP3 의 checks/ 레지스트리와 pipeline.manifest.json 은 이 파일 기준 두 단계 위
# (kernel/ -> scoring/ -> theseus-harness/) 에 있다. manifest.py 의 회귀 테스트가
# 쓰는 것과 동일한 상대 위치 규약(parents[2])이다.
_THESEUS_HARNESS_DIR = Path(__file__).resolve().parents[2]
_DEFAULT_MANIFEST = _THESEUS_HARNESS_DIR / "pipeline.manifest.json"
_DEFAULT_CHECKS_DIR = _THESEUS_HARNESS_DIR / "checks"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _integrity_only_spec(spec: CheckSpec) -> CheckSpec:
    """assertion/value 를 제거한 무결성 전용 spec — 커널이 법칙1~3(존재·provenance·
    producer/digest)만 강제하고 법칙4~5(값 술어)는 no-op 이 된다.

    WHY 필요한가: 적용성(NA) 판정은 measured 값을 신뢰해야 하는데, 그 값이 provenance·
    digest 로 뒷받침되지 않으면 'NA 도 증거로 입증'이 무너진다(가짜 evidence 로 게이트
    회피). 이 stripped spec 으로 커널을 재사용해 evidence 무결성을 먼저 세운다 —
    kernel.py 를 수정하지 않고(그대로 쓴다) 법칙1~3 만 태우는 방법.
    """
    return CheckSpec(
        check_id=spec.check_id,
        phase=spec.phase,
        grades=spec.grades,
        status=spec.status,
        producer=spec.producer,
        provenance_required=spec.provenance_required,
        assertions=[],
        value=None,
        absence_policy=spec.absence_policy,
        applicability=None,
    )


def _evaluate_check(
    spec: CheckSpec,
    ev: evidence_mod.EvidenceRecord | None,
    root: Path,
    verified_at: str | None,
) -> dict[str, Any]:
    """한 체크의 정책 판정 → {result: PASS|FAIL|NA, value, reasons}.

    적용성이 없으면 커널 판정 그대로. 적용성이 있으면:
      1. evidence 부재 → FAIL(evidence_missing) — 적용성으로 못 구한다(설계 요구).
      2. 무결성(법칙1~3) 실패 → FAIL — 신뢰 못 하는 evidence 로 NA 를 줄 수 없다.
      3. 적용성 expr(measured 값 위)이 false → NA(비게이팅). "단일 사이드"라는 사실이
         producer 가 emit 한 measured 값으로 *입증*되어야만 NA 가 된다.
      4. true → 커널 완전 판정(PASS/FAIL).
    """
    if spec.applicability is None:
        v = kernel.verify(spec, ev, artifact_root=root, verified_at=verified_at)
        return {"result": v.result, "value": v.value, "reasons": list(v.reasons)}

    # 1. 부재는 적용성과 무관하게 FAIL — 커널 법칙1이 그대로 잡는다.
    if ev is None:
        v = kernel.verify(spec, None, artifact_root=root, verified_at=verified_at)
        return {"result": v.result, "value": v.value, "reasons": list(v.reasons)}

    # 2. 무결성 선검사 — evidence 가 provenance·digest 로 신뢰 가능한가.
    integ = kernel.verify(
        _integrity_only_spec(spec), ev, artifact_root=root, verified_at=verified_at
    )
    if integ.result != kernel.PASS:
        return {"result": integ.result, "value": None, "reasons": list(integ.reasons)}

    # 3. 적용성 평가 — 신뢰 가능한 measured 값 위에서.
    try:
        applicable = bool(safe_eval(spec.applicability, ev.measured_values()))
    except (UnsafeExpressionError, ZeroDivisionError, TypeError) as exc:
        return {
            "result": kernel.FAIL,
            "value": None,
            "reasons": [f"applicability expr error: {spec.applicability!r}: {exc}"],
        }
    if not applicable:
        return {
            "result": NA,
            "value": None,
            "reasons": [f"not applicable (applicability false): {spec.applicability}"],
        }

    # 4. 적용됨 → 커널 완전 판정.
    v = kernel.verify(spec, ev, artifact_root=root, verified_at=verified_at)
    return {"result": v.result, "value": v.value, "reasons": list(v.reasons)}


def run_meta_audit(
    project_root: str | Path,
    grade: str,
    *,
    manifest_path: str | Path = _DEFAULT_MANIFEST,
    checks_dir: str | Path = _DEFAULT_CHECKS_DIR,
    verified_at: str | None = None,
) -> dict[str, Any]:
    """레지스트리를 열거해 이 grade 에서 활성인 모든 체크를 커널로 재판정한다.

    WHY 하드코딩이 아닌가: 아래 `active` 는 이 함수 안에 적힌 리스트가 아니라
    `manifest_mod.active_checks(m, grade)` 호출의 반환값이다 — 매니페스트 파일에
    check_id 를 추가하면 이 함수는 코드 변경 없이 다음 호출에서 그 id 를 그대로
    순회한다. "declared but not invoked" 가 구조적으로 불가능해지는 지점이 정확히
    이 한 줄이다(설계 §6).
    """
    root = Path(project_root)
    m = manifest_mod.load_manifest(manifest_path)
    active = manifest_mod.active_checks(m, grade)

    results: dict[str, Any] = {}
    failed: list[str] = []
    na: list[str] = []

    for check_id in active:
        spec_path = Path(checks_dir) / f"{check_id}.json"
        try:
            spec = checkspec.load_checkspec(spec_path)
        except checkspec.CheckSpecError as exc:
            results[check_id] = {
                "result": kernel.FAIL,
                "value": None,
                "reasons": [f"checkspec_load_error: {exc}"],
            }
            failed.append(check_id)
            continue

        ev_path = root / "evidence" / f"{check_id}.json"
        # evidence 부재/공백/파싱불가는 모두 None 으로 흡수된다. 적용성 없는 체크는
        # kernel.verify(spec, None, ...) 이 법칙1(evidence_missing)로 FAIL — 별도 skip
        # 경로 없음. 적용성 있는 체크의 NA 판정은 _evaluate_check(정책)가 소유한다.
        ev = evidence_mod.try_load_evidence(ev_path)
        outcome = _evaluate_check(spec, ev, root, verified_at)

        results[check_id] = outcome
        if outcome["result"] == NA:
            na.append(check_id)
        elif outcome["result"] != kernel.PASS:
            failed.append(check_id)

    return {
        "schema_version": SCHEMA_VERSION,
        "project_root": str(root),
        "grade": grade,
        "active_checks": list(active),
        "results": results,
        "failed": failed,
        # NA 는 비게이팅 — verdict 계산에서 제외한다(§ 적용성 정책, 침묵 skip 아님).
        "na": na,
        "verdict": "pass" if not failed else "fail",
        "evaluated_at": verified_at or _now_iso(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="meta_audit — 레지스트리 열거 기반 생성형 메타 감사 (P5 구조적 제거, 설계 §6)"
    )
    parser.add_argument("--project-root", required=True, help="run 의 project root 디렉터리")
    parser.add_argument("--grade", required=True, help="감사할 그레이드 (예: G3)")
    parser.add_argument("--manifest", default=str(_DEFAULT_MANIFEST), help="pipeline.manifest.json 경로")
    parser.add_argument("--checks-dir", default=str(_DEFAULT_CHECKS_DIR), help="CheckSpec 레지스트리 디렉터리")
    parser.add_argument("--output", default=None, help="report JSON 저장 경로")
    parser.add_argument(
        "--verified-at",
        default=None,
        help="Verdict/report 타임스탬프 주입(재현 검증용; 기본: 현재 UTC)",
    )
    args = parser.parse_args(argv)

    report = run_meta_audit(
        args.project_root,
        args.grade,
        manifest_path=args.manifest,
        checks_dir=args.checks_dir,
        verified_at=args.verified_at,
    )

    out_text = json.dumps(report, indent=2, ensure_ascii=False)
    print(out_text)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out_text + "\n", encoding="utf-8")

        # 관례 경로에도 기록 — webview/dashboard 가 고정 경로에서 로드할 수 있게.
        gate_path = Path(args.project_root) / "quality" / "gate_meta_audit.json"
        gate_path.parent.mkdir(parents=True, exist_ok=True)
        gate_path.write_text(out_text + "\n", encoding="utf-8")

    return 0 if report["verdict"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
