# Domain Failure Patterns — 도메인 어댑터별 근본 결손 패턴 카탈로그

## 한 줄 요약

**사용자 제공 도메인 어댑터 (per-project) 의 schema 에 `failure_patterns:` 항목 추가하는 *프레임워크*** — 도메인 별 *근본 결손 패턴* 카탈로그 누적. 페이즈 09 가 작업 도메인 추정 후 해당 어댑터의 failure pattern 자체 검증. 회차마다 어댑터에 누적되어 *우로보로스 자기 강화* (regression-derived-lint-rule-autogen v0.9.16 정합). **본 하네스에 built-in 어댑터 0** (sprint-19+, 벤치 어뷰징 회피).

## 1. 결손 진단

기존 [`anti-patterns.md`](anti-patterns.md) (v0.9.16) = A1~A10 *도메인 무관 공통* 패턴 (조기 추상화 / 분산 모놀리스 / 두괄식 누락 등). 그러나 *도메인 별 근본 결손 패턴* 인식 0 — 사용자가 per-project 어댑터로 정의. 외부 evaluator 가 도메인 패턴 검출 시 점수 cap. 본 하네스에 *built-in 어댑터 0* 이지만 사용자 어댑터 활성 시 자체 검증 가능.

## 2. 운영 룰

### Step 1 — 도메인 어댑터 schema 확장 (사용자 제공)

사용자 per-project 작성 `domain-adapters/<domain>.md` 의 frontmatter (예시 schema, 도메인 X 일반화) :

```yaml
---
domain: <user-supplied-domain-name>
nfr_dimensions: [...]            # 도메인 NFR 차원 list
failure_patterns:
  - id: DFP-<DOMAIN>-1
    name: "<failure pattern name>"
    detection: "<concrete detection rule — regex / AST / file check>"
    severity: cap_total | cap_correctness | cap_experimental | cap_results | warning
    remediation: "<corrective action>"
  - id: DFP-<DOMAIN>-2
    ...
---
```

severity 4 단계 + warning 의무. detection 은 *검증 가능한 구체적 패턴* (정규식 / AST / 파일 검사). built-in 어댑터 0 (sprint-19+, 벤치 어뷰징 회피).

### Step 2 — 페이즈 09 자동 검증

phase 09 가 작업 도메인 추정 후 해당 어댑터의 `failure_patterns` 모두 자동 검증 (사용자 어댑터 매칭 시):

```yaml
gate_failure_patterns:
  domain: <user-supplied-domain>
  patterns_checked: [DFP-<DOMAIN>-1, DFP-<DOMAIN>-2, ...]
  failures_found: []         # 매칭 시 cap 발동
  evidence:
    DFP-<DOMAIN>-1: "<concrete file:line evidence>"
```

매칭 어댑터 0 (default — built-in 0, 사용자 미제공 시) → `gate_failure_patterns` skip + handoff 에 *"domain adapter 미매칭"* 명시.

### Step 3 — 회차마다 어댑터 누적

매 sprint 회차 / cold session 후 *발견된 신규 failure pattern* 을 *사용자 어댑터* 에 추가. v0.9.16 [`regression-derived-lint-rule-autogen.md`](regression-derived-lint-rule-autogen.md) 와 정합 — 회귀 정정 commit 시 동일 차원 차단 룰 신규. 본 하네스 자체에는 built-in 어댑터 0 — 누적 = 사용자 책임.

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
| [`anti-patterns.md`](anti-patterns.md) (A1~A10) | *도메인 무관* 공통 패턴 (모든 작업, **본 하네스 built-in**) |
| **본 컨벤션 + 사용자 제공 domain-adapters/** | *도메인 종속* 근본 결손 (해당 도메인만, **사용자 per-project**) |

두 카탈로그 합성 = anti-pattern 인식 풀 발현. 본 하네스는 도메인 무관 카탈로그만 built-in (벤치 어뷰징 회피).

## 7. 자기 검증

본 하네스 자체에 적용 — *meta-domain* 으로 "skill-design" 어댑터 신규 가능. failure_patterns 예: "키워드 매칭 grade 추정" (v0.9.16 → v0.9.17 정정), "SKILL.md 비대" (C26 fragmentation cleanup) 등 본 회차 누적.
