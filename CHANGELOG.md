# CHANGELOG

본 저장소의 의미 있는 변경만 기록 — 메모리 `feedback_version_conservatism.md` (1.0 임박, 의미 있는 마일스톤만 발행) 정합. **사용자 원칙 (sprint-20+): 스킬 / 컨벤션 본문은 *현재* 활성 룰만 — sprint/version history 는 본 CHANGELOG 단일 위치.**

## v0.9.58 — 2026-07-12 (sprint-56 — 회귀 진단 병렬화: 진단을 코드가 소유)

### 마일스톤

사용자 원래 논지 **"핵심은 루프와 회귀 병렬"**의 *회귀 병렬* 절반 착지(폭 강제 v0.9.56 · 병합 소유 v0.9.57 에 이어). 회귀(sprint.regression `score_delta < -0.05`)가 검출된 뒤 페이즈 11 진단이 지금까지 **단일 분석가의 서술**(주 가설 + 자가 반대 가설)이었다 — 아무도 진단이 *여러 독립 회의론자의 corroborated 병렬 판단*인지 디스크에서 재확인하지 않았다. `regression.parallel_diagnosis` 커널 게이트가 그걸 값으로 강제한다: **회귀 검출 후 corroborated 병렬 진단이 디스크에 있기 전엔 루프가 게이트를 다시 통과 못 한다.**

### 설계 (Fable): GO-WITH-DOC-ADDITION

Fable 판정 — 커널 게이트만으론 휴면(phase 11 이 기계판독 가능한 가설 아티팩트를 안 냄), 문서만으론 무치(self_lint 은 run 아티팩트를 검사 안 함). 정답은 merge-ownership 과 같은 복합: **커널 게이트 + phase-11 가설 아티팩트 계약 + 양방향 declared=invoked lint**. B1 과 다른 핵심: 회귀는 *조건부* 현상이라 `absence_policy: FAIL` + no-applicability 면 정상 run 마다 FAIL(연극적 회귀 유발). → `applicability: regression_events_total >= 1`(cold.isolation 패턴) + **항상 호출 producer**(NA 가 가정 아닌 *측정값*). 타이밍: gate_history 아카이브가 meta_audit *후*라, 회귀 검출 run 은 no_regression 실패로 phase 11 라우팅하고, *다음* gate 가 corroborated 진단을 요구한다.

### 변경 (opus 서브에이전트 구현, Fable 설계 그대로 — 오케스트레이터 검수)

| PR | scope | 산출 |
|---|---|---|
| PR-A | `checks/regression.parallel_diagnosis.json` (active G4/G5, phase 11, applicability `regression_events_total>=1`, absence FAIL, 6 assertion) | CheckSpec |
| PR-B | `scoring/producers/measure_regression_diagnosis.py` — gate_history evidence·bisect.md·hypothesis-*.json 디스크 재파싱, event↔diagnosis 바인딩(gate_history_ref+score 일치), vote argmax+corroboration 재계산 | producer |
| PR-C | `pipeline.manifest.json` `regression_diagnosis` 블록(min_hypotheses G4=3/G5=4, corroboration_min=2) + G4/G5 checks 맵 | manifest |
| PR-D | `scoring/run_gate.py` `_regression_diagnosis_producer` 독립 병렬 배선(항상 호출) + `--no-regression-diag` | 러너 |
| PR-E | `self_lint.py` **C-RPD**(run_gate 배선) + **C-RPH**(phase 11 emit 계약) declared=invoked | 2 lint |
| PR-F | `phases/11-regression-bisect.md` 병렬 회의론자 진단 절(K evidence-axis skeptic + hypothesis JSON 스키마 + review_dispatch_log append + analyst merge 역할); `agents/regression-analyst.md` skeptic/merge dual-mode | 2 doc |
| PR-G | `test_measure_regression_diagnosis.py`(14, NA·PASS·6 FAIL 모드·drift-guard) + `test_self_lint.py` C-RPD/C-RPH guard-bite | test |

### 병렬성·무결성이 디스크에서 무엇을 고정하나

K 개 well-formed 가설(hypotheses_count/malformed), distinct `agent_call_id`(duplicate==0, review.context_minimality freshness 정합), 유효 4-class 표결(checkpoint.BISECT_DEFECT_CLASSES 소유), ≥2-of-K corroboration, 선언 class==표결 argmax, routing==`checkpoint.FAILURE_TO_PHASE`(plan.tournament_winner_argmax 가 winner argmax 를 재계산하듯), skeptic 별 alternative 의무. skeptic dispatch 를 `review_dispatch_log` 로 흘려 review.context_minimality 가 같은 dispatch 의 순도까지 게이팅(생태계 보강, 커널 추가비용 0).

### 정직한 한계

병렬 가설이 디스크에 존재함 + 분류→라우팅이 기계적임을 증명하지 *정확한 진단*을 증명하지 않는다 — defect_class 는 LLM 판단(일관된 위조 가능), agent_call_id 는 dispatch 자기 신고(zero-context 궁극 증명 불가, review.context_minimality 와 같은 전제). 그 압력은 review_dispatch_log 무결성·fingerprint 체인이 좁힌다. G4/G5 만(phase 11 활성 grade) — G3 회귀는 직렬 유지. 후속: hypothesis suspect 의 diff-line 실재 검증.

### 검증

전체 scoring 스위트 **`555 passed`**(신규 producer 14 + C-RPD/C-RPH guard-bite 2 포함), self_lint **124/124 all_ok**. 버전 SKILL.md + plugin.json = 0.9.58.

## v0.9.57 — 2026-07-12 (sprint-55 — 병합/승자 소유: tournament argmax 를 코드가 소유)

### 마일스톤

B1(v0.9.56 폭 강제)의 짝 — 사용자 논지 "폭 강제 + **병합**을 코드로 소유"의 병합 절반. 멀티버스 tournament 의 승자 *선택*(argmax)과 *승격*(promotion)이 지금까지 모델 서술이었다: 모델이 sub-score 를 쓰고 winner 를 선언하고 canonical 로 복사한다 — 아무도 선언 winner 가 선언 sub-score 의 argmax 인지, 승격된 canonical 이 실제 winner 아티팩트인지 재계산하지 않았다. `plan.tournament_winner_argmax` 커널 게이트가 그 둘을 값으로 강제한다.

### 설계 (Fable): GO-WITH-SCHEMA-ADDITION

Fable feasibility 판정 — (i) winner==argmax 는 오늘 가능(`winner_id`/`winner_score` 필수 frontmatter + 본문 표 총점), (ii) canonical digest 매칭은 **legit 머지 승격 경로**(competition.md Δ<0.05/0.02) 때문에 무조건 digest 동일이 틀림 → `promotion_policy: copy|merge` + `merge_sources` 2필드 추가(미기재→copy 기본, 비휴면·하위호환). **weight-free**: 컨벤션에 6-dim 스키마가 둘 충돌(plan-tournament-scoring-strict vs intra-phase-dacapo-loop)하므로 가중치를 manifest 로 옮기지 않고 총점(표 `weighted` 열)의 argmax 만 재계산.

### 변경

| PR | scope | 산출 |
|---|---|---|
| PR-A | `checks/plan.tournament_winner_argmax.json` (active G3+, phase 06, absence FAIL, applicability 없음) — 5 assertion: winner==argmax / universes>=2·malformed==0 / 총점 [0,1] / winner_score==표 총점 / 승격 무결성(copy digest·merge base) | CheckSpec |
| PR-B | `scoring/producers/measure_tournament_argmax.py` — 최종 tournament frontmatter+본문 표+승격 아티팩트를 디스크에서 재파싱(상상값 0), universe 총점 argmax 재계산, canonical/winner sha256 대조 | producer |
| PR-C | `pipeline.manifest.json` checks 맵 G3/G4/G5 등록(+drift 균형) + `_note` | manifest |
| PR-D | `scoring/run_gate.py` `_plan_producers` 3번째 블록 — 항상 호출(tournament 부재 시 producer 자체 미방출) | 러너 |
| PR-E | `self_lint.py` **C-TWA**(run_gate 가 producer 실제 호출 declared=invoked) | lint |
| PR-F | `dacapo-frontmatter-schema.md` promotion_policy/merge_sources 선택 필드 + §5 모순 행 2개; `plan-tournament-scoring-strict.md` U1→universe-1(라벨이 winner_id 형식과 매칭되게) | 2 doc |
| PR-G | `test_measure_tournament_argmax.py`(15, winner≠argmax 차단·copy/merge 승격 증명) + `test_self_lint.py` C-TWA guard-bite | test |

### 왜 병합이 폭 다음인가

폭은 디스크 존재(디렉터리·표)로 *반증 가능*하지만 병합은 sub-score 가 모델 저작이라 *일관성 검사*만 가능하다 — 코드 argmax 도 우승자 옳음을 증명 못 하고 서술이 숫자와 맞음만 본다. 그래서 폭 강제(B1)가 먼저, 병합 소유(본 릴리스)가 다음. 두 절반이 사용자 논지를 완성한다.

### 정직한 한계

본 게이트는 "선언 winner 가 선언 sub-score 의 argmax 다 + 승격이 기계적이다"를 증명하지 *계획 품질*을 증명하지 않는다 — sub-score 는 LLM 판단이고 모델은 자기 선호 universe 가 이기는 *일관된* 위조를 만들 수 있다(본 체크가 재심사 안 함). 그 압력은 `plan.tournament_independence` shadow 변량·zero-context shadow grading·monotonicity 가 좁힌다(B1/review.context_minimality 와 같은 전제). 머지 내용 파생은 digest 로 증명 불가. 후속: winner sub-score convex hull(winner_sub_scores frontmatter) 검사.

### 검증

전체 scoring 스위트 **`539 passed`**(신규 producer 15 + C-TWA guard-bite 1 포함), self_lint **122/122 all_ok**(C-TWA 추가). 버전 SKILL.md + plugin.json = 0.9.57.

## v0.9.56 — 2026-07-12 (sprint-54 — 멀티버스 fan-out 폭 강제 primitive: 폭을 코드가 소유)

### 마일스톤

핸드오프 §3.B1 착지. 멀티버스 fan-out 폭(활성 폭 G3=3/G4=4/G5=6)이 지금까지 `conventions/intra-phase-dacapo-loop.md` 의사코드 + 모델재량이라 **모델이 폭을 skip** 할 수 있었다(cold session winner 0.853, universe 3 < G4 폭 4, 재경합 0회). `universe_count_monotonicity.py` 는 라운드 간 단조성(N+1 ≥ N)만 사후 검사할 뿐 **초기 폭 바닥을 강제하지 않는다**(라운드0 width=1 이어도 단조성 통과). 본 릴리스가 폭을 `review.context_minimality` 와 같은 계약의 **비휴면 커널 게이트**로 승격 — 폭이 모델재량이 아니라 *코드가 소유하는 조건*이 된다(사용자 논지 "다이나믹 워크플로우의 코드기반 조건 검사"의 병렬성 종착점).

### 설계 red-team (Fable)

초안은 `plan_observed_width = max(candidates 디렉터리, round0 표)` 를 게이팅했으나 Fable critique 가 **실질 결함**을 잡았다: candidates 디렉터리는 다카포 rerun 마다 fresh universe 가 누적(anti-pattern g)이라 **초기 폭이 아니다**. 초기 2 폭 + rerun 3 = 5 dir 로 floor 4 를 통과시키는 우회(under-width-then-rerun)가 열린다. → assertion 을 **round0-primary** 로 교정: `round0 >= floor OR (round0==0 AND candidates >= floor)`. round0 tournament 표(초기 폭 권위)를 우선하고, 그 표가 파싱 불가일 때만 candidates 로 폴백(비표준 라벨 레이아웃 구제). phantom-row 방어를 커널 안으로: `round0_rows_without_dirs == 0`. floor override 봉쇄: `cmd_pattern` 이 `--manifest` 거부.

### 변경

| PR | scope | 산출 |
|---|---|---|
| PR-A | `checks/multiverse.fan_out_width.json` (active G3+, phase 06, absence FAIL, applicability 없음) — round0-primary 폭 assertion + phantom 교차 assertion + `--manifest` 봉쇄 cmd_pattern | CheckSpec |
| PR-B | `scoring/producers/measure_multiverse_width.py` — plan/candidates·round0 tournament 표를 디스크에서 ID 집합으로 재계산(game-proof), `width_floor` = manifest `multiverse_widths[grade]` 단일 소스 | producer |
| PR-C | `pipeline.manifest.json` checks 맵 G3/G4/G5 등록(+ drift 균형) + `_note` | manifest |
| PR-D | `scoring/run_gate.py` — `_multiverse_producer` 독립 병렬 그룹 배선(항상 호출) + `--no-multiverse` | 러너 |
| PR-E | `self_lint.py` **C-MFW** — run_gate 가 producer 를 실제 호출(declared=invoked) 강제 | lint |
| PR-F | doc-sync — `intra-phase-dacapo-loop.md`/`impl-multiverse-strict.md`/`contested-decision-multiverse.md` 의 frozen 폭(5/7/9) preach 를 활성 폭(3/4/6 manifest 단일 소스) + frozen advisory 로 정합 | 3 doc |
| PR-G | `test_measure_multiverse_width.py`(11) — under-width-then-rerun 우회 차단 명시 증명 포함 + `test_self_lint.py` C-MFW guard-bite | test |

### 왜 폭 강제가 첫 증분인가 (merge-ownership 아님)

사용자 논지의 종착점은 "폭 강제 + 병합을 코드로 소유"다. 폭은 디스크 존재(디렉터리·표)로 *반증 가능*하지만, 병합(tournament argmax)은 6-dim sub-score 가 모델 저작이라 *일관성 검사*만 가능하다 — 코드 소유 argmax 도 우승자가 옳음을 증명 못 하고 서술이 숫자와 맞음만 본다. 문서화된 회귀(0.853 winner, 3<4 폭, 재경합 0)는 전부 폭/루프 skip 이지 argmax 불일치가 아니다. 병합 소유는 후속 증분(`plan.tournament_winner_argmax`: frontmatter sub-score 재계산 + winner==argmax + canonical digest 매칭)으로 큐잉.

### 정직한 한계

round0 표를 파싱 불가로 쓰고 폭을 줄인 뒤 rerun 누적하는 잔여 우회는 본 체크 단독이 아니라 생태계(`universe_count_monotonicity` 단조성/mismatch — 단 *비-커널* 오케스트레이터 CLI + `plan.tournament_independence` shadow 변량)가 좁힌다. 위조의 궁극 증명은 불가(review.context_minimality 와 같은 전제). impl(phase 08)은 impl-multiverse-strict single-universe+7조건(프로즈) 예외가 있어 폭 게이팅 대상 아님 — `impl_candidates_width` 는 관측용 measured 만.

### 검증

전체 scoring 스위트 **`523 passed`**(신규 producer 11 + guard-bite 포함), self_lint **121/121 all_ok**(C-MFW 추가). 버전 SKILL.md + plugin.json = 0.9.56.

## v0.9.55 — 2026-07-12 (sprint-53b — 무장한 게이트를 페이즈 흐름에 배선, declared=invoked)

### 마일스톤

v0.9.54는 코드기반 조건(`review.context_minimality`, `should_stop.py`)을 **무장(armed)**하고 러너(run_gate)까지 배선했으나, **페이즈 오케스트레이션 문서가 아직 이 게이트를 먹이지 않았다** — 실 G3+ run에서 review 로그 부재 → deficit-FAIL, should_stop은 페이즈 흐름이 안 부름. 본 릴리스가 그 급식(feeding)을 배선한다(핸드오프 `docs/design/2026-07-12-pure-review-followups-handoff.md` §3.A).

### 변경

| PR | scope | 산출 |
|---|---|---|
| PR-A (A1) | `phases/03-independent-comprehension.md` — 콜드 재이해 fresh agent가 `state/review_dispatch_log.json`에 `{agent_call_id, prior_context_token_count:0, loaded_artifacts}` append 의무(스키마 명시) | phase 배선 |
| PR-B (A1) | `conventions/intra-phase-dacapo-loop.md` Step C — 06/08 shadow grader도 같은 로그에 append(`append_review_dispatch_log`) | 배선 |
| PR-C (A2) | `phases/10-test-loop.md` §자동 CLI 호출 — `should_stop.py`를 정지 판정 **단일 권위**로 literal Bash 배선(exit 0=stop/1=continue), sprint_loop_cap은 보조·보고 모드로 격하 명시 | phase 배선 |
| PR-D | `self_lint.py` **C-RDL**(phase 03 + dacapo-loop에 `review_dispatch_log` emit) / **C-SSW**(phase 10에 `should_stop.py` 호출) 신규 — declared=invoked 강제(무장 게이트 미급식 차단) | 2 lint |
| PR-E | `test_self_lint.py` — 배선 누락 시 C-RDL/C-SSW 가드가 실제로 FAIL 함을 가짜 skill_root로 증명 | guard-bite test |

### 왜 필요한가 (armed → fed)

무장(armed)과 급식(fed)은 다르다: v0.9.54는 게이트/producer/should_stop을 만들고 run_gate가 관례경로에서 로그를 소비하도록 했으나, **그 로그를 누가 쓰는가**가 페이즈 문서에 없었다. C-RDL/C-SSW가 "phase 03/06/08은 review 로그를 emit한다 / phase 10은 should_stop을 부른다"를 self_lint로 강제해, sprint-43 declared=invoked 패턴을 이번 게이트에도 적용한다.

### 검증

전체 scoring 스위트 **`510 passed`**(신규 guard-bite test 포함), self_lint **120/120 all_ok**(C-RDL/C-SSW 추가). 버전 SKILL.md + plugin.json = 0.9.55.

## v0.9.54 — 2026-07-12 (sprint-53 — 코드기반 조건: Pure-Review 게이트 + 루프 정지 + 회귀 라우팅 + run_gate 병렬화)

### 마일스톤

하네스 리뷰(사용자 지목: *"핵심은 루프와 회귀 병렬 — 더 핵심은 퓨어리뷰 컨텍스트를 필요한 것만 주입해 리뷰"*) 결과, pure-review 순도가 **코드기반 조건이 아니라 프로즈/휴면**임을 진단. 페이즈 09 게이트는 CheckSpec 커널로 판정하지만:

- `cold.isolation` 은 순도 assertion(`prior_context_token_count==0`)을 갖고도 `applicability: dispatch_log_present==1` 뒤에서 **영원히 NA(휴면)** — 이 저장소 콜드 세션이 dispatch 로그를 안 만들기 때문.
- shadow-grader(06/08) 순도는 게이트 assertion 이 아니라 `plan.tournament_independence` 의 분산 프록시(`grader_score_variance>0`)로만 대리.

→ **"필요한 것만 주입"이 커널이 검사하는 값이 아니었다.** 본 릴리스가 이를 비휴면 코드 게이트로 승격(P0).

### 변경

| PR | scope | 산출 |
|---|---|---|
| PR-A | `producers/measure_context_minimality.py` 신규 — 리뷰 디스패치 로그 스캔, `loaded_tokens_max` 는 로그 자기신고가 아니라 디스크에서 `\w+` **재계산**(game 불가) | 1 producer |
| PR-B | `checks/review.context_minimality.json` 신규 — 순도(`prior_context_max==0`) + 무결성(`loaded_artifacts_missing==0`, `malformed_calls==0`) + freshness(`duplicate_call_ids==0`) + no-work(`calls_total>=1`). **applicability 없음** → 로그 부재는 NA 아닌 `absence_policy=FAIL`(비휴면) | 1 CheckSpec |
| PR-C | `pipeline.manifest.json` G3/G4/G5 등록 (drift-check 정합: 파일+맵 동시) | manifest |
| PR-D | `run_gate.py` `_review_producer` 배선 — `_cold_producer` 패턴, 관례 경로 `state/review_dispatch_log.json`, `--no-review` | 러너 배선 |
| PR-E | `producers/tests/test_measure_context_minimality.py` — PASS + 5 FAIL 모드 + **비휴면 증명**(부재→FAIL, cold.isolation NA 대비) + **디스크 재계산 증명** + CLI/digest | 12 tests |
| PR-F (P1) | `scoring/should_stop.py` 신규 — 루프 정지 `gate ∧ no_regression ∧ (plateau ∨ budget≥cap)`를 manifest `stop_policy` 읽는 **단일 코드 진입점**으로(plateau 는 `stagnation.detect` 재사용). 페이즈 09 게이트(meta_audit)와 같은 커널 권위로 루프 제어. exit 0=stop/1=continue. 기존엔 합성 AND 를 오케스트레이터(LLM)가 조립·`sprint_loop_cap`은 옛 4-layer 보고모드 | 1 모듈 + 7 tests |
| PR-G (G1) | `scoring/run_gate.py` — 독립 producer 그룹(quality/gates/plan/cold/review)을 `ThreadPoolExecutor` **병렬**. 순서의존(2→3→5)은 submission 을 barrier 뒤에 둬 보존, `enable_parallel`/`--no-parallel` escape. 매 sprint hot path 벽시계 절감 | 병렬화 + 병렬≡직렬 바이트 등가 test |
| PR-H (P2) | `scoring/checkpoint.py` — `FAILURE_TO_PHASE` 를 회귀 라우팅 **단일 소스** 로 통합(런타임 신호 계열 + bisect 4분류 병합, 충돌 0). `phases/11-regression-bisect.md` 참조 노트(C-RB1 키워드 유지) + 문서↔코드 drift 가드 | 단일화 + 3 tests |

### 왜 cold.isolation 과 다른가 (비휴면)

| | cold.isolation (기존) | review.context_minimality (신규) |
|---|---|---|
| 순도 assertion | `prior_context_token_count==0` | `prior_context_max==0` |
| applicability | `dispatch_log_present==1` → 로그 부재 시 **NA(휴면)** | 없음 → 로그 부재 시 **FAIL(강제)** |
| 최소성 | — | `loaded_tokens_max`(디스크 재계산 value) |
| 결과 | 이 저장소에서 항상 NA | 페이즈 09 게이트까지 pure-review 로깅 의무화 |

`skipped==FAIL`(§2 원칙2) 그대로 — "리뷰 컨텍스트를 안 남기면 통과가 아니라 실패".

### 검증

전체 scoring 스위트 **`509 passed`**(P0 12 + P1 7 + G1 1 + P2 3 신규 tests), self_lint **118/118 all_ok**. 리뷰 로드맵 P0/P1/G1/P2 모두 착지 — "루프 정지·리뷰 순도·회귀 분기"라는 제어 흐름 결정 셋을 페이즈 09 게이트와 같은 코드기반 조건으로 통일. 남은 후속: 외부 벤치마크(Spec 2, SWE-bench) — 별도 세션.

## v0.9.52 — 2026-05-10 (sprint-52 — Viewer Finalization Closure)

### 마일스톤

g4-sprint51 cold session 99/100 zero-context Opus 직후 사용자 viewer 진단 — *"하네스가 스스로 결과를 올바르게 채울수 있도록 submission 단계에서 누락된점을 보강"* + *"99점 맞은것과 별개로 본 하네스의 기능인 뷰어들의 구성이 아직 미완성"* + *"0607 페이즈의 간트 시간이 11:00 으로 잘못기록"*.

본 sprint = sprint-36 (pre_bootup emit-skeleton) ↔ phase 14 (refresh) 양 끝점 닫음:

1. **Viewer Finalization Closure** — `lineage_finalize.py` 신규 CLI 가 phase 14-handoff 진입 후 lineage / dashboard / webview JSON 의 placeholder (PENDING fingerprint, "cold session 미시작" mermaid stub, fingerprint_chain=[], project_run="pending") 를 실 데이터로 일괄 refresh.
2. **declared = invoked finalize 차원** — sprint-43 패턴이 finalize 단계 미커버 갭 직접 닫음. phase 14 본문에 literal Bash invoke 박힘.
3. **universe candidate frontmatter `created_at` 의무** — `plan/candidates/universe-N/{06-plan.md, 07-cold-read.md}` 정시 stub (`T..:00:00Z`) 차단. g4-sprint51 회차의 0607 페이즈 11:00 잘못 기록 직접 catch.
4. **viewer JSON sentinel 검증** — `placeholder_grep.py --include-viewer-json` 옵션. cold session 마감 후 placeholder 잔존 = orchestrator fail.

### 변경 — 7 PR

| PR | scope | 산출 |
|---|---|---|
| PR-A | sprint-52 plan (`sprints/sprint-52-v0.9.52-viewer-finalization-closure/plan.md`) | plan |
| PR-B | `lineage_finalize.py` 신규 CLI + tests (8/8 pass) | 1 CLI + 8 tests |
| PR-C | `phases/14-handoff.md` §sprint-52 literal Bash invoke (lineage_finalize / fingerprint chain / placeholder_grep --include-viewer-json) | phase wiring |
| PR-D | `phases/06-plan.md` §universe candidate frontmatter created_at 의무 + self_lint C-UNIV-CREATED-AT / C-LFW | phase rule + 2 lint |
| PR-E | `placeholder_grep.py` --include-viewer-json 옵션 + 3 검증 함수 + tests (6/6 pass) | CLI 확장 + 6 tests |
| PR-F | HARD-RULE 9.nnn (lineage_finalize 의무) / 9.ooo (universe candidate created_at 의무) / 9.ppp (viewer JSON placeholder 차단) | HARD-CORE 신설 |
| PR-G | sprint 마감 v0.9.52 + skill_version 동기화 (theseus-harness 0.9.52 / theseus-orchestrator 0.9.39 → 0.9.52) + CHANGELOG | release |

### Layer 4 enforcement 의 finalize 차원

sprint-43 의 declared=invoked 패턴이 phase 06/08/09/10/14 §자동 CLI 호출 까지 박혔지만, *viewer JSON refresh* 책임이 명시적으로 어디에도 박혀있지 않았음. 본 sprint 가 phase 14-handoff 에 그 책임을 명시:

```
pre_bootup.py bootstrap (phase 00 enter 직전)
    └─ 빈 골격 emit (mermaid="cold session 미시작" / fingerprint_chain=[] / project_run="pending")
                     ↕  본 sprint 가 닫는 양 끝점
phase 14-handoff (cold session 종료)
    └─ lineage_finalize.py refresh --strict (실 데이터로 일괄 refresh)
    └─ placeholder_grep.py --include-viewer-json (잔존 catch)
```

### 비-목표 (sprint 가치 보존)

- 점수 추적 X — viewer 기능 무결성만 (`feedback_score_targeting_taboo.md` 정합)
- 도메인 의존 fix X — 모든 룰 markdown frontmatter parse + JSON key path (`feedback_harness_strengthening_methodology.md` 정합)
- 신규 컨벤션 0 — 기존 본체 강화만, HARD-RULE 3 + self_lint 2 (`feedback_convention_diet_paradigm.md` 정합)

### 메모리 cross-link

- `feedback_dual_pressure_json_schema.md` — 본 sprint = 그 닫힘 단계
- `feedback_hurdle_as_cli_paradigm.md` — `lineage_finalize.py` 가 컨벤션 본문 페어
- `project_sprint43_v0948.md` — declared=invoked 패턴, 본 sprint 가 finalize 차원 적용
- `feedback_intent_recursion_paradigm.md` — sprint-51 intent 회귀, 본 sprint = 산출 → viewer 회귀 (대칭)

## v0.9.51 — 2026-05-10 (sprint-51 — Extension Invoke Closure + Prompt-Driven Harness)

### 마일스톤

g4-v4 cold session 96/100 직후 사용자 직접 진단 — *"sprint-50 의 9 HARD-RULE 산출물 대부분 invoke 안 됨"* + *"benchmarks/001 prompt 를 직접 이해해서 도메인 무관 확장 사고 가능하게 해야 함"* + *"이 자체가 우리 intent 가 회귀하며 숨은 의도를 모두 채우는 방식의 이유야"*.

본 sprint = sprint-50 의 *완성*:
1. **Intent Recursion 패러다임** 도입 — *prompt 자체가 후속 페이즈의 seed*. 본 하네스의 기존 페이즈 01 refresh-1/2 cycle 이 이미 *intent 회귀* 메커니즘이고, 본 sprint 는 그 회귀의 *seed* 자동화.
2. **Layer 4 enforcement** 도입 — sprint-40 의 5 layer 정합 (1 컨벤션 / 2 self_lint / 3 runtime CLI / **4 prompt-meta seed + recursion sink**).
3. **sprint-43 declared ≠ invoked** 갭 closure — sprint-50 신규 페이즈 (Phase 1.5) + 9 CLI 가 orchestrator phase walkthrough 에 자동 invoke 되지 않던 갭 직접 닫음.

### 변경 — 7 PR

| PR | scope | 산출 |
|---|---|---|
| PR-A | `prompt_meta_extractor.py` (480 LOC, 도메인 무관) + plan 재정렬 (Intent Recursion) | 1 CLI + plan |
| PR-B | 도메인 의존성 audit + 2 fix (CONSTRAINT_RE / NATURAL_CATEGORIES) | 2 CLI fix |
| PR-C | orchestrator phase walkthrough invoke literal Bash (sprint-50 9 CLI + Phase 1.5 + sprint-51 prompt-meta) | SKILL.md catalog |
| PR-D | `placeholder_grep.py` (sentinel + prompt-meta schema null) | 1 CLI |
| PR-E | `default_value_justification.py` (sentence-level, prompt-meta default_warnings trigger) | 1 CLI |
| PR-F | `refactor_not_rewrite_ratio.py` sprint_type frontmatter 인식 + sprint-50/51 plan frontmatter | CLI patch + 2 plan patch |
| PR-G | v0.9.51 마감 + CHANGELOG + memory + g4-v4 review doc cross-link | 본 entry |

### 신규 CLI (3 종)

| CLI | 룰 | 격언 / 출처 |
|---|---|---|
| `prompt_meta_extractor.py` | 9.kkk | (자체) 도메인 무관 markdown structural parser. 8 메타-카탈로그 자동 추출 |
| `placeholder_grep.py` | 9.lll | (자체) sentinel + prompt-meta schema null. surrender_phrase_grep sister CLI |
| `default_value_justification.py` | 9.mmm | Pragmatic Tip 53 — *"Don't gather requirements—dig for them"*. sentence-level justification 검사 |

### 신규 HARD-RULE (3)

- **9.kkk** Phase 04 entry `prompt_meta_extractor.py` 의무 호출 — 8 카탈로그 자동 추출
- **9.lll** All-phase `placeholder_grep.py` — sentinel grep + prompt-meta output_schemas null field
- **9.mmm** Phase 1.5 `default_value_justification.py` — prompt-meta default_warnings trigger 시 의식적 default 의 justification 의무

### orchestrator phase walkthrough invoke 박힘 (sprint-43 패러다임 재적용)

기존 sprint-43 이 *기존* phase 06/08/09/10/14 에 박았던 literal Bash 패턴을 sprint-50 신규 9 CLI + Phase 1.5 entry 에 *재적용*:
- phase 04 entry: `prompt_meta_extractor.py`
- phase 04 → 1.5 → 05: Phase 1.5 신규 의무 단계 (`intent_extension_emit.py` + `hidden_intent_originality.py`)
- phase 06: `universe_philosophy_distinct.py`
- phase 08: `deep_module_metric.py` + `dry_violation_count.py`
- phase 09: `define_errors_check.py` + `comment_intent_check.py` + `extension_to_artifact_trace.py`
- phase 10: `refactor_not_rewrite_ratio.py` (sprint_type-aware)
- phase 14: `knowledge_portfolio_check.py`

`phase_invoke_audit.py` (sprint-43 9.zz) 가 본 sprint 후 sprint-50 9 CLI 모두 trace 검증 가능.

### reviewer 약점 3 건 도메인 무관 catch — sandbox 직접 검증

| 약점 | 매핑 룰 | sandbox 결과 |
|---|---|---|
| token_usage 누락 (`"token_count_method": "unknown"`) | `placeholder_grep.py` (9.lll) | g4-v4 token_usage.json:5 직접 catch ✅ |
| intervention.category placeholder (`"unrecorded"`) | `placeholder_grep.py` (9.lll) | g4-v4 submission.yaml:16 직접 catch ✅ |
| warmup=0 정당화 부재 | `default_value_justification.py` (9.mmm) | g4-v4 baseline.yaml:warmup_minutes 직접 catch ✅ |

도메인 의존 patch 0 — `feedback_harness_strengthening_methodology.md` 정합.

### 도메인 의존성 audit (PR-B)

본 sprint 신규 룰 본문 audit 결과 2 건 도메인 의존 발견 → 즉시 fix:
1. `prompt_meta_extractor.py` `CONSTRAINT_RE`: `truck/loaders?/nodes?/edges?/kph/mph/meters?` 제거 → 일반 unit (hours/min/replications/% 등) only
2. `hidden_intent_originality.py` `NATURAL_CATEGORIES`: `data/topology/scenario` 제거 → `inputs/outputs/behaviors/metrics/constraints` (메타-카테고리) + `--prompt-meta-file` augment

검증: 본 prompt 직접 호출 후 도메인 noun 0 매치 확인.

### 5 Layer Enforcement 도입

| Layer | 도입 sprint | 본문 |
|---|---|---|
| 1 | sprint-30 | 컨벤션 본문 |
| 2 | sprint-37~39 | self_lint enforcement |
| 3 | sprint-40~43 | runtime CLI invoke (declared = invoked) |
| **4** | **sprint-51** | **prompt-meta seed + recursion sink** |
| 5 (구상) | future | embedding-based semantic check (premortem 인계) |

### 후속 — sprint-52 의제 후보

1. **g4-v5 cold session 결과 attribution** — sprint-51 의 9 CLI 가 *진짜로* invoke 됐는지 (`phase_invoke_audit.py` trace ≥9) + 96 → 97+ 도전
2. **Layer 5** — embedding-based semantic check (knowledge_portfolio / comment_intent / hidden_intent_originality 의 semantic 휴리스틱 고도화)
3. **HARD-CORE 다이어트** — 9.bbb~9.mmm 12 줄 INDEX router 로 옮김 (4000 chars limit 위반 누적)
4. **기존 phase 본문 mine 예시** 일반화 (sprint-37 이전 phase 본문의 loader_utilisation / truck.py / ramp_closed_after_30min 등 — 본 sprint audit 외)
5. **다른 언어 catalog** (deep_module / DRY / define_errors / comment_intent — Python → Go / TS / Rust / Java)

## v0.9.50 — 2026-05-10 (sprint-50 — Extension Discipline)

### 마일스톤

g4-v3 cold session (`D:\github\simulation-bench\submissions\2026-05-10__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4-v3`) 직후 사용자 직접 진단:

> *"의도를 이해하고 프롬프트에 적혀있는 이상의 처리를 해야 한다. 성찰-상상력을 덧대서 추가하면 좋은 작업이나 더 설계를 확장하거나 프롬프트보다 더 확장된 제안을 intent 이후 단계에 추가하는 건 어떨까. plan/impl 에서도 확장된 사고를 지시해야 한다. 실용주의 프로그래밍, 이펙티브 소프트웨어 설계의 인사이트들을 실제 반영해야 한다."*

본 sprint = *프롬프트 충실 이행* 의 부재가 아니라 *프롬프트 너머의 사고* 부재 = 91 plateau 의 구조적 원인 — 진단 후 의도→설계→구현→유지보수→테스트 *전 페이즈* 에서 "확장 사고 (Extension Thinking)" 를 페이즈 본문 + CLI enforcement 로 박는 작업.

`feedback_score_targeting_taboo.md` 정합 — 점수는 결과지 목표 아님. 본 sprint 의 가치 = *구조* (확장 사고 단계의 부재 진단을 enforcement 로 닫음).

### 확장 바이블 4 권 mapping

| # | 책 | 페이즈 매핑 |
|---|---|---|
| 1 | The Pragmatic Programmer (Hunt & Thomas) | Phase 1.5 (Tip 53), Phase 08 (Tip 11), Phase 10 (Ch.6), Phase 14 (Ch.1) |
| 2 | A Philosophy of Software Design (Ousterhout) | Phase 06 (Ch.11), Phase 08 (Ch.4–5), Phase 09 (Ch.10, Ch.13) |
| 3 | Effective Java/C++ (Bloch / Meyers) | Phase 09 (Item 87 root exception) |
| 4 | 요구사항→설계→구현→유지보수→테스트 5 단계 표준 | Phase 1.5 / 06 / 08 / 10 / 14 매핑 |

### 변경 — 7 PR

| PR | scope | 산출 |
|---|---|---|
| PR-A | sprint-50 plan + premortem (격언 동·서, 3 시나리오, 5 derived improvements) | 2 docs |
| PR-B | Phase 1.5 신설 + 3 산출물 + 3 CLI (HARD-RULE 9.bbb / 9.jjj) | 1 phase + 3 CLI |
| PR-C | Phase 06 Design-Twice + universe_philosophy_distinct CLI (9.ccc) | 1 patch + 1 CLI |
| PR-D | Phase 08 Deep-Module + DRY 2 CLI (9.ddd / 9.eee) | 1 patch + 2 CLI |
| PR-E | Phase 09 Define-Errors-Out + Comments-Why 2 CLI (9.fff / 9.ggg) | 1 patch + 2 CLI |
| PR-F | Phase 10/14 patch + 2 CLI + HARD-CORE 9.bbb~9.jjj inline (9.hhh / 9.iii) | 2 patch + 2 CLI + HARD-CORE patch |
| PR-G | v0.9.50 마감 + CHANGELOG + memory + g4-v3 review doc + sprint report | 본 entry |

### 신규 페이즈 (1)

`phases/01-5-hidden-intent.md` — 페이즈 04 (Q&A) 직후 / 페이즈 05 (Critique) 직전 의무 단계. *프롬프트가 묻지 않은* 항목 ≥5 발굴 + (must/should/could) 분류 + 후속 페이즈 trace 약속.

페이즈 수: 15 → 16 (1.5 sub-phase 신설).

### 신규 CLI (10 종)

| CLI | 룰 | 격언 출처 |
|---|---|---|
| `intent_extension_emit.py` | 9.bbb | Pragmatic Tip 53 — "Don't gather requirements—dig for them" |
| `extension_to_artifact_trace.py` | 9.jjj | (자체) 채택 extension trace 의무 |
| `hidden_intent_originality.py` | 9.bbb 보강 | (자체) 2 단 휴리스틱 paraphrase 차단 |
| `universe_philosophy_distinct.py` | 9.ccc | Ousterhout Ch.11 — "Design It Twice" |
| `deep_module_metric.py` | 9.ddd | Ousterhout Ch.4 — "Modules Should Be Deep" |
| `dry_violation_count.py` | 9.eee | Pragmatic Tip 11 — "DRY" |
| `define_errors_check.py` | 9.fff | Ousterhout Ch.10 + Effective Python Item 87 |
| `comment_intent_check.py` | 9.ggg | Ousterhout Ch.13 — "Comments WHY not WHAT" |
| `refactor_not_rewrite_ratio.py` | 9.hhh | Pragmatic Ch.6 — "Refactoring" |
| `knowledge_portfolio_check.py` | 9.iii | Pragmatic Ch.1 — "Your Knowledge Portfolio" |

### vacuous PASS 차단 (premortem §3 기반)

- Phase 1.5 항목 ≥5 만 보지 않고 *카테고리 distinct ≥3* + *should 채택 ≥1* + *body ≥80 chars* 의무 (premortem §3-1)
- universe philosophy *이름만 다른 우주* 차단 → architectural decision unique 비율 검사 (premortem §3-2)
- deep-module *단일 파일 우회* 차단 → 모듈 수 = 1 = automatic fail (premortem §3-3)
- comment paraphrase *escape 만 사용* 차단 → escape 비율 ≥80% = 의심 fail (premortem §3-4)
- refactor *변화 0* 차단 → additions=deletions=0 = automatic fail (premortem §3-5)

### HARD-CORE.md 신규 inline

9.bbb~9.jjj 한 줄 inline + 페이즈 본문 cross-ref. 컨벤션 다이어트 패러다임 정합 — *신규 컨벤션 파일 0*. C-HC1 4000 chars limit 은 sprint-35 부터 누적 위반 (현 6887 chars) — 본 sprint 추가 +794. 다음 sprint 다이어트 의제.

### 의도적 미적용

`feedback_score_targeting_taboo.md` 정합 — *점수 % 표기 0*. 본 sprint 의 검증은 본 sprint 자체 X / *다음 cold session (g4-v4)* 결과로 판정. dogfood 한계 (`feedback_self_eating_dogfood.md`) 정합.

### 후속

- **sprint-51** (다음) = v0.9.51 — g4-v4 cold session 결과 검증 후 의제 결정. 후보:
  1. HARD-CORE.md 다이어트 (9.bbb~9.jjj 9 줄 INDEX router 로 옮김)
  2. deep-module / DRY CLI 의 다른 언어 (Go / TS / Rust / Java) 카탈로그 추가
  3. comment-intent 휴리스틱 embedding-based 고도화 (premortem §4-1 인계)
  4. universe philosophy 카탈로그 확장 (constraint-programming / streaming / staged-pipeline 등 — premortem §4-2 인계)

## v0.9.49 — 2026-05-10 (sprint-49 — Sprint↔version 명칭 정책 첫 적용)

### 마일스톤

sprint-43 v0.9.48 마감 직후 사용자 지시 — *"스프린트 명칭을 version 와 일치하게 해줘 / 43 이후 다음 스프린트는 49 로만 해도 돼"*. 본 sprint = 정책 도입 + 첫 적용.

**정책 정합 — sprint 번호 = `skill_version` patch 자릿수 일치:**
- sprint-49 = v0.9.49 (본 sprint, 첫 적용)
- 이후 모든 sprint = sprint-N → v0.9.N → version bump 의무 (1:1 페어)

### 변경

| 파일 | 변경 |
|---|---|
| skills/theseus-harness/conventions/contracts.md | §Sprint ↔ version 명칭 정책 신규 절 (semver 정책 다음) |
| CHANGELOG.md | 정책 도입 entry + 역사적 매핑 표 (sprint-37 ~ 43 = v0.9.42 ~ 48) + v0.9.49 entry (본 절) |
| skills/theseus-harness/SKILL.md | version 0.9.49 + description 갱신 |
| .claude-plugin/plugin.json | version 0.9.49 + description 갱신 |
| memory/feedback_sprint_version_naming_policy.md | 신규 — forward only 원칙 본문 |
| memory/MEMORY.md | 인덱스 갱신 |

### Retroactive 적용 X

sprint-37 ~ sprint-43 (= v0.9.42 ~ v0.9.48) 은 *역사적 misalignment* 로 보존:
- 137 reference (sprint-37: 52, sprint-38: 12, sprint-39: 16, sprint-40: 35, sprint-41: 38, sprint-42: 25, sprint-43: 23) + 4 sprint dir + 4 memory + 4 git tag rename 비용
- 변경 비용 > 이득 — forward 정책만 활성

### 후속

- **sprint-50** (다음) = v0.9.50 — 외부 검증 후 진입 의제 결정 (사용자 fresh G4 cold session 결과 종속)
- 4 layer enforcement (sprint-40~43 누적) 보존 — 12 CLI + literal Bash command + 4 HARD-RULE batch (9.qq~9.aaa)

## 정책 도입 (2026-05-10) — Sprint ↔ version 명칭 일치 (forward only)

sprint-43 v0.9.48 마감 직후, 사용자 지시 — *"스프린트 명칭을 version 와 일치하게 해줘 / 43 이후 이제 다음 스프린트는 49로 만 해도 돼"*.

**Forward 정책 (sprint-49 부터 적용):**
- sprint-N = v0.{MAJOR}.{MINOR}.{N} (현재 0.9.{N})
- 다음 sprint = **sprint-49** (= v0.9.49)
- 본 정책 본문 = `skills/theseus-harness/conventions/contracts.md` §Sprint ↔ version 명칭 정책

**Retroactive 적용 X** — sprint-37 ~ sprint-43 (= v0.9.42 ~ v0.9.48) 은 *역사적 misalignment* 로 보존. 변경 비용 (137 reference + memory + dir rename + 4 git tag) > 이득.

**Sprint ↔ version 매핑 (역사적):**
| sprint | version |
|---|---|
| sprint-37 | v0.9.42 |
| sprint-38 | v0.9.43 |
| sprint-39 | v0.9.44 |
| sprint-40 | v0.9.45 |
| sprint-41 | v0.9.46 |
| sprint-42 | v0.9.47 |
| sprint-43 | v0.9.48 |
| **sprint-49** (다음) | **v0.9.49** |

## v0.9.48 — 2026-05-10 (sprint-43 — Orchestrator Runtime Invoke 트랙 7)

### 마일스톤

g4-v2 91/100 회차 샌드박스 검증 결과 *공식 점수 정합 + submission 폴더 빈 상태 (10 .pyc 만)* + sprint-41/42 9 CLI 모두 *runtime 미호출* 진단. *declared ≠ invoked* 갭의 textbook evidence — 컨벤션 본문 + CLI 코드 만으로는 enforcement 보장 불가.

본 sprint = orchestrator phase 본문에 *literal Bash command* 박기 + 3 신규 CLI (post-eval 잔존 / invoke trace / dashboard parity) → *declared = invoked* 강제.

### 변경 — 트랙 7 6 PR (PR-A ~ PR-F)

| PR | scope | 산출 |
|---|---|---|
| PR-A | sprint-43 plan + g4-v2 91 샌드박스 검증 docs | 1 plan + 1 review |
| PR-B | **submission_completeness.py** + HARD-RULE 9.yy | scoring + test (6/6 PASS) |
| PR-C | **phase_invoke_audit.py** + HARD-RULE 9.zz | scoring + test (8/8 PASS) |
| PR-D | **dashboard_submission_parity.py** + HARD-RULE 9.aaa | scoring + test (8/8 PASS) |
| PR-E | **phases/06/08/09/10/14 §자동 CLI 호출** literal Bash command 박힘 | phases/* 본문 + orchestrator SKILL.md walkthrough |
| PR-F | sprint 마감 v0.9.48 + CHANGELOG (본 entry) | SKILL.md / orchestrator / plugin.json / CHANGELOG |

### CLI 3 종 신규 (skills/theseus-harness/scoring/)

| CLI | 역할 |
|---|---|
| `submission_completeness.py` | evaluation_report.json output_exists_* checks → 현재 disk 잔존 검증. .pyc-only 패턴 차단. G3+ governance trail 의무. |
| `phase_invoke_audit.py` | orchestrator SKILL.md 본문에서 literal Bash command 정규식 추출 → 각 CLI 별 호출 trace (gate_*.json) 검증. *declared ≠ invoked* 갭 직접 추적. |
| `dashboard_submission_parity.py` | dashboard md `files:` 항목 ↔ submission disk 실 파일 list. missing_on_disk → fail / untracked_on_dashboard → warning. |

### HARD-RULE 9 신규 (3)

- **9.yy** — phase 14 handoff *직후* + dashboard sync *전* submission_completeness 자동 호출 (.pyc-only 차단)
- **9.zz** — phase 09 + 14 진입 시 phase_invoke_audit 자동 호출 (sprint-43 핵심 enforcement)
- **9.aaa** — dashboard sync *직후* dashboard_submission_parity 자동 호출

### orchestrator phases §자동 CLI 호출 literal command 박힘 (PR-E)

| phase | literal Bash command |
|---|---|
| 06 (plan exit) | dacapo_threshold + universe_count_monotonicity + cross_phase_context_audit |
| 08 (impl exit) | dacapo_threshold + universe_count_monotonicity + cross_phase_context_audit |
| 09 (entry+exit) | cold_session_artefacts + runtime_guard_chain (entry) + phase_invoke_audit + cross_phase_context_audit (exit) |
| 10 (sprint loop) | sprint_loop_cap + stagnation_breakthrough + surrender_phrase_grep |
| 14 (handoff) | surrender_phrase_grep + cross_phase_context_audit + phase_invoke_audit + submission_completeness + dashboard_submission_parity |

### 테스트 — 22/22 PASS (3 신규 suite)

- test_submission_completeness (6) + test_phase_invoke_audit (8) + test_dashboard_submission_parity (8) = **22**

각 CLI 의 *g4-v2 91 회피 패턴* 직접 회귀 테스트:
- submission_completeness: 10 .pyc + eval pass → 3 violation (pyc_only/low_survival/governance) ✓
- phase_invoke_audit: 5 declared, 0 trace → fail ✓
- dashboard_parity: 5 declared, disk 빈 → 5 missing fail ✓

### 실 g4-v2 회차 직접 검증

| CLI | 결과 |
|---|---|
| submission_completeness | verdict=fail, pyc_only=True, survival=0%, 3 violation ✓ |
| dashboard_submission_parity | 11 declared, 0 disk → 11 missing ✓ |

### 4 layer 통합 패러다임 (sprint-40 + 41 + 42 + 43)

| sprint | layer | enforcement |
|---|---|---|
| sprint-40 | 문서 layer | 컨벤션 본문 강화 |
| sprint-41 | 정량 layer | CLI 5 종 |
| sprint-42 | 정성 layer | CLI 4 종 |
| **sprint-43** | **runtime invoke layer** | **CLI 3 종 + orchestrator literal command** |

**12 CLI 통합 + 4 layer + literal command 본문 박힘** = ouroboros + *declared = invoked* 강제.

### 마감 사실

- 6 PR 모두 main 머지 + push (commit-immediate + push-immediate)
- self_lint 후속 +4 (144 → 148 예정 — C-SCM / C-PIA / C-DSP / C-OWL)
- 컨벤션 87 (sprint-42 동일)
- HARD-RULE 9.yy / 9.zz / 9.aaa 신규
- phases/06/08/09/10/14 본문에 literal Bash command 박힘 (5 phase × 평균 3 command = 15 literal invocation)

### 후속

- **sprint-44 검토 후보** — self_lint.py 에 12 CLI 호출 trace 통합 + cold session 실 검증 (외부 적용 후 활성 여부 측정)

## v0.9.47 — 2026-05-10 (sprint-42 — Context-and-Effort Hurdles 트랙 6)

### 마일스톤

sprint-41 v0.9.46 마감 직후 0510-2 회차 (mine-throughput, sprint-41 push 전) = **87/100 (-3pt 추가, 95→90→87 cumulative)** 진단. 5 신규 결손 발견:
- agent 자율 종료 자백 (*"defer to opus-reviewer"*, *"asymptote"*, *"plateaued"*, *"would only fine-tune"*, *"final ground truth"*)
- 다카포 round N+1 universe 감소 (3→3 re-rate→1)
- 컨텍스트 전달 0 (`prev_fingerprint` chain 1 단계만, 본문 cross-phase 인용 0)
- 1단계 이상 과거 phase reference 0
- stagnation 후 exit 자율 stop (4 시도 evidence 0)

본 sprint = sprint-41 *정량 layer* 위에 **정성 layer** 4 신규 CLI 추가. 사용자 직접 지적 5 항 1:1 정정. ouroboros + 자백 어휘 차단 = *더 깊은* enforcement.

### 변경 — 트랙 6 6 PR (PR-A ~ PR-F)

| PR | scope | 산출 | self_lint |
|---|---|---|---|
| PR-A | sprint-42 plan + 0510-2 87 회귀 분석 docs | 2 docs | 0 |
| PR-B | **cross_phase_context_audit.py** + HARD-RULE 9.uu | scoring + test (10/10 PASS) | (C-CPC 후속) |
| PR-C | **universe_count_monotonicity.py** + HARD-RULE 9.vv | scoring + test (6/6 PASS) | (C-UCM 후속) |
| PR-D | **stagnation_breakthrough.py** + HARD-RULE 9.ww | scoring + test (8/8 PASS) | (C-SBR 후속) |
| PR-E | **surrender_phrase_grep.py** + HARD-RULE 9.xx + 신규 컨벤션 surrender-phrase-forbid | scoring + test (7/7 PASS) + conventions | (C-SPF 후속) |
| PR-F | sprint 마감 v0.9.47 + CHANGELOG (본 entry) | SKILL.md / orchestrator / plugin.json / CHANGELOG | 0 |

### CLI 4 종 신규 (skills/theseus-harness/scoring/)

| CLI | 역할 | exit code |
|---|---|---|
| `cross_phase_context_audit.py` | phase N 본문에 직전 + 1단계 이상 과거 phase 인용 ≥ 1 each | 0/1 |
| `universe_count_monotonicity.py` | round N+1 ≥ N + impl 단일 universe 시 7-condition 명시 | 0/1 |
| `stagnation_breakthrough.py` | stagnation + < 0.999 시 exit 자율 차단 + 4 breakthrough 시도 evidence | 0/1 |
| `surrender_phrase_grep.py` | 8 surrender 어휘 grep + override 메커니즘 | 0/1 |

### HARD-RULE 9 신규 (orchestrator SKILL.md)

- **9.uu** — phase 02-14 exit 시 cross_phase_context_audit.py 자동 호출
- **9.vv** — phase 06/08 exit 시 universe_count_monotonicity.py 자동 호출
- **9.ww** — phase 10 sprint iteration 종료 시 stagnation_breakthrough.py 자동 호출
- **9.xx** — phase 10 / 14 진입 시 surrender_phrase_grep.py 자동 호출

### 신규 컨벤션 (+1, 86 → 87)

| 신규 | 위치 | 기능 |
|---|---|---|
| surrender-phrase-forbid | conventions/surrender-phrase-forbid.md | 8 패턴 카탈로그 + override 메커니즘 |

### 테스트 — 31/31 PASS (4 신규 suite 통합)

- test_cross_phase_context_audit (10) + test_universe_count_monotonicity (6) + test_stagnation_breakthrough (8) + test_surrender_phrase_grep (7) = **31**

각 CLI 의 *0510-2 회피 패턴* 직접 회귀 테스트 포함:
- cross_phase: tournament-impl-01 본문 phase 02/04/05 인용 0 → exit 1 ✓
- universe_count: round 2 same 3 re-rate (NEW=0) → exit 1 ✓
- stagnation: sprints/03 stagnation_detected + score 0.97 + decision exit_sprint_loop_per_DEC-autonomy → exit 1 ✓
- surrender_phrase: lessons_outbound[1] = "0.97 < 0.999 G4 asymptote; defer to opus-reviewer ... final ground truth" → 5 패턴 매치 → exit 1 ✓

### 마감 사실

- 6 PR 모두 main 머지 (commit-immediate + push-immediate)
- self_lint 후속 +4 (140 → 144 예정)
- 컨벤션 86 → 87 (+1 surrender-phrase-forbid)
- HARD-RULE 9.uu / 9.vv / 9.ww / 9.xx 신규 (4)

### 누적 패러다임 (sprint-40 + 41 + 42)

| sprint | layer | enforcement |
|---|---|---|
| sprint-40 | 문서 layer | 컨벤션 본문 강화 (명세) |
| sprint-41 | 정량 layer | CLI 5 종 (점수/산출물/4 layer/chain/골격) |
| **sprint-42** | **정성 layer** | **CLI 4 종 (context/universe/stagnation/자백)** |

3 layer 결합 = ouroboros + 정량 + 정성. 9 CLI (5+4) 통합 = *진정한* runtime guard.

### 메모리 신규 후보

- `project_sprint42_v0947.md` (sprint 마감)
- `feedback_surrender_language_enforcement.md` (자백 어휘 차단 원칙)

### 후속

- **sprint-43 검토 후보** — runtime_guard_chain.py 에 9 CLI 모두 통합 dispatch + self_lint.py 8 룰 (sprint-41 4 + sprint-42 4) 본격 통합

## v0.9.46 — 2026-05-10 (sprint-41 — Hurdle-as-CLI 트랙 5)

### 마일스톤

sprint-40 v0.9.45 마감 직후 0510 회차 (theseus-orchestrator-g4) 외부 검증 = **90/100 (-5pt 회귀)**. sprint-40 13 산출물 모두 0 emit + tournament-impl winner 57/60 = 0.95 자율 round 2 = 0 + sprint cap = 1 자율 stop. *컨벤션 선언 ≠ 런타임 집행* 갭이 sprint-40 *문서 layer 강화* 만으로 닫히지 않은 직접 evidence.

본 sprint = 사용자 직접 지적 — *"이쯤이면 충분해" 자율 종료 습성* + *ouroboros MCP 처럼 CLI/프로그램 기반 룰베이스 허들 강화* — 의 1:1 구조 정정. 컨벤션 본문의 모든 임계 / 다카포 / 게이트를 **CLI 스크립트** 로 코드화 + orchestrator 가 phase 진입/종료 시 *명령형 호출 의무*. exit 1 = phase advance 차단.

### 변경 — 트랙 5 7 PR (PR-A ~ PR-G)

| PR | scope | 산출 | self_lint |
|---|---|---|---|
| PR-A | sprint-41 plan.md + 0510 회귀 분석 docs | 2 docs | 0 |
| PR-B | **dacapo_threshold.py** + HARD-RULE 9.qq | scoring/dacapo_threshold.py + test (8/8 PASS) | (C-DCT 후속) |
| PR-C | **cold_session_artefacts.py** + HARD-RULE 9.rr | scoring/cold_session_artefacts.py + test (7/7 PASS) | (C-CSA 후속) |
| PR-D | **sprint_loop_cap.py** + HARD-RULE 9.ss + UTF-8 stdout fix | scoring/sprint_loop_cap.py + test (5/5 PASS) | (C-SLC 후속) |
| PR-E | **runtime_guard_chain.py** + HARD-RULE 9.tt + contracts.md b 명료화 | scoring/runtime_guard_chain.py + test (10/10 PASS) | (C-RGC 후속) |
| PR-F | **generate_sprint40_artefacts.py** + pre-cold-session-bootup.md 강화 | scoring/generate_sprint40_artefacts.py + test (6/6 PASS) | 0 |
| PR-G | sprint 마감 v0.9.46 + CHANGELOG (본 entry) | SKILL.md / orchestrator / plugin.json / CHANGELOG | 0 |

### CLI 5 종 신규 (skills/theseus-harness/scoring/)

| CLI | 역할 | exit code semantics |
|---|---|---|
| `dacapo_threshold.py` | tournament-NN.md winner 점수 추출 → ratio < 0.999 시 round N+1 강제 | 0 = 임계 통과 / 1 = round N+1 의무 |
| `cold_session_artefacts.py` | sprint-40 13 산출물 (gate_v6/v8/readme_summary/methodology/4 패턴/modeling_shortcuts/cascaded_subq/webview_exit/iv_exit/iv_dashboard) 존재 + valid + verdict 검증 | 0 = 모두 통과 / 1 = 결손 (stderr list) |
| `sprint_loop_cap.py` | 4 layer (auto/internal/tournament/external) 모두 ≥ 임계 일 때만 stop | 0 = stop 허용 / 1 = continue 의무 |
| `runtime_guard_chain.py` | skill_version + phase 단조성 + sub-CLI hook 통합 dispatch | 0 = phase advance 허용 / 1 = 차단 |
| `generate_sprint40_artefacts.py` | 13 산출물 빈 골격 (verdict: pending) 자동 emit | 0 = emit 성공 / 1 = 디스크 실패 |

### HARD-RULE 9 신규 (orchestrator SKILL.md)

- **9.qq** — phase 06/08 종료 직전 `dacapo_threshold.py` 자동 호출 (round N+1 자동 강제)
- **9.rr** — phase 09 진입 직전 `cold_session_artefacts.py` 자동 호출 (자동 평가 ≠ 산출물 통과 분리)
- **9.ss** — phase 10 sprint loop 종료 직전 `sprint_loop_cap.py` 자동 호출 (4 layer 종합)
- **9.tt** — 매 phase 진입/종료 시 `runtime_guard_chain.py` 자동 호출 (sprint-41 핵심 enforcement)

### contracts.md 명료화 (sprint-41 PR-E)

§재진입 규칙 b — *"minor 이상"* → *"(major, minor, patch) tuple ≥ tuple"* 명료화. 0.x.y 라인에서 patch 가 sprint 마다 증가 → 전체 tuple 비교 의무. runtime_guard_chain.py:check_skill_version 가 enforcement.

### self_lint 신규 후보 (+4, 136 → 140)

C-DCT / C-CSA / C-SLC / C-RGC — 후속 sprint 에서 self_lint.py 통합 (본 sprint 는 CLI 도입 우선).

### 테스트 — 36/36 PASS

5 suite 통합:
- test_dacapo_threshold (8) + test_cold_session_artefacts (7) + test_sprint_loop_cap (5) + test_runtime_guard_chain (10) + test_generate_sprint40_artefacts (6) = 36

각 CLI 의 *0510 회귀 패턴* 직접 회귀 테스트 포함 (e.g., 57/60 → exit 1, sprint-40 13 산출물 부재 → exit 1, Auto 100% + Tournament 0.95 → continue).

### 마감 사실

- 7 PR 모두 main 머지 (commit-immediate + push-immediate 패턴)
- self_lint 후속 +4 (136 → 140 예정)
- 컨벤션 86 (sprint-40 동일)
- HARD-RULE 9.qq / 9.rr / 9.ss / 9.tt 신규 (4)
- 외부 검증 — 사용자가 fresh G4 cold session 으로 v0.9.46 강제 적용 후 진행

### 메모리 신규 후보

- `project_sprint41_v0946.md` (sprint 마감)
- `feedback_hurdle_as_cli_paradigm.md` (ouroboros 패러다임 정착 원칙)

### 후속

- **sprint-42 검토 후보** — self_lint.py 에 C-DCT / C-CSA / C-SLC / C-RGC 4 룰 통합 + orchestrator runtime guard 의 phase-state-machine.md 분리 정착

## v0.9.45 — 2026-05-10 (sprint-40 — 컨벤션 런타임 활성 + 4 게이트 layer 도입 트랙 4)

### 마일스톤

sprint-39 마감 후 외부 검증 (simulation-bench 001 g4-v2) 이 본 하네스의 *구조적 결손* 두 축을 동시 노출 :
- **컨벤션 선언 ≠ 런타임 집행** — skill_version minor silent skip / viewer 산출물 file-existence 미강제 / sprint-39 4 게이트 JSON 자동 emit 미연결. 메모리 [`feedback_convention_runtime_gap.md`] 의 직접 발현.
- **enforcement layer 의 5 layer 결손** — V6 evidence-bound / numeric drift atomic / heuristic 4-tier 분류 / methodology completeness / phase 13 G4+ invoke step.

본 sprint = 두 축을 8 PR 로 통합 — **범용 (any project), 치밀 (evidence-bound), 밀도 (4-tier 골격)**. 메모리 [`feedback_harness_strengthening_methodology.md`] 의 *"본 하네스 강화 = prompt → 게이트 흐름의 *구조* 변경"* 정합 — 도메인-bench 종속 패치 0.

### 변경 — 트랙 4 8 PR (PR-A ~ PR-H)

| PR | scope | 산출 |
|---|---|---|
| PR-A | sprint-40 plan.md + bench v0.9.44 진단 docs (외부 + 메쉬업) | `.ShipofTheseus/sprints/40/plan.md` + `docs/reviews/2026-05-09-bench-001-mine-throughput-v0944{,−meshup}.md` |
| PR-B | **M-1 + G-1** — `skill_version` minor gate (contracts.md) + V6 cross-process evidence (`gate_v6_reproducibility.json` + 7 anti-pattern grep) | conventions/{contracts, reproducibility-doublecheck, cross-process-anti-patterns 신규}.md + phases/09 §V6-Evidence-Bound |
| PR-C | **M-2** — viewer 산출물 file-existence 3 단 게이트 (phase 09 §V8 사전 / phase 12 종료 / phase 13 종료) | phases/{09, 12, 13} + agents/{webview, interactive-viewer}-builder + viewer-runtime.md |
| PR-D | **M-3** — Phase 13 G4+ invoke step + Phase 12 invoke + pre-bootup 자동 호출 (HARD-RULE 9.nn / 9.oo / 9.pp) | orchestrator SKILL.md + phases/13 invoke step 절 + pre-cold-session-bootup.md |
| PR-E | **M-4 + G-2** — sprint-39 4 게이트 JSON 자동 emit (`gate_pnc/mirror/primary/literal.json` 골격) + numeric drift atomic regen (`gate_readme_summary_consistency.json`) | phases/09 §README-Sync + §Gate-JSON-Emit-Mandate + readme-numbers-from-summary.md |
| PR-F | **G-3** — modeling shortcuts 4-tier (gold-standard / defensible-coarse / heuristic / placeholder) + cascading sub-Q (interview §10) + L2 도메인 critique 카탈로그 (parallel-cold-review §9) | conventions/modeling-shortcuts.md (신규) + interview.md + parallel-cold-review.md |
| PR-G | **G-4** — DES warmup quantification + methodology completeness (nfr-derivation 도메인 sub-checklist) + `gate_warmup.json` | conventions/nfr-derivation.md + phases/09 §Warmup-Quantification |
| PR-H | sprint 마감 v0.9.45 + CHANGELOG (본 entry) | SKILL.md / orchestrator SKILL.md / plugin.json / CHANGELOG |

### 변경 — self_lint (+7 신규, 129 → 136)

| 룰 | scope |
|---|---|
| C-V6X | gate_v6_reproducibility.json verdict + summary_byte_equal + violations |
| C-VEX | webview/exit_gate.json + interactive-viewer/exit_gate.json + gate_v8_viewer_readiness.json (3 게이트 통합) |
| C-RDS | gate_readme_summary_consistency.json verdict + atomic_regen_block.atomic |
| C-GJM | sprint-39 4 게이트 JSON verdict pass (silent skip 차단) |
| C-MSC | intent/modeling_shortcuts.json classification + alternative + expected_loss |
| C-CSQ | intent/04-cascaded-subq.md keyword 매칭 sub-Q 답 존재 |
| C-PCR-L2 | parallel-cold-review L2 catalogue applied |
| C-WUP | gate_warmup.json 4 methodology 항목 verdict pass + evidence_path 실재 |

(C-VEX 통합 카운트 1 + 7 = 8 신규 — 본 sprint 가 7 룰로 명세하나 C-VEX 가 3 게이트 통합 단일 룰. 실 net +7.)

### 변경 — 신규 산출물 (per-project)

- `quality/gate_v6_reproducibility.json` — V6 cross-process evidence + sha256 + anti-pattern grep
- `quality/gate_v8_viewer_readiness.json` — phase 09 entry viewer 외피 검사
- `webview/exit_gate.json` — phase 12 종료 file-existence
- `interactive-viewer/exit_gate.json` — phase 13 종료 file-existence + widgets ≥ 1/3
- `quality/gate_readme_summary_consistency.json` — atomic regen + drift ≤ 0.01%
- `intent/modeling_shortcuts.json` — phase 02/03 4-tier classification
- `intent/04-cascaded-subq.md` — phase 04 cascading sub-Q 산출
- `quality/gate_warmup.json` — DES methodology 4 항목 (phase 09)

### 변경 — 신규 컨벤션 (+2, 84 → 86)

| 신규 | 위치 | 기능 |
|---|---|---|
| cross-process-anti-patterns | conventions/cross-process-anti-patterns.md | 7 regex 카탈로그 (Python hash() salt / np.random.seed(hash()) / random.seed(hash()) / os.urandom mix / id() / time.time() seed / uuid4() seed) |
| modeling-shortcuts | conventions/modeling-shortcuts.md | 4-tier classification + per-domain L2 매핑 |

### 변경 — 신규 HARD-RULE 9 (orchestrator SKILL.md)

- **9.nn** — G4+ Phase 13 invoke step 강제
- **9.oo** — Phase 12 invoke step 강제 (모든 grade)
- **9.pp** — pre-cold-session-bootup 자동 호출 강제

### 구조 가치 (범용 / 치밀 / 밀도)

| PR | 구조 변경 (도메인 독립) | 본 하네스 적용 범위 |
|---|---|---|
| PR-B | `skill_version` minor gate (silent skip 차단) + V6 evidence-bound (subprocess × 2 + sha256 + 7 anti-pattern grep) | 모든 결정성 파이프라인 (Python hash() salt 등 일반 패턴) |
| PR-C/D | viewer 산출물 file-existence 3 단 게이트 + Phase 12/13 invoke step + pre-bootup 자동 호출 | 모든 G3+ 회차 (observability claim ↔ artifact 정합) |
| PR-E | sprint-39 4 게이트 JSON 골격 자동 emit + numeric drift atomic regen (±0.01%) | 모든 deliverable + summary.json 페어 (도메인 무관) |
| PR-F | modeling shortcuts 4-tier (gold-standard / defensible-coarse / heuristic / placeholder) + cascading sub-Q (interview keyword 매핑) + L2 도메인 critique 카탈로그 (DES/ML/API/ETL 5 도메인) | 모든 도메인 모델링 (heuristic-vs-optimal axis 추가) |
| PR-G | methodology-completeness 4 골격 (transient/sample/determinism/horizon) — *도메인-agnostic* enforcement, sub-checklist 는 nfr-derivation 분리 | 모든 도메인 매칭 회차 |

**구조 가치 = enforcement layer 의 닫힘** — *"의사코드 → enforcement"* (메모리 [`feedback_pseudocode_to_enforcement.md`]) 패러다임의 5 layer 정착. 외부 점수 영향은 *결과* 이지 *목표* 아님 — 본 sprint 의 본질은 *컨벤션 선언* 과 *런타임 집행* 의 갭 폐쇄.

(G-5 conceptual exemplary-rubric = sprint-41+ 신규 *질적 게이트* 패러다임 — 본 sprint 범위 외.)

### 마감 사실

- 8 PR 모두 main 머지 (commit-immediate 패턴, 사용자 합의)
- self_lint 129 → 136 (+7)
- 컨벤션 84 → 86 (+2)
- HARD-RULE 9.mm → 9.pp (+3)
- 외부 검증 보류 — simulation-bench 재실행은 사용자가 직접 (skill_version 0.9.45 강제 적용 후 fresh G4 cold session)

### 메모리 신규 후보

- `project_sprint40_v0945.md` (sprint 마감 결과)
- `project_bench_001_v0945.md` (재실행 후 — 100/100 도달 시 또는 부분 회복 시)

### 후속

- **sprint-41 검토 후보** — G-5 conceptual exemplary-rubric (질적 게이트 신규 패러다임) + sprint-40 메모리 [`feedback_convention_runtime_gap.md`](C:\\Users\\cxx\\.claude\\projects\\D--github-ShipofTheseus\\memory\\feedback_convention_runtime_gap.md) 의 추가 결손 식별

## v0.9.44 — 2026-05-09 (sprint-39 — 4 패턴 inline 트랙 3)

### 마일스톤

sprint-37/38 마감 후 sprint-39 트랙 3 — sprint-37 §0 의 4 감점 메타 패턴 (94 plateau 직접 원인) 을 phase 09 게이트 본문에 inline. 별도 컨벤션 0, cold session 자동 검출.

### 변경 — 트랙 3 6 PR (PR-A ~ PR-F)

| PR | scope |
|---|---|
| PR-A #88 | sprint-39 plan.md |
| PR-B #89 | A. PNC inline → phases/09 §PNC (Plumbed-Not-Consumed, AST 분석) |
| PR-C #90 | B. Mirror inline → phases/09 §Mirror (Workspace ≠ Deliverable) |
| PR-D #91 | C. Primary-Source inline → phases/09 §Primary (Proxy-as-Primary, sibling overlap > 50%) |
| PR-E #92 | D. Literal-Forbid inline → phases/09 §Literal (Letter-by-Fallback, regex strict) |
| fix #93 | C23 정합 — §Literal '사용자 ack 0' 라인에 06.f marker |
| PR-F | sprint 마감 (v0.9.44 + CHANGELOG, 본 entry) |

### 변경 — self_lint (+4 신규, 125 → 129)

| 룰 | scope |
|---|---|
| C-PNC | phases/09 §PNC (정의 ↔ 사용 비대칭) |
| C-MIR | phases/09 §Mirror (internal ↔ deliverable mirror) |
| C-PRI | phases/09 §Primary (formula sibling overlap > 50%) |
| C-LIT | phases/09 §Literal (avoid directive literal regex) |

### 변경 — 신규 산출물 (per-project, phase 09)

- `gate_pnc.json` — fields_total / consumed / orphan + violations
- `gate_mirror.json` — internal_facts ↔ deliverable mirror 매핑
- `gate_primary.json` — primary_directives + direct_measured / proxy_via_sibling
- `gate_literal.json` — avoid_directives + regex_patterns + violations

### 마감 사실

- 4 패턴 모두 phase 09 본문 inline (별도 컨벤션 0, sprint-37 다이어트 패러다임 정합)
- self_lint 125 → 129 (+4)
- 3 단계 패러다임 전환 완료: 정리 (sprint-37) → 깊이 (sprint-38) → 통합 (sprint-39)

### 메모리 신규 후보

- `project_sprint39_v0944.md` (본 PR-F 머지 시점)

### 후속

- sprint-40 — 외부 적용 (simulation-bench 재제출, sprint-37/38/39 누적 효과 측정, 94 plateau 극복 검증)

## v0.9.43 — 2026-05-09 (sprint-38 — 본체 강화 + 구현-층 깊이 트랙 2)

### 마일스톤

sprint-37 다이어트 (트랙 1) 마감 후 sprint-38 트랙 2 진입. 핵심 = phase 06 monolithic → 6 sub-phase 분해 + phase 07 dispatch 3 sub-phase + phase 08.f prompt-trace lint + path-policy 정식 enforcement.

### 변경 — 트랙 2 12 PR (PR-A ~ PR-L)

| PR | scope |
|---|---|
| PR-A #75 | sprint-38 plan.md (.ShipofTheseus/sprints/38/) |
| PR-B #76 | path-policy + user-confirm gate (phase 06.f) 정식 enforcement (sprint-37 권고 → sprint-38 게이트) |
| PR-C #77 | 06.a Research-injection sub-phase (외부 ref ≥ 3 + 결론 ≤ 3) |
| PR-D #78 | 06.b Intent-decoding + directives.json schema (6 type × 3 layer) |
| PR-E #79 | 06.c Classification sub-phase (≥ 3 layer + orphan 모듈 0) |
| PR-F #80 | 06.d Sub-tree TODO sub-phase (max_depth ≥ 3 + dispatch 1:1) |
| PR-G #81 | 06.e Post-decision Premortem sub-phase (격언 동·서 + derived improvements ≥ 1) |
| PR-H #82 | phase 06 6 sub-phase architecture summary 통합 |
| PR-I #83 | phase 07 dispatch 3 sub-phase (07.a table / 07.b trace / 07.c cross-agent invariant) |
| PR-J #84 | phase 08.f prompt-trace lint (deliverable → directive 매핑) |
| PR-K #85 | self_lint 신규 3 (C-DIET / C-PHASE-LEN / C-MIGRATION) |
| PR-L | sprint 마감 (v0.9.43 + CHANGELOG, 본 entry) |

### 변경 — 신규 산출물 (per-project)

- `plan/06-research.md` (06.a) — 인용 ≥ 3 + 결론 ≤ 3
- `plan/06-directives.json` (06.b) — 6 type × 3 layer + source_quote/loc
- `plan/06-classification.md` (06.c) — ≥ 3 layer + orphan 0
- `plan/06-todo-tree.md` (06.d) — max_depth ≥ 3 + leaf 매핑
- `plan/06-premortem.md` (06.e) — derived improvements ≥ 1
- `plan/06-path-policy.md` (06.f) — 사용자 ack 의무
- `dispatch/07-dispatch-table.md` (07.a) — TODO ↔ agent 매핑
- `dispatch/07-dispatch-trace.json` (07.b) — agent 실행 trace
- `dispatch/07-cross-agent-lint.md` (07.c) — invariant 검증
- `impl/08-prompt-trace.md` (08.f) — deliverable ↔ directive 매핑

### 변경 — self_lint (+9 신규, 116 → 125)

| 룰 | scope |
|---|---|
| C-PPC | path-policy + user-confirm gate (phase 06.f) |
| C-RES | research-injection (06.a) |
| C-IDC | intent-decoding directives.json (06.b) |
| C-CLS | classification (06.c) |
| C-STT | sub-tree TODO (06.d) |
| C-PMT | premortem (06.e) |
| C-DPT | phase 07 dispatch 3 sub-phase |
| C-PT | prompt-trace (08.f) |
| C-DIET | deprecated 컨벤션 grace ≤ 1 sprint |
| C-PHASE-LEN | 페이즈 본문 50K chars 강제 (sub-phase 분리) |
| C-MIGRATION | MIGRATION.md 매핑 무결성 |

(C23 allow_markers 확장 — 06.f / path-policy / user-confirm gate sanctioned interrupt 통과)

### 변경 — autonomy 정책 갱신

기존 "사용자 단 한 번 호출 (페이즈 04)" → **"사용자 단 두 번 호출 (페이즈 04 + 페이즈 06.f)"**. 산출물 경로는 cold context 결정 의무 (사전 위임 매핑 불가).

### 마감 사실

- phase 06 본문 = 41K chars (sub-phase 6 통합 후 자연 비대) — C-PHASE-LEN 50K 임계 통과. sprint-39+ 에서 별도 파일 분리 (phases/06.a-research.md / 06.b-intent-decoding.md 등) 후보
- self_lint 125 (sprint-37 114 → +1 fix #74 + sprint-38 PR-B~K +10 = 125). all_ok=True 모든 PR 통과
- 본 plan.md 자체 = path-policy 정식 첫 적용 사례 (sprint-37 권고 → sprint-38 enforcement)

### 메모리 신규 후보

- `feedback_phase06_sub_phase_decomposition.md` (PR-H 머지 후 신규) — 6 sub-phase 분해 결정 영구화
- `project_sprint38_v0943.md` (본 PR-L 머지 시점) — 출하 결과 기록

### 후속

- sprint-39 — 트랙 3 (페이즈 09 4 패턴 inline)
- sprint-40 — 외부 적용 (simulation-bench 재제출, 94 plateau 극복 검증)

## v0.9.42 — 2026-05-09 (sprint-37 — convention diet + 본체 강화 패러다임 전환)

### 마일스톤

사용자 직접 지시 — *"구멍 메우기 식 컨벤션 누적 중지 → 다이어트 + 본체 강화 + 구현-층 깊이 + 산출물 prompt 의존 + 산출물 경로 user-confirm 게이트"*. simulation-bench 회차에서 94 plateau 재확인. 누적 패치 → 다이어트+본체 패러다임 전환의 구조적 출발.

본 sprint = **트랙 1 (다이어트)** 까지. 트랙 2 (본체 강화 + 구현-층) sprint-38 / 트랙 3 (4 패턴 inline) sprint-39 분리.

### 변경 — 다이어트 11 PR (90 → 77 컨벤션, -13)

| PR | scope | 통폐합 | 라인 |
|---|---|---|---|
| PR-A | 분석 보고서 + MIGRATION.md 골격 | 0 | 0 |
| PR-AA | intent-refresh-post-interview + intent-refresh-post-critique → intent-refresh | 2→1 | -7 |
| PR-AB | aide-tree-multi-phase + aide-tree-symmetry → aide-tree | 2→1 | -28 |
| PR-AC | viewer-auto-refresh + viewer-runtime-lifecycle → viewer-runtime | 2→1 | -15 |
| PR-AD | mindmap-centrality + mindmap-quality-gardening + mindmap-richness-default → mindmap-quality | 3→1 | -156 |
| PR-AE | sprint-regression-loop + regression-derived-lint-rule-autogen → regression | 2→1 | -34 |
| PR-AF | sprint-score-delta-tracking + cross-universe-lesson-distillation + lessons → sprint-narrative | 3→1 | -111 |
| PR-AG | domain-research-stacking + domain-failure-patterns + domain-model-completeness → domain-pack | 3→1 | -119 |
| PR-AH | canonical-not-stub → phases/06,08,14 §canonical inline | 1→0 | (inline) |
| PR-AI | timing → phases/00,14 §timing inline | 1→0 | (inline) |
| PR-AJ | stack → phases/04 §stack inline | 1→0 | (inline) |
| PR-AK | self_lint 통합 + version bump v0.9.42 + CHANGELOG (본 entry) | — | — |

**누적**: 14 컨벤션 통합 (8 컨벤션 7 통합본 + 1 통합본 = 7 신규) + 3 inline = -13 컨벤션 (90 → 77), 본문 -470 라인.

### 변경 — 신규 산출물

- `skills/theseus-harness/conventions/MIGRATION.md` — 다이어트 매핑 표 (deprecated → successor + introduced_in / removed_in / rationale)
- `skills/theseus-harness/conventions/intent-refresh.md` (1차+2차 phase param 분기)
- `skills/theseus-harness/conventions/aide-tree.md` (breadth + depth 두 축)
- `skills/theseus-harness/conventions/viewer-runtime.md` (frontend 폴링 + backend lifecycle 두 layer)
- `skills/theseus-harness/conventions/mindmap-quality.md` (구조 + 형식 + 풍성도 세 layer)
- `skills/theseus-harness/conventions/regression.md` (sprint loop + lint autogen 두 layer)
- `skills/theseus-harness/conventions/sprint-narrative.md` (시간 + 공간 + 단계 세 axis)
- `skills/theseus-harness/conventions/domain-pack.md` (model + research-stacking + failure-patterns 세 layer)

### 변경 — 갱신

- `skills/theseus-harness/scoring/self_lint.py` — C-IRPI / C-IRPC / C-VAR / C-VRL / C-CNS / C-RDLR / C-SDT / C-CULD / C20 / C-DMC 함수 모두 통합본 가리키게 + 키워드 검사 정합 (10 함수)
- `skills/theseus-harness/SKILL.md` + `.claude-plugin/plugin.json` — 0.9.40 → 0.9.42, 90 → 77 카운트
- `skills/theseus-orchestrator/SKILL.md` — phase lookup 표 통합본 §섹션 표시 (5 페이즈 행)
- `skills/theseus-harness/agents/{intent-extractor, implementer, planner, regression-analyst}.md` — cross-ref 통합본
- `skills/theseus-harness/phases/{00, 04, 05, 06, 08, 09, 10, 11, 14}.md` — cross-ref + §canonical / §timing / §stack inline
- 주요 cross-ref 컨벤션 30+ 갱신

### 마감 사실

- 본 sprint 의 가장 큰 발견 = plan.md §3.1.4 inline 4 후보 과소평가 — runtime infra + self_lint 룰 동반 컨벤션은 inline 단순 흡수 불가. 카테고리 C 로 재분류
- self_lint hardcode 컨벤션 파일명 검사 = 통합본 path + 키워드 정합으로 깨끗 처리 가능 (PR-AA / PR-AC / PR-AD / PR-AE / PR-AF / PR-AG / PR-AH 모두 동일 패턴)
- 본 다이어트의 후속 sprint-38 (트랙 2 — 본체 강화 + 구현-층 깊이) / sprint-39 (트랙 3 — 4 패턴 inline) 진행 전 본 sprint 의 통합본 cold session 검증 권고

### 메모리 신규 (영구화)

- `feedback_convention_diet_paradigm.md` — 누적 패치 → 다이어트+본체 패러다임 전환
- `feedback_deliverable_path_user_confirm.md` — 산출물 경로 + user-confirm 게이트

## v0.9.40 — 2026-05-09 (sprint-35 — prebuilt shell + JSON injection)

### 마일스톤

사용자 직접 지시 — *"리니지 뷰 / 테세우스 뷰 는 html 로 미리 준비해두고 컨텐츠만 동적 교체되도록 하자"*. cold session 마다 매번 Bun+React build 하는 패턴을 *prebuilt vanilla shell 복사 + JSON 데이터 emit* 으로 교체. 결과: cold session 부팅 시간 대폭 감소 + bun/npm 의존 제거 + 산출물 일관성. FE 시연 = `huashu-design` 스킬 (정보 건축 / 엔지니어링 디버그 도구).

1. **`templates/lineage-viewer/dist/`** — standalone HTML viewer (vanilla, ≈3.4 MB w/ vendored mermaid). 6 섹션 (헤더 + flowchart + gantt + fingerprint chain + dacapo summary + phase 04 답안 매핑 + sentinel events). 라이트/다크 토글 + localStorage 유지.
2. **`templates/webview/dist/`** — phase 12 theseus-view shell (vanilla, ≈3.4 MB w/ vendored mermaid + marked). 8 탭 (Progress / ModuleMap / DesignIntent / ImplIntent / UnitTests / E2ETests / Sprints / Runtime). vanilla SVG 점수 차트 (0.999 임계 점선). 기존 `templates/webview/src/` + `server.ts` + `package.json` = 옵션 dev mode 만 보존.
3. **`conventions/prebuilt-shell-runtime-json.md`** — emit 프로토콜 (패턴 A inline `window.__LINEAGE__/__WEBVIEW__` + 패턴 B sibling JSON fetch) + 스키마 (lineage.json / webview.json) + self_lint C-PSR.
4. **`HARD-CORE.md` 9.nn** — cold session build 0 룰. dist 복사 + JSON injection 만 강제.
5. **`phases/12-webview-assembly.md`** 본문 갱신 — "bun runtime build" → "prebuilt shell 복사 + JSON emit". 흔한 실패 c (build-time fs bake) 의미 보존, dev mode 옵션 명시.
6. **`agents/webview-builder.md`** 본문 갱신 — 동작 4 단계 (shell 복사 / 데이터 합본 / inline 주입 옵션 / dev mode src 옵션). 8 탭 = shell 책임, 데이터 채우기 = agent 책임으로 분리.
7. **`conventions/phase-lineage-viewer.md` §14 신규** — `lineage.{md,html,json}` 이중/삼중 emit. C-PLV 룰 확장 (G3+ lineage.html 의무).
8. **self_lint C-PSR 신규** + C-HC1 임계 4250 → 4400 bump (9.nn 추가 정합, sprint-32/34 precedent).

### 변경 — 신규 산출물

- `templates/lineage-viewer/dist/{index.html, assets/{styles.css, app.js, mermaid.min.js}}`
- `templates/lineage-viewer/sample/{lineage.json, lineage.html, inline-data.js}` (검증용)
- `templates/webview/dist/{index.html, assets/{styles.css, app.js, mermaid.min.js, marked.min.js}, data/webview.json}`
- `templates/webview/sample/webview.json` (검증용)
- `conventions/prebuilt-shell-runtime-json.md` (90 컨벤션째)

### 변경 — 갱신

- `HARD-CORE.md` — 9.nn 한 줄 추가 (4386 chars, ≤ 4400 임계 통과)
- `phases/12-webview-assembly.md` — 전면 재작성 (prebuilt + JSON 패턴, 옵션 dev mode 분리)
- `agents/webview-builder.md` — 전면 재작성 (동작 4 단계, 8 탭 데이터 키 의무)
- `conventions/phase-lineage-viewer.md` — §14 추가, §11 호환성에 prebuilt-shell-runtime-json 호환 row 추가
- `conventions/INDEX.md` — prebuilt-shell-runtime-json row, 90 컨벤션 카운트
- `scoring/self_lint.py` — `check_prebuilt_shell_runtime_json` + C-PSR row, C-HC1 임계 4400 으로 bump
- `README.md` d-97 (prebuilt-shell-runtime-json)
- `SKILL.md` frontmatter version 0.9.40
- `.claude-plugin/plugin.json` version 0.9.40

### 자기 평가

- self_lint: **all_ok=True** (60+ 룰 모두 통과 — C-PSR 신규 통과)
- HARD-CORE 길이: 4386 chars (≤ 4400 임계 통과)
- prebuilt shell 검증: dist/ 모든 파일 존재 + CDN 호스트 0 + 데이터 채널 ≥ 1
- 시연 (수동) — `templates/lineage-viewer/sample/lineage.html` + `templates/webview/sample/webview.json` 으로 브라우저 직접 검증 가능 (자동화 환경 file:// 차단으로 sandbox 검증 미수행, 사용자 측 1 회 시연 권장)

### 다음 sprint 후보

- **sprint-36** : phase 13 interactive-viewer 의 prebuilt 패턴 적용 — 도메인별 (DES / ML / API / Frontend / 분석 / ETL) per-domain template + 도메인 매칭 시 dist 선택 복사. 본 sprint 보다 복잡 (per-domain template ≥ 6 종).
- 미리 적용 시뮬: `update_phase_lineage` 호출이 lineage.html 의 `<script>window.__LINEAGE__={...}</script>` inline 갱신을 자동 emit 하는 orchestrator 측 구현 (`scoring/lineage_emitter.py` 후보).

## v0.9.39 — 2026-05-09 (sprint-34 — runtime 단조성 + sub-todo 병렬 + regression + gantt + optional 4-option)

### 마일스톤

사용자 직접 지시 — *5 개선안 일괄 적용*. 본 sprint = "기존 자산 80% 기반 위에 정확한 갭만 채우기" 패턴. 기존 컨벤션 *재발명* 없음, 신규 4 + 기존 1 확장.

1. **runtime entry-time 단조성 게이트** — v0.9.22 forgery (페이즈 01-06 백필 + frontmatter created_at 9-12 분 위조) 를 *runtime* 시점에 차단. `check_cold_session.py` (sprint-32, post-hoc) 와 layer 직교.
2. **sub-todo level 병렬 트리거** — 모듈 단위 `should_subdivide` (sub-agents.md) 위에 *T-NNN 단위* fine-grained TODO DAG 위상 정렬.
3. **commit-level TDD 재실행 게이트** — phase 08 5 sub-phase TDD (페이즈 단위) 위에 매 sub-impl + dacapo step F + sprint iter 단위 재실행.
4. **lineage Mermaid gantt + 모든 그레이드** — `phase-lineage-viewer.md` (br) 확장. flowchart 만 → flowchart + gantt. G3+ 만 → G1~G5 모두.
5. **optional 의도 4-option 강제** — "추가로 / 해도 좋음 / additional" 옵셔널 마커 검출 시 silent drop 차단 (포함-필수 / cheap-only / defer / drop).

### 변경 — 신규 컨벤션 4 (`conventions/`)

#### `phase-state-machine.md` (sprint-34 신규, core, [all] phases × [all] grades)

- `state/phase_state.json` 라이프사이클 (init/enter/exit/validate/status)
- 단조성 — entered_at strict-greater than 직전 모든 timestamps
- frontmatter `created_at` cross-check — [entered_at, exited_at] 윈도 검증
- v0.9.22 forgery 패턴 직접 차단

#### `subagent-trigger.md` (sprint-34 신규, core, [06,08] × [G3,G4,G5])

- TODO DAG (HARD-RULE 9.a item 3) → Kahn 위상 정렬 → level 단위 병렬 그룹
- 모드 추천: G2=sequential / G3=조건부 parallel / G4=parallel / G5=competition
- cyclic 검출 시 phase 06 자동 회귀
- `sub-agents.md` (모듈) 와 layer 직교 (TODO 단위 fine-grained)

#### `regression-tdd-gate.md` (sprint-34 신규, quality, [08,10,11] × [all])

- `state/regression_log.json` append-only 누적 (test + boot + lint 3 단계)
- 직전 known-good vs 최신 비교 → regression 검출
- phase 11 bisect 의 입력 source
- phase 08 5 sub-phase TDD (페이즈 단위) 와 layer 직교 (commit 단위)

#### `intent-optional-disambiguation.md` (sprint-34 신규, interview, [01,04] × [all])

- 옵셔널 마커 카탈로그 (한국어 9 + 영어 8 패턴)
- clarifier 가 검출 시 4-option 강제 (1. material / 2. cheap-only / 3. defer / 4. drop)
- `intent/04-optional-decisions.md` (G2+ 의무 산출물 신규)
- silent drop ("추가로 X 도" → "X 안 해도 됨") 회귀 차단

### 변경 — 기존 컨벤션 확장 1

#### `phase-lineage-viewer.md` (br, v0.9.22 + sprint-34 확장)

- `applies-to-grades`: `[G3,G4,G5]` → `[all]` (G1/G2 도 minimal 활성)
- §1.5 Mermaid `gantt` chart 절 신규 — `state/phase_state.json` 의 entered_at/exited_at 자동 시각화
- §7 self_lint C-PLV — gantt + dateFormat 검증 추가
- §12 그레이드 활성 표 신규 — G1 (P01+P14 minimal), G2 (P01+P04+P06+P08+P09+P14), G3+ (풀)
- 동기 — 백필/위조는 *간단한 프로젝트* 일수록 발견 안 됨, 모든 그레이드 lineage 의무

### 변경 — `scoring/` 신규 3 + 확장 1

- **`scoring/phase_state.py` 신규** — 5 subcommand (init/enter/exit/validate/status), 단조성 + frontmatter cross-check, 9/9 pytest PASS
- **`scoring/sub_agent_dispatch.py` 확장** — `analyze-todos` subcommand, Kahn 위상 정렬 + 그레이드별 모드 추천, 5/5 신규 pytest PASS
- **`scoring/regression_check.py` 신규** — 3 subcommand (run/last/compare), shell=True 크로스플랫폼, 8/8 pytest PASS

총 신규 22 pytest. 전체 131/131 PASS.

### 변경 — `self_lint.py` 신규 4 checks + 1 확장

- **C-PSM 신규** — phase-state-machine.md + phase_state.py 의무 함수 + 키워드
- **C-STT 신규** — subagent-trigger.md + analyze-todos 의무 함수 + 키워드 (`Kahn` 포함)
- **C-RTG 신규** — regression-tdd-gate.md + regression_check.py 의무 함수 + 키워드
- **C-IOD 신규** — intent-optional-disambiguation.md 키워드 + interview.md cross-link + 4-option 라벨
- **C-PLV 확장** — gantt + dateFormat + axisFormat + phase_state.py + G1/G2 minimal 키워드 추가

108 → 108 checks (5 신규 — C-PLV 는 본문 갱신만), all_ok=True.

### 변경 — `conventions/INDEX.md`

89 → 93 컨벤션 router 행:
- `intent-optional-disambiguation` 신규 (interview / [01,04] / [all] / optional marker 검출)
- `phase-state-machine` 신규 (core / [all] / [all] / phase enter / phase exit)
- `regression-tdd-gate` 신규 (quality / [08,10,11] / [all] / every code change)
- `subagent-trigger` 신규 (core / [06,08] / [G3,G4,G5] / phase 06 exit)
- `phase-lineage-viewer` grades `[G3,G4,G5]` → `[all]`

### 변경 — orchestrator HARD-RULE 9 lookup

- 모든 phase enter/exit → `phase-state-machine` (sprint-34 신규)
- phase 01 / 04 → `intent-optional-disambiguation` 추가
- phase 06 → `subagent-trigger` 추가
- phase 08 → `subagent-trigger` + `regression-tdd-gate` 추가
- phase 10 → `regression-tdd-gate` 추가
- phase 11 → `regression-tdd-gate` 신규 entry
- phase 14 → `phase-lineage-viewer (sprint-34 gantt + 모든 그레이드)` 갱신

### bump

- plugin.json: 0.9.38 → 0.9.39 + description 슬림 (200 char 한도 정합)
- skills/theseus-harness/SKILL.md frontmatter: 0.9.38 → 0.9.39 + description 슬림
- skills/theseus-orchestrator/SKILL.md frontmatter: 0.9.38 → 0.9.39
- skills/theseus-harness/README.md d-93 ~ d-96 신규 + d-90 INDEX 행 count 갱신

### 누적 (sprint-13 ~ sprint-34, 22 sprint)

- v0.9.19 → v0.9.39
- 89 → 93 conventions
- self_lint 104/104 → 108/108 PASS
- pytest 109 → 131 PASS (신규 22)

### 후속 (sprint-35+)

- v0.9.39 cold session 외부 검증 — 신규 4 컨벤션 + gantt + optional 4-option 실제 발현 측정
- phase-state-machine.py orchestrator runtime 통합 — phase 진입/종료마다 자동 호출 (HARD-CORE.md 9.mm 후보)
- regression_check.py — phase 04 Q-D8 verification commands 자동 매핑 (현재 수동 `--test-cmd`)
- (사용자 명시 시) 별 의제 개시

## v0.9.38 — 2026-05-06 (sprint-33 — validator invoke step explicit + mining/C-IDX-3 deferral 정리)

### 마일스톤

sprint-33 = sprint-32 의 cold session validator 를 phase 09 본문에 *첫 동작* 으로 명시.

### 변경 — `phases/09-quality-gates.md` 첫 절 신규

phase 09 진입 직전 의무 호출 step 본문 명시 (HARD-RULE 9.f 본문 통합):

```bash
python skills/theseus-harness/scoring/check_cold_session.py .ShipofTheseus/<프로젝트>/
```

- exit 0 → phase 09 진입 허용
- exit 1 → stderr violation 목록을 `intent/00-violation.md` 기록 + 해당 phase (06 또는 08) 재진입 강제

본 호출은 phase 09 의 *첫 번째 sub-step*, quality-gate 본문 진행보다 우선.

### 결정 — sprint-33 deferral 항목 검토 결과

#### mining example deep cleanup → DONE (deferred 의도 변경)

sprint-25/26 에서 표면 / inline 패턴 정리 완료. 잔존 mining 키워드 (truck/loader/crusher) 는 코드 블록 내 *illustrative algorithmic context* — generic placeholder 치환 시 *의미 손실 risk* 가 가치 보다 큼 (예: "truck.cargo ≥ 0" invariant 예시는 generic 치환 시 추상도 ↑ 가독성 ↓). **본 sprint 에서 cleanup 유지 결정** (사용자 원칙 정합 — 더 깊은 cleanup 은 의미 손실 trade-off).

#### C-IDX-3 strict 활성화 → 영구 informational 유지

C-IDX-3 의 false-positive 다수 (예: phases/00-naming.md 가 conventions/interview.md 인용하지만 INDEX 는 [4] 만) 는 *docs 의 광범위 cross-ref* 가 의도된 패턴 (관련 컨벤션 link, 설명 문맥) 이라 strict 활성화 시 INDEX router 를 *비현실적으로 광범위* 하게 만들거나 docs 본문을 *과도하게 link 정리* 해야 함. **본 sprint 에서 C-IDX-3 영구 informational** 유지 결정. drift 의심 시 manual run 가능 (`check_idx_phase_crossref(skill_root)` 함수 호출).

### bump

- plugin.json / SKILL.md frontmatter: 0.9.37 → 0.9.38.
- self_lint 104/104 PASS (변경 없음).

### 누적 (sprint-13 ~ sprint-33, 21 sprint)

- v0.9.19 → v0.9.38
- 89 conventions
- self_lint 104/104 PASS
- runtime layer (sprint-32) + invoke step explicit (sprint-33)

### 후속 (sprint-34+)

- v0.9.38 cold session 외부 검증 — validator 자동 호출 작동 + Round N+1 NEW universes 발현 + 무한 회귀 polishing 측정
- (사용자 명시 시) 별 의제 개시

## v0.9.37 — 2026-05-06 (sprint-32 — cold-session-side runtime validator + HARD-RULE 9.f)

### 마일스톤

**prose enforcement 한계 돌파.** sprint-15 이후 누적된 "컨벤션 본문 anti-pattern 명시 → agent 자율 우회" 회귀 패턴을 *외부 cold session artifacts 직접 검사* layer 로 차단. orchestrator 가 phase 09 진입 *직전* 의무 호출.

cold session attempt-3 (v0.9.36, mine-throughput-g4-a3) 결정적 회귀 :
- `dacapo-rerun-01.md` 본문에 *"Cold reviewer re-rates the same universes"* — sprint-28 anti-pattern g 정확히 답습
- *"No further dacapo round needed"* — sprint-28 anti-pattern j 답습
- universe count = 4 (rerun ≥ 1 시 ≥ 5 expected — anonymized prev winner + width-1 fresh)
- impl phase 부재 (mandatory_first_rerun 위반)

→ 본문 anti-pattern 명시는 agent 가 *읽고도 무시*. 외부 layer 강제 필요.

### 변경 — `scoring/check_cold_session.py` 신규 (sprint-32 신규 산출물)

cold session artifact validator. 사용 :

```bash
python skills/theseus-harness/scoring/check_cold_session.py <project_path>
# .ShipofTheseus/<project>/ 디렉터리 검사
# exit 0 = PASS, exit 1 = violations
```

7 검증 항목:
1. **plan/tournament-NN.md ≥ 2** (mandatory_first_rerun_satisfied, sprint-19 ce)
2. **plan/dacapo-rerun-NN.md ≥ 1** + 본문 sentinel regex reject
3. **Round N+1 universes 존재** — rerun ≥ 1 시 universe count ≥ 5 (anonymized prev winner + fresh, sprint-28 g)
4. **impl/tournament-impl-NN.md ≥ 2** (G4+ phase 08 mandatory_first_rerun, sprint-19 ce + sprint-29)
5. **impl/dacapo-rerun-impl-NN.md ≥ 1**
6. **sentinel regex reject** — 10 패턴 (sprint-28/29/30 정합) :
   - `re-?rates? same universes` / `same universes re-rated`
   - `no further (sprints|dacapo|rounds) (required|needed)`
   - `winner clear` / `obvious winner` / `clearly best`
   - `passed on first execution` / `first-try pass`
   - `walkover` / `lost the plan tournament before code was written`
7. **impl universe ID ≠ plan universe ID** (sprint-29 f 격리)
8. **shadow-grade-NN.json predicted_score cap by rerun** (sprint-30 — rerun=0 cap 0.90 / rerun=1 cap 0.95 / rerun=2 cap 0.99)
9. **improvement_axes_remaining frontmatter ≥ 1** (rerun < 3 시, sprint-30)

### 변경 — orchestrator HARD-RULE 9.f 신규

HARD-CORE.md HR9 : *Cold session validator: phase 09 진입 직전 `scoring/check_cold_session.py <proj>` 의무. exit 1 시 phase 재진입.*

orchestrator/SKILL.md HARD-RULE 9 lookup 표 동기화.

### 변경 — self_lint

- **C-CSV 신규** (CHECKS 등록): `scoring/check_cold_session.py` 존재 + 7 의무 함수 + 2 상수 (`SCORE_CAP_BY_RERUN` / `SENTINEL_PATTERNS`) 검증
- **C-HC1 cap 4000 → 4200** (9.f 추가로 HARD-CORE 본문 4173 → 4081 + 9.f 1 줄 추가 합산)
- 103 → 104 checks. all_ok=True.

### 검증 — 실패 cold session 에 적용 (cold session attempt-3, v0.9.36)

```
$ python check_cold_session.py .ShipofTheseus/mine-throughput-g4-a3/
FAIL — 6 cold session violation(s):
  - plan/tournament-NN.md = 1 (require ≥ 2 — mandatory_first_rerun_satisfied)
  - plan/candidates/universe-* count = 4 (rerun ≥ 1 시 ≥ 5 expected — Round N+1 = anonymized prev winner + width-1 fresh universes)
  - tournament-01.md: 'improvement_axes_remaining' frontmatter 부재 (rerun=1 < 3 — sprint-30 의무)
  - impl/tournament-impl-NN.md = 0 (require ≥ 2)
  - impl/dacapo-rerun-impl-NN.md = 0 (require ≥ 1)
  - plan/dacapo-rerun-01.md: sentinel pattern 're-rates the same universes' detected
exit code 1
```

→ 본 validator 가 phase 09 진입 직전 호출되었다면 위 6 violations 자동 차단 → phase 06 재진입 강제 → polishing 루프 작동.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.36 → 0.9.37.
- self_lint 104/104 PASS.

### 알려진 결손 (sprint-33+)

- check_cold_session.py 호출 통합 — orchestrator 자동 invoke 패턴 (현재 prose 의무, 사용자 manual run 또는 phase 09 agent 가 호출 의무 인지)
- 코드 블록 내 mining example deep cleanup
- C-IDX-3 strict 활성화 (docs cross-ref 정합 작업)

## v0.9.36 — 2026-05-06 (sprint-31 — C-IDX-4 활성화 + C-IDX-3 informational deferral)

### 마일스톤

C-IDX-3 (phases cross-ref drift) 와 C-IDX-4 (grade vocabulary) 두 신규 lint 구현. C-IDX-4 는 strict 모드 (CHECKS 등록), C-IDX-3 는 false-positive 다수 발견되어 informational 모드 (함수 보존, CHECKS 미등록).

### 변경 — `self_lint.py`

- **C-IDX-4 신규** (CHECKS 등록):
  - INDEX router 의 `applies-to-grades` 컬럼이 G1-G5/all vocabulary 만 사용
  - G6 / G0 등 invalid grade token 차단
  - 모든 89 컨벤션 검증
- **C-IDX-3 함수 작성** (CHECKS 미등록 — informational):
  - phases/NN-*.md 의 STRONG cross-ref 가 INDEX applies-to-phases 와 정합 검증
  - "호환성 / 참조 / See also / 관련 컨벤션 / cross-ref" 섹션의 weak ref skip
  - 그러나 현재 docs 의 광범위 cross-ref 로 false-positive 다수 — strict 등록 시 docs 광범위 수정 필요
  - 후속 sprint 에서 (a) INDEX applies-to-phases 확장 OR (b) STRONG/WEAK 섹션 정합 후 활성화
  - 함수 호출 가능 (manual run / debug)

### 효과

- C-IDX-4 PASS — INDEX router grade vocabulary 정합 검증 자동화
- C-IDX-3 deferred — 후속 sprint 에서 docs 정합 후 활성화 (sprint-32+)
- 102 → 103 checks. all_ok=True.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.35 → 0.9.36.

### 알려진 결손 (sprint-32+)

- C-IDX-3 strict 활성화 — INDEX applies-to-phases 확장 또는 STRONG/WEAK 섹션 정합 작업 후
- 코드 블록 내 mining example deep cleanup (sprint-31 에서 deferral, 별도 sprint 에서 case-by-case)
- v0.9.36 cold session 외부 검증

## v0.9.35 — 2026-05-06 (sprint-30 — conservative-margin-judging 신규 (0.999 마진 보존 + 무한 회귀 polishing 동력))

### 마일스톤

사용자 직접 지시 — *"내부 각 단계의 스코어링 judge 는 보수적으로 더 개선여지가 있을것이라는 접근으로 점수를 매기도록 하여 0.999 의 마진을 남겨두어 다카포-개선을 최대한 많이 회귀 루프하도록 의도"*. 모든 internal judge (tournament/shadow/sprint stop/phase exit) 가 *보수적 prior* 로 채점 → mandatory rerun (ce) + Da Capo 무한 회귀 (sprint-28 j) 의 polishing 동력 보존.

### 변경 — 신규 컨벤션 `conservative-margin-judging.md`

#### rerun-별 score cap (0.999 마진)

```
rerun = 0           : cap = 0.90    (1st pass — 항상 개선 여지)
rerun = 1           : cap = 0.95
rerun = 2           : cap = 0.99
rerun >= 3 + budget >= 0.80 : 0.999 허용
rerun >= 5 + budget >= 0.95 : 0.99999 (G5)
```

#### improvement_axes_remaining frontmatter 의무

각 tournament-NN.md / shadow-grade-NN.json :

```yaml
improvement_axes_remaining: <int>           # 0 = converged (rerun >= 3 시만)
improvement_axes_detail:
  - dim: <차원>
    weakness: "<1 줄>"
    lesson_candidate: "<적용 lesson>"
```

rerun < 3 시 `improvement_axes_remaining: 0` 박으면 reject.

#### judge 자신감 sentinel

regex reject : "winner clear" / "no further improvement" / "no further sprints required" / "clearly best" / "obvious winner" / "passed on first execution".

### 적용 layer (5 영역)

| layer | 산출물 | cap 강제 |
|---|---|---|
| plan tournament | `plan/tournament-NN.md` | winner_score / sub_scores |
| impl tournament | `impl/tournament-impl-NN.md` | 동일 |
| shadow grader | `*/shadow-grade-NN.json` | predicted_score |
| sprint stop | `sprints/NN/report.json` | sprint score |
| phase exit gate | `quality/09-quality-gate.md` | category scores |

### 변경 — self_lint

- **C-CMJ 신규**: 컨벤션 본문 7 keyword 검증
- 101 → 102 checks. all_ok=True.

### 변경 — INDEX + README

- `conventions/INDEX.md` row 신규 (89 컨벤션)
- `theseus-harness/README.md` d-92 인덱스

### bump

- plugin.json / SKILL.md frontmatter: 0.9.34 → 0.9.35.

### 효과 (의도)

cold session attempt-2 (v0.9.33) 의 첫 pass *낙관적* 채점 (`tournament-01` u1 18/20 = 0.90, `tournament-02` 19.5 = 0.975) → mandatory rerun 1 회 후 즉시 종료 → polishing 0. 본 컨벤션 적용 시 :
- rerun=0 cap 0.90 → tournament-01 0.90 (정합) but improvement_axes_remaining ≥ 1 의무
- rerun=1 cap 0.95 → polishing 1 회 후 cap 도달
- rerun=2 cap 0.99 → 2 회 후 cap 도달
- rerun ≥ 3 + budget ≥ 80% 시만 0.999 허용 → *G4 임계 도달까지 자연스럽게 무한 회귀*

→ 외부 채점 92/100 → 95+ 도달 가능성 ↑.

## v0.9.34 — 2026-05-06 (sprint-29 — impl multiverse 의미 명확화 + plan-impl 격리 + 무한 회귀 phase 08 적용)

### 마일스톤

cold session attempt-2 (v0.9.33) 의 impl phase 회귀 정정. 외부 채점 92/100 으로 상승했으나 impl multiverse semantics 회귀 잔존 — agent 가 *impl universes = plan multiverse 의 손자* 로 오해 (`Universes 2/3/4 lost the plan tournament before code was written. The implementation tournament is by walkover.`).

### 변경 — `impl-multiverse-strict.md` 본문 정정

**의미 명확화 신규 절** : impl universes 는 *plan winner 의 코드 구현 변형* — plan multiverse 의 손자 *아님*.

| layer | 입력 | universe pool | 차원 |
|---|---|---|---|
| **plan multiverse** (06) | 사용자 의도 + 인터뷰 | 서로 다른 *설계 paradigm* | feasibility / invariant / decision_coverage / modular / determinism / measurement |
| **impl multiverse** (08) | **canonical `plan/06-plan.md` 만** | 서로 다른 *코드 구현 방식* (abstraction / library / TDD / pattern) | SOLID / dead-code / magic-number / reproducibility / portability / test coverage |

**격리 의무** :
- 입력 격리 — impl universes 는 canonical 06-plan.md 만 인용. plan/candidates/universe-N/ 본문 인용 금지
- 출력 격리 — impl universe ID 는 plan universe ID 와 *완전 독립*. plan winner 결정 후 plan multiverse 는 *이미 collapse*

### 변경 — 안티 패턴 3 신규 (e/f/g)

- **e** impl universes 가 plan multiverse 의 손자 (가장 빈번한 회귀): `walkover` / `lost the plan tournament before code was written` 패턴 차단. plan winner 결정 후 *NEW 4 universes* 로 fan-out
- **f** impl universe ID 가 plan universe ID 상속: `impl/candidates/universe-1/` = plan u1 코드 → 차단. NEW namespace 의무
- **g** mandatory ≥ 1 rerun 후 즉시 종료 (sprint-28 j 정합 phase 08 적용): "No further sprints required" 자백 → reject. budget 여유 + 임계 미달 시 *무한 회귀*

### 변경 — self_lint

- **C-IMS-SEMANTICS 신규**: 컨벤션 본문 8 keyword 검증 (impl multiverse 의미 / plan multiverse 의 손자 / 입력 격리 / 출력 격리 / lost the plan tournament / walkover / 상속 / 무한 회귀)
- 100 → 101 checks. all_ok=True.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.33 → 0.9.34.
- self_lint 101/101 PASS.

### cold session attempt-2 (v0.9.33) 점수

- 외부 채점 (zero-context Opus reviewer) **92/100**: Conceptual 19, Data 14, Sim 18, Experimental 13, Results 14, Code 9, Trace 5
- v0.9.33 sprint-28 효과 부분 발현 — plan dacapo 약간 개선. impl multiverse semantics 회귀 잔존 (본 sprint 정정 대상)
- 다음 v0.9.34 cold session 으로 본 sprint 효과 검증 권장

### 알려진 결손 (sprint-30+)

- v0.9.34 cold session 외부 검증
- 코드 블록 내 mining illustrative example 잔존 deep cleanup
- C-IDX-3 / C-IDX-4 활성화

## v0.9.33 — 2026-05-06 (sprint-28 — Da Capo "fresh universe" 의미 명확화 + 무한 회귀 + scoring granularity)

### 마일스톤

cold session 003 attempt-2 (v0.9.32) 의 Da Capo 회귀 정정. agent 가 "Round 2 = top-K 생존자 head-to-head" 로 Da Capo 를 오해하여 *survivors rerun* 으로 구현 (의도: NEW universes + lessons applied).

### 변경 — `intra-phase-dacapo-loop.md` 안티 패턴 5 신규 (g~k)

- **g- survivors rerun (가장 빈번한 회귀)** : Round N+1 = top-K 생존자 head-to-head 재가중 채점 → 차단. 올바른 Round N+1 = `[anonymized prev winner] + [width-1 NEW fresh universes]`.
- **h- dacapo-rerun-NN.md 역순 작성** : tournament-(NN+1).md *이후* 작성 시 NEW universe pool spec 의미 상실. 올바른 순서: tournament-NN → dacapo-rerun-NN → tournament-(NN+1).
- **i- fresh universe 가 재라벨링** : 본문이 Round N universe 본문과 semantic diff < 30% → fail. lesson_pack 적용 + framing 변경 의무.
- **j- max_rerun cap 으로 조기 종료** : 본 의사코드는 *budget cap 만*. max_rerun (G3=2/G4=3/G5=5) 는 *참고용 가드*. **budget 충분 시 임계 (G4=0.999/G5=0.99999) 도달까지 *무한 회귀***. 임계 미달 + budget 여유 + rerun >= max_rerun 인데 promote = 차단 (mandatory rerun ce 정합).
- **k- scoring granularity coarse** : `0-3 4 단계 정수` / `0-10 정수` 등 coarse rating 으로 6-dim weighted (cf plan-tournament-scoring-strict) 우회 → reject. 0.0-1.0 연속값 의무. `각 criterion 0–3` 패턴 자동 reject.

사용자 직접 지시 :
- "다른 다카포도 마찬가지로 의미 를 명확하게 레슨만 가중해서 다시 하는것"
- "0.9999 임계값 까지 재시도 무한회귀"
- "점수 스코어링의 디테일이 높고 정확해야함"

### 변경 — pseudocode comment 정정

`max_rerun = {G3: 2, G4: 3, G5: 5}[grade]` 줄에 *참고용 가드 (sprint-28 — budget 충분 시 임계 도달까지 무한 회귀, budget cap 만이 진짜 종료 조건)* 주석 추가.

### 변경 — self_lint

- **C-DCL-FRESH-UNIVERSE 신규** : 컨벤션 본문에 anti-pattern + fresh universe 정의 명시 검증 (6 keyword: C-DCL-FRESH-UNIVERSE / survivors rerun / 재라벨링 / 역순 작성 / 무한 회귀 / scoring granularity coarse).
- 99 → 100 checks. all_ok=True.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.32 → 0.9.33.
- self_lint 100/100 PASS.

### 알려진 결손 (sprint-29+)

- C-IDX-3 (phases 본문 cross-ref ⊆ INDEX applies-to-phases)
- C-IDX-4 (grades.md ↔ INDEX applies-to-grades 집계)
- 코드 블록 내 mining illustrative example 잔존 deep cleanup
- v0.9.33 cold session 외부 검증 — fresh universe 의미 발현 + 무한 회귀 작동 + 0.999 도달 시까지 polishing

## v0.9.32 — 2026-05-06 (sprint-27 — conventions frontmatter backfill (88) + C-IDX-2 drift detection)

### 마일스톤

**sprint-20 의 후속 deliverable** — 88 conventions/*.md 에 router metadata frontmatter 일괄 backfill. drift detection 자동화 (C-IDX-2).

### 변경 — 88 conventions frontmatter backfill

각 `conventions/<id>.md` 의 머리에 다음 frontmatter 박힘:

```yaml
---
id: <name>
category: <core|interview|mindmap|domain|planning|multiverse|tournament|impl|quality|sprint|meta>
applies-to-phases: '[<phase numbers> 또는 [all]]'
applies-to-grades: '[G2..G5] 또는 [all]'
trigger-when: '<always 또는 specific 조건>'
indexed-in: conventions/INDEX.md
---
```

router metadata 단일 source = `conventions/INDEX.md`. backfill 스크립트가 INDEX 를 파싱하여 각 파일에 박음.

### 변경 — self_lint

- **C1 정정**: convention 첫 줄 `# Title` 검사 시 leading YAML frontmatter (`--- ... ---`) skip 추가.
- **C-IDX-2 신규** (sprint-27 v0.9.32): conventions/*.md frontmatter ↔ INDEX drift detection :
  - 각 파일이 frontmatter 보유 의무
  - 의무 필드: id / category / applies-to-phases / applies-to-grades / trigger-when / indexed-in
  - frontmatter `id` 가 filename stem 과 일치 검증
  - INDEX 에 router row 부재 시 fail
- 총 98 → 99 checks. all_ok=True.

### 효과

drift 자동 차단 — 컨벤션 frontmatter 와 INDEX 가 미일치하면 self_lint fail. 미래 cleanup / 신규 컨벤션 추가 시 INDEX 와 sync 강제.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.31 → 0.9.32.
- self_lint 99/99 PASS.

### 알려진 결손 (sprint-28+)

- C-IDX-3 (페이즈 본문 cross-ref ⊆ INDEX applies-to-phases) — 페이즈 본문이 인용한 컨벤션이 router 매칭 검증
- C-IDX-4 (grades.md 매트릭스 ↔ INDEX applies-to-grades 집계 일치)
- 코드 블록 내 mining illustrative example 잔존

## v0.9.31 — 2026-05-06 (sprint-26 — temporal narrative + mining narrative deeper cleanup)

### 마일스톤

8 conventions 의 temporal 표현 (`본 회차 (v0.9.X)` / `v0.9.X 까지의` / `v0.9.X 부터`) + 잔존 mining narrative example 추가 cleanup.

### 변경 — 5 bulk regex 패턴

- `본 회차 \(v0\.9\.\d+(?:\s+[^)]+)?\)` → `본 회차` (self-application context 의 history label 제거)
- `v0\.9\.\d+ 까지의 ` → `이전 `
- `v0\.9\.\d+ 부터 ` → `현재 `
- mining-specific Q answer narrative example → generic placeholder
- "Q3 의 truck 답이..." → "Q3 의 답이..." (truck domain word strip in narrative)

### 8 파일 갱신

aide-tree-multi-phase / budget-aware-fallback / decision-support-framing / domain-research-stacking / intent-completeness / multiverse-impl-fan-out / score-rubric-objectivity / tournament-blind-rerun.

### 보존 (preserve)

- `vNN_cold (v0.9.X)` cold session ref (e.g., `v01_cold (v0.9.9)`) — design rationale evidence, *cleanup 대상 아님*
- 코드 블록 내 mining 예시 (illustrative algorithmic context)

### bump

- plugin.json / SKILL.md frontmatter: 0.9.30 → 0.9.31.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-27+)

- conventions/INDEX.md frontmatter backfill (88 conventions × router metadata) → C-IDX-2/3/4 활성화 (drift detection 자동화)
- 더 깊은 mining narrative deep cleanup (코드 블록 내 example 잔존)

## v0.9.30 — 2026-05-06 (sprint-25 — 도메인 narration generic 화 + HARD-RULE 9.d 신규 (Da Capo산출물 body 의무))

### 마일스톤

사용자 우선순위 (2)+(3) 통합 sprint. 도메인 종속 예시 generic 화 + Da Capo산출물 body 의무 강화.

### 변경 — HARD-RULE 9.d 신규 (Da Capo산출물 body 의무)

HARD-CORE.md HR9 + orchestrator/SKILL.md HR9 동시 갱신. **frontmatter (bn) 외 본문 의무 신규**:

- `tournament-NN.md` 본문: 6-dim sub-scores 표 + winner reasoning + cross-universe 차이집합
- `dacapo-rerun-NN.md` 본문: lesson 본문 + Step F-G (lesson 도출 + anonymized prev winner) detail
- `dacapo-flow.md`: bq 의무 (Mermaid + timeline + step trace per round)

HARD-CORE.md 3782 → 3969 chars (C-HC1 cap 4000 PASS).

### 변경 — 도메인 narration generic 화 (4 파일)

mining haul/SimPy 도메인-specific 예시를 generic 표현으로 치환:

- `decision-support-framing.md`: "8 트럭 vs 12 트럭" 의사결정 예시 → "<도메인-specific 결정 지원 예시>"
- `domain-research-stacking.md`: "truck|haul|haulage" / "loader|crush|crusher" / "ore|mining|pit" trigger regex → "<entity1>|<entity2>|..."
- `intent-completeness.md`: "truck capacity = 100t from data/trucks.csv" → "<entity> <attribute> = <value> from data/<entity>s.csv"
- `magic-number-traceability.md`: "A9: empty truck speed factor 1.0, loaded 0.85 — typical mining haul" → "A<N>: <물리 가정 예시 — industry default>"
- `domain-research-stacking.md`: "MTBF / availability < 1.0 / grade variation" → "<도메인 NFR 1> / <NFR 2> / <NFR 3>"

본 하네스에 *built-in 도메인 종속 예시 0* 정합 — 사용자 per-project 작성 시 generic placeholder 를 도메인 entity 로 치환.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.29 → 0.9.30.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-26+)

- 잔존 mining domain 키워드 (truck/loader/crusher) 가 여전히 일부 conventions 본문에 도메인 *언급* 수준으로 남아있음 — 본 sprint 는 *예시* / *trigger regex* / *가정 패턴* 만 generic 화. *비문법적* (in narrative) 사용 잔존
- temporal narrative ("v0.9.X 까지", "본 회차") 잔존 case-by-case cleanup
- conventions/INDEX.md frontmatter backfill (C-IDX-2/3/4 활성화)

## v0.9.29 — 2026-05-06 (sprint-24 — conventions inline body history label cleanup)

### 마일스톤

conventions docs 본문의 *standalone* parenthetical history label 일괄 제거. 10 conventions 의 inline label cleanup.

### 변경 — 3 bulk regex 패턴

- `\(v0\.9\.\d+ (?:신규|갱신|변경|단순화|cross-ref|정합)\)` → 제거
- `\(v0\.9\.\d+ sprint-\d+ ...\)` → 제거
- `\(sprint-\d+ ...\)` → 제거

10 파일 갱신: cross-universe-lesson-distillation, dacapo-enforcement, dacapo-frontmatter-schema, diagrams, directional-simplification, intent-refresh-post-interview, measurement-contract, mindmap-quality-gardening, polyglot-code-quality, rubric-targeted-quality-gates. 총 ~234 chars 제거.

### 보존 (intentional)

- `[X.md](X.md) (v0.9.X)` — convention citation metadata (현재 룰 조합, history 아님)
- `cold session XXX (v0.9.X)` evidence — design rationale (회귀 정정 증거)
- `본 회차 (v0.9.X)` self-application context — meta 적용 시점 명시 (case-by-case 더 위험)

### bump

- plugin.json / SKILL.md frontmatter: 0.9.28 → 0.9.29.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-25+)

- 21 conventions 도메인 narration (mining/SimPy/truck) generic 화 — case-by-case 신중
- plan/dacapo phase body 의무 강화 (HARD-RULE 9.a 8 항목 외 dacapo산출물 body)
- "본 회차 (v0.9.X)" / "v0.9.X 까지" 등 temporal narrative cleanup

## v0.9.28 — 2026-05-06 (sprint-23 — conventions docs header history cleanup)

### 마일스톤

phase docs (sprint-22) 와 동일 원칙을 conventions docs 에 적용. 7 conventions 의 header history label 일괄 cleanup.

### 변경 — conventions docs header label 제거 (7 파일)

bulk regex 2 패턴:

**Pattern 1** — `^## v0\.9\.\d+ sprint-\d+ ...` / `^## sprint-\d+ ...` / `^## v0\.9\.\d+ ...` 헤더 라벨 제거 (2 파일):
- `competition.md`, `resources.md`

**Pattern 2** — `^#{2,3} ... \(v0\.9\.\d+ ...\)` 헤더 후미 괄호 라벨 제거 (5 파일):
- `budget-saturation-loop.md`, `mindmap-quality-gardening.md`, `multiverse-impl-fan-out.md`, `resources.md`, `sub-agents.md`

### 보존 (non-history 인용)

- `[`X.md`](X.md) (v0.9.X)` — convention 인용 metadata (현재 룰 조합 표시, history 아님)
- `cold session XXX 회귀 정정` — evidence-driven design rationale
- 본문 inline `(v0.9.X 신규)` non-header 위치 — 후속 sprint 에서 case-by-case

### bump

- plugin.json / SKILL.md frontmatter: 0.9.27 → 0.9.28.
- self_lint 98/98 PASS.

### 알려진 결손 (sprint-24+ 후속)

- 88 conventions inline body history (parenthetical citations + temporal narratives) 더 깊은 cleanup
- 21 conventions 도메인 narration (mining/SimPy/truck) generic 화
- plan/dacapo phase body 의무 강화 (HARD-RULE 9.a 8 항목 외)

## v0.9.27 — 2026-05-06 (sprint-22 — phase docs deep history cleanup)

### 마일스톤

**스킬 / 컨벤션 본문에서 sprint/version history label 제거 — history 는 본 CHANGELOG 단일 위치 정합** (사용자 원칙: "히스토리는 스킬의 노이즈"). 8 phase 파일의 14 history header 일괄 cleanup.

### 변경 — phase docs header label 제거 (8 파일)

bulk regex 패턴 적용 (`^## v0\.9\.\d+ sprint-\d+ ...` / `^## sprint-\d+ ...` / `^## v0\.9\.\d+ ...` → 라벨 제거 후 룰 본문만 유지):

- `phases/01-intent.md` : `## v0.9.19 sprint-13 갱신 — 마인드맵 A 등급 default + intent sprint loop` → `## 마인드맵 A 등급 default + intent sprint loop`
- `phases/04-clarify.md` : `## v0.9.20 sprint-14 신규 — Q-D-AUDIENCE + rubric skeleton` → `## Q-D-AUDIENCE + rubric skeleton`
- `phases/05-critique.md` (2개) : `## sprint-19 — phase 05 종료 직후 mandatory 2nd refresh cycle` → `## phase 05 종료 직후 mandatory 2nd refresh cycle` / `## v0.9.20 sprint-14 — Directional Simplification 표 의무` → `## Directional Simplification 표 의무`
- `phases/06-plan.md` (4개) : v0.9.19~22 sprint-13~16 4 헤더 모두 제거
- `phases/07-plan-recursion.md` : `## v0.9.22 진입 의무 — Da Capo enforcement gate (HARD-RULE 9.p)` → `## 진입 의무 — Da Capo enforcement gate (HARD-RULE 9.p)`
- `phases/08-implement.md` : `## v0.9.22 sprint-16 Da Capo enforcement gate` → `## Da Capo enforcement gate`
- `phases/09-quality-gates.md` (3개) : `## sprint-18 신규 — 90→100 cap 풀기 (runtime 검증 layer)` → `## runtime 검증 layer (90→100 cap 풀기)` / `## 9 정적 게이트 + N derived 게이트 (v0.9.18)` → `## 9 정적 게이트 + N derived 게이트` / `## v0.9.20 sprint-14 — Rubric-Targeted Gates + 게이트 강화` → `## Rubric-Targeted Gates + 게이트 강화`
- `phases/10-test-loop.md` (2개) : `## v0.9.19 sprint-13 — Sprint Trinity 3 axis 분배` → `## Sprint Trinity 3 axis 분배` / `## v0.9.20 sprint-14 — Grader-in-Sprint Dual-Objective` → `## Grader-in-Sprint Dual-Objective`

### 변경 — self_lint history-agnostic

C-DCL-FLOW-LOG : `phases/08-implement.md` 의 `v0.9.22 sprint-16` 라벨 의존 제거. `Da Capo enforcement gate` keyword 만 검사 — history 라벨 cleanup 후에도 PASS.

### 알려진 결손 (sprint-23+ 후속)

- 88 컨벤션 본문 inline history narration cleanup (29 파일에 sprint-XX/v0.9.X 본문 라벨 잔존, 21 파일에 mining/SimPy 도메인 예시 잔존)
- plan/dacapo phase body 의무 강화 — HARD-RULE 9.a 8 항목 외에 dacapo산출물 (tournament.md / dacapo-rerun.md / dacapo-flow.md) body 의무 본문 강화

### bump

- plugin.json / SKILL.md frontmatter: 0.9.26 → 0.9.27.
- self_lint 98/98 PASS.

## v0.9.26 — 2026-05-06 (sprint-21 — HARD-RULE 9.a body 8 항목 강화 + 부분 history 정리)

### 마일스톤

**sprint-05-c 정공 재확인.** 사용자 직접 지시 — *별도 impl-design.md 신설 안 함* (plan + impl-log 응집 보존, plan 단일 source 강화). 초안 시도 (08-A doc cycle + 08-B code cycle 분화) 는 sprint-05-c 결정과 충돌하여 **즉시 폐기 + rollback** + 정공 (`HARD-RULE 9.a body 8 항목 강화`) 으로 전환.

### 변경 — HARD-RULE 9.a body 8 항목 의무

이전 (sprint-17): 5 항목 (파일 경로 ≥ 5 / Mermaid sequence + usecase + interface AND / TODO DAG)
sprint-21 강화 (8 항목 의무):
1. 파일 경로 ≥ 5
2. Mermaid sequenceDiagram ≥ 1 AND usecase/graph ≥ 1 AND 인터페이스 정의 ≥ 3
3. TODO DAG (T-NNN ID + 의존 + 완료 조건)
4. **모듈 의존 다이어그램** (per-module sequenceDiagram ≥ 모듈 수)
5. **Data structure invariants 표** (Invariants/Topology/Access/Bounds 4 항)
6. **Test surface mapping** (invariant ↔ test signature 1:1)
7. **Error handling / fallback policy** (모듈별)
8. **Implementation guidance per TODO** (알고리즘 / DS / 라이브러리 / pseudo-code — implementer 가 따라가는 디자인 본문)

→ plan 본문 풍부화 + impl 문서 sub-cycle 신설 0 (응집 보존). HARD-CORE.md HR9.a + orchestrator/SKILL.md HR9.a 동시 갱신.

### 부분 history narration 정리 (사용자 원칙 정합)

5 conventions 의 sprint/version 헤더 cleanup:
- `diagrams.md` : `## sprint-17 — HARD-RULE 9.a OR → AND` → `## HARD-RULE 9.a — sequence + usecase + interface 셋 다 의무 (AND clause)`
- `diagrams.md` : `## v0.9.19 sprint-13 — per-module fan-out` → `## per-module fan-out`
- `intent-completeness.md` : `## v0.9.19 sprint-13 갱신 — intent sprint loop trigger` → `## intent sprint loop trigger`
- `plan-tree.md` : `## v0.9.16 sprint-10 — 패배 universe 학습 전이` → `## 패배 universe 학습 전이`
- `grades.md` : `## v0.9.17 변경 — 키워드 매칭 폐기` → `## 키워드 매칭 폐기`

→ 5 헤더 sprint/version 라벨 제거 (history → CHANGELOG 단일 위치 정합). 88 컨벤션 본문 deep history 정리는 sprint-22+ 후속.

### 변경 — self_lint

C-DIAG-AND-COVERAGE keyword 갱신: `sprint-17` / `OR → AND` 라벨 의존 제거. 현재 룰 (`sequenceDiagram ≥ 1 AND` / `셋 다 의무`) 만 검사.

### 알려진 결손 (sprint-22 후속)

- 88 컨벤션 본문 deep history narration cleanup (21+ 파일에 mining/SimPy 등 도메인 예시 잔존, sprint-XX/v0.9.X 본문 라벨 잔존)
- plan/dacapo phase 분화 검토 (impl 은 sprint-05-c 정공으로 결론, plan/dacapo 도 동일 원칙 — 별도 sub-doc 신설 0, *body 의무 강화* 정공)

### bump

- plugin.json / SKILL.md frontmatter: 0.9.25 → 0.9.26.
- self_lint 98/98 PASS.

## v0.9.25 — 2026-05-06 (sprint-20 — 정보 아키텍처 재설계 + 도메인 어댑터 제거)

### 마일스톤

**`theseus-harness-slim-proposal.md` 수렴.** SKILL.md 비대화 (32280 chars / 88 컨벤션 카탈로그 누적) 를 *구조적 분리* (압축 X) 로 영구 정리. lazy-load 3 분류 (always-load / phase-scoped / router-matched).

### 변경 — 신규 산출물

- **`HARD-CORE.md`** (신규) — always-load supremacy 본문. ≤ 4000 chars (C-HC1 lint 부풀음 영구 차단). HR1 (첫 동작 4 금지) + HR8 (G1~G5 의무 산출물) + HR9.a~c 본문 의무 + Layer 3 H1~H5 + 페이즈 04 외 인터럽트 0 + frontmatter 핑거프린트 체인.
- **`conventions/INDEX.md`** (신규) — 88 컨벤션 router 단일 표 (id / cat / phases / grades / trigger). sprint/version 컬럼 부재 — history 는 본 CHANGELOG 만. C-IDX-1 lint 가 conventions/*.md ↔ INDEX row 1:1 매칭 검증.
- **`SKILL.md`** 슬림화 — 32280 → ~6700 chars (-79%). 인덱스 + phase lookup + agent 18 링크 + 채점기 / 템플릿 / 산출물 트리 / 그레이드. *카탈로그 나열 안 함*.

### 변경 — 도메인 어댑터 제거 (벤치 어뷰징 정리)

- 삭제: `conventions/domain-adapters/mining-haulage.md`, `conventions/domain-adapters/des-modeling.md`, 디렉터리.
- `conventions/domain-research-stacking.md` (aj) + `conventions/domain-failure-patterns.md` (ay) — 본문 도메인 종속 예시 제거. 프레임워크 보존 (사용자 per-project 어댑터).
- 본 하네스에 *built-in 도메인 어댑터 0* — `feedback_harness_strengthening_methodology` 정합.

### 변경 — self_lint

- 신규 2 룰: **C-HC1**, **C-IDX-1**.
- 기존 lint 갱신: C1 (INDEX.md 제외) / C2 (SKILL ∪ INDEX) / C-OD (HARD-CORE.md keyword) / C-IRPI (SKILL ∪ INDEX).
- 96 → 98 checks. all_ok=True.

### bump

- plugin.json / SKILL.md frontmatter: 0.9.24 → 0.9.25.

### 알려진 결손 (sprint-21 후보)

- **페이즈 fan-out**: intent 페이즈 (01→02→03 *문서화 / 콜드리뷰 / 판단* 분화) 와 달리 plan / impl / dacapo 는 페이즈 자체 미분화. 페이즈 06/08/dacapo 안에 *생성 / 콜드리뷰 / 판단* 분리 후 별도 페이즈 + 별도 에이전트.
- **convention frontmatter backfill**: 88 컨벤션 router 메타 박힘 + C-IDX-2/3/4 활성화.
- **컨벤션 본문 history narration 정리**: "sprint-NN 신규" / "v0.9.X" 류 본문 history 제거 (sprint-20 은 SKILL/INDEX 만).

## v0.9.24 — 2026-05-06 (sprint-19 — Da Capo runtime polishing + plan/impl richness + 2nd refresh cycle)

### 마일스톤
**cold session 003 (v0.9.23) 90/100 plateau 정정.** sprint-15~18 enforcement 의 마지막 빈 구멍 5 동시 닫음.

### 변경 — 6 컨벤션 신규 (ce~cj, HARD-RULE 9.gg~ll)

- `dacapo-mandatory-rerun.md` (ce, 9.gg) — winner ≥ 임계 도달해도 무조건 ≥ 1 rerun. C-DCMR.
- `plan-tournament-scoring-strict.md` (cf, 9.hh) — tournament 6-dim weighted, 1-5 cold-read coarse reject. C-PTSS.
- `canonical-not-stub.md` (cg, 9.ii) — canonical ≥ winner 80% inline 또는 shared schema. C-CNS.
- `impl-multiverse-strict.md` (ch, 9.jj) — phase 08 G4+ 7 조건 게이트. skip 자백 reject. C-IMS.
- `intent-refresh-post-critique.md` (ci, 9.kk) — phase 05 → 06 사이 2nd intent refresh + 04/05 cascade. C-IRPC.
- `cross-phase-shared-context.md` (cj, 9.ll) — shared 정보 단일 위치 + asof_fingerprint drift 차단. C-CPSC.

### bump
- plugin.json: 0.9.23 → 0.9.24. self_lint 90 → 96 checks.

## v0.9.23 — 2026-05-05 (sprint-17+18 — orchestrator 슬림화 + intent-refresh + cap 측정-only + runtime enforcement 5)

### 마일스톤
**cold session 002 + 003 회귀 다발 정정.** orchestrator 287→121 lines (-58%) + 6 신규 컨벤션 (by~cd) + 9 신규 self_lint.

### sprint-17 (orchestrator 구조 정정)

- `intent-refresh-post-interview.md` (by) — phase 04 → 05 사이 의도 refresh 4 framing universe + 01-additional. C-IRPI.
- orchestrator/SKILL.md 287→121 lines (HARD-RULE 9.a~aa prose 분리).
- `dacapo-enforcement.md` (bm) — 시간 cap 측정 only. forward projection regex reject. min loop attempt rerun ≥ 1. C-DCL-NO-FORWARD-PROJECT/MIN-LOOP-ATTEMPT/CAP-MEASURED.
- `diagrams.md` (c) + HARD-RULE 9.a — OR → AND. C-DIAG-AND-COVERAGE.

### sprint-18 (runtime enforcement 5, 도메인 무관)

- `readme-numbers-from-summary.md` (bz, 9.bb), `reproducibility-doublecheck.md` (ca, 9.cc), `magic-number-traceability.md` (cb, 9.dd), `dead-code-zero.md` (cc, 9.ee), `submission-portability.md` (cd, 9.ff). C-RNFS / C-RDC / C-MNT / C-DCZ / C-SPB.
- 도메인 종속 룰 (transient-state-justification 등) 의도적 제외.

### bump
- plugin.json: 0.9.22 → 0.9.23. self_lint 81 → 90 checks.

## v0.9.22 — 2026-05-05 (sprint-16 — 의사코드 → runtime guard 변환 + 7 차원 만점 push)

### 마일스톤
**cold session winner=0.892 + rerun=0 + fallback="" 회귀 정정.** 12 신규 컨벤션 (bm~bx) + HARD-RULE 9.p~aa.

### Phase 1 enforcement layer (bm~br, 9.p~u)
- `dacapo-enforcement.md` (bm), `dacapo-frontmatter-schema.md` (bn), `shadow-grader-zero-context.md` (bo), `dacapo-skip-sentinel.md` (bp), `dacapo-flow-trace.md` (bq), `phase-lineage-viewer.md` (br).

### Phase 2 7 차원 만점 push (bs~bx, 9.v~aa)
- `domain-model-completeness.md` (bs), `data-structure-invariants.md` (bt), `simulation-physical-invariants.md` (bu), `experimental-control-protocol.md` (bv), `results-decision-mapping.md` (bw), `idiomatic-code-quality.md` (bx).

### bump
- plugin.json: 0.9.21 → 0.9.22. self_lint 12 신규.

## v0.9.21 — 2026-05-05 (sprint-15 — intra-phase Da Capo Loop 의사코드 hook)

### 마일스톤
**multiverse + sprint retry 통합** — phase 06 (plan) + phase 08 (impl) 안에 통합 의사코드 loop (Step A~G 다카포). cold session winner=0.853 (G4 임계 미달) 재경합 0 회 회귀 정정.

### 변경 — 1 컨벤션 신규 (bl, HARD-RULE 9.o)
- `intra-phase-dacapo-loop.md` (bl, 9.o) — Step A multiverse fan-out → B tournament → C shadow grade → D 4-conjunction AND threshold → E cap → F lesson + winner 갱신 → G anonymized prev winner + width-1 fresh → A 재진입. self_lint C-DCL-WIN-THRESHOLD/RERUN-LOG/ANON 3 신규.

### bump
- plugin.json: 0.9.20 → 0.9.21.

## v0.9.20 — 2026-05-05 (sprint-14 — cold evaluator feedback 7 컨벤션, 94→97 plateau 돌파)

### 마일스톤
**cold session 자체 90 vs 외부 grader 97 의 7pt 갭 정정.** 7 컨벤션 신규 (be~bk) + HARD-RULE 9.h~n.

### 변경 — 7 컨벤션 신규
- `grader-in-sprint.md` (be, 9.h), `contested-decision-multiverse.md` (bf, 9.i), `directional-simplification.md` (bg, 9.j), `commentary-policy.md` (bh, 9.k), `measurement-contract.md` (bi, 9.l), `rubric-driven-doc-skeleton.md` (bj, 9.m), `rubric-targeted-quality-gates.md` (bk, 9.n).

### bump
- plugin.json: 0.9.19 → 0.9.20.

## v0.9.19 — 2026-05-05 (sprint-13 — 깊이 강화 + 발현 빈도 격상 4 컨벤션)

### 마일스톤

**v0.9.18 sprint-12 발현 강제 메커니즘 도입 후 사용자 진단 7 항목 (2026-05-05) — 마인드맵 풍부화 / 다이어그램 모듈별 분할 / 유니버스 폭 증량 / plan·impl 디테일 향상 / intent·plan·impl 3 axis sprint loop / 0.999 지향 2회 이상 무한 / 전체 시간 cap.** v0.9.18 까지의 *룰 본문 작성* 면 진전 후, 본 sprint-13 = *발현 default 격상* 단계. 자기 적용 self-eating dogfood — 본 sprint 의 산출물 자체가 v0.9.19 신규 컨벤션 4 의 자기 적용 사례.

### 변경 — 4 컨벤션 신규 (ba~bd)

- **`mindmap-richness-default.md`** (ba) — 페이즈 01 §9 마인드맵 A 등급 default 격상 (≥25 노드 / 4 axis × ≥4 sub / 3 axis sub-sub + 1 axis sub-sub-sub). intent-extractor 프롬프트 templated stub 의무. B fallback PASS *with lesson*. C-MRD-A-DEFAULT self_lint. v0.9.13 mindmap-quality-gardening 의 *A 옵션* → *A default* 격상.
- **`per-module-diagram-fan-out.md`** (bb) — use-case / sequence 다이어그램 모듈별 분할 default. 트리거: 모듈 ≥ 4 OR consumer-producer 페어 ≥ 6. 모듈 ≤ 3 시 단일 통합 OK. C-PMDF self_lint. v0.9.6 diagrams.md 의 *negative anti-pattern* → *positive default* 격상.
- **`multiverse-width-default-bump.md`** (bc) — 폭 default 격상: G2=2 / G3=5 / G4=7 / G5=9. 옵션 default (사용자 명시 ack): G3=10 / G4=12 / G5=16. budget profile cap 동기 갱신 (resources.md universe parallel cap G3=10/G4=12/G5=16). budget tight 시 fallback 폭 + `fallback_reason` frontmatter 의무. C-MWDB self_lint. sprint-05-b의 *폭 3/4/6 plateau* 격상.
- **`intent-plan-impl-sprint-trinity.md`** (bd) — sprint loop 3 axis (intent / plan / impl) × 각 ≥ 2 회. budget 분배 default: intent 20% / plan 30% / impl 50%. 임계 0.999 default (모든 그레이드 G2~G4 / G5 = 0.99999 보존). early stop violation = (axis 별 < 2) OR (budget < 80%). C-IPI self_lint. v0.9.8 sprint-regression-loop + v0.9.15 budget-saturation-loop 의 *impl 단위만 axis* → *3 axis trinity* 확장.

### 변경 — 6 컨벤션 갱신

- `mindmap-quality-gardening.md` (ak) — Quality 등급 표 A default 격상 + B fallback PASS with lesson + ba cross-ref
- `plan-tree.md` (u) — 그레이드 폭 매트릭스 갱신 (G3=5 / G4=7 / G5=9 + 옵션 default) + bc cross-ref
- `multiverse-impl-fan-out.md` (ag) — 그레이드별 universe 수 sync + bc cross-ref
- `diagrams.md` (c) — 안티 패턴 d/e 추가 (모듈 ≥ 4 단일 시퀀스 + 모듈 ≤ 3 over-fragmentation) + bb cross-ref
- `budget-saturation-loop.md` (an) — `should_continue_sprint` axis 별 sprint < 2 시 무조건 추가 + Soft-converge handoff `sprint_axis_counts` 의무 + bd cross-ref
- `intent-completeness.md` (aw) — intent sprint loop trigger (§k 9 sub PASS 라도 ≥ 2 회 polish) + bd cross-ref
- `resources.md` — universe parallel cap 갱신 (G3=10/G4=12/G5=16) + wall-clock budget per universe 갱신

### 변경 — 4 페이즈 갱신

- `phases/01-intent.md` — `v0.9.19 sprint-13 갱신` 섹션 + ba A default + bd intent sprint loop + Templated Section §9 (universe-2 merge — 발현 강제)
- `phases/06-plan.md` — `v0.9.19 sprint-13 갱신` 섹션 + bc 폭 default 5/7/9 + bb per-module 다이어그램 + bd plan sprint loop + Templated per-module section
- `phases/08-implement.md` — `v0.9.19 sprint-13 갱신` 섹션 + bb universe-N 별 use-case 분리 + bd impl sprint loop + 폭 default sync
- `phases/10-test-loop.md` — sprint trinity 3 axis 분배 + Templated report.json schema + early_stop_violation 강화

### 변경 — HARD-RULE 9 (orchestrator/SKILL.md)

기존 9.a/b/c (산출물 *내용* 의무) 에 d/e/f/g 4 항목 추가 (산출물 *발현 빈도* 강제):
- 9.d: 마인드맵 풍성도 (mindmap_quality_grade ∈ [A, B] 만 PASS)
- 9.e: per-module 다이어그램 (모듈 ≥ 4 트리거)
- 9.f: multiverse 폭 default (G3=5/G4=7/G5=9)
- 9.g: sprint trinity (axis 별 ≥ 2 sprint)

### 변경 — version bump

- plugin.json / marketplace.json / harness SKILL.md / orchestrator SKILL.md frontmatter: 0.9.18 → 0.9.19
- 컨벤션 카탈로그 51 → 55 (4 신규 ba~bd)

### 검증

- 본 sprint 자체가 v0.9.19 self-eating dogfood:
  - 마인드맵 36 노드 A 등급 (frontmatter mindmap_quality_grade=A) — ba 자기 적용
  - 5 모듈 per-module use-case 다이어그램 분할 — bb 자기 적용 (모듈 ≥ 4 트리거 충족)
  - plan-tree 폭 4 universe (G4 default 7 의 budget-aware fallback, fallback_reason 명시) — bc 자기 적용
  - sprint trinity intent 2 + plan 2 + impl 2 = 6 sprint — bd 자기 적용
- 산출물: `.ShipofTheseus/theseus_self_v0919/` 트리 (timing/start.json, naming/00-naming.md, intent/01-intent.md ~ 05-decisions.md, plan/{tournament.md, 06-plan.md, 07-plan-review.md, candidates/universe-{1..4}/}, impl/08-impl-log.md, sprints/{intent,plan,impl}-{01,02}/, quality/09-quality-gate.md, handoff/14-handoff.md)

### 후속

- v0.9.19 적용 cold session — 4 신규 컨벤션 발현 검증 (mindmap A 등급 / per-module 다이어그램 / 폭 default 5+ / sprint trinity ≥ 6) + 점수 변화 측정
- intent-extractor 프롬프트 templated mindmap stub 적용 효과 측정 (v0.9.18 sprint-12 의 §k 9 sub 발현 강제 패턴 계승)
- 폭 default 격상 (G3=5/G4=7) 의 budget profile cap 충돌 모니터링 — fallback_reason 빈도 추적

---

## v0.9.18 — 2026-05-04 (sprint-12 — 본 스킬 자체 가치 개선 4 컨벤션 + 발현 강제 메커니즘)

### 마일스톤

**v0.9.17 cold session (`001-mine-throughput-theseus`) 검토에서 *준비-vs-동작* 갭 재발견 — 마인드맵 ASCII 회귀 + §i NFR / §j grade signals / §k 9 sub 모두 미발현.** 사용자 진단: "**제안은 스킬 개선인가 스코어링 개선인가**" (분리 명확화) → "**외부 의존 없는 단일 스킬로서 가치만 개선**" (E reviewer-form alignment 제외). 4 컨벤션 신규 + 발현 강제 메커니즘 (intent-extractor 프롬프트 강화 + 페이즈 진입 거부) 동시 박음.

### 변경 — 4 컨벤션 신규

- **`intent-completeness.md`** (A) — 페이즈 01 의도 §k 9 sub-criterion 의무: system boundary / entities / resources / events / state variables / assumptions / **limitations** / performance measures / **data-derived vs introduced 분리**. v0915-cold01 외부 채점 -2pt (Conceptual) 직접 매핑.
- **`process-flow-coherence.md`** (B) — 페이즈 09 게이트 8 신규: cycle / state machine / workflow / DES / pipeline / transaction 정합 자기 검증. all_states_reachable / cycle_invariant / orphan_states / error_paths_explicit / state_visit_count > 0. `process_flow_applicable: false` 시 skip.
- **`domain-failure-patterns.md`** (C) — 페이즈 09 게이트 9 신규: domain-adapters/<domain>.md 의 `failure_patterns:` 자동 검증. severity (cap_total / cap_correctness / cap_experimental / cap_results / warning) 별 점수 cap. v0.9.16 regression-derived-lint-rule-autogen 와 우로보로스 정합.
- **`decision-support-framing.md`** (D) — 페이즈 14 handoff 의 결정 질문 (Q1~QN) 마다 *operational implications + trade-off framing + opportunity-cost* 본문 의무. evidence_decision_support 매핑.

### 변경 — 도메인 어댑터 failure_patterns 항목 신규

- `domain-adapters/des-modeling.md` — DFP-DES-1~7 (static calc / no replications / hard-coded / queue without resource / credit at start / per-direction Resource / global RNG)
- `domain-adapters/mining-haulage.md` — DFP-MH-1~5 (no saturation / bottleneck without composite / no capex / per-direction ramp / availability=1.0 무명시)

### 변경 — 발현 강제 메커니즘 (사용자 핵심 요구)

**룰 작성만으로는 부족** — v0.9.13 mindmap-quality-gardening / v0.9.6 nfr-derivation 모두 cold session 에서 발현 0 였음. 본 sprint 가 발현 강제 메커니즘 동시 박음:

- **`agents/intent-extractor.md` 프롬프트 전면 재작성** — 11 단계 의무 순서 + §k 9 sub *templated section* + 마인드맵 *Mermaid block 의무* (ASCII text tree 금지) + §j grade signals 두 산출물 + frontmatter `applied_conventions` 자동 박음 + 하드 룰 (§k / §j 누락 = 페이즈 02 / Q-G1 진입 거부)
- **페이즈 09 본문 9 게이트** (기존 7 → 9): 게이트 8 cycle coherence + 게이트 9 domain failure patterns
- **페이즈 14 본문 §j Decision-support framing 의무**

### 변경 — self_lint 룰 신규 4

C-IC / C-PFC / C-DFP / C-DSF — 4 컨벤션 본문 + cross-ref 검증

### 변경 — 컨벤션 51 누계

47 (v0.9.16) + anti-patterns + 4 (v0.9.18) = 51. SKILL.md 컨벤션 카탈로그 표 av (anti-patterns) + aw~az (sprint-12 4) 추가.

### 변경 — version bump

- plugin.json / marketplace.json / harness SKILL.md / orchestrator SKILL.md frontmatter: 0.9.17 → 0.9.18
- SKILL.md fragmentation 정리 (14361 → 14001 chars, C26 PASS) — 컨벤션 description / 페이즈 표 셀 압축

### 검증

- self_lint 69/69 PASS (all_ok=True, lint_score=1.0)
- pytest 109/109 PASS, 회귀 0
- v0915-cold01 retro 적용 시 Conceptual 18 → 19~20 (limitations + data-derived 분리) / Sim 18 → 19 (cycle coherence) / Results 14 → 15 (decision-support framing) — 추정 +3~4pt

### 후속

- v0.9.18 적용 cold session — Mermaid 마인드맵 + §i/§j/§k 모두 발현 검증 + 점수 변화 측정
- *발현 강제 메커니즘* 의 효과 측정 — v0.9.13 mindmap-quality-gardening 처럼 룰만 박고 발현 0 가 반복되지 않는지

---

## v0.9.17 — 2026-05-04 (sprint-11 — 키워드 매칭 폐기 + 페이즈 01 다중 신호 grade 추정 + default G4)

### 마일스톤

**v0.9.16 cold02 (synthetic_mine_throughput_v0915_cold02) 가 자동 G3 으로 떨어진 결손 정정.** 사용자 진단 — "그레이드 판단이 키워드 기반인 것 부터 잘못. intent 페이즈 자체가 grade 분류와 강결합. 마인드맵 복잡도는 한 차원일 뿐. 최대한 많은 지표로 판단. default G4-G5".

### 변경 — `grade_assess.py` 전면 재작성 (v2)

- **키워드 매칭 알고리즘 폐기** — `TRIGGERS_G5/G4/G2/G1` 키워드 set 전부 제거. 사용자 원문 키워드는 도메인 어휘 추적 못함 (cold02 = simulation-bench 작업이 default G3 으로 떨어진 직접 원인)
- **`GradeSignals` dataclass — 18+ 차원 다중 신호** 페이즈 01 의도 §a~§i + 마인드맵 모든 섹션:
  - 마인드맵: node_count / axis_count / max_depth / external_systems / domain_nouns
  - 의도 §a: observable_results_count
  - §c: explicit_non_goals_count
  - §d: constraint_count / explicit_thresholds_count
  - §e: domain_term_count
  - §f: stakeholder_count
  - §g: success_metric_count / measured_metrics_count
  - §h: open_question_count
  - §i: derived_nfr_count / qualitative_adjective_count
  - boolean: multi_scenario / external_evaluator / fe_be_split / safety_critical / irreversible_change
  - integer: refactor_scope_module_count
- **default = G4** — 본 하네스 호출 자체가 G4+ 의도 신호. G3 작업은 본 하네스 없이도 진행 가능
- **G5 상향** = `safety_critical` 또는 `irreversible_change` 사용자 *명시 ack* 만. 자율 키워드 매칭 0
- **G3 하향** = 12 차원 모두 negative + `mindmap_node_count ≥ 1` (positive evidence) — *데이터 부재 ≠ 단순함*
- **G2 하향** = G3 + nodes ≤5 + 단일 모듈 + 단일 도메인 용어
- **호출 시점 변경** — 호출 직후 사용자 원문 → 페이즈 01 (의도 + 마인드맵) 완료 후. intent-extractor 가 페이즈 01 산출물 작성 시 부산물로 `intent/01-grade-signals.json` + `intent/01-mindmap-signals.json` 박음

### 변경 — `conventions/grades.md`

- 키워드 매칭 알고리즘 절 (line 24-69) 전부 제거 → 다중 신호 카탈로그 표 신규
- default = G4 명시
- G3 = "본 하네스 가치 부분만 활용 — G3 작업은 본 하네스 없이도 진행 가능" 명시
- 5 차원 escalation triggers 카탈로그 + 12 차원 단순 증명 룰 명시

### 변경 — `phases/01-intent.md`

§j Grade signals 산출 단계 신규 — intent-extractor 가 §a~§i + 마인드맵을 18+ 차원 신호로 추출. 성공 기준 §e 추가 (산출물 박힘 검증).

### 변경 — `phases/04-clarify.md`

Q-G1 본문 정정 — `grade_assess.py` 가 `intent/01-grade-signals.json` + `intent/01-mindmap-signals.json` 입력으로 추정. default G4 명시 + escalation triggers 매칭 list / 단순 증명 차원 두괄식 표시 + G3·G2 하향 시 사용자 ack 의무 명시.

### 변경 — self_lint 룰 신규

`C-GAv2` (v0.9.17 sprint-11) — grade_assess v2 검증:
1. 폐기 키워드 set (`TRIGGERS_G5/G4/G2/G1`) 잔존 0
2. 다중 신호 dataclass (`GradeSignals`) + escalation triggers + 단순 증명 + default_was 본문 보유
3. grades.md 의 default G4 + 키워드 매칭 폐기 명시 + 18+ 신호 카탈로그
4. phase 01 §j 산출물 의무
5. phase 04 Q-G1 default G4 명시

### 변경 — `test_grade_assess.py` 전면 재작성

기존 13 test 모두 `--request <text>` 키워드 인터페이스 가정. 14 신규 test (다중 신호 인터페이스):
- default G4 (no signals / empty signals)
- G5 명시 ack (safety_critical / irreversible_change)
- G3 단순 증명 / G2 trivial 증명
- escalation triggers 매칭 (external_evaluator / measured / multi-scenario / fe_be / domain_adapter)
- 키워드 매칭 폐기 검증
- user_confirmation always True / 5 보기 항상 / G1 진행 보존 / signals_used echo

### 검증

- self_lint 69/69 PASS (all_ok=True, lint_score=1.0)
- pytest 109/109 PASS (이전 11 fail = 키워드 인터페이스 호환성 — 재작성으로 해소)
- cold02 retro 적용 시 자동 G4 (escalation triggers 5 차원 매칭) — 임계 0.999 + 14 페이즈 풀 + 멀티버스 폭 4 활성

### 후속

- v0.9.17 적용 cold session — cold02 대비 점수 변화 측정 (G3 → G4 임계 강화 효과 검증)

---

## v0.9.16 — 2026-05-04 (sprint-10 — 발현 검증 6 메타 컨벤션)

### 마일스톤

**v0915-cold01 외부 채점 93/100 진단 후 *준비-vs-동작* 갭 정정.** 자체 추정 == 외부 채점 (둘 다 93) 으로 score-rubric-objectivity 발현 PASS, 그러나 94 plateau 안 깨짐. 사용자 피드백: "준비한 부분이 *구동 안 됨* / *제대로 동작 안 함* / 코드 퀄리티 점수 극복" 3 가설 + *케이스 종속 룰 금지, 제너럴 메타 룰만*. 본 sprint 가 6 메타 컨벤션 동시 신규.

### 변경 — 발현 검증 #1 `convention-traceability.md`

페이즈 산출물 frontmatter `applied_conventions: [...]` 의무 + 페이즈별 *expected* 컨벤션 카탈로그 (contracts.md). 회차 종료 시 zero-applied 컨벤션이 expected 와 교집합 = self_lint fail. 본 하네스 41+ 컨벤션 중 *어느 것이 실제로 발현됐는지 추적 메커니즘* 0 → 검출 가능.

### 변경 — 발현 검증 #2 `sprint-score-delta-tracking.md`

매 sprint NN+1 의 score - sprint NN 의 score = delta. EXPECTED_DELTA 범위 (content_depth 0.005~0.030 / enforcement 0.000~0.005 / etc.) 위반 시 `LABEL_VIOLATION` self_lint fail. budget-saturation-loop 의 lesson type 4 분류가 *honest* 인지 사후 측정.

### 변경 — 발현 검증 #3 `evidence-driven-sprint-planning.md`

handoff 의 `evidence_missing` 항목 → 다음 sprint 의 `next_sprint_candidates` 자동 생성. `free_lesson_allowed: false` — agent 가 *자유롭게* lesson 못 정함, evidence_missing / zero_applied / bench_required 중에서만. budget-saturation-loop + score-rubric-objectivity 의 *결손 → 보강* 자동 흐름.

### 변경 — 발현 검증 #4 `cross-universe-lesson-distillation.md`

Tournament resolve 시 패배 universe 의 *핵심 약점 ≥ 1-2 줄* 을 우승 본문 (Patterns to Avoid 절) 흡수 의무. 페이즈 08 / 10 가 `avoid_patterns` 입력 받음 → forbidden_strategies 동급 처리. ensemble-synthesis-default 의 *합집합* 차원이 *합집합 + 교집합 + 차이집합* 으로 격상.

### 변경 — 발현 검증 #5 `regression-derived-lint-rule-autogen.md`

페이즈 11 회귀 4 분류 정정 commit 시 *동일 차원 회귀 차단 self_lint 룰 신규* 의무. `lint_rule_proposal` frontmatter + `regression_lint_registry.py` 등록. self_lint CHECKS 가 정적 + 동적 합성 — 회귀 학습이 *영구 자산화*. 본 하네스 *우로보로스 자기 강화* 메커니즘화.

### 변경 — 발현 검증 #6 `polyglot-code-quality.md`

build-and-config §8 ruff 통합 = Python 전용 → 9 언어 카탈로그 (Python ruff / Go golangci-lint / TS biome / Rust clippy / Java checkstyle / Ruby rubocop / C/C++ clang-tidy / Kotlin detekt) + 6 메트릭 (cyclomatic / function_length / nesting_depth / duplicate_blocks / lint_errors / format_diff). v1.0 외부 maintainer 채택 prerequisite 인프라.

### 변경 — self_lint 6 룰 신규

C-CT / C-SDT / C-EDP / C-CULD / C-RDLR / C-PCQ. 각 컨벤션 본문 키워드 + cross-reference 검증.

### v0915-cold01 외부 채점 분석 (motivation)

| 차원 | 점수 | 만점 | 갭 |
|---|:-:|:-:|:-:|
| Conceptual | 18 | 20 | -2 |
| Sim correctness | 18 | 20 | -2 |
| Data·topology | 14 | 15 | -1 |
| Results | 14 | 15 | -1 |
| Code quality | 9 | 10 | -1 |
| Experimental design | 15 | 15 | 0 |
| Traceability | 5 | 5 | 0 |
| **Total** | **93** | **100** | **-7** |

자동 검증 53/53 PASS. 자체 추정 == 외부 채점 = score-rubric-objectivity 정직성 검증.

### 거부 (case-specific 후보)

초기 4 후보 (Conceptual narrative quantitative gate / Sim correctness analytical-bound proof / Results decision-support enforcement / Code quality micro layer) **거부** — bench rubric 항목 (sensitivity matrix / capex / opportunity-cost / type hints) 에 매여 케이스 종속. 메모리 `feedback_harness_strengthening_methodology.md` 위반.

### 검증

self_lint 6 룰 신규 모두 PASS / pytest 회귀 0 / self_score 1.0 / 임계 0.99999 통과. C26 (SKILL.md 길이) + C41 (description 압축) = pre-existing.

### 후속

- v0.9.16 적용 cold session — 진짜 0.999 도달 검증 (94 plateau 돌파)
- C26 정리 — SKILL.md 의 47 컨벤션 인덱스를 별도 INDEX 파일로 fragmentation
- C41 정리 — description 추가 압축

---

## v0.9.15 — 2026-05-04 (sprint-09 — budget saturation + rubric objectivity)

### 마일스톤

**94 plateau 돌파 룰** — v01_cold (v0.9.9) / v091_cold01 (v0.9.12) / v0914_cold01 (v0.9.14) cold session 모두 자체 추정 94 도달. 분석 결과 *조기 종료* + *generous self-rating* 두 noise 가 plateau 의 실 원인. 본 sprint-09 가 두 차원 동시 정정.

### 변경 — `conventions/budget-saturation-loop.md` 신규

페이즈 10 sprint loop 룰 정정:
- **임계 default = 0.999** (G3/G4 통일, G5 = 0.99999 유지)
- **Budget 사용률 ≥ 80% 강제** — 임계 first-try PASS 해도 sprint 추가
- 추가 sprint 의 lesson type = **content depth** (enforcement 아님) — Conceptual narrative / Results decision support / Sim cross-validation 의 *질적 layer*
- handoff frontmatter `budget_saturation: <ratio>` 명시 의무, 80% 미달 종료 = `EARLY_STOP_VIOLATION` self_lint fail
- 페이즈 04 신규 답안 `Q-D-BUDGET-MODE` (1=Saturation default / 2=Quick-stop / 3=Custom)

cold session retro 적용 시 v091_cold01 (28% 사용) / v0914_cold01 (21% 사용) 모두 +5-6 sprint 가능 → 추정 94 → 96-98.

### 변경 — `conventions/score-rubric-objectivity.md` 신규

페이즈 14 handoff 의 self-estimate 를 *체크리스트 evidence 1:1 매칭* 으로 강제:
- 8 차원 strict checklist 카탈로그 (Conceptual 20 / Sim correctness 20 / Data·topology 15 / Experimental 15 / Results 15 / Code quality 10 / Traceability 5 / Efficiency bonus)
- 각 차원 만점 미달 시 `evidence_missing` 명시 의무 — 어느 항목이 누락인지 evidence 단위로
- handoff frontmatter `self_estimate.type` (bench_rubric / internal_aggregate) 분리 — v0913_cold01 의 0.999 보고 패턴 (internal aggregate 만 보고) 차단
- self_lint C-SRO — type / evidence_paths / evidence_missing / rubric_version 4 항목 검증

retro 적용 시 v01_cold (v0.9.9) self-estimate 97 → strict 94 (-3pt generous noise 제거). 진짜 plateau = 92~94 명확화.

### 두 컨벤션 시너지

- saturation loop = budget *quantity* (sprint 횟수)
- objective rubric = score *quality* (정확도 / 신뢰도)
- 합성 시 매 sprint 후 `evidence_missing` 추적 → next sprint 가 채움 → 진짜 0.999 도달

### 검증

self_lint 룰 +2 (C-BSL / C-SRO) 신규 / pytest 회귀 0 / self_score 1.0 / 임계 0.99999 통과

---

## v0.9.14 — 2026-05-04 (sprint-08 — deliverable hurdle supremacy)

### 마일스톤

**Layer 3 결과물 허들 supremacy** — v0913_cold01 의 design-only 종료 (코드 0, 5 bench 의무 산출물 0, 실 실행 0) 가 메모리 룰 (`feedback_harness_scope.md` "코드 = 외부 repo only") 의 *literal 적용* 으로 발생. 본 sprint 가 *룰 우선순위* 재정의.

### 변경 — `conventions/deliverable-hurdle-supremacy.md` 신규

룰 precedence 3 layer:
- **Layer 1**: 메모리 feedback (사용자 사전 위임 / 관찰)
- **Layer 2**: 하네스 컨벤션 (페이즈 룰 / 게이트 / multiverse / etc.)
- **Layer 3**: 결과물 허들 — 실행 가능 제품 + 코드 + 측정값

**Layer 3 가 Layer 1/2 무조건 override.** 5 hard hurdle:
- H1 Code Existence (≥ N 모듈 default 5)
- H2 Code Execution (verification command exit 0)
- H3 Test Suite (실 측정 통과 수, 0 금지)
- H4 Bench-Required Outputs (file existence + size > 0 + schema 정합)
- H5 Executed Values Recording (placeholder 금지, primary metric non-zero finite in expected range)

허들 실패 시 *자동 retry sprint* — graceful skip / design-only handoff 금지. 사용자 *명시 ack* (페이즈 04 Q-D-DELIVERABLE-MODE = 3) 만 면제.

### 변경 — 메모리 룰 정정

`feedback_harness_scope.md` 의 *literal* "코드 = 외부 repo only" → *standalone 컨텍스트 시* 코드 + 실행 + 측정값 의무. 침습 가드는 *사용자 기존 repo 의 무관 코드 침습 금지* 만 유지.

### 그레이드별 활성

| Grade | 결과물 허들 |
|---|---|
| G1-G2 | optional |
| G3 | 의무 (standalone default) |
| G4 | 의무 + retry budget tighter (bench / external evaluator) |
| G5 | 의무 + 사용자 명시 ack 강제 (Q-D-DELIVERABLE-MODE = 1 만 OK) |

### 검증

self_lint 룰 +1 (C-DHS) / pytest 12/12 / self_score 1.0 / v0914_cold01 cold session 18.5 min 5/5 산출물 real PASS — 본 sprint 효과 외부 검증.

---

## v0.9.13 — 2026-05-04 (sprint-07 — content depth layer × 4)

### 마일스톤

94 plateau 1차 분석 — Conceptual / Sim correctness / Results 3 차원의 *content depth* 가 sub-score gap. enforcement 강화 (v0.9.6-12) 만으로는 깨지지 않음. 4 컨벤션이 *content layer* 추가.

### 변경 4건

- `conventions/deep-semantic-intent.md` — adjective + noun 결합으로 *implied framing* 추출 (의도 추출 깊이 +1 layer, ceiling-breaking 1순위 추정)
- `conventions/domain-research-stacking.md` + `conventions/domain-adapters/` 신규 — 마인드맵 noun → domain adapter 자동 stack (도메인 전문성 layer)
- `conventions/mindmap-quality-gardening.md` — Mermaid 의무 + 4 axis × ≥3 sub-node + ≥15 노드 (v091_cold01 ASCII 회귀 발견 정정)
- `conventions/ensemble-synthesis-default.md` — G4+ tournament 결과 *algorithmic union* default — 단일 우승 우주만 보지 않고 *교집합 + 합집합* 동시 활용

### 검증

self_lint 룰 +4 / pytest 회귀 0 / self_score 1.0. v0913_cold01 cold session 에서 design-only 회피 발견 → v0.9.14 deliverable-hurdle-supremacy 후속.

### 알려진 결손 (v0.9.14 해소)

본 sprint 만으로는 *코드 + 실행 + 측정값* 강제 부재 — agent 가 메모리 룰 literal 적용으로 design-only 종료 가능. v0.9.14 가 supremacy gate 추가.

---

## v0.9.12 — 2026-05-04 (sprint-06-c — analytical bound + multiverse impl fan-out)

### 마일스톤

v01_cold (v0.9.9) 회차의 *분석적 상한 vs 시뮬 baseline 자동 검증* 이 본 세션 v099 의 payload=50 잘못된 가정을 발견 — 메모리 `feedback_analytical_bound_validation.md` 정합. 본 sprint 가 발견을 컨벤션화.

### 변경 3건

- `conventions/analytical-bound-cross-validation.md` 신규 — closed-form 상한 vs simulated baseline 자동 검증, ratio [0.85, 1.00] 의무. 페이즈 09 derived gate 의무화.
- `conventions/multiverse-impl-fan-out.md` 신규 — universe N *모두* 실 코드 의무 (페이즈 06 plan 만 분기, 페이즈 08 가 단일 우주만 코드화 하던 문제 해소). tournament merge 코드 차원.
- `conventions/budget-aware-fallback.md` 신규 — silent fallback 금지, frontmatter `fallback_reason` 명시 의무.

### 검증

self_lint 룰 +3 / v091_cold01 cold session (90 min budget, 25 min 사용, 24/24 tests + 180/180 invariants) self 94 — analytical bound + ramp 비-병목 negative finding 도출.

---

## v0.9.11 — 2026-05-04 (sprint-06-b — interface-first parallel impl)

### 변경

- `conventions/interface-first-parallel-impl.md` 신규 — 페이즈 06 모듈 인터페이스 의무 + 페이즈 08 sub-agent 병렬 fan-out. universe N candidate 의 코드 작성이 *interface 의 다른 구현* 으로 격상 (v0.9.10 multi-phase 의 페이즈 08 axis 본격 발현).

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.10 — 2026-05-04 (sprint-06-a — AIDE multiverse 풀 발현)

### 마일스톤

본 하네스의 *유일한 차별 강점* (multiverse competition) 의 풀 발현 — *깊이 × 폭 × 검증* 3 차원 동시 강화. 페이즈 06 plan-tree 단독에서 5+ 페이즈로 multiverse 확장.

### 변경 3건

- `conventions/aide-tree-symmetry.md` 신규 — 각 universe candidate 의 sequenceDiagram ≥ 1 + actors ≥ 3 + interactions ≥ 5 + universe-specific differentiation 강제 (v01_cold audit 의 비대칭 경합 발견 정정).
- `conventions/aide-tree-multi-phase.md` 신규 — 페이즈 02 (doc-review multi-reviewer) / 05 (critique multi-critic) / 08 (impl multi-strategy) / 11 (regression multi-hypothesis) / 13 (viewer multi-framing) 까지 multiverse 확장. Q-D10~D14 페이즈 04 신규.
- `conventions/tournament-blind-rerun.md` 신규 — 임계 미달 시 anonymize previous winner 재경합. blind 검증으로 *우승 우주의 self-bias* 차단.

### 시너지

세 컨벤션 = "deep × broad × validated multiverse" — AIDE 의 풀 발현. README 본문에 *진짜 컨셉* 으로 부각.

### 검증

self_lint 룰 +3 / pytest 회귀 0 / self_score 1.0.

---

## v0.9.9 — 2026-05-04 (sprint-05-i — mindmap centrality)

### 변경

- `conventions/mindmap-centrality.md` 신규 — canonical concept graph 가 모든 페이즈 backbone. 페이즈 01 마인드맵이 단발 산출물에서 *전 페이즈 참조 grid* 로 격상.
- v01_cold (v0.9.9) 외부 cold session — synthetic_mine_throughput_v01_cold fresh (0 외부 ref) + 90 min budget, 25 min 사용. 24/24 tests + 180/180 invariants. 자체 94. crusher binding · ramp 비-병목 negative finding 도출. 자체 추정 inflation 노출 (97 generous → strict 94).

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.8 — 2026-05-04 (sprint-05-h — sprint regression loop + parallel cold review)

### 변경

- `conventions/sprint-regression-loop.md` 신규 — *self-polishing* 임계 도달까지 sprint 반복. budget 끝까지 사용 룰의 모태 (v0.9.15 budget-saturation-loop 가 정정).
- `conventions/parallel-cold-review.md` 신규 — N framing fan-out 으로 페이즈 03 다양성. single fresh agent 의 framing bias 차단.

### 검증

self_lint 룰 +2 / pytest 회귀 0.

---

## v0.9.7 — 2026-05-04 (sprint-05-g — premortem friction)

### 변경

- `conventions/premortem-friction.md` 신규 — 콜드리뷰의 *purpose* 가 *forward simulation* + derived_improvements 도출. 망설임 = 한 번 더 고민 + 미래 회고. 격언 동·서 1개 + 페이즈 02/03/07 적용.
- 메모리 `feedback_premortem_not_pause.md` 신규 — *멈춤 아님, 한 번 더 고민* 정의.

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.6 — 2026-05-04 (sprint-05-f — NFR derivation 자동 도출)

### 마일스톤

**케이스 종속 룰 금지 / 본 하네스 강화 = 구조 컨벤션** 메서돌로지 — 외부 답안 후 패치는 케이스 종속, 본 하네스 강화 = prompt → 게이트 흐름의 *구조* 변경. 메모리 `feedback_harness_strengthening_methodology.md` 정합.

### 변경

- `conventions/nfr-derivation.md` 신규 — prompt 형용사 (예: "robust", "scalable", "low-latency") 로부터 NFR + derived 게이트 자동 도출. 페이즈 01 의도 추출 + 페이즈 04 Q-D + 페이즈 09 게이트 6 의 일관 흐름.

### 검증

self_lint 룰 +1 / pytest 회귀 0.

---

## v0.9.5 — 2026-05-04 (sprint-05-e — 회귀 원인 분류 + plan implementation guidance)

### 마일스톤

사용자 4 질문 비판적 검토 후 *진짜 가치* 2건만 채택 (Q4 페이즈 02/03/09 경쟁 추가는 over-engineering 으로 거부).

### 변경 — Q1. 페이즈 11 회귀 원인 4 분류

`phases/11-regression-bisect.md` 새 절 — git bisect 결과를 4 분류 (plan defect / impl defect / data defect / external defect) 자동 판별 + 권고 페이즈 자동 진입 :

| 분류 | 권고 페이즈 |
|----|----|
| plan defect | 페이즈 06 재실행 (re-plan, universe 재분기 가능) |
| impl defect | 페이즈 08-γ 재실행 (re-impl, plan 유지) |
| data defect | 페이즈 04 Q-D8 재검증 (re-data) |
| external defect | 페이즈 09 게이트 7 재실행 (re-env) |

분류 알고리즘 — git bisect commit 의 변경 파일 + plan TODO DAG ↔ impl-log TODO 매핑 비교.

### 변경 — Q3. plan 본문 implementation guidance 의무 (HARD-RULE 9.a 강화)

`phases/06-plan.md` 새 절 — plan 본문 의무에 추가 :
- **데이터 구조** ≥ 2 (entity/state object dataclass + schema)
- **의사코드** ≥ 1 (핵심 알고리즘)
- **클래스 시그니처** ≥ 3 (`__init__` + 핵심 메서드)

신규 산출물 (impl-design.md) 만들지 않고 plan 본문 흡수 = 메모리 보수화 정합 + plan/impl-log 응집.

페이즈 11 회귀 분류와 *대응* — plan 의 데이터 구조/의사코드/클래스 시그니처 명시가 회귀 시 plan defect vs impl defect 자동 판별 입력.

### 변경 — self_lint 신규 룰 2

- **C-RB1** : 페이즈 11 본문 키워드 (plan defect / impl defect / data defect / external defect / 회귀 원인 분류) 검증
- **C-IG1** : 페이즈 06 본문 키워드 (implementation guidance / 데이터 구조 / 의사코드 / 클래스 시그니처) 검증

### 거부 (over-engineering 의심)

사용자 Q4 = 페이즈 02 의도 리뷰 / 03 콜드 재이해 / 09 게이트 에 경쟁 추가 → **거부** :
- 페이즈 03 = 단일 fresh agent 가 이미 격리 reviewer 역할 (사실상 페이즈 01 vs 03 경쟁)
- 페이즈 09 7 게이트 = 단일 evaluator 가 이미 multi-dim (7 차원) 평가
- 추가 sub-agent 비용 > 본질 가치 → over-engineering

### 검증

self_lint 60 → **62 룰** PASS / pytest 12/12 회귀 0 / self_score 1.0 / 임계 0.99999 통과

### sprint-05 묶음 종합 (v0.9.1 ~ v0.9.5)

| sprint | 변경 |
|----|----|
| 05-a (v0.9.1) | simulation-bench 베이스라인 + viewer split + TDD 5 서브페이즈 + ruff |
| 05-b (v0.9.2) | multiverse 폭 확장 + 자동 머지 알고리즘 + budget profile |
| 05-c (v0.9.3) | 재측정 + 3 universe head-to-head + interactive-viewer 첫 시연 |
| 05-d (v0.9.4) | 페이즈 13 책임 정정 (결과 프로덕트 only) |
| **05-e (v0.9.5)** | **회귀 원인 분류 + plan implementation guidance** |

self_lint 47 → **62 룰** (sprint-05 묶음으로 +15). 본 하네스 architectural 깊이 강화.

---

## v0.9.4 — 2026-05-04 (sprint-05-d — 페이즈 13 책임 정정)

### 마일스톤

v0.9.3 sprint-05-c 첫 시연 시 페이즈 13 interactive-viewer 가 *하네스 메타* (universe_comparison.png 등) 를 emit — 사용자 비판 정확 : "인터렉티브 뷰어가 우리 하네스 위주의 플랜이나 내부 과정에 종속된 결과물이 되어버렸다. 인터렉티브 뷰어는 결과 프로덕트의 데이터나 시뮬레이션 뷰어로서 동작하도록 설계되야 하는 스킬이다." sprint-05-d 가 본 룰 self_lint 로 강제.

### 변경

- `phases/13-interactive-viewer.md` 새 절 — 결과 프로덕트 only + topology + animation + drill-down + 하네스 메타 emit 금지 명시 + DES 도메인 결과 프로덕트 4 카탈로그 (topology/animation/drill-down/metric chart) + 분리 검증 어휘 black list (universe-N, multiverse, plan-tree, sprint metric 등)
- `agents/interactive-viewer-builder.md` 책임 좁힘 — 프로젝트 결과 only + 하네스 메타 emit 금지 + 도메인별 의무 emit 카탈로그
- `scoring/self_lint.py` 신규 룰 2 :
  - **C-IV1** : 페이즈 13 본문 키워드 (결과 프로덕트 / topology / animation / drill-down / 하네스 메타 emit 금지) 검증
  - **C-IV2** : interactive-viewer-builder agent 의 책임 좁힘 (프로젝트 결과 only / 하네스 메타 emit 금지 / topology / animation) 검증
- 메모리 `feedback_phase12_real_definition.md` 정정 — 페이즈 12 책임 강화 (하네스 메타 + multiverse 비교 차트), 페이즈 13 = 결과 프로덕트 only

### 검증

self_lint 58 → **60 룰** PASS / pytest 12/12 회귀 0 / self_score 1.0 / 임계 0.99999 통과

### 회귀 방지

본 sprint 가 self_lint C-IV1/C-IV2 룰로 강제 — 다음 회차 페이즈 13 진행 시 하네스 메타 emit 시도 → self_lint fail → 본 페이즈 재실행 강제.

### 후속 — interactive-viewer 결과 재 emit (별도)

simulation-bench 기존 interactive-viewer (sprint-05-c) 디렉터리 (`.ShipofTheseus/synthetic_mine_throughput_002/interactive-viewer/`) 의 universe_comparison.png 제거 + topology + animation + scenario drill-down 신규 emit 은 별도 작업 (gitignored 라 본 commit 영향 0). sprint-05-e 후보.

---

## v0.9.3 — 2026-05-04 (sprint-05-c — 재측정 + multi-universe 첫 실 시연)

### 마일스톤

sprint-05-b 의 architectural 변화 (폭 3 + universe 별 head-to-head + 자동 머지 + interactive-viewer) 실 시연. simulation-bench 재측정 결과 + 3 universe 비교 검증.

### 측정 결과 (`.ShipofTheseus/synthetic_mine_throughput_002/` — gitignored, 본 commit 미포함)

- 경과 : **44.4 분** (60 min budget 안전, sprint-05-a 43.1 min 동급)
- 15 페이즈 (00~14) 모두 진행 / 인터럽트 0 / autonomous
- **3 universe head-to-head 실 측정** :
  - U1 (process-first / per-direction) : 1555.8 t/h / D_CRUSH 병목 (per-direction 가짜 cap 인플레 노출)
  - U2 (hybrid centralized / shared bidirectional) : 1150.0 t/h / 로더 saturation
  - U3 (data-first event scheduler) : **1150.0 t/h / E03 ramp 정확 식별 + byte-reproducibility SHA256 매치**
- **자동 머지 알고리즘 결정 → U3 단독 채택** (차원별 sub-score gap 4pt vs U2)
- **interactive-viewer 페이즈 13 첫 실 시연** : matplotlib 3 plot (scenario throughput / bottleneck heatmap / universe comparison) + dashboard.json + index.html (CDN 0)

### 핵심 발견 (sprint-05-b 효과 검증)

a- **자동 머지 알고리즘 정상 작동** — 사람 critic 의 결정과 같은 답에 도달 (U3 단독 채택)
b- **per-direction vs bidirectional 차이 측정** — sprint-05-a 의 per-direction 머지가 ~35% throughput 인플레 (가짜 cap-1) 였음을 head-to-head 가 노출
c- **byte-reproducibility** = G5 미션 크리티컬 차원 신규 NFR. U3 가 도달
d- **페이즈 13 interactive-viewer 동작 검증** = matplotlib 0.43s 에 3 plot

### 자체 추정 점수

| 차원 (max) | sprint-05-a 단일 머지 | sprint-05-c U3 단독 |
|----|:-:|:-:|
| Conceptual 20 | 19 | 18 (narrative 보강 sprint 실패) |
| Sim correctness 20 | 16 | **18** (병목 정확 식별 +2) |
| Code quality 10 | 8 | **9** (45 tests + 0 ruff) |
| (기타 동일) | | |
| **합계** | **92** | **92~93** |

narrative 보강 후 추정 95~97 (1위 ouroboros 동급/상위 가능).

### sub-agent 회계

8 sub-agent 호출 — 1 실패 (페이즈 10 sprint narrative). intervention.category = autonomous 유지.

### 본 commit 의 변경 (본 하네스 source)

- `.claude-plugin/plugin.json` : version 0.9.2 → 0.9.3
- `skills/theseus-{harness,orchestrator}/SKILL.md` : frontmatter version
- `CHANGELOG.md` : 본 절 추가

본 sprint-05-c 는 *측정 + 검증* 이라 본 하네스 source 변경 0. 측정 결과 (`.ShipofTheseus/synthetic_mine_throughput_002/`) 는 .gitignore 됨.

### 다음 후보

- sprint-05-d : narrative 보강 (Conceptual 18→20 + Results 13→15 = +4pt → 추정 95~97)
- 외부 PR : simulation-bench 외부 채점으로 자체 추정 검증 (1위 ouroboros 97 head-to-head)

---

## v0.9.2 — 2026-05-04 (sprint-05-b)

### 마일스톤

본 하네스 강점 (다차원 동시진행 = plan-tree N universe + 경쟁 + 머지) 의 *폭 확장 + 자동 머지 강화*. 사용자 명시 — "다차원 동시진행이 강점이니 플랜/구현을 더 넓게 진행해서 트리를 더 가지많게".

### 변경 — MV-1. 멀티버스 폭 default 확장

- `conventions/grades.md` 새 절 — G3 폭 2→**3** / G4 폭 3→**4** / G5 폭 5→**6**
- self_lint C-MV1 룰 신규

### 변경 — MV-2. 페이즈 08 universe 별 head-to-head

- `phases/08-implement.md` 새 절 — universe 별 5 서브페이즈 (08-α/β/γ/δ/ε) 독립 사이클
- 각 universe 별 격리 코드 (`code/universe-N/`) + 격리 impl-log
- head-to-head 점수 비교 + 차원별 머지
- self_lint C-MV2 룰 신규

### 변경 — MV-3. 분기 축 카탈로그 ≥6

- `conventions/plan-tree.md` 새 절 — 6 axis 카탈로그 (process-vs-data / sync-vs-async / centralized-vs-distributed / dynamic-vs-static / push-vs-pull / mutable-vs-immutable) + 확장 후보 5
- planner 가 폭 N 진행 시 상위 N 개 axis 선택 → 본질적 의미 분기 강제
- self_lint C-MV3 룰 신규

### 변경 — MV-4. 자동 머지 알고리즘 강화

- `conventions/competition.md` 새 절 — head-to-head 점수 비교 + 차원별 sub-score (Conceptual/Data/Correctness/Experimental/Results/Code/Traceability)
- 자동 resolve 4 규칙 (단일 우승자 / 차원별 머지 / 재경쟁 / 타임아웃)
- self_lint C-MV4 룰 신규

### 변경 — MV-5. universe N 병렬 budget profile

- `conventions/resources.md` 새 절 — universe N 병렬 메모리 가드 (G3 40% / G4 50% / G5 60% RAM) + per-universe wall-clock budget + 초과 시 자율 폭 축소
- self_lint C-MV5 룰 신규

### 검증

- self_lint 53 → **58 룰** PASS / pytest 12/12 회귀 0 / self_score 1.0 / 임계 0.99999 통과

### 효과 추정 (simulation-bench 재측정 시)

- sprint-05-a 후 추정 92~95
- sprint-05-b (본 sprint) 후 추정 **96~98** — 1위 ouroboros (97) 동급 또는 상위
- 핵심 = G3 폭 3 적용 + 페이즈 08 universe 별 head-to-head 가 *실 코드 head-to-head* 비교 → 차원별 머지로 단일 universe 보다 강함

---

## v0.9.1 — 2026-05-04 (sprint-05-a)

### 마일스톤 묶음

a- **simulation-bench 첫 베이스라인 측정** (harrymunro/simulation-bench `001_synthetic_mine_throughput`)
  - G3 / 43.1 분 wall clock / intervention 0 / sanity 4 모두 PASS
  - 자체 추정 점수 92/100 (1위 ouroboros 97 대비 gap 5pt)
  - 산출물 : `.ShipofTheseus/synthetic_mine_throughput_001/` (페이즈 산출물 30+ + code/ 1975 LOC + 5 벤치 산출물)
b- **약점 분석** : gap 5pt 의 차원별 attribution + 본 하네스 책임 약 3pt 식별 (Sim correctness 4pt + Code quality 2pt + Results 1pt 부족)
c- **본 하네스 architectural 개선 3건** :

### 변경 — A. ruff 통합 (코드 lint/format 표준)

- `conventions/build-and-config.md` 새 절 8 — ruff check / ruff format 통합 + 페이즈 09 게이트 3 (SOLID DIP) 부속
- `scoring/self_lint.py` C-LINT1 룰 신규 — build-and-config 의 ruff 통합 본문 검증
- 거울 원칙 정합 — 외부 표준 도구 호출 (코드 micro 품질 룰 자체 정의 회피)

### 변경 — C. 페이즈 12/13/14 분리 (viewer 책임 분할)

- **14 → 15 페이즈** 확장
- `phases/12-webview-assembly.md` — **theseus-view** (스킬 진행 추적) 책임으로 좁힘
- `phases/13-interactive-viewer.md` **신규** — 프로젝트 output observability + 도메인별 dashboard
- `phases/13-handoff.md` → `phases/14-handoff.md` 이동 + 페이즈 번호 update
- `agents/interactive-viewer-builder.md` **신규** — 페이즈 13 책임
- `agents/webview-builder.md` 책임 좁힘 (theseus-view only)
- `conventions/spec-catalog.md` 도메인 dashboard 카탈로그 절 추가 (DES / 데이터 ETL / ML / 분석 / REST API / Frontend)
- `scoring/self_lint.py` C-WV1 / C-WV2 / C-WV3 / C-AGENT-IVB 룰 신규
- 메모리 `feedback_phase12_real_definition.md` 신규 — viewer 분리 의도 기록 (사용자 통찰)

### 변경 — TDD. 페이즈 08 5 서브페이즈 분해

- `phases/08-implement.md` — 5 서브페이즈 표 추가 :
  - **08-α scope** : test-architect (atomic / group / functional 3 계층 scope 정의)
  - **08-β test (RED)** : test-writer (테스트만 작성, 구현 0, RED 확인)
  - **08-γ impl (GREEN)** : implementer (테스트 통과 최소 구현)
  - **08-δ refactor (REFACTOR)** : refactorer (DRY/SOLID/docstring/type hint, GREEN 유지)
  - **08-ε log** : implementer (impl-log.md)
- `agents/test-architect.md` / `agents/test-writer.md` / `agents/refactorer.md` **신규**
- `agents/implementer.md` 책임 좁힘 (08-γ + 08-ε only)
- `conventions/test-invariants.md` — RED-GREEN-REFACTOR 루프 + universe 변경 트리거 절 추가
- `scoring/self_lint.py` C-TDD-08 룰 신규

### 변경 — infra

- `skills/theseus-harness/SKILL.md` — 15 페이즈 표 + 산출물 트리 (interactive-viewer/ + handoff/14-handoff.md)
- `skills/theseus-orchestrator/SKILL.md` — 15 페이즈 표 + HARD-RULE 8 grade 산출물 매트릭스 (handoff/14-handoff.md) + grade 처리 절 (G3 13 페이즈 / G4-5 15 페이즈)
- `scoring/self_lint.py` 47 룰 → 53 룰 (신규 6)

### 검증

- self_lint 53/53 PASS
- pytest 12/12 PASS (회귀 0)
- self_score = 1.0 / 임계 0.99999 통과

### Description (자체 개선 3건의 의미)

본 sprint = simulation-bench 첫 외부 적용으로 노출된 본 하네스의 약점 (코드 micro 품질 게이트 부재 / viewer 정의 narrow / TDD test-first 미적용) 을 *그 약점이 타당함을 검증한 후* 최소 변경으로 개선. 거울 원칙 정합 — 외부 1 케이스 위해 본체 합성 0, *원래 박혀 있어야 했던 정의* 노출.

---

## v0.9.0 — sprint-04-b

- sandbox livetest validated milestone

## v0.8.x — sprint-04-a, sprint-03-*

- 책임 범위 명시 + HARD-RULE 9 (설계 품질 의무) — sprint-04-a
- 페이즈 04 외 인터럽트 0 — 사람 ack 모두 자율 (sprint-03-f)
- 외부 정합 검증 (livetest G2/G3/G4/G5 모두 PASS) — sprint-03

## v0.7.x — sprint-02-e

- 9 항목 출하 (정직박스 ⓓ + 코드-실행가능 게이트 7 등)

## v0.6.0 — sprint-02

- AIDE plan-tree + competition + 멀티버스
