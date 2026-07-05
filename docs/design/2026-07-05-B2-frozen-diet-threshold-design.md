# 설계 문서 — B2: 동결 prose 다이어트 + 임계 재설정 (perverse incentive 제거)

> **작성**: Claude Fable 5 (설계 확정 — 코드/컨벤션/phase 편집 없음, 본 문서 단일 산출)
> **구현 위임**: opus/sonnet (§5 작업 패키지 기준)
> **일자**: 2026-07-05
> **선행 설계**: `docs/design/2026-07-04-verification-kernel-design.md` (§7.1/§7.2/§8/§11.5) · `docs/design/2026-07-05-B1-kernel-wiring-design.md` (순감 프로토콜 §6 방식 계승)
> **동기 근거**: `docs/design/2026-07-05-improvement-headroom-assessment.md` — B2 정의(§3 sufficiency bar) + §1.3(동결 prose 전액 과금 실측) + §1.4(임계 재설정 미실행 실측)
> **대상 저장소 상태**: HEAD `17147e6` — **B1 완료**(run_gate 배선 + phase 01/04/06/08/09 마이그레이션 + B1d 발화 리허설). frozen.* CheckSpec 2종은 WP6 에서 이미 advisory. 본 문서의 모든 라인/바이트 수치는 이 HEAD 실측이다.

---

## 0. 이 문서가 확정하는 것 (범위 계약)

두 부분, 원자적으로 한 묶음:

- **(A) 동결 prose 다이어트** — 설계 §8 이 동결(freeze)한 6개 mandate 군(멀티버스 폭
  5/7/9 · 7-우주 풀 의무 · universe philosophy distinct · viewer 3종/8탭 · 앙상블
  origin ≥0.2 · budget 80% 강제 소진)이 **커널 수준에서는 advisory 인데 prose 수준에서는
  여전히 전액 의무로 명령**되는 불일치를 해소한다. prose 의무를 advisory 로 강등한다.
- **(B) 임계 재설정** — 도달 불가 임계 `0.999`/`0.99999` 가 만드는 perverse incentive
  (점수 인플레이션 유인 + budget 소각 유인 + 세리머니 rerun 유인)를 **구조적으로 제거**한다.
  핵심은 숫자를 다른 숫자로 바꾸는 것이 아니라, "임계 도달"이라는 종료 의미론 자체를
  "값 기반 정지 조건(게이트 pass + 무회귀 + plateau + budget cap)"으로 교체하는 것이다.

**위반 불가 원칙 3개:**

1. **능력 삭제 아님, 의무 해제.** 멀티버스 폭 확대·viewer 3종·philosophy 분기·pre-bootup
   은 전부 *할 수 있는 채로* 남는다(스크립트/템플릿/CLI/컨벤션 how-to 물리 존치). 해제되는
   것은 "반드시 하라"는 명령뿐이다. 재승격 경로 = frozen.* A/B CheckSpec 의 편익 실증(§8).
2. **진실성 룰은 동결 대상이 아니다.** "산출물을 만들라"(의무)와 "만든 산출물이 거짓말하지
   않게 하라"(진실성)를 구분한다. 후자(9.ooo created_at 실값, 9.oo emit fidelity,
   9.nnn/9.ppp placeholder 차단)는 **조건부 존치** — 해당 산출물이 존재할 때만 발동.
3. **순감(§11.5a).** 편집 대상 파일 총량 after ≤ before 하드 룰(§3) — B1 §6 프로토콜 그대로.

**비목표(§6):** 멀티버스/viewer 의 재설계·물리 제거 · B3(self_lint 광역 순감) · 외부 벤치
harness · 구조화 dispatch log.

---

## 1. (A) 동결 강등 인벤토리 — mandate 군 6개, 실파일·실라인

각 항목: `{현재 의무 문구(위치), 강등 후, 근거, 순감 추정}`. 라인 번호는 HEAD `17147e6` 실측.

### F1. 멀티버스 폭 5/7/9 + 7-우주 풀 의무

manifest 는 이미 이중 진실을 기록한다: `pipeline.manifest.json` `multiverse_widths`
(활성 = G2:1/G3:3/G4:4/G5:6) vs `frozen_widths`(G3:5/G4:7/G5:9 — "편익 미실증, §8 동결,
비활성(advisory)"). 그러나 prose 는 여전히 5/7/9 를 default 의무로 명령한다 — 스펙 드리프트.

| # | 현재 의무 문구 (위치) | 강등 후 | 순감 추정 |
|---|---|---|---:|
| F1-1 | `conventions/multiverse-width-default-bump.md` **전체**(6,073 bytes) — "폭 default 격상 G3 3→5 / G4 4→7 / G5 6→9", 폭 7 head-to-head, root 폭 9 + child 18 universe | **동결 stub 으로 축약(≤1,000 bytes)**: "본 컨벤션의 폭 격상은 §8 동결 — 활성 폭은 manifest `multiverse_widths`(3/4/6), 격상 폭은 `frozen_widths` 참조. 폭 확대는 *가능*(사용자 명시 ack)하나 의무 아님. 재승격 = `frozen.multiverse_width_benefit` A/B 실증." frontmatter `trigger-when: 'frozen(advisory)'` | −5,100 |
| F1-2 | `phases/06-plan.md` L265-277 "폭 default 5/7/9" 표(G3 **5**(←3)/G4 **7**(←4)/G5 **9**(←6)) + "self_lint C-MWDB 가 검증" | 표 삭제 → "폭 = manifest `multiverse_widths` 단일 권위(활성 3/4/6). 격상은 frozen(advisory)" 2줄. **C-MWDB 는 self_lint 에 미구현(grep 0 — 가짜 참조)** → 참조 문구 삭제 | −700 |
| F1-3 | `conventions/resources.md` L279 "플랜-트리 폭 확장 (G3 폭 5/G4 폭 7/G5 폭 9, 옵션 default 10/12/16)" 기반 병렬 메모리 가드 서술 | 활성 폭(manifest) 기준으로 재표기 — 가드 로직 자체는 존치(능력) | −250 |
| F1-4 | `conventions/grades.md` L144 plan-tree 행 "✅ 강제 (폭 5 / 깊이 2)" | 활성 폭 표기 정정(manifest 참조) — L224 의 폭 6(활성) 표는 무수정 | −50 |
| F1-5 | `conventions/INDEX.md` L72 multiverse-width-default-bump 행 `trigger-when: always` | `frozen(advisory)` 로 갱신 | ±0 |

**7-우주 풀 의무**: G4 폭 7 전 우주 full 구현 의무는 F1-1/F1-2 의 격상 폭에서만 발생 —
격상 강등으로 함께 소멸. 활성 폭 3/4/6 의 기존 동작(`impl-multiverse-strict` 포함)은
**무수정**(§8 동결 리스트 밖 — 능력·현행 기본 동작 보존).

### F2. universe philosophy distinct (9.ccc) — phase 06 세리머니

| # | 현재 의무 문구 (위치) | 강등 후 | 순감 추정 |
|---|---|---|---:|
| F2-1 | `phases/06-plan.md` L70-143(실측 3,858 bytes) — universe meta.md `philosophy:` 필드 의무 + catalog 7종 + 본문 결정 헤더 ≥3 §-표제 의무 + `universe_philosophy_distinct.py` CLI 의무 호출(L129) + vacuous PASS 차단 절 | advisory 압축(≤1,200 bytes): "universe 간 설계 철학 분기는 *가능하며 권장* — catalog 7종, `universe_philosophy_distinct.py` 로 검증 *가능*. 강제 아님(§8 동결 — 분기 편익 A/B 미실증)." CLI 의무 호출 블록·차단 절 삭제. **단 L87-105 의 created_at 실값 규칙(9.ooo)은 진실성 룰 — candidate 파일 존재 시 조건부 존치**(원칙 2) | −2,600 |
| F2-2 | `conventions/hard-rule-9-extended.md` L22 의 9.ccc 항목("universe philosophy distinct") | "advisory(§8 동결)" 표기 부가 | −0 (표기 교체) |

`universe_philosophy_distinct.py` 스크립트·테스트는 물리 존치(능력). self_lint
C-UNIV-CREATED-AT 는 진실성 룰 검증이므로 존치.

### F3. viewer 3종 (HARD-RULE 9.nn/9.oo/9.pp 계열) + 8탭

감사 T7 이 "외부 배점 중립 45+ 산출물"로 지목한 최대 세리머니 비용. 강등 원칙:
**생산 의무 → advisory, 산출 시 진실성 의무 → 조건부 존치.**

| # | 현재 의무 문구 (위치) | 강등 후 | 순감 추정 |
|---|---|---|---:|
| F3-1 | `phases/00-naming.md` L12 — "phase 00 enter *직전* `pre_bootup.py bootstrap` 호출(3 viewer shell + 빈 골격 + HTTP server)" 의무 step 0 | "viewer 실시간 관측이 필요하면 `pre_bootup.py bootstrap` 으로 부팅 *가능*(옵션)" 1줄 | −350 |
| F3-2 | `conventions/pre-cold-session-bootup.md` (7,812 bytes) — 9.pp 부팅·teardown 의무 전문 | how-to(능력 문서)로 재프레임 + 의무 문구 제거 + 압축(≤4,500). teardown(PID 누수 차단)은 *부팅한 경우* 조건부 의무 존치(진실성/위생) | −3,300 |
| F3-3 | `phases/12-webview-assembly.md` L49 "필수 탭 (8 탭, 모두 항상 생성)" + L101 "키 자체는 의무" + L107-124 "emit fidelity — 8 탭 의무 키 + 빈값 정책" + L126-195 종료 게이트(6파일 존재 강제 + 검사 알고리즘 + `exit_gate.json` + "self_lint C-VEX" 선언) | phase 12 자체를 **옵션 phase(advisory)** 로 재표기. 탭 카탈로그·emit 프로토콜은 how-to 존치. 8탭 의무 키·종료 게이트·exit_gate 강제 삭제. **emit 하는 경우** 키 정직성(빈값을 채운 척 금지)만 조건부 존치(9.oo 진실성). **C-VEX 는 self_lint 에 미구현(가짜 참조)** → 선언 절 삭제 | −2,900 |
| F3-4 | `phases/13-interactive-viewer.md` L97-104 그레이드 매트릭스(G3 widgets ≥1 / G4+ ≥3 kpi_grid+topology+metric_chart 의무 + "HARD-RULE 9.nn invoke step 강제") + L106-120 Invoke step 의무 + L122-198 종료 게이트 + C-VEX 선언 | phase 13 을 **옵션 phase(advisory)** 로 재표기(G5 강제 해제 포함). dashboard.json schema·widget 카탈로그는 how-to 존치. invoke 강제·widget 하한·종료 게이트 삭제 | −2,400 |
| F3-5 | `phases/14-handoff.md` L138-160 — 9.nnn `lineage_finalize.py refresh --strict` + 9.ppp `placeholder_grep.py --include-viewer-json` **무조건 의무** | **조건부 의무로 전환**: "viewer 산출물(lineage.json/webview.json/dashboard.json)이 존재하면 refresh + placeholder 검사 의무" — 만든 viewer 가 거짓 placeholder 를 담은 채 마감되는 것 차단은 진실성 룰(원칙 2). viewer 미산출 run 은 해당 없음 | −150 |
| F3-6 | `phases/09-quality-gates.md` §V8 viewer-readiness (B1 존치분) | advisory 강등 — viewer 산출 시에만 참조 | −200 |
| F3-7 | `conventions/hard-rule-9-extended.md` L19-21(9.nn/9.oo/9.pp) + L24(9.nnn~9.ppp) | 각 항목에 "advisory / 조건부(산출 시 진실성)" 재표기 — 전문 압축 | −300 |
| F3-8 | `conventions/viewer-runtime.md`(11,039) · `phase-lineage-viewer.md`(27,557) · `prebuilt-shell-runtime-json.md` | **본문 대량 삭제는 B3 몫** — B2 는 frontmatter/도입부의 의무 어휘("의무", "강제")를 advisory 로 재표기 + INDEX trigger 갱신만(최소침습, 각 ≤10줄 편집) | −300 |
| F3-9 | `skills/theseus-orchestrator/SKILL.md` L38 산출물 매트릭스의 "`webview/` (8 탭)" 의무 나열 | "(webview 옵션)" 표기 | −50 |

viewer 템플릿(`templates/{webview,lineage-viewer,interactive-viewer}/dist/`)·스크립트
(`pre_bootup.py`/`emit_fidelity.py`/`lineage_finalize.py`/`placeholder_grep.py`/
`viewer_runtime.py`)·에이전트(`interactive-viewer-builder.md` 등)는 전부 물리 존치.

### F4. 앙상블 origin ≥0.2 each

| # | 현재 의무 문구 (위치) | 강등 후 | 순감 추정 |
|---|---|---|---:|
| F4-1 | `conventions/tournament-blind-rerun.md` L81 §6-d — "self_lint C-TBR-UNION 가 union 의 origin 분포 ≥ 0.2 each 검증" | 삭제. 근거 2중: (a) §8 동결 명시 대상, (b) §7.2 가 확정한 수학 모순 — 폭 7에서 7×0.2 = 1.4 > 1.0 (충족 불가능한 제약). **C-TBR-UNION 은 self_lint 미구현(가짜 참조)**. cherry-picking 방지 취지는 "origin 분포 *측정·보고*"(값, 강제 분포 없음)로 대체 1줄 | −250 |
| F4-2 | `conventions/ensemble-synthesis-default.md` L109 — origin ≥0.2 carry 적용 | 동일 강등(보고로 대체) | −150 |

### F5. budget 80% 강제 소진 — (B)와 한 몸 (§2.4 상호작용 참조)

| # | 현재 의무 문구 (위치) | 강등 후 | 순감 추정 |
|---|---|---|---:|
| F5-1 | `conventions/budget-saturation-loop.md` (6,723 bytes) — "minimum budget 사용률 ≥ 80% 강제", Step 2 pseudocode `budget_used_ratio < 0.80 → return True`(임계 도달 무관 sprint 강제 추가), `EARLY_STOP_VIOLATION`, "self_lint C-BSL + C-IPI fail" | **stop-policy 컨벤션으로 전면 재작성(≤3,000 bytes)**: 정지 조건 = §2.2 의 값 기반 3조건(게이트 pass + 무회귀 + plateau) OR budget ≥ 95%(hard cap 존치). 80% floor·EARLY_STOP_VIOLATION 삭제. Q-D-BUDGET-MODE default 반전 — 답 1 = "converge-on-evidence(신호 기반 정지)", Saturation 은 **사용자 명시 ack opt-in** 으로 강등(능력 보존). **C-BSL/C-IPI 는 self_lint 미구현(가짜 참조)** → 삭제 | −3,700 |
| F5-2 | `phases/10-test-loop.md` L4("0.999 까지 무한 반복 + budget cap 80% 사용… soft-converge") + L90("C-IPI 가 axis ≥2, C-BSL 이 budget 80%, C-GIS 가…" — **C-GIS 도 미구현**) + L69/83/155/211/223 의 0.999 | stop_policy(§2.2) 참조로 교체 + 가짜 참조 3건 제거 | −700 |
| F5-3 | `conventions/intent-plan-impl-sprint-trinity.md` — "axis 별 ≥ 2 sprint 강제" + 0.999 지향(L14/48/108/174-176) | axis ≥2 는 "권장 + 미달 시 handoff 에 사유 1줄 기록"으로 강등. **정직 표기**: 이 항목은 §8 동결 리스트 밖의 확장 적용이다 — 80% floor 와 동일한 세리머니-강제 계열(신호 없이 sprint 을 강제)이라 함께 강등하되, 그 판단을 본 문서가 명시적으로 진다 | −600 |

---

## 2. (B) 임계 재설정 — 0.999 / 0.99999 전수 조사 + 인센티브 구조 교체

### 2.1 실사용 전수 (HEAD 실측 — grep 확정, 추측 없음)

- `grep -rn "0\.999" conventions/` = **86 hits / 25 files**. `0\.99999` = repo 전체 **26 hits**.
- **커널 게이팅 경로(최우선)**: `checks/plan.dacapo_threshold.json` assertion 3 =
  `winner_score / winner_max >= 0.999`, `status: active`, `absence_policy: FAIL` — **B1 배선
  이후 이 도달 불가 임계가 phase 09 를 실제로 차단하는 커널 게이트가 됐다.** 정직 채점의
  실측 분포(감사·dogfood: winner 0.853/0.892/0.95/0.967, 정직 plateau 92~94)에서 이
  assertion 은 사실상 항상 FAIL → 실 run 은 (a) 영구 재경합 소각 또는 (b) winner 점수
  인플레이션 중 하나를 강요받는다. 감사 발견 8의 구조가 커널 안으로 이식된 상태.
- **코드 default 4곳 + self_lint**: `score.py:228`(`--threshold` default 0.999, exit 1 미달) ·
  `stagnation.py:37,153`(threshold 0.999 — plateau 인데 0.999 미달이면 "정체 문제"로 규정) ·
  `sprint_loop_cap.py`(4-layer 모두 ≥0.999 여야 stop 허용, 미달 시 exit 1 = 계속) ·
  `dacapo_threshold.py`(≥0.999 아니면 round N+1 강제, exit 1) · `self_lint.py:3335,3354`
  (`--score` 임계 0.99999).
- **컨벤션 규범 사용(주요)**: `budget-saturation-loop.md`(default 임계 0.999 통일) ·
  `grades.md` L25-27/114-116(그레이드 임계 컬럼 0.999·0.99999)/L208(자기평가 G5 0.99999) ·
  `autonomy.md` L111(rubric ≥0.999)/L237(0.999 미달→다음 스프린트 자율)/L275(메타 자기평가
  임계 0.99999) · `conservative-margin-judging.md` L26-34(rerun-별 score cap: rerun<3 이면
  0.999 채점 *금지*, 0.99999 는 rerun≥5+budget≥0.95 시만 허용) · `dacapo-mandatory-rerun.md`
  (임계 이상이라도 ≥1 rerun 의무) · `intra-phase-dacapo-loop.md` L54/345(임계 dict + "budget
  충분 시 임계 도달까지 무한 회귀") · `dacapo-enforcement.md`/`dacapo-skip-sentinel.md`
  L41,62(`fm.get('threshold', 0.999)`)/`dacapo-frontmatter-schema.md` L36 ·
  `plan-tournament-scoring-strict.md` L44 · `grader-in-sprint.md` L14/50(auto_proxy ≥0.999
  AND shadow ≥ target) · `impl-multiverse-strict.md` L74 · `regression.md` L20/49/216 ·
  `resources.md` L242/275 · `score-rubric-objectivity.md`/`deliverable-hurdle-supremacy.md`/
  `evidence-driven-sprint-planning.md`/`convention-traceability.md`(합성 서술).
- **phase/skill**: `phases/10-test-loop.md` 6곳 · `SKILL.md` L59/61/97/98/111 ·
  `theseus-orchestrator/SKILL.md` L39("임계 0.999 도달까지 무한 sprint")/L161/L165
  (stagnation_detected AND score<0.999 → exit 차단 + breakthrough 4종 의무)/L188(4-layer
  0.999)/L201(dacapo exit 1 시 round N+1 자동).
- **사례·회고 인용(비규범)**: `dacapo-flow-trace.md`/`intent-refresh.md` L211/
  `phase-lineage-viewer.md` L333 등 — 과거 회차 기록의 임계 언급. 강제력 없음.

### 2.2 재설정안 — 종료 의미론의 교체 (숫자 교환이 아님)

**perverse incentive 진단** (감사 발견 8 + 본 전수의 구조 종합): 도달 불가 임계 T 를
종료 게이트로 두면 — (i) **인플레이션 유인**: 종료하는 유일한 방법이 점수를 T 위로 신고하는
것(자기 신고 시절의 실측 패턴; 커널 후에는 winner 점수 성형 유인으로 이동), (ii) **budget
소각 유인**: 정직하게 채점하면 T 미달이 영구 지속 → 80% floor·무한 회귀 룰과 결합해
budget 95% cap 까지 세리머니 sprint/rerun 소각, (iii) **부정직 채점의 의무화**:
`conservative-margin-judging` 의 rerun-별 cap 은 측정값이 얼마든 rerun<3 이면 0.95/0.97
로 *깎아서* 보고하라는 명령 — 반대 방향의 점수 성형 강제.

**교체안 — 정지 조건을 인센티브-호환 값으로:**

1. **단일 권위**: `pipeline.manifest.json` 에 `stop_policy` 블록 신설(§11.3 정합):

   ```json
   "stop_policy": {
     "gate": "meta_audit_verdict_pass",
     "no_regression": true,
     "plateau_eps": 0.005,
     "plateau_window": {"G3": 2, "G4": 2, "G5": 3},
     "budget_hard_cap": 0.95,
     "_note": "종료 = gate AND no_regression AND (plateau OR budget_hard_cap). 점수는 보고 측정값 — 게이트 아님. plateau_eps/window 는 초기 스냅샷 파라미터(§2.3 정직 고지) — 리허설/벤치 run 마다 관측 delta 분포로 재추정."
   }
   ```

2. **sprint loop 종료** = 3조건 AND (또는 cap): (i) **게이트** — `run_gate` exit 0
   (meta_audit 게이팅 체크 전건 pass — 값), (ii) **무회귀** — `sprint.regression` 체크
   pass(커널 검증 값 시계열), (iii) **plateau** — 직전 `plateau_window` 회 sprint 의 score
   delta < `plateau_eps`(개선이 실측으로 멈춤 = 정직한 정지, 벌 아님). budget ≥ 95% 는
   무조건 정지(cap — 소진 의무 아님). **점수 절대값은 어디서도 게이트가 아니다** — 인플레
   해봤자 종료가 안 당겨지고(종료는 delta·verdict 가 결정), 정직 plateau 가 벌 대신 정지를
   준다. 두 유인이 동시에 소멸한다.
3. **dacapo rerun 결정** = 동일 구조의 라운드 단위 적용: 재경합은 "임계 미달이면 무한"이
   아니라 "직전 라운드 대비 winner delta ≥ eps 인 동안"(개선이 실측되는 동안) + budget cap.
   `dacapo-mandatory-rerun`(임계 초과여도 ≥1 rerun)은 advisory 로 강등 — rerun 은 신호가
   있을 때 하는 것이지 세리머니가 아니다.
4. **stagnation 의미 반전**: 현행(`stagnation.py` + orchestrator 9.ww L165) plateau AND
   score<0.999 → *exit 차단* + breakthrough 4종 의무 = 정직한 수렴을 벌하고 소각을 강제.
   재설정: plateau = **정지 신호**(최종 실측 점수를 정직 보고하고 종료). breakthrough 는
   budget 여유 + 사용자 opt-in(Q-D-BUDGET-MODE Saturation 답) 시에만 옵션.
5. **judge 점수 성형 폐지**: `conservative-margin-judging` 의 rerun-별 score cap 삭제 —
   judge 는 측정된 값을 그대로 보고한다(성형 강제는 방향 불문 부정직). polishing 동력은
   3의 delta 룰이 대체한다.

### 2.3 위치별 재설정 표 + "측정으로 정할 수 있는 것"의 정직한 경계

| 위치 (현행 의미) | 재설정 |
|---|---|
| `checks/plan.dacapo_threshold.json` assertion 3 `>= 0.999` (커널 게이팅) | **assertion 삭제** — 측정 유효성 assertion 1·2(winner_max>0, score≤max)만 게이팅 존치, `value`(ratio)는 계속 emit·보고. rerun 결정은 §2.2-3 의 delta 룰(컨벤션)로 이동. 무게이트 공백 아님: 유효성은 여전히 게이팅 + ratio 하락은 `sprint.regression` 이 잡는다 |
| `dacapo_threshold.py` `--threshold 0.999` + exit 1 = round 강제 | CLI 존치(능력). default 를 보고 모드로(threshold 미지정 시 exit 0 + ratio 보고). orchestrator L201 의 "exit 1 → round N+1 자동" 문구는 delta 룰 참조로 교체 |
| `score.py:228` `--threshold 0.999`, `passes_threshold` 로 exit | 보고 모드 default — 출력에 `delta`/`plateau` 필드 추가, exit 1 은 회귀(`prior - regression_threshold` 초과 하락) 시만. `passes_threshold` 필드는 하위호환 위해 유지하되 threshold 는 manifest 참조 |
| `stagnation.py` `threshold=0.999`("임계 미달 정체") | 의미 반전(§2.2-4): plateau 검출 = 정지 신호. `delta_to_threshold` 류 필드는 `last_delta` 로 교체 |
| `sprint_loop_cap.py` 4-layer ≥0.999 → stop 차단 | stop 판정을 `stop_policy` 3조건으로 교체(meta_audit verdict + regression + plateau) |
| `self_lint.py --score` 임계 0.99999 + `autonomy.md:275` | **삭제** — 판정은 이미 존재하는 `all_ok` boolean(값), score 는 보고 전용. "0.99999 도달"이라는 자기 평가 세리머니 제거 |
| `grades.md` L25-27/114-116 임계 컬럼(G3/G4 0.999, G5 0.99999) | 컬럼을 "stop_policy(manifest)" 참조로 교체. G5 의 엄격성은 도달 불가 숫자가 아니라 **구조**로: `plateau_window` 3(무개선 3회 확인 후 정지) + G5 전용 게이팅 체크 셋 |
| `conservative-margin-judging.md` L26-34 rerun-별 cap | 폐지(§2.2-5). 컨벤션은 "보수적 *prior* 로 심사하되 측정값 그대로 보고" 1절로 축약. self_lint C-CMJ 키워드 리스트 동기 수정(§4) |
| `dacapo-mandatory-rerun.md` ≥1 rerun 의무 | advisory 강등(§2.2-3) |
| `budget-saturation-loop.md` "default 임계 0.999 + 80% 강제" | F5-1 재작성 — stop_policy 컨벤션화 |
| `grader-in-sprint.md` L50 `auto_proxy ≥ 0.999 AND shadow ≥ target` | `meta_audit verdict pass AND shadow delta plateau` 로 교체 |
| `intra-phase-dacapo-loop.md` L54 임계 dict / L345 "임계 도달까지 무한 회귀" · `dacapo-enforcement.md` · `dacapo-skip-sentinel.md` L41,62 default 0.999 · `dacapo-frontmatter-schema.md` L36 · `plan-tournament-scoring-strict.md` L44 · `impl-multiverse-strict.md` L74 · `regression.md` L20/49/216 · `resources.md` L242/275 · `autonomy.md` L111/237 · `phases/10-test-loop.md` 6곳 · `SKILL.md` 5곳 · orchestrator `SKILL.md` L39/161/165/188/201 | 규범 문구를 stop_policy 참조로 일괄 교체. frontmatter `threshold:` 키는 `stop_policy_ref` 로 대체(스키마 문서 갱신) |
| 사례·회고 인용(dacapo-flow-trace 등) | "당시 임계 0.999(현행 stop_policy 이전)" 각주화 또는 삭제 — 순감 우선, 강제력 없음 명시 |

**측정으로 정할 수 있는 것 / 없는 것 (정직):** 현재 보유한 분포 데이터는 감사 n=1 +
dogfood self-run + cold 회차 3개의 정직 채점 92~97 — **새 "정상 임계"(예: 0.94)를 실측
분포 기반이라 주장하기엔 표본이 부족하다.** 그래서 B2 는 새 마법 숫자를 만들지 않는다:
임계-게이트 자체를 제거하고, 정지를 관측 가능한 값(verdict·delta·budget)에 건다. 이것은
"측정값 재설정"이 아니라 **인센티브 구조 변경**이며 그렇게 부른다. `plateau_eps 0.005` /
`window 2~3` 도 실측 분포가 아니라 초기 스냅샷 파라미터다 — manifest `_note` 에 재추정
의무를 박제하고, 리허설(B4)·벤치 run 의 sprint delta 분포로 갱신한다. §7.1 의 "측정값
분포 기반 재정의"는 이 재추정 루프로 이행된다.

### 2.4 budget 80% 강제와의 상호작용 (B2-A F5 와 겹침 정리)

두 룰은 하나의 소각 구동계다: **80% floor**("임계 도달해도 80% 미만이면 sprint 강제
추가") × **도달 불가 임계**("80% 넘어도 임계 미달이면 95%까지 계속") = 모든 run 이 budget
80~95% 를 무조건 소비. 한쪽만 고치면: 임계만 재설정 → 80% floor 가 여전히 세리머니
sprint 를 강제(개선 신호 없이도); floor 만 제거 → 임계 추격이 95% cap 까지 소각. 따라서
**F5(80% 해제)와 §2.2(임계 교체)는 한 커밋 계열(WP-B2b)에서 원자적으로 처리**하며, 두
자리를 모두 같은 `stop_policy` 참조로 수렴시킨다(권위 1곳 — 드리프트 재발 차단).

---

## 3. 순감 프로토콜 (§11.5a — B1 §6 방식 그대로)

**측정 방법**: 파일별 `wc -c`(bytes) + `python len()`(chars) 병기. 아래 before 는 HEAD
`17147e6` 실측 bytes.

| 파일 | before | after 목표 |
|---|---:|---|
| `conventions/multiverse-width-default-bump.md` | 6,073 | ≤ 1,000 |
| `conventions/budget-saturation-loop.md` | 6,723 | ≤ 3,000 |
| `conventions/conservative-margin-judging.md` | 5,710 | ≤ 2,200 |
| `conventions/dacapo-mandatory-rerun.md` | 4,303 | ≤ 1,500 |
| `conventions/pre-cold-session-bootup.md` | 7,812 | ≤ 4,500 |
| `conventions/intent-plan-impl-sprint-trinity.md` | 7,179 | ≤ 6,600 |
| `conventions/grader-in-sprint.md` | 10,393 | ≤ 9,900 |
| `conventions/tournament-blind-rerun.md` | 5,196 | ≤ 4,950 |
| `conventions/ensemble-synthesis-default.md` | 5,972 | ≤ 5,850 |
| `conventions/intra-phase-dacapo-loop.md` | 19,513 | ≤ 18,800 |
| `conventions/dacapo-enforcement.md` | 14,197 | ≤ 13,800 |
| `conventions/dacapo-skip-sentinel.md` | 12,523 | ≤ 12,300 |
| `conventions/dacapo-frontmatter-schema.md` | 9,903 | ≤ 9,750 |
| `conventions/plan-tournament-scoring-strict.md` | 4,225 | ≤ 4,150 |
| `conventions/autonomy.md` | 19,416 | ≤ 19,100 |
| `conventions/grades.md` | 13,297 | ≤ 13,000 |
| `conventions/regression.md` | 11,492 | ≤ 11,250 |
| `conventions/resources.md` | 15,445 | ≤ 15,200 |
| `conventions/impl-multiverse-strict.md` | 7,068 | ≤ 6,950 |
| `conventions/hard-rule-9-extended.md` | 4,893 | ≤ 4,700 |
| `conventions/INDEX.md` | 7,932 | ≤ 8,050 (행 표기 갱신 — 개별 순증 허용) |
| `phases/00-naming.md` | 5,447 | ≤ 5,200 |
| `phases/06-plan.md` | 56,329 | ≤ 53,000 |
| `phases/09-quality-gates.md` | 32,506 | ≤ 32,350 |
| `phases/10-test-loop.md` | 16,160 | ≤ 15,400 |
| `phases/12-webview-assembly.md` | 11,375 | ≤ 8,500 |
| `phases/13-interactive-viewer.md` | 13,927 | ≤ 11,500 |
| `phases/14-handoff.md` | 10,131 | ≤ 10,050 |
| `SKILL.md` (harness) | 9,773 | ≤ 9,700 |
| `../theseus-orchestrator/SKILL.md` | 34,388 | ≤ 34,000 |
| **합계 (30파일)** | **389,301** | **≤ 360,000 (순감 ≥ ~29KB — 개별 목표 합산 ≈ 356,250)** |

**하드 룰(WP 완료 조건):** 위 표 대상 **총량 after ≤ before — 초과 시 그 WP 실패, 재작업.**
개별 파일 순증은 허용(INDEX 등), 총량이 기준. `viewer-runtime.md`/`phase-lineage-viewer.md`
/`prebuilt-shell-runtime-json.md` 는 B2 에서 ≤10줄 표기 편집만이므로 표 밖(총량 계산에는
포함해도 무방 — 변동 ±0.5KB). `self_lint.py`/manifest/CheckSpec/코드 4종은 실행체 —
지시 질량 표 밖이되, self_lint.py 는 **줄수 after ≤ before 보고 의무**(C-CMJ 축소 + C-PCB
서브체크 삭제로 소폭 순감 예상). **보고 의무**: 각 WP 완료 시 after 실측치를 커밋 메시지
또는 docs/design/ 갱신에 수치 기록(B1 §6 동일).

---

## 4. 회귀 안전 — 무엇이 안 깨지는지, 실측 근거로

1. **frozen.\* CheckSpec 은 무영향 (확인 완료).** `frozen.multiverse_width_benefit` /
   `frozen.viewer_mandatory` 는 `status: "frozen"` — `meta_audit.py` L105/L231-235/L259 가
   무조건 ADVISORY(비게이팅) 처리하며 `test_meta_audit_frozen.py` 5개 테스트가 이를 고정.
   B2 는 이 2파일과 커널 frozen 정책을 **건드리지 않는다** — prose 를 manifest 의 이미
   확립된 상태에 *정합*시킬 뿐이다.
2. **커널 게이팅 변경은 1곳뿐, 방향은 완화.** `plan.dacapo_threshold.json` assertion 3
   삭제(§2.3)는 FAIL→PASS 방향 완화라 기존 pass run 을 깨지 않는다. 게이트 공백 반론에
   대한 답: 유효성 assertion 1·2 존치 + ratio 는 value 로 계속 기록 + 하락은
   `sprint.regression`(active, 게이팅)이 잡는다. WP-B2a 가 B1d 리허설 fixture 재실행으로
   "정직 ratio 0.95 → 유효성 PASS + value 보고" 전환을 관측·기록한다.
3. **self_lint — 구현 룰과 가짜 참조의 구분 (grep 실측):**
   - **미구현(가짜 참조 — self_lint 무영향, prose 정리만)**: C-MWDB · C-BSL · C-IPI ·
     C-GIS · C-TBR-UNION · C-VEX — 전부 `self_lint.py` grep 0 (B1 이 확인한 C-V6X/C-GJM
     류 "선언≠구현" 패턴의 잔여분). 참조 문구 삭제는 어떤 테스트도 못 깬다.
   - **구현 룰 중 수정 필요**: **C-CMJ**(L2714-2722 — 키워드 `"0.999 마진"`,
     `"rerun-별 score cap"` 요구) → 컨벤션 재작성과 동기해 키워드 리스트를
     `"보수적 prior"`/`"측정값 그대로 보고"` 류로 교체. **C-PCB**(L2897 — phase 00 에
     `'pre_bootup.py bootstrap'` step 문자열 요구) → 해당 서브체크 삭제(옵션 문구에도
     문자열은 남지만, 키워드-핀으로 의무를 되박는 P2 잔재를 남기지 않기 위해 요구 자체를
     제거). **`--score` 경로**(L3335/3354) → 0.99999 판정 삭제, all_ok 보고.
   - **구현 룰 중 존치(양립 확인)**: C-PSR/C-EFS/C-VAR/C-VRL/C-IVP/C-PLV/C-WV1/C-WV2/
     C-IV1 — 스킬 저장소 *자기 파일*(컨벤션·템플릿·샘플)의 존재/키워드 검증이며, 검증
     키워드가 능력 명칭(예: "prebuilt shell", "theseus-view")이라 advisory 재표기 후에도
     본문에 자연 잔존. C-SDT/C-EDP/C-ESD — cross-ref 문장 검증: budget-saturation-loop
     재작성 시 해당 cross-ref 문장 유지를 WP 지시에 명시. C-UNIV-CREATED-AT/C-IMS/
     C-IMS-SEMANTICS/C-CNS — B2 비대상 또는 진실성 룰, 무수정.
   - **완료 조건**: 매 WP 후 `self_lint.py` **all_ok=True**.
4. **B1 과의 충돌 없음 (구역 분리).** B1 이 확정한 편집 구역과 B2 구역은 파일 내 분리:
   phase 06 — B1c 의 §plan-todos(L61-68) vs B2 의 L70-143/L265-277; phase 09 — B1b 의
   run_gate §첫 동작 vs B2 의 §V8 1절; phase 10 — B1 의 §진입 전제(L6-11, gate_meta_audit
   확인) **존치**, B2 는 종료 조건 절만 교체. `run_gate.py`/`meta_audit.py`/`kernel.py` 는
   B2 무수정. B1d 리허설 fixture 는 WP-B2a/B2d 의 회귀 기준선으로 재사용.
5. **테스트 동기화 목록(수정 예상)**: `test_dacapo_threshold.py`(보고 모드 default) ·
   `test_score.py`(threshold 의미) · `test_stagnation.py`(의미 반전) ·
   `test_sprint_loop_cap.py`(stop_policy 조건) · `test_manifest.py`(stop_policy 블록 —
   `REQUIRED_KEYS` 확장 시) · `test_self_lint.py`(C-CMJ/C-PCB/--score). 커널 코어
   (`kernel.py`/`meta_audit.py`) 테스트는 무영향(스키마 무변경 — assertion 배열 내용만).
   완료 조건: `pytest scoring/ -q` 전건 + dogfood 재실행 verdict·counts 불변.

---

## 5. 롤아웃 WP (opus/sonnet) + 값 기반 완료 조건

| WP | 내용 | 권장 모델 | 완료 조건 (값 기반) |
|---|---|---|---|
| **WP-B2a** | stop_policy 기계부 — manifest `stop_policy` 블록(§2.2-1) + `plan.dacapo_threshold.json` assertion 3 삭제(§2.3) + `score.py`/`stagnation.py`/`sprint_loop_cap.py`/`dacapo_threshold.py` 보고-모드 default + `self_lint.py --score` 0.99999 삭제 + 테스트 동기화(§4.5) | **opus** | (i) `pytest scoring/ -q` 전건 통과, (ii) dogfood 재실행 verdict·counts 불변, (iii) B1d 리허설 fixture 재실행 — 정직 winner ratio(<0.999)가 게이트 FAIL 이 아니라 "유효성 PASS + value 보고"로 관측·기록, (iv) `grep -rn "0\.999" scoring/ checks/` 에서 게이팅 판정 경로 하드코드 0(보고 필드·주석 제외 목록 명시) |
| **WP-B2b** | (B)+F5 prose — `budget-saturation-loop.md` stop-policy 재작성(F5-1) + `conservative-margin-judging.md`/`dacapo-mandatory-rerun.md`/`grader-in-sprint.md`/trinity/dacapo 4종/`plan-tournament-scoring-strict.md`/`autonomy.md`/`grades.md`/`regression.md`/`resources.md`/`impl-multiverse-strict.md`/`phases/10`/양 SKILL.md 의 임계·80% 규범 문구를 stop_policy 참조로 교체(§2.3 표) + C-CMJ 키워드 동기화 + 가짜 참조(C-BSL/C-IPI/C-GIS) 제거 | sonnet | (i) `self_lint.py` all_ok=True, (ii) `grep -rn "0\.999\|0\.99999" conventions/ phases/ SKILL.md ../theseus-orchestrator/SKILL.md` 의 규범(의무·게이트) 사용 0 — 잔존 hit 전건이 사례 각주임을 목록으로 보고, (iii) §3 표 해당분 after 실측 보고 + 총량 순감 유지 |
| **WP-B2c** | (A) F1~F4 prose — 멀티버스 폭(F1-1~5) + philosophy(F2) + viewer(F3-1~9, 진실성 조건부 존치 포함) + origin(F4) + INDEX 행 + HR9 재표기 + C-PCB 서브체크 삭제 + 가짜 참조(C-MWDB/C-TBR-UNION/C-VEX) 제거 | sonnet | (i) self_lint all_ok=True, (ii) manifest `drift-check` == [] (활성 폭 3/4/6 과 prose 정합), (iii) 의무 문구 부재 grep 검증: `"폭 default 5"` / `"8 탭, 모두 항상 생성"` / `"invoke step 강제"` / `"80% 강제"` / `"≥ 0.2 each"` 0건, (iv) 능력 존치 검증: `pre_bootup.py`/`universe_philosophy_distinct.py`/`lineage_finalize.py`/viewer templates 파일 존재 + 각 how-to 문서에서 참조 유지, (v) §3 표 해당분 after 실측 보고 |
| **WP-B2d** | **회귀 리허설(완료 게이트)** — B1d fixture full 재실행 + dogfood + 전체 pytest + 왕복 관측 | sonnet | (i) run_gate 가 리허설 submission 에서 exit 0/1 을 §2.2 의미론대로 냄(의도적 회귀 주입 시 `sprint.regression` FAIL 관측 → 제거 시 pass 전환 — **임계 게이트 제거 후에도 문이 실제로 여닫힘을 값으로 증명**), (ii) frozen.\* 2종이 여전히 ADVISORY 로 분류(비게이팅 유지 확인), (iii) §3 표 **전체** after 실측 최종 보고 — 총량 after ≤ before 하드 룰 판정, (iv) `pytest scoring/ -q` + self_lint all_ok |

**의존**: WP-B2a → {WP-B2b, WP-B2c}(병렬 가능 — 파일 교집합은 phases/10·SKILL.md 뿐이므로
B2b 선행 권장) → WP-B2d. **WP-B2d 가 B2 의 완료 게이트다** — (i) 왕복 관측 없이 B2 완료
선언 불가(B1d 와 동일 규율).

---

## 6. 비목표 · 정직 고지

1. **재설계·물리 제거가 아니다.** 멀티버스/viewer/philosophy/pre-bootup 의 스크립트·템플릿·
   에이전트·how-to 문서는 전부 남는다. B2 가 하는 것은 §8 동결의 prose 이행 — *의무 해제*
   뿐이다. 재설계는 A/B 실측 이후 별도 판단(커널 설계 §13 비목표 유지).
2. **편익은 A/B 로만 실증된다 — 양방향.** 폭 확대·viewer 가 외부 점수에 편익이 있다는
   실증이 0건이라 동결하는 것이지, *손해라는 실증*도 0건이다. breadth 가 유효했던 과제군
   에서 이 다이어트가 손해일 가능성은 배제 못 하며(평가 §4.1), 그 판별이 frozen.\*
   CheckSpec(A/B producer)과 벤치의 존재 이유다. 재승격 경로는 열려 있다.
3. **외부 점수 인과는 가설이다.** "세리머니 토큰 회수 → content depth ↑ → 외부 점수 ↑"는
   벤치(§11.5b)로만 확증된다. B2 가 사전에 값으로 증명하는 것은 §3 의 지시 질량 순감과
   §5 의 게이트 동작 뿐이다 — 둘을 혼동해 "줄었으니 개선됐다"고 주장하지 않는다.
4. **plateau 파라미터는 실측 분포가 아니라 스냅샷이다.** `plateau_eps`/`window` 초기값의
   근거 표본(감사 n=1 + dogfood + cold 3회)은 분포라 부르기에 부족하다. manifest `_note`
   에 재추정 의무를 박고, 리허설(B4)·벤치의 sprint delta 로 갱신한다. §7.1 의 "측정값 분포
   기반"은 일회 확정이 아니라 이 재추정 루프로 이행한다.
5. **범위의 명시적 확장 2건**: (a) trinity axis ≥2 강등(F5-3)과 (b) stagnation-breakthrough
   의무(9.ww) 반전(§2.2-4)은 §8 동결 리스트의 문자 밖이다 — 그러나 둘 다 "신호 없는 세리머니
   강제"라는 동일 인센티브 결함이라 함께 처리하며, 이 판단의 책임은 본 문서에 있다.
6. **진실성 룰 존치의 비용**: 9.nnn/9.ppp/9.ooo 를 조건부로 남기는 것은 viewer/candidate
   를 *만든* run 에는 여전히 과금이다 — 거짓 산출물 방지 비용으로 정당하다고 판단하나,
   이 역시 벤치 데이터로 재평가 대상이다.
7. **B3 와의 경계**: viewer 계열 대형 컨벤션(`phase-lineage-viewer.md` 27.5KB 등)의 본문
   다이어트, dacapo/regression/shadow 계열 self_lint C-룰 광역 순감(~300줄 후보)은 B3 몫 —
   B2 는 의무 어휘 재표기와 커널-인수·검증대상-소멸분만 지운다(무게이트 공백 금지, B1 규율).

---

## 7. 역추적 매핑

| 근거 | 본 설계 대응 |
|---|---|
| 평가 B2 완료 조건 "frozen 의무 prose→advisory, 임계 실측 기반 교체, budget 80% 해제" | §1 F1~F5 + §2.2 stop_policy + F5-1 |
| 커널 §8 동결("게이트 자격 정지 — 삭제 아님") | §0 원칙 1 + §6.1 (능력 전량 존치, 재승격 경로) |
| 커널 §7.1 "임계를 측정값 분포 기반으로 재정의, 인플레·budget 소진 유인 제거" | §2.2 (게이트→값 정지 조건) + §2.3 (정직한 경계 — 새 마법 숫자 없음, 재추정 루프) |
| 커널 §7.2 origin 0.2 수학 모순(7×0.2>1.0) | F4 삭제 근거 |
| 감사 발견 8 (도달 불가 임계의 소각 구조) | §2.2 perverse incentive 진단 + §2.4 (80%×임계 동시 제거의 원자성) |
| 감사 T5/T7 (멀티버스·viewer 편익 미실증, 목적-수단 역배분) | §1 F1~F3 |
| 커널 §11.3 단일 매니페스트 | §2.2-1 stop_policy — 임계 권위 1곳, 드리프트 재발 차단 |
| 커널 §11.5(a) 순감 | §3 — before 실측 31파일 409,301 bytes, after ≤ 383,000, 총량 하드 룰 |
| B1 §6 순감 프로토콜 · §7 WP-B1d 왕복 관측 규율 | §3 방식 계승 + §5 WP-B2d 완료 게이트 |
| P2 (키워드-박힘) 재발 방지 | §4.3 — C-PCB 키워드-핀 제거, 가짜 참조 6건(C-MWDB/C-BSL/C-IPI/C-GIS/C-TBR-UNION/C-VEX) 정리 |
| 진실성 vs 세리머니 구분 (9.ooo/9.oo/9.nnn/9.ppp) | §0 원칙 2 + F2-1/F3-3/F3-5 조건부 존치 + §6.6 비용 정직 고지 |

---

*본 문서는 설계 확정본이다. 사용자 리뷰 후 §5 WP 순서로 구현을 전개한다.*
