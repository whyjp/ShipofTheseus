# Intent refresh post critique (`intent-refresh-post-critique`) — phase 05 후 2nd refresh + 04/05 cascade (sprint-19, ci, HARD-RULE 9.kk)

## 한 줄 요약

**Phase 05 critique 종료 직후 ~ phase 06 plan 진입 *전* 에 *2nd intent refresh* (사용자 인터랙션 없음, 페이즈 04 외 인터럽트 0 정합) + 04/05 doc cascade re-write 의무.** sprint-17 by ([`intent-refresh-post-interview.md`](intent-refresh-post-interview.md)) 가 04 → 05 사이 1 회 refresh 만 — critique 가 새로 드러낸 갭이 plan 으로 흐르지 못한 채 끝남. 사용자 직접 지적: "04-05 이후 다시한번 intent 리프레쉬 및 사용자 인터렉션 없는 intent 리프레쉬 이후의 04/05 문서 리프레쉬".

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| sprint-17 by 1 회 refresh 한정 | 04 인터뷰 후 4 framing universe + 01-additional 만, critique 산출물 흡수 cycle 부재 |
| critique 산출물 → plan 직진 | cold 003 의 05-decisions.md (2393 byte) 에서 06-plan.md 직진. critique 가 드러낸 "decision_coverage" 갭 등 plan 진입 전 흡수 안 됨 |
| 04/05 doc 가 *최초 작성* 그대로 | critique 후 04 답변 / 05 결정 의 framing 갱신 부재 → plan 이 stale 입력 위 동작 |

## 트리거

Phase 05 critique 산출물 (`intent/05-critique.md` + `intent/05-decisions.md`) 완성 직후, phase 06 plan 진입 *전*. **자동 — 사용자 ack 없음** (페이즈 04 외 인터럽트 0 정합).

## 의무 산출물 (5 신규)

```
intent/
├─ 01-1-intent.v2.md       universe-1 v2 — domain-paradigm + critique-absorbed
├─ 01-2-intent.v2.md       universe-2 v2 — constraint-paradigm + critique-absorbed
├─ 01-3-intent.v2.md       universe-3 v2 — risk-paradigm + critique-absorbed
├─ 01-4-intent.v2.md       universe-4 v2 — outcome-paradigm + critique-absorbed
└─ 04-refreshed.md         04 answers / decisions / autonomy / stack 통합 v2 (critique-absorbed cascade)
└─ 05-refreshed.md         05 critique / decisions 통합 v2 (mismatch resolved against v2 framing)
```

**6 신규 산출물** (4 universe v2 + 04-refreshed + 05-refreshed). 각 frontmatter:

```yaml
---
phase: "05+"                                  # phase 05 와 06 사이
phase_name: intent-refresh-post-critique
universe: 1                                   # 01-{1..4}-intent.v2.md 만
framing: domain-paradigm                      # 01-{1..4} 만
fingerprint: "P05R-uniN-..."
prev_fingerprint: "P05-decisions-..."
created_at: "..."
critique_findings_consumed: ["05-critique.md", "05-decisions.md"]
intent_v1_supersedes: ["01-1-intent.md", ..., "01-additional.md"]
contradicts_v1: <bool>                        # v1 의도와 모순 여부
contradiction_dims: [...]                    # 모순 차원
---
```

## 자동 reject 패턴

다음 detect 시 fail:
- 6 산출물 중 ≥ 1 누락
- v2 본문이 v1 본문 그대로 복붙 (diff < 50 byte)
- `critique_findings_consumed` frontmatter 부재 또는 05-* 미인용
- phase 06 plan 의 `prev_fingerprint` 가 `P05-decisions-*` 직접 인용 (sprint-19 시 `P05R-*` 인용 의무)

## phase 06 plan 진입 게이트 갱신

```python
for u in [1, 2, 3, 4]:
    if not (intent_dir / f"01-{u}-intent.v2.md").exists():
        raise SkillEntryError(f"intent/01-{u}-intent.v2.md 부재 — phase 05+ refresh 미완료. intent-refresh-post-critique.md 의무.")
if not (intent_dir / "04-refreshed.md").exists():
    raise SkillEntryError("intent/04-refreshed.md 부재 — phase 05+ cascade re-write 미완료.")
if not (intent_dir / "05-refreshed.md").exists():
    raise SkillEntryError("intent/05-refreshed.md 부재 — phase 05+ cascade re-write 미완료.")
```

## self_lint C-IRPC

컨벤션 파일 존재 + 페이즈 05 본문 "intent-refresh-post-critique" + 6 산출물 명시 + 페이즈 06 plan 진입 게이트 갱신 명시.

## 안티 패턴

a- phase 04 → 05 1 회 refresh (sprint-17 by) 만으로 충분하다 가정 — sprint-19 차단. critique 가 드러낸 갭은 *post-05 cascade* 로만 흡수 가능.
b- v2 산출물 본문이 v1 본문 그대로 복붙 — diff threshold (≥ 50 byte 또는 ≥ 5% 변경) 강제.
c- `intent_v1_supersedes` 부재 → cascade 추적 불가.
d- 사용자 ack 시도 — phase 04 외 인터럽트 0 정합. 자율로만 진행.

## cold session 003 검증

`intent/05-decisions.md` (2393 byte) 직후 `plan/tournament.md` 진입.
- 04-05 사이 refresh 1 회 (sprint-17 by) 완료
- 05 → 06 사이 refresh 부재 (sprint-19 본 룰 부재로 자연 skip)
- critique 가 드러낸 "ramp_upgrade vs baseline 1% 미만" 같은 outcome-paradigm 인사이트 → 06 plan 의 decision_coverage 차원 sub_score 0.85 (gap)
→ sprint-19 게이트 적용 시 6 산출물 강제 → critique 인사이트 흡수 → plan decision_coverage 차원 사전 보강.

## 호환성

- [`intent-refresh-post-interview.md`](intent-refresh-post-interview.md) (by) — sprint-17 의 1st refresh. 본 룰 = 2nd refresh cycle.
- [`autonomy.md`](autonomy.md) — 페이즈 04 외 인터럽트 0 정합 (사용자 ack 없음).
- [`contracts.md`](contracts.md) — fingerprint chain (05 → 05+ → 06).
- [`cross-phase-shared-context.md`](cross-phase-shared-context.md) (cj) — 04-refreshed.md / 05-refreshed.md 가 phase 06 plan 의 입력 source.
