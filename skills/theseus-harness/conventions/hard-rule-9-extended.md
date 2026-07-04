---
id: hard-rule-9-extended
category: meta
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'phase 진입 시 매칭 sub-rule lazy load (HARD-CORE.md HR9 9.d 이후 전문)'
indexed-in: conventions/INDEX.md
---

# HARD-RULE 9 확장 — 9.d ~ 9.ppp 전문 (HARD-CORE.md 로부터 이동, C-HC1 cap 준수)

## 한 줄 요약

**HARD-CORE.md 의 HR9 는 9.a~c 만 always-load inline 유지 — 9.d 이후 (Da Capo / Cold validator / Phase state / Prebuilt shell / Emit fidelity / Pre-bootup / Extension Discipline / Prompt-Driven Harness / Viewer Finalization Closure) 30+ sub-rule 전문은 본 파일이 단일 source.** 페이즈 진입 시 매칭 항목만 참조 (lazy load) — always-load 본문 부풀음 영구 차단 (sprint-20 C-HC1).

- **9.d** Da Capo산출물 본문 의무: `tournament-NN.md` (6-dim sub-scores 표 + winner reasoning + cross-universe 차이집합), `dacapo-rerun-NN.md` (lesson 본문 + Step F-G detail), `dacapo-flow.md` (bq 의무)
- **9.f** Cold session validator: phase 09 진입 직전 `scoring/check_cold_session.py <proj>` 의무. exit 1 시 phase 재진입.
- **9.mm** Phase state runtime (sprint-34): 매 phase enter/exit `scoring/phase_state.py` 의무. 단조성 + forgery 차단. exit 1 = 재진입.
- **9.nn** Prebuilt shell + JSON emit (sprint-35): cold session 은 webview / lineage viewer 를 *build 0* — `templates/{webview,lineage-viewer}/dist/` 복사 + JSON injection 만. C-PSR 검증.
- **9.oo** Emit fidelity (sprint-35-extra): lineage.json/webview.json 의무 키 enum + 빈/dummy 금지 + gantt ★/parallel≥3/bypass:done 룰. `emit_fidelity.py check` + C-EFS.
- **9.pp** Pre-bootup + viewer lifecycle (sprint-36): phase 00 enter 직전 `pre_bootup.py bootstrap` (3 viewer + 빈 골격 + HTTP server up). phase 14 종료 시 `teardown` 의무 (PID 누수 차단). interactive-viewer prebuilt + dashboard.json schema-driven (5 widget 타입). 3 viewer auto-refresh 5s polling + visibility + manual. C-PCB/C-VAR/C-VRL/C-IVP.
- **9.bbb~9.jjj** Extension Discipline (sprint-50): 9 룰 페이즈 본문 단일 source — 9.bbb Phase 1.5 hidden intent 3 산출물 (`intent_extension_emit.py`) / 9.ccc universe philosophy distinct (`universe_philosophy_distinct.py`) / 9.ddd deep-module metric (`deep_module_metric.py`) / 9.eee DRY violation count (`dry_violation_count.py`) / 9.fff define-errors-out (`define_errors_check.py`) / 9.ggg comment-why-not-what (`comment_intent_check.py`) / 9.hhh refactor-not-rewrite sprint_type-aware (`refactor_not_rewrite_ratio.py`) / 9.iii knowledge portfolio refresh (`knowledge_portfolio_check.py`) / 9.jjj extension trace (`extension_to_artifact_trace.py`). 격언: Pragmatic Programmer + A Philosophy of Software Design. 페이즈 본문 §자동 CLI 호출 literal Bash 박힘 (sprint-43 패러다임).
- **9.kkk~9.mmm** Prompt-Driven Harness (sprint-51): Intent Recursion 패러다임. 9.kkk phase 04 entry `prompt_meta_extractor.py` 의무 호출 — `intent/00-prompt-meta.json` 8 카탈로그 자동 추출 (도메인 무관 markdown structural parse). 9.lll all-phase `placeholder_grep.py` — sentinel 카탈로그 (TBD/FIXME/XXX/unrecorded/unknown/undefined/<insert>/...) + prompt-meta output_schemas null field 검사. 9.mmm phase 1.5 `default_value_justification.py` — prompt-meta default_warnings trigger 시 의식적 default (0/null/auto) 의 sentence-level justification 의무. reviewer 약점 3 건 (token_usage/warmup/intervention.category) 도메인 무관 catch.
- **9.nnn~9.ppp** Viewer Finalization Closure (sprint-52): pre_bootup 의 emit-skeleton ↔ phase 14 의 refresh 양 끝점 닫음. 9.nnn phase 14-handoff 진입 시 `lineage_finalize.py refresh --strict` 의무 호출 — `.ShipofTheseus/` 재귀 스캔 → fingerprint chain / mermaid_flowchart / mermaid_gantt / project_run / final_outcome / duration_seconds / phases_completed / winner 실값 refresh + dashboard.json + webview/data/webview.json 동시 정정. 9.ooo universe candidate (`plan/candidates/universe-N/{06-plan.md, 07-cold-read.md}`) frontmatter `created_at` 의무 — 정시 stub (`T..:00:00Z`) 차단, self_lint C-UNIV-CREATED-AT. 9.ppp `placeholder_grep.py --include-viewer-json` 의무 — cold session 마감 후 lineage.json `project_run != "completed"` / `winner == null` / `fingerprint_chain == []` / `phases[].fingerprint == "PENDING"` / `mermaid_*` 에 "미시작"/"Empty"/"Pending" / dashboard.json `final_phase == null` + status complete 모순 / webview.json `final_phase == null` + duration<60s 잔존 catch. sprint-43 declared=invoked 패턴의 finalize 차원.

위반 시 self_lint 페이즈 exit fail → 페이즈 재진입 (자율, 누적 ≥ 3 시만 ack).

## 호환성

[`HARD-CORE.md`](../HARD-CORE.md) HR9 절이 본 파일을 링크 — always-load 본문은 9.a~c 요지만 유지하고 9.d 이후 전문은 본 파일 단일 source (C-HC1 cap 준수).
