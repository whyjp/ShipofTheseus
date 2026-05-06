"""check_cold_session.py — Cold session artifact validator (sprint-32 v0.9.37).

본 스크립트는 *외부 cold session* 의 산출물 (`.ShipofTheseus/<project>/`) 을 직접 검사한다.
self_lint.py 가 본 저장소 markdown 정합성을 검사한다면, 본 스크립트는 *bench 외부 cold session*
의 phase artifacts (tournament-NN.md / dacapo-rerun-NN.md / shadow-grade-NN.json /
universe candidates) 를 mandatory_first_rerun_satisfied + Da Capo NEW universe + conservative
margin cap 정합 검증한다.

사용:
    python check_cold_session.py <cold_session_path>

여기서 ``<cold_session_path>`` = ``.ShipofTheseus/<project>/`` (timing/start.json 부모).

Exit codes:
    0 — all checks pass
    1 — violations found (stderr 에 명세)

참조:
- sprint-28 (intra-phase-dacapo-loop 안티 패턴 g/h/i/j/k)
- sprint-29 (impl-multiverse-strict 안티 패턴 e/f/g)
- sprint-30 (conservative-margin-judging cap + sentinel)
- sprint-19 (dacapo-mandatory-rerun ce, mandatory ≥ 1 rerun)

orchestrator 가 phase 09 진입 직전 의무 호출 (HARD-RULE 9.f, sprint-32 v0.9.37 신규).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# rerun-별 score cap (sprint-30 conservative-margin-judging)
SCORE_CAP_BY_RERUN = {0: 0.90, 1: 0.95, 2: 0.99}


SENTINEL_PATTERNS = [
    re.compile(r'\bre-?rate(?:s)?\s+(?:the\s+)?same\s+universes?\b', re.I),
    re.compile(r'\bsame\s+universes?\s+re-?rated?\b', re.I),
    re.compile(r'\bno\s+further\s+(?:sprints?|dacapo|rounds?)\s+(?:required|needed)\b', re.I),
    re.compile(r'\bwinner\s+clear\b', re.I),
    re.compile(r'\bobvious\s+winner\b', re.I),
    re.compile(r'\bclearly\s+best\b', re.I),
    re.compile(r'\bpassed\s+on\s+first\s+execution\b', re.I),
    re.compile(r'\bfirst-?try\s+pass\b', re.I),
    re.compile(r'\bwalkover\b', re.I),
    re.compile(r'\blost\s+the\s+plan\s+tournament\s+before\s+code\s+was\s+written\b', re.I),
]


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    block = text[4:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def check_mandatory_first_rerun_plan(plan_dir: Path) -> list[str]:
    """sprint-19 ce — phase 06 mandatory ≥ 1 rerun + tournament-NN ≥ 2."""
    issues: list[str] = []
    tournaments = sorted(plan_dir.glob("tournament-*.md"))
    reruns = sorted(plan_dir.glob("dacapo-rerun-*.md"))
    if len(tournaments) < 2:
        issues.append(
            f"plan/tournament-NN.md = {len(tournaments)} (require ≥ 2 — mandatory_first_rerun_satisfied)"
        )
    if len(reruns) < 1:
        issues.append(f"plan/dacapo-rerun-NN.md = {len(reruns)} (require ≥ 1)")
    return issues


def check_mandatory_first_rerun_impl(impl_dir: Path) -> list[str]:
    """sprint-19 ce + sprint-29 — phase 08 mandatory ≥ 1 rerun + tournament-impl-NN ≥ 2."""
    issues: list[str] = []
    if not impl_dir.exists():
        return issues  # phase 08 미실행 = phase 09 entry 게이트가 별도 차단
    tournaments = sorted(impl_dir.glob("tournament-impl-*.md"))
    reruns = sorted(impl_dir.glob("dacapo-rerun-impl-*.md"))
    if len(tournaments) < 2:
        issues.append(
            f"impl/tournament-impl-NN.md = {len(tournaments)} (require ≥ 2)"
        )
    if len(reruns) < 1:
        issues.append(f"impl/dacapo-rerun-impl-NN.md = {len(reruns)} (require ≥ 1)")
    return issues


def check_sentinel_patterns(plan_dir: Path, impl_dir: Path) -> list[str]:
    """sprint-28 g/k + sprint-29 e + sprint-30 sentinel — confident first-pass language reject."""
    issues: list[str] = []
    for d in [plan_dir, impl_dir]:
        if not d.exists():
            continue
        for p in d.glob("*.md"):
            try:
                body = p.read_text(encoding="utf-8")
            except Exception:
                continue
            for pat in SENTINEL_PATTERNS:
                m = pat.search(body)
                if m:
                    issues.append(
                        f"{p.relative_to(d.parent)}: sentinel pattern '{m.group(0)}' "
                        f"detected — sprint-28/29/30 anti-pattern"
                    )
                    break
    return issues


def check_round2_universes_new(plan_dir: Path) -> list[str]:
    """sprint-28 g — Round N+1 = NEW universes (NOT survivors of Round N).

    dacapo-rerun-01.md 가 존재하면 그 mtime 이후 새 universe (universe-5..N) 가 작성됐어야 함.
    OR 본문에 'same universes' regex match 시 fail (이미 sentinel 에서 처리됨).
    """
    issues: list[str] = []
    rerun_files = sorted(plan_dir.glob("dacapo-rerun-*.md"))
    if not rerun_files:
        return issues  # mandatory rerun check 가 별도로 처리
    cand_dir = plan_dir / "candidates"
    if not cand_dir.exists():
        return issues
    universes = sorted(cand_dir.glob("universe-*"))
    if len(universes) <= 4:
        # rerun ≥ 1 인데 universe count ≤ 4 = NEW universes 미생성 의심
        issues.append(
            f"plan/candidates/universe-* count = {len(universes)} (rerun ≥ 1 시 ≥ 5 expected — "
            f"Round N+1 = anonymized prev winner + width-1 fresh universes)"
        )
    return issues


def check_impl_universe_isolation(plan_dir: Path, impl_dir: Path) -> list[str]:
    """sprint-29 f — impl universe ID ≠ plan universe ID (출력 격리)."""
    issues: list[str] = []
    if not impl_dir.exists():
        return issues
    plan_cand = plan_dir / "candidates"
    impl_cand = impl_dir / "candidates"
    if not (plan_cand.exists() and impl_cand.exists()):
        return issues
    plan_ids = {p.name for p in plan_cand.glob("universe-*")}
    impl_ids = {p.name for p in impl_cand.glob("universe-*")}
    overlap = plan_ids & impl_ids
    if overlap:
        # exact overlap suggests inheritance (plan u1 → impl u1)
        # NOTE: this is heuristic — namespace 갱신 권장 (impl-u1 / impl-1 등 NEW namespace)
        issues.append(
            f"impl/candidates/{sorted(overlap)} = plan/candidates/{sorted(overlap)} "
            f"(impl universe ID = plan universe ID 상속 — sprint-29 anti-pattern f)"
        )
    return issues


def check_score_cap(plan_dir: Path) -> list[str]:
    """sprint-30 — rerun-별 score cap (shadow-grade-NN.json predicted_score)."""
    issues: list[str] = []
    for sg in sorted(plan_dir.glob("shadow-grade-*.json")):
        try:
            data = json.loads(sg.read_text(encoding="utf-8"))
        except Exception:
            continue
        rerun_match = re.search(r'shadow-grade-(\d+)', sg.stem)
        if not rerun_match:
            continue
        rerun = int(rerun_match.group(1))
        cap = SCORE_CAP_BY_RERUN.get(rerun, 0.999)
        score = data.get("predicted_score") or data.get("score_total_weighted") or ""
        if isinstance(score, str):
            m = re.search(r'(\d+(?:\.\d+)?)\s*/?\s*(\d+(?:\.\d+)?)?', score)
            if m:
                num = float(m.group(1))
                den = float(m.group(2)) if m.group(2) else 100.0
                normalized = num / den if den else num / 100.0
            else:
                continue
        elif isinstance(score, (int, float)):
            normalized = score / 100.0 if score > 1 else float(score)
        else:
            continue
        if normalized > cap:
            issues.append(
                f"{sg.name}: predicted_score = {normalized:.3f} > rerun={rerun} cap = {cap} "
                f"(sprint-30 conservative-margin-judging)"
            )
    return issues


def check_improvement_axes_remaining(plan_dir: Path) -> list[str]:
    """sprint-30 — improvement_axes_remaining ≥ 1 (rerun < 3 시)."""
    issues: list[str] = []
    for t in sorted(plan_dir.glob("tournament-*.md")):
        rerun_match = re.search(r'tournament-(\d+)', t.stem)
        if not rerun_match:
            continue
        rerun = int(rerun_match.group(1))
        if rerun >= 3:
            continue
        try:
            body = t.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = _frontmatter(body)
        axes = fm.get("improvement_axes_remaining")
        if axes is None:
            issues.append(
                f"{t.name}: 'improvement_axes_remaining' frontmatter 부재 "
                f"(rerun={rerun} < 3 — sprint-30 의무)"
            )
        elif axes.isdigit() and int(axes) == 0:
            issues.append(
                f"{t.name}: 'improvement_axes_remaining: 0' but rerun={rerun} < 3 "
                f"(sprint-30 — judge 가 보수적 prior 위반)"
            )
    return issues


def main(cold_session_path: Path) -> int:
    if not cold_session_path.exists():
        print(f"ERROR: cold session path 부재: {cold_session_path}", file=sys.stderr)
        return 2
    plan_dir = cold_session_path / "plan"
    impl_dir = cold_session_path / "impl"
    all_issues: list[str] = []
    if plan_dir.exists():
        all_issues += check_mandatory_first_rerun_plan(plan_dir)
        all_issues += check_round2_universes_new(plan_dir)
        all_issues += check_score_cap(plan_dir)
        all_issues += check_improvement_axes_remaining(plan_dir)
    all_issues += check_mandatory_first_rerun_impl(impl_dir)
    all_issues += check_sentinel_patterns(plan_dir, impl_dir)
    all_issues += check_impl_universe_isolation(plan_dir, impl_dir)
    if all_issues:
        print(f"FAIL — {len(all_issues)} cold session violation(s):", file=sys.stderr)
        for i in all_issues:
            print(f"  - {i}", file=sys.stderr)
        return 1
    print(f"PASS — cold session {cold_session_path} all checks PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    sys.exit(main(Path(sys.argv[1])))
