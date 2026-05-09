---
id: regression
category: meta
applies-to-phases: '[10,11]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'always (sprint loop) / 회귀 정정 (lint autogen)'
indexed-in: conventions/INDEX.md
---

# Regression — sprint loop (self-polishing) + lint rule autogen (회귀 → self_lint)

## 한 줄 요약

**본 하네스의 *self-polishing 의지* + *우로보로스 자기 강화* 두 메커니즘 통합.** ① **sprint loop** (페이즈 10) — 임계 도달까지 무한 반복, dimension gap 입력 + weakest dim lesson 적용 + budget cap 내 최대 폴리싱. ② **lint rule autogen** (페이즈 11) — 회귀 바이섹트 4 분류 (plan/impl/data/external defect) 정정 commit 시 *동일 차원 회귀 차단 self_lint 룰 신규* 의무, 회차마다 self_lint 룰 자동 누적 → 본 하네스가 *회차마다 더 단단해진다* 의 객관 측정.

## 1. 결손 진단

### 1.1 sprint loop 결손 (sprint-08 v0.9.8 도입 동기)

페이즈 10 ([`../phases/10-test-loop.md`](../phases/10-test-loop.md)) 의 SKILL.md 인덱스가 "무한 스프린트 (임계 0.999)" 로 명시되어 있으나, *실 운영에서 단일 sprint 통과 후 정상 종료* 케이스 발생. cold 회차 (`synthetic_mine_throughput_cold`) 에서 sprint-01 의 자체 추정 92-95 / 100 이 임계 (0.97 G3 / 0.999 G4) 미달임에도 *재실행 0 회* — 본 스킬의 self-polishing 의도 누락.

### 1.2 lint autogen 결손 (sprint-10 v0.9.16 도입 동기)

기존 흐름 — 회귀 정정 commit *이후* 동일 차원 회귀가 *다시* 발생할 수 있음. 본 하네스의 self_lint 60+ 룰은 *명시 신규* (sprint 단위) 만, *회귀로부터 도출된 룰* 는 0. 매 회차의 회귀 학습이 *영구 자산화* 안 됨. BOOTSTRAP §1 의 *우로보로스 자기 강화* 컨셉의 missing piece.

## 2. Layer ① — sprint loop (페이즈 10)

### 2.1 score-per-dimension (sprint 출력)

매 sprint 종료 시 산출물 `sprints/NN/report.json` 에 *bench rubric (또는 일반 success criteria) 차원별 점수* 의무 :

```yaml
self_estimate:
  per_dimension:
    Conceptual_modelling: {score: 18, max: 20, gap: 2}
    Sim_correctness: {score: 19, max: 20, gap: 1}
    ...
  total: 94
  threshold_target: 97   # G4 = 0.97 × 100
  weakest_dimension: "Conceptual_modelling"
  weakest_gap: 2
```

### 2.2 gap-from-threshold 검사

- 모든 dimension `score / max ≥ threshold` → **CONVERGED** (sprint 종료, phase 14 진입).
- 어느 한 dimension `score / max < threshold` → **REGRESS** (sprint NN+1 진입).

threshold 는 grade 별 (G3=0.97 / G4=0.999 / G5=0.99999) — [`grades.md`](grades.md) 정합.

### 2.3 weakest-dimension lesson 적용

REGRESS 시 :

a- weakest_dimension 의 *원인 lesson* 식별 ([`lessons.md`](lessons.md) 의 차원 5 매핑 참조).
b- 해당 lesson 의 *수정 범위* 결정 :
   - 단순 narrative 보강 → outputs/ 재생성 (페이즈 08-ε log 만 재진입)
   - 모듈 결손 → 페이즈 06 plan 부분 재진입
   - 기획-구현 갭 → 페이즈 06 부터 통째 re-architect (HARD-RULE e-1)
c- 수정 적용 후 sprint NN+1 재실행 + Step 1 재측정.

### 2.4 budget cap

- 정해진 budget (페이즈 04 Q-D6 답) 내에서 *무한 반복*.
- budget 초과 시 *최선 sprint* 로 phase 14 진입 + handoff 에 *gap 명시*.

본 룰이 단순히 "임계 미달 시 정지" 가 아닌 *budget 내 최대 폴리싱* 보장.

### 2.5 Lesson dimension 매핑 (의미군 단위)

매 dimension 의 weakest 시 *어떤 lesson 의 수정* 을 할 것인가 — 케이스가 아닌 의미군 별 :

| Dimension 약점 | Lesson 의미군 | 적용 페이즈 |
|---|---|---|
| Conceptual / clarity | narrative 분량/깊이 + assumption 분리 | 페이즈 08-ε log (outputs/ regen) |
| Sim correctness / accuracy | 모델 결손 — analytical bound mismatch / sanity 차원 추가 | 페이즈 06 plan 부분 재진입 |
| Experimental / reproducibility | seed 분리 / determinism / 더 많은 reps | 페이즈 06/08 |
| Results / interpretability | 운영 권고 깊이 (ROI, sensitivity matrix) | 페이즈 08-ε |
| Code quality / maintainability | DIP 위반 / cyclomatic | 페이즈 06 re-architect (HARD-RULE e-1) |
| Traceability | event log 컬럼 추가 / 결정 추적표 | 페이즈 08 |
| Completeness | optional scope 활용 / requirement coverage | 페이즈 06 plan 추가 |
| Efficiency | wall clock / LOC | 페이즈 08 refactor |

본 표는 *씨앗* — 새 dimension 의 의미군 매핑은 추가 가능, 케이스별 추가 X.

## 3. Layer ② — lint rule autogen (페이즈 11)

### 3.1 페이즈 11 산출물에 *lint_rule_proposal* 의무

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

### 3.2 `scoring/self_lint.py` 자동 등록

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

### 3.3 신규 룰 즉시 PASS 검증

자동 등록 직후 self_lint 실행 — 신규 룰이 정정된 산출물에 대해 PASS 확인. PASS 안 되면 정정 incomplete → 페이즈 11 재진입.

### 3.4 회차 누적 보고

`.ShipofTheseus/theseus-self/sprints/NN/report.md` 에 누적 룰 시계열:

```
Self-derived lint rules: 0 → 1 → 3 → 5 (4 회차 누적)
Most recent:
  - C-RDR-005 (sprint 09 plan_defect): "plan/06-plan.md must contain ≥3 interface definitions"
  - C-RDR-004 (sprint 08 impl_defect): "impl/08-impl-log.md must map ≥3 TODO IDs"
```

매 회차 누적 = 본 하네스가 *진짜 더 단단해진다* 의 객관 측정.

### 3.5 self_lint C-RDLR

```python
def lint_regression_derived_rule_autogen(skill_root: Path) -> list[str]:
    errors = []
    rdlr = (skill_root / "conventions" / "regression.md").read_text(encoding="utf-8")
    phase11 = (skill_root / "phases" / "11-regression-bisect.md").read_text(encoding="utf-8")
    # 1. 페이즈 11 본문이 본 컨벤션 cross-reference
    if "regression" not in phase11:
        errors.append("phase 11 missing regression cross-ref")
    # 2. 본 컨벤션 키워드
    required = ["lint_rule_proposal", "rule_id", "regression_lint_registry", "C-RDR"]
    for kw in required:
        if kw not in rdlr:
            errors.append(f"regression.md missing keyword: {kw}")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

### 4.1 sprint loop layer

a- trigger = *sprint 종료 시 dimension gap* — 도메인 무관. simulation-bench 든 결제 시스템이든 같은 룰.
b- lesson 매핑 = 의미군 단위, 케이스별 X.
c- iteration 종료 조건 = 임계 또는 budget — 외부 답안 visit 0.

### 4.2 lint autogen layer

d- 4 분류 (plan/impl/data/external defect) = sprint-05-e 의 generic 분류 재사용.
e- rule_id namespace `C-RDR-NNN` = generic 시퀀셜.
f- 룰 본문은 페이즈 11 의 root_cause 에서 도출 — 도메인 무관 (회귀의 *분류* 만이 매핑 키).

## 5. 안티 패턴

### 5.1 sprint loop 안티 패턴

a- **Single-sprint 종료** — sprint-01 통과로 phase 14 진입 = 본 컨벤션 위반. 임계 도달 명시 의무.
b- **Theatrical regression** — 매 sprint 가 *형식적 score increment* 만 (예: assumption 표 row 1개 추가 = +0pt). lesson 의 *실 effect* 측정 의무.
c- **Lesson dimension mismatch** — weakest 가 Conceptual 인데 Code quality lesson 적용. 위 §2.5 표 참조 강제.
d- **Budget 초과 후 gap 은닉** — handoff 에 *gap 명시* 의무. 임계 미달도 *최선 결과 보존* 으로 종료.

### 5.2 lint autogen 안티 패턴

e- **회귀 정정 commit 에 lint_rule_proposal 누락** — 본 컨벤션 핵심 위반.
f- **rule_id 중복** — registry 가 ValueError raise.
g- **신규 룰이 정정 산출물에 fail** — 룰 자체가 잘못 = 페이즈 11 재진입.
h- **bench 도메인 키워드 룰** (예: "plan must contain crusher") — 도메인 종속 룰. self_lint C-RDR-DOMAIN-AGNOSTIC (TBD) 검증.

## 6. 본 하네스 *우로보로스 자기 강화* 의 메커니즘화

기존 BOOTSTRAP §1: "본 하네스는 자기 자신을 같은 게이트로 평가한다."

본 컨벤션 추가 후: "본 하네스는 자기 자신의 *회귀 학습* 을 *룰로 박아 자기 자신을 더 빡빡하게 평가한다*." → 회차마다 self_lint 룰이 *자동* 누적.

sprint loop (§2) + lint autogen (§3) 결합 = "self-polishing 임계 도달 + 학습 영구 자산화" 두 axis 의 회귀 자기 강화.

## 7. 호환성

- [`budget-saturation-loop.md`](budget-saturation-loop.md) — 본 §2 의 *조기 종료 회피* + 임계 0.999 정정 (default 임계 + 80% budget 사용 강제).
- [`intent-plan-impl-sprint-trinity.md`](intent-plan-impl-sprint-trinity.md) — 본 §2 의 *impl 단위만* → trinity 3 axis 로 확장 (intent / plan / impl 각 ≥ 2 sprint).
- [`tournament-blind-rerun.md`](tournament-blind-rerun.md) — 본 §2 의 sprint-level 임계 미달 시 *project-wide* lesson 적용 + 임계 미달 시 anonymize 재경합.
- [`domain-failure-patterns.md`](domain-failure-patterns.md) — 본 §3 정합 (회귀 정정 시 도메인 어댑터 failure_patterns 누적).
- [`regression-tdd-gate.md`](regression-tdd-gate.md) — sprint iteration trigger + regression_log binary search (별도 컨벤션 유지).

## 8. 통합 history (sprint-37 PR-AE)

본 컨벤션은 sprint-37 PR-AE (다이어트) 에서 **`sprint-regression-loop`** (sprint-08 v0.9.8, 페이즈 10) + **`regression-derived-lint-rule-autogen`** (sprint-10 v0.9.16, 페이즈 11) 두 컨벤션을 단일 컨벤션의 §2/§3 두 layer 로 통합. 책임 = "self-polishing + 우로보로스 자기 강화" 단일, 두 layer = sprint loop (페이즈 10) / lint autogen (페이즈 11). `regression-tdd-gate` 는 별도 컨벤션 유지 (다른 책임 axis: TDD gate trigger). 매핑은 [`MIGRATION.md`](MIGRATION.md) 단일 source.
