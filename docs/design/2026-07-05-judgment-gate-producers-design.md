# 설계 문서 — 판단-게이트 Producer (deficit 충전 Spec 1)

> **작성**: Claude Fable 5 (설계 검토·확정)
> **구현 위임**: opus/sonnet (본 문서 §9 작업 패키지 기준)
> **일자**: 2026-07-05
> **대상 저장소**: Ship of Theseus (theseus-harness)
> **선행 설계**: `docs/design/2026-07-04-verification-kernel-design.md` (검증 커널 §2/§4/§5/§7.1)
> **동기 근거**: `docs/design/2026-07-04-kernel-dogfood-report.md` §1.1(deficit 표), §3.2(원인 분석)

---

## 0. 이 문서가 확정하는 것 (범위 계약)

dogfood 보고가 낸 `verdict=FAIL` 의 8개 deficit 중 **판단-파생 4키**를 실측 backing 으로
전환하는 상류 producer 를 확정한다. 커널·measure_submission·CheckSpec·manifest 는
**무수정** — 이들은 이미 `--from-evidence` 승계를 기다리고 있고, 결손인 것은 오직 그
승계를 채울 상류 producer 다.

대상 4키 → 해소되는 deficit 3종:

| 판단-파생 키 | 소비 CheckSpec | 현재 상태 |
|---|---|---|
| `intent_fidelity` | `scoring.correctness` | deficit (phase-09 Gate-1 판단값 producer 부재) |
| `files_mapped_to_todos` | `scoring.scope_fit` | deficit (todo↔파일 매핑 producer 부재) |
| `modules_passing_solid` + `dip_violation` | `scoring.solid` | deficit (SOLID/DIP 분석 producer 부재) |

(`modules_total` 은 `measure_deep_module` 브릿지로 이미 승계됨 — 본 producer 는 동일
enumeration 을 공유해 정합만 유지한다.)

**비목표(§8):** coverage/e2e/dacapo/tournament/regression deficit — 이들은 판단이 아니라
도구·fixture 부재이므로 본 스펙 밖. solid-contract 미제공 시 zero-config AST 바닥값.
phase 01/04/06/08 프롬프트 wiring(선언 아티팩트 저작 지시). 외부 벤치 harness(별도 Spec 2).

---

## 1. 문제 — "판단"을 자기 신고 없이 값으로

검증 커널 설계 §2 원칙1은 위반 불가다: **"LLM 이 산출한 숫자·판정은 게이트 입력이 될 수
없다."** 그런데 `intent_fidelity`(구현이 clarify 된 의도를 충족했는가)·SOLID 준수는
본질적으로 *의미 판단*이다. 판단 producer 가 LLM 자기평가를 한 겹 감싸기만 하면 커널
전체가 무의미해진다(감사 T1 self-rating 순환성의 재발).

dogfood `measure_deep_module` docstring 이 이미 정직한 하한을 세웠다: deep-module 비율은
SOLID 와 다른 차원이고 의존 방향을 전혀 안 보므로 `modules_passing_solid`/`dip_violation`
을 **승계하지 않고 결손 처리**한다. 즉 이 값들은 *실제로 그 개념을 기계 측정하는* 새
producer 가 낳아야 하며, 억지 매핑이나 자기 신고로 채워선 안 된다.

---

## 2. 승인된 메커니즘 — 구조화 기준 + 기계 backing

판단을 **개별 반증가능한 claim 으로 분해**하고, 각 claim 은 *무엇을 볼지*(mechanical
backing)만 선언한다. producer 는 각 backing 을 **디스크에서 실제 검사해** 통과 여부를
산출한다. 측정값 = 기계 검증된 claim 의 함수이지 LLM 숫자가 아니다.

```
[상류 선언 아티팩트]  LLM 저작 · claim(무엇을 볼지)만 · pass/fail·점수 절대 없음
        │
        ▼   measure_*.py  (producer)
[claims.py 로 디스크 실검사]  test junit 조회 · git diff 조회 · AST import 조회 · 심볼 조회
        │
        ▼
[Evidence Record]  measured.<key> = 기계 검증 결과의 함수 + provenance(검사 리포트 digest)
        │
        ▼   measure_submission --from-evidence (무수정, 이미 대기 중)
[기존 scoring CheckSpec]  커널이 값 술어로 최종 판정
```

**위반 불가 불변식 (§2 원칙1 경계):**
1. 상류 아티팩트는 `backing.ref`(무엇을 찾을지)만 담는다. `verified:true` 같은 판정 필드를
   담으면 그 자체가 계약 위반이다 — producer 는 아티팩트의 판정을 절대 신뢰하지 않고
   claims.py 로 재검사한다.
2. producer 는 verdict/score 를 내지 않는다(§5 producer/kernel 분리). 오직 provenance 붙은
   measured 값만 emit. 이산화·집계는 "측정된 claim 검증 결과의 결정 함수"일 뿐 판단이 아니다.
3. claim 하나도 선언되지 않으면 measured 를 emit 하지 않는다 → 커널 법칙1(evidence_missing)
   FAIL. 무노동 만점(`_safe_div default=1.0`) 회귀를 구조적으로 봉쇄한다.

---

## 3. 아키텍처 — 공유 claim 코어 + 3 producer

```
scoring/producers/
  claims.py                    ← 신설: backing-kind 검증기 (닫힌 화이트리스트, 공유)
  measure_intent_fidelity.py   ← 신설: intent_fidelity
  measure_scope_map.py         ← 신설: files_mapped_to_todos
  measure_solid_static.py      ← 신설: modules_passing_solid, modules_total, dip_violation
```

세 producer 는 `_evidence_common.py`(WP5 공유 헬퍼: `build_measured`/`assemble_record`/
`write_evidence`/`sha256_of_file`/`relpath`/`now_iso`)를 재사용한다 — Evidence 조립 로직을
복제하지 않는다(§2 원칙4).

### 3.1 `claims.py` — 공유 backing 검증 코어

verdict 아님. 각 검증기는 순수 디스크 검사로 `(bool, detail)` 을 반환한다. detail 은
리포트 artifact 에 기록될 근거(무엇을 어디서 확인했는지).

```python
# 공개 계약
def verify(claim: dict, ctx: Context) -> tuple[bool, dict]:
    """claim = {"kind": str, "ref": <str|dict>}. ctx 는 검사에 필요한 디스크 핸들.
    kind 가 화이트리스트 밖이면 UnknownBackingKind 예외(임의 검사 표면 차단)."""
```

`Context` 필드(검증기가 필요한 것만 읽음):

| 필드 | 내용 |
|---|---|
| `submission` | 제출물 루트 Path (file/symbol 검사) |
| `git_files` | `git diff --name-only <base>` 결과 리스트 or None (diff/symbol 검사) |
| `junit` | 파싱된 junit 결과(테스트 id→상태) or None (test 검사) |
| `code_root` | AST 스캔 대상 루트 (import/symbol_count 검사) |
| `module` | 현재 검사 중인 모듈의 `code_root` 기준 상대경로 or None (solid 모듈 스코프) |

backing kind 화이트리스트(닫힘):

| kind | ref | 검증(기계) |
|---|---|---|
| `test` | test id/name 문자열 | `ctx.junit` 에 존재 **AND** 상태=passed. junit 없으면 False. |
| `symbol` | 심볼 문자열 | `ctx.git_files` 중 하나 이상의 파일 텍스트에 존재(정규식 경계 매칭). |
| `diff` | 경로 glob | `ctx.git_files` 중 하나 이상이 glob 매칭. |
| `file` | 경로 | `ctx.submission/<ref>` 디스크 존재. |
| `absent_import` | import 대상 문자열 | `ctx.module` 의 AST import 집합에 ref **없음**(DIP: 구체 의존 부재). |
| `import_of` | 추상 대상 문자열 | `ctx.module` 의 AST import 집합에 ref **있음**(DIP: 추상 의존 존재). |
| `symbol_count_max` | `{"symbol":"public_class"\|"public_function","max":int}` | `ctx.module` AST 의 해당 심볼 수 ≤ max (SRP). |

**결정성:** 검사는 파일 내용·경로에만 의존하고 시간/난수/네트워크를 읽지 않는다. 같은
디스크 상태 → 같은 결과(§2 원칙5). 정규식·AST 파싱 실패는 False + detail 에 사유 기록(예외
로 producer 를 죽이지 않음 — 측정 실패는 "미검증"으로 관측된다).

**ctx 결손 규칙(일반):** 검증기가 필요로 하는 ctx 필드가 None 이면(예: junit 미제공,
git diff 실패로 `git_files=None`) 해당 claim 은 **False + detail 에 결손 사유** — 입력이
없다는 것을 "검증됨"으로 치지 않는다(§2 원칙2 "증거 없음 = FAIL"과 동형). 위 표의
"junit 없으면 False"는 이 규칙의 한 사례다.

### 3.2 `measure_intent_fidelity.py` → `intent_fidelity`

- **입력**: `--criteria <intent-criteria.json>` · `--submission <dir>` · `--test-junit <path>`
  (test kind 용, optional) · `--git-base HEAD` · `--out-dir <run>/evidence` (+ 결정성 인자).
- **intent-criteria.json 스키마** (phase 01/04 저작, 값 없음):
  ```jsonc
  {"criteria": [
    {"id": "c1", "text": "로그인 성공 경로", "required": true,
     "backing": {"kind": "test", "ref": "test_login_ok"}},
    {"id": "c2", "text": "AuthService 진입점 존재", "required": true,
     "backing": {"kind": "symbol", "ref": "class AuthService"}},
    {"id": "c3", "text": "비밀번호 재설정(부가)", "required": false,
     "backing": {"kind": "diff", "ref": "src/auth/reset*.py"}}
  ]}
  ```
- **알고리즘**: git diff → `ctx.git_files`; junit 파싱 → `ctx.junit`; 각 criterion 을
  `claims.verify` 로 검사. 리포트 artifact(`gate.intent_fidelity.report.json`)에 per-criterion
  {id, required, kind, ref, verified, detail} 기록.
- **이산화 규칙**(커널 assertion `intent_fidelity ∈ {1.0,0.7,0.0}` 준수):
  - required 중 하나라도 미검증 → **0.0**
  - required 전부 검증 + optional 중 **하나 이상** 미검증 → **0.7**
  - 전 criterion 검증 → **1.0**
  - criteria 0개 **또는 required criterion 0개** → emit 안 함(결손 → 커널 FAIL).
    필수 주장이 하나도 없는 criteria 는 충실도를 반증할 수 없으므로 측정으로 인정하지
    않는다(§2 불변식3의 강화 — optional 만으로 0.7 바닥을 확보하는 경로 봉쇄).
- **emit**: check_id `gate.intent_fidelity`, `measured.intent_fidelity = {value, source:"claims_backing",
  artifact_path: 리포트}`. (manifest 체크가 아니므로 meta_audit 이 직접 게이팅하지 않는다 —
  measure_submission 이 `--from-evidence` 로 승계하는 입력이다.)

### 3.3 `measure_scope_map.py` → `files_mapped_to_todos`

- **입력**: `--plan-todos <plan-todos.json>` · `--submission <dir>` · `--git-base HEAD` · `--out-dir`.
- **plan-todos.json 스키마** (phase 06 저작):
  ```jsonc
  {"todos": [
    {"id": "t1", "text": "인증 모듈", "paths": ["src/auth/**", "api/login.py"]},
    {"id": "t2", "text": "스키마", "paths": ["db/schema/**"]}
  ]}
  ```
- **알고리즘**: `git diff --name-only <base>` → touched 파일 집합. `files_mapped_to_todos`
  = touched 중 **어느 todo 의 path glob 에라도 매칭되는 파일 수**. 리포트 artifact
  (`gate.scope_map.report.json`)에 per-file→매칭 todo id 기록. touched ⊇ matched 이므로
  같은 git-base 에서 **항상 ≤ files_touched**(커널 assertion
  `files_mapped_to_todos <= files_touched` 자동 충족).
- **결손 조건**: todos 0개 또는 git diff 실패 → emit 안 함(§2 불변식3 — 매핑 주장이
  없거나 touched 집합을 관측 못 하면 측정이 아니다).
- **emit**: check_id `gate.scope_map`, `measured.files_mapped_to_todos`. (`files_touched` 는
  measure_submission 이 자기 git diff 로 직접 측정 — 여기서 emit 안 함.)

### 3.4 `measure_solid_static.py` → `modules_passing_solid` · `modules_total` · `dip_violation`

- **입력**: `--code-root <dir>` · `--solid-contract <solid-contract.json>` (optional) · `--out-dir`.
- **solid-contract.json 스키마** (phase 08 저작, optional):
  ```jsonc
  {"modules": [
    {"module": "src/auth.py", "claims": [
      {"principle": "DIP", "backing": {"kind": "absent_import", "ref": "sqlite3"}},
      {"principle": "DIP", "backing": {"kind": "import_of",     "ref": "Repository"}},
      {"principle": "SRP", "backing": {"kind": "symbol_count_max",
                                        "ref": {"symbol": "public_class", "max": 1}}}
    ]}
  ]}
  ```
- **알고리즘**:
  - `modules_total` = **`deep_module_metric` 의 모듈 enumeration 을 재사용**(필요 시 순수
    함수로 추출 — WP5 패턴)해 센 `code_root` 아래 .py 모듈 수 — enumeration 이 정의의
    단일 소스이며, 이것이 브릿지 값과의 정합을 보장한다.
  - 각 contract 모듈에 대해 `ctx.module=그 경로` 로 claim 전부 `claims.verify`. **모든 claim
    검증 → 그 모듈 solid 통과.** contract 의 module 경로가 **enumeration 밖**(비존재·비 .py)
    이면 그 모듈은 통과 불가로 계수하고 리포트에 사유 기록 — 따라서 통과 모듈 ⊆
    (contract ∩ enumeration) ⊆ modules_total 이 항상 성립해 assertion
    `modules_passing_solid <= modules_total` 이 구조적으로 충족된다.
  - `dip_violation` = `principle=="DIP"` claim 중 **하나라도 미검증이면 1**, 아니면 0.
    (커널 CheckSpec 이 `dip_violation == 0` hard fail.)
  - 리포트 artifact(`gate.solid_static.report.json`): enumeration 목록 + per-module
    per-claim 검증 상세 — `modules_total` 을 포함한 세 값 모두의 backing 근거.
- **contract 미제공**: `modules_passing_solid`/`dip_violation` 을 **emit 안 함**(결손 유지 —
  §0 결정). `modules_total` 만 emit(브릿지와 동일). scoring.solid 는 결손으로 남아 커널이
  정직하게 FAIL — 부정확한 zero-config AST SOLID 휴리스틱을 지어내지 않는다(감사 비판 회피).
- **emit**: check_id `gate.solid_static`, `measured.{modules_passing_solid, modules_total,
  dip_violation}`.

---

## 4. 정합성 처리 — 승계 충돌·불변식

1. **`modules_total` 충돌.** `measure_submission._index_from_evidence` 는 키별 *사전순 첫
   파일* 이 이긴다. `gate.solid_static.json` 과 `quality.deep_module.json` 이 둘 다
   `modules_total` 을 제공하면 전자(`g` < `q`, 사전순 앞)가 이긴다 — 즉 신규 producer 값이
   승계된다. 두 producer 가 **동일 enumeration** 을 쓰면 어느 쪽이 이겨도 값이 같아
   무해하다 — 그래서 §3.4 가 enumeration 재사용을 의무화한다. (같은 이유로 `gate.*` 접두는
   `quality.*`/`scoring.*` 보다 항상 사전순 앞이라, 4키 전부에서 승자가 결정적으로 신규
   producer 다.)
2. **`files_mapped_to_todos <= files_touched`.** 두 값이 같은 `--git-base` 와 submission 에서
   나오면 matched ⊆ touched 로 항상 성립. 서로 다른 base 를 주면 불변식이 깨질 수 있고 그때
   커널이 FAIL(정직 — 입력 불일치를 통과시키지 않음).
3. **provenance 사슬.** measure_submission 은 승계 시 값의 artifact_path 를 *상류 evidence
   파일* 로 두고 그 sha256 을 pin 한다(`_add_derived`). 커널 법칙3 은 그 파일의 디스크 존재+
   해시를 대조한다. 상류 evidence 파일은 자신의 리포트 artifact 를 pin 하고, 리포트는
   claims.py 가 실제 검사한 디스크 근거를 담는다. 사슬: submission evidence → 상류 evidence
   → 리포트 → 디스크 검사. (deep_module 브릿지와 동일 사슬 구조 — 기존 계약 준수.)

---

## 5. 통합 — 기존 자산 무수정

`measure_submission.py --from-evidence <dir>` 가 4키를 그대로 승계한다. 세 producer 를
`<run>/evidence/` (measure_submission 의 `--from-evidence` 대상 디렉터리)에 emit 하면 파이프
라인이 자동 정합한다. **measure_submission·checkspec(scoring.correctness/scope_fit/solid)·
pipeline.manifest.json 은 한 줄도 바꾸지 않는다** — 이들은 이미 이 승계를 기다리며 backing
부재 시 정직히 결손 처리하도록 설계돼 있다.

호출 순서(파이프라인 phase 09):
```
measure_intent_fidelity.py --criteria ... --out-dir <run>/evidence
measure_scope_map.py       --plan-todos ... --out-dir <run>/evidence
measure_solid_static.py    --solid-contract ... --out-dir <run>/evidence
measure_submission.py --from-evidence <run>/evidence ... --out-dir <run>/evidence
meta_audit.py <run> --grade G3   # 커널 재판정
```

---

## 6. 검증 (값 기반 완료 조건)

각 WP 는 스크립트 실행-결과로 검증한다(설계 §2 원칙 — 선언 금지).

1. **fixture producer 테스트**: 소형 submission(임시 git repo)+criteria/todos/contract+junit
   fixture → producer 실행 → emit 된 measured 값 단언(intent 이산화 3케이스, scope 매칭 카운트,
   solid 통과/dip 케이스).
2. **claims.py 단위 테스트**: 각 backing kind 의 True/False 케이스 + 화이트리스트 밖 kind →
   예외. AST 파싱 실패 → False+detail(예외 아님).
3. **커널 왕복**: emit 된 evidence 를 measure_submission 이 승계 → `kernel.verify` 가 실제로
   PASS(값 술어 충족) 또는 FAIL(위반) 재판정. deficit→backed 전환 실증.
4. **결정성**: 같은 `--measured-at` 2회 실행 → 리포트/evidence 바이트 동일(경로 제외).
5. **self-repo 데모**: scoring 자기 코드에 criteria/contract 를 작성해 producer 를 태우고,
   dogfood 재실행 시 scoring.correctness/scope_fit/solid 가 deficit → PASS/실FAIL 로
   바뀌는 것을 값으로 보인다(dogfood 보고 갱신).
6. **회귀 없음**: `pytest skills/theseus-harness/scoring/ -q` 전건 통과 + `self_lint.py`
   all_ok + manifest `drift-check` == []. (신규 파일이 기존 계약을 깨지 않음.)

---

## 7. 반(反)군비경쟁 고지 (§11.1 순감 지표)

파일은 4개(claims.py + producer 3) 늘지만, 이는 **순증이 아니라 대체**다: self_lint 의
prose C-룰·self_score 자기 신고가 "선언"하던 correctness/scope/solid 를 *기계 검사가 낳는
값*으로 바꾼다. 목적은 기존 scoring CheckSpec 3종이 **deficit 이 아니라 실제 게이팅**되게
만드는 backing 제공이지 병렬 증설이 아니다. 상류 선언 아티팩트(criteria/todos/contract)는
새 prose 룰이 아니라 *반증가능 claim 목록* 이며, 그 판정은 문서 grep 이 아니라 디스크 검사다.

**정직 고지(한계):** 본 메커니즘이 기계 보증하는 것은 claim 의 *진위* 다. claim 의
*충분성*(선언된 기준이 의도/SOLID 를 얼마나 덮는가 — 예: DIP claim 0개 contract 는
`dip_violation=0` 을 공진리로 얻는다)은 보증하지 않는다 — 그것은 phase wiring(§8 후속)의
저작 지시와 리뷰의 몫이며, per-claim 리포트 artifact 가 그 감사를 가능하게 남는 근거다.

---

## 8. 비목표 (이 스펙이 다루지 않는 것)

- **zero-config AST SOLID 바닥값** — contract 없으면 solid 결손 유지(정직). 부정확한 자동
  SOLID 휴리스틱은 하네스가 비판받은 지점이라 도입하지 않는다.
- **phase 01/04/06/08 프롬프트 wiring** — 선언 아티팩트 저작 지시 추가는 얇은 후속 단계.
  producer 가 먼저 존재해야 wiring 이 의미를 갖는다.
- **coverage/e2e/dacapo/tournament/regression deficit** — 판단 아님(도구·fixture 부재). 범위 밖.
- **외부 벤치 harness** — 별도 Spec 2(§11.5 controlled 비교, 외부 evaluator 필요).
- **parity_category producer** — 프레임워크별 라우트 추출은 fragile, 단일 사이드에서 NA.
  본 스펙 밖(필요 시 별도).

---

## 9. 구현 롤아웃 — opus/sonnet 작업 패키지

| WP | 내용 | 권장 모델 | 완료 조건(값 기반) |
|---|---|---|---|
| **JW1** | `claims.py` 공유 코어 + 단위 테스트 | **opus** | 7 backing kind True/False + 화이트리스트 밖 예외 테스트 통과 |
| **JW2** | `measure_intent_fidelity.py` + fixture 테스트 | sonnet | 이산화 3케이스 + 커널 왕복 PASS/FAIL + 결정성 |
| **JW3** | `measure_scope_map.py` + fixture 테스트 | sonnet | 매칭 카운트 정확 + `≤ files_touched` + 커널 왕복 |
| **JW4** | `measure_solid_static.py` (+ deep_module enum 재사용/추출) + 테스트 | **opus** | 통과 카운트/dip 케이스 + `modules_total` 브릿지 정합 + contract 미제공 결손 |
| **JW5** | self-repo 데모 + dogfood 보고 갱신 | sonnet | 3 deficit → backed 전환 값 실증, 회귀 없음(§6.6) |

**의존:** JW1 → {JW2, JW3, JW4} 병렬 → JW5. JW1(claims 코어)이 임계 경로.

**병렬성 주의:** JW2/JW3/JW4 는 서로 다른 신규 파일만 쓴다(파일 경계 무충돌). 각 작업자는
자기 producer + 자기 테스트만 소유하고, 공유 `claims.py`(JW1)·`_evidence_common.py`(기존)·
`deep_module_metric.py`(JW4 만 추출 편집)에는 손대지 않는다. 통합 검증(§6.6 전건 pytest/
self_lint/drift)은 오케스트레이터(본인)가 직접 수행한다.

---

## 10. 이 설계가 감사/deficit 에 대응하는 매핑 (역추적)

| 근거 | 본 설계 대응 |
|---|---|
| dogfood deficit `intent_fidelity` | §3.2 구조화 기준 + 기계 backing 이산화 |
| dogfood deficit `files_mapped_to_todos` | §3.3 plan-todos × git diff 교집합 |
| dogfood deficit `modules_passing_solid`/`dip_violation` | §3.4 solid-contract + AST claim 검증 |
| 감사 T1 self-rating 순환성 | §2 불변식 — 아티팩트는 claim 만, 판정은 producer 디스크 검사 |
| 커널 §2 원칙1 "측정하라" | §2 불변식1/2 — LLM 숫자가 커널에 닿지 않는 경계 |
| 커널 §2 원칙4 "줄인다" | §3 claims.py 단일 코어 공유(복제 없음) + §7 대체(순증 아님) |
| deep_module 정직한 결손(SOLID 미승계) | §3.4 실제 의존방향/SRP 를 기계 측정하는 별도 producer |

---

*본 문서는 설계 확정본이다. 사용자 리뷰 후 writing-plans 로 구현 계획을 전개한다.*
