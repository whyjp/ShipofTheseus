#!/usr/bin/env python3
"""run_gate.py — phase-09 게이트 러너 (설계 B1 §2, WP-B1a).

실 run 에서 커널이 phase-09 의 *실제 게이트* 가 되게 하는 단일 결정적 진입점이다.
producer 오케스트레이션 → meta_audit → verdict 를 낸다. 이 파일은 dogfood.py 의
오케스트레이션을 **흡수(이동)** 한 것이다 — dogfood.py 는 이제 이 라이브러리 API 를
자기 기본값·자기 exit 의미론으로 부르는 얇은 wrapper 다(§2.5 DRY, 오케스트레이션 1벌).

상상값 주입 0: 이 러너는 어떤 measured 값도 스스로 만들지 않는다. producer 가 파일을
파싱해 emit 한 Evidence 만 커널(meta_audit)에 태우고, verdict 는 전적으로 커널이 낸다 —
러너는 오케스트레이션 + exit 매핑만 소유한다(producer/kernel 분리).

exit 의미론(dogfood 와 다름 — verdict 가 곧 exit):
  - exit 0 = meta_audit verdict `pass` (게이팅 집합 기준)
  - exit 1 = verdict `fail` — phase-09 진행 차단
  - exit 2 = pipeline 크래시(verdict 미산출) — 부재는 통과가 아니라 별도 실패

산출물(전부 --project-root 아래):
    evidence/<check_id>.json          producer emit (실행마다 선청소 — stale 봉쇄)
    results/junit.xml                 러너가 직접 실행한 pytest
    quality/gate_meta_audit.json      verdict 아티팩트 (하류 phase 확인 대상)
    state/gate_history/<NN>/          이번 실행의 evidence + verdict 사본 (sprint.regression prior 소스)

실행 단계(§2.2, dogfood 순서 계승 + plan/sprint 신규):
    1 junit  2 quality  3 gates  4 plan  5 submission  6 sprint  7 cold
    8 meta_audit  9 archive
순서 의존(2→3→5): quality/gates evidence 가 먼저 디스크에 있어야 measure_submission 의
`--from-evidence` 가 modules_total/gate 값을 승계한다. sprint(6)는 submission(5)이 낳은
현재 scoring.correctness.json 을 --current 로 읽으므로 submission 뒤에 둔다.

저장소 self_lint C35 — 모든 open/subprocess encoding="utf-8". main() 맨 앞 force_utf8_stdio().
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_SCORING_DIR = Path(__file__).resolve().parent
_PRODUCERS_DIR = _SCORING_DIR / "producers"
_KERNEL_DIR = _SCORING_DIR / "kernel"
# scoring -> theseus-harness -> skills -> <repo root>.
_REPO_ROOT = _SCORING_DIR.parents[2]

# kernel/_stdio 의 공유 UTF-8 강제 헬퍼(cp949 콘솔에서 비-ASCII print 크래시 방지).
if str(_KERNEL_DIR) not in sys.path:
    sys.path.insert(0, str(_KERNEL_DIR))
from _stdio import force_utf8_stdio  # noqa: E402


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    """subprocess 한 번 실행 → {cmd, returncode, stdout, stderr}. text/utf-8 고정(C35)."""
    proc = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def _parse_json_stdout(step: dict[str, Any]) -> dict[str, Any] | None:
    """producer 는 요약 JSON 을 stdout 으로 낸다 — 파싱 실패는 None(감사 추적용)."""
    try:
        return json.loads(step["stdout"])
    except (json.JSONDecodeError, TypeError):
        return None


# --- pytest (자기 테스트 실행 → junit) -----------------------------------------


def _produce_junit(
    test_target: Path, junit_path: Path, reuse_junit: Path | None, cwd: Path
) -> dict[str, Any]:
    """테스트를 junit 으로 실행. --junit 재사용 시 pytest 를 돌리지 않고 복사(테스트가
    pytest-in-pytest 재귀를 피하는 seam). 반환에 pytest exit 를 담아 tests_* 실측 근거를
    감사 가능하게 한다."""
    junit_path.parent.mkdir(parents=True, exist_ok=True)
    if reuse_junit is not None:
        shutil.copyfile(reuse_junit, junit_path)
        return {"ran_pytest": False, "reused": str(reuse_junit), "junit": str(junit_path)}
    step = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_target),
            "-q",
            f"--junitxml={junit_path}",
        ],
        cwd,
    )
    return {
        "ran_pytest": True,
        "pytest_returncode": step["returncode"],
        "junit": str(junit_path),
        "tail": step["stdout"].splitlines()[-3:] if step["stdout"] else [],
    }


# --- producer 호출 -------------------------------------------------------------


def _quality_producers(
    code_root: Path, evidence_dir: Path, measured_at: str, cwd: Path
) -> dict[str, Any]:
    """WP5 승격군 producer 3종을 code_root 에 돌려 quality.* evidence 조립."""
    out: dict[str, Any] = {}
    specs = [
        ("deep_module", _PRODUCERS_DIR / "measure_deep_module.py"),
        ("dry", _PRODUCERS_DIR / "measure_dry_violation.py"),
        ("define_errors", _PRODUCERS_DIR / "measure_define_errors.py"),
    ]
    for name, script in specs:
        step = _run(
            [
                sys.executable,
                str(script),
                "--code-root",
                str(code_root),
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out[name] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    return out


def _gate_producers(
    submission: Path,
    code_root: Path,
    junit_path: Path,
    evidence_dir: Path,
    git_base: str,
    intent_criteria: Path,
    plan_todos: Path,
    solid_contract: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """판단-게이트 producer 3종을 코드에 적용해 `intent_fidelity`/`files_mapped_to_todos`/
    `modules_passing_solid`+`dip_violation` 을 실측 backing 으로 emit(설계 §6.5). quality
    뒤·submission 앞이어야 measure_submission 의 `--from-evidence` 가 이 세 evidence 를
    함께 승계한다.

    선언 아티팩트(criteria/todos/contract)가 디스크에 없으면 그 producer 는 아예 부르지
    않고 사유만 기록한다(정직한 결손 경로 보존 — 러너는 값을 만들지 않는다)."""
    out: dict[str, Any] = {}

    if intent_criteria.is_file():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_intent_fidelity.py"),
                "--criteria",
                str(intent_criteria),
                "--submission",
                str(submission),
                "--test-junit",
                str(junit_path),
                "--git-base",
                git_base,
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["intent_fidelity"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["intent_fidelity"] = {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "intent-criteria 파일 부재 — measure_intent_fidelity 미실행",
            },
        }

    if plan_todos.is_file():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_scope_map.py"),
                "--plan-todos",
                str(plan_todos),
                "--submission",
                str(submission),
                "--git-base",
                git_base,
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["scope_map"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["scope_map"] = {
            "returncode": None,
            "summary": {"emitted": False, "reason": "plan-todos 파일 부재 — measure_scope_map 미실행"},
        }

    if solid_contract.is_file():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_solid_static.py"),
                "--code-root",
                str(code_root),
                "--solid-contract",
                str(solid_contract),
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["solid_static"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["solid_static"] = {
            "returncode": None,
            "summary": {"emitted": False, "reason": "solid-contract 파일 부재 — measure_solid_static 미실행"},
        }

    return out


def _plan_producers(
    plan_dir: Path,
    tournament_md: Path | None,
    shadow_grades_dir: Path | None,
    evidence_dir: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """plan.* producer 3종(§2.2 단계 4, run_gate 신규). tournament-md 로 dacapo_threshold,
    shadow-grade glob 으로 tournament_independence, 최종 tournament 로 tournament_winner_argmax
    (병합/승자 소유)를 emit 한다. 앞 둘은 artifact 부재 시 producer 를 부르지 않고 사유만
    기록하지만, tournament_winner_argmax 는 항상 호출(producer 가 tournament 부재 시 스스로
    미방출) → 병합 소유는 무조건 발동. evidence 부재 → 커널 법칙1 FAIL(정직). dogfood 는 이
    단계를 비활성화한다(plan/sprint 미호출은 dogfood 특수성)."""
    out: dict[str, Any] = {}

    if tournament_md is not None and tournament_md.is_file():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_dacapo_threshold.py"),
                "--tournament-md",
                str(tournament_md),
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["dacapo_threshold"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["dacapo_threshold"] = {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "tournament-md 부재 — measure_dacapo_threshold 미실행",
            },
        }

    if shadow_grades_dir is not None and shadow_grades_dir.is_dir():
        step = _run(
            [
                sys.executable,
                str(_PRODUCERS_DIR / "measure_tournament.py"),
                "--shadow-grades-dir",
                str(shadow_grades_dir),
                "--measured-at",
                measured_at,
                "--out-dir",
                str(evidence_dir),
            ],
            cwd,
        )
        out["tournament_independence"] = {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}
    else:
        out["tournament_independence"] = {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "shadow-grades 디렉터리 부재 — measure_tournament 미실행",
            },
        }

    # 병합/승자 소유(run_gate 신규) — 항상 호출. producer 가 최종 tournament/winner_id 부재 시
    # 스스로 evidence 를 안 낸다(그 경우 G3+ 는 absence_policy FAIL). tournament_md 처럼 미리
    # 가드하지 않는 이유: 병합 소유는 tournament 가 있으면 무조건 발동해야 한다(declared=invoked C-TWA).
    step = _run(
        [
            sys.executable,
            str(_PRODUCERS_DIR / "measure_tournament_argmax.py"),
            "--measured-at",
            measured_at,
            "--out-dir",
            str(evidence_dir),
        ],
        cwd,
    )
    out["tournament_winner_argmax"] = {
        "returncode": step["returncode"],
        "summary": _parse_json_stdout(step),
    }

    return out


def _submission_producer(
    submission: Path,
    junit_path: Path,
    evidence_dir: Path,
    git_base: str,
    coverage: Path | None,
    e2e_junit: Path | None,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """measure_submission 으로 scoring.* evidence 조립. --from-evidence 로 quality/gate
    evidence 를 승계. coverage/e2e-junit 은 있으면 패스스루(러너는 도구 정책 무판단)."""
    cmd = [
        sys.executable,
        str(_PRODUCERS_DIR / "measure_submission.py"),
        "--submission",
        str(submission),
        "--test-junit",
        str(junit_path),
        "--from-evidence",
        str(evidence_dir),
        "--git-base",
        git_base,
        "--measured-at",
        measured_at,
        "--out-dir",
        str(evidence_dir),
    ]
    if coverage is not None:
        cmd += ["--coverage", str(coverage)]
    if e2e_junit is not None:
        cmd += ["--e2e-junit", str(e2e_junit)]
    step = _run(cmd, cwd)
    return {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}


# sprint.regression 이 회귀 감시하는 correctness 스칼라. scoring.correctness 의 value 는
# 파생식((tests_passed/tests_total)*intent_fidelity)이라 단일 스칼라가 아니므로, evidence
# measured 에 실린 intent_fidelity(정직-검사된 correctness 신호)를 회귀 대상으로 뽑는다.
_SPRINT_SCORE_KEY = "intent_fidelity"


def _sprint_producer(
    prior: Path | None,
    current: Path,
    evidence_dir: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """sprint.regression producer(§2.2 단계 6, run_gate 신규). gate_history 최신의
    scoring.correctness.json(prior) 과 이번 실행의 evidence/scoring.correctness.json
    (current) 을 measure_regression 에 태워 score delta 를 emit 한다. 두 correctness evidence
    는 Evidence Record 라 measured 스칼라 키(--score-key)로 점수를 뽑는다. prior/current 부재
    시 미실행 → evidence 부재(첫 실행은 --phase-upto 게이팅이 deferred 로 처리). dogfood 는
    이 단계를 비활성화한다."""
    if prior is None or not prior.is_file():
        return {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "prior score(gate_history) 부재 — measure_regression 미실행(첫 실행)",
            },
        }
    if not current.is_file():
        return {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "current scoring.correctness evidence 부재 — measure_regression 미실행",
            },
        }
    step = _run(
        [
            sys.executable,
            str(_PRODUCERS_DIR / "measure_regression.py"),
            "--prior",
            str(prior),
            "--current",
            str(current),
            "--score-key",
            _SPRINT_SCORE_KEY,
            "--measured-at",
            measured_at,
            "--out-dir",
            str(evidence_dir),
        ],
        cwd,
    )
    return {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}


def _cold_producer(
    reunderstanding: Path | None,
    reference: Path | None,
    evidence_dir: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """measure_cold_isolation 으로 cold.isolation evidence 조립. dispatch 로그를 주지
    않으므로 dispatch_log_present=0 → meta_audit 가 NA(§7.4). 두 텍스트가 없으면 producer
    를 안 부르고 사유만 기록 → evidence 부재 → 커널 법칙1 FAIL(정직한 결손)."""
    if reunderstanding is None or reference is None or not (
        reunderstanding.exists() and reference.exists()
    ):
        return {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "cold-read/reference 파일 부재 — cold.isolation producer 미실행",
            },
        }
    step = _run(
        [
            sys.executable,
            str(_PRODUCERS_DIR / "measure_cold_isolation.py"),
            "--reunderstanding",
            str(reunderstanding),
            "--reference",
            str(reference),
            "--measured-at",
            measured_at,
            "--out-dir",
            str(evidence_dir),
        ],
        cwd,
    )
    return {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}


def _review_producer(
    dispatch_log: Path | None,
    evidence_dir: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """review.context_minimality producer(pure-review 순도, run_gate 신규). 관례 경로의
    리뷰 디스패치 로그를 measure_context_minimality 에 태워 prior_context/무결성/freshness/
    최소성을 emit 한다. 로그 부재 시 producer 를 안 부르고 사유만 기록 → evidence 부재 →
    커널 법칙1 FAIL(정직). cold.isolation 과 달리 CheckSpec 에 applicability 가 없어 부재가
    NA 가 아니라 FAIL 이다(비휴면: 페이즈 09 게이트까지 pure-review 디스패치 로깅 의무)."""
    if dispatch_log is None or not dispatch_log.is_file():
        return {
            "returncode": None,
            "summary": {
                "emitted": False,
                "reason": "review dispatch 로그 부재 — measure_context_minimality 미실행",
            },
        }
    step = _run(
        [
            sys.executable,
            str(_PRODUCERS_DIR / "measure_context_minimality.py"),
            "--dispatch-log",
            str(dispatch_log),
            "--measured-at",
            measured_at,
            "--out-dir",
            str(evidence_dir),
        ],
        cwd,
    )
    return {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}


def _multiverse_producer(
    grade: str,
    evidence_dir: Path,
    measured_at: str,
    cwd: Path,
) -> dict[str, Any]:
    """multiverse.fan_out_width producer(폭 강제 primitive, run_gate 신규). plan 초기 fan-out
    폭이 grade 활성 폭(manifest multiverse_widths) 바닥을 채웠는지 디스크에서 세어 emit 한다.
    항상 호출한다 — cold/review 처럼 입력 파일을 미리 가드하지 않는 이유: 입력이 항상 존재하는
    run_root(plan/ 스캔)라 '폭 강제'는 무조건 발동해야 한다(declared=invoked, C-MFW). producer 는
    plan 디렉터리 부재 시 스스로 evidence 를 안 낸다 — 그 경우 G3+ 는 absence_policy FAIL 로
    강제되고 G2 는 체크 맵 제외라 무영향(멀티버스 없음)."""
    step = _run(
        [
            sys.executable,
            str(_PRODUCERS_DIR / "measure_multiverse_width.py"),
            "--grade",
            grade,
            "--measured-at",
            measured_at,
            "--out-dir",
            str(evidence_dir),
        ],
        cwd,
    )
    return {"returncode": step["returncode"], "summary": _parse_json_stdout(step)}


# --- meta_audit --------------------------------------------------------------


def _meta_audit(
    run_root: Path,
    grade: str,
    verified_at: str,
    phase_upto: str | None,
    cwd: Path,
) -> dict[str, Any]:
    """생성형 meta_audit 를 레지스트리 열거로 실행 → run verdict + gate_meta_audit.json.
    phase_upto 는 지정된 경우에만 CLI 로 전달한다 — None 이면 인자를 아예 붙이지 않아
    meta_audit 의 기존(전 체크 게이팅) 경로를 바이트까지 보존한다(dogfood behavior-preserving)."""
    gate_path = run_root / "quality" / "gate_meta_audit.json"
    cmd = [
        sys.executable,
        str(_KERNEL_DIR / "meta_audit.py"),
        "--project-root",
        str(run_root),
        "--grade",
        grade,
        "--output",
        str(gate_path),
        "--verified-at",
        verified_at,
    ]
    if phase_upto is not None:
        cmd += ["--phase-upto", phase_upto]
    step = _run(cmd, cwd)
    report = _parse_json_stdout(step)
    if report is None and gate_path.exists():
        report = json.loads(gate_path.read_text(encoding="utf-8"))
    return {"returncode": step["returncode"], "gate_path": str(gate_path), "report": report}


# --- gate_history 아카이브 -----------------------------------------------------


def _next_history_index(history_root: Path) -> str:
    """state/gate_history/ 아래 다음 순번(2자리 zero-pad). 기존 NN 디렉터리 최대+1."""
    if not history_root.is_dir():
        return "00"
    nums = [int(p.name) for p in history_root.iterdir() if p.is_dir() and p.name.isdigit()]
    return f"{(max(nums) + 1) if nums else 0:02d}"


def _latest_history_correctness(history_root: Path) -> Path | None:
    """가장 최근 gate_history/<NN>/evidence/scoring.correctness.json — sprint prior 소스.
    NN 사전순 최대(결정성). 없으면 None(첫 실행)."""
    if not history_root.is_dir():
        return None
    dirs = sorted(
        (p for p in history_root.iterdir() if p.is_dir() and p.name.isdigit()),
        key=lambda p: p.name,
    )
    for p in reversed(dirs):
        candidate = p / "evidence" / "scoring.correctness.json"
        if candidate.is_file():
            return candidate
    return None


def _archive_gate_history(
    run_root: Path, evidence_dir: Path, gate_path: Path
) -> str:
    """이번 실행의 evidence/ + gate_meta_audit.json 을 state/gate_history/<NN>/ 로 복사.
    다음 sprint.regression 실행의 prior 소스가 된다. gate_meta_audit.json 산출 뒤에
    실행되므로 verdict 아티팩트(quality/) 바이트에는 영향 없다."""
    history_root = run_root / "state" / "gate_history"
    idx = _next_history_index(history_root)
    dest = history_root / idx
    dest_evidence = dest / "evidence"
    dest_evidence.mkdir(parents=True, exist_ok=True)
    for ev in sorted(evidence_dir.glob("*.json")):
        shutil.copyfile(ev, dest_evidence / ev.name)
    if gate_path.exists():
        shutil.copyfile(gate_path, dest / "gate_meta_audit.json")
    return str(dest)


# --- run 관례 경로 유도(§2.3) --------------------------------------------------


def _latest_tournament_md(plan_dir: Path) -> Path | None:
    """plan/tournament-*.md 중 사전순(NN) 최대 — mtime 아닌 이름 기준(결정성, §2.3)."""
    if not plan_dir.is_dir():
        return None
    files = sorted(plan_dir.glob("tournament-*.md"), key=lambda p: p.name)
    return files[-1] if files else None


def _resolve_cold_pair(project_root: Path) -> tuple[Path | None, Path | None]:
    """cold 재이해/원본 쌍 관례(§2.3): plan/candidates/<winner>/07-cold-read.md vs
    plan/06-plan.md 존재 시 그 쌍, 아니면 intent/03-comprehension.md vs intent/01-intent.md.
    winner 후보가 여럿이면 사전순 첫 candidate(결정성). 어느 것도 없으면 (None, None)."""
    plan_ref = project_root / "plan" / "06-plan.md"
    candidates_dir = project_root / "plan" / "candidates"
    if plan_ref.is_file() and candidates_dir.is_dir():
        cold_reads = sorted(candidates_dir.glob("*/07-cold-read.md"), key=lambda p: p.as_posix())
        if cold_reads:
            return cold_reads[0], plan_ref
    intent_ru = project_root / "intent" / "03-comprehension.md"
    intent_ref = project_root / "intent" / "01-intent.md"
    if intent_ru.is_file() and intent_ref.is_file():
        return intent_ru, intent_ref
    return None, None


def _opt_path(value: str | Path | None) -> Path | None:
    return Path(value).resolve() if value else None


# --- 독립 producer 그룹 병렬 실행(G1) ------------------------------------------


def _run_producer_group(
    jobs: dict[str, Callable[[], dict[str, Any]]],
    parallel: bool,
    max_workers: int,
) -> dict[str, dict[str, Any]]:
    """상호 무의존 producer 그룹을 병렬(스레드) 또는 직렬로 실행 → {name: step_result}.

    이 그룹의 job 들은 서로 다른 evidence 파일만 쓰고 서로의 산출을 읽지 않는다
    (quality/gates/plan/cold/review/multiverse) — subprocess.run 이 GIL 을 풀어 스레드로 진짜 병렬이
    되며, 파일명이 겹치지 않아 동시 쓰기 경쟁이 없다. verdict/gate_meta_audit.json 의
    *바이트* 는 producer 실행 순서가 아니라 evidence 내용에만 의존하므로 병렬화는
    결정성을 깨지 않는다(measured_at 주입 시 동일 evidence → 동일 verdict).

    parallel=False 또는 job ≤ 1 이면 삽입 순서대로 직렬 — 정확히 옛 동작(escape hatch)."""
    if not parallel or len(jobs) <= 1:
        return {name: job() for name, job in jobs.items()}
    out: dict[str, dict[str, Any]] = {}
    with cf.ThreadPoolExecutor(max_workers=min(max_workers, len(jobs))) as ex:
        futures = {name: ex.submit(job) for name, job in jobs.items()}
        for name, fut in futures.items():
            out[name] = fut.result()
    return out


# --- 오케스트레이션(라이브러리 API) --------------------------------------------


def run_gate(
    *,
    project_root: str | Path,
    grade: str,
    submission: str | Path,
    test_target: str | Path,
    code_root: str | Path | None = None,
    git_base: str = "HEAD",
    junit: str | Path | None = None,
    coverage: str | Path | None = None,
    e2e_junit: str | Path | None = None,
    intent_criteria: str | Path | None = None,
    plan_todos: str | Path | None = None,
    solid_contract: str | Path | None = None,
    tournament_md: str | Path | None = None,
    shadow_grades_dir: str | Path | None = None,
    cold_reunderstanding: str | Path | None = None,
    cold_reference: str | Path | None = None,
    review_dispatch_log: str | Path | None = None,
    phase_upto: str | None = None,
    enable_plan: bool = True,
    enable_sprint: bool = True,
    enable_archive: bool = True,
    enable_review: bool = True,
    enable_multiverse: bool = True,
    enable_parallel: bool = True,
    measured_at: str | None = None,
    verified_at: str | None = None,
) -> dict[str, Any]:
    """게이트 러너 라이브러리 진입점. producer 오케스트레이션 → meta_audit → verdict.

    반환 dict 는 verdict(커널 소유) + report(전체 meta_audit) + steps + emitted_evidence 를
    담는다. classify/요약/보고는 호출자(러너 CLI 또는 dogfood wrapper)의 몫이다 —
    이 함수는 값을 만들지 않는다.

    관례 경로(§2.3)는 명시 인자가 None 일 때만 project_root 아래에서 유도한다(테스트/
    호출자 override seam). dogfood 는 자기 기본값을 전부 명시로 넘겨 관례 유도를 우회한다.
    """
    measured_at = measured_at or _now_iso()
    verified_at = verified_at or measured_at

    run_root = Path(project_root).resolve()
    evidence_dir = run_root / "evidence"
    junit_path = run_root / "results" / "junit.xml"
    for d in (run_root, evidence_dir, run_root / "results", run_root / "quality"):
        d.mkdir(parents=True, exist_ok=True)

    # 이전 실행 잔재 청소 — 이번 실행 producer/meta_audit 이 낳은 것만 남게 해 stale
    # gate/evidence 를 '재현'으로 착각하는 경로를 구조적으로 봉쇄한다(dogfood 규율 계승).
    # results/(junit) 는 --junit 재사용 seam 을 위해 보존한다. state/(gate_history) 도
    # 보존한다 — 누적 이력이 sprint.regression 의 prior 소스이기 때문.
    for stale in list(evidence_dir.glob("*.json")):
        stale.unlink()
    stale_gate = run_root / "quality" / "gate_meta_audit.json"
    if stale_gate.exists():
        stale_gate.unlink()

    cwd = _REPO_ROOT
    submission_p = Path(submission).resolve()
    code_root_p = Path(code_root).resolve() if code_root else submission_p
    test_target_p = Path(test_target).resolve()
    reuse_junit = _opt_path(junit)

    # 관례 경로 유도(명시 override 우선).
    intent_criteria_p = _opt_path(intent_criteria) or (run_root / "intent" / "01-intent-criteria.json")
    plan_todos_p = _opt_path(plan_todos) or (run_root / "plan" / "06-plan-todos.json")
    solid_contract_p = _opt_path(solid_contract) or (run_root / "impl" / "08-solid-contract.json")
    plan_dir = run_root / "plan"
    tournament_md_p = _opt_path(tournament_md) or _latest_tournament_md(plan_dir)
    shadow_grades_dir_p = _opt_path(shadow_grades_dir) or plan_dir
    if cold_reunderstanding or cold_reference:
        cold_ru_p = _opt_path(cold_reunderstanding)
        cold_ref_p = _opt_path(cold_reference)
    else:
        cold_ru_p, cold_ref_p = _resolve_cold_pair(run_root)
    # 관례 경로(§2.3): 명시 override 없으면 state/review_dispatch_log.json.
    review_log_p = _opt_path(review_dispatch_log) or (run_root / "state" / "review_dispatch_log.json")

    steps: dict[str, Any] = {}
    # junit 은 gates/submission 이 --test-junit 으로 소비하므로 병렬 그룹 *앞* 에 직렬.
    steps["junit"] = _produce_junit(test_target_p, junit_path, reuse_junit, cwd)

    # 독립 producer 그룹(G1 병렬) — quality/gates/plan/cold/review/multiverse 는 상호 무의존.
    # 순서 의존(2→3→5)은 submission 을 이 barrier *뒤* 에 둠으로써 보존한다
    # (quality+gates evidence 가 먼저 디스크에 존재해야 --from-evidence 가 승계).
    indep_jobs: dict[str, Callable[[], dict[str, Any]]] = {
        "quality": lambda: _quality_producers(code_root_p, evidence_dir, measured_at, cwd),
        "gates": lambda: _gate_producers(
            submission=submission_p,
            code_root=code_root_p,
            junit_path=junit_path,
            evidence_dir=evidence_dir,
            git_base=git_base,
            intent_criteria=intent_criteria_p,
            plan_todos=plan_todos_p,
            solid_contract=solid_contract_p,
            measured_at=measured_at,
            cwd=cwd,
        ),
        "cold": lambda: _cold_producer(cold_ru_p, cold_ref_p, evidence_dir, measured_at, cwd),
    }
    if enable_plan:
        indep_jobs["plan"] = lambda: _plan_producers(
            plan_dir, tournament_md_p, shadow_grades_dir_p, evidence_dir, measured_at, cwd
        )
    if enable_review:
        indep_jobs["review"] = lambda: _review_producer(review_log_p, evidence_dir, measured_at, cwd)
    if enable_multiverse:
        indep_jobs["multiverse"] = lambda: _multiverse_producer(grade, evidence_dir, measured_at, cwd)
    steps.update(_run_producer_group(indep_jobs, enable_parallel, max_workers=8))

    # submission — quality+gates barrier 뒤(2→3→5 순서 보존). sprint 은 submission 뒤.
    steps["submission"] = _submission_producer(
        submission_p, junit_path, evidence_dir, git_base,
        _opt_path(coverage), _opt_path(e2e_junit), measured_at, cwd,
    )
    if enable_sprint:
        history_root = run_root / "state" / "gate_history"
        prior = _latest_history_correctness(history_root)
        current = evidence_dir / "scoring.correctness.json"
        steps["sprint"] = _sprint_producer(prior, current, evidence_dir, measured_at, cwd)

    audit = _meta_audit(run_root, grade, verified_at, phase_upto, cwd)
    steps["meta_audit"] = {"returncode": audit["returncode"], "gate_path": audit["gate_path"]}

    report = audit["report"] or {}

    gate_history_dir: str | None = None
    if enable_archive:
        gate_history_dir = _archive_gate_history(
            run_root, evidence_dir, Path(audit["gate_path"])
        )

    return {
        "run_root": str(run_root),
        "grade": grade,
        "measured_at": measured_at,
        "verified_at": verified_at,
        "code_root": str(code_root_p),
        "submission": str(submission_p),
        "phase_upto": phase_upto,
        "verdict": report.get("verdict"),
        "report": report,
        "steps": steps,
        "emitted_evidence": sorted(p.name for p in evidence_dir.glob("*.json")),
        "gate_path": audit["gate_path"],
        "gate_history_dir": gate_history_dir,
    }


def _verdict_exit(verdict: str | None) -> int:
    """verdict → exit 매핑(§2.1): pass=0 / fail=1 / 미산출(크래시)=2."""
    if verdict == "pass":
        return 0
    if verdict == "fail":
        return 1
    return 2


def _print_human(result: dict[str, Any]) -> None:
    report = result.get("report") or {}
    print(f"run_gate verdict: {result['verdict']}  (grade {result['grade']})")
    active = report.get("active_checks", [])
    failed = set(report.get("failed", []))
    na = set(report.get("na", []))
    advisory = set(report.get("advisory", []))
    deferred = set(report.get("deferred", []))
    for check_id in active:
        if check_id in deferred:
            tag = "deferred"
        elif check_id in failed:
            tag = "FAIL"
        elif check_id in na:
            tag = "NA"
        elif check_id in advisory:
            tag = "ADVISORY"
        else:
            tag = "PASS"
        outcome = report.get("results", {}).get(check_id, {})
        val = outcome.get("value")
        val_s = "" if val is None else f" value={val}"
        print(f"  [{tag:>8}] {check_id}{val_s}")
    print(f"  run_root: {result['run_root']}")
    if result.get("gate_history_dir"):
        print(f"  gate_history: {result['gate_history_dir']}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="run_gate — phase-09 게이트 러너(producer→meta_audit→verdict, 설계 B1 §2)"
    )
    p.add_argument("--project-root", required=True, help="run 산출물 루트(evidence/results/quality/state)")
    p.add_argument("--grade", required=True, help="감사 그레이드(G2|G3|G4|G5)")
    p.add_argument("--submission", required=True, help="git diff 대상 제출물(코드 루트)")
    p.add_argument("--test-target", required=True, help="pytest 대상 디렉터리")
    p.add_argument("--code-root", default=None, help="quality.* 스캔 코드 루트(기본: --submission)")
    p.add_argument("--git-base", default="HEAD", help="git diff base ref(기본 HEAD)")
    p.add_argument("--junit", default=None, help="기존 junit XML 재사용(pytest 미실행 seam)")
    p.add_argument("--coverage", default=None, help="BE coverage.xml 패스스루")
    p.add_argument("--e2e-junit", default=None, help="e2e junit XML 패스스루")
    p.add_argument("--intent-criteria", default=None, help="override: intent-criteria 경로(기본 관례: intent/01-intent-criteria.json)")
    p.add_argument("--plan-todos", default=None, help="override: plan-todos 경로(기본 관례: plan/06-plan-todos.json)")
    p.add_argument("--solid-contract", default=None, help="override: solid-contract 경로(기본 관례: impl/08-solid-contract.json)")
    p.add_argument("--tournament-md", default=None, help="override: tournament md(기본 관례: plan/tournament-*.md 최신)")
    p.add_argument("--shadow-grades-dir", default=None, help="override: shadow-grade dir(기본 관례: plan/)")
    p.add_argument("--cold-reunderstanding", default=None, help="override: cold 재이해 텍스트")
    p.add_argument("--cold-reference", default=None, help="override: cold 참조 텍스트")
    p.add_argument("--review-dispatch-log", default=None, help="override: 리뷰 디스패치 로그(기본 관례: state/review_dispatch_log.json)")
    p.add_argument("--phase-upto", default=None, help="이 페이즈 이하만 게이팅(나중 페이즈=deferred). phase-09 게이트=09")
    p.add_argument("--no-plan", action="store_true", help="plan producer 단계 비활성")
    p.add_argument("--no-sprint", action="store_true", help="sprint producer 단계 비활성")
    p.add_argument("--no-archive", action="store_true", help="gate_history 아카이브 비활성")
    p.add_argument("--no-review", action="store_true", help="review.context_minimality producer 단계 비활성")
    p.add_argument("--no-multiverse", action="store_true", help="multiverse.fan_out_width producer 단계 비활성")
    p.add_argument("--no-parallel", action="store_true", help="독립 producer 그룹 병렬 실행 비활성(직렬 escape hatch)")
    p.add_argument("--measured-at", default=None, help="모든 producer 에 주입할 measured_at(결정성)")
    p.add_argument("--verified-at", default=None, help="meta_audit 에 주입할 verified_at(기본: measured_at)")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)
    result = run_gate(
        project_root=args.project_root,
        grade=args.grade,
        submission=args.submission,
        test_target=args.test_target,
        code_root=args.code_root,
        git_base=args.git_base,
        junit=args.junit,
        coverage=args.coverage,
        e2e_junit=args.e2e_junit,
        intent_criteria=args.intent_criteria,
        plan_todos=args.plan_todos,
        solid_contract=args.solid_contract,
        tournament_md=args.tournament_md,
        shadow_grades_dir=args.shadow_grades_dir,
        cold_reunderstanding=args.cold_reunderstanding,
        cold_reference=args.cold_reference,
        review_dispatch_log=args.review_dispatch_log,
        phase_upto=args.phase_upto,
        enable_plan=not args.no_plan,
        enable_sprint=not args.no_sprint,
        enable_archive=not args.no_archive,
        enable_review=not args.no_review,
        enable_multiverse=not args.no_multiverse,
        enable_parallel=not args.no_parallel,
        measured_at=args.measured_at,
        verified_at=args.verified_at,
    )
    _print_human(result)
    # exit = verdict(§2.1): pass=0 / fail=1 / 미산출(크래시)=2. verdict 는 커널 소유 —
    # 러너는 매핑만 한다(상상 판정 0).
    return _verdict_exit(result["verdict"])


if __name__ == "__main__":
    sys.exit(main())
