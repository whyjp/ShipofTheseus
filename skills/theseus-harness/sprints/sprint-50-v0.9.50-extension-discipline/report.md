# Sprint-50 — v0.9.50 — Extension Discipline (마감 report)

> 시작: 2026-05-10
> 끝: 2026-05-10 (당일 마감 — 7 PR consecutive)
> 사용자 직접 지시: g4-v3 cold session 91/100 SHIP 직후 — *"확장 사고 단계의 부재 = 91 plateau 의 구조적 원인"* 진단 + *"실용주의 프로그래밍 + 이펙티브 소프트웨어 설계 인사이트들의 실제 반영"* 요청.

## 1. 의도 — 한 줄

*프롬프트 너머의 사고* 를 페이즈 본문 + CLI enforcement 로 박는다. 의도→설계→구현→유지보수→테스트 *전 페이즈* 에서 "확장 사고 (Extension Thinking)" 가 별도 단계로 존재하게 한다.

## 2. 변경 — 7 PR consecutive

### PR-A — plan + premortem (`docs(sprint-50): PR-A`)

| 산출 | 본문 |
|---|---|
| `sprints/sprint-50-v0.9.50-extension-discipline/plan.md` | 7 PR matrix + 확장 바이블 4 권 mapping + 9 HARD-RULE 표 + 외부 검증 의무 |
| `sprints/sprint-50-v0.9.50-extension-discipline/premortem.md` | 격언 동·서 + 3 시나리오 (BEST/LIKELY/WORST) + 5 derived improvements + 떠안는 risk 3 |

### PR-B — Phase 1.5 Hidden Intent + 3 CLI (`feat(sprint-50): PR-B`)

| 산출 | 본문 |
|---|---|
| `phases/01-5-hidden-intent.md` | 신규 페이즈. 페이즈 04 직후 / 페이즈 05 직전. ≥5 항목 + ≥3 카테고리 + ≥1 should 채택 |
| `scoring/intent_extension_emit.py` | 3 산출물 emit + vacuous PASS 차단 + cross-file id consistency. self-test PASS |
| `scoring/extension_to_artifact_trace.py` | 채택 항목 plan/impl/sprint/handoff/코드 grep trace ≥1 + frontmatter 만 mention 제외 |
| `scoring/hidden_intent_originality.py` | 2 단 휴리스틱 paraphrase 차단 (token Jaccard ≤ 0.4 + escape category ≥1) |

### PR-C — Phase 06 Design-Twice (`feat(sprint-50): PR-C`)

| 산출 | 본문 |
|---|---|
| `phases/06-plan.md` patch | universe meta.md 의 `philosophy:` 필드 의무 (7 카탈로그) + 본문 architectural decision header ≥3 |
| `scoring/universe_philosophy_distinct.py` | 1 단 declared distinct + 2 단 unique decision 비율 ≥ 50% (premortem §3-2) |

### PR-D — Phase 08 Deep-Module + DRY (`feat(sprint-50): PR-D`)

| 산출 | 본문 |
|---|---|
| `phases/08-implement.md` patch | sprint-50 § Deep-Module + DRY 절 + invoke step |
| `scoring/deep_module_metric.py` | (interface / functional) 비율 ≤ 0.4 + 모듈 수 = 1 fail (premortem §3-3) |
| `scoring/dry_violation_count.py` | n-gram (n=8) 중복 비율 ≤ 5% + boilerplate catalog 제외 |

### PR-E — Phase 09 Define-Errors-Out + Comments-Why (`feat(sprint-50): PR-E`)

| 산출 | 본문 |
|---|---|
| `phases/09-quality-gates.md` patch | sprint-50 § Define-Errors-Out + Comments-Why 절 + invoke step |
| `scoring/define_errors_check.py` | raise/handle pair + bare except only fail (Effective Python Item 87) |
| `scoring/comment_intent_check.py` | comment-vs-next-code Jaccard ≥ 0.5 = paraphrase + sentinel escape ≥80% fail (premortem §3-4) |

### PR-F — Phase 10/14 + HARD-CORE 9.bbb~9.jjj (`feat(sprint-50): PR-F`)

| 산출 | 본문 |
|---|---|
| `phases/10-test-loop.md` patch | sprint-50 § Refactor-not-Rewrite + invoke step |
| `phases/14-handoff.md` patch | §g-2 Knowledge Portfolio refresh + invoke step |
| `scoring/refactor_not_rewrite_ratio.py` | git diff modified ratio ≥ 0.3 + zero-diff fail (premortem §3-5) |
| `scoring/knowledge_portfolio_check.py` | handoff insight section ≥3 + body ≥80 chars + distinct topic |
| `HARD-CORE.md` 9.bbb~9.jjj inline | 9 룰 한 줄 inline + 페이즈 본문 cross-ref |

### PR-G — 마감 (`feat(sprint-50): PR-G`)

본 report.md + version bump + CHANGELOG + memory entry + g4-v3 review doc.

## 3. premortem 시나리오 사후 평가

본 sprint 마감 시점 (= 본 sprint 자체) 에서는 *3 시나리오 중 어느 것이 실제* 였는지 *판정 불가*. dogfood 한계 — `feedback_self_eating_dogfood.md` 정합. 다음 cold session (g4-v4) 결과로 판정.

| 시나리오 | 본 sprint 자체 검증 가능 여부 |
|---|---|
| BEST (95-97 갱신) | g4-v4 결과 종속 |
| LIKELY (91-93 plateau 1-2pt 상승) | g4-v4 결과 종속 |
| WORST (88-90 metric-gaming) | g4-v4 결과 종속 |

## 4. derived improvements 의 적용 결과

premortem §3 의 5 derived improvements 모두 본 sprint 의 CLI 휴리스틱에 *반영*:

| Derived | 적용 |
|---|---|
| §3-1 hidden_intent_originality 2 단 휴리스틱 | ✅ token Jaccard + escape category 이중 의무 |
| §3-2 universe philosophy 결정 distinct | ✅ universe_philosophy_distinct.py 의 §2 단 검사 |
| §3-3 deep_module 단일 파일 fail | ✅ deep_module_metric.py module count = 1 = automatic fail |
| §3-4 comment escape ≥80% fail | ✅ comment_intent_check.py max-escape-ratio 0.8 default |
| §3-5 refactor zero-diff fail | ✅ refactor_not_rewrite_ratio.py allow-zero-diff default OFF |

## 5. 떠안은 risk 의 사후 평가

premortem §4 의 3 risk 모두 본 sprint *내부* 에서 mitigation 안 함 — 다음 sprint 인계:

| Risk | 본 sprint 처리 | 다음 sprint 의제 |
|---|---|---|
| §4-1 NLP-grade 휴리스틱 부재 | 토큰-level 휴리스틱 + sentinel escape 만 | embedding-based 고도화 |
| §4-2 universe philosophy 카탈로그 한정 | 7 카탈로그 + `--allow-extra` declare 1 회 ack | constraint-programming / streaming / staged-pipeline 추가 |
| §4-3 dogfood 검증 시간 격차 | g4-v4 결과 대기 | g4-v4 결과 분석 + sprint-51 attribution |

## 6. 외부 검증 의무

본 sprint 마감 != 본 sprint 검증. 본 sprint 의 *진짜 marker* = g4-v4 cold session 의 외부 평가 결과.

g4-v4 결과 분석 시 다음 attribution 분석:
- Phase 1.5 채택 extension 이 코드 / plan 어느 부분에 반영됐는가
- universe philosophy distinct 가 plan tournament winner 패턴을 변경했는가
- deep-module / DRY CLI 가 코드 구조를 실제로 변경했는가
- 외부 평가 차원 (Experimental / Conceptual / Code quality) 별 변동

이 분석 결과가 sprint-51 의제를 결정.

## 7. 자기 점검

`feedback_score_targeting_taboo.md` 정합 ✅ — 본 sprint 본문 / 모든 commit / report.md 모두 *점수 % 표기 0*. 구조 framing 만.

`feedback_convention_diet_paradigm.md` 정합 ✅ — 신규 컨벤션 파일 0. 페이즈 본문 patch + CLI 만.

`feedback_no_human_ack.md` 정합 ✅ — 페이즈 04 외 인터럽트 0. 본 sprint 진행 중 사용자 ack 1 회 (sprint-50 진행 방식 confirmation, AskUserQuestion).

`feedback_grade_scope.md` 정합 ✅ — sprint-50 가 grade 게이트 추가 X (확장 사고 강제는 모든 grade 적용).

## 8. 마감 조건 충족 여부

- [x] 7 PR 모두 main 머지
- [x] 10 신규 CLI 모두 self-test PASS (단, refactor_not_rewrite 는 git diff 의존이라 self-test 는 parser 만)
- [x] 9 HARD-RULE 모두 페이즈 본문 + HARD-CORE inline 등록
- [x] skill_version 0.9.49 → 0.9.50 (plugin.json + theseus-harness/SKILL.md)
- [x] CHANGELOG sprint-50 entry
- [x] memory entry 2 종 신규 (project_sprint50_v0950 + feedback_extension_discipline)
- [x] docs/reviews/2026-05-10-bench-001-mine-throughput-91-g4v3-extension-gap.md

본 sprint 가 진짜로 효과를 봤는지는 g4-v4 cold session 결과로 판정.
