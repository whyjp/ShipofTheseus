# Decision-Support Framing — Results 차원 의 본문 의무

## 한 줄 요약

**handoff Results 차원의 본문이 *operational implications + trade-off framing + opportunity-cost* 3 항목 명시 의무.** v0915-cold01 외부 채점 -1pt (Results 14/15) 의 직접 원인 = 결정 질문 답에 *operational 의미* / *대안 비교* / *기회 비용* 본문 부족.

## 1. 결손 진단

기존 [`score-rubric-objectivity.md`](score-rubric-objectivity.md) (v0.9.15) Results 15 차원 카탈로그:

```
Results: 6 결정 질문 답 + 95% CI 명시 + sensitivity matrix + R1-R5 capex+payback +
         decision-support framing + opportunity-cost mention + integrated narrative
```

→ 카탈로그는 있지만 *어떻게 작성하는지* 의 본문 룰 부재. handoff 작성 시 evidence_missing 만 박고 *실제 본문 의무* 안 강제.

결과: cold session 산출물의 Q1~Q6 답이 *수치 + bottleneck 결론* 만 — *operational 의미* / *대안 비교* / *기회 비용* 자주 누락.

## 2. 운영 룰

### Step 1 — Results 차원 본문 3 항목 의무

handoff 또는 README.md (외부 evaluator 시) 의 결정 질문 답마다 다음 3 항목 본문 의무:

```markdown
## Q. <결정 질문>

### 답
<수치 + 결론 — 기존>

### Operational implications
<이 결과가 *운영* 에 의미하는 것 — 1-2 문단>
예 (DES): "<도메인-specific 결정 지원 예시>"
예 (Web API): "RPS 200 = current DB pool 의 sweet spot. RPS 400 = same throughput, p99 latency 5x — UX 회복 불가."

### Trade-off framing
<주어진 결정의 *대안* 들 + 비교 차원>
예: "<업그레이드 vs 자원 추가 비교 예시>"

### Opportunity-cost
<선택 시 *포기하는* 것 명시>
예: "<자본 trade-off 예시>"
```

### Step 2 — handoff frontmatter 검증

```yaml
self_estimate:
  per_dimension:
    Results: 14
  evidence_decision_support:
    Q1:
      operational_implications: true   # 본문 보유
      trade_off_framing: true
      opportunity_cost: true
    Q2:
      operational_implications: true
      trade_off_framing: false        # 누락 — evidence_missing 박힘
      opportunity_cost: true
    ...
  evidence_missing:
    Results:
      - "Q2: trade_off_framing 누락"
      - "Q5: opportunity_cost 누락"
```

evidence-driven-sprint-planning (v0.9.16) 와 정합 — Results 차원의 evidence_missing 항목이 다음 sprint 의 lesson source 가 됨.

### Step 3 — 도메인별 적용

본 컨벤션은 *도메인 무관 generic*. 적용 도메인 예:

| 도메인 | operational_implications 형식 | trade_off | opportunity_cost |
|---|---|---|---|
| DES (시뮬레이션) | throughput / queue / utilization 운영 의미 | 시나리오 N 가지 비교 | capex / maintenance 차원 |
| Web API | RPS / latency / error rate UX 의미 | 인프라 옵션 N 가지 | 비용 / 복잡도 차원 |
| ML model | accuracy / precision / recall 비즈니스 의미 | 알고리즘 N 가지 | 추론 비용 / 학습 시간 |
| 데이터 분석 | metric A vs B 의 의사결정 의미 | 정책 옵션 N 가지 | 정책 cost |

### Step 4 — Q 답이 numeric only 인 경우 fail

self_lint 가 *Q 답에 numeric / 수치 만* 있고 *operational implications / trade-off / opportunity-cost* 본문 부재 시 fail:

```python
def check_decision_support_present(handoff_md: str, q_count: int) -> list[str]:
    errors = []
    for q_id in range(1, q_count + 1):
        q_section = extract_question_section(handoff_md, q_id)
        if not re.search(r"(operational impl|운영 의미)", q_section, re.I):
            errors.append(f"Q{q_id}: operational_implications 본문 누락")
        if not re.search(r"(trade.?off|대안 비교)", q_section, re.I):
            errors.append(f"Q{q_id}: trade_off_framing 본문 누락")
        if not re.search(r"(opportunity.?cost|기회 비용)", q_section, re.I):
            errors.append(f"Q{q_id}: opportunity_cost 본문 누락")
    return errors
```

## 3. self_lint 룰

`scoring/self_lint.py` C-DSF (신규):

```python
def lint_decision_support_framing(skill_root: Path) -> list[str]:
    errors = []
    dsf = (skill_root / "conventions" / "decision-support-framing.md").read_text(encoding="utf-8")
    sro = (skill_root / "conventions" / "score-rubric-objectivity.md").read_text(encoding="utf-8")
    required = ["operational implications", "trade-off framing", "opportunity-cost", "evidence_decision_support"]
    for kw in required:
        if kw.lower() not in dsf.lower():
            errors.append(f"decision-support-framing.md: '{kw}' 키워드 누락")
    if "decision-support-framing" not in sro:
        errors.append("score-rubric-objectivity.md: decision-support-framing cross-ref 누락")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 3 항목 (operational / trade-off / opportunity-cost) = decision-making 의 generic dimension, 도메인 X.
b- 본문 의무 룰 = generic markdown 패턴.
c- 도메인 별 적용 예시 4 종 (§2 step 3) — 매핑만 다름, 의무는 동일.

## 5. 안티 패턴

a- **Q 답 = numeric + bottleneck 결론 only** — 본 컨벤션 핵심 위반. operational/trade-off/opportunity-cost 본문 부재.
b- **opportunity-cost 형식적 ("기회 비용 있음")** — *명시 옵션* 의무 (예: "<자본 trade-off 예시>").
c- **trade-off 표 없이 텍스트만** — 비교 차원 ≥ 3 의 *표 형식* 권장.
d- **integrated narrative 누락** — Q1~Q6 답이 isolated. *cross-question integration* (Q3 의 truck 답이 Q5 의 sensitivity 와 어떻게 연결) 한 단락 의무.

## 6. score-rubric-objectivity 와의 합성

| 컨벤션 | 차원 |
|---|---|
| score-rubric-objectivity (v0.9.15) | Results 15 차원의 *evidence 1:1 매칭* |
| **본 컨벤션 (v0.9.18)** | Results 차원의 *본문 의무 3 항목* |

두 합성 = 진짜 Results 만점 (15/15) 도달 가능.

## 7. 자기 검증

본 하네스 자체에 적용 — 본 하네스의 *decision question* = "어느 페이즈를 어느 grade 에서 활성?" / "어느 컨벤션을 어느 페이즈에 인용?" 등. 본 하네스 README / docs 가 *operational implications + trade-off + opportunity-cost* 본문 보유 가능. 자기 적용 = v0.9.18 sprint-12.
