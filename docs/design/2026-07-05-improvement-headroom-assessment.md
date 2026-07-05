# 개선 여지 평가 — 벤치마크 진입 충분성 판정 (콜드 분석)

> **작성**: Claude Fable 5 (콜드 분석가 — 코드/설계 산출 없음, 본 평가 문서 단일 산출)
> **일자**: 2026-07-05
> **질문**: 지금 상태가 외부 벤치마크(비싸고 느림)를 쓸 만큼 충분히 개선됐는가, 아니면 값싸게 딸 개선이 더 남았는가?
> **근거**: `.tmp/cold-parallel-audit-2026-07-04-report.md` · `docs/design/2026-07-04-verification-kernel-design.md` · `docs/design/2026-07-04-kernel-dogfood-report.md` · `docs/design/2026-07-05-judgment-gate-producers-design.md` · 저장소 실파일 실측 (본문 각 항목에 명시)
> **baseline (재평가 제외)**: 검증 커널 5법칙 + Evidence Contract + pipeline.manifest.json + 생성형 meta_audit + 측정 producer 13종(scoring/quality/plan/sprint/cold) + 판단-게이트 producer 3종(JW1~5) + 승격군 CheckSpec 15개 + frozen advisory 정책 + 인코딩/재현성 수정 — 이상은 완료로 인정하고 평가하지 않는다.

---

## 0. 판정 한 줄

**아니오 — 지금 벤치마크에 가면 안 된다.** 결정적 이유는 단순하다: **지금 실 파이프라인 run 을 돌리면 커널이 단 한 번도 실행되지 않는다.** 16개 페이즈 파일·orchestrator SKILL.md·HARD-CORE.md·컨벤션 90개 전부에 `meta_audit`/`measure_submission`/`pipeline.manifest`/`CheckSpec`/`kernel` 참조가 **0건**이다(§1.1 실측). 커널의 유일한 호출자는 `dogfood.py`(자기 코드 검사)다. 비싼 벤치마크가 측정하게 될 것은 "커널 도입 후" 시스템이 아니라 감사 시점과 동일한 "도입 전" 시스템 — prose 게이트 + self_lint 74 C-룰 + 0.999 소각 루프 + 동결 항목 전액 과금 — 이다. 설계 §11.5(b)가 요구한 "커널 도입 전/후 controlled 비교"의 '후'가 아직 존재하지 않는다.

---

## 1. 남은 개선 기회 인벤토리

각 항목: `{무엇, 외부 성능 인과(또는 내부 위생), 레버리지, 비용, 선행 의존}`. 레버리지의 외부 인과는 §4 정직 고지대로 **가설**이며, 여기서는 "외부 점수에 닿는 경로가 논증 가능한가"를 기준으로 분류한다.

### 1.1 커널 파이프라인 배선 0 — §9 마이그레이션 전면 미착수 (최대 갭)

**실측 확정** (추측 아님):

```
grep -rE 'meta_audit|measure_submission|pipeline\.manifest|CheckSpec|kernel' \
  phases/ SKILL.md HARD-CORE.md ../theseus-orchestrator/SKILL.md conventions/
→ 0건 (exit 0, 매치 없음)
```

- 16개 페이즈 파일 중 커널 경로를 참조하는 것은 **0개**. `phases/09-quality-gates.md`의 `measure_` 매치는 sprint-40의 옛 `harness/measure_run.py`(별개 물건)뿐이며, phase 09 는 여전히 "9 정적 게이트 + N derived 게이트"(prose) + self_lint 로 판정한다.
- 판단-게이트 producer 의 선언 아티팩트(`intent-criteria.json`/`plan-todos.json`/`solid-contract.json`)를 저작하라는 지시가 phase 01/04/06/08 어디에도 없다 — JW 설계 §8이 명시적 비목표로 미룬 "얇은 후속 wiring"이 그대로 미착수. 따라서 실 run 에서 `scoring.correctness/scope_fit/solid` 는 dogfood 에서와 달리 **다시 deficit** 이 된다.
- §9 표의 15 페이즈 분류(P/W/F/N) 중 실제로 페이즈 게이트가 CheckSpec 으로 교체된 페이즈: **0개**. producer 는 존재하나(scoring/producers/ 13종) 파이프라인의 어떤 페이즈도 그것을 호출하도록 지시받지 않는다.
- 부수 효과: 생성형 meta_audit 이 배선되지 않았으므로, 하드코딩 사각이 확인된 옛 `phase_invoke_audit.py`(P5)가 여전히 실 run 의 현역 감사기다 — P5 해소가 실 run 에는 아직 미적용.

| 무엇 | phase 09 진입/종료에 producer 실행 + `meta_audit` 게이팅 의무 1블록; phase 01/04/06/08 에 선언 아티팩트 저작 지시; 옛 prose 게이트/`phase_invoke_audit` 를 커널 판정으로 대체(순증 아닌 교체) |
|---|---|
| 외부 인과 | **간접이지만 전제 조건.** (a) sprint loop 의 개선 신호가 자기 신고에서 값으로 바뀌어야 "재채점 종료"가 아닌 "산출물 개선"으로 budget 이 흐른다(감사 T1). (b) 벤치마크가 '커널 후' 시스템을 측정하게 만드는 유일한 방법 — 이것 없이는 벤치 결과의 attribution 자체가 성립 안 함. |
| 레버리지 | **H** |
| 비용 | **M** (producer/CheckSpec/manifest 는 완성 — 남은 것은 프롬프트 편집. JW 설계 §8 스스로 "얇은 후속 단계"로 규정) |
| 의존 | 없음 (모든 하부 자산 완료) |

### 1.2 지시 질량 순감(§11.1/§11.5a) 미실행 — 수치로 역방향

**실측**:

| 지표 | 감사 시점 (2026-07-04) | 현재 HEAD | 방향 |
|---|---:|---:|---|
| self_lint.py | 3,466줄 / 93 C-룰 | **3,472줄 / 74 C-룰 계열(고유 접두 실측)** 전부 활성 — 삭제·강등 0 | 사실상 불변 |
| conventions/ | 87개 | **90개 / 809,152 bytes** | **순증** |
| phases/06-plan.md | 44,890 chars | **55,695 bytes** | **순증** |
| orchestrator SKILL.md | HR9 서브룰 ~28개 inline | **34,176 bytes, HR9 인덱스+서브룰 유지** | 불변 |
| HARD-CORE.md | 7,211 chars (cap 위반) | **3,888 chars** (all_ok) | **유일한 감소** |

dogfood 보고 §4가 스스로 자백한 대로("이 dogfood 자체는 self_lint 의 prose C-룰을 삭제하지 않는다"), 성공 지표 §11.5(a) "phase 진입 지시문 chars 감소"는 always-load 계층(HARD-CORE) 밖에서 **실행되지 않았고, 총량은 오히려 늘었다.** 감사 발견 4의 "phase 06 진입 실측 ~41만 chars → silent skip 필연" 구조가 그대로 살아 있다 — phase 06 하나에 컨벤션 ~20개가 lookup 매핑되어 있고(HR9 인덱스 실측) 그 원천 809KB 는 커졌다.

| 무엇 | (a) 커널이 게이팅을 인수한 차원(correctness/scope/solid/deep/dry/define/dacapo/regression/cold)의 self_lint C-룰 삭제·참조 강등, (b) phase 06/09 prose 와 HR9 인덱스에서 커널·frozen 이 대체한 의무 제거, (c) §11.5(a) 값 재측정(페이즈별 진입 chars) |
|---|---|
| 외부 인과 | **가장 직접적 후보.** 외부 채점자는 산출물 내용을 본다 — 지시 질량이 모델의 컨텍스트/준수 능력을 포화시키면(발견 4) 실 코드·문서 depth 가 잠식된다는 가설. 인과는 벤치로만 확증되나, ~41만 chars 가 "어떤 모델도 동시 준수 불가" 수준이라는 정적 논증은 감사가 이미 확립. |
| 레버리지 | **H** |
| 비용 | **M** (C-룰 삭제는 기계적·저위험 — 커널이 동일 차원을 값으로 게이팅한다는 전제에서. phase 06 prose 다이어트는 신중한 편집) |
| 의존 | **1.1 선행** (커널이 게이팅을 실제 인수해야 C-룰을 안전하게 지울 수 있음 — 안 그러면 무게이트 공백) |

### 1.3 §8 동결 다이어트 — CheckSpec 은 advisory, prose 는 여전히 전액 과금

**실측**: frozen.* 2종은 manifest/meta_audit 수준에서 비게이팅 처리됐다(WP6 완료 — baseline). 그러나 LLM 이 실제로 읽고 따르는 prose 는 동결 대상 작업을 **여전히 의무로 명령한다**:

- 멀티버스: `multiverse_widths` G3-3/G4-4/G5-6 활성 + phase 06 universe philosophy distinct 의무(9.ccc, catalog 7종) + universe 별 06-plan.md 결정 헤더 ≥3 + `impl-multiverse-strict`(9.jj) + G5 깊이 2 트리 — phase 06-plan.md·HR9 인덱스 실측.
- viewer: 9.nn/9.oo/9.pp — phase 12 webview 6파일 강제 + phase 13 widgets ≥1(G3)/≥3(G4, kpi_grid+topology+metric_chart 의무) + invoke step 강제 + 8탭 의무 키. 감사 T7이 "외부 배점 중립 45+ 산출물"로 지목한 바로 그 비용.
- budget: `budget-saturation-loop.md` — 임계 0.999 default + **budget 80% 사용 강제** + 조기 종료 금지, 전부 현행.

즉 §8 동결의 편익("의무 해제 후에만 content depth 부족이 오버헤드의 결과인지 원인인지 판별 가능")은 **아직 실행되지 않았다** — 커널은 종료를 안 막지만, 에이전트의 토큰은 prose 명령대로 계속 소비된다.

| 무엇 | 동결 대상(폭 확대 세리머니·viewer 3종 의무·8탭·budget 80% 강제)의 prose 의무를 advisory 로 강등하고 manifest frozen 상태와 정합시킴. 삭제 아님 — §8 그대로 "게이트 자격 정지". |
|---|---|
| 외부 인과 | **직접 후보.** 한정 budget 벤치에서 breadth·viewer 세리머니가 winner 의 depth(디버깅·엣지케이스)를 잠식한다는 감사 T5/T7 가설의 실행. 외부 배점이 0인 산출물에 강제 배분되던 토큰이 채점 대상으로 회수됨. |
| 레버리지 | **H** |
| 비용 | **L~M** (prose 강등 편집 — 신규 메커니즘 불요) |
| 의존 | 없음 (manifest 측은 이미 준비됨) |

### 1.4 임계 0.999/0.99999 재설정 미실행 (§7.1)

**실측**: `conventions/budget-saturation-loop.md` — "default 임계 = 0.999 (G3/G4)", "G5 = 0.99999", "minimum budget 사용률 ≥ 80% 강제" 전부 현행. `conventions/autonomy.md:275` 는 메타 자기평가 임계 0.99999. 설계 §7.1 은 "구체 임계값은 dogfood 실측 후 확정"이라 했고 dogfood 는 실측값(정직 채점 plateau 92~94 재확인 + 커널 value 분포)을 냈으나, **재설정은 수행되지 않았다.** 감사 발견 8의 구조 — 도달 불가 임계는 인플레이션·budget 소각·라운드 소각만 남긴다 — 가 실 run 에 그대로 적용된다.

| 무엇 | 임계를 커널 검증 값 분포 기반으로 재정의(예: 측정된 plateau + 회귀-부재 조건), budget 80% 강제 소진 해제(1.3과 중첩) |
|---|---|
| 외부 인과 | **직접 후보.** 벤치 budget 이 도달 불가 임계 추격(= 재채점 세리머니)에 소각되는 대신 content 에 흐름. |
| 레버리지 | **H** |
| 비용 | **L** (컨벤션 값 편집 + 근거 기록) |
| 의존 | 1.1 과 약결합 (재설정의 근거 분포가 "커널 검증 값"이어야 정당 — dogfood 실측으로 1차 근거는 이미 존재) |

### 1.5 잔여 5 deficit — 각각 성격이 다르다

| deficit | 저비용 사전 마감 가능? | 판정 |
|---|---|---|
| `scoring.coverage` | **예** — coverage 도구(pytest-cov) 설치·배선. producer 의 coverage artifact 파싱 경로는 이미 존재, 환경에 도구만 부재(dogfood §1.1 #4). | 비용 **L**, 레버리지 **M** (내부 신호 완결 + 테스트 품질의 실측화 — 외부 rubric 에 coverage 차원이 있으면 직접) |
| `scoring.e2e` | 부분 — self-run 에 e2e analog 없음. 실 과제 run 에서 e2e junit 이 나오면 자동 충족. | 사전 마감 대상 아님 — **리허설 run 에서 충족 확인**이 올바른 마감 형태 |
| `plan.dacapo_threshold` | 아니오 — tournament winner artifact = 실 파이프라인 run 필요 | 동일 — 리허설 run 검증 항목 |
| `plan.tournament_independence` | 아니오 — shadow-grade artifact = 실 run 필요 | 동일 |
| `sprint.regression` | 아니오 — 점수 시계열 = 2+ sprint 필요 | 동일 |

즉 5개 중 사전에 값싸게 닫히는 것은 coverage 1개뿐이고, 나머지 4개의 "마감"은 **실 run 1회에서 evidence 가 실제로 생산되는지의 확인**이다 — 이것이 §3 sufficiency bar 의 드레스 리허설 항목이 되는 이유다.

### 1.6 감사 P/T 테마 중 기타 미해소분

| 항목 | 무엇 / 현황 (실측) | 외부 인과 | 레버리지 | 비용 | 의존 |
|---|---|---|---|---|---|
| **에이전트 모델 라우팅 역전** (발견 28) | `agents/implementer.md` "권장 모델: Sonnet", `agents/tester.md` "권장 모델: Haiku" 현행 — 점수를 결정하는 implementer 가 중간 모델, Opus 는 문서 페이즈 집중. 설계 §13 비목표였으나 편집 비용은 몇 줄. | **직접 후보** — implementer 출력 품질이 외부 점수와 가장 짧은 인과 사슬. 단 달러 비용 증가 트레이드오프. | **H** (가설) | **L** | 없음 |
| **headless 인터뷰 프로토콜** (발견 20) | 사전 답 매핑 HARD-RULE 로 부분 완화(감사 자체 판정). 무인 벤치에서 phase 04 가 자가 채움으로 새는 잔여 리스크. | 직접 (의도 오독 → 외부 감점) | M | L (리허설 run 에서 관측 후 필요 시 보강) | 리허설 |
| **의도 의미검증 심화** (T6) | `measure_intent_fidelity` 존재하나 phase 01/04 미배선(=1.1에 포함). `cold.isolation` 은 dispatch log 부재로 NA — 구조화 dispatch log 도입은 별도 작업. paraphrase/Jaccard 희석(발견 13), 의도 문서 11+ 병존 단일 권위(발견 12)는 미해소. | 부분 직접 (의도 오독 증폭 차단) | M | M | 1.1 이후 |
| **fingerprint 원거리(암호 서명)** | 설계 §10 근시 강화는 완료(baseline). 러너 소유 키 서명은 비목표 유지. | **내부 위생** — 외부 채점자는 fingerprint 를 안 봄 | L | H | — |
| **스펙 드리프트 잔여** | manifest 가 권위 확립(baseline)이나 manifest 스스로 "conventions/grades.md 의 페이즈 활성화 표는 stale"이라 명시 — prose 측 드리프트 잔존. 1.2 다이어트에 포섭. | 내부 위생 위주 | L~M | L | 1.2 와 함께 |
| **phase_invoke_audit 은퇴** | meta_audit 이 대체 설계이나 배선 전(1.1)까지 옛 하드코딩 감사기가 현역. | 1.1 에 포섭 | — | — | 1.1 |

---

## 2. 우선순위 랭킹 — 레버리지 × 비용

### 상위군: 외부 점수에 닿는 고레버리지 · 저~중비용 (벤치마크 전 소진 대상)

| 순위 | 항목 | 레버리지 | 비용 | 한 줄 |
|---|---|---|---|---|
| 1 | **커널 파이프라인 배선** (1.1) | H | M | 이것 없이는 벤치가 '개선 전' 시스템을 측정 — 비교성의 전제이자 최대 갭 |
| 2 | **§8 동결 prose 다이어트** (1.3) | H | L~M | 외부 배점 중립 세리머니(viewer·폭 의무·80% 강제)에서 토큰 회수 |
| 3 | **임계 0.999 실측 기반 재설정** (1.4) | H | L | 도달 불가 임계의 소각 루프 제거 — 사실상 1.3 과 한 묶음 |
| 4 | **self_lint 순감 + phase 06/09 prose 다이어트** (1.2) | H | M | §11.5(a) 성공 지표 자체 — 값으로 측정 가능한 유일한 사전 지표 |
| 5 | **모델 라우팅 교정** (1.6) | H(가설) | L | implementer↑ 몇 줄 편집 — 단 달러 비용 트레이드오프는 명시적 승인 필요 |

### 중위군: 저비용이나 레버리지 중간 (하는 김에)

- coverage 도구 배선 (1.5) — L 비용, 내부 신호 완결.
- headless 인터뷰 리허설 관측 (1.6) — 리허설 run 에 무료 동반.

### 내부 위생 분류 (정직 — 벤치마크 전 필수 아님)

- fingerprint 암호 서명, 구조화 dispatch log(cold.isolation NA 해소), e2e self-fixture, grades.md 등 prose 드리프트 완전 정리, phase 02/03/05/07/10~14 의 개별 CheckSpec 화 완주(§9 잔여 — 1.1 의 phase 09 중심 배선 이후 점진), 의도 문서 단일 권위 병합.
- 이들은 시스템을 더 정직하게 만들지만 외부 채점자가 관측하는 표면에 닿는 경로가 길다. 벤치 후 결과를 보고 재우선순위화하는 것이 합리적.

---

## 3. 충분성 권고

### 판정: **아니오 — 지금 벤치마크에 가지 않는다.**

근거 3개, 전부 실측:

1. **측정 대상이 아직 '개선 전' 시스템이다.** 커널·producer·manifest 는 완성됐으나 실 run 의 어떤 지점도 이를 호출하지 않는다(§1.1 grep 0건). 지금 벤치를 돌리면 그 결과는 지난 3일 작업의 효과를 **원리적으로 반영할 수 없고**, §11.5(b) controlled 비교의 '후' 데이터도 되지 못한다. 비싼 측정을 attribution 불가능한 시점에 소비하는 것.
2. **감사가 확증한 외부-점수-직결 구조 결함이 그대로 살아 있다.** ~41만 chars 지시 질량(발견 4), 0.999 소각 루프(발견 8), 외부 배점 중립 세리머니 강제(T5/T7) — 셋 다 저~중비용으로 닫히는데 미착수. "저비용·고레버리지 개선 먼저 소진" 방침에 정면으로 미달.
3. **잔여 deficit 4종의 마감 형태가 어차피 '실 run 1회'다** (§1.5). 벤치 전에 내부 드레스 리허설이 한 번 필요하며, 그 리허설이 sufficiency bar 의 검증 게이트를 겸한다.

### Sufficiency bar — 벤치마크 전 반드시 닫을 최소 항목 (이것만)

| # | 항목 | 완료 조건 (값 기반) | 기대 효과 (가설임을 명시) |
|---|---|---|---|
| B1 | 커널 배선 (랭킹 1) | 실 run 에서 phase 09 가 `meta_audit` verdict 로 게이팅되고, phase 01/04/06/08 이 선언 아티팩트를 저작해 correctness/scope/solid 가 deficit 아닌 실측 판정을 받음 | sprint loop 이 재채점이 아닌 산출물 개선으로 종료; 벤치 결과의 전/후 비교성 성립 |
| B2 | 동결 prose 다이어트 + 임계 재설정 (랭킹 2+3) | frozen 대상 의무가 prose 에서 advisory 로 강등; 임계가 실측 분포 기반 값으로 교체; budget 80% 강제 해제 | 외부 배점 중립 토큰의 회수 — content depth 잠식 가설의 실행 |
| B3 | self_lint 순감 1차분 (랭킹 4) | 커널 인수 차원의 C-룰 삭제 후 `self_lint all_ok=True` 유지 + 페이즈 진입 chars 재실측 값 보고(§11.5a) | 지시 질량 감소 — 사전에 값으로 확인 가능한 유일한 지표 |
| B4 | **드레스 리허설 1회** — 소형 내부 과제 full-run | (i) 커널이 실 run 에서 발화, (ii) tournament/regression/dacapo/e2e deficit 이 실 artifact 로 채워지거나 정직 NA 판정, (iii) headless 인터뷰가 자가 채움 없이 통과, (iv) 진입 지시 질량 실측 | 벤치에서 처음 밟을 경로의 사전 검증 — 실패 모드를 싼 곳에서 소진 |

선택(권고하나 bar 아님): 모델 라우팅 교정(랭킹 5 — 달러 비용 승인 필요), coverage 배선.

**bar 이후에는 즉시 벤치마크가 맞다.** B1~B4 를 넘기면, 남은 고레버리지 후보(의도 의미검증 심화, §9 완주, 라우팅 최적화)는 전부 "벤치 데이터가 있어야 우선순위를 정할 수 있는" 것들이다 — 내부 측정계는 이미 정직해졌으므로(baseline), 그 이상의 내부 개선은 외부 신호 없이는 과적합 위험이 있다. 이 시점의 벤치는 최종 검증이 아니라 **다음 개선 사이클의 입력**으로 기능한다.

---

## 4. 정직 고지

1. **외부 인과는 전부 가설이다.** 본 문서의 레버리지 H/M/L 판정 중 실측으로 확립된 것은 (a) 커널이 실 run 에 배선되지 않았다는 사실, (b) 지시 질량이 HARD-CORE 밖에서 순증했다는 사실, (c) 동결 대상 의무가 prose 에 현행이라는 사실 — 즉 **개선이 실행되지 않았다는 것**뿐이다. 그 개선이 외부 점수를 실제로 올린다는 인과(지시 질량↓→depth↑→점수↑, 세리머니 해제→depth↑, implementer↑→점수↑)는 벤치마크로만 확증되며, 효과가 0이거나 음(예: 폭 동결이 breadth 가 유효했던 과제군에서 손해)일 가능성도 배제하지 못한다. 그것을 판별하는 것이 벤치마크의 존재 이유다.
2. **사전에 값으로 확인 가능한 것은 §11.5(a)뿐이다.** 지시 질량 감소는 chars 실측으로 벤치 전에 확인된다. 외부 점수(§11.5b)는 별개이며, 둘을 혼동해 "질량이 줄었으니 개선됐다"고 주장해선 안 된다.
3. **본 평가 자체의 한계.** 정적 분석이다 — "배선 0"은 grep 으로 확정했으나, "배선하면 sprint loop 행동이 바뀐다"는 실행 관측이 아니다(그래서 B4 리허설이 bar 에 있다). 또한 레버리지 순위는 단일 분석가 판정이며 감사의 n=1 한계(judge 분산 미실측)가 여기에도 적용된다.
4. **재현 근거.** 본 문서의 모든 실측치는 HEAD `e077bc7` 기준: 커널 참조 grep(§0), `wc -c phases/*.md`(219,280 bytes 총), `du -sb conventions/`(809,152), self_lint 3,472줄/74 C-룰 계열, HARD-CORE 3,888 chars(python len 실측), `budget-saturation-loop.md`/`autonomy.md` 임계 원문, `agents/{implementer,tester}.md` 모델 권고 원문, `checks/` 15 CheckSpec, `pipeline.manifest.json` frozen_widths.
