# AIDE-tree Multi-Phase — 페이즈 06 외 다른 페이즈에도 universe 경합 확장

## 한 줄 요약

**기존에는 페이즈 06 (plan-tree) 만 multiverse 경합** — 현재 다른 페이즈 (02 doc-review / 05 critique / 08 impl strategy / 11 regression bisect / 13 interactive-viewer) 에도 *AIDE-tree N universe 경합* 활성. 본 하네스의 *유일한 차별 강점* (multiverse competition) 을 plan 외 axis 로 확장.

## 1. 결손 진단

기존 [`plan-tree.md`](plan-tree.md) + [`competition.md`](competition.md) :

- 페이즈 06 만 N universe planner sub-agent 호출.
- 페이즈 02 / 05 / 08 / 11 / 13 = single agent. 단일 산출물 = 단일 *세계관*.

→ multiverse 강점이 *plan* axis 만에 적용. *review* / *critique* / *implementation* / *regression* / *visualization* axis 는 single-world 한계.

## 2. 페이즈별 활성 룰

각 페이즈가 *어떤 axis 의 multiverse* 인지 명시 :

| 페이즈 | universe 차별 axis | N (G3 / G4 / G5) | 합집합 type |
|---|---|:-:|---|
| 02 doc-review | reviewer 시각 (skeptic / supportive / domain-naive) | 2 / 3 / 4 | tournament merge |
| 05 critique | critic 차원 (structural / behavioral / cost-benefit / risk) | 2 / 3 / 4 | tournament merge + ensemble |
| 06 plan-tree | architecture seed | 2 / 3-4 / 5-6 | tournament merge (기존) |
| 08 impl strategy | implementation 전략 (idiomatic / optimized / minimal) | 2 / 3 / 4 | tournament + integrate |
| 11 regression bisect | hypothesis space (commit / data / config / env) | 2 / 3 / 4 | parallel hypothesis tournament |
| 13 interactive-viewer | UX framing (operator / engineer / executive) | — / 2 / 3 | gallery (no merge — show all) |

각 페이즈의 universe 별 산출물 = `<phase_dir>/candidates/universe-N/<phase_artifact>.md` (page 06 와 동일 패턴).

## 3. tournament resolve

각 페이즈 별 차원 :

- 02 doc-review = 결손 발견 수 + 결손 우선순위 매칭 + remediation 제안 quality
- 05 critique = 대안 다양성 + 비용-효익 정량화 + 우선순위 합리성
- 08 impl strategy = (코드 품질 + 테스트 커버리지 + LOC) × NFR 충족
- 11 regression bisect = hypothesis 의 evidence weight + 검증 가능성
- 13 viewer = decision-support clarity per stakeholder

각 페이즈 별 차원 *재정의* — generic 차원이 아닌 phase-specific. self_lint C-AT-MP 가 차원 정의 frontmatter 박힘 검증.

## 4. 페이즈 04 자율 설정

페이즈 04 NFR-V 단계에서 *각 페이즈의 multiverse 활성 여부* 사용자 위임 (Q-D10~D14, v0.9.10 신규) :

```
Q-D10 — 페이즈 02 multi-reviewer 활성?
1. 비활성 (single reviewer, default G3)
2. 폭 2 (G4+)
3. 폭 3+
4. N/A (페이즈 02 skip)

Q-D11 — 페이즈 05 multi-critic ?
... 동일 패턴 ...

Q-D12 — 페이즈 08 multi-strategy?
Q-D13 — 페이즈 11 multi-hypothesis?
Q-D14 — 페이즈 13 multi-framing viewer?
```

cold context 의 자동 매핑 = G4 default (페이즈 02/05/08 = 폭 2-3, 페이즈 11/13 = 폭 2). 사용자 명시 시 override.

## 5. blind rerun 활성

각 multiverse 페이즈가 [`tournament-blind-rerun.md`](tournament-blind-rerun.md) 의 임계-미달-재경합 룰 적용 가능. 페이즈 04 Q-D2 답 (auto-fix-trigger) 정합 — fail 시 자동 blind rerun 진입.

## 6. v0.9.10 의 통합 효과 (3 컨벤션 시너지)

| 컨벤션 | 작용 axis |
|---|---|
| aide-tree-symmetry.md | 각 universe 의 sequenceDiagram 강제 (depth) |
| **aide-tree-multi-phase.md** | **5+ 페이즈로 multiverse 확장 (breadth)** |
| tournament-blind-rerun.md | 임계 미달 시 blind 재경합 (validity) |

세 컨벤션 시너지 = "deep × broad × validated multiverse" — 본 하네스의 *유일한 차별 강점* 의 풀 발현.

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 페이즈별 차별 axis = 의미군 (reviewer 시각 / critic 차원 등), 도메인 X.
b- N (G3/G4/G5) = 그레이드별 generic 룰.
c- tournament resolve = 페이즈별 차원 정의만 차이, 알고리즘은 competition.md 동일.

## 8. 안티 패턴

a- *모든 페이즈* 에 multiverse 활성 — over-engineering. 룰 §2 표의 axis 가 의미 있을 때만.
b- universe N 마다 *동일한 산출물 변형* — 차별 axis 위반. self_lint C-AT-MP-AXIS 검증.
c- multi-phase 활성 시 tournament merge 없이 *형식적 N 산출물* 만 — single-world 와 동급. merge 의무.

## 9. 호환성

기존 [`competition.md`](competition.md) / [`plan-tree.md`](plan-tree.md) 의 페이즈 06 룰은 *불변* — 본 컨벤션은 *추가 페이즈* 만 정의. backward compatible.

## 10. 자기 검증

본 conventions/aide-tree-multi-phase.md 자체에 *meta-application* 가능 — 본 문서 작성 시점에 페이즈 02 (doc-review) 가 multiverse 적용되었으면 reviewer 의 다른 시각 ≥ 3 의 결손 발견 / 개선 도출. 본 회차 에서는 미적용 (single-shot 작성).
