#!/usr/bin/env python3
"""measure_scope_map.py — gate.scope_map 증거 조립기 (판단-게이트 스펙 §3.3, JW3).

phase 06 이 저작한 plan-todos.json(반증가능 claim 아님 — todo id + path glob 목록)과
`git diff --name-only <base>` 로 관측한 touched 파일 집합을 `claims.match_glob` 하나로
교차해 `files_mapped_to_todos`(파일 단위 계수) 하나만 raw 값으로 emit 한다. 판정은
내지 않는다 — measure_submission.py `--from-evidence` 가 이 값을 승계하고, 커널이
CheckSpec `checks/scoring.scope_fit.json` 으로 최종 판정한다(§5 producer/kernel 분리).

핵심 불변식(스펙 §2, §3.3):
  - plan-todos 는 **선언**(무엇을 볼지)만 담는다. 판정 필드(verified/score/pass/passed/
    result/verdict)가 엔트리에 있으면 그 자체가 계약 위반 — emit 없이 exit 2(구체화
    결정 5).
  - **결손(no-emit) 조건**: plan-todos 파일 부재 / todos 0개 / git diff 실패(None).
    이 셋은 "측정 불가"이지 "선언이 틀렸다"가 아니므로 exit 0 으로 정직하게 구분한다
    (구체화 결정 6). **빈 diff(변경 없음)는 결손이 아니다** — touched 집합 관측은
    성공했으므로 `files_mapped_to_todos = 0` 을 emit 한다(커널의 `files_touched > 0`
    assertion 이 이 경우를 정직하게 FAIL 시킨다, measure_submission 소관).
  - **파일 단위 계수**: touched 파일 하나가 여러 todo 의 glob 에 걸려도 1로만 센다.
    matched ⊆ touched 이므로 같은 `--git-base`·submission 에서
    `files_mapped_to_todos <= files_touched` 가 구조적으로 성립한다(스펙 §4.2).
  - `files_touched_observed` 는 리포트 전용 관측값이다 — `files_touched` 는
    measure_submission 이 자기 git diff 로 직접 측정하므로 여기서는 emit 하지 않는다.

CLI:
    python measure_scope_map.py --plan-todos <plan-todos.json> --submission <dir> \\
        [--git-base HEAD] [--phase 09] [--project-run <name>] \\
        [--measured-at <ISO8601>] --out-dir <run>/evidence

저장소 self_lint C35 — 모든 open/subprocess `encoding="utf-8"`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import claims

import _evidence_common as ec

from _stdio import force_utf8_stdio  # noqa: E402

CHECK_ID = "gate.scope_map"
DEFAULT_PHASE = "09"
SOURCE = "todo_glob_git_diff"

# 선언 아티팩트(plan-todos)에 판정 필드가 있으면 즉시 거부(구체화 결정 5).
_VERDICT_KEYS = frozenset({"verified", "score", "pass", "passed", "result", "verdict"})


class ScopeMapSchemaError(ValueError):
    """plan-todos 저작 오류(JSON 파싱 불가·스키마 위반·판정 필드 포함) — exit 2.

    "선언이 없어서 못 잰다"(결손, exit 0)와 "선언이 틀렸다"(저작 오류, exit 2)를
    예외 타입으로 구분한다(구체화 결정 6).
    """


def _load_todos(path: Path) -> list[dict[str, Any]]:
    """plan-todos.json 로드 + 스키마 검증. 위반 시 ScopeMapSchemaError.

    최상위 `{"todos": [...]}`; 엔트리 `id`(str, 중복 금지) + `paths`(비어있지 않은
    str 리스트). `text` 는 선택 — 검사에 안 쓰고 리포트에 그대로 통과시킨다(엔트리를
    그대로 반환하므로 별도 처리 불필요).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ScopeMapSchemaError(f"cannot read plan-todos file: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ScopeMapSchemaError(f"plan-todos JSON malformed: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("todos"), list):
        raise ScopeMapSchemaError('plan-todos top-level must be {"todos": [...]}')
    todos = data["todos"]
    seen_ids: set[str] = set()
    for i, entry in enumerate(todos):
        if not isinstance(entry, dict):
            raise ScopeMapSchemaError(f"todos[{i}] must be an object")
        hit = _VERDICT_KEYS & entry.keys()
        if hit:
            raise ScopeMapSchemaError(
                f"todos[{i}] carries judgment field(s) {sorted(hit)} - "
                "declarative artifacts must not embed verdicts"
            )
        tid = entry.get("id")
        if not isinstance(tid, str) or not tid:
            raise ScopeMapSchemaError(f"todos[{i}].id must be a non-empty string")
        if tid in seen_ids:
            raise ScopeMapSchemaError(f"duplicate todo id: {tid}")
        seen_ids.add(tid)
        paths = entry.get("paths")
        if (
            not isinstance(paths, list)
            or not paths
            or not all(isinstance(p, str) and p for p in paths)
        ):
            raise ScopeMapSchemaError(
                f"todos[{i}].paths must be a non-empty list of non-empty strings"
            )
    return todos


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    return " ".join(
        [
            "python",
            str(Path(__file__).resolve()),
            "--plan-todos",
            args.plan_todos,
            "--submission",
            args.submission,
            "--git-base",
            args.git_base,
            "--out-dir",
            args.out_dir,
        ]
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    """알고리즘 7단계(스펙 §3.3). `ScopeMapSchemaError` 는 저작 오류(main() 이 exit 2로
    변환) — 그 외 경로는 emit True/False 어느 쪽이든 exit 0(결손도 정상 종료)."""
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    # 1. plan-todos 파일 부재 → emit 안 함, exit 0 (결손).
    plan_todos_path = Path(args.plan_todos)
    if not plan_todos_path.is_file():
        return {"emitted": False, "reason": "plan-todos file absent"}

    # 2. 스키마 검증(위반 → ScopeMapSchemaError, main() 이 exit 2 로 변환).
    todos = _load_todos(plan_todos_path)

    # 3. todos 0개 → emit 안 함, exit 0 (결손 — 매핑 주장이 없으면 측정이 아니다).
    if not todos:
        return {"emitted": False, "reason": "no todos declared - refusing vacuous measurement"}

    # 4. git diff. None(실패) → emit 안 함, exit 0. **빈 리스트는 실패가 아니다.**
    submission = Path(args.submission).resolve()
    git_files, git_error = claims.git_diff_files(submission, args.git_base)
    if git_files is None:
        return {
            "emitted": False,
            "reason": "git diff failed - cannot observe touched file set",
            "git_error": git_error,
        }

    # 5. 매칭 — 파일 단위 계수(여러 todo 에 걸려도 1). matched ⊆ touched.
    report_files: list[dict[str, Any]] = []
    mapped_count = 0
    for f in sorted(git_files):
        matched = [t["id"] for t in todos if any(claims.match_glob(f, p) for p in t["paths"])]
        if matched:
            mapped_count += 1
        report_files.append({"path": f, "matched_todos": matched})

    # 6. 리포트 — files_touched_observed 는 리포트 전용(measured 로 emit 하지 않음).
    #    절대경로 없음: git_base 는 ref 문자열, files/todos 는 상대경로/글롭 문자열뿐.
    report = {
        "git_base": args.git_base,
        "files_touched_observed": len(git_files),
        "files": report_files,
        "todos": todos,
        "value": mapped_count,
    }
    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    rel = ec.relpath(report_path, run_root)
    digest = ec.sha256_of_file(report_path)

    # 7. measured 하나만 emit.
    measured = {
        "files_mapped_to_todos": ec.build_measured(mapped_count, SOURCE, rel),
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
        "evidence_path": str(evidence_path),
        "report_path": str(report_path),
        "value": mapped_count,
        "files_touched_observed": len(git_files),
        "git_base": args.git_base,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_scope_map — gate.scope_map 증거 조립기 (verdict 없음, §5)"
    )
    p.add_argument("--plan-todos", required=True, help="phase 06 이 저작한 plan-todos.json 경로")
    p.add_argument("--submission", required=True, help="제출물 디렉터리 (git diff 대상)")
    p.add_argument("--git-base", default="HEAD", help="git diff base ref (기본 HEAD)")
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
    p.add_argument("--project-run", default=None)
    p.add_argument("--measured-at", default=None)
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<run>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)
    try:
        summary = run(args)
    except ScopeMapSchemaError as exc:
        print(f"measure_scope_map: plan-todos schema error: {exc}", file=sys.stderr)
        return 2
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
