---
id: readme-numbers-from-summary
category: quality
applies-to-phases: '[09,14]'
applies-to-grades: '[all]'
trigger-when: 'doc + summary'
indexed-in: conventions/INDEX.md
---

# README numbers from summary (`readme-numbers-from-summary`) — README 숫자 vs summary.json ±0.01% 일치 (sprint-18, bz, HARD-RULE 9.bb)

## 한 줄 요약

**README.md / handoff 본문의 모든 숫자 토큰은 summary.json (또는 대응 measurement 산출물) 의 같은 키와 ±0.01% 이내 일치.** 페이즈 09 게이트가 README grep → summary.json 매핑 → drift 검출 + 강제 정정. 외부 cold session 003 의 `README 1569.6 vs summary.json 1559.6` (10 t = 0.64% drift) 회귀 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| README 의 숫자가 *직전 run* 값을 반영 안 함 | summary.json 갱신 후 README 미반영 → grader 가 number drift 지적 |
| ±5% 같은 느슨한 tolerance 가 default | 데이터 정합성은 완전 일치 또는 명시적 drift 표시여야 함 — sprint-18 ±0.01% strict |
| 정합 검증 게이트 부재 | 페이즈 09 게이트 1~9 모두 README ↔ summary.json drift 검사 안 함 |

## 트리거

페이즈 09 quality gate (모든 grade). 페이즈 14 handoff 직전 재검증.

## 알고리즘

1. `README.md` + `outputs/README.md` + `handoff/14-handoff.md` 본문에서 숫자 literal grep — regex `\b[0-9]+\.[0-9]+\b` (decimal) + `\b[0-9]{2,}\b` (integer ≥ 2자리).
2. 각 숫자 주변 5 단어 컨텍스트 → `summary.json` key 매핑 (fuzzy match OR explicit `summary.json` 인용 본문 detect).
3. 매핑된 README 숫자 vs summary.json 값 ±0.01% 이내 일치 검증.
4. 매핑 실패 숫자 → frontmatter `external_source: <url|path>` 명시 의무 (외부 source 인용 시).
5. drift ≥ 1 → fail. README 갱신 또는 summary.json 갱신 + entry script 재실행 강제.

## frontmatter (handoff/14-handoff.md)

```yaml
readme_numbers_total: <int>
readme_numbers_drift_count: 0
summary_keys_referenced: [baseline.mean_throughput, ramp_closed.median, ...]
unmapped_numbers_with_source: []      # external 인용 시 (path 또는 url)
```

## self_lint C-RNFS

컨벤션 파일 존재 + 페이즈 09 게이트 본문에 "readme-numbers" + 알고리즘 step ≥ 4 명시.

## 안티 패턴

a- README 숫자가 *고정* 으로 적힘 (실험 갱신 후 미반영) → drift.
b- ±5% 같은 느슨한 tolerance — sprint-18 strict ±0.01%.
c- README 가 summary.json 외 source 인용 → frontmatter `external_source` 의무, missing 시 fail.
d- summary.json 가 부정확하지만 README 가 *맞음* — drift 방향 거꾸로. 양쪽 모두 정정 필요.

## cold session 003 검증

`outputs/README.md`: "Baseline produces 1569.6 t/shift on average"
`outputs/summary.json`: `{"baseline": {"mean_throughput": 1559.6, ...}}`

Drift = 10 t = 0.64% (>> 0.01% 임계). grader -3pt Results & interpretation. sprint-18 게이트 적용 시 fail → README 갱신 강제.
