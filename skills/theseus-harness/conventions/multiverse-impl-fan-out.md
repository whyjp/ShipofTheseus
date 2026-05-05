# Multiverse Implementation Fan-Out — universe N 모두 실 코드 의무 + tournament merge

## 한 줄 요약

**페이즈 06 plan-tree 의 N universe 모두 *실 코드 implementation* 의무 (winner-only 패턴 금지).** v01_cold (v0.9.9) 와 본 세션 v099 모두 winner universe 만 implement, 나머지 plan-only — multiverse 경합의 *코드 차원* 부재. 본 컨벤션이 enforcement.

## 1. 결손 진단

기존 [`plan-tree.md`](plan-tree.md) + v0.9.10 [`aide-tree-symmetry.md`](aide-tree-symmetry.md) :

- plan-tree 의 N universe 06-plan.md = ✅ 강제
- aide-tree-symmetry = sequenceDiagram per-universe ✅ 강제
- **그러나 *실 코드 implementation* 은 winner only** — U1/U2 = plan-only, 코드 0

→ multiverse 경합의 *plan 차원* 만 실, *코드 차원* 가짜. tournament merge 는 *plan 비교* 만 — 실 결과 비교 없음.

v01_cold 회차 결과 :
- plan/candidates/{universe-1, universe-2, universe-3}/ 12 산출물 ✅
- code/{universe-1, universe-2, universe-3}/ = **부재**, single `code/mine_sim/` (winner U2 only)

## 2. 운영 룰

### Step 1 — universe 별 code 디렉터리 강제

페이즈 06 결정 후 페이즈 08 impl 진입 시 *N universe 모두* `code/universe-N/` 디렉터리 의무 :

```
code/
├── universe-1/{mine_sim or 도메인 패키지}/   ← 실 코드
├── universe-2/{...}/                        ← 실 코드
├── universe-3/{...}/                        ← 실 코드
└── (winner symlink 또는 채택 후보 메타)
```

각 universe-N/ 는 자기 plan/candidates/universe-N/06-plan.md 따라 *독립 implement*.

### Step 2 — universe 별 sub-agent 병렬 fan-out

[`interface-first-parallel-impl.md`](interface-first-parallel-impl.md) 와 *직교* — interface-first 는 *모듈 단위* fan-out, 본 컨벤션은 *universe 단위* fan-out. 합성 시 :

```
For each universe U_i (parallel):
  spawn agent_universe_U_i (subagent_type="general-purpose"):
    context (fresh):
      - U_i 의 plan/candidates/universe-U_i/06-plan.md
      - U_i 의 plan/candidates/universe-U_i/07-cold-read.md
      - 페이즈 04 NFR-V 답안
      - 페이즈 06 의 인터페이스 정의 (모든 universe 공유)
    instructions:
      - U_i 의 plan 따라 코드 작성
      - 다른 universe 의 코드 모름
      - code/universe-U_i/ 디렉터리에 작성
    output:
      - code/universe-U_i/{도메인 패키지}/*.py
      - tests/test_*.py per U_i
      - 페이즈 08-ε log fragment per U_i

After all N universes complete:
  Tournament merge (실측 차원 추가):
    - 각 universe 의 run_experiment.py 실행 → 실 결과 비교
    - sub-score 차원에 *실 throughput / wallclock / test pass / NFR 충족* 모두
    - winner 채택 또는 ensemble (algorithmic union)
```

### Step 3 — Tournament merge (코드 차원)

기존 [`competition.md`](competition.md) 의 차원별 sub-score 알고리즘 + *실 측정 차원* 추가 :

| 차원 | weight (default) | 측정 |
|---|---|---|
| Sim correctness | 20 | 분석적 상한 vs simulated ratio (analytical-bound-cross-validation 적용) |
| Code quality | 10 | LOC / DIP / test pass |
| Throughput (도메인별) | 10 | implement 결과 절대값 |
| Wall clock | 5 | run_experiment.py 시간 |
| Reproducibility | 10 | byte-repro + seed 분리 |

각 universe 의 sub-score 계산 → *실 차원 비교* 가능. plan 만 비교하던 v0.9.9 한계 보완.

## 3. 그레이드별 활성

| Grade | universe 수 (default) | universe 수 (옵션 default) | impl fan-out | 비고 |
|---|:-:|:-:|:-:|---|
| G2 Simple | 2 | n/a | optional | single 또는 2 후보 |
| G3 Standard | **5** (← 3) | 10 (사용자 ack) | optional (cost vs benefit) | plan + impl 동기 |
| **G4 Complex** | **7** (← 3-4) | 12 | **의무** | 모든 universe code, [`multiverse-width-default-bump.md`](multiverse-width-default-bump.md) bc 정합 |
| G5 Critical | **9** (← 5-6) + 깊이 2 | 16 | 의무 + 깊이 2 의 child universe 도 impl | 깊은 multiverse |

**v0.9.19 sprint-13 갱신** — [`plan-tree.md`](plan-tree.md) 폭 매트릭스 갱신 + 본 컨벤션 동기. budget tight 시 fallback 폭 ([`budget-aware-fallback.md`](budget-aware-fallback.md) `fallback_reason` 의무).

## 4. 안티 패턴

a- **winner only impl** — v0.9.9 의 default 패턴. 본 컨벤션 핵심 위반. self_lint C-MIF (multiverse impl fan-out) 가 G4+ 시 code/universe-N/ 디렉터리 갯수 = plan/candidates/universe-N/ 갯수 검증.
b- **code/universe-N/ 형식만 박고 내용 동일** — *symbolic fan-out*. 각 universe 의 코드가 plan/candidates/universe-N/06-plan.md 의 architecture seed 와 *의미적 매칭* 검증 (LSP / AST diff).
c- **tournament merge 가 *plan 만* 비교** — 실 측정 차원 누락. 본 컨벤션 §2-step 3 의 5 차원 모두 의무.
d- **wall clock budget 으로 N universe 중 일부 skip** — silent. budget-aware-fallback.md 의 fallback_reason frontmatter 명시 의무 (skip 시).

## 5. 호환성

- v0.9.10 aide-tree-symmetry = plan 차원 sequenceDiagram per-universe → 본 컨벤션이 *코드 차원* 으로 확장.
- v0.9.10 tournament-blind-rerun = 임계 미달 시 anonymize champion 재경합 → 본 컨벤션의 코드 fan-out 후 적용 가능.
- v0.9.11 interface-first-parallel-impl = 모듈 단위 fan-out → 본 컨벤션 universe 단위와 *합성* (universe × 모듈 = 2D fan-out).

## 6. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- universe-N/ 디렉터리 = 일반 패턴 (도메인 X).
b- sub-agent fan-out = `Agent` 도구의 일반 메커니즘.
c- 5 차원 sub-score = generic, 도메인 X.

## 7. 자기 검증 (메타)

본 컨벤션 자체에 적용 시 — N universe 컨벤션 작성 fan-out (skeptic / domain / outsider 등 framing 차원 universe) 가능. 본 회차 (v0.9.12) = single-shot.
