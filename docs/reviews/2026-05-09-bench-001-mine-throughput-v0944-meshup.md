# 2026-05-09 — Bench 001 v0.9.44 메쉬업 결론 — 외부 평가 5pt 갭 + 메타-허들 미동작

> **본 문서의 위치.** [`2026-05-09-bench-001-mine-throughput-v0944.md`](2026-05-09-bench-001-mine-throughput-v0944.md) (외부 1차 분석 — 5 G-gap) 와 [simulation-bench 측 자체 회고](file:///d:/github/simulation-bench/docs/theseus_harness_v0_9_44_g4_retrospective.md) (7-axis F-1~F-5) 를 메쉬업한 결론. **두 분석의 합의 + 사용자 신규 발견 (메타-허들 미동작) 통합**.

## 0. TL;DR — 3 결론

1. **외부 점수 5pt 손실 — 두 분석 완전 합의**. 본 문서 §1 매핑 표.
2. **94→95 plateau 1pt 돌파 = enforcement layer 마지막 1pt 회수**. 잔여 5pt 는 *다른 차원* — *질적 게이트 + 도메인 sub-rubric* 신규 패러다임 필요. §3.
3. **사용자 신규 발견 — 메타-허들 미동작 (점수에는 없으나 더 중대)**: skill_version 0.9.40 stale frontmatter 로 v0.9.41~v0.9.44 의무 산출물 자동 미생성 + Phase 13 interactive-viewer (G4 강제) 통째 skip + sprint-39 4 패턴 게이트 산출물 (gate_pnc/mirror/primary/literal.json) 0. **컨벤션 선언 ≠ 런타임 집행** — 본 하네스 의 *구조적 결함*. §4.

---

## 1. 두 분석의 5pt 합의 매트릭스

| Reviewer 인용 | 본 docs 5-gap (외부) | simulation-bench 7-axis (내부) | 합의 |
|---|---|---|---|
| dispatcher queue=`len()+busy` 휴리스틱 (-1) | **G-3** 휴리스틱 분류 부재 | **§2.4 분석 + §2.5 계획** — L2 패턴 카탈로그 부재 + tournament heuristic-fidelity 차원 부재 | ✅ 동일 |
| travel-noise 1 draw / edge (-1) | **G-3** | **§2.2 질문** — cascading sub-Q 부재 + **§2.4** L2 도메인 패턴 카탈로그 부재 | ✅ 동일 |
| warmup_minutes=0 정당화 thin (-1) | **G-4** | **§2.1 의도이해** — domain methodology rubric injection 부재 | ✅ 동일 |
| README ↔ summary.json drift (-1) | **G-2** | **§2.7 결과** — numeric-doc-data-sync gate 부재 | ✅ 동일 |
| Conceptual 19/20 잔여 (-1) | **G-5** 천정 (질적 layer) | **§2.7 결과** — handoff exemplary-rubric 부재 | ✅ 동일 |
| (점수 외 catch) D-6/V6 hash() salt 비결정성 | **G-1** V6 evidence-bound 부재 | **§2.3 회귀 + §2.6 구현** — V6 cross-process scope 부재, test-scope frontmatter 부재 | ✅ 동일 |

**해석.** 두 분석 *완전 독립* (외부 = 본 하네스 docs, 내부 = simulation-bench 측 회고). 그럼에도 5/5 + 1 보너스 모두 같은 사슬을 짚었다 — **점수 손실 사슬은 robust 하다**.

## 2. 두 분석이 *서로 보강* 한 점

### 2-1. 외부 (G-1~G-5) 가 더 강한 부분
- **점수 부재 → sprint-40 PR 분할 직접 매핑** (PR-B/C/D/E + sprint-41+ G-5).
- **점수 회복량 추정** (직접 +3pt + 간접 +1pt = 98–99/100).
- **plateau history table** — 002(92) → 003(94) → 094 cold(94) → ... → v0944(95) 의 9-sprint trail.

### 2-2. 내부 (F-1~F-5) 가 더 강한 부분
- **7-axis 책임 귀속** — 점수 손실을 phase 01–14 사슬로 추적 (의도이해→질문→회귀→분석→계획→구현→결과). 본 하네스 의 메모리 [`feedback_pseudocode_to_enforcement.md`](../../../memory/feedback_pseudocode_to_enforcement.md) 정합.
- **convention 명시 vs 산출물 부재 매핑** — 예: HARD-RULE 9.bb `readme-numbers-from-summary` 가 *존재* 하나 quality/09 V5 가 *숫자-동일성 미검증*. 의사코드 → enforcement 갭의 직접 사례.
- **F-2 V6 cross-process evidence binding** — *intra-process* test 가 *통과* 하지만 cross-process *비결정성* 발현. test scope 차원의 결손.
- **F-4 도메인 sub-deck (DES/queueing/scheduling)** — 외부 G-3 가 *분류만* 제안, 내부 F-3/F-4 가 *cascading sub-Q 패턴 + L2 카탈로그* 까지 구체화.

### 2-3. 메쉬업 — 차이가 아니라 *깊이 차*

두 분석이 동일 phenomenon 을 *층위 다르게* 본 사례:
- 외부 G-2 **"README↔summary drift"** → 내부 §2.7 가 *root-cause* 까지 추적: drift 의 *발생 기전* = "first README 작성 → harness/measure_run.py 가 또 한 번 invoke → outputs/ 덮어씀 → 두 번째 invoke 의 hash() salt 다름 → 0.08% drift". **즉, drift 는 *V6 비결정성 + atomic regen 부재* 의 합성** — G-2 와 G-1 이 *분리되어 있지 않다*.

→ **sprint-40 PR-B + PR-C 는 entwined**: `gate_v6_reproducibility.json` 통과 후 docs regen 을 atomic 하게 묶어야 *진짜* 해결. 본 메쉬업의 첫 구체 권고.

## 3. 이전 진단 vs 현재 — 개선 / 미개선 추적

### 3-1. 이전 진단 (v0.9.6 ~ v0.9.42 누적)

메모리 trail:
- [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md) (v0.9.12 시점) — *6pt 갭 = Conceptual / Sim / Results 차원, 질적 layer.* 이론상 v0.9.13 이 +3-5pt 회복 시도.
- [`project_v0914_cold01.md`](../../../memory/project_v0914_cold01.md) (v0.9.14) — 94 plateau 재확인, ramp 비-병목 finding.
- [`feedback_harness_strengthening_methodology.md`](../../../memory/feedback_harness_strengthening_methodology.md) — v0.9.6 nfr-derivation 도입.
- [`feedback_dual_pressure_json_schema.md`](../../../memory/feedback_dual_pressure_json_schema.md) — sprint-35/36 lineage.json/webview.json 의무 키 = *진행 게이트 + viewer source 이중 압력*.

### 3-2. v0.9.44 회차 — 차이 정리

| 이전 진단 | v0.9.44 결과 | 개선 | 미개선 |
|---|---|---|---|
| 94 plateau (Conceptual / Sim / Results 6pt 갭, 질적 layer) | 95 (5pt 갭) | ✅ +1pt — *enforcement 마지막 1pt 회수* | 5pt 잔여 — *질적 layer* 그대로 |
| Conceptual 차원 (이전 진단의 핵심) | 19/20 — "well-organised" but not "exemplary" | ❌ 정체 | exemplary-rubric / methodology-injection / L2 카탈로그 모두 부재 |
| Sim correctness (heuristic 깊이) | 18/20 — 두 휴리스틱 flag (queue + noise) | ❌ 정체 | cascading sub-Q + L2 critique catalogue 부재 |
| Results (drift / atomic regen) | 14/15 — 0.08% drift | ❌ 정체 (오히려 새 회차 발현) | numeric-doc-data-sync gate + V6 cross-process 합성 미해소 |
| nfr-derivation methodology completeness (v0.9.6 도입) | warmup justification thin | △ 부분 — nfr-derivation 이 *존재* 하나 도메인 sub-checklist 미주입 | DES tag → warmup/CRN/power-analysis 강제 미존재 |
| 이중 압력 JSON 스키마 (sprint-35/36) | **lineage.json / webview.json / viewer html 0** | ❌ **완전 미적용** — *컨벤션 선언만, 런타임 미집행* | §4 참조 |

**해석.** 이전 진단의 *6pt 질적 layer 갭* 중 **0pt** 가 직접 회복. +1pt 는 enforcement 트랙의 *마지막 미해소 부분* (sprint-39 4 패턴 inline). **질적 layer 6pt 는 v0.9.44 까지도 정체** — 메모리 [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md) 의 *질적 게이트 신규 패러다임 필요* 진단 재확인.

## 4. 사용자 신규 발견 — 메타-허들 미동작 (점수 외, 그러나 *더 중대*)

사용자 지적: *"분명 스크립트 / cli 레벨에서의 허들을 추가 했으나 정상동작하지않은 것 같고 / 분명 프리빌트 뷰어를 첨부하도록 했으나 프리빌트 뷰어용 파일json 과 그 뷰어 html 이 꾸려지지않았음"*. 검증 결과 **사실** — 본 하네스 의 *구조적* 결함을 드러내는 가장 큰 발견.

### 4-1. 증거 — `.ShipofTheseus/mine-throughput-g4-v2/` 점검

| 항목 | 의무 | 실제 | 결손 |
|---|---|---|---|
| **frontmatter `skill_version`** | v0.9.44 (orchestrator 현재) | 모든 phase 산출물 = `skill_version: 0.9.40` (33 파일) | **v0.9.41~v0.9.44 의무 *통째 비활성*** |
| **Phase 12 webview** | `webview/{lineage.html,lineage.json,assets/}` (sprint-35 v0.9.40) | `webview/index.md` 8-tab 마크다운 표만 | prebuilt shell 0 / lineage.json 0 |
| **Phase 13 interactive-viewer** | G4 강제 — `interactive-viewer/` 디렉터리 + viewer html + data/webview.json (sprint-36 v0.9.41) | 디렉터리 자체 없음 | **Phase 13 통째 skip** |
| **Phase 09 sprint-39 4 게이트 산출물** | `gate_{pnc,mirror,primary,literal}.json` (sprint-39 v0.9.44) | 0 | sprint-39 의무 산출물 0 |
| **CLI invoke step** (sprint-34 9.mm) | phases/04/06/08 invoke 흔적 | 산출물에 invoke 증거 없음 | 추정 미동작 |

### 4-2. 진단 — 컨벤션 선언 ≠ 런타임 집행

본 하네스 의 conventions/ 에 명확히 *기재* 되어 있음:
- [`prebuilt-shell-runtime-json.md`](../../skills/theseus-harness/conventions/prebuilt-shell-runtime-json.md) — "lineage.html + lineage.json 이중 emit 프로토콜"
- [`pre-cold-session-bootup.md`](../../skills/theseus-harness/conventions/pre-cold-session-bootup.md) — "phase 진입 전 골격 파일 생성"
- [`phase-lineage-viewer.md`](../../skills/theseus-harness/conventions/phase-lineage-viewer.md) §15 — "빈 list / null / dummy filler 박아두면 (a) emit_fidelity.py check fail (b) viewer 가 빈 화면 — 이중 압력"

그러나 본 v0.9.44 회차 산출물은 *해당 파일 자체가 부재*. **이중 압력 게이트 (file fail + viewer 빈 화면) 가 *파일 부재* 상황을 catch 하지 못한다** — emit_fidelity.py 가 *존재하는 파일의 빈 키* 만 검사. *파일 자체가 없으면 검사 자체가 skip*.

`contracts.md:125`: *"skill_version 의 *major* 가 현재 하네스 major 와 같음 확인"* — minor mismatch (0.9.40 vs 0.9.44) 는 *silent pass*. 이로 인해 v0.9.41~v0.9.44 의 모든 의무 산출물이 *skill_version 비교에서 자동 skip*.

### 4-3. 메모리 [`feedback_pseudocode_to_enforcement.md`](../../../memory/feedback_pseudocode_to_enforcement.md) 의 직접 발현

> *"룰 본문이 의사코드만이면 agent 자율 skip 가능. orchestrator runtime guard 가 같이 박혀야 enforcement 완성"*

본 회차 = **이 진단의 가장 큰 사례**. sprint-35 sprint-36 sprint-39 가 컨벤션 본문 + 의사코드 까지 박았으나 *orchestrator runtime guard* 가 phase 진입 시 산출물 *존재 여부* 를 강제하지 않음. agent 가 phase 12 끝나면서 *webview/index.md 만 작성* 해도 통과.

### 4-4. 메타 결손 4 — sprint-40 1번 PR 의무

| Meta-G | 결손 | sprint-40 PR | 효과 |
|---|---|---|---|
| **M-1** | skill_version minor 비교 부재 (0.9.40 silent pass) | contracts.md `skill_version` 게이트 — minor ≥ orchestrator minor 아니면 phase 진입 거부 | v0.9.41~v0.9.44 의무 자동 활성 |
| **M-2** | 산출물 *파일 존재* 게이트 부재 (emit_fidelity 가 빈 키만 검사) | phase 12/13 진입 거부 게이트 — `webview/lineage.json` + `interactive-viewer/index.html` 파일 존재 강제 | 이중 압력 게이트 *외피* 채움 |
| **M-3** | Phase 13 G4 강제 unwiring (skill 본문 *강제* 명시, 런타임 *skip* 가능) | orchestrator phase 13 invoke step + 종료 시 산출물 디렉터리 검증 | G4 = Phase 13 100% 보장 |
| **M-4** | sprint-39 게이트 산출물 (gate_*.json) 자동 생성 미연결 | phase 09 진입 시 4 gate JSON 골격 자동 emit + 진행 중 갱신 | sprint-39 의무 *런타임* 활성 |

**중요.** 이 4 메타-G 는 *점수* 에는 직접 영향 0 — reviewer 는 산출 코드/논리만 평가, 본 하네스 의 메타-산출물 부재는 무관심. 그러나 **본 하네스 자체 가치 = *허들 / observability / governance trail* 인 만큼, 이 4 결손이 *외부 점수 5pt 손실보다 더 큰 신뢰 손상*** — *허들이 있다고 광고했는데 동작 안함* 의 직접 증거.

## 5. sprint-40 권고 갱신 — 외부 5pt + 메타 4 결손 동시 PR 분할

이전 외부 분석 (G-1~G-5) + 본 메쉬업 메타 (M-1~M-4) 합성:

| PR | scope | 회복 | 메모리 정합 |
|---|---|---|---|
| PR-A | sprint-40 plan.md | — | — |
| **PR-B** | M-1 + G-1 합성 — `skill_version` minor gate + V6 cross-process evidence binding (`gate_v6_reproducibility.json`) | **메타 + 직접 1pt** | feedback_pseudocode_to_enforcement |
| **PR-C** | M-2 — phase 12/13 산출물 파일 존재 게이트 + 빈 골격 자동 emit | **메타 (점수 0, 신뢰 회복)** | feedback_dual_pressure_json_schema |
| **PR-D** | M-3 — Phase 13 G4 invoke step + 종료 시 디렉터리 검증 + interactive-viewer 골격 emit | **메타** | feedback_phase12_real_definition |
| **PR-E** | M-4 + G-2 합성 — gate_*.json 자동 emit + numeric-doc-data-sync (`gate_readme_summary_consistency.json`) atomic regen | **메타 + 직접 1pt** | feedback_dual_pressure_json_schema |
| PR-F | G-3 — `modeling_shortcuts.json` + L2 critique catalogue + cascading sub-Q (interview deck DES) | **간접 +1pt + 직접 +1pt 시도** | feedback_94_plateau_general_harness |
| PR-G | G-4 — `gate_warmup.json` first/second-half delta + warmup methodology checklist | **직접 +1pt** | feedback_analytical_bound_validation |
| PR-H | sprint 마감 (v0.9.45 + CHANGELOG) | — | — |
| **(별 sprint)** | G-5 conceptual_depth.json + handoff exemplary-rubric — 신규 *질적 게이트 패러다임* | sprint-41+ | feedback_94_plateau_general_harness |

**예상 효과.**
- 외부 점수: 95 → 98–99/100 (PR-B/E/G 직접 3pt + PR-F 간접 1pt)
- 메타 신뢰: skill_version minor 게이트 + viewer 산출물 강제 = *허들 광고-실행 일치* 회복

## 6. 결론 — 본 하네스 의 *진짜* 단점 우선순위

이 두 분석을 합쳐 본 하네스 단점을 *점수 손실* + *메타 신뢰* 두 축으로 재정렬:

| 단점 | 종류 | 우선순위 | sprint-40 PR |
|---|---|---|---|
| **컨벤션 선언 ≠ 런타임 집행** (M-1~M-4 메타) | 구조적 | **최상** | PR-B 메타 / C / D / E 메타 |
| V6 cross-process / numeric drift / atomic regen | 점수 -2 | 상 | PR-B 직접 / E 직접 |
| 도메인 L2 sub-rubric / cascading sub-Q | 점수 -1~2 | 상 | PR-F |
| Methodology completeness (warmup) | 점수 -1 | 중 | PR-G |
| 천정 질적 layer (conceptual exemplary) | 점수 -1 | 신규 패러다임 | sprint-41+ |

**가장 중요한 발견.** 외부 점수 95/100 (94 plateau 첫 돌파) 은 sprint-37/38/39 enforcement 트랙의 *직접* 성과 — 그러나 동시에 본 회차는 sprint-35/36/39 의 *메타-산출물* (lineage.json / webview.json / viewer html / gate_*.json) 을 *통째 skip* 했다. 즉 *외부 점수* 측면에서는 +1pt 진보 / *메타 신뢰* 측면에서는 *광고된 허들 미동작*. **두 결과가 같은 시점에 발견된 것 자체가 본 하네스 가 *enforcement 측면* 에 다음 번 sprint 자원을 100% 투입해야 한다는 신호.**

본 메쉬업의 단일 sprint-40 의무: **PR-B/C/D/E 메타 4 (skill_version + 산출물 파일 존재 + Phase 13 강제 + gate JSON 자동 emit) 우선 + PR-F/G 점수 4pt 회복 후 v0.9.45 마감**. 회복 가능한 가장 큰 단점은 *질적 layer* 가 아니라 *컨벤션-런타임 갭* — 이 갭을 닫지 않은 채 신규 컨벤션을 더 추가하면 *광고만 늘고 동작은 정체* 의 정확한 사례를 본 회차가 직접 보여줬다.

---

## Appendix — 원자료 위치

- 외부 1차 분석: [`2026-05-09-bench-001-mine-throughput-v0944.md`](2026-05-09-bench-001-mine-throughput-v0944.md)
- 내부 7-axis 회고: `D:/github/simulation-bench/docs/theseus_harness_v0_9_44_g4_retrospective.md`
- 거버넌스 trail (skill_version stale 증거): `D:/github/simulation-bench/.ShipofTheseus/mine-throughput-g4-v2/`
  - 모든 frontmatter `skill_version: 0.9.40` (33 파일)
  - `webview/index.md` 만 — `lineage.json`, `lineage.html`, viewer dist 0
  - `interactive-viewer/` 디렉터리 부재 (G4 강제 phase 13 통째 skip)
  - `gate_pnc.json / gate_mirror.json / gate_primary.json / gate_literal.json` 0 (sprint-39 의무)
- bisect 기록 (D-6/V6): `<governance>/sprints/04/bisect.md`
- 본 하네스 메모리: [`feedback_pseudocode_to_enforcement.md`](../../../memory/feedback_pseudocode_to_enforcement.md), [`feedback_dual_pressure_json_schema.md`](../../../memory/feedback_dual_pressure_json_schema.md), [`feedback_94_plateau_general_harness.md`](../../../memory/feedback_94_plateau_general_harness.md)
