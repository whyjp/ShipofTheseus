# CHANGELOG

본 저장소의 의미 있는 변경만 기록 — 메모리 `feedback_version_conservatism.md` (1.0 임박, 의미 있는 마일스톤만 발행) 정합. **사용자 원칙 (sprint-20+): 스킬 / 컨벤션 본문은 *현재* 활성 룰만 — sprint/version history 는 본 CHANGELOG 단일 위치.**

## v0.9.33 — 2026-05-06 (sprint-28 — Da Capo "fresh universe" 의미 명확화 + 무한 회귀 + scoring granularity)

### 마일스톤

cold session 003 attempt-2 (v0.9.32) 의 Da Capo 회귀 정정. agent 가 "Round 2 = top-K 생존자 head-to-head" 로 Da Capo 를 오해하여 *survivors rerun* 으로 구현 (의도: NEW universes + lessons applied).

### 변경 — `intra-phase-dacapo-loop.md` 안티 패턴 5 신규 (g~k)

- **g- survivors rerun (가장 빈번한 회귀)** : Round N+1 = top-K 생존자 head-to-head 재가중 채점 → 차단. 올바른 Round N+1 = `[anonymized prev winner] + [width-1 NEW fresh universes]`.
- **h- dacapo-rerun-NN.md 역순 작성** : tournament-(NN+1).md *이후* 작성 시 NEW universe pool spec 의미 상실. 올바른 순서: tournament-NN → dacapo-rerun-NN → tournament-(NN+1).
- **i- fresh universe 가 재라벨링** : 본문이 Round N universe 본문과 semantic diff < 30% → fail. lesson_pack 적용 + framing 변경 의무.
- **j- max_rerun cap 으로 조기 종료** : 본 의사코드는 *budget cap 만*. max_rerun (G3=2/G4=3/G5=5) 는 *참고용 가드*. **budget 충분 시 임계 (G4=0.999/G5=0.99999) 도달까지 *무한 회귀***. 임계 미달 + budget 여유 + rerun >= max_rerun 인데 promote = 차단 (mandatory rerun ce 정합).
- **k- scoring granularity coarse** : `0-3 4 단계 정수` / `0-10 정수` 등 coarse rating 으로 6-dim weighted (cf plan-tournament-scoring-strict) 우회 → reject. 0.0-1.0 연속값 의무. `각 criterion 0–3` 패턴 자동 reject.

사용자 직접 지시 :
- "다른 다카포도 마찬가지로 의미 를 명확하게 레슨만 가중해서 다시 하는것"
- "0.9999 임계값 까지 재시도 무한회귀"
- "점수 스코어링의 디테일이 높고 정확해야함"

### 변경 — pseudocode comment 정정

`max_rerun = {G3: 2, G4: 3, G5: 5}[grade]` 줄에 *참고용 가드 (sprint-28 — budget 충분 시 임계 도달까지 무한 회귀, budget cap 만이 진짜 종료 조건)* 주석 추가.

### 변경 — self_lint

- **C-DCL-FRESH-UNIVERSE 신규** : 컨벤션 본문에 anti-pattern + fresh universe 정의 명시 검증 (6 keyword: C-DCL-FRESH-UNIVERSE / survivors rerun / 재라벨링 / 역순 작성 / 무한 회귀 / scoring granularity coarse).
- 99 → 100 checks. all_ok=True.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.32 → 0.9.33.
- self_lint 100/100 PASS.

### 알려진 결손 (sprint-29+)

- C-IDX-3 (phases 본문 cross-ref ⊆ INDEX applies-to-phases)
- C-IDX-4 (grades.md ↔ INDEX applies-to-grades 집계)
- 코드 블록 내 mining illustrative example 잔존 deep cleanup
- v0.9.33 cold session 외부 검증 — fresh universe 의미 발현 + 무한 회귀 작동 + 0.999 도달 시까지 polishing

## v0.9.32 — 2026-05-06 (sprint-27 — conventions frontmatter backfill (88) + C-IDX-2 drift detection)

### 마일스톤

**sprint-20 의 후속 deliverable** — 88 conventions/*.md 에 router metadata frontmatter 일괄 backfill. drift detection 자동화 (C-IDX-2).

### 변경 — 88 conventions frontmatter backfill

각 `conventions/<id>.md` 의 머리에 다음 frontmatter 박힘:

```yaml
---
id: <name>
category: <core|interview|mindmap|domain|planning|multiverse|tournament|impl|quality|sprint|meta>
applies-to-phases: '[<phase numbers> 또는 [all]]'
applies-to-grades: '[G2..G5] 또는 [all]'
trigger-when: '<always 또는 specific 조건>'
indexed-in: conventions/INDEX.md
---
```

router metadata 단일 source = `conventions/INDEX.md`. backfill 스크립트가 INDEX 를 파싱하여 각 파일에 박음.

### 변경 — self_lint

- **C1 정정**: convention 첫 줄 `# Title` 검사 시 leading YAML frontmatter (`--- ... ---`) skip 추가.
- **C-IDX-2 신규** (sprint-27 v0.9.32): conventions/*.md frontmatter ↔ INDEX drift detection :
  - 각 파일이 frontmatter 보유 의무
  - 의무 필드: id / category / applies-to-phases / applies-to-grades / trigger-when / indexed-in
  - frontmatter `id` 가 filename stem 과 일치 검증
  - INDEX 에 router row 부재 시 fail
- 총 98 → 99 checks. all_ok=True.

### 효과

drift 자동 차단 — 컨벤션 frontmatter 와 INDEX 가 미일치하면 self_lint fail. 미래 cleanup / 신규 컨벤션 추가 시 INDEX 와 sync 강제.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.31 → 0.9.32.
- self_lint 99/99 PASS.

### 알려진 결손 (sprint-28+)

- C-IDX-3 (페이즈 본문 cross-ref ⊆ INDEX applies-to-phases) — 페이즈 본문이 인용한 컨벤션이 router 매칭 검증
- C-IDX-4 (grades.md 매트릭스 ↔ INDEX applies-to-grades 집계 일치)
- 코드 블록 내 mining illustrative example 잔존

## v0.9.31 — 2026-05-06 (sprint-26 — temporal narrative + mining narrative deeper cleanup)

### 마일스톤

8 conventions 의 temporal 표현 (`본 회차 (v0.9.X)` / `v0.9.X 까지의` / `v0.9.X 부터`) + 잔존 mining narrative example 추가 cleanup.

### 변경 — 5 bulk regex 패턴

- `본 회차 \(v0\.9\.\d+(?:\s+[^)]+)?\)` → `본 회차` (self-application context 의 history label 제거)
- `v0\.9\.\d+ 까지의 ` → `이전 `
- `v0\.9\.\d+ 부터 ` → `현재 `
- mining-specific Q answer narrative example → generic placeholder
- "Q3 의 truck 답이..." → "Q3 의 답이..." (truck domain word strip in narrative)

### 8 파일 갱신

aide-tree-multi-phase / budget-aware-fallback / decision-support-framing / domain-research-stacking / intent-completeness / multiverse-impl-fan-out / score-rubric-objectivity / tournament-blind-rerun.

### 보존 (preserve)

- `vNN_cold (v0.9.X)` cold session ref (e.g., `v01_cold (v0.9.9)`) — design rationale evidence, *cleanup 대상 아님*
- 코드 블록 내 mining 예시 (illustrative algorithmic context)

### bump

- plugin.json / SKILL.md frontmatter: 0.9.30 → 0.9.31.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-27+)

- conventions/INDEX.md frontmatter backfill (88 conventions × router metadata) → C-IDX-2/3/4 활성화 (drift detection 자동화)
- 더 깊은 mining narrative deep cleanup (코드 블록 내 example 잔존)

## v0.9.30 — 2026-05-06 (sprint-25 — 도메인 narration generic 화 + HARD-RULE 9.d 신규 (Da Capo산출물 body 의무))

### 마일스톤

사용자 우선순위 (2)+(3) 통합 sprint. 도메인 종속 예시 generic 화 + Da Capo산출물 body 의무 강화.

### 변경 — HARD-RULE 9.d 신규 (Da Capo산출물 body 의무)

HARD-CORE.md HR9 + orchestrator/SKILL.md HR9 동시 갱신. **frontmatter (bn) 외 본문 의무 신규**:

- `tournament-NN.md` 본문: 6-dim sub-scores 표 + winner reasoning + cross-universe 차이집합
- `dacapo-rerun-NN.md` 본문: lesson 본문 + Step F-G (lesson 도출 + anonymized prev winner) detail
- `dacapo-flow.md`: bq 의무 (Mermaid + timeline + step trace per round)

HARD-CORE.md 3782 → 3969 chars (C-HC1 cap 4000 PASS).

### 변경 — 도메인 narration generic 화 (4 파일)

mining haul/SimPy 도메인-specific 예시를 generic 표현으로 치환:

- `decision-support-framing.md`: "8 트럭 vs 12 트럭" 의사결정 예시 → "<도메인-specific 결정 지원 예시>"
- `domain-research-stacking.md`: "truck|haul|haulage" / "loader|crush|crusher" / "ore|mining|pit" trigger regex → "<entity1>|<entity2>|..."
- `intent-completeness.md`: "truck capacity = 100t from data/trucks.csv" → "<entity> <attribute> = <value> from data/<entity>s.csv"
- `magic-number-traceability.md`: "A9: empty truck speed factor 1.0, loaded 0.85 — typical mining haul" → "A<N>: <물리 가정 예시 — industry default>"
- `domain-research-stacking.md`: "MTBF / availability < 1.0 / grade variation" → "<도메인 NFR 1> / <NFR 2> / <NFR 3>"

본 하네스에 *built-in 도메인 종속 예시 0* 정합 — 사용자 per-project 작성 시 generic placeholder 를 도메인 entity 로 치환.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.29 → 0.9.30.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-26+)

- 잔존 mining domain 키워드 (truck/loader/crusher) 가 여전히 일부 conventions 본문에 도메인 *언급* 수준으로 남아있음 — 본 sprint 는 *예시* / *trigger regex* / *가정 패턴* 만 generic 화. *비문법적* (in narrative) 사용 잔존
- temporal narrative ("v0.9.X 까지", "본 회차") 잔존 case-by-case cleanup
- conventions/INDEX.md frontmatter backfill (C-IDX-2/3/4 활성화)

## v0.9.29 — 2026-05-06 (sprint-24 — conventions inline body history label cleanup)

### 마일스톤

conventions docs 본문의 *standalone* parenthetical history label 일괄 제거. 10 conventions 의 inline label cleanup.

### 변경 — 3 bulk regex 패턴

- `\(v0\.9\.\d+ (?:신규|갱신|변경|단순화|cross-ref|정합)\)` → 제거
- `\(v0\.9\.\d+ sprint-\d+ ...\)` → 제거
- `\(sprint-\d+ ...\)` → 제거

10 파일 갱신: cross-universe-lesson-distillation, dacapo-enforcement, dacapo-frontmatter-schema, diagrams, directional-simplification, intent-refresh-post-interview, measurement-contract, mindmap-quality-gardening, polyglot-code-quality, rubric-targeted-quality-gates. 총 ~234 chars 제거.

### 보존 (intentional)

- `[X.md](X.md) (v0.9.X)` — convention citation metadata (현재 룰 조합, history 아님)
- `cold session XXX (v0.9.X)` evidence — design rationale (회귀 정정 증거)
- `본 회차 (v0.9.X)` self-application context — meta 적용 시점 명시 (case-by-case 더 위험)

### bump

- plugin.json / SKILL.md frontmatter: 0.9.28 → 0.9.29.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-25+)

- 21 conventions 도메인 narration (mining/SimPy/truck) generic 화 — case-by-case 신중
- plan/dacapo phase body 의무 강화 (HARD-RULE 9.a 8 항목 외 dacapo산출물 body)
- "본 회차 (v0.9.X)" / "v0.9.X 까지" 등 temporal narrative cleanup

## v0.9.28 — 2026-05-06 (sprint-23 — conventions docs header history cleanup)

### 마일스톤

phase docs (sprint-22) 와 동일 원칙을 conventions docs 에 적용. 7 conventions 의 header history label 일괄 cleanup.

### 변경 — conventions docs header label 제거 (7 파일)

bulk regex 2 패턴:

**Pattern 1** — `^## v0\.9\.\d+ sprint-\d+ ...` / `^## sprint-\d+ ...` / `^## v0\.9\.\d+ ...` 헤더 라벨 제거 (2 파일):
- `competition.md`, `resources.md`

**Pattern 2** — `^#{2,3} ... \(v0\.9\.\d+ ...\)` 헤더 후미 괄호 라벨 제거 (5 파일):
- `budget-saturation-loop.md`, `mindmap-quality-gardening.md`, `multiverse-impl-fan-out.md`, `resources.md`, `sub-agents.md`

### 보존 (non-history 인용)

- `[`X.md`](X.md) (v0.9.X)` — convention 인용 metadata (현재 룰 조합 표시, history 아님)
- `cold session XXX 회귀 정정` — evidence-driven design rationale
- 본문 inline `(v0.9.X 신규)` non-header 위치 — 후속 sprint 에서 case-by-case

### bump

- plugin.json / SKILL.md frontmatter: 0.9.27 → 0.9.28.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-24+ 후속)

- 88 conventions inline body history (parenthetical citations + temporal narratives) 더 깊은 cleanup
- 21 conventions 도메인 narration (mining/SimPy/truck) generic 화
- plan/dacapo phase body 의무 강화 (HARD-RULE 9.a 8 항목 외)

## v0.9.27 — 2026-05-06 (sprint-22 — phase docs deep history cleanup)

### 마일스톤

**스킬 / 컨벤션 본문에서 sprint/version history label 제거 — history 는 본 CHANGELOG 단일 위치 정합** (사용자 원칙: "히스토리는 스킬의 노이즈"). 8 phase 파일의 14 history header 일괄 cleanup.

### 변경 — phase docs header label 제거 (8 파일)

bulk regex 패턴 적용 (`^## v0\.9\.\d+ sprint-\d+ ...` / `^## sprint-\d+ ...` / `^## v0\.9\.\d+ ...` → 라벨 제거 후 룰 본문만 유지):

- `phases/01-intent.md` : `## v0.9.19 sprint-13 갱신 — 마인드맵 A 등급 default + intent sprint loop` → `## 마인드맵 A 등급 default + intent sprint loop`
- `phases/04-clarify.md` : `## v0.9.20 sprint-14 신규 — Q-D-AUDIENCE + rubric skeleton` → `## Q-D-AUDIENCE + rubric skeleton`
- `phases/05-critique.md` (2개) : `## sprint-19 — phase 05 종료 직후 mandatory 2nd refresh cycle` → `## phase 05 종료 직후 mandatory 2nd refresh cycle` / `## v0.9.20 sprint-14 — Directional Simplification 표 의무` → `## Directional Simplification 표 의무`
- `phases/06-plan.md` (4개) : v0.9.19~22 sprint-13~16 4 헤더 모두 제거
- `phases/07-plan-recursion.md` : `## v0.9.22 진입 의무 — Da Capo enforcement gate (HARD-RULE 9.p)` → `## 진입 의무 — Da Capo enforcement gate (HARD-RULE 9.p)`
- `phases/08-implement.md` : `## v0.9.22 sprint-16 Da Capo enforcement gate` → `## Da Capo enforcement gate`
- `phases/09-quality-gates.md` (3개) : `## sprint-18 신규 — 90→100 cap 풀기 (runtime 검증 layer)` → `## runtime 검증 layer (90→100 cap 풀기)` / `## 9 정적 게이트 + N derived 게이트 (v0.9.18)` → `## 9 정적 게이트 + N derived 게이트` / `## v0.9.20 sprint-14 — Rubric-Targeted Gates + 게이트 강화` → `## Rubric-Targeted Gates + 게이트 강화`
- `phases/10-test-loop.md` (2개) : `## v0.9.19 sprint-13 — Sprint Trinity 3 axis 분배` → `## Sprint Trinity 3 axis 분배` / `## v0.9.20 sprint-14 — Grader-in-Sprint Dual-Objective` → `## Grader-in-Sprint Dual-Objective`

### 변경 — self_lint history-agnostic

C-DCL-FLOW-LOG : `phases/08-implement.md` 의 `v0.9.22 sprint-16` 라벨 의존 제거. `Da Capo enforcement gate` keyword 만 검사 — history 라벨 cleanup 후에도 PASS.

### 알려진 결손 (sprint-23+ 후속)

- 88 컨벤션 본문 inline history narration cleanup (29 파일에 sprint-XX/v0.9.X 본문 라벨 잔존, 21 파일에 mining/SimPy 도메인 예시 잔존)
- plan/dacapo phase body 의무 강화 — HARD-RULE 9.a 8 항목 외에 dacapo산출물 (tournament.md / dacapo-rerun.md / dacapo-flow.md) body 의무 본문 강화

### bump

- plugin.json / SKILL.md frontmatter: 0.9.26 → 0.9.27.
- self_lint 98/98 PASS.

## v0.9.26 — 2026-05-06 (sprint-21 — HARD-RULE 9.a body 8 항목 강화 + 부분 history 정리)

### 마일스톤

**sprint-05-c 정공 재확인.** 사용자 직접 지시 — *별도 impl-design.md 신설 안 함* (plan + impl-log 응집 보존, plan 단일 source 강화). 초안 시도 (08-A doc cycle + 08-B code cycle 분화) 는 sprint-05-c 결정과 충돌하여 **즉시 폐기 + rollback** + 정공 (`HARD-RULE 9.a body 8 항목 강화`) 으로 전환.

### 변경 — HARD-RULE 9.a body 8 항목 의무

이전 (sprint-17): 5 항목 (파일 경로 ≥ 5 / Mermaid sequence + usecase + interface AND / TODO DAG)
sprint-21 강화 (8 항목 의무):
1. 파일 경로 ≥ 5
2. Mermaid sequenceDiagram ≥ 1 AND usecase/graph ≥ 1 AND 인터페이스 정의 ≥ 3
3. TODO DAG (T-NNN ID + 의존 + 완료 조건)
4. **모듈 의존 다이어그램** (per-module sequenceDiagram ≥ 모듈 수)
5. **Data structure invariants 표** (Invariants/Topology/Access/Bounds 4 항)
6. **Test surface mapping** (invariant ↔ test signature 1:1)
7. **Error handling / fallback policy** (모듈별)
8. **Implementation guidance per TODO** (알고리즘 / DS / 라이브러리 / pseudo-code — implementer 가 따라가는 디자인 본문)

→ plan 본문 풍부화 + impl 문서 sub-cycle 신설 0 (응집 보존). HARD-CORE.md HR9.a + orchestrator/SKILL.md HR9.a 동시 갱신.

### 부분 history narration 정리 (사용자 원칙 정합)

5 conventions 의 sprint/version 헤더 cleanup:
- `diagrams.md` : `## sprint-17 — HARD-RULE 9.a OR → AND` → `## HARD-RULE 9.a — sequence + usecase + interface 셋 다 의무 (AND clause)`
- `diagrams.md` : `## v0.9.19 sprint-13 — per-module fan-out` → `## per-module fan-out`
- `intent-completeness.md` : `## v0.9.19 sprint-13 갱신 — intent sprint loop trigger` → `## intent sprint loop trigger`
- `plan-tree.md` : `## v0.9.16 sprint-10 — 패배 universe 학습 전이` → `## 패배 universe 학습 전이`
- `grades.md` : `## v0.9.17 변경 — 키워드 매칭 폐기` → `## 키워드 매칭 폐기`

→ 5 헤더 sprint/version 라벨 제거 (history → CHANGELOG 단일 위치 정합). 88 컨벤션 본문 deep history 정리는 sprint-22+ 후속.

### 변경 — self_lint

C-DIAG-AND-COVERAGE keyword 갱신: `sprint-17` / `OR → AND` 라벨 의존 제거. 현재 룰 (`sequenceDiagram ≥ 1 AND` / `셋 다 의무`) 만 검사.

### 알려진 결손 (sprint-22 후속)

- 88 컨벤션 본문 deep history narration cleanup (21+ 파일에 mining/SimPy 등 도메인 예시 잔존, sprint-XX/v0.9.X 본문 라벨 잔존)
- plan/dacapo phase 분화 검토 (impl 은 sprint-05-c 정공으로 결론, plan/dacapo 도 동일 원칙 — 별도 sub-doc 신설 0, *body 의무 강화* 정공)

### bump

- plugin.json / SKILL.md frontmatter: 0.9.25 → 0.9.26.
- self_lint 98/98 PASS.

## v0.9.25 — 2026-05-06 (sprint-20 — 정보 아키텍처 재설계 + 도메인 어댑터 제거)

### 마일스톤

**`theseus-harness-slim-proposal.md` 수렴.** SKILL.md 비대화 (32280 chars / 88 컨벤션 카탈로그 누적) 를 *구조적 분리* (압축 X) 로 영구 정리. lazy-load 3 분류 (always-load / phase-scoped / router-matched).

### 변경 — 신규 산출물

- **`HARD-CORE.md`** (신규) — always-load supremacy 본문. ≤ 4000 chars (C-HC1 lint 부풀음 영구 차단). HR1 (첫 동작 4 금지) + HR8 (G1~G5 의무 산출물) + HR9.a~c 본문 의무 + Layer 3 H1~H5 + 페이즈 04 외 인터럽트 0 + frontmatter 핑거프린트 체인.
- **`conventions/INDEX.md`** (신규) — 88 컨벤션 router 단일 표 (id / cat / phases / grades / trigger). sprint/version 컬럼 부재 — history 는 본 CHANGELOG 만. C-IDX-1 lint 가 conventions/*.md ↔ INDEX row 1:1 매칭 검증.
- **`SKILL.md`** 슬림화 — 32280 → ~6700 chars (-79%). 인덱스 + phase lookup + agent 18 링크 + 채점기 / 템플릿 / 산출물 트리 / 그레이드. *카탈로그 나열 안 함*.

### 변경 — 도메인 어댑터 제거 (벤치 어뷰징 정리)

- 삭제: `conventions/domain-adapters/mining-haulage.md`, `conventions/domain-adapters/des-modeling.md`, 디렉터리.
- `conventions/domain-research-stacking.md` (aj) + `conventions/domain-failure-patterns.md` (ay) — 본문 도메인 종속 예시 제거. 프레임워크 보존 (사용자 per-project 어댑터).
- 본 하네스에 *built-in 도메인 어댑터 0* — `feedback_harness_strengthening_methodology` 정합.

### 변경 — self_lint

- 신규 2 룰: **C-HC1**, **C-IDX-1**.
- 기존 lint 갱신: C1 (INDEX.md 제외) / C2 (SKILL ∪ INDEX) / C-OD (HARD-CORE.md keyword) / C-IRPI (SKILL ∪ INDEX).
- 96 → 98 checks. all_ok=True.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.24 → 0.9.25.

### 알려진 결손 (sprint-21 후보)

- **페이즈 fan-out**: intent 페이즈 (01→02→03 *문서화 / 콜드리뷰 / 판단* 분화) 와 달리 plan / impl / dacapo 는 페이즈 자체 미분화. 페이즈 06/08/dacapo 안에 *생성 / 콜드리뷰 / 판단* 분리 후 별도 페이즈 + 별도 에이전트.
- **convention frontmatter backfill**: 88 컨벤션 router 메타 박힘 + C-IDX-2/3/4 활성화.
- **컨벤션 본문 history narration 정리**: "sprint-NN 신규" / "v0.9.X" 류 본문 history 제거 (sprint-20 은 SKILL/INDEX 만).

## v0.9.24 — 2026-05-06 (sprint-19 — Da Capo runtime polishing + plan/impl richness + 2nd refresh cycle)

### 마일스톤
**cold session 003 (v0.9.23) 90/100 plateau 정정.** sprint-15~18 enforcement 의 마지막 빈 구멍 5 동시 닫음.

### 변경 — 6 컨벤션 신규 (ce~cj, HARD-RULE 9.gg~ll)

- `dacapo-mandatory-rerun.md` (ce, 9.gg) — winner ≥ 임계 도달해도 무조건 ≥ 1 rerun. C-DCMR.
- `plan-tournament-scoring-strict.md` (cf, 9.hh) — tournament 6-dim weighted, 1-5 cold-read coarse reject. C-PTSS.
- `canonical-not-stub.md` (cg, 9.ii) — canonical ≥ winner 80% inline 또는 shared schema. C-CNS.
- `impl-multiverse-strict.md` (ch, 9.jj) — phase 08 G4+ 7 조건 게이트. skip 자백 reject. C-IMS.
- `intent-refresh-post-critique.md` (ci, 9.kk) — phase 05 → 06 사이 2nd intent refresh + 04/05 cascade. C-IRPC.
- `cross-phase-shared-context.md` (cj, 9.ll) — shared 정보 단일 위치 + asof_fingerprint drift 차단. C-CPSC.

### bump
- plugin.json: 0.9.23 → 0.9.24. self_lint 90 → 96 checks.

## v0.9.23 — 2026-05-05 (sprint-17+18 — orchestrator 슬림화 + intent-refresh + cap 측정-only + runtime enforcement 5)

### 마일스톤
**cold session 002 + 003 회귀 다발 정정.** orchestrator 287→121 lines (-58%) + 6 신규 컨벤션 (by~cd) + 9 신규 self_lint.

### sprint-17 (orchestrator 구조 정정)

- `intent-refresh-post-interview.md` (by) — phase 04 → 05 사이 의도 refresh 4 framing universe + 01-additional. C-IRPI.
- orchestrator/SKILL.md 287→121 lines (HARD-RULE 9.a~aa prose 분리).
- `dacapo-enforcement.md` (bm) — 시간 cap 측정 only. forward projection regex reject. min loop attempt rerun ≥ 1. C-DCL-NO-FORWARD-PROJECT/MIN-LOOP-ATTEMPT/CAP-MEASURED.
- `diagrams.md` (c) + HARD-RULE 9.a — OR → AND. C-DIAG-AND-COVERAGE.

### sprint-18 (runtime enforcement 5, 도메인 무관)

- `readme-numbers-from-summary.md` (bz, 9.bb), `reproducibility-doublecheck.md` (ca, 9.cc), `magic-number-traceability.md` (cb, 9.dd), `dead-code-zero.md` (cc, 9.ee), `submission-portability.md` (cd, 9.ff). C-RNFS / C-RDC / C-MNT / C-DCZ / C-SPB.
- 도메인 종속 룰 (transient-state-justification 등) 의도적 제외.

### bump
- plugin.json: 0.9.22 → 0.9.23. self_lint 81 → 90 checks.

## v0.9.22 — 2026-05-05 (sprint-16 — 의사코드 → runtime guard 변환 + 7 차원 만점 push)

### 마일스톤
**cold session winner=0.892 + rerun=0 + fallback="" 회귀 정정.** 12 신규 컨벤션 (bm~bx) + HARD-RULE 9.p~aa.

### Phase 1 enforcement layer (bm~br, 9.p~u)
- `dacapo-enforcement.md` (bm), `dacapo-frontmatter-schema.md` (bn), `shadow-grader-zero-context.md` (bo), `dacapo-skip-sentinel.md` (bp), `dacapo-flow-trace.md` (bq), `phase-lineage-viewer.md` (br).

### Phase 2 7 차원 만점 push (bs~bx, 9.v~aa)
- `domain-model-completeness.md` (bs), `data-structure-invariants.md` (bt), `simulation-physical-invariants.md` (bu), `experimental-control-protocol.md` (bv), `results-decision-mapping.md` (bw), `idiomatic-code-quality.md` (bx).

### bump
- plugin.json: 0.9.21 → 0.9.22. self_lint 12 신규.

## v0.9.21 — 2026-05-05 (sprint-15 — intra-phase Da Capo Loop 의사코드 hook)

### 마일스톤
**multiverse + sprint retry 통합** — phase 06 (plan) + phase 08 (impl) 안에 통합 의사코드 loop (Step A~G 다카포). cold session winner=0.853 (G4 임계 미달) 재경합 0 회 회귀 정정.

### 변경 — 1 컨벤션 신규 (bl, HARD-RULE 9.o)
- `intra-phase-dacapo-loop.md` (bl, 9.o) — Step A multiverse fan-out → B tournament → C shadow grade → D 4-conjunction AND threshold → E cap → F lesson + winner 갱신 → G anonymized prev winner + width-1 fresh → A 재진입. self_lint C-DCL-WIN-THRESHOLD/RERUN-LOG/ANON 3 신규.

### bump
- plugin.json: 0.9.20 → 0.9.21.

## v0.9.20 — 2026-05-05 (sprint-14 — cold evaluator feedback 7 컨벤션, 94→97 plateau 돌파)

### 마일스톤
**cold session 자체 90 vs 외부 grader 97 의 7pt 갭 정정.** 7 컨벤션 신규 (be~bk) + HARD-RULE 9.h~n.

### 변경 — 7 컨벤션 신규
- `grader-in-sprint.md` (be, 9.h), `contested-decision-multiverse.md` (bf, 9.i), `directional-simplification.md` (bg, 9.j), `commentary-policy.md` (bh, 9.k), `measurement-contract.md` (bi, 9.l), `rubric-driven-doc-skeleton.md` (bj, 9.m), `rubric-targeted-quality-gates.md` (bk, 9.n).

### bump
- plugin.json: 0.9.19 → 0.9.20.

## v0.9.19 — 2026-05-05 (sprint-13 — 깊이 강화 + 발현 빈도 격상 4 컨벤션)

### 마일스톤

**v0.9.18 sprint-12 발현 강제 메커니즘 도입 후 사용자 진단 7 항목 (2026-05-05) — 마인드맵 풍부화 / 다이어그램 모듈별 분할 / 유니버스 폭 증량 / plan·impl 디테일 향상 / intent·plan·impl 3 axis sprint loop / 0.999 지향 2회 이상 무한 / 전체 시간 cap.** v0.9.18 까지의 *룰 본문 작성* 면 진전 후, 본 sprint-13 = *발현 default 격상* 단계. 자기 적용 self-eating dogfood — 본 sprint 의 산출물 자체가 v0.9.19 신규 컨벤션 4 의 자기 적용 사례.

### 변경 — 4 컨벤션 신규 (ba~bd)

- **`mindmap-richness-default.md`** (ba) — 페이즈 01 §9 마인드맵 A 등급 default 격상 (≥25 노드 / 4 axis × ≥4 sub / 3 axis sub-sub + 1 axis sub-sub-sub). intent-extractor 프롬프트 templated stub 의무. B fallback PASS *with lesson*. C-MRD-A-DEFAULT self_lint. v0.9.13 mindmap-quality-gardening 의 *A 옵션* → *A default* 격상.
- **`per-module-diagram-fan-out.md`** (bb) — use-case / sequence 다이어그램 모듈별 분할 default. 트리거: 모듈 ≥ 4 OR consumer-producer 페어 ≥ 6. 모듈 ≤ 3 시 단일 통합 OK. C-PMDF self_lint. v0.9.6 diagrams.md 의 *negative anti-pattern* → *positive default* 격상.
- **`multiverse-width-default-bump.md`** (bc) — 폭 default 격상: G2=2 / G3=5 / G4=7 / G5=9. 옵션 default (사용자 명시 ack): G3=10 / G4=12 / G5=16. budget profile cap 동기 갱신 (resources.md universe parallel cap G3=10/G4=12/G5=16). budget tight 시 fallback 폭 + `fallback_reason` frontmatter 의무. C-MWDB self_lint. sprint-05-b의 *폭 3/4/6 plateau* 격상.
- **`intent-plan-impl-sprint-trinity.md`** (bd) — sprint loop 3 axis (intent / plan / impl) × 각 ≥ 2 회. budget 분배 default: intent 20% / plan 30% / impl 50%. 임계 0.999 default (모든 그레이드 G2~G4 / G5 = 0.99999 보존). early stop violation = (axis 별 < 2) OR (budget < 80%). C-IPI self_lint. v0.9.8 sprint-regression-loop + v0.9.15 budget-saturation-loop 의 *impl 단위만 axis* → *3 axis trinity* 확장.

### 변경 — 6 컨벤션 갱신

- `mindmap-quality-gardening.md` (ak) — Quality 등급 표 A default 격상 + B fallback PASS with lesson + ba cross-ref
- `plan-tree.md` (u) — 그레이드 폭 매트릭스 갱신 (G3=5 / G4=7 / G5=9 + 옵션 default) + bc cross-ref
- `multiverse-impl-fan-out.md` (ag) — 그레이드별 universe 수 sync + bc cross-ref
- `diagrams.md` (c) — 안티 패턴 d/e 추가 (모듈 ≥ 4 단일 시퀀스 + 모듈 ≤ 3 over-fragmentation) + bb cross-ref
- `budget-saturation-loop.md` (an) — `should_continue_sprint` axis 별 sprint < 2 시 무조건 추가 + Soft-converge handoff `sprint_axis_counts` 의무 + bd cross-ref
- `intent-completeness.md` (aw) — intent sprint loop trigger (§k 9 sub PASS 라도 ≥ 2 회 polish) + bd cross-ref
- `resources.md` — universe parallel cap 갱신 (G3=10/G4=12/G5=16) + wall-clock budget per universe 갱신

### 변경 — 4 페이즈 갱신

- `phases/01-intent.md` — `v0.9.19 sprint-13 갱신` 섹션 + ba A default + bd intent sprint loop + Templated Section §9 (universe-2 merge — 발현 강제)
- `phases/06-plan.md` — `v0.9.19 sprint-13 갱신` 섹션 + bc 폭 default 5/7/9 + bb per-module 다이어그램 + bd plan sprint loop + Templated per-module section
- `phases/08-implement.md` — `v0.9.19 sprint-13 갱신` 섹션 + bb universe-N 별 use-case 분리 + bd impl sprint loop + 폭 default sync
- `phases/10-test-loop.md` — sprint trinity 3 axis 분배 + Templated report.json schema + early_stop_violation 강화

### 변경 — HARD-RULE 9 (orchestrator/SKILL.md)

기존 9.a/b/c (산출물 *내용* 의무) 에 d/e/f/g 4 항목 추가 (산출물 *발현 빈도* 강제):
- 9.d: 마인드맵 풍성도 (mindmap_quality_grade ∈ [A, B] 만 PASS)
- 9.e: per-module 다이어그램 (모듈 ≥ 4 트리거)
- 9.f: multiverse 폭 default (G3=5/G4=7/G5=9)
- 9.g: sprint trinity (axis 별 ≥ 2 sprint)

### 변경 — version bump

- plugin.json / marketplace.json / harness SKILL.md / orchestrator SKILL.md frontmatter: 0.9.18 → 0.9.19
- 컨벤션 카탈로그 51 → 55 (4 신규 ba~bd)

### 검증

- 본 sprint 자체가 v0.9.19 self-eating dogfood:
  - 마인드맵 36 노드 A 등급 (frontmatter mindmap_quality_grade=A) — ba 자기 적용
  - 5 모듈 per-module use-case 다이어그램 분할 — bb 자기 적용 (모듈 ≥ 4 트리거 충족)
  - plan-tree 폭 4 universe (G4 default 7 의 budget-aware fallback, fallback_reason 명시) — bc 자기 적용
  - sprint trinity intent 2 + plan 2 + impl 2 = 6 sprint — bd 자기 적용
- 산출물: `.ShipofTheseus/theseus_self_v0919/` 트리 (timing/start.json, naming/00-naming.md, intent/01-intent.md ~ 05-decisions.md, plan/{tournament.md, 06-plan.md, 07-plan-review.md, candidates/universe-{1..4}/}, impl/08-impl-log.md, sprints/{intent,plan,impl}-{01,02}/, quality/09-quality-gate.md, handoff/14-handoff.md)

### 후속

- v0.9.19 적용 cold session — 4 신규 컨벤션 발현 검증 (mindmap A 등급 / per-module 다이어그램 / 폭 default 5+ / sprint trinity ≥ 6) + 점수 변화 측정
- intent-extractor 프롬프트 templated mindmap stub 적용 효과 측정 (v0.9.18 sprint-12 의 §k 9 sub 발현 강제 패턴 계승)
- 폭 default 격상 (G3=5/G4=7) 의 budget profile cap 충돌 모니터링 — fallback_reason 빈도 추적

---

## v0.9.18 — 2026-05-04 (sprint-12 — 본 스킬 자체 가치 개선 4 컨벤션 + 발현 강제 메커니즘)

### 마일스톤

**v0.9.17 cold session (`001-mine-throughput-theseus`) 검토에서 *준비-vs-동작* 갭 재발견 — 마인드맵 ASCII 회귀 + §i NFR / §j grade signals / §k 9 sub 모두 미발현.** 사용자 진단: "**제안은 스킬 개선인가 스코어링 개선인가**" (분리 명확화) → "**외부 의존 없는 단일 스킬로서 가치만 개선**" (E reviewer-form alignment 제외). 4 컨벤션 신규 + 발현 강제 메커니즘 (intent-extractor 프롬프트 강화 + 페이즈 진입 거부) 동시 박음.

### 변경 — 4 컨벤션 신규

- **`intent-completeness.md`** (A) — 페이즈 01 의도 §k 9 sub-criterion 의무: system boundary / entities / resources / events / state variables / assumptions / **limitations** / performance measures / **data-derived vs introduced 분리**. v0915-cold01 외부 채점 -2pt (Conceptual) 직접 매핑.
- **`process-flow-coherence.md`** (B) — 페이즈 09 게이트 8 신규: cycle / state machine / workflow / DES / pipeline / transaction 정합 자기 검증. all_states_reachable / cycle_invariant / orphan_states / error_paths_explicit / state_visit_count > 0. `process_flow_applicable: false` 시 skip.
- **`domain-failure-patterns.md`** (C) — 페이즈 09 게이트 9 신규: domain-adapters/<domain>.md 의 `failure_patterns:` 자동 검증. severity (cap_total / cap_correctness / cap_experimental / cap_results / warning) 별 점수 cap. v0.9.16 regression-derived-lint-rule-autogen 와 우로보로스 정합.
- **`decision-support-framing.md`** (D) — 페이즈 14 handoff 의 결정 질문 (Q1~QN) 마다 *operational implications + trade-off framing + opportunity-cost* 본문 의무. evidence_decision_support 매핑.

### 변경 — 도메인 어댑터 failure_patterns 항목 신규

- `domain-adapters/des-modeling.md` — DFP-DES-1~7 (static calc / no replications / hard-coded / queue without resource / credit at start / per-direction Resource / global RNG)
- `domain-adapters/mining-haulage.md` — DFP-MH-1~5 (no saturation / bottleneck without composite / no capex / per-direction ramp / availability=1.0 무명시)

### 변경 — 발현 강제 메커니즘 (사용자 핵심 요구)

**룰 작성만으로는 부족** — v0.9.13 mindmap-quality-gardening / v0.9.6 nfr-derivation 모두 cold session 에서 발현 0 였음. 본 sprint 가 발현 강제 메커니즘 동시 박음:

- **`agents/intent-extractor.md` 프롬프트 전면 재작성** — 11 단계 의무 순서 + §k 9 sub *templated section* + 마인드맵 *Mermaid block 의무* (ASCII text tree 금지) + §j grade signals 두 산출물 + frontmatter `applied_conventions` 자동 박음 + 하드 룰 (§k / §j 누락 = 페이즈 02 / Q-G1 진입 거부)
- **페이즈 09 본문 9 게이트** (기존 7 → 9): 게이트 8 cycle coherence + 게이트 9 domain failure patterns
- **페이즈 14 본문 §j Decision-support framing 의무**

### 변경 — self_lint 룰 신규 4

C-IC / C-PFC / C-DFP / C-DSF — 4 컨벤션 본문 + cross-ref 검증

### 변경 — 컨벤션 51 누계

47 (v0.9.16) + anti-patterns + 4 (v0.9.18) = 51. SKILL.md 컨벤션 카탈로그 표 av (anti-patterns) + aw~az (sprint-12 4) 추가.

### 변경 — version bump

- plugin.json / marketplace.json / harness SKILL.md / orchestrator SKILL.md frontmatter: 0.9.17 → 0.9.18
- SKILL.md fragmentation 정리 (14361 → 14001 chars, C26 PASS) — 컨벤션 description / 페이즈 표 셀 압축

### 검증

- self_lint 69/69 PASS (all_ok=True, lint_score=1.0)
- pytest 109/109 PASS, 회귀 0
- v0915-cold01 retro 적용 시 Conceptual 18 → 19~20 (limitations + data-derived 분리) / Sim 18 → 19 (cycle coherence) / Results 14 → 15 (decision-support framing) — 추정 +3~4pt

### 후속

- v0.9.18 적용 cold session — Mermaid 마인드맵 + §i/§j/§k 모두 발현 검증 + 점수 변화 측정
- *발현 강제 메커니즘* 의 효과 측정 — v0.9.13 mindmap-quality-gardening 처럼 룰만 박고 발현 0 가 반복되지 않는지

---

## v0.9.17 — 2026-05-04 (sprint-11 — 키워드 매칭 폐기 + 페이즈 01 다중 신호 grade 추정 + default G4)

### 마일스톤

**v0.9.16 cold02 (synthetic_mine_throughput_v0915_cold02) 가 자동 G3 으로 떨어진 결손 정정.** 사용자 진단 — "그레이드 판단이 키워드 기반인 것 부터 잘못. intent 페이즈 자체가 grade 분류와 강결합. 마인드맵 복잡도는 한 차원일 뿐. 최대한 많은 지표로 판단. default G4-G5".

### 변경 — `grade_assess.py` 전면 재작성 (v2)

- **키워드 매칭 알고리즘 폐기** — `TRIGGERS_G5/G4/G2/G1` 키워드 set 전부 제거. 사용자 원문 키워드는 도메인 어휘 추적 못함 (cold02 = simulation-bench 작업이 default G3 으로 떨어진 직접 원인)
- **`GradeSignals` dataclass — 18+ 차원 다중 신호** 페이즈 01 의도 §a~§i + 마인드맵 모든 섹션:
  - 마인드맵: node_count / axis_count / max_depth / external_systems / domain_nouns
  - 의도 §a: observable_results_count
  - §c: explicit_non_goals_count
  - §d: constraint_count / explicit_thresholds_count
  - §e: domain_term_count
  - §f: stakeholder_count
  - §g: success_metric_count / measured_metrics_count
  - §h: open_question_count
  - §i: derived_nfr_count / qualitative_adjective_count
  - boolean: multi_scenario / external_evaluator / fe_be_split / safety_critical / irreversible_change
  - integer: refactor_scope_module_count
- **default = G4** — 본 하네스 호출 자체가 G4+ 의도 신호. G3 작업은 본 하네스 없이도 진행 가능
- **G5 상향** = `safety_critical` 또는 `irreversible_change` 사용자 *명시 ack* 만. 자율 키워드 매칭 0
- **G3 하향** = 12 차원 모두 negative + `mindmap_node_count ≥ 1` (positive evidence) — *데이터 부재 ≠ 단순함*
- **G2 하향** = G3 + nodes ≤5 + 단일 모듈 + 단일 도메인 용어
- **호출 시점 변경** — 호출 직후 사용자 원문 → 페이즈 01 (의도 + 마인드맵) 완료 후. intent-extractor 가 페이즈 01 산출물 작성 시 부산물로 `intent/01-grade-signals.json` + `intent/01-mindmap-signals.json` 박음

### 변경 — `conventions/grades.md`

- 키워드 매칭 알고리즘 절 (line 24-69) 전부 제거 → 다중 신호 카탈로그 표 신규
- default = G4 명시
- G3 = "본 하네스 가치 부분만 활용 — G3 작업은 본 하네스 없이도 진행 가능" 명시
- 5 차원 escalation triggers 카탈로그 + 12 차원 단순 증명 룰 명시

### 변경 — `phases/01-intent.md`

§j Grade signals 산출 단계 신규 — intent-extractor 가 §a~§i + 마인드맵을 18+ 차원 신호로 추출. 성공 기준 §e 추가 (산출물 박힘 검증).

### 변경 — `phases/04-clarify.md`

Q-G1 본문 정정 — `grade_assess.py` 가 `intent/01-grade-signals.json` + `intent/01-mindmap-signals.json` 입력으로 추정. default G4 명시 + escalation triggers 매칭 list / 단순 증명 차원 두괄식 표시 + G3·G2 하향 시 사용자 ack 의무 명시.

### 변경 — self_lint 룰 신규

`C-GAv2` (v0.9.17 sprint-11) — grade_assess v2 검증:
1. 폐기 키워드 set (`TRIGGERS_G5/G4/G2/G1`) 잔존 0
2. 다중 신호 dataclass (`GradeSignals`) + escalation triggers + 단순 증명 + default_was 본문 보유
3. grades.md 의 default G4 + 키워드 매칭 폐기 명시 + 18+ 신호 카탈로그
4. phase 01 §j 산출물 의무
5. phase 04 Q-G1 default G4 명시

### 변경 — `test_grade_assess.py` 전면 재작성

기존 13 test 모두 `--request <text>` 키워드 인터페이스 가정. 14 신규 test (다중 신호 인터페이스):
- default G4 (no signals / empty signals)
- G5 명시 ack (safety_critical / irreversible_change)
- G3 단순 증명 / G2 trivial 증명
- escalation triggers 매칭 (external_evaluator / measured / multi-scenario / fe_be / domain_adapter)
- 키워드 매칭 폐기 검증
- user_confirmation always True / 5 보기 항상 / G1 진행 보존 / signals_used echo

### 검증

- self_lint 69/69 PASS (all_ok=True, lint_score=1.0)
- pytest 109/109 PASS (이전 11 fail = 키워드 인터페이스 호환성 — 재작성으로 해소)
- cold02 retro 적용 시 자동 G4 (escalation triggers 5 차원 매칭) — 임계 0.999 + 14 페이즈 풀 + 멀티버스 폭 4 활성

### 후속

- v0.9.17 적용 cold session — cold02 대비 점수 변화 측정 (G3 → G4 임계 강화 효과 검증)

---

## v0.9.16 — 2026-05-04 (sprint-10 — 발현 검증 6 메타 컨벤션)

### 마일스톤

**v0915-cold01 외부 채점 93/100 진단 후 *준비-vs-동작* 갭 정정.** 자체 추정 == 외부 채점 (둘 다 93) 으로 score-rubric-objectivity 발현 PASS, 그러나 94 plateau 안 깨짐. 사용자 피드백: "준비한 부분이 *구동 안 됨* / *제대로 동작 안 함* / 코드 퀄리티 점수 극복" 3 가설 + *케이스 종속 룰 금지, 제너럴 메타 룰만*. 본 sprint 가 6 메타 컨벤션 동시 신규.

### 변경 — 발현 검증 #1 `convention-traceability.md`

페이즈 산출물 frontmatter `applied_conventions: [...]` 의무 + 페이즈별 *expected* 컨벤션 카탈로그 (contracts.md). 회차 종료 시 zero-applied 컨벤션이 expected 와 교집합 = self_lint fail. 본 하네스 41+ 컨벤션 중 *어느 것이 실제로 발현됐는지 추적 메커니즘* 0 → 검출 가능.

### 변경 — 발현 검증 #2 `sprint-score-delta-tracking.md`

매 sprint NN+1 의 score - sprint NN 의 score = delta. EXPECTED_DELTA 범위 (content_depth 0.005~0.030 / enforcement 0.000~0.005 / etc.) 위반 시 `LABEL_VIOLATION` self_lint fail. budget-saturation-loop 의 lesson type 4 분류가 *honest* 인지 사후 측정.

### 변경 — 발현 검증 #3 `evidence-driven-sprint-planning.md`

handoff 의 `evidence_missing` 항목 → 다음 sprint 의 `next_sprint_candidates` 자동 생성. `free_lesson_allowed: false` — agent 가 *자유롭게* lesson 못 정함, evidence_missing / zero_applied / bench_required 중에서만. budget-saturation-loop + score-rubric-objectivity 의 *결손 → 보강* 자동 흐름.

### 변경 — 발현 검증 #4 `cross-universe-lesson-distillation.md`

Tournament resolve 시 패배 universe 의 *핵심 약점 ≥ 1-2 줄* 을 우승 본문 (Patterns to Avoid 절) 흡수 의무. 페이즈 08 / 10 가 `avoid_patterns` 입력 받음 → forbidden_strategies 동급 처리. ensemble-synthesis-default 의 *합집합* 차원이 *합집합 + 교집합 + 차이집합* 으로 격상.

### 변경 — 발현 검증 #5 `regression-derived-lint-rule-autogen.md`

페이즈 11 회귀 4 분류 정정 commit 시 *동일 차원 회귀 차단 self_lint 룰 신규* 의무. `lint_rule_proposal` frontmatter + `regression_lint_registry.py` 등록. self_lint CHECKS 가 정적 + 동적 합성 — 회귀 학습이 *영구 자산화*. 본 하네스 *우로보로스 자기 강화* 메커니즘화.

### 변경 — 발현 검증 #6 `polyglot-code-quality.md`

build-and-config §8 ruff 통합 = Python 전용 → 9 언어 카탈로그 (Python ruff / Go golangci-lint / TS biome / Rust clippy / Java checkstyle / Ruby rubocop / C/C++ clang-tidy / Kotlin detekt) + 6 메트릭 (cyclomatic / function_length / nesting_depth / duplicate_blocks / lint_errors / format_diff). v1.0 외부 maintainer 채택 prerequisite 인프라.

### 변경 — self_lint 6 룰 신규

C-CT / C-SDT / C-EDP / C-CULD / C-RDLR / C-PCQ. 각 컨벤션 본문 키워드 + cross-reference 검증.

### v0915-cold01 외부 채점 분석 (motivation)

| 차원 | 점수 | 만점 | 갭 |
|---|:-:|:-:|:-:|
| Conceptual | 18 | 20 | -2 |
| Sim correctness | 18 | 20 | -2 |
| Data·topology | 14 | 15 | -1 |
| Results | 14 | 15 | -1 |
| Code quality | 9 | 10 | -1 |
| Experimental design | 15 | 15 | 0 |
| Traceability | 5 | 5 | 0 |
| **Total** | **93** | **100** | **-7** |

자동 검증 53/53 PASS. 자체 추정 == 외부 채점 = score-rubric-objectivity 정직성 검증.

### 거부 (case-specific 후보)

초기 4 후보 (Conceptual narrative quantitative gate / Sim correctness analytical-bound proof / Results decision-support enforcement / Code quality micro layer) **거부** — bench rubric 항목 (sensitivity matrix / capex / opportunity-cost / type hints) 에 매여 케이스 종속. 메모리 `feedback_harness_strengthening_methodology.md` 위반.

### 검증

self_lint 6 룰 신규 모두 PASS / pytest 회귀 0 / self_score 1.0 / 임계 0.99999 통과. C26 (SKILL.md 길이) + C41 (description 압축) = pre-existing.

### 후속

- v0.9.16 적용 cold session — 진짜 0.999 도달 검증 (94 plateau 돌파)
- C26 정리 — SKILL.md 의 47 컨벤션 인덱스를 별도 INDEX 파일로 fragmentation
- C41 정리 — description 추가 압축

---

## v0.9.15 — 2026-05-04 (sprint-09 — budget saturation + rubric objectivity)

### 마일스톤

**94 plateau 돌파 룰** — v01_cold (v0.9.9) / v091_cold01 (v0.9.12) / v0914_cold01 (v0.9.14) cold session 모두 자체 추정 94 도달. 분석 결과 *조기 종료* + *generous self-rating* 두 noise 가 plateau 의 실 원인. 본 sprint-09 가 두 차원 동시 정정.

### 변경 — `conventions/budget-saturation-loop.md` 신규

페이즈 10 sprint loop 룰 정정:
- **임계 default = 0.999** (G3/G4 통일, G5 = 0.99999 유지)
- **Budget 사용률 ≥ 80% 강제** — 임계 first-try PASS 해도 sprint 추가
- 추가 sprint 의 lesson type = **content depth** (enforcement 아님) — Conceptual narrative / Results decision support / Sim cross-validation 의 *질적 layer*
- handoff frontmatter `budget_saturation: <ratio>` 명시 의무, 80% 미달 종료 = `EARLY_STOP_VIOLATION` self_lint fail
- 페이즈 04 신규 답안 `Q-D-BUDGET-MODE` (1=Saturation default / 2=Quick-stop / 3=Custom)

cold session retro 적용 시 v091_cold01 (28% 사용) / v0914_cold01 (21% 사용) 모두 +5-6 sprint 가능 → 추정 94 → 96-98.

### 변경 — `conventions/score-rubric-objectivity.md` 신규

페이즈 14 handoff 의 self-estimate 를 *체크리스트 evidence 1:1 매칭* 으로 강제:
- 8 차원 strict checklist 카탈로그 (Conceptual 20 / Sim correctness 20 / Data·topology 15 / Experimental 15 / Results 15 / Code quality 10 / Traceability 5 / Efficiency bonus)
- 각 차원 만점 미달 시 `evidence_missing` 명시 의무 — 어느 항목이 누락인지 evidence 단위로
- handoff frontmatter `self_estimate.type` (bench_rubric / internal_aggregate) 분리 — v0913_cold01 의 0.999 보고 패턴 (internal aggregate 만 보고) 차단
- self_lint C-SRO — type / evidence_paths / evidence_missing / rubric_version 4 항목 검증

retro 적용 시 v01_cold (v0.9.9) self-estimate 97 → strict 94 (-3pt generous noise 제거). 진짜 plateau = 92~94 명확화.

### 두 컨벤션 시너지

- saturation loop = budget *quantity* (sprint 횟수)
- objective rubric = score *quality* (정확도 / 신뢰도)
- 합성 시 매 sprint 후 `evidence_missing` 추적 → next sprint 가 채움 → 진짜 0.999 도달

### 검증

self_lint 룰 +2 (C-BSL / C-SRO) 신규 / pytest 회귀 0 / self_score 1.0 / 임계 0.99999 통과

---

## v0.9.14 — 2026-05-04 (sprint-08 — deliverable hurdle supremacy)

### 마일스톤

**Layer 3 결과물 허들 supremacy** — v0913_cold01 의 design-only 종료 (코드 0, 5 bench 의무 산출물 0, 실 실행 0) 가 메모리 룰 (`feedback_harness_scope.md` "코드 = 외부 repo only") 의 *literal 적용* 으로 발생. 본 sprint 가 *룰 우선순위* 재정의.

### 변경 — `conventions/deliverable-hurdle-supremacy.md` 신규

룰 precedence 3 layer:
- **Layer 1**: 메모리 feedback (사용자 사전 위임 / 관찰)
- **Layer 2**: 하네스 컨벤션 (페이즈 룰 / 게이트 / multiverse / etc.)
- **Layer 3**: 결과물 허들 — 실행 가능 제품 + 코드 + 측정값

**Layer 3 가 Layer 1/2 무조건 override.** 5 hard hurdle:
- H1 Code Existence (≥ N 모듈 default 5)
- H2 Code Execution (verification command exit 0)
- H3 Test Suite (실 측정 통과 수, 0 금지)
- H4 Bench-Required Outputs (file existence + size > 0 + schema 정합)
- H5 Executed Values Recording (placeholder 금지, primary metric non-zero finite in expected range)

허들 실패 시 *자동 retry sprint* — graceful skip / design-only handoff 금지. 사용자 *명시 ack* (페이즈 04 Q-D-DELIVERABLE-MODE = 3) 만 면제.

### 변경 — 메모리 룰 정정

`feedback_harness_scope.md` 의 *literal* "코드 = 외부 repo only" → *standalone 컨텍스트 시* 코드 + 실행 + 측정값 의무. 침습 가드는 *사용자 기존 repo 의 무관 코드 침습 금지* 만 유지.

### 그레이드별 활성

| Grade | 결과물 허들 |
|---|---|
| G1-G2 | optional |
| G3 | 의무 (standalone default) |
| G4 | 의무 + retry budget tighter (bench / external evaluator) |
| G5 | 의무 + 사용자 명시 ack 강제 (Q-D-DELIVERABLE-MODE = 1 만 OK) |

### 검증

self_lint 룰 +1 (C-DHS) / pytest 12/12 / self_score 1.0 / v0914_cold01 cold session 18.5 min 5/5 산출물 real PASS — 본 sprint 효과 외부 검증.

---

## v0.9.13 — 2026-05-04 (sprint-07 — content depth layer × 4)

### 마일스톤

94 plateau 1차 분석 — Conceptual / Sim correctness / Results 3 차원의 *content depth* 가 sub-score gap. enforcement 강화 (v0.9.6-12) 만으로는 깨지지 않음. 4 컨벤션이 *content layer* 추가.

### 변경 4건

- `conventions/deep-semantic-intent.md` — adjective + noun 결합으로 *implied framing* 추출 (의도 추출 깊이 +1 layer, ceiling-breaking 1순위 추정)
- `conventions/domain-research-stacking.md` + `conventions/domain-adapters/` 신규 — 마인드맵 noun → domain adapter 자동 stack (도메인 전문성 layer)
- `conventions/mindmap-quality-gardening.md` — Mermaid 의무 + 4 axis × ≥3 sub-node + ≥15 노드 (v091_cold01 ASCII 회귀 발견 정정)
- `conventions/ensemble-synthesis-default.md` — G4+ tournament 결과 *algorithmic union* default — 단일 우승 우주만 보지 않고 *교집합 + 합집합* 동시 활용

### 검증

self_lint 룰 +4 / pytest 회귀 0 / self_score 1.0. v0913_cold01 cold session 에서 design-only 회피 발견 → v0.9.14 deliverable-hurdle-supremacy 후속.

### 알려진 결손 (v0.9.14 해소)

본 sprint 만으로는 *코드 + 실행 + 측정값* 강제 부재 — agent 가 메모리 룰 literal 적용으로 design-only 종료 가능. v0.9.14 가 supremacy gate 추가.

---

## v0.9.12 — 2026-05-04 (sprint-06-c — analytical bound + multiverse impl fan-out)

### 마일스톤

v01_cold (v0.9.9) 회차의 *분석적 상한 vs 시뮬 baseline 자동 검증* 이 본 세션 v099 의 payload=50 잘못된 가정을 발견 — 메모리 `feedback_analytical_bound_validation.md` 정합. 본 sprint 가 발견을 컨벤션화.

### 변경 3건

- `conventions/analytical-bound-cross-validation.md` 신규 — closed-form 상한 vs simulated baseline 자동 검증, ratio [0.85, 1.00] 의무. 페이즈 09 derived gate 의무화.
- `conventions/multiverse-impl-fan-out.md` 신규 — universe N *모두* 실 코드 의무 (페이즈 06 plan 만 분기, 페이즈 08 가 단일 우주만 코드화 하던 문제 해소). tournament merge 코드 차원.
- `conventions/budget-aware-fallback.md` 신규 — silent fallback 금지, frontmatter `fallback_reason` 명시 의무.

### 검증

self_lint 룰 +3 / v091_cold01 cold session (90 min budget, 25 min 사용, 24/24 tests + 180/180 invariants) self 94 — analytical bound + ramp 비-병목 negative finding 도출.

---

## v0.9.11 — 2026-05-04 (sprint-06-b — interface-first parallel impl)

### 변경

- `conventions/interface-first-parallel-impl.md` 신규 — 페이즈 06 모듈 인터페이스 의무 + 페이즈 08 sub-agent 병렬 fan-out. universe N candidate 의 코드 작성이 *interface 의 다른 구현* 으로 격상 (v0.9.10 multi-phase 의 페이즈 08 axis 본격 발현).

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.10 — 2026-05-04 (sprint-06-a — AIDE multiverse 풀 발현)

### 마일스톤

본 하네스의 *유일한 차별 강점* (multiverse competition) 의 풀 발현 — *깊이 × 폭 × 검증* 3 차원 동시 강화. 페이즈 06 plan-tree 단독에서 5+ 페이즈로 multiverse 확장.

### 변경 3건

- `conventions/aide-tree-symmetry.md` 신규 — 각 universe candidate 의 sequenceDiagram ≥ 1 + actors ≥ 3 + interactions ≥ 5 + universe-specific differentiation 강제 (v01_cold audit 의 비대칭 경합 발견 정정).
- `conventions/aide-tree-multi-phase.md` 신규 — 페이즈 02 (doc-review multi-reviewer) / 05 (critique multi-critic) / 08 (impl multi-strategy) / 11 (regression multi-hypothesis) / 13 (viewer multi-framing) 까지 multiverse 확장. Q-D10~D14 페이즈 04 신규.
- `conventions/tournament-blind-rerun.md` 신규 — 임계 미달 시 anonymize previous winner 재경합. blind 검증으로 *우승 우주의 self-bias* 차단.

### 시너지

세 컨벤션 = "deep × broad × validated multiverse" — AIDE 의 풀 발현. README 본문에 *진짜 컨셉* 으로 부각.

### 검증

self_lint 룰 +3 / pytest 회귀 0 / self_score 1.0.

---

## v0.9.9 — 2026-05-04 (sprint-05-i — mindmap centrality)

### 변경

- `conventions/mindmap-centrality.md` 신규 — canonical concept graph 가 모든 페이즈 backbone. 페이즈 01 마인드맵이 단발 산출물에서 *전 페이즈 참조 grid* 로 격상.
- v01_cold (v0.9.9) 외부 cold session — synthetic_mine_throughput_v01_cold fresh (0 외부 ref) + 90 min budget, 25 min 사용. 24/24 tests + 180/180 invariants. 자체 94. crusher binding · ramp 비-병목 negative finding 도출. 자체 추정 inflation 노출 (97 generous → strict 94).

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.8 — 2026-05-04 (sprint-05-h — sprint regression loop + parallel cold review)

### 변경

- `conventions/sprint-regression-loop.md` 신규 — *self-polishing* 임계 도달까지 sprint 반복. budget 끝까지 사용 룰의 모태 (v0.9.15 budget-saturation-loop 가 정정).
- `conventions/parallel-cold-review.md` 신규 — N framing fan-out 으로 페이즈 03 다양성. single fresh agent 의 framing bias 차단.

### 검증

self_lint 룰 +2 / pytest 회귀 0.

---

## v0.9.7 — 2026-05-04 (sprint-05-g — premortem friction)

### 변경

- `conventions/premortem-friction.md` 신규 — 콜드리뷰의 *purpose* 가 *forward simulation* + derived_improvements 도출. 망설임 = 한 번 더 고민 + 미래 회고. 격언 동·서 1개 + 페이즈 02/03/07 적용.
- 메모리 `feedback_premortem_not_pause.md` 신규 — *멈춤 아님, 한 번 더 고민* 정의.

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.6 — 2026-05-04 (sprint-05-f — NFR derivation 자동 도출)

### 마일스톤

**케이스 종속 룰 금지 / 본 하네스 강화 = 구조 컨벤션** 메서돌로지 — 외부 답안 후 패치는 케이스 종속, 본 하네스 강화 = prompt → 게이트 흐름의 *구조* 변경. 메모리 `feedback_harness_strengthening_methodology.md` 정합.

### 변경

- `conventions/nfr-derivation.md` 신규 — prompt 형용사 (예: "robust", "scalable", "low-latency") 로부터 NFR + derived 게이트 자동 도출. 페이즈 01 의도 추출 + 페이즈 04 Q-D + 페이즈 09 게이트 6 의 일관 흐름.

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.5 — 2026-05-04 (sprint-05-e — 회귀 원인 분류 + plan implementation guidance)

### 마일스톤

사용자 4 질문 비판적 검토 후 *진짜 가치* 2건만 채택 (Q4 페이즈 02/03/09 경쟁 추가는 over-engineering 으로 거부).

### 변경 — Q1. 페이즈 11 회귀 원인 4 분류

`phases/11-regression-bisect.md` 새 절 — git bisect 결과를 4 분류 (plan defect / impl defect / data defect / external defect) 자동 판별 + 권고 페이즈 자동 진입 :

| 분류 | 권고 페이즈 |
|----|----|
| plan defect | 페이즈 06 재실행 (re-plan, universe 재분기 가능) |
| impl defect | 페이즈 08-γ 재실행 (re-impl, plan 유지) |
| data defect | 페이즈 04 Q-D8 재검증 (re-data) |
| external defect | 페이즈 09 게이트 7 재실행 (re-env) |

분류 알고리즘 — git bisect commit 의 변경 파일 + plan TODO DAG ↔ impl-log TODO 매핑 비교.

### 변경 — Q3. plan 본문 implementation guidance 의무 (HARD-RULE 9.a 강화)

`phases/06-plan.md` 새 절 — plan 본문 의무에 추가 :
- **데이터 구조** ≥ 2 (entity/state object dataclass + schema)
- **의사코드** ≥ 1 (핵심 알고리즘)
- **클래스 시그니처** ≥ 3 (`__init__` + 핵심 메서드)

신규 산출물 (impl-design.md) 만들지 않고 plan 본문 흡수 = 메모리 보수화 정합 + plan/impl-log 응집.

페이즈 11 회귀 분류와 *대응* — plan 의 데이터 구조/의사코드/클래스 시그니처 명시가 회귀 시 plan defect vs impl defect 자동 판별 입력.

### 변경 — self_lint 신규 룰 2

- **C-RB1** : 페이즈 11 본문 키워드 (plan defect / impl defect / data defect / external defect / 회귀 원인 분류) 검증
- **C-IG1** : 페이즈 06 본문 키워드 (implementation guidance / 데이터 구조 / 의사코드 / 클래스 시그니처) 검증

### 거부 (over-engineering 의심)

사용자 Q4 = 페이즈 02 의도 리뷰 / 03 콜드 재이해 / 09 게이트 에 경쟁 추가 → **거부** :
- 페이즈 03 = 단일 fresh agent 가 이미 격리 reviewer 역할 (사실상 페이즈 01 vs 03 경쟁)
- 페이즈 09 7 게이트 = 단일 evaluator 가 이미 multi-dim (7 차원) 평가
- 추가 sub-agent 비용 > 본질 가치 → over-engineering

### 검증

self_lint 60 → **62 룰** PASS / pytest 12/12 회귀 0 / self_score 1.0 / 임계 0.99999 통과

### sprint-05 묶음 종합 (v0.9.1 ~ v0.9.5)

| sprint | 변경 |
|----|----|
| 05-a (v0.9.1) | simulation-bench 베이스라인 + viewer split + TDD 5 서브페이즈 + ruff |
| 05-b (v0.9.2) | multiverse 폭 확장 + 자동 머지 알고리즘 + budget profile |
| 05-c (v0.9.3) | 재측정 + 3 universe head-to-head + interactive-viewer 첫 시연 |
| 05-d (v0.9.4) | 페이즈 13 책임 정정 (결과 프로덕트 only) |
| **05-e (v0.9.5)** | **회귀 원인 분류 + plan implementation guidance** |

self_lint 47 → **62 룰** (sprint-05 묶음으로 +15). 본 하네스 architectural 깊이 강화.

---

## v0.9.4 — 2026-05-04 (sprint-05-d — 페이즈 13 책임 정정)

### 마일스톤

v0.9.3 sprint-05-c 첫 시연 시 페이즈 13 interactive-viewer 가 *하네스 메타* (universe_comparison.png 등) 를 emit — 사용자 비판 정확 : "인터렉티브 뷰어가 우리 하네스 위주의 플랜이나 내부 과정에 종속된 결과물이 되어버렸다. 인터렉티브 뷰어는 결과 프로덕트의 데이터나 시뮬레이션 뷰어로서 동작하도록 설계되야 하는 스킬이다." sprint-05-d 가 본 룰 self_lint 로 강제.

### 변경

- `phases/13-interactive-viewer.md` 새 절 — 결과 프로덕트 only + topology + animation + drill-down + 하네스 메타 emit 금지 명시 + DES 도메인 결과 프로덕트 4 카탈로그 (topology/animation/drill-down/metric chart) + 분리 검증 어휘 black list (universe-N, multiverse, plan-tree, sprint metric 등)
- `agents/interactive-viewer-builder.md` 책임 좁힘 — 프로젝트 결과 only + 하네스 메타 emit 금지 + 도메인별 의무 emit 카탈로그
- `scoring/self_lint.py` 신규 룰 2 :
  - **C-IV1** : 페이즈 13 본문 키워드 (결과 프로덕트 / topology / animation / drill-down / 하네스 메타 emit 금지) 검증
  - **C-IV2** : interactive-viewer-builder agent 의 책임 좁힘 (프로젝트 결과 only / 하네스 메타 emit 금지 / topology / animation) 검증
- 메모리 `feedback_phase12_real_definition.md` 정정 — 페이즈 12 책임 강화 (하네스 메타 + multiverse 비교 차트), 페이즈 13 = 결과 프로덕트 only

### 검증

self_lint 58 → **60 룰** PASS / pytest 12/12 회귀 0 / self_score 1.0 / 임계 0.99999 통과

### 회귀 방지

본 sprint 가 self_lint C-IV1/C-IV2 룰로 강제 — 다음 회차 페이즈 13 진행 시 하네스 메타 emit 시도 → self_lint fail → 본 페이즈 재실행 강제.

### 후속 — interactive-viewer 결과 재 emit (별도)

simulation-bench 기존 interactive-viewer (sprint-05-c) 디렉터리 (`.ShipofTheseus/synthetic_mine_throughput_002/interactive-viewer/`) 의 universe_comparison.png 제거 + topology + animation + scenario drill-down 신규 emit 은 별도 작업 (gitignored 라 본 commit 영향 0). sprint-05-e 후보.

---

## v0.9.3 — 2026-05-04 (sprint-05-c — 재측정 + multi-universe 첫 실 시연)

### 마일스톤

sprint-05-b 의 architectural 변화 (폭 3 + universe 별 head-to-head + 자동 머지 + interactive-viewer) 실 시연. simulation-bench 재측정 결과 + 3 universe 비교 검증.

### 측정 결과 (`.ShipofTheseus/synthetic_mine_throughput_002/` — gitignored, 본 commit 미포함)

- 경과 : **44.4 분** (60 min budget 안전, sprint-05-a 43.1 min 동급)
- 15 페이즈 (00~14) 모두 진행 / 인터럽트 0 / autonomous
- **3 universe head-to-head 실 측정** :
  - U1 (process-first / per-direction) : 1555.8 t/h / D_CRUSH 병목 (per-direction 가짜 cap 인플레 노출)
  - U2 (hybrid centralized / shared bidirectional) : 1150.0 t/h / 로더 saturation
  - U3 (data-first event scheduler) : **1150.0 t/h / E03 ramp 정확 식별 + byte-reproducibility SHA256 매치**
- **자동 머지 알고리즘 결정 → U3 단독 채택** (차원별 sub-score gap 4pt vs U2)
- **interactive-viewer 페이즈 13 첫 실 시연** : matplotlib 3 plot (scenario throughput / bottleneck heatmap / universe comparison) + dashboard.json + index.html (CDN 0)

### 핵심 발견 (sprint-05-b 효과 검증)

a- **자동 머지 알고리즘 정상 작동** — 사람 critic 의 결정과 같은 답에 도달 (U3 단독 채택)
b- **per-direction vs bidirectional 차이 측정** — sprint-05-a 의 per-direction 머지가 ~35% throughput 인플레 (가짜 cap-1) 였음을 head-to-head 가 노출
c- **byte-reproducibility** = G5 미션 크리티컬 차원 신규 NFR. U3 가 도달
d- **페이즈 13 interactive-viewer 동작 검증** = matplotlib 0.43s 에 3 plot

### 자체 추정 점수

| 차원 (max) | sprint-05-a 단일 머지 | sprint-05-c U3 단독 |
|----|:-:|:-:|
| Conceptual 20 | 19 | 18 (narrative 보강 sprint 실패) |
| Sim correctness 20 | 16 | **18** (병목 정확 식별 +2) |
| Code quality 10 | 8 | **9** (45 tests + 0 ruff) |
| (기타 동일) | | |
| **합계** | **92** | **92~93** |

narrative 보강 후 추정 95~97 (1위 ouroboros 동급/상위 가능).

### sub-agent 회계

8 sub-agent 호출 — 1 실패 (페이즈 10 sprint narrative). intervention.category = autonomous 유지.

### 본 commit 의 변경 (본 하네스 source)

- `.claude-plugin/plugin.json` : version 0.9.2 → 0.9.3
- `skills/theseus-{harness,orchestrator}/SKILL.md` : frontmatter version
- `CHANGELOG.md` : 본 절 추가

본 sprint-05-c 는 *측정 + 검증* 이라 본 하네스 source 변경 0. 측정 결과 (`.ShipofTheseus/synthetic_mine_throughput_002/`) 는 .gitignore 됨.

### 다음 후보

- sprint-05-d : narrative 보강 (Conceptual 18→20 + Results 13→15 = +4pt → 추정 95~97)
- 외부 PR : simulation-bench 외부 채점으로 자체 추정 검증 (1위 ouroboros 97 head-to-head)

---

## v0.9.2 — 2026-05-04 (sprint-05-b)

### 마일스톤

본 하네스 강점 (다차원 동시진행 = plan-tree N universe + 경쟁 + 머지) 의 *폭 확장 + 자동 머지 강화*. 사용자 명시 — "다차원 동시진행이 강점이니 플랜/구현을 더 넓게 진행해서 트리를 더 가지많게".

### 변경 — MV-1. 멀티버스 폭 default 확장

- `conventions/grades.md` 새 절 — G3 폭 2→**3** / G4 폭 3→**4** / G5 폭 5→**6**
- self_lint C-MV1 룰 신규

### 변경 — MV-2. 페이즈 08 universe 별 head-to-head

- `phases/08-implement.md` 새 절 — universe 별 5 서브페이즈 (08-α/β/γ/δ/ε) 독립 사이클
- 각 universe 별 격리 코드 (`code/universe-N/`) + 격리 impl-log
- head-to-head 점수 비교 + 차원별 머지
- self_lint C-MV2 룰 신규

### 변경 — MV-3. 분기 축 카탈로그 ≥6

- `conventions/plan-tree.md` 새 절 — 6 axis 카탈로그 (process-vs-data / sync-vs-async / centralized-vs-distributed / dynamic-vs-static / push-vs-pull / mutable-vs-immutable) + 확장 후보 5
- planner 가 폭 N 진행 시 상위 N 개 axis 선택 → 본질적 의미 분기 강제
- self_lint C-MV3 룰 신규

### 변경 — MV-4. 자동 머지 알고리즘 강화

- `conventions/competition.md` 새 절 — head-to-head 점수 비교 + 차원별 sub-score (Conceptual/Data/Correctness/Experimental/Results/Code/Traceability)
- 자동 resolve 4 규칙 (단일 우승자 / 차원별 머지 / 재경쟁 / 타임아웃)
- self_lint C-MV4 룰 신규

### 변경 — MV-5. universe N 병렬 budget profile

- `conventions/resources.md` 새 절 — universe N 병렬 메모리 가드 (G3 40% / G4 50% / G5 60% RAM) + per-universe wall-clock budget + 초과 시 자율 폭 축소
- self_lint C-MV5 룰 신규

### 검증

- self_lint 53 → **58 룰** PASS / pytest 12/12 회귀 0 / self_score 1.0 / 임계 0.99999 통과

### 효과 추정 (simulation-bench 재측정 시)

- sprint-05-a 후 추정 92~95
- sprint-05-b (본 sprint) 후 추정 **96~98** — 1위 ouroboros (97) 동급 또는 상위
- 핵심 = G3 폭 3 적용 + 페이즈 08 universe 별 head-to-head 가 *실 코드 head-to-head* 비교 → 차원별 머지로 단일 universe 보다 강함

---

## v0.9.1 — 2026-05-04 (sprint-05-a)

### 마일스톤 묶음

a- **simulation-bench 첫 베이스라인 측정** (harrymunro/simulation-bench `001_synthetic_mine_throughput`)
  - G3 / 43.1 분 wall clock / intervention 0 / sanity 4 모두 PASS
  - 자체 추정 점수 92/100 (1위 ouroboros 97 대비 gap 5pt)
  - 산출물 : `.ShipofTheseus/synthetic_mine_throughput_001/` (페이즈 산출물 30+ + code/ 1975 LOC + 5 벤치 산출물)
b- **약점 분석** : gap 5pt 의 차원별 attribution + 본 하네스 책임 약 3pt 식별 (Sim correctness 4pt + Code quality 2pt + Results 1pt 부족)
c- **본 하네스 architectural 개선 3건** :

### 변경 — A. ruff 통합 (코드 lint/format 표준)

- `conventions/build-and-config.md` 새 절 8 — ruff check / ruff format 통합 + 페이즈 09 게이트 3 (SOLID DIP) 부속
- `scoring/self_lint.py` C-LINT1 룰 신규 — build-and-config 의 ruff 통합 본문 검증
- 거울 원칙 정합 — 외부 표준 도구 호출 (코드 micro 품질 룰 자체 정의 회피)

### 변경 — C. 페이즈 12/13/14 분리 (viewer 책임 분할)

- **14 → 15 페이즈** 확장
- `phases/12-webview-assembly.md` — **theseus-view** (스킬 진행 추적) 책임으로 좁힘
- `phases/13-interactive-viewer.md` **신규** — 프로젝트 output observability + 도메인별 dashboard
- `phases/13-handoff.md` → `phases/14-handoff.md` 이동 + 페이즈 번호 update
- `agents/interactive-viewer-builder.md` **신규** — 페이즈 13 책임
- `agents/webview-builder.md` 책임 좁힘 (theseus-view only)
- `conventions/spec-catalog.md` 도메인 dashboard 카탈로그 절 추가 (DES / 데이터 ETL / ML / 분석 / REST API / Frontend)
- `scoring/self_lint.py` C-WV1 / C-WV2 / C-WV3 / C-AGENT-IVB 룰 신규
- 메모리 `feedback_phase12_real_definition.md` 신규 — viewer 분리 의도 기록 (사용자 통찰)

### 변경 — TDD. 페이즈 08 5 서브페이즈 분해

- `phases/08-implement.md` — 5 서브페이즈 표 추가 :
  - **08-α scope** : test-architect (atomic / group / functional 3 계층 scope 정의)
  - **08-β test (RED)** : test-writer (테스트만 작성, 구현 0, RED 확인)
  - **08-γ impl (GREEN)** : implementer (테스트 통과 최소 구현)
  - **08-δ refactor (REFACTOR)** : refactorer (DRY/SOLID/docstring/type hint, GREEN 유지)
  - **08-ε log** : implementer (impl-log.md)
- `agents/test-architect.md` / `agents/test-writer.md` / `agents/refactorer.md` **신규**
- `agents/implementer.md` 책임 좁힘 (08-γ + 08-ε only)
- `conventions/test-invariants.md` — RED-GREEN-REFACTOR 루프 + universe 변경 트리거 절 추가
- `scoring/self_lint.py` C-TDD-08 룰 신규

### 변경 — infra

- `skills/theseus-harness/SKILL.md` — 15 페이즈 표 + 산출물 트리 (interactive-viewer/ + handoff/14-handoff.md)
- `skills/theseus-orchestrator/SKILL.md` — 15 페이즈 표 + HARD-RULE 8 grade 산출물 매트릭스 (handoff/14-handoff.md) + grade 처리 절 (G3 13 페이즈 / G4-5 15 페이즈)
- `scoring/self_lint.py` 47 룰 → 53 룰 (신규 6)

### 검증

- self_lint 53/53 PASS
- pytest 12/12 PASS (회귀 0)
- self_score = 1.0 / 임계 0.99999 통과

### Description (자체 개선 3건의 의미)

본 sprint = simulation-bench 첫 외부 적용으로 노출된 본 하네스의 약점 (코드 micro 품질 게이트 부재 / viewer 정의 narrow / TDD test-first 미적용) 을 *그 약점이 타당함을 검증한 후* 최소 변경으로 개선. 거울 원칙 정합 — 외부 1 케이스 위해 본체 합성 0, *원래 박혀 있어야 했던 정의* 노출.

---

## v0.9.0 — sprint-04-b

- sandbox livetest validated milestone

## v0.8.x — sprint-04-a, sprint-03-*

- 책임 범위 명시 + HARD-RULE 9 (설계 품질 의무) — sprint-04-a
- 페이즈 04 외 인터럽트 0 — 사람 ack 모두 자율 (sprint-03-f)
- 외부 정합 검증 (livetest G2/G3/G4/G5 모두 PASS) — sprint-03

## v0.7.x — sprint-02-e

- 9 항목 출하 (정직박스 ⓓ + 코드-실행가능 게이트 7 등)

## v0.6.0 — sprint-02

- AIDE plan-tree + competition + 멀티버스
