# 정체 극복 컨벤션 — 무한 재귀의 함정과 레슨 전달

## 한 줄 요약
**점수가 임계 미달인데 N 회 연속 같은 수준에 머물면 그건 진보가 아닌 정체 — 표면 수정으로 같은 모양에 머물고 있다는 신호.** 레슨을 명시적으로 다음 루프에 전달하고, 정체가 확인되면 *부분 수정 금지·모듈 통째 재작성* 으로 강제 전환한다.

## 무한 재귀의 두 얼굴

ⓐ **건강한 재귀** — 매 루프에서 점수가 *의미 있게* 오르거나 (`Δ ≥ 0.01`) 다른 차원으로 옮겨 가며 보강. 임계 도달까지 향하는 단조 증가 또는 차원별 균형화.
ⓑ **병리적 재귀 (정체)** — 매 루프에서 점수가 같은 값 ± 0.005 내에서 진동, 같은 차원이 같은 수준에 머묾. LLM 비결정성 노이즈만 흔들 뿐 의미 있는 개선 없음. **이 상태는 진보가 아니라 정지** — 영원히 임계 도달 못 함.

## 정체 감지 알고리즘

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

    - 종합 정체: 직전 N 스프린트 점수의 (max-min) < score_eps 이고 마지막 점수가 임계 미달.
    - 차원 정체: 어떤 sub-score 가 N 스프린트 동안 (max-min) < dim_eps 이고 < 0.95.
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

    return StagnationReport(
        overall=overall,
        stagnant_dims=stagnant_dims,
        window=window,
        last_score=sprint_scores[-1] if sprint_scores else None,
    )
```

기본 파라미터 (튜닝 가능, [`../scoring/stagnation.py`](../scoring/stagnation.py) CLI 인자):

ⓐ `window = 3` — 3 스프린트 이상 같은 수준이면 정체.
ⓑ `score_eps = 0.005` — 종합 점수 변동이 0.005 미만이면 같은 수준.
ⓒ `dim_eps = 0.005` — 차원별도 동일.
ⓓ 차원 정체 임계 `< 0.95` — 0.95 이상에서 머무는 건 미세 조정 단계로 취급, 정체 아님.

## 정체 시 강제 행동 (자율 결정, 사용자 ack 없음)

`autonomy.md` 위임 수준 1 (최대 자율) 기준으로:

ⓐ **종합 정체** (overall=True) → **페이즈 06 부터 재시작** — 계획 자체가 잘못된 것. 비평가 페이즈를 다시 거쳐 다른 분할 후보를 도출. 이번 회차의 `impl/` 디렉터리는 `competitions/stagnation-NN/losers/` 로 이동 (보존, 사후 회수 가능).

ⓑ **차원 정체** (특정 sub-score 만) → **그 차원에 해당하는 모듈을 재작성** — `re-architect <module>` 권고가 페이즈 11 의 회귀 바이섹트와 같은 메커니즘. 단, 회귀가 아닌 정지에서 트리거되므로 회귀 권고와 별도 marker (`reason: stagnation`).

ⓒ **부분 수정 금지** — 정체가 감지된 모듈에 대해서는 다음 implementer 호출에 **"기존 코드를 보존하지 말고 처음부터 다시 작성하라"** 가 명시적으로 박힌다. 이전 코드 git history 에 보존, 작업 트리는 빈 상태로 시작.

## 레슨 전달 메커니즘 (lesson_pack)

매 스프린트 종료 후, 다음 implementer/planner 호출에 다음 객체를 *반드시* 첨부 — 단순 "테스트 실패" 가 아니라 *왜 실패했고·이전에 무엇을 시도했고·무엇이 효과 없었는지* 가 명시.

```yaml
lesson_pack:
  current_sprint: 5
  current_score: 0.913
  threshold: 0.999
  delta_to_threshold: 0.086

  # 시계열 — 이전 N 스프린트의 점수와 차원별 sub-score
  history:
    - sprint: 3, score: 0.910, sub: {correctness: 0.95, coverage: 0.85, e2e: 0.90, ...}
    - sprint: 4, score: 0.912, sub: {correctness: 0.95, coverage: 0.86, e2e: 0.90, ...}
    - sprint: 5, score: 0.913, sub: {correctness: 0.95, coverage: 0.86, e2e: 0.91, ...}

  # 정체 분석
  stagnation:
    overall: false
    stagnant_dims: [coverage]            # coverage 가 0.85→0.86 미세 변동, 0.95 미달
    window: 3

  # 이전 시도 요약 — 무엇을 했고 효과 어땠는지
  prior_attempts:
    - sprint: 3, what_was_tried: "FE 통합 테스트 5건 추가", delta: +0.002
    - sprint: 4, what_was_tried: "mock fixture 강화", delta: +0.001
    - sprint: 5, what_was_tried: "에러 경로 unit test", delta: +0.000

  # 효과 없는 전략 (반복 금지)
  forbidden_strategies:
    - "테스트 케이스만 더 추가"            # 3·4·5 모두 시도 → 효과 미미
    - "기존 mock 변형"

  # 추천 행동 (정체 시)
  recommended_action: "rewrite"          # rewrite | extend | accept
  rewrite_targets:
    - module: "fe/login"
      reason: "coverage 차원이 3 스프린트 정체 — DIP 위반 의심, 컴포넌트와 서비스 결합 추정"
  rewrite_rule:
    preserve: false                       # 기존 코드 보존하지 말 것
    start_from: "phase-06-replan"         # 또는 "fresh-impl"

  # 사용자가 결정한 자율 위임 수준 (autonomy.md)
  autonomy_level: 1                       # 1 = 최대 자율, 정체 시에도 자동 rewrite
```

## 부분 수정 vs 깨고 다시 작성 — 판단 기준

| 상황 | 권장 행동 |
| --- | -------- |
| 점수 단조 증가, Δ ≥ 0.01/sprint | extend (이어서 보강) |
| 차원 사이로 균형화, 한 차원 성장하면 다른 차원 보강 필요 | extend |
| 종합 정체 (window=3, eps=0.005) | **rewrite** (페이즈 06 부터) |
| 차원 정체 + 그 차원 < 0.95 | **rewrite module** (해당 모듈만) |
| 점수 회귀 (Δ ≤ -0.05) | 페이즈 11 (회귀 바이섹트) — 별 룰 |
| 점수 ≥ 0.95 + 미세 정체 | extend 허용 (마지막 0.05 는 미세 조정) |

## 깨고 다시 작성 시 보존 정책

ⓐ **git history 보존** — 모든 이전 코드는 git 에 남는다. 작업 트리에서 삭제해도 회수 가능.
ⓑ **`.ShipofTheseus/<프로젝트>/sprints/NN/snapshot/` 보존** — 정체로 폐기되는 코드를 sprint 디렉터리에 스냅샷. 다음 회차의 reference (어떤 모양이었는지 비교 가능).
ⓒ **lesson_pack 누적** — 새 시도가 또 정체되면, 이전 lesson_pack 도 같이 첨부 → "두 번 깨봤지만 같은 차원이 정체 → 의도 자체가 잘못되었을 가능성, 페이즈 04 사용자 질의로 회귀".
ⓓ **3 회 깨고도 정체** → **사용자 ack 강제** (자율성 위임 수준 무관). 본 시스템은 사람 없이 무한 시도 안 함.

## 페이즈 10 (스프린트 루프) 통합

```
sprint = 1
prev_scores = []
dim_history = defaultdict(list)
attempts = []

while True:
    suite = run_test_matrix()
    score, sub = score.py(suite, prior=prev_scores[-1] if prev_scores else None)
    write `sprints/{sprint:02d}/report.md`
    prev_scores.append(score)
    for d, v in sub.items(): dim_history[d].append(v)

    report_to_user_with_timing(sprint, score, prev_scores)

    if score >= 0.999:
        break

    # 회귀 우선 (페이즈 11)
    if len(prev_scores) >= 2 and score < prev_scores[-2] - 0.05:
        run_phase_11(bisect)
        ack_per_autonomy_level()

    # 정체 감지 (NEW — lessons.md)
    stag = detect_stagnation(prev_scores, dim_history)
    if stag.overall:
        spawn_planner(force_replan=True, lesson_pack=build_lesson_pack(...))
        # 페이즈 06 재실행 → 새 분할 후보
        prev_scores = []  # 재시작 — 시계열 분기
        sprint = 1
        continue
    if stag.stagnant_dims:
        for module in identify_modules(stag.stagnant_dims):
            spawn_implementer(rewrite=True, target=module,
                              lesson_pack=build_lesson_pack(...))
        attempts.append({"sprint": sprint, "rewrites": stag.stagnant_dims})

    # 일반 다음 스프린트
    if not stag.overall and not stag.stagnant_dims:
        spawn_implementer(failing=suite.failing, lesson_pack=build_lesson_pack(...))

    sprint += 1
```

## 사용자에게 알리는 정체 보고 형식

[`timing.md`](timing.md) 의 라이브 보고 + [`autonomy.md`](autonomy.md) 의 자율 결정 보고에 한 줄:

```
스프린트 5 완료 — 점수 0.913 (직전 0.912, 0.910). 누적 1시간 5분. 자율 결정: coverage 차원 정체 감지 → fe/login 모듈 재작성 (이전 코드는 sprints/05/snapshot/ 보존). 다음 스프린트 진행.
```

3 회 깨고도 정체 시:

```
경고: fe/login 모듈을 3 회 재작성했지만 coverage 차원이 계속 정체. 의도 또는 계획 단계의 모호함이 의심됩니다. 페이즈 04 사용자 질의로 돌아갈까요?

선택지:
1. 페이즈 04 재실행 (의도 다시 명확화)
2. 한 번 더 시도 (rewrite 4회차)
3. 정지 — 사람이 직접 검토
4. 임계 0.999 → 0.95 로 일시 완화 후 진행 (사용자 명시 동의)
```

## 안티 패턴

ⓐ **점수 정체를 "임계 미달 = 다음 스프린트" 만으로 처리** → 영원한 같은 수준 반복.
ⓑ **레슨 누락** — implementer 가 `failing_tests` 만 받고 *왜 실패했는지·이전에 무엇을 시도했는지* 모르면 같은 패턴 반복.
ⓒ **rewrite 트리거에서 부분 수정** — implementer 가 "rewrite 권고 무시하고 기존 코드 보강" 하면 정체 지속. **rewrite_rule.preserve=false 강제 준수**.
ⓓ **3 회 자동 rewrite 후에도 사용자 ack 안 함** — 자율은 무한 시도가 아니라 *합리적 자율*. 한계는 항상 있다.
