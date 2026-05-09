---
id: cross-phase-shared-context
category: meta
applies-to-phases: '[06,08,09,14]'
applies-to-grades: '[all]'
trigger-when: 'shared 정보 인용'
indexed-in: conventions/INDEX.md
---

# Cross-phase shared context (`cross-phase-shared-context`) — 공통 정보 단일 위치 + 양쪽 phase 인용 의무 (sprint-19, cj, HARD-RULE 9.ll)

## 한 줄 요약

**Phase 간 공유 정보 (schema / contract / shared decisions / cross-cutting NFR) 는 단일 위치에 1 회 박힘 + 양쪽 phase 산출물이 그 위치 인용 의무.** 사용자 메타 원칙 직접 정합: "독립 문서에만 독립 정보가 존재해서 다른 문서에서 스킬의 공통 혹은 공유해야 할 정보를 가져가지 못함" 문제 차단. 동시에 [`fragmentation.md`](fragmentation.md) (p) 의 "단일 헤비 스킬 금지" 원칙과 양립 — *shared* 만 단일 위치, *phase-specific* 은 분리 유지.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| canonical 위임 stub | cold 003 의 06-plan.md = "see universe-1/06-plan.md" → phase 08 가 어느 source 봐야 할지 모호 |
| schema/contract 정보 분산 | TruckProcess interface 가 phase 06 universe-1 본문에만 → phase 08 impl/08-impl-log.md 가 그 interface 재정의 → drift 가능 |
| 사용자 메타 원칙 위반 | 분산 + isolation = 두 끝의 실패 모드 동시 발생 |

## 트리거

Phase 06 plan 진입 시 + Phase 08 impl 진입 시 + Phase 09 quality gate. 모든 grade.

## shared 정보 카탈로그 (단일 위치 의무)

| 정보 | 단일 위치 | 인용해야 할 phase |
|---|---|---|
| **Domain entity catalog** (D1, [`domain-pack.md`](domain-pack.md) §2, sprint-37 PR-AG 통합) | `intent/01-intent.md` §m 또는 `intent/01-shared-context.md` (sprint-19 신규 위치 후보) | 06 plan, 08 impl, 14 handoff |
| **Module interface signatures** | `plan/06-plan.md` § Module interfaces (canonical, canonical-not-stub cg 의무) | 08 impl |
| **Data structure invariants table** ([`data-structure-invariants.md`](data-structure-invariants.md) bt) | `plan/06-plan.md` § Data Structure Invariants & Topology | 08 impl, 09 quality gate |
| **TODO DAG** | `plan/06-plan.md` § TODO DAG (T-001..T-NNN) | 08 impl (impl-log T-NN 매핑), 14 handoff |
| **Measurement contract** ([`measurement-contract.md`](measurement-contract.md) bi) | `plan/06-plan.md` § Measurement contract | 08 impl, 11 regression-bisect |
| **Decision answers (Q1~Q6)** | `intent/04-answers.md` 또는 `intent/04-refreshed.md` (sprint-19 ci 정합) | 06 plan, 14 handoff |
| **Performance / NFR thresholds** ([`spec-catalog.md`](spec-catalog.md) k + [`nfr-derivation.md`](nfr-derivation.md) w) | `intent/01-intent.md` §d / §i | 09 quality gate |

## 의무 — 인용 패턴

각 phase 산출물이 shared 정보를 사용 시 **인용 패턴 강제**:

```markdown
[참조: `plan/06-plan.md` § Module interfaces — TruckProcess.dispatch() 시그니처 의무 준수]
```

또는 frontmatter:

```yaml
shared_context_refs:
  - path: "plan/06-plan.md"
    section: "Module interfaces"
    asof_fingerprint: "smg4-06-final-2026-05-06"
```

`asof_fingerprint` 가 source 의 *그 시점* fingerprint 와 일치 의무 — drift 방지.

## 자동 reject 패턴

1. phase 08 impl/08-impl-log.md 본문에 *모듈 interface 재정의* (plan 인용 없이) → drift 의심 → fail.
2. phase 06 canonical 06-plan.md 가 stub 인 채 phase 08 가 universe-N 직접 인용 → canonical-not-stub (cg) 와 결합 fail.
3. shared 정보가 *두 곳* 에 박힘 (예: D1 entity catalog 가 intent/01 + plan/06 양쪽에 본문 박힘) → DRY 위반 → 한 쪽이 인용 으로 전환 강제.
4. `asof_fingerprint` 부재 또는 source 파일의 현재 fingerprint 와 mismatch → drift detect → fail.

## self_lint C-CPSC

컨벤션 파일 존재 + 페이즈 06/08/09 본문 "cross-phase-shared-context" + shared 카탈로그 ≥ 5 항목 + asof_fingerprint 의무 명시.

## 안티 패턴

a- canonical 위임 stub + phase 08 universe-N 직접 인용 — sprint-19 cg + cj 결합 차단.
b- shared 정보 두 곳 본문 (DRY 위반) — 한 곳을 인용 으로 전환 강제.
c- 인용 frontmatter `asof_fingerprint` 부재 — drift 추적 불가.
d- 단일 헤비 위치 (모든 shared 정보를 intent/01 에만 박음) — `fragmentation.md` (p) 위반. *카테고리별 분산 + 인용* 패턴 의무.

## cold session 003 검증

- canonical 06-plan.md = stub (cg 와 결합 fail)
- impl/08-impl-log.md 가 universe-1/06-plan.md 의 TODO ID (T-013, T-016) 를 *재정의 없이 인용* — 인용 패턴은 일부 정합하지만 `asof_fingerprint` 부재
- D1 entity catalog 가 conceptual_model.md (외부 산출물) 에만 박힘 → intent/01-intent.md §m 본문 부재
→ sprint-19 게이트 적용 시 shared 카탈로그 5 항목 위치 의무 + asof_fingerprint 의무 → drift 차단 강제.

## 호환성

- [`fragmentation.md`](fragmentation.md) (p) — 본 룰의 *반대 끝*. 둘 다 만족해야 (분산 + 인용).
- [`indexing.md`](indexing.md) (s) — 산출물 = DB / 비직렬성 트리 인덱싱 정합.
- [`canonical-not-stub.md`](canonical-not-stub.md) (cg) — canonical 위치가 본 룰의 단일 위치 역할.
- [`contracts.md`](contracts.md) (f) — fingerprint chain + asof_fingerprint 결합.
