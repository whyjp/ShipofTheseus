---
id: budget-saturation-loop
category: sprint
applies-to-phases: '[10]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Stop-Policy 컨벤션 (`budget-saturation-loop`) — 값 기반 정지 (구 budget 80% 강제 전면 재작성, 설계 B2 §2.2/F5-1)

## 한 줄 요약

**phase 10 sprint loop 의 정지 권위는 `pipeline.manifest.json` 의 `stop_policy` 블록 단일 소스다.** 정지 = (i) 게이트 pass(`meta_audit` verdict) AND (ii) 무회귀(`sprint.regression`) AND (iii) plateau(직전 `plateau_window` 회 score delta < `plateau_eps`) — OR budget ≥ `budget_hard_cap`(0.95, 무조건 정지). **점수 절대값은 어디서도 게이트가 아니다.** 80% floor 강제와 `EARLY_STOP_VIOLATION` 라벨은 폐지 — 정직한 plateau 는 벌이 아니라 정지 신호다.

## 1. 폐지 이력

구판(v0.9.15)의 "budget 사용률 ≥ 80% 강제"(임계 도달 무관 sprint 강제 추가)는 (a) 정직한 1st-pass PASS 를 "위반"으로 라벨링해 세리머니 sprint 를 강제했고, (b) 도달 불가 임계 0.999/0.99999 와 결합해 모든 run 이 budget 80~95% 를 무조건 소각했다(perverse incentive — 설계 B2 §2.2/§2.4). 본 개정은 그 강제를 삭제하고 정지를 `stop_policy`(값 기반)로 교체한다.

## 2. 정지 조건 (manifest `stop_policy` 인용)

```
종료 = gate(meta_audit verdict pass) AND no_regression(sprint.regression pass)
       AND (plateau(delta < plateau_eps, plateau_window[grade] 회 연속)
            OR budget_used_ratio >= budget_hard_cap(0.95))
```

- **gate / no_regression** — `run_gate.py` + `kernel/meta_audit.py` 가 값으로 산출(B1/B2a 배선, 본 컨벤션 무수정).
- **plateau** — `scoring/stagnation.py` 가 delta 만으로 판정(절대 점수 무관, 의미 반전). plateau 는 *정지 신호*이지 벌이 아니다.
- **budget_hard_cap 0.95** — 상한(over-budget 방지)이지 소진 의무가 아니다. 80% floor 는 폐지.

## 3. Lesson type = content depth (유지)

정지 전 추가 sprint 의 lesson 은 *content depth* 우선 — enforcement structure 추가는 self-estimate 효과 0. [`sprint-narrative.md`](sprint-narrative.md) §2 delta tracking 이 이 라벨의 정직성을 사후 검증한다.

| Lesson type | 효과 |
|---|---|
| content depth / evidence / integrated insight | 개선 유효 |
| enforcement structure | self-estimate +0 (이미 PASS) |

## 4. Q-D-BUDGET-MODE (default 반전)

페이즈 04 Q-D 답:
1. **converge-on-evidence (default)** — `stop_policy` 3조건 신호 기반 정지. budget 강제 소진 없음.
2. **Saturation (opt-in)** — 사용자 명시 ack 시에만 budget ≥ 80% 소진을 목표로 sprint 계속(능력 보존).
3. Custom budget cap (사용자 명시).

## 5. Lesson source 통합

[`evidence-driven-sprint-planning.md`](evidence-driven-sprint-planning.md) 의 `evidence_missing` 이 다음 sprint lesson source 로 자동 매핑 — plateau 미도달 + evidence 결손 시 다음 sprint 진입(§2 와 합성).

## 6. 안티 패턴

a- plateau 를 "정체 문제"로 벌하고 sprint 강제 — 폐지된 구 룰. plateau 는 정지 신호다.
b- 추가 sprint 의 lesson 이 enforcement — content depth 의무는 유지.
c- budget 95% 초과 — over-budget, 여전히 회피 대상.
d- stop_policy 우회한 별도 임계 판정 도입 — 종료 권위는 manifest 1곳(드리프트 재발 차단).
