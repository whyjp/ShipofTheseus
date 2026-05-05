---
id: parallel-cold-review
category: interview
applies-to-phases: '[03]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# Parallel Cold Review — N 개 직교 framing 의 fresh-eye 동시 진행

## 한 줄 요약

**페이즈 03 콜드 재이해 = *N 개 직교 framing* 의 동시 fresh-eye agent.** 단일 fresh-eye 의 *친숙성 자동 동의* 위험을 *복수 framing 의 결손 다양성* 으로 보완. tournament-merge 로 composite 결손 + 개선 생성. 본 컨벤션이 본 하네스의 *multiverse 강점* 을 페이즈 03 에 확장.

## 1. 결손 진단

페이즈 03 ([`../phases/03-independent-comprehension.md`](../phases/03-independent-comprehension.md)) 가 fresh-eye 1 회. v0.9.7 premortem 강화로 결손 발견 능력 ↑ 됐으나, *동일 agent 의 단일 framing* 한계는 잔존. 한 framing 이 본 도메인의 한 *축* 만 보고 다른 축의 결손은 못 찾음.

cold 회차 (`synthetic_mine_throughput_cold`) 에서 페이즈 03 의 콜드 재이해는 *engineering framing* 만 적용 — bench reviewer 의 *external evaluator framing* / domain operator 의 *operational framing* / pessimist 의 *failure-mode framing* 모두 미적용. 자체 추정 점수 92-95 의 일부가 본 framing 다양성 부재에서 발생.

## 2. 4 직교 framing (의미군 단위, 케이스 종속 0)

매 페이즈 03 에서 다음 4 framing agent 를 *동시 병렬* 호출. 각 agent 는 *같은 artifact* (intent/01-intent.md) 를 *다른 angle* 로 cold-read.

| Framing ID | 시각 | premortem 핵심 질문 |
|---|---|---|
| F-skeptic | 모든 결론을 의심하는 reviewer | "이 의도 문서의 *명시 안 된 가정* ≥ 5 개 — 한 개라도 빠지면 무엇이 깨지는가?" |
| F-domain-expert | 도메인 깊은 전문가 | "*도메인 best practice* 에 비추어 이 의도 문서가 *naive 한* 결정 ≥ 3 개?" |
| F-outsider | 도메인 무지 외부인 | "이 문서를 *처음 읽는 사람* 이 *의미를 못 잡는* 용어 / 결정 ≥ 5 개?" |
| F-pessimist | failure-mode 강조 | "이대로 1 sprint 진행 시 *가장 회한할* 결정 ≥ 3 개?" |

본 4 framing 은 *씨앗* — 5 번째 framing (예: F-time-pressed = 짧은 review window) 추가 가능, 케이스별 추가 X.

## 3. 운영 메커니즘

### Step 1 — fan-out

페이즈 03 진입 시 지휘자가 4 sub-agent 를 *동시* 호출 :

```
parallel agents:
  - F-skeptic   → intent/03-comprehension.skeptic.md
  - F-domain    → intent/03-comprehension.domain.md
  - F-outsider  → intent/03-comprehension.outsider.md
  - F-pessimist → intent/03-comprehension.pessimist.md
```

각 agent 는 [`premortem-friction.md`](premortem-friction.md) 의 v0.9.7 protocol 적용 — 격언 prepend (F2+F5) + premortem 절 의무. *framing 별 핵심 질문* 만 차별, 격언 / 절 형식 동일.

### Step 2 — tournament-merge

4 산출물의 `proceed_as_is_findings` + `derived_improvements` 합집합 → composite `intent/03-comprehension.md` :

```yaml
parallel_cold_review:
  framings_run: [F-skeptic, F-domain, F-outsider, F-pessimist]
  total_findings: N (sum of 4)
  unique_findings: M (after dedup by dimension)
  composite_derived_improvements: K
  framing_diversity_score: M/N   # 0=완전 중복, 1=완전 직교
```

`framing_diversity_score < 0.5` = framing 들이 *서로 너무 비슷한 결손만 발견* → 추가 framing 호출 또는 framing prompt 강화.

### Step 3 — composite 의 합집합 → 페이즈 04/06 입력

페이즈 04 NFR-V 질의 + 페이즈 06 plan 의 입력으로 `composite_derived_improvements` 모두 흐름. 단일 framing 대비 *발견 결손 ~3-4 배* 예상.

## 4. v0.9.7 premortem 와의 관계

v0.9.7 premortem-friction 은 *single-agent* 콜드리뷰의 망설임 강화 — 본 v0.9.8 parallel-cold-review 는 *multi-agent* 확장. 두 컨벤션 *합성* :

- 페이즈 02 / 07 = single-agent + premortem (v0.9.7) — 본 컨벤션 미적용 (이 페이즈는 *문서 author 의 자기 review*, framing 다양성 효익 약).
- 페이즈 03 = N-agent + premortem 각각 (v0.9.7 + v0.9.8) — *fresh-eye 의 framing 다양성* 이 핵심.

## 5. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 4 framing = 도메인 무관 의미군 — simulation-bench 든 결제 시스템이든 동일.
b- tournament merge = 룰 (합집합 + dedup), 도메인 X.
c- diversity score = 정량 메트릭 (M/N), 도메인 X.

## 6. 안티 패턴

a- **N=1 회피** — "1 framing 으로 충분" 으로 본 컨벤션 우회. 페이즈 03 의무 N=4 (G4+) 또는 N=3 (G3) 강제.
b- **framing 통합** — 4 sub-agent 가 *같은 컨텍스트 공유* → framing 다양성 0. 각 agent *fresh* (HARD-RULE 03 페이즈 b 정합).
c- **diversity score 미측정** — composite 산출물에 metric 누락 = self_lint C-PCR fail.

## 7. 그레이드 별 활성

| Grade | 활성 framing 수 | 사유 |
|---|:-:|---|
| G2 Simple | 1 (current) | over-engineering 회피 |
| G3 Standard | **3** (skeptic + domain + outsider) | 단일 사이드 작업도 framing 다양성 효익 |
| G4 Complex | **4** (전체) | 본 컨벤션 default |
| G5 Critical | **5+** (4 + F-time-pressed 등 추가) | 미션 크리티컬은 framing 더 |

## 8. 자기 검증

본 컨벤션 자체에 4 framing 적용 가능 — 본 conventions/parallel-cold-review.md 를 4 framing 으로 cold-review 시 :
- F-skeptic : "framing 4 가 진짜 직교한가? F-pessimist 와 F-skeptic 의 결손 차이가 무엇인가?"
- F-outsider : "tournament-merge 의 dedup 룰이 *의미적* dedup 인가 *문자적* dedup 인가?"
- ... 등

이 자기 검증의 결과가 v0.9.8 후속 PR 의 입력.
