# Sprint Score Delta Tracking — sprint NN+1 점수 향상 검증

## 한 줄 요약

**매 sprint NN 의 lesson 적용 후 sprint NN+1 의 점수 - sprint NN 의 점수 = delta.** delta 가 lesson type 라벨에 부합하지 않으면 self_lint C-SDT fail. v0.9.15 budget-saturation-loop 가 lesson type 분류 (content depth / enforcement / etc.) 만 명시, *측정* 메커니즘 없음 → 본 컨벤션이 *honest 분류* 강제.

## 1. 결손 진단

[`sprint-regression-loop.md`](sprint-regression-loop.md) (v0.9.8) 가 sprint NN+1 lesson 적용 룰 도입.
[`budget-saturation-loop.md`](budget-saturation-loop.md) (v0.9.15) 가 lesson type 4 분류 도입:

| Lesson type | 기대 효과 (claim) |
|---|---|
| content depth | self-estimate +0.5-1pt |
| enforcement structure | +0pt (이미 PASS) |
| content evidence | +0.5pt |
| integrated insight | +0.5pt |

→ 그러나 *실제 측정* 안 함. agent 가 sprint NN+1 의 lesson 을 "content depth" 로 라벨링하고 점수 +0pt 반복해도 검출 불가. v0.9.6-12 의 enforcement 만 강화 패턴 재발.

## 2. 운영 룰

### Step 1 — sprint frontmatter 에 score 시계열 의무

`sprints/NN/report.md` frontmatter:

```yaml
sprint_id: NN
prev_sprint_score: 0.872            # NN-1 의 self-estimate (또는 외부 채점)
current_sprint_score: 0.891
delta: 0.019
lesson_applied:
  type: content_depth                # content_depth | enforcement | content_evidence | integrated_insight
  description: "Conceptual narrative ≥3 sub-section 추가 (Threats / Confidence / V&V)"
  source: evidence_missing[Conceptual]  # evidence-driven-sprint-planning 정합
```

### Step 2 — delta 검증 룰

`scoring/sprint_delta.py` 신규:

```python
EXPECTED_DELTA = {
    "content_depth": (0.005, 0.030),       # 0.5~3.0pt
    "content_evidence": (0.003, 0.015),    # 0.3~1.5pt
    "integrated_insight": (0.003, 0.015),
    "enforcement": (0.000, 0.005),         # 0~0.5pt — 큰 효과 기대 X
}

def check_sprint_delta(sprint_dir: Path) -> list[str]:
    errors = []
    report = read_yaml(sprint_dir / "report.md")
    delta = report["delta"]
    lesson_type = report["lesson_applied"]["type"]
    lo, hi = EXPECTED_DELTA[lesson_type]
    if not (lo <= delta <= hi):
        # honesty 위반: 라벨링이 실 효과와 불일치
        errors.append(f"{sprint_dir.name}: delta {delta:.3f} outside expected [{lo:.3f}, {hi:.3f}] for type={lesson_type}")
    return errors
```

### Step 3 — 라벨링 위반 처리

label-honesty 위반 시:
- sprint NN+1 = `LABEL_VIOLATION` 마킹
- 해당 lesson 의 라벨 자동 재분류 (실 delta 에 부합하는 type 으로 권고)
- handoff 의 `self_estimate` 에 *lesson_label_corrections* 본문 의무

### Step 4 — 누적 honesty 점수

회차 종료 시:

```
Sprint label honesty:
  total sprints: 6
  honest labels: 5 (83.3%)
  violations: 1 (sprint 03 — claimed content_depth, delta=0.001 → suggest enforcement)
```

honesty < 80% = 회차 *self-rating noise* 의심 → score-rubric-objectivity 와 합쳐 회귀 분류.

## 3. self_lint 룰

`scoring/self_lint.py` C-SDT (신규):

```python
def lint_sprint_score_delta(skill_root: Path) -> list[str]:
    errors = []
    bsl = (skill_root / "conventions" / "budget-saturation-loop.md").read_text(encoding="utf-8")
    sdt = (skill_root / "conventions" / "sprint-score-delta-tracking.md").read_text(encoding="utf-8")
    # 1. budget-saturation-loop 가 본 컨벤션을 cross-reference
    if "sprint-score-delta-tracking" not in bsl:
        errors.append("budget-saturation-loop missing sprint-score-delta-tracking cross-ref")
    # 2. sprint_delta 모듈 또는 self_lint 함수 존재
    self_lint_body = (skill_root / "scoring" / "self_lint.py").read_text(encoding="utf-8")
    if "sprint_delta" not in self_lint_body and not (skill_root / "scoring" / "sprint_delta.py").exists():
        errors.append("sprint_delta measurement function missing")
    # 3. 본 컨벤션 본문 키워드
    required = ["delta", "lesson_applied", "EXPECTED_DELTA", "label honesty"]
    for kw in required:
        if kw not in sdt:
            errors.append(f"sprint-score-delta-tracking missing keyword: {kw}")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- delta 메트릭 = generic 정량 (점수 차), 도메인 X.
b- lesson type 4 분류 = budget-saturation-loop 의 generic 분류 재사용.
c- EXPECTED_DELTA 범위 = 의미군 단위, 도메인 X.
d- label honesty 메트릭 = 모든 회차 / 모든 도메인 동일.

## 5. 안티 패턴

a- **모든 lesson 을 content_depth 로 라벨링** — 실 delta 작아도 honest 라벨 위반. EXPECTED_DELTA 범위 강제.
b- **delta 음수 (회귀)** — sprint NN+1 점수 < sprint NN 점수 = 회귀 즉시 페이즈 11 트리거.
c- **delta 측정 누락** — frontmatter 의 prev/current/delta 누락 시 self_lint fail.
d- **bench 채점 외부 데이터 미반영** — 외부 채점 갱신 시 prev_sprint_score 가 외부 채점 값으로 갱신 의무 (self-rating noise 차단).

## 6. 자기 검증

본 컨벤션 자체에 *meta-application* — 본 컨벤션 도입 후 다음 sprint 의 lesson type 라벨링 정합성을 self 가 검증. v0.9.16 sprint-10 첫 회차 = 본 컨벤션 자체.
