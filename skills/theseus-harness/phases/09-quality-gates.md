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
| **G-RDC** ([`../conventions/reproducibility-doublecheck.md`](../conventions/reproducibility-doublecheck.md)) | ca · 9.cc | entry script 2회 실행 + sha256 byte-equal assert (PYTHONHASHSEED 회귀 차단) |
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
d- **regex pattern 사용자 ack 0** + 자동 fail — false positive 폭증. ack 게이트 통과 후 enforce.

## sprint-39 4 패턴 통합 (트랙 3 마감)

§PNC (A) + §Mirror (B) + §Primary (C) + §Literal (D) — phase 09 cold session 자동 검출 4 패턴. self_lint C-PNC / C-MIR / C-PRI / C-LIT 4 룰 동시 통과 의무.
