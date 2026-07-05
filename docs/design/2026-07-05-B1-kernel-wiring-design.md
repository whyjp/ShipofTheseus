# 설계 문서 — B1: 검증 커널 파이프라인 배선 (phase-09 게이트 러너 + 선언 아티팩트 저작)

> **작성**: Claude Fable 5 (설계 확정 — 코드/phase 편집 없음, 본 문서 단일 산출)
> **구현 위임**: opus/sonnet (본 문서 §7 작업 패키지 기준)
> **일자**: 2026-07-05
> **선행 설계**: `docs/design/2026-07-04-verification-kernel-design.md` (§7.1/§9/§11/§13) · `docs/design/2026-07-05-judgment-gate-producers-design.md` (§3.2~3.4/§8)
> **동기 근거**: `docs/design/2026-07-05-improvement-headroom-assessment.md` — B1 정의(§3 sufficiency bar) + §1.1 "커널 파이프라인 배선 0" 실측
> **대상 저장소 상태**: 커널 5법칙 + CheckSpec 15개 + producer 13종 + meta_audit(생성형) + dogfood 전부 완성·자가검증(476 테스트). 유일 결손 = 실 파이프라인의 어느 지점도 이들을 호출하지 않음(phase 16개·conventions 90개·orchestrator 전부에서 `meta_audit`/`CheckSpec`/`kernel` 참조 0건 — grep 실측).

---

## 0. 이 문서가 확정하는 것 (범위 계약)

**실 run 에서 커널이 phase 09 의 실제 게이트가 되게 하고, 그 입력인 선언 아티팩트를
phase 01/04/06/08 이 저작하게 한다.** 핵심 제약은 §11.1 반군비경쟁: 옛 prose/self_lint
게이트를 **대체(net-reduce)** 하는 것이지 병렬 층 추가가 아니다 — 본 문서의 모든 추가에는
그보다 큰 명시적 삭제·강등이 짝으로 붙는다(§3 명시 목록 + §6 측정 프로토콜).

확정 대상 5개:

1. **phase-09 게이트 러너** `scoring/run_gate.py` — producer 오케스트레이션 → meta_audit
   → verdict 를 내는 단일 결정적 진입점. dogfood.py 오케스트레이션의 일반화(§2).
2. **phase 09 마이그레이션** — 커널 verdict 가 *the gate*. 대체·삭제·강등 명시 목록(§3).
3. **phase 01/04/06/08 선언 아티팩트 저작 지시** — intent-criteria / plan-todos /
   solid-contract (§4).
4. **P7(honor-system) 완화 장치** — 단일 호출 + verdict 아티팩트 하류 확인(§5).
5. **§11.5(a) 지시 질량 측정·보고 프로토콜** — before 실측 포함(§6).

**비목표(§8):** 전체 15-페이즈 §9 마이그레이션 완주(B1 은 scoring-관련 09 + 01/04/06/08
만) · B2(동결 prose 다이어트·임계 재설정) · B3(self_lint 광역 순감 — 본 문서는 09 직결
5룰만) · 외부 벤치 harness · 구조화 dispatch log.

---

## 1. 현황 실측 — 무엇이 무엇을 기다리고 있는가

| 자산 | 상태 (실파일 확인) | 배선 상태 |
|---|---|---|
| `scoring/kernel/meta_audit.py` | CLI 완성: `--project-root --grade [--manifest --checks-dir --output --verified-at]`. exit 0=pass/1=fail. `--output` 시 `quality/gate_meta_audit.json` 관례 경로에도 기록 | 호출자 = dogfood.py 뿐 |
| `checks/` 15 CheckSpec + `pipeline.manifest.json` | scoring 6 + quality 3 + plan 2 + sprint 1 + cold 1 + frozen 2. frozen=ADVISORY, cold.isolation/plan.tournament_independence/scoring.coverage/fe_be_parity/quality.dry 는 applicability 보유 | 동일 |
| producer 13종 (`scoring/producers/`) | 전부 `--out-dir <run>/evidence` 로 `<check_id>.json` emit. measure_submission 은 `--from-evidence` 승계 + `--coverage/--e2e-junit` 지원 | 동일 |
| 판단-게이트 producer 3종 (JW1~4) | measure_intent_fidelity / scope_map / solid_static — 선언 아티팩트(criteria/todos/contract)를 claims.py 로 디스크 재검사 | 선언 아티팩트를 저작하는 phase 지시 0 (JW §8 비목표로 미룸) |
| `scoring/dogfood.py` | junit→quality→gates→submission→cold→meta_audit 오케스트레이션 완성. 인자화 거의 완료(경로 전부 CLI). 자기코드 기본값 + exit-0-on-FAIL 만 dogfood 특수 | **사실상 phase-09 러너의 원형** |
| phase 09 실물 (`phases/09-quality-gates.md`, 40,014 bytes) | check_cold_session.py(9.f) + define_errors_check/comment_intent_check(9.fff/ggg) + prose 정적 게이트 9 + §PNC/§Mirror/§Primary/§Literal(producer 0, sprint-40 에 0-emit 실적) + phase_invoke_audit(9.zz, P5 하드코딩 사각 확정) 로 채점 | 커널 참조 0 |

**dogfood 재사용 판단(실코드 기준): 재사용 가능 — 신규 러너를 dogfood 에서 추출한다.**
dogfood.py 의 `_run/_produce_junit/_quality_producers/_gate_producers/_submission_producer/
_cold_producer/_meta_audit` 는 이미 경로를 전부 인자로 받는 순수 오케스트레이션이다.
dogfood 특수성은 (a) 기본값(scoring/ 자기 디렉터리·dogfood_inputs·v0919 cold 쌍),
(b) exit 0-on-FAIL 의미론, (c) plan/sprint producer 미호출 — 셋뿐이다. 따라서 신규
`run_gate.py` 가 이 함수들을 **소유**하고(이동), dogfood.py 는 run_gate 의 라이브러리
API 를 자기 기본값·자기 exit 의미론으로 부르는 **얇은 wrapper** 로 강등한다(DRY —
오케스트레이션 로직 1벌).

---

## 2. phase-09 게이트 러너 — `scoring/run_gate.py`

### 2.1 공개 계약 (CLI)

```bash
python skills/theseus-harness/scoring/run_gate.py \
    --project-root .ShipofTheseus/<프로젝트>/ \
    --grade <G2|G3|G4|G5> \
    --submission <코드 루트(git repo 내)> \
    --test-target <테스트 디렉터리> \
    [--git-base <ref>] [--coverage <coverage.xml>] [--e2e-junit <junit.xml>] \
    [--junit <재사용 junit>] [--phase-upto 09] \
    [--measured-at ISO8601] [--verified-at ISO8601]
```

- **exit 0** = meta_audit verdict `pass` (게이팅 집합 기준, §2.4)
- **exit 1** = verdict `fail` — **phase 09 진행 차단** (dogfood 와 달리 verdict 가 곧 exit)
- **exit 2** = pipeline 크래시(verdict 미산출) — verdict 부재는 통과가 아니라 별도 실패

산출물(전부 `--project-root` 아래):

```
evidence/<check_id>.json          # producer emit (실행마다 선청소 — dogfood stale 봉쇄 규율 계승)
results/junit.xml                 # 러너가 직접 실행한 pytest (측정하라 — 자기 신고 junit 불신)
quality/gate_meta_audit.json      # verdict 아티팩트 (하류 phase 확인 대상, §5)
state/gate_history/<NN>/          # 이번 실행의 evidence + verdict 사본 (sprint.regression 의 prior 소스)
```

### 2.2 실행 단계 (dogfood 순서 계승 + plan/sprint 2단계 신규)

```
1. junit        pytest <test-target> → results/junit.xml            (dogfood _produce_junit 이동)
2. quality      measure_deep_module / dry / define_errors            (dogfood _quality_producers 이동)
3. gates        measure_intent_fidelity / scope_map / solid_static   (dogfood _gate_producers 이동;
                선언 아티팩트 경로는 §2.3 run 관례에서 유도, 부재 시 미실행+사유 기록 = 정직 결손)
4. plan  (신규) measure_dacapo_threshold  --tournament-md <최신 plan/tournament-*.md>
                measure_tournament        --shadow-grades-dir plan/  (shadow-grade-*.json glob)
                해당 artifact 부재 시 미실행 → evidence 부재 → 커널 법칙1 FAIL (정직)
5. sprint (신규) measure_regression --prior <gate_history 최신의 scoring.correctness.json>
                                    --current <이번 evidence>
                gate_history 비어 있으면(첫 실행) 미실행 — §2.4 의 phase-upto 게이팅이 처리
6. submission   measure_submission --from-evidence evidence/ --coverage/--e2e-junit 패스스루
7. cold         measure_cold_isolation — 재이해/원본 쌍은 §2.3 규약. dispatch log 부재 환경에선
                dispatch_log_present=0 → NA (§7.4 정직 고지 — 실 run 에서도 동일)
8. meta_audit   meta_audit.py --project-root <root> --grade <G> --output quality/gate_meta_audit.json
9. archive      evidence/ + verdict → state/gate_history/<NN>/ 사본
```

순서 의존(2→3→6)은 dogfood 주석 그대로: quality/gates evidence 가 먼저 디스크에 있어야
`--from-evidence` 가 modules_total/4키를 승계한다.

### 2.3 run 관례 경로 (선언 아티팩트·재이해 쌍의 단일 규약)

러너는 다음 고정 관례로 입력을 찾는다 — phase 지시가 저작 위치를 이 규약으로 통일한다(§4):

| 입력 | 관례 경로 | 저작 phase |
|---|---|---|
| intent-criteria | `intent/01-intent-criteria.json` | 01 초안 → 04 확정 → 08 backing.ref 보충(§4.4 동결 규칙) |
| plan-todos | `plan/06-plan-todos.json` | 06 |
| solid-contract | `impl/08-solid-contract.json` | 08 (08-δ) |
| tournament md | `plan/tournament-*.md` 최신 (mtime 아닌 NN 사전순 최대) | 06 기존 산출물 그대로 |
| shadow grades | `plan/shadow-grade-*.json` glob | 06 기존 산출물 그대로 |
| cold 재이해 쌍 | `plan/candidates/<winner>/07-cold-read.md` vs `plan/06-plan.md` 존재 시 그 쌍, 아니면 `intent/03-comprehension.md` vs `intent/01-intent.md` | 03/07 기존 산출물 그대로 |

CLI 로 전 항목 override 가능(테스트 seam) — 그러나 phase 지시에는 관례 경로만 등장한다
(지시 chars 최소화).

### 2.4 `--phase-upto` — 단계 게이팅 (meta_audit 소폭 확장, 유일한 기존 코드 수정)

manifest 의 checks 는 grade 별 전 파이프라인 체크다. `sprint.regression`(phase 10)은
phase 09 시점에 evidence 가 원리적으로 없다 — 이를 FAIL 로 게이팅하면 첫 run 이 영구
차단된다. 해소는 skip 부활이 아니라 **단계 스코프**다:

- `meta_audit.py` 에 optional `--phase-upto <id>` 추가: manifest 의 phases 순서에서
  해당 id 이하의 phase 를 가진 CheckSpec 만 **verdict 계산(failed 집계)에 산입**.
  범위 밖 체크는 여전히 평가·기록하되 report 의 신규 `deferred: [...]` 리스트로 분류
  (침묵 skip 아님 — 평가는 하되 이 단계의 게이트가 아님을 값으로 명시).
- phase 09 호출 = `--phase-upto 09` (03/06/08/09 체크 게이팅). phase 10 sprint N≥2
  재호출 = `--phase-upto 10` (regression 합류). 미지정 = 전 체크 게이팅(기본값 —
  dogfood·기존 테스트 무영향, 하위호환).
- 커널(kernel.py)·CheckSpec·manifest 스키마는 **무수정**. 수정은 meta_audit 의 정책
  레이어 1곳뿐이다(§11.2 위반 없음 — prose 체크 신설 아님).

### 2.5 dogfood.py = 얇은 wrapper (DRY)

- 오케스트레이션 함수들을 run_gate.py 로 이동, dogfood.py 는 import 해 자기 기본값
  (scoring/ 자기 코드·dogfood_inputs/·v0919 cold 쌍·plan/sprint 단계 비활성)으로 호출.
- dogfood 고유 유지분: `classify()`(PASS/FAIL/NA/ADVISORY/deficit 세분류 보고),
  exit-0-on-FAIL 의미론(실행 성공 = verdict 산출), `dogfood_summary.json`.
- 완료 조건: dogfood 재실행 결과(verdict·counts)가 이동 전과 값 동일(회귀 없음).

### 2.6 결정성·인코딩

`--measured-at/--verified-at` 전 단계 패스스루(dogfood 계승). `force_utf8_stdio()` +
모든 subprocess `encoding="utf-8"`(C35). 같은 디스크 상태 + 같은 주입 시각 → evidence/
verdict 바이트 동일(§2 원칙5) — WP 완료 조건에 포함.

---

## 3. phase 09 마이그레이션 — 커널 verdict 가 *the gate*

### 3.1 새 구조 (phase 09 본문의 뼈대)

phase 09 첫 sub-step = **§V8 viewer-readiness(존치) 직후, literal Bash 1블록**:

```bash
python skills/theseus-harness/scoring/run_gate.py \
    --project-root .ShipofTheseus/<프로젝트>/ --grade <G> \
    --submission <submission>/ --test-target <submission>/tests/ --phase-upto 09
# exit 0 → 존치 게이트(§3.3) 진행. exit 1 → quality/gate_meta_audit.json 의 failed[] 를
# remediation TODO (T-NNN-fix) 로 폴드백, phase 08 step C 재진입. exit 2 → 러너 자체 진단.
```

종합 판정 = **meta_audit verdict(pass 의무) AND 존치 게이트 전부 pass**. FAIL 처리
플로우(remediate-then-proceed / halt)는 기존 구조 유지 — 판정의 *소스*만 커널로 교체.

### 3.2 대체·삭제·강등 명시 목록 (순감 지표 — 수치)

**(A) 옛 게이트 스크립트 — 실 파이프라인에서 은퇴**

| 옛 게이트 | 대체 커널 체크 | 조치 | 순감 |
|---|---|---|---|
| `check_cold_session.py` 의무 호출 (HARD-RULE 9.f, phase 09 첫 동작) | `plan.dacapo_threshold` + `plan.tournament_independence` + `cold.isolation` (값 기반) — 영어 sentinel regex·파일 개수 검사는 §7.4 가 폐기 선언한 P3 그 자체. rerun 세리머니 강제분은 frozen(ADVISORY) 관할 | phase 09 호출 삭제 + 스크립트 삭제 (유일 호출자가 9.f) + C-CSV 삭제 | 스크립트 276줄 + phase 09 §첫 동작 ~12줄 |
| `define_errors_check.py` 의무 호출 (9.fff) | `quality.define_errors` (producer `measure_define_errors` — WP5 승격 완료) | phase 09 호출 삭제. 스크립트는 WP 에서 producer 와 assertion 동등성 확인 후 삭제(gap 발견 시 producer 의 라이브러리로 흡수 후 CLI 게이트만 은퇴) | 스크립트 294줄 + phase 09 해당 절 ~20줄 |
| `phase_invoke_audit.py` 의무 호출 (9.zz, phase 09 exit) | `meta_audit`(생성형 레지스트리 — P5 의 설계상 대체물) | phase 09 호출 삭제 + 스크립트 삭제(다른 호출자 없음 확인 후) | 스크립트 전체 + phase 09 블록 ~6줄 |
| phase 08 exit 의 `deep_module_metric.py`/`dry_violation_count.py`/`dacapo_threshold.py` 의무 호출 (9.ddd/9.eee/9.qq) | `quality.deep_module`/`quality.dry`/`plan.dacapo_threshold` — 러너가 09 에서 1회 측정 | phase 08 의 CLI 의무 블록 삭제(스크립트 본체는 producer 가 enumeration 재사용하므로 존치) | phase 08 ~31줄 (~1.6KB) |

**(B) phase 09 prose 정적 게이트 — 커널 체크로 행 대체**

| 옛 prose 게이트 | 대체 |
|---|---|
| 정적 게이트 1 의도 일치 | `scoring.correctness` (intent_fidelity — criteria 기계 재검사) |
| 정적 게이트 2 범위 규율 | `scoring.scope_fit` (files_mapped_to_todos ≤ files_touched) |
| 정적 게이트 3 SOLID | `scoring.solid` (modules_passing_solid·dip_violation) |
| 정적 게이트 4 테스트 모양 | `scoring.correctness`(tests) + `scoring.coverage` + `scoring.e2e` 값 |
| 정적 게이트 5 FE/BE 패리티 | `scoring.fe_be_parity` (applicability: fe_side_exists) |

9-게이트 표는 존치 게이트(§3.3)만 남는 축약 표로 재작성 — 대체된 행은 "커널 체크 id"
1셀 참조로 강등.

**(C) producer 없는 게이트 4패턴 — advisory 강등 (§11.2 "prose 체크 금지")**

§PNC / §Mirror / §Primary / §Literal (sprint-39) + §Gate-JSON-Emit-Mandate (sprint-40):
producer 0, 실 run emit 실적 0(sprint-40 보고의 "0 emit" — JSON-Emit-Mandate 자체가
그 미발화의 패치였다). 커널 원칙상 producer 없는 것은 게이트가 아니다. **삭제가 아니라
강등**: 4패턴의 검사 알고리즘·안티패턴 요지를 안티패턴 카탈로그 참조(각 ~5줄)로 압축하고
"producer 승격 후보(후속 §9 완주 대상)"로 명시. 게이팅·JSON 골격 의무·self_lint 연동은
제거.

| 절 | 현재 분량 (실측 라인) | 강등 후 |
|---|---:|---:|
| §PNC L216-259 | 44줄 | ~5줄 |
| §Mirror L262-305 | 44줄 | ~5줄 |
| §Primary L308-355 | 48줄 | ~5줄 |
| §Literal L358-405 | 48줄 | ~5줄 |
| sprint-39 통합 L407-409 | 3줄 | 0줄 |
| §Gate-JSON-Emit-Mandate L570-626 | 57줄 | 0줄 (골격 emit 의무 자체가 미발화 게이트의 보철) |
| 소계 | **244줄 (~11.6KB)** | **~20줄** |

**(D) self_lint C-룰 — B1 직결분 5룰 삭제 (88 등록 룰 → 83)**

| 룰 | 함수 | 라인 (실측) | 삭제 근거 |
|---|---|---:|---|
| C-PNC | `check_pnc` | 17 | (C) 강등 절의 키워드-박힘 검증 — 검증 대상 소멸 |
| C-MIR | `check_mirror` | 18 | 동일 |
| C-PRI | `check_primary_source` | 18 | 동일 |
| C-LIT | `check_literal_forbid` | 18 | 동일 |
| C-CSV | `check_cold_session_validator` | 27 | check_cold_session.py 은퇴(A) — 존재 검증 대상 소멸 |
| 소계 | | **98줄 + 등록 5행** | |

주: phase 09 본문이 선언한 C-V6X/C-GJM/C-MCC/C-VEX 는 **self_lint 에 실재하지 않는다**
(선언≠구현 — grep 실측). 마이그레이션 시 해당 본문 선언 문구도 함께 정리한다(가짜 참조
제거). 광역 self_lint 순감(dacapo/regression/shadow 계열 등 ~300줄 추가 후보 실측)은
**B3 의 몫** — B1 은 위 5룰만 (커널이 인수한 것과 검증 대상이 소멸한 것만 지운다 —
무게이트 공백 금지).

### 3.3 존치 목록 (커널이 못 보는 진짜 정합 — 정직한 경계)

| 존치 게이트 | 존치 이유 |
|---|---|
| 게이트 6 NFR 임계 + derived gates (NFR-V) | 임계·검증 프로토콜이 phase 04 사용자 답 종속 — producer 화는 후속 |
| 게이트 7 runtime-prereq 실 부팅 1회 | 이미 실행 기반 검사 — 커널 밖이지만 P2 아님 |
| 게이트 8/9 process-flow·domain failure patterns | 도메인 판단 — producer 없음, 후속 |
| G-RNFS/§README-Sync · G-RDC/§V6 · G-MNT · G-DCZ · G-SPB | 이미 스크립트 실행 + JSON evidence 기반(sprint-40 이중압력) — 커널 CheckSpec 화는 §9 완주 후보이나 지금도 값 기반 |
| `comment_intent_check.py` (9.ggg) | 결정적 스크립트 게이트, producer 미존재 — 존치(승격 후보) |
| RTG (rubric-targeted) · §Methodology-Completeness · §V8 viewer-readiness | rubric/도메인/사전차단 — B1 밖 |

### 3.4 phase 09 분량 수지 (예상)

40,014 bytes → 삭제·강등 ~13.5KB(§3.2 A+B+C) + 러너 절 신규 ~2KB = **약 28.5KB
(−29%)**. 실측·보고는 §6 프로토콜.

### 3.5 orchestrator SKILL.md — phase 09 행 교체

`theseus-orchestrator/SKILL.md` 의 phase 09 매핑 행(현재 10+ 항목 나열)을 "run_gate.py
호출 + `gate_meta_audit.json` verdict==pass + 존치 게이트" 1행으로 교체(순감). phase 09
게이트 lookup 의 단일 책임 원칙 유지.

---

## 4. phase 01/04/06/08 — 선언 아티팩트 저작 (최소 지시)

원칙 재확인: **선언은 판정이 아니다.** 아티팩트는 `backing.ref`(무엇을 볼지)만 담는다 —
`verified`/`pass`/`score` 류 판정 필드는 계약 위반이며 producer 가 어차피 신뢰하지 않는다
(JW §2 불변식 1). 각 phase 추가는 **≤ 15줄** 의 §절 하나 + 스키마는 JW 설계 §3.2~3.4
링크 참조(스키마 본문 복붙 금지 — 지시 chars 최소화).

### 4.1 phase 01 (`01-intent.md`) — intent-criteria 초안

산출물 항목 k- 로 1절 추가 (~10줄):

- `intent/01-intent-criteria.json` — §a 관찰 결과 + §g 성공 지표를 criterion 배열로
  변환. 각 항목 `{id, text, required, backing:{kind, ref}}`. kind 는 claims.py
  화이트리스트(test/symbol/diff/file — 스키마: JW 설계 §3.2). 이 시점 test id 는
  미존재하므로 kind 는 file/symbol/diff 위주 잠정 — test backing 은 phase 08 이 보충.
- **required criterion ≥ 1 의무** (0 이면 producer 가 emit 거부 → 커널 FAIL — 저작 실패가
  조용히 통과하지 않는다).
- 판정 필드 금지 명시 1줄.

### 4.2 phase 04 (`04-clarify.md`) — criteria 확정 (~5줄)

인터뷰 답 확정 후(Q-D9 뒤) `intent/01-intent-criteria.json` in-place 갱신: 사용자 답으로
required/optional 재분류 + 범위 밖 criterion 삭제. **이 시점 이후 criterion 의 id/text/
required 집합은 동결** — §4.4.

### 4.3 phase 06 (`06-plan.md`) — plan-todos (~8줄)

canonical `plan/06-plan.md` 확정 직후 `plan/06-plan-todos.json` 저작: TODO 표의
`ID`/`제목`/`모듈` → `{id, text, paths}` 기계적 변환. paths glob 은 plan 본문 의무
"모듈 분할 + 파일 배치(≥5 파일 경로)" 절에서 그대로 취한다(새 정보 생산 없음 — 이미
있는 계획의 기계 판독 형식화). 스키마: JW 설계 §3.3.

### 4.4 phase 08 (`08-implement.md`) — solid-contract + criteria backing 보충 (~12줄)

- 08-δ(refactor) 종료 시 winner 코드에 대해 `impl/08-solid-contract.json` 저작: 모듈별
  DIP(absent_import/import_of)·SRP(symbol_count_max) claim. **참인 claim 만** — 거짓
  claim 은 producer 디스크 재검사에서 실 FAIL 로 관측된다(저작 인센티브가 정직 쪽으로
  정렬). contract 미저작 시 scoring.solid 결손 FAIL — 저작이 곧 게이트 통과의 전제.
  스키마: JW 설계 §3.4.
- 08-ε 시점에 `intent/01-intent-criteria.json` 의 **backing.ref 만** 실 test id 로 보충
  가능(kind=test). **criterion 추가·삭제·required 강등 금지**(04 동결) — implementer 가
  기준을 통과 가능한 것으로 바꿔치기하는 경로 차단. 러너 리포트(per-criterion trace)가
  이 감사를 가능하게 남긴다.

### 4.5 지시 질량 수지

phase 01 +~0.8KB · 04 +~0.4KB · 06 +~0.5KB · 08 +~0.9KB−1.6KB(§3.2A CLI 블록 삭제)
= 4파일 합산 **+~1.0KB**, phase 09 −~11.5KB 로 상쇄 — 5파일 총량 순감(§6 표).

---

## 5. honor-system(P7) 완화 — LLM-driven 한계 안의 최선

이 하네스는 LLM 이 phase 마크다운을 읽고 실행한다 — 훅/래퍼 없는 환경에서 "호출 안 함"을
물리적으로 막을 수는 없다. 가능한 것은 **호출 부재가 하류에서 값으로 발각되게** 만드는
것이다. 4겹:

1. **호출 지점 수축**: 옛 6+개 의무 CLI 호출(9.f/9.fff/9.ggg/9.zz/9.qq/9.ddd/9.eee…)이
   **literal Bash 1블록**으로 준다. 기억해야 할 prose 가 줄면 skip 표면적도 준다 —
   sprint-43 "literal Bash 박힘" 패러다임의 적용이지 신규 메커니즘이 아니다.
2. **verdict 아티팩트의 하류 소비**: phase 10 입력 목록에
   `quality/gate_meta_audit.json` (verdict==pass) 1줄 추가 — 러너를 안 불렀으면 파일이
   없고, phase 10 진입이 정의되지 않는다. phase 14 handoff 의 lineage_finalize 는 이미
   산출물 존재 검사를 하는 단계이므로 gate_meta_audit.json 을 검사 목록에 추가(각 1줄
   편집 — B1 스코프의 명시적 예외 2건).
3. **위조 불가성은 커널 몫**: 아티팩트를 손으로 써서 존재만 채우는 우회는 커널 법칙 1~3
   (producer_cmd 패턴·exit 0·artifact digest 디스크 대조)이 잡는다 — 러너를 실제로
   돌리는 것보다 위조가 더 어렵게 이미 설계돼 있다(B1 이 추가할 것 없음).
4. **HARD-CORE 1줄 (옵션)**: always-load 계층에 "phase 09 게이트 = run_gate.py exit 0 +
   gate_meta_audit.json" 1줄(≈70 chars). 단 4,000 chars cap 재실측 후 여유 있을 때만 —
   cap 초과 시 생략(§11.4 자기 준수 우선).

정직 고지: 이 4겹으로도 "LLM 이 phase 09 절 전체를 안 읽는" 시나리오는 못 막는다. 그
잔여 리스크의 검증이 §7 WP-B1d 리허설(발화 관측)이다.

---

## 6. 반군비경쟁 준수 검증 — §11.5(a) 측정·보고 프로토콜

**측정 방법**: 대상 파일별 `python -c "print(len(open(f,encoding='utf-8').read()))"`
(chars) + `wc -c` (bytes) 둘 다. 측정 대상 = 편집 파일 전부 + self_lint.py.

**before (본 문서 작성 시점 HEAD 실측, bytes)**:

| 파일 | before | after 목표 |
|---|---:|---|
| `phases/09-quality-gates.md` | 40,014 | ≤ 30,000 |
| `phases/01-intent.md` | 6,333 | ≤ 7,200 |
| `phases/04-clarify.md` | 15,494 | ≤ 16,000 |
| `phases/06-plan.md` | 55,695 | ≤ 56,300 |
| `phases/08-implement.md` | 12,807 | ≤ 12,200 |
| 5파일 합계 | **130,343** | **≤ 121,700 (순감 의무)** |
| `scoring/self_lint.py` | 3,472줄 / 88 등록 룰 | ≤ 3,374줄 / 83룰 |
| 삭제 스크립트 | check_cold_session 276줄 + define_errors_check 294줄 + phase_invoke_audit | −570줄 이상 |

**보고 의무**: WP-B1b/B1c 완료 시 위 표의 after 실측치를 커밋 메시지 또는
`docs/design/` 갱신에 수치로 기록. **판정 룰: 5파일 합계 chars 가 before 보다 크면 그
WP 는 실패** — 재작업. (개별 파일 순증은 허용 — 01/04/06 은 저작 지시가 순증이다.
총량이 기준.) run_gate.py 신규 코드는 지시 질량이 아니라 실행체이므로 이 표 밖 —
단 dogfood.py 와의 중복 0(함수 이동 확인)이 WP-B1a 완료 조건.

---

## 7. 롤아웃 WP (opus/sonnet) + 값 기반 완료 조건

| WP | 내용 | 권장 모델 | 완료 조건 (값 기반) |
|---|---|---|---|
| **WP-B1a** | `run_gate.py` 신설(§2 — dogfood 오케스트레이션 이동 + plan/sprint 단계 + gate_history + exit 의미론) + `meta_audit.py --phase-upto`/`deferred` (§2.4) + dogfood 얇은 wrapper 화 + 테스트 | **opus** | (i) fixture run(임시 git repo + 3 선언 아티팩트 + junit)에서 run_gate exit 0/1 이 verdict 와 일치, (ii) `--phase-upto 09` 시 sprint.regression 이 `deferred` 로 분류(FAIL 아님), (iii) dogfood 재실행 verdict·counts 이동 전과 값 동일, (iv) 같은 `--measured-at` 2회 실행 evidence 바이트 동일, (v) `pytest scoring/ -q` 전건 통과 |
| **WP-B1b** | phase 09 마이그레이션(§3.1~3.3 — 러너 블록 삽입, A/B/C 삭제·강등, 존치 표 재작성) + orchestrator SKILL.md 09행 교체(§3.5) + phase 10 입력 1줄·phase 14 검사 1줄(§5.2) + self_lint 5룰 삭제(§3.2D) + 스크립트 3종 은퇴(A — define_errors 는 producer 동등성 확인 선행) | sonnet | (i) `self_lint.py` all_ok=True (5룰 삭제 후), (ii) §6 표 after 실측 보고 + 5파일 총량 순감, (iii) 저장소 전체 grep 에서 `check_cold_session\|phase_invoke_audit` 참조 0건, (iv) manifest `drift-check` == [] |
| **WP-B1c** | phase 01/04/06/08 선언 아티팩트 저작 지시(§4 — 각 ≤15줄) + phase 08 CLI 블록 삭제(§3.2A) | sonnet | (i) 각 phase 파일에 관례 경로·스키마 링크·판정 필드 금지·동결 규칙 포함, (ii) §6 표 반영, (iii) self_lint all_ok 유지 |
| **WP-B1d** | **발화 리허설** — 소형 실 submission(기존 fixture 급 실코드, 실 git diff·실 pytest) 에 대해 `.ShipofTheseus/<rehearsal>/` run 골격 + 3 선언 아티팩트를 §4 지시대로 저작하고 run_gate 를 실행 | sonnet | (i) **run_gate 가 실 submission 에서 발화해 `quality/gate_meta_audit.json` verdict 를 냄**, (ii) **의도적 결함 1개 주입(예: required criterion 의 backing 미충족) 시 exit 1 = FAIL 이 관측되고, 결함 제거 시 pass 로 전환** — 게이트가 실제로 문을 여닫음을 값으로 증명, (iii) plan.dacapo_threshold/tournament_independence 는 리허설 run 의 실 tournament/shadow artifact 로 채워지거나 evidence 부재 FAIL 로 정직 관측(어느 쪽인지 기록), (iv) cold.isolation NA(dispatch log 부재) 정직 기록 |

**의존**: WP-B1a → {WP-B1b, WP-B1c} → WP-B1d. WP-B1a 가 임계 경로.
**WP-B1d 가 B1 의 완료 게이트다** — (ii) 의 FAIL→pass 왕복 관측 없이는 B1 을 완료로
선언할 수 없다(개선-여지 평가 B4 드레스 리허설의 선행 축소판이며, B4 full-run 리허설을
대체하지 않는다).

---

## 8. 비목표 (이 문서가 다루지 않는 것)

- **§9 15-페이즈 마이그레이션 완주** — B1 은 scoring-관련 phase 09 게이팅 + 01/04/06/08
  저작만. phase 02/03/05/07/10~14 의 개별 CheckSpec 화·존치 게이트(§3.3)의 producer
  승격은 후속(벤치 데이터 이후 재우선순위).
- **B2** — frozen prose 다이어트(멀티버스 폭·viewer·budget 80%)·임계 0.999 재설정.
  본 문서는 phase 09 게이팅 소스만 바꾼다.
- **B3** — self_lint 광역 순감(§3.2D 의 5룰 외 dacapo/regression/shadow 계열 등).
- **구조화 dispatch log** — cold.isolation 의 NA 해소는 별도 작업(§7.4 후속).
- **외부 벤치 harness / §11.5(b) controlled 비교** — Spec 2.
- **e2e/coverage 도구 정책** — 러너는 패스스루만. pytest-cov 배선·e2e fixture 는
  리허설/B4 에서 관측 후 판단.
- **comment_intent/RTG/NFR-derived/domain 게이트의 producer 화** — 존치(§3.3), 승격 후보.

---

## 9. 역추적 매핑

| 근거 | 본 설계 대응 |
|---|---|
| 평가 §1.1 배선 0 (grep 실측) | §2 run_gate 단일 진입점 + §3.1 phase 09 the-gate 화 |
| 평가 B1 완료 조건 "correctness/scope/solid 가 deficit 아닌 실측 판정" | §4 선언 아티팩트 저작 + §2.2 단계 3 |
| 커널 §11.1 순감 | §3.2 명시 목록(스크립트 570줄+ · phase prose ~13.5KB · C-룰 5) > §4.5 추가(~1KB+러너 절 2KB) |
| 커널 §11.5(a) | §6 측정·보고 프로토콜 + before 실측표 + 총량 순증 시 WP 실패 룰 |
| P5 (phase_invoke_audit 사각) | §3.2A — meta_audit 로 은퇴 |
| P7 (honor system) | §5 4겹 + §7 WP-B1d 발화 관측 |
| P2 (키워드-박힘 채점) | §3.2C/D — producer 없는 게이트 advisory 강등 + 키워드 C-룰 삭제 |
| JW §8 "phase wiring 은 얇은 후속" | §4 — 각 phase ≤15줄, 스키마는 링크 참조 |
| dogfood 재사용 질문 | §1 실코드 판단 — 함수 이동 + 얇은 wrapper (§2.5) |

---

*본 문서는 설계 확정본이다. 사용자 리뷰 후 §7 WP 순서로 구현을 전개한다.*
