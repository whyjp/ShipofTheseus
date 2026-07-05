# 채점 rubric

## 한 줄 요약
**정지 권위는 manifest `stop_policy`(설계 B2 §2.2) — 절대 총점 임계(구 0.999)는 게이트가 아니다.** 점수는 보고용 측정값(6 차원 가중 평균, 각 차원 `[0, 1]`)이며, 도달 불가 임계를 종료 조건으로 쓰면 인플레이션 유인이 생긴다는 것이 판명됐다(perverse incentive). **DIP 위반 = `scoring.solid` 차원 게이트 FAIL + 총점 hard cap 0.6 (이중 방어) — 이 cap 은 stop_policy 와 무관하게 존치.** 1 차 경로(커널)에서 DIP 위반은 solid 차원을 만점이 아니라 *게이트 FAIL* 로 만들고, 집계(`aggregate_scores`)가 총점을 다시 0.6 으로 눌러 어떤 다른 차원이 만점이어도 이 cap 을 강제한다. 가중치 합은 1.0. `score.py --threshold` 는 하위호환 보고 필드(`passes_threshold`)용으로만 남으며 exit code 를 좌우하지 않는다(§2.3).

## ⚠️ 0.999 / 0.99999 는 게이트가 아니다 — 폐지 이력 + SLO 오해 방지

과거 버전은 총점 ≥ 0.999(사용자 프로젝트)/0.99999(자기 평가)를 종료 게이트로 썼다. 이 표기는 SLO(Service Level Objective) 가용성 기호와 *형태만* 같을 뿐 의미가 달랐고, 게이트로도 도달 불가능해 perverse incentive(점수 인플레이션 유인 + budget 소각 유인)를 낳았다(설계 B2 §2.2). 두 자리 모두 폐지 — 정지 판정은 `stop_policy`(gate AND no_regression AND (plateau OR budget≥95%)) 로 이관됐다.

| 구 표기 | 구 의미 | 현재 |
| ---- | -------- | ------------- |
| 0.999 (사용자 프로젝트) | 6 차원 가중평균 ≥ 0.999 + hard cap 미적용 + DIP 위반 부재 | 폐지 — `stop_policy`(manifest) 가 정지 판정, 점수는 보고 전용 |
| 0.99999 (자기 평가, self_lint --score) | self_lint 전건 pass + pytest 전건 pass + sample_score 1.0 의 가중 평균 | 폐지 — 판정은 `all_ok`(lint 전건 pass) boolean, self_score 는 보고 전용 |
| 0.05 (회귀 임계) | 직전 스프린트 대비 점수 하락 폭 — `score(N) < score(N-1) - 0.05` 면 페이즈 11 발동 | 존치 — 절대 임계 아닌 delta 게이트라 perverse incentive 대상 아님 |

절대 점수를 *SLO* 로 오인(예: "1000 회 실행 중 1 회만 실패")하면 안 된다는 원 취지는 유효하다 — 본 점수는 *단일 산출물의 정합 채점* 이지 *반복 사건 분포* 의 신뢰 통계가 아니다.

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
solid (1차 경로) = DIP 위반이면 scoring.solid CheckSpec 게이트 FAIL (차원 자체가 통과 못 함)
                 아니면 solid_raw
solid (deprecated shim) = min(solid_raw, 0.5) if DIP 위반  # score.py --inputs 하위호환 경로만

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

a- `.only` / 정당화 없는 `.skip` 테스트 → 총점 cap 0.5.
b- 프로덕션 코드에 `console.log` / `fmt.Println` 디버그 잔재 → cap 0.85.
c- Lint 에러 → cap 0.85.
d- Type 에러 → cap 0.7.
e- DIP 위반 → cap 0.6 (위 SOLID 섹션과 동일, hard cap 으로 재차 강제).

## 회귀 임계

`score(N) < score(N-1) - 0.05` → 페이즈 11 (회귀 바이섹트) 자동 트리거. 임계값은 `score.py --regression-threshold` 로 튜닝 가능 (기본 0.05).

## rubric 이 *아닌* 것

a- 코드 미감 측정기.
b- 실행 중 조정 가능한 노브 — read-only.
c- 사람의 아키텍처 판단 대체 — 0.95 점에 나쁜 아키텍처면 여전히 나쁜 결과. 본 rubric 은 *실행* 실패를 잡고, 페이즈 05 (비평) 가 *방향* 실패를 잡는다.

## 왜 DIP 만 hard cap 인가

DIP 가 살아 있으면 나머지 SOLID 위반은 국지적 수술로 고칠 수 있다. DIP 가 깨지면 테스트 가능성이 무너지고 후속 위반들이 누적된다 — 한 위반이 다음 위반을 부르는 구조. 그래서 DIP 위반만 단독으로 임계 미달을 강제한다. [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) 의 "가장 중요한 원칙" 절 참조.

**구현 정합(WP4a)**: 1 차 경로에서 이 강제는 두 층으로 실현된다 — (1) `scoring.solid` CheckSpec 이 `dip_violation == 0` assertion 으로 DIP 위반 시 solid 차원을 *게이트 FAIL* 시키고(커널 법칙4; `checks/scoring.solid.json`), (2) `aggregate_scores(dim_values, dip_violation)` 가 총점을 `min(raw, 0.6)` 으로 다시 누른다(`score.py`). 코드와 본 문서가 어긋나지 않게 두 지점을 함께 유지한다. deprecated `score.py --inputs` shim 은 여전히 `min(solid_raw, 0.5)` sub-score cap + 총점 0.6 cap 을 쓰지만, 이는 자기 신고 하위호환 경로일 뿐 1 차 경로가 아니다.
