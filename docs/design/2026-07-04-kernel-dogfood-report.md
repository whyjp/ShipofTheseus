# Dogfood 보고 — 검증 커널을 harness 자기 코드에 적용 (WP8)

> **작성**: opus (WP8 실행)
> **일자**: 2026-07-04
> **대상**: theseus-harness `scoring/` 자기 코드
> **근거 설계**: `docs/design/2026-07-04-verification-kernel-design.md` (§11.5, §12 WP8, §13)
> **실행체**: `skills/theseus-harness/scoring/dogfood.py`
> **run dir**: `.ShipofTheseus/theseus-self-kernel-dogfood/run/`

---

## 0. 한 줄 요약

커널을 harness 자기 `scoring/` 코드에 실제로 돌렸고, meta_audit 은 **verdict = FAIL** 을
냈다. 이 FAIL 은 결함이 아니라 **정직한 관측 결과**다 — 15개 활성 체크 중 실측 backing
된 것은 5개(3 PASS + 2 NA)뿐이고, 8개는 상류 producer 부재로 evidence_missing FAIL,
2개는 동결 ADVISORY 다. 옛 자기평가(self_lint all_ok=True, self_score 1.0)가 **선언**이던
자리에, 새 커널은 값이 없으면 통과를 **거부**한다.

---

## 1. dogfood 실행 실측 결과 (grade G3, 15 활성 체크)

meta_audit **verdict: FAIL** (게이팅). 분류 카운트:

| 분류 | 개수 | 의미 |
|---|---:|---|
| PASS | 3 | 커널이 evidence 를 로드해 assertion 을 실제로 통과 |
| FAIL (실 assertion) | 0 | 실측 값이 술어를 위반한 것은 0건 |
| deficit (evidence_missing FAIL) | 8 | 상류 producer 부재로 측정 자체가 없음 → 법칙1 FAIL |
| NA (비게이팅) | 2 | evidence 로 입증된 적용 불가(적용성 false) |
| ADVISORY (비게이팅) | 2 | 동결 체크(§8) — verdict 를 종료 게이트로 쓰지 않음 |
| **실측 backing (measured_backed)** | **5 / 15** | PASS + 실FAIL + NA — 커널이 evidence 를 실제 평가 |

### 1.1 체크별 실측 표

| # | check_id | 분류 | 실측 값 | 근거 / 사유 |
|---|---|---|---|---|
| 1 | scoring.correctness | **deficit** | — | `intent_fidelity`(phase-09 Gate-1 판단값) 상류 producer 부재 → dimension 미emit. (junit 은 실제 실행됨: **tests_total=381, passed=381, failed=0** — 실측이지만 판단 차원 결손으로 dimension 봉인) |
| 2 | scoring.scope_fit | **deficit** | — | `files_mapped_to_todos` 결손. (`files_touched` 는 git diff 로 measurable) |
| 3 | scoring.solid | **deficit** | — | `modules_passing_solid` + `dip_violation` 결손. (`modules_total` 는 deep_module 브릿지로 승계됨 — 부분 승계 확인) |
| 4 | scoring.coverage | **deficit** | — | `be_coverage` 결손 (이 환경에 coverage 도구 미설치) |
| 5 | scoring.fe_be_parity | **NA** | — | `fe_side_exists=0`(단일 사이드) → 적용성 false. 침묵 0.0 채점이 아니라 비게이팅 NA |
| 6 | scoring.e2e | **deficit** | — | e2e junit artifact 부재 |
| 7 | plan.dacapo_threshold | **deficit** | — | tournament winner artifact 부재 (자기 코드 dogfood 에 토너먼트 없음) |
| 8 | plan.tournament_independence | **deficit** | — | shadow-grade artifact 부재 |
| 9 | sprint.regression | **deficit** | — | prior/current score 시계열 부재 |
| 10 | cold.isolation | **NA** | computed_overlap = **0.187** | `dispatch_log_present=0` → 적용성 false (§7.4). overlap 은 실측(v0919 `07-cold-read.md` vs `06-plan.md` Jaccard, 토큰 173 vs 462) |
| 11 | quality.deep_module | **PASS** | max_shallow_ratio = **0.205** | **module_count=61**, 최대 얕은비율 0.205 ≤ 0.4 ✓ (Ousterhout Ch.4 "Modules Should Be Deep") |
| 12 | quality.dry | **PASS** | violation_ratio = **0.0068** | total_ngrams=14281, violation_count=97, 비율 0.0068 ≤ 0.05 ✓; scanned_line_count=16110 (Pragmatic Programmer Tip 11) |
| 13 | quality.define_errors | **PASS** | raised−unhandled = **9** | module_count=61, raised_type_count=9, **unhandled_type_count=0** ✓, bare_except_vacuous=False ✓ (Ousterhout Ch.10) |
| 14 | frozen.multiverse_width_benefit | **ADVISORY** | — | status:frozen, kernel_result=FAIL(evidence_missing), 비게이팅 (§8) |
| 15 | frozen.viewer_mandatory | **ADVISORY** | — | status:frozen, kernel_result=FAIL, 비게이팅 (§8) |

**핵심:** 3개 품질 체크는 harness 자기 `scoring/` 61개 모듈을 **실제로 스캔한 값**으로
PASS 했고, 실 assertion 위반은 0건이었다. 나머지 8개 deficit 은 상류 판단/프로세스
producer 가 없어 커널이 통과를 거부한 것이며, 상상 값을 주입해 통과시키지 않았다.

### 1.2 emit 된 evidence (실 backing artifact)

```
evidence/quality.deep_module.json        (+ .report.json — per-module 상세)
evidence/quality.dry.json                (+ .report.json)
evidence/quality.define_errors.json      (+ .report.json)
evidence/cold.isolation.json             (+ .report.json)
evidence/scoring.fe_be_parity.json
results/junit.xml                        (381 passed, pytest exit 0)
quality/gate_meta_audit.json             (meta_audit verdict)
```

모든 measured 값의 `artifact_path` 는 위 디스크 파일을 가리키고 그 실 sha256 이
`artifact_digests` 에 pin 되어, 커널 법칙3이 재판정 시 디스크와 대조한다.
**재현성 확인**: 같은 `--measured-at`/`--verified-at` 로 2회 실행 시 gate_meta_audit.json
의 verdict/value/reasons 가 비트 단위로 동일했다(project_root 경로 제외).

---

## 2. Before / After — 선언에서 실행-결과 값으로

| 축 | 옛 자기평가 (before) | 새 커널 측정 (after) |
|---|---|---|
| correctness | `inputs.json` 손으로 작성 → `score.py` 산술 → 임의 숫자 | pytest 실제 실행 → junit 파싱 (381/381) → digest pin |
| solid / scope | `_safe_div(default=1.0)` → files_touched=0 이면 만점 | `files_touched>0` 술어 + backing 없으면 emit 자체 불가 → 무노동 만점 **구조적 봉쇄** |
| quality | self_lint C-룰 = 컨벤션 문서에 키워드 grep | 61 모듈 실 스캔: interface/functional 비율 0.205, DRY 0.0068, 예외 9종 전부 handle |
| verdict 원천 | self_lint all_ok=True (마크다운/인덱스 텍스트 패턴 정합) | 커널 5법칙 — evidence 없으면 FAIL, 값 술어 위반 없으면 PASS |
| 무증거 | `skipped == pass` (측정 안 하면 통과) | `skipped == FAIL` (측정 안 하면 실패, §2 원칙2) |

**한 문장 대비:** 옛 경로는 올바른 마크다운 키워드만 있으면 **1.0/all_ok 를 선언**했다.
새 경로는 backing producer 가 없는 correctness/solid/scope/e2e 를 **1.0 으로 지어내지 않고
evidence_missing FAIL 로 거부**한다 — README ⓐⓑ 가 자백한 "self_lint/self_score 는 텍스트
패턴 정합이지 LLM 행동 실증이 아니다"를, 이 dogfood 는 실행-결과 값으로 대체해 보인다.

---

## 3. 정직한 한계 (측정 못 하는 것을 명시)

1. **외부 벤치 점수 delta: 미측정.** 설계 §11.5 는 성공을 "지시 질량 감소 + 외부 점수의
   controlled 비교"로 정의하지만, 이 환경에는 외부 evaluator 가 없다. 외부 rubric 1:1
   매핑은 설계 §13 의 명시적 비목표다. **이 dogfood 는 내부 evidence-backed verdict 와
   지시 질량만 측정하며, 외부 품질 delta 는 측정하지 않는다.** 커널 도입 전/후 외부
   점수 비교는 외부 evaluator 가 붙는 별도 작업으로 남는다.

2. **deficit 8종의 원인.** `intent_fidelity`, `files_mapped_to_todos`,
   `modules_passing_solid`, `dip_violation` 은 phase-09 Gate-1 의도충실도·todo 매핑·SOLID/DIP
   모듈 분석 같은 **판단-게이트 파생 값**으로, 이를 값으로 낳는 `measure_*` producer 가
   아직 없다. measure_submission 은 이를 `--from-evidence` 로만 승계하도록 설계돼 있어
   backing 이 없으면 상상하지 않고 결손 처리한다(정직한 부분 상태). dacapo/tournament/
   regression 은 자기 코드 dogfood 에 토너먼트·점수 시계열 자체가 없어 결손이다.

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
  실행 비트 재현).
- 품질 메트릭이 자기 신고가 아니라 **디스크 artifact 에서 실측**된다 — 61 모듈,
  깊이비율 0.205, DRY 0.0068, 예외 9종 전부 handle.
- **"증거 없음 = FAIL"** 법칙이 정확히 발동한다 — backing producer 없는 8차원이
  evidence_missing FAIL 을 받고, 지어낸 pass 로 새지 않는다. `_safe_div(default=1.0)`
  무노동 만점 경로가 구조적으로 닫혔다.

**증명하지 못하는 것:**
- **외부 벤치 점수 개선** — 외부 evaluator 부재(§3.1).
- 전체 15-페이즈 파이프라인 동작 — 자기 코드에는 phase 08/09/03 차원만 실측 가능하고,
  프로세스 게이트(06/10)는 자기 코드 analog 이 없다.
- deficit 차원이 **언젠가 채워진다는 보장** — 판단-게이트 producer 는 별도 후속 스펙(§13).
- 지시 질량이 **후속 페이즈에서도 낮게 유지된다는 보장** — WP0 baseline 만 측정.

---

## 6. 재현 방법

```bash
python skills/theseus-harness/scoring/dogfood.py \
    --measured-at 2026-07-04T00:00:00+00:00
# → .ShipofTheseus/theseus-self-kernel-dogfood/run/{evidence,results,quality}/
#   quality/gate_meta_audit.json 에 verdict, dogfood_summary.json 에 분류표.
```

검증: `pytest skills/theseus-harness/scoring/ -q` (384 passed),
`python skills/theseus-harness/scoring/self_lint.py` (all_ok=True).
