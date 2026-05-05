# Da Capo mandatory rerun (`dacapo-mandatory-rerun`) — 점수 임계 도달해도 무조건 ≥ 1 rerun (sprint-19, ce, HARD-RULE 9.gg)

## 한 줄 요약

**Phase 06 / 08 의 다카포 loop 는 winner_score 가 grade 임계 (G4=0.999) 이상이라도 *최소 1 회 rerun 의무*.** "이미 충분하다 → skip" 은 자율 우회의 마지막 빈 구멍 — 본 룰이 차단. polishing pass 강제로 plan/impl detail richness 자동 확보. cold session 003 의 1-5 cold-read 19/20 단일 promote 회귀 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| sprint-15 bl Step D AND threshold | tournament_pass=true AND shadow_pass=true → CONVERGED → 즉시 promote, rerun 0 |
| sprint-16 9.o BUDGET_BOUND fallback | rerun ≥ max OR budget ≥ 95% 시만 fallback. *high score* 는 그대로 promote |
| sprint-17 9.p min loop attempt | cap claim 시 rerun ≥ 1 강제. **cap 미발동 + high score → 그대로 promote** (빈 구멍) |
| 결과 | cold 003 winner U1=19/20 = 0.95 (1-5 cold-read coarse, 0.999 임계와 무관) → rerun=0 → polishing 0 |

→ 모든 sprint-15~17 enforcement 가 *high score* 시 promote 를 허용. 본 sprint 가 그 마지막 구멍 닫음.

## 트리거

Phase 06 (plan) / Phase 08 (impl) 의 Da Capo loop. Step D AND threshold 통과해도 **rerun_count < 1 이면 promote 거부 + Step F (lesson 도출) + Step G (anonymized prev winner + width-1 fresh) → Step A 재진입**.

## 변경 — Step D AND check 정정

```
sprint-15 bl 원형:
  if tournament_pass AND shadow_pass:
    → CONVERGED → promote

sprint-19 정정:
  if tournament_pass AND shadow_pass:
    if rerun_count >= 1:
      → CONVERGED → promote
    else:
      → MANDATORY_FIRST_RERUN → Step F + G + Step A 재진입
      (예외 0 — high score 도 무조건 1 회 polishing)
```

## 의무 산출물 (예외 0)

| 파일 | rerun_count == 0 | rerun_count >= 1 |
|---|---|---|
| `tournament-NN.md` (≥ 2 개) | **fail** | OK |
| `dacapo-rerun-01.md` 본문 ≥ 1 lesson | **fail** | OK |
| `shadow-grade-NN.json` (≥ 2 개) | **fail** | OK |
| anonymized previous winner | **fail** | OK |
| `dacapo-flow.md` Step G subgraph | **fail** | OK |

→ 단일 tournament.md + rerun=0 + promote = 본 룰 위반. self_lint C-DCMR 가 강제.

## frontmatter (tournament-NN.md)

```yaml
mandatory_first_rerun_satisfied: true   # rerun_count >= 1 의무
mandatory_first_rerun_lesson: "..."     # 1st rerun 에서 도출한 lesson 1 줄
```

## self_lint C-DCMR

컨벤션 파일 존재 + 페이즈 06/08 본문 "mandatory-rerun" + "rerun_count >= 1" + "예외 0" 명시.

## 안티 패턴

a- "winner score 0.999 이상 + step_d_*_pass: true → 즉시 promote" — sprint-19 차단.
b- `mandatory_first_rerun_satisfied: true` 거짓 박기 — `dacapo-rerun-01.md` 파일 존재 + 본문 lesson ≥ 1 줄 cross-validation.
c- 1-5 cold-read coarse scoring 으로 high score 가장 (예 19/20 = 0.95) — `plan-tournament-scoring-strict.md` (cf) 가 6-dim weighted 강제로 차단.
d- rerun 1 회 후 lesson 본문이 빈 (placeholder) — `dacapo-rerun-01.md` 본문 ≥ 30 byte + frontmatter `lesson_applied` non-empty 의무.

## cold session 003 검증

`plan/tournament.md`:
- `multiverse_width: 4`
- 1-5 × 4 dims = U1 winner 19/20
- `dacapo_loop_executed`/`step_d_*_pass`/`rerun_count`/`fallback_reason` 모두 부재
- `dacapo-rerun-*.md` 0
- → sprint-19 게이트 적용 시 5 조건 모두 fail. mandatory rerun 강제 → Step F lesson 도출 (e.g., "U1 의 inflight-blind dispatch 갭 → universe-1' 추가 axis: queue-aware dispatch") → Step G anonymized U1' 재 fan-out → Step A 재진입. rerun=1 후 promote 가능.

## 호환성

- [`dacapo-enforcement.md`](dacapo-enforcement.md) (bm) — 본 룰은 9.p 게이트의 6 조건 + 1 추가 조건 (mandatory_first_rerun_satisfied).
- [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) — Step D 분기 정정 (CONVERGED 직진 → MANDATORY_FIRST_RERUN 분기 추가).
- [`tournament-blind-rerun.md`](tournament-blind-rerun.md) (ad) — anonymized prev winner 의무는 그대로.
