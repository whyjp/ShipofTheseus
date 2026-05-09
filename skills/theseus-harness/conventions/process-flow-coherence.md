---
id: process-flow-coherence
category: quality
applies-to-phases: '[09]'
applies-to-grades: '[all]'
trigger-when: 'process 차원'
indexed-in: conventions/INDEX.md
---

# Process Flow Coherence — cycle / state-machine / workflow 정합성 자기 검증

## 한 줄 요약

**페이즈 09 신규 게이트 — 작업이 *프로세스 / cycle / state machine* 차원이면 *cycle coherence* 자기 검증 의무.** v0915-cold01 외부 채점 -2pt (Sim correctness 18/20) 의 직접 원인 = load-haul-dump-return cycle 일관성 자체 검증 룰 부재. 페이즈 09 게이트 7 (env-satisfied + 실 부팅) 만으로는 *프로세스 모델 자체 정합* 검증 불가.

## 1. 결손 진단

기존 페이즈 09 게이트 7 종 (의도 / 범위 / SOLID / 테스트 / FE-BE / NFR / 실 부팅) 이 *cycle / state machine / workflow* 차원의 정합성 검증 안 함:

| 도메인 | 검증되어야 할 cycle 정합 | 결손 |
|---|---|---|
| DES (시뮬레이션) | load → haul → dump → return cycle 모든 entity 완료 | 검증 룰 0 |
| Workflow (job orchestration) | created → queued → running → completed → archived 모든 state 도달 가능 | 검증 룰 0 |
| Transaction (거래) | begin → operation → commit | rollback 모든 path | 검증 룰 0 |
| State machine (FSM) | initial → ... → terminal 모든 path coverage | 검증 룰 0 |
| Pipeline (ETL) | extract → transform → load 모든 stage 통과 + error path | 검증 룰 0 |

→ phase 09 *실 부팅* 게이트 7 가 booting 만 검증. *프로세스 동역학 정합* 은 검증 안 됨.

## 2. 운영 룰

### Step 1 — 페이즈 06 plan 의 *cycle / state machine* 명시 의무

`plan/06-plan.md` 본문에 (작업이 process 차원이면):

```markdown
## Process Flow / State Machine

states: [initial, running, completed, error, archived]
transitions:
  - initial → running    (start_event)
  - running → completed  (success_event)
  - running → error      (error_event)
  - error → running      (retry_event, max=3)
  - completed → archived (cleanup_event)
  - error → archived     (cleanup_event)
terminal_states: [archived]
cycle_invariant: "모든 entity 가 archived 도달 (또는 timeout)"
```

작업 도메인이 process 차원 X (예: 단순 calc / 정적 변환) 면 본 절 skip + frontmatter `process_flow_applicable: false`.

### Step 2 — 페이즈 09 신규 게이트 8 — Cycle Coherence

`quality/09-quality-gate.md` 게이트 8:

```yaml
gate_8_cycle_coherence:
  applicable: true   # process_flow_applicable 정합
  checks:
    - all_states_reachable: true       # initial → 모든 state 경로 존재
    - all_terminal_reachable: true     # 모든 entity 가 terminal 도달 가능
    - no_orphan_states: true           # transition 0 인 state 없음
    - cycle_invariant_holds: true      # plan §cycle_invariant 검증
    - error_paths_explicit: true       # error / timeout / cancellation path 명시
  evidence:
    - sprints/01/cycle_coverage.json   # 실 코드 실행 결과 — 모든 state 도달 횟수
    - tests/test_process_flow.py       # state machine 단위 테스트
```

### Step 3 — 도메인별 cycle coherence 검증 함수

generic 검증 함수 + 도메인별 specific:

```python
def check_cycle_coherence(plan: dict, sprint_evidence: dict) -> list[str]:
    states = plan["process_flow"]["states"]
    transitions = plan["process_flow"]["transitions"]
    terminals = plan["process_flow"]["terminal_states"]
    errors = []
    # 1. 모든 state reachable from initial
    reachable = _bfs_reachable(states, transitions, plan["initial_state"])
    unreachable = set(states) - reachable
    if unreachable:
        errors.append(f"unreachable states: {unreachable}")
    # 2. 모든 terminal reachable
    for term in terminals:
        if term not in reachable:
            errors.append(f"terminal {term} unreachable")
    # 3. orphan states (transition 0)
    for s in states:
        if s in terminals:
            continue
        out_count = sum(1 for t in transitions if t["from"] == s)
        if out_count == 0:
            errors.append(f"orphan state: {s} (no outgoing transition)")
    # 4. sprint evidence: 실 실행 시 state 도달 카운트
    coverage = sprint_evidence.get("state_visit_count", {})
    for s in states:
        if coverage.get(s, 0) == 0 and s not in terminals:
            errors.append(f"state {s} never reached in sprint run (zero coverage)")
    return errors
```

### Step 4 — 도메인-specific 추가 검증 (사용자 per-project)

본 하네스에 *built-in 도메인 어댑터 0* (sprint-19+, 벤치 어뷰징 회피). 사용자가 per-project 로 도메인 어댑터 (`domain-adapters/<domain>.md`) 작성 시 [`domain-pack.md`](domain-pack.md) §3 (sprint-37 PR-AG 통합) 프레임워크 준수 — process-flow-coherence 게이트가 어댑터의 cycle pattern 카탈로그를 자동 활용.

## 3. self_lint 룰

`scoring/self_lint.py` C-PFC (신규):

```python
def lint_process_flow_coherence(skill_root: Path) -> list[str]:
    errors = []
    pfc = (skill_root / "conventions" / "process-flow-coherence.md").read_text(encoding="utf-8")
    p9 = (skill_root / "phases" / "09-quality-gates.md").read_text(encoding="utf-8")
    p6 = (skill_root / "phases" / "06-plan.md").read_text(encoding="utf-8")
    required = ["all_states_reachable", "cycle_invariant", "terminal_states", "orphan_states", "error_paths_explicit"]
    for kw in required:
        if kw not in pfc:
            errors.append(f"process-flow-coherence.md: '{kw}' 키워드 누락")
    if "process-flow-coherence" not in p9 and "cycle coherence" not in p9.lower():
        errors.append("phases/09-quality-gates.md: process-flow-coherence (게이트 8) 인용 누락")
    if "process_flow_applicable" not in p6:
        errors.append("phases/06-plan.md: process_flow_applicable frontmatter 인용 누락")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- state machine / cycle = 모든 process-차원 도메인 generic.
b- reachable / terminal / orphan / coverage 메트릭 = generic graph 분석.
c- domain adapter (DES / workflow / FSM 등) 가 specific cycle pattern 추가.
d- `process_flow_applicable: false` 옵션 — 정적 calc 작업은 skip.

## 5. 안티 패턴

a- **process_flow 명시 안 하고 게이트 8 skip** — applicable false 명시 의무.
b- **cycle_invariant 명시 안 함** — 모든 cycle 작업은 invariant 1+ 의무.
c- **error path 누락** — happy path 만 plan, error/timeout/cancellation 무시. self_lint 가 transitions 의 error keyword 검증.
d- **state coverage 0 인데 PASS** — 실 실행 시 한 번도 도달 안 한 state 가 있으면 *plan 결손* 또는 *test 결손*.

## 6. 자기 검증

본 하네스 자체에 적용 — 페이즈 00 → 14 가 *15 page state machine*. initial = 호출 직후, terminal = handoff 완료. 본 하네스 자체에 cycle_invariant ("호출 시 14 페이즈 산출물 모두 박힘") 적용 가능.
