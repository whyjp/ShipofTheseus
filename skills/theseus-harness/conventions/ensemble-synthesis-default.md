# Ensemble Synthesis Default — G4+ tournament 결과의 algorithmic union default 화

## 한 줄 요약

**G4+ multiverse tournament 의 *default 결과 = ensemble (algorithmic union)*, single-winner 는 opt-out.** v0.9.10 [`tournament-blind-rerun.md`](tournament-blind-rerun.md) 의 union 옵션을 default 로 승격. 각 universe 의 strongest sub-component 만 선별 합성 → tournament 1위 + N 위 의 strength 모두 채택.

## 1. 결손 진단

v0.9.10 [`competition.md`](competition.md) + [`tournament-blind-rerun.md`](tournament-blind-rerun.md) 의 default = single winner. union = 옵션. 결과 :
- v01_cold / v091_cold01 / 본 세션 cold/v099 모두 single-winner 채택
- 패배 universe 의 *부분 강점* 채택 0 — bench reviewer 의 차원별 1위 합산 시 single-winner 한계
- 점수 ceiling 97 plateau 의 일부 원인 = ensemble 미적용

## 2. 운영 룰

### Step 1 — sub-score per dimension (tournament 입력)

각 universe 의 차원별 sub-score (bench 8 차원 또는 generic 차원) :

```yaml
universe_sub_scores:
  U1:
    Conceptual: 18
    Sim_correctness: 19  ← 차원별 1위
    Code_quality: 9
    ...
  U2:
    Conceptual: 19      ← 차원별 1위
    Sim_correctness: 18
    Code_quality: 10    ← 차원별 1위
    ...
  U3:
    Conceptual: 18
    Sim_correctness: 18
    Code_quality: 9
    ...
```

### Step 2 — Ensemble winner per dimension

각 차원별 1위 universe 의 *해당 sub-component* 만 선별 :

```python
def ensemble_synthesis(universes: list[Universe], dimensions: list[str]) -> Ensemble:
    ensemble = {}
    for dim in dimensions:
        winner = max(universes, key=lambda u: u.sub_score(dim))
        ensemble[dim] = winner.sub_component(dim)  # 코드 / narrative / 테스트 등 dimension-specific
    return ensemble
```

각 dimension 의 sub-component = :
- Conceptual = conceptual_model.md 의 해당 절
- Sim_correctness = mine_sim/ 의 해당 모듈 (예: U1 의 dispatcher / U2 의 resource model)
- Code_quality = test 패턴 + DIP 구조
- Results = operational_recommendations.txt
- ...

### Step 3 — Sub-component merge (코드 차원)

코드 차원의 sub-component 합성 = [`interface-first-parallel-impl.md`](interface-first-parallel-impl.md) 의 인터페이스 룰 활용 :

a- 각 universe 가 동일 인터페이스 기준 → sub-component 교체 자유.
b- merge 충돌 (둘 다 dispatcher 정의 등) → dimension-별 winner 의 sub-component 채택.
c- 통합 테스트 = `interface-first-parallel-impl.md §3` 의 integration adapter test.

### Step 4 — Ensemble candidate 의 검증

ensemble 결과 = U_ensemble 신규 universe (코드 디렉터리 `code/universe-ensemble/`).

ensemble 의 자체 sub-score 측정 → 단일 universe 1위 와 비교 :

| ensemble 결과 | 채택 |
|---|---|
| U_ensemble sub-score > 1위 universe sub-score | **ensemble 채택** (default) |
| U_ensemble sub-score == 1위 universe (gap < 1pt) | ensemble (opt-out 명시 시 single-winner) |
| U_ensemble sub-score < 1위 universe | **single-winner 채택** (ensemble 합성이 sub-component 충돌로 약화 → 본 케이스에서 ensemble 적합 X) |

## 3. opt-out 룰

페이즈 04 Q-D 답안 에 `Q-D-ensemble = single-winner` 명시 시 ensemble skip. default = `Q-D-ensemble = algorithmic-union`.

## 4. 그레이드별 활성

| Grade | ensemble 활성 |
|---|:-:|
| G2 Simple | n/a (single universe) |
| G3 Standard | optional |
| **G4 Complex** | **default ON** |
| G5 Critical | default ON + ensemble 자체에 대한 blind rerun (v0.9.10 tournament-blind-rerun §3 algorithmic union 옵션 합성) |

## 5. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- sub-score 차원 = bench 또는 generic 8 차원, 도메인 X.
b- sub-component 매핑 = artifact 단위 (file path / 절), 도메인 X.
c- merge 룰 = interface-first-parallel-impl.md 의 일반 인터페이스 패턴 활용.

## 6. 안티 패턴

a- **ensemble 의 cherry-picking** — 약한 sub-component 도 winner 의 것으로 채택 (모든 dimension 같은 universe). v0.9.10 [`tournament-blind-rerun.md`](tournament-blind-rerun.md) §6-d 의 *origin 분포 ≥ 0.2 each* 검증 carry — ensemble 도 적용.
b- **ensemble 합성 후 코드 결합 검증 누락** — interface 정합 검증 의무 (interface-first-parallel-impl §3).
c- **ensemble vs single-winner 비교 단계 skip** — §2 step 4 의 비교 의무. ensemble 무조건 채택 0.

## 7. 효과 추정

bench 8 차원 × 3 universe 시 :
- single-winner 채택 = 1위 universe 의 모든 차원 합 = 보통 90-94 합
- ensemble (각 차원 1위 합) = 보통 +2-4pt (1위 universe 가 모든 차원에서 1위가 아닌 한)

97 plateau → 99-100 시도 가능.

## 8. 자기 검증

본 컨벤션 자체 = single artifact (Markdown). ensemble 적용 X. 단 본 컨벤션이 *기존 컨벤션의 sub-component* 합성 :
- v0.9.10 tournament-blind-rerun §3 의 union 옵션 = 본 컨벤션의 default 화의 *원본 sub-component*
- v0.9.11 interface-first-parallel-impl §3 의 integration test = 본 컨벤션의 *합성 검증 sub-component*
- v0.9.12 multiverse-impl-fan-out §2 의 universe 코드 fan-out = 본 컨벤션의 *입력 sub-component*

3 컨벤션의 sub-component 합성 = 본 컨벤션. 메타-ensemble 시연.

## 9. v0.9.16 sprint-10 — 차이집합 합성 추가 ([`cross-universe-lesson-distillation.md`](cross-universe-lesson-distillation.md))

본 컨벤션이 *합집합* (우승 + 다른 우주의 강점) 만 정의. v0.9.16 [`cross-universe-lesson-distillation.md`](cross-universe-lesson-distillation.md) 가 *차이집합* (패배 우주의 약점 → 회피) 추가 — ensemble 의 union 차원이 *합집합 + 교집합 + 차이집합* 3 차원 합성으로 격상. 두 컨벤션 합성 시 multiverse 의 *모든 학습* 이 다음 페이즈로 전이.
