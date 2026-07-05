#!/usr/bin/env python3
"""Verification Kernel — 유일한 판정자 (설계 §4).

verify(check_spec, evidence) -> Verdict. 커널은 실행하지 않고 상상하지 않는다.
Evidence Record 만 받아 5법칙을 '명시된 순서 = 우선순위'로 적용한다(§4.3):

  1. 증거 존재·파싱 가능?                    아니면 FAIL(evidence_missing)   [_law1]
  2. produced_by=="run" & self_reported 화이트리스트 & provenance 완전?     [_law2]
  3. producer_cmd 매칭 & exit==0 & artifact_digests 가 디스크 실파일과 일치? [_law3]
  4. 모든 assertion(값 술어) 참?              아니면 FAIL(첫 거짓의 on_fail)  [_law4]
  5. value(측정값의 결정 함수) 계산 후 Verdict(PASS, value, ...) 반환        [_law5]

결정성(§2 원칙5): 같은 증거 → 같은 Verdict(result/value/reasons/evidence_digest).
`verified_at` 만 시각에 의존하므로 Verdict 동등성 비교에서 제외(field compare=False)하고
주입 가능한 인자로 둔다 — 커널 코어 판정 로직은 어떤 시각 함수도 읽지 않는다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# 스크립트(`python kernel.py ...`) 실행과 pytest(conftest 가 dir 를 sys.path 에 삽입)
# 양쪽에서 같은 최상위 모듈로 import 되도록 평면 import 를 쓴다.
import checkspec
import evidence
from checkspec import CheckSpec, UnsafeExpressionError, safe_eval
from evidence import EvidenceRecord

PASS = "PASS"
FAIL = "FAIL"

# self_reported:true 를 예외적으로 허용하는 극소수 check_id (§3.1). 기본 공집합 —
# 어떤 자기 신고도 화이트리스트 밖이므로 FAIL. 필요한 곳에서만 주입해 확장한다.
DEFAULT_SELF_REPORT_WHITELIST: frozenset[str] = frozenset()


@dataclass
class Verdict:
    check_id: str
    result: str  # "PASS" | "FAIL"
    value: float | None
    reasons: list[str]
    evidence_digest: str
    # WHY compare=False: verified_at 만 시각 의존 — 같은 증거의 재현 비교에서 제외해
    # Verdict 동등성이 판정 내용(result/value/reasons/digest)에만 걸리게 한다.
    verified_at: str = field(default="", compare=False)

    def to_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "result": self.result,
            "value": self.value,
            "reasons": list(self.reasons),
            "evidence_digest": self.evidence_digest,
            "verified_at": self.verified_at,
        }


def _now_iso() -> str:
    """UTC ISO8601 — Verdict 메타데이터 스탬프에만 쓰이고 판정 결과에는 영향 없음."""
    return datetime.now(timezone.utc).isoformat()


# --- 5법칙 (구현 순서 = 우선순위) -----------------------------------------------


def _law1(spec: CheckSpec, ev: EvidenceRecord | None) -> list[str]:
    """법칙1 — 증거 존재·파싱 가능? absence_policy 반영."""
    if ev is None:
        # absence_policy 는 부재 시 동작을 정의. WP1 범위에서는 FAIL 만 실동작
        # (advisory/frozen 처리는 WP6). 기본값 FAIL.
        return [f"evidence_missing (absence_policy={spec.absence_policy})"]
    return []


def _law2(
    spec: CheckSpec,
    ev: EvidenceRecord,
    self_report_whitelist: frozenset[str],
) -> list[str]:
    """법칙2 — 자기 신고 차단 + provenance 완전성(§3.1, P1 차단)."""
    reasons: list[str] = []
    # produced_by 는 "run" 만 허용 — "assert" 등은 존재 자체가 FAIL(§3.1).
    if ev.produced_by != "run":
        reasons.append(f"produced_by must be 'run', got {ev.produced_by!r}")
    # self_reported:true 는 화이트리스트된 극소수만.
    if ev.self_reported and ev.check_id not in self_report_whitelist:
        reasons.append("self_reported=true outside whitelist")
    # provenance_required 키는 measured 에 반드시 존재해야 검사가 성립.
    for key in spec.provenance_required:
        if key not in ev.measured:
            reasons.append(f"required measured key absent: {key}")
    # 모든 measured 값의 value/source/artifact_path 완전성.
    reasons.extend(ev.provenance_gaps())
    return reasons


def _law3(spec: CheckSpec, ev: EvidenceRecord, artifact_root: Path) -> list[str]:
    """법칙3 — producer 매칭 + exit==0 + artifact 디지털 대조(§3.1, P4/P7 차단)."""
    reasons: list[str] = []
    if re.search(spec.producer.cmd_pattern, ev.producer_cmd) is None:
        reasons.append(
            f"producer_cmd does not match cmd_pattern: {spec.producer.cmd_pattern!r}"
        )
    if spec.producer.must_exit_zero and ev.producer_exit_code != 0:
        reasons.append(f"producer_exit_code != 0 (got {ev.producer_exit_code})")
    # artifact_digests 를 디스크 실파일 sha256 과 대조 — 상상한 숫자는 여기서 걸린다.
    for rel_path, declared in ev.artifact_digests.items():
        disk_path = artifact_root / rel_path
        if not disk_path.exists():
            reasons.append(f"artifact missing on disk: {rel_path}")
            continue
        actual = evidence.sha256_of_file(disk_path)
        if actual != evidence.normalize_digest(declared):
            reasons.append(
                f"artifact digest mismatch for {rel_path}: "
                f"declared {evidence.normalize_digest(declared)[:12]}.. "
                f"actual {actual[:12]}.."
            )
    return reasons


def _law4(spec: CheckSpec, ev: EvidenceRecord) -> list[str]:
    """법칙4 — 모든 assertion 참? 첫 거짓의 on_fail 반환(값 기반 게이트)."""
    variables = ev.measured_values()
    for assertion in spec.assertions:
        try:
            result = safe_eval(assertion.expr, variables)
        except UnsafeExpressionError as exc:
            # 위험/부정 식은 통과가 아니라 안전 실패 — 임의 실행 없이 FAIL.
            return [f"unsafe or invalid assertion rejected: {assertion.expr!r}: {exc}"]
        except (ZeroDivisionError, TypeError) as exc:
            return [f"assertion evaluation error: {assertion.expr!r}: {exc}"]
        if not result:
            return [assertion.on_fail]
    return []


def _law5(spec: CheckSpec, ev: EvidenceRecord) -> tuple[float | None, list[str]]:
    """법칙5 — value(측정값의 결정 함수) 계산. 없으면 None."""
    if not spec.value:
        return None, []
    variables = ev.measured_values()
    try:
        raw = safe_eval(spec.value, variables)
    except UnsafeExpressionError as exc:
        return None, [f"unsafe or invalid value expression rejected: {spec.value!r}: {exc}"]
    except (ZeroDivisionError, TypeError) as exc:
        return None, [f"value evaluation error: {spec.value!r}: {exc}"]
    return float(raw), []


def verify(
    spec: CheckSpec,
    ev: EvidenceRecord | None,
    *,
    verified_at: str | None = None,
    artifact_root: str | Path = ".",
    self_report_whitelist: frozenset[str] = DEFAULT_SELF_REPORT_WHITELIST,
) -> Verdict:
    """유일 판정 진입점. 5법칙을 순서대로 적용해 결정성 있는 Verdict 를 낸다.

    verified_at 은 주입 가능(테스트가 고정값으로 비트 재현 검증). 미주입 시 현재 UTC 를
    스탬프하지만, 이는 Verdict 동등성에서 제외되는 메타데이터일 뿐 판정에는 무관하다.
    """
    stamp = verified_at if verified_at is not None else _now_iso()
    digest = ev.digest() if ev is not None else ""
    root = Path(artifact_root)

    def fail(reasons: list[str]) -> Verdict:
        return Verdict(
            check_id=spec.check_id,
            result=FAIL,
            value=None,
            reasons=reasons,
            evidence_digest=digest,
            verified_at=stamp,
        )

    r1 = _law1(spec, ev)
    if r1:
        return fail(r1)
    assert ev is not None  # 법칙1 통과 → 이후 ev 는 존재

    r2 = _law2(spec, ev, self_report_whitelist)
    if r2:
        return fail(r2)

    r3 = _law3(spec, ev, root)
    if r3:
        return fail(r3)

    r4 = _law4(spec, ev)
    if r4:
        return fail(r4)

    value, r5 = _law5(spec, ev)
    if r5:
        return fail(r5)

    return Verdict(
        check_id=spec.check_id,
        result=PASS,
        value=value,
        reasons=[],
        evidence_digest=digest,
        verified_at=stamp,
    )


# --- CLI -----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verification Kernel — 유일 판정자")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("verify", help="CheckSpec + Evidence → Verdict")
    v.add_argument("--spec", required=True, help="CheckSpec JSON 경로")
    v.add_argument("--evidence", required=True, help="Evidence Record JSON 경로")
    v.add_argument(
        "--artifact-root",
        default=None,
        help="artifact 상대 경로 해석 기준 디렉터리 (기본: evidence 파일의 부모)",
    )
    v.add_argument(
        "--verified-at",
        default=None,
        help="Verdict 타임스탬프 주입 (재현 검증용; 기본: 현재 UTC)",
    )
    args = parser.parse_args(argv)

    spec = checkspec.load_checkspec(args.spec)
    ev = evidence.try_load_evidence(args.evidence)
    # artifact 는 통상 evidence 와 같은 run root 에 놓인다 — 기본 해석 기준을 그리로.
    artifact_root = args.artifact_root or Path(args.evidence).parent

    verdict = verify(
        spec,
        ev,
        verified_at=args.verified_at,
        artifact_root=artifact_root,
    )
    json.dump(verdict.to_dict(), sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if verdict.result == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
