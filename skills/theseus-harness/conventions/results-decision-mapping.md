---
id: results-decision-mapping
category: quality
applies-to-phases: '[14]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Results Decision Mapping — Results & interpretation 만점 push (sprint-16 / v0.9.22)

## 한 줄 요약

**Results & interpretation 13→15 (-2pt, 가장 큰 갭) 정정.** [`directional-simplification.md`](directional-simplification.md) (bg) + [`decision-support-framing.md`](decision-support-framing.md) (az) 위에 *결과 → 의사결정 1:1 매핑* 강제 — 모든 numerical result 가 *최소 1 actionable decision* 으로 매핑되어야 만점. "결과 해석" 이 *서술* 이 아니라 *결정 항목* 이어야.

## 1. 결과 → 결정 매핑 표 의무

핸드오프 본문 (`handoff/14-handoff.md`) 강화 :

```markdown
## Results → Decisions Mapping (bw v0.9.22 의무)

| 결과 (numerical) | 해석 1 줄 | 의사결정 항목 | Owner | Deadline |
|---|---|---|---|---|
| throughput = 23.2 loads/hour ± 0.8 (t-CI95) | scenario default 가 capacity 87% 사용 | fleet_size 50 → 60 검토 (예상 +12% throughput) | mining ops lead | 2026 Q3 |
| crusher_busy_proxy = 0.94 ± 0.02 | crusher 가 binding 병목, ramp 비-병목 | crusher 라인 1 추가 검토 (예상 unblocking 가치 $2M/yr) | engineering | 2026 Q3 |
| ramp_utilization = 0.61 | ramp 비-병목 (negative finding) | ramp 확장 투자 *연기* (opportunity cost 회수) | finance | 즉시 |
| dump_queue_max = 18 | 큐가 max_capacity 90% 도달 | dump_site 추가 검토 (3→4) | mining ops | 2026 Q4 |
| simulation_runtime = 22 min | 45 min budget 49% 사용 | budget 여유 확보, scenario 확장 가능 | (run-internal) | n/a |
```

각 numerical result → ≥ 1 decision 1:1 매핑 의무. *해석만* 으로는 0pt — *action* 까지 가야.

## 2. frontmatter sync

```yaml
---
results_decision_mapping:
  total_results: 5
  with_decision_ratio: 1.00              # 모든 결과 → ≥1 decision 매핑
  with_owner_ratio: 1.00                  # 모든 decision 에 owner 명시
  with_deadline_ratio: 0.80               # 80% deadline 명시 (run-internal 제외)
  negative_findings_count: 1              # ramp 비-병목 같은 negative finding 도 decision 의무
results_interpretation_grade: A          # A (모두 1.0) / B (≥0.75) / C (<0.75)
---
```

## 3. self_lint C-RDM 룰

```python
def check_results_decision_mapping(artifact_dir: Path) -> list[str]:
    handoff = artifact_dir / 'handoff' / '14-handoff.md'
    if not handoff.exists():
        return []
    fm = parse_frontmatter(handoff)
    body = handoff.read_text()
    errors = []

    if 'Results → Decisions Mapping' not in body and 'Results -> Decisions Mapping' not in body:
        errors.append('handoff/14-handoff.md: § Results → Decisions Mapping 표 부재')

    rdm = fm.get('results_decision_mapping', {})
    if rdm.get('with_decision_ratio', 0) < 1.0:
        errors.append(f'with_decision_ratio {rdm.get("with_decision_ratio")} < 1.0')
    if rdm.get('with_owner_ratio', 0) < 1.0:
        errors.append('with_owner_ratio < 1.0')
    if rdm.get('total_results', 0) < 3:
        errors.append('total_results < 3 (의미 있는 결과 ≥ 3)')

    if fm.get('results_interpretation_grade') not in ['A', 'B']:
        errors.append('results_interpretation_grade ∉ {A, B}')

    # negative finding 의무 — ramp 비-병목 같은 *기각* 결과도 결정 (자원 회수)
    if rdm.get('negative_findings_count', 0) < 1:
        errors.append('negative_findings_count < 1 (negative finding 도 decision 의무 — 자원 회수 / 가설 기각)')

    return errors
```

## 4. cold session 적용 — Results & interpretation 13→15 push

가장 큰 갭 (-2pt). 본 컨벤션 적용 후 :
- 모든 numerical result → action item 매핑 → +1pt 회수
- negative finding 도 *기각 결정* (자원 회수 / 가설 폐기) 명시 → +1pt 회수

cold session 의 ramp 비-병목 finding 이 단순 "ramp 는 병목 아님" 서술이 아니라 "ramp 확장 투자 *연기 결정* + opportunity cost 회수 ($XM)" 으로 가야 만점.

## 5. 안티 패턴

a- **결과 *서술만*** — "throughput 이 23.2 였다" → 0pt. "fleet 50→60 검토 (+12% throughput 예상)" 까지.
b- **decision 의 owner 부재** — "검토 필요" 만, 누가 검토? owner 명시 의무.
c- **negative finding 무시** — "ramp 안 막힌다" 만 박고 끝 → opportunity cost 회수 안 함. 기각 결정 의무.
d- **decision 이 *너무 추상*** — "best practice 따르기" 금지. 정량 + deadline 의무.
e- **run-internal 결과 제외** — simulation_runtime 같은 메타도 의무 (budget 평가 결정).

## 6. 호환성

- [`directional-simplification.md`](directional-simplification.md) (bg) — direction ↑/↓/? + magnitude → 본 컨벤션의 결과 입력.
- [`decision-support-framing.md`](decision-support-framing.md) (az) — Operational implications + Trade-off + Opportunity-cost 3 항목 → 본 컨벤션 의무 표의 의사결정 본문 입력.
- [`commentary-policy.md`](commentary-policy.md) (bh) — audience=external-reviewer 시 본 컨벤션 매핑이 더 강제.
