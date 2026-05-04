# Ship of Theseus — AIDE 멀티버스 코딩 하네스

> **English readers**: see [`README.en.md`](README.en.md) — single-page summary in English.

## 한 줄 요약

**한 요구를 *N 우주의 트리* 로 동시 탐색하고 *토너먼트* 로 우승 우주를 선별해, 처음 의도한 타이틀로 끝까지 부를 자격을 만드는 재귀 멀티 에이전트 코딩 하네스.** 본 프로젝트의 *진짜 컨셉* 은 **AIDE 트리 (Plan Tree × N Universe × Tournament × Ensemble Synthesis × Blind Rerun × Multi-Phase 확장)** 다 — 페이즈 06 plan-tree 가 본체, 후반 회차 (v0.9.10~v0.9.15) 에서 페이즈 02 / 05 / 08 / 11 / 13 으로 multiverse 가 확장되며 본 하네스의 *유일한 차별 강점* 으로 부각됐다. *Theseus* 는 브랜딩 + 신뢰 담보 메타포 (도자기 장인의 깨고 다시 빚기) 로 남는다. 진입점은 [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md) (1 entry) + [`theseus-harness`](skills/theseus-harness/SKILL.md) (1 source) 의 2 SKILL.md.

## 현재 성숙도 — 정직 박스 (v0.9.18)

> **v0.9.16 = 발현 검증 6 메타 컨벤션 마일스톤.** 47 컨벤션 + 18 에이전트 + 15 페이즈 + 2 도메인 어댑터. v0915-cold01 외부 채점 93/100 (자체 추정과 일치 — score-rubric-objectivity 발현 PASS) 진단 후 *준비-vs-동작 갭* 정정 sprint. simulation-bench 외부 적용 6 회차 (002 / 003 / v01_cold / v091_cold01 / v0913_cold01 / v0914_cold01 / v0915-cold01) 모두 *94 plateau* 도달 — v0.9.16 적용 cold session 으로 돌파 검증 대기.
>
> **진척 지표 (2026-05-04)**:
> - ✅ 자기 평가 — self_lint 모든 룰 PASS / pytest 회귀 0 / self_score 1.0 / 임계 0.99999 통과
> - ✅ **livetest 4/4 PASS** (G2/G3/G4/G5) — sandbox sub-claude fresh load + 15 페이즈 산출물 정상
> - ✅ **HARD-RULE 1~9 안정화** + **Layer 3 결과물 허들 supremacy** (메모리 / 컨벤션 override 불가)
> - ✅ **simulation-bench 외부 적용 6 회차** — 18.5 ~ 44 분 wall clock / intervention 0 / sanity 4 PASS
> - ✅ **AIDE multiverse 풀 발현** — 페이즈 06 폭 3-6 + 깊이 1-2 + 페이즈 02/05/08/11/13 multi-phase 확장 + sequenceDiagram per-universe + tournament blind rerun + ensemble synthesis default
> - ✅ **94 plateau 측정** — v01_cold (v0.9.9) / v091_cold01 (v0.9.12) / v0914_cold01 (v0.9.14) 자체 추정 모두 94 — *content depth layer* 만이 천정 깬다
> - ✅ **self_lint 68/68 PASS** — 본 저장소 최초 완전 통과 (lint_score = 1.0, all_ok = True). BOOTSTRAP "내가 강제하는 모든 것을 내가 100% 통과한다" 약속 달성.
> - ⏸ **94 → 97+ 천정 돌파 검증** — v0.9.16 발현 검증 6 메타 (convention-traceability / sprint-score-delta-tracking / evidence-driven-sprint-planning / cross-universe-lesson-distillation / regression-derived-lint-rule-autogen / polyglot-code-quality) 적용 cold session 미실행. 본 적용 후 maturity 0.7~0.8.
>
> v1.0 = 사용자 외 maintainer 가 prod 채택 + 외부 적용 ≥ 5 건 + 94 plateau 돌파 검증.
>
> **livetest lessons** (sprint-03+04-a 6 PR 의 발견): [docs/lessons/2026-05-03-livetest-validated.md](docs/lessons/2026-05-03-livetest-validated.md)
>
> ⓐ `self_lint pass`, `sample_score 1.0`, `임계 0.99999 통과` 같은 수치는 **본 저장소의 마크다운·코드 인덱스 정합성·예시 입력 채점 통과** 를 의미합니다 — *LLM 에이전트가 프롬프트를 행동으로 따르는지* 의 외부 실증과 다릅니다.
> ⓑ self_lint 는 *마크다운 텍스트 패턴* 만 검사합니다. "phase 본문에 키워드가 박혀 있는가" 는 검증되지만, "implementer 에이전트가 *실제로* lesson_pack 을 받아 forbidden 전략을 회피하는가" 는 검증 불가 — bench 외부 채점 회차로 대신 검증.
> ⓒ **임계 0.999 / 자기 임계 0.99999 는 SLO 가용성이 아닙니다** — 6 차원 rubric 가중평균 + DIP 단독 hard cap 0.6 + 5 hard cap 의 *명명 규칙*. 외부 사용자에게 "99.999% 신뢰 가능" 으로 오해되지 않도록 본 README 에서 명시.
> ⓓ **v0.9.16 의 시급 목표**: 94 plateau 돌파 — v0.9.15 의 budget saturation × evidence 1:1 self-rating + v0.9.16 의 발현 검증 6 메타 (applied_conventions traceability × sprint score delta honesty × evidence-driven sprint planning × cross-universe lesson distillation × regression-derived lint autogen × polyglot code quality) 합성으로 진짜 0.999 도달. 사용자 외 prod 채택은 그 다음.
> ⓔ **자기 평가 통과 수치는 OS 무관** — Linux / Mac / Windows 모두에서 `bash scripts/self-check.sh` 또는 `scripts\self-check.bat` 으로 같은 결과 재현. cp949 잠재 버그는 v0.2.2 self_lint C35 가드로 해소.
> ⓕ **외부 차용 메서돌로지 — 거울 원칙**: 외부 스킬은 *사각지대 탐지용 거울* 로만 사용. *합성 source 가 아님*. 차용은 본 하네스 *컨셉 보존* 우선, *직교 차원 입증 시* 만 *기존 한 단락 증강*. 자세한 메서돌로지는 [`PHILOSOPHY.md`](PHILOSOPHY.md) "외부 패턴 차용 메서돌로지" 절.
> ⓖ **Layer 3 결과물 허들 supremacy** (v0.9.14): 메모리 룰 / 컨벤션 / 사용자 사전 위임 *어느 것도 결과물 허들 override 불가*. v0913_cold01 의 design-only 회피 차단 + 003 / v091_cold01 의 코드 + 실행 결과 generalize.

## 왜 *AIDE 멀티버스* 인가 — 본 프로젝트의 진짜 동력

페이즈 06 plan-tree 의 결과는 단일 플랜이 아니라 **N 개 우주의 트리** 다. 5 시드 카탈로그 (domain-first / adapter-first / minimal-subtraction / tdd-topology / strict-layering) + 6 분기 축 (process-vs-data / sync-vs-async / centralized-vs-distributed / dynamic-vs-static / push-vs-pull / mutable-vs-immutable) 에서 우주가 갈리고, plan-reviewer 가 fresh 콜드 리딩으로 채점, tournament 가 우승 우주를 선별한다. v0.9.10~v0.9.15 회차에서 본 컨셉이 *후반 핵심* 으로 부각:

- **v0.9.10** — `aide-tree-symmetry` (universe 별 sequenceDiagram 강제) + `aide-tree-multi-phase` (페이즈 02/05/08/11/13 까지 확장) + `tournament-blind-rerun` (임계 미달 시 anonymize 재경합)
- **v0.9.11** — `interface-first-parallel-impl` (페이즈 06 인터페이스 의무 + 페이즈 08 sub-agent 병렬 fan-out)
- **v0.9.12** — `multiverse-impl-fan-out` (universe N 모두 실 코드 의무) + `analytical-bound-cross-validation` + `budget-aware-fallback`
- **v0.9.13** — `ensemble-synthesis-default` (G4+ tournament 결과 algorithmic union default) + `deep-semantic-intent` + `domain-research-stacking`
- **v0.9.14** — `deliverable-hurdle-supremacy` (Layer 3 결과물 허들이 메모리/컨벤션 override)
- **v0.9.15** — `budget-saturation-loop` + `score-rubric-objectivity`
- **v0.9.16** — 발현 검증 6 메타 컨벤션 (`convention-traceability` + `sprint-score-delta-tracking` + `evidence-driven-sprint-planning` + `cross-universe-lesson-distillation` + `regression-derived-lint-rule-autogen` + `polyglot-code-quality`) + `anti-patterns.md` fragmentation 분리
- **v0.9.17** — `grade_assess.py` v2: 키워드 매칭 폐기 + 페이즈 01 다중 신호 (18+ 차원) 기반 + **default = G4** (본 하네스 호출 자체가 G4+ 의도 신호). G3 하향은 12 차원 단순 증명 + 사용자 ack 의무. G5 상향은 명시 ack 만.
- **v0.9.18** — 본 스킬 자체 가치 개선 4 컨벤션 (`intent-completeness` §k 9 sub + `process-flow-coherence` 게이트 8 + `domain-failure-patterns` 게이트 9 + `decision-support-framing`) + 발현 강제 메커니즘 (intent-extractor 프롬프트 전면 재작성, 마인드맵 Mermaid 의무 + §k/§j 누락 시 페이즈 진입 거부). 도메인 어댑터 (DES / mining-haulage) 에 failure_patterns 항목 누적.

**닥터 스트레인지가 14,000,605 미래를 본 이유와 같다 — 결정 이전에 다 가본다.** LLM 비결정성을 *분기 동력* 으로 전환하는 것이 본 하네스의 유일한 차별 강점.

## 왜 "Ship of Theseus" 라 부르는가 — 브랜딩과 신뢰 담보

배의 모든 판자를 하나씩 갈아 끼워도 같은 배라고 부를 수 있는가 — 이 사고 실험은 본 저장소의 *브랜딩 + 신뢰 담보 메타포* 다. AIDE 멀티버스가 N 우주를 깨뜨리고 합치는 동안에도, **최초 의도한 타이틀의 결과물이라고 부를 수 있는 신뢰** 가 끝까지 유지되어야 한다. 그 신뢰를 만드는 골격이 *도자기 장인의 깨고 다시 빚기* (페이즈 11 `re-architect` 6 차원 트리거 + 회귀 바이섹트 + 점수 시계열) 다.

깊은 설계 동기, 도자기 장인 비유, AIDE 트리 격상, Ralph 루프·OhMy 시리즈·우로보로스·Karpathy LLM Wiki·Da Capo 합성 근거는 [`PHILOSOPHY.md`](PHILOSOPHY.md) 참조.

## 어떤 작업에 쓰는가

ⓐ **추천 (G3 이상)** — 다중 모듈 / FE+BE 동시 / 도메인이 미정착인 신규 기능 / 회귀 바이섹트가 필요한 장기 리팩터 / *외부 evaluator 가 채점하는 bench 작업* (G4 자동 escalation).
ⓑ **거부 (G1)** — 한 줄 수정, 오타 정정, 단일 함수 추가. 본 하네스가 자기 거부 — `intent` 페이즈에서 grade-assess 가 G1 으로 판정되면 호출이 종료된다 ([`conventions/grades.md`](skills/theseus-harness/conventions/grades.md)).
ⓒ **미니 모드 (G2)** — 단일 모듈·단일 스택의 작은 기능. 페이즈 일부 스킵.

## 15 페이즈 파이프라인

| 단계 | 페이즈 | 산출물 |
| ---: | ----- | ------ |
| 00 | 명명 (G3+) | `naming/00-naming.md` |
| 01 | 의도 + 마인드맵 (G2+) | `intent/01-intent.md` |
| 02 | 의도 리뷰 (G3+, multi-reviewer multi-phase 옵션) | `intent/02-intent-review.md` |
| 03 | 콜드 재이해 (G3+, parallel cold review) | `intent/03-comprehension.md` |
| 04 | 사용자 질의 + 스택 + Q-D9 사전 위임 + Q-D-DELIVERABLE-MODE + Q-D-BUDGET-MODE | `intent/04-{questions,answers,autonomy,stack,verification,runtime-prereq}.md` |
| 05 | 비평 (G3+, multi-critic multi-phase 옵션) | `intent/05-critique.md` |
| 06 | **AIDE Plan-Tree** — N 우주 토너먼트 (G3-3 / G4-4 / G5-6 폭 + 깊이 1-2 + sequenceDiagram per-universe + ensemble synthesis default) | `plan/{tournament.md, 06-plan.md, candidates/universe-N/}` |
| 07 | 계획 재이해 (G4+) | `plan/07-plan-review.md` |
| 08 | 구현 — 5 서브페이즈 TDD (α scope / β test-RED / γ impl-GREEN / δ refactor / ε log) + multiverse impl fan-out (universe N 모두 실 코드) | `impl/{08-impl-log.md, 08-test-scope.md}` + 코드 |
| 09 | 7 종 게이트 (의도·범위·SOLID·테스트·FE-BE·NFR·실 부팅) + Gate 0 결과물 허들 (H1-H5) supremacy | `quality/09-quality-gate.md` |
| 10 | 무한 스프린트 — budget-saturation-loop (≥80% 사용 강제) + sprint-regression-loop + content depth lesson | `sprints/NN/{report,inputs}.*` |
| 11 | 회귀 바이섹트 (G4+, 4 분류: plan/impl/data/external defect + multi-hypothesis multi-phase 옵션) | `sprints/NN/bisect.md` |
| 12 | theseus-view (스킬 진행 추적, bun + hono + react) | `webview/` |
| 13 | interactive-viewer (프로젝트 output observability + 도메인별 dashboard, multi-framing 옵션) | `interactive-viewer/` |
| 14 | 핸드오프 (one-liner + score-rubric-objectivity self-estimate + evidence_missing) | `handoff/14-handoff.md` |

페이즈별 활성 그레이드 + 컨벤션은 [`conventions/grades.md`](skills/theseus-harness/conventions/grades.md) 의 매트릭스. 47 컨벤션 + 18 에이전트 + 채점기는 모두 `theseus-harness/` 단일 source.

## 책임 범위 (Scope)

| 본 하네스 책임 | 외부 프로젝트 repo 책임 |
|---|---|
| ✅ 의도 추출 + Q-D9 인터뷰 + Q-D-MODE 사전 위임 | — |
| ✅ AIDE Plan-Tree (N 우주 토너먼트 + ensemble synthesis + blind rerun) | — |
| ✅ 모듈 분할 / 파일 배치 / 폴더 배치 / 모듈간 인터페이스 (interface-first) | — |
| ✅ TODO DAG + 7 게이트 + sprint 점수 시계열 + 회귀 바이섹트 *권고* | — |
| ✅ multiverse impl fan-out (universe N 모두 실 코드) — *standalone* 컨텍스트 시 | ✅ *기존 repo* 컨텍스트 시 코드 작성 |
| ✅ webview (스킬 진행) + interactive-viewer (프로젝트 output observability) | — |
| ✅ 핸드오프 산출 (one-liner + evidence-based self-estimate + 자율 결정 이력) | — |
| — | ✅ 실 빌드 (`go build`, `bun build`) + 테스트 실행 |
| — | ✅ 실 부팅 + healthz 검증 (실 env / 실 DB) — *기존 repo* 시 |
| — | ✅ 실 회귀 검출 (commit-by-commit 바이섹트) |

**Layer 3 결과물 허들 supremacy** (v0.9.14): standalone 컨텍스트 (= bench / 단독 진행) 시 본 하네스가 *코드 + 실행 + 측정값* 까지 의무. design-only 종료는 사용자 명시 ack (Q-D-DELIVERABLE-MODE = 3) 만 예외.

## 수록 스킬 (2 개, v0.9.16)

| 스킬 | 역할 | 가이드 |
| ---- | ---- | ----- |
| [`theseus-orchestrator`](skills/theseus-orchestrator/SKILL.md) | **사용자 entry point.** HARD-RULE (호출 직후 첫 동작 강제) + 그레이드 처리 인덱스 + harness 동반 의존 명시. | [docs/skills/theseus-orchestrator.md](docs/skills/theseus-orchestrator.md) |
| [`theseus-harness`](skills/theseus-harness/SKILL.md) | **콘텐츠 source of truth.** 47 컨벤션 + 15 페이즈 + 18 에이전트 + 채점기 (`scoring/`) + 템플릿 (`templates/`) + 2 도메인 어댑터 (`conventions/domain-adapters/`). | [docs/skills/theseus-harness.md](docs/skills/theseus-harness.md) |

> **v0.9.0 sprint-03-b 단순화** — 이전 9 SKILL.md (orchestrator + harness + 7 phase 분해 stub) 에서 7 phase stub 제거. pure delegation 이라 cost > benefit 으로 판정 (livetest #1 fail 분석). 사용자 entry namespace (`/shipoftheseus:theseus-orchestrator`) 동일.

스킬 간 인터페이스는 산출물 frontmatter ([`conventions/contracts.md`](skills/theseus-harness/conventions/contracts.md)) 가 계약. 페이즈 산출물 fingerprint chain 으로 무결성 검증.

새 스킬은 `skills/<이름>/SKILL.md` 로 추가하고 [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) 에 등록한다.

## 빠른 사용

**기본** — `theseus-orchestrator` 가 15 페이즈를 자동 driver 로:

```
/shipoftheseus:theseus-orchestrator <요구사항>
```

페이즈 04 인터뷰 1회 후 인터럽트 0. 그레이드 매트릭스 + Q-D1~Q-D9 + Q-D-DELIVERABLE-MODE + Q-D-BUDGET-MODE 사전 위임 답에 따라 자율 진행.

frontmatter 핑거프린트가 입력 무결성을 검증해야 다음 페이즈 진입한다.

## 설치

상세 안내는 [`INSTALL.md`](INSTALL.md). 가장 단순한 형태:

```bash
git clone https://github.com/whyjp/shipoftheseus.git ~/src/shipoftheseus

# 본인 프로젝트 루트에서 — 2 스킬 일괄 링크
cd /path/to/your/project
mkdir -p .claude/skills
for s in ~/src/shipoftheseus/skills/*/; do
  ln -s "$s" ".claude/skills/$(basename "$s")"
done
```

또는 Claude Code 마켓플레이스 패턴 (본 저장소가 마켓플레이스 + 단일 플러그인 동시 역할 — [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) 등록):

```
/plugin marketplace add https://github.com/whyjp/shipoftheseus
/plugin install shipoftheseus@shipoftheseus
```

## 산출물 위치

모든 산출물은 프로젝트 루트의 `.ShipofTheseus/<프로젝트명>/` 아래에 카테고리·단계·스프린트별로 배치된다. 자세한 트리는 [`skills/theseus-harness/SKILL.md`](skills/theseus-harness/SKILL.md) 의 "산출물 트리" 섹션 참조.

```
.ShipofTheseus/<프로젝트명>/
├── timing/start.json
├── naming/00-naming.md
├── intent/01..05*.md
├── plan/{06-plan.md, 07-plan-review.md, tournament.md, candidates/universe-N/...}
├── impl/{08-impl-log.md, 08-test-scope.md}
├── code/                              # standalone 컨텍스트 시 (Layer 3 결과물 허들)
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, unit.json, e2e.json}
├── webview/                           # 페이즈 12 — theseus-view (스킬 진행)
├── interactive-viewer/                # 페이즈 13 — 프로젝트 output observability
└── handoff/14-handoff.md
```

## 자기 평가 (부트스트래핑)

본 하네스는 *자기 자신* 을 같은 게이트로 평가한다 — *내가 너에게 강제하는 것은 나에게도 강제되어야 한다.* 자세한 절차는 [`BOOTSTRAP.md`](BOOTSTRAP.md).

```bash
./scripts/self-check.sh        # linux/mac
scripts\self-check.bat         # windows
```

수행 단계: self_lint 체크 → pytest (score + self_lint) → sample 채점 → 자기 점수 (임계 0.99999) → frontmatter 체인 무결성. 결과는 `.ShipofTheseus/theseus-self/` 에 누적되어 회차 간 점수 시계열로 회귀를 잡는다.

## 더 읽을거리

- [`examples/`](examples/) — 3 시나리오 (evolving-spec / frozen-spec / fix-bug) — 페이즈 04 의 사전 위임 답 실제 입력 예시.
- [`PHILOSOPHY.md`](PHILOSOPHY.md) — 신뢰 담보의 의미, AIDE 트리 격상, 도자기 장인 비유, Ralph 루프·OhMy 시리즈·우로보로스·Karpathy LLM Wiki·Da Capo 합성 근거, SOLID/TDD/BDD/DDD/Hexagonal 매핑.
- [`BOOTSTRAP.md`](BOOTSTRAP.md) — 본 하네스로 본 저장소를 평가하는 부트스트래핑 절차.
- [`CHANGELOG.md`](CHANGELOG.md) — v0.9.0 → v0.9.16 의미 있는 변경 기록.
- [`INSTALL.md`](INSTALL.md) — 설치·갱신·트러블슈팅.
- [`docs/skills/`](docs/skills/) — 스킬별 가이드 (역할, 입출력, 단독 호출 시점, 자주 묻는 질문).
- [`skills/theseus-harness/conventions/`](skills/theseus-harness/conventions/) — 47 컨벤션 모듈 + 2 도메인 어댑터.

## 라이선스

MIT. [`LICENSE`](LICENSE) 참조.
