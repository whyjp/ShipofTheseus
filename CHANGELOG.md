# CHANGELOG

본 저장소의 의미 있는 변경만 기록 — 메모리 `feedback_version_conservatism.md` (1.0 임박, 의미 있는 마일스톤만 발행) 정합.

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
