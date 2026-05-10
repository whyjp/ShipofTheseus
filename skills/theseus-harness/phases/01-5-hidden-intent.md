# Phase 1.5 — Hidden Intent (확장 사고 단계)

> sprint-50 v0.9.50 신설. 페이즈 04 (Q&A / autonomy / stack / verification / runtime-prereq) 직후, 페이즈 05 (Critique + Decisions) 직전 의무 단계.
>
> 본 페이즈는 *프롬프트 충실 이행* 만으로는 채울 수 없는 차원 (Conceptual / Experimental / Results 일부) 을 *명시적으로* 별도 단계로 박는다.

## 한 줄 요약

**프롬프트가 *묻지 않은* 것을 묻고, 답하고, 후속 페이즈로 trace 한다.** 본 페이즈는 "프롬프트 너머의 합리적 평가자가 기대할 항목" 을 발굴하는 *확장 사고 (Extension Thinking)* 의 단일 컨테이너.

## 격언

> *"Don't gather requirements—dig for them."* — Hunt & Thomas, *The Pragmatic Programmer*, Tip 53.
>
> 동: *不患寡而患不均* — 적음을 걱정하지 말고 고르지 않음을 걱정하라. 의도가 *적은* 게 문제가 아니라 *치우친* 게 문제.

## 입력

- 페이즈 04 산출물 전체 (questions/answers/autonomy/stack/verification/runtime-prereq)
- 페이즈 01-{1..4}-intent.md (mindmap fan-out 포함)
- 사용자 원문 요청 (대화 첫 메시지)
- *없는 것* — 페이즈 05 critique 는 본 페이즈 *이후* 산출. 본 페이즈는 critique *이전* 의 확장.

## 서브에이전트

`Agent(subagent_type="general-purpose")` — `agents/extension-thinker.md` 프롬프트 사용 (PR-F 에서 신설).

본 에이전트의 핵심 지시 (요지):
- 페이즈 04 답안과 *직교하는* 차원에서 *합리적 평가자가 기대할* 항목 ≥5 추출.
- 항목별 (a) 한 줄 진술 (b) 출처 카테고리 (c) prompt 직접 인용 *아님* 증명 (d) impact 추정.
- 자기 *prompt paraphrase* 가 아닌지 self-check (`hidden_intent_originality.py` 통과 의무).

## 산출물 (3 페어)

### 1. `intent/01-hidden-intent.md` — *발굴*

≥5 항목. 각 항목 frontmatter 5 필드:

```markdown
## HI-01 — <한 줄 진술>

- **카테고리**: validation | sensitivity | non-functional | domain-modeling | risk | observability | scalability | accessibility | maintainability | reproducibility (10 catalog 중 1)
- **prompt 직접 인용 여부**: NO (token-overlap < τ + 카테고리가 prompt 의 5 자연 카테고리 외)
- **합리적 평가자 expectation 근거**: <왜 평가자가 이걸 기대할 가능성이 높은지 1 문단>
- **impact 추정**: high | medium | low — 본 회차 산출물에 미칠 영향
- **본 회차 reach 의향**: must | should | could (다음 산출물 §2 와 일치)
```

10 카테고리 catalog 의 의미:

| 카테고리 | 의미 |
|---|---|
| validation | 입력 검증 / 가정 검증 / sanity 체크 — prompt 가 *결과* 만 묻고 *검증 절차* 안 묻는 경우 흔히 발생 |
| sensitivity | parameter sensitivity / DoE / sweep — prompt 가 *fixed* 시나리오만 주고 *sweep* 안 묻는 경우 |
| non-functional | 성능 / 메모리 / 가용성 / observability — prompt 가 *기능* 만 묻는 경우 |
| domain-modeling | 도메인 이론 framing / 표준 모델 (e.g. queueing theory / control theory) — prompt 가 *도메인 표준* 안 묻는 경우 |
| risk | 실패 모드 / 데이터 결손 / numerical instability — prompt 가 *happy path* 만 묻는 경우 |
| observability | 로깅 / tracing / metric — prompt 가 *결과 산출* 만 묻고 *과정 관찰* 안 묻는 경우 |
| scalability | 데이터/시간 규모 변화 거동 — prompt 가 *고정 규모* 만 주는 경우 |
| accessibility | UI / 문서 / API 의 외부 사용자 측면 — prompt 가 *내부 메트릭* 만 묻는 경우 |
| maintainability | 모듈 분해 / 확장 지점 / 변경 비용 — prompt 가 *기능* 만 묻고 *유지보수* 안 묻는 경우 |
| reproducibility | seed / 환경 / 외부 의존 고정 — prompt 가 *결과* 만 묻고 *재현* 안 묻는 경우 |

≥5 항목 + ≥3 카테고리 distinct 의무.

### 2. `intent/01-extension-scope.md` — *분류*

§1 의 ≥5 항목을 (must / should / could) 분류 + 본 회차 reach 결정.

```markdown
| ID | 진술 (단축) | 카테고리 | reach | trace 대상 페이즈 |
|---|---|---|---|---|
| HI-01 | ... | validation | should | plan / impl / sprint |
| HI-02 | ... | sensitivity | could | plan only |
| HI-03 | ... | reproducibility | must | impl |
| HI-04 | ... | observability | should | impl / handoff |
| HI-05 | ... | maintainability | could | (보류 — 다음 회차) |
```

**의무**:
- *should* 채택 ≥1 (즉 *should* 등급 항목이 본 회차 plan/impl/sprint 산출물에 trace).
- *must* 항목은 자동 채택 (페이즈 04 답안과 충돌 없는지 §3 에서 확인).
- *could* 는 본 회차 보류 가능 — 다음 회차 인계.

### 3. `intent/01-extension-trace.md` — *추적 약속*

§2 의 채택 항목 (must + should) 각각이 *어느 후속 페이즈 산출물에 trace 될 것인가* 의 explicit pointer.

```markdown
## HI-01 (must) — <한 줄>

- **trace 대상**:
  - `plan/06-plan.md` §X — <plan 본문에서 어떤 항목으로 나타날 것인가>
  - `impl/08-impl-log.md` §Y — <impl 산출물에서 어떤 모듈/함수로 나타날 것인가>
- **검증 방법**: `extension_to_artifact_trace.py --hi-id HI-01` 으로 페이즈 14 직전 grep 검증

## HI-04 (should) — <한 줄>

- **trace 대상**:
  - `impl/08-impl-log.md` §Z — observability hook 으로 추가
  - `handoff/14-handoff.md` Knowledge Portfolio §3 — 본 회차 학습 통찰
- **검증 방법**: 동일
```

본 산출물은 *약속* 단계. 실제 trace 검증은 페이즈 09 quality gate + 페이즈 14 handoff 시점.

## CLI 의무 — *§자동 호출 literal Bash* (sprint-43 패러다임)

페이즈 1.5 exit 직전 orchestrator 가 의무 호출:

```bash
python skills/theseus-harness/scoring/intent_extension_emit.py \
    --project-root .ShipofTheseus/<proj>/ \
    --min-items 5 \
    --min-categories 3 \
    --require-should-adoption

python skills/theseus-harness/scoring/hidden_intent_originality.py \
    --project-root .ShipofTheseus/<proj>/ \
    --max-token-overlap 0.4 \
    --escape-categories-min 1
```

`extension_to_artifact_trace.py` 는 페이즈 09 quality gate 시점 호출 (HARD-RULE 9.jjj).

## 성공 기준

a- 3 산출물 모두 emit (`intent_extension_emit.py` PASS)
b- 항목 ≥5 + 카테고리 distinct ≥3 + should 채택 ≥1
c- 모든 항목이 *prompt paraphrase* 가 아님 (`hidden_intent_originality.py` PASS) — token-overlap ≤ 0.4 AND 카테고리가 prompt 의 5 자연 카테고리 외 ≥1
d- 채택 항목이 §3 trace 약속 명시 (페이즈 09 시점 검증)

## 흔한 실패

a- *프롬프트의 5 자연 카테고리 (data / topology / scenario / metrics / constraints) 안에서만* 항목 추출 — `hidden_intent_originality.py` 의 §2 카테고리 escape 검사 fail. 재실행 (다른 카테고리 의무).

b- 항목이 ≥5 지만 모두 같은 카테고리 (e.g. validation 5 개) — distinct ≥3 fail. 재실행.

c- *should* 채택 0 (전부 *could* 보류) — `intent_extension_emit.py` --require-should-adoption fail. 재실행 (적어도 1 should reach).

d- §3 trace 약속이 vague ("plan 어딘가") — explicit §X / §Y / §Z pointer 의무. 재실행.

e- 항목이 페이즈 04 답안과 충돌 (e.g. autonomy 답에서 "외부 데이터 X" 인데 HI 가 "외부 데이터 fetch") — 충돌 시 페이즈 04 우선. HI 항목 수정 또는 *could* 강등.

## 다음 페이즈 인계

페이즈 05 (Critique + Decisions) 입력 = 페이즈 04 산출물 + 본 페이즈 1.5 의 3 산출물. critique 는 *본 회차 채택* 항목까지 포함하여 비판.

페이즈 06 (Plan tournament) 입력 = 페이즈 05 decisions + 본 페이즈 1.5 채택 항목. universe N 의 plan 본문이 채택 항목을 *직접* 다룸.

페이즈 14 (Handoff) Knowledge Portfolio = §1 항목 중 본 회차 *수행* 한 것 vs *보류* 한 것 explicit list.
