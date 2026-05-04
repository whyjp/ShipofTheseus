# Domain Research Stacking — 마인드맵 도메인 noun → 도메인 어댑터 자동 stack

## 한 줄 요약

**페이즈 01 마인드맵의 *기능 axis 도메인 noun* (예: "광산", "트럭", "크러셔") 자동 추출 → 매칭되는 도메인 어댑터 (`conventions/domain-adapters/<domain>.md`) 가 *intent / NFR / architecture* layer 에 자동 stack.** 본 하네스의 *제너럴 골격* 위에 *도메인 전문성* layer 추가. 외부 URL visit 0 (어댑터는 plugin 에 bundled).

## 1. 결손 진단

v0.9.6-12 의 모든 컨벤션 = *제너럴 구조 enforcement*. 도메인 *지식* 0 — mining 도메인 prompt 든 결제 시스템 prompt 든 같은 룰. 결과 :
- mining bench 의 *도메인-specific behavior* (MTBF / grade variation / capex sequencing 패턴) 미반영
- general harness가 mining-specific *insight* 미보유 → bench reviewer 의 도메인 점수 ceiling 97 plateau

## 2. 운영 룰

### Step 1 — 마인드맵 도메인 noun 추출

페이즈 01 §9 마인드맵의 *기능 axis* 의 sub-node 들이 도메인 noun 후보 :

```
기능
├── domain
│   ├── truck            ← noun: "truck" + "haulage"
│   ├── loader           ← noun: "loader"
│   ├── crusher          ← noun: "crusher" + "ore"
│   └── topology         ← noun: "graph" + "discrete-event"
```

도메인 noun 추출 룰 = v0.9.13 [`deep-semantic-intent.md`](deep-semantic-intent.md) 의 noun 추출과 *동일 source*.

### Step 2 — 도메인 어댑터 매칭

`skills/theseus-harness/conventions/domain-adapters/` 디렉터리의 어댑터 파일들과 매칭 :

```
domain-adapters/
├── des-modeling.md          (discrete-event simulation 일반)
├── mining-haulage.md        (광산 haulage 시뮬)
├── payment-systems.md       (결제 / idempotency / latency)
├── search-ranking.md        (검색 / recall / precision)
├── logistics.md             (logistics / routing / dispatch)
└── ...
```

각 어댑터 파일의 frontmatter `triggers: [...]` (도메인 noun 패턴 list) 와 매칭. 1+ 어댑터 매칭 시 stack.

### Step 3 — Stack into intent

매칭된 어댑터의 본문이 페이즈 01 의 다음 절에 자동 stack :

a- **NFR 후보 추가** — 어댑터의 §i-additions = §i NFR 추가 (예: mining-haulage 의 "MTBF / availability < 1.0 / grade variation").
b- **Architecture 패턴** — 어댑터의 §architecture-patterns = 페이즈 06 plan 의 *도메인 검증* 입력 (예: "haulage = bidirectional cap-1 single-pool 정합" / "shift handover 모델 의무").
c- **Known limitations** — 어댑터의 §limitations = 페이즈 01 §3 비목표 / 페이즈 09 limitation 절 입력.
d- **Decision question 패턴** — 어댑터의 §decision-templates = 페이즈 04 NFR-V 질의 + 페이즈 14 handoff 의 권고 형식.

### Step 4 — Stack frontmatter

페이즈 01 산출물의 frontmatter 에 stacked adapter 명시 :

```yaml
domain_adapters_stacked:
  - name: "mining-haulage"
    matched_nouns: ["truck", "loader", "crusher", "haulage"]
    contributions:
      - nfr_additions: ["MTBF", "availability_lt_1.0", "grade_variation"]
      - architecture_patterns: ["bidirectional_cap1_single_pool", "shift_handover"]
      - limitations: ["no_grade_modeling", "no_breakdown"]
  - name: "des-modeling"
    matched_nouns: ["simpy", "process", "resource", "event"]
    contributions:
      - nfr_additions: ["determinism", "byte_repro"]
      - architecture_patterns: ["single_mutation_point", "fifo_queue"]
```

self_lint C-DRS (domain research stacking) = stack 0 인 경우 "general-only" 명시 검증 + 1+ 매칭 시 contributions 본문 적용 검증.

## 3. 어댑터 기여 한계 (안티 패턴 가드)

a- **어댑터가 prompt 명시 외 기능 추가** — 사용자 의도 위반. 어댑터는 *prompt 명시한 도메인 noun* 의 *known constraints / patterns* 만 stack. 신규 기능 도입 0.
b- **여러 어댑터 매칭 시 충돌** — 도메인 어댑터 간 NFR 충돌 (예: "real-time" payment vs "throughput-only" logistics) 시 prompt 가 어느 쪽인지 명시 안 했으면 *둘 다 후보로 stack* + 페이즈 04 추가 질의로 사용자 ack.
c- **어댑터 contributions 가 prompt 와 무관** — drift. self_lint C-DRS-EVIDENCE 가 각 contribution 이 prompt 의 어떤 noun 에서 trigger 되었는지 evidence 의무.

## 4. 어댑터 작성 룰

각 `conventions/domain-adapters/<domain>.md` 의무 frontmatter :

```yaml
---
name: <domain>
triggers:                         # 마인드맵 noun 매칭 패턴
  - regex: "truck|haul|haulage"
    weight: 0.4
  - regex: "loader|crush|crusher"
    weight: 0.3
  - regex: "ore|mining|pit"
    weight: 0.3
match_threshold: 0.5              # weighted match score 임계 (어댑터 활성화)
authority: "industry-standard | academic | empirical | best-practice"
references:                       # 어댑터 본문의 출처 (논문 / 표준 / 산업 best-practice)
  - "..."
---
```

본문 절 :

```
## §i-additions
## §architecture-patterns
## §limitations
## §decision-templates
## §verification-hooks
```

각 절은 *empirical evidence 인용 의무* (논문 / 산업 표준 / 공식 best-practice 출처 명시).

## 5. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 어댑터 매칭 메커니즘 = 도메인 무관 룰 (regex + weight + threshold).
b- 어댑터 자체는 *각 도메인 별 1 파일* — 본 컨벤션 = 그 *룰* + *디렉터리 layout*.
c- contributions 카테고리 (NFR / architecture / limitations / decision-templates) = 일반 schema.

## 6. v0.9.13 reference 어댑터 (2 개 시드)

플러그인 v0.9.13 에 다음 2 어댑터 시드 포함 :
- `domain-adapters/des-modeling.md` — DES 일반 (SimPy / event-driven / determinism / byte-repro)
- `domain-adapters/mining-haulage.md` — 광산 haulage (truck / loader / crusher / ramp / shift)

후속 PR 에서 추가 어댑터 (payment / search / logistics 등) 작성 가능. 어댑터 추가 = 컨벤션 추가 0 (본 컨벤션 룰 그대로).

## 7. 효과 추정 (mining bench 적용)

reference 어댑터 활성 시 :
- §i NFR 추가: MTBF / availability / grade-variation → +1pt (Conceptual)
- Architecture pattern 검증: bidirectional cap-1 single-pool 정합 자동 → +1pt (Sim correctness)
- Decision-template: 6 결정 질문의 *operational answer 형식* → +1pt (Results)

→ self-estimate 97 → 99-100 보강 (v0.9.13 [`deep-semantic-intent.md`](deep-semantic-intent.md) 와 합성).

## 8. 자기 검증

본 컨벤션 자체에 적용 시 — *컨벤션 도메인 noun* (rule / convention / harness / framework) → 매칭 어댑터 = *meta-convention adapter* (만일 작성된다면). 본 회차 (v0.9.13) = single-shot, 메타 어댑터 미작성.
