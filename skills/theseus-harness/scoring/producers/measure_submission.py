#!/usr/bin/env python3
"""measure_submission.py — scoring 증거 조립기 (설계 §5, §7.1, WP4a).

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다. verdict·score 를 절대 내지
않는다 — 실행 산물(junit/coverage/e2e XML, git diff)을 파싱해 provenance 붙은 원시
measured 값만 Evidence Record 로 emit 한다. 커널(kernel.verify)이 이 레코드를 받아
판정한다.

핵심 불변식 — "손 넣은 숫자" 구조적 봉쇄:
  1. **직접 측정 값**(tests_*, be_coverage, fe_coverage, e2e_*, files_touched,
     fe_side_exists)은 오직 *파일을 파싱해서* 얻는다. CLI 는 artifact *경로* 만 받고,
     어떤 measured 값도 raw 숫자로 주입하는 인자는 존재하지 않는다.
  2. **분석 파생 값**(intent_fidelity, files_mapped_to_todos, modules_passing_solid,
     modules_total, dip_violation, parity_category)은 이 스크립트가 상상하지 않는다.
     `--from-evidence <dir>` 가 가리키는 상류 Evidence Record 파일에서 value+provenance
     를 *승계* 한다. 그 backing 파일이 없으면 값을 emit 하지 않고 **결손 처리** —
     해당 차원 evidence 자체를 쓰지 않으므로 커널 법칙1(evidence_missing)이 FAIL 시킨다.
  3. 모든 measured 값의 `artifact_path` 는 디스크 실파일을 가리키고, 그 실 sha256 이
     `artifact_digests` 에 들어간다. 커널 법칙3이 이를 디스크와 대조하므로, backing
     artifact 없는 숫자는 계약을 통과할 수 없다.

artifact_path/디지털 대조 규약: 모든 상대 경로는 **run_root = out_dir 의 부모** 기준.
meta_audit 는 `<project_root>/evidence/<check_id>.json` 을 읽고 artifact_root=project_root
로 검증하므로, `--out-dir <project_root>/evidence` 로 쓰면 정확히 정합한다.

CLI:
    python measure_submission.py --submission <dir> --test-junit <path> \
        [--coverage <xml>] [--fe-coverage <xml>] [--e2e-junit <path>] \
        [--from-evidence <dir>] [--git-base HEAD] [--project-run <name>] \
        [--measured-at <ISO8601>] --out-dir <run>/evidence

저장소 self_lint C35 — 모든 open/subprocess `encoding="utf-8"`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import parsers

# evidence.py(kernel)의 sha256_of_file/schema 버전/형태검증을 재사용한다 — producer 가
# emit 하는 레코드가 커널이 로드하는 것과 같은 스키마임을 한 소스로 보증(§2 원칙4).
_KERNEL_DIR = Path(__file__).resolve().parents[1] / "kernel"
if str(_KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(_KERNEL_DIR))
import evidence as evidence_mod  # noqa: E402

PHASE = "09"

# 차원별 필수 measured 키. coverage/fe_be_parity 는 fe_side 존재 여부에 따라 동적으로
# 확장된다(단일 사이드면 fe_coverage/parity_category 를 요구하지 않는다 — 적용성 NA).
_BASE_DIMENSIONS: dict[str, list[str]] = {
    "scoring.correctness": ["tests_total", "tests_passed", "tests_failed", "intent_fidelity"],
    "scoring.scope_fit": ["files_touched", "files_mapped_to_todos"],
    "scoring.solid": ["modules_passing_solid", "modules_total", "dip_violation"],
    "scoring.e2e": ["e2e_total", "e2e_passing"],
    "scoring.coverage": ["be_coverage", "fe_side_exists"],
    "scoring.fe_be_parity": ["fe_side_exists"],
}

# from-evidence 로만 채울 수 있는 분석 파생 키 — 직접 측정 경로가 없다(손 넣기 봉쇄).
_DERIVED_KEYS = frozenset(
    {
        "intent_fidelity",
        "files_mapped_to_todos",
        "modules_passing_solid",
        "modules_total",
        "dip_violation",
        "parity_category",
    }
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _relpath(abs_path: Path, run_root: Path) -> str:
    """run_root 기준 상대 경로(posix 표기) — 커널 artifact 대조가 이 문자열을 쓴다."""
    import os

    return Path(os.path.relpath(abs_path, run_root)).as_posix()


class _ArtifactPool:
    """측정 결과 누적기 — measured 엔트리 + 그 backing artifact 의 실 digest.

    책임 하나: (key -> {value,source,artifact_path}) 와 (rel_path -> sha256) 를 정합하게
    유지. 차원 evidence 는 이 풀에서 필요한 키만 골라 조립된다.
    """

    def __init__(self, run_root: Path) -> None:
        self.run_root = run_root
        self.measured: dict[str, dict[str, Any]] = {}
        self.digests: dict[str, str] = {}
        self.deficits: dict[str, str] = {}

    def _register(self, abs_path: Path) -> str:
        rel = _relpath(abs_path, self.run_root)
        if rel not in self.digests:
            self.digests[rel] = evidence_mod.sha256_of_file(abs_path)
        return rel

    def add(self, key: str, value: Any, source: str, artifact_abs: Path) -> None:
        rel = self._register(artifact_abs)
        self.measured[key] = {"value": value, "source": source, "artifact_path": rel}

    def deficit(self, key: str, reason: str) -> None:
        self.deficits[key] = reason


# --- from-evidence 승계 (분석 파생 값의 유일 입구) ------------------------------


def _index_from_evidence(from_evidence_dir: Path) -> dict[str, tuple[Any, Path]]:
    """--from-evidence 디렉터리의 상류 Evidence Record 들을 key -> (value, file) 로 색인.

    상류 파일은 Evidence Contract 의 `measured` 형태({key:{value,...}})를 가져야 한다.
    같은 키를 여러 파일이 제공하면 파일명 정렬 첫 파일이 이긴다(결정성). value 필드가
    없는 엔트리는 무시 — 값 없는 provenance 는 승계할 수 없다.
    """
    index: dict[str, tuple[Any, Path]] = {}
    if not from_evidence_dir.is_dir():
        return index
    for jf in sorted(from_evidence_dir.glob("*.json")):
        try:
            data = json.loads(jf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        measured = data.get("measured") if isinstance(data, dict) else None
        if not isinstance(measured, dict):
            continue
        for key, entry in measured.items():
            if key in index:
                continue
            if isinstance(entry, dict) and "value" in entry:
                index[key] = (entry["value"], jf)
    return index


def _add_derived(pool: _ArtifactPool, key: str, index: dict[str, tuple[Any, Path]]) -> None:
    """파생 키를 상류 evidence 에서 승계. 없으면 결손 — 상상하지 않는다."""
    if key not in index:
        pool.deficit(key, "no backing evidence in --from-evidence (analysis producer absent)")
        return
    value, src_file = index[key]
    # backing artifact = 상류 evidence 파일 자체. 그 실 sha256 을 우리 evidence 가 pin
    # 하므로, 커널이 상류 파일 존재+해시를 대조한다(승계 값의 provenance 사슬).
    pool.add(key, value, f"from_evidence:{src_file.name}", src_file)


# --- 직접 측정 (실행 산물 파싱) ------------------------------------------------


def _measure_tests(pool: _ArtifactPool, junit_path: Path) -> None:
    try:
        c = parsers.parse_junit(junit_path)
    except parsers.ArtifactParseError as exc:
        for k in ("tests_total", "tests_passed", "tests_failed"):
            pool.deficit(k, f"test junit unparseable: {exc}")
        return
    pool.add("tests_total", c.total, "junit_xml", junit_path)
    pool.add("tests_passed", c.passed, "junit_xml", junit_path)
    pool.add("tests_failed", c.failed, "junit_xml", junit_path)


def _measure_e2e(pool: _ArtifactPool, e2e_path: Path) -> None:
    try:
        c = parsers.parse_junit(e2e_path)
    except parsers.ArtifactParseError as exc:
        for k in ("e2e_total", "e2e_passing"):
            pool.deficit(k, f"e2e junit unparseable: {exc}")
        return
    pool.add("e2e_total", c.total, "junit_xml_e2e", e2e_path)
    pool.add("e2e_passing", c.passed, "junit_xml_e2e", e2e_path)


def _measure_coverage(pool: _ArtifactPool, key: str, cov_path: Path, source: str) -> None:
    try:
        rate = parsers.parse_coverage(cov_path)
    except parsers.ArtifactParseError as exc:
        pool.deficit(key, f"coverage unparseable: {exc}")
        return
    pool.add(key, rate, source, cov_path)


def _git_diff_files(submission: Path, base: str) -> tuple[list[str] | None, str | None]:
    """git diff --name-only <base> 로 변경 파일 목록. 실패 시 (None, error)."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(submission), "diff", "--name-only", base],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, ValueError) as exc:
        return None, f"git invocation failed: {exc}"
    if proc.returncode != 0:
        return None, f"git diff exit {proc.returncode}: {proc.stderr.strip()}"
    files = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    return files, None


def _write_manifest(
    run_root: Path,
    submission: Path,
    git_base: str,
    git_files: list[str] | None,
    git_error: str | None,
    fe_side_exists: int,
    inputs_provided: dict[str, bool],
) -> Path:
    """producer 자기 관측 artifact — files_touched/fe_side_exists 의 backing 근거."""
    manifest = {
        "submission": str(submission),
        "git_base": git_base,
        "git_diff_files": git_files,
        "git_error": git_error,
        "fe_side_exists": fe_side_exists,
        "inputs_provided": inputs_provided,
    }
    path = run_root / "measure_submission.manifest.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


# --- evidence 조립 -------------------------------------------------------------


def _build_record(
    check_id: str,
    keys: list[str],
    pool: _ArtifactPool,
    project_run: str,
    producer_cmd: str,
    measured_at: str,
) -> dict[str, Any]:
    measured = {k: pool.measured[k] for k in keys}
    digests: dict[str, str] = {}
    for k in keys:
        ap = pool.measured[k]["artifact_path"]
        digests[ap] = pool.digests[ap]
    record = {
        "evidence_schema_version": evidence_mod.EVIDENCE_SCHEMA_VERSION,
        "check_id": check_id,
        "phase": PHASE,
        "project_run": project_run,
        "produced_by": "run",
        "producer_cmd": producer_cmd,
        "producer_exit_code": 0,
        "measured": measured,
        "artifact_digests": digests,
        "measured_at": measured_at,
        "self_reported": False,
    }
    # 우리가 emit 하는 레코드가 커널 로더와 같은 스키마임을 즉시 검증(producer 자기 점검).
    evidence_mod.from_dict(record)
    return record


def _dimension_keysets(pool: _ArtifactPool) -> dict[str, list[str]]:
    """차원별 필수 키 — fe_side 존재 시 coverage/fe_be_parity 를 dual-side 키로 확장."""
    fe_on = pool.measured.get("fe_side_exists", {}).get("value") == 1
    dims = {cid: list(keys) for cid, keys in _BASE_DIMENSIONS.items()}
    if fe_on:
        dims["scoring.coverage"].append("fe_coverage")
        dims["scoring.fe_be_parity"].append("parity_category")
    return dims


def assemble(pool: _ArtifactPool, project_run: str, producer_cmd: str, measured_at: str):
    """풀에서 차원별 evidence 를 조립. 필수 키가 하나라도 결손이면 그 차원은 emit 안 함
    (evidence 부재 → 커널 법칙1 FAIL). 반환: (emitted_records, skipped_reasons)."""
    dims = _dimension_keysets(pool)
    emitted: dict[str, dict[str, Any]] = {}
    skipped: dict[str, list[str]] = {}
    for check_id, keys in dims.items():
        missing = [k for k in keys if k not in pool.measured]
        if missing:
            skipped[check_id] = missing
            continue
        emitted[check_id] = _build_record(
            check_id, keys, pool, project_run, producer_cmd, measured_at
        )
    return emitted, skipped


# --- CLI -----------------------------------------------------------------------


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 문자열 재구성 — CheckSpec cmd_pattern `^python .*measure_submission\\.py`
    과 정합하도록 'python <script> <args>' 형태. 실 호출을 충실히 반영한다."""
    parts = ["python", str(Path(__file__).resolve())]
    parts += ["--submission", args.submission, "--test-junit", args.test_junit]
    if args.coverage:
        parts += ["--coverage", args.coverage]
    if args.fe_coverage:
        parts += ["--fe-coverage", args.fe_coverage]
    if args.e2e_junit:
        parts += ["--e2e-junit", args.e2e_junit]
    if args.from_evidence:
        parts += ["--from-evidence", args.from_evidence]
    parts += ["--git-base", args.git_base, "--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or _now_iso()
    producer_cmd = _reconstruct_cmd(args)

    pool = _ArtifactPool(run_root)

    # 직접 측정 — 실행 산물 파싱.
    _measure_tests(pool, Path(args.test_junit).resolve())
    if args.coverage:
        _measure_coverage(pool, "be_coverage", Path(args.coverage).resolve(), "coverage_xml")
    else:
        pool.deficit("be_coverage", "no --coverage artifact provided")
    if args.fe_coverage:
        _measure_coverage(pool, "fe_coverage", Path(args.fe_coverage).resolve(), "coverage_xml_fe")
    if args.e2e_junit:
        _measure_e2e(pool, Path(args.e2e_junit).resolve())
    else:
        for k in ("e2e_total", "e2e_passing"):
            pool.deficit(k, "no --e2e-junit artifact provided")

    # git diff → 자기 관측 manifest → files_touched + fe_side_exists.
    submission = Path(args.submission).resolve()
    git_files, git_error = _git_diff_files(submission, args.git_base)
    fe_side_exists = 1 if args.fe_coverage else 0
    inputs_provided = {
        "test_junit": True,
        "coverage": bool(args.coverage),
        "fe_coverage": bool(args.fe_coverage),
        "e2e_junit": bool(args.e2e_junit),
    }
    manifest_path = _write_manifest(
        run_root, submission, args.git_base, git_files, git_error, fe_side_exists, inputs_provided
    )
    pool.add("fe_side_exists", fe_side_exists, "submission_manifest", manifest_path)
    if git_files is not None:
        pool.add("files_touched", len(git_files), "git_diff_name_only", manifest_path)
    else:
        pool.deficit("files_touched", git_error or "git diff unavailable")

    # 분석 파생 값 — from-evidence 승계만. backing 없으면 결손.
    index = _index_from_evidence(Path(args.from_evidence).resolve()) if args.from_evidence else {}
    for key in sorted(_DERIVED_KEYS):
        _add_derived(pool, key, index)

    emitted, skipped = assemble(pool, project_run, producer_cmd, measured_at)

    out_dir.mkdir(parents=True, exist_ok=True)
    for check_id, record in emitted.items():
        (out_dir / f"{check_id}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return {
        "out_dir": str(out_dir),
        "emitted": sorted(emitted.keys()),
        "skipped": skipped,
        "deficits": pool.deficits,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_submission — scoring 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument("--submission", required=True, help="제출물 디렉터리 (git diff 대상)")
    p.add_argument("--test-junit", required=True, help="단위/통합 테스트 junit XML 경로")
    p.add_argument("--coverage", default=None, help="BE coverage.xml (Cobertura) 경로")
    p.add_argument("--fe-coverage", default=None, help="FE coverage.xml 경로 (있으면 dual-side)")
    p.add_argument("--e2e-junit", default=None, help="e2e junit XML 경로")
    p.add_argument(
        "--from-evidence",
        default=None,
        help="분석 파생 값 승계용 상류 Evidence Record 디렉터리 (손 넣기 대신 유일 입구)",
    )
    p.add_argument("--git-base", default="HEAD", help="git diff base ref (기본 HEAD)")
    p.add_argument("--project-run", default=None, help="project_run 이름 (기본: run_root.name)")
    p.add_argument("--measured-at", default=None, help="measured_at 주입(결정성 테스트용)")
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<project_root>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    summary = run(args)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
