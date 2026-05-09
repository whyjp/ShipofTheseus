# Phase 10 — 무한 스프린트 루프 (v0.9.19 sprint-13: 3 axis trinity)

## 한 줄 요약
**점수 ≥ 0.999 가 나올 때까지 무한 반복한다 + axis 별 ≥ 2 sprint 강제 (intent / plan / impl trinity).** 회수 캡 없음 — 단, *전체 budget cap 80% 사용 + axis 별 sprint ≥ 2* 충족 시 soft-converge. 점수가 직전 스프린트 대비 0.05 이상 떨어지면 즉시 페이즈 11(회귀 바이섹트) — Q-D1 사전 위임 답에 따라 자동 적용 (인터럽트 없음, 자동 매핑).

## Sprint Trinity 3 axis 분배

[`../conventions/intent-plan-impl-sprint-trinity.md`](../conventions/intent-plan-impl-sprint-trinity.md) (bd) 의 3 axis :

| Axis | 내용 | sprint 산출물 |
|---|---|---|
| **intent** | 페이즈 01 mindmap richness / §k 9 sub depth / §i derived NFR 보강 | sprints/intent-NN/report.json |
| **plan** | 페이즈 06 plan/06-plan.md 의 인터페이스/모듈/per-module use-case/TODO DAG 보강 | sprints/plan-NN/report.json |
| **impl** | 페이즈 08 impl/08-impl-log.md 의 코드/테스트/NFR (regression §2 sprint loop) | sprints/impl-NN/report.json |

### budget 분배 default

```yaml
budget_default_split:
  intent: 0.20    # 20% (90 min × 0.20 = 18 min)
  plan:   0.30    # 30% (27 min)
  impl:   0.50    # 50% (45 min)
```

### Templated sprint trinity report.json schema

```json
{
  "sprint_axis": "intent | plan | impl",
  "sprint_n": 1,
  "per_dimension": {
    "<dim_name>": {"score": 18, "max": 20, "gap": 2}
  },
  "total_score": 94,
  "threshold_target": 0.999,
  "weakest_dimension": "<name>",
  "lesson_type": "content_depth | enforcement_structure | content_evidence | integrated_insight",
  "lesson_applied": "<one-line description>",
  "budget_used_axis": 0.45,
  "axis_sprint_count": 2
}
```

### early stop violation (강화 — sprint-14 dual-objective AND)

```python
def should_stop_sprint(state) -> bool:
  # sprint-14 v0.9.20 — grader-in-sprint be 의 dual-objective AND
  auto_pass    = state.auto_proxy_pass_rate >= 0.999
  shadow_pass  = state.shadow_grader_predicted_score >= state.target_score  # default 95
  axis_pass    = all(c >= 2 for c in state.axis_sprint_counts.values())     # bd v0.9.19
  budget_pass  = state.budget_used_total >= 0.80                             # an v0.9.15
  return auto_pass AND shadow_pass AND axis_pass AND budget_pass
```

**4 conjunction 만 PASS** — 어느 하나 미달 시 sprint 추가. self_lint C-IPI 가 axis 별 sprint ≥ 2, C-BSL 이 budget 80%, C-GIS 가 shadow_grader 호출 + 종료점 검증.

## Grader-in-Sprint Dual-Objective ([`../conventions/grader-in-sprint.md`](../conventions/grader-in-sprint.md), be)

### shadow grader 호출 — sprint 마다 1 회

매 sprint NN 종료 *직전* zero-context shadow grader (Sonnet) 1 회 호출. 입력 = rubric (페이즈 04 의 RubricAdapter 출력 OR `scoring/rubric.md` fallback) + 본 sprint 의 변경 산출물 list. 출력 = `predicted_score / per_category_score / weakest_category / lesson_candidates` (top 3).

```yaml
shadow_grader:
  call_phase: 페이즈 10 sprint NN 종료 직전
  inputs:
    - rubric: scoring/rubric.md OR <bench>/expected/scoring_rules.yaml
    - artifacts: [plan/06-plan.md, impl/08-impl-log.md, code/, quality/09-quality-gate.md, handoff (있으면)]
    - context_mode: zero-context  # 누적 conversation 없이 fresh load
  output:
    - predicted_score: 0~100
    - per_category_score: {<category>: <score>}
    - weakest_category: <name>
    - weakest_category_evidence: <citation>
    - lesson_candidates: [<top-3 specific suggestions>]
  model: Sonnet (cheap shadow — precise score 가 아니라 delta direction)
  cost_cap: 1 call per sprint axis × NN
```

### Sprint report.json 갱신 (sprint-14)

```json
{
  "sprint_axis": "intent | plan | impl",
  "sprint_n": 1,
  "auto_proxy_pass_rate": 1.0,
  "shadow_grader_predicted_score": 92,
  "shadow_grader_call_id": "<uuid>",
  "shadow_grader_per_category": {"conceptual": 18, ...},
  "shadow_grader_weakest_category": "data_topology",
  "shadow_grader_lesson_candidates": [...],
  "target_score": 95,
  "stop_decision": "continue",  // 4 AND 미달
  "lesson_type": "content_depth",
  "lesson_applied": "<one-line>",
  "budget_used_axis": 0.45,
  "axis_sprint_count": 2
}
```

### Lesson source 통합 (3 layer)

다음 sprint NN+1 의 lesson source = 3 source 합산 :

1. v0.9.16 [`evidence-driven-sprint-planning.md`](../conventions/evidence-driven-sprint-planning.md) 의 `evidence_missing` (self-rating)
2. v0.9.20 [`grader-in-sprint.md`](../conventions/grader-in-sprint.md) shadow grader `lesson_candidates`
3. v0.9.20 [`rubric-targeted-quality-gates.md`](../conventions/rubric-targeted-quality-gates.md) fail RTG → lesson 매핑

가장 자주 등장하는 weakest_category 가 sprint NN+1 의 axis lesson 우선순위.

### target_score 매트릭스

| Grade | shadow target |
|---|:-:|
| G2 | 80 |
| G3 | 90 |
| G4 (default) | 95 |
| G5 | 98 |

[`../conventions/grades.md`](../conventions/grades.md) 의 *automated 임계 0.999* 와 *human-rubric target* row 직교.

## 매 스프린트 테스트 매트릭스

a- 백엔드 단위 — Go `testing` (또는 사용자 명시 스택).
b- 백엔드 통합 — `httptest` 로 어댑터 페이크.
c- 프론트엔드 단위 — `bun test` + 컴포넌트 단위.
d- 프론트엔드 통합 — fake 서비스로 컴포넌트 와이어드.
e- E2E — Playwright 등 — happy-path + 에러 1 경로.
f- 속성 기반 (직전 스프린트가 커버리지 얕음 플래그 시).

## 서브에이전트
[`../agents/tester.md`](../agents/tester.md). 테스터는 *실행* 만, 채점은 안 함 — 채점은 [`../scoring/score.py`](../scoring/score.py) 가 권위.

## 산출물 (스프린트별)
`sprints/NN/report.md` — [`../templates/sprint-report.template.md`](../templates/sprint-report.template.md), 헤더에 [`../conventions/timing.md`](../conventions/timing.md) 의 시간 메타 필수.
`sprints/NN/inputs.json` — `score.py` 입력 (test_pass_rate, coverage, modules_passing_solid 등).
`sprints/NN/score.json` — `score.py --out` 산출. **v0.2.1 부터 의무** — `inputs.json` 은 *입력* 이고 `score.json` 이 *출력* (score / raw_score / sub_scores / caps_applied / dip_violation / passes_threshold). webview/be4fe `/api/sprints` 가 이 파일을 직접 로드해 Sprints 차트의 데이터 소스로 사용.
`sprints/NN/bisect.md` — 회귀 트리거 시.

**score.py 호출 형식 (v0.2.1)**:

```bash
python scoring/score.py \
  --inputs sprints/NN/inputs.json \
  --prior sprints/N-1/score.json \
  --out sprints/NN/score.json
```

`--out` 누락 시 `inputs.json` 만 남고 `score.json` 미산출 → webview Sprints 차트가 빈 상태 (Cursor Bugbot PR#1 지적 회귀).

각 스프린트는 git 체크포인트 커밋 (테스터가 수행) — 페이즈 11 이 바이섹트할 수 있도록.

## 루프 (의사코드)

```
sprint = 1
prev_scores = []
dim_history = defaultdict(list)
prior_attempts = []
forbidden_strategies = []

while True:
    suite = run_test_matrix()
    inputs = build_score_inputs(suite, gate_results)
    write `sprints/{sprint:02d}/inputs.json` (score.py 입력)
    score, sub = score.py(
        inputs=`sprints/{sprint:02d}/inputs.json`,
        prior=`sprints/{sprint-1:02d}/score.json` if prev_scores else None,
        out=`sprints/{sprint:02d}/score.json`,            # v0.2.1 의무 — webview 차트 데이터 소스
    )
    write `sprints/{sprint:02d}/report.md` (timing header + score.json 본문 paste)
    prev_scores.append(score)
    for d, v in sub.items(): dim_history[d].append(v)
    report_to_user_with_timing(sprint, score, prev_scores)

    if score >= 0.999:
        return "pass"

    # 1- 회귀 우선 — 페이즈 11 (lessons.md 의 정체와 별 트리거)
    if len(prev_scores) >= 2 and score < prev_scores[-2] - 0.05:
        run_phase_11 → `sprints/{sprint:02d}/bisect.md`
        # autonomy.md Q-D1 사전 위임 답 자동 적용 — 인터럽트 없음
        apply_q_d1_policy(bisect_recommendation, autonomy_policy["Q-D1"])
        report_live("회귀 권고 자동 적용 (Q-D1.<답>)")

    # 2- 정체 감지 — lessons.md / scoring/stagnation.py
    history_json = build_history(prev_scores, dim_history)
    stag = stagnation.detect(prev_scores, dim_history, threshold=0.999)
    lesson_pack = stagnation.build_lesson_pack(
        sprint=sprint,
        history=history_records,
        stagnation_report=stag,
        prior_attempts=prior_attempts,
        forbidden=forbidden_strategies,
        autonomy_level=user_autonomy_level,  # autonomy.md 페이즈 04 답
    )
    write `sprints/{sprint:02d}/lesson_pack.json`

    if stag["stagnation_overall"]:
        # 종합 정체 — 페이즈 06 부터 재시작
        snapshot_current_impl_to(`sprints/{sprint:02d}/snapshot/`)
        spawn_planner(force_replan=True, lesson_pack=lesson_pack)
        prev_scores = []          # 시계열 분기, 새 회차 시작
        dim_history = defaultdict(list)
        sprint = 1
        continue

    if stag["stagnant_dims"]:
        # 2-1 천정 검토 — 정체 차원이 NFR 측정 (latency/RPS) 이면
        # resource_ceiling.detect 로 추정 천정 도달 여부 판단 (resources.md)
        for dim in stag["stagnant_dims"]:
            if dim in {"p99_ms", "p95_ms", "rps", "latency_ms"}:
                ceiling = resource_ceiling.detect(
                    measurements=dim_history[dim],
                    current_threshold=nfr_thresholds[dim],
                    estimated_ceiling=resource_profile.estimated_ceiling[dim],
                    metric=dim,
                )
                if ceiling["near_ceiling"]:
                    # autonomy.md Q-D3 사전 위임 답 자동 적용 — 인터럽트 없음
                    policy_action = ceiling["policy_actions"][autonomy_policy["Q-D3"]]
                    apply_policy_action(policy_action, dim)
                    report_live(
                        f"천정 도달 ({ceiling['avg']:.1f}, 천정 "
                        f"{ceiling['ceiling_pct_actual']*100:.0f}%) → "
                        f"Q-D3.{autonomy_policy['Q-D3']} 자동 적용"
                    )
                    continue   # 다음 차원으로

        # 2-2 천정 아닌 정체 — 해당 모듈 통째 재작성 (preserve=false 강제)
        snapshot_current_impl_to(`sprints/{sprint:02d}/snapshot/`)
        for module in identify_modules_for_dims(stag["stagnant_dims"]):
            spawn_implementer(
                rewrite=True,            # preserve=false, fresh-impl
                target=module,
                lesson_pack=lesson_pack,
            )
        prior_attempts.append({
            "sprint": sprint,
            "rewrites": stag["stagnant_dims"],
        })

        # 같은 차원 3 회 연속 rewrite 도 정체면 autonomy.md Q-D4 자동 적용 — 인터럽트 없음
        if rewrite_streak(stag["stagnant_dims"], prior_attempts) >= 3:
            apply_q_d4_policy(autonomy_policy["Q-D4"])  # 1=06재시작 / 2=임계완화 / 3=정체수용
            report_live("3회 rewrite 정체 → Q-D4.<답> 자동 적용")

    else:
        # 일반 다음 스프린트 — extend (기존 코드 보강)
        failing_dims = [d for d, s in sub.items() if s < 0.95]
        spawn_implementer(
            failing=suite.failing_tests,
            failing_dims=failing_dims,
            lesson_pack=lesson_pack,    # 정체 아니어도 레슨 첨부
        )

    sprint += 1
    # 캡 없음 — 정체 누적은 Q-D4 사전 위임 답으로 자동 매핑 (인터럽트 없음)
```

핵심:

a- **레슨 전달 강제** — implementer/planner 호출에 `lesson_pack` (history + 이전 시도 + 금지 전략 + rewrite 룰) 항상 첨부. [`../conventions/lessons.md`](../conventions/lessons.md) 의 형식.
b- **정체 감지 자동** — `scoring/stagnation.py` 가 매 스프린트 종료 후 시계열 분석. 종합 정체 → 페이즈 06 재시작, 차원 정체 → 해당 모듈 통째 재작성.
c- **부분 수정 금지 강제** — 정체로 트리거된 rewrite 는 `preserve=false` 명시. 구현자가 기존 코드를 *보강* 하면 정체 지속.
d- **3 회 누적 rewrite 도 정체면 Q-D4 사전 위임 답** 자동 매핑 (인터럽트 없음, 자동 적용) — 무한 자율의 합리적 한계.

## 사용자 보고 (매 스프린트)

[`../conventions/timing.md`](../conventions/timing.md) 룰에 따라 매 스프린트 종료 시 한 줄 보고:

```
스프린트 NN 완료 — 점수 0.78 (직전 0.81). 누적 23분 11초. 현재 18:07:23. 다음 시도 진행.
```

## 성공 기준

a- 점수 ≥ 0.9 도달 — 테스트 비활성화·임계값 낮추기·rubric 편집 없이.
b- 모든 스프린트 보고서 존재.
c- 회귀 트리거가 있었던 스프린트는 `bisect.md` 가 동행, 자동 적용된 Q-D1 매핑 결과 기록 (인터럽트 없음).

## 금지된 안티 패턴 (테스터)

a- flaky 테스트 skip 처리 → 점수 부풀리기.
b- 커버리지 임계 낮추기.
c- "rubric 조정" — rubric 은 실행 동안 read-only.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).
