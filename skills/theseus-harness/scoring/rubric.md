# 채점 rubric

## 한 줄 요약
**총점 ≥ 0.999 일 때 하네스가 종료된다.** 자율적으로 최대 결과를 지향하기 위한 빡빡한 임계. 점수는 6 차원의 가중 평균이며, 각 차원은 `[0, 1]`. **DIP 위반은 단독 hard cap 0.6** — 다른 차원이 만점이어도 DIP 가 깨지면 임계 미달. 가중치 합은 1.0. 임계는 `score.py --threshold` 로 튜닝 가능하지만, 0.999 미만 임계 사용은 사용자 명시 동의 필요.

## ⚠️ 0.999 / 0.99999 의 의미 — SLO 가용성이 아니다

본 임계 표기는 *수치 형태* 가 SLO(Service Level Objective) 의 가용성 기호와 같지만, **의미는 완전히 다르다.** 외부 사용자가 "이 시스템 99.999% 신뢰 가능" 으로 오해하지 않도록 본 절을 README/SKILL.md 가 cross-link.

| 표기 | 진짜 의미 | SLO 와 다른 점 |
| ---- | -------- | ------------- |
| **0.999** (사용자 프로젝트 임계) | 6 차원 가중평균 ≥ 0.999 + 5 hard cap 미적용 + DIP 위반 부재 | 가용성·실패율과 무관. *한 산출물의 정합 점수* 임계. |
| **0.99999** (자기 평가 임계, BOOTSTRAP.md) | self_lint 34/34 pass + pytest 90+/90+ + sample_score 1.0 의 가중 평균 | 본 저장소의 *마크다운 텍스트 인덱스 정합성* 측정값. LLM 행동 정확도가 아님. |
| **0.05** (회귀 임계) | 직전 스프린트 대비 점수 하락 폭 — `score(N) < score(N-1) - 0.05` 면 페이즈 11 발동 | 무관. 단순 차분 임계. |

본 표기를 *SLO* 로 오인 (예: "1000 회 실행 중 1 회만 실패") 하면 안 된다. 본 점수는 *단일 산출물의 정합 채점* — SLO 는 *반복 사건 분포* 의 신뢰 통계.

## 차원·가중치

| 차원 | 가중치 | 무엇을 본다 |
| ---- | ----: | ---------- |
| `correctness` | 0.25 | 테스트 통과율 × 의도 일치도 |
| `scope_fit` | 0.10 | 변경 파일 중 TODO 매핑 비율 |
| `solid` | 0.20 | 모듈별 SOLID 통과 비율, **DIP 가중 강화** |
| `coverage` | 0.15 | 분기 커버리지, BE/FE 의 `min` |
| `fe_be_parity` | 0.10 | 양쪽 테스트 깊이 동등성 |
| `e2e_pass` | 0.20 | E2E 통과율 |

## sub-score 공식

```
correctness   = test_pass_rate × intent_fidelity
                intent_fidelity ∈ {1.0 (Gate 1 pass), 0.7 (remediable), 0.0 (halt)}

scope_fit     = files_mapped_to_todos / files_touched

solid_raw     = modules_passing_solid / modules_total
solid         = solid_raw if no DIP violation
                else min(solid_raw, 0.5)              # DIP 위반 발견 시 sub-score 0.5 cap

coverage      = min(be_coverage, fe_coverage)         # avg 가 아닌 min — 패리티 강제

fe_be_parity  = 1.0 (full {unit, integration, e2e})
              | 0.7 (한쪽이 한 단 누락)
              | 0.4 (한쪽이 두 단 누락)
              | 0.0 (한쪽이 smoke 만)
              | "n/a" (단일 사이드 기능)

e2e_pass      = e2e_passing / e2e_total
```

## 총점

```
score_raw = Σ (weight_i × sub_score_i)  for active dimensions
            (active = sub_score 가 "n/a" 가 아닌 차원)
            (가중치는 active 셋 위에서 재정규화)

# DIP 단독 hard cap
score = min(score_raw, 0.6)  if DIP 위반 발견
      = score_raw            otherwise
```

## 점수와 무관한 hard cap

ⓐ `.only` / 정당화 없는 `.skip` 테스트 → 총점 cap 0.5.
ⓑ 프로덕션 코드에 `console.log` / `fmt.Println` 디버그 잔재 → cap 0.85.
ⓒ Lint 에러 → cap 0.85.
ⓓ Type 에러 → cap 0.7.
ⓔ DIP 위반 → cap 0.6 (위 SOLID 섹션과 동일, hard cap 으로 재차 강제).

## 회귀 임계

`score(N) < score(N-1) - 0.05` → 페이즈 11 (회귀 바이섹트) 자동 트리거. 임계값은 `score.py --regression-threshold` 로 튜닝 가능 (기본 0.05).

## rubric 이 *아닌* 것

ⓐ 코드 미감 측정기.
ⓑ 실행 중 조정 가능한 노브 — read-only.
ⓒ 사람의 아키텍처 판단 대체 — 0.95 점에 나쁜 아키텍처면 여전히 나쁜 결과. 본 rubric 은 *실행* 실패를 잡고, 페이즈 05 (비평) 가 *방향* 실패를 잡는다.

## 왜 DIP 만 hard cap 인가

DIP 가 살아 있으면 나머지 SOLID 위반은 국지적 수술로 고칠 수 있다. DIP 가 깨지면 테스트 가능성이 무너지고 후속 위반들이 누적된다 — 한 위반이 다음 위반을 부르는 구조. 그래서 DIP 위반만 단독으로 임계 미달을 강제한다. [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) 의 "가장 중요한 원칙" 절 참조.
