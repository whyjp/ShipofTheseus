# Experimental Control Protocol — Experimental design 만점 push (sprint-16 / v0.9.22)

## 한 줄 요약

**Experimental design 14→15 (-1pt) 정정.** [`intent-plan-impl-sprint-trinity.md`](intent-plan-impl-sprint-trinity.md) (bd, v0.9.19) 의 axis × ≥ 2 sprint 위에 *실험 control protocol 4 차원* 의무 — independent variable / dependent variable / control variable / replicate count + seed 명시. 실험이 *스칼라 1 점 측정* 이 아니라 *재현 가능한 protocol* 이어야 만점.

## 1. 실험 protocol 4 차원 의무

페이즈 06 plan 의 *실험 차원* 산출물 의무 :

```markdown
## Experimental Control Protocol (bv v0.9.22 의무)

### Experiment 1 — Throughput vs Fleet Size

| 차원 | 값 | 정당화 |
|---|---|---|
| **IV** independent | fleet_size ∈ {10, 20, 30, 40, 50} | 5 datapoint, log scale 충분 |
| **DV** dependent | throughput (loads/hour, 95% t-CI) | bench rubric primary metric |
| **CV** control | scenario.travel_time_cv = 0.10 (fixed) | other source of variance 차단 |
| **CV** control | scenario.loader_count = 3 (fixed) | bottleneck 위치 isolate |
| **N** replicates | 30 runs/datapoint | t-CI95 width ≤ 5% 보장 |
| **seed** | seeds = [1, 2, ..., 30] (deterministic) | reproducibility |

### Experiment 2 — Crusher Binding (negative finding)

(... 동일 4 차원 ...)
```

각 실험마다 IV / DV / CV / N / seed 5 항목 의무.

## 2. frontmatter sync

```yaml
---
experiments:
  count: 3
  with_iv_dv_cv_ratio: 1.00              # 모든 실험에 IV/DV/CV 명시
  total_replicates_min: 30                # 최소 N
  reproducibility_seed_explicit: true     # seed 명시 의무
  control_variables_count: 6              # 누적 CV 수
experimental_design_grade: A              # A (모두 1.0 + N≥30) / B (≥0.75) / C (<0.75)
---
```

## 3. self_lint C-ECP 룰

```python
def check_experimental_control_protocol(artifact_dir: Path) -> list[str]:
    plan = artifact_dir / 'plan' / '06-plan.md'
    if not plan.exists():
        return []
    fm = parse_frontmatter(plan)
    body = plan.read_text()
    errors = []

    if 'Experimental Control Protocol' not in body:
        errors.append('§ Experimental Control Protocol 부재')

    # 각 실험 본문에 IV / DV / CV / N / seed 명시
    for token in ['**IV**', '**DV**', '**CV**', '**N**', '**seed**']:
        if token not in body:
            errors.append(f'experiments 본문에 {token} 표기 부재')

    e = fm.get('experiments', {})
    if e.get('with_iv_dv_cv_ratio', 0) < 1.0:
        errors.append('with_iv_dv_cv_ratio < 1.0')
    if e.get('total_replicates_min', 0) < 30:
        errors.append(f'total_replicates_min {e.get("total_replicates_min")} < 30')
    if e.get('reproducibility_seed_explicit') != True:
        errors.append('reproducibility_seed_explicit != true')
    if fm.get('experimental_design_grade') not in ['A', 'B']:
        errors.append('experimental_design_grade ∉ {A, B}')

    return errors
```

## 4. cold session 적용 — Experimental design 14→15 push

본 컨벤션 적용 후 :
- 모든 실험 IV/DV/CV/N/seed 의무 박힘 → +1pt 회수
- 30+ replicates + t-CI95 width ≤ 5% → reproducibility 보장

## 5. 안티 패턴

a- **single point measurement** — N=1 결과만 → CI 없음. N ≥ 30 의무.
b- **CV 누락** — IV 만 명시, *고정 변수* 미명시 → confounding 위험.
c- **seed 부재** — 같은 결과 재현 불가 → reproducibility 0pt.
d- **IV 가 실제로 IV 아님** — fleet_size 변화시키면서 loader_count 도 변화 → IV 가 아니라 *교란*. CV 표 의무.

## 6. 호환성

- [`intent-plan-impl-sprint-trinity.md`](intent-plan-impl-sprint-trinity.md) (bd) — sprint axis × ≥ 2 + 본 컨벤션 실험 protocol = trinity 가 *코드/plan 차원*, 본 컨벤션이 *실험 차원*.
- [`measurement-contract.md`](measurement-contract.md) (bi) — DV measurement method 정합 (sample/accumulate/reconstruct).
- [`evidence-driven-sprint-planning.md`](evidence-driven-sprint-planning.md) — IV 변경 시 evidence_missing 입력.
