# 설계 문서 — Verification Kernel + Evidence Contract

> **작성**: Claude Fable 5 (설계·문서화)
> **구현 위임**: opus/sonnet (본 문서 §12 작업 패키지 기준)
> **일자**: 2026-07-04
> **대상 저장소**: Ship of Theseus (theseus-harness v0.9.52)
> **근거**: `.tmp/cold-parallel-audit-2026-07-04-report.md` (8-렌즈 콜드 병렬 감사, CONFIRMED 19 / PLAUSIBLE 11)

---

## 0. 이 문서가 확정하는 것 (범위 계약)

이 문서는 **측정계를 "형식 게이트 + 선언"에서 "스크립트 기반 실행-결과(값) 확인 게이트"로 전환**하는 설계를 확정한다.

세 결정은 다음으로 확정됐다 (사용자 승인):

1. **아키텍처 자세** = 하이브리드 검증 커널 + 증거 계약 — 단일 커널이 "값 없는 verdict는 기계적 거부"를 유일 게이트로 삼고, 기존 CLI는 커널에 꽂히는 *증거 생산자*로 재활용.
2. **문서 범위** = 일반 메커니즘(범용 커널 계약 + Evidence Contract 스키마) + 측정 코어 4점 상세 적용 + 15-페이즈 마이그레이션 표(요약). 페이즈별 상세는 후속 스펙.
3. **마이그레이션 정책** = 승격(promote) / 래핑(wrap) / 동결(freeze) 3분류.

**이 문서의 비목표(§13):** 전체 15-페이즈 각각의 producer 구현 상세, 암호학적 서명 인프라, 외부 evaluator 연동 rubric 매핑 — 모두 후속 스펙.

---

## 1. 문제 정의 — "측정"이 실은 "자기 신고"다

감사가 실측으로 확증한 핵심 결함 (파일:증거):

| # | 결함 | 실측 근거 |
|---|---|---|
| P1 | **채점 입력이 자기 신고** | `scoring/score.py`는 손으로 쓴 `inputs.json`(`test_pass_rate`, `modules_passing_solid`…)을 그대로 받아 산술만 수행. 값의 출처 검증 0. `_safe_div(default=1.0)` (score.py:75) → `files_touched=0`이면 `scope_fit=1.0` (무노동 만점). |
| P2 | **verdict가 산출물이 아닌 문서/키워드 검사** | `self_lint.py` 3,466줄 / 93 C-룰 다수가 *컨벤션 문서 자신에 키워드가 있는지* grep. 선언된 산출물 검증(C-MIF/C-TBR/C-PCR 류)은 미구현. |
| P3 | **콜드 인증이 격리를 안 봄** | `check_cold_session.py`는 파일 개수(tournament≥2, rerun≥1) + **영어 sentinel 정규식**(한국어 산출물 미매치)만. 세션 오염 차단 검사 0. `prior_context_token_count: 0`은 템플릿 하드코딩. |
| P4 | **fingerprint 위조 무방비** | `fingerprint.py`는 비밀 없는 자기 sha256. `compute`가 in-place 재서명, `verify`는 재계산 비교뿐 — 의도적 위조를 잡지 못함. 자기 적용 산출물은 sha256 규격조차 아닌 사람이 쓴 슬러그(= 실행된 적 없다는 물증). |
| P5 | **메타 감사가 하드코딩 사각** | `phase_invoke_audit.py`의 `CLI_TRACE_PATHS`는 10개 하드코딩. 매핑 없는 신규 CLI(sprint-50~52 ~14개)는 `invoked: None → audit_skipped`이고 `overall_pass = len(not_invoked)==0` (phase_invoke_audit.py:166) → **감사 사각이 FAIL을 유발하지 않음**. |
| P6 | **회귀/바이섹트 사문** | 점수 시계열이 자기 채점의 단조 상승 편향 → 회귀 트리거(0.05 하락) 발동 실적 0회. `regression_check`는 cmd 미지정 시 skipped를 pass 취급. bisect 축에 good/bad 판정 함수 없음. |
| P7 | **enforcement가 honor system** | 30여 CLI 전부 "LLM이 prose를 읽고 기억해 호출"(훅/래퍼 0). declared≠invoked 갭이 sprint-43/51/52에서 3회 반복, 매번 해법이 새 룰 추가 → 지시 질량 발산(phase 06 진입 시 지시문 실측 상한 ~41만 chars). |

**근본 원인 한 줄:** 파이프라인의 모든 핵심 신호원(점수·토너먼트·shadow grade·회귀 트리거·콜드 인증)이 *LLM 자기 신고* 위에 서 있고, 그것을 지키게 하는 장치조차 *문서 키워드 grep*이다. 내부 94 vs 외부 저평가의 괴리는 이 구조의 필연적 출력이다.

---

## 2. 설계 원칙 (5개, 위반 불가)

1. **측정하라, 주장하지 마라 (Measure, don't assert).** 게이트의 입력은 *스크립트를 실행해서 나온 원시 값*이어야 한다. LLM이 산출한 숫자·판정은 게이트 입력이 될 수 없다.
2. **증거 없음 = FAIL (No evidence is FAIL).** verdict의 부재·공백·파싱 불가·자기 신고는 통과가 아니라 실패다. `skipped == pass`를 `skipped == FAIL`로 뒤집는다.
3. **하나의 매니페스트 (One manifest).** 페이즈 수·멀티버스 폭·그레이드별 활성 체크는 *기계 판독 가능한 단일 소스*에 정의하고 러너와 메타 감사가 같은 파일을 읽는다. 스펙이 두 곳에 있으면 그것은 스펙이 아니라 드리프트다.
4. **줄인다, 늘리지 않는다 (Shrink, don't add).** 새 결함의 대응은 "새 prose 룰 추가"가 아니라 "기존 체크를 값 기반으로 교체". 커널 도입은 self_lint의 prose verdict 역할을 *대체*하며, 측정 가능한 것을 grep하던 C-룰은 삭제/참조 강등한다.
5. **재현 가능성 (Determinism).** 같은 증거 → 같은 verdict, 항상. 커널을 재실행하면 판정이 비트 단위로 재현된다. 재현 불가한 판정은 판정이 아니다.

---

## 3. Evidence Contract — 단일 인터페이스

모든 게이트/체크는 실행 후 **Evidence Record**(JSON) 하나를 산출한다. 이것이 커널과 생산자 사이의 유일한 계약이다.

```json
{
  "evidence_schema_version": "1.0",
  "check_id": "scoring.correctness",
  "phase": "09",
  "project_run": "synthetic_mine_throughput_001",
  "produced_by": "run",
  "producer_cmd": "python scoring/producers/measure_tests.py --suite tests/ --junit results/junit.xml",
  "producer_exit_code": 0,
  "measured": {
    "tests_total":  { "value": 42, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml" },
    "tests_passed": { "value": 40, "source": "pytest_junit_xml", "artifact_path": "results/junit.xml" },
    "tests_failed": { "value": 2,  "source": "pytest_junit_xml", "artifact_path": "results/junit.xml" }
  },
  "artifact_digests": { "results/junit.xml": "sha256:abc123..." },
  "measured_at": "2026-07-04T10:00:00Z",
  "self_reported": false
}
```

### 3.1 필드 규약

| 필드 | 규약 | 커널의 처리 |
|---|---|---|
| `produced_by` | `"run"` 만 허용. `"assert"`는 금지 값 — 존재 자체가 FAIL. | 값이 `"run"`이 아니면 즉시 FAIL. |
| `producer_cmd` | 증거를 낳은 *실제 명령* 문자열. | CheckSpec의 선언 producer와 정규 매칭. 불일치=FAIL. |
| `producer_exit_code` | 정수. | `!= 0`이면 FAIL (측정 실행 자체가 실패). |
| `measured.<key>` | **원시 값 + provenance.** 각 값은 `{value, source, artifact_path}`. score/verdict/등급 같은 *가공 결과 금지* — 오직 관측된 원시 수치·불리언·카운트. | provenance 3필드 중 하나라도 결손=해당 값 무효=FAIL. |
| `artifact_digests` | `measured`가 참조한 모든 artifact의 content hash. | 커널이 디스크의 실제 파일 hash와 대조. 불일치=FAIL. |
| `self_reported` | 불리언. `true`는 화이트리스트된 극소수(예: 사용자 인터뷰 답)만. | `true`이고 화이트리스트 밖이면 FAIL. |

**핵심 불변식:** `measured`의 모든 값은 *디스크에 존재하는 artifact에서 파싱된 것*이어야 하며, 그 artifact의 hash가 `artifact_digests`에 있고 실제 파일과 일치해야 한다. LLM이 상상한 숫자는 backing artifact가 없어 구조적으로 이 계약을 통과할 수 없다.

---

## 4. Kernel — 유일한 판정자

### 4.1 공개 계약

```
kernel.verify(check_spec: CheckSpec, evidence: EvidenceRecord) -> Verdict
```

```python
@dataclass
class Verdict:
    check_id: str
    result: str            # "PASS" | "FAIL"
    value: float | None    # 측정값의 결정 함수 (해당 시)
    reasons: list[str]     # FAIL 사유 (값·경로 명시)
    evidence_digest: str   # 판정에 사용한 증거의 hash (재현 추적)
    verified_at: str
```

### 4.2 CheckSpec — 게이트의 정의

게이트는 prose가 아니라 CheckSpec 하나로 정의된다. 이것이 "일반 메커니즘"의 핵심이다.

```json
{
  "check_id": "scoring.correctness",
  "phase": "09",
  "grades": ["G2", "G3", "G4", "G5"],
  "status": "active",
  "producer": {
    "cmd_pattern": "^python scoring/producers/measure_tests\\.py ",
    "must_exit_zero": true
  },
  "provenance_required": ["tests_total", "tests_passed", "tests_failed"],
  "assertions": [
    { "expr": "tests_total > 0",              "on_fail": "no tests executed" },
    { "expr": "tests_failed == 0",            "on_fail": "failing tests present" }
  ],
  "value": "tests_passed / tests_total",
  "absence_policy": "FAIL"
}
```

- `producer.cmd_pattern` — 증거의 `producer_cmd`가 이 정규식과 맞아야 함. (임의 스크립트가 아니라 *선언된* 측정기가 낳은 증거만 인정.)
- `assertions` — `measured` 값에 대한 술어. verdict = 전 술어의 AND. 술어는 값 비교만 — 자연어 판단 불가.
- `value` — 점수가 필요하면 *측정값의 결정 함수*. 자기 신고 숫자가 아니라 계산식.
- `absence_policy: "FAIL"` — 증거 부재 시 기본 FAIL (원칙 2).

### 4.3 커널의 5개 법칙 (구현 순서 = 우선순위)

```
verify(spec, evidence):
    1. 증거 존재·파싱 가능? 아니면 → FAIL("evidence_missing")           # P5, P6 차단
    2. evidence.self_reported == true 이고 화이트리스트 밖? → FAIL       # P1 차단
       또는 measured 값 중 provenance(source/artifact_path) 결손? → FAIL
    3. producer_cmd가 spec.producer.cmd_pattern 매칭?                    # P7 차단
       그리고 producer_exit_code == 0? 아니면 → FAIL
       그리고 artifact_digests가 디스크 실파일 hash와 일치? 아니면 → FAIL # P4 차단
    4. 모든 assertion(값 술어) 참? 아니면 → FAIL(첫 거짓 술어의 on_fail)   # 값 기반 게이트
    5. value 계산 (측정값의 함수), Verdict(PASS, value, evidence_digest) 반환
```

**법칙 1~3이 "형식 게이트 → 실행-결과 확인"의 전환점이다.** 증거가 실제 실행의 산물이고 그 값이 디스크 artifact로 뒷받침되지 않으면, 술어 평가(법칙 4)에 도달하지도 못한다.

---

## 5. Producer / Kernel 분리 — 측정기와 판정기의 분업

세계를 둘로 나눈다:

- **Producer** — 실세계에서 *무언가를 실행*하고(테스트 러너, lint, 파일 스캔, git diff, 서브에이전트 dispatch 로그 파싱), provenance 붙은 원시 값만 emit. **verdict·score를 절대 내지 않는다.**
- **Kernel** — Evidence Record만 받아 판정. 실행하지 않는다. 상상하지 않는다.

이 분업이 P1을 근본에서 없앤다. `score.py`는 더 이상 손으로 쓴 `inputs.json`을 받지 않는다:

```
[변경 전]  agent가 inputs.json 작성 → score.py가 산술 → score
[변경 후]  measure_submission.py 실행 → junit/lint/coverage artifact → 
           Evidence Record(원시 counts) → kernel.verify(scoring.* CheckSpec) → Verdict
           score.py = kernel이 호출하는 순수 함수 (측정값 → 가중 평균)
```

`_safe_div(default=1.0)` 문제는 CheckSpec 술어로 해소: `scope_fit`은 `files_touched > 0` 술어를 갖고, 0이면 만점이 아니라 FAIL. `n/a`는 명시적 상태이지 1.0 default가 아니다.

---

## 6. Registry + 메타 감사 — 하드코딩 사각 제거

P5(하드코딩 `CLI_TRACE_PATHS`)를 생성형 레지스트리로 대체한다.

- **`checks/` 디렉터리** — CheckSpec 하나 = 파일 하나. 새 체크 추가 = 파일 추가(자동 등록).
- **매니페스트** (`pipeline.manifest.json`, 원칙 3) — 페이즈 순서, 그레이드별 활성 CheckSpec ID, 멀티버스 폭. 러너와 감사가 *같은 파일*을 읽는다.
- **메타 감사** (`meta_audit.py`) — 하드코딩 리스트를 열거하지 않는다. *레지스트리를 열거*해 "이 실행의 그레이드/페이즈에서 활성인 모든 CheckSpec에 대해 Evidence Record가 존재하고 커널을 통과했는가"를 단언.

```
meta_audit(run_root, grade):
    active = manifest.active_checks(grade)          # 매니페스트에서 열거 (하드코딩 아님)
    for spec in active:
        ev = load_evidence(run_root, spec.check_id)
        v  = kernel.verify(spec, ev)                # 실제 커널로 재판정 (재현)
        if v.result != "PASS": violations.append(...)
    verdict = PASS if not violations else FAIL
```

결과: "declared but not invoked"가 구조적으로 불가능해진다 — 감사가 파이프라인이 실행하는 바로 그 레지스트리를 순회하므로, 선언되고 감사 안 되는 체크는 존재할 수 없다. 신규 CLI가 사각이던 P5가 사라진다.

---

## 7. 측정 코어 4점 상세 적용

### 7.1 Scoring (score.py) — **wrap**

- **Producer**: `measure_submission.py` — 테스트/lint/type-check/coverage를 *실행*, 원시 counts를 junit·coverage·lint artifact에서 파싱해 Evidence Record emit.
- **CheckSpec**: `scoring.correctness / scoring.solid / scoring.coverage / scoring.e2e …` — 각 sub-score가 하나의 CheckSpec. `score.py`는 kernel이 호출하는 순수 함수로 강등(측정값 → 가중 평균).
- **해소**: P1(자기 신고), `_safe_div default=1.0`(분모 0 술어), 임계 0.999를 *측정된* plateau 위에서 재설정.
- **임계 재설정 방향**: 0.999는 정직한 strict 채점(실측 92~94)과 양립 불가하므로, 임계를 "측정값 분포 기반"으로 재정의하고 도달 불가 임계로 인한 인플레이션·budget 소진 유인을 제거. (구체 임계값은 §12 dogfood 실측 후 확정.)

### 7.2 Tournament (tournament.py) — **wrap**

- **Producer**: `measure_shadow_grades.py` — 각 shadow grade가 *커널을 통과한 Evidence Record*여야 winner_ratio 계산에 입력됨.
- **독립성을 값으로 측정**: "3pt 차이 의무 / weakest_category 상이 의무" 같은 *퍼포먼스적 불일치 강제*를 폐기. 대신 grader 간 점수 *분산*을 측정값으로 계산해 `variance > 0` 같은 값 술어로 독립성 확인. (정직한 수렴을 벌하지 않음.)
- **해소**: shadow grade 성형(감사 발견 16), 앙상블 origin 분포 모순(폭 7에서 7×0.2>1.0 — §8 freeze 대상).

### 7.3 Regression (regression_check) — **promote**

- **good/bad를 값으로**: 두 Evidence Record(`score(N)`, `score(N-1)`)의 *커널 검증된* value를 비교. bisect는 실제 값 시계열에서 작동.
- **skipped=pass 뒤집기**: cmd 미지정 시 skipped를 pass로 취급하던 것을 `absence_policy: FAIL`로 교체. 측정 안 하면 통과가 아니라 실패.
- **해소**: P6(회귀 사문). 트리거가 자기 채점 단조 상승이 아니라 커널 검증 값의 실제 하락에 발동.

### 7.4 Cold session (check_cold_session) — **redesign**

- **격리 증거 producer**: `measure_cold_isolation.py` — 서브에이전트 dispatch 로그를 파싱해 *실제* `prior_context_token_count`, 콜드 에이전트가 접근 허용된 파일 목록을 Evidence Record로 emit(하드코딩 0 폐기).
- **값 기반 오염 검사**: 콜드 산출물이 하류 artifact(플랜/구현/내부 컨벤션명)를 참조하는지 *계산된 overlap 값*으로 판정. 영어 sentinel 정규식(한국어 미매치) 폐기 → 언어 무관 값 검사.
- **재이해 diff를 소비**: 콜드 재이해(03)/계획 재이해(07)와 원문의 *측정된 의미 overlap*이 임계 미달이면 차이를 좁히는 루프로 소비(단순 파일 축적 아님).
- **해소**: P3(격리 미검사), 감사 T4(콜드의 허구).

---

## 8. 마이그레이션 3분류 — 승격 / 래핑 / 동결

| 분류 | 정의 | 대상 (예시) | 조치 |
|---|---|---|---|
| **승격 (promote)** | 이미 값 기반에 가까움 | `dacapo_threshold`, `deep_module_metric`, `dry_violation_count`, `define_errors_check`, `refactor_not_rewrite_ratio` | CheckSpec + producer로 재작성, 최소 변경. |
| **래핑 (wrap)** | 유용하나 자기 신고/verdict emit | `score.py`, `tournament.py`, `self_lint.py`, `check_cold_session.py`, `fingerprint.py` | producer + CheckSpec으로 분리, 커널이 verdict 소유. |
| **동결 (freeze)** | 편익 미실증 / 고정 비용 | 멀티버스 폭 5/7/9, 7-우주 풀 구현 의무, viewer 3종 의무, 앙상블 `origin ≥0.2 each`, budget 80% 강제 소진 | `status: "frozen"`. 커널이 **비게이팅(advisory)**으로 처리. A/B Evidence Record가 편익을 실증하기 전까지 종료를 막지 않음. |

**동결의 의미:** 감사 T5/T7이 확증한 "비용 확정·편익 실증 0건"을 직접 처리한다. `.ShipofTheseus` 전체에 code/universe-N·shadow-grade·dacapo-rerun 실행 흔적이 0개 — 폭 5/7/9는 한 번도 돌아본 적 없는 선언이다. 동결은 삭제가 아니라 *게이트 자격 정지*이며, 편익을 값으로 증명하는 A/B 체크가 통과하면 재승격한다.

**동결이 여는 진단:** viewer 3종·HTTP 서버 등 외부 배점 중립 산출물의 의무를 해제하면, "content depth 부족"이 하네스 오버헤드의 *결과*인지 *원인*인지를 이 다이어트 이후에만 판별할 수 있다.

---

## 9. 15-페이즈 마이그레이션 표 (요약)

각 페이즈 게이트를 CheckSpec으로 매핑. `P`=promote, `W`=wrap, `F`=freeze, `N`=신규 producer 필요.

| 페이즈 | 현재 게이트(대표) | 측정할 값 (producer) | 분류 |
|---|---|---|---|
| 00 naming | pre_bootup 서버 up | 서버 PID 살아있음 + 포트 응답 (measure_bootup) | W |
| 01 intent | mindmap Mermaid 존재 | Mermaid 노드/엣지 카운트 + §k/§j 섹션 존재 (measure_intent_struct) | W·N |
| 01.5 hidden | 3 산출물 + ≥5항목 | 산출물 파싱 카운트 + prompt-meta overlap 값 (intent_extension_emit 승격) | P |
| 02 document | 리뷰 존재 | 리뷰 항목 카운트 + 원문 인용 trace (measure_review) | W·N |
| 03 cold re-read | 콜드 산출물 존재 | **격리 증거 + 의미 overlap 값** (measure_cold_isolation) | N |
| 04 clarify | 04-answers 존재 | 질문↔답 매핑 카운트 + headless 응답 provenance | W |
| 05 critique | 비평 존재 | 비평 항목 카운트 + friction 축 커버 | W |
| 06 plan | tournament≥2, plan 8항목 | winner_ratio(커널 검증 shadow grade) + plan 항목 파싱 | W |
| 06 multiverse 폭 | 폭 5/7/9 강제 | **동결** — 편익 A/B 나올 때까지 advisory | F |
| 07 plan re-read | 계획 재이해 존재 | 계획↔원문 overlap 값 | W·N |
| 08 implement | 7-우주 풀, dacapo | 실 코드 모듈 카운트 + deep/dry 메트릭 (승격) | P + F(폭) |
| 09 quality gate | 7 게이트 + self_lint | **measure_submission 4점** (§7.1) + 커널 재판정 | W |
| 10 sprint loop | budget 80% 강제 | sprint score delta(커널 검증 값) | W + F(80%) |
| 11 regression | bisect, 트리거 | **값 시계열 비교** (§7.3) | P |
| 12 webview | 6파일 강제 | 파일 존재 + JSON schema 정합 | W + F(의무성) |
| 13 iv | dashboard widgets | widget 카운트 + schema | W + F(의무성) |
| 14 handoff | lineage_finalize | placeholder grep → 값 검사 + 메타 감사(§6) | W |

*상세 producer 명세·값 술어·임계는 페이즈별 후속 스펙에서 확정 (본 문서 범위 밖).*

---

## 10. fingerprint 강화 — 자기 해시에서 증거 기반 provenance로

P4의 근본은 "비밀 없는 자기 해시라 에이전트가 재서명 가능"이다. 단계적 처리:

- **근시(near-term)**: fingerprint의 *의미*를 바꾼다 — frontmatter fingerprint 단독으로는 아무것도 보증하지 않는다. 커널이 "이 페이즈 산출물의 backing Evidence Record가 존재하고 통과했는가"를 별도 검증하며, 통과하는 증거가 없는 frontmatter는 위조로 간주(FAIL). 위조 차단이 hash가 아니라 *커널*에서 일어난다.
- **fingerprint 대상 이동**: 자기 해시(본문 sha256)가 아니라 *Evidence Record가 참조하는 artifact들의 content hash 체인*을 지문의 뿌리로. 산출물이 실제 실행 artifact에 묶인다.
- **회귀 vs 체인 충돌 해소**: 페이즈 N→M(M<N) 회귀 시 체인 무결성과 단조성 가드가 충돌하는 문제(감사 발견 26)에 *수복 프로토콜*을 정의 — 회귀는 체인을 끊는 게 아니라 새 브랜치(rework-N)로 기록하고, 커널이 브랜치 지점을 값으로 추적.
- **원거리(follow-on, 비목표)**: 진짜 암호학적 서명(러너 소유 키) — 별도 스펙.

---

## 11. 반(反)군비경쟁 제약 — 이것이 또 다른 층이 되지 않으려면

감사 T2/T3의 핵심 경고: 이 설계가 30여 CLI에 31번째를 더하는 것이면 실패다. 다음은 위반 불가 제약이다.

1. **커널은 self_lint의 verdict 역할을 대체한다.** 측정 가능한 것을 grep하던 C-룰(문서 키워드 검사)은 삭제 또는 참조 강등. self_lint는 "커널 없는 정합성"(순수 마크다운 인덱스)만 남긴다. **순증(net-add)이 아니라 순감(net-reduce)이 성공 지표.**
2. **prose 체크 금지.** 새 체크는 producer + CheckSpec을 가진 것만 존재한다. "문서에 키워드가 있으면 통과"는 더 이상 체크가 아니다.
3. **단일 매니페스트.** 페이즈 수(현재 14/15/16 병존)·폭({3,4,6} vs 5/7/9)·그레이드별 활성 체크·질문 상한을 `pipeline.manifest.json` 한 곳에. 러너·메타 감사·문서가 모두 이 파일을 참조. 스펙 드리프트(감사 발견 2)가 구조적으로 불가능해진다.
4. **HEAD 자기 준수 선행.** 현재 저장소 HEAD가 self_lint 6건 실패·HARD-CORE 4000자 cap을 7,211자로 초과한 채 "마감"돼 있다(감사 발견 15). 커널 도입 전, 자기 룰을 지키는 상태 복원이 모든 후속 작업의 전제.
5. **성공 측정 = 지시 질량 감소 + 외부 점수.** 이 작업의 성패는 "새 기능 추가"가 아니라 (a) phase 진입 지시문 chars 감소, (b) 커널 도입 전/후 외부 벤치 점수의 *controlled* 비교로 판정한다.

---

## 12. 구현 롤아웃 — opus/sonnet 작업 패키지

문서 작성(Fable) 이후 실제 구현은 opus/sonnet에 위임. 각 패키지는 독립 커밋 + 검증 게이트.

| WP | 내용 | 권장 모델 | 완료 조건(값 기반) |
|---|---|---|---|
| **WP0** | HEAD 자기 준수 복원 (self_lint 6건, HARD-CORE 4000자) | sonnet | `self_lint.py` all_ok=True, HARD-CORE ≤4000 chars |
| **WP1** | Evidence Contract 스키마 + `kernel.py`(5법칙) + 단위 테스트 | **opus** | 커널 재실행 시 verdict 비트 재현 테스트 통과 |
| **WP2** | `pipeline.manifest.json` 단일 매니페스트 + 스펙 드리프트 제거 | opus | 페이즈 수/폭이 매니페스트에서 유일 정의, 러너·감사가 참조 |
| **WP3** | `checks/` 레지스트리 + `meta_audit.py`(생성형) | sonnet | 신규 CheckSpec 추가 시 감사가 자동 열거(하드코딩 0) |
| **WP4** | 측정 코어 4점 producer (§7) + score.py/tournament/regression/cold wrap | **opus** | 각 producer가 backing artifact 없이는 Evidence 생성 불가 |
| **WP5** | 승격군 CheckSpec 재작성 (§8 promote) | sonnet | dacapo/deep/dry/define가 커널 경유 |
| **WP6** | 동결군 `status:frozen` 표기 + advisory 처리 (§8 freeze) | sonnet | 동결 체크가 종료를 막지 않음 확인 |
| **WP7** | fingerprint 근시 강화 (§10) | opus | 증거 없는 frontmatter가 커널에서 FAIL |
| **WP8** | **dogfood** — 커널을 theseus-self에 적용, 커널 도입 전/후 외부 벤치 controlled 비교 | opus | 임계 재설정 실측값 확보 + 외부 점수 delta 측정 |

**의존:** WP0 → WP1 → {WP2, WP3} → WP4 → {WP5, WP6, WP7} → WP8. WP1(커널)이 임계 경로.

---

## 13. 비목표 (이 문서가 다루지 않는 것)

- 15-페이즈 각각의 producer 구현 상세 (페이즈별 후속 스펙).
- 진짜 암호학적 서명 인프라 (fingerprint 원거리 — 별도 스펙).
- 외부 evaluator rubric과의 1:1 매핑 (감사 발견 30 — 별도 스펙).
- 멀티버스/앙상블의 *재설계* — 본 문서는 동결(게이트 자격 정지)까지만. 재설계는 A/B 실측 이후 별도 판단.
- 에이전트 모델 라우팅 재배분 (감사 발견 28 — 별도 판단).

---

## 14. 이 설계가 감사 발견에 대응하는 매핑 (역추적)

| 감사 테마 | 본 설계 대응 |
|---|---|
| T1 Self-rating 순환성 | §3 provenance 강제 + §4 법칙 1~2 + §5 producer 분리 + §7.1 임계 재설정 |
| T2 Enforcement 군비경쟁 | §6 생성형 레지스트리 + §11 반군비경쟁 제약(순감) |
| T3 복잡도·스펙 비결정성 | §11.3 단일 매니페스트 + §11.4 HEAD 자기 준수 |
| T4 콜드의 허구 | §7.4 격리 증거 producer + 값 기반 오염 검사 |
| T5 멀티버스 편익 미실증 | §8 동결 + §12 WP8 A/B |
| T6 의도 의미 검증 부재 | §7.4 재이해 diff 소비 + §9 페이즈 03/07 overlap 값 |
| T7 목적-수단 역배분 | §8 동결(viewer/budget) + §11.5 성공 측정 재정의 |

---

*본 문서는 설계 확정본이다. 사용자 리뷰 후 writing-plans로 구현 계획을 전개한다.*
