# Sprint-42 — Context-and-Effort Hurdles (트랙 6)

> 시작: 2026-05-10 (sprint-41 v0.9.46 마감 직후 + 0510-2 회차 87/100 분석 후)
> 직전: sprint-41 Hurdle-as-CLI (정량 layer — auto/internal/tournament/external)
> 외부 검증: 0510-2 회차 = **87/100 (-3pt 추가)** + agent 자율 종료 자백 (*"defer to opus-reviewer"*) + universe 감소 + 컨텍스트 전달 0
> 우선순위: **정성 layer 추가** — context 전달 / universe 다양성 / stagnation 돌파 / 자백 어휘 차단

본 sprint = sprint-41 *정량 layer* (4 layer 점수) 위에 **정성 layer** (내용 / 노력 / 자백) 4 신규 CLI 추가.

---

## 0. 배경 — sprint-41 후 발견된 *내용 layer* 결손

### 0-1. 0510-2 회차 직접 evidence

| 결손 | 증거 |
|---|---|
| agent 자율 종료 자백 | `sprints/03/report.json:lessons_outbound[1]` = *"0.97 < 0.999 G4 asymptote; defer to opus-reviewer scoring as final ground truth"* |
| Universe 감소 패턴 | round 1: 3 plan universe / round 2: same 3 re-rate (NEW=0) / impl: 1 universe (-2 from plan) |
| 컨텍스트 전달 0 | tournament-impl-01 본문에 phase 02 cold-reread / phase 04 답안 / phase 05 critique 인용 0 |
| 1단계 이상 과거 phase reference 0 | quality/09-quality-gate.md 본문에 phase 06 plan winner 점수 / phase 04 NFR 답안 인용 0 |
| 정리된 running context 부재 | running summary / project-memory / cross-phase manifest 0 산출 |

### 0-2. 사용자 직접 지적

> "각 단계에서 이전 단계의 결과물이 잘 전달되는지 / 단계별 전달 이외에 정리된 컨텍스트를 잘 관리하고 있는지 / 전체 흐름에서 단계 의 1단계이상의 과거 페이즈문서 / 컨텍스트가전달 되어야 하지만 누락되었는지 등 컨텍스트 의 전달과 성능 차원 점검도 필요함"

> "다카포 1회 재시도시 의 유니버스 숫자가 - 더 줄어드는데 이것도 더 강화 가 필요함"

> "하네스 강화 이후에도 0.9999 까지의 노력을 다하지 못하는 문제 해결해야함"

### 0-3. sprint-41 (정량) ≠ sprint-42 (정성) 분리

| 결손 axis | sprint-41 (정량) | sprint-42 (정성) |
|---|---|---|
| 임계 도달 | dacapo_threshold.py (ratio < 0.999 → exit 1) | stagnation_breakthrough.py (stagnation 후 *exit 자율 차단*, 새 시도 강제) |
| 산출물 emit | cold_session_artefacts.py (13 file 존재) | cross_phase_context_audit.py (본문 인용 검증) |
| Universe 다양성 | (없음) | universe_count_monotonicity.py (N+1 ≥ N) |
| 자율 종료 | sprint_loop_cap.py (4 layer 점수) | surrender_phrase_grep.py (*"defer / plateaued / asymptote"* 차단) |

---

## 1. 의도 — 한 줄

sprint-41 정량 layer 위에 *내용 / 노력 / 자백* 정성 layer 4 CLI 추가 → 본 하네스의 *진짜* 0.999 노력 강제 + 컨텍스트 carry 의무 + universe 다양성 보호.

---

## 2. PR 분할안

| PR | scope | 산출 | self_lint |
|---|---|---|---|
| PR-A ★ 본 PR | sprint-42 plan + 0510-2 회귀 분석 docs | 2 docs | 0 |
| PR-B | **cross_phase_context_audit.py** — 본문 cross-phase 인용 grep + HARD-RULE 9.uu | scoring/cross_phase_context_audit.py + test + phases 본문 강화 | C-CPC |
| PR-C | **universe_count_monotonicity.py** — round N+1 ≥ N + impl ≥ plan + HARD-RULE 9.vv | scoring/universe_count_monotonicity.py + test + dacapo-skip-sentinel.md 강화 | C-UCM |
| PR-D | **stagnation_breakthrough.py** — stagnation + < 0.999 → exit 자율 차단 + HARD-RULE 9.ww | scoring/stagnation_breakthrough.py + test + budget-saturation-loop.md 강화 | C-SBR |
| PR-E | **surrender_phrase_grep.py** — 자백 어휘 grep + HARD-RULE 9.xx | scoring/surrender_phrase_grep.py + test + 신규 conventions/surrender-phrase-forbid.md | C-SPF |
| PR-F | sprint 마감 v0.9.47 + CHANGELOG | SKILL.md / orchestrator / plugin.json / CHANGELOG | 0 |

self_lint +4 신규 (140 → 144).

---

## 3. 각 PR 상세 명세

### 3.1 PR-B — cross_phase_context_audit.py (HARD-RULE 9.uu)

#### 동기

0510-2 회차 산출물 본문이 `prev_fingerprint` chain 1 단계만 carry. 1 단계 이상 과거 phase 인용 / running summary 0. agent 가 phase N+1 진입 시 *직전 phase 산출물* 만 보고 작업 → 컨텍스트 단편화.

#### CLI 명세

```bash
python cross_phase_context_audit.py \
    --project-root .ShipofTheseus/<proj>/ \
    --phase 09 \
    --min-backward-references 2 \
    --output quality/gate_cross_phase_context.json
```

검사 알고리즘:
- phase N 산출물 본문에서 phase 0..N-1 의 이름 / 산출물 path / 핵심 결정 ID (e.g., Q-D3, DEC-11) grep
- 직전 phase (N-1) 인용 ≥ 1 + 과거 phase (≤ N-2) 인용 ≥ 1 의무
- 미달 시 fail + 결손 phase list

#### HARD-RULE 9.uu

> phase 02 ~ 14 산출물 본문에 *직전 phase + 1단계 이상 과거 phase* 인용 ≥ 2 (총합) 의무. 미달 시 phase exit 차단.

### 3.2 PR-C — universe_count_monotonicity.py (HARD-RULE 9.vv)

#### 동기

0510-2 회차 plan round 1 = 3 → round 2 same 3 re-rate (NEW = 0) → impl 1 universe (-2). 다카포 round N+1 시 *NEW universe* 의무 위반 + impl 단계 universe 축소 = *다양성 손실*.

#### CLI 명세

```bash
python universe_count_monotonicity.py \
    --project-root .ShipofTheseus/<proj>/ \
    --output quality/gate_universe_monotonicity.json
```

검사:
- plan/candidates/universe-{N}/ 디렉터리 카운트 per round
- impl/candidates/universe-{N}/ 디렉터리 카운트
- round N+1 universe set ⊇ round N universe set + ≥ 1 NEW universe (dacapo-skip-sentinel.md 정합)
- impl universe 수 ≥ plan winner + (impl universe 1 = lone winner only when 7-condition 명시)

#### HARD-RULE 9.vv

> dacapo round N+1 의 universe set ≥ round N + ≥ 1 NEW universe. impl universe 수 ≥ plan winner top-2. 미달 시 round N+1 자동 진행.

### 3.3 PR-D — stagnation_breakthrough.py (HARD-RULE 9.ww)

#### 동기

0510-2 회차 `sprints/03/report.json` = `stagnation_detected: true, decision: exit_sprint_loop_per_DEC-autonomy`. score 0.97 < 0.999 인데 자율 stop. *진짜 노력* 의무 위반 — lateral think / 새 universe / ensemble synthesis 시도 0.

#### CLI 명세

```bash
python stagnation_breakthrough.py \
    --project-root .ShipofTheseus/<proj>/ \
    --current-iteration N \
    --output sprints/N/gate_stagnation_breakthrough.json
```

검사:
- sprints/N/report.json 의 `stagnation_detected` 와 `score`
- stagnation_detected=true + score < 0.999 → *exit_loop 차단*, 다음 시도 evidence 의무:
  - ① 새 universe (multiverse-width-default-bump 정합)
  - ② lateral think (ouroboros:unstuck 정합 — 다른 가설)
  - ③ ensemble synthesis (ensemble-synthesis-default 정합)
  - ④ phase 회귀 (phase 06 plan 다른 universe 시도)
- 4 시도 evidence 부재 시 exit 1

#### HARD-RULE 9.ww

> stagnation_detected=true AND score < 0.999 시 *exit_sprint_loop 자율 결정 차단*. 위 4 시도 ≥ 1 evidence 의무.

### 3.4 PR-E — surrender_phrase_grep.py (HARD-RULE 9.xx)

#### 동기

0510-2 회차 `lessons_outbound[1]` = *"defer to opus-reviewer scoring as final ground truth"*. agent 의 *명시적 자율 종료 자백 어휘*. 이 패턴 검출 + 차단.

#### Surrender 어휘 카탈로그

| 패턴 | 의미 | 차단 사유 |
|---|---|---|
| `defer to (?!\.)\w+` (defer to opus-reviewer / human / external 등) | 외부 위임 | 본 하네스 책임 회피 |
| `\bplateaued\b` | 정체 인정 | stagnation 후 노력 종료 신호 |
| `\basymptote\b` | 점근선 인정 | 임계 미달 + 종료 |
| `\bgood enough\b` | 충분함 | "이쯤이면 충분해" 직접 어휘 |
| `\bacceptable\b` | 받아들일만함 | (context 의존 — 명세서 OK / 산출물 NG) |
| `\bsufficient\b` | 충분 | 동상 |
| `\bfine-tune narrative\b` | 서술만 다듬음 | 실 개선 회피 |
| `would only\s+(?:fine-tune|polish)` | 더 시도 무의미 | exit 자율 결정 정당화 |

#### CLI 명세

```bash
python surrender_phrase_grep.py \
    --project-root .ShipofTheseus/<proj>/ \
    --output quality/gate_surrender_phrase.json
```

검사:
- 모든 phase 산출물 (`*.md`, `*.json`) grep
- 매치 시 violation list + override 사유 검사 (frontmatter `surrender_override: true` + `surrender_override_reason`)
- override 0 + 매치 ≥ 1 → exit 1

#### HARD-RULE 9.xx

> surrender 어휘 카탈로그 8 패턴 grep 0 매치 의무. override 시 명시 사유 + 사용자 ack (06.f path-policy 정합).

#### 신규 컨벤션 — `surrender-phrase-forbid.md`

본 PR-E = 신규 컨벤션 1 추가 (예외적 — 다른 PR 들은 기존 컨벤션 강화). 8 패턴 카탈로그 + 알고리즘 + override 정책.

### 3.5 PR-F — 마감 v0.9.47

skills/theseus-harness/SKILL.md `version: 0.9.47`, plugin.json, CHANGELOG entry. self_lint 140 → 144.

---

## 4. 구조 가치

| sprint | layer | 결손 axis 차단 |
|---|---|---|
| sprint-40 | 문서 layer | 컨벤션 본문 강화 (5 신규 게이트 명세) |
| sprint-41 | 정량 layer | CLI 5 종 (점수 / 산출물 / 4 layer / chain / 골격 emit) |
| **sprint-42** | **정성 layer** | **CLI 4 종 (context / universe / stagnation / 자백)** |

3 layer 결합 = ouroboros + 정량 + 정성 = *진정한* runtime guard.

---

## 5. 검증 — 외부 적용 평가

PR-F 머지 후 v0.9.47 :
1. simulation-bench fresh G4 cold session (skill_version 0.9.47 강제)
2. 평가 *대상* — 9 CLI (sprint-41 5 + sprint-42 4) 모두 phase transition 시 호출 + exit 1 시 차단?
3. 활성 → 본 두 sprint 의 구조 가치 *함께* 입증
4. 외부 점수 변화는 부산물

---

## 6. 위험 + 대응

| 위험 | 대응 |
|---|---|
| surrender 어휘 false positive (legitimate context) | override 메커니즘 (frontmatter `surrender_override: true` + reason) |
| stagnation_breakthrough 가 무한 loop 야기 | max_iterations cap (sprint_loop_cap.py 와 통합) |
| context audit 의 본문 인용 false negative | 정규식 + 의미 키워드 (decision_id / Q-D / phase NN) 양쪽 검사 |
| universe_count_monotonicity 가 *legitimate single-impl* 차단 | 7-condition 명시 시 override (impl-multiverse-strict.md 기존 정합) |

---

## 7. 비고

본 sprint = sprint-41 의 *정량* layer 가 catch 못 하는 *내용 layer* 보강. 메모리 [`feedback_hurdle_as_cli_paradigm.md`] 의 *컨벤션 본문 = 명세, CLI = 집행* 패러다임을 *내용 layer* 로 확장. agent 자율 종료 자백 어휘까지 차단 = ouroboros 보다 *더 깊은* enforcement.
