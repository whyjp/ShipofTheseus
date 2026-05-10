# Sprint-51 — v0.9.51 — Extension Invoke Closure (plan 초안)

> 시작: 2026-05-10 (g4-v4 96 회차 직후 진단 시점)
> 사용자 직접 지시 (요지):
> - g4-v4 96 = 95 plateau 첫 돌파, 그러나 sprint-50 9 HARD-RULE 산출물 *대부분 invoke 안 됨*
> - reviewer 약점 3 건 (token_usage / warmup / intervention.category) 은 *벤치마크 도메인 의존* 표면 — 본 하네스는 *일반 구조 룰* 만 적용 (`feedback_harness_strengthening_methodology.md` 정합)

본 sprint 는 두 트랙 — *invoke 갭 closure* + *일반화 hygiene*.

---

## 0. 진단 — *왜* 본 sprint 인가

### 0-1. g4-v4 cold session 직접 증거 (`docs/reviews/2026-05-10-bench-001-g4v4-96-attribution.md`)

- v0.9.50 g4-v4 = **96/100** ← 역대 최고 (이전 v0.9.44 95)
- 그러나 sprint-50 의 9 HARD-RULE 산출물 대부분 *invoke 안 됨*:
  - `intent/01-{hidden-intent,extension-scope,extension-trace}.md` ❌ 부재
  - `plan/candidates/universe-N/meta.md` 의 `philosophy:` 필드 ❌ 부재 (Approach prose 만)
- +5pt attribution: sprint-50 직접/사상 +2pt (Experimental + Conceptual) / 본 회차 자체 향상 +3pt

### 0-2. sprint-43 declared ≠ invoked 갭 *재발*

sprint-43 (v0.9.48) 이 *기존 phase 06/08/09/10/14* 에 literal Bash command 박았다. **그러나 sprint-50 의 신규 *Phase 1.5* + 9 신규 CLI 는 orchestrator phase walkthrough 에 박히지 않음** — sprint-43 패러다임이 *신규 룰에 자동 적용되지 않는 구조적 결함*.

### 0-3. reviewer 약점 3 건의 *기저 패턴*

| 도메인 표면 | 기저 패턴 (일반) |
|---|---|
| token_usage.json 누락 | self-measurement artifact 의 non-null 필드 누락 |
| warmup=0 정당화 부재 | agent 가 의식적 default 선택 시 *왜* 안 적는 패턴 |
| intervention.category: unrecorded | placeholder 채우기 잊는 패턴 |

3 약점 → *일반 룰 2 종* (placeholder grep + default justification) 으로 catch.

`feedback_harness_strengthening_methodology.md` 정합 — 본 하네스 강화는 *케이스 종속 patch* 가 아닌 *prompt→게이트 흐름의 구조 변경*.

---

## 1. 본 sprint 의 단일 의도

> **sprint-50 의 *완성*** — 9 HARD-RULE 의 invoke 갭 닫기 + reviewer 약점의 *기저 패턴* 을 일반 룰로 룰화.

---

## 2. 5 PR 매핑

### PR-A — Phase 1.5 + 9 신규 CLI invoke literal Bash 박기

orchestrator phase walkthrough (`skills/theseus-orchestrator/SKILL.md` 의 phase walkthrough §) 에 Phase 1.5 신규 entry + sprint-50 9 CLI 의 literal Bash command 박힘.

추가 phases 본문 patch:
- `phases/01-5-hidden-intent.md` 의 *§자동 CLI 호출 literal Bash* 가 이미 박혀 있음 — 그러나 orchestrator SKILL.md 의 phase walkthrough 에 *해당 페이즈 entry 자체* 가 부재. 추가.
- `phases/06-plan.md` / `phases/08-implement.md` / `phases/09-quality-gates.md` / `phases/10-test-loop.md` / `phases/14-handoff.md` 의 sprint-50 § 본문에는 박혀 있지만 orchestrator phase walkthrough 에 sprint-50 신규 9 CLI 가 catalog 미포함.

자동 검증: `phase_invoke_audit.py` 가 sprint-50 9 CLI 모두 trace.

### PR-B — `placeholder_grep.py` 신규 CLI (일반 룰)

`scoring/placeholder_grep.py` — sentinel 카탈로그 산출물 본문 + frontmatter + YAML / JSON 검사:

```python
PLACEHOLDER_SENTINELS = [
    'unrecorded', 'unknown', 'TBD', 'placeholder', 'pending',
    'TODO', 'FIXME', 'XXX', '???', '<insert>', '<replace>',
    # YAML/JSON null 패턴
    'null', '~', 'None',  # only as field VALUE (key 는 제외)
    # numeric placeholder
    '-1', '0.0', # context-dependent — opt-in only
]
```

- surrender_phrase_grep 의 sister CLI — 도메인 무관, 모든 cold session 적용
- 적용: phase 09 quality gate + phase 14 handoff entry
- vacuous PASS 차단:
  - sentinel grep 만으로는 *legitimate* 사용 (코드 본문 의 `0.0` 상수 등) false positive 가능
  - escape: comment `# placeholder-ok:` prefix 또는 explicit `intent/04-autonomy.md` 답안 매핑

### PR-C — `default_value_justification` rule (Phase 1.5 inline 또는 별도 CLI)

agent 가 의식적 default 선택 시 reasoning 의무. 두 옵션:

- 옵션 A (inline): Phase 1.5 의 10 카테고리 catalog 에 `default-justification` sub-rule 추가 (`validation` 카테고리 inline). HI-NN 항목으로 *agent 가 default 사용 한 모든 numeric/categorical 결정* 이 catalog 에 등록.
- 옵션 B (separate CLI): `default_value_justification.py` 신규 — YAML / JSON 산출물 의 numeric default 값 검출 + 산출물 본문 grep 으로 *justification* 찾기.

**default A 권고** — Phase 1.5 의 의도와 정합 (확장 사고 = 의식적 결정). 별도 CLI 신설 = 컨벤션 다이어트 위반 가능.

### PR-D — `refactor_not_rewrite_ratio.py` sprint type frontmatter

sprint-50 sandbox §4-1 노출 — 본 CLI 의 적용 대상 명확화. sprint frontmatter 에 `sprint_type` 신규 필드:

```yaml
---
name: Sprint-NN
sprint_type: rule-addition | refactoring | feature | bug-fix
---
```

본 CLI 가 sprint_type 별 적용 여부 자동 판정:
- `rule-addition` → skip (적용 대상 외)
- `refactoring` / `feature` / `bug-fix` → modified ratio ≥ 0.3 의무

### PR-E — sprint 마감 v0.9.51

- skill_version 0.9.50 → 0.9.51
- CHANGELOG sprint-51 entry
- memory entry 신규
- sprint-51 report.md

---

## 3. HARD-RULE 신규

| ID | 페이즈 | 본문 |
|---|---|---|
| 9.kkk | all | placeholder_grep.py PASS — sentinel 카탈로그 + escape comment |
| 9.lll | 1.5 | default-justification sub-rule (HI-NN 항목으로 agent default 결정 catalog) |
| 9.mmm | 10 | sprint_type-aware refactor_not_rewrite (sprint_type ∈ {refactoring, feature, bug-fix} 시만 적용) |

(9.nnn, 9.ooo 는 본 sprint 자체에서 신설 검토 후 PR-E 시점에 결정.)

---

## 4. dogfood + 외부 검증 의무

본 sprint 마감 != 본 sprint 검증. **다음 cold session (g4-v5)** 의 외부 평가 결과로 진짜 marker 확인:
- sprint-50 9 HARD-RULE 산출물이 *진짜로* emit 되는지 (invoke 갭 closure 검증)
- placeholder grep 이 *진짜로* token_usage / intervention.category 등을 catch 하는지
- default justification 이 *진짜로* warmup=0 같은 default 를 *왜* 명시하게 만드는지
- 96 → 97+ 도전

---

## 5. 반-원칙 (anti-goal)

- 도메인 의존 룰 추가 (token_usage / intervention.category / warmup 같은 *케이스 종속* 룰) — `feedback_harness_strengthening_methodology.md` 정합
- 점수 % targeting framing — `feedback_score_targeting_taboo.md` 정합
- 컨벤션 폴더 신규 추가 — `feedback_convention_diet_paradigm.md` 정합 (페이즈 본문 + CLI 우선)

---

## 6. 후속

본 plan 은 *초안*. PR-A 진입 시점에 phase walkthrough 의 정확한 위치 + literal Bash command 의 catalog 확정 후 본 plan 보강.
