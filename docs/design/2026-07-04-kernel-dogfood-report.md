# Dogfood 보고 — 검증 커널을 harness 자기 코드에 적용 (WP8)

> **작성**: opus (WP8 실행)
> **일자**: 2026-07-04
> **대상**: theseus-harness `scoring/` 자기 코드
> **근거 설계**: `docs/design/2026-07-04-verification-kernel-design.md` (§11.5, §12 WP8, §13)
> **실행체**: `skills/theseus-harness/scoring/dogfood.py`
> **run dir**: `.ShipofTheseus/theseus-self-kernel-dogfood/run/`
> **갱신**: 2026-07-05 — 판단-게이트 producer 적용 재실행 (JW5,
> `docs/design/2026-07-05-judgment-gate-producers-{design,plan}.md`). `gate.intent_fidelity`/
> `gate.scope_map`/`gate.solid_static` 3 producer 를 scoring 자기 코드에 실제로 태워
> `scoring.correctness`/`scope_fit`/`solid` 3개 deficit 을 실측 backing 으로 전환한 값을
> 아래 §1/§1.1/§1.2/§2/§3 에 반영했다(8 deficit → 5 deficit, measured_backed 5 → 8;
> PASS 3 → 5 — correctness/solid 는 실측 PASS 전환, scope_fit 은 clean 체크아웃 기준
> **실 assertion FAIL** 로 전환. §1.1 #2). 본 보고의 모든 헤드라인 카운트는 **커밋된
> clean 체크아웃 기준(canonical)** 이다 — 독자가 체크아웃해 재현하는 바로 그 상태.

---

## 0. 한 줄 요약

커널을 harness 자기 `scoring/` 코드에 실제로 돌렸고, meta_audit 은 **verdict = FAIL** 을
냈다. 이 FAIL 은 결함이 아니라 **정직한 관측 결과**다 — clean 체크아웃(canonical) 기준
15개 활성 체크 중 실측 backing 된 것은 **8개(5 PASS + 1 실 assertion FAIL + 2 NA)**이고,
**5개**는 상류 producer 부재로 evidence_missing FAIL, 2개는 동결 ADVISORY 다. 실 FAIL
1건은 `scoring.scope_fit` — self-dogfood 에는 진짜 제출물 diff 가 없어 clean 체크아웃에서
`files_touched=0` → "no files touched" 위반이 결정적으로 관측된다(무노동 만점 봉쇄가
실제로 발동한 것이다. §1.1 #2). 옛 자기평가(self_lint all_ok=True, self_score 1.0)가
**선언**이던 자리에, 새 커널은 값이 없으면 통과를 **거부**하고, 노동이 없으면 만점을
**거부**한다.

(2026-07-05 갱신: 최초 dogfood 실행 시점엔 판단-게이트 producer 부재로 correctness/
scope_fit/solid 3개도 evidence_missing deficit 이었다. JW1~JW4 가 `claims.py` 공유
backing 검증 코어 + `measure_intent_fidelity`/`measure_scope_map`/`measure_solid_static`
producer 를 신설했고, JW5 가 scoring 자기 코드에 대한 참인 선언 아티팩트
(`scoring/dogfood_inputs/{intent-criteria,plan-todos,solid-contract}.json`)를 저작해
이 dogfood 에 적용했다 — 그 결과가 아래 값이다. 3개 모두 deficit 에서 **실측 backing 판정**
으로 전환됐고, 그 중 correctness/solid 는 PASS, scope_fit 은 clean 체크아웃에서 실 FAIL 이다.)

---

## 1. dogfood 실행 실측 결과 (grade G3, 15 활성 체크) — 2026-07-05 재실행

meta_audit **verdict: FAIL** (게이팅). 분류 카운트(판단-게이트 producer 적용 후,
**clean 체크아웃 기준 canonical** — §6 재현 상태와 동일):

| 분류 | 개수 | 의미 |
|---|---:|---|
| PASS | 5 | 커널이 evidence 를 로드해 assertion 을 실제로 통과 (이전 3 → 5, +correctness/solid) |
| FAIL (실 assertion) | 1 | `scoring.scope_fit` — clean 체크아웃에서 `files_touched=0` → "no files touched" 술어 위반 (§1.1 #2) |
| deficit (evidence_missing FAIL) | 5 | 상류 producer 부재로 측정 자체가 없음 → 법칙1 FAIL (이전 8 → 5) |
| NA (비게이팅) | 2 | evidence 로 입증된 적용 불가(적용성 false) |
| ADVISORY (비게이팅) | 2 | 동결 체크(§8) — verdict 를 종료 게이트로 쓰지 않음 |
| **실측 backing (measured_backed)** | **8 / 15** | PASS + 실FAIL + NA = 5+1+2 — 커널이 evidence 를 실제 평가 (이전 5 → 8) |

**최초 실행(2026-07-04, WP8) 대비 변화**: `intent_fidelity`/`files_mapped_to_todos`/
`modules_passing_solid`+`dip_violation` 4개 판단-파생 키가 결손에서 실측 backing 으로
전환되어, 그 값을 assertion 에 태우는 `scoring.correctness`/`scope_fit`/`solid` 3개
CheckSpec 이 deficit 에서 **실측 판정**으로 바뀌었다 — correctness(1.0)/solid(0.0308)
는 트리 상태 무관 안정적 PASS, scope_fit 은 clean 체크아웃에서 실 assertion FAIL
(과장 없이 그대로 보고한다). measured_backed 8/15 와 deficit 5 는 트리 상태 무관
불변이다. 나머지 5개 deficit(coverage/e2e/dacapo/tournament/regression)은 이 스펙
(JW1~5)의 비목표(도구·fixture 부재)라 그대로 남는다.

### 1.1 체크별 실측 표

| # | check_id | 분류 | 실측 값 | 근거 / 사유 |
|---|---|---|---|---|
| 1 | scoring.correctness | **PASS** (이전 deficit) | value = **1.0** | `intent_fidelity`=1.0(`gate.intent_fidelity` producer — `scoring/dogfood_inputs/intent-criteria.json` 의 참인 claim 2건(required, file/test kind) + 1건(optional, file kind) 전부 claims.py 로 디스크 재검사되어 검증됨). **tests_total=476, tests_passed=476, tests_failed=0**. value = (476/476)×1.0 = 1.0. **트리 상태 무관, 안정** — clean/dirty 어느 체크아웃에서도 동일 |
| 2 | scoring.scope_fit | **FAIL (실 assertion, clean 체크아웃 기준)** (이전 deficit) | files_touched = **0** | `gate.scope_map` producer 는 `git diff --name-only HEAD` 를 실측한다. **이 체크는 트리 상태 의존**: `.ShipofTheseus/` 가 gitignore 라 dogfood 실행 자체는 트리를 더럽히지 않으므로, 커밋된 clean 체크아웃(= 독자가 재현하는 canonical 상태)에서는 `files_touched=0`, `files_mapped_to_todos=0` → 커널 assertion `files_touched > 0` 위반("no files touched")이 **결정적으로** 관측된다. **정직 고지**: 미커밋 편집이 있는 dirty tree 에서는 그 diff 를 측정해 PASS 가 될 수 있다 — 예컨대 JW5 가 이 문서를 저작하던 시점엔 `dogfood.py`/`test_dogfood.py` 가 tracked-modified 라 value=1.0 이 관측됐다. self-dogfood 에는 진짜 제출물 diff 가 없어 이 체크의 값은 **퇴화적(degenerate)** 이다 — `measure_scope_map` producer 자체의 유효성은 JW3 의 실제 diff fixture 테스트가 증명하며, 이 self-run 이 증명하는 것이 아니다. 이 FAIL 은 옛 `_safe_div(default=1.0)` 가 무노동에 만점을 주던 자리에서 커널 봉쇄가 실제 발동함을 보이는 관측이다 |
| 3 | scoring.solid | **PASS** (이전 deficit) | value = **0.0308** | `modules_passing_solid`=2, `modules_total`=65, `dip_violation`=0 (`gate.solid_static` producer — `solid-contract.json`의 `producers/_evidence_common.py`(DIP `absent_import:requests` + SRP `public_class≤0`)·`producers/claims.py`(DIP `absent_import:sqlite3` + `import_of:Callable` + SRP `public_class≤2`) 참인 claim 전부 검증). value = 2/65 = 0.0308. **트리 상태 무관, 안정** — code_root 디스크 스캔 기반 |
| 4 | scoring.coverage | **deficit** | — | `be_coverage` 결손 (이 환경에 coverage 도구 미설치) — 이 스펙의 비목표 |
| 5 | scoring.fe_be_parity | **NA** | — | `fe_side_exists=0`(단일 사이드) → 적용성 false. 침묵 0.0 채점이 아니라 비게이팅 NA |
| 6 | scoring.e2e | **deficit** | — | e2e junit artifact 부재 — 이 스펙의 비목표 |
| 7 | plan.dacapo_threshold | **deficit** | — | tournament winner artifact 부재 (자기 코드 dogfood 에 토너먼트 없음) — 이 스펙의 비목표 |
| 8 | plan.tournament_independence | **deficit** | — | shadow-grade artifact 부재 — 이 스펙의 비목표 |
| 9 | sprint.regression | **deficit** | — | prior/current score 시계열 부재 — 이 스펙의 비목표 |
| 10 | cold.isolation | **NA** | computed_overlap = **0.187** | `dispatch_log_present=0` → 적용성 false (§7.4). overlap 은 실측(v0919 `07-cold-read.md` vs `06-plan.md` Jaccard, 토큰 173 vs 462) |
| 11 | quality.deep_module | **PASS** | max_shallow_ratio = **0.205** | **module_count=65**(JW1~JW4 가 producer 파일 4개 신설해 61→65), 최대 얕은비율 0.205 ≤ 0.4 ✓ (Ousterhout Ch.4 "Modules Should Be Deep") |
| 12 | quality.dry | **PASS** | violation_ratio = **0.00776** | total_ngrams=15208, violation_count=118, 비율 0.00776 ≤ 0.05 ✓; scanned_line_count=17155 (Pragmatic Programmer Tip 11) |
| 13 | quality.define_errors | **PASS** | raised−unhandled = **13** | module_count=65, raised_type_count=13, **unhandled_type_count=0** ✓, bare_except_vacuous=False ✓ (Ousterhout Ch.10) |
| 14 | frozen.multiverse_width_benefit | **ADVISORY** | — | status:frozen, kernel_result=FAIL(evidence_missing), 비게이팅 (§8) |
| 15 | frozen.viewer_mandatory | **ADVISORY** | — | status:frozen, kernel_result=FAIL, 비게이팅 (§8) |

**핵심:** 5개 체크(품질 3종 + correctness/solid)가 harness 자기 `scoring/` 65개 모듈을
**실제로 스캔·검사한 값**으로 PASS 했다 — 특히 correctness(1.0)와 solid(0.0308)는 트리
상태와 무관한 안정적 실측값으로, deficit→PASS 전환이 **의미 있게 실증**된 두 축이다.
실 assertion 위반은 1건(scope_fit, clean 체크아웃 기준 files_touched=0)으로, 이는 자기
코드 dogfood 에 제출물 diff 가 없다는 구조적 사실을 커널이 만점 대신 FAIL 로 관측한
것이다. correctness/scope_fit/solid 는 2026-07-04 최초 실행 시 deficit 이었으나, JW1~JW4 가
`claims.py` 공유 backing 검증 코어(test/symbol/diff/file/absent_import/import_of/
symbol_count_max 7종 kind) + 3 producer(`measure_intent_fidelity`/`measure_scope_map`/
`measure_solid_static`)를 신설하고, JW5 가 scoring 자기 코드에 대한 **참인** 선언
아티팩트를 저작해 dogfood 에 적용한 결과 실측 backing 으로 전환됐다(§0 갱신 이력).
나머지 5개 deficit(coverage/e2e/dacapo/tournament/regression)은 상류 판단 producer
가 아니라 도구·fixture 부재이며 이 스펙의 명시적 비목표(§8)라 그대로 남는다.

### 1.2 emit 된 evidence (실 backing artifact)

```
evidence/quality.deep_module.json        (+ .report.json — per-module 상세)
evidence/quality.dry.json                (+ .report.json)
evidence/quality.define_errors.json      (+ .report.json)
evidence/cold.isolation.json             (+ .report.json)
evidence/scoring.fe_be_parity.json
evidence/gate.intent_fidelity.json       (+ .report.json — per-criterion 상세, JW5 신규)
evidence/gate.scope_map.json             (+ .report.json — per-file 매핑 상세, JW5 신규)
evidence/gate.solid_static.json          (+ .report.json — per-module per-claim 상세, JW5 신규)
evidence/scoring.correctness.json        (measure_submission 이 gate.intent_fidelity 승계)
evidence/scoring.scope_fit.json          (measure_submission 이 gate.scope_map 승계)
evidence/scoring.solid.json              (measure_submission 이 gate.solid_static 승계)
results/junit.xml                        (476 passed, pytest exit 0)
quality/gate_meta_audit.json             (meta_audit verdict)
```

모든 measured 값의 `artifact_path` 는 위 디스크 파일을 가리키고 그 실 sha256 이
`artifact_digests` 에 pin 되어, 커널 법칙3이 재판정 시 디스크와 대조한다.
**재현성 확인**: 같은 `--measured-at`/`--verified-at` 로 2회 실행 시 gate_meta_audit.json
의 verdict/value/reasons 가 비트 단위로 동일했다(project_root 경로 제외). 단, 15개 중
`scoring.scope_fit` 하나만 working-tree diff 에 의존하므로(§1.1 #2) 비트 재현은 **동일
트리 상태 내**에서 성립한다 — clean 체크아웃끼리는 항상 동일(canonical), 나머지 14개는
트리 상태와도 무관하다.

---

## 2. Before / After — 선언에서 실행-결과 값으로

| 축 | 옛 자기평가 (before) | 새 커널 측정 (after, 2026-07-05 판단-게이트 적용 후) |
|---|---|---|
| correctness | `inputs.json` 손으로 작성 → `score.py` 산술 → 임의 숫자 | pytest 실제 실행 → junit 파싱 (476/476) + `intent_fidelity` 는 `claims.py` 가 criteria 의 file/test backing 을 디스크에서 재검사해 이산화(1.0/0.7/0.0) → digest pin |
| intent_fidelity | 상류 producer 부재 → **결손**(evidence_missing) | `gate.intent_fidelity` producer — 참인 criteria(required 2 + optional 1, 전부 검증) → value=1.0 |
| solid / scope | `_safe_div(default=1.0)` → files_touched=0 이면 만점 | `files_touched>0` 술어(무노동 만점 **구조적 봉쇄** 유지 — clean 체크아웃 self-dogfood 에서 files_touched=0 → 실제로 FAIL 이 발동한다, §1.1 #2) + `files_mapped_to_todos`/`modules_passing_solid`/`dip_violation` 은 `gate.scope_map`/`gate.solid_static` 이 plan-todos glob·solid-contract claim 을 각각 git diff·AST 로 실측해 emit |
| quality | self_lint C-룰 = 컨벤션 문서에 키워드 grep | 65 모듈 실 스캔: interface/functional 비율 0.205, DRY 0.00776, 예외 13종 전부 handle |
| verdict 원천 | self_lint all_ok=True (마크다운/인덱스 텍스트 패턴 정합) | 커널 5법칙 — evidence 없으면 FAIL, 값 술어 위반 없으면 PASS |
| 무증거 | `skipped == pass` (측정 안 하면 통과) | `skipped == FAIL` (측정 안 하면 실패, §2 원칙2) |

**한 문장 대비:** 옛 경로는 올바른 마크다운 키워드만 있으면 **1.0/all_ok 를 선언**했다.
새 경로는 backing producer 가 없던 2026-07-04 시점엔 correctness/solid/scope/e2e 를
**1.0 으로 지어내지 않고 evidence_missing FAIL 로 거부**했고, 2026-07-05 시점엔
correctness/solid 2개가 `claims.py` 기계 재검사를 통과한 **참인 claim** 으로 실측 PASS
전환됐으며, scope 는 실측 backing 으로 전환되되 clean 체크아웃에선 files_touched=0 을
만점이 아니라 **실 FAIL 로 관측**한다(e2e 등 5개는 여전히 도구·fixture 부재로 결손) —
README ⓐⓑ 가 자백한 "self_lint/self_score 는 텍스트 패턴 정합이지 LLM 행동 실증이
아니다"를, 이 dogfood 는 실행-결과 값으로 대체해 보인다.

---

## 3. 정직한 한계 (측정 못 하는 것을 명시)

1. **외부 벤치 점수 delta: 미측정.** 설계 §11.5 는 성공을 "지시 질량 감소 + 외부 점수의
   controlled 비교"로 정의하지만, 이 환경에는 외부 evaluator 가 없다. 외부 rubric 1:1
   매핑은 설계 §13 의 명시적 비목표다. **이 dogfood 는 내부 evidence-backed verdict 와
   지시 질량만 측정하며, 외부 품질 delta 는 측정하지 않는다.** 커널 도입 전/후 외부
   점수 비교는 외부 evaluator 가 붙는 별도 작업으로 남는다.

2. **deficit 5종(갱신: 이전 8종)의 원인.** 2026-07-04 최초 실행 시점엔
   `intent_fidelity`, `files_mapped_to_todos`, `modules_passing_solid`, `dip_violation`
   4개 판단-파생 값도 결손이었다 — phase-09 Gate-1 의도충실도·todo 매핑·SOLID/DIP 모듈
   분석을 값으로 낳는 `measure_*` producer 가 없었기 때문이다. `docs/design/
   2026-07-05-judgment-gate-producers-{design,plan}.md`(JW1~JW5)가 `claims.py` 공유
   backing 검증 코어 + `measure_intent_fidelity`/`measure_scope_map`/`measure_solid_static`
   3 producer 를 신설했고, 이 dogfood 가 scoring 자기 코드에 대한 참인 선언 아티팩트로
   그 producer 를 실제로 적용해 4키 전부 실측 backing 으로 전환했다(§1.1 — 단
   `files_mapped_to_todos` 는 self-run 에 제출물 diff 가 없어 clean 체크아웃에서 0 이라는
   퇴화 값이고, 그 결과 scope_fit 은 실 FAIL 이다. §1.1 #2). 남은 5개
   deficit — `be_coverage`(coverage 도구 미설치), e2e junit, dacapo/tournament(토너먼트
   artifact), regression(점수 시계열) — 은 **판단이 아니라 도구·fixture 부재**이며, 이
   스펙(JW1~5)의 명시적 비목표(§8)라 backing producer 자체가 계획돼 있지 않다.
   measure_submission 은 여전히 `--from-evidence` 로만 승계하도록 설계돼 있어 backing 이
   없으면 상상하지 않고 결손 처리한다(정직한 부분 상태 — 회귀 없음).

3. **cold.isolation NA 의 이유.** 이 저장소의 콜드 세션은 LLM 주도라 구조화된 dispatch
   로그가 없다(§7.4). 그래서 `prior_context_token_count==0`·`allowed_file_count>=1` 격리
   assertion 은 게이팅되지 못하고, 언어 무관 `computed_overlap`(0.187)만 실측된다.
   dispatch_log_present=0 → NA(비게이팅). — 참고로 overlap 대조에 쓴 두 파일은 v0919
   self-run 의 실 phase-07 계획 재이해/원본 계획 쌍이다(scoring 코드 자체의 cold re-read
   는 없어, producer 를 실 파일로 end-to-end 태워 NA 경로를 실증하기 위한 입력이다).

4. **frozen.\* ADVISORY 의 이유.** 멀티버스 폭·viewer 편익 A/B producer
   (`measure_multiverse_width_ab`, `measure_viewer_benefit_ab`)는 미구현이다. 설계 §8
   동결에 따라 커널이 이를 **비게이팅(advisory)** 으로 처리해, 편익이 값으로 실증되기
   전까지 종료를 막지 않는다. kernel_result 는 FAIL 이지만 정책 레이어가 verdict 에서
   제외한다.

---

## 4. 지시 질량 (§11.5) — "줄인다"의 실측 근거

`§11.5(a)` phase 진입 지시문 chars 감소의 가장 직접적 실측 지점은 **always-load 계층인
`HARD-CORE.md`** 다:

| 시점 | HARD-CORE.md 크기 | 근거 |
|---|---:|---|
| 감사 시점 (before) | ~**7,211 chars** (4,000 cap 초과) | 설계 §11.4 발견 15 — "마감됐으나 자기 룰 위반" |
| WP0 복원 후 | (commit `7636c27`) | self_lint C-HC1 통과로 복원 |
| 현재 HEAD | **3,888 chars** | 파일 실측 + self_lint `all_ok=True` |

**7,211 → 3,888 chars** 는 always-load 지시 질량의 **실측 감소**이며, §11.5 "줄인다,
늘리지 않는다"의 성공 지표를 선언이 아니라 값으로 만족한다.

**정직 고지 (반군비경쟁 §11.1):** 이 dogfood 자체는 self_lint 의 prose C-룰을 삭제하지
않는다 — 그 순감(net-reduce)은 페이즈별 후속 마이그레이션(§9)의 몫이다. 여기서는 커널이
verdict 역할을 값 기반으로 **대체 가능함**을 실행으로 확립하고, always-load 계층의 감소
baseline 만 측정했다. 새 체크는 producer+CheckSpec 파일로 추가되므로 파일 수는 늘지만,
그 목적은 grep-C-룰의 대체이지 병렬 증설이 아니다.

---

## 5. 이 dogfood 가 증명하는 것 / 증명하지 못하는 것

**증명하는 것:**
- 커널이 harness 실 코드에서 **끝까지 돌아 결정적·evidence-backed verdict** 를 낸다(2회
  실행 비트 재현 — 2026-07-05 재실행에서도 `gate_meta_audit.json` 바이트 동일 재확인).
- 품질 메트릭이 자기 신고가 아니라 **디스크 artifact 에서 실측**된다 — 65 모듈,
  깊이비율 0.205, DRY 0.00776, 예외 13종 전부 handle.
- **판단-게이트 값도 자기 신고가 아니라 기계 재검사로 실측 가능함** — `intent_fidelity`/
  `files_mapped_to_todos`/`modules_passing_solid`/`dip_violation` 4키가 `claims.py`
  (test/symbol/diff/file/absent_import/import_of/symbol_count_max 화이트리스트 검증)로
  디스크에서 재검사되어 correctness/scope_fit/solid 3개 CheckSpec 이 deficit 에서 실측
  판정으로 전환됐다(2026-07-05, §1.1) — correctness(1.0)/solid(0.0308)는 트리 상태 무관
  안정적 PASS, scope_fit 은 clean 체크아웃 기준 실 FAIL.
- **"증거 없음 = FAIL"** 법칙이 정확히 발동한다 — backing producer 없는 나머지 5차원
  (coverage/e2e/dacapo/tournament/regression)이 evidence_missing FAIL 을 받고, 지어낸
  pass 로 새지 않는다. `_safe_div(default=1.0)` 무노동 만점 경로가 구조적으로 닫혔고,
  clean 체크아웃 self-dogfood 의 scope_fit 실 FAIL(files_touched=0)이 그 봉쇄가 실제로
  발동함을 관측으로 보인다.

**증명하지 못하는 것:**
- **외부 벤치 점수 개선** — 외부 evaluator 부재(§3.1).
- **scope_fit 의 실 제출물 판별력** — self-dogfood 엔 진짜 제출물 diff 가 없어 값이
  퇴화적(clean 체크아웃에서 files_touched=0)이다. `measure_scope_map` 의 유효성 증명은
  JW3 의 실제 diff fixture 테스트 몫이며, 이 self-run 은 무노동 봉쇄 발동만 보인다(§1.1 #2).
- 전체 15-페이즈 파이프라인 동작 — 자기 코드에는 phase 08/09/03 차원만 실측 가능하고,
  프로세스 게이트(06/10)는 자기 코드 analog 이 없다.
- 남은 5개 deficit 차원(coverage/e2e/dacapo/tournament/regression)이 **언젠가 채워진다는
  보장** — 이 스펙(JW1~5)의 명시적 비목표(§8)이며 별도 후속 작업이 필요하다.
- claim 의 **충분성**(선언된 기준이 의도/SOLID 를 얼마나 덮는가) — 기계 보증되는 것은
  claim 의 *진위*뿐이며, 충분성은 phase wiring·리뷰의 몫이다(설계 §7 정직 고지).
- 지시 질량이 **후속 페이즈에서도 낮게 유지된다는 보장** — WP0 baseline 만 측정.

---

## 6. 재현 방법

```bash
python skills/theseus-harness/scoring/dogfood.py \
    --measured-at 2026-07-05T00:00:00+00:00 --verified-at 2026-07-05T00:00:00+00:00
# → .ShipofTheseus/theseus-self-kernel-dogfood/run/{evidence,results,quality}/
#   quality/gate_meta_audit.json 에 verdict, dogfood_summary.json 에 분류표.
# gate.intent_fidelity/gate.scope_map/gate.solid_static 선언 아티팩트는
#   skills/theseus-harness/scoring/dogfood_inputs/*.json 기본값을 쓴다
#   (--intent-criteria/--plan-todos/--solid-contract 로 재정의 가능).
```

**clean 체크아웃(커밋 직후 상태)에서 위 명령은 본 보고의 canonical 카운트를 그대로
재현한다**: verdict=**FAIL**, PASS=**5**, 실 FAIL=**1**(`scoring.scope_fit` — "no files
touched", files_touched=0), deficit=**5**, NA=**2**, ADVISORY=**2**,
measured_backed=**8/15**. `.ShipofTheseus/` 는 gitignore 라 dogfood 실행 자체가 트리를
더럽히지 않으므로 이 결과는 결정적이다. 미커밋 편집이 트리에 있으면 15개 중
`scoring.scope_fit` 하나만 그 diff 를 측정해 값이 달라질 수 있다(§1.1 #2) — 나머지
14개 체크와 measured_backed/deficit 카운트는 트리 상태 무관이다.

검증: `pytest skills/theseus-harness/scoring/ -q` (476 passed, 2026-07-05 재실행),
`python skills/theseus-harness/scoring/self_lint.py` (all_ok=True).
