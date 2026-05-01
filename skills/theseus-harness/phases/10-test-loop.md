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
prev_score = None
while True:
    suite = run_test_matrix()
    inputs = build_score_inputs(suite, gate_results)
    score, sub = score.py(inputs, prior=prev_score)
    write `sprints/{sprint:02d}/report.md` (timing header 포함)
    write `sprints/{sprint:02d}/inputs.json`
    report_to_user_with_timing(sprint, score, prev_score)

    if score >= 0.9:
        return "pass"

    if prev_score is not None and score < prev_score - 0.05:
        run_phase_11 → `sprints/{sprint:02d}/bisect.md`
        ack = AskUserQuestion(권고: revert | re-architect | accept | 정지)
        if ack == 정지: halt

    failing_dims = [d for d, s in sub.items() if s < 0.9]
    spawn_implementer(failing_dims, suite.failing_tests)
    prev_score = score
    sprint += 1
    # 캡 없음 — 무한 루프
```

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
