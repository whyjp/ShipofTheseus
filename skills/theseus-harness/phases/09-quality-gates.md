# Phase 09 — 9종 품질 게이트 + runtime enforcement

## 첫 동작 — run_gate.py 커널 게이트 러너 의무 호출 (HARD-RULE 9.f, the-gate)

phase 06/08 종료 → phase 09 진입 *직전* 다음 명령 의무 호출 (설계:
[`../../../docs/design/2026-07-05-B1-kernel-wiring-design.md`](../../../docs/design/2026-07-05-B1-kernel-wiring-design.md) §2/§3.1):

```bash
python skills/theseus-harness/scoring/run_gate.py \
    --project-root .ShipofTheseus/<프로젝트>/ --grade <G> \
    --submission <submission>/ --test-target <submission>/tests/ --phase-upto 09
```

- exit 0 → `quality/gate_meta_audit.json` verdict `pass` — 이하 §존치 게이트(게이트 6~9 +
  runtime 검증 layer + RTG + Methodology-Completeness + §V8) 진행.
- exit 1 → verdict `fail`. `gate_meta_audit.json` 의 `failed[]` 를 remediation TODO
  (`T-NNN-fix`) 로 phase 08 step C 에 폴드백 후 phase 09 재진입.
- exit 2 → 러너 자체 크래시(verdict 미산출 — 통과 아닌 별도 실패). phase 09 halt + 진단.

종합 판정 = **meta_audit verdict(pass 의무) AND 존치 게이트 전부 pass** — 판정의 *소스*가
prose 정적 게이트에서 커널로 교체됐다(§3.2 마이그레이션 표). run_gate 가 내부적으로
producer 13종 → meta_audit 오케스트레이션을 수행한다. 옛 `check_cold_session.py` 의
sentinel-regex/파일-개수 검사(prose-only enforcement 의 근본 우회 패턴, P3)는
`plan.dacapo_threshold` / `plan.tournament_independence` / `cold.isolation` 값 기반
CheckSpec 로 대체 — **스크립트 자체는 존치**(`producers/measure_cold_isolation.py` 가
`check_cold_session.build_report()` 를 라이브러리로 실 import, grep 실측 확인). 은퇴한
것은 phase 09 의 *CLI 의무 호출 한 줄* 뿐이다.

## runtime 검증 layer (90→100 cap 풀기)

bs/bt/bu/bv/bw/bx (HARD-RULE 9.v~aa) 가 *내용 의무*, 본 5 게이트가 *runtime 검증* — 두 layer 결합 시 enforcement 닫힘. **도메인 종속 룰 의도적 제외** — 본 하네스는 벤치 어뷰징 안 함.

| 게이트 | 컨벤션 | 알고리즘 (요약) |
|---|---|---|
| **G-RNFS** ([`../conventions/readme-numbers-from-summary.md`](../conventions/readme-numbers-from-summary.md)) | bz · 9.bb | doc grep `\b[0-9]+\.[0-9]+\b` + measurement artifact key 매핑 → ±0.01% 일치 |
| **G-RDC** ([`../conventions/reproducibility-doublecheck.md`](../conventions/reproducibility-doublecheck.md)) | ca · 9.cc | entry script 2회 실행 + sha256 byte-equal assert (PYTHONHASHSEED 회귀 차단). **sprint-40 강화 — *별도 subprocess invocation* 의무 + `quality/gate_v6_reproducibility.json` evidence 필수 emit. 본문 attestation 만으로는 통과 불가 (§V6-Evidence-Bound 본문 절 참조).** [`../conventions/cross-process-anti-patterns.md`](../conventions/cross-process-anti-patterns.md) 카탈로그 grep 자동 검사. |
| **G-MNT** ([`../conventions/magic-number-traceability.md`](../conventions/magic-number-traceability.md)) | cb · 9.dd | 모든 code literal → A_i 가정 또는 데이터 파일 출처 1:1 매핑 (programming constants 0/1/2/60/100/1024/3600 제외) |
| **G-DCZ** ([`../conventions/dead-code-zero.md`](../conventions/dead-code-zero.md)) | cc · 9.ee | 언어별 dead-code analyzer 위반 0 (Python: `ruff check --select F,ARG,SIM` 또는 `vulture`. 다른 언어는 [`../conventions/polyglot-code-quality.md`](../conventions/polyglot-code-quality.md) au 표 참조) |
| **G-SPB** ([`../conventions/submission-portability.md`](../conventions/submission-portability.md)) | cd · 9.ff | entry script grep — `Path(__file__).parent.parent` 등 path 하드코딩 detect → fail. `--data-dir` CLI + `DATA_DIR` env fallback 의무 |

각 게이트 fail 시 :
- `quality/09-quality-gate.md` frontmatter 에 `<gate_id>_pass: false` + `<gate_id>_violations: [...]` 박힘
- 페이즈 09 종합 판정 = halt (수정 후 재진입 강제)
- 페이즈 14 handoff 의 `lessons:` 에 자동 추가

---

## sprint-50 — Comments-Why (HARD-RULE 9.ggg) + Define-Errors-Out 커널 이관 (9.fff)

> 격언:
> - Ousterhout, *A Philosophy of Software Design*, Ch.10 — *"Define Errors Out of Existence"*
> - Ousterhout, Ch.13 — *"Comments Should Describe Things That Are Not Obvious from the Code"*

### 9.fff — Define-Errors-Out (커널 이관, phase 09 자체 CLI 호출 은퇴)

`quality.define_errors` CheckSpec(producer `measure_define_errors`, WP5 승격 완료)이 위
§첫 동작의 run_gate 호출 안에서 이미 측정한다(raise catalog ≥ 1 + handle 의무 + bare
except only fail — 알고리즘 동일). `define_errors_check.py` 는 producer 가 `build_report()`
를 라이브러리로 직접 import 하므로 스크립트 존치 — 은퇴한 것은 phase 09 의 개별 CLI 호출뿐.

### 9.ggg — Comments-Why-Not-What 검사 (`scoring/comment_intent_check.py`, 존치)

comment 와 *바로 다음 코드 줄* 의 token Jaccard overlap ≥ 0.5 = paraphrase. paraphrase 비율 ≤ τ=0.5 의무.

vacuous PASS 차단:
- sentinel marker (`# why:` / `# 이유:`) 가 escape — *그러나* 전체 comment 중 escape ≥ 80% = 의심 fail (escape 만 사용 우회 차단).
- comment 수 < 5 = 검사 skip (small codebase).

producer 미존재(승격 후보) — CLI 게이트로 존치. phase 09 종합 판정 *직전* 의무 호출:

```bash
python skills/theseus-harness/scoring/comment_intent_check.py \
    --code-root <submission>/src/ \
    --max-paraphrase-ratio 0.5 \
    --max-escape-ratio 0.8 \
    --json-out .ShipofTheseus/<프로젝트>/quality/comment_intent.json
```

- exit 0 → phase 10 sprint loop 진입
- exit 1 → phase 08 step C implementer 재진입 (comment 의도 수정).

## 한 줄 요약
**테스트 실행 전에 아홉 게이트로 *코드 모양 + 실행 가능성 + 프로세스 정합 + 도메인 결손 부재* 를 감사한다.** 게이트 1~5 = 정적 모양, 게이트 6 = NFR 측정, **게이트 7 = env-satisfied + 실 부팅 1회** ([`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md), v0.7.0), **게이트 8 (v0.9.18) = process flow / cycle coherence**, **게이트 9 (v0.9.18) = domain failure patterns 자기 검증**.

## 9 정적 게이트 + N derived 게이트 (v0.9.18)

총 게이트 수 = `static_gates_9 ∪ derived_gates(NFR_answers)`. NFR 0 = derived 0 = static 9. NFR 5 = derived 5 추가 = 14 게이트.

### 정적 게이트 (9)

**게이트 1~5 는 커널 verdict 가 판정한다** (§첫 동작의 run_gate 호출 — meta_audit 이
CheckSpec 을 producer evidence 로 재검사, prose 정적 판독 아님). 아래 표의 "무엇을 보는가"
열은 대체된 커널 체크 id 참조로 강등 — 상세 producer/schema 는
[`docs/design/2026-07-05-judgment-gate-producers-design.md`](../../../docs/design/2026-07-05-judgment-gate-producers-design.md) §3.

| # | 게이트 | 커널 체크 id (run_gate 판정) | fail 신호 |
| - | ----- | ------------ | -------- |
| 1 | **의도 일치** | `scoring.correctness` (intent_fidelity — `intent/01-intent-criteria.json` 기계 재검사) | criterion backing 불충족 |
| 2 | **범위 규율** | `scoring.scope_fit` (files_mapped_to_todos ≤ files_touched) | TODO 가 인가하지 않은 파일 변경 |
| 3 | **SOLID** | `scoring.solid` (modules_passing_solid · dip_violation, `impl/08-solid-contract.json` 재검사) | 거짓 claim 실 FAIL 관측 |
| 4 | **테스트 모양** | `scoring.correctness`(tests) + `scoring.coverage` + `scoring.e2e` | public 함수에 테스트 없음, coverage/e2e 결손 |
| 5 | **FE/BE 패리티** | `scoring.fe_be_parity` (applicability: fe_side_exists) | BE 80% 커버리지 + FE 스냅샷만 |
| 6 | **NFR 명시 임계 일치** (존치 — producer 화 후속) | `intent/01-intent.md` §d 의 ✅ NFR 항목별 페이즈 10 측정 결과 — [`../conventions/spec-catalog.md`](../conventions/spec-catalog.md) | p99/가용성/LCP 임계 미달. ⏸ 항목 skip |
| 7 | **env-satisfied + 실 실행 1회** ([`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md), v0.7.0) | env / 부팅 / healthz 검증 |
| 8 | **Process flow / cycle coherence** ([`../conventions/process-flow-coherence.md`](../conventions/process-flow-coherence.md), v0.9.18) — 작업이 process 차원 (workflow / state machine / DES / pipeline / transaction) 이면 활성. `process_flow_applicable: false` 시 skip | all_states_reachable / all_terminal_reachable / no_orphan_states / cycle_invariant_holds / error_paths_explicit / state_visit_count > 0 |
| 9 | **Domain failure patterns 자기 검증** ([`../conventions/domain-pack.md`](../conventions/domain-pack.md) §4, sprint-37 PR-AG 통합) — 작업 도메인 추정 후 [`../conventions/domain-adapters/<domain>.md`](../conventions/domain-adapters/) 의 `failure_patterns:` 모든 항목 자동 검증. 매칭 어댑터 없으면 skip + 명시 | DFP-* 패턴 매칭 시 severity 별 cap (cap_total / cap_correctness / cap_experimental / cap_results / warning) |

### Derived 게이트 (NFR-V 답안 종속, v0.9.6) — [`../conventions/nfr-derivation.md`](../conventions/nfr-derivation.md)

페이즈 01 의 §i "Derived NFRs" + 페이즈 04 의 NFR-V 답안 (`intent/04-nfr-verifications.md`) 으로부터 자동 생성:

```python
# pseudo-code in agents/quality-gate.md
def derived_gates(nfr_verifications: list[NFRAnswer]) -> list[Gate]:
    gates = []
    for ans in nfr_verifications:
        if ans.option == 4:   # N/A
            continue
        gates.append(Gate(
            id=f"DG-{ans.nfr_id}-V{ans.option}",
            check=ans.verification_protocol,  # 페이즈 04 답안 본문
            on_fail=ans.fail_policy,           # auto-fix-trigger | truthful-record
            evidence_path=ans.evidence_path,
        ))
    return gates
```

각 derived gate 의 fail 처리 = 본 페이즈가 결정 안 함 — 페이즈 04 답안에 종속:

a- `auto-fix-trigger` — fail 시 페이즈 08 의 fix-TODO 자동 생성 (Q-D1 회귀 자율과 정합).
b- `truthful-record` — fail 시 산출물 (run_metrics.json 또는 동등) 에 정직 기록 + 게이트 통과 (단, 차원 점수 cap 0.95). 외부 채점에 정직 노출 차원 +1pt 보상 가능.

### 게이트 수 동적성 검증

a- 본 페이즈의 `quality/09-quality-gate.md` 산출물에 `static_gates: 7` + `derived_gates: N` + `total: 7+N` 명시.
b- self_lint C42 (v0.9.6 신규) 가 페이즈 01 §i NFR 갯수 와 페이즈 09 `derived_gates` 갯수 일치 검증 — 누락 시 자동 fail.

## 입력
- `intent/01-intent.md`, `intent/04-answers.md`, `intent/05-decisions.md`
- `plan/06-plan.md`, `impl/08-impl-log.md`
- 디스크 위 실제 코드 — 에이전트는 로그 믿지 말고 파일 Read.

## 서브에이전트
[`../agents/quality-gate.md`](../agents/quality-gate.md).

## 산출물
`quality/09-quality-gate.md`:

a- 게이트마다 `pass` | `fail` + 증거 (`경로:라인` 인용).
b- fail 마다 remediation TODO (`T-NNN-fix`) — 계획에 폴드백.
c- 종합 판정: `proceed` | `remediate-then-proceed` | `halt`.

## 헤더 시간 정보 검증

각 페이즈 산출물 헤더에 [`../conventions/timing.md`](../conventions/timing.md) 의 시간 메타가 빠지면 자동 fail (게이트 1 의 일부).

## 지휘자 후속

a- `proceed` → 페이즈 10.
b- `remediate-then-proceed` → 페이즈 08 을 fix-TODO 만 재실행 → 페이즈 09 재실행.
c- `halt` → 사용자 질의. 구조적 문제.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).

## Rubric-Targeted Gates + 게이트 강화

### Rubric-Targeted Gates (RTG-*) 신규 ([`../conventions/rubric-targeted-quality-gates.md`](../conventions/rubric-targeted-quality-gates.md), bk)

총 게이트 = 정적 9 + derived N + **rubric-targeted R** :

```python
# rubric 매칭 시 (페이즈 04 의 RubricAdapter 와 같은 인스턴스 재사용)
def generate_rubric_targeted_gates(rubric: RubricSpec) -> list[Gate]:
  gates = []
  for category in rubric.categories:
    for bullet in category.bullets:
      gates.append(Gate(
        id=f"RTG-{category.name}-{bullet.idx}",
        category=category.name,
        bullet=bullet.text,
        check=convert_bullet_to_yes_no(bullet),
        artifact=infer_artifact_for_bullet(bullet),
      ))
  return gates
```

`quality/09-quality-gate.md` 신규 섹션 — RTG 표 :

```markdown
## Rubric-Targeted Gates (R = <N>)

| RTG ID | category | bullet | artifact | result | evidence |
|---|---|---|---|---|---|
| RTG-conceptual-1 | conceptual | "explains warm-up choice" | conceptual_model.md §Warmup | ✅ | "L88: ## Warmup Choice" |
| RTG-results-3 | results | "interpolates beyond measured grid" | README §8 | ❌ | "regex 0 match" |
```

종합 판정 :
- `proceed` → 모든 RTG PASS + 정적 9 PASS + derived PASS
- `remediate-then-proceed` → RTG fail ≤ 30% + 정적 9 PASS
- `halt` → RTG fail > 30% OR 정적 9 fail

self_lint C-RTG 검증. fail RTG 자동 → 페이즈 10 sprint NN+1 lesson source ([`../conventions/grader-in-sprint.md`](../conventions/grader-in-sprint.md) be 의 shadow grader lesson 과 합산).

### 게이트 강화 (sprint-14)

기존 게이트 본문 강화 :

| # | 게이트 | sprint-14 강화 |
|:-:|---|---|
| 1 | 의도 일치 | simplification 표 ≥ 1 row + direction 명시 ≥ 50% (bg, [`../conventions/directional-simplification.md`](../conventions/directional-simplification.md)) |
| 6 | NFR 임계 일치 | Measurement Contract row 1:1 매핑 + reconstruct 정당화 (bi, [`../conventions/measurement-contract.md`](../conventions/measurement-contract.md)). direct_ratio < 0.7 시 cap 0.85 |

새 self_lint 룰 (이번 sprint 적용) :
- C-CDM (contested decisions + universe spike) — bf
- C-MC (measurement contract) — bi
- C-DS (directional simplification) — bg
- C-CP (commentary policy) — bh
- C-GIS (grader-in-sprint) — be (페이즈 10 검증 위치, 본 페이즈 frontmatter 일부)
- C-RDS (rubric-driven-doc-skeleton) — bj
- C-RTG (rubric-targeted-gates) — bk


## §PNC/§Mirror/§Primary/§Literal — 4 감점 메타 패턴 (advisory, sprint-39 PR-B~E, B1 강등)

producer 0 · 실 run emit 실적 0(sprint-40 "0 emit" 보고 — 옛 §Gate-JSON-Emit-Mandate 자체가
그 미발화의 patch 였다). 커널 원칙상 producer 없는 검사는 게이트가 아니다 — **게이팅에서
제외, producer 승격 후보로 강등**(§9 완주 후속). 4 패턴 요지:

| 패턴 | 4 감점 메타 패턴 | 요지 |
|---|---|---|
| **§PNC** | A: Plumbed-Not-Consumed | 필드/변수 정의 ✓ / 실효 사용 ✗ 비대칭 |
| **§Mirror** | B: Workspace ≠ Deliverable | 내부 verification fact ↔ deliverable mirror 비대칭 |
| **§Primary** | C: Proxy-as-Primary | 06.b primary directive 가 sibling-metric proxy (`1 − queue/shift` 류) |
| **§Literal** | D: Letter-by-Fallback | 06.b avoid directive 의 literal 이 fallback 무관 재등장 |

게이팅·JSON 골격 의무(`gate_pnc/mirror/primary/literal.json`)·self_lint 연동
(C-PNC/C-MIR/C-PRI/C-LIT) 은 제거 — B1 은 커널이 인수한 것과 검증 대상이 소멸한 것만
지운다(무게이트 공백 금지 원칙, 본 4패턴은 애초 producer 부재로 게이팅 실효 0 이었다).


## §V6-Evidence-Bound — Cross-process reproducibility evidence (sprint-40 PR-B 강화)

**증거 회피 사례.** simulation-bench 001 v0.9.44 g4-v2 회차의 `quality/09-quality-gate.md` §V6 — 본문에 *"Two consecutive python run_experiment.py invocations produce bit-identical summary.json aggregates"* attestation 만 박힘, 실제 두 번 invoke 한 sha256 0. zero-context Opus reviewer 가 README ↔ summary.json 0.08% drift 를 catch 한 후에야 D-6/V6 회귀 (`hash(scenario_id)` salt randomization in `numpy.random.SeedSequence`) 발견. **본 절 = 그 회피 패턴 차단.**

### 검사 알고리즘 (G-RDC 실행 본문)

1. **별 subprocess invocation × 2** — 같은 process 안의 두 함수 호출 *아님*. `subprocess.run([python, entry_script], ...)` × 2.
   ```python
   # phase 09 게이트 본문이 의무 실행
   result1 = subprocess.run([sys.executable, entry_script, ...], capture_output=True, env={**os.environ, "PYTHONHASHSEED": "0"})
   shutil.copy(out_dir / "summary.json", gate_dir / "summary.run1.json")
   result2 = subprocess.run([sys.executable, entry_script, ...], capture_output=True, env={**os.environ, "PYTHONHASHSEED": "0"})
   shutil.copy(out_dir / "summary.json", gate_dir / "summary.run2.json")
   ```
2. **sha256 byte-equal** — `hashlib.sha256(open(f, "rb").read()).hexdigest()` × 2 비교.
3. **anti-pattern grep** ([`../conventions/cross-process-anti-patterns.md`](../conventions/cross-process-anti-patterns.md)) — src/ 안에서 다음 regex 모두 빈 결과 의무 :
   - `SeedSequence\([^)]*hash\(`
   - `np\.random\.seed\(.*hash\(`
   - `random\.seed\(.*hash\(`
   - `os\.urandom\(.*\)\s*[+]\s*\d`  (entropy mix into seed)
4. **PYTHONHASHSEED=0 강제** — entry script 실행 시 환경 변수 명시 의무.

### 산출물 — `quality/gate_v6_reproducibility.json`

```json
{
  "schema_version": "0.9.45",
  "intra_process": {
    "test_id": "tests/test_distributions.py::test_replication_rng_deterministic",
    "passed": true
  },
  "cross_process": {
    "pythonhashseed": "0",
    "invoke_1": {
      "stdout_sha256": "...",
      "summary_sha256": "...",
      "summary_path": "quality/v6/summary.run1.json"
    },
    "invoke_2": {
      "stdout_sha256": "...",
      "summary_sha256": "...",
      "summary_path": "quality/v6/summary.run2.json"
    },
    "summary_byte_equal": true
  },
  "anti_pattern_grep": {
    "scanned_globs": ["src/**/*.py"],
    "patterns_checked": 4,
    "violations": []
  },
  "verdict": "pass"
}
```

### 게이트 룰

- `cross_process.summary_byte_equal == true` 의무
- `anti_pattern_grep.violations == []` 의무
- `pythonhashseed == "0"` 명시 의무 (env 강제 + frontmatter 박힘)
- 미달 시 phase 09 verdict = `halt` → phase 10 sprint loop 진입 (regression bisect)
- *본문 attestation 만* (json 부재) = silent fail = phase 09 진입 거부

### 산출물 경로

```
.ShipofTheseus/<프로젝트>/quality/
├── 09-quality-gate.md                       # 본문 (frontmatter 에 sha256 박힘)
├── gate_v6_reproducibility.json             # 본 절 산출물 (필수)
└── v6/
    ├── summary.run1.json                    # subprocess 1 의 outputs/summary.json 복사본
    └── summary.run2.json                    # subprocess 2 의 outputs/summary.json 복사본
```

### phase 09 진입 시 검증 (B1 정정 — self_lint 규칙 아님, phase 09 본문 자체 검사)

- `quality/gate_v6_reproducibility.json` 존재 확인
- 본 JSON 의 `verdict == "pass"` 확인
- `cross_process.summary_byte_equal == true` 확인
- `anti_pattern_grep.violations` 비어 있음 확인
- 미달 시 phase 09 진입 거부

### 안티 패턴

a- **본문에 "byte-identical" 텍스트만 박고 JSON 부재** — sprint-40 회피 패턴 직접 차단.
b- **같은 process 안의 두 함수 호출로 cross-process 위장** — `subprocess.run` 별 호출 의무.
c- **PYTHONHASHSEED 미설정** — Python `hash()` salt 비결정성 발현. 환경 변수 의무.
d- **anti-pattern grep skip** — D-6 회귀 (hash(scenario_id) → SeedSequence) 의 직접 카탈로그. skip 시 sprint-40 보강이 무력화.

### 메모리 정합

- [`feedback_pseudocode_to_enforcement.md`](../../../memory/feedback_pseudocode_to_enforcement.md) — 의사코드 → enforcement 본 절이 *runtime guard* 역할.
- [`feedback_convention_runtime_gap.md`](../../../memory/feedback_convention_runtime_gap.md) — 컨벤션 선언 ≠ 런타임 집행. 본 §V6-Evidence-Bound 가 런타임 활성.
- [`project_bench_001_v0944.md`](../../../memory/project_bench_001_v0944.md) — D-6/V6 회귀 root cause 의 1:1 대응 lint.


## §README-Sync — Numeric drift atomic regen (sprint-40 PR-E 강화)

**증거 회피 사례.** simulation-bench 001 v0.9.44 g4-v2 회차 — README §7 baseline 12 126.7 t vs `summary.json` 12 116.7 t (0.08% drift, strict 임계 0.01% 의 8 배). zero-context Opus reviewer -1pt Results & interpretation. **본 절 = G-RNFS 의 *atomic regen* + *JSON evidence* layer.**

### 검사 알고리즘 (G-RNFS 강화)

1. **숫자 literal grep** ([`../conventions/readme-numbers-from-summary.md`](../conventions/readme-numbers-from-summary.md) §알고리즘 1-5).
2. **Atomic regen block (sprint-40 PR-E 신규)** — `harness/measure_run.py` (또는 entry script) invoke 와 README 갱신을 *atomic step* 으로 묶음:
   ```python
   # phase 09 게이트 본문이 의무 실행
   subprocess.run([sys.executable, entry_script, ...], env={**os.environ, "PYTHONHASHSEED": "0"})
   summary = json.load(open(out_dir / "summary.json"))
   regenerate_readme_from_summary(README_PATH, summary)   # 자동 regen
   # 두 step 사이에 다른 phase 진입 금지
   ```
3. **drift ≤ 0.01% 검증** — 모든 numeric literal 매핑 후 fuzzy match.
4. **JSON evidence emit** — `quality/gate_readme_summary_consistency.json` 산출.

### 산출물 — `quality/gate_readme_summary_consistency.json`

```json
{
  "schema_version": "0.9.45",
  "atomic_regen_block": {
    "measure_run_started_at": "2026-05-..T..:..:..+09:00",
    "summary_emitted_at": "...",
    "readme_regenerated_at": "...",
    "atomic": true,
    "phases_between": []
  },
  "scanned": {
    "files": ["README.md", "outputs/README.md", "handoff/14-handoff.md"],
    "numbers_total": 47,
    "numbers_mapped": 45,
    "numbers_external_source": 2
  },
  "drift": {
    "tolerance_pct": 0.01,
    "violations": [],
    "max_observed_drift_pct": 0.0
  },
  "verdict": "pass"
}
```

### 게이트 룰

- `atomic_regen_block.atomic == true` 의무 (`phases_between == []` 보장)
- `drift.violations == []` 의무
- `numbers_mapped + numbers_external_source == numbers_total` 의무 (모든 숫자 추적)
- 미달 시 phase 09 verdict = `halt` + atomic regen step 자동 재실행 → phase 09 재진입

### self_lint C-RDS (sprint-40 PR-E 신규)

phase 09 진입 시 `quality/gate_readme_summary_consistency.json` 의 `verdict == "pass"` + `atomic_regen_block.atomic == true` 검증. fail 시 phase 09 진입 거부.

### 메모리 정합

- [`feedback_pseudocode_to_enforcement.md`](../../../memory/feedback_pseudocode_to_enforcement.md) — G-RNFS 컨벤션은 v0.9.18 도입, atomic regen layer 가 sprint-40 에서 enforcement 닫음.
- [`feedback_convention_runtime_gap.md`](../../../memory/feedback_convention_runtime_gap.md) — atomic step 강제로 *컨벤션 선언 ≠ 런타임* 갭 G-2 layer 정정.


## §Methodology-Completeness — 도메인 매칭 시 methodology checklist enforcement (sprint-40 PR-G 신규)

본 절 = [`../conventions/nfr-derivation.md`](../conventions/nfr-derivation.md) §도메인 sub-checklist (sprint-40 PR-G) 의 phase 09 enforcement layer. *형용사 → NFR* 채널 (nfr-derivation 본 컨벤션) 과 직교 — *도메인 매칭* 시 *methodology* 차원의 checklist 자동 활성.

### 활성 조건

phase 01 의도 추출 시 `domain` field 가 [`../conventions/domain-pack.md`](../conventions/domain-pack.md) 카탈로그의 한 항목과 매칭되면 활성. 미매칭 시 본 게이트 skip + frontmatter `methodology_completeness_skipped: true` + `skip_reason: "domain unmatched"` 명시.

### 도메인 매칭 시 검사 항목 (도메인-agnostic 골격)

각 도메인의 *구체* sub-checklist 는 [`../conventions/nfr-derivation.md`](../conventions/nfr-derivation.md) §도메인 sub-checklist 에 박힘. 본 절은 *모든 도메인* 공통 골격 :

| 골격 항목 | 도메인 별 매핑 |
|---|---|
| **transient/steady-state classification** | DES: warmup justification · ML: train/val/test split · API: cold-start vs warm · ETL: batch boundary |
| **sample size / power analysis** | DES: replication count + CI half-width · ML: cross-val folds + variance · API: load duration + percentile coverage · ETL: batch sample size |
| **determinism protocol** | 모든 도메인: seed derivation + reproducibility byte-equal evidence (PR-B `gate_v6_reproducibility.json` 정합) |
| **horizon classification** | DES: terminating vs steady-state · ML: epoch budget vs early stop · API: SLO window · ETL: backfill vs incremental |

각 도메인의 구체 verification method 는 nfr-derivation §도메인 sub-checklist 본문 참조. 본 §은 *4 골격 항목 통과* 만 검사.

### 산출물 — `quality/gate_methodology_completeness.json` (도메인 매칭 시 의무)

```json
{
  "schema_version": "0.9.45",
  "domain": "<DES | ML | API | ETL | ...>",
  "domain_matched": true,
  "skeleton_checks": {
    "transient_classification": {"verdict": "pass", "evidence_path": "..."},
    "sample_size_power": {"verdict": "pass", "evidence_path": "..."},
    "determinism_protocol": {"verdict": "pass", "evidence_path": "quality/gate_v6_reproducibility.json"},
    "horizon_classification": {"verdict": "pass", "evidence_path": "..."}
  },
  "verdict": "pass"
}
```

도메인-specific 필드는 nfr-derivation §도메인 sub-checklist 의 schema 가 추가 박음 (e.g., DES = `warmup_minutes_value` / `first_half_throughput_mean`).

### 게이트 룰

- `domain_matched == false` → 본 게이트 skip (frontmatter 명시).
- `domain_matched == true` → 4 skeleton 항목 모두 `verdict == "pass"` 의무.
- evidence_path 미존재 또는 빈 파일 → fail.
- 미달 시 phase 09 verdict = `halt` → phase 06 plan 재진입 (해당 도메인 methodology 항목 보강).

### phase 09 진입 시 검증 (B1 정정 — self_lint 규칙 아님, phase 09 본문 자체 검사)

- domain 매칭 시 `quality/gate_methodology_completeness.json` 존재 확인
- 4 skeleton 항목 모두 verdict == "pass" 확인
- evidence_path 실제 파일 존재 확인
- 미달 시 phase 09 진입 거부

### 도메인 사례 (예시 — 본문 구조와 별개)

> **예시 footnote.** simulation-bench 001 (DES, mining) 회차 = warmup_minutes=0 정당화 thin (transient_classification skeleton 의 DES 매핑 — `warmup justification` evidence 부재). 본 §의 *구조 룰* 이 활성 시 `gate_methodology_completeness.json` 의 `transient_classification.verdict == "fail"` → phase 06 plan 재진입.
>
> 이 사례는 본 룰의 *적용* 결과이지 *케이스 종속* 룰이 아님. ML / API / ETL 도메인에도 동일 4 skeleton 적용 — 본 §은 도메인-agnostic.

### 메모리 정합

- [`feedback_harness_strengthening_methodology.md`](../../../memory/feedback_harness_strengthening_methodology.md) — *구조 변경 vs 케이스 패치* 정합. 본 §은 4-항목 골격 = 구조, 도메인 매핑은 nfr-derivation 분리.
- [`feedback_analytical_bound_validation.md`](../../../memory/feedback_analytical_bound_validation.md) — *cross-validation* 의 도메인 직교 확장.


## §V8 — Viewer-readiness (advisory, §8 동결 B2-F3 — 구 사전 차단 게이트)

phase 12/13 viewer 생산이 옵션(advisory)으로 강등되면서 본 사전 차단도 함께 강등 — **phase 09 진입은 viewer 디렉터리 존재와 무관하게 진행**. viewer 를 산출하기로 한 경우에 한해, `webview/`·`interactive-viewer/` 디렉터리·`index.html` 이 있는지 참고 확인 *가능*(옵션 체크, gate 아님). 빈 골격이든 채워졌든 phase 09 를 막지 않는다 — 내용 검사는 실행하는 경우 phase 12/13 자체 책임.

재승격 경로: `frozen.viewer_mandatory` A/B 실증.

## §자동 CLI 호출 (sprint-43 PR-E)

phase 09 진입 + 종료 시 orchestrator 의무 호출 :

```bash
# === phase 09 entry ===
# HARD-RULE 9.tt — runtime guard chain (skill_version + monotonicity + sub-CLI)
python skills/theseus-harness/scoring/runtime_guard_chain.py \
    --project-root .ShipofTheseus/<proj>/ \
    --phase 09 --transition entry \
    --grade <G> --domain <D> --orchestrator-version 0.9.48 \
    --output .ShipofTheseus/<proj>/quality/gate_runtime_guard_chain_entry.json

# === phase 09 exit ===
# HARD-RULE 9.uu — phase 09 본문에 phase 06/08 인용 검증
python skills/theseus-harness/scoring/cross_phase_context_audit.py \
    --project-root .ShipofTheseus/<proj>/ --phase 09 \
    --output .ShipofTheseus/<proj>/quality/gate_cross_phase_context_09.json
```

9.zz (phase invoke audit, phase 09 exit 분) 은 **은퇴** — `meta_audit`(생성형 레지스트리) 가
kernelized CheckSpec 의 declared≠invoked 갭을 더 강하게 잡는다(§첫 동작의 run_gate verdict).
`phase_invoke_audit.py` 는 phase 14 최종 감사(전체 phase 대상 broader audit)가 여전히
호출하므로 **스크립트는 존치**(grep 실측 — 다른 호출자 존재) — 은퇴한 것은 phase 09
자체의 개별 호출뿐.

본 §은 sprint-43 의 *literal Bash command* 박힘. exit 1 시 phase 09 진입/종료 차단.
