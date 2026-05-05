# Score Rubric Objectivity — strict checklist 기반 self-rating, 자유 판단 0

## 한 줄 요약

**페이즈 14 handoff 의 self-estimate 를 *체크리스트 evidence 1:1 매칭* 으로 강제** — 자유 판단 0. v0.9.9 의 generous 97 vs v0.9.12 의 strict 94 같은 *agent 의 self-rating noise* 제거. 0.999 도달이 *objective 기준* 되도록.

## 1. 결손 진단

cold session 결과 비교 :

| 회차 | 버전 | 측정 데이터 | self-estimate | discipline |
|---|---|---|:---:|---|
| v01_cold | v0.9.9 | baseline 1483 + sanity 4 + 24 tests | **97** | generous |
| v091_cold01 | v0.9.12 | baseline 1483 + sanity 4 + 24 tests + 180 invariants | **94** | strict |

같은 측정 데이터 (실제로 v0.9.12 가 더 강함) — 그러나 **self-estimate -3pt**. 차이 = *agent 의 self-rating discipline*. *측정 도구 noise* 가 ±3pt.

→ self-estimate 신뢰도 약. 0.999 도달이 *agent 마다 다른 의미*.

## 2. 운영 룰 — 8 차원 strict checklist

### Conceptual 20

| 점수 | 충족 조건 |
|:---:|---|
| 20/20 | data-derived ✓ + introduced ✓ + 각 ≥3 row + Threats §12 ✓ + Confidence §13 ✓ + V&V §14 ✓ + sensitivity matrix ✓ + extended discussion ≥11 sub-section ✓ + ≥350 lines |
| 19/20 | 위 9 항목 중 1 누락 |
| 18/20 | 2 누락 |
| 17/20 | 3 누락 |
| 16/20 이하 | 4+ 누락 또는 *내용 부재* |

### Sim correctness 20

| 점수 | 충족 조건 |
|:---:|---|
| 20/20 | sanity 4 PASS + analytical bound cross-validation PASS + bottleneck identified with composite score + per-edge utilisation tracked + analytical-bound ratio in [0.85, 1.00] + behavioral checks (≥10 pytest) + reachability self-check PASS |
| 19/20 | 위 7 항목 중 1 누락 |
| ... | |

### Results 15

| 점수 | 충족 조건 |
|:---:|---|
| 15/15 | 6 결정 질문 답 + 95% CI 명시 + sensitivity matrix + R1-R5 with capex+payback + decision-support framing + opportunity-cost mention + integrated narrative across scenarios |
| 14/15 | 7 항목 중 1 누락 |
| ... | |

### Data·topology 15 / Experimental 15 / Code quality 10 / Traceability 5 / Efficiency (bonus)

각 차원 별 strict checklist 동일 패턴. 본 컨벤션 §A 카탈로그.

## 3. self-rating 룰

### Step 1 — Evidence 수집

handoff 작성 시 산출물 디렉터리 검색 :

```python
def collect_evidence(project_dir: Path) -> dict:
    evidence = {}
    cm = (project_dir / "code" / "outputs" / "conceptual_model.md").read_text()
    evidence["data_derived_section"] = "data-derived" in cm.lower()
    evidence["introduced_section"] = "introduced" in cm.lower()
    evidence["threats_section"] = re.search(r"##\s+\d+\.\s*Threats", cm)
    evidence["confidence_section"] = re.search(r"##\s+\d+\.\s*Confidence", cm)
    # ... 등 모든 checklist 항목 자동 검색
    return evidence
```

### Step 2 — Score 도출

```python
def score_conceptual(evidence: dict) -> int:
    required = [
        "data_derived_section", "introduced_section", "data_derived_rows_3",
        "introduced_rows_3", "threats_section", "confidence_section",
        "vv_section", "sensitivity_matrix", "extended_11_sub", "lines_350"
    ]
    missing = sum(1 for k in required if not evidence.get(k))
    return max(20 - missing, 16)
```

### Step 3 — Frontmatter 박힘

handoff frontmatter :

```yaml
self_estimate:
  type: bench_rubric  # internal aggregate 와 분리
  evidence_collection_at: 2026-05-04T14:00:00Z
  rubric_version: v0.9.15
  per_dimension:
    Conceptual: 19   # 1 항목 누락 (lines 313 < 350)
    Sim_correctness: 19
    Results: 14
    ...
  total: 94
  evidence_paths:
    - code/outputs/conceptual_model.md
    - code/outputs/operational_recommendations.txt
    - sprints/01/report.json
    - ...
  evidence_missing:                # 누락 항목 명시 의무
    Conceptual:
      - "lines 350 미달 (313 lines)"
    Results:
      - "opportunity-cost mention 부재"
```

`evidence_missing` 명시 의무 — 각 차원 만점 미달 시 *어떤 항목이 누락* 인지 evidence 단위 명시.

### Step 4 — self_lint C-SRO 검증

```python
def lint_score_rubric_objectivity(handoff: dict) -> list[str]:
    errors = []
    se = handoff.get("self_estimate", {})

    # 1. type 명시 의무
    if se.get("type") not in ["bench_rubric", "internal_aggregate"]:
        errors.append("self_estimate.type missing")

    # 2. evidence_paths 의무
    if not se.get("evidence_paths"):
        errors.append("evidence_paths missing")

    # 3. evidence_missing 의무 (만점 차원 외)
    for dim, score in se.get("per_dimension", {}).items():
        max_pts = RUBRIC_MAX[dim]
        if score < max_pts and dim not in se.get("evidence_missing", {}):
            errors.append(f"{dim} {score}/{max_pts} but no evidence_missing")

    return errors
```

## 4. 효과 추정

retro 적용 시 :

| 회차 | 자체 보고 | strict rubric 적용 | 차이 |
|---|:---:|:---:|:---:|
| 002 (v0.9.2) | 92 | ~92 | 0 |
| 003 (v0.9.5) | 94 | ~94 | 0 |
| 004 (v0.9.6) | (claim) 98 | ~94 | -4 (imaginary 노출) |
| v099 (v0.9.9) | (claim) 97-98 | ~94 (payload 오류) | -3-4 |
| **v01_cold (v0.9.9)** | **97** | **~94** | **-3 (generous noise 제거)** |
| v091_cold01 (v0.9.12) | 94 | ~94 | 0 |
| v0914_cold01 (v0.9.14) | 94 | ~94 | 0 |

→ self-rating noise 제거 시 *진짜 plateau = 92→94* 명확. 인위 inflation 차단.

## 5. budget-saturation-loop 와의 합성

본 컨벤션 = score *quality* (정확도 / 신뢰도). budget-saturation-loop = score *quantity* (sprint 횟수). 두 합성 :

- saturation loop = budget 80% 사용까지 sprint 추가
- objective rubric = 매 sprint 후 self-rating 정확화 + evidence 누락 명시
- 추가 sprint 의 lesson = `evidence_missing` 의 항목 채움 (예: "lines 350 미달" → 다음 sprint 가 narrative 보강)

→ 두 컨벤션 = strict iteration loop, 진짜 0.999 도달.

## 6. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- bench rubric 8 차원 = simulation-bench 의 *공개 standard*. 다른 bench (HumanEval / SWE-Bench 등) 적용 시 다른 rubric 카탈로그 추가 (의미군 단위, 케이스 X).
b- evidence collection = artifact path + regex 검색, 도메인 X.
c- 평가 룰 (만점 -1 per missing) = generic.

## 7. 안티 패턴

a- **evidence 없이 자체 추정** — 본 컨벤션 핵심 위반. self_lint C-SRO.
b- **type 누락** — bench_rubric vs internal_aggregate 혼동. v0913_cold01 의 0.999 보고 패턴.
c- **evidence_missing 누락** — 차원 만점 미달인데 누락 항목 명시 0. *generous self-rating* 회귀.
d- **rubric_version 누락** — 어느 버전 rubric 적용했는지 불명.

## 8. v0.9.15 효과 종합

budget-saturation-loop + score-rubric-objectivity 합성 :
- 매 cold session = budget 80% 사용 (5-8 sprint)
- 매 sprint = strict rubric 으로 self-rating 정확
- 모든 차원 evidence_missing 추적 → next sprint 가 채움
- 결과 : self-estimate noise 제거 + 진짜 0.999 도달 가능

## 9. 자기 검증

본 컨벤션 = strict rubric 룰 자체에 적용 시 — 본 컨벤션의 *체크리스트 카탈로그* 가 *모든 도메인 / 모든 bench* 적용 가능한지 검증. 본 회차 = simulation-bench 만 카탈로그 명시. 다른 bench 적용 시 후속 PR 에서 추가.

## 10. v0.9.16 sprint-10 후속 — evidence_missing 자동 흐름

본 컨벤션이 `evidence_missing` 명시 의무만 강제. v0.9.16 [`evidence-driven-sprint-planning.md`](evidence-driven-sprint-planning.md) 가 그 항목을 *다음 sprint 의 lesson source 로 자동 매핑* — handoff 에서 evidence_missing 박고 종료하지 않고, budget 여유 시 자동 sprint 진입. 두 합성 시 진짜 0.999 도달.
