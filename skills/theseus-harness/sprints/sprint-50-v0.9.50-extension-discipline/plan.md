# Sprint-50 — v0.9.50 — Extension Discipline

> 시작: 2026-05-10
> 사용자 직접 지시 (요지):
> - *"의도를 이해하고 프롬프트에 적혀있는 이상의 처리를 해야 한다"*
> - *"이해 만으로 멈춰서 그런데 성찰-상상력을 덧대서 추가하면 좋은 작업이나 더 설계를 확장하거나 프롬프트보다 더 확장된 제안을 intent 이후 단계에 추가하는 건 어떨까"*
> - *"지금 남은 점수들 그 이상을 하려면 프롬프트를 지키는 것 이상으로 프롬프트를 실행하고 숨겨진 의도를 파악하는 것"*
> - *"plan/impl 에서도 확장된 사고를 지시해야 한다. 실용주의 프로그래밍, 이펙티브 소프트웨어 설계의 인사이트들을 실제 반영해야 한다. 요구사항 이해와 설계·구현·유지보수·테스트들에 대한 바이블이다"*

본 sprint 는 `feedback_score_targeting_taboo.md` 를 정합한다 — *점수 회복은 결과지 목표 아님*. 본 sprint 의 가치는 *구조* (확장 사고 단계의 부재라는 진단을 페이즈 본문 + CLI enforcement 로 닫는다).

---

## 0. 진단 — *왜* 본 sprint 인가

### 0-1. g4-v3 의 직접 증거 (2026-05-10 cold session)

- **제출 위치**: `D:\github\simulation-bench\submissions\2026-05-10__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4-v3`
- **자동 평가**: 53/53 = 1.000
- **외부 Opus zero-context 평가**: 91/100, SHIP
- **6 차원 손실 위치 — *프롬프트 너머* 영역에 집중**

| 차원 | 손실 | 손실 성격 |
|---|---:|---|
| Conceptual modelling | -2 | 모델이 프롬프트 그대로. 이론 framing 부재 |
| Data + topology | -1 | topology 단순 따라하기 |
| Simulation correctness | -2 | `node_overrides` dead-path |
| **Experimental design** | **-2** | **시나리오 6 개만 / sensitivity sweep · DoE 부재** |
| **Results + interpretation** | **-1** | **해석이 표층 머무름** |
| Code quality | -1 | `_choose_loader` realtime queue 무시 |

**6 차원 손실 중 *최소 3 차원* (Experimental / Results + Conceptual 일부)** 은 코드 디테일이 아니라 *"프롬프트가 묻지 않은 것을 제안 + 실행"* 으로만 채워지는 영역.

### 0-2. 산출물 직접 증거

```
01-additional.md (refresh-1 supplement)  →  단 17 줄 / design decision 1 개
05-decisions.md DEC-10 (7th scenario)   →  loader_balance 1 개 추가 제안
```

이건 *extension* 이 아니라 **supplement**. 페이즈 01–05 의 모든 산출물이 *프롬프트 충실 이행* 패턴이고 *프롬프트 너머의 상상* 단계가 페이즈 본문에 **부재**.

### 0-3. 누적 plateau — 91/94/95 의 천정

| 회차 | 일자 | 점수 | 비고 |
|---|---|---:|---|
| v0.9.44 | 2026-05-09 | **95** | 94 plateau 첫 돌파 (역대 최고) |
| v0.9.45 (1차) | 2026-05-10 | 90 | 회귀 |
| v0.9.45 (2차) | 2026-05-10 | 87 | universe 감소 + 자율 종료 |
| v0.9.47 g4-v2 | 2026-05-10 | 91 | sandbox 검증 |
| **v0.9.49 g4-v3** | **2026-05-10** | **91** | **본 sprint 진단 대상** |

**95 첫 돌파 *이후* 93~91 plateau 를 떠돈다.** sprint-37~49 의 enforcement 누적은 *기존 차원* 에 한해 효과를 냈지만, *프롬프트 너머* 차원은 부재. 이게 본 sprint 의 제거 대상.

---

## 1. 본 sprint 의 단일 의도

> **확장 사고 (Extension Thinking) 를 페이즈 본문 + CLI enforcement 로 박는다.** 의도 → 설계 → 구현 → 유지보수 → 테스트 *전 페이즈* 에서 "프롬프트가 묻지 않은 것" 을 묻고, 답하고, trace 한다.

확장 사고의 *원천* = 사용자 명시 인용 4 권 (이하 "확장 바이블"):

| # | 책 / 출처 | 페이즈 매핑 |
|---|---|---|
| 1 | **The Pragmatic Programmer** (Hunt & Thomas) — 실용주의 프로그래밍 | Phase 1.5 (Tip 53), Phase 08 (Tip 11), Phase 10 (Ch.6), Phase 14 (Ch.1) |
| 2 | **A Philosophy of Software Design** (Ousterhout) — 이펙티브 설계 | Phase 06 (Ch.11), Phase 08 (Ch.4–5), Phase 09 (Ch.10, Ch.13) |
| 3 | **Effective Java/C++** (Bloch / Meyers) — 작은 단위 격언 | Phase 08 (visibility), Phase 09 (immutability) |
| 4 | **요구사항 → 설계 → 구현 → 유지보수 → 테스트 5 단계 표준** | Phase 1.5 / 06 / 08 / 10 / 14 매핑 |

---

## 2. 7 PR 매핑

본 sprint 는 7 PR 로 분할. 각 PR = 독립 commit-merge 페어. 모든 PR 은 *컨벤션 다이어트 패러다임* (`feedback_convention_diet_paradigm.md`) 정합 — 신규 컨벤션 추가는 최후 수단, 우선 페이즈 본문 patch + CLI enforcement.

### PR-A — plan + premortem + 격언 + 전체 design (본 문서)

- `sprints/sprint-50-v0.9.50-extension-discipline/plan.md` (본 문서)
- `sprints/sprint-50-v0.9.50-extension-discipline/premortem.md` — 격언 동·서 1 개씩 + forward simulation + derived improvements (premortem-friction 정합)
- 코드 변경 0

### PR-B — Phase 1.5 (Hidden Intent) — *요구사항 단계*

신규 페이즈 본문: `phases/01-5-hidden-intent.md`

페이즈 04 (Q&A 등) 직후 / 페이즈 05 (Critique) 직전.

3 산출물 페어 (intent/ 군 내부):

| 파일 | 역할 |
|---|---|
| `intent/01-hidden-intent.md` | 프롬프트가 *묻지 않은* "합리적 평가자가 기대할" 항목 ≥5. (Pragmatic Tip 53 — *"Don't gather requirements—dig for them"*) |
| `intent/01-extension-scope.md` | 위를 (must / should / could) 분류 + 본 회차 reach 결정 (≥1 *should* 채택 의무) |
| `intent/01-extension-trace.md` | 채택 extension 이 plan / impl / sprint / README / 코드 어디에든 trace ≥1 — *explicit pointer* 의무 |

3 enforcement CLI:

| CLI | 검사 |
|---|---|
| `scoring/intent_extension_emit.py` | 3 파일 존재 + hidden-intent 항목 ≥5 + should 채택 ≥1 |
| `scoring/extension_to_artifact_trace.py` | 채택 extension 이 plan / impl / sprint / README / 코드 어디에든 grep trace ≥1 |
| `scoring/hidden_intent_originality.py` | extension 이 *프롬프트 직접 인용* 이 아닌지 휴리스틱 (token-overlap ≤ τ) — *진짜 추가* 강제 |

HARD-RULE 9.bbb 신설 (HARD-CORE.md 4000 chars 제약 → INDEX.md router lazy load).

### PR-C — Phase 06 Design-Twice — *설계 단계*

`phases/06-plan.md` patch:

> universe N (G3=3, G4=4, G5=6) 은 *서로 다른 설계 철학* 으로 출발. universe meta.md 의 `philosophy` 필드 의무 (allowed values: `modular` / `oop` / `functional` / `data-driven` / `event-driven` / `actor` / `dsl-first` 등).
>
> 같은 철학 universe ≥2 = fail.

Ousterhout Ch.11 — *"Design It Twice"* 의 enforcement 화. 본 하네스의 *기존 multiverse* 는 *코드만 다름* — 본 PR 은 *설계 철학을 다르게* 강제.

CLI: `scoring/universe_philosophy_distinct.py`

HARD-RULE 9.ccc.

### PR-D — Phase 08 Deep-Module + DRY — *구현 단계*

`phases/08-implement.md` patch.

2 CLI:

| CLI | 검사 | 출처 |
|---|---|---|
| `scoring/deep_module_metric.py` | 모듈별 *public interface 줄 수* / *내부 functional 줄 수* 비율 ≤ τ. 얕은 모듈 (interface 가 implementation 만큼 큰) 검출 | Ousterhout Ch.4 — *"Modules Should Be Deep"* |
| `scoring/dry_violation_count.py` | n-gram (n=8) 코드 token 중복 ≥ k 회 = violation. 임계 ≤ N% | Pragmatic Tip 11 — *"DRY"* |

HARD-RULE 9.ddd + 9.eee.

### PR-E — Phase 09 Define-Errors-Out + Comments-Why — *품질 게이트 단계*

`phases/09-quality-gates.md` patch.

2 CLI:

| CLI | 검사 | 출처 |
|---|---|---|
| `scoring/define_errors_check.py` | 예외 종류 catalog ≥ N + 각 예외 raise/handle pair grep 검사 | Ousterhout Ch.10 — *"Define Errors Out of Existence"* (역방향 강제 — *예외를 정의했다면 *처리* 해라) |
| `scoring/comment_intent_check.py` | comment 가 *코드 paraphrase* 인지 vs *WHY* 인지 휴리스틱 (코드 token 과의 overlap > τ → paraphrase = violation) | Ousterhout Ch.13 — *"Comments Should Describe Things That Are Not Obvious from the Code"* |

HARD-RULE 9.fff + 9.ggg.

### PR-F — Phase 10/14 Refactor-Not-Rewrite + Knowledge-Portfolio — *유지보수 + 회고 단계*

`phases/10-test-loop.md` + `phases/14-handoff.md` patch.

| 항목 | 본문 | 출처 |
|---|---|---|
| Refactor-not-rewrite | sprint loop 의 개선이 *기존 함수/모듈 변경* 비율 ≥ 신규 추가 의무. *전부 추가만* = fail | Pragmatic Ch.6 — *"Refactoring"* |
| Knowledge Portfolio refresh | 페이즈 14 handoff.md 가 *본 회차에서 학습한 통찰 ≥ 3* 명시 (단순 산출물 list 가 아니라 *insight*) | Pragmatic Ch.1 — *"A Pragmatic Philosophy"* |

HARD-RULE 9.hhh + 9.iii.

페이즈 본문 §자동 CLI 호출 literal Bash 박힘 (sprint-43 패러다임 계승) — declared = invoked.

INDEX.md router 등록 — 9.bbb~9.iii lazy load 매핑.

### PR-G — v0.9.50 마감 + CHANGELOG + memory + g4-v3 review doc

- `.claude-plugin/plugin.json` + `skills/theseus-harness/SKILL.md` + `skills/theseus-orchestrator/SKILL.md` frontmatter 0.9.49 → 0.9.50
- `CHANGELOG.md` sprint-50 entry — 본 sprint 의 *구조* framing (점수 X)
- 메모리 신규 entry:
  - `project_sprint50_v0950.md` — 본 sprint 마감 사실
  - `feedback_extension_discipline.md` — *"프롬프트 충실 이행 ≠ 완성. 확장 사고 단계가 별도 page"* 격언화
- `docs/reviews/2026-05-10-bench-001-mine-throughput-91-g4v3-extension-gap.md` — g4-v3 산출물 직접 분석 (intent/ 17 줄 supplement / 6 차원 손실 위치 / 본 sprint design rationale)
- `sprints/sprint-50-v0.9.50-extension-discipline/report.md` — sprint 마감

---

## 3. 9 신규 HARD-RULE 한 표

| ID | 페이즈 | 본문 |
|---|---|---|
| 9.bbb | 1.5 | 페이즈 04 직후 Phase 1.5 emit 의무 (3 산출물 + ≥5 항목 + ≥1 should 채택). 부재 시 phase 05 진입 차단 |
| 9.ccc | 06 | universe N 의 design philosophy distinct ≥ N (G3=3, G4=4, G5=6) — 같은 philosophy ≥2 = fail |
| 9.ddd | 08 | deep_module_metric.py PASS — 모듈별 (interface 줄/internal 줄) 비율 ≤ τ |
| 9.eee | 08 | dry_violation_count.py PASS — n-gram 중복 ≤ N% |
| 9.fff | 09 | define_errors_check.py PASS — 예외 catalog ≥ N + raise/handle pair |
| 9.ggg | 09 | comment_intent_check.py PASS — comment paraphrase ratio ≤ τ |
| 9.hhh | 10 | refactor-not-rewrite ratio — sprint loop 변경/추가 비율 ≥ τ |
| 9.iii | 14 | knowledge portfolio insight ≥ 3 명시 (단순 list 아님) |
| 9.jjj | 1.5 | extension_to_artifact_trace.py PASS — 채택 extension trace ≥1 |

(9.kkk 는 보류 — 본 sprint 에서 신설 검토 후 PR-F 시점에 결정.)

---

## 4. 외부 검증 의무 — *dogfood 한계*

`feedback_self_eating_dogfood.md` 정합. 본 sprint 의 자기 산출물 적용은 *지금* 가능하지만, *다음 cold session (theseus-orchestrator-g4-v4)* 에서 본 페이즈 1.5 + Phase 06 design-twice 가 실제로 외부 평가 차원 (특히 Experimental + Conceptual + Code quality) 을 끌어올리는지 *검증 의무*.

본 sprint 마감 != 본 sprint 검증. 검증은 g4-v4 회차 결과물.

---

## 5. 반-원칙 (anti-goal)

본 sprint 는 *아래 안 한다*:

- 점수 % 표기 (목표 X / 결과 O)
- 신규 컨벤션 폴더 추가 (페이즈 본문 patch + CLI 우선; 컨벤션 파일은 최후 수단)
- HARD-CORE.md 본문 부풀림 (4000 chars 제약)
- 단일 cold session 점수 회복 패치 (구조 변경 우선)
- 사용자 ack 강제 인터럽트 (페이즈 04 외 인터럽트 0 정합)

---

## 6. 마감 조건

- 7 PR 모두 main 머지
- 7 신규 CLI 모두 self-test (각 CLI 의 `--self-test` flag 1.000 PASS)
- 9 HARD-RULE 모두 INDEX.md router 등록 + 페이즈 본문 invoke step 박힘 (sprint-43 패러다임)
- skill_version 0.9.49 → 0.9.50
- CHANGELOG + memory entry
- docs/reviews/ g4-v3 분석 doc

본 sprint 가 진짜로 효과를 봤는지는 g4-v4 cold session 의 외부 평가 결과로 판정.

---

## 7. 참고 — 사용자 메시지 원문 (지시 trace)

> *"의도를 이해하고 프롬프트에 적혀있는 이상의 처리를 해야 한다. 이해 만으로 멈춰서 그런데 성찰-상상력을 덧대서 추가하면 좋은 작업이나 더 설계를 확장하거나 프롬프트 보다 더 확장된 제안을 intent 이후 단계에 추가하는 건 어떨까. 지금 남은 점수들 그 이상을 하려면 프롬프트를 지키는 것 이상으로 프롬프트를 실행하고 숨겨진 의도를 파악하는 것이다."*
>
> *"plan/impl 에서도 확장 된 사고를 지시해야 한다. 실용주의 프로그래밍 이펙티브 소픝크웨어 설계의 인사이트들을 실제 반영해야 한다. 요구사항이해와 설계 구현 유지보수 -테스트 들에 대한 바이블이다."*

본 sprint 의 모든 PR 본문은 위 인용을 *direct trace* — 위 문장 외의 추가 지시 없음.
