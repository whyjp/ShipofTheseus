# 설계 문서 — B3: self_lint 광역 순감 + stale 정리 + §11.5(a) 지시질량 재실측

> **작성**: Claude Fable 5 (설계 확정 — 코드/self_lint/컨벤션/phase 편집 없음, 본 문서 단일 산출)
> **구현 위임**: opus/sonnet (§6 작업 패키지 기준)
> **일자**: 2026-07-05
> **선행 설계**: `docs/design/2026-07-04-verification-kernel-design.md` (§11.1 순감·§11.5(a) 성공 측정) · `docs/design/2026-07-05-B1-kernel-wiring-design.md` (§3.2D 5룰 삭제 + §6 순감 프로토콜) · `docs/design/2026-07-05-B2-frozen-diet-threshold-design.md` (§4.3 self_lint 실측 구분 + §6.7 "B3 몫" 명시 이월)
> **대상 저장소 상태**: HEAD `6e047c5`(WP-B2c 완료) + working tree 의 B2 잔여 수정. 본 문서의 모든 라인·바이트·룰 수는 이 working tree **grep/실행 실측**이다 — `self_lint.py` 3,374줄, 등록 체크 **126 엔트리(124 고유 id — C-PT·C-STT 각 2중 등록)**, `all_ok=True` 확인.

---

## 0. 범위 계약 — B3 가 확정하는 것

B1(커널 배선)·B2(동결 다이어트+임계 교체) 이후 측정계를 마지막으로 다진다. 세 부분:

1. **self_lint 광역 순감** — 커널 CheckSpec/meta_audit 이 이제 *실측*하는 차원을 문서
   키워드 grep 으로 중복 검사하던 prose C-룰(P2 패턴)과, 미구현 메커니즘을 문서에
   선언하도록 강제하던 룰(선언≠구현 핀)을 삭제·수정. **보수 원칙: 애매하면 존치.**
   진짜 문서 정합(마크다운 인덱스·교차참조·버전·자산 존재·진실성)은 전량 존치.
2. **stale 정리** — B2 의 viewer-게이트 advisory 강등 이후 stale 이 된 9.rr
   `cold_session_artefacts.py` 파일존재 강제 계열 + B1 이 은퇴시킨 9.f/9.zz 의 잔존
   참조 + B1/B2 가 플래그한 가짜 self_lint 귀속(선언된 룰이 self_lint 에 실재하지 않음).
3. **§11.5(a) 재실측** — phase 진입 지시질량을 B1-이전 baseline(`d0754f7`) 대비 실측해
   B1~B3 누적 감소를 **값으로** 문서화. 측정 프로토콜 + before/after 표 + 총량 하드 룰.

**위반 불가 원칙:**

- **무게이트 공백 금지 (B1 규율)**: 삭제하는 룰은 (a) 커널이 같은 차원을 값으로 실측하거나
  (b) 검사 대상 메커니즘이 미구현(가짜)이거나 (c) B2 강등과 모순되는 stale mandate 핀인
  것만. 각각 §1.2 표에 대체 커널 체크 id 또는 grep 근거를 1:1 명시.
- **신규 lint 룰 추가 금지**: 순감 sprint 에 순증 금지(§11.1). B3 의 모든 검증은 기존
  도구(self_lint all_ok · pytest · `kernel/manifest.py drift-check` · grep)로 한다.
- **커널 코어 무수정**: `checks/*.json` · `kernel/` · `run_gate.py` · `meta_audit.py` ·
  `producers/` · `pipeline.manifest.json` 은 B3 에서 건드리지 않는다 — B1 게이팅 무영향.

---

## 1. self_lint C-룰 분류표 (126 엔트리 전수 — grep 실측 기반)

### 1.1 분류 기준 + 결합 테스트 구조 (먼저)

- **(a) kernel 대체**: 해당 차원을 `checks/` CheckSpec + producer 가 런타임 값으로 실측
  (scoring 6종 · quality 3종 · `plan.dacapo_threshold`(유효성 assertion + ratio value) ·
  `plan.tournament_independence`(grader_count≥2 + variance>0) · `sprint.regression`
  (score_delta≥−0.05) · `cold.isolation` · frozen 2종 advisory) — 문서 키워드 grep 은 중복.
- **(b) 가짜(선언≠구현)**: 룰이 문서에 **미구현 메커니즘의 선언을 강제**한다 —
  마크다운 의사코드 함수(`gate_phase06_to_07`/`check_shadow_independence`/
  `update_phase_lineage`/`regression_lint_registry` — 전부 `scoring/*.py` grep 0, 실측)나
  실행된 적 없는 영문 regex 카탈로그(`SENTINEL_*_PATTERNS` — B1 이 P3 로 폐기 선언한
  check_cold_session sentinel-regex 와 동일 부류). 또는 B2 가 advisory 로 강등한 의무의
  **의무 어휘를 문서에 되박도록 강제**(stale mandate 핀 — B2 §4.3 C-PCB 정리와 동일 원리).
- **(c) 진짜 문서 정합**: 마크다운 인덱스/교차링크/버전/frontmatter 무결성 · 실파일(스크립트
  ·템플릿·에이전트) 존재 · 진실성 룰(9.ooo/9.nnn/9.ppp·fingerprint·grade≠gate) · 커널이
  못 보는 프로세스/카탈로그 정의의 자기 완결성 → **존치**.

**결합 테스트 (실측)**: `test_self_lint.py` 는 **일반형 4개뿐**(all_ok · 체크 수 ≥18 ·
`--score` 보고모드 필드 · lint_score==1.0) — **룰별 개별 테스트 0** (`grep C-DCL-GATE|C-PLV|…
scoring/test_*.py kernel/tests/*.py` = 0 실측). 따라서 룰 삭제의 테스트 동기화 비용은
"삭제 후 all_ok 유지 + 체크 수 118 ≥ 18" 뿐이다. 스크립트-쌍 테스트 3종
(`test_cold_session_artefacts.py`/`test_generate_sprint40_artefacts.py`/
`test_phase_invoke_audit.py`)·`test_runtime_guard_chain.py` 는 §2 stale 정리의 동기 대상.

### 1.2 삭제 — 8룰 (~153줄: 함수 129줄 + 공백/등록 ~24줄)

| id | 목적 한줄 | 분류 | 삭제 근거 (1:1 대체/실측) | 짝 prose 정리 (동일 커밋) |
|---|---|---|---|---|
| **C-DCL-GATE** (L1713-1731) | dacapo-enforcement.md 에 phase 06→07 frontmatter 의사코드 게이트 선언 강제 | (a)+(b) | 게이트 실체 = `run_gate.py` + `plan.dacapo_threshold`/`plan.tournament_independence`(값). `gate_phase06_to_07` 은 의사코드(구현 grep 0). frontmatter 자기신고 검증은 커널이 불신하는 채널(법칙 1~3) | `dacapo-enforcement.md` L169(표 행)/L188 귀속 문구, `phases/06-plan.md` L546 |
| **C-DCL-SHADOW-CONTEXT** (L1754-1769) | shadow-grader-zero-context.md 에 무결성 5룰 의사코드 선언 강제 | (a)+(b) | 독립성은 `plan.tournament_independence` 의 `grader_score_variance > 0` + `grader_count >= 2` 가 **값으로** 실측(동일 점수=복사 의심 assertion). `check_shadow_independence`/`check_unique_agent_call` 은 의사코드(구현 0). `prior_context_token_count` 류는 자기신고 필드 — 커널 원칙상 판정 근거 아님 | `shadow-grader-zero-context.md` §4(L133)/L229, `phases/06-plan.md` L549 |
| **C-DCL-SENTINEL** (L1772-1789) | dacapo-skip-sentinel.md 에 Sentinel A/B/C regex 카탈로그 선언 강제 | (b) | `SENTINEL_*_PATTERNS` = 실행 0 의 영문 regex prose(P3 — B1 이 check_cold_session 에서 은퇴시킨 그 패턴). skip 차단의 실체 = stop_policy delta 룰 + `sprint.regression`(값) + `plan.*` evidence-missing FAIL | `dacapo-skip-sentinel.md` §5(L247)/L300, `phases/06-plan.md` L550 |
| **C-DCL-MIN-LOOP-ATTEMPT** (L2059-2073) | dacapo-enforcement.md 에 "최소 1회 실 rerun" 의무 선언 강제 | (b) stale | B2 §2.2-3 이 rerun 을 "신호(delta) 있을 때"로 교체·mandatory-rerun 을 advisory 강등 — 본 룰은 강등된 의무 어휘를 문서에 되박는 stale mandate 핀 | `dacapo-enforcement.md` L175/L194/L216 |
| **C-DCMR** (L2234-2245) | dacapo-mandatory-rerun.md 에 "rerun_count ≥ 1 예외 0" 의무 키워드 강제 | (b) stale | 동일 — B2 §2.3 표가 컨벤션 자체를 advisory 로 강등. 의무 키워드("예외 0") 핀은 강등과 모순 | `dacapo-mandatory-rerun.md` L24 §C-DCMR 절 |
| **C-MV1** (L1430-1438) | grades.md 에 "폭 3/폭 4/폭 6/sprint-05-b" 키워드 강제 | (a) | 폭의 단일 권위 = manifest `multiverse_widths`(B2 F1) + `kernel/manifest.py drift-check`. grades.md 숫자 핀은 권위 2중화(드리프트 재발 경로) + "sprint-05-b" history-라벨 핀(P2 취약) | grades.md 는 무수정(manifest 참조 표기는 B2 완료분) |
| **C-PLV** (L1887-1909) | phase-lineage-viewer.md 에 27 키워드(gantt/sentinel/의사코드 포함) 강제 | (a)+(b) | 핵심 emit 정합(lineage.html/`window.__LINEAGE__`/dist 경로)은 **C-PSR 서브체크 6 이 이미 검증(중복, DRY)**. 잔여 = `update_phase_lineage` 의사코드 + "Sentinel 위반 이벤트"(삭제되는 sentinel 기계) + gantt 세리머니 핀. viewer 생산 의무는 B2-F3 강등 — 본 핀이 B2 §6.7 이월분(본문 다이어트)을 구조적으로 차단 중 | `phase-lineage-viewer.md` §7(L269)/L351/§14.3(L431) 귀속 절 |
| **C-RDLR** (L1631-1647) | regression.md §3 에 "lint 룰 자동생성 registry" 선언 강제 | (b) | `regression_lint_registry`/`lint_rule_proposal` 구현 grep 0(self_lint 키워드 리스트 자신뿐 — 실측). 회귀→lint 룰 자기증식은 §11.1 반군비경쟁(순감)과 정면 모순인 메커니즘의 선언 강제. 회귀 검출 실체 = `sprint.regression`(커널 게이팅) + `regression_check.py`(C-RTG 존치) | `regression.md` §3.5(L158), `MIGRATION.md` L36 rationale 셀("C-RDLR 함수 유지" 문구 → 삭제 반영) |

**보수성 방어**: 삭제 8룰 전부 "커널 값 실측 대체" 또는 "미구현/강등-모순 선언 핀" 중
하나 이상의 **grep-실측 근거**를 가진다. 문서 자체(dacapo-enforcement/skip-sentinel/
shadow-grader/phase-lineage-viewer/regression/dacapo-mandatory-rerun)는 **전부 물리 존치**
— 삭제되는 것은 self_lint 의 키워드 핀과 그 귀속 문구뿐이다(how-to·anti-pattern 본문 유지).

### 1.3 수정 존치 — 2룰 + ID 위생 2건

| id | 수정 | 근거 |
|---|---|---|
| **C-PSM** (L1912-1939) | 키워드 리스트에서 `"check_cold_session"` 1건 제거 (나머지 전부 존치) | §2 S6 이 phase-state-machine.md 의 은퇴 9.f 참조를 정리하면 본 키워드가 FAIL — stale 정리와 **동일 커밋 계열 동기 의무** (B2 §4.3 C-CMJ 동기와 같은 원리) |
| **C-DCL-FLOW-LOG** (L2010-2034) | `phases/06-plan.md` 에 `"v0.9.22"` 문자열을 요구하는 서브체크(L2026-2027)만 삭제 — dacapo-flow.md 포맷 키워드 검증은 존치 | 버전-라벨 history 핀(P2 취약 — sprint-22 에 phase 08 쪽 동일 핀은 이미 제거된 전례가 함수 주석에 실측). dacapo-flow.md 산출물 포맷 정의(9.d)는 유효한 문서 정합이라 존치 |
| C-PT 2중 등록 | prompt-trace 쪽(L3202) 등록 id 를 `C-PTRC` 로 리네임 (plan-tree 쪽 C-PT 유지) + `phases/08-implement.md` L189 §헤더 동기 | 동일 id 2 등록 = 리포트 상 구분 불능(실측 dups: C-PT, C-STT). 함수·검사 내용 무변 — id 문자열만 |
| C-STT 2중 등록 | subagent-trigger 쪽(L3221) 등록 id 를 `C-SAT` 로 리네임 + `subagent-trigger.md` 내 귀속 표기 동기 (sub-tree TODO 쪽 C-STT 유지) | 동일 |

### 1.4 존치 — 116 고유 id (전수, 분류 (c) — 보수 근거 명시)

결합 테스트는 전 룰 공통(§1.1 — test_self_lint 일반형). 사유 열은 존치 근거의 유형.

**구조·인덱스·교차링크 정합 (커널이 원리적으로 못 보는 마크다운 무결성):**

| id | 목적 한줄 | 존치 사유 |
|---|---|---|
| C1 | conventions 헤더(# 제목 + 한 줄 요약) 형식 | 인덱스 가독 규약 |
| C2/C3/C4 | SKILL∪INDEX 가 conventions/phases/agents 전량 링크 | 링크 무결성 |
| C5 | agents '권장 모델:' 줄 | 라우팅 메타 무결성 |
| C6 | PHILOSOPHY↔SKILL 교차링크 | 링크 무결성 |
| C7 | plugin.json↔SKILL 버전 일치 | 버전 드리프트 차단 |
| C8 | score/fingerprint/self_lint 컴파일 가능 | 실행체 건강 |
| C9/C38 | INSTALL 설치 경로 + fresh-user 절 | 문서 정합 |
| C10 | phase↔agent 링크 | 링크 무결성 |
| C11 | skill README 가 conventions 전량 노출 | 인덱스 무결성 |
| C26 | SKILL.md 길이 cap(fragmentation) | 반군비 자기 규율 |
| C28/C37 | 두 스킬 존재 + 의존 정직 명시 | 구조 정합 |
| C32 | 룰 본문 중복 검출(DRY) | 반군비 자기 규율 |
| C41 | description ≤200 + gate 어휘 금지 | 정합+정책 |
| C42 | prd-handling 흡수 + dead link 0 | 링크 무결성 |
| C43 | HARD-RULE 마크업 | 구조 정합 |
| C-HC1 | HARD-CORE ≤4,900 chars + 의무 키워드 | §11.4 always-load cap |
| C-IDX-1/C-IDX-2/C-IDX-4 | conventions↔INDEX 1:1 + frontmatter drift + grade 어휘 | router 단일 진실 원천 |
| C-DIET/C-MIGRATION/C-PHASE-LEN | deprecated grace ≤1 sprint + successor 실재 + phase 50K cap | 다이어트 자기 규율 |

**진실성·정책 무결성 (커널 게이트와 직교하는 부정직 차단):**

| id | 목적 한줄 | 존치 사유 |
|---|---|---|
| C14 | quality-gate frontmatter 누락 자동 fail 룰 명시 | 진실성 |
| C17 | writer agent 12종 fingerprint 호출 명시 | fingerprint 체인 |
| C23 | phase 05~13 사용자 인터럽트 패턴 0 (negative grep) | autonomy 정책 — 커널 밖 행동 규율 |
| C-GS | grade+거부/차단 결합 표현 검출 (negative grep) | grade≠gate 정책 |
| C33 | PRD 입력 시 인터뷰 스킵 금지 허들 | 정책 |
| C-CNS | canonical 산출물 ≥ winner 80% inline/schema | 산출물 stub-사기 차단 |
| C-UNIV-CREATED-AT | universe candidate `created_at` 실값 (9.ooo) | B2 원칙 2 조건부 진실성 |
| C-LFW | phase 14 lineage_finalize + placeholder 검사 literal invoke (9.nnn/9.ppp) | 동일 |
| C-IV1/C-IV2 | phase 13 결과-프로덕트 only + 하네스 메타 emit 금지 | SoC 진실성(산출 시 조건부) |
| C-CMJ | 보수적 prior + 측정값 그대로 보고 (B2 재정정본) | B2 완료분 계승 |
| C35 | subprocess/tempfile encoding 명시 | Windows 실버그 가드 |

**능력·자산 실파일 검증 (스크립트/템플릿/에이전트 존재 — B2 §4.3 양립 확인 계승):**

| id | 목적 한줄 | 존치 사유 |
|---|---|---|
| C-PSR/C-EFS/C-VAR/C-VRL/C-IVP | prebuilt shell 3종 dist 실파일 + CDN 0 + sample fidelity(값 검증) + polling/lifecycle 능력 | 자산 무결성 — advisory 후에도 능력은 존치 |
| C-PCB | pre_bootup.py 함수 존재 + teardown 조건부(B2 정정본) | 능력+위생 |
| C-WV1/C-WV2/C-WV3/C-AGENT-IVB | phase 12/13/14 파일·명명·에이전트 존재 | 구조 정합 |
| C24/C27/C29/C30/C31 | checkpoint/grade_assess/dispatch/index_builder/resume 스크립트+컨벤션 배선 | 능력 배선 |
| C-PSM(수정 후)/C-RTG | phase_state.py·regression_check.py 함수 존재 + 컨벤션 | phase 단조성 runtime 가드 / **commit-level** 회귀 로그 — `sprint.regression`(sprint-level delta)과 별차원 |
| C-GAv2 | grade_assess v2 다중신호 + 키워드매칭 폐기 확인 | 능력+회귀 방지 |
| C-RP | runtime-prereq Q-D9/게이트7/템플릿/detector 배선 | 능력 배선 |
| C-LINT1 | build-and-config ruff 통합 | 능력 배선 |

**프로세스·카탈로그 정의의 자기 완결성 (커널이 결과만 보고 정의는 못 보는 것):**

| id | 목적 한줄 | 존치 사유 |
|---|---|---|
| C12/C13/C-TDD-08/C-MV2 | phase 06 시퀀스 절 / 08 sh+bat / 5서브 TDD / head-to-head | 활성 프로세스 정의(B2 무수정 영역 — 활성 폭 3/4/6 동작) |
| C-IMS/C-IMS-SEMANTICS | impl multiverse 7조건 + "plan 손자 아님" 의미론 | cold-session 회귀 교훈의 의미 정의 |
| C-DCL-FRESH-UNIVERSE | Round N+1 = fresh universe (survivors-rerun 금지 anti-pattern) | 동일 — 커널은 결과 변량만 봄, 의미 정의는 문서 몫 |
| C-PTSS | tournament 6-dim weighted + coarse 1-5 reject 프로토콜 | **경계 사례 정직 고지**: 커널 variance>0 은 복사만 잡고 채점 granularity 는 못 봄 → 존치(애매→존치) |
| C-DCL-FRONTMATTER | dacapo frontmatter 스키마 필드 카탈로그 완결성 | **경계 사례 정직 고지**: 자기신고 스키마지만 dacapo_threshold.py(보고모드)가 실소비하는 스키마 문서의 자기 완결성 → 존치 |
| C-DCL-FLOW-LOG(수정 후) | dacapo-flow.md 포맷(9.d 산출물) 정의 | 산출물 포맷 정합 |
| C-DCL-NO-FORWARD-PROJECT | 시간 forward projection 금지(측정 only) | 정직 룰 — 커널 미측정 |
| C-PPC/C-RES/C-IDC/C-CLS/C-STT/C-PMT | phase 06 §06.a~f 서브페이즈 정의 | 프로세스 정의 |
| C-DPT/C-PTRC(구 C-PT)/C-IG1/C-RB1 | phase 07 dispatch / 08.f prompt-trace / impl guidance / 회귀 4분류 | 프로세스 정의 |
| C-IRPI/C-IRPC/C-CPSC/C-IOD | intent refresh 1·2차 / shared context / optional 마커 | 프로세스 정의 |
| C-CT/C-SDT/C-EDP/C-CULD | 컨벤션 발현 추적 / delta / evidence 계획 / cross-universe 교훈 — cross-ref 문장 | B2 §4.3 이 보존을 명시 지시한 cross-ref 정합 |
| C-DMC/C-DSI/C-SPI/C-ECP/C-RDM/C-ICQ/C-PCQ | 도메인 품질 카탈로그(entity/invariant/IV-DV/…) 완결성 | 카탈로그 무결성 |
| C-RNFS/C-RDC/C-MNT/C-DCZ/C-SPB | README↔summary drift / 재현성 2회 / 매직넘버 / dead-code / 포터빌리티 | B1 §3.3 존치 결정 계승(스크립트+JSON 이중압력 실게이트 — producer 승격 후보) |
| C-DIAG-AND-COVERAGE | sequence+usecase+interface AND 셋 다 | 콘텐츠 의무 — 커널 미측정, 애매→존치 |
| C-MV3/C-MV4/C-MV5 | 분기축 카탈로그 ≥6 / 자동머지 알고리즘 / 병렬 budget 가드 | 카탈로그·가드 정의 |
| C15/C16/C18/C19/C20/C21/C22/C25/C34/C36/C39/C40/C-OD/C-SAT(구 C-STT) | 나머지 배선·정책·카탈로그 정합 | 전부 (c) — 커널 미측정 차원 |

**수지**: 등록 126 → **118 엔트리** (고유 124 → 116). `self_lint.py` 3,374줄 → **≤ 3,230줄**
(삭제 ~153줄 + C-PSM/C-DCL-FLOW-LOG 소폭 감소, 리네임은 ±0).

---

## 2. stale 정리 목록 — 파일·라인·조치 (worktree 실측)

### 2.1 9.rr 계열 — viewer-게이트 advisory 강등(B2-F3) 후 stale 이 된 file-existence 강제

`cold_session_artefacts.py` 가 강제하는 13 산출물 중 **7개의 생산 의무가 이미 해제**됐다:
gate_pnc/mirror/primary/literal 4종(B1 §3.2C advisory 강등 — producer 0) +
webview/exit_gate·iv/exit_gate·iv/dashboard 3종(B2-F3 viewer 옵션화 — phase 12/13 종료
게이트 삭제). 남은 6종(gate_v6/v8/readme_summary/methodology/modeling_shortcuts/
cascaded_subq)은 phase 09 존치 게이트가 **각자 스크립트 실행+JSON 으로 이중압력**(B1
§3.3) — 별도 존재-메타검사는 중복. "declared≠invoked" 갭의 실 차단은 run_gate verdict
아티팩트 하류 소비(B1 §5)가 대체했다.

| # | 위치 (실측) | 조치 |
|---|---|---|
| S1 | `phases/09-quality-gates.md` L477-483 — "§자동 CLI 호출" 의 9.rr cold_session_artefacts literal Bash 블록 | 블록 삭제 (9.tt runtime_guard_chain·9.uu cross_phase_context 블록은 존치) |
| S2 | `skills/theseus-orchestrator/SKILL.md` L180-186 — 9.rr 룰 절 전문 | 절 삭제 + L169-170 chain 구성 문구에서 "phase 09 entry = cold_session_artefacts" 및 "9.rr" 나열 제거 |
| S3 | `scoring/runtime_guard_chain.py` L205-224 — phase 09 entry hook = cold_session_artefacts sub-CLI | hook 제거(09 entry 의 게이트는 run_gate — phase 09 §첫 동작이 이미 배선) + `test_runtime_guard_chain.py` 동기 |
| S4 | `scoring/cold_session_artefacts.py`(+`test_cold_session_artefacts.py`) 및 페어 `scoring/generate_sprint40_artefacts.py`(+test — "부재 시 골격 emit" 보철, B1 이 미발화 게이트의 보철로 진단한 부류) | 4파일 은퇴(삭제). `scoring/phase_invoke_audit.py` L52 의 PHASE_ARTEFACTS 맵에서 `cold_session_artefacts`(및 generate 페어) 항목 제거 — phase 14 최종 감사가 은퇴 산출물을 요구하지 않도록 + `test_phase_invoke_audit.py` fixture 동기(L23-26/L54/L71-79/L113) |
| S5 | `conventions/hard-rule-9-extended.md` L17 — "**9.f** … `check_cold_session.py` 의무. exit 1 시 재진입" | 은퇴 표기로 교체: "9.f 은퇴(B1) — cold session 검증은 `run_gate.py` 의 `cold.isolation`/`plan.*` CheckSpec(값 기반). 스크립트는 `measure_cold_isolation` 의 라이브러리로 잔존" (1~2줄) |
| S6 | `conventions/phase-state-machine.md` L14/L20/L26/L161-180 — check_cold_session 을 "HARD-RULE 9.f post-hoc layer" 로 서술하는 layer-분리 절 | post-hoc layer 를 run_gate/meta_audit(cold.isolation) 로 재표기. **§1.3 C-PSM 키워드 수정과 동일 커밋 계열**(아니면 lint FAIL) |
| S7 | `conventions/regression-tdd-gate.md` L21/L169 — check_cold_session 9.f 참조 2건 | 동일 재표기 (C-RTG 키워드 리스트는 check_cold_session 미포함 — lint 무영향 실측) |

**주의(보수)**: `check_cold_session.py` **스크립트 자체는 삭제하지 않는다** —
`producers/measure_cold_isolation.py` 가 `build_report()` 를 라이브러리로 실 import
(phases/09 L22-26 서술과 일치, grep 실측). 은퇴한 것은 *CLI 의무 호출* 이며 B1 이 이미
수행 — B3 는 그 잔존 참조만 정리한다.

### 2.2 9.zz 잔존 불일치 (B1 부분 은퇴의 문서 동기 누락)

| # | 위치 | 조치 |
|---|---|---|
| S8 | `skills/theseus-orchestrator/SKILL.md` L134-135 — 9.zz 가 "phase 09 진입 + phase 14 진입 시 … 의무" | phase 09 분은 은퇴(phases/09 L499-503 이 이미 선언 — meta_audit 대체). "phase 14 진입 시" 단독으로 정정 |

### 2.3 가짜 self_lint 귀속 참조 — 전수 정리 (grep 프로토콜 + 실측 인벤토리)

**정의**: `*.md` 본문이 "self_lint C-<id> (fail|검증|강제)" 형태로 **등록되지 않은 룰에
집행을 귀속**하는 문구. 등록 여부의 단일 권위 = `self_lint.py` CHECKS 리스트.

**프로토콜 (WP-B3c 검증 스크립트 겸용, 신규 lint 룰 아님 — 1회성 grep):**

```
1. reg = self_lint.py CHECKS 등록 id 집합 (§1 조치 후: 118 엔트리)
2. skills/**/*.md 에서 (i) `self_lint\s+C-[A-Za-z0-9-]+` (ii) §헤더 `self_lint C-…`
   (iii) 표 검증-컬럼의 bare `C-…` 토큰을 수집
3. 후보 − reg − 화이트리스트 = 가짜 귀속 → 귀속어만 제거(내용 룰은 존치)
   화이트리스트(실측 false-positive): C-GAv2 의 소문자 절단(C-GA), C-RP 의 서브라벨
   표기(C-RP1~RP4 = [RP1]~[RP4]), 컨벤션 자체 룰 명명(귀속 없는 bare id — 예:
   C-IRPI-COUNT 류 컨벤션 내부 조항 번호)
4. 완료 = 스크립트 출력 0건 + 화이트리스트 목록 보고
```

**실측 인벤토리 (worktree, 설계 시점)**: 미등록 귀속 id **~40종 / ~35파일**. B1/B2 플래그분
포함 전량:

- **B1/B2 플래그 잔존분**: `C-RDS`(phases/09 L221-222·L391 §헤더, phases/04 L141,
  readme-numbers-from-summary.md L53, rubric-driven-doc-skeleton.md L126-222 다수) ·
  `C-GIS`(phases/09 L221) · `C-V6X`(reproducibility-doublecheck.md L64 §헤더) ·
  `C-VEX`(viewer-runtime.md L225-227 표 검증-컬럼 3건) · `C-MWDB`(plan-tree.md L64 —
  B2 F1-2 는 phases/06 쪽만 정리). C-GJM/C-MCC 는 잔존 0 (B1 정리 완료 — grep 실측).
- **본 설계 grep 이 추가 확정한 미등록 귀속** (각 1~4건): C-AB-DATA/C-AB-RATIO
  (analytical-bound-cross-validation) · C-AT-MP/C-AT-MP-AXIS/C-PT-SEQ(aide-tree) ·
  C-BAF(budget-aware-fallback) · C-CDM/C-MC/C-OWL/C-PMDF(phases/06, diagrams) ·
  C-CSQ(interview) · C-CT-HONEST(convention-traceability) · C-CXP(cross-process-anti-patterns) ·
  C-DHS(deliverable-hurdle-supremacy ×3) · C-DRS-EVIDENCE(domain-pack) ·
  C-DS(phases/05, directional-simplification) · C-DSF(phases/14) ·
  C-DSI-VERIFY(deep-semantic-intent — 주의: 같은 파일의 C-DSI 참조는 등록 룰과 **동명이인
  오귀속**, 데이터구조 룰이 아님 → 함께 정리) · C-IC(intent-completeness) ·
  C-IF-DIP/C-IF-PLAN(interface-first-parallel-impl) · C-MIF(multiverse-impl-fan-out) ·
  C-MM/C-MQG-FORMAT(mindmap-quality)/C-MQG(intent-extractor.md)/C-MRD-A-DEFAULT(phases/01) ·
  C-MSC(modeling-shortcuts) · C-PCR/C-PCR-L2(parallel-cold-review) ·
  C-PM(premortem-friction, phases/02·07 — 4건) · C-RDR-DOMAIN-AGNOSTIC(regression) ·
  C-SPF(surrender-phrase-forbid) · C-SRO(score-rubric-objectivity ×2) ·
  C-TBR-ANON(tournament-blind-rerun) · C-WUP(nfr-derivation) ·
  C-DCL-RERUN-LOG(dacapo-frontmatter-schema L194).

**정리 원칙 (내용 보존)**: 귀속어만 제거/재표기 — 예: "0 면 self_lint C-PM fail" →
"0 면 fail(본 컨벤션 §의무)". **내용 룰(의무 자체)을 지우지 않는다** — 그 판단은 B3 밖.
§1.2 삭제 8룰의 귀속(C-DCL-GATE 등)도 삭제 후 같은 프로토콜에 자동 포섭된다.

---

## 3. §11.5(a) 지시질량 재실측 — 프로토콜 + before/after 표

### 3.1 측정 프로토콜

- **baseline ref = `d0754f7`** (WP8 dogfood 커밋 = B1 구현 시작 `9307c81` 직전의 phase/
  convention 최종 상태. `git diff d0754f7 a728828 -- phases/ conventions/ HARD-CORE.md`
  = **empty 실측** — jw2~jw5·설계 커밋은 scoring/docs 만 편집. 따라서 d0754f7 과
  a728828 은 측정상 동치이며 과제 지정대로 d0754f7 을 쓴다).
- **측정 집합 3계층** (phase 진입 시 로드되는 지시문의 구조 그대로):
  - **A. always-load** = `skills/theseus-harness/HARD-CORE.md` + 양 `SKILL.md`
  - **B. phase 진입부** = `skills/theseus-harness/phases/*.md` 전체(16파일 — 진입 시 해당
    파일 전문 로드가 규약이므로 파일 전문이 곧 진입 지시문)
  - **C. lazy 컨벤션** = `skills/theseus-harness/conventions/*.md`(90파일 — INDEX router
    경유 조건부 로드; 참고 계층으로 병기)
- **측정 명령** (bytes + chars 병기 — B1 §6/B2 §3 프로토콜 그대로):

  ```bash
  # before (파일별): git show d0754f7:<path> | wc -c
  # after  (파일별): wc -c <path>
  # chars: python -c "print(len(open(f,encoding='utf-8').read()))"   # after
  #        git show d0754f7:<path> 를 임시파일로 받아 동일 len()      # before
  ```

- **보고 의무**: WP-B3d 가 아래 표의 after 열을 실측치로 채워 커밋 메시지 또는 본 문서
  갱신에 기록(B1 §6 동일). 측정 시점 = B3 전 WP 완료 후 working tree.

### 3.2 before / 중간 / after 표 (bytes — before·B2-후는 본 설계 시점 실측, B3-후는 목표)

| 계층 | before (`d0754f7`) | B2-후 (worktree 실측) | B1+B2 누적 Δ | B3-후 목표 |
|---|---:|---:|---:|---|
| A. HARD-CORE.md | 4,970 | 4,970 | ±0 | ≤ 4,970 |
| A. SKILL.md (harness) | 9,773 | 9,933 | +160 | ≤ 9,933 |
| A. SKILL.md (orchestrator) | 34,176 | 32,915 | −1,261 | ≤ 32,100 (S2/S8 ≈ −0.8KB) |
| **A 소계 (always-load)** | **48,919** | **47,818** | **−1,101 (−2.3%)** | **≤ 47,000** |
| B. phases/*.md (16) | 219,280 | 195,638 | **−23,642 (−10.8%)** | ≤ 194,600 (S1 + 가짜 귀속 ≈ −1.0KB) |
| **A+B (phase 진입 지시질량 — §11.5(a) 본체)** | **268,199** | **243,456** | **−24,743 (−9.2%)** | **≤ 241,600 (누적 ≥ −26.6KB, ≥ −9.9%)** |
| C. conventions/*.md (90) | 809,152 | 792,831 | −16,321 (−2.0%) | ≤ 788,000 (§1.2 짝 귀속 절 + §2.3 ≈ −5KB) |
| **총계 A+B+C** | **1,077,351** | **1,036,287** | **−41,064 (−3.8%)** | **≤ 1,030,300 (누적 ≥ −47KB)** |
| (참고) self_lint.py — 실행체, 지시질량 표 밖 | 3,466줄 | 3,374줄 | −92줄 | **≤ 3,230줄** (−144줄 이상) |

**정직 고지**: (i) B2-후 열은 uncommitted B2 잔여 수정 포함 worktree 실측 — WP-B2d/B3d
최종 실측이 확정치다. (ii) A+B 만이 §11.5(a) 의 "phase 진입 지시문"이고 C 는 조건부
로드라 과금이 균일하지 않다 — 세 계층을 분리 보고하는 이유. (iii) B3 자체의 감소분
(~−6KB)은 B1(−8.7KB, phase09 중심)·B2(−29KB 목표)보다 작다 — B3 의 주 순감은 지시질량이
아니라 **측정계(self_lint −144줄 + stale 스크립트 4파일 ~700줄)** 쪽이며 그렇게 부른다.

---

## 4. 순감 하드 룰 (WP 완료 조건)

1. **편집 대상 `*.md` 파일 총량(bytes) after ≤ before.** 개별 파일 순증 허용(재표기 시
   문구 교체로 소폭 증가 가능), 총량이 기준. 초과 시 그 WP 실패 — 재작업(B1 §6 판정 룰).
2. **`self_lint.py` 줄수 after ≤ 3,230** (−144줄 이상) + **등록 엔트리 126 → 118**.
3. **삭제 스크립트 순감 보고**: `cold_session_artefacts.py`(~400줄)+
   `generate_sprint40_artefacts.py`(~270줄)+테스트 2파일 — 실측 줄수를 WP-B3b 가 기록.
4. **신규 파일 0, 신규 lint 룰 0, 신규 CheckSpec 0** — B3 는 순감 sprint 다.

---

## 5. 회귀 안전 — 무엇이 안 깨지는지, 실측 근거로

1. **test_self_lint.py 무수정 통과**: 룰별 개별 테스트 0(실측 §1.1). 삭제 후 체크 수
   118 ≥ 18(하한), all_ok 는 남은 룰이 결정 — 아래 3의 편집 제약이 그것을 보장.
2. **커널 게이팅(B1) 무영향**: B3 는 `checks/`·`kernel/`·`run_gate.py`·`meta_audit.py`·
   `producers/`·manifest 를 편집하지 않는다. 완료 조건에 `kernel/manifest.py drift-check
   == []` + dogfood 재실행 verdict·counts 불변 + **B1d 리허설 fixture 재실행에서 run_gate
   exit 의미론 불변**을 포함(B2-WP-B2d 와 동일 규율).
3. **삭제 룰이 검사하던 문서와 존치 룰의 교차 제약 (grep 확정 — WP 지시에 박음):**
   - `dacapo-enforcement.md` 편집(C-DCL-GATE/MIN-LOOP 귀속 정리) 시 **존치 룰
     C-DCL-NO-FORWARD-PROJECT 의 4 키워드**("forward projection"/"측정 only"/
     "anticipated"/"C-DCL-NO-FORWARD-PROJECT") 보존 의무.
   - `phase-state-machine.md` 편집(S6)과 C-PSM 키워드 수정(§1.3)은 동일 커밋 계열.
   - `intra-phase-dacapo-loop.md` 무수정(C-DCL-FRESH-UNIVERSE 존치 키워드 파일).
   - 컨벤션 **파일 삭제 0** → C2/C11/C-IDX-1/C-IDX-2/INDEX row 전부 무영향.
   - `phases/06-plan.md` L546-550 정리는 §헤더/리스트 행 삭제만 — 같은 파일의 존치 룰
     (C-PPC/C-RES/C-IDC/C-CLS/C-STT/C-PMT/C-CNS/C-UNIV-CREATED-AT/C-DCL-FLOW-LOG 수정본)
     키워드는 다른 §에 있어 무영향(라인 실측).
4. **pytest 동기 목록(전부 §2 소속)**: 삭제 — `test_cold_session_artefacts.py`/
   `test_generate_sprint40_artefacts.py`; 수정 — `test_phase_invoke_audit.py`(fixture
   에서 은퇴 산출물 제거)/`test_runtime_guard_chain.py`(09-entry hook 제거 반영).
   `check_cold_session.py` 존치로 `measure_cold_isolation` 테스트 무영향.
5. **완료 조건 (매 WP)**: `python self_lint.py` all_ok=True + `pytest scoring/ -q` 전건 +
   drift-check [] + dogfood verdict·counts 불변.

---

## 6. 롤아웃 WP (opus/sonnet) + 값 기반 완료 조건

| WP | 내용 | 권장 모델 | 완료 조건 (값 기반) |
|---|---|---|---|
| **WP-B3a** | self_lint 순감 — 8룰 삭제(§1.2, 함수+등록행) + C-PSM/C-DCL-FLOW-LOG 키워드 수정(§1.3) + ID 위생 2건(C-PTRC/C-SAT 리네임 + 문서측 표기 동기) + 삭제 룰의 짝 prose 귀속 절 정리(§1.2 우측 열 — dacapo-enforcement/skip-sentinel/shadow-grader/mandatory-rerun/phase-lineage-viewer/regression/MIGRATION/phases 06) | sonnet | (i) self_lint all_ok=True + 등록 118 엔트리, (ii) `self_lint.py` ≤ 3,230줄, (iii) pytest 전건, (iv) §5.3 교차 제약 키워드 보존을 grep 으로 확인(C-DCL-NO-FORWARD-PROJECT 4 키워드 등), (v) 편집 md 총량 after ≤ before |
| **WP-B3b** | stale 정리 — S1~S8(§2.1~2.2): 9.rr 블록·절 삭제, cold_session_artefacts/generate_sprint40 4파일 은퇴, runtime_guard_chain 09-entry hook 제거, phase_invoke_audit 맵·테스트 동기, 9.f/9.zz 잔존 참조 재표기 | sonnet | (i) `grep -rn "cold_session_artefacts\|9\.rr" skills/` = 0건(docs/design·sprints 회고 제외 목록 보고), (ii) `grep -rn "check_cold_session" skills/` 잔존이 라이브러리 사용처(measure_cold_isolation·phases/09 §해설·S5 은퇴 표기)뿐임을 목록으로 보고, (iii) pytest 전건 + dogfood verdict·counts 불변, (iv) 편집 md 총량 after ≤ before |
| **WP-B3c** | 가짜 self_lint 귀속 전수 정리(§2.3) — ~40 id/~35파일, 귀속어만 제거(내용 룰 존치), 프로토콜 스크립트(1회성 grep — scratchpad, 저장소 편입 금지)로 검증 | sonnet | (i) §2.3 프로토콜 출력 0건 + false-positive 화이트리스트 목록 보고, (ii) self_lint all_ok, (iii) 편집 md 총량 after ≤ before |
| **WP-B3d** | **재실측 + 완료 게이트** — §3 표 after 열 전체 실측(bytes+chars) 기록 + §4 하드 룰 판정 + 전 검증 재실행 | sonnet | (i) §3.2 표 실측 기록(A+B ≤ 241,600 / self_lint ≤ 3,230줄 판정), (ii) 편집 파일 총량 after ≤ before 하드 룰 판정, (iii) pytest 전건 + self_lint all_ok + drift-check [] + dogfood verdict·counts 불변 + **B1d 리허설 fixture 재실행에서 run_gate exit 0/1 의미론 불변 관측·기록**, (iv) 결과를 본 문서 갱신 또는 커밋 메시지에 수치 기록 |

**의존**: WP-B3a ∥ WP-B3b ∥ WP-B3c 병렬 가능 — 단 파일 교집합 2건 순서 강제:
`phases/09-quality-gates.md` 는 B3b(9.rr 블록) → B3c(C-RDS/C-GIS 귀속) 순,
`phase-state-machine.md`/`dacapo-*` 는 B3a 가 소유. → **WP-B3d 가 B3 의 완료 게이트다**
— (iii) 왕복 검증 없이 B3 완료 선언 불가(B1d/B2d 와 동일 규율).

---

## 7. 비목표 · 정직 고지

1. **진짜 정합 룰 삭제 금지 (과다 삭제 경계).** §1.4 의 116 존치 룰은 전량 유지 —
   특히 경계 사례로 판단한 C-PTSS/C-DCL-FRONTMATTER/C-DIAG-AND-COVERAGE 는 "커널이 결과는
   보지만 정의·granularity 는 못 본다"는 이유로 **존치 쪽으로** 판정했다(애매→존치).
   후속 sprint 이 커널 producer 로 해당 차원을 실측하게 되면 그때 재분류한다.
2. **viewer 대형 컨벤션 본문 다이어트는 재이월.** B2 §6.7 이 "B3 몫"으로 넘긴
   `phase-lineage-viewer.md`(27.5KB)/`viewer-runtime.md`(11KB) 등의 본문 압축은 —
   C-PLV 삭제로 **구조적 차단은 해제**되지만 — 본 B3 의 헌장(측정계 다지기) 밖이라
   후속(벤치 전 별도 판단)으로 재이월한다. 그 판단의 책임은 본 문서가 진다.
3. **내용 룰의 존폐 판단 아님.** §2.3 은 가짜 *귀속* 만 제거한다 — "derived_improvements
   ≥ 1" 같은 의무 자체의 타당성 재평가는 벤치 데이터 이후.
4. **미구현 룰의 구현 아님.** C-RDS/C-PM 등 선언만 있던 룰을 self_lint 에 구현하는 것은
   순증(§11.1 위반)이라 하지 않는다 — 해당 의무가 게이트 자격을 얻으려면 producer +
   CheckSpec 경로(§11.2)뿐이다.
5. **측정 한계 정직**: §3 의 B2-후 수치는 uncommitted worktree 실측 — B2d 커밋 후
   WP-B3d 실측이 확정치. bytes 는 한국어 UTF-8 특성상 chars 의 ~1.5배 — 두 단위 병기로
   해석 왜곡을 막는다. "지시질량 감소 → 외부 점수 개선"은 여전히 가설이며 §11.5(b)
   벤치로만 확증된다 — B3 가 값으로 증명하는 것은 감소량 자체뿐이다.
6. **커널/CheckSpec/manifest/벤치 harness 무관여** — 전부 B3 밖.

---

## 8. 역추적 매핑

| 근거 | 본 설계 대응 |
|---|---|
| 커널 §11.1 "측정 가능한 것을 grep 하던 C-룰 삭제·강등, self_lint 는 순수 마크다운 정합만" | §1.2 삭제 8(커널 실측 차원의 문서 핀) + §1.4 존치(마크다운 정합 전량) |
| 커널 §11.5(a) 성공 측정 = 지시질량 감소 | §3 프로토콜 + before(`d0754f7` 실측 268,199 bytes A+B)/after 표 + §4 하드 룰 |
| B1 §3.2D "광역 self_lint 순감(dacapo/regression/shadow 계열)은 B3 몫" | §1.2 — dacapo 4(GATE/SENTINEL/SHADOW/MIN-LOOP) + regression 1(RDLR) + 인접 3(DCMR/MV1/PLV) |
| B2 §4.3 가짜 참조 구분(C-MWDB/C-BSL/C-IPI/C-GIS/C-TBR-UNION/C-VEX) + B1 §3.2D 주(C-V6X/C-GJM/C-MCC/C-RDS) | §2.3 전수 인벤토리(~40 id) — 잔존분(C-RDS/C-GIS/C-V6X/C-VEX/C-MWDB) + 신규 확정분, C-GJM/C-MCC 잔존 0 실측 |
| B2-F3 viewer advisory 강등 → 파일존재 강제 stale | §2.1 — 9.rr `cold_session_artefacts.py` 계열 은퇴(13 중 7 산출물의 의무가 이미 해제 — 실측 대조) |
| B2 §2.2-3 rerun 의무 → advisory | §1.2 C-DCL-MIN-LOOP-ATTEMPT/C-DCMR 삭제(강등-모순 mandate 핀) |
| B1 §5 honor-system 완화(verdict 하류 소비) | §2.1 근거 — 존재-메타검사 CLI 의 대체물 명시 |
| P2(키워드-박힘)·P3(prose regex 집행) 재발 방지 | §1.2 전 행의 (b) 근거 + §1.3 버전-라벨 핀 제거 + §7.4(미구현 룰 구현 금지) |
| B1 §6/B2 §3 순감 프로토콜·왕복 관측 규율 | §3 방식 계승 + §6 WP-B3d 완료 게이트(B1d fixture 재실행 포함) |
| 보수 원칙(과다 삭제 경계) | §1.1 기준 (c) + §1.4 경계 사례 3건의 존치-방향 판정 + §7.1 |

---

*본 문서는 설계 확정본이다. 사용자 리뷰 후 §6 WP 순서로 구현을 전개한다.*
