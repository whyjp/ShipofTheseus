---
skill_name: theseus-harness
skill_version: 0.2.0
phase: 06-plan
project_id: theseus-self
project_run: 20260501-184946
fingerprint: sha256:c21dd8c126cf1ce98be5c15123a83e19be8e4e2cf6b89abd5ed7ee690208bc64
prev_fingerprint: sha256:8b28c3d8165f5bc6276500fbe62a01fa53c3cb82f52a3465bc447deb42364dfe
produced_at: 2026-05-01T18:49:46Z
producer_agent: human-bootstrap
---
> **시작:** 2026-05-01T18:53:00Z · **종료:** 2026-05-01T18:55:00Z · **소요:** 2분
> **누적 경과:** 5분 14초 · **현재 시각:** 2026-05-01T18:55:00Z

# 보완 계획 — 1차 (v0.3.0 후보)

## 한 줄 요약
**1차 자체 비평이 발견한 9개 갭과 3개 미스초이스를 v0.3.0 의 PR 백로그로 변환.** TODO 11 개, DAG acyclic, 각 TODO 는 한 서브에이전트 호출에 끝낼 단위.

## 아키텍처 개요
본 회차는 본 저장소 *명세 문서* 의 보강만 — 새 코드 모듈 추가 없음. self_lint 체크 5 개 추가 + phase/agent 본문 보강 + 추가 sample 입력 + INSTALL/BOOTSTRAP 교차 링크.

## TODO 목록

### § 1. self_lint 확장 (C12–C16)

- **T-001 — self_lint C12 추가: phases/06-plan.md 가 시퀀스 다이어그램 동봉 의무 명시**
  - 모듈: `scoring/self_lint.py`
  - 레이어: test
  - 의존: []
  - 완료 조건: `check_phase_diagram_clauses` 함수, "시퀀스 다이어그램" 또는 "Mermaid" 가 06-plan.md 본문에 존재 검사
  - 테스트: `test_self_lint.py::test_c12_phase06_diagram_clause`
  - 목 표면: n/a

- **T-002 — self_lint C13: phases/08-implement.md 가 sh+bat 강제 본문 명시**
  - 의존: []
  - 완료 조건: 08-implement 본문에 "sh" 와 "bat" 모두 등장
  - 테스트: `test_self_lint.py::test_c13_phase08_script_clause`

- **T-003 — self_lint C14: quality-gate.md 가 frontmatter 누락 자동 fail 명시**
  - 의존: []
  - 완료 조건: quality-gate.md 본문에 "frontmatter" 와 "fail" 같은 줄에 등장
  - 테스트: `test_self_lint.py::test_c14_quality_gate_frontmatter`

- **T-004 — self_lint C15: regression-analyst.md 가 경쟁 컨벤션 사용 가능성 언급**
  - 의존: []
  - 완료 조건: regression-analyst.md 가 `competition.md` 또는 "경쟁" 을 언급
  - 테스트: `test_self_lint.py::test_c15_regression_competition`

- **T-005 — self_lint C16: competition.md 가 critic / plan-reviewer 트리거 책임 명시**
  - 의존: []
  - 완료 조건: competition.md 가 "critic" 또는 "plan-reviewer" 를 트리거 주체로 언급
  - 테스트: `test_self_lint.py::test_c16_competition_triggers`

### § 2. phase / agent 본문 보강 (M1, M3, 발견 6)

- **T-010 — phase 06/08 에 경쟁 컨벤션 트리거 룰 박음**
  - 모듈: `phases/06-plan.md`, `phases/08-implement.md`
  - 의존: [T-005]
  - 완료 조건: 두 페이즈 본문에 "competition.md 의 트리거 조건이 충족되면 경쟁 모드 진입" 명시
  - 테스트: T-005 의 self_lint 체크가 통과

- **T-011 — agent 들에 fingerprint 강제 박음 (M1 해소)**
  - 모듈: `agents/intent-extractor.md`, `agents/planner.md`, `agents/implementer.md`, `agents/clarifier.md` 등 산출물 작성 에이전트
  - 의존: []
  - 완료 조건: 각 에이전트 "동작" 섹션에 "산출물 작성 직후 `python scoring/fingerprint.py compute --file <path> --prev <prev>` 호출" 명시
  - 테스트: self_lint C17 (신규) — 산출 작성 에이전트가 fingerprint 호출 명시 검사

- **T-012 — webview-builder 가 server.ts 에 Mermaid 자동 렌더 추가 명시 (발견 6)**
  - 모듈: `agents/webview-builder.md`
  - 의존: []
  - 완료 조건: webview-builder 가 Mermaid 코드 펜스를 SVG 로 렌더하는 클라이언트 lib (mermaid npm 패키지) 를 React 컴포넌트로 통합 명시
  - 테스트: self_lint C18 (신규)

### § 3. 샘플 / 문서 보강 (발견 8, 9)

- **T-020 — sample-inputs-dip-violation.json 추가**
  - 모듈: `templates/sample-inputs-dip-violation.json`
  - 의존: []
  - 완료 조건: dip_violation=true 케이스, score 0.6 cap 으로 sample 채점 결과 임계 미달 보임
  - 테스트: `test_score.py::test_sample_dip_violation_cap`

- **T-021 — INSTALL.md 가 BOOTSTRAP.md 와 self-check 언급**
  - 모듈: `INSTALL.md`
  - 의존: []
  - 완료 조건: INSTALL 6번 점검 섹션에 `scripts/self-check.sh` 명령과 BOOTSTRAP.md 링크
  - 테스트: self_lint C9 보강 — `BOOTSTRAP.md` 와 `self-check` 둘 다 언급 검사

### § 4. 회차 시계열 (S2 해소)

- **T-030 — 자기 평가 회차 보존 룰 BOOTSTRAP.md 명시**
  - 모듈: `BOOTSTRAP.md`
  - 의존: []
  - 완료 조건: 회차마다 `.ShipofTheseus/theseus-self/sprints/NN/quality-gate.md` 를 누적 보존, 회차 간 점수 diff 절차 명시
  - 테스트: 사람 리뷰 (정량 검사 어려움)

## 의존 DAG

```
T-001..T-005  (self_lint 5 체크 신규, 병렬)
   │
T-010  (페이즈 06/08 보강, T-005 의존)
T-011  (에이전트 fingerprint 강제)
T-012  (webview-builder Mermaid)
T-020  (DIP sample)
T-021  (INSTALL 보강)
T-030  (회차 시계열)
```

T-001 ~ T-005, T-011, T-012, T-020, T-021, T-030 은 모두 병렬 가능 (서로 의존 없음). T-010 만 T-005 에 직렬.

## 설계 근거
- **DIP 직접 적용:** self_lint 의 새 체크는 *명세 문서* (페이즈/에이전트/컨벤션) 가 *추상 룰* (컨벤션) 에 의존하는지 검사 — 콘크리트 룰을 본문에 박지 않으면 fail.
- **SoC:** self_lint 는 검사기 / phase·agent 는 명세 / 컨벤션은 룰 추상 / fingerprint 는 무결성 — 네 책임이 분리.
- **경쟁 트리거 명시화:** v0.2.0 의 경쟁 컨벤션이 *적용 의무* 로 박혀야 의미 있다.

## 보류 항목 (다음 회차 v0.4.0+)
- 모듈 분해 (`skills/theseus-orchestrator` + …) — 회차 2~3 누적 후.
- 경쟁 결과의 자동 머지 알고리즘 (현재는 critic/planner 가 수동) — Sonnet 모델로 자동화 검토.
- 사용자 인터뷰 회차의 답을 *프로젝트 간* reference 로 활용 (예: 비슷한 도메인의 이전 답을 시드로).
