# 플랜 트리 (AIDE Plan Tree) 컨벤션

## 한 줄 요약

**Phase 06 의 결과는 단일 플랜이 아니라 N 개 우주의 트리다.** 각 우주는 격리된 별개 분기 시드 (도메인 우선 / 어댑터 우선 / 미니멀 / TDD 우선 / 레이어 엄격) 에서 출발해 독립 에이전트가 병렬로 자기 플랜을 작성하고, 우주 간 모호함이 남으면 자식 우주로 재귀 분기한다. 토너먼트가 우승 우주를 뽑고, 그 우주의 플랜이 Phase 07 콜드 재이해 → Phase 08 구현으로 흐른다. **본 프로젝트의 두 강점 — 회귀성 (recursion) + 병렬성 (parallelism) — 을 페이즈 06 에 노출한 것.**

## 왜 트리인가

a- **단일 플랜 → 단일 구현** 회귀에서 멀티버스 (구현 경쟁) 만 돌리면 *이미 좁혀진 분할 위에서* 노이즈만 비교하게 된다. 분할 자체가 모호한 케이스를 못 잡음.
b- **플랜 = 분할 결정** 이고, 분할은 LLM 비결정성이 가장 크게 발산하는 지점. 평행 우주에서 동시 탐색 → 토너먼트 → 우승 = 가장 의미 있는 노이즈 분리 지점.
c- 닥터 스트레인지가 14,000,605 미래를 본 이유와 같다 — *결정 이전에* 다 가본다.
d- 회귀: 우주 안에 또 우주. 병렬: 형제 우주는 동시 디스패치. 두 강점이 페이즈 06 한 곳에 동시 표현됨.

## AIDE 의 의미

**A**I-**D**riven **E**xploration — 트리 탐색은 사람의 휴리스틱 (어떤 분기를 쳐야 할지) 이 아니라 LLM 비결정성 자체를 분기 동력으로 사용. 시드 카탈로그가 *의미 있는 분기 방향* 을 강제함으로써 노이즈 분기 대신 의미 분기를 만든다.

## 트리 구조 (IDE 스타일 디렉터리)

```
.ShipofTheseus/<프로젝트>/plan/
├── tournament.md                     # 최종 우승 우주 + 의사결정 트레이스 (사용자 대면 단일 파일)
├── 06-plan.md                        # 우승 우주의 플랜 사본 (호환성: 다음 페이즈 입력)
├── 07-plan-review.md                 # 우승 우주의 콜드 재이해
└── candidates/
    ├── universe-1-domain-first/
    │   ├── meta.md                   # 시드, 진입 가설, score
    │   ├── 06-plan.md                # 본 우주의 플랜 (Mermaid 시퀀스 동봉)
    │   ├── 07-cold-read.md           # plan-reviewer 의 4 답
    │   └── children/                 # 깊이 ≥ 2 시 재귀
    │       ├── universe-1-a-by-bounded-context/
    │       └── universe-1-b-by-aggregate-root/
    ├── universe-2-adapter-first/
    │   └── ...
    ├── universe-3-minimal-subtraction/
    │   └── ...
    ├── universe-4-tdd-topology/      # G5 만
    │   └── ...
    └── universe-5-strict-layering/   # G5 만
        └── ...
```

각 우주 디렉터리는 [`competition.md`](competition.md) 의 격리 룰을 따른다 — **형제 우주의 산출물을 절대 보지 않음**.

## 그레이드별 트리 매트릭스

| Grade | 폭 (root 우주 수) | 깊이 cap | 분기 시드 (필수) | 분기 시드 (옵션) |
| ----- | :---------------: | :------: | ---------------- | ---------------- |
| **G1** Trivial | 1 (트리 비활성) | — | — | — |
| **G2** Simple | 1 (트리 비활성) | — | — | — |
| **G3** Standard | 2 | 1 | domain-first, adapter-first | minimal |
| **G4** Complex | 3 | 1 (옵션 2) | domain-first, adapter-first, minimal | tdd-topology |
| **G5** Critical | 5 | 2 (강제) | 5 시드 모두 | — |

**디폴트 활성화** — G3 이상이면 자동으로 트리. 단일 플랜 모드는 G1·G2 만. 본 매트릭스는 [`grades.md`](grades.md) 의 모듈레이션 표에 row 로 편입됨.

## 분기 시드 카탈로그 (5 시드)

각 시드는 planner 에이전트의 프롬프트 prefix 로 들어가 동일 입력에서 *의미적으로 다른* 분할을 강제한다.

### 1- domain-first (도메인 우선)

> **분할 동력**: 비즈니스 boundary = 모듈 boundary. 동사형 도메인 (`auth`, `billing`, `inventory`) 별로 모듈 분리.
> **잘 맞는 사례**: 요구사항 문서가 비즈니스 워크플로 중심.
> **약점**: 어댑터 다양성 (다중 DB, 다중 인증 공급자) 표현이 약함.

### 2- adapter-first (어댑터 우선)

> **분할 동력**: 외부 의존 (DB / Cache / 외부 API / 인증 공급자) 의 다양성 = 모듈 boundary. 포트 인터페이스를 먼저 정의, 어댑터마다 구현.
> **잘 맞는 사례**: 다중 DB 마이그레이션, 다중 결제 게이트웨이.
> **약점**: 단순한 도메인엔 over-abstraction.

### 3- minimal-subtraction (미니멀 / 감산)

> **분할 동력**: 모듈 수 최소화. 같은 책임을 합쳐 단일 모듈로. *추가 보다 감산을 보상*.
> **잘 맞는 사례**: MVP, throwaway, 빠른 검증.
> **약점**: 확장성 제로. SOLID 위반 가능.

### 4- tdd-topology (TDD 우선) — G4 옵션, G5 필수

> **분할 동력**: 테스트하기 좋은 토폴로지가 모듈 토폴로지를 결정. 단위 ↔ 통합 ↔ E2E 비율을 먼저 그리고 그에 맞춰 모듈 자름.
> **잘 맞는 사례**: 회귀 위험 큰 시스템, 결제·인증.
> **약점**: 도메인 경계가 자연스럽지 않을 수 있음.

### 5- strict-layering (레이어 엄격) — G5 필수

> **분할 동력**: domain / application / adapter / ui / infra 5 레이어 빡빡 분리. 도메인은 어댑터 import 절대 금지, application 만이 어댑터 호출. DIP 가장 빡빡.
> **잘 맞는 사례**: 미션 크리티컬, 장기 유지보수.
> **약점**: 보일러플레이트 비용.

각 우주의 `meta.md` 에 시드 ID 와 *왜 이 시드가 본 의도에 맞을 가설인가* 한 단락 기록 (planner 가 작성).

## 깊이 재귀 (자식 우주)

부모 우주가 자기 플랜 안에서 다음 모호함을 *남긴 채* 제출하면 자식 우주로 재귀 분기:

a- 한 모듈의 **하위 분할** 이 둘 이상 가능 (예: `auth` 를 `JWTAuth` + `SessionAuth` 로 또는 `AuthCore` + `AuthPolicy` 로).
b- **포트 인터페이스의 입자도** 가 길항 (메서드 5개 vs 메서드 12개).
c- **테스트 토폴로지** 가 두 가지 모두 합리적 (포트 단위 통합 vs 어댑터 단위 단위).

자식 우주의 시드는 부모 시드를 *상속하되 한 차원만* 다르게 — 예: 부모 `domain-first` 의 자식 두 개 = `domain-first/by-bounded-context` + `domain-first/by-aggregate-root`. 자식 디렉터리 이름에 분기 차원 인코딩.

깊이 cap (그레이드 매트릭스 위) 도달 시 더 분기 안 함. 그래도 모호하면 페이즈 04 인터뷰 회귀 (Q-D 신규 답안 후보).

## 격리 + 병렬 디스패치

[`competition.md`](competition.md) §격리 + §병렬 디스패치 그대로 재사용. 본 컨벤션이 추가하는 것은:

a- **시드별 프롬프트 prefix** — `agents/planner.md` 의 시드별 카탈로그 인용.
b- **자원 가드 강화** — 동시 디스패치 우주 ≤ 5 (G5 cap), 자식 우주 디스패치는 부모 우주 완료 후. RAM/모델 비용은 [`build-and-config.md`](build-and-config.md) §7 + [`models.md`](models.md) 의 합산 가드.
c- **모델 라우팅** — 시드 1·2·5 = Opus (구조 결정), 시드 3·4 = Sonnet (단순/테스트 패턴) 권장.

## 토너먼트 채점

각 우주의 플랜에 **fresh** plan-reviewer 에이전트 (`agents/plan-reviewer.md` 콜드 모드) 가 4 질문 답을 산출:

1- 이 계획만 보면 어떤 기능을 만드는 것인가?
2- 어떤 TODO 부터 시작하겠는가?
3- 과소 명세·과대 사이즈·순서 어긋남이 보이는 TODO 는?
4- 누락·잘못된 의존은?

채점 차원 (5 종, 각 0.0~1.0):

| 차원 | 의미 | 가중 |
| ---- | ---- | ---: |
| `cold_recall` | 1- 답이 `intent/01-intent.md` 의 "무엇을" 과 의미상 일치 | 0.30 |
| `dip_strictness` | DIP 위반 TODO 수 (역 비례) | 0.25 |
| `simplicity` | 모듈 수 / 총 TODO 수 (적을수록 가산, 단 단순화 한도 LOC 가드) | 0.20 |
| `test_topology` | leaf TODO 마다 테스트 TODO 존재 + E2E 시나리오 cover | 0.15 |
| `fe_be_parity` | FE 와 BE TODO 가 의존 그래프에서 짝맞춤 (G4 이상) | 0.10 |

**`cold_recall < 0.6` 인 우주는 즉시 탈락** — 의도를 인코딩 못한 플랜은 점수 무관 폐기.

## 자율 결정 (재사용)

[`competition.md`](competition.md) §자동 resolve 알고리즘 그대로:

a- **Δ ≥ 0.05** → SELECT (top 우주 채택, 패자 우주는 `losers/` 로 이동)
b- **0.02 ≤ Δ < 0.05** → 차원별 분석 → 한쪽 모든 차원 우위면 SELECT, 분점이면 MERGE_BY_DIMENSION
c- **Δ < 0.02** → AUTO_MERGE (`simplicity` 차원 우위 우주 base, 다른 우주의 차별 강점만 머지)
d- **모든 우주 cold_recall < 0.6** → HALT_AND_ASK_USER (의도 자체가 모호 → 페이즈 04 회귀)

[`autonomy.md`](autonomy.md) 위임 수준 1·2 면 ack 없이 적용. `tournament.md` 가 사후 audit trail.

## 산출물

### `plan/tournament.md` (사용자 대면 단일 파일)

```markdown
---
skill_name: theseus-orchestrator
phase: 06
project_id: <명명 페이즈 산출>
fingerprint: <자동>
prev_fingerprint: <intent/05-decisions.md 핑거프린트>
produced_at: <ISO8601>
---

# 플랜 토너먼트 — <프로젝트>

## 우주 카탈로그
| 우주 | 시드 | cold_recall | dip_strictness | simplicity | test_topology | fe_be_parity | 종합 |
| ---- | ---- | ----------: | -------------: | ---------: | ------------: | -----------: | ---: |
| 1-domain-first | domain | 0.92 | 0.95 | 0.78 | 0.90 | 0.85 | 0.892 |
| 2-adapter-first | adapter | 0.88 | 0.97 | 0.65 | 0.92 | 0.88 | 0.871 |
| 3-minimal-subtraction | minimal | 0.94 | 0.80 | 0.95 | 0.78 | 0.70 | 0.847 |

## 결정: SELECT (Δ = 0.021 → 차원별 분석 → 1 모든 차원 우위는 아니나 simplicity 분점, MERGE_BY_DIMENSION 발동)

## 머지 디테일
- 1 의 도메인 분할 (`auth`, `billing`, `inventory`) base
- 3 의 미니멀 어댑터 1개 (단일 DB 가정) 머지
- 2 의 포트 추상화는 *연결 TODO* 단계에 옵션으로 보존 (현재는 진입 안 함)

## 패자 우주
`plan/candidates/losers/universe-2-adapter-first/`, `universe-3-minimal-subtraction/`

## 다음 페이즈 입력
`plan/06-plan.md` ← `candidates/universe-1-domain-first/06-plan.md` 사본 + 머지 패치
```

### `plan/06-plan.md`

우승 우주의 플랜 사본 (Phase 07/08 호환). 사본 헤더에 `source_universe: universe-1-domain-first` + `merged_from: [universe-3-minimal-subtraction]` 명시.

### `plan/candidates/universe-N/meta.md`

```markdown
---
universe_id: 1-domain-first
seed: domain-first
parent: null
depth: 1
hypothesis: <왜 이 시드가 본 의도에 맞다 가정했는지 한 단락>
score:
  cold_recall: 0.92
  dip_strictness: 0.95
  simplicity: 0.78
  test_topology: 0.90
  fe_be_parity: 0.85
  overall: 0.892
status: winner | runner_up | loser | merged
---
```

## 자원 가드

a- **동시 root 우주 디스패치** ≤ 5 (G5 cap). G3 = 2, G4 = 3, G5 = 5.
b- **자식 우주는 부모 우주 완료 후** 디스패치 — 깊이 1 동시성과 깊이 2 동시성을 곱해서 디스패치하지 않음. 한 깊이씩 layer 진행.
c- **취소 가능** — `tournament.md` 가 진행 중이면 [`timing.md`](timing.md) 라이브 보고에 "토너먼트 진행 중 (3/3 우주 작업 중)" 명시. 사용자가 비용 보고 중단 요청 시 깊이 1 결과로 fallback.
d- **모델 비용 합산** — Opus 우주 ≥ 3 면 [`models.md`](models.md) 의 비용 가드 트리거 → 시드 4·5 자동 Sonnet 다운그레이드 (cold_recall 가중 보전).

## 자율 결정 보고 (timing.md 라이브)

```
Phase 06 토너먼트 시작 (G4, 3 우주 / 깊이 1)
├─ universe-1-domain-first    [Opus, dispatched 12:34:00]
├─ universe-2-adapter-first   [Opus, dispatched 12:34:00]
└─ universe-3-minimal-subtraction [Sonnet, dispatched 12:34:00]

12:38:42  토너먼트 완료
결정: SELECT/MERGE — 1 base + 3 의 미니멀 어댑터
근거: Δ = 0.021, simplicity 분점 → MERGE_BY_DIMENSION
패자: 2 (adapter-first) → losers/
```

인터럽트 0 — 사용자 ack 절대 안 부름 (자율 결정 룰).

## 안티 패턴

a- **트리 = 단일 플랜 N 회 복사** — 시드 강제 안 하면 LLM 비결정성이 표면 차이만 만들고 점수 모두 비슷 (Δ < 0.02). 시드 카탈로그가 강제력.
b- **깊이 무한** — 깊이 cap 없이 재귀하면 모호함이 영원히 안 끝남. G5 도 깊이 2 까지.
c- **우주 5개 초과** — 비교 노이즈에 묻힘. 시드 카탈로그가 5 종이 cap.
d- **우승 우주만 보고 패자 디렉터리 즉시 삭제** — 사후 audit / regression bisect 가 패자 우주를 참조할 수 있음. `losers/` 보존 (회수 페이즈 13 핸드오프 시 정리).
e- **토너먼트 결과 로깅 누락** — `tournament.md` 없으면 "왜 이 플랜이 이겼지" 답 못함. 인터럽트 0 룰의 신뢰 담보가 무너짐.
f- **시드 직접 LLM 에 노출 안 하고 추측 시킴** — planner 프롬프트에 시드 prefix 가 *문자 그대로* 포함되어야 함. 짐작에 의존하면 시드별 우주가 합쳐짐.

## 적용 페이즈

- **페이즈 06 (계획)** — 본 컨벤션의 home. 디폴트 활성화 (G3+).
- 페이즈 08 (구현) 의 멀티버스는 [`competition.md`](competition.md) 가 따로 정의 — 플랜 트리와 *중첩 안 함* (한 페이즈 = 한 토너먼트).
- 페이즈 11 (회귀 바이섹트) 의 `revert` vs `re-architect` 길항도 [`competition.md`](competition.md) 의 트리거 c 로 처리 — 본 컨벤션 적용 안 함.

## 회귀성·병렬성 — 강점 인코딩 명시

본 프로젝트의 두 강점이 페이즈 06 한 곳에서 동시 표현되는 지점이 본 컨벤션:

a- **회귀성** — 우주 안에 우주 (자식 분기) → 페이즈 06 의 self-similar 호출. 부모 frontmatter chain 이 child 의 prev_fingerprint 가 됨.
b- **병렬성** — 형제 우주 격리 동시 디스패치. 한 메시지에 N `Agent` 호출. [`build-and-config.md`](build-and-config.md) §7 자원 가드.
c- 두 강점의 곱 — 깊이 D × 폭 W 이면 D+W 개 디스패치 (depth 별 layer). 5 우주 × 깊이 2 = 5+5 = 10 호출, 비용 가드 안.
d- 강점이 안 닿는 페이즈에서는 본 컨벤션 비활성 (G1·G2). 모든 페이즈에 트리 강제는 안티 패턴 a.

## 후속 (sprint-02-c)

a- `agents/planner.md` 시드별 프롬프트 prefix 추가 (별도 PR).
b- ✅ `scoring/tournament.py` — 우주별 점수 산출 + auto_resolve 호출 헬퍼 (sprint-02-e #2 출하). CLI: `tournament.py resolve --plan-root <path>` → `plan/tournament.md` 자동 생성.
c- `phases/06-plan.md` 본 컨벤션 흡수 + 트리거 → 디폴트 격상.
d- ✅ `templates/universe-meta.template.md` 신규 (sprint-02-e #5 출하). frontmatter 키 (universe_id / seed / depth / hypothesis / score / status) + 본문 reference.
e- self_lint C-PT 룰 — `plan/tournament.md` + `plan/candidates/` 무결성 검증.

## 분기 축 카탈로그 (sprint-05-b)

플랜-트리 폭 확장 (G3 폭 3 / G4 폭 4 / G5 폭 6) 시 *형식적 분기 (네이밍만 다른 plan)* 가 아닌 *본질적 의미 분기* 를 강제하는 ≥6 axis 카탈로그. planner 서브에이전트가 폭 N 진행 시 본 카탈로그에서 *상위 N 개 axis* 를 선택해 universe seed 부여.

| axis | universe-A stance | universe-B stance | 적합 도메인 |
|----|----|----|----|
| **process-vs-data** | process-first (각 entity = 활성 generator/coroutine) | data-first (state arrays + event scheduler) | DES, simulation, queueing |
| **sync-vs-async** | 동기 인터페이스 (request/response) | 비동기 (event/queue/promise) | API, ETL, 실시간 |
| **centralized-vs-distributed** | 중앙 코디네이터 (Dispatcher/Scheduler) | 분산 (peer-to-peer, eventual consistency) | 분산 시스템, 마이크로서비스 |
| **dynamic-vs-static** | 런타임 결정 (re-evaluate per cycle) | 컴파일/init 시 결정 (precompute) | dispatch/routing/binding |
| **push-vs-pull** | producer 가 consumer 에 push (broadcast) | consumer 가 pull (poll/fetch) | 데이터 fetch, eventing |
| **mutable-vs-immutable** | 가변 상태 (in-place update) | 불변 + 새 값 (functional/persistent) | 상태 관리, replay |

추가 후보 axis (확장 카탈로그) :
- **eager-vs-lazy** : 즉시 계산 vs 지연 (iterator/promise)
- **typed-vs-duck** : 명시 타입 vs 덕 타이핑
- **monolith-vs-microservice** : 단일 배포 단위 vs 다중
- **stream-vs-batch** : 연속 흐름 vs 배치 윈도우
- **optimistic-vs-pessimistic** : 낙관적 락 vs 비관적 락

본 카탈로그는 *외부 패턴 차용 아님* — 본 하네스의 plan-tree 본래 의도 (의미 분기) 를 *명시적 enumeration* 으로 강화. 메모리 `feedback_borrow_discipline.md` 정합.

## v0.9.16 sprint-10 — 패배 universe 학습 전이 (cross-universe-lesson-distillation)

[`cross-universe-lesson-distillation.md`](cross-universe-lesson-distillation.md) (v0.9.16 신규) — tournament resolve 시 *우승 universe 만 채택* 으로 끝나지 않고, 패배 universe 의 *핵심 약점 ≥ 1-2 줄* 을 우승 본문에 흡수 의무. forward exploration (본 컨벤션) + backward weakness transfer (cross-universe-lesson) 결합으로 multiverse 의 *모든 학습* 이 다음 페이즈로 전이.
