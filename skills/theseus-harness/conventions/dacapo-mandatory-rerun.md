---
id: dacapo-mandatory-rerun
category: tournament
applies-to-phases: '[06,08]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'step D AND pass'
indexed-in: conventions/INDEX.md
---

# Da Capo mandatory rerun (`dacapo-mandatory-rerun`) — advisory 강등 (구 "무조건 ≥1 rerun", 설계 B2 §2.2-3/§2.3)

## 한 줄 요약

**구판은 winner_score 가 임계 이상이라도 무조건 ≥1 rerun(`rerun_count >= 1`, "예외 0")을 강제했다 — 신호(개선 여지) 유무와 무관한 세리머니 rerun 이었다. 본 개정은 advisory 로 강등한다: rerun 은 직전 라운드 대비 winner delta 가 관측될 때 하는 것이지 의무가 아니다.**

## 재설정 (§2.2-3)

Da Capo rerun 결정 = "직전 라운드 대비 winner delta ≥ eps 인 동안"(개선이 실측되는 동안 계속) + budget cap — `stop_policy`(budget-saturation-loop.md)와 동일 구조. `mandatory_first_rerun_satisfied` frontmatter 필드는 하위호환으로 남기되(Step F/Step G 경로 기록용), 값이 없어도 promote 를 막지 않는다 — 세리머니 rerun 의무(`rerun_count >= 1`, "예외 0") 자체가 강등 대상이다.

## Step F / Step G (능력 존치)

신호(delta)가 있을 때 rerun 하면: Step F(lesson 도출) → Step G(anonymized prev winner + width-1 fresh) → Step A 재진입. 절차는 그대로 쓸 수 있다 — 무조건 호출 의무만 해제.

## self_lint 검증 이력 (참고)

구 개별 룰은 B3 삭제 — advisory 강등과 모순되는 stale mandate 핀이었다.

## 안티 패턴 (재정정)

a- 개선 신호(delta) 없이 rerun 강행 — 세리머니, 폐지 대상 그 자체.
b- delta 가 관측되는데 rerun 을 건너뜀 — 여전히 손해(polishing 기회 상실), 권장 사항 위반.

## 호환성

- [`budget-saturation-loop.md`](budget-saturation-loop.md) — delta/plateau 룰이 rerun 여부의 신호 소스.
- [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) — Step D 분기(advisory).
- [`tournament-blind-rerun.md`](tournament-blind-rerun.md) — anonymized prev winner 절차는 그대로.
