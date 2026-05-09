---
id: convention-traceability
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Convention Traceability — 컨벤션 발현 추적

## 한 줄 요약

**41 컨벤션 중 cold session 에서 *실제로 인용·발현된 것* 을 산출물 frontmatter `applied_conventions: [...]` 로 추적 의무.** v0915-cold01 진단 — *준비한 컨벤션이 동작했는지* 자체 검출 메커니즘 0 이었음. self_lint C-CT 가 회차의 컨벤션 활용률 (count + ratio) 검증.

## 1. 결손 진단

본 하네스에 41 컨벤션 (v0.9.15) 이 박혀있지만, cold session 종료 후 다음 질문에 답할 수 없었음:

- *어느 컨벤션이 실제로 페이즈 산출물에 반영됐는가?*
- *어느 컨벤션이 명시되었지만 한 번도 인용 안 됐는가?*
- *낮은 활용률 컨벤션이 점수 갭의 원인인가, 아니면 케이스에 부적합한가?*

→ "준비한 게 동작 안 했다" (사용자 가설 1) 가 발생해도 *검출 불가능*. 본 하네스의 자기 강화 루프 (BOOTSTRAP) 가 컨벤션 신규에만 집중, *발현 검증* 부재.

## 2. 운영 룰

### Step 1 — 산출물 frontmatter `applied_conventions` 의무

각 페이즈 산출물의 frontmatter 에 신규 필드:

```yaml
applied_conventions:
  - interview          # 페이즈 04 답안 형식이 두괄식·1질의·숫자 5개 룰 준수
  - autonomy           # Q-D1~D9 사전 위임 매핑
  - plan-tree          # 페이즈 06 N universe 토너먼트
  - aide-tree          # universe 별 sequenceDiagram 강제 (depth) + multi-phase multiverse 확장 (breadth)
  ...
```

각 항목 = 컨벤션 파일명 (확장자 없음). 본문에 *실제로* 해당 컨벤션의 룰을 따랐을 때만 등재.

### Step 2 — 페이즈 별 *expected* 컨벤션 카탈로그

`conventions/contracts.md` 의 frontmatter 표에 페이즈별 *expected* 컨벤션 매핑 추가:

| 페이즈 | expected 컨벤션 (의무) | optional |
|---|---|---|
| 04 | interview, autonomy, stack, runtime-prereq | nfr-derivation |
| 06 | plan-tree, aide-tree (§3 symmetry), competition, models | aide-tree (§2 multi-phase), ensemble-synthesis-default |
| 08 | test-invariants, multiverse-impl-fan-out, interface-first-parallel-impl | dacapo |
| 10 | sprint-regression-loop, budget-saturation-loop, lessons | parallel-cold-review |
| 14 | score-rubric-objectivity, deliverable-hurdle-supremacy | — |
| ... | ... | ... |

산출물의 `applied_conventions` 가 expected 의 부분집합 X = self_lint fail.

### Step 3 — 회차 누적 활용률 보고

`scoring/convention_usage.py` 신규 (또는 self_lint 모듈) — cold session 종료 후 산출물 트리 스캔:

```
Convention usage report — synthetic_mine_throughput_v0915_cold01:
  applied:  21 / 41 (51.2%)
  high (≥3 phases): plan-tree, autonomy, contracts, interview
  medium (1-2 phases): 17 conventions
  zero-applied: 13 conventions
    [budget-saturation-loop, score-rubric-objectivity, ...]   # 적용 누락 의심
```

zero-applied 컨벤션이 *expected 카탈로그* 와 교집합이면 self_lint fail.

## 3. self_lint 룰

`scoring/self_lint.py` C-CT (신규):

```python
def lint_convention_traceability(skill_root: Path) -> list[str]:
    errors = []
    contracts = (skill_root / "conventions" / "contracts.md").read_text(encoding="utf-8")
    # 1. contracts.md 가 페이즈별 expected catalog 본문 포함
    if "applied_conventions" not in contracts:
        errors.append("contracts.md missing applied_conventions frontmatter spec")
    if "expected 컨벤션" not in contracts and "expected conventions" not in contracts:
        errors.append("contracts.md missing per-phase expected conventions table")
    # 2. self_lint 또는 별도 모듈에 convention_usage 함수 존재
    self_lint_body = (skill_root / "scoring" / "self_lint.py").read_text(encoding="utf-8")
    if "convention_usage" not in self_lint_body and not (skill_root / "scoring" / "convention_usage.py").exists():
        errors.append("convention_usage measurement function missing")
    return errors
```

본 룰은 *컨벤션 자체* 검증 — cold session 산출물 검증은 별도 모듈 (실 회차 시 호출).

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- `applied_conventions` 필드 = generic 메타데이터, 도메인 X.
b- expected 카탈로그 = 페이즈별 컨벤션 매핑, 도메인 X.
c- 활용률 메트릭 (count + ratio) = generic 정량.
d- 본 컨벤션은 *모든 회차* (simulation-bench / 외부 repo / 본 저장소 자기 평가) 에 동일 적용.

## 5. 안티 패턴

a- **`applied_conventions` 누락한 산출물** — frontmatter 가 자동 fail (C14 의 확장).
b- **모든 컨벤션을 무차별 등재** — *실제 인용* 만 등재 의무. 형식 통과 위한 dump 는 self_lint C-CT-HONEST 추가 검증 (TBD).
c- **expected 카탈로그 변경 없이 컨벤션 신규 추가** — 신규 컨벤션이 어느 페이즈의 expected 인지 contracts.md 에 명시 의무.
d- **zero-applied 컨벤션 무시** — 회차 종료 시 zero-applied 가 *expected* 와 교집합이면 페이즈 11 회귀 분류 (impl defect) 트리거.

## 6. budget-saturation-loop / score-rubric-objectivity 와의 합성

- budget-saturation-loop: budget *quantity* (≥80% 사용)
- score-rubric-objectivity: score *quality* (evidence 1:1)
- **convention-traceability**: convention *발현 검증* (적용 vs 미적용)

세 컨벤션 합성 시 — 매 sprint 의 *content depth lesson* 을 (a) 가장 큰 evidence_missing 항목 + (b) zero-applied 컨벤션 중 expected 와 교집합 의 *둘 모두* 채우도록 강제. 진짜 0.999 도달 + 컨벤션 활용률 80%+ 동시.

## 7. 자기 검증

본 컨벤션 자체에 적용 — 본 README / SKILL.md 가 본 컨벤션을 인용했는지 self_lint 가 검증. 적용 회차 = v0.9.16 sprint-10.
