# Sprint-40 — 100/100 도전 + 메타-허들 활성 (트랙 4)

> 시작: 2026-05-09 (sprint-39 v0.9.44 마감 직후)
> 직전: sprint-39 4 패턴 inline (PNC / Mirror / Primary / Literal — phase 09 게이트 본문)
> 외부 검증: simulation-bench 001 v0.9.44 g4-v2 = **95/100 (94 plateau 첫 돌파)**
> 우선순위: **메타-허들 활성 (M-1~4) → 점수 회복 (G-1~4) → 100/100 재시도**

본 sprint = simulation-bench 001 의 95/100 결과 [메쉬업 결론](../../../docs/reviews/2026-05-09-bench-001-mine-throughput-v0944-meshup.md) 의 권고를 1:1 PR 분할.

---

## 0. 배경 — 두 축의 결손

### 0-1. 외부 점수 5pt 갭 (zero-context Opus reviewer)

| 손실 | 카테고리 | 진단 G-id |
|---|---|---|
| -2 | Sim correctness — dispatcher queue 휴리스틱 + travel-noise per-edge | G-3 |
| -1 | Experimental design — warmup_minutes=0 정당화 thin | G-4 |
| -1 | Results — README ↔ summary.json 0.08% drift | G-2 |
| -1 | Conceptual — "well-organised" but not "exemplary" | G-5 (sprint-41+) |
| (catch) | V6 reproducibility — `hash(scenario_id)` salt randomization | G-1 |

### 0-2. 메타-허들 미동작 (사용자 신규 발견)

| 결손 | 본질 | 진단 M-id |
|---|---|---|
| frontmatter `skill_version: 0.9.40` 33 파일 | major 만 비교, minor mismatch silent skip | **M-1** |
| `webview/lineage.json`, viewer html 0 | 컨벤션 선언 ✓ / 산출물 부재 → emit_fidelity 가 *파일 부재* skip | **M-2** |
| `interactive-viewer/` 디렉터리 통째 부재 | Phase 13 G4 강제 unwiring | **M-3** |
| `gate_pnc/mirror/primary/literal.json` 0 | sprint-39 신규 의무 산출물 자동 emit 미연결 | **M-4** |

**핵심 진단.** 메모리 [`feedback_pseudocode_to_enforcement.md`](../../../../memory/feedback_pseudocode_to_enforcement.md) 의 가장 큰 발현 사례. 컨벤션 선언 ≠ 런타임 집행. *광고된 허들* 이 동작하지 않으면 본 하네스 자체 가치가 흔들린다.

---

## 1. 의도 — 한 줄

skill_version minor gate + 산출물 파일 존재 게이트로 *기존 컨벤션 런타임 활성* + 점수 회복 4 게이트 (V6 evidence / numeric drift / modeling shortcuts / warmup quantification) 도입 → bench 001 재실행에서 100/100 도전.

---

## 2. PR 분할안

| PR | scope | 산출 | self_lint |
|---|---|---|---|
| PR-A ★ 본 PR | sprint-40 plan.md + bench v0.9.44 진단 docs (외부 + 메쉬업) | 3 docs | 0 |
| PR-B | **M-1 + G-1** — `skill_version` minor gate (contracts.md) + V6 cross-process evidence (`gate_v6_reproducibility.json` + bin-identical sha256 강제) | contracts.md edit + phases/09 §V6 본문 갱신 + new conv `v6-cross-process.md` (또는 inline) | C-V6X (신규) |
| PR-C | **M-2** — Phase 12/13 산출물 *파일 존재* 게이트 (phases/09 진입 시 viewer 산출물 디렉터리 검증; phase 12/13 종료 시 파일 강제) | phases/09 + 12 + 13 본문 + agents/{webview,interactive-viewer}-builder.md 의무 step | C-VEX (viewer-existence) |
| PR-D | **M-3** — Phase 13 G4 invoke step (orchestrator 본문) + interactive-viewer 골격 자동 emit (cold session 부팅 시) | skills/theseus-orchestrator/SKILL.md + phases/13 + pre-cold-session-bootup.md | (PR-C 의 lint 와 합성) |
| PR-E | **M-4 + G-2** — sprint-39 4 게이트 JSON 자동 emit 연결 (phase 09 진입 시 골격) + numeric-doc-data-sync (`gate_readme_summary_consistency.json`) atomic regen | phases/09 §PNC/Mirror/Primary/Literal 본문 + new §README-Sync | C-RDS (신규) |
| PR-F | **G-3** — `modeling_shortcuts.json` (phase 02/03) + L2 critique catalogue (phase 05 cold reviewer DES sub-deck) + cascading sub-Q (phase 04 interview deck) | conventions/modeling-shortcuts.md (신규) + interview-deck-des.md (신규) + phases/02/04/05 본문 | C-MSC (신규) |
| PR-G | **G-4** — `gate_warmup.json` (phase 09) first-half/second-half delta 의무 + warmup methodology checklist (DES tag 강제) | phases/09 §Warmup + nfr-derivation.md 본문 (DES sub-checklist) | C-WUP (신규) |
| PR-H | sprint 마감 v0.9.45 + CHANGELOG | SKILL.md / orchestrator SKILL.md / plugin.json / CHANGELOG | 0 |

self_lint +5 신규 (129 → 134) — C-V6X / C-VEX / C-RDS / C-MSC / C-WUP. (G-5 conceptual exemplary-rubric = sprint-41+ 신규 *질적 게이트* 패러다임.)

이번 세션 범위 = **PR-A + PR-B + PR-C** (사용자 합의 — *PR-A 플랜 + PR-B/C 메타*).

---

## 3. 각 PR 상세 명세

### 3.1 PR-B — M-1 skill_version minor gate + G-1 V6 cross-process evidence

#### 3.1.1 M-1 — skill_version minor gate

**현재 상태.** [`contracts.md:125`](../../../skills/theseus-harness/conventions/contracts.md):

> b- `skill_version` 의 *major* 가 현재 하네스 major 와 같음 확인.

**문제.** v0.9.40 frontmatter 가 v0.9.44 orchestrator 에서 silent pass. v0.9.41~v0.9.44 의 의무 산출물 (lineage.json / viewer html / gate_*.json) 자동 skip.

**변경안.** contracts.md 본문 :

> b- `skill_version` 의 *major* 가 현재 하네스 major 와 같고, *minor* 가 현재 하네스 minor 이상임 확인.
>   - minor 미달 시 phase 진입 거부, 사용자에게 *전체 재실행* 또는 *frontmatter 갱신* 객관식 제시 (interview.md 패턴).
>   - patch 차이는 silent pass 허용 (오타 / 프롬프트 미세조정).

자율 사용자 ack 0 — *전체 재실행* 자동 트리거 (페이즈 04 외 인터럽트 0, 메모리 [`feedback_no_human_ack.md`](../../../../memory/feedback_no_human_ack.md) 정합).

contracts.md §안티 패턴 d 보강 — `skill_version` 임의 변경 외에도 *minor 누락 회차 산출물 재사용* 도 명시 안티.

#### 3.1.2 G-1 — V6 cross-process evidence

**현재 상태.** [`reproducibility-doublecheck.md`](../../../skills/theseus-harness/conventions/reproducibility-doublecheck.md) 가 *intra-process* test 만 의무 — `test_xxx_deterministic` pytest. cross-process (별 python invocation × 2) 검증 부재.

**변경안.** phases/09 본문 §V6 :

> V6 통과는 다음 두 evidence 모두 attach 의무:
>
> 1. intra-process pytest (기존)
> 2. cross-process — 별 subprocess invoke ×2 → outputs/summary.json sha256 1:1 동일.
>
> 산출물: `quality/gate_v6_reproducibility.json`
>
> ```json
> {
>   "intra_process": {"test_id": "...", "passed": true},
>   "cross_process": {
>     "invoke_1": {"stdout_sha256": "...", "summary_sha256": "..."},
>     "invoke_2": {"stdout_sha256": "...", "summary_sha256": "..."},
>     "summary_equal": true
>   },
>   "verdict": "pass"
> }
> ```
>
> `summary_equal: false` 시 phase 10 sprint loop 진입 (regression bisect).

**파생 anti-pattern lint** — `simulation-bench` 회차의 `bisect.md:50-56` auto-derived rule 일반화:

```
grep -E 'SeedSequence\([^)]*hash\(' src/  # must be empty
grep -E 'random\.seed\(.*hash\(' src/      # must be empty
grep -E 'np\.random\.seed\(.*hash\(' src/  # must be empty
```

추가 분야 — `os.urandom`, `id()`, `random` global, Python `hash()` 의 비결정성 야기 함수 카탈로그 (`conventions/cross-process-anti-patterns.md` 신규 1 페이지).

#### 3.1.3 self_lint 신규

**C-V6X** (cross-process V6 evidence) — phase 09 진입 시:
- `quality/gate_v6_reproducibility.json` 존재 확인
- `cross_process.summary_equal: true` 확인
- 미달 시 phase 09 진입 거부

#### 3.1.4 변경 파일 (PR-B)

| 파일 | 변경 종류 | 줄 수 |
|---|---|---|
| skills/theseus-harness/conventions/contracts.md | edit (§ 재진입 규칙 b + § 안티 d) | ~10 |
| skills/theseus-harness/phases/09-quality-gates.md | edit (§V6 본문 보강) | ~30 |
| skills/theseus-harness/conventions/reproducibility-doublecheck.md | edit (cross-process scope 추가) | ~20 |
| skills/theseus-harness/conventions/cross-process-anti-patterns.md | new | ~50 |
| skills/theseus-harness/self_lint/C-V6X.json (또는 통합 lint table) | new | ~10 |

PR-B 총 ~120 줄 변경.

---

### 3.2 PR-C — M-2 Phase 12/13 산출물 파일 존재 게이트

#### 3.2.1 진단

[`phase-lineage-viewer.md` §15](../../../skills/theseus-harness/conventions/phase-lineage-viewer.md) 의 emit_fidelity.py 는 *존재하는 파일의 빈 키* 만 검사. 파일 자체 부재 시 skip.

**증거.** simulation-bench v0.9.44 회차 — `webview/index.md` 만 (마크다운 표). lineage.json / lineage.html / interactive-viewer/ 모두 0. 그럼에도 phase 12 종료 marker 만 박힘.

#### 3.2.2 변경안 — 3 단 게이트

**Gate-1 (phase 12 종료 시).** phases/12-webview-assembly.md 본문 종료 절 :

> 페이즈 12 종료 직전 다음 파일 *존재* 강제 :
> - `<project>/webview/index.html` (prebuilt shell 복사본)
> - `<project>/webview/data/webview.json` (8 탭 합본)
> - `<project>/webview/assets/app.js` + `mermaid.min.js` + `marked.min.js`
>
> 미존재 시 phase 12 미완 — sprint loop 진입 (phase 10) 또는 webview-builder agent 재실행.

**Gate-2 (phase 13 종료 시).** phases/13-interactive-viewer.md 본문 종료 절 :

> 페이즈 13 종료 직전 다음 파일 *존재* 강제 (G3+ 모든 grade) :
> - `<project>/interactive-viewer/index.html`
> - `<project>/interactive-viewer/dashboard.json`
> - `<project>/interactive-viewer/assets/app.js`
>
> G4+ 추가 — `dashboard.json` 의 `widgets` 배열 길이 ≥ 3 (kpi_grid + topology + metric_chart 최소).
>
> 미존재 시 phase 13 미완 — interactive-viewer-builder agent 재실행.

**Gate-3 (phase 09 진입 시 — 사전 차단).** phases/09 §V8 (신규 — viewer-readiness) :

> phase 09 quality gate 진입 시 viewer 디렉터리 *외피* 강제 :
> - `webview/` + `interactive-viewer/` 디렉터리 *존재*
> - 빈 골격이라도 OK — phase 12/13 가 채움을 보장
> - 디렉터리 부재 시 pre-cold-session-bootup.md 가 누락된 신호 → phase 00 재실행

#### 3.2.3 self_lint 신규

**C-VEX** (viewer-existence) — phase 12/13 종료 직전 file existence check. fail 시 phase 미완.

#### 3.2.4 변경 파일 (PR-C)

| 파일 | 변경 종류 | 줄 수 |
|---|---|---|
| skills/theseus-harness/phases/12-webview-assembly.md | edit (§종료 게이트 신규) | ~30 |
| skills/theseus-harness/phases/13-interactive-viewer.md | edit (§종료 게이트 신규 + G4+ widgets ≥ 3) | ~30 |
| skills/theseus-harness/phases/09-quality-gates.md | edit (§V8 viewer-readiness 신규) | ~25 |
| skills/theseus-harness/agents/webview-builder.md | edit (강제 산출물 표 명시) | ~10 |
| skills/theseus-harness/agents/interactive-viewer-builder.md | edit (강제 산출물 표 명시) | ~10 |
| skills/theseus-harness/conventions/viewer-runtime.md (또는 새 파일) | edit (file-existence semantics) | ~20 |

PR-C 총 ~125 줄 변경.

---

### 3.3 PR-D — M-3 Phase 13 G4 invoke step

(이번 세션 범위 외 — PR-D 이후 후속 세션.)

orchestrator SKILL.md 가 phase 13 invoke 본문에 *G4 강제 unwiring* 명시. cold session 이 phase 12 종료 후 phase 13 자동 진입 강제. pre-cold-session-bootup.md 가 *interactive-viewer/* 디렉터리 빈 골격 사전 생성.

### 3.4 PR-E — M-4 + G-2

(이번 세션 범위 외.)

phase 09 진입 시 4 게이트 JSON (`gate_pnc.json` 등) 골격 자동 emit + numeric-doc-data-sync atomic regen. README/conceptual_model.md 의 모든 `\d` 패턴을 summary.json leaf 와 0.05% tol fuzzy match.

### 3.5 PR-F — G-3

(후속.)

`conventions/modeling-shortcuts.md` 신규 — phase 02/03 산출 의무. 4-tier classification (gold-standard / defensible-coarse / heuristic / placeholder). DES domain interview deck (`conventions/interview-deck-des.md`) — cascading sub-Q 패턴 ("noise 답변 → per-event/per-unit 추가 질문").

### 3.6 PR-G — G-4

(후속.)

`gate_warmup.json` — first-half/second-half throughput delta 의무. delta > 5% 시 warmup_minutes 정당화 evidence 강제. nfr-derivation.md 의 *DES sub-checklist* 추가 (warmup / CRN / power-analysis / terminating vs steady-state).

### 3.7 PR-H — 마감

(후속.)

skills/theseus-harness/SKILL.md `version: 0.9.45`, plugin.json 동시 갱신, CHANGELOG 항목 신설.

---

## 4. 구조 가치 — 범용 / 치밀 / 밀도 (벤치 점수 targeting 아님)

> **원칙 정합** — 메모리 [`feedback_harness_strengthening_methodology.md`](../../../../memory/feedback_harness_strengthening_methodology.md): *"외부 답안 후 패치는 케이스 종속. 본 하네스 강화 = prompt → 게이트 흐름의 *구조* 변경"*. 본 §4 = 각 PR 의 *구조 가치* (도메인 독립). 외부 점수 영향은 *결과* 이지 *목표* 아님.

| PR | 구조 변경 | 도메인 독립 적용 범위 |
|---|---|---|
| PR-B | `skill_version` minor gate (silent regression 차단) + V6 evidence-bound (subprocess × 2 + sha256 + 7 anti-pattern grep) | 모든 결정성 파이프라인 (Python/Rust/Go/TS — 언어별 anti-pattern catalogue 확장 가능) |
| PR-C/D | viewer 산출물 file-existence 3 단 게이트 + Phase 12/13 invoke step + pre-bootup 자동 호출 | 모든 G3+ 회차 (observability claim ↔ artifact 정합 — 도메인 무관) |
| PR-E | 4 게이트 JSON 골격 자동 emit + numeric drift atomic regen (±0.01%) | 모든 deliverable + summary 페어 (mining / ML / ETL / API 모두) |
| PR-F | modeling shortcuts 4-tier (gold-standard / defensible-coarse / heuristic / placeholder) + cascading sub-Q (interview keyword) + L2 도메인 critique 카탈로그 | 모든 도메인 모델링 (DES/ML/API/ETL/분석 5 도메인 본문 박힘) |
| PR-G | methodology-completeness 4 골격 (transient/sample/determinism/horizon) — *도메인-agnostic* enforcement | 도메인 매칭 시 모든 회차 (sub-checklist 는 nfr-derivation 분리) |

**구조 가치 = enforcement layer 의 닫힘**. 메모리 [`feedback_pseudocode_to_enforcement.md`] 의 *"의사코드 → runtime guard"* 패러다임 5 layer 정착:
1. `skill_version` minor gate — 컨벤션 *버전* layer
2. file-existence 게이트 (phase 09/12/13) — *산출물* layer
3. evidence-bound JSON (V6 / numeric / 4 게이트 / methodology) — *증거* layer
4. invoke step (HARD-RULE 9.nn/9.oo/9.pp) — *호출* layer
5. cascading sub-Q + L2 catalogue — *질문 깊이* layer

## 5. 검증 — 외부 적용 후 평가

PR-H 머지 후:

1. simulation-bench (또는 다른 외부 도메인 적용처) 에서 fresh G4 cold session 실행 (skill_version 0.9.45 강제).
2. zero-context 외부 reviewer 의 채점.
3. 평가 *대상* = 본 sprint 의 5 layer enforcement 가 *실 cold session 에서 활성* 인가? (구조 검증)
   - 활성 → 본 sprint 구조 가치 입증.
   - 일부 미활성 → 어느 layer 의 runtime guard 가 미반영 인지 진단, sprint-41 fix.
   - 전체 미활성 → orchestrator runtime guard 의 더 깊은 결손, sprint-41 핵심 의제 격상.

평가 *부산물* = 외부 점수 변화. 본 sprint 의 구조 변경이 *직접* 점수 회복을 noun 으로 삼지 않는 이유 = *케이스 종속 패치* 회피 ([`feedback_harness_strengthening_methodology.md`] 정합).

검증 기록 위치: `docs/reviews/2026-05-1?-bench-001-mine-throughput-v0945-100.md` (재실행 일자 + 결과).

## 6. 메모리 신규 후보

PR-H 머지 시점 :
- `project_sprint40_v0945.md` (sprint 마감 결과)
- `feedback_skill_version_minor_gate.md` (M-1 의 sprint-바운드 정합 사례)
- `project_bench_001_v0945_100.md` (100/100 도달 시) 또는 `project_bench_001_v0945_partial.md` (부분 회복 시)

---

## 7. 위험 + 대응

| 위험 | 영향 | 대응 |
|---|---|---|
| skill_version minor gate 가 *과거 산출물* 통째 거부 → 재진입 어려움 | 중 | PR-B contracts.md 안티 d 본문에 *frontmatter 일괄 갱신* 옵션 제공 (사용자 ack 0 자동 트리거) |
| Gate-3 (phase 09 viewer 디렉터리 사전 검증) 가 *cold session 부팅 누락* 으로 광범위 false positive | 중 | pre-cold-session-bootup.md 가 *디렉터리 + 빈 골격* 만 사전 생성 — phase 12/13 가 *내용* 채움. Gate-3 = 디렉터리 존재만 검사, 빈 골격 OK |
| viewer 산출물 강제 가 *G2 등급* 에서도 발현 → 단순 프로젝트에 과부하 | 저 | phase 13 본문이 이미 G2-옵션 명시. PR-C Gate-2 도 G3+ 만 강제. G2 = optional |
| 100/100 도달 실패 (PR-F/G 후 99 또는 그 이하) | 중 | 재진단 후 sprint-41 신규 패러다임 (질적 게이트) 우선 진입 — *score saturation* 가 본 하네스 의 다음 천정 |

---

## 8. 비고

본 sprint = 신규 컨벤션 *추가* 보다 **기존 컨벤션 *런타임 활성*** 우선. sprint-37 다이어트 패러다임 ([`feedback_convention_diet_paradigm.md`](../../../../memory/feedback_convention_diet_paradigm.md)) 정합 — *광고만 늘고 동작 정체* 의 정확한 사례를 v0.9.44 회차가 직접 보여준 결과를 1:1 대응.
