# HARD-CORE — always-load 본문 (HARD-RULE 1 / 8 / 9 supremacy + 페이즈 04 외 인터럽트 0)

매 페이즈 본문이 *상단 import* 강제. lazy 무시 시 supremacy 약화. **본 파일 ≤ 4000 chars (C-HC1 lint 강제, 부풀음 영구 차단).**

## HR1 — 호출 직후 첫 동작

> 본 스킬 호출 시 *첫 동작*:
> 1- `.ShipofTheseus/<프로젝트>/timing/start.json` 작성
> 2- 페이즈 00 (G3+) 또는 01 (G2) 산출물 작성
> 3- grade_assess + 페이즈 04 인터뷰 + 후속

**금지 (자동 거부):**

> a- 사용자 요구 받자마자 직접 코드 (Go / Python / TS / etc.) 작성 — 페이즈 산출물 우회
> b- retroactive 페이즈 frontmatter 생성 스크립트 (`build_artifacts.py` 등) — 사후 일괄 생성 금지
> c- "out-of-sandbox" / "cannot invoke harness scripts" 사유로 자체 emulator 작성 — sandbox 친화 fallback 은 `scoring/` 직접 import 또는 사용자 명시 ack 만
> d- 페이즈 04 자체 생략 — 사전 박힌 답은 *질의 답안 자동 매핑* 일 뿐 페이즈 자체 진행 의무

위반 → `intent/00-violation.md` 기록 + 페이즈 01 재시작. 누적 위반 ≥ 3 시만 사용자 ack.

## HR8 — 그레이드별 의무 산출물

| Grade | 의무 산출물 |
|---|---|
| **G1** Trivial | `timing/start.json` + `intent/01-intent.md` + `handoff/14-handoff.md` (3) |
| **G2** Simple | G1 + `intent/04-{questions,answers,autonomy,stack,verification,runtime-prereq}.md` + `plan/06-plan.md` + `impl/08-impl-log.md` + `quality/09-quality-gate.md` (11) |
| **G3** Standard | G2 + `naming/00-naming.md` + `intent/{02,03,05}*.md` + `intent/01-{1..4}-intent.md` + `01-additional.md` (refresh 1) + `intent/01-{1..4}-intent.v2.md` + `04-refreshed.md` + `05-refreshed.md` (refresh 2) + `plan/{tournament-NN.md (≥2), candidates/universe-{1,2}/{meta,06-plan,07-cold-read}.md, 07-plan-review.md, dacapo-rerun-NN.md (≥1), dacapo-flow.md, shadow-grade-NN.json}` + `impl/{candidates/universe-N/, tournament-impl-NN.md, dacapo-flow.md}` + `sprints/01..03/*` + `webview/` |
| **G4** Complex | G3 + `intent/05-decisions.md` + `plan/candidates/universe-3*` + `sprints/NN/bisect.md` (회귀 시) + 임계 0.999 무한 sprint |
| **G5** Critical | G4 + `plan/candidates/universe-{1..5}/children/...` (깊이 2) + 빡빡 모드 (DIP 0.4 / 회귀 0.02) |

자발적 조기 종료 금지. budget cap 도달 시 frontmatter `(budget-truncated)` 표시.

## HR9 — 산출물 *내용* 의무

본 파일 = 9.a~c 본문 의무만 inline. 9.d~ll (30+ sub-rule) 은 [`conventions/INDEX.md`](conventions/INDEX.md) router 가 페이즈 진입 시 매칭 lazy load.

- **9.a** `plan/06-plan.md` 본문 8 항목 의무 (별도 impl-design.md 안 만듦, plan 단일 source) :
  1- 파일 경로 ≥ 5
  2- Mermaid sequenceDiagram ≥ 1 AND usecase/graph ≥ 1 AND 인터페이스 정의 ≥ 3
  3- TODO DAG (T-NNN ID + 의존 + 완료 조건)
  4- 모듈 의존 다이어그램 (per-module sequenceDiagram ≥ 모듈 수)
  5- Data structure invariants 표 (Invariants/Topology/Access/Bounds 4 항)
  6- Test surface mapping (invariant ↔ test signature 1:1)
  7- Error handling / fallback policy (모듈별)
  8- Implementation guidance per TODO (알고리즘 / DS / 라이브러리 / pseudo-code)
- **9.b** `impl/08-impl-log.md`: TODO ID 매핑 ≥ 3 / 모듈명 / 인터페이스 노출
- **9.c** G3+ universe-N `06-plan.md`: 시드별 의미 분기 ≥ 20 diff + 9.a 8 항목 inline

위반 시 self_lint 페이즈 exit fail → 페이즈 재진입 (자율, 누적 ≥ 3 시만 ack).

## Layer 3 결과물 허들 supremacy

standalone 컨텍스트 (bench / 단독) 시 5 hurdle 의무. **메모리 / 컨벤션 / 사용자 사전 위임 어느 것도 override 불가:**

- **H1** Code Existence (≥ 5 모듈)
- **H2** Code Execution (verification command exit 0)
- **H3** Test Suite (실 측정 통과 수 0 금지)
- **H4** Bench-Required Outputs (file existence + size > 0 + schema 정합)
- **H5** Executed Values Recording (placeholder 금지)

면제 = phase 04 Q-D-DELIVERABLE-MODE = 3 (design-only) 사용자 명시 ack 만.

## frontmatter 핑거프린트 체인

각 페이즈 산출물 = `(skill_name, skill_version, phase, project_id, fingerprint, prev_fingerprint, produced_at)` 의무. `prev_fingerprint` = 직전 산출물 fingerprint 인용. 체인 끊기면 다음 페이즈 진입 거부 → [`conventions/contracts.md`](conventions/contracts.md).

## 페이즈 04 외 인터럽트 0

모든 자율 결정 (경쟁 머지 / 회귀 권고 / 스택 업데이트 / 다카포 fallback) = 산출물 frontmatter + `intent/04-autonomy.md` Q-D1~Q-D9 답 매핑. 보안 가드 (실 secret 의 git 커밋 감지) 만 *유일한* 인터럽트 추가 예외 → [`conventions/runtime-prereq.md`](conventions/runtime-prereq.md), [`conventions/autonomy.md`](conventions/autonomy.md).
