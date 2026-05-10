---
name: Sprint-51
sprint_type: rule-addition
version: 0.9.51
---

# Sprint-51 — v0.9.51 — Extension Invoke Closure + Prompt-Driven Harness

> 시작: 2026-05-10 (g4-v4 96 회차 직후 진단 시점, 사용자 직접 지시 후 plan 재정렬)
> 사용자 직접 지시 (요지):
> - g4-v4 96 = 95 plateau 첫 돌파, 그러나 sprint-50 9 HARD-RULE 산출물 *대부분 invoke 안 됨*
> - reviewer 약점 3 건 (token_usage / warmup / intervention.category) 은 *벤치마크 도메인 의존* 표면 — 본 하네스는 *일반 구조 룰* 만 (`feedback_harness_strengthening_methodology.md` 정합)
> - **추가 (재정렬)**: *"benchmarks/001_synthetic_mine_throughput/prompt.md 프롬프트를 이해하고 벤치마크 도메인 미의존 프롬프트 이해와 확장 사고를 가능하게 해서 token_usage / warmup / intervention.category 약점을 개선해야 함"*

본 sprint 의 *진짜 핵심* = **prompt-driven harness** 패러다임 도입. *프롬프트 자체* 가 모든 후속 게이트의 source.

---

## 0. 진단 — *왜* 본 sprint 인가 (재정렬)

### 0-1. g4-v4 발견의 *기저 진단*

reviewer 약점 3 건 (token_usage / warmup / intervention.category) 의 *진짜* 기저는:

> agent 가 *프롬프트의 명시적 메타-요구* 를 자동 catch 하지 못하고, *cold session 외부의 사용자 도메인 지식* 에 의존한다.

본 prompt.md (`benchmarks/001_synthetic_mine_throughput/prompt.md`) 직접 분석 → *명시 메타-요구* catalog:

| Prompt 본문 위치 | 메타-요구 | reviewer 약점 매핑 |
|---|---|---|
| line 311 *"Use meaningful values rather than zeros"* | **default value 0 사용 시 정당화 의무** 명시 | warmup=0 약점 직접 |
| line 282-309 `summary.json` schema (24 fields) | 모든 field non-null 의무 | token_usage / intervention.category 약점 직접 |
| line 261-271 `results.csv` columns (10 fields) | 모든 column 의무 | placeholder 약점 일반 |
| line 322-336 `event_log.csv` columns (12 fields) | 모든 column 의무 | placeholder 약점 일반 |
| line 14-21 6 decision questions | README 답변 의무 | Results 차원 일반 |
| line 345-356 README 11 의무 항목 | README 본문 grep 의무 | README quality 일반 |
| line 100, 228, 373 부정 표현 (anti-pattern) | static calculation / silent failure / manually fabricated 금지 | Conceptual / Simulation 일반 |
| line 461 *"reasonable token and tool usage, where measurable"* | token_usage 명시 측정 의무 | token_usage 약점 직접 |

**핵심 발견**: reviewer 가 짚은 3 약점 *모두* prompt 본문에 *명시 메타-요구* 로 박혀 있다. 즉 본 하네스가 prompt 를 *자동 parse* 했다면 자동 catch 가능했을 것.

### 0-2. *벤치 무관* 일반 패러다임

prompt 의 *공통 markdown 패턴* 만 추출 — 도메인 의존 0:

- **code block** (```` ``` ````) → output schema field list
- **numbered list** (`1. ... 2. ...`) → 의무 항목 list
- **bullet list** + table → field catalogs
- **부정 표현 catalog** (`not / avoid / should fail / not sufficient / instead of / rather than`) → anti-pattern catalog
- **명시 numeric** (`8-hour`, `30 replications`, `95%`) → constraint catalog
- **조건부 표현** (`where applicable`, `where measurable`, `if appropriate`) → optional-but-required-if-met catalog

이건 LLM 의미 parse 가 아닌 *structural markdown parse* — 단순 정규식. 도메인 무관.

---

## 1. 본 sprint 의 단일 의도 (재정렬)

> **prompt-driven harness** — *프롬프트 메타-요구 catalog* 가 후속 모든 페이즈의 source. agent 의 hidden intent / placeholder grep / default justification / anti-pattern 검사 모두 *prompt-meta 카탈로그* 가 입력.

---

## 2. 6 PR 매핑 (재정렬)

### PR-A — `prompt_meta_extractor.py` 신규 CLI (본 sprint 의 *핵심*)

`scoring/prompt_meta_extractor.py`:

입력: `--prompt-file <path>` (또는 `--prompt-glob` 패턴)

출력: `intent/00-prompt-meta.json`:

```json
{
  "schema_version": "0.9.51",
  "prompt_path": "benchmarks/001_synthetic_mine_throughput/prompt.md",
  "output_schemas": [
    {
      "file": "results.csv",
      "fields": ["scenario_id", "replication", ...],
      "field_count": 10,
      "required": true,
      "extraction_marker": "## `results.csv`"
    },
    {
      "file": "summary.json",
      "fields": [...],
      "field_count": 24,
      "extraction_marker": "## `summary.json`"
    }
  ],
  "readme_required_items": ["How to install dependencies", ...],
  "decision_questions": ["What is the expected ore throughput...", ...],
  "evaluation_dimensions": [
    {"name": "Conceptual modelling", "criteria": [...]},
    ...
  ],
  "anti_patterns": [
    {"phrase": "static calculation", "context": "...", "category": "implementation"},
    {"phrase": "silently producing misleading results", "context": "...", "category": "robustness"},
    {"phrase": "manually fabricated", "context": "...", "category": "fabrication"}
  ],
  "explicit_constraints": [
    {"text": "Simulate an 8-hour shift", "kind": "duration"},
    {"text": "Run at least 30 replications", "kind": "count"},
    {"text": "95% confidence intervals", "kind": "statistical"}
  ],
  "default_warnings": [
    {"phrase": "Use meaningful values rather than zeros", "scope": "summary.json fields"}
  ],
  "conditional_obligations": [
    {"text": "where applicable", "context": "results.csv columns"},
    {"text": "where measurable", "context": "token and tool usage"}
  ]
}
```

본 CLI = *벤치 무관* 일반 markdown parser. domain knowledge 0.

self-test: 본 prompt.md 에 직접 호출 → 8 카탈로그 추출 결과 (위 표 매핑) 검증.

**실 sandbox 결과 (2026-05-10, `benchmarks/001_synthetic_mine_throughput/prompt.md` 에 직접 호출):**

| 카탈로그 | 추출 수 | 검증 |
|---|---:|---|
| output_schemas | **3/43 fields** | `results.csv` (10) + `summary.json` (21) + `event_log.csv` (12) — 모든 prompt 본문 schema 정확 |
| readme_required_items | **11** | README §1~11 (사용자 prompt 본문 정확 매치) |
| decision_questions | **6** | 6 operational decision questions |
| evaluation_dimensions | **8** | Conceptual / Data / Simulation / Experimental / Results / Code / Traceability / Efficiency |
| anti_patterns | 6 | "not sufficient" / "silently producing" / "rather than" / "instead of" 등 |
| explicit_constraints | 2 | "8-hour" / "30 replications" 등 |
| default_warnings | 2 | "Use meaningful values rather than zeros" / "non-trivial" 등 |
| conditional_obligations | 6 | "where applicable" / "where measurable" / "if appropriate" 등 |

reviewer 약점 3 건 직접 매핑 검증:
- token_usage 누락 → `conditional_obligations` "where measurable" + `output_schemas` summary.json fields placeholder grep
- warmup=0 정당화 → `default_warnings` "meaningful values rather than zeros" 자동 trigger
- intervention.category placeholder → `output_schemas` fields + placeholder grep

self-test (embedded fixture) PASS: 3 decisions / 3 readme / 2 schemas / 4 anti / 2 defaults.

### PR-B — Phase 1.5 + 9 신규 CLI invoke literal Bash 박기 + prompt-meta seed

기존 sprint-50 의 9 룰 invoke 갭 closure (sprint-43 패러다임 재적용) + Phase 1.5 의 hidden intent 가 *prompt-meta 카탈로그* 를 자동 seed:

- Phase 1.5 진입 시 `intent/00-prompt-meta.json` *없으면* `prompt_meta_extractor.py` 의무 호출
- Phase 1.5 의 `01-hidden-intent.md` 항목 = *prompt-meta 의 anti_patterns + default_warnings + conditional_obligations* 자동 list
- 즉 agent 가 *프롬프트 너머* 사고를 자력 발굴할 필요 X — *프롬프트 본문에 박힌 메타-요구* 부터 자동 catch

### PR-C — `placeholder_grep.py` 신규 CLI (일반 룰, prompt-meta 입력)

`scoring/placeholder_grep.py`:

- prompt-meta 의 `output_schemas` 의 모든 field 가 *placeholder 아닌* 값으로 채워졌는지 검사
- sentinel 카탈로그: `unrecorded` / `unknown` / `TBD` / `placeholder` / `pending` / `null` value / `?` / `<insert>` / `<replace>` + numeric `0` (default_warnings 매치 시만)
- surrender_phrase_grep 의 sister CLI

vacuous PASS 차단:
- comment `# placeholder-ok:` prefix escape, 단 escape ≥ 50% = 의심 fail

### PR-D — `default_value_justification` rule (Phase 1.5 inline)

prompt-meta 의 `default_warnings` 카탈로그가 자동 트리거:

- `Use meaningful values rather than zeros` 매치 → agent 가 산출물에 numeric `0` / `null` / `"none"` default 사용 시 본문에 reasoning 의무
- Phase 1.5 의 10 카테고리 catalog 에 `default-justification` sub-rule 추가 (`validation` 카테고리 inline)

### PR-E — `refactor_not_rewrite_ratio.py` sprint type frontmatter

sprint-50 sandbox §4-1 후속. 일반 적용:

```yaml
---
sprint_type: rule-addition | refactoring | feature | bug-fix
---
```

본 CLI 가 sprint_type 별 적용 여부 자동 판정.

### PR-F — sprint 마감 v0.9.51

- skill_version 0.9.50 → 0.9.51
- CHANGELOG sprint-51 entry
- memory entry 신규 (`project_sprint51_v0951.md` + `feedback_prompt_driven_harness.md`)
- sprint-51 report.md
- g4-v4 review doc cross-link

---

## 3. HARD-RULE 신규

| ID | 페이즈 | 본문 |
|---|---|---|
| 9.kkk | 04 / 1.5 entry | `prompt_meta_extractor.py` 의무 호출 — `intent/00-prompt-meta.json` emit |
| 9.lll | all | `placeholder_grep.py` PASS — prompt-meta 의 output schema fields 입력 |
| 9.mmm | 1.5 | default-justification sub-rule (default_warnings 카탈로그 trigger) |
| 9.nnn | 10 | sprint_type-aware refactor_not_rewrite |

---

## 4. dogfood + 외부 검증 의무

본 sprint 마감 != 본 sprint 검증. **다음 cold session (g4-v5)** 의 외부 평가 결과로 진짜 marker 확인:
- prompt_meta_extractor 가 *진짜로* 호출되어 8 카탈로그 emit
- placeholder grep 이 *진짜로* token_usage / intervention.category 등 catch
- default justification 이 *진짜로* warmup=0 같은 default 를 *왜* 명시하게 만듦
- 96 → 97+ 도전

---

## 5. 반-원칙 (anti-goal)

- 도메인 의존 룰 추가 (token_usage / intervention.category / warmup 같은 *케이스 종속* 룰) — `feedback_harness_strengthening_methodology.md` 정합
- 점수 % targeting framing — `feedback_score_targeting_taboo.md` 정합
- 컨벤션 폴더 신규 추가 — `feedback_convention_diet_paradigm.md` 정합 (페이즈 본문 + CLI 우선)
- LLM 기반 prompt 의미 parse — 단순 markdown structural parse 만 (재현성 + 가시성)

---

## 6. 패러다임 명명 — *Intent Recursion via Prompt-Meta*

사용자 직접 인용 (2026-05-10, plan 재정렬 직후):

> *"이 자체가 우리 intent 가 회귀하며 숨은 의도를 모두 채우는 방식의 이유야"*

본 sprint 의 *진짜* 패러다임은 *prompt-driven* 이 아니라 **Intent Recursion** — *재귀*. 본 하네스의 기존 페이즈 01 refresh-1 / refresh-2 cycle 이 이미 *intent 회귀* 메커니즘이고, 본 sprint 는 그 회귀의 *seed* 를 자동화하는 것.

### 6-1. 회귀 cycle 의 통합 view

```
prompt.md
  ↓ [PR-A] prompt_meta_extractor.py
intent/00-prompt-meta.json (8 catalog: schemas / decisions / anti-patterns / default-warnings / ...)
  ↓ seed
phase 01 intent/01-intent.md (사용자 의도)
  ↓ refresh-1 (페이즈 01-{1..4})
intent/01-{1..4}-intent.md (mindmap 깊이 1)
  ↓ phase 04 Q&A + autonomy + stack + verification
intent/04-*.md
  ↓ [sprint-50] Phase 1.5 — hidden intent 발굴 (prompt-meta 카탈로그 입력 + agent 추가 발견)
intent/01-{hidden-intent, extension-scope, extension-trace}.md
  ↓ refresh-2 (페이즈 05 critique + 페이즈 01-{1..4}.v2)
intent/01-{1..4}-intent.v2.md + 04-refreshed + 05-refreshed
  ↓ phase 06 plan tournament — universe 가 prompt-meta 카탈로그 직접 반영
plan/...
  ↓ phase 08 impl — placeholder grep + default justification (prompt-meta 카탈로그 입력)
impl/... + 산출물
  ↓ phase 09 quality gate — anti-pattern grep
quality/...
  ↓ phase 14 handoff — knowledge portfolio (prompt-meta 의 조건부 의무 충족 여부)
handoff/14-handoff.md
```

회귀의 *fixed point* = prompt-meta 의 모든 카탈로그가 산출물에 *trace* 됨. trace 0 = phase 09 fail = phase 08 재진입 = refresh 반복.

### 6-2. 회귀의 *seed* vs *sink*

| 역할 | 산출물 | 도입 sprint |
|---|---|---|
| **seed** (cycle 시작) | `intent/00-prompt-meta.json` | **sprint-51 (본 sprint)** |
| 1 차 발견 | `intent/01-intent.md` 의 §a~§i | sprint-13 (이전) |
| 회귀 1 | `intent/01-{1..4}-intent.md` (mindmap) | sprint-13 (이전) |
| **숨은 발굴** | `intent/01-hidden-intent.md` | **sprint-50** |
| 회귀 2 | `intent/01-{1..4}-intent.v2.md` + `*-refreshed.md` | sprint-13 (이전) |
| critique | `intent/05-critique.md` + `05-decisions.md` | sprint-04 (이전) |
| **sink** (cycle 종료) | `phase 09 quality gate` 의 *모든 prompt-meta 카탈로그 trace* | **sprint-51 (본 sprint)** |

본 sprint = *seed + sink* 동시 도입 — 기존 회귀 cycle 의 *양 끝* 에 prompt-meta 박힘. 회귀 자체는 이미 존재 (sprint-13 mindmap fan-out + refresh-1/2).

### 6-3. layer 통합

본 하네스 enforcement 의 *4 번째 layer* (sprint-40 의 5 layer 정합):

| Layer | 도입 sprint | 본문 | recursion role |
|---|---|---|---|
| 1 | sprint-30 | 컨벤션 본문 | static spec |
| 2 | sprint-37~39 | self_lint enforcement | content check |
| 3 | sprint-40~43 | runtime CLI invoke (declared = invoked) | runtime gate |
| **4** | **sprint-51** | **prompt-meta seed + recursion sink** | **fixed-point loop closer** |

회귀 = sprint-13 의 refresh-1/2 + sprint-50 의 Phase 1.5 hidden intent + sprint-51 의 prompt-meta 가 *합쳐서* 완성.

---

## 7. 후속

본 plan = *재정렬 초안*. PR-A 진입 시점에 prompt_meta_extractor.py 의 정확한 markdown parse 휴리스틱 catalog 확정 후 보강.
