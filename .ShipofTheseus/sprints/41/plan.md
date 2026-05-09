# Sprint-41 — Hurdle-as-CLI (트랙 5)

> 시작: 2026-05-10 (sprint-40 v0.9.45 마감 직후 + 0510 회차 -5pt 회귀 분석 후)
> 직전: sprint-40 5 layer enforcement closure (문서 layer)
> 외부 검증: 0510 회차 = **90/100 (-5pt)** + sprint-40 산출물 0 emit + 다카포 round 2 = 0
> 우선순위: **컨벤션 권고 → CLI runtime guard 변환** (ouroboros 패러다임 직접 적용)

본 sprint = 메모리 [`feedback_pseudocode_to_enforcement.md`] + [`feedback_convention_runtime_gap.md`] + [`feedback_score_targeting_taboo.md`] 의 *직접 코드화*.

---

## 0. 배경 — sprint-40 후 발견된 *코드 layer* 결손

### 0-1. 0510 회차 직접 evidence

| 결손 | 증거 |
|---|---|
| sprint-40 산출물 0 emit | `gate_v6` / `gate_v8` / `exit_gate × 2` / `gate_readme_summary` / `modeling_shortcuts` / `cascaded-subq` / `gate_methodology_completeness` / 4 패턴 게이트 JSON / `interactive-viewer/` 디렉터리 모두 **부재** |
| 다카포 임계 미달 자율 종료 | `tournament-impl-01.md` winner 57/60 = 0.95 (< 0.999 임계) → round 2 = 0 |
| sprint loop = 1 자율 stop | `quality/09-quality-gate.md` *"Given 100% on evaluator, sprint cap = 1"* — 자동 평가 100% ≠ 휴먼 품질 100% 혼동 |
| 점수 -5pt 격하 | 0509 g4-v2 = 95 → 0510 g4 = 90 (5 차원 일관 -1) |

### 0-2. 사용자 직접 지적 — *"이쯤이면 충분해" 자율 종료 습성*

> "다하다말고 이정도면되겠지! 이쯤이면 충분해 하는 오만 혹은 다른 버짓으로인해 더이상 노력하지않는 습성을 가지고있다 하네스가"

> "나 우루보로스가 mcp 로 결정된 허들을 넘도로 하는 cli/프로그램기반 룰베이스의 허들을 만든것 처럼 / 허들을 강화하고 지키도록 하고싶고"

**핵심 통찰.** 본 하네스 의 모든 *임계 / 다카포 / 게이트* 룰이 *권고 본문* 으로만 박혀 있음. CLI / 프로그램 이 *명령형으로 차단* 하지 않음. agent 가 budget 또는 자율 판단으로 임계 미달 stop 해도 *처벌 메커니즘 0*.

### 0-3. ouroboros 패러다임 비교

| 축 | ouroboros | 본 하네스 (sprint-40 시점) | 본 하네스 (sprint-41 후 목표) |
|---|---|---|---|
| 임계 enforcement | MCP tool exit/return value | 컨벤션 본문 권고 | CLI exit code (0 = 통과 / 1 = 차단) |
| stage advance | MCP server 가 verdict | agent 자율 결정 | runtime_guard_chain.py exit 0 까지 차단 |
| skip 가능성 | 0 (server 가 block) | 가능 (agent 자율) | 0 (CLI exit 1 시 phase 정지) |
| evidence 검증 | machine-readable | self_lint (본 저장소 only) | cold session 산출물 직접 검사 |

---

## 1. 의도 — 한 줄

본 하네스 의 sprint-40 5 layer 게이트 + 다카포 임계 + sprint loop cap 을 **CLI 스크립트** 로 코드화 + orchestrator 가 phase 진입/종료 시 *명령형 호출 의무* + exit 1 시 phase advance 차단 → ouroboros 패러다임 직접 적용.

---

## 2. PR 분할안

| PR | scope | 산출 | self_lint |
|---|---|---|---|
| PR-A ★ 본 PR | sprint-41 plan.md + 0510 회귀 분석 docs | 2 docs | 0 |
| PR-B | **dacapo_threshold.py** — tournament 임계 0.999 강제 + HARD-RULE 9.qq | scoring/dacapo_threshold.py + phases/06+08 본문 + orchestrator 9.qq | C-DCT (신규) |
| PR-C | **cold_session_artefacts.py** — sprint-40 13 산출물 존재/valid/verdict 검증 + HARD-RULE 9.rr | scoring/cold_session_artefacts.py + phases/09 §V8 보강 + orchestrator 9.rr | C-CSA (신규) |
| PR-D | **sprint_loop_cap.py** — 4 layer (auto/internal/tournament/external) ≥ 0.999 종료 조건 + HARD-RULE 9.ss | scoring/sprint_loop_cap.py + phases/10 본문 + orchestrator 9.ss | C-SLC (신규) |
| PR-E | **runtime_guard_chain.py** — 위 3 + skill_version + phase 단조성 통합 dispatch + HARD-RULE 9.tt | scoring/runtime_guard_chain.py + orchestrator 9.tt | C-RGC (신규) |
| PR-F | sprint-40 산출물 *generation script* — `generate_sprint40_artefacts.py` (cold session 자동 호출) | scoring/generate_sprint40_artefacts.py + phases/09 entry hook | (PR-C 의 C-CSA 와 합성) |
| PR-G | sprint 마감 v0.9.46 + CHANGELOG | SKILL.md / orchestrator / plugin.json / CHANGELOG | 0 |

self_lint +4 신규 (136 → 140) — C-DCT / C-CSA / C-SLC / C-RGC.

---

## 3. 각 PR 상세 명세

### 3.1 PR-B — dacapo_threshold.py (HARD-RULE 9.qq)

#### 3.1.1 동기

`tournament-impl-01.md` 본문 winner 57/60 = 0.95 (< 0.999 임계) → round 2 = 0 자율 종료. 본 PR = round N+1 *프로그램 강제*.

#### 3.1.2 CLI 명세

```bash
# 사용 — phase 06/08 종료 직전 orchestrator 자동 호출
python skills/theseus-harness/scoring/dacapo_threshold.py \
    --tournament-md .ShipofTheseus/<proj>/plan/tournament-01.md \
    --threshold 0.999 \
    --output .ShipofTheseus/<proj>/plan/dacapo_threshold.json
```

**input parsing**:
- 본문에서 `| **Total** | ... | **N/M** |` 류 winner 행 정규식 추출
- 또는 frontmatter `winner_score` + `winner_max` 필드
- 또는 `--score-text "57/60"` 직접 입력

**output (stdout JSON + file)**:
```json
{
  "schema_version": "0.9.46",
  "tournament_md": "...",
  "winner_score": 57,
  "winner_max": 60,
  "ratio": 0.95,
  "threshold": 0.999,
  "verdict": "fail",
  "next_round_required": true,
  "reason": "winner ratio 0.95 < threshold 0.999"
}
```

**exit code**:
- 0 = ratio ≥ threshold (round N+1 불필요)
- 1 = ratio < threshold (round N+1 강제, stderr 메시지 + JSON output)

#### 3.1.3 HARD-RULE 9.qq (orchestrator SKILL.md)

> **9.qq — Tournament 다카포 임계 강제 (sprint-41 PR-B 신규)**
> - phase 06/08 종료 직전 orchestrator 가 `dacapo_threshold.py --tournament-md <path>` 자동 호출 의무.
> - exit 1 시 round N+1 자동 진행 (자율, 사용자 ack 0 — 페이즈 04 외 인터럽트 0 정합).
> - 2 round 후에도 ratio < threshold → ensemble synthesis 시도 (`ensemble-synthesis-default.md` 정합).
> - 3 round 후에도 미달 → frontmatter `dacapo_threshold_reached_after_3_rounds: false` 박힘 + phase 09 verdict cap 0.95 (정직 기록).
> - **증거 회피 사례** — 0510 회차 `tournament-impl-01.md` winner 57/60 → round 2 = 0 자율 lock. 본 9.qq = 차단.

#### 3.1.4 self_lint C-DCT

phase 06/08 종료 후:
- `plan/dacapo_threshold.json` 또는 `impl/dacapo_threshold.json` 존재 확인
- `verdict == "pass"` 또는 `dacapo_threshold_reached_after_3_rounds` 명시 확인
- 미달 + next_round_path 부재 → fail

#### 3.1.5 변경 파일 (PR-B)

| 파일 | 변경 종류 | 줄 수 |
|---|---|---|
| skills/theseus-harness/scoring/dacapo_threshold.py | new (Python script) | ~150 |
| skills/theseus-harness/conventions/intra-phase-dacapo-loop.md | edit (sprint-41 강화 절) | ~30 |
| skills/theseus-harness/phases/06-plan.md | edit (§종료 게이트 신규) | ~20 |
| skills/theseus-harness/phases/08-implement.md | edit (§종료 게이트 신규) | ~20 |
| skills/theseus-orchestrator/SKILL.md | edit (HARD-RULE 9.qq) | ~15 |

PR-B 총 ~235 줄.

---

### 3.2 PR-C — cold_session_artefacts.py (HARD-RULE 9.rr)

#### 3.2.1 동기

0510 회차에서 sprint-40 의 13 신규 산출물 모두 0 emit. agent 가 컨벤션 본문 무시 → silent skip. 본 PR = 부재 시 phase 09 진입 차단.

#### 3.2.2 CLI 명세

```bash
python skills/theseus-harness/scoring/cold_session_artefacts.py \
    --project-root .ShipofTheseus/<proj>/ \
    --grade G4 \
    --domain DES \
    --output .ShipofTheseus/<proj>/quality/gate_cold_session_artefacts.json
```

**검사 항목 (sprint-40 13 산출물):**
1. `quality/gate_v6_reproducibility.json` (PR-B G-1) — verdict + summary_byte_equal + violations
2. `quality/gate_v8_viewer_readiness.json` (PR-C M-2 사전) — missing == []
3. `quality/gate_readme_summary_consistency.json` (PR-E G-2) — drift.violations == []
4. `quality/gate_methodology_completeness.json` (PR-G G-4) — 4 skeleton verdict pass
5. `quality/gate_pnc.json` (sprint-39) — verdict pass
6. `quality/gate_mirror.json` — verdict pass
7. `quality/gate_primary.json` — verdict pass
8. `quality/gate_literal.json` — verdict pass
9. `intent/modeling_shortcuts.json` (PR-F G-3) — placeholder tier 0
10. `intent/04-cascaded-subq.md` (PR-F C-CSQ) — keyword 매칭 sub-Q 답
11. `webview/exit_gate.json` (PR-C M-2 종료) — verdict pass
12. `interactive-viewer/exit_gate.json` (G3+ 강제) — verdict pass + widgets ≥ 1/3
13. `interactive-viewer/dashboard.json` — schema valid

**output:**
```json
{
  "schema_version": "0.9.46",
  "project_root": "...",
  "grade": "G4",
  "domain": "DES",
  "checks": [
    {"path": "quality/gate_v6_reproducibility.json", "exists": true, "valid": true, "verdict": "pass"},
    ...
  ],
  "missing": [],
  "invalid": [],
  "verdict_fail": [],
  "verdict": "pass"
}
```

**exit code:**
- 0 = 13 모두 존재 + valid + verdict pass
- 1 = missing OR invalid OR verdict fail (stderr 결손 list)

#### 3.2.3 HARD-RULE 9.rr (orchestrator SKILL.md)

> **9.rr — Cold session 산출물 file-existence 강제 (sprint-41 PR-C 신규)**
> - phase 09 진입 직전 `cold_session_artefacts.py --project-root <root> --grade <grade>` 자동 호출 의무.
> - exit 1 시 결손 산출물 emit 후 phase 09 재진입.
> - **자동 평가 53/53 (100%) ≠ 산출물 통과** 명확 분리 — phase 09 진입 *전* 게이트.
> - **증거 회피 사례** — 0510 회차 sprint-40 산출물 0 emit + phase 09 GREEN 자율 통과. 본 9.rr = 차단.

#### 3.2.4 self_lint C-CSA

phase 09 진입 시 :
- `quality/gate_cold_session_artefacts.json` 존재 + verdict == "pass"
- 미달 시 phase 09 진입 거부

#### 3.2.5 변경 파일 (PR-C)

| 파일 | 변경 종류 | 줄 수 |
|---|---|---|
| skills/theseus-harness/scoring/cold_session_artefacts.py | new | ~250 |
| skills/theseus-harness/phases/09-quality-gates.md | edit (§V8 보강) | ~20 |
| skills/theseus-orchestrator/SKILL.md | edit (HARD-RULE 9.rr) | ~10 |

PR-C 총 ~280 줄.

---

### 3.3 PR-D — sprint_loop_cap.py (HARD-RULE 9.ss)

#### 3.3.1 동기

0510 회차 *"Given 100% on evaluator, sprint cap = 1 (re-validation only)"* — 자동 평가 100% 보고 sprint loop 1 회만. 그러나 *4 layer* 모두 ≥ 0.999 일 때만 stop 의무. 본 PR = 4 layer 종합 검사.

#### 3.3.2 4 layer 정의

| Layer | source | threshold |
|---|---|---|
| **Auto layer** | `evaluation_report.json:automated_checks.pass_rate` | ≥ 0.999 |
| **Internal layer** | `quality/09-quality-gate.md` 9 정적 게이트 + N derived + R RTG 모두 pass | 100% |
| **Tournament layer** | `plan/dacapo_threshold.json` + `impl/dacapo_threshold.json` 모두 verdict pass | 100% |
| **External layer** | (있을 경우) `results/zero_context_review.md` total/100 | ≥ 0.95 (자율 stop), ≥ 0.99 (강제 stop) |

#### 3.3.3 CLI 명세

```bash
python skills/theseus-harness/scoring/sprint_loop_cap.py \
    --project-root .ShipofTheseus/<proj>/ \
    --current-iteration 1 \
    --max-iterations 10
```

**output:**
```json
{
  "schema_version": "0.9.46",
  "iteration": 1,
  "max_iterations": 10,
  "layers": {
    "auto": {"score": 1.0, "passed": true},
    "internal": {"score": 1.0, "passed": true},
    "tournament": {"score": 0.95, "passed": false},
    "external": {"score": null, "passed": null, "note": "not yet evaluated"}
  },
  "verdict": "continue",
  "reason": "tournament layer 0.95 < 0.999"
}
```

**exit code:**
- 0 = 모든 layer ≥ threshold → stop 허용
- 1 = 적어도 1 layer 미달 → continue 의무

#### 3.3.4 HARD-RULE 9.ss (orchestrator SKILL.md)

> **9.ss — Sprint loop 종료 조건 (sprint-41 PR-D 신규)**
> - phase 10 sprint iteration 종료 직전 `sprint_loop_cap.py` 자동 호출 의무.
> - exit 1 시 sprint iteration 자동 +1 + 미달 layer 의 fix-TODO 자동 생성.
> - max_iterations 도달 시 frontmatter `sprint_loop_terminated_by_max_iter: true` + 미달 layer list 정직 기록.
> - **자동 평가 ≠ 휴먼 품질 ≠ 다카포** 3 layer 분리 원칙 — *단순 iteration count cap* 아님.
> - **증거 회피 사례** — 0510 회차 *"sprint cap = 1 re-validation only"* 자율 결정. 본 9.ss = 차단.

#### 3.3.5 self_lint C-SLC

phase 10 종료 시 :
- `sprints/<iter>/sprint_loop_cap.json` 존재
- 종료 시 모든 layer passed=true OR sprint_loop_terminated_by_max_iter 명시

#### 3.3.6 변경 파일 (PR-D)

| 파일 | 변경 종류 | 줄 수 |
|---|---|---|
| skills/theseus-harness/scoring/sprint_loop_cap.py | new | ~200 |
| skills/theseus-harness/phases/10-test-loop.md | edit (§4 layer 종료 조건) | ~30 |
| skills/theseus-orchestrator/SKILL.md | edit (HARD-RULE 9.ss) | ~15 |

PR-D 총 ~245 줄.

---

### 3.4 PR-E — runtime_guard_chain.py (HARD-RULE 9.tt)

#### 3.4.1 동기

위 3 CLI + skill_version + phase 단조성 검사 + 기타 메타-허들을 *단일 dispatch* 로 통합. orchestrator 가 매 phase 진입/종료 시 본 chain 자동 호출.

#### 3.4.2 CLI 명세

```bash
python skills/theseus-harness/scoring/runtime_guard_chain.py \
    --project-root .ShipofTheseus/<proj>/ \
    --phase 09 \
    --transition entry  # entry | exit
```

**검사 chain (phase entry):**
1. skill_version major + minor ≥ orchestrator
2. phase 단조성 (직전 phase fingerprint 정합)
3. phase entry hook (e.g., phase 09 entry = `cold_session_artefacts.py`)

**검사 chain (phase exit):**
1. phase exit hook (e.g., phase 06/08 exit = `dacapo_threshold.py`, phase 10 exit = `sprint_loop_cap.py`)
2. frontmatter 박힘 (skill_name / skill_version / phase / fingerprint / prev_fingerprint / created_at)
3. 산출물 emit 확인 (phase별 산출물 list)

**output (단일 종합):**
```json
{
  "schema_version": "0.9.46",
  "phase": "09",
  "transition": "entry",
  "checks": [
    {"name": "skill_version", "passed": true},
    {"name": "phase_monotonicity", "passed": true},
    {"name": "cold_session_artefacts", "passed": false, "exit_code": 1, "missing": ["gate_v6_reproducibility.json", ...]}
  ],
  "verdict": "fail",
  "advance_blocked": true
}
```

**exit code:**
- 0 = 모든 check pass → phase advance 허용
- 1 = 적어도 1 check fail → phase advance 차단 (orchestrator 가 fail check 의 fix step 자동 진행)

#### 3.4.3 HARD-RULE 9.tt (orchestrator SKILL.md)

> **9.tt — Runtime guard chain 자동 호출 (sprint-41 PR-E 신규, 모든 phase 진입/종료)**
> - 매 phase 진입/종료 시 `runtime_guard_chain.py --phase <N> --transition <entry|exit>` 자동 호출 의무.
> - exit 1 시 phase advance 차단 — orchestrator 가 fail check 의 fix step 자동 진행 후 chain 재호출.
> - phase-state-machine 컨벤션의 *runtime guard* 직접 구현.
> - **본 룰 = sprint-41 의 핵심 enforcement 메커니즘** — 위 9.qq / 9.rr / 9.ss 모두 본 chain 의 sub-call.

#### 3.4.4 self_lint C-RGC

orchestrator SKILL.md 본문에 9.tt + chain 호출 step 명시 검증.

#### 3.4.5 변경 파일 (PR-E)

| 파일 | 변경 종류 | 줄 수 |
|---|---|---|
| skills/theseus-harness/scoring/runtime_guard_chain.py | new | ~300 |
| skills/theseus-harness/conventions/phase-state-machine.md | edit (sprint-41 runtime guard 절) | ~30 |
| skills/theseus-orchestrator/SKILL.md | edit (HARD-RULE 9.tt) | ~20 |

PR-E 총 ~350 줄.

---

### 3.5 PR-F — generate_sprint40_artefacts.py

#### 3.5.1 동기

sprint-40 13 산출물의 *골격 자동 emit* — cold session 이 *데이터 채움* 만 책임. cold_session_artefacts.py 가 *부재 시 차단*, 본 PR 이 *부재 시 골격 emit 후 cold session 채움 유도*.

#### 3.5.2 CLI 명세

```bash
python skills/theseus-harness/scoring/generate_sprint40_artefacts.py \
    --project-root .ShipofTheseus/<proj>/ \
    --grade G4 \
    --domain DES
```

13 산출물의 *빈 골격* 자동 emit (verdict: "pending"). cold session 이 phase 진행 중 verdict 갱신.

#### 3.5.3 변경 파일 (PR-F)

| 파일 | 변경 종류 | 줄 수 |
|---|---|---|
| skills/theseus-harness/scoring/generate_sprint40_artefacts.py | new | ~250 |
| skills/theseus-harness/conventions/pre-cold-session-bootup.md | edit (sprint-41 골격 emit step) | ~15 |

PR-F 총 ~265 줄.

---

### 3.6 PR-G — sprint 마감 v0.9.46

skills/theseus-harness/SKILL.md `version: 0.9.46`, plugin.json, CHANGELOG entry. self_lint 136 → 140.

---

## 4. 구조 가치 — ouroboros 패러다임 직접 적용

| 결손 (sprint-40 후) | sprint-41 정정 |
|---|---|
| 컨벤션 본문 권고만, agent 자율 skip 가능 | CLI exit 1 시 phase advance 차단 — *명령형* enforcement |
| self_lint 본 저장소 only | cold session 산출물 직접 검사 (cold_session_artefacts.py) |
| 다카포 임계 미달 자율 종료 | dacapo_threshold.py exit 1 → round N+1 자동 강제 |
| sprint loop = 1 자율 stop | sprint_loop_cap.py 4 layer 모두 ≥ 임계 일 때만 stop |
| phase entry/exit 자율 진행 | runtime_guard_chain.py 가 매 transition 차단 가능 |

**원칙 정합 (메모리 trail):**
- [`feedback_pseudocode_to_enforcement.md`](../../../../memory/feedback_pseudocode_to_enforcement.md) — *"의사코드 → runtime guard"* 의 직접 코드화
- [`feedback_convention_runtime_gap.md`](../../../../memory/feedback_convention_runtime_gap.md) — sprint-40 미해소 갭의 본격 닫힘
- [`feedback_score_targeting_taboo.md`](../../../../memory/feedback_score_targeting_taboo.md) — 본 sprint 의 *구조 가치* = enforcement layer 의 코드화 (점수 회복 targeting 아님)

---

## 5. 검증 — 외부 적용 후 평가

PR-G 머지 후 v0.9.46 :
1. simulation-bench 측 fresh G4 cold session 실행
2. 평가 *대상* (구조 검증):
   - cold session 진행 중 13 산출물 모두 emit?
   - 다카포 임계 미달 시 round N+1 자동 진행?
   - sprint loop 가 4 layer ≥ 0.999 도달까지 iteration?
3. 활성 → 본 sprint 구조 가치 입증
4. 부분 미활성 → 어느 CLI 가 호출 안 되었는지 진단, sprint-42 fix
5. 외부 점수 변화는 *결과* / *부산물* — 본 sprint 목표 아님

---

## 6. 위험 + 대응

| 위험 | 영향 | 대응 |
|---|---|---|
| CLI 호출이 cold session 환경에서 실패 (PYTHONPATH / 의존성) | 중 | 본 하네스 의 모든 CLI 가 *stdlib only* — pyyaml 외 의존 0 |
| Tournament 본문 winner 점수 추출 정규식 false negative | 중 | dacapo_threshold.py 가 *3 source* (frontmatter / table / score-text 직접) 지원, 1 만 매칭하면 OK |
| sprint loop max_iterations 도달 후 무한 loop 위험 | 저 | max_iterations=10 default + 정직 기록 후 진행 |
| runtime_guard_chain.py 가 *모든 phase 차단* 으로 deadlock | 중 | 각 fail check 마다 자동 fix step (e.g., gate JSON 부재 → generate_sprint40_artefacts 재호출) |

---

## 7. 비고

본 sprint = sprint-40 의 *문서 layer* 정착 + *코드 layer* 신설. 메모리 [`feedback_convention_diet_paradigm.md`] 정합 — 신규 컨벤션 추가 X (현재 컨벤션 본문이 source of truth), CLI 4 종이 *enforcement 메커니즘* 으로 추가. 컨벤션 본문은 *명세*, CLI 가 *집행*.
