# theseus-harness

## 한 줄 요약

**v0.9.16 — AIDE 멀티버스 코딩 하네스의 콘텐츠 source of truth.** 15 페이즈 + 47 컨벤션 + 18 에이전트 + 2 도메인 어댑터 + 채점기 + 템플릿 + 발현 검증 6 메타 (v0.9.16) + Layer 3 결과물 허들 supremacy. 진짜 차별 동력은 **AIDE 트리 (Plan-Tree × Multi-Phase × Tournament × Ensemble Synthesis × Blind Rerun)**. 메인 진입점은 [`SKILL.md`](SKILL.md) (LLM 이 읽음). 사용자 entry 는 [`../theseus-orchestrator/SKILL.md`](../theseus-orchestrator/SKILL.md) — 본 스킬 동반 필수.

## 빠른 참조

a- [`SKILL.md`](SKILL.md) — 지휘자가 가장 먼저 읽는 라이트 인덱스. 15 페이즈 표 + 모델 컬럼 + 단계 재진입 룰 + 47 컨벤션 인덱스.
b- [`phases/`](phases/) — 페이즈 00–14 (15 페이즈).
c- [`agents/`](agents/) — 18 개 서브에이전트 프롬프트 (각각 권장 모델 명시):
  c-1 핵심 5: `intent-extractor` / `clarifier` / `planner` / `implementer` / `quality-gate`
  c-2 리뷰/검증 4: `doc-reviewer` / `independent-comprehender` / `critic` / `plan-reviewer`
  c-3 TDD 5: `test-architect` / `test-writer` / `implementer` / `refactorer` / `tester`
  c-4 후속 4: `regression-analyst` / `webview-builder` / `interactive-viewer-builder` / `runtime-detector`
  c-5 명명: `project-namer`
d- [`conventions/`](conventions/) — 47 컨벤션 모듈 (각 파일 명시):
  d-1 [`conventions/interview.md`](conventions/interview.md) — 두괄식·1질의·숫자 5개·확증 회귀·PRD 처리 허들
  d-2 [`conventions/timing.md`](conventions/timing.md) — 산출물 헤더 시간 메타·라이브 보고
  d-3 [`conventions/diagrams.md`](conventions/diagrams.md) — 마인드맵→유즈케이스→시퀀스 진화
  d-4 [`conventions/stack.md`](conventions/stack.md) — 언어/컴파일러/패키지 매니저 사전 점검·자율 업데이트
  d-5 [`conventions/build-and-config.md`](conventions/build-and-config.md) — sh+bat·TOML·docs/·폐기·병렬·메모리·ruff 통합
  d-6 [`conventions/contracts.md`](conventions/contracts.md) — frontmatter·단계 재진입
  d-7 [`conventions/models.md`](conventions/models.md) — 에이전트 역할별 Opus/Sonnet/Haiku 매핑
  d-8 [`conventions/competition.md`](conventions/competition.md) — 격리 병렬 경쟁 + 자동 resolve
  d-9 [`conventions/autonomy.md`](conventions/autonomy.md) — 페이즈 04 외 자율 결정
  d-10 [`conventions/lessons.md`](conventions/lessons.md) — 정체 감지·레슨팩·통째 재작성 강제
  d-11 [`conventions/spec-catalog.md`](conventions/spec-catalog.md) — 도메인별 NFR 자동 카탈로그
  d-12 [`conventions/resources.md`](conventions/resources.md) — 리소스 기반 임계 + 천정 자동 조정
  d-13 [`conventions/checkpoints.md`](conventions/checkpoints.md) — 체크포인트·멀티버스 (닥터 스트레인지)
  d-14 [`conventions/test-invariants.md`](conventions/test-invariants.md) — 테스트 목적 보호·Phase V 측정 유효성
  d-15 [`conventions/dacapo.md`](conventions/dacapo.md) — Da Capo 루프·AIDE × LLM Wiki 결합
  d-16 [`conventions/fragmentation.md`](conventions/fragmentation.md) — 파편화 우선·단일 헤비 스킬 금지
  d-17 [`conventions/grades.md`](conventions/grades.md) — 그레이드 시스템 (G1~G5) — 내부 모듈레이션만
  d-18 [`conventions/sub-agents.md`](conventions/sub-agents.md) — 서브에이전트 재귀 분해
  d-19 [`conventions/indexing.md`](conventions/indexing.md) — 산출물 = DB·비직렬성 트리 인덱싱
  d-20 [`conventions/resume.md`](conventions/resume.md) — 리줌 (중단/재개)·state.json
  d-21 [`conventions/plan-tree.md`](conventions/plan-tree.md) — **AIDE 플랜 트리** — 5 시드 + 6 분기 축 + 토너먼트
  d-22 [`conventions/runtime-prereq.md`](conventions/runtime-prereq.md) — Q-D9 + 게이트 7
  d-23 [`conventions/nfr-derivation.md`](conventions/nfr-derivation.md) — prompt 형용사 → NFR 자동 도출 (v0.9.6)
  d-24 [`conventions/premortem-friction.md`](conventions/premortem-friction.md) — 콜드리뷰 한 번 더 고민 + 미래 회고 (v0.9.7)
  d-25 [`conventions/sprint-regression-loop.md`](conventions/sprint-regression-loop.md) — self-polishing 임계 도달까지 반복 (v0.9.8)
  d-26 [`conventions/parallel-cold-review.md`](conventions/parallel-cold-review.md) — N framing fan-out 페이즈 03 다양성 (v0.9.8)
  d-27 [`conventions/mindmap-centrality.md`](conventions/mindmap-centrality.md) — canonical concept graph 모든 페이즈 backbone (v0.9.9)
  d-28 [`conventions/aide-tree-symmetry.md`](conventions/aide-tree-symmetry.md) — universe candidate sequenceDiagram 강제 (v0.9.10)
  d-29 [`conventions/aide-tree-multi-phase.md`](conventions/aide-tree-multi-phase.md) — 페이즈 02/05/08/11/13 multiverse 확장 (v0.9.10)
  d-30 [`conventions/tournament-blind-rerun.md`](conventions/tournament-blind-rerun.md) — 임계 미달 시 anonymize 재경합 (v0.9.10)
  d-31 [`conventions/interface-first-parallel-impl.md`](conventions/interface-first-parallel-impl.md) — 페이즈 06 인터페이스 의무 + 페이즈 08 fan-out (v0.9.11)
  d-32 [`conventions/analytical-bound-cross-validation.md`](conventions/analytical-bound-cross-validation.md) — closed-form 상한 vs simulated baseline (v0.9.12)
  d-33 [`conventions/multiverse-impl-fan-out.md`](conventions/multiverse-impl-fan-out.md) — universe N 모두 실 코드 의무 (v0.9.12)
  d-34 [`conventions/budget-aware-fallback.md`](conventions/budget-aware-fallback.md) — silent fallback 금지 + fallback_reason 명시 (v0.9.12)
  d-35 [`conventions/deep-semantic-intent.md`](conventions/deep-semantic-intent.md) — adjective + noun → implied framing (v0.9.13)
  d-36 [`conventions/domain-research-stacking.md`](conventions/domain-research-stacking.md) — 마인드맵 noun → domain adapter stack (v0.9.13)
  d-37 [`conventions/mindmap-quality-gardening.md`](conventions/mindmap-quality-gardening.md) — Mermaid 의무 + 4 axis × ≥3 sub-node (v0.9.13)
  d-38 [`conventions/ensemble-synthesis-default.md`](conventions/ensemble-synthesis-default.md) — G4+ tournament 결과 algorithmic union default (v0.9.13)
  d-39 [`conventions/deliverable-hurdle-supremacy.md`](conventions/deliverable-hurdle-supremacy.md) — **Layer 3 결과물 허들 supremacy** (v0.9.14)
  d-40 [`conventions/budget-saturation-loop.md`](conventions/budget-saturation-loop.md) — budget ≥80% 사용 강제 + content depth lesson (v0.9.15)
  d-41 [`conventions/score-rubric-objectivity.md`](conventions/score-rubric-objectivity.md) — strict checklist self-rating, evidence 1:1 (v0.9.15)
  d-42 [`conventions/convention-traceability.md`](conventions/convention-traceability.md) — 페이즈 산출물 frontmatter applied_conventions 의무 + 활용률 추적 (v0.9.16 발현 검증 #1)
  d-43 [`conventions/sprint-score-delta-tracking.md`](conventions/sprint-score-delta-tracking.md) — sprint NN+1 점수 delta + lesson type 라벨링 정직성 (v0.9.16 #2)
  d-44 [`conventions/evidence-driven-sprint-planning.md`](conventions/evidence-driven-sprint-planning.md) — evidence_missing → 다음 sprint lesson 자동 매핑 (v0.9.16 #3)
  d-45 [`conventions/cross-universe-lesson-distillation.md`](conventions/cross-universe-lesson-distillation.md) — 패배 universe 약점 우승 본문 흡수 + 차이집합 합성 (v0.9.16 #4)
  d-46 [`conventions/regression-derived-lint-rule-autogen.md`](conventions/regression-derived-lint-rule-autogen.md) — 페이즈 11 4 분류 정정 후 self_lint 룰 자동 신규 (v0.9.16 #5)
  d-47 [`conventions/polyglot-code-quality.md`](conventions/polyglot-code-quality.md) — 언어 무관 메트릭 + 9 언어 표준 도구 카탈로그 (v0.9.16 #6)
  d-48 [`conventions/anti-patterns.md`](conventions/anti-patterns.md) — A1~A10 공통 안티 패턴 카탈로그 (v0.9.16 sprint-11 fragmentation 분리)
  d-49 [`conventions/intent-completeness.md`](conventions/intent-completeness.md) — 페이즈 01 §k 9 sub-criterion (limitations + data-derived 분리 등) (v0.9.18 sprint-12)
  d-50 [`conventions/process-flow-coherence.md`](conventions/process-flow-coherence.md) — 페이즈 09 게이트 8: cycle / state machine / workflow 정합 (v0.9.18)
  d-51 [`conventions/domain-failure-patterns.md`](conventions/domain-failure-patterns.md) — 페이즈 09 게이트 9: 도메인 어댑터 failure_patterns 자기 검증 (v0.9.18)
  d-52 [`conventions/decision-support-framing.md`](conventions/decision-support-framing.md) — 페이즈 14 Q 답에 operational/trade-off/opportunity-cost 본문 (v0.9.18)
  d-53 [`conventions/domain-adapters/`](conventions/domain-adapters/) — 도메인 어댑터 2개 (v0.9.13~)
  d-54 [`conventions/mindmap-richness-default.md`](conventions/mindmap-richness-default.md) — 마인드맵 A 등급 default 격상 (≥25 노드 / 4 axis × ≥4 sub) (v0.9.19 sprint-13)
  d-55 [`conventions/per-module-diagram-fan-out.md`](conventions/per-module-diagram-fan-out.md) — use-case / sequence 모듈별 분할 default (v0.9.19)
  d-56 [`conventions/multiverse-width-default-bump.md`](conventions/multiverse-width-default-bump.md) — 폭 default G2=2 / G3=5 / G4=7 / G5=9 + 옵션 default G3=10/G4=12/G5=16 (v0.9.19)
  d-57 [`conventions/intent-plan-impl-sprint-trinity.md`](conventions/intent-plan-impl-sprint-trinity.md) — sprint loop 3 axis (intent / plan / impl) × ≥ 2 (v0.9.19)
  d-58 [`conventions/grader-in-sprint.md`](conventions/grader-in-sprint.md) — sprint stop = `auto AND shadow AND axis AND budget` (4 conjunction) + zero-context shadow grader (v0.9.20 sprint-14)
  d-59 [`conventions/contested-decision-multiverse.md`](conventions/contested-decision-multiverse.md) — tournament axis = paradigm → contested decisions + per-universe code spike (v0.9.20)
  d-60 [`conventions/directional-simplification.md`](conventions/directional-simplification.md) — 페이즈 05 simplification 표 의무 (direction ↑/↓/? + magnitude ±%) (v0.9.20)
  d-61 [`conventions/commentary-policy.md`](conventions/commentary-policy.md) — Q-D-AUDIENCE flag → 페이즈 08 implementer 주석 density swap (v0.9.20)
  d-62 [`conventions/measurement-contract.md`](conventions/measurement-contract.md) — 페이즈 06 metric method 의무 (sample / accumulate / reconstruct + 정당화) (v0.9.20)
  d-63 [`conventions/rubric-driven-doc-skeleton.md`](conventions/rubric-driven-doc-skeleton.md) — RubricAdapter (yaml/markdown/openapi) → `_skeleton/` 빈 헤더 + fallback generic ToC (v0.9.20)
  d-64 [`conventions/rubric-targeted-quality-gates.md`](conventions/rubric-targeted-quality-gates.md) — 페이즈 09 RTG-* (rubric bullet → yes/no) + bj 와 같은 adapter 공유 (v0.9.20)
e- [`scoring/rubric.md`](scoring/rubric.md) + [`scoring/score.py`](scoring/score.py) — 6 차원 채점, **임계 0.999** (G3/G4 통일, v0.9.15) / **0.99999** (G5), **DIP 위반 단독 hard cap 0.6**.
f- [`scoring/fingerprint.py`](scoring/fingerprint.py) — frontmatter 핑거프린트 계산·검증·체인 무결성.
g- [`scoring/self_lint.py`](scoring/self_lint.py) + [`scoring/test_self_lint.py`](scoring/test_self_lint.py) — 본 저장소 자기 평가 60+ 룰 + `--score` 모드, 임계 **0.99999** (자기 표준).
h- [`scoring/tournament.py`](scoring/tournament.py) — universe 점수 산출 + auto_resolve. 페이즈 06 plan-tree + v0.9.10 multi-phase 확장 (페이즈 02/05/08/11/13) 모두 활용.
i- [`scoring/grade_assess.py`](scoring/grade_assess.py) — 호출 직후 그레이드 자동 추정 (Q-G1 객관식 사용자 확정).
j- [`templates/`](templates/) — intent / plan / sprint-report / naming / universe-meta 템플릿 + bun 기반 webview 스캐폴드.

## 주요 원칙 (v0.9.16)

a- **AIDE 멀티버스가 진짜 차별 동력** — 페이즈 06 plan-tree + v0.9.10 multi-phase 확장 (5+ 페이즈) + ensemble synthesis default + tournament blind rerun. 닥터 스트레인지처럼 *결정 이전에 다 가본다*.
b- **의존성 역전(DIP) 이 SOLID 중 최우선** — 위반은 단독 hard fail (cap 0.6).
c- **관심사 분리(SoC) 가 단위 테스트 기반** — 모듈 경계를 기능보다 먼저.
d- **장인의 도자기처럼** 깊은 품질 위반 (DIP/SOLID · 코드 오류 누적 · 기획-구현 갭 · 성능/NFR 미달 · 의도 표류 · 정체/회귀 누적) *어느 차원* 이라도 깊이 임계 초과면 모듈을 깨고 페이즈 06 부터 다시 빚는다 (페이즈 11 `re-architect`). 트리거 매핑은 [`conventions/lessons.md`](conventions/lessons.md) + [`conventions/checkpoints.md`](conventions/checkpoints.md) 의 11 분류.
e- **모든 산출물은 파일** — `.ShipofTheseus/<프로젝트>/` 트리에 카테고리별로 떨어진다. fingerprint chain 으로 단계 재진입.
f- **무한 스프린트 루프 + budget 80% 사용 강제** (v0.9.15) — 임계 도달해도 budget ≥ 80% 까지 sprint 추가, 추가 sprint 의 lesson type = *content depth* (enforcement 아님).
g- **Layer 3 결과물 허들 supremacy** (v0.9.14) — standalone 컨텍스트 시 코드 + 실행 + 측정값 의무. 메모리 / 컨벤션 override 불가, 사용자 명시 ack (Q-D-DELIVERABLE-MODE = 3) 만 면제.
h- **Score rubric objectivity** (v0.9.15) — handoff self-estimate 가 evidence 1:1 매칭, evidence_missing 명시 의무. agent self-rating noise 차단.
i- **시간 라이브 표시** — 매 산출물 헤더에 시작·소요·누적·현재.
j- **백엔드 기본값 Go** — 사용자 명시 없을 때.
k- **theseus-view (페이즈 12) + interactive-viewer (페이즈 13)** — 스킬 진행 추적 + 프로젝트 output observability 분리. 하네스 메타와 결과 프로덕트 emit 분리.

## 산출물 트리 (한 프로젝트 실행 결과)

```
.ShipofTheseus/<프로젝트명>/
├── timing/start.json
├── naming/{00-candidates.md, 00-naming.md}
├── intent/{01-intent.md, 02-intent-review.md, 03-comprehension.md, 04-{questions,answers,autonomy,stack,verification,runtime-prereq}.md, 05-critique.md}
├── plan/{06-plan.md, 07-plan-review.md, tournament.md, candidates/universe-N/...}
├── impl/{08-impl-log.md, 08-test-scope.md}
├── code/                              # standalone 컨텍스트 시 (Layer 3 결과물 허들 H1~H5)
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, unit.json, e2e.json}
├── webview/                           # 페이즈 12 — theseus-view (스킬 진행 추적, bun + hono + react)
├── interactive-viewer/                # 페이즈 13 — 프로젝트 output observability (도메인별 dashboard)
└── handoff/14-handoff.md              # score-rubric-objectivity self_estimate frontmatter
```

## 채점 검증

```bash
python -m pytest scoring/ -q
python scoring/self_lint.py
python scoring/self_lint.py --score
```

또는 일괄:

```bash
./scripts/self-check.sh        # linux/mac
scripts\self-check.bat         # windows
```

## 호출

Claude Code 세션에서:

```
/shipoftheseus:theseus-orchestrator <요구사항>   # 사용자 entry — 권장
/shipoftheseus:theseus-harness <요구사항>        # 콘텐츠 source 단독 — BOOTSTRAP 자기 평가용
```

LLM 이 [`SKILL.md`](SKILL.md) 를 읽고 페이즈 00 부터 시작한다.

## 더 읽을거리

a- [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — AIDE 멀티버스 (진짜 차별 동력), 도자기 장인 비유, 합성 패턴 6 (Ralph/OhMy/우로보로스/AIDE/Wiki/Da Capo), SOLID/TDD/BDD/DDD/Hexagonal 매핑.
b- [`../../INSTALL.md`](../../INSTALL.md) — git clone 기반 설치, 플러그인 매니페스트, 트러블슈팅.
c- [`../../BOOTSTRAP.md`](../../BOOTSTRAP.md) — 본 하네스로 본 저장소를 평가하는 부트스트래핑 절차 (60+ self_lint 룰).
d- [`../../CHANGELOG.md`](../../CHANGELOG.md) — v0.9.0 → v0.9.16 의미 있는 변경.
e- [`../../docs/skills/theseus-harness.md`](../../docs/skills/theseus-harness.md) — 사람용 가이드 (역할, 입출력, FAQ).
