---
id: cross-universe-lesson-distillation
category: sprint
applies-to-phases: '[06,11]'
applies-to-grades: '[G4,G5]'
trigger-when: 'universe 패배 흡수'
indexed-in: conventions/INDEX.md
---

# Cross-Universe Lesson Distillation — 패배 universe 의 lessons 우승 본문 흡수

## 한 줄 요약

**Tournament resolve 시 *우승 universe 만 채택* (또는 ensemble union) 으로 끝나지 않고, *패배 universe 의 핵심 약점 ≥ 1-2 줄* 을 우승 본문에 흡수 의무.** 본 하네스의 차별 동력 AIDE 멀티버스의 *learned weakness transfer* missing piece. v0.9.13 ensemble-synthesis-default 의 *합집합* 외에 *교집합 + 차이집합* 까지 합성.

## 1. 결손 진단

[`plan-tree.md`](plan-tree.md) (v0.6.0) + [`competition.md`](competition.md) (v0.6.0) + [`ensemble-synthesis-default.md`](ensemble-synthesis-default.md) (v0.9.13) 의 결과:

- 우승 universe → `plan/06-plan.md` 사본 + 머지 패치
- 패배 universe → `plan/candidates/losers/` 보존
- ensemble synthesis = *합집합* (우승 + 다른 우주의 차별 강점)

→ 패배 universe 의 *핵심 약점* (예: "minimal-subtraction universe 가 시도한 단일 모듈 합치기는 SoC 위반으로 5 차원에서 fail") 이 *우승 본문에 박히지 않음*. 다음 페이즈 (08 구현 / 10 sprint) 가 *같은 약점을 재발견* 할 위험.

multiverse 의 *forward exploration* 강점이 *learned weakness backward transfer* 까지 확장 안 됨.

## 2. 운영 룰

### Step 1 — 패배 universe 의 핵심 약점 추출

각 패배 universe 의 `meta.md` (또는 plan-reviewer 의 4 답) 에서 *결정적 약점 reason* 을 1-2 줄로 추출:

```python
def extract_loser_weakness(loser_meta: dict) -> str:
    # 채점 5 차원 중 가장 낮은 차원 + 그 사유
    scores = loser_meta["score"]
    weakest_dim = min(scores, key=scores.get)
    reason = loser_meta["plan_reviewer_4_answers"]["question_3"]  # "과소 명세·과대 사이즈·순서 어긋남이 보이는 TODO?"
    return f"{loser_meta['universe_id']}: weakest={weakest_dim} ({scores[weakest_dim]:.2f}) — {reason}"
```

### Step 2 — 우승 본문에 *흡수 절* 의무

`plan/06-plan.md` (우승 universe 사본) 에 신규 절 *"## Patterns to Avoid (from defeated universes)"*:

```markdown
## Patterns to Avoid (from defeated universes)

본 우승 universe (universe-1-domain-first) 가 채택되었으나, 패배 universe 가 시도한 다음 패턴은 본 페이즈 08 구현 시 *명시 회피*:

- **universe-2-adapter-first**: weakest=simplicity (0.65) — 모든 도메인에 포트 인터페이스 강제로 보일러플레이트 비대 (4 어댑터 × 5 메서드 = 20 인터페이스). 본 우주는 단일 도메인에 인터페이스 X.
- **universe-3-minimal-subtraction**: weakest=test_topology (0.78) — 모듈 합치기로 단위 테스트 표면적 부족 (단일 모듈에 5 책임). 본 우주는 페이즈 08 시 단일 모듈 분할 검토 의무.
```

### Step 3 — 페이즈 08 구현 시 *avoid_patterns* 입력 의무

`impl/08-impl-log.md` 의 inputs:

```yaml
plan_source: plan/06-plan.md
avoid_patterns:                         # 페이즈 06 의 흡수 절 자동 추출
  - "포트 인터페이스 강제 (단일 도메인 시)"
  - "모듈 합치기 (테스트 표면 부족)"
verification: 페이즈 08 산출물이 avoid_patterns 위반 시 자동 fail
```

`agents/implementer.md` 가 avoid_patterns 를 *forbidden_strategies* 와 동급으로 처리 (lessons.md 정합).

### Step 4 — 페이즈 10 sprint 시 transfer 추적

sprint NN 의 inputs.json 에 `avoid_patterns_inherited: [...]` 명시. self_lint 가 sprint 회차 동안 avoid_patterns 위반 0 건 검증.

## 3. self_lint 룰

`scoring/self_lint.py` C-CULD (신규):

```python
def lint_cross_universe_lesson_distillation(skill_root: Path) -> list[str]:
    errors = []
    culd = (skill_root / "conventions" / "cross-universe-lesson-distillation.md").read_text(encoding="utf-8")
    plan_tree = (skill_root / "conventions" / "plan-tree.md").read_text(encoding="utf-8")
    ensemble = (skill_root / "conventions" / "ensemble-synthesis-default.md").read_text(encoding="utf-8")
    # 1. plan-tree + ensemble 가 본 컨벤션 cross-reference
    if "cross-universe-lesson-distillation" not in plan_tree:
        errors.append("plan-tree missing cross-universe-lesson-distillation cross-ref")
    if "cross-universe-lesson-distillation" not in ensemble:
        errors.append("ensemble-synthesis-default missing cross-universe-lesson-distillation cross-ref")
    # 2. 본 컨벤션 키워드
    required = ["Patterns to Avoid", "avoid_patterns", "extract_loser_weakness", "weakest_dim"]
    for kw in required:
        if kw not in culd:
            errors.append(f"cross-universe-lesson-distillation missing keyword: {kw}")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- weakest_dim 추출 = 5 차원 중 min, 도메인 X.
b- avoid_patterns 흡수 절 = 일반 markdown 절, 도메인 X.
c- 페이즈 08 / 10 의 forbidden_strategies 매핑 = lessons.md 의 generic 패턴 재사용.

## 5. 안티 패턴

a- **우승 universe 만 채택 + 패배 즉시 losers/ 폐기** — 학습 전이 0. 본 컨벤션 핵심 위반.
b- **흡수 절 형식적** — "패배 universe 가 있다" 만 박고 *실 weakest_dim + reason* 없음. self_lint C-CULD-DETAIL (TBD) 추가 검증.
c- **avoid_patterns 페이즈 08 미반영** — implementer 가 avoid_patterns 를 forbidden 으로 처리 안 하면 lessons.md 위반 동급.

## 6. ensemble-synthesis-default 와의 합성

| 컨벤션 | 합성 차원 |
|---|---|
| ensemble-synthesis-default | *합집합* (우승 + 다른 우주의 강점) |
| **cross-universe-lesson-distillation** (본) | *차이집합* (패배 우주의 약점 → 회피) |

두 합성 = 진짜 *forward + backward* multiverse — 우주 N 의 *모든 학습* 이 다음 페이즈로 전이.

## 7. 자기 검증

본 컨벤션 자체에 적용 — 본 컨벤션이 *어떤 패배 universe 시뮬레이션* 을 통해 도출됐는지 본문에 박혀야 함. 본 회차 에서는 v0915-cold01 의 단일 universe 패턴 (multiverse 발현 부족) 이 *meta-loser*. 다음 회차에서 본 컨벤션 자체 적용.
