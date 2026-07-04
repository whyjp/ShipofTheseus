# Phase 08 — 구현 (모듈별, 5 sub-phase TDD + multiverse + 다카포)

## 한 줄 요약

**계획의 TODO DAG 를 따라 한 TODO 당 한 구현 에이전트를 띄운다.** 5 서브페이즈 (08-α/β/γ/δ/ε) test-first 분해 + multiverse fan-out (G3=5/G4=7/G5=9 폭) + intra-phase 다카포 loop + mandatory ≥ 1 rerun.

## 매 sub-impl 후 sub-step — regression check 의무 호출 (sprint-34 v0.9.39)

5 서브페이즈 TDD 의 *implementer* (08-γ) 가 한 universe 의 코드 산출을 끝낸 *직후* + 다카포 step F (re-evaluate) 시점에 다음 명령 의무 호출:

```bash
python skills/theseus-harness/scoring/regression_check.py run \
    --root .ShipofTheseus/<프로젝트>/ --module <T-NNN> --phase 08 --trigger {impl,dacapo-step-f} \
    --test-cmd "<intent/04-verification.md 의 verification_command>" \
    --boot-cmd "<intent/04-runtime-prereq.md 의 boot_command>"
```

- exit 0 → 다음 sub-impl 진행
- exit 1 (test/boot/lint fail) → phase 08 step C (implementer) 재진입, lesson_pack 누적
- 직전 known-good 대비 회귀 의심 시 추가 호출:

```bash
python skills/theseus-harness/scoring/regression_check.py compare --root .ShipofTheseus/<프로젝트>/
# exit 0 = no regression, exit 1 = G4+ phase 11 bisect 트리거
```

`state/regression_log.json` 은 append-only — phase 11 bisect 의 입력 source. 자세한 알고리즘: [`../conventions/regression-tdd-gate.md`](../conventions/regression-tdd-gate.md).

---

## sprint-50 — Deep-Module + DRY (HARD-RULE 9.ddd / 9.eee)

> 격언:
> - Ousterhout, *A Philosophy of Software Design*, Ch.4 — *"Modules Should Be Deep"* — "A deep module is one that has a lot of functionality hidden behind a simple interface."
> - Hunt & Thomas, *The Pragmatic Programmer*, Tip 11 — *"DRY"* — "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."

### 9.ddd — Deep-Module 검사 (`scoring/deep_module_metric.py`)

각 모듈의 (public interface 줄 수) / (내부 functional 줄 수) 비율 ≤ τ=0.4 의무. *얕은 모듈* (interface ≈ implementation) 검출.

vacuous PASS 차단:
- 모듈 수 = 1 (단일 파일) = automatic fail.
- 모듈 수 < ⌈sqrt(LOC/100)⌉ = warning.

### 9.eee — DRY 검사 (`scoring/dry_violation_count.py`)

코드 token n-gram (n=8) 중복 ≥ k 회 = violation. violation 비율 ≤ τ=0.05 의무.

boilerplate 제외 catalog: `import` / `class` header / `__init__` / `if __name__ == '__main__'` / decorator / `pass` / 단독 `return` — *재사용 가능한 abstraction* 의 정상 반복은 metric-gaming 으로 카운트하지 않는다.

### CLI 의무 호출 — *§자동 CLI 호출 literal Bash* (sprint-43 패러다임)

phase 08 종료 *직전* (multiverse winner 확정 후, phase 09 진입 전) 의무 호출:

```bash
python skills/theseus-harness/scoring/deep_module_metric.py \
    --code-root <submission>/src/ \
    --max-ratio 0.4 \
    --json-out .ShipofTheseus/<프로젝트>/impl/deep_module_metric.json

python skills/theseus-harness/scoring/dry_violation_count.py \
    --code-root <submission>/src/ \
    --n-gram 8 \
    --max-violation-ratio 0.05 \
    --json-out .ShipofTheseus/<프로젝트>/impl/dry_violation.json
```

- exit 0 (둘 다) → phase 09 quality gate 진입
- exit 1 (어느 하나) → phase 08 step C (implementer) 재진입. lesson_pack 누적 (모듈 분해 또는 중복 제거).

### 다음 sprint 확장 의제 (떠안는 risk)

본 sprint 의 deep_module / dry CLI 는 Python 한정 1 차 휴리스틱. 다른 언어 (Go / TS / Rust / Java) 는 다음 sprint 후속. 본 sprint 마감 시점에서 Python 외 언어로 산출 시 invocation 시점 `--lang <name>` flag 로 **사전 위임** declare (phase 08 실행 중 추가 인터럽트 없음) = 다음 sprint 카탈로그 1 회성 추가로 반영.

## 입력

- canonical `plan/06-plan.md` (canonical-not-stub 정합 — stub 금지, sprint-37 PR-AH inline). HARD-RULE 9.a 본문 의무 8 항목 (파일 경로 / sequenceDiagram / usecase / interface / TODO DAG / 모듈 의존 / data structure invariants / test surface mapping / error handling / **implementation guidance per TODO**) 가 plan 본문에 박혀 있어야 함 — *별도 impl-design.md 신설 안 함, plan 단일 source*.
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


## §canonical 산출물 룰 (sprint-37 PR-AH inline, prev: canonical-not-stub.md)

`impl/08-impl-log.md` (canonical) 도 phase 06 §canonical 룰 동등 적용 — winner inline ≥80% 또는 shared schema 3 섹션 의무. asof_fingerprint frontmatter 의무. "80%", "shared schema", "asof_fingerprint" 키워드 본문 박힘 강제 (self_lint C-CNS).



## §08.f Prompt-trace lint (sprint-38 PR-J — 신규 sub-phase)

**phase 08 의 6번째 sub-phase (08-α/β/γ/δ/ε + 08.f).** 모든 deliverable 산출물 → originating directive 역추적 의무. 미추적 산출물 = warn or fail.

### 트리거

phase 08-ε (impl-log) 직후, phase 09 진입 *전*. impl/* 의 모든 deliverable 가 06.b directives.json 의 어느 directive 충족인지 매핑.

### 산출물 — `impl/08-prompt-trace.md`

```markdown
---
phase: "08.f"
prev_fingerprint: "P08E-..."
fingerprint: "P08F-..."
deliverables_count: <int>
mapped_count: <int>
unmapped_count: 0           # 의무 0
---

# Phase 08.f Prompt-trace

## Deliverable → Directive 매핑

| Deliverable | Module | Directives 충족 | Source |
|---|---|---|---|
| `code/truck.py` | truck | D-001 (must), D-007 (canonical) | 06-directives.json:D-001,D-007 |
| `code/loader.py` | loader | D-002 (must), D-009 (primary) | 06-directives.json:D-002,D-009 |
| `code/tests/test_truck.py` | test | D-001 (must) verification | 06-directives.json:D-001 |

## Unmapped deliverables

(부재 — unmapped_count: 0)

## Directive coverage

| Directive | Type | Deliverables 매핑 |
|---|---|---|
| D-001 | must | code/truck.py, code/tests/test_truck.py |
| D-002 | must | code/loader.py |
| D-007 | canonical | code/truck.py |
```

### 의무 체크

a- **unmapped_count: 0** — 모든 deliverable 이 ≥ 1 directive 매핑.
b- **모든 must directive 가 ≥ 1 deliverable** — must directive 가 deliverable 매핑 0 = 구현 누락.
c- **모든 canonical directive 가 정확히 1 deliverable** — canonical 정의 위치 단일.
d- **모든 primary directive 가 ≥ 1 deliverable + ≥ 1 measurement** — proxy 우회 차단.

### self_lint C-PT

```python
def check_prompt_trace(skill_root: Path) -> list[str]:
    """C-PT (sprint-38 PR-J) — phase 08.f prompt-trace."""
    issues = []
    p08 = skill_root / "phases" / "08-implement.md"
    body = p08.read_text(encoding="utf-8")
    for kw in ["§08.f", "Prompt-trace", "deliverables_count",
              "unmapped_count: 0", "Deliverable → Directive 매핑",
              "Directive coverage"]:
        if kw not in body:
            issues.append(f"phases/08-implement.md: §08.f '{kw}' 키워드 누락 (sprint-38 PR-J)")
    return issues
```

### 안티 패턴

a- **unmapped_count ≥ 1** — orphan deliverable. 의도 외 코드 가능성 또는 directive 추가 누락.
b- **must directive deliverable 매핑 0** — 구현 누락. phase 08 재진입.
c- **canonical directive 가 ≥ 2 deliverable** — single source 위반.
d- **primary directive 의 measurement 부재** — proxy metric 우회.

### 호환성

- 06.b → 08.f: directives.json 의 visibility layer 가 deliverable ↔ directive 매핑 source.
- 08.f → 09 quality gate: prompt-trace 가 phase 09 의 *intent-impl 정합* 차원 입력.
- 08.f → 14 handoff: prompt-trace 의 directive coverage 표가 handoff 의 *완료 보고* 입력.

## §자동 CLI 호출 (sprint-43 PR-E)

phase 08 종료 직전 orchestrator 의무 호출 :

```bash
# HARD-RULE 9.qq — impl 다카포 임계
python skills/theseus-harness/scoring/dacapo_threshold.py \
    --tournament-md .ShipofTheseus/<proj>/impl/tournament-impl-01.md \
    --threshold 0.999 \
    --output .ShipofTheseus/<proj>/impl/dacapo_threshold.json

# HARD-RULE 9.vv — impl universe 수 검증 (1 universe 시 7-condition 명시 의무)
python skills/theseus-harness/scoring/universe_count_monotonicity.py \
    --project-root .ShipofTheseus/<proj>/ \
    --output .ShipofTheseus/<proj>/quality/gate_universe_monotonicity_impl.json

# HARD-RULE 9.uu — phase 08 본문에 phase 06 plan + phase 04 답안 인용 ≥ 1 each
python skills/theseus-harness/scoring/cross_phase_context_audit.py \
    --project-root .ShipofTheseus/<proj>/ \
    --phase 08 \
    --output .ShipofTheseus/<proj>/quality/gate_cross_phase_context_08.json
```

본 §은 sprint-43 의 *literal Bash command* 박힘. agent 자율 skip 금지.
