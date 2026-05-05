---
id: analytical-bound-cross-validation
category: quality
applies-to-phases: '[09,11]'
applies-to-grades: '[all]'
trigger-when: 'analytical bound 가능'
indexed-in: conventions/INDEX.md
---

# Analytical Bound Cross-Validation — closed-form 상한 vs simulated baseline

## 한 줄 요약

**페이즈 09 derived gate 에 *closed-form bound* 자동 도출 + simulated baseline ratio 검증 의무.** v01_cold 가 외부 reference 0 으로 본 세션 v099 의 payload=50 잘못된 가정을 자력 발견한 패턴을 룰화. simulated 가 분석적 상한의 *80%~100% 범위 외* 면 *입력 데이터 가정 재검증* 자동 트리거.

## 1. 결손 진단

기존 v0.9.6 [`nfr-derivation.md`](nfr-derivation.md) 의 derived gate Q7 (accuracy) 가 *측정 protocol* 만 명시 — 정확한 분석적 상한 룰 미정. 따라서 simulated baseline 의 *절대값* 정합성 검증 없음.

v01_cold (v0.9.9) 자체 적용 결과 :
- loader-bound = 60/4.5 × 100t × 2 loaders = **2666 t/h**
- crusher-bound = 60/3.5 × 100t = **1714 t/h**
- observed baseline = **1483 t/h**
- ratio = 1483 / 1714 = **86.5%** ← 임계 80% 통과 → sanity 정합

본 세션 v099 (v0.9.7-9 carry) 결과 :
- payload 가정 = 50t (임의)
- loader-bound = 60/4.5 × 50 × 2 = **1333 t/h**
- crusher-bound = 60/3.5 × 50 = **857 t/h**
- observed baseline = **626.5 t/h**
- ratio = 626.5 / 857 = **73.1%** ← 임계 80% 미달 → 가정 재검증 트리거 *필요*

→ v099 가 본 컨벤션 적용 시 *payload=50 잘못* 자동 발견. enforcement 부재로 catch 못함.

## 2. 운영 룰

### Step 1 — closed-form bound 자동 도출

페이즈 09 진입 시, 페이즈 06 plan 의 도메인 명사 + 페이즈 04 NFR 답에서 *입력 파라미터* 추출 :

```python
def derive_analytical_bounds(plan: Plan, data: BenchData) -> dict:
    bounds = {}
    if has_resource(plan, "loader"):
        rate_per_min = 60 / data["loader_mean_min"]
        bounds["loader_bound"] = rate_per_min * data["payload"] * data["n_loaders"]
    if has_resource(plan, "crusher") or has_resource(plan, "sink"):
        bounds["crusher_bound"] = (60 / data["crusher_mean_min"]) * data["payload"]
    if has_constraint(plan, "cap_1_segment"):
        # 단일 lane bidirectional → 양방향 통과율 50%
        bounds["ramp_bound"] = (60 / data["ramp_traverse_min"]) * data["payload"] * 0.5
    return bounds
```

도메인 무관 — *resource type* 단위로 자동.

### Step 2 — simulated vs bound ratio 검증

```python
def gate_analytical_bound(simulated_baseline: float, bounds: dict) -> tuple[bool, str]:
    binding_bound = min(bounds.values())
    ratio = simulated_baseline / binding_bound
    if 0.80 <= ratio <= 1.00:
        return True, f"baseline {simulated_baseline:.1f} = {ratio*100:.1f}% of binding bound {binding_bound:.1f} ({min_key(bounds)})"
    if ratio < 0.80:
        return False, f"baseline UNDER-ESTIMATE: {ratio*100:.1f}% of bound — 입력 가정 재검증 (특히 payload / capacity / service-time)"
    if ratio > 1.00:
        return False, f"baseline OVER-ESTIMATE: {ratio*100:.1f}% of bound — 모델이 물리 위반 (e.g. per-direction 인플레)"
```

### Step 3 — fail policy

`fail_policy: trigger_input_assumption_reverification` (auto-fix-trigger 의 specialized variant).

페이즈 04 의 *입력 파라미터* (예: payload / capacity) 답안 재확정 — 페이즈 04 의 NFR-V 답안 frontmatter 의 `confirmed_at` timestamp 갱신 또는 ground-truth source (bench data CSV 등) 직접 인용 의무.

재확정 후 페이즈 08 impl 부분 재진입 + 본 게이트 재측정.

## 3. v0.9.6 nfr-derivation 와의 관계

본 컨벤션은 *Q7 accuracy* derived gate 의 *concrete protocol*. nfr-derivation 의 Q7 은 *seed* (verification 후보 abstract), 본 컨벤션이 *그 중 하나* (analytical bound) 의 운영 형태. 다른 verification (ground-truth 비교 / confusion matrix) 도 추가 활성 가능.

## 4. 그레이드별 활성

| Grade | 활성 |
|---|:-:|
| G2 Simple | n/a (single-attempt) |
| G3 Standard | optional (외부 채점 없을 시) |
| **G4 Complex** | **의무** (외부 evaluator 작업) |
| G5 Critical | 의무 + tighter 임계 (≥90% AND ≤100%) |

## 5. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- closed-form bound = resource type 단위 (loader / crusher / cap-1 segment), 도메인 X.
b- ratio 임계 (80%~100%) = generic, 도메인 X.
c- fail policy = 입력 가정 재검증 trigger, 도메인 X.

## 6. 안티 패턴

a- **bound 와 simulated 가 *같은 가정* 으로 도출** — circular validation. bound 는 *입력 파라미터 (raw data)*, simulated 는 *코드 결과*. 두 입력 불일치 시 mismatch 자동.
b- **ratio 임계 임의 조정** — 80% 미만에서 의도적으로 60% 임계로 낮추면 잘못된 가정 catch 못함. self_lint C-AB-RATIO 가 임계 ≥ 80% 강제.
c- **fail 후 *입력 재검증 없이 코드만 수정*** — 본질 위반. fail policy 가 *입력 답안 재확정* 명시 의무 (페이즈 04 답 timestamp 갱신).

## 7. 자기 검증 (메타)

본 컨벤션 자체에 적용 — 가정 (payload, capacity, service-time) 이 bench data CSV 와 일치하는지 self_lint C-AB-DATA 검증. 본 컨벤션이 본인의 적용 회차 (v0.9.12 첫 적용) 에서 실 결과 박힘.
