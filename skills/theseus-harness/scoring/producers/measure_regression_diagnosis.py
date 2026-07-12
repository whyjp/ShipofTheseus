#!/usr/bin/env python3
"""measure_regression_diagnosis.py — regression.parallel_diagnosis 증거 조립기 (진단 병렬화 소유).

회귀(sprint.regression)가 검출된 뒤 *진단*이 모델재량이 아니라 코드가 소유하는 조건이 되게
한다. 오늘까지 페이즈 11 bisect 는 단일 분석가의 서술(주 가설 + 반대 가설)이었다 — 아무도
"진단이 실제로 *여러 독립 회의론자*의 corroborated 병렬 판단인가"를 디스크에서 재확인하지
않았다. 본 producer 는 최신 회귀 이벤트의 진단 산출물을 파싱해 emit 한다:
  - regression_events_total        : gate_history 중 score_delta < -0.05 인 이벤트 수
  - undiagnosed_events             : 회귀 이벤트 중 bound 진단(bisect.md)이 없는 수
  - hypotheses_count               : 최신 회귀의 bound 진단 sprint 의 hypothesis-*.json 수
  - malformed_hypotheses           : 필수 필드 결손 가설 수(무결성)
  - duplicate_call_ids             : agent_call_id 중복 수(dispatch 위조 방어)
  - invalid_class_votes            : defect_class 가 BISECT_DEFECT_CLASSES 밖인 수
  - corroboration_count            : 같은 defect_class 에 투표한 가설 최대 수(합의 신호)
  - class_argmax_match             : bisect 선언 regression_class == 표결 argmax(1/0)
  - routing_matches_class          : bisect fix_target_phase == FAILURE_TO_PHASE[class](1/0)
  - hypotheses_without_alternative : 비어있지 않은 alternative_class 없는 가설 수
  - hypo_floor                     : manifest regression_diagnosis.min_hypotheses[grade]
  - corroboration_min              : manifest regression_diagnosis.corroboration_min

이 스크립트는 *측정기(producer)* 이지 판정기가 아니다 — 판정은 커널이 CheckSpec
regression.parallel_diagnosis.json 의 assertion 으로 내린다. 모든 수치는 로그 자기 신고가
아니라 producer 가 디스크의 gate_history evidence·bisect.md frontmatter·hypothesis-*.json 을
다시 파싱해 낸 값이다(상상값 주입 0). 회귀 라우팅(defect_class→phase)과 유효 4-class 집합은
checkpoint.py 의 FAILURE_TO_PHASE / BISECT_DEFECT_CLASSES 단일 소스를 재사용한다(이원화 0).

정직 고지: 본 게이트는 "진단이 corroborated 병렬 가설로 뒷받침됨 + 라우팅이 코드 소유"를
증명하지 *정확한* 진단을 증명하지 않는다 — 병렬 가설의 존재가 진단의 진리를 보장하지 않고,
agent_call_id 는 dispatch 자기 신고(zero-context skeptic 여부의 궁극 증명 불가)다. 그 위조
압력은 본 체크 단독이 아니라 생태계(review.context_minimality 의 dispatch 순도·freshness,
review_dispatch_log 무결성)가 좁힌다(순도의 궁극 증명 불가와 같은 전제).

플래그: manifest regression_diagnosis 블록/grade 결손이면 evidence 를 emit 하지 않는다(floor
를 상상하지 않는다) — G4/G5 는 absence_policy FAIL(비휴면). 회귀 이벤트가 0 이면(정상 진행)
zeros + floor 로 *emit* 한다 — 이건 디렉터리 부재(상상 금지)가 아니라 진짜 측정된 0 이며,
CheckSpec applicability(regression_events_total >= 1)가 NA(비게이팅)로 처리한다.

CLI:
    python measure_regression_diagnosis.py --grade G4 \\
        [--manifest <pipeline.manifest.json>] [--phase 11] [--project-run <name>] \\
        [--measured-at <ISO8601>] --out-dir <project_root>/evidence
    (커널 게이팅 경로는 --manifest override 를 금지한다 — CheckSpec cmd_pattern 이 canonical
     form 만 수용해 floor 몰래 낮추기 채널을 봉쇄. --manifest 는 producer 단위 테스트 전용.)

저장소 self_lint C35 — 모든 open encoding="utf-8".
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

_SCORING_DIR = Path(__file__).resolve().parents[1]
if str(_SCORING_DIR) not in sys.path:
    sys.path.insert(0, str(_SCORING_DIR))

import _evidence_common as ec  # noqa: E402
import evidence as evidence_mod  # noqa: E402  (Evidence Record 로더; kernel dir 는 ec 가 path 에 올림)
from _stdio import force_utf8_stdio  # noqa: E402
import checkpoint  # noqa: E402  (FAILURE_TO_PHASE, BISECT_DEFECT_CLASSES 단일 소스)

CHECK_ID = "regression.parallel_diagnosis"
DEFAULT_PHASE = "11"

# 활성 소스 단일화(manifest). 이 파일 기준 producers -> scoring -> theseus-harness.
_DEFAULT_MANIFEST = Path(__file__).resolve().parents[2] / "pipeline.manifest.json"

# 회귀 판정 임계(하락 delta) — checks/sprint.regression.json 의 assertion `score_delta >= -0.05`
# 과 같은 상수. drift 는 test 의 가드가 FAIL 로 잡는다(sprint.regression 이 유일 권위, 본 상수는 거울).
REGRESSION_SCORE_DELTA_THRESHOLD = -0.05

# 두 score 매칭 허용 오차(bisect frontmatter 숫자 ↔ evidence measured 숫자).
_SCORE_TOL = 1e-6

# 가설이 malformed 가 아니려면 채워야 하는 핵심 식별 필드(alternative_* 는 별도 지표로 추적).
_REQUIRED_HYP_FIELDS = ("agent_call_id", "defect_class", "suspect_file_or_commit", "failing_test")

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_HYP_RE = re.compile(r"^hypothesis-.*\.json$")


def _parse_frontmatter(text: str) -> dict[str, str]:
    """최상위 key: value 만 파싱(중첩 블록은 건너뜀) — measure_tournament_argmax 와 동일 방식.

    regression_class / fix_target_phase / gate_history_ref / prior_score / current_score 는
    전부 최상위 스칼라라 nested 블록(lint_rule_proposal 등) 평탄화 오염을 피한다."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).split("\n"):
        if line[:1] in (" ", "\t"):
            continue  # 들여쓴 중첩(예: lint_rule_proposal 하위) 무시
        s = line.strip()
        if not s or s.startswith("#") or ":" not in s:
            continue
        key, _, val = s.partition(":")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def _parse_num(s: str) -> float | None:
    """`0.913` / `**0.913**` → float. 미파싱 None."""
    s = (s or "").strip().strip("*").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _load_floors(manifest_path: Path, grade: str) -> tuple[int, int] | None:
    """manifest regression_diagnosis → (hypo_floor, corroboration_min). 결손이면 None(상상 금지).

    min_hypotheses[grade] 는 grade 의존(G4=3/G5=4), corroboration_min 은 grade 무관."""
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    block = data.get("regression_diagnosis")
    if not isinstance(block, dict):
        return None
    mh = block.get("min_hypotheses")
    if not isinstance(mh, dict):
        return None
    hv = mh.get(grade)
    # bool 은 int 서브타입이라 명시 배제.
    if isinstance(hv, bool) or not isinstance(hv, int):
        return None
    cm = block.get("corroboration_min")
    if isinstance(cm, bool) or not isinstance(cm, int):
        return None
    return hv, cm


def _measured_value(ev: evidence_mod.EvidenceRecord, key: str) -> Any:
    """Evidence Record measured 스칼라 접근 — ev.measured[key]["value"] 또는 None."""
    entry = ev.measured.get(key)
    if isinstance(entry, dict):
        return entry.get("value")
    return None


def _scan_regression_events(run_root: Path) -> list[dict[str, Any]]:
    """gate_history/<NN>/evidence/sprint.regression.json → score_delta < -0.05 인 이벤트 목록.

    각 sprint.regression.json 은 Evidence Record 다 — measure_regression 이 emit 한 measured
    (score_delta/prior_score/current_score) 를 읽는다. dir 이름(<NN>)이 diagnosis 의
    gate_history_ref 와 매칭될 앵커다. NN 사전순 정렬(결정성)."""
    events: list[dict[str, Any]] = []
    gh_root = run_root / "state" / "gate_history"
    if not gh_root.is_dir():
        return events
    for sub in sorted((p for p in gh_root.iterdir() if p.is_dir()), key=lambda p: p.name):
        ev_path = sub / "evidence" / "sprint.regression.json"
        if not ev_path.is_file():
            continue
        ev = evidence_mod.try_load_evidence(ev_path)
        if ev is None:
            continue
        delta = _measured_value(ev, "score_delta")
        if not isinstance(delta, (int, float)) or isinstance(delta, bool):
            continue
        if delta < REGRESSION_SCORE_DELTA_THRESHOLD:
            events.append({
                "gate_history_ref": sub.name,
                "score_delta": float(delta),
                "prior_score": _measured_value(ev, "prior_score"),
                "current_score": _measured_value(ev, "current_score"),
            })
    return events


def _scan_diagnoses(run_root: Path) -> list[dict[str, Any]]:
    """sprints/<NN>/bisect.md frontmatter → 진단 목록(binding 키 + 라우팅 키)."""
    diags: list[dict[str, Any]] = []
    sprints_root = run_root / "sprints"
    if not sprints_root.is_dir():
        return diags
    for sub in sorted((p for p in sprints_root.iterdir() if p.is_dir()), key=lambda p: p.name):
        bisect = sub / "bisect.md"
        if not bisect.is_file():
            continue
        fm = _parse_frontmatter(bisect.read_text(encoding="utf-8", errors="ignore"))
        diags.append({
            "sprint_dir": sub,
            "gate_history_ref": fm.get("gate_history_ref", "").strip(),
            "prior_score": _parse_num(fm.get("prior_score", "")),
            "current_score": _parse_num(fm.get("current_score", "")),
            "regression_class": fm.get("regression_class", "").strip(),
            "fix_target_phase": fm.get("fix_target_phase", "").strip(),
        })
    return diags


def _scores_match(a: Any, b: Any) -> bool:
    if not isinstance(a, (int, float)) or isinstance(a, bool):
        return False
    if not isinstance(b, (int, float)) or isinstance(b, bool):
        return False
    return abs(float(a) - float(b)) <= _SCORE_TOL


def _is_bound(event: dict[str, Any], diag: dict[str, Any]) -> bool:
    """진단이 이벤트에 BOUND 인가: gate_history_ref 일치 + prior/current score 일치(tolerance)."""
    if not diag["gate_history_ref"] or diag["gate_history_ref"] != event["gate_history_ref"]:
        return False
    return _scores_match(diag["prior_score"], event["prior_score"]) and \
        _scores_match(diag["current_score"], event["current_score"])


def _load_hypotheses(sprint_dir: Path) -> list[Any]:
    """sprint_dir/hypotheses/hypothesis-*.json 로드. 파싱 불가/비-객체는 None(malformed)."""
    hyps: list[Any] = []
    hdir = sprint_dir / "hypotheses"
    if not hdir.is_dir():
        return hyps
    for hp in sorted(hdir.iterdir(), key=lambda p: p.name):
        if not hp.is_file() or not _HYP_RE.match(hp.name):
            continue
        try:
            data = json.loads(hp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = None
        hyps.append(data if isinstance(data, dict) else None)
    return hyps


def _hypothesis_metrics(hyps: list[Any], diag: dict[str, Any] | None) -> dict[str, Any]:
    """가설 목록 + bound 진단(bisect) → 병렬성/합의/라우팅 지표."""
    malformed = 0
    without_alt = 0
    invalid = 0
    call_ids: list[str] = []
    votes: list[str] = []
    for h in hyps:
        if not isinstance(h, dict):
            malformed += 1
            without_alt += 1  # 파싱 불가 = alternative 도 없음
            continue
        if any(not str(h.get(f, "")).strip() for f in _REQUIRED_HYP_FIELDS):
            malformed += 1
        cid = str(h.get("agent_call_id", "")).strip()
        if cid:
            call_ids.append(cid)
        dc = str(h.get("defect_class", "")).strip()
        if dc:
            votes.append(dc)
            if dc not in checkpoint.BISECT_DEFECT_CLASSES:
                invalid += 1
        if not str(h.get("alternative_class", "")).strip():
            without_alt += 1

    duplicate_call_ids = len(call_ids) - len(set(call_ids))
    if votes:
        counter = Counter(votes)
        corroboration_count = max(counter.values())
        # argmax defect_class — 동률은 클래스 이름 사전순 tie-break(결정성).
        argmax_class = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    else:
        corroboration_count = 0
        argmax_class = ""

    regression_class = (diag or {}).get("regression_class", "")
    fix_target_phase = (diag or {}).get("fix_target_phase", "")
    class_argmax_match = 1 if regression_class and regression_class == argmax_class else 0
    expected_phase = checkpoint.FAILURE_TO_PHASE.get(regression_class)
    routing_matches_class = 1 if (expected_phase is not None and fix_target_phase == expected_phase) else 0

    return {
        "hypotheses_count": len(hyps),
        "malformed_hypotheses": malformed,
        "duplicate_call_ids": duplicate_call_ids,
        "invalid_class_votes": invalid,
        "corroboration_count": corroboration_count,
        "class_argmax_match": class_argmax_match,
        "routing_matches_class": routing_matches_class,
        "hypotheses_without_alternative": without_alt,
        "argmax_class": argmax_class,
        "regression_class": regression_class,
        "fix_target_phase": fix_target_phase,
    }


def _build_report(run_root: Path, grade: str, hypo_floor: int, corroboration_min: int) -> dict[str, Any]:
    """gate_history + sprints 디스크 스캔 → 원시 관측 리포트(verdict 없음).

    이 리포트 자체가 measured 값들의 backing artifact 다."""
    events = _scan_regression_events(run_root)
    diags = _scan_diagnoses(run_root)

    # 각 회귀 이벤트에 bound 진단이 있는가.
    undiagnosed = 0
    for ev in events:
        if not any(_is_bound(ev, d) for d in diags):
            undiagnosed += 1

    # 최신 회귀 이벤트(gate_history 인덱스 최대)의 bound 진단으로 가설 스캔.
    latest = None
    if events:
        latest = sorted(events, key=lambda e: e["gate_history_ref"])[-1]
    bound_diag = None
    if latest is not None:
        for d in diags:
            if _is_bound(latest, d):
                bound_diag = d
                break

    hyps = _load_hypotheses(bound_diag["sprint_dir"]) if bound_diag is not None else []
    metrics = _hypothesis_metrics(hyps, bound_diag)

    report: dict[str, Any] = {
        "grade": grade,
        "regression_events_total": len(events),
        "undiagnosed_events": undiagnosed,
        "hypotheses_count": metrics["hypotheses_count"],
        "malformed_hypotheses": metrics["malformed_hypotheses"],
        "duplicate_call_ids": metrics["duplicate_call_ids"],
        "invalid_class_votes": metrics["invalid_class_votes"],
        "corroboration_count": metrics["corroboration_count"],
        "class_argmax_match": metrics["class_argmax_match"],
        "routing_matches_class": metrics["routing_matches_class"],
        "hypotheses_without_alternative": metrics["hypotheses_without_alternative"],
        "hypo_floor": hypo_floor,
        "corroboration_min": corroboration_min,
        # 비-measured 감사 detail(backing artifact 에만; measured 는 스칼라만).
        "latest_gate_history_ref": (latest or {}).get("gate_history_ref"),
        "bound_sprint": bound_diag["sprint_dir"].name if bound_diag is not None else None,
        "declared_regression_class": metrics["regression_class"],
        "declared_fix_target_phase": metrics["fix_target_phase"],
        "vote_argmax_class": metrics["argmax_class"],
    }
    return report


_MEASURED_KEYS = (
    "regression_events_total",
    "undiagnosed_events",
    "hypotheses_count",
    "malformed_hypotheses",
    "duplicate_call_ids",
    "invalid_class_votes",
    "corroboration_count",
    "class_argmax_match",
    "routing_matches_class",
    "hypotheses_without_alternative",
    "hypo_floor",
    "corroboration_min",
)


def _reconstruct_cmd(args: argparse.Namespace) -> str:
    """producer_cmd 재구성. canonical form(--manifest override 없음)은 CheckSpec cmd_pattern
    `^python (?!.*--manifest).*measure_regression_diagnosis\\.py` 에 매칭된다. --manifest 를
    쓰면 cmd 에 그 토큰이 실려 pattern 이 거부 → 커널 법칙3 FAIL(floor 몰래 낮추기 봉쇄)."""
    parts = ["python", str(Path(__file__).resolve()), "--grade", args.grade]
    if args.manifest:
        parts += ["--manifest", args.manifest]
    parts += ["--out-dir", args.out_dir]
    return " ".join(parts)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out_dir = Path(args.out_dir).resolve()
    run_root = out_dir.parent
    project_run = args.project_run or run_root.name
    measured_at = args.measured_at or ec.now_iso()
    producer_cmd = _reconstruct_cmd(args)

    manifest_path = Path(args.manifest).resolve() if args.manifest else _DEFAULT_MANIFEST
    floors = _load_floors(manifest_path, args.grade)
    if floors is None:
        # floor 를 못 구함(블록/grade 결손) → evidence 미기록(상상 0). G4/G5 는 이 경로에
        # 오지 않아야 하며, 오면 absence_policy FAIL 로 정직하게 잡힌다.
        return {
            "emitted": False,
            "reason": f"manifest regression_diagnosis[{args.grade}] 미존재 — measure_regression_diagnosis 미실행",
        }
    hypo_floor, corroboration_min = floors

    # 회귀 이벤트가 0 이어도 emit 한다 — 디렉터리 부재(상상 금지)가 아니라 측정된 0.
    # CheckSpec applicability(regression_events_total >= 1)가 NA 로 처리(비게이팅).
    report = _build_report(run_root, args.grade, hypo_floor, corroboration_min)

    report_path = out_dir / f"{CHECK_ID}.report.json"
    ec.write_json_artifact(report_path, report)
    report_rel = ec.relpath(report_path, run_root)
    report_digest = ec.sha256_of_file(report_path)

    src = "regression_diagnosis_scan"
    measured = {k: ec.build_measured(report[k], src, report_rel) for k in _MEASURED_KEYS}
    artifact_digests = {report_rel: report_digest}
    record = ec.assemble_record(
        check_id=CHECK_ID,
        phase=args.phase,
        project_run=project_run,
        producer_cmd=producer_cmd,
        measured=measured,
        artifact_digests=artifact_digests,
        measured_at=measured_at,
    )
    path = ec.write_evidence(out_dir, CHECK_ID, record)
    summary = {"emitted": True, "evidence_path": str(path), "grade": args.grade}
    summary.update({k: report[k] for k in _MEASURED_KEYS})
    return summary


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="measure_regression_diagnosis — regression.parallel_diagnosis 증거 조립기 (verdict 없음)"
    )
    p.add_argument(
        "--grade", required=True,
        help="floor 조회용 grade(G4|G5). manifest regression_diagnosis.min_hypotheses[grade] 를 hypo_floor 로 읽는다.",
    )
    p.add_argument(
        "--manifest", default=None,
        help="floor 소스 override(기본: skills/theseus-harness/pipeline.manifest.json). "
             "커널 게이팅 경로에선 금지 — producer 단위 테스트 전용(CheckSpec cmd_pattern 이 거부).",
    )
    p.add_argument("--phase", default=DEFAULT_PHASE, help="정보용 — 커널 게이팅에는 쓰이지 않는다.")
    p.add_argument("--project-run", default=None, help="project_run 이름(기본: run_root.name)")
    p.add_argument("--measured-at", default=None, help="measured_at 주입(결정성 테스트용)")
    p.add_argument("--out-dir", required=True, help="evidence 출력 디렉터리 (<project_root>/evidence)")
    return p


def main(argv: list[str] | None = None) -> int:
    force_utf8_stdio()  # cp949 등 로캘 콘솔에서 비-ASCII print 크래시 방지(공유 헬퍼)
    args = build_parser().parse_args(argv)
    summary = run(args)
    json.dump(summary, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
