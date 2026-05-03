# CHANGELOG

본 저장소의 의미 있는 변경만 기록 — 메모리 `feedback_version_conservatism.md` (1.0 임박, 의미 있는 마일스톤만 발행) 정합.

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
