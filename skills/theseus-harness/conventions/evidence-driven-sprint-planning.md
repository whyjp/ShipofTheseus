---
id: evidence-driven-sprint-planning
category: sprint
applies-to-phases: '[10]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Evidence-Driven Sprint Planning — evidence_missing → 다음 sprint lesson 자동 매핑

## 한 줄 요약

**[`score-rubric-objectivity.md`](score-rubric-objectivity.md) 의 `evidence_missing` 항목이 *handoff 에서 박고 종료* 되지 않고, 다음 sprint 의 lesson source 로 *자동 연결* 되어야 함.** budget-saturation-loop 가 budget *quantity* 만, score-rubric-objectivity 가 score *quality* 만 강제 — 두 룰 사이에 *결손 → 보강* 자동 흐름이 없음. 본 컨벤션이 그 흐름.

## 1. 결손 진단

v0.9.15 의 두 컨벤션이 기대한 흐름:

```
sprint NN 종료
  → handoff.self_estimate.evidence_missing = [Conceptual: sensitivity matrix, Sim: ratio, ...]
  → budget < 80% → sprint NN+1 진입
  → sprint NN+1 의 lesson = (사람이 골라야 함?)
  → ???
```

evidence_missing 이 *무엇을 채워야 하는지* 명시되어 있는데, 다음 sprint 의 lesson 으로 *자동 매핑* 되지 않음. agent 가 자유롭게 lesson 선택 → 가장 쉬운 enforcement 항목 선택 가능 (실 delta 0pt). v0915-cold01 진단의 *준비-vs-동작* 갭 핵심.

## 2. 운영 룰

### Step 1 — evidence_missing → lesson candidate 자동 변환

handoff 작성 시점에 *evidence_missing 항목 → sprint lesson candidate* 매핑 자동 생성:

```yaml
# handoff.next_sprint_candidates (자동 생성)
next_sprint_candidates:
  - source: evidence_missing.Conceptual[0]
    description: "lines 350 미달 (313 lines) → narrative 보강 ≥40 lines"
    expected_score_dim: Conceptual
    expected_delta_range: [0.005, 0.020]  # content_depth type
    lesson_type: content_depth
  - source: evidence_missing.Results[0]
    description: "opportunity-cost mention 부재 → Q answer 마다 추가"
    expected_score_dim: Results
    expected_delta_range: [0.003, 0.010]
    lesson_type: content_evidence
  - source: zero_applied_convention[mindmap-quality]
    description: "마인드맵 ≥15 노드 미충족 → 페이즈 01 재진입"
    expected_score_dim: Conceptual
    expected_delta_range: [0.005, 0.020]
    lesson_type: content_depth
```

source 종류:
- `evidence_missing.<dim>[<i>]` — score-rubric-objectivity 항목
- `zero_applied_convention[<name>]` — convention-traceability 항목 (expected 와 교집합)
- `bench_required_outputs.<name>` — deliverable-hurdle-supremacy H4 항목

### Step 2 — sprint NN+1 진입 자동 룰

```python
def should_enter_next_sprint(handoff) -> bool:
    if handoff.budget_used_ratio < 0.80:
        # budget-saturation-loop 룰 — 무조건 진입
        return True
    if handoff.evidence_missing:
        # 본 컨벤션 룰 — evidence 결손 + budget 여유면 진입
        if handoff.budget_used_ratio < 0.95:
            return True
    return False
```

### Step 3 — sprint NN+1 의 lesson 강제 source

sprint NN+1 의 inputs.json:

```json
{
  "sprint_id": "NN+1",
  "lesson_source": "next_sprint_candidates[0]",   // handoff 의 candidate 중 1순위
  "lesson_priority_rule": "expected_delta_range_high_first",
  "free_lesson_allowed": false                    // candidate 무관 lesson 금지
}
```

`free_lesson_allowed: false` 가 핵심 — agent 가 *자유롭게* lesson 을 못 정하고, evidence_missing / zero_applied / bench_required 중에서만 선택.

### Step 4 — sprint NN+1 종료 후 검증

sprint NN+1 의 report.md:

```yaml
lesson_applied_source: evidence_missing.Conceptual[0]
candidate_match: true                # 1순위 candidate 그대로 적용
delta: 0.018                         # expected [0.005, 0.020] 범위 안 — honest
evidence_now_present: true           # 해당 evidence_missing 항목 해소
```

`candidate_match: false` = `LABEL_VIOLATION` (sprint-narrative.md §2 delta tracking 정합, sprint-37 PR-AF 통합).

## 3. self_lint 룰

`scoring/self_lint.py` C-EDP (신규):

```python
def lint_evidence_driven_sprint_planning(skill_root: Path) -> list[str]:
    errors = []
    edp = (skill_root / "conventions" / "evidence-driven-sprint-planning.md").read_text(encoding="utf-8")
    sro = (skill_root / "conventions" / "score-rubric-objectivity.md").read_text(encoding="utf-8")
    bsl = (skill_root / "conventions" / "budget-saturation-loop.md").read_text(encoding="utf-8")
    # 1. SRO 와 BSL 가 본 컨벤션 cross-reference
    if "evidence-driven-sprint-planning" not in sro:
        errors.append("score-rubric-objectivity missing evidence-driven-sprint-planning cross-ref")
    if "evidence-driven-sprint-planning" not in bsl:
        errors.append("budget-saturation-loop missing evidence-driven-sprint-planning cross-ref")
    # 2. 본 컨벤션 핵심 키워드
    required = ["next_sprint_candidates", "lesson_source", "free_lesson_allowed", "candidate_match"]
    for kw in required:
        if kw not in edp:
            errors.append(f"evidence-driven-sprint-planning missing keyword: {kw}")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- candidate source 3 종 (evidence_missing / zero_applied / bench_required) = 모두 generic 메타.
b- expected_delta_range 가 generic (0.000~0.030 범위), 도메인 X.
c- candidate_match 검증 = 단순 비교, 도메인 X.

## 5. 안티 패턴

a- **handoff 에서 evidence_missing 박고 종료** — budget < 80% 면 본 컨벤션 룰 위반. self_lint fail.
b- **sprint NN+1 lesson 이 candidate 와 무관** — `free_lesson_allowed: false` 위반.
c- **evidence_missing 비어있음 + budget < 80% + handoff 종료** — *모든 evidence 채웠는데 budget 남음* = budget-saturation-loop 의 saturation 룰 우선 적용 (다른 차원의 lesson 신규 진입).
d- **candidate 자동 생성 안 함** — handoff 에 next_sprint_candidates 누락 시 self_lint fail.

## 6. 합성 — 3 메타 룰 시너지

| 컨벤션 | 차원 |
|---|---|
| **budget-saturation-loop** (v0.9.15) | budget *quantity* (≥80% 강제) |
| **score-rubric-objectivity** (v0.9.15) | score *quality* (evidence 1:1) |
| **evidence-driven-sprint-planning** (v0.9.16, 본) | *결손 → 보강 자동 흐름* |

세 컨벤션 합성 시 진짜 *self-iterating to 0.999* 루프 — agent 자유 의지 없이 evidence_missing 가 끝까지 채워질 때까지 sprint 추가.

## 7. 자기 검증

본 컨벤션 도입 후 본 하네스의 자기 평가 루프 (BOOTSTRAP) 가 본 컨벤션을 자기에게 적용 — `self_score` < 1.0 이면 evidence_missing 자동 도출 → 다음 self-eval 회차 lesson source.
