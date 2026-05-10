---
name: theseus-orchestrator
version: 0.9.39
description: theseus-harness 의 15 페이즈 자율 driver — entry point. 페이즈 04 인터뷰 후 인터럽트 0. 본 entry skill = 순서 + 인터럽트 정책 + 그레이드 라우팅 단일 책임. 산출물 내용 컨벤션은 ../theseus-harness/conventions/ 단일 source — 페이즈 진입 시 매핑된 본문만 lookup.
---

# theseus-orchestrator — 사용자 entry skill

## 한 줄 요약

**본 스킬은 사용자 entry point.** 콘텐츠 source 는 [`../theseus-harness/`](../theseus-harness/) 동반 필수. 호출되면 14 페이즈를 자율 driver 로 진행 — 페이즈 04 인터뷰 1회 후 인터럽트 0.

## HARD-RULE — 본 스킬 호출 직후 첫 동작 (위반 시 즉시 정지)

> 본 스킬이 호출되면 당신의 *첫 동작* 은 다음이다 — 다른 어떤 작업도 우선 안 됨:
>
> 1- `.ShipofTheseus/<프로젝트>/timing/start.json` 작성 (시작 시각).
> 2- 페이즈 00 (G3+) 또는 페이즈 01 (G2) 의 산출물 작성 — `.ShipofTheseus/<프로젝트>/{naming/00-naming.md | intent/01-intent.md}`.
> 3- 그 *다음* 에 grade_assess + 페이즈 04 인터뷰 + 후속 페이즈 진행.
>
> **금지 (자동 거부 — 실행 에이전트 의 첫 동작이 다음이면 본 스킬 위반):**
>
> a- 사용자 요구를 받자마자 *직접* 코드 (Go / Python / TS / etc.) 작성 — 페이즈 산출물 우회.
> b- `.ShipofTheseus/<프로젝트>/_tools/` 또는 `code/` 디렉터리에 *retroactive* 페이즈 frontmatter 생성 스크립트 (`build_artifacts.py` 등) 작성. **하네스의 frontmatter 는 페이즈가 *진행되며 박는 것* 이지 사후 일괄 생성 대상이 아님.**
> c- "out-of-sandbox" / "cannot invoke harness scripts" 등의 사유로 자체 emulator 작성 — sandbox 친화 fallback 은 [`../theseus-harness/scoring/`](../theseus-harness/scoring/) 의 도구를 *직접 import* 하거나 사용자에게 명시적 ack 요청.
> d- 페이즈 04 인터뷰의 "사전 박힌 답" 지시를 *페이즈 04 자체 생략* 으로 해석. 사전 답은 *질의 답안 자동 매핑* 일 뿐 페이즈 자체는 진행되어야 함 (`intent/04-questions.md` + `04-answers.md` 산출물 의무).
>
> **위반 시 처리** — 실행 에이전트 가 위 a-d 중 어느 하나라도 시작하면 본 스킬은 즉시 정지 + `intent/00-violation.md` 에 위반 사유 기록 + 페이즈 01 부터 정상 진행 재시작.
>
> **HARD-RULE 8 — 그레이드별 의무 산출물 (모든 페이즈 완주 강제):**
>
> 본 스킬 호출 후 종료 시 다음 산출물이 *모두* `.ShipofTheseus/<프로젝트>/` 에 박혀 있어야 함. 누락 = 본 스킬 미완. budget cap 도달 시에도 *최소한 frontmatter 만이라도* 박고 `(budget-truncated)` 표시.
>
> | Grade | 의무 산출물 |
> | ----- | ---------- |
> | **G1** Trivial | `timing/start.json` + `intent/01-intent.md` + `handoff/14-handoff.md` (3개) |
> | **G2** Simple | G1 + `intent/04-{questions,answers,autonomy,stack,verification,runtime-prereq}.md` + `plan/06-plan.md` + `impl/08-impl-log.md` + `quality/09-quality-gate.md` (총 11개) |
> | **G3** Standard | G2 + `naming/00-naming.md` + `intent/{02,03,05}*.md` + **refresh 1**: `intent/01-{1,2,3,4}-intent.md` + `intent/01-additional.md` + **refresh 2**: `intent/01-{1,2,3,4}-intent.v2.md` + `intent/04-refreshed.md` + `intent/05-refreshed.md` + `plan/{tournament-NN.md (≥ 2), candidates/universe-{1,2}/{meta,06-plan,07-cold-read}.md, 07-plan-review.md, dacapo-rerun-NN.md (≥ 1), dacapo-flow.md, shadow-grade-NN.json}` (plan body 8 항목 의무 — implementation guidance 포함, sprint-21 정공) + `impl/{candidates/universe-N/실 코드 + tests, tournament-impl-NN.md (≥ 1), shadow-grade-impl-NN.json, dacapo-rerun-impl-NN.md (≥ 1), dacapo-flow.md, 08-impl-log.md (canonical, ≥ winner 80% inline 또는 shared schema)}` + `sprints/01..03/{inputs,report}.json` + `webview/` (8 탭) (총 45+) |
> | **G4** Complex | G3 + `intent/05-decisions.md` + `plan/candidates/universe-3*` + `sprints/NN/bisect.md` (회귀 발생 시) + 임계 0.999 도달까지 무한 sprint |
> | **G5** Critical | G4 + `plan/candidates/universe-{1..5}/children/...` (깊이 2) + 멀티버스 강제 + 빡빡 모드 가드 |
>
> **자발적 조기 종료 금지** — 실행 에이전트 가 페이즈 06 까지만 만들고 "끝" 으로 보고하면 본 스킬 위반. 위 표의 의무 산출물을 *모두* 박아야 정상 종료.
>
> **부분 채움 OK** — 본문이 한 줄이라도 frontmatter (skill_name / skill_version / phase / fingerprint / prev_fingerprint / created_at) 는 박혀야 함. 본문 truncated 시 마지막 줄에 `<!-- budget-truncated -->` 명시.
>
> **HARD-RULE 9 — 산출물 *내용* 컨벤션 (페이즈별 lookup 인덱스, 본문은 [`../theseus-harness/conventions/`](../theseus-harness/conventions/) 단일 source):**
>
> 본 entry skill 의 책임은 *순서 + 인터럽트 + 그레이드 라우팅* (HARD-RULE 1, 8). 산출물 *내용* 컨벤션은 본 prompt 안에서 *전부 읽지 않음* — 페이즈 진입 시 매핑된 컨벤션 본문만 lookup. 본 prompt context 에서 27 항목 prose 가 빠져 HARD-RULE 1 (페이즈 순서) 의 cognitive bandwidth 가 회복됨. self_lint.py 가 페이즈 exit 시 모두 검증.
>
> | 페이즈 | 컨벤션 (lookup) |
> | --- | --- |
> | 모든 phase enter/exit | **phase-state-machine** (sprint-34 신규, runtime 단조성 게이트 + frontmatter forgery 차단) |
> | 01 의도 | **mindmap-quality** (sprint-37 PR-AD 통합) · deep-semantic-intent · **domain-pack §2 §3** (sprint-37 PR-AG 통합: model + research-stacking) · intent-completeness · **intent-optional-disambiguation** (sprint-34, optional marker 검출 시) |
> | 04 인터뷰 | commentary-policy · runtime-prereq · interview · **intent-optional-disambiguation** (sprint-34, Q-OPT-NN + optional-decisions.md) |
> | 04 → 05 (refresh 1) | **intent-refresh §3.1** (sprint-17 by, sprint-37 PR-AA 통합, 01-{1..4}-intent + 01-additional 의무) |
> | 05 → 06 (refresh 2) | **intent-refresh §3.2** (sprint-19 ci, sprint-37 PR-AA 통합, 01-{1..4}-intent.v2 + 04-refreshed + 05-refreshed 의무, 사용자 ack 없음 자율) |
> | 05 비평 | directional-simplification · premortem-friction · **domain-pack §4** (failure patterns, sprint-37 PR-AG 통합) · parallel-cold-review |
> | 06 계획 | per-module-diagram-fan-out · multiverse-width-default-bump · contested-decision-multiverse · measurement-contract · rubric-driven-doc-skeleton · intra-phase-dacapo-loop · dacapo-enforcement (**HARD-RULE 9.p**) · dacapo-frontmatter-schema · shadow-grader-zero-context · dacapo-skip-sentinel · dacapo-flow-trace · data-structure-invariants · plan-tree · tournament-blind-rerun · interface-first-parallel-impl · **dacapo-mandatory-rerun (HARD-RULE 9.gg)** · **plan-tournament-scoring-strict (9.hh)** · **canonical-not-stub (9.ii)** · **cross-phase-shared-context (9.ll)** · **subagent-trigger** (sprint-34, phase 06 exit 시 analyze-todos 호출) |
> | 08 구현 | intra-phase-dacapo-loop · simulation-physical-invariants · idiomatic-code-quality · experimental-control-protocol · deliverable-hurdle-supremacy · multiverse-impl-fan-out · **impl-multiverse-strict (HARD-RULE 9.jj, 7 조건 게이트)** · **dacapo-mandatory-rerun (9.gg)** · **canonical-not-stub (9.ii)** · dead-code-zero · magic-number-traceability · submission-portability · reproducibility-doublecheck · **subagent-trigger** (sprint-34) · **regression-tdd-gate** (sprint-34, 매 sub-impl + dacapo step F) |
> | 09 게이트 | rubric-targeted-quality-gates · score-rubric-objectivity · test-invariants · nfr-derivation · readme-numbers-from-summary (**HARD-RULE 9.bb**) · reproducibility-doublecheck (**9.cc**) · magic-number-traceability (**9.dd**) · dead-code-zero (**9.ee**) · submission-portability (**9.ff**) |
> | 10 스프린트 | intent-plan-impl-sprint-trinity · grader-in-sprint · **regression §2** (sprint loop, sprint-37 PR-AE 통합) · budget-saturation-loop · **sprint-narrative §2 §4** (delta + lessons/stagnation, sprint-37 PR-AF 통합) · evidence-driven-sprint-planning · **regression-tdd-gate** (sprint-34, sprint iteration trigger) |
> | 11 회귀 바이섹트 | **regression §3** (lint autogen, sprint-37 PR-AE 통합) · **regression-tdd-gate** (sprint-34, regression_log binary search) |
> | 12 theseus-view | prebuilt-shell-runtime-json · phase-lineage-viewer · viewer-runtime · **(sprint-40 PR-C) phase 12 §종료 게이트 — webview/{index.html, data/webview.json, assets/{app.js, mermaid.min.js, marked.min.js, styles.css}} 6 파일 강제 + webview/exit_gate.json emit** · webview-builder agent invoke 의무 |
> | 13 interactive-viewer | prebuilt-shell-runtime-json · viewer-runtime · interactive-viewer-builder agent · **(sprint-40 PR-C) phase 13 §종료 게이트 — interactive-viewer/{index.html, dashboard.json, assets/app.js} 강제 + dashboard.json widgets ≥ 1 (G3+) / ≥ 3 (G4+, kpi_grid+topology+metric_chart 의무) + interactive-viewer/exit_gate.json emit** · **(sprint-40 PR-D) HARD-RULE 9.nn — G4+ phase 13 invoke step 강제** |
> | 14 핸드오프 | results-decision-mapping · phase-lineage-viewer (**sprint-34 gantt + 모든 그레이드**) · decision-support-framing |
>
> **9.a~c 본문 의무 (페이즈 06/08 산출물 구조)** — 본 entry skill 에 직접 박힘 (실 코드 외부 repo 따라 구현 가능 의무):
> - 9.a `plan/06-plan.md` 본문 8 항목 의무 (별도 impl-design.md 안 만듦, plan 단일 source — plan + impl-log 응집 보존):
>   1. 파일 경로 ≥ 5
>   2. **Mermaid sequenceDiagram ≥ 1 AND Mermaid usecase/graph ≥ 1 AND 인터페이스 정의 ≥ 3** (셋 다 의무)
>   3. TODO DAG (T-NNN ID + 의존 + 완료 조건)
>   4. 모듈 의존 다이어그램 (per-module sequenceDiagram ≥ 모듈 수)
>   5. Data structure invariants 표 (Invariants/Topology/Access/Bounds 4 항)
>   6. Test surface mapping (invariant ↔ test signature 1:1)
>   7. Error handling / fallback policy (모듈별)
>   8. Implementation guidance per TODO (알고리즘 / DS / 라이브러리 / pseudo-code — implementer 가 따라가는 디자인)
> - 9.d Da Capo산출물 본문 의무 (frontmatter 외): `tournament-NN.md` (6-dim sub-scores 표 + winner reasoning + cross-universe 차이집합), `dacapo-rerun-NN.md` (lesson 본문 + Step F-G detail), `dacapo-flow.md` (bq 의무 — Mermaid + timeline + step trace per round)
> - 9.b `impl/08-impl-log.md`: TODO ID 매핑 ≥ 3 / 모듈명 명시 / 인터페이스 노출
> - 9.c G3+ universe N `06-plan.md`: 시드별 의미 분기 ≥ 20 diff 라인 (universe-1 vs universe-2 동일 ≠ 형식적 분기)
> - **9.nn — G4+ Phase 13 invoke step 강제 (sprint-40 PR-D 신규)**:
>   - phase 12 종료 marker 박힘 후 orchestrator 가 *자동* phase 13 진입 의무 — agent 자율 skip 금지.
>   - phase 13 진입 시 `interactive-viewer-builder` agent invoke 의무 (subagent_type=`interactive-viewer-builder`).
>   - phase 13 종료 marker 박힘 *직전* `interactive-viewer/exit_gate.json` 의 `verdict == "pass"` 검증 (phase 13 §종료 게이트 1:1 정합).
>   - 도메인 미매칭 + skip 시 `handoff/14-handoff.md` 사유 1줄 의무 (regex `phase 13 .* skip|interactive-viewer .* skip`).
>   - **증거 회피 사례** — simulation-bench 001 v0.9.44 g4-v2 회차 (G4) 가 `interactive-viewer/` 디렉터리 자체 부재 + phase 13 종료 marker 자동 진행. 본 9.nn = 그 silent skip 차단.
> - **9.oo — Phase 12 invoke step 강제 (sprint-40 PR-D 신규, 모든 grade)**:
>   - phase 11 종료 후 (또는 phase 09 종료 후 G2 시) phase 12 자동 진입.
>   - phase 12 진입 시 `webview-builder` agent invoke 의무.
>   - phase 12 종료 marker 박힘 *직전* `webview/exit_gate.json` 의 `verdict == "pass"` 검증.
>   - **증거 회피 사례** — v0.9.44 g4-v2 회차 가 `webview/index.md` 마크다운 표 만 박고 `webview/index.html` + `data/webview.json` + `assets/*.{js,css}` 6 파일 통째 부재. 본 9.oo = 차단.
> - **9.pp — pre-cold-session-bootup 자동 호출 의무 (sprint-40 PR-D 신규)**:
>   - phase 00 진입 *직전* orchestrator 가 `python skills/theseus-harness/scoring/pre_bootup.py bootstrap --root <project>` 자동 호출.
>   - 호출 결과로 lineage / webview / interactive-viewer 빈 골격 디렉터리 + JSON 골격 + viewer-runtime/{up.{sh,ps1}, lock} 자동 생성.
>   - 미호출 시 phase 09 §V8 viewer-readiness 게이트가 fail → phase 00 재실행 강제 (양쪽 압력).
>   - **증거 회피 사례** — v0.9.44 g4-v2 회차 가 pre-bootup 자동 호출 0 → `webview/`, `interactive-viewer/` 디렉터리 통째 부재 → 그러나 phase 09 통과. 본 9.pp = 차단.
> - **9.aaa — Dashboard ↔ submission parity CLI (sprint-43 PR-D 신규)**:
>   - dashboard sync *직후* orchestrator 가 `python skills/theseus-harness/scoring/dashboard_submission_parity.py --submission-dir <sub> --dashboard-md <md>` 자동 호출 의무.
>   - 검사: dashboard md 의 `files:` 항목 (path 추출) ↔ submission disk 실 파일 list. 차집합 — *missing on disk* (dashboard declared, disk 부재) = fail. *untracked on dashboard* (disk 있음, dashboard 미tracked) = warning. `__pycache__` 등 legitimate cleanup 제외.
>   - exit 1 시 *dashboard 재생성* 또는 *disk 복구* 강제. parity 불일치 = 데이터 무결성 실패.
>   - **증거 회피 사례** — g4-v2 91 회차 = dashboard md 11 declared (`requirements.txt` / `run_experiment.py` / `src/mine_sim/*.py` 등), submission disk 0. 본 9.aaa = 11/11 missing → fail.
> - **9.zz — Phase invoke audit CLI (sprint-43 PR-C 신규, *declared ≠ invoked* 갭 차단)**:
>   - phase 09 진입 + phase 14 진입 시 orchestrator 가 `python skills/theseus-harness/scoring/phase_invoke_audit.py --orchestrator-skill <path> --project-root <root>` 자동 호출 의무.
>   - 검사: orchestrator SKILL.md 본문에서 *literal Bash command* (`python skills/.../<NAME>.py`) 정규식 추출 + cold session 산출물의 *호출 trace* (gate_<NAME>.json 존재 + evaluated_at) 검증.
>   - exit 1 시 미호출 CLI *전체 재호출* + phase 재진입.
>   - **증거 회피 사례** — g4-v2 91 회차 = sprint-41/42 9 CLI declared (HARD-RULE 9.qq~9.xx), cold session 산출물 0 trace. *declared 9, invoked 0*. 본 9.zz = 차단.
>   - 본 룰 = sprint-43 의 핵심 enforcement — declared 와 invoked 의 *측정 가능한* 갭을 직접 추적.
> - **9.yy — Submission completeness 검증 CLI (sprint-43 PR-B 신규)**:
>   - phase 14 handoff *직후* + dashboard sync *전* orchestrator 가 `python skills/theseus-harness/scoring/submission_completeness.py --submission-dir <sub> --eval-report <eval> --grade <G>` 자동 호출 의무.
>   - 검사: `evaluation_report.json` 의 `output_exists_*` pass 산출물이 *현재* disk 잔존 + `.pyc-only` 패턴 차단 + G3+ governance trail 의무.
>   - exit 1 시 산출물 재emit 또는 *재실행* 강제. 평가 후 대량 삭제 / scratch cleanup 패턴 차단.
>   - **증거 회피 사례** — g4-v2 91 회차 = `submissions/.../theseus-orchestrator-g4-v2/` 안에 *10 .pyc 파일만*, README/submission.yaml/conceptual_model/run_experiment/outputs/.ShipofTheseus 모두 부재. 본 9.yy = 차단 (pyc_only + low_survival + governance_missing 3 violation).
> - **9.xx — Surrender phrase 차단 CLI (sprint-42 PR-E 신규, ouroboros 보다 깊은 enforcement)**:
>   - phase 10 sprint loop 종료 + phase 14 handoff 진입 시 orchestrator 가 `python skills/theseus-harness/scoring/surrender_phrase_grep.py --project-root <root>` 자동 호출 의무.
>   - 검사: 8 surrender 패턴 (`defer_to_external` / `plateaued` / `asymptote` / `good_enough` / `sufficient` / `fine_tune_narrative` / `would_only` / `final_ground_truth_external`) grep. 매치 시 frontmatter `surrender_override: true` + `surrender_override_reason` 의무.
>   - exit 1 시 phase 진입 거부 — 자백 어휘 제거 또는 override 보강 후 재진입.
>   - **증거 회피 사례** — 0510-2 회차 `sprints/03/report.json:lessons_outbound[1]` = *"0.97 < 0.999 G4 asymptote; defer to opus-reviewer scoring as final ground truth"* — 4 surrender 어휘 동시 발현. 본 9.xx CLI = 차단.
>   - 신규 컨벤션 — `surrender-phrase-forbid.md` (8 패턴 카탈로그 + override 메커니즘).
> - **9.ww — Stagnation 후 자율 종료 차단 CLI (sprint-42 PR-D 신규)**:
>   - phase 10 sprint iteration 종료 직전 orchestrator 가 `python skills/theseus-harness/scoring/stagnation_breakthrough.py --project-root <root> --current-iteration N` 자동 호출 의무.
>   - 검사: `sprints/N/report.json` 의 `stagnation_detected: true` AND `score < 0.999` 시 *exit_sprint_loop 자율 결정 차단*. 4 breakthrough 시도 (new_universe / lateral_think / ensemble_synthesis / phase_regression) 중 ≥ 1 evidence 의무.
>   - exit 1 시 sprint iteration 자동 +1 + breakthrough 시도 강제.
>   - **증거 회피 사례** — 0510-2 회차 `sprints/03/report.json`: `score: 0.97, stagnation_detected: true, decision: exit_sprint_loop_per_DEC-autonomy`, 4 시도 0. 본 9.ww = 차단.
> - **9.vv — Universe 단조성 강제 CLI (sprint-42 PR-C 신규)**:
>   - phase 06 / 08 exit 시 orchestrator 가 `python skills/theseus-harness/scoring/universe_count_monotonicity.py --project-root <root>` 자동 호출 의무.
>   - 검사: plan tournament round N+1 universe set ⊇ round N + ≥ 1 NEW universe (`dacapo-skip-sentinel.md` 정합) + impl 단일 universe 시 `impl-multiverse-strict.md` 7-condition ≥ 5 키워드 명시 의무.
>   - exit 1 시 round N+1 강제 (NEW universe 추가) 또는 7-condition 명시 보강.
>   - **증거 회피 사례** — 0510-2 회차 plan round 1 = 3 universe / round 2 = same 3 re-rate (NEW=0) / impl = 1 universe (-2). 본 9.vv = 차단.
> - **9.uu — Cross-phase 컨텍스트 전달 audit CLI (sprint-42 PR-B 신규)**:
>   - phase 02-14 *exit* 시 orchestrator 가 `python skills/theseus-harness/scoring/cross_phase_context_audit.py --project-root <root> --phase <N>` 자동 호출 의무.
>   - phase N 본문에 *직전 phase (N-1) 인용 ≥ 1* + *1단계 이상 과거 phase 인용 ≥ 1* 의무. 미달 시 phase exit 차단.
>   - 인용 패턴 — phase label / decision ID (Q-D, DEC-) / 산출물 path (intent/04-answers.md 류) / 핵심 결정 키워드.
>   - **증거 회피 사례** — 0510-2 회차 `tournament-impl-01.md` 본문이 phase 02 cold-reread / phase 04 답안 / phase 05 critique 인용 0 + `prev_fingerprint` chain 1 단계만. 본 9.uu CLI = 차단.
> - **9.tt — Runtime guard chain 자동 호출 의무 (sprint-41 PR-E 신규, 본 sprint 핵심 enforcement 메커니즘)**:
>   - 매 phase 진입/종료 시 `python skills/theseus-harness/scoring/runtime_guard_chain.py --project-root <root> --phase <N> --transition <entry|exit> --grade <G> --orchestrator-version <V>` 자동 호출 의무.
>   - exit 1 시 phase advance 차단 — orchestrator 가 fail check 의 fix step 자동 진행 후 chain 재호출.
>   - **chain 구성** — skill_version semver tuple 비교 + phase 단조성 + sub-CLI hook (phase 09 entry = cold_session_artefacts / phase 06/08 exit = dacapo_threshold / phase 10 exit = sprint_loop_cap).
>   - 본 룰 = sprint-41 의 핵심 enforcement 메커니즘 — 위 9.qq / 9.rr / 9.ss 모두 본 chain 의 sub-call.
>   - phase-state-machine 컨벤션 의 *runtime guard* 직접 구현.
>   - **증거 회피 사례** — 0510 회차 의 모든 메타-허들 미동작 (skill_version stale silent skip + 13 산출물 0 + 다카포 round 2 = 0 + sprint cap = 1 자율) — 본 9.tt 활성 시 매 transition 차단으로 일괄 정정.
> - **9.ss — Sprint loop 4-layer 종료 조건 CLI (sprint-41 PR-D 신규)**:
>   - phase 10 sprint iteration 종료 직전 orchestrator 가 `python skills/theseus-harness/scoring/sprint_loop_cap.py --project-root <root> --current-iteration N --max-iterations 10` 자동 호출 의무.
>   - exit 1 시 sprint iteration 자동 +1 + 미달 layer 의 fix-TODO 자동 생성.
>   - **4 layer 종합** — Auto (evaluation_report pass_rate) + Internal (quality/09 verdict==proceed) + Tournament (plan/impl dacapo_threshold both pass) + External (zero_context_review ≥ 0.95). 각 layer 임계 0.999 (external 0.95 자율 / 0.99 강제).
>   - max_iterations 도달 시 `sprint_loop_terminated_by_max_iter: true` + 미달 layer list 정직 기록.
>   - **자동 평가 ≠ 휴먼 품질 ≠ 다카포** 3 layer 분리 원칙 — *단순 iteration count cap* 아님.
>   - **증거 회피 사례** — 0510 회차 *"Given 100% on evaluator, sprint cap = 1 (re-validation only)"* 자율 결정. Auto 100% 만 보고 stop, Tournament 0.95 + External 0.90 미고려. 본 9.ss CLI = 차단.
> - **9.rr — Cold session 산출물 file-existence 강제 CLI (sprint-41 PR-C 신규)**:
>   - phase 09 진입 직전 orchestrator 가 `python skills/theseus-harness/scoring/cold_session_artefacts.py --project-root <root> --grade <grade> --domain <domain>` 자동 호출 의무.
>   - exit 1 시 결손 산출물 emit 후 phase 09 재진입 — agent 자율 통과 금지.
>   - **자동 평가 53/53 (100%) ≠ 산출물 통과** 명확 분리. phase 09 진입 *전* 의 게이트.
>   - 13 산출물 (gate_v6 / gate_v8 / gate_readme_summary / gate_methodology_completeness / gate_pnc/mirror/primary/literal / modeling_shortcuts / cascaded_subq / webview/exit_gate / iv/exit_gate / iv/dashboard) 모두 *존재 + valid JSON + verdict pass* 의무.
>   - **증거 회피 사례** — 0510 회차 skill_version 0.9.45 frontmatter 박힘에도 13 산출물 모두 부재 + phase 09 GREEN 자율 통과. 본 9.rr CLI = 차단.
>   - 본 CLI = ouroboros 패러다임 직접 적용 — 컨벤션 본문 = 명세, CLI = 집행.
> - **9.qq — Tournament 다카포 임계 강제 CLI (sprint-41 PR-B 신규)**:
>   - phase 06 (plan tournament) + phase 08 (impl tournament) 종료 직전 orchestrator 가 `python skills/theseus-harness/scoring/dacapo_threshold.py --tournament-md <path>` 자동 호출 의무.
>   - exit 1 (winner ratio < 0.999) 시 round N+1 자동 진행 — agent 자율 skip 금지. 본 CLI 의 verdict 가 phase advance gatekeeper.
>   - 2 round 후에도 ratio < threshold → ensemble synthesis 시도 ([`../theseus-harness/conventions/ensemble-synthesis-default.md`](../theseus-harness/conventions/ensemble-synthesis-default.md) 정합).
>   - 3 round 후에도 미달 → frontmatter `dacapo_threshold_reached_after_3_rounds: false` + phase 09 verdict cap 0.95 (정직 기록).
>   - **증거 회피 사례** — 0510 회차 `tournament-impl-01.md` winner 57/60 = 0.95 → round 2 = 0 자율 lock. 본 9.qq CLI = 차단 (exit 1 → orchestrator 재진입 의무).
>   - 본 CLI = ouroboros MCP 패러다임 직접 적용 — 컨벤션 본문 = 명세, CLI = 집행. 자율 skip 불가.
>
> **위반 처리** — 컨벤션 미달 = self_lint 페이즈 exit fail → 페이즈 재진입 (자율, ≥ 3 회 위반 시만 ack). cold session evidence (sprint-17 슬림화 도입 동기 — v0.9.18~v0.9.22 동안 본 영역이 118 → 287 lines 비대화 + 신규 컨벤션 fabrication 표적화 사고) → `intent/00-violation.md` 추적.

## 15 페이즈 진행

상세는 [`../theseus-harness/SKILL.md`](../theseus-harness/SKILL.md) 의 15 페이즈 표 + [`../theseus-harness/phases/`](../theseus-harness/phases/) 의 페이즈 문서. 본 entry skill 은 그 표를 따라 sub-agent 호출 + frontmatter chain + 산출물 의무 + autonomy 정책을 강제할 뿐, 룰 본문은 한 곳 (theseus-harness) 에 있다.

| # | 페이즈 | 그레이드 활성 (그레이드 매트릭스: [`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md)) |
| --- | --- | --- |
| 00 | 명명 | G3+ |
| 01 | 의도 + 마인드맵 | G2+ (모든 그레이드) |
| 02 | 의도 리뷰 | G3+ |
| 03 | 콜드 재이해 | G3+ |
| 04 | 사용자 질의 | G2+ (모든 그레이드, *유일한 인터럽트*) |
| 05 | 비평 | G3+ |
| 06 | 계획 (G3+ AIDE 트리) | G2+ |
| 07 | 계획 재이해 | G4+ |
| 08 | 구현 (5 서브페이즈 TDD) | G2+ |
| 09 | 게이트 (7 게이트) | G2+ |
| 10 | 스프린트 루프 | G3+ |
| 11 | 회귀 바이섹트 | G4+ |
| 12 | theseus-view (스킬 진행 추적) | G3+ (G2 단순) |
| 13 | interactive-viewer (프로젝트 output observability) | G3+ (G2 옵션, G5 강제) |
| 14 | 핸드오프 | G2+ |

## 그레이드 처리 (호출 직후 첫 동작 후)

```
1. grade_assess.py 자동 추정 (사용자 원문)
2. 페이즈 04 의 Q-G1 객관식 → 사용자 그레이드 확정
3. 그레이드별 매트릭스 활성 페이즈만 진행 (모든 그레이드 진행 — 그레이드는 *내부 모듈레이션만*):
   - Grade 1 (Trivial): mini_harness_tbd 모드 — 최소 페이즈 (모듈레이션 정의 진행 중)
   - Grade 2 (Simple):  intent + plan + implement + quality + handoff (5 페이즈)
   - Grade 3 (Standard): naming + intent + plan-tree + implement(5 sub-phase TDD) + quality + sprint(3 cap) + theseus-view + interactive-viewer + handoff (13 페이즈)
   - Grade 4 (Complex): 15 페이즈 풀 (default)
   - Grade 5 (Critical): 15 페이즈 풀 + 빡빡 모드 (DIP 0.4 / 회귀 0.02 / 멀티버스 강제 5 / 깊이 2 + interactive-viewer 강제)
```

자세한 그레이드 매트릭스는 [`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md).

## 단일 source of truth — theseus-harness 동반 필수

> **본 스킬 단독 설치 시 동작 안 함.** 본 저장소의 [`../theseus-harness/`](../theseus-harness/) 가 모든 룰 본문 source. 본 스킬은:
> - HARD-RULE entry 룰 (위)
> - harness 의존 명시
> - 사용자 마켓플레이스 namespace (`/shipoftheseus:theseus-orchestrator`)
> - 그레이드 처리 흐름 인덱스 (위)

## 자율 결정 (인터럽트 0)

페이즈 04 외 인터럽트 절대 없음. 모든 자율 결정은 산출물 frontmatter + `intent/04-autonomy.md` 의 Q-D1 ~ Q-D9 답에 기록되어 사후 회수 가능. 보안 가드 (실 secret 의 git 커밋 감지) 만 *유일한* 인터럽트 추가 예외 — [`../theseus-harness/conventions/runtime-prereq.md`](../theseus-harness/conventions/runtime-prereq.md).

## 안전 보장

a- **HARD-RULE 양쪽** — 본 SKILL.md + [`../theseus-harness/SKILL.md`](../theseus-harness/SKILL.md) 모두 HARD-RULE 명시. self_lint C-OD 가 양쪽 keyword 일치 검증.
b- **single source of truth** — 콘텐츠는 [`../theseus-harness/`](../theseus-harness/) 한 곳. self_lint C28 검증.
c- **fingerprint 체인** — 각 페이즈 산출물이 직전 산출물의 fingerprint 를 prev_fingerprint 로. 체인 끊기면 다음 페이즈 진입 거부. [`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md).
