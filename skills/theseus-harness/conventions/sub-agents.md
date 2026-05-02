# 서브에이전트 재귀 분해 컨벤션

## 한 줄 요약
**한 모듈이 너무 크거나 복합 책임이면, 그 안의 하위 모듈을 *개별 서브에이전트* 로 디스패치하고 결과를 머지한다.** AIDE tree search 의 분기 + competition.md 의 격리 병렬 + checkpoints.md 의 멀티버스를 *모듈 내부 단위* 로도 동일하게 적용 — 본 컨벤션이 그 재귀의 정식화.

## 출처

ⓐ AIDE Tree Search (Weco AI, 2024) — Draft/Improve/Debug/Memory 4 오퍼레이터를 *모든 깊이* 의 노드에 적용 가능.
ⓑ [`competition.md`](competition.md) §"멀티버스" — 페이즈 단위 N 우주 격리 병렬을 *모듈 단위* 로 일반화.
ⓒ [`checkpoints.md`](checkpoints.md) — 체크포인트 회귀를 *하위 모듈 단위* 로도 누적.
ⓓ 사용자 요청 (2026.05) — "모듈 단위 분해가 필요한 경우 모듈에서 하위 모듈을 개별 서브에이전트로 호출".

## 트리거 조건

부모 에이전트(implementer / planner / critic 등) 가 다음 신호 중 하나를 만나면 *자동* 으로 하위 디스패치:

ⓐ **LOC 임계 초과** — 한 TODO 의 추정 LOC > 200 (또는 그레이드별 임계). 한 호출에 끝낼 수 없는 단위.
ⓑ **복합 책임 신호** — TODO 제목에 "and" / 두 동사 / 두 명사 / 콜론 후 다른 영역 ([`fragmentation.md`](fragmentation.md) §6 의 SRP 위반).
ⓒ **다중 스택** — Go + TypeScript + SQL 처럼 한 모듈이 여러 언어 동시.
ⓓ **명시 분해 요구** — 계획 단계에서 planner 가 `subdivide: true` 마크 박음.
ⓔ **회귀 누적** — 같은 모듈에 회귀 3 회 누적 → checkpoints.md 의 rewrite 가 *하위 분해* 로 전환.

## 분해 깊이 한도

기본 *재귀 깊이 2*:

```
페이즈 08 (구현)
  └─ 모듈 A (TODO T-020)
       ├─ 하위 모듈 A.1  (서브에이전트 1)
       ├─ 하위 모듈 A.2  (서브에이전트 2)
       └─ 하위 모듈 A.3  (서브에이전트 3)
            └─ 손자 모듈 A.3.a  (재귀 깊이 2 — 마지막)
```

깊이 3 이상은 의도 자체가 너무 복잡하다는 신호 → 페이즈 06 (계획) 으로 자동 회귀 ([`checkpoints.md`](checkpoints.md) `find_regression_target("plan_misfit")`).

## AIDE 4 오퍼레이터 — 하위 모듈 단위 매핑

| AIDE Operator | 하위 모듈 단위 적용 |
| ------------- | ------------------ |
| **Draft** | 새 하위 모듈을 빈 상태에서 작성 (부모 lesson_pack + 형제 결과 주입) |
| **Improve** | 기존 하위 모듈을 개선 (단위 테스트 통과 후 다음 sprint 에서 보강) |
| **Debug** | 하위 모듈 fail 시 회귀 — 같은 깊이 다른 후보로 / 또는 부모로 회귀 |
| **Memory** | 한 하위 모듈의 lesson_pack 을 *형제* 모듈에 자동 주입 (병렬 디스패치 후 머지 시) |

## 단독 호출 input 계약

각 분해 스킬을 *단독 호출* 할 때 다음 frontmatter 스펙이 입력 산출물에 박혀 있어야 진입 허용:

| 분해 스킬 | 단독 호출 시 *반드시 있어야 하는* 입력 산출물 |
| -------- | ---------------------------------------- |
| `theseus-intent` | `00-request.txt` (사용자 원문) — 단독 시작점 |
| `theseus-plan` | `intent/01-intent.md` + `intent/04-answers.md` + `intent/05-decisions.md` |
| `theseus-implement` | `plan/06-plan.md` + `plan/07-plan-review.md` |
| `theseus-quality` | `impl/08-impl-log.md` + 실제 코드 디스크 상태 |
| `theseus-sprint` | `quality/09-quality-gate.md` + `intent/04-autonomy.md` (Q-D 답) |
| `theseus-webview` | `intent/01-intent.md` + `plan/06-plan.md` + `impl/08-impl-log.md` (최소) |
| `theseus-handoff` | `quality/09-quality-gate.md` + 가장 최근 sprint report |

각 입력 산출물은 [`contracts.md`](contracts.md) 의 frontmatter (skill_name, skill_version 호환, fingerprint, prev_fingerprint 체인) 검증 통과해야 함. 단독 호출 시작점(`theseus-intent`) 만 예외 — 사용자 원문이 입력.

## 디스패치 의사코드 (`scoring/sub_agent_dispatch.py`)

```python
def dispatch_sub_agents(
    parent_module: Module,
    sub_modules: list[SubModuleSpec],
    parent_lesson_pack: dict,
    mode: str = "parallel",   # "parallel" | "sequential" | "competition"
    autonomy_level: int = 1,
) -> MergeResult:
    """
    부모 모듈이 하위 모듈을 N 서브에이전트로 디스패치.

    - parallel: 같은 형제 N 개를 한 번에 병렬 실행 (Memory 는 *직전 형제* 의 lesson_pack 주입)
    - sequential: 한 형제 끝나야 다음 형제 시작 (Memory 누적)
    - competition: 같은 하위 모듈을 N 후보로 격리 병렬 (competition.md resolve)
    """
    if depth(parent_module) >= 2:
        # 깊이 한도 초과 → 페이즈 06 으로 자동 회귀
        return Result.REGRESS_TO_PLAN_PHASE

    results: list[SubResult] = []
    for spec in sub_modules:
        sub_lesson = build_sub_lesson_pack(
            parent_lesson_pack,
            sibling_results=results if mode == "sequential" else [],
        )
        sub_result = invoke_sub_agent(spec, sub_lesson, autonomy_level)
        results.append(sub_result)

        # 한 형제가 fail + 회귀 누적 임계 도달 → 부모로 회귀
        if sub_result.failed and rewrite_streak(spec) >= 3:
            return Result.REGRESS_TO_PARENT(reason="sub-module 회귀 누적")

    # 머지 — competition.md 알고리즘 차용
    if mode == "competition":
        return select_universe([r.to_universe() for r in results])  # checkpoint.py
    return merge_sub_results(results, parent_module)
```

## 머지 룰

ⓐ **parallel / sequential** — 모든 하위 결과 그대로 채택. 하위 모듈 간 코드 충돌 (같은 파일 수정) 발생 시 [`build-and-config.md`](build-and-config.md) §7 의 *같은 파일 직렬* 가드 위반 — 부모 fail.
ⓑ **competition** — `checkpoint.py` 의 `select_universe` 알고리즘 적용. DIP 위반 우주 즉시 탈락 → 점수 비교 → Δ ≥ 0.05 SELECT / Δ < 0.02 AUTO_MERGE.

## 산출물 — 하위 모듈 체인

각 하위 모듈은 자기 산출물 + 부모 모듈의 fingerprint 를 prev_fingerprint 로 가짐:

```
.ShipofTheseus/<프로젝트>/impl/T-020/
├── parent.md           # 부모 모듈 의사결정 + 분해 사유
├── sub/A.1/
│   ├── code.go
│   ├── tests/
│   └── lesson.md       # 본 하위 모듈에서 배운 것
├── sub/A.2/...
└── merge.md            # 머지 결과 + 채택/탈락 사유
```

부모 모듈의 `impl/08-impl-log.md` 항목에 `subdivision: true` + 하위 모듈 ID 목록 기록.

## 단독 호출 시 하위 분해 가능성

각 분해 스킬이 *단독 호출* 됐을 때도 본 컨벤션이 그대로 동작 — 예:

```bash
# theseus-implement 단독 호출 (이미 plan 산출물 있음)
/theseus-implement --from .ShipofTheseus/<프로젝트>/

# 만약 plan/06-plan.md 의 한 TODO 가 LOC 추정 > 200 이면
# implementer 가 자동 하위 디스패치 (sub_agent_dispatch.py)
```

본 컨벤션은 *모든 분해 스킬에 공통* — 콘텐츠는 단일 source 이고 메커니즘만 모든 스킬에서 호출.

## 그레이드별 활성화

| Grade | 하위 디스패치 | 깊이 한도 | 모드 default |
| ----- | -----------: | --------: | ----------- |
| 1 Trivial | n/a (호출 거부) | n/a | n/a |
| 2 Simple | ❌ (단순 모듈은 분해 안 함) | 0 | n/a |
| 3 Standard | ⚠️ LOC > 300 일 때만 | 1 | sequential |
| 4 Complex | ✅ 기본 활성화 | 2 | parallel |
| 5 Mission Critical | ✅ + competition 강제 | 2 | competition |

## 비용 가드

ⓐ 한 부모 모듈에 동시 디스패치 하위 수 ≤ 5 (`build-and-config.md` 의 RAM 50% 가드 + 동시 LLM 호출 비용).
ⓑ Opus 사용 모듈의 하위 디스패치는 동시 3 개까지 — 비용 상한.
ⓒ 깊이 2 + 동시 5 = 최대 25 서브에이전트 동시 — 임계 초과 시 자동 sequential 모드 전환.

## 안티 패턴

ⓐ **모든 모듈을 무조건 분해** — 본 컨벤션은 *복합 모듈* 에만 적용. SRP 만족 단순 모듈 분해는 비용 폭발.
ⓑ **하위 모듈 간 lesson_pack 미주입** — 형제가 같은 실수 반복. parallel 시 직전 형제 결과를, sequential 시 누적 lesson 을 *반드시* 주입.
ⓒ **머지 사유 미기록** — `merge.md` 가 없으면 사후 회수 시 *왜 이 결과가* 채택됐는지 모름.
ⓓ **재귀 깊이 3 시도** — 본 컨벤션 핵심 위반. 깊이 3 신호는 *의도 자체* 가 너무 큰 신호 → 페이즈 06 자동 회귀.
ⓔ **단독 호출 시 input 계약 검증 생략** — 본 컨벤션의 *단독 호출* 매트릭스를 무시하면 valid 안 한 산출물로 진입 → 핸드오프 깨짐.
