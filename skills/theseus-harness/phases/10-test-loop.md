# Phase 10 — 무한 스프린트 루프

## 한 줄 요약
**점수 ≥ 0.9 가 나올 때까지 무한 반복한다.** 회수 캡 없음. 점수가 직전 스프린트 대비 0.05 이상 떨어지면 즉시 페이즈 11(회귀 바이섹트) 로, 사용자 ack 없이는 추가 구현 금지.

## 매 스프린트 테스트 매트릭스

ⓐ 백엔드 단위 — Go `testing` (또는 사용자 명시 스택).
ⓑ 백엔드 통합 — `httptest` 로 어댑터 페이크.
ⓒ 프론트엔드 단위 — `bun test` + 컴포넌트 단위.
ⓓ 프론트엔드 통합 — fake 서비스로 컴포넌트 와이어드.
ⓔ E2E — Playwright 등 — happy-path + 에러 1 경로.
ⓕ 속성 기반 (직전 스프린트가 커버리지 얕음 플래그 시).

## 서브에이전트
[`../agents/tester.md`](../agents/tester.md). 테스터는 *실행* 만, 채점은 안 함 — 채점은 [`../scoring/score.py`](../scoring/score.py) 가 권위.

## 산출물 (스프린트별)
`sprints/NN/report.md` — [`../templates/sprint-report.template.md`](../templates/sprint-report.template.md), 헤더에 [`../conventions/timing.md`](../conventions/timing.md) 의 시간 메타 필수.
`sprints/NN/inputs.json` — `score.py` 입력.
`sprints/NN/bisect.md` — 회귀 트리거 시.

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
    score, sub = score.py(inputs, prior=prev_scores[-1] if prev_scores else None)
    write `sprints/{sprint:02d}/report.md` (timing header 포함)
    write `sprints/{sprint:02d}/inputs.json`
    prev_scores.append(score)
    for d, v in sub.items(): dim_history[d].append(v)
    report_to_user_with_timing(sprint, score, prev_scores)

    if score >= 0.999:
        return "pass"

    # ① 회귀 우선 — 페이즈 11 (lessons.md 의 정체와 별 트리거)
    if len(prev_scores) >= 2 and score < prev_scores[-2] - 0.05:
        run_phase_11 → `sprints/{sprint:02d}/bisect.md`
        ack_per_autonomy_level()

    # ② 정체 감지 — lessons.md / scoring/stagnation.py
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
        # ②-1 천정 검토 — 정체 차원이 NFR 측정 (latency/RPS) 이면
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
                    # 자동 조정 권고 — 사용자 ack 필수 (autonomy.md 의 임계 변경)
                    ack = AskUserQuestion(
                        f"리소스 천정 도달: 측정 {ceiling['avg']} 이 추정 천정의 "
                        f"{ceiling['ceiling_pct_actual']*100:.0f}%. 임계 조정?",
                        options=ceiling["user_options"],
                    )
                    apply_user_choice(ack, dim)
                    continue   # 다음 차원으로

        # ②-2 천정 아닌 정체 — 해당 모듈 통째 재작성 (preserve=false 강제)
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

        # 같은 차원 3 회 연속 rewrite 도 정체면 사용자 ack 강제
        if rewrite_streak(stag["stagnant_dims"], prior_attempts) >= 3:
            ask_user_per_lessons_md_section_3회_초과()

    else:
        # 일반 다음 스프린트 — extend (기존 코드 보강)
        failing_dims = [d for d, s in sub.items() if s < 0.95]
        spawn_implementer(
            failing=suite.failing_tests,
            failing_dims=failing_dims,
            lesson_pack=lesson_pack,    # 정체 아니어도 레슨 첨부
        )

    sprint += 1
    # 캡 없음 — 단 정체 누적은 사용자 ack 로 차단
```

핵심:

ⓐ **레슨 전달 강제** — implementer/planner 호출에 `lesson_pack` (history + 이전 시도 + 금지 전략 + rewrite 룰) 항상 첨부. [`../conventions/lessons.md`](../conventions/lessons.md) 의 형식.
ⓑ **정체 감지 자동** — `scoring/stagnation.py` 가 매 스프린트 종료 후 시계열 분석. 종합 정체 → 페이즈 06 재시작, 차원 정체 → 해당 모듈 통째 재작성.
ⓒ **부분 수정 금지 강제** — 정체로 트리거된 rewrite 는 `preserve=false` 명시. 구현자가 기존 코드를 *보강* 하면 정체 지속.
ⓓ **3 회 누적 rewrite 도 정체면 사용자 ack** — 자율 무한 시도 차단.

## 사용자 보고 (매 스프린트)

[`../conventions/timing.md`](../conventions/timing.md) 룰에 따라 매 스프린트 종료 시 한 줄 보고:

```
스프린트 NN 완료 — 점수 0.78 (직전 0.81). 누적 23분 11초. 현재 18:07:23. 다음 시도 진행.
```

## 성공 기준

ⓐ 점수 ≥ 0.9 도달 — 테스트 비활성화·임계값 낮추기·rubric 편집 없이.
ⓑ 모든 스프린트 보고서 존재.
ⓒ 회귀 트리거가 있었던 스프린트는 `bisect.md` 가 동행, 사용자 ack 기록.

## 금지된 안티 패턴 (테스터)

ⓐ flaky 테스트 skip 처리 → 점수 부풀리기.
ⓑ 커버리지 임계 낮추기.
ⓒ "rubric 조정" — rubric 은 실행 동안 read-only.
