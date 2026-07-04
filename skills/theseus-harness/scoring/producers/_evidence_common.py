"""_evidence_common.py — WP5 promote-group producer 공유 유틸 (설계 §5).

measure_dacapo_threshold / measure_deep_module / measure_dry_violation /
measure_define_errors 넷만 쓰는 내부 헬퍼다. measure_submission.py(WP4a, 다른 작업자
소유)는 건드리지 않고, 그 파일이 이미 쓰는 패턴(run_root 기준 상대경로, 자기점검하는
Evidence 조립, 결정적 직렬화)만 여기서 다시 구현해 네 producer 가 공유한다 — 로직을
네 곳에 복제하면 그 자체가 DRY 위반(이 스크립트 군이 감시하는 원칙)이라 단일 지점으로
모았다(§2 원칙4 "줄인다").

verdict/score 는 여기서 만들지 않는다 — Evidence Record 조립(측정값 + provenance)만
책임진다(§5 producer/kernel 분리). `assemble_record` 는 조립 직후 `evidence.from_dict`
로 자기 점검해, 이 헬퍼가 만드는 레코드가 커널이 로드하는 것과 같은 스키마임을 즉시
검증한다.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_KERNEL_DIR = Path(__file__).resolve().parents[1] / "kernel"
if str(_KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(_KERNEL_DIR))
import evidence as evidence_mod  # noqa: E402

EVIDENCE_SCHEMA_VERSION = evidence_mod.EVIDENCE_SCHEMA_VERSION


def now_iso() -> str:
    """UTC ISO8601 — measured_at 기본값(주입 가능; 결정성 테스트는 항상 주입한다)."""
    return datetime.now(timezone.utc).isoformat()


def relpath(abs_path: Path, run_root: Path) -> str:
    """run_root 기준 상대 경로(posix 표기) — 커널 법칙3의 artifact 대조가 이 문자열을 쓴다."""
    return Path(os.path.relpath(abs_path, run_root)).as_posix()


def sha256_of_file(path: Path) -> str:
    return evidence_mod.sha256_of_file(path)


def write_json_artifact(path: Path, data: dict[str, Any]) -> Path:
    """producer 의 raw scan 결과를 backing artifact 로 디스크에 기록.

    이 파일 자체가 measured 값들의 provenance artifact 다 — '이 실행이 실제로 관측한
    원시 리포트'를 가리키게 해, 값이 재현·감사 가능하게 한다(측정 산출물 자체를 backing
    으로 삼는 패턴; measure_submission.py 의 자기관측 manifest.json 과 동일 원리).
    sort_keys 로 직렬화해 같은 report dict 이 항상 같은 바이트를 내도록(결정성, §2 원칙5).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def build_measured(value: Any, source: str, artifact_rel: str) -> dict[str, Any]:
    return {"value": value, "source": source, "artifact_path": artifact_rel}


def assemble_record(
    *,
    check_id: str,
    phase: str,
    project_run: str,
    producer_cmd: str,
    measured: dict[str, dict[str, Any]],
    artifact_digests: dict[str, str],
    measured_at: str,
) -> dict[str, Any]:
    """Evidence Record 조립. produced_by='run', self_reported=False 고정 — 이 producer
    군은 항상 실행 산물(스캔 리포트)을 파싱해서만 값을 낸다(자기 신고 경로가 없다, §3.1).
    """
    record = {
        "evidence_schema_version": EVIDENCE_SCHEMA_VERSION,
        "check_id": check_id,
        "phase": phase,
        "project_run": project_run,
        "produced_by": "run",
        "producer_cmd": producer_cmd,
        "producer_exit_code": 0,
        "measured": measured,
        "artifact_digests": artifact_digests,
        "measured_at": measured_at,
        "self_reported": False,
    }
    # 우리가 emit 하는 레코드가 커널 로더와 같은 스키마임을 즉시 검증(producer 자기 점검).
    evidence_mod.from_dict(record)
    return record


def write_evidence(out_dir: Path, check_id: str, record: dict[str, Any]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{check_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
