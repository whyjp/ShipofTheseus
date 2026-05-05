# Da Capo Enforcement — 의사코드 → 강제 게이트 변환 (sprint-16 / v0.9.22)

## 한 줄 요약

**v0.9.21 [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) 의 의사코드는 *문서 가이드*. 본 컨벤션은 그 의사코드를 *runtime guard* 로 격상.** Da Capo Loop 의 Step A-G 가 단순 권고가 아니라 phase 06 → 07 / phase 08 → 09 핸드오프 시점의 *의무 게이트* 로 강제. 외부 cold session `2026-05-05__001_mine_g4` 에서 winner=0.892 (G4 임계 0.999 미달) 이 dacapo loop 0회 실행 후 phase 07 진입한 회귀의 직접 원인 정정.

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
>    OR (rerun_count >= max_rerun(grade) OR budget_used >= 0.95)
>      AND `fallback_reason` 본문 ≥ 1 줄 → BUDGET_BOUND
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

    # 조건 3b — BUDGET_BOUND 경로
    rerun = fm.get('rerun_count', 0)
    max_rerun = MAX_RERUN[grade]   # G3=2 / G4=3 / G5=5
    budget_used = fm.get('budget_used_total', 0.0)

    if rerun >= max_rerun OR budget_used >= 0.95:
        if not (artifact_dir / 'plan/fallback-reason.md').exists():
            return REJECT('BUDGET_BOUND 인데 fallback-reason.md 부재')
        if (artifact_dir / 'plan/fallback-reason.md').read_text().strip() == '':
            return REJECT('fallback-reason.md 본문 비어있음')
        # 조건 4
        rerun_logs = list((artifact_dir / 'plan').glob('dacapo-rerun-*.md'))
        if len(rerun_logs) != rerun:
            return REJECT(f'dacapo-rerun-NN.md {len(rerun_logs)} != rerun_count {rerun}')
        # 조건 5
        if not has_anonymized_previous_winner(artifact_dir, rerun):
            return REJECT('anonymized previous winner 부재 (ad C-TBR-ANON)')
        return ACCEPT('BUDGET_BOUND')

    # 조건 1-3 통과 못 함 — 의사코드 미완 실행
    return REJECT(
        f'winner_score={fm["winner_score"]} < threshold + rerun_count={rerun} < max_rerun '
        f'+ budget={budget_used} < 0.95 — Step F/G skip detected'
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

## 9. cold session 검증

`2026-05-05__001_mine_g4/plan/tournament.md` 재검증 :

| frontmatter 필드 | 값 | 게이트 조건 | 판정 |
|---|---|---|---|
| dacapo_loop_executed | (부재) | 조건 1 | **FAIL** |
| step_d_tournament_pass | (부재) | 조건 2 | **FAIL** |
| step_d_shadow_pass | (부재) | 조건 2 | **FAIL** |
| winner_score | 0.892 | 조건 3a (>= 0.999) | FAIL |
| rerun_count | (부재) | 조건 3b (>= 3) | FAIL |
| fallback_reason | "" | 조건 3b 본문 ≥ 1 줄 | **FAIL** |

→ 5 조건 모두 미달. v0.9.22 게이트 적용 시 phase 07 진입 *자동 거부* + phase 06 재진입.

## 10. 호환성

- v0.9.21 [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) — 본 컨벤션 = 그 의사코드의 *runtime enforcement layer*
- [`autonomy.md`](autonomy.md) C23 — 페이즈 04 외 인터럽트 0 정합 (자율 회귀 default, 3회 후만 ack)
- [`tournament-blind-rerun.md`](tournament-blind-rerun.md) (ad) — 조건 5 의 anonymized prev winner = ad C-TBR-ANON 재사용
- [`budget-aware-fallback.md`](budget-aware-fallback.md) (ah) — BUDGET_BOUND 시 fallback_reason 의무 정합
