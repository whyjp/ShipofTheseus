---
id: regression-derived-lint-rule-autogen
category: meta
applies-to-phases: '[11]'
applies-to-grades: '[G4,G5]'
trigger-when: '회귀 정정'
indexed-in: conventions/INDEX.md
---

# Regression-Derived Lint Rule Auto-Generation — 회귀 정정 → self_lint 룰 자동 신규

## 한 줄 요약

**페이즈 11 회귀 바이섹트의 4 분류 (plan/impl/data/external defect) 정정 commit 시 *동일 차원 회귀 차단 self_lint 룰 신규* 의무.** 회귀 정정이 *일회성* 이 아니라 *부트스트래핑 자기 강화* — 본 하네스가 *회차마다 더 단단해지는* 약속 (BOOTSTRAP §1) 을 메커니즘 단위로 강제.

## 1. 결손 진단

현재 흐름:

```
sprint NN 점수 0.05 하락 검출
  → 페이즈 11 회귀 바이섹트
  → 4 분류 (plan/impl/data/external)
  → 권고 페이즈 진입 (06 / 08-γ / 04 / 09)
  → 정정 commit
  → 종료
```

→ 정정 commit *이후* 동일 차원 회귀가 *다시* 발생할 수 있음. 본 하네스의 self_lint 60+ 룰은 *명시 신규* (sprint 단위) 만, *회귀로부터 도출된 룰* 는 0. 매 회차의 회귀 학습이 *영구 자산화* 안 됨.

본 하네스의 *우로보로스 자기 강화* 컨셉 (BOOTSTRAP §1) 의 missing piece.

## 2. 운영 룰

### Step 1 — 페이즈 11 산출물에 *lint_rule_proposal* 의무

`sprints/NN/bisect.md` frontmatter:

```yaml
regression_class: plan_defect              # plan / impl / data / external
root_cause_summary: "페이즈 06 plan 본문에 데이터 구조 명시 ≥2 룰 위반 — entity dataclass 없이 dict 사용"
fix_target_phase: 06
lint_rule_proposal:
  rule_id: C-RDR-001                       # regression-derived rule, sequential
  rule_name: "plan/06-plan.md must contain dataclass | TypedDict | pydantic.BaseModel"
  rule_check: |
    plan_body = read("plan/06-plan.md")
    if not re.search(r"@dataclass|TypedDict|class \w+\(BaseModel\)", plan_body):
      return ["plan/06-plan.md missing structured data definition"]
  applies_to: phase 06
  derived_from_sprint: NN
  derived_from_class: plan_defect
```

### Step 2 — `scoring/self_lint.py` 자동 등록

페이즈 11 정정 commit 시:

```python
# scoring/regression_lint_registry.py (신규)
import json
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent / "regression_derived_rules.json"

def register_rule(proposal: dict):
    """페이즈 11 산출물의 lint_rule_proposal 을 등록."""
    registry = json.loads(REGISTRY_PATH.read_text()) if REGISTRY_PATH.exists() else {"rules": []}
    if any(r["rule_id"] == proposal["rule_id"] for r in registry["rules"]):
        raise ValueError(f"rule_id {proposal['rule_id']} 이미 존재")
    registry["rules"].append(proposal)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False))

def all_rules() -> list:
    return json.loads(REGISTRY_PATH.read_text())["rules"] if REGISTRY_PATH.exists() else []
```

self_lint 메인 CHECKS 리스트가 동적 로드:

```python
from regression_lint_registry import all_rules

CHECKS_BASE = [...]  # 정적 룰
CHECKS_DYNAMIC = [(r["rule_id"], r["rule_name"], compile_check(r["rule_check"])) for r in all_rules()]
CHECKS = CHECKS_BASE + CHECKS_DYNAMIC
```

### Step 3 — 신규 룰 즉시 PASS 검증

자동 등록 직후 self_lint 실행 — 신규 룰이 정정된 산출물에 대해 PASS 확인. PASS 안 되면 정정 incomplete → 페이즈 11 재진입.

### Step 4 — 회차 누적 보고

`.ShipofTheseus/theseus-self/sprints/NN/report.md` 에 누적 룰 시계열:

```
Self-derived lint rules: 0 → 1 → 3 → 5 (4 회차 누적)
Most recent:
  - C-RDR-005 (sprint 09 plan_defect): "plan/06-plan.md must contain ≥3 interface definitions"
  - C-RDR-004 (sprint 08 impl_defect): "impl/08-impl-log.md must map ≥3 TODO IDs"
```

매 회차 누적 = 본 하네스가 *진짜 더 단단해진다* 의 객관 측정.

## 3. self_lint 룰

`scoring/self_lint.py` C-RDLR (신규, 메타):

```python
def lint_regression_derived_rule_autogen(skill_root: Path) -> list[str]:
    errors = []
    rdlr = (skill_root / "conventions" / "regression-derived-lint-rule-autogen.md").read_text(encoding="utf-8")
    phase11 = (skill_root / "phases" / "11-regression-bisect.md").read_text(encoding="utf-8")
    # 1. 페이즈 11 본문이 본 컨벤션 cross-reference
    if "regression-derived-lint-rule-autogen" not in phase11:
        errors.append("phase 11 missing regression-derived-lint-rule-autogen cross-ref")
    # 2. 본 컨벤션 키워드
    required = ["lint_rule_proposal", "rule_id", "regression_lint_registry", "C-RDR"]
    for kw in required:
        if kw not in rdlr:
            errors.append(f"regression-derived-lint-rule-autogen missing keyword: {kw}")
    # 3. registry 모듈 존재 여부 (선택 — 회귀 발생 후만 활성)
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 4 분류 (plan/impl/data/external defect) = sprint-05-e 의 generic 분류 재사용.
b- rule_id namespace `C-RDR-NNN` = generic 시퀀셜.
c- 룰 본문은 페이즈 11 의 root_cause 에서 도출 — 도메인 무관 (회귀의 *분류* 만이 매핑 키).

## 5. 안티 패턴

a- **회귀 정정 commit 에 lint_rule_proposal 누락** — 본 컨벤션 핵심 위반.
b- **rule_id 중복** — registry 가 ValueError raise.
c- **신규 룰이 정정 산출물에 fail** — 룰 자체가 잘못 = 페이즈 11 재진입.
d- **bench 도메인 키워드 룰** (예: "plan must contain crusher") — 도메인 종속 룰 = 본 컨벤션 §4 위반. self_lint C-RDR-DOMAIN-AGNOSTIC (TBD) 검증.

## 6. 본 하네스 *우로보로스 자기 강화* 의 메커니즘화

기존 BOOTSTRAP §1: "본 하네스는 자기 자신을 같은 게이트로 평가한다."

본 컨벤션 추가 후: "본 하네스는 자기 자신의 *회귀 학습* 을 *룰로 박아 자기 자신을 더 빡빡하게 평가한다*." → 회차마다 self_lint 룰이 *자동* 누적.

## 7. 자기 검증

본 컨벤션 자체에 적용 — 본 v0.9.16 sprint-10 도입 후, 본 하네스 자기 평가 (BOOTSTRAP) 에서 첫 회귀 발생 시 즉시 본 룰 자동 등록 → 자기 강화.
