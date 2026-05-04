# Premortem Friction — *한 번 더 고민* + 미래 회고로 더 나은 결론

## 한 줄 요약

**AI 의 *망설임 결손* 을 *멈춤* 으로 메우는 게 아니라 *한 번 더 고민 + 그대로 진행했을 때의 미래 회고* 로 메운다.** 콜드리뷰 페이즈 (02/03/07) 진입 시 격언 1 개를 prepend + premortem 프로토콜 1 단을 적용. 산출은 `derived_improvements ≥ 1` — 0 면 *theatrical premortem* 으로 자동 fail. 본 컨벤션의 목적 = *더 나은 결론 도출* 이지 contemplative 가 아니다.

## 1. 결손 진단 — AI 의 콜드리뷰가 콜드가 아닌 메커니즘

a- *손실 함수가 외재* — 결정의 비용을 *내재적으로* 못 느낌.
b- *자기 글에 대한 친숙성* — 페이즈 03/07 의 콜드 재이해가 자기 글의 의미를 *기억* 해 자동 동의.
c- *시간성 비매개* — "한 sprint 뒤 이게 깨졌다면" 의 미래 가설을 *현재* 와 동등 비중으로 다루지 못함.

→ 콜드리뷰가 *rubber-stamp* 됨. 본 컨벤션이 외부적으로 *premortem* (사전 부검) 을 강제 주입.

## 2. 격언 — 동·서 한 줄 (mechanism 직접 매핑)

> **知之為知之 不知為不知 是知也** (지지위지지 부지위부지 시지야) — *아는 것을 안다 하고 모르는 것을 모른다 하는 것이 앎이다* (공자 / 논어).
> ***De omnibus dubitandum est*** — *모든 것은 의심받아야 한다* (Descartes — 의심은 *결론* 이 아니라 *method*, 시험 후 더 단단한 결론에 도달하기 위한 도구).
>
> 두 격언은 본 컨벤션의 *3 step protocol* 의 원리 자체를 인코딩한다 — *모든 결론을 시험하고* (F2 → Step 1) *모르는 것을 명시한다* (F5 → Step 3) *그 사이에서 더 나은 결론을 derive 한다* (메커니즘 → Step 2). 본 페이즈는 위 태도로 진행한다.

본 격언은 *contemplative pause* 가 아니다. *forward simulation* — 그대로 진행했을 때의 결과를 미리 살아본 후 본 시점에 더 나은 선택을 내리는 *능동적* 도구. Descartes 의 doubt 는 *결론 보류* 가 아니라 *결론 시험* 임을 다시 강조 — 본 컨벤션의 `derived_improvements ≥ 1` hard gate 가 그 정합 강제.

## 3. Premortem 프로토콜 (3 step)

콜드리뷰 페이즈의 agent prompt 헤더에 다음을 prepend + 산출물에 `premortem` 절 박음.

**Step 1 — proceed-as-is 시뮬** *(F2 *de omnibus dubitandum est*)*
> "이 산출물의 *모든 결론* 을 시험한다 — *수정 0* 인 채 다음 페이즈로 넘어갔다 가정. 1~3 sprint 후 *반드시* 표면에 떠오르는 결손 ≥ 3 개를 적는다. Descartes 의 doubt = method, halt 아님."

**Step 2 — 회고적 미래 발견** *(메커니즘 — Step 1 ↔ Step 3 사이의 purposive 발견)*
> "각 결손에 대해, *그때의 나* 가 본 시점의 나에게 *지금* 무엇을 바꿔달라 할까? `derived_improvements` 로 ≥ 1 항목 추출."

**Step 3 — silence boundary** *(F5 *知之為知之 不知為不知 是知也*)*
> "premortem 후에도 *모르겠는 것* 은 `accepted_silence` 로 명시. 모르는 것을 *모른다* 인정하는 것이 앎. 의심 무한 회귀 차단."

## 4. 산출물 형식 (frontmatter + 본문)

```yaml
premortem:
  primer: "知之為知之 不知為不知 是知也 (Confucius) + de omnibus dubitandum est (Descartes)"
  artifact_under_review: "intent/01-intent.md"      # 어떤 산출물 콜드리뷰?
  proceed_as_is_findings:                            # Step 1: 결손 ≥ 3
    - "..."
    - "..."
    - "..."
  derived_improvements:                              # Step 2: 본 시점 개선 ≥ 1
    - description: "..."
      target_phase: "06-plan"                        # 어느 페이즈에 적용?
      effort_estimate: "low|medium|high"
  accepted_silence:                                  # Step 3: 모르겠는 것
    - "..."
```

`derived_improvements` 가 0개 = *theatrical premortem* → self_lint C-PM (premortem) 자동 fail.

## 5. 페이즈 매핑

본 컨벤션은 *concept understanding cold review* 페이즈 3 곳만 적용 — 비평 (05) / 회귀 (11) 는 다른 axis 라 별개.

| 페이즈 | 책임 | review 대상 | premortem 핵심 질문 |
|---|---|---|---|
| 02 의도 리뷰 (doc-reviewer) | 자기 의도 글 | `intent/01-intent.md` | "이 의도가 *문맥 누락* 으로 1 sprint 뒤 재해석되면 어떤 차이가 발생할까?" |
| 03 콜드 재이해 (independent-comprehender) | fresh-eye 재이해 | `intent/01-intent.md` | "이 문서를 *처음 보는 사람* 의 첫 5 질문이 자기가 답할 수 없으면 어떤 결손이 표면화될까?" |
| 07 플랜 재이해 (plan-reviewer) | 플랜 자기 검증 | `plan/06-plan.md` | "이 플랜이 *수정 0* 으로 페이즈 08 진입 시, sprint 01 의 회귀 발생 위치 ≥ 3 곳?" |

## 6. 안티 패턴

a- **Theatrical premortem** — `proceed_as_is_findings` 에 일반론만 ("코드 결손 가능", "테스트 부족 가능"). 결손 ≥ 3 *구체* — 페이즈/모듈/줄 단위.
b- **derived_improvements 0개** — 결손만 적고 개선 안 함. 본 컨벤션 hard fail.
c- **격언 인용 + 본문 동의** — 격언 박고 본문은 "이대로 좋다". 격언이 *수단* 이 아닌 *태도* 임을 위반.
d- **무한 분기 의심** — `accepted_silence` 로 멈춤 신호. silence 0 = 의심이 끝없이 분기 = 안티 패턴.
e- **모든 페이즈에 동일 primer 만** — primer 는 동일 (1 개) 이지만 *page-level 핵심 질문* 은 페이즈별 (위 §5 표).

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- trigger = *콜드리뷰 페이즈 진입* (02/03/07). 도메인 / prompt 무관.
b- 격언 = *동·서 1 개씩* — 추가 격언은 의미군 단위만. 케이스별 추가 X.
c- premortem 프로토콜 (3 step) = 도메인 독립. simulation-bench 든 결제 시스템이든 같은 프로토콜.

본 컨벤션은 v0.9.6 의 [`nfr-derivation.md`](nfr-derivation.md) 와 *직교* 채널 — nfr-derivation 은 *prompt 형용사 → 게이트*, premortem 은 *agent review 태도*.

## 8. 자기 검증 (메타 적용)

본 컨벤션 자체에 premortem 적용한 결과 :

```yaml
premortem:
  primer: "知之為知之 不知為不知 是知也 (Confucius) + de omnibus dubitandum est (Descartes)"
  artifact_under_review: "본 conventions/premortem-friction.md (자체)"
  proceed_as_is_findings:
    - "agent 가 'theatrical premortem' 회피 못 하고 결손 항목을 일반론으로 채울 가능성"
    - "premortem 자체가 페이즈 시간 +30% 비용으로 사용자가 끄고 싶어할 가능성"
    - "primer 격언 1 개로는 다른 contemplative 차원 (예: 윤리적 결정) 담아내기 부족할 가능성"
  derived_improvements:
    - description: "self_lint C-PM 룰에 'findings 의 구체성 — 페이즈/모듈/줄 단위 인용 ≥ 1' 추가"
      target_phase: "본 conventions/premortem-friction.md §6"
      effort_estimate: "low"
    - description: "성능 영향 측정 — premortem on/off 비교 wall clock 차이 측정 회차 1건"
      target_phase: "synthetic_mine_throughput_005 (검증)"
      effort_estimate: "medium"
    - description: "v0.9.8 후속에서 윤리 axis 차원의 primer 추가 (예: '내 결정이 사용자 외 누구에 영향?')"
      target_phase: "v0.9.8 backlog"
      effort_estimate: "medium"
  accepted_silence:
    - "premortem 의 *얼만큼* 이 적정한가 — 페이즈별 시간 cap 정량화 미정"
    - "format 의 yaml 강제가 사용자 경험에 부담일지 미측정"
```

본 절 자체가 자기 검증 — 본 컨벤션이 동작 가능 입증.
