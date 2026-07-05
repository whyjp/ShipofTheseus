---
id: dacapo-enforcement
category: tournament
applies-to-phases: '[06,08]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'phase exit'
indexed-in: conventions/INDEX.md
---

# Da Capo Enforcement — 의사코드 → 강제 게이트 변환 (sprint-16 / v0.9.22)

## 한 줄 요약

**v0.9.21 [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) 의 의사코드는 *문서 가이드*. 본 컨벤션은 그 의사코드를 *runtime guard* 로 격상.** Da Capo Loop 의 Step A-G 가 단순 권고가 아니라 phase 06 → 07 / phase 08 → 09 핸드오프 시점의 *의무 게이트* 로 강제. 외부 cold session `2026-05-05__001_mine_g4` 에서 winner=0.892 (당시 G4 임계 0.999 미달 — 현재는 stop_policy §2.2 참조, 설계 B2) 이 dacapo loop 0회 실행 후 phase 07 진입한 회귀의 직접 원인 정정.

## 1. 결손 진단

v0.9.21 sprint-15 의 [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) 가 phase 06/08 본문에 의사코드 6 step 박았으나 :

| 결손 | 증거 |
|---|---|
| 의사코드 = agent 권고 | phase 06 본문 `def phase_06(...)` 가 *agent 가 따라가는 흐름* 일 뿐, agent 자율로 "Winner clear → phase 07" 결론 가능 |
| HARD-RULE 9.o 본문 부재 | orchestrator SKILL.md (v0.9.5) 의 HARD-RULE 9 a/b/c 만 있음 — Da Capo loop 미실행 차단 룰 없음 |
| self_lint 강제 부재 | C-DCL-WIN-THRESHOLD 정의는 있으나 phase 07 진입 전 의무 hook 부재 |
| frontmatter 추적 부재 | tournament.md 가 winner_score 만 박고 rerun_count, step_d_pass 등 누락 가능 |

→ agent 가 의사코드를 *읽고도 skip* 가능한 구조. 본 컨벤션이 4 결손 정정.

## 2. HARD-RULE 9.o — 본문 (orchestrator SKILL.md 박힘)

```
> **HARD-RULE 9.o — Da Capo Loop 의무 게이트 (sprint-16 / v0.9.22):**
>
> Phase 06 (plan-tree) 또는 Phase 08 (impl multiverse) 의 tournament 산출물
> (`plan/tournament-NN.md` / `impl/tournament-impl-NN.md`) 이 다음 조건을
> *모두* 만족하지 않으면 phase 07 / phase 09 진입을 *자동 거부*:
>
> 1- frontmatter 에 `dacapo_loop_executed: true` 명시
> 2- `step_d_tournament_pass: bool` + `step_d_shadow_pass: bool` 명시
> 3- (tournament_pass=true AND shadow_pass=true) → CONVERGED
>    OR (rerun_count >= max_rerun(grade)) → CAP_REACHED
>    OR (clock_now - timing/start.json.started_at_utc > wall_budget) → BUDGET_OVERRUN
>      AND `fallback_reason` 본문 ≥ 1 줄 (CAP_REACHED / BUDGET_OVERRUN 시)
>      AND `rerun_count >= 1` 의무 (최소 1 회 실 rerun 후에만 cap 발동 — sprint-17)
>      AND `fallback_reason` 본문에 forward projection 라벨 (anticipated / would exceed / infeasible to continue / wall makes ... infeasible / further .* infeasible / 45.?min wall) 부재 의무 — sprint-17
>
> **시간 cap = 측정 only — LLM forward projection 자동 거부:**
> clock_elapsed = now() - timing/start.json.started_at_utc (실 wall clock 측정).
> LLM 의 시간 추정은 인간 작업시간 기준 → 항상 "시간내 처리 불가능" 으로 편향.
> 측정값이 wall_budget 초과 했을 때만 BUDGET_OVERRUN 발동 — 재시도 후 *예상* 시간 계산 금지.
> 4- rerun_count >= 1 시 dacapo-rerun-NN.md 갯수 == rerun_count
>    (Step F lesson 산출물 의무)
> 5- rerun_count >= 1 시 universe 1 개가 anonymized previous winner
>    (Step G ad anonymize 의무)
>
> **위반 시 처리** — orchestrator 가 phase 07/09 진입 *전* 본 5 조건 검증.
> 미달 시 :
> a- `intent/00-violation.md` 에 위반 기록 (어느 조건, 어느 frontmatter 값)
> b- phase 06 / 08 *재진입* 강제 (Step A 부터)
> c- 사용자 ack 없이 자율 회귀 — autonomy.md 정합 (페이즈 04 외 인터럽트 0)
> d- 위반 횟수 ≥ 3 시에만 사용자 ack (예외 처리)
>
> **본 룰의 *unique role*** — 의사코드는 룰 본문이 아닌 *agent 행동 가이드*,
> 본 룰은 *orchestrator 게이트*. 두 layer 모두 박혀야 enforcement 완성.
```

## 3. 게이트 위치

```
phase 06 진행
  → tournament-00.md 산출
  → shadow-grade-00.md 산출
  → Step D AND check
     ├─ PASS → 06-plan.md promote → ★ 게이트 진입 ★
     │            ├─ 5 조건 검증 PASS → phase 07 진입
     │            └─ 5 조건 검증 FAIL → 00-violation.md + phase 06 재진입
     └─ FAIL → Step E cap 검사
        ├─ rerun < max → Step F lesson + Step G anonymize → Step A 재진입
        └─ rerun >= max → BUDGET_BOUND + fallback_reason → ★ 게이트 진입 ★
                            (위와 동일 5 조건 검증)
```

phase 08 동일 — `impl/tournament-impl-NN.md` + `impl/shadow-grade-NN.md` + `impl/08-impl-log.md` promote 후 게이트.

## 4. orchestrator 책임 (구현 인터페이스)

```python
def gate_phase06_to_07(artifact_dir: Path, grade: Grade) -> GateResult:
    """phase 06 종료 → 07 진입 전 의무 게이트. HARD-RULE 9.o 정합."""

    tournament = load_latest('tournament-NN.md', artifact_dir / 'plan')
    fm = parse_frontmatter(tournament)

    # 조건 1
    if not fm.get('dacapo_loop_executed'):
        return REJECT('dacapo_loop_executed 부재 또는 false')

    # 조건 2
    if 'step_d_tournament_pass' not in fm or 'step_d_shadow_pass' not in fm:
        return REJECT('step_d_*_pass frontmatter 부재')

    # 조건 3a — CONVERGED 경로
    if fm['step_d_tournament_pass'] AND fm['step_d_shadow_pass']:
        return ACCEPT('CONVERGED')

    # 조건 3b — CAP_REACHED OR BUDGET_OVERRUN 경로 (sprint-17 — 측정 only)
    rerun = fm.get('rerun_count', 0)
    max_rerun = MAX_RERUN[grade]   # G3=2 / G4=3 / G5=5

    # 시간 cap = 측정 only (LLM 추정 금지)
    import datetime as dt, json, re
    start_at = dt.datetime.fromisoformat(
        json.loads((artifact_dir.parent / 'timing' / 'start.json').read_text())['started_at_utc'].replace('Z','+00:00')
    )
    clock_elapsed_min = (dt.datetime.now(dt.timezone.utc) - start_at).total_seconds() / 60
    wall_budget_min = WALL_BUDGET_MIN[grade]   # benchmark prompt 명시값 (e.g., 45)

    cap_reached = (rerun >= max_rerun)
    budget_overrun = (clock_elapsed_min > wall_budget_min)

    if cap_reached or budget_overrun:
        if rerun == 0:                              # sprint-17 — min loop attempt
            return REJECT('rerun_count=0 인데 cap claim — 최소 1 회 실 rerun 후에만 발동 가능')
        fr_path = artifact_dir / 'plan/fallback-reason.md'
        if not fr_path.exists() or not fr_path.read_text().strip():
            return REJECT('CAP_REACHED/BUDGET_OVERRUN 인데 fallback-reason.md 부재 또는 빈 본문')
        # sprint-17 — forward projection 차단
        forward_pat = r'(anticipated|would exceed|infeasible to continue|wall makes .* infeasible|further .{0,40} infeasible|45.?min wall|budget tight 예상)'
        if re.search(forward_pat, fr_path.read_text(), re.I):
            return REJECT('fallback_reason 에 forward projection 라벨 detected — 측정값 외 사용 금지')
        # 조건 4
        rerun_logs = list((artifact_dir / 'plan').glob('dacapo-rerun-*.md'))
        if len(rerun_logs) != rerun:
            return REJECT(f'dacapo-rerun-NN.md {len(rerun_logs)} != rerun_count {rerun}')
        # 조건 5
        if not has_anonymized_previous_winner(artifact_dir, rerun):
            return REJECT('anonymized previous winner 부재 (ad C-TBR-ANON)')
        return ACCEPT('CAP_REACHED' if cap_reached else 'BUDGET_OVERRUN')

    # 조건 1-3 통과 못 함 — 의사코드 미완 실행 + 측정 시간 미초과 → re-enter Step A 의무
    return REJECT(
        f'winner_score={fm["winner_score"]} < threshold + rerun_count={rerun} < max_rerun '
        f'+ clock_elapsed={clock_elapsed_min:.1f}min < wall_budget={wall_budget_min}min — Step F/G skip detected'
    )


def on_gate_reject(reason: str, phase: int):
    """REJECT 시 자율 회귀 — 페이즈 04 외 인터럽트 0 정합."""
    write_violation(intent/00-violation.md, phase=phase, reason=reason)
    increment_violation_count()
    if violation_count >= 3:
        return ASK_USER('Da Capo gate 3회 연속 fail — 진단 필요')
    force_re_enter_phase(phase)   # phase 06 또는 08 의 Step A 부터 재실행 (부분 재진입 금지)
```

## 5. 의사코드 vs 게이트 — 두 layer 책임 분리

| Layer | 책임 | 위치 | enforcement |
|---|---|---|---|
| **의사코드** (bl v0.9.21) | agent 행동 가이드 — Step A~G 명시 | `phases/06-plan.md` + `phases/08-implement.md` 본문 | agent 자율 (skip 가능) |
| **게이트** (본 컨벤션 v0.9.22) | orchestrator runtime guard — 5 조건 검증 | `gate_phase06_to_07()` + HARD-RULE 9.o | 미달 시 자동 회귀 |

→ 두 layer 가 *상호 보완*. 의사코드가 *방법*, 게이트가 *증거*. agent 가 의사코드를 잘 따르면 게이트 통과, skip 하면 게이트 reject.

## 6. self_lint 신규 룰 — 5 조건 정합

| Lint ID | 검증 | PASS | FAIL |
|---|---|---|---|
| **C-DCL-GATE** | tournament.md frontmatter 5 조건 | 모두 만족 | 하나라도 누락 |
| **C-DCL-WIN-THRESHOLD** (v0.9.21 재정의) | winner < threshold + rerun=0 + phase N+1 산출물 존재 | (해당 없음) | fail |
| **C-DCL-RERUN-LOG** (v0.9.21 재정의) | rerun >= 1 시 dacapo-rerun-NN.md 갯수 == rerun_count | 일치 | 불일치 |
| **C-DCL-ANON** (v0.9.21 재정의) | rerun >= 1 시 anonymized prev winner 존재 | 존재 | 부재 |
| **C-DCL-FALLBACK** (신규) | BUDGET_BOUND 시 fallback-reason.md 본문 ≥ 1 줄 | 존재 | 부재 또는 빈 |
| **C-DCL-NO-FORWARD-PROJECT** | fallback_reason 본문 regex (anticipated / would exceed / infeasible to continue / wall makes … infeasible) | 매치 0 | 매치 ≥ 1 |
| **C-DCL-MIN-LOOP-ATTEMPT** | step_e_cap_reached=true OR fallback claim 시 rerun_count ≥ 1 | 만족 | rerun=0 인데 cap claim |
| **C-DCL-CAP-MEASURED** | BUDGET_OVERRUN claim 시 (clock_now - start) > wall_budget 측정 일치 | 측정 일치 | 측정 미달인데 claim |

[`../scoring/self_lint.py`](../scoring/self_lint.py) 의 `check_dacapo_enforcement()` 함수가 phase 06 / 08 종료 시점에 자동 호출.

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- frontmatter 5 조건 = phase 06 / 08 무관 일반 게이트 스키마.
b- gate_phase06_to_07() = orchestrator 의 일반 핸드오프 hook (다른 phase 도 동일 패턴 가능).
c- on_gate_reject() = autonomy.md 의 페이즈 04 외 인터럽트 0 + 위반 횟수 캡 의 일반 패턴.

## 8. 안티 패턴

a- **게이트 SKIP** — orchestrator 가 tournament.md frontmatter 검증 안 하고 phase 07/09 진입 → 본 컨벤션 무력화. self_lint C-DCL-GATE 강제.
b- **의사코드만 갱신, 게이트 누락** — sprint-15 의 실제 패턴. 의사코드 + 게이트 *양쪽* 갱신 의무.
c- **violation_count 무시 ack** — 위반 3회 후에도 자율 회귀만 → 무한 회귀 가능. 3회 이상 사용자 ack 의무.
d- **gate REJECT 후 partial 재진입** — Step F 부터만 재실행 → universe 변경 룰 위반. Step A 부터 전체 재실행 의무.
e- **frontmatter `dacapo_loop_executed: true` 거짓 박기** — agent 가 검증 우회 위해 거짓 박을 가능. 다른 4 조건과 cross-validation (rerun_count + step_d_*_pass + dacapo-rerun-NN.md 존재) 으로 검증.
f- ** forward time projection** — agent 가 "rerun N 번 더 하면 시간 부족" 으로 *예측* 해 BUDGET_BOUND 라벨. 시간은 *측정만*, 예측 금지. cold session `2026-05-05__001_mine_g4_theseus/plan/tournament-01.md` 의 `step_e_cap_reached: false` + `rerun_count: 0` + `budget_used_total: 0.20` 인데 promote universe-1 + `next_action: "...45min wall makes further universe rerun infeasible"` 의 직접 회귀 정정.
g- ** min loop attempt 우회** — rerun 0 회로 BUDGET_OVERRUN 직행. 최소 1 회 실 rerun 후에만 cap 발동. C-DCL-MIN-LOOP-ATTEMPT 강제.
h- ** LLM 시간 추정 사용** — `budget_used_total` 을 측정값 아닌 LLM 추정값으로 박기. 본 필드는 (clock_now - start) / wall_budget 산식으로 계산되어야 하며 LLM 이 *추측* 안 됨. 추정값 박을 시 C-DCL-CAP-MEASURED 가 측정 mismatch 로 fail.

## 9. cold session 검증

`2026-05-05__001_mine_g4/plan/tournament.md` 재검증 :

| frontmatter 필드 | 값 | 게이트 조건 | 판정 |
|---|---|---|---|
| dacapo_loop_executed | (부재) | 조건 1 | **FAIL** |
| step_d_tournament_pass | (부재) | 조건 2 | **FAIL** |
| step_d_shadow_pass | (부재) | 조건 2 | **FAIL** |
| winner_score | 0.892 | 조건 3a (당시 >= 0.999, 현 stop_policy 참조) | FAIL |
| rerun_count | (부재) | 조건 3b (>= 3) | FAIL |
| fallback_reason | "" | 조건 3b 본문 ≥ 1 줄 | **FAIL** |

→ 5 조건 모두 미달. v0.9.22 게이트 적용 시 phase 07 진입 *자동 거부* + phase 06 재진입.

### sprint-17 추가 — 002 cold session `2026-05-05__001_mine_g4_theseus/plan/tournament-01.md`

| frontmatter / next_action | 값 | sprint-17 게이트 | 판정 |
|---|---|---|---|
| step_e_cap_reached | false | C-DCL-MIN-LOOP-ATTEMPT (rerun=0 인데 cap claim) | **FAIL** |
| rerun_count | 0 | min loop attempt | **FAIL** |
| budget_used_total | 0.20 | C-DCL-CAP-MEASURED (clock_elapsed > wall_budget?) | **FAIL** (측정 미달) |
| fallback_reason_2 | "single-pass tournament with budget BUDGET_BOUND" | C-DCL-NO-FORWARD-PROJECT (forward projection regex) | **FAIL** ("BUDGET_BOUND" + projection) |
| next_action | "45min wall makes further universe rerun infeasible" | C-DCL-NO-FORWARD-PROJECT | **FAIL** ("wall makes … infeasible") |

→ sprint-17 게이트 4 신규 모두 fail. 본 회귀가 sprint-17 의 직접 도입 동기.

## 10. 호환성

- v0.9.21 [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) — 본 컨벤션 = 그 의사코드의 *runtime enforcement layer*
- [`autonomy.md`](autonomy.md) C23 — 페이즈 04 외 인터럽트 0 정합 (자율 회귀 default, 3회 후만 ack)
- [`tournament-blind-rerun.md`](tournament-blind-rerun.md) (ad) — 조건 5 의 anonymized prev winner = ad C-TBR-ANON 재사용
- [`budget-aware-fallback.md`](budget-aware-fallback.md) (ah) — BUDGET_BOUND 시 fallback_reason 의무 정합
