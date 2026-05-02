# Phase 11 — 회귀 바이섹트

## 한 줄 요약
**점수가 0.05 이상 하락한 스프린트가 발생하면 *추가 구현 전* 에 원인 판자를 찾는다.** 테세우스의 배에 잘못된 판자가 박혀 있다 — 더 박기 전에 빼낸다. 분석가는 진단만, 코드 수정 금지.

## 트리거

페이즈 10 의 루프가 `score(N) < score(N-1) - 0.05` 일 때 자동 호출. 수동: `score.py --bisect`.

## 입력
- `sprints/N-1/report.md` (마지막 양호)
- `sprints/N/report.md` (회귀)
- 두 체크포인트 사이의 `git diff`
- 스프린트 N 의 실패 테스트 목록 + 에러 메시지

## 서브에이전트
[`../agents/regression-analyst.md`](../agents/regression-analyst.md). **코드 편집 금지** — 진단만.

## 산출물
`sprints/NN/bisect.md` — [`../conventions/timing.md`](../conventions/timing.md) 헤더 + 다음:

ⓐ **무엇이 떨어졌나** — 어떤 sub-score 가 얼마만큼.
ⓑ **무엇이 변했나** — diff 요약 (파일·함수·라인).
ⓒ **주 가설** — 함수/라인 수준에서 단일 후보. 실패 테스트 1개 이상이 이 가설과 정합.
ⓓ **반대 가설** — 최소 1개, 왜 덜 가능성 있는지.
ⓔ **권고** — 다음 셋 중 하나:
  ① `revert <commit-or-file>` — 외과적 되돌림.
  ② `re-architect <module>` — 더 깊은 SOLID 위반의 증상 → 그 모듈에 대해 페이즈 06 부터 재실행.
  ③ `accept` — 회귀가 실은 의도된 변화 (제약이 중간에 바뀜) — 사용자가 명시 확인.

## 지휘자 후속 — 사전 위임 자동 적용 (인터럽트 없음)

페이즈 04 의 [`../conventions/autonomy.md`](../conventions/autonomy.md) Q-D1 답에 따라 회귀 권고를 *자동 적용*. 인터뷰 종료 후 사용자에게 추가 ack 호출 절대 없음:

ⓐ Q-D1 답 = `1` (모든 권고 자동) → bisect 의 `recommendation` (revert / re-architect / accept) 그대로 자동 적용.
ⓑ Q-D1 답 = `2` (revert 만 자동) → recommendation 이 revert 면 자동, 그 외는 lessons.md 의 정체로 판정해 Q-D4 매핑.
ⓒ Q-D1 답 = `3` (모두 정지) → 본 스킬 의도 위반 — 페이즈 04 에서 비권장으로 표시, 그래도 사용자가 선택했다면 정지.

[`../conventions/timing.md`](../conventions/timing.md) 의 라이브 보고에 한 줄:

```
스프린트 NN 회귀 (점수 0.92 → 0.78) → bisect 권고 revert (path/a.go:42) → Q-D1.1 자동 적용. 누적 1시간 12분.
```

## 왜 필요한가

우로보로스의 두 번째 자기 무는 지점이며, 회귀 직후 추가 구현 차단을 위한 강제 게이트. 없으면 재귀 하네스는 회귀를 더 많은 코드로 "고치려" 하고, 스프린트마다 누적 악화로 들어간다.

## 성공 기준

ⓐ `bisect.md` 가 특정 commit/파일/함수를 명시.
ⓑ 사전 위임 Q-D1 답이 자동 적용되어 다음 스프린트 진행 — 인터럽트 없음 ([`../conventions/autonomy.md`](../conventions/autonomy.md) 의 인터뷰 후 인터럽트 0 룰).
