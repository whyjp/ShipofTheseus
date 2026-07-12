# 핸드오프 — 하네스 리뷰 후속 (v0.9.54, PR #98 착지 후)

작성 2026-07-12. 이 문서 하나로 새 세션이 이어받을 수 있게 자족적으로 쓴다.
관련 메모리: `verification-kernel-state.md`(자동 로드). 상위 로드맵: `docs/design/2026-07-05-spec2-swebench-bench-harness-design.md`(외부 벤치).

---

## 0. 현재 상태 (TL;DR)

- 브랜치 `main` = `8bdaab4`(PR #98 merged). 버전 **0.9.54**(SKILL.md=plugin.json).
- 전체 scoring 스위트 **509 passed**, self_lint **118/118 all_ok**.
- 이번 세션 = 사용자 하네스 리뷰("핵심=루프+회귀병렬, 더 핵심=퓨어리뷰 컨텍스트 필요한 것만 주입, 다이나믹 워크플로우의 코드기반 조건검사") → 진단 → P0~P2 + G1 구현/머지.

## 1. 리뷰의 관통 진단 (왜 이 작업들인가)

페이즈 09 게이트는 CheckSpec 커널(`scoring/kernel/`: `checkspec.safe_eval` AST 화이트리스트 + `evidence`/`kernel` producer/판정 분리 + `meta_audit` 레지스트리 열거 + `absence_policy=FAIL`)로 **값 판정**한다. 그런데 **제어 흐름 결정 셋**이 코드가 아니라 프로즈/휴면/이원화였다:

| 결정 | 리뷰 전 상태 | 이번에 |
|---|---|---|
| 리뷰 순도(퓨어리뷰) | `cold.isolation`이 `prior_context==0` assertion을 갖고도 `applicability: dispatch_log_present==1` 뒤 **영원히 NA(휴면)**; shadow-grader는 분산 프록시 | **P0** 비휴면 게이트 신설 |
| 루프 정지 | `stop_policy`가 manifest에 선언만, 합성 AND를 오케스트레이터(LLM)가 조립; `sprint_loop_cap`은 옛 4-layer 보고모드 | **P1** 단일 코드 진입점 |
| 회귀 분기 | `checkpoint.FAILURE_TO_PHASE`(8종) ↔ phase-11 4분류 **이원화** | **P2** 단일 소스 |
| (성능) 검증층 병렬 | run_gate producer 전부 직렬(매 sprint hot path) | **G1** 병렬화 |

## 2. 이번 세션 착지물 (PR #98, 커밋 4개)

- `bd34ff9` **P0** — `checks/review.context_minimality.json`(applicability 없는 비휴면: `prior_context_max==0` + `loaded_artifacts_missing==0` + `malformed_calls==0` + `duplicate_call_ids==0` + `calls_total>=1`, value=`loaded_tokens_max`) + `producers/measure_context_minimality.py`(`loaded_tokens_max`를 로그 신고 아닌 **디스크 재계산**) + manifest G3/G4/G5 등록 + `run_gate._review_producer`(관례경로 `state/review_dispatch_log.json`, `--no-review`) + `producers/tests/test_measure_context_minimality.py`(12).
- `8f7217d` **P1** — `scoring/should_stop.py`: `stop = gate(meta_audit verdict pass) ∧ no_regression ∧ (plateau ∨ budget≥cap)`를 manifest `stop_policy` 읽어 합성. plateau=`stagnation.detect` 재사용. exit 0=stop/1=continue. `test_should_stop.py`(7).
- `0d04430` **G1** — `run_gate.py`: 독립 producer(quality/gates/plan/cold/review) `ThreadPoolExecutor` 병렬. 순서의존(2→3→5)은 submission을 barrier 뒤에 둬 보존. `enable_parallel`/`--no-parallel`. `test_run_gate.py`에 병렬≡직렬 바이트 등가 test.
- `9bd16f5` **P2** — `checkpoint.FAILURE_TO_PHASE` 단일 소스 통합(bisect 4분류 병합, 충돌 0) + `BISECT_DEFECT_CLASSES` + `phases/11-regression-bisect.md` 노트(C-RB1 유지) + drift 가드 test. + CHANGELOG v0.9.54.

## 3. 남은 작업 (우선순위) — 새 세션 시작점

### A. 배선 — 무장한 게이트를 페이즈 흐름에 먹이기 ★ 최시급
> 이번 PR은 조건을 **무장(armed)** 하고 러너(run_gate)까지 배선했으나, **페이즈 오케스트레이션 문서가 아직 이 게이트를 먹이지 않는다.** 실 G3+ run에서 아직 완전 작동 아님(의도된 forcing-function 상태 — 지금은 review 로그 부재 → deficit-FAIL).

- **A1** — `phases/03-independent-comprehension.md`(+ 06/08 shadow-grader 지점)이 fresh 리뷰 sub-agent 호출마다 `state/review_dispatch_log.json`에 `{agent_call_id, prior_context_token_count, loaded_artifacts:[상대경로]}` 를 **누적 append**하도록 본문에 literal 지시 추가. 스키마는 `producers/measure_context_minimality.py` docstring(`_CALLS_KEYS`, `_valid_call`) 참조. 로그 생기면 `run_gate`가 관례경로에서 자동 소비 → review.context_minimality가 deficit→실 게이팅.
- **A2** — `phases/10-test-loop.md`가 매 sprint iteration 경계에서 `scoring/should_stop.py --gate-report quality/gate_meta_audit.json --score-history <scores> --grade <G> --budget-used <r>` 를 호출하고 exit 0=stop/1=continue로 분기하도록 배선(프로즈 정지 판정 대체). `sprint_loop_cap` 호출 지점을 should_stop으로 교체.
- **주의**: A1/A2는 phase 문서(markdown) 편집이라 self_lint 페이즈-문서 룰(C-RB1류)을 안 깨는지 확인 필요. 새 self_lint 룰(C-…)로 "phase 03/06/08 본문에 review 로그 emit 지시 존재", "phase 10 본문에 should_stop 호출 존재"를 강제하면 declared=invoked 패턴 정합.

### B. 더 깊은 병렬성 갭 (병렬성 리뷰 결론, 미착수)
- **B1 (최대 가치)** — **멀티버스 fan-out 코드 primitive.** 현재 `intra-phase-dacapo-loop.md`의 fan-out(width G4=4/G5=6)이 의사코드/모델재량 → 모델이 skip 가능(cold session winner 0.853 재경합 0회가 증거). `universe_count_monotonicity.py`는 사후 검사일 뿐. 폭 강제 + 병합을 코드로 소유하는 harness 필요(Workflow의 parallel()/pipeline() 유형). 당신 논지가 병렬성에 도달하는 종착점.
- **B2** — 회귀 진단(phase 11 `regression-analyst`)이 단일 에이전트 직렬. 가설을 adversarial 병렬 skeptic으로 검증하도록 fan-out.
- **B3** — 하네스 오케스트레이션에 백그라운드/async 개념 부재. **[2026-07-12 DEFER — Fable 판정, 착수 안 함]** gap 이 과장. (a) 뷰어 서버(유일한 실 장기 서비스)는 이미 완전 백그라운드(`viewer_runtime.py` `Popen(start_new_session/CREATE_NEW_PROCESS_GROUP)` + PID lock + `server.log` + up/down/status lifecycle) + lint(C-VRL) 소유. (b) 나머지 병렬성은 전부 parallel-then-**join** 이 올바른 시맨틱(게이트는 전 evidence 필요, fan-out 은 tournament-merge 로 join, 스프린트 루프는 결과에 의존해 본질상 순차). (c) 페이즈 오버랩은 명시적 안티패턴(`intra-phase-dacapo-loop.md` §8.e 페이즈 의존성). (d) `run_in_background` 는 skill 트리에 0 회(핸드오프 §68 언급은 유지보수 콘솔-포커스 팁이지 오케스트레이션 개념 아님). (e) "run 중 백그라운드 뷰어"는 이미 시도→편익 미실증으로 §8 동결(`pre-cold-session-bootup.md`). **게이트(A) 불가**: 비휴면 아티팩트 없음(viewer.lock 게이팅은 뷰어 미부팅=기본값 시 휴면 → cold.isolation dormant-NA 병폐 재현; "detached 실행" 은 scoring 층이 관측 불가한 순수 자기신고). **컨벤션(B) 불가**: doc-only 모델재량=무치(C1 shim 류) + 측정불가 + 루프가 즉시 join. **부활 조건**: D1(Spec 2 SWE-bench) 착지 시 per-instance Docker eval 이 독립 장기 job → 코드소유 job manifest(`jobs/<id>.json`: pid/container-id/submitted_at/collected_at)가 실 아티팩트가 됨(viewer.lock 패턴 복제). 또는 B1 의 parallel primitive 설계 공간에 흡수. 독립 착수는 강제 약증분이라 non-goal 기록.

### C. 정리
- **C1** — `sprint_loop_cap.py` 폐기/redirect(should_stop이 정지 권위 됨). test_sprint_loop_cap 정리 동반.
- **C2** — shadow-grader(06/08) 순도를 `plan.tournament_independence`에 `prior_context==0` assertion 추가(현재 `grader_score_variance>0` 프록시만). shadow-grade-NN.json이 A1의 dispatch-log 스키마를 겸하면 review.context_minimality로 06/08도 커버 가능.

### D. 선재 로드맵 (메모리 verification-kernel-state)
- **D1** — 외부 벤치마크(Spec 2, SWE-bench). 계획 `docs/design/2026-07-05-spec2-swebench-bench-harness-design.md`. WSL2 Ubuntu-24.04 Docker eval. 실제 외부 점수 개선(미증명 가설) 확증. **별도 클린 세션** 권고.

**추천 순서**: A(배선) → B1(멀티버스 primitive) → C/D.

## 4. 새 세션이 알아야 할 리포 기계 (재학습 비용 절감)

- **테스트**: `python -m pytest skills/theseus-harness/scoring -q -p no:cacheprovider` (전체 ~64s). self_lint 값 확인: `python skills/theseus-harness/scoring/self_lint.py --score`(JSON, `all_ok`/`lint_failures`).
- **새 CheckSpec 추가 계약**(P0가 모델): ① `checks/<id>.json` 파일 + ② `pipeline.manifest.json` `checks` 맵(G3/G4/G5) 동시 갱신(둘 중 하나만 하면 `manifest.drift_check` FAIL) + ③ producer `producers/measure_<x>.py`(Evidence Record는 `_evidence_common.assemble_record` 사용, `build_measured`로 value/source/artifact_path) + ④ (선택) `run_gate.py`에 producer step 배선 + ⑤ test. meta_audit는 하드코딩 0 — 레지스트리 열거라 파일+맵만 추가하면 자동 감사.
- **kernel 5법칙**(`kernel/kernel.py`): 1 evidence 존재 → 2 produced_by=run+provenance → 3 producer_cmd 매칭+artifact_digests 디스크 대조 → 4 assertion(safe_eval) → 5 value. `absence_policy=FAIL` = 로그/evidence 부재는 통과 아닌 FAIL.
- **safe_eval 제약**: 산술+비교+and/or/not+measured 이름만. 함수호출/속성/첨자 금지.

### 버전/lint 함정 (이번에 밟음)
- **C7** = `SKILL.md version:` ↔ `plugin.json version` 정합. 릴리스 시 둘 다 bump. (orchestrator SKILL.md는 미검사라 별개.)
- **C41** = SKILL.md `description` **≤200자** + 금지어구("사용 금지"/"호출 거부"/"진입 거부"/"사소한 작업") 없음. plugin.json description은 미검사(길어도 됨).
- CHANGELOG는 version 정합 lint 없음(자유). 하지만 sprint/version history 단일 위치.

### Windows 환경 함정
- **콘솔 포커스**: 사용자가 게임 중일 때 pytest/파이썬 subprocess가 새 cmd 창 포커스를 뺏음. → 무거운 실행은 **run_in_background**로 묶고, 파일 작성(Write/Edit)은 창 안 뜸(가능한 한 편집 먼저·실행 마지막 1회).
- **exit code 함정**: `pytest ... | tail`은 tail의 exit(0)을 잡아 실패를 가림. 파일로 리다이렉트 후 `echo EXIT=$?` 또는 output 파일 직접 read.
- cp949 콘솔 — 모든 producer가 `force_utf8_stdio()`, 모든 open `encoding="utf-8"`(self_lint C35).

## 5. 정직한 한계 (과장 금지)
- P0/P1은 **도구는 무장, 페이즈 흐름 미배선**(§3.A) — 실 run에서 아직 완전 발현 아님.
- `prior_context_token_count==0`은 여전히 디스패치 계층의 자기신고(producer가 sub-agent conversation을 직접 못 봄). 무결성/freshness/토큰 재계산으로 조이지만 순도 자체의 궁극 증명은 불가 — cold.isolation과 같은 전제.
- 외부 점수 개선(D1)은 미증명 가설 — 내부 self-score/테스트 초록은 외부 evaluator 확증과 별개.
