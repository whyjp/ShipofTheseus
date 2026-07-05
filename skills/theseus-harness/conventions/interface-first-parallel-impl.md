---
id: interface-first-parallel-impl
category: impl
applies-to-phases: '[06,08]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Interface-First Parallel Implementation — 페이즈 08 모듈 분리 + 병렬 sub-agent

## 한 줄 요약

**페이즈 06 plan = 모듈별 인터페이스 (Port) 명시 의무, 페이즈 08 impl = 모듈마다 별도 sub-agent 병렬 호출.** 각 sub-agent 는 *자기 모듈의 인터페이스* + *자기가 의존하는 다른 모듈의 인터페이스* 만 알고, *구현 본문* 은 모름. DIP enforcement 의 운영 형태. v0.9.10 cold 검증 (synthetic_mine_throughput_v01_cold) 에서 single agent 가 mine_sim/ 12 파일 모두 작성 — 모듈 결합 발생 가능 + context 압박 — 이 결손이 본 컨벤션 도입 동기.

## 1. 결손 진단

기존 [`sub-agents.md`](sub-agents.md) + [`08-implement.md`](../phases/08-implement.md) :

- sub-agents.md = 재귀 분해 정책 (parallel/sequential/competition) 명시 — 단 *interface 우선* 룰 미명시.
- phase 08 = TDD 5 sub-phase (scope/test-RED/impl-GREEN/refactor/log) 진행 — 단 *모듈 단위 분리* 미강제.

→ 결과 : 단일 agent 가 mine_sim/ 의 모든 모듈 (topology / scenarios / resources / simulation / runner / aggregator / analysis 등 7+) 을 *연속 작성*. 두 가지 위험 :
a- *Cross-module 결합* — 한 모듈에서 다른 모듈의 *내부 구조* 직접 인용 → DIP 위반.
b- *Context 압박* — 단일 agent context 가 12 파일 + 1000+ LOC 누적 → 후반 모듈에서 *조잡한 통합*.

## 2. 운영 룰

### Step 1 — 페이즈 06 plan 의 인터페이스 의무

기존 HARD-RULE 9-a "인터페이스 정의 ≥ 3" 가 *카운트만* 강제 — 본 컨벤션이 강화 :

a- **모든 모듈** 이 자기 인터페이스 (Port / Protocol / abstract base class / typing.Protocol) 명시 의무. exception 0.
b- 인터페이스 = *공개 API 만* (private helper 제외). 메서드명 + 파라미터 + 반환 타입.
c- 다른 모듈에 의존 시 — 의존 대상의 *인터페이스* 만 인용 (구현 0). 예: `from .topology import Topology  # interface only` 가 plan 본문에 명시.

C-IF-PLAN (미등록, 신규) — 페이즈 06 plan/06-plan.md 의 모든 모듈 정의가 *인터페이스 절* 가지는지 검증 의무.

### Step 2 — 페이즈 08 impl 의 sub-agent 병렬 fan-out

페이즈 08-α (scope) 가 모듈 list 확정 후, 페이즈 08-γ (impl-GREEN) 진입 시 :

```
페이즈 06 의 N 모듈 → N sub-agent 병렬 호출

For each module M_i:
  spawn agent_M_i (subagent_type="general-purpose"):
    context (fresh):
      - M_i 의 인터페이스 (페이즈 06 §i)
      - M_i 가 의존하는 모듈들의 인터페이스 (구현 X)
      - M_i 의 페이즈 08-α scope (TODO 부분집합)
      - M_i 의 페이즈 08-β test-RED (TDD 페이즈)
    instructions:
      - 자기 모듈의 인터페이스를 만족하는 구현 작성
      - 의존하는 다른 모듈의 인터페이스만 사용 (구현 본문 0 인용)
      - 자기 페이즈 08-β 테스트 GREEN 만들기
      - 다른 모듈의 GREEN 여부 모름 (parallel 진행 — race-free)
    output:
      - <module_path>/M_i.py (구현)
      - tests/test_M_i.py (단위 테스트 GREEN)
      - 본 sub-agent 의 8-impl-log fragment

After all N sub-agents complete:
  Integration adapter test (페이즈 08-δ refactor 단계):
    - cross-module 통합 테스트 — 각 인터페이스가 *contract* 그대로 동작 검증
    - 위반 시 페이즈 08-γ 재진입 (해당 모듈만)
```

병렬 fan-out 의 *유리* :
- N agent 의 context 부담 = 각각 1 모듈만 → 조잡한 통합 0.
- agents 가 다른 agent 의 *구현* 모름 → 강제 인터페이스 의존 (DIP enforcement).
- N 병렬 → wall clock = max(M_1..M_N) ≤ N × max single agent.

### Step 3 — 통합 검증 (페이즈 08-δ refactor)

각 sub-agent 산출 완료 후 :

a- **Integration adapter test** — 각 모듈의 인터페이스 *대상별* 일관성 검증. mock 또는 fake 1 종 + real impl 1 종 모두 테스트 통과.
b- **Cross-module path test** — 페이즈 06 의 sequenceDiagram 따라 actor 전체 path 가 동작하는 통합 테스트 ≥ 1.
c- 위반 시 — 해당 모듈만 페이즈 08-γ 재호출 (다른 모듈 retain).

## 3. 그레이드별 활성

| Grade | 활성도 |
|---|---|
| G2 Simple | single agent 그대로 (모듈 ≤ 3) |
| G3 Standard | 인터페이스 명시 의무 + 모듈 ≥ 4 시 sub-agent fan-out 권장 |
| **G4 Complex** | **인터페이스 명시 의무 + sub-agent fan-out 의무 (모듈 ≥ 3 시)** |
| G5 Critical | G4 + cross-cutting 인터페이스 테스트도 별도 sub-agent (test-architect) 호출 |

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 인터페이스 / Port / Protocol = 도메인 무관 SOLID 패턴.
b- sub-agent fan-out = `Agent` 도구의 일반 메커니즘 (도메인 X).
c- 통합 테스트 = 일반 패턴 (Adapter / Contract test).

## 5. v0.9.10 의 enforcement 갭 (재확인)

v01_cold audit :
- impl/08-impl-log.md 가 *single agent 작성* 으로 추정 — sub-agent fan-out 흔적 0
- code/mine_sim/ 의 7+ 모듈 모두 single agent context 누적
- 인터페이스 / Protocol class 명시 *어느 정도* 있으나 (universe-2/06-plan.md 의 sequenceDiagram + actors) 분리 강제 안 됨

→ v0.9.11 의 본 컨벤션이 위 둘 모두 enforcement.

## 6. 안티 패턴

a- **인터페이스 정의 후 *구현 인용* 으로 sub-agent 가 다른 모듈의 본문 모방** — DIP 우회. cross-module import 검증 의무 (C-IF-DIP, 미등록 — only interface symbols).
b- **N sub-agent 병렬 호출 후 통합 적용 누락** — 본 §2-step 3 위반. integration adapter test ≥ 1 의무.
c- **각 sub-agent 가 자기 모듈 외 *마스터 코드* 도 작성** — sub-agent context 분리 위반. instruction 의무 명시.
d- **단일 monolithic agent 로 phase 08 진행 후 *형식적* 모듈 분할** — 본 컨벤션 핵심 위반. 페이즈 08-γ 진입 시 *fan-out 산출 evidence* 의무 (각 sub-agent 의 separate log).

## 7. 호환성

기존 [`sub-agents.md`](sub-agents.md) 의 재귀 분해 정책과 *합성* — 본 컨벤션은 *모듈 분리 axis* 를 명시. 기존 [`competition.md`](competition.md) 의 universe 경합과 *직교* — universe-N 내부에서 본 컨벤션이 *모듈 fan-out* 적용.

## 8. 자기 검증 (메타)

본 컨벤션 자체에 적용 가능 :
- 본 컨벤션 = single 모듈 (Markdown 문서 1 개).
- 모듈 ≥ 3 조건 미달 → fan-out 비활성. self_lint pass.
- 본 컨벤션이 다른 컨벤션 (sub-agents.md / competition.md / spec-catalog.md) 인용 시 *그 컨벤션의 인터페이스* (즉 그 컨벤션이 약속하는 룰) 만 인용 — 본문 인용 0. ✅
