# Impl multiverse strict (`impl-multiverse-strict`) — phase 08 G4+ 멀티버스 의무 강제 (sprint-19, ch, HARD-RULE 9.jj)

## 한 줄 요약

**Phase 08 G4+ 의 `impl/candidates/universe-N/` 디렉터리 + `impl/tournament-impl-NN.md` + `impl/dacapo-flow.md` 모두 의무.** 단일 `impl/08-impl-log.md` 만으로 phase 09 진입 자동 거부. cold session 003 의 phase 08 단일 doc + multiverse 0 회귀 직접 정정 — [`multiverse-impl-fan-out.md`](multiverse-impl-fan-out.md) (ag) + [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) phase 08 부분의 *runtime gate* 추가.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| ag (multiverse-impl-fan-out) prose 만 | 컨벤션 본문에 "universe N 모두 실 코드 의무" 적혀있으나 *runtime gate* 부재 — agent skip 가능 |
| bl (intra-phase-dacapo-loop) phase 08 부분 prose 만 | step A-G 의사코드 phase 08 본문에 박혀있으나 9.p 게이트가 phase 06 만 검사, phase 08 검사 누락 |
| cold session 003 결과 | impl/08-impl-log.md 단일 3691 byte. impl/candidates/ 0. impl/tournament-impl-*.md 0. impl/dacapo-flow.md 0. 자백: "08-2 red: skipped because production code was written holistically before tests" |

→ phase 08 가 *full TDD multiverse 우회* 한 채 phase 09 진입.

## 의무 — phase 08 → 09 핸드오프 7 조건 게이트

```
1- impl/candidates/universe-1/, universe-2/, ..., universe-N/ 디렉터리 존재
   N == multiverse_width (G3=5/G4=7/G5=9 default)
   각 디렉터리 본문 ≥ 1 (placeholder 금지)
2- impl/tournament-impl-NN.md frontmatter 6-dim weighted (cf plan-tournament-scoring-strict 정합)
3- impl/shadow-grade-impl-NN.json (be 정합)
4- impl/08-impl-log.md (canonical, canonical-not-stub cg 정합 — winner inline 또는 shared schema)
5- impl/dacapo-flow.md (bq dacapo-flow-trace 정합 — phase 08 view)
6- mandatory_first_rerun_satisfied: true (ce dacapo-mandatory-rerun 정합 — rerun_count >= 1 의무)
7- 5 sub-phase TDD trace (08-1 plan-to-code / 08-2 red / 08-3 green / 08-4 refactor / 08-5 invariants) 본문 + 각 sub 별 ≥ 5 줄 본문 (skip 자백 금지)
```

미달 시 phase 09 진입 자동 거부 + `intent/00-violation.md` 기록 + phase 08 Step A 부터 재진입.

## 자동 reject 패턴

다음 자백 패턴 regex detect 시 fail:
- `(skipped|skip).*(test|red|TDD|production code .* holistically before tests|tight budget)` 류
- `08-2 red.*passed on first execution`
- 단일 universe 만 작성 + tournament 부재

## self_lint C-IMS

컨벤션 파일 존재 + 페이즈 08 본문 "impl-multiverse-strict" + "7 조건" + "phase 09 진입 자동 거부" + `08-implement.md` v0.9.24 절 명시.

## 안티 패턴

a- "tight 45-min budget 으로 phase 08 multiverse skip" — sprint-19 차단. budget 부족 시 multiverse_width fallback (ag width-1 + budget-aware-fallback ah) 으로 진행, *완전 skip 금지*.
b- impl/candidates/ 디렉터리만 만들고 06-plan.md 빈 placeholder — 본문 ≥ 1 KB 의무.
c- 5 sub-phase TDD 자백 ("production code written holistically before tests") — RED-GREEN-REFACTOR 정합 강제. test 가 production 보다 먼저 작성된 git history 또는 sub-phase 명시 의무.
d- impl tournament 1-5 cold-read coarse — cf plan-tournament-scoring-strict 가 phase 08 도 적용 (6-dim weighted).

## cold session 003 검증

`impl/08-impl-log.md`:
- 3691 byte 단일 doc
- `impl/candidates/` 디렉터리 부재
- `impl/tournament-impl-*.md` 0
- `impl/dacapo-flow.md` 0
- 본문 자백: "08-2 red: ... skipped because production code was written holistically before tests (acceptable for tight 45-min budget)"
- "08-4 refactor: ... skipped for budget"
→ sprint-19 게이트 적용 시 7 조건 모두 fail. phase 08 Step A 재진입 강제 + RED-GREEN-REFACTOR 5 sub-phase 본문 ≥ 5 줄 + multiverse_width fallback.

## 호환성

- [`multiverse-impl-fan-out.md`](multiverse-impl-fan-out.md) (ag) — 본 룰 = ag 의 *runtime gate* layer.
- [`intra-phase-dacapo-loop.md`](intra-phase-dacapo-loop.md) (bl) — phase 08 부분의 게이트 강제.
- [`dacapo-mandatory-rerun.md`](dacapo-mandatory-rerun.md) (ce) — phase 08 rerun_count >= 1 의무.
- [`dacapo-flow-trace.md`](dacapo-flow-trace.md) (bq) — `impl/dacapo-flow.md` per-phase view 의무.
- [`canonical-not-stub.md`](canonical-not-stub.md) (cg) — `impl/08-impl-log.md` 가 stub 금지.
