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
- **9.f 은퇴(B1)** — cold session 검증은 `run_gate.py` 의 `cold.isolation` / `plan.*` CheckSpec(값 기반)으로 대체. 스크립트 `check_cold_session.py` 는 `producers/measure_cold_isolation.py` 의 라이브러리로 잔존.
- **9.mm** Phase state runtime (sprint-34): 매 phase enter/exit `scoring/phase_state.py` 의무. 단조성 + forgery 차단. exit 1 = 재진입.
- **9.nn/9.oo/9.pp** viewer 3종(webview/lineage/interactive) + prebuilt shell + emit + pre-bootup lifecycle (sprint-35/35-extra/36): **advisory — §8 동결(B2-F3), 생산 의무 해제.** viewer 를 산출하는 경우에 한해 조건부 진실성 존치: (9.nn) build 0 원칙(prebuilt dist 복사 + JSON injection), (9.oo) emit fidelity(빈/dummy 키 금지), (9.pp) pre-bootup 부팅 시 teardown(PID 누수 차단). 스크립트(`pre_bootup.py`/`emit_fidelity.py`)·템플릿·5-widget 스키마는 물리 존치, CLI 로 옵션 실행 가능. C-PSR/C-EFS/C-VAR/C-VRL/C-IVP 는 능력 명칭(파일·키워드) 검증이라 존치.
- **9.bbb~9.jjj** Extension Discipline (sprint-50): 9 룰 페이즈 본문 단일 source — 9.bbb Phase 1.5 hidden intent 3 산출물 (`intent_extension_emit.py`) / **9.ccc universe philosophy distinct advisory(§8 동결, B2-F2) — `universe_philosophy_distinct.py` 선택적 실행 가능, 강제 아님** / 9.ddd deep-module metric (`deep_module_metric.py`) / 9.eee DRY violation count (`dry_violation_count.py`) / 9.fff define-errors-out (`define_errors_check.py`) / 9.ggg comment-why-not-what (`comment_intent_check.py`) / 9.hhh refactor-not-rewrite sprint_type-aware (`refactor_not_rewrite_ratio.py`) / 9.iii knowledge portfolio refresh (`knowledge_portfolio_check.py`) / 9.jjj extension trace (`extension_to_artifact_trace.py`). 격언: Pragmatic Programmer + A Philosophy of Software Design.
- **9.kkk~9.mmm** Prompt-Driven Harness (sprint-51): 9.kkk phase 04 entry `prompt_meta_extractor.py` 의무 호출 — `intent/00-prompt-meta.json` 8 카탈로그 자동 추출. 9.lll all-phase `placeholder_grep.py` sentinel 카탈로그 검사. 9.mmm phase 1.5 `default_value_justification.py` default_warnings trigger 시 justification 의무.
- **9.nnn/9.ooo/9.ppp** Viewer Finalization Closure (sprint-52): **생산 의무는 §8 동결(B2-F3) — viewer 산출물이 존재하는 경우에 한해 조건부 진실성 의무.** 9.nnn viewer 산출물(lineage.json/webview.json/dashboard.json) 존재 시 `lineage_finalize.py refresh --strict` 로 fingerprint chain/실값 refresh 의무. 9.ooo universe candidate 산출 시 frontmatter `created_at` 실값 의무(정시 stub 차단, self_lint C-UNIV-CREATED-AT). 9.ppp viewer 산출물 존재 시 `placeholder_grep.py --include-viewer-json` 로 거짓 placeholder(`project_run != "completed"`/`winner == null`/`fingerprint_chain == []`/`PENDING`/"미시작" 등) 차단 의무. viewer 미산출 run 은 해당 없음.

위반 시 self_lint 페이즈 exit fail → 페이즈 재진입 (자율, 누적 ≥ 3 시만 ack).

## 호환성

[`HARD-CORE.md`](../HARD-CORE.md) HR9 절이 본 파일을 링크 — always-load 본문은 9.a~c 요지만 유지하고 9.d 이후 전문은 본 파일 단일 source (C-HC1 cap 준수).
