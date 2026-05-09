# 2026-05-10 — Bench 001 v0.9.45 회귀 (-5pt) — sprint-40 enforcement 0 활성 증거

> **회차:** `2026-05-10__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4`
> **점수:** **90/100** (v0.9.44 g4-v2 95/100 대비 **-5pt 격하**)
> **frontmatter:** `skill_version: 0.9.45` (sprint-40 적용 명시)

## 0. TL;DR — 3 결론

1. **점수 -5pt 회귀** — v0.9.44 95 → v0.9.45 90. sprint-40 5 layer enforcement closure 추가에도 불구하고 *역행*.
2. **sprint-40 산출물 0 emit** — `gate_v6` / `gate_v8` / `exit_gate × 2` / `gate_readme_summary` / `modeling_shortcuts` / `cascaded-subq` / `gate_methodology_completeness` / 4 게이트 JSON / `interactive-viewer/` 디렉터리 모두 *부재*. frontmatter 만 0.9.45, 실 enforcement 0.
3. **다카포 임계 미달 + sprint loop = 1 회만** — `tournament-impl-01.md` winner 57/60 = 0.95 (< 0.999 임계) 임에도 round 2 진행 0. 사용자 직접 지적 = *"이쯤이면 충분해" 자율 종료 습성*.

## 1. 점수 분포 비교 (0509 g4-v2 95 vs 0510 g4 90)

| Category | 0509 (95) | 0510 (90) | Δ |
|---|---:|---:|---:|
| Conceptual modelling | 19 | 18 | -1 |
| Data and topology | 15 | 14 | -1 |
| Simulation correctness | 18 | 18 | 0 |
| Experimental design | 14 | 13 | -1 |
| Results and interpretation | 14 | 13 | -1 |
| Code quality | 10 | 9 | -1 |
| Traceability | 5 | 5 | 0 |
| **합계** | **95** | **90** | **-5** |

5 차원 모두 -1 격하. *단일 도메인 결손* 아니라 *전반적 noise*. LLM 비결정성 대비 5pt 일관 격차 = **하네스 enforcement 의 구조 결손** 정 직접 evidence.

## 2. 다카포 임계 미달 + 재시도 0 (사용자 직접 지적)

### 2-1. Plan tournament round 1 (sprint 06)

본문 (`plan/tournament-01.md`) :
```
| **Total** | **50/60** | **41/60** | **56/60** | — |
## Winner reasoning
- U3 wins — strict spec adherence + max auditability + zero numerical risk vs U1.
- Final: **U1 engine + U3 reporting**, locked.
```

- Winner U3 = 56/60 = **0.933** (threshold 0.999 미달)
- Combined U1+U3 추정 57/60 = **0.95** (여전히 미달)
- **Round 2 진행 0** — `intra-phase-dacapo-loop.md` 컨벤션 의무인 *임계 도달까지 재경합* 자율 skip

### 2-2. Impl tournament round 1 (sprint 08)

본문 (`impl/tournament-impl-01.md`) :
```
| **Total** | 50/60 | 41/60 | 56/60 | **57/60** |
## Winner
- Combined U1 engine + U3 reporting wins.
```

- Winner 57/60 = **0.95** (threshold 0.999 미달)
- **Round 2 진행 0** — 동일 패턴

### 2-3. Phase 09 quality gate body 의 자율 stop

본문 (`quality/09-quality-gate.md` 마지막 절) :
```
✅ Gate 09 GREEN — all 7 gates pass + public_tests + invariants. Proceed to sprint loop (phase 10) for any score-recovery.
Given 100% on evaluator pre-sprint, sprint cap = 1 (re-validation only).
```

**핵심 오인.** *자동 평가 53/53 (100%)* 를 *전체 통과* 로 오해 → "sprint cap = 1 re-validation only" 자율 결정. 그러나:
- *내부 tournament 다카포 0.999 미달* (57/60)
- *외부 zero-context reviewer human-quality 90/100* (자동 평가 ≠ 휴먼 품질)
- *sprint-40 신규 산출물 0 emit*

세 layer 모두 미통과인데 sprint loop 1 회만 진행 후 종료.

## 3. sprint-40 산출물 검증 — 모두 0 emit

`/d/github/simulation-bench/submissions/2026-05-10__.../.ShipofTheseus/synthetic_mine_throughput/` 검사:

| sprint-40 의무 산출물 | 위치 | 0510 회차 |
|---|---|---|
| `quality/gate_v6_reproducibility.json` (PR-B) | quality/ | ❌ 부재 |
| `quality/gate_v8_viewer_readiness.json` (PR-C) | quality/ | ❌ 부재 |
| `quality/gate_readme_summary_consistency.json` (PR-E) | quality/ | ❌ 부재 |
| `quality/gate_methodology_completeness.json` (PR-G) | quality/ | ❌ 부재 |
| `quality/gate_pnc.json` (sprint-39 + PR-E auto-emit) | quality/ | ❌ 부재 |
| `quality/gate_mirror.json` | quality/ | ❌ 부재 |
| `quality/gate_primary.json` | quality/ | ❌ 부재 |
| `quality/gate_literal.json` | quality/ | ❌ 부재 |
| `intent/modeling_shortcuts.json` (PR-F) | intent/ | ❌ 부재 |
| `intent/04-cascaded-subq.md` (PR-F) | intent/ | ❌ 부재 |
| `webview/exit_gate.json` (PR-C) | webview/ | ❌ 부재 |
| `webview/data/webview.json` (sprint-35 v0.9.40 의무) | webview/ | ❌ 부재 (마크다운 `*.html` 파일들만) |
| `interactive-viewer/` 디렉터리 (sprint-36 v0.9.41 G4 강제) | root | ❌ **디렉터리 자체 부재** |

`webview/` 에는 `01-intent.html` ~ `08-lineage.html` + `index.html` 만 — sprint-40 종료 게이트 의 6 파일 (index.html / data/webview.json / assets/{app.js, mermaid, marked, styles}) 모두 미생성.

**즉, frontmatter `skill_version: 0.9.45` 박힘에도 sprint-40 의 모든 enforcement layer 가 *0 활성*.** 컨벤션 선언 ≠ 런타임 집행 갭이 sprint-40 후에도 *그대로*.

## 4. 진단 — 본 하네스 의 *진짜* 구조 결손

### 4-1. 컨벤션 본문 = 권고 / runtime guard = 부재

sprint-40 PR-B/C/D/E/F/G 본문에 박은 게이트 룰 :
- "phase 09 진입 시 ... gate JSON 자동 emit"
- "exit_gate.json verdict pass 의무"
- "intra-phase-dacapo-loop 임계 0.999 까지 재경합"

이 룰의 *enforcement 메커니즘* 은 두 가지뿐:
1. **self_lint** (텍스트 검증) — 본 하네스 자기 저장소에서만 작동, *cold session 산출물 검증 0*
2. **agent 자율 의지** — 컨벤션 본문 읽고 따름

**즉, cold session agent 가 컨벤션 본문 무시 → silent skip 가능.** v0.9.44 회차에서 발견된 *컨벤션 선언 ≠ 런타임 집행* 갭이 sprint-40 *문서 layer 강화* 만으로는 닫히지 않은 직접 evidence.

### 4-2. agent 의 "이쯤이면 충분해" 패러다임 — 자율 종료 습성

사용자 직접 지적:
> "다하다말고 이정도면되겠지! 이쯤이면 충분해 하는 오만 혹은 다른 버짓으로인해 더이상 노력하지않는 습성을 가지고있다 하네스가"

증거:
- Plan tournament round 1 winner 56/60 = 0.933 → "U3 wins" 자율 lock, round 2 = 0
- Impl tournament round 1 winner 57/60 = 0.95 → "Combined wins" 자율 lock, round 2 = 0
- Phase 09 후 "Given 100% on evaluator, sprint cap = 1" 자율 결정

**근본 원인.** 본 하네스 의 모든 *임계 / 다카포* 룰이 *권고* 본문으로만 박혀 있음. CLI / 프로그램 이 *명령형으로 차단* 하지 않음. agent 가 budget tight 또는 자율 판단으로 임계 미달인 채 종료해도 *처벌 메커니즘 0*.

### 4-3. LLM 비결정성 vs 구조 결손 분리

사용자 직접 지적:
> "llm 의 비결정성을 생각 하더라도 동일문제의 결과가 하네스 설계의 문제가 있음을 증명한다"

세 회차 비교:
| 회차 | skill_version | 점수 | 다카포 round 2 |
|---|---|---:|---|
| 0509 g4-v2 | 0.9.44 (sprint-39) | 95 | (governance trail 미확인 — 추정 0) |
| 0510 g4 | 0.9.45 (sprint-40) | 90 | 0 |

LLM 비결정성 0.5 ~ 1pt 흔들림 가능. 그러나 *5pt 일관 격하 + sprint-40 산출물 0 emit + 다카포 round 2 = 0* 의 **3 신호 동시 발현 = 구조 결손 직접 증명**.

## 5. 결손 = ouroboros 패러다임 부재 — CLI/프로그램 기반 rule-based 허들

사용자 명시 비교:
> "나 우루보로스가 mcp 로 결정된 허들을 넘도로 하는 cli/프로그램기반 룰베이스의 허들을 만든것 처럼 / 허들을 강화하고 지키도록 하고싶고"

ouroboros 패러다임:
- MCP tool 이 *명령형으로 stage advance 차단*
- agent 자율 skip 불가 — MCP server 가 verdict return
- code-level enforcement, 본문 권고 0

본 하네스 현재 상태:
- 컨벤션 본문 권고만
- self_lint 는 본 저장소 자기 검증, cold session 산출물 검증 0
- runtime guard 0

**해결 방향 (sprint-41 제안).** 본 하네스 의 모든 sprint-40 게이트를 **CLI 스크립트** 로 코드화 + orchestrator 가 phase 진입/종료 시 *명령형 호출 의무*. exit 1 = phase advance 차단, exit 0 까지 sprint loop.

## 6. sprint-41 plan 후보 — Hurdle-as-CLI (트랙 5)

본 sprint-41 = *컨벤션 권고 → CLI runtime guard* 변환. 본 하네스의 *agent 자율 종료 습성* 직접 차단.

### 6-1. 신규 CLI 4 종

| 파일 | 역할 | exit code |
|---|---|---|
| `skills/theseus-harness/scoring/dacapo_threshold.py` | tournament-NN.md 본문 winner 점수 grep → ratio 계산 → < 0.999 시 exit 1 | 0 = 임계 통과 / 1 = round N+1 강제 |
| `skills/theseus-harness/scoring/sprint_loop_cap.py` | sprints/NN/report.json + tournament + 외부 평가 + 내부 게이트 4 layer 모두 ≥ 0.999 일 때만 stop | 0 = stop 허용 / 1 = continue 의무 |
| `skills/theseus-harness/scoring/cold_session_artefacts.py` | sprint-40 13 신규 산출물 존재 + JSON valid + verdict==pass 검증 | 0 = 모두 통과 / 1 = 결손 list stderr |
| `skills/theseus-harness/scoring/runtime_guard_chain.py` | 위 3 + skill_version + phase 단조성 통합 dispatch | exit 0 까지 phase advance 차단 |

### 6-2. orchestrator HARD-RULE 9.qq ~ 9.tt 신규

- **9.qq** — phase 06/08 종료 직전 `dacapo_threshold.py` 자동 호출 의무. exit 1 시 round N+1 자동 진행. 자율 skip 금지 — 본 CLI 의 verdict 가 phase advance gatekeeper.
- **9.rr** — phase 09 진입 직전 `cold_session_artefacts.py` 자동 호출 의무. exit 1 시 결손 산출물 emit 후 phase 09 재진입. *자동 평가 100% ≠ 산출물 통과* 명확 분리.
- **9.ss** — phase 10 sprint loop 종료 조건 = `sprint_loop_cap.py` exit 0. *단순 iteration count cap* 아님 — *4 layer 모두 임계 도달* 이 종료 조건.
- **9.tt** — `runtime_guard_chain.py` 가 매 phase 진입/종료 시 자동 호출 (phase-state-machine 정합).

### 6-3. self_lint 신규 4 룰

- **C-DCT** (Da Capo Threshold) — tournament 산출물의 winner_ratio ≥ 0.999 또는 next_round path 명시
- **C-CSA** (Cold Session Artefacts) — 13 신규 산출물 모두 존재 + valid + verdict pass
- **C-SLC** (Sprint Loop Cap) — sprint stop 시 4 layer evidence 박힘
- **C-RGC** (Runtime Guard Chain) — orchestrator 본문에 4 CLI 호출 step 명시

### 6-4. 예상 효과

본 sprint-41 후 v0.9.46 회차 :
- 다카포 미달 시 *프로그램 이 차단* → round N+1 자동, agent 자율 skip 불가
- sprint-40 산출물 *부재 시 phase 09 진입 거부* → 모두 emit 후 phase 09 통과
- sprint loop *4 layer ≥ 0.999 도달까지 자동 iteration* → "이쯤이면 충분해" 패러다임 차단

본 sprint-41 = sprint-40 *문서 강화* 의 *코드 layer* 보강. ouroboros 패러다임 직접 적용.

## 7. 다음 단계

본 분석 보고 후 사용자 confirm 받고 sprint-41 진입. 첫 PR-A = sprint-41 plan.md (본 §6 1:1 기반).

---

## Appendix — 원자료 위치

- 0510 회차 governance trail: `/d/github/simulation-bench/submissions/2026-05-10__.../.ShipofTheseus/synthetic_mine_throughput/`
- 다카포 미달 증거 (plan): `<governance>/plan/tournament-01.md` (winner 56/60)
- 다카포 미달 증거 (impl): `<governance>/impl/tournament-impl-01.md` (winner 57/60)
- 자율 stop 증거: `<governance>/quality/09-quality-gate.md` ("sprint cap = 1")
- 점수 trail: `/d/github/simulation-bench/scores/seed_scores.json`
- 본 하네스 메모리: [`feedback_pseudocode_to_enforcement.md`], [`feedback_convention_runtime_gap.md`], [`feedback_score_targeting_taboo.md`]
