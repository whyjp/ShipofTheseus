---
id: canonical-not-stub
category: meta
applies-to-phases: '[06,08,14]'
applies-to-grades: '[all]'
trigger-when: 'canonical 산출 시'
indexed-in: conventions/INDEX.md
---

# Canonical not stub (`canonical-not-stub`) — canonical 산출물 ≥ winner universe 본문 80% 또는 shared schema (sprint-19, cg, HARD-RULE 9.ii)

## 한 줄 요약

**`plan/06-plan.md` (canonical) / `impl/08-impl-log.md` (canonical) 등 phase canonical 산출물은 단순 위임 stub 금지 — winner universe-N 본문의 80% 이상 *또는* shared schema + 통합 결정 본문 의무.** cold session 003 의 canonical 06-plan.md = 818 byte stub ("see candidates/universe-1/06-plan.md") 회귀 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| canonical 이 위임 stub | cold 003 canonical 06-plan.md 818 byte vs winner universe-1/06-plan.md 6126 byte (canonical = 13% 만) |
| 정보 고립 | impl/08-impl-log.md 가 "T-013, T-016" TODO 인용 → 실 본문은 universe-1 에만 → 다른 phase doc 가 어느 source 봐야 할지 모호 |
| 사용자 메타 원칙 위반 | "독립 문서에만 독립 정보가 존재해서 다른 문서에서 스킬의 공통 혹은 공유 해야할 정보를 가져가지 못함" |

## 트리거

Phase 06 / Phase 08 / Phase 14 의 canonical 산출물:
- `plan/06-plan.md`
- `impl/08-impl-log.md` (impl-multiverse-strict ch 정합)
- `handoff/14-handoff.md`

## 알고리즘

1. canonical 파일 byte size 측정.
2. winner universe-N 본문 byte size 측정 (`plan/candidates/universe-<winner_id>/06-plan.md`).
3. 다음 중 ≥ 1 만족 의무:
   - **(A) Inline mode**: `canonical_size >= 0.80 × winner_size` (winner 본문 80% 이상 본문 박힘 + universe-anonymisation).
   - **(B) Shared schema mode**: canonical 본문에 § Shared Schema + § Integration Decisions + § Cross-phase Reference 3 섹션 의무 (각 ≥ 5 줄). winner universe-N 와 phase 08 가 공유하는 schema/contract 가 canonical 에 1 회 명시 + 양쪽 phase 가 인용.
4. 두 mode 모두 미달 → fail. canonical 본문 inline 또는 shared schema mode 로 보강 강제.

## 의무 frontmatter (canonical 산출물)

```yaml
canonical_mode: inline | shared-schema
canonical_size_bytes: <int>
winner_size_bytes: <int>
canonical_to_winner_ratio: <float>     # inline mode 시 >= 0.80
shared_schema_sections: 3              # shared-schema mode 시 == 3
shared_schema_cross_refs: [...]        # phase 08 / phase 14 cross-ref 목록
asof_fingerprint: "<source_winner_fingerprint>"   # cross-phase-shared-context (cj) 정합 — drift 차단
```

**asof_fingerprint** 의무 — canonical 의 본문 / 인용 source (winner universe-N) 의 그 시점 fingerprint 와 일치. drift 시 phase 08 진입 거부.

## self_lint C-CNS

컨벤션 파일 존재 + 페이즈 06/08/14 본문 "canonical-not-stub" + "80%" 또는 "shared schema" + 두 mode 정의 명시.

## 안티 패턴

a- canonical 본문 = "See `candidates/universe-N/06-plan.md`" 한 줄 위임 — sprint-19 차단.
b- canonical 본문 = winner 본문 그대로 복붙 (universe identifier 도 그대로) — *anonymised inline mode* 의무. universe-1 식별자 → canonical 본문에 노출 금지.
c- shared-schema mode 인척 § 헤더만 추가 + 본문 빈 — 각 § ≥ 5 줄 강제.
d- canonical 박지만 phase 08 가 universe-1 직접 인용 (canonical 우회) — phase 08 산출물이 canonical 만 인용 의무, universe-N 직접 인용 시 fail.

## cold session 003 검증

`plan/06-plan.md` 818 byte:
```
# Phase 06 — Final Plan (Universe-1 + cross-universe lessons)
See `candidates/universe-1/06-plan.md` for the full plan with mermaid diagrams, interfaces, and TODO DAG.
...
```
→ canonical_to_winner_ratio = 818/6126 = 0.13 (< 0.80). shared_schema_sections = 0.
→ sprint-19 게이트 적용 시 fail → canonical 본문 inline (anonymised universe-1 본문 ≥ 4900 byte) 또는 shared-schema mode (3 섹션 ≥ 15 줄) 강제.

## 호환성

- [`fragmentation.md`](fragmentation.md) (p) — 단일 헤비 스킬 금지의 *역방향* 안전. 본 룰은 정보 *고립* 금지 (단일 위치에 너무 많이 vs 분산된 위치에 너무 적게 — 양 끝 모두 차단).
- [`aide-tree.md`](aide-tree.md) §3 (sprint-37 PR-AB 통합) — universe candidate sequenceDiagram 강제 + 본 룰의 canonical inline mode 결합 시 winner sequence 가 canonical 에도 박힘.
- [`indexing.md`](indexing.md) (s) — canonical 산출물이 phase 간 cross-ref index 역할.
