# Phase 08 — 구현 (모듈별, 5 sub-phase TDD + multiverse + 다카포)

## 한 줄 요약

**계획의 TODO DAG 를 따라 한 TODO 당 한 구현 에이전트를 띄운다.** 5 서브페이즈 (08-α/β/γ/δ/ε) test-first 분해 + multiverse fan-out (G3=5/G4=7/G5=9 폭) + intra-phase 다카포 loop + mandatory ≥ 1 rerun.

## 입력

- canonical `plan/06-plan.md` ([`../conventions/canonical-not-stub.md`](../conventions/canonical-not-stub.md) cg 정합 — stub 금지). HARD-RULE 9.a 본문 의무 8 항목 (파일 경로 / sequenceDiagram / usecase / interface / TODO DAG / 모듈 의존 / data structure invariants / test surface mapping / error handling / **implementation guidance per TODO**) 가 plan 본문에 박혀 있어야 함 — *별도 impl-design.md 신설 안 함, plan 단일 source*.
- `intent/01-{1..4}-intent.v2.md` + `04-refreshed.md` + `05-refreshed.md` (refresh 2 cycle 결과).

## 5 sub-phase TDD test-first 분해

페이즈 08 은 *한 sub-agent 가 코드 + 테스트 + 실행을 동시 진행* 하면 test-first 위반. 5 서브페이즈 강제 분해:

| 서브페이즈 | 책임 | sub-agent | 산출물 | 게이트 |
|---|---|---|---|---|
| **08-α scope** | atomic / group / functional 3 계층 test scope 정의 | test-architect (Sonnet) | impl/08-test-scope.md | scope 분리 ≥ 3 계층 |
| **08-β test (RED)** | test-first writer — 테스트만 작성, 구현 0 | test-writer (Sonnet) | code/tests/* | 모든 테스트 RED (right reason) |
| **08-γ impl (GREEN)** | 통과 최소 구현 | implementer (Sonnet/Opus) | code/<modules>/*.py + .sh + .bat 빌드 스크립트 + 산출물 emit | 모두 GREEN |
| **08-δ refactor** | DRY/SOLID 정리 + docstring + type hint | refactorer (Sonnet) | code/* 수정 | GREEN 유지 |
| **08-ε log** | impl-log 작성 | implementer (Sonnet) | impl/08-impl-log.md | TODO ID 매핑 ≥ 3 + 모듈명 + 인터페이스 노출 |

skip 자백 ("production code holistically before tests" / "tight budget" 등) regex reject ([`../conventions/impl-multiverse-strict.md`](../conventions/impl-multiverse-strict.md) ch 정합).

## Multiverse fan-out + 다카포 loop (universe 별 5 서브페이즈 head-to-head)

```
Step A. universe 별 implementer 호출 (G3=5/G4=7/G5=9 폭)
    각 universe 가 plan canonical 의 implementation guidance 를 *서로 다른 implementation* 으로 풀어 5 sub-phase TDD 진행
    artifact: impl/candidates/universe-N/{code, tests, 08-impl-log}

Step B. tournament — universe 별 6-dim weighted (SOLID/dead-code/magic-number/reproducibility/portability/test-coverage)

Step C. shadow grade (zero-context, [`../conventions/shadow-grader-zero-context.md`](../conventions/shadow-grader-zero-context.md) bo 정합)

Step D. 4 conjunction AND threshold + mandatory_first_rerun_satisfied ([`../conventions/dacapo-mandatory-rerun.md`](../conventions/dacapo-mandatory-rerun.md) ce 정합)

Step E. cap check (측정 only, forward projection 금지, [`../conventions/dacapo-enforcement.md`](../conventions/dacapo-enforcement.md) bm 정합)

Step F. lesson 도출 + winner 갱신

Step G. Da Capo — anonymized prev winner + width-1 fresh universes 재 fan-out → Step A 재진입 (universe 변경 — 부분 재진입 금지)
```

## RULE 9.p):

```
1- frontmatter dacapo_loop_executed: true
2- step_d_tournament_pass + step_d_shadow_pass 명시
3- CONVERGED OR (cap 도달 + fallback-reason 본문 ≥ 1 줄)
4- rerun_count ≥ 1 시 dacapo-rerun-NN.md 갯수 == rerun_count
5- rerun_count ≥ 1 시 anonymized previous winner
6- impl/dacapo-flow.md (Mermaid + timeline) 의무 ([`../conventions/dacapo-flow-trace.md`](../conventions/dacapo-flow-trace.md) bq 정합)
```

## 의무 산출물

```
impl/
├── candidates/universe-{1..N}/        실 코드 + 테스트 (multiverse-impl-fan-out ag 정합)
│   ├── <모듈>.py / .go / .ts
│   ├── tests/
│   └── 08-impl-log.md (per universe)
├── 08-test-scope.md                   (08-α scope, ≥ 3 계층)
├── tournament-impl-NN.md              (≥ 1, mandatory_first_rerun)
├── shadow-grade-impl-NN.json
├── dacapo-rerun-NN.md                 (≥ 1)
├── dacapo-flow.md                     (Mermaid + timeline)
└── 08-impl-log.md                     (canonical, ≥ winner 80% inline 또는 shared schema, cg 정합)
```

## 핸드오프 게이트 (페이즈 08 → 09)

- impl-multiverse-strict (ch) 7 조건 PASS
- mandatory_first_rerun_satisfied: true (ce)
- canonical 08-impl-log.md (cg) — winner inline 또는 shared schema mode
- dacapo gate 6 조건 (bm)

## 안티 패턴

a- "TODO: 테스트는 나중에" — 코드 + 테스트 동반 출하 의무.
b- skipped / `.only` 테스트 금지.
c- 본인 TODO 모듈 외 편집 금지.
d- universe 별 implementer 가 다른 universe 코드 인용 — head-to-head cycle 격리 위반.
e- single-pass tournament + rerun=0 → mandatory_first_rerun_satisfied 위반.
