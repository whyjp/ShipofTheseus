"""Evidence Record — 커널과 producer 사이의 유일 계약 (설계 §3).

측정계의 모든 게이트는 실행 후 Evidence Record(JSON) 하나를 emit 하고, 커널은
오직 이 레코드만 받아 판정한다. LLM 이 상상한 숫자는 backing artifact 가 없어
`artifact_digests` 대조(커널 법칙3)를 구조적으로 통과할 수 없다 — 그것이 이 계약의
핵심 불변식이다(§3 말미).

WHY 로딩(파싱)과 판정(kernel)을 분리했나: '증거 부재/공백/파싱불가/구조결손'을
커널 5법칙 중 법칙1 단일 지점이 FAIL 처리하도록, 여기서는 스키마 표현·로드·형태
검증만 책임진다(§2 원칙4 "줄인다").
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EVIDENCE_SCHEMA_VERSION = "1.0"

# provenance 필수 세 필드 — 하나라도 결손이면 해당 measured 값은 무효(§3.1).
_PROVENANCE_FIELDS = ("value", "source", "artifact_path")

# 파일 해시는 스트리밍으로 — 대용량 artifact 를 메모리에 통째로 올리지 않는다.
_HASH_CHUNK = 65536

# 최상위 필수 필드 (설계 §3.1 표). measured/artifact_digests 는 dict 여야 한다.
_REQUIRED_TOP_FIELDS = (
    "evidence_schema_version",
    "check_id",
    "phase",
    "project_run",
    "produced_by",
    "producer_cmd",
    "producer_exit_code",
    "measured",
    "artifact_digests",
    "measured_at",
    "self_reported",
)


class EvidenceParseError(ValueError):
    """증거 부재·공백·파싱불가·구조결손 — 커널 법칙1의 evidence_missing 원천."""


@dataclass
class EvidenceRecord:
    """설계 §3.1 필드를 그대로 담는 불변식 캐리어.

    measured 는 `{key: {value, source, artifact_path}}` 형태의 원시 dict 를 유지한다.
    구조화 래퍼를 두지 않는 이유: 정규화 직렬화(digest)가 원본 구조를 그대로 반영해야
    같은 증거가 같은 digest 를 내는 결정성이 자명해지기 때문.
    """

    evidence_schema_version: str
    check_id: str
    phase: str
    project_run: str
    produced_by: str
    producer_cmd: str
    producer_exit_code: int
    measured: dict[str, dict[str, Any]]
    artifact_digests: dict[str, str]
    measured_at: str
    self_reported: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "evidence_schema_version": self.evidence_schema_version,
            "check_id": self.check_id,
            "phase": self.phase,
            "project_run": self.project_run,
            "produced_by": self.produced_by,
            "producer_cmd": self.producer_cmd,
            "producer_exit_code": self.producer_exit_code,
            "measured": self.measured,
            "artifact_digests": self.artifact_digests,
            "measured_at": self.measured_at,
            "self_reported": self.self_reported,
        }

    def canonical_json(self) -> str:
        """정규화 직렬화 — 키 정렬 + 고정 구분자로 결정성 확보(§2 원칙5)."""
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        )

    def digest(self) -> str:
        """이 증거의 sha256(정규화 직렬화) — Verdict.evidence_digest 재현 추적용."""
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def measured_values(self) -> dict[str, Any]:
        """assertion/value 안전 평가에 노출할 변수 맵 — measured 원시 값만."""
        return {
            key: entry.get("value")
            for key, entry in self.measured.items()
            if isinstance(entry, dict)
        }

    def provenance_gaps(self) -> list[str]:
        """provenance 결손 목록 — measured 각 값의 value/source/artifact_path 완전성.

        커널 법칙2가 소비한다. 결손이 하나라도 있으면 그 값은 무효(§3.1).
        `value` 는 0/False 도 유효하므로 '키 존재' 로만 판정하고, source/artifact_path 는
        비어있지 않은 문자열이어야 한다(경로/출처 없는 provenance 는 신고나 다름없음).
        """
        gaps: list[str] = []
        for key, entry in self.measured.items():
            if not isinstance(entry, dict):
                gaps.append(f"measured[{key}] is not an object")
                continue
            if "value" not in entry:
                gaps.append(f"measured[{key}].value missing")
            src = entry.get("source")
            if not isinstance(src, str) or not src.strip():
                gaps.append(f"measured[{key}].source missing")
            ap = entry.get("artifact_path")
            if not isinstance(ap, str) or not ap.strip():
                gaps.append(f"measured[{key}].artifact_path missing")
        return gaps


def validate_shape(data: Any) -> list[str]:
    """최상위 형태 검증 — 결손·타입오류 목록 반환(빈 리스트 = 정상)."""
    problems: list[str] = []
    if not isinstance(data, dict):
        return ["evidence root is not a JSON object"]
    for fname in _REQUIRED_TOP_FIELDS:
        if fname not in data:
            problems.append(f"missing field: {fname}")
    if "producer_exit_code" in data and not isinstance(data["producer_exit_code"], int):
        problems.append("producer_exit_code must be an integer")
    if "self_reported" in data and not isinstance(data["self_reported"], bool):
        problems.append("self_reported must be a boolean")
    if "measured" in data and not isinstance(data["measured"], dict):
        problems.append("measured must be an object")
    if "artifact_digests" in data and not isinstance(data["artifact_digests"], dict):
        problems.append("artifact_digests must be an object")
    return problems


def from_dict(data: Any) -> EvidenceRecord:
    """dict → EvidenceRecord. 형태 검증 실패 시 EvidenceParseError."""
    problems = validate_shape(data)
    if problems:
        raise EvidenceParseError("; ".join(problems))
    return EvidenceRecord(
        evidence_schema_version=data["evidence_schema_version"],
        check_id=data["check_id"],
        phase=data["phase"],
        project_run=data["project_run"],
        produced_by=data["produced_by"],
        producer_cmd=data["producer_cmd"],
        producer_exit_code=data["producer_exit_code"],
        measured=data["measured"],
        artifact_digests=data["artifact_digests"],
        measured_at=data["measured_at"],
        self_reported=data["self_reported"],
    )


def load_evidence(path: str | Path) -> EvidenceRecord:
    """경로에서 Evidence Record 로드. 부재/공백/파싱불가/구조결손 → EvidenceParseError.

    커널 계약상 verify 는 이미 로드된 레코드(또는 None)를 받으므로, 로드 실패의
    세 원인(부재·공백·파싱불가)을 여기서 단일 예외로 정규화한다.
    """
    p = Path(path)
    if not p.exists():
        raise EvidenceParseError(f"evidence file not found: {p}")
    raw = p.read_text(encoding="utf-8")
    if not raw.strip():
        raise EvidenceParseError(f"evidence file empty: {p}")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EvidenceParseError(f"evidence not parseable JSON: {p}: {exc}") from exc
    return from_dict(data)


def try_load_evidence(path: str | Path) -> EvidenceRecord | None:
    """로드 실패를 None 으로 흡수 — CLI 가 verify(spec, None) 로 법칙1을 태우게 한다."""
    try:
        return load_evidence(path)
    except EvidenceParseError:
        return None


def sha256_of_file(path: str | Path) -> str:
    """디스크 실파일의 sha256 (hex, prefix 없음). 커널 법칙3의 artifact 대조에 사용."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(_HASH_CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_digest(value: str) -> str:
    """'sha256:abc...' / 'abc...' / 대문자 표기를 하나의 소문자 hex 로 정규화."""
    v = value.strip()
    if ":" in v:
        v = v.split(":", 1)[1]
    return v.strip().lower()
