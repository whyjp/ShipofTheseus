---
id: sprint-narrative
category: sprint
applies-to-phases: '[06,10,11]'
applies-to-grades: '[all]'
trigger-when: 'always (lessons / stagnation) / sprint NN+1 (delta) / universe 패배 (cross-universe)'
indexed-in: conventions/INDEX.md
---

# Sprint Narrative — sprint loop 의 *시간/공간/단계* 3 layer 학습 전이

## 한 줄 요약

**sprint loop 의 *학습 전이* 3 layer 통합** :
① **시간 axis** (delta-tracking) — sprint NN→NN+1 점수 + lesson type label honesty.
② **공간 axis** (cross-universe) — 패배 universe 약점을 우승 본문에 *Patterns to Avoid* 로 흡수.
③ **단계 axis** (stagnation + lessons) — 정체 감지 + lesson_pack + rewrite 정책 (`preserve=false`) + Q-D4 사전 위임.

본 컨벤션이 본 하네스의 *forward + backward + temporal* multiverse 학습 전이 운영 형태.

## 1. 결손 진단 (3 layer 통합)

| layer | 결손 | 영향 |
|---|---|---|
| ① delta | budget-saturation-loop 가 lesson type 4 분류만 명시, *실 측정* 안 함. 모든 lesson 을 `content_depth` 라벨링하고 점수 +0pt 반복 검출 불가 | self-rating noise → score plateau |
| ② cross-universe | tournament resolve 가 우승 universe 채택 + ensemble *합집합* 만, 패배 universe 의 *핵심 약점* 이 우승 본문에 박히지 않음 | 페이즈 08 / 10 가 같은 약점 재발견 |
| ③ stagnation | 점수 임계 미달인데 N 회 같은 수준 = 정체. 표면 수정으로 같은 모양 머뭄 — implementer 가 부분 수정만 반복 | 영원한 임계 도달 실패 |

→ 3 axis 모두 학습 전이 강제 박혀야 sprint loop 의 self-polishing 이 진짜 작동.

## 2. Layer ① — Sprint Score Delta Tracking (시간 axis)

매 sprint NN 의 lesson 적용 후 sprint NN+1 의 점수 - sprint NN 의 점수 = delta. delta 가 lesson type 라벨에 부합하지 않으면 self_lint C-SDT fail. *honest 분류* 강제.

### 2.1 sprint frontmatter score 시계열 의무

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

### 2.2 delta 검증 룰 (EXPECTED_DELTA)

`scoring/sprint_delta.py`:

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
        errors.append(f"{sprint_dir.name}: delta {delta:.3f} outside expected [{lo:.3f}, {hi:.3f}] for type={lesson_type}")
    return errors
```

label-honesty 위반 시:
- sprint NN+1 = `LABEL_VIOLATION` 마킹
- 해당 lesson 의 라벨 자동 재분류 (실 delta 에 부합하는 type 으로 권고)
- handoff 의 `self_estimate` 에 *lesson_label_corrections* 본문 의무

### 2.3 누적 label honesty 점수

회차 종료 시:

```
Sprint label honesty:
  total sprints: 6
  honest labels: 5 (83.3%)
  violations: 1 (sprint 03 — claimed content_depth, delta=0.001 → suggest enforcement)
```

honesty < 80% = 회차 *self-rating noise* 의심 → score-rubric-objectivity 와 합쳐 회귀 분류.

## 3. Layer ② — Cross-Universe Lesson Distillation (공간 axis)

Tournament resolve 시 *우승 universe 만 채택* (또는 ensemble union) 으로 끝나지 않고, *패배 universe 의 핵심 약점 ≥ 1-2 줄* 을 우승 본문에 흡수 의무.

### 3.1 패배 universe 핵심 약점 추출

각 패배 universe 의 `meta.md` (또는 plan-reviewer 의 4 답) 에서 *결정적 약점 reason* 을 1-2 줄로 추출:

```python
def extract_loser_weakness(loser_meta: dict) -> str:
    # 채점 5 차원 중 가장 낮은 차원 + 그 사유
    scores = loser_meta["score"]
    weakest_dim = min(scores, key=scores.get)
    reason = loser_meta["plan_reviewer_4_answers"]["question_3"]
    return f"{loser_meta['universe_id']}: weakest={weakest_dim} ({scores[weakest_dim]:.2f}) — {reason}"
```

### 3.2 우승 본문 흡수 절 의무

`plan/06-plan.md` (우승 universe 사본) 에 신규 절 *"## Patterns to Avoid (from defeated universes)"*:

```markdown
## Patterns to Avoid (from defeated universes)

본 우승 universe (universe-1-domain-first) 가 채택되었으나, 패배 universe 가 시도한 다음 패턴은 본 페이즈 08 구현 시 *명시 회피*:

- **universe-2-adapter-first**: weakest=simplicity (0.65) — 모든 도메인에 포트 인터페이스 강제로 보일러플레이트 비대.
- **universe-3-minimal-subtraction**: weakest=test_topology (0.78) — 모듈 합치기로 단위 테스트 표면적 부족.
```

### 3.3 페이즈 08 구현 시 avoid_patterns 입력 의무

`impl/08-impl-log.md` 의 inputs:

```yaml
plan_source: plan/06-plan.md
avoid_patterns:                         # 페이즈 06 의 흡수 절 자동 추출
  - "포트 인터페이스 강제 (단일 도메인 시)"
  - "모듈 합치기 (테스트 표면 부족)"
verification: 페이즈 08 산출물이 avoid_patterns 위반 시 자동 fail
```

`agents/implementer.md` 가 avoid_patterns 를 *forbidden_strategies* 와 동급 처리 (§4 lessons 정합).

### 3.4 페이즈 10 sprint 시 transfer 추적

sprint NN 의 `inputs.json` 에 `avoid_patterns_inherited: [...]` 명시. self_lint 가 sprint 회차 동안 avoid_patterns 위반 0 건 검증.

## 4. Layer ③ — Stagnation + Lessons (단계 axis)

점수가 임계 미달인데 N 회 연속 같은 수준에 머물면 *진보가 아닌 정체*. 레슨을 명시적으로 다음 루프에 전달하고, 정체 확인 시 *부분 수정 금지·모듈 통째 재작성*.

### 4.1 무한 재귀의 두 얼굴

a- **건강한 재귀** — 매 루프 점수가 *의미 있게* 오르거나 (`Δ ≥ 0.01`) 다른 차원으로 옮겨 가며 보강.
b- **병리적 재귀 (정체)** — 매 루프 점수가 같은 값 ± 0.005 진동, 같은 차원이 같은 수준 머묾. **이 상태는 진보가 아니라 정지**.

### 4.2 정체 감지 알고리즘

```python
def detect_stagnation(
    sprint_scores: list[float],
    dim_history: dict[str, list[float]],
    window: int = 3,
    score_eps: float = 0.005,
    dim_eps: float = 0.005,
) -> StagnationReport:
    """
    직전 N(window) 스프린트의 sub-score 시계열로 정체 판단.
    - 종합 정체: 직전 N 스프린트 (max-min) < score_eps + 마지막 임계 미달.
    - 차원 정체: 어떤 sub-score N 스프린트 (max-min) < dim_eps + < 0.95.
    """
    n = len(sprint_scores)
    overall = False
    if n >= window:
        recent = sprint_scores[-window:]
        if (max(recent) - min(recent)) < score_eps and recent[-1] < 0.999:
            overall = True
    stagnant_dims: list[str] = []
    for dim, hist in dim_history.items():
        if len(hist) < window:
            continue
        rec = hist[-window:]
        if (max(rec) - min(rec)) < dim_eps and rec[-1] < 0.95:
            stagnant_dims.append(dim)
    return StagnationReport(overall=overall, stagnant_dims=stagnant_dims, window=window, last_score=sprint_scores[-1] if sprint_scores else None)
```

기본 파라미터 ([`../scoring/stagnation.py`](../scoring/stagnation.py) CLI 인자):
- `window = 3` — 3 스프린트 이상 같은 수준이면 정체.
- `score_eps = 0.005` / `dim_eps = 0.005`
- 차원 정체 임계 `< 0.95` — 0.95 이상은 미세 조정 단계로 취급.

### 4.3 정체 시 강제 행동 (자율 결정, 사용자 ack 없음)

`autonomy.md` 위임 수준 1 (최대 자율) 기준:

a- **종합 정체 (overall=True)** → **페이즈 06 부터 재시작**. 이번 회차의 `impl/` 디렉터리는 `competitions/stagnation-NN/losers/` 로 이동.
b- **차원 정체 (특정 sub-score)** → **그 차원에 해당하는 모듈을 재작성**. `re-architect <module>` 권고 (페이즈 11 회귀 바이섹트와 같은 메커니즘, marker `reason: stagnation`).
c- **부분 수정 금지** — 정체 모듈 implementer 호출에 *"기존 코드를 보존하지 말고 처음부터 다시 작성하라"* 명시. 이전 코드 git history 보존, 작업 트리 빈 상태로 시작.

### 4.4 lesson_pack — 레슨 전달 메커니즘

매 스프린트 종료 후, 다음 implementer/planner 호출에 다음 객체 *반드시* 첨부 :

```yaml
lesson_pack:
  current_sprint: 5
  current_score: 0.913
  threshold: 0.999
  delta_to_threshold: 0.086

  # 시계열
  history:
    - sprint: 3, score: 0.910, sub: {correctness: 0.95, coverage: 0.85, ...}
    - sprint: 4, score: 0.912, sub: {correctness: 0.95, coverage: 0.86, ...}
    - sprint: 5, score: 0.913, sub: {correctness: 0.95, coverage: 0.86, ...}

  # 정체 분석
  stagnation:
    overall: false
    stagnant_dims: [coverage]
    window: 3

  # 이전 시도 + 효과
  prior_attempts:
    - sprint: 3, what_was_tried: "FE 통합 테스트 5건 추가", delta: +0.002
    - sprint: 4, what_was_tried: "mock fixture 강화", delta: +0.001
    - sprint: 5, what_was_tried: "에러 경로 unit test", delta: +0.000

  # 효과 없는 전략 (반복 금지)
  forbidden_strategies:
    - "테스트 케이스만 더 추가"
    - "기존 mock 변형"

  # 추천 행동
  recommended_action: "rewrite"          # rewrite | extend | accept
  rewrite_targets:
    - module: "fe/login"
      reason: "coverage 차원 3 sprint 정체 — DIP 위반 의심"
  rewrite_rule:
    preserve: false                       # 기존 코드 보존하지 말 것
    start_from: "phase-06-replan"
  autonomy_level: 1

  # 방어 테스트 (dacapo §"방어 테스트")
  defense_test:
    test_id: "T-AUTH-DEFENSE-042"
    test_path: "internal/auth/defense_test.go::TestExpiredTokenStillRejected"
    reproduces_failure: "지난 실패 X 조건 + 그 레슨이 적용된 코드"
    added_to_regression_suite: true
    added_at: "2026-05-01T18:42:11+09:00"
```

### 4.5 부분 수정 vs 깨고 다시 작성 — 판단 기준

**rewrite 트리거는 단일 차원이 아니다 — 다음 *어느 차원* 이라도 깊이가 임계를 넘으면 부분 수정 금지·통째 재작성.**

| 위반 차원 | 깊이 임계 | 권장 행동 |
| -------- | -------- | -------- |
| **정체 / 회귀 누적** (종합) | window=3, eps=0.005 | **rewrite** (페이즈 06 부터 재계획) |
| **정체** (차원별) | window=3 + 그 차원 < 0.95 | **rewrite module** |
| **DIP / SOLID 깊은 위반** | 단독 hard cap 0.6 (게이트 1) | **rewrite module** (DIP 경계 재정의) |
| **코드 오류 누적** | 동일 사상 버그 ≥ 3 모듈 | **rewrite module** |
| **기획-구현 갭 (스펙 누락)** | 의도 항목 누락 부분 추가로 책임 정합 불가 | **rewrite module** + 페이즈 06 부분 재계획 |
| **성능 / NFR 미달** | 게이트 6 (resources.md 천정) 깊은 미달 | **rewrite module** (자료구조·알고리즘 재선정) |
| **의도 표류** | 페이즈 04 사전 위임 답과 모순 누적 | **rewrite from phase-06** |
| 점수 단조 증가, Δ ≥ 0.01/sprint | — | extend |
| 차원 사이 균형화 | — | extend |
| 점수 회귀 (Δ ≤ -0.05) | — | 페이즈 11 (회귀 바이섹트) — 별 룰 |
| 점수 ≥ 0.95 + 미세 정체 | — | extend (마지막 0.05 미세 조정) |

위 차원 중 하나라도 임계 깊이 초과 시 implementer 호출에 `rewrite_rule.preserve=false` 강제. 어느 차원에서 트리거되었는지 `rewrite_targets[].reason` 명시 ([`checkpoints.md`](checkpoints.md) 11 분류 1:1 매핑).

### 4.6 깨고 다시 작성 시 보존 정책

a- **git history 보존** — 모든 이전 코드는 git 에 남는다.
b- **`.ShipofTheseus/<프로젝트>/sprints/NN/snapshot/` 보존** — 정체로 폐기되는 코드를 sprint 디렉터리에 스냅샷.
c- **lesson_pack 누적** — 새 시도가 또 정체되면, 이전 lesson_pack 도 같이 첨부 → "두 번 깨봤지만 같은 차원이 정체 → 의도 자체 잘못".
d- **3 회 깨고도 정체** → [`autonomy.md`](autonomy.md) Q-D4 사전 위임 답 자동 적용. 인터뷰 후 ack 호출 없음.

### 4.7 페이즈 10 sprint loop 통합

```
sprint = 1
prev_scores = []
dim_history = defaultdict(list)

while True:
    suite = run_test_matrix()
    score, sub = score.py(suite, prior=prev_scores[-1] if prev_scores else None)
    write `sprints/{sprint:02d}/report.md`
    prev_scores.append(score)
    for d, v in sub.items(): dim_history[d].append(v)

    if score >= 0.999: break

    # 회귀 우선 (페이즈 11)
    if len(prev_scores) >= 2 and score < prev_scores[-2] - 0.05:
        run_phase_11(bisect)
        ack_per_autonomy_level()

    # 정체 감지
    stag = detect_stagnation(prev_scores, dim_history)
    if stag.overall:
        spawn_planner(force_replan=True, lesson_pack=build_lesson_pack(...))
        prev_scores = []  # 시계열 분기
        sprint = 1
        continue
    if stag.stagnant_dims:
        for module in identify_modules(stag.stagnant_dims):
            spawn_implementer(rewrite=True, target=module, lesson_pack=build_lesson_pack(...))

    if not stag.overall and not stag.stagnant_dims:
        spawn_implementer(failing=suite.failing, lesson_pack=build_lesson_pack(...))

    sprint += 1
```

### 4.8 사용자에게 알리는 정체 보고 형식

```
스프린트 5 완료 — 점수 0.913 (직전 0.912, 0.910). 누적 1시간 5분.
자율 결정: coverage 차원 정체 감지 → fe/login 모듈 재작성 (이전 코드는 sprints/05/snapshot/ 보존).
```

3 회 깨고도 정체 시 — 인터뷰 후 ack 없이 [`autonomy.md`](autonomy.md) Q-D4 사전 위임 답 자동 적용.

## 5. self_lint 룰 요약

| 룰 ID | layer | 검증 |
|---|---|---|
| **C-SDT** | ① delta | sprint-narrative.md 본문 키워드 (delta, lesson_applied, EXPECTED_DELTA, label honesty) + budget-saturation-loop cross-ref |
| **C-CULD** | ② cross-universe | sprint-narrative.md 본문 키워드 (Patterns to Avoid, avoid_patterns, extract_loser_weakness, weakest_dim) + plan-tree / ensemble cross-ref |
| **C20** | ③ lessons | sprint-narrative.md 존재 + scoring/stagnation.py 존재 + phases/10 / agents/implementer / agents/planner 의 lesson_pack + preserve / stagnation 키워드 |

## 6. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- delta 메트릭 = generic 정량, 도메인 X.
b- weakest_dim 추출 = 5 차원 중 min, 도메인 X.
c- 정체 감지 알고리즘 = window/eps 기반, 도메인 X.
d- lesson_pack 구조 = generic frontmatter, 도메인 X.
e- rewrite 트리거 = checkpoints.md 11 분류 generic.

## 7. 호환성

- [`budget-saturation-loop.md`](budget-saturation-loop.md) — §2 의 lesson type 4 분류 honest tracking 정합.
- [`evidence-driven-sprint-planning.md`](evidence-driven-sprint-planning.md) — `LABEL_VIOLATION` 정합 (§2 lesson honesty).
- [`grader-in-sprint.md`](grader-in-sprint.md) — shadow predicted_score *덮어쓰기* 차단 (§2 honest 라벨링 위반).
- [`plan-tree.md`](plan-tree.md) / [`ensemble-synthesis-default.md`](ensemble-synthesis-default.md) — §3 차이집합 합성 (합집합 보완).
- [`contested-decision-multiverse.md`](contested-decision-multiverse.md) — 패배 universe 의 *spike 차이집합* 도 §3 흡수 의무.
- [`checkpoints.md`](checkpoints.md) — §4 의 11 분류 / `find_regression_target` 8 가지 failure_kind 1:1 매핑.
- [`autonomy.md`](autonomy.md) — Q-D4 사전 위임 답 (3 회 rewrite 후 정체 정책).
- [`dacapo.md`](dacapo.md) — §4 의 lesson_pack 이 dacapo 의 Memory step + defense_test 필드 정합.

## 8. 안티 패턴

### 8.1 Layer ① 안티 패턴

a- **모든 lesson 을 content_depth 로 라벨링** — EXPECTED_DELTA 범위 강제.
b- **delta 음수 (회귀)** — sprint NN+1 점수 < NN 점수 = 페이즈 11 즉시 트리거.
c- **delta 측정 누락** — frontmatter 의 prev/current/delta 누락 시 self_lint fail.
d- **bench 채점 외부 데이터 미반영** — 외부 채점 갱신 시 prev_sprint_score 갱신 의무.

### 8.2 Layer ② 안티 패턴

e- **우승 universe 만 채택 + 패배 즉시 losers/ 폐기** — 학습 전이 0.
f- **흡수 절 형식적** — "패배 universe 가 있다" 만 박고 *실 weakest_dim + reason* 없음.
g- **avoid_patterns 페이즈 08 미반영** — implementer 가 avoid_patterns 를 forbidden 처리 안 함.

### 8.3 Layer ③ 안티 패턴

h- **점수 정체를 "임계 미달 = 다음 스프린트" 만으로 처리** → 영원한 같은 수준 반복.
i- **레슨 누락** — implementer 가 `failing_tests` 만 받고 *왜 실패했는지·이전에 무엇을 시도했는지* 모르면 같은 패턴 반복.
j- **rewrite 트리거에서 부분 수정** — `rewrite_rule.preserve=false` 강제 준수.
k- **3 회 자동 rewrite 후에도 정체** — Q-D4 답에 따라 자동 fallback. ack 없음.

## 9. 통합 history (sprint-37 PR-AF)

본 컨벤션은 sprint-37 PR-AF (다이어트) 에서 **`sprint-score-delta-tracking`** (sprint-10 v0.9.16, 시간 axis) + **`cross-universe-lesson-distillation`** (sprint-10 v0.9.16, 공간 axis) + **`lessons`** (sprint-02, 단계 axis) 세 컨벤션을 단일 컨벤션의 §2/§3/§4 세 axis 로 통합. 책임 = "sprint loop 학습 전이" 단일, 세 axis = 시간 (delta) / 공간 (cross-universe) / 단계 (stagnation+lessons). 매핑은 [`MIGRATION.md`](MIGRATION.md) 단일 source.
