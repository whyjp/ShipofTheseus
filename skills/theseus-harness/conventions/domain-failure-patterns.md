# Domain Failure Patterns — 도메인 어댑터별 근본 결손 패턴 카탈로그

## 한 줄 요약

**[`conventions/domain-adapters/`](domain-adapters/) 의 각 어댑터 schema 에 `failure_patterns:` 항목 추가** — 도메인 별 *근본 결손 패턴* (DES = static calc / no replications / hard-coded outputs; Web API = no input validation / hardcoded creds; ML = data leakage / no train-test split) 누적. 페이즈 09 가 작업 도메인 추정 후 해당 어댑터의 failure pattern 자체 검증. 회차마다 어댑터에 누적되어 본 하네스의 *우로보로스 자기 강화* (regression-derived-lint-rule-autogen v0.9.16 정합).

## 1. 결손 진단

기존 [`anti-patterns.md`](anti-patterns.md) (v0.9.16) = A1~A10 *도메인 무관 공통* 패턴 (조기 추상화 / 분산 모놀리스 / 두괄식 누락 등). 그러나 *도메인 별 근본 결손 패턴* 인식 0:

- DES domain: static calculation rather than DES / no multiple replications / hard-coded outputs / queue without resource
- Web API domain: no input validation / hardcoded credentials / no rate limit / synchronous I/O blocking
- ML pipeline domain: data leakage / no train-test split / target encoding before split / no cross-validation
- Database domain: N+1 query / no transaction boundary / unbounded result set
- Workflow domain: no idempotency / no timeout / no compensation action

외부 evaluator (bench / reviewer) 가 이런 도메인 패턴 검출 시 점수 cap. 본 하네스가 *자체 검증* 메커니즘 0.

## 2. 운영 룰

### Step 1 — 도메인 어댑터 schema 확장

`domain-adapters/<domain>.md` 의 frontmatter:

```yaml
---
domain: des-modeling
nfr_dimensions: [throughput, queue_stability, replications]
failure_patterns:
  - id: DFP-DES-1
    name: "Static calculation rather than DES"
    detection: "no SimPy / Process / yield / queue mechanism in code"
    severity: cap_total      # 발견 시 점수 cap
    remediation: "discrete event 메커니즘 도입 — SimPy / asyncio queue / 직접 event loop"
  - id: DFP-DES-2
    name: "No multiple replications"
    detection: "single run only, no seed loop, no CI95"
    severity: cap_experimental
    remediation: "≥30 replications + seeded RNG + 95% CI"
  - id: DFP-DES-3
    name: "Hard-coded outputs"
    detection: "results.csv values 가 input data / scenario 와 무관하게 fixed"
    severity: cap_total
    remediation: "scenario perturbation 마다 results 변동 검증"
  - id: DFP-DES-4
    name: "Queue without resource constraint"
    detection: "trucks queued but no resource (loader/crusher) capacity defined"
    severity: cap_correctness
    remediation: "SimPy.Resource(capacity=N) 또는 동등 cap 메커니즘"
---
```

### Step 2 — 페이즈 09 자동 검증

phase 09 가 작업 도메인 추정 후 해당 어댑터의 `failure_patterns` 모두 자동 검증:

```yaml
gate_failure_patterns:
  domain: des-modeling
  patterns_checked: [DFP-DES-1, DFP-DES-2, DFP-DES-3, DFP-DES-4]
  failures_found: []         # 매칭 시 cap 발동
  evidence:
    DFP-DES-1: "SimPy.Process found at code/mine_sim/entities.py:42 ✓"
    DFP-DES-2: "30 replications confirmed at run_experiment.py:80 ✓"
```

### Step 3 — 회차마다 어댑터 누적

매 sprint 회차 / cold session 후 *발견된 신규 failure pattern* 을 도메인 어댑터에 추가. v0.9.16 [`regression-derived-lint-rule-autogen.md`](regression-derived-lint-rule-autogen.md) 와 정합 — 회귀 정정 commit 시 동일 차원 차단 룰 신규.

```yaml
# 회차 누적 예시
DFP-DES-5 (v0.9.18 sprint-12):
  name: "Tonnes credited at start instead of dump_end"
  source: "v0915-cold01 - cold02 측정에서 발견"
  detection: "tonnes_recorded event != dump_end event"
```

### Step 4 — 도메인 추정 알고리즘

phase 09 가 작업 도메인 추정 (페이즈 01 의도 §e 도메인 용어 + 마인드맵 noun + grade_assess.py 의 `mindmap_domain_nouns` 활용):

```python
def estimate_domain(intent_signals: dict, mindmap_signals: dict) -> str | None:
    nouns = mindmap_signals.get("domain_nouns", [])
    domain_terms = intent_signals.get("domain_terms", [])
    # 어댑터 매칭 (가장 strong 한 어댑터 1 개)
    for adapter_path in (skill_root / "conventions" / "domain-adapters").glob("*.md"):
        adapter = read_yaml_frontmatter(adapter_path)
        keywords = adapter.get("trigger_keywords", [])
        if any(kw in nouns + domain_terms for kw in keywords):
            return adapter["domain"]
    return None    # 매칭 어댑터 없음 = 일반 도메인
```

매칭 어댑터 0 = failure_patterns 검증 skip + handoff 에 *"domain adapter 미매칭"* 명시.

## 3. self_lint 룰

`scoring/self_lint.py` C-DFP (신규):

```python
def lint_domain_failure_patterns(skill_root: Path) -> list[str]:
    errors = []
    dfp = (skill_root / "conventions" / "domain-failure-patterns.md").read_text(encoding="utf-8")
    required = ["failure_patterns", "DFP-", "severity", "cap_", "detection", "remediation"]
    for kw in required:
        if kw not in dfp:
            errors.append(f"domain-failure-patterns.md: '{kw}' 키워드 누락")
    # 모든 도메인 어댑터에 failure_patterns 항목
    adapters_dir = skill_root / "conventions" / "domain-adapters"
    if adapters_dir.exists():
        for adapter in adapters_dir.glob("*.md"):
            body = adapter.read_text(encoding="utf-8")
            if "failure_patterns" not in body:
                errors.append(f"domain-adapters/{adapter.name}: failure_patterns 항목 누락")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- failure_patterns schema = generic frontmatter (id / name / detection / severity / remediation), 도메인 X.
b- 도메인 어댑터는 *카탈로그 누계* — 도메인이 추가되면 어댑터 추가 (anti-patterns.md A1~A10 동일 패턴).
c- 회차 누적 = regression-derived-lint-rule-autogen 의 generic 메커니즘 활용.
d- 도메인 매칭 0 = skip + 명시 — 모든 작업에 안전.

## 5. 안티 패턴

a- **failure_patterns 카탈로그 만들고 phase 09 에서 검증 안 함** — gate_failure_patterns 의무.
b- **severity 명시 안 함** — cap_total / cap_correctness / cap_experimental / warning 4 단계 의무.
c- **detection 추상적 ("코드 품질 낮음")** — 검증 가능한 *구체적 패턴* (정규식 / AST / 파일 검사) 의무.
d- **도메인 추정 강제** — 매칭 어댑터 없으면 *skip + 명시*. 잘못된 도메인 적용 금지.

## 6. anti-patterns.md 와의 관계

| 카탈로그 | 적용 |
|---|---|
| [`anti-patterns.md`](anti-patterns.md) (A1~A10) | *도메인 무관* 공통 패턴 (모든 작업) |
| **본 컨벤션 + domain-adapters/** | *도메인 종속* 근본 결손 (해당 도메인만) |

두 카탈로그 합성 = 본 하네스의 *anti-pattern 인식 풀 발현*.

## 7. 자기 검증

본 하네스 자체에 적용 — *meta-domain* 으로 "skill-design" 어댑터 신규 가능. failure_patterns 예: "키워드 매칭 grade 추정" (v0.9.16 → v0.9.17 정정), "SKILL.md 비대" (C26 fragmentation cleanup) 등 본 회차 누적.
