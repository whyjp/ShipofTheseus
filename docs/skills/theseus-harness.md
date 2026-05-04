# theseus-harness 가이드 (콘텐츠 source of truth)

## 한 줄 요약

**15 페이즈 + 47 컨벤션 + 18 에이전트 + 2 도메인 어댑터 + 채점기를 한 곳에 담은 단일 source of truth.** [`theseus-orchestrator`](theseus-orchestrator.md) 가 사용자 entry 로 본 스킬을 콘텐츠 source 로 호출 — 두 스킬 모두 설치 필수.

## 언제 호출하는가

ⓐ orchestrator 가 자동으로 본 스킬의 페이즈 본문 / 컨벤션 / 에이전트 프롬프트를 페이즈마다 인용 (LLM 이 SKILL.md 인덱스를 따라 필요한 컨벤션을 페이즈마다 가져감).
ⓑ 본 저장소 자체를 평가할 때 (BOOTSTRAP 자기 평가 — 본 하네스로 본 하네스 회귀, 임계 0.99999).

## 본 스킬이 담는 것

| 카테고리 | 개수 | 위치 |
| ------- | --- | ---- |
| 페이즈 본문 | 15 | [`../../skills/theseus-harness/phases/`](../../skills/theseus-harness/phases/) |
| 컨벤션 | 41 | [`../../skills/theseus-harness/conventions/`](../../skills/theseus-harness/conventions/) |
| 도메인 어댑터 | 2 | [`../../skills/theseus-harness/conventions/domain-adapters/`](../../skills/theseus-harness/conventions/domain-adapters/) |
| 서브 에이전트 프롬프트 | 18 | [`../../skills/theseus-harness/agents/`](../../skills/theseus-harness/agents/) |
| 채점기 | 4+ 모듈 | [`../../skills/theseus-harness/scoring/`](../../skills/theseus-harness/scoring/) |
| 템플릿 | 6+ | [`../../skills/theseus-harness/templates/`](../../skills/theseus-harness/templates/) |

## 47 컨벤션 (의미군별 분류)

### 핵심 (1~22, v0.4.x ~ v0.9.5)

| # | 컨벤션 | 핵심 |
| - | ------ | --- |
| 1 | `interview.md` | 두괄식·1 회 1 질의·숫자 5 개·확증 회귀 + PRD 처리 허들 |
| 2 | `timing.md` | 산출물 헤더 시간 메타·라이브 보고 |
| 3 | `diagrams.md` | 마인드맵→유즈케이스→시퀀스 진화 |
| 4 | `stack.md` | 언어/컴파일러/패키지 매니저 사전 점검 |
| 5 | `build-and-config.md` | sh+bat·TOML·docs/·폐기·병렬·메모리·ruff 통합 |
| 6 | `contracts.md` | 산출물 frontmatter — 단계 재진입 |
| 7 | `models.md` | 에이전트 역할별 Opus/Sonnet/Haiku 매핑 |
| 8 | `competition.md` | 2~3 후보 격리 병렬 경쟁 + 자동 resolve |
| 9 | `autonomy.md` | 자율성 우선·페이즈 04 외 자율 결정 |
| 10 | `lessons.md` | 정체 감지·레슨팩·통째 재작성 강제 |
| 11 | `spec-catalog.md` | 도메인별 NFR 자동 카탈로그 |
| 12 | `resources.md` | 리소스 기반 임계 + 천정 자동 조정 |
| 13 | `checkpoints.md` | 체크포인트·멀티버스 (닥터 스트레인지) |
| 14 | `test-invariants.md` | 테스트 목적 보호·Phase V 측정 유효성 |
| 15 | `dacapo.md` | Da Capo 루프·AIDE × LLM Wiki 결합 |
| 16 | `fragmentation.md` | 파편화 우선·단일 헤비 스킬 금지 |
| 17 | `grades.md` | 그레이드 시스템 (G1 ~ G5) — 내부 모듈레이션만 |
| 18 | `sub-agents.md` | 서브 에이전트 재귀 분해 |
| 19 | `indexing.md` | 산출물 = DB·비직렬성 트리 인덱싱 |
| 20 | `resume.md` | 리줌·state.json |
| 21 | `plan-tree.md` | **AIDE 플랜 트리** — 5 시드 + 6 분기 축 + 토너먼트 |
| 22 | `runtime-prereq.md` | 런타임 사전조건 + Q-D9 + 게이트 7 |

### v0.9.6~v0.9.16 신규 (22건 — AIDE 멀티버스 + content depth + supremacy + 발현 검증 메타)

| # | 컨벤션 | 버전 | 핵심 |
| - | ------ | --- | --- |
| 23 | `nfr-derivation.md` | v0.9.6 | prompt 형용사 → NFR + derived 게이트 자동 도출 |
| 24 | `premortem-friction.md` | v0.9.7 | 콜드리뷰 한 번 더 고민 + 미래 회고 |
| 25 | `sprint-regression-loop.md` | v0.9.8 | self-polishing 임계 도달까지 반복 |
| 26 | `parallel-cold-review.md` | v0.9.8 | N framing fan-out 페이즈 03 다양성 |
| 27 | `mindmap-centrality.md` | v0.9.9 | canonical concept graph 모든 페이즈 backbone |
| 28 | `aide-tree-symmetry.md` | v0.9.10 | universe candidate sequenceDiagram 강제 |
| 29 | `aide-tree-multi-phase.md` | v0.9.10 | 페이즈 02/05/08/11/13 까지 multiverse 확장 |
| 30 | `tournament-blind-rerun.md` | v0.9.10 | 임계 미달 시 anonymize 재경합 |
| 31 | `interface-first-parallel-impl.md` | v0.9.11 | 페이즈 06 인터페이스 의무 + 페이즈 08 fan-out |
| 32 | `analytical-bound-cross-validation.md` | v0.9.12 | closed-form 상한 vs simulated baseline |
| 33 | `multiverse-impl-fan-out.md` | v0.9.12 | universe N 모두 실 코드 의무 |
| 34 | `budget-aware-fallback.md` | v0.9.12 | silent fallback 금지, fallback_reason 명시 |
| 35 | `deep-semantic-intent.md` | v0.9.13 | adjective + noun → implied framing 추출 |
| 36 | `domain-research-stacking.md` | v0.9.13 | 마인드맵 noun → domain adapter stack |
| 37 | `mindmap-quality-gardening.md` | v0.9.13 | Mermaid 의무 + 4 axis × ≥3 sub-node + ≥15 노드 |
| 38 | `ensemble-synthesis-default.md` | v0.9.13 | G4+ tournament 결과 algorithmic union default |
| 39 | `deliverable-hurdle-supremacy.md` | v0.9.14 | **Layer 3 결과물 허들 supremacy** (메모리/컨벤션 override 불가) |
| 40 | `budget-saturation-loop.md` | v0.9.15 | budget ≥80% 사용 강제 + content depth lesson |
| 41 | `score-rubric-objectivity.md` | v0.9.15 | strict checklist self-rating, evidence 1:1 |
| 42 | `convention-traceability.md` | v0.9.16 | **발현 검증 #1** — frontmatter `applied_conventions` 의무 + 활용률 추적 |
| 43 | `sprint-score-delta-tracking.md` | v0.9.16 | **발현 검증 #2** — sprint NN+1 점수 delta + lesson type 라벨링 honesty |
| 44 | `evidence-driven-sprint-planning.md` | v0.9.16 | **발현 검증 #3** — `evidence_missing` → 다음 sprint lesson 자동 매핑 |
| 45 | `cross-universe-lesson-distillation.md` | v0.9.16 | **발현 검증 #4** — 패배 universe 약점 우승 본문 흡수 (차이집합) |
| 46 | `regression-derived-lint-rule-autogen.md` | v0.9.16 | **발현 검증 #5** — 회귀 정정 후 self_lint 룰 자동 신규 (우로보로스) |
| 47 | `polyglot-code-quality.md` | v0.9.16 | **발현 검증 #6** — 9 언어 카탈로그 + 6 메트릭 (Python 종속 해소) |

> 47 카탈로그 누계 — sprint-04 단순화 (PRD 흡수) + sprint-05 ~ sprint-10 추가.

## 채점기

| 모듈 | 역할 |
| ---- | --- |
| `score.py` | 6 차원 가중평균 채점, 임계 0.999, DIP hard cap 0.6, 5 hard cap |
| `fingerprint.py` | frontmatter 핑거프린트 계산·검증·체인 무결성 |
| `self_lint.py` | 본 저장소 60+ 룰 + `--score` 모드 (임계 0.99999) |
| `tournament.py` | universe 점수 산출 + auto_resolve (페이즈 06 + multi-phase 확장) |
| `grade_assess.py` | 호출 직후 그레이드 자동 추정 |
| `rubric.md` | 6 차원 채점 룰 + 0.999 / 0.99999 의미론 |

## 입출력

- **입력**: orchestrator 가 페이즈마다 호출하는 sub-agent 의 페이즈 본문 / 컨벤션 / agent 프롬프트 인용. 또는 사용자 자연어 요청 (단독 호출 시).
- **출력**: 15 페이즈 산출물 모두 + (standalone 시) 코드 + 웹뷰 + interactive-viewer + 핸드오프.

산출물 위치: `.ShipofTheseus/<project_id>/`.

## 자주 묻는 질문

**Q. orchestrator 와 둘 중 무엇을 고르는가?**
A. orchestrator 가 *사용자 entry point*. harness 는 콘텐츠 source — 둘 다 설치 필수다. 본 저장소 자체 평가 (BOOTSTRAP) 시에만 harness 단독 호출 의미가 있다 (자기 게이트 임계 0.99999 검증).

**Q. 47 컨벤션을 다 읽어야 호출 가능한가?**
A. 사용자는 안 읽어도 된다. LLM 이 [`SKILL.md`](../../skills/theseus-harness/SKILL.md) 인덱스를 통해 필요한 컨벤션을 페이즈마다 가져간다. 사용자는 [`README.md`](../../README.md) + [`PHILOSOPHY.md`](../../PHILOSOPHY.md) (AIDE 멀티버스 절) + 본 가이드 정도만 읽으면 충분.

**Q. AIDE 멀티버스가 본 하네스의 진짜 차별 동력인 이유는?**
A. v0.9.10 `aide-tree-multi-phase` + `aide-tree-symmetry` + `tournament-blind-rerun` 3 컨벤션이 페이즈 06 plan-tree 를 *5+ 페이즈 multiverse 확장* + *깊이 강제* + *blind 검증* 으로 격상. v0.9.13 `ensemble-synthesis-default` 가 단일 우승 우주만 채택하던 룰을 *algorithmic union default* 로 정정. v0.9.12 `multiverse-impl-fan-out` 이 universe N 모두 실 코드 의무화. *Theseus 메타포는 브랜딩*, AIDE 멀티버스가 실 차별 동력. 자세히는 [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) "AIDE 멀티버스" 절.

## 더 읽을거리

- [`../../skills/theseus-harness/SKILL.md`](../../skills/theseus-harness/SKILL.md) — 기계 진입점 (LLM 이 읽음).
- [`../../skills/theseus-harness/README.md`](../../skills/theseus-harness/README.md) — 빠른 참조 (사람이 읽음).
- [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — AIDE 멀티버스 격상 + 도자기 장인 + 합성 패턴 6 + SOLID/TDD/DDD 매핑.
- [`../../BOOTSTRAP.md`](../../BOOTSTRAP.md) — 본 하네스로 본 저장소를 평가하는 절차 (60+ self_lint 룰).
- [`../../CHANGELOG.md`](../../CHANGELOG.md) — v0.9.0 → v0.9.15 의미 있는 변경.
