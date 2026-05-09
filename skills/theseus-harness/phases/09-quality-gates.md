# Phase 09 — 9종 품질 게이트 + runtime enforcement

## 첫 동작 — cold session validator 의무 호출 (HARD-RULE 9.f)

phase 06/08 종료 → phase 09 진입 *직전* 다음 명령 의무 호출 :

```bash
python skills/theseus-harness/scoring/check_cold_session.py .ShipofTheseus/<프로젝트>/
```

- exit 0 → phase 09 진입 허용 (이하 정적/derived 게이트 진행)
- exit 1 → stderr 의 violation 목록을 `intent/00-violation.md` 에 기록 + 해당 phase (06 또는 08) 재진입 강제

본 호출은 phase 09 의 *첫 sub-step* 이며 quality-gate 본문 진행보다 우선. validator 가 detect 하는 카테고리 (mandatory_first_rerun_satisfied / Round N+1 NEW universes / sentinel regex / impl-plan 격리 / score cap by rerun / improvement_axes_remaining) 는 prose-only enforcement 의 *근본 우회 패턴* — runtime 차단으로만 효과.

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



## 한 줄 요약
**테스트 실행 전에 아홉 게이트로 *코드 모양 + 실행 가능성 + 프로세스 정합 + 도메인 결손 부재* 를 감사한다.** 게이트 1~5 = 정적 모양, 게이트 6 = NFR 측정, **게이트 7 = env-satisfied + 실 부팅 1회** ([`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md), v0.7.0), **게이트 8 (v0.9.18) = process flow / cycle coherence**, **게이트 9 (v0.9.18) = domain failure patterns 자기 검증**.

## 9 정적 게이트 + N derived 게이트 (v0.9.18)

총 게이트 수 = `static_gates_9 ∪ derived_gates(NFR_answers)`. NFR 0 = derived 0 = static 9. NFR 5 = derived 5 추가 = 14 게이트.

### 정적 게이트 (9)

| # | 게이트 | 무엇을 보는가 | fail 신호 |
| - | ----- | ------------ | -------- |
| 1 | **의도 일치** | 만든 것이 `01-intent.md` + `04-answers.md` + `05-decisions.md` 와 맞는가 | 요청 안 한 기능 등장, 또는 요청 기능 누락 |
| 2 | **범위 규율** | 계획 외 변경 있는가 | TODO 가 인가하지 않은 파일 변경 |
| 3 | **SOLID** | 모듈별 SRP/OCP/LSP/ISP/DIP | 변경 사유 2개 클래스, 포트 자리에 콘크리트 |
| 4 | **테스트 모양** | 모든 public 표면에 단위, 모든 교차 모듈 경로에 통합, 사용자 시나리오 happy-path E2E | public 함수에 테스트 없음, 모듈에 페이크 없음 |
| 5 | **FE/BE 패리티** | 양쪽 모두 동등한 테스트 깊이 | BE 80% 커버리지 + FE 스냅샷만 |
| 6 | **NFR 명시 임계 일치** | `intent/01-intent.md` §d 의 ✅ NFR 항목별 페이즈 10 측정 결과 — [`../conventions/spec-catalog.md`](../conventions/spec-catalog.md) | p99/가용성/LCP 임계 미달. ⏸ 항목 skip |
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


## §PNC — Plumbed-Not-Consumed pattern (sprint-39 PR-B inline)

**4 감점 메타 패턴 A** — 필드/변수 정의 layer ↔ 실효 사용 layer 의 비대칭. 정의 ✓ / 사용 ✗ = PNC 위반.

### 검사 알고리즘

1. AST 분석 (Python: `ast` / Go: `go/ast` / TS: `tsc --noEmit + ts-morph`)
2. dataclass / TypedDict / class field / yaml schema 추출
3. 각 field 가 어디서 *읽기* 되는지 (read access) 추적
4. read access 0 = PNC 위반 (define-only)

### 산출물 — `gate_pnc.json`

```json
{
  "fields_total": <int>,
  "fields_consumed": <int>,
  "fields_orphan": <int>,
  "violations": [
    {
      "field": "warmup_minutes",
      "defined_at": "config.py:L12",
      "consumed_at": null,
      "severity": "cap_correctness"
    }
  ]
}
```

### 게이트 룰

- violations 0 의무 (cap_correctness — 정의 layer fact 가 코드 실효에 영향 0 = correctness 신뢰 0)
- false positive allow_list: per-project frontmatter `pnc_allow_list: ["debug_*", "_reserved_*"]`
- skip 조건: project 가 *외부 schema* (e.g., OpenAPI request body) 정의만 하는 경우 — 내부 read 0 정상

### self_lint C-PNC

phases/09-quality-gates.md 본문에 §PNC 룰 키워드 박힘 검증. cold session 의 gate_pnc.json 산출물 검증은 phase 09 game 단계에서.

### 안티 패턴

a- **field 정의 후 read 0** — orphan field. PNC 위반.
b- **allow_list 남용** — 모든 field 를 allow 로 우회 = 실효 검사 0. allow_list ≤ 5% 권고.
c- **AST 분석 skip** — string grep 으로 대체 = false positive/negative 폭증. AST 의무.


## §Mirror — Workspace ≠ Deliverable pattern (sprint-39 PR-C inline)

**4 감점 메타 패턴 B** — 내부 verification fact ↔ deliverable mirror 의 비대칭. 내부 압력 강함 / 외부 압력 빈약.

### 검사 알고리즘

1. 내부 산출물 (impl/ 안의 verification fact, 예: `assert ramp_closed_after_30min`) 수집
2. deliverable (handoff/, README.md, 외부 evaluator 입력) 수집
3. 매핑 표 생성: 모든 internal fact 가 ≥ 1 deliverable 에 mirror 의무
4. unmirrored = 위반

### 산출물 — `gate_mirror.json`

```json
{
  "internal_facts_total": <int>,
  "mirrored_count": <int>,
  "unmirrored_count": <int>,
  "violations": [
    {
      "fact": "ramp_closed_after_30min",
      "internal_loc": "impl/sim.py:L89",
      "deliverable_mirror": null,
      "severity": "cap_results"
    }
  ]
}
```

### 게이트 룰

- unmirrored_count 0 의무 (cap_results — 내부 fact 가 외부 가시 0 = results 신뢰 0)
- internal fact 분류: assert 문 + invariant 검증 + sanity check 모두 fact
- skip 조건: project 가 deliverable 단일 (impl-only spike) 시 — frontmatter `deliverable_mode: workspace_only` 명시

### self_lint C-MIR

phases/09-quality-gates.md 본문에 §Mirror 룰 키워드 박힘 검증.

### 안티 패턴

a- **internal assert 만 있고 README mirror 0** — workspace-only 검증.
b- **deliverable 본문이 internal fact paraphrase** — *원본 위치 인용* 의무 (file:line). paraphrase 만 = mirror 0.
c- **external evaluator 가 internal fact 못 봄** — handoff 에 fact list 의무.


## §Primary — Proxy-as-Primary pattern (sprint-39 PR-D inline)

**4 감점 메타 패턴 C** — 형제 metric reformulation 을 1차 측정으로 통과 (e.g., `truck_util = 1 − queue/shift`). 직접 측정 아닌 derived metric 의 proxy.

### 검사 알고리즘

1. 06.b directives.json 의 `primary` type directive 추출
2. 각 primary directive 의 *measurement source* 추적 (산출물 frontmatter `measurement.formula`)
3. formula 안의 sibling metric 인용 감지 (다른 metric 변수 참조)
4. sibling overlap 계산: 같은 raw signal 사용 비율
5. sibling overlap > 50% 시 warn (proxy 의심)

### 산출물 — `gate_primary.json`

```json
{
  "primary_directives_total": <int>,
  "direct_measured": <int>,
  "proxy_via_sibling": <int>,
  "violations": [
    {
      "directive": "D-009 (primary)",
      "metric": "truck_util",
      "formula": "1 - queue/shift",
      "sibling_overlap": 0.6,
      "severity": "cap_correctness"
    }
  ]
}
```

### 게이트 룰

- sibling_overlap > 50% 0 건 의무 (cap_correctness — primary metric 이 proxy = correctness 신뢰 0)
- direct measurement 정의: signal 이 *시뮬 또는 실측* 직접 출력 (formula 0 또는 단순 단위 변환)
- skip 조건: primary directive 0 인 작업 (functional-only)
- override: 사용자 ack 시 sibling_overlap > 50% 허용 — `gate_primary_acked: true` frontmatter (06.f path-policy 정합)

### self_lint C-PRI

phases/09-quality-gates.md 본문에 §Primary 룰 키워드 박힘 검증.

### 안티 패턴

a- **truck_util = 1 - queue/shift** 류 — sibling (queue, shift) 이 truck_util 의 *raw signal* 과 같음. proxy.
b- **direct measurement 정의 모호** — formula = "throughput / capacity" 인데 capacity 가 derived = chain proxy.
c- **primary 라벨 없이 "1차" 주장** — 06.b directive 의 type 정합 의무.
d- **override 남용** — ack 후 violation 누적 = bench cheat. ack ≤ 1 권고.


## §Literal — Letter-by-Fallback (Literal-Forbid) pattern (sprint-39 PR-E inline)

**4 감점 메타 패턴 D** — 06.b directives.json 의 `avoid` directive 의 *literal* (e.g., hardcoded path / forbidden API) 가 deliverable source 에 등장. fallback 가 있어도 letter 위반.

### 검사 알고리즘

1. avoid directive 추출 (e.g., "no hardcoded paths", "no /mnt/", "no localhost", "no print()")
2. regex 자동 추출 (e.g., `r"/mnt/[a-z]/"`, `r"localhost:[0-9]+"`, `r"\bprint\("`)
3. 모든 deliverable source code grep
4. 매치 시 위반 (fallback 존재 무관 — letter-strict)

### 산출물 — `gate_literal.json`

```json
{
  "avoid_directives_total": <int>,
  "regex_patterns": [
    {"directive": "D-005", "pattern": "/mnt/[a-z]/", "source_quote": "no hardcoded /mnt paths"}
  ],
  "violations": [
    {
      "directive": "D-005",
      "pattern": "/mnt/[a-z]/",
      "match": "/mnt/d/data",
      "file": "src/loader.py:L42",
      "fallback_present": true,
      "severity": "cap_correctness"
    }
  ]
}
```

### 게이트 룰

- violations 0 의무 (cap_correctness — fallback 존재 무관, letter-strict)
- regex 자동 추출 + 사용자 ack (06.f path-policy 정합) — false positive 회피
- skip 조건: avoid directive 0 인 작업 (functional-only). avoid 가 *non-textual* (e.g., performance constraint) 인 경우 별도 분류

### self_lint C-LIT

phases/09-quality-gates.md 본문에 §Literal 룰 키워드 박힘 검증.

### 안티 패턴

a- **fallback 존재로 letter 위반 무시** — letter-strict. fallback 보장 != letter 통과.
b- **regex 추출 자동화 skip** + 수동 grep — false negative 폭증.
c- **avoid 의 의도가 *행동 패턴*** (e.g., "no synchronous wait") 인데 regex 로 매치 안 됨 — 행동 패턴은 별도 분류 (sprint-40 검토 후보).
d- **regex pattern 사용자 ack 0** (06.f path-policy 정합) + 자동 fail — false positive 폭증. ack 게이트 통과 후 enforce.

## sprint-39 4 패턴 통합 (트랙 3 마감)

§PNC (A) + §Mirror (B) + §Primary (C) + §Literal (D) — phase 09 cold session 자동 검출 4 패턴. self_lint C-PNC / C-MIR / C-PRI / C-LIT 4 룰 동시 통과 의무.


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

### self_lint C-V6X (sprint-40 PR-B 신규)

phase 09 진입 시 :
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


## §Gate-JSON-Emit-Mandate — sprint-39 4 게이트 자동 emit (sprint-40 PR-E 강화)

**증거 회피 사례.** simulation-bench 001 v0.9.44 g4-v2 회차 — sprint-39 가 도입한 4 패턴 게이트 (§PNC / §Mirror / §Primary / §Literal) 의 JSON 산출물 (`gate_pnc.json` / `gate_mirror.json` / `gate_primary.json` / `gate_literal.json`) **0 emit**. 컨벤션 선언만 박히고 cold session 이 *통째 skip*. **본 절 = 런타임 집행 layer.**

### 의무

phase 09 *진입* 시 (그러나 게이트 본문 진행 전) 다음 4 JSON 골격을 *자동* emit. cold session 이 skip 할 수 없음 — 골격 부재 시 phase 09 진입 거부.

```python
# orchestrator phase 09 entry hook
GATE_JSONS = ['gate_pnc.json', 'gate_mirror.json', 'gate_primary.json', 'gate_literal.json']

for fname in GATE_JSONS:
    path = quality_dir / fname
    if not path.exists():
        # 빈 골격 emit — cold session 이 본문 채움
        skeleton = SKELETONS[fname]   # 컨벤션 본문 §산출물 참조
        path.write_text(json.dumps(skeleton, indent=2))
```

### 4 골격 스키마

phase 09 §PNC / §Mirror / §Primary / §Literal 본문 §산출물 절 정합. 빈 골격 형식:

```json
// gate_pnc.json (PNC) 골격
{"schema_version": "0.9.45", "fields_total": 0, "fields_consumed": 0, "fields_orphan": 0, "violations": [], "verdict": "pending"}

// gate_mirror.json 골격
{"schema_version": "0.9.45", "internal_facts_total": 0, "mirrored_count": 0, "unmirrored_count": 0, "violations": [], "verdict": "pending"}

// gate_primary.json 골격
{"schema_version": "0.9.45", "primary_directives_total": 0, "direct_measured": 0, "proxy_via_sibling": 0, "violations": [], "verdict": "pending"}

// gate_literal.json 골격
{"schema_version": "0.9.45", "avoid_directives_total": 0, "regex_patterns": [], "violations": [], "verdict": "pending"}
```

cold session 진행 중 phase 09 본문이 각 게이트의 *실제 검사* 후 `verdict` 를 `pass` / `fail` 로 갱신.

### 게이트 룰

- 4 JSON 모두 *존재* 의무 (phase 09 entry 시 자동 골격 emit)
- 모든 `verdict == "pass"` 의무 (phase 09 종합 판정 통과 조건)
- `verdict == "pending"` 인 채로 phase 10 진입 시도 = silent skip 신호 → phase 09 재진입 강제

### self_lint C-GJM (sprint-40 PR-E 신규 — Gate-JSON-emit Mandate)

phase 09 종료 직전 :
- 4 JSON 파일 존재 확인
- 4 JSON 모두 `verdict == "pass"` 확인
- 미달 시 phase 09 종료 거부

### 메모리 정합

- [`feedback_dual_pressure_json_schema.md`](../../../memory/feedback_dual_pressure_json_schema.md) — *이중 압력* 패러다임 (게이트 + JSON evidence). 본 §Gate-JSON-Emit-Mandate = 4 게이트의 런타임 활성.
- [`feedback_convention_runtime_gap.md`](../../../memory/feedback_convention_runtime_gap.md) — sprint-39 4 패턴 inline 의 *런타임* layer 닫음.


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

### self_lint C-MCC (sprint-40 PR-G — Methodology Completeness Catalogue, sprint-40 fix 일반화)

phase 09 진입 시 :
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


## §V8 — Viewer-readiness 사전 차단 (sprint-40 PR-C 신규)

phase 09 진입 시 phase 12/13 viewer 산출 디렉터리 *외피 존재* 사전 검사. **목적**: pre-cold-session-bootup.md 가 빈 골격을 사전 생성했는지 확인 — 부재 시 phase 00 재실행 트리거. (pre-bootup 누락 → 12/13 종료 게이트 fail → 시간 낭비. 09 사전 차단으로 빠른 실패.)

### 검사 항목

| 검사 | G2 | G3+ | G4+ | fail 시 |
|---|---|---|---|---|
| `webview/` 디렉터리 존재 | ✓ | ✓ | ✓ | phase 00 (pre-bootup) 재실행 |
| `webview/index.html` 빈 골격 또는 채워짐 | ✓ | ✓ | ✓ | 동일 |
| `interactive-viewer/` 디렉터리 존재 | (도메인 매칭 시) | ✓ | ✓ | 동일 |
| `interactive-viewer/index.html` 빈 골격 또는 채워짐 | (매칭 시) | ✓ | ✓ | 동일 |

**빈 골격 OK** — phase 12/13 가 *내용* 채움을 보장. §V8 = *디렉터리 존재* 만 검사 (phase 12/13 종료 게이트 = *내용* 검사).

### 검사 알고리즘 (orchestrator phase 09 entry)

```python
import pathlib

def check_phase09_viewer_readiness(project_root: pathlib.Path, grade: str, domain_matched: bool) -> tuple[bool, list[str]]:
    missing = []
    # webview always
    if not (project_root / 'webview').is_dir():
        missing.append('webview/ 디렉터리 부재 (pre-cold-session-bootup.md 누락 신호)')
    if not (project_root / 'webview' / 'index.html').exists():
        missing.append('webview/index.html 부재')
    # interactive-viewer
    require_iv = (grade != 'G2') or domain_matched
    if require_iv:
        if not (project_root / 'interactive-viewer').is_dir():
            missing.append('interactive-viewer/ 디렉터리 부재')
        if not (project_root / 'interactive-viewer' / 'index.html').exists():
            missing.append('interactive-viewer/index.html 부재')
    return (len(missing) == 0, missing)
```

### 산출물 — `quality/gate_v8_viewer_readiness.json`

```json
{
  "schema_version": "0.9.45",
  "grade": "G4",
  "domain_matched": true,
  "checked_at": "...",
  "checks": [
    {"path": "webview/", "kind": "dir", "exists": true},
    {"path": "webview/index.html", "kind": "file", "exists": true, "size": 2451},
    {"path": "interactive-viewer/", "kind": "dir", "exists": true},
    {"path": "interactive-viewer/index.html", "kind": "file", "exists": true, "size": 1842}
  ],
  "missing": [],
  "verdict": "pass"
}
```

### 게이트 룰

- `missing == []` 의무 — 미달 시 phase 09 진입 거부, phase 00 (pre-cold-session-bootup) 재실행 강제.
- *빈 골격 OK* — 사전 차단의 목적 = *디렉터리 외피* 만 보장, *내용* 은 12/13 의 종료 게이트 책임.

### self_lint C-VEX (phase 12/13 종료 게이트와 통합)

phase 09 진입 시 `quality/gate_v8_viewer_readiness.json` 의 `verdict == "pass"` 검증. fail 시 phase 09 진입 거부.

### 메모리 정합

- [`feedback_dual_pressure_json_schema.md`](../../../memory/feedback_dual_pressure_json_schema.md) — *세 단* 압력 (pre-bootup 디렉터리 / phase 12-13 종료 / viewer 자체 빈 화면).
- [`feedback_convention_runtime_gap.md`](../../../memory/feedback_convention_runtime_gap.md) — 컨벤션 선언 ≠ 런타임 집행 갭 직접 정정.

### 안티 패턴

a- **phase 12/13 종료 게이트만 두고 09 사전 차단 skip** — 12 까지 진행한 뒤 fail → sprint loop 대량 자원 낭비. 09 사전 차단이 효율.
b- **빈 골격 검사를 *내용* 검사로 대체** — 09 = 디렉터리 외피, 12/13 = 내용. 책임 분리.
c- **`webview/index.md` 마크다운으로 `webview/index.html` 우회** — v0.9.44 회차 직접 사례. 본 §V8 grep 자동 차단 (`.html` 확장자 의무).
