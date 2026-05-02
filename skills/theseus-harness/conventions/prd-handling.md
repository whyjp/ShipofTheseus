# PRD 처리 컨벤션 — 충실한 문서가 인터뷰를 대체하지 못하게 하는 허들

## 한 줄 요약
**충실한 PRD 가 입력으로 와도 인터뷰는 그대로 진행된다 — 단, 매 질의가 PRD 의 *근거를 인용* 하고 본 하네스 비평가의 *다른 제안* 을 함께 제시해 사용자가 *적극적으로 비교 선택* 하게 한다.** PRD 추출값을 default 1번에 두는 *passive 채택* 금지. 모든 답에 `user_explicit_confirmation: true` + `confirmed_at` + `prd_evidence_cited: true` + `alternative_proposals_offered: true` 강제.

## 왜 이 허들이 필요한가

ⓐ **인터럽트 0 의 전제 깨짐 위험** — `autonomy.md` 의 인터뷰 후 인터럽트 0 약속은 *페이즈 04 가 모든 답을 받았다는 전제* 위에서 성립. 하나라도 빠지면 페이즈 05 이후의 자율 결정이 *근거 없는* 자동 추정이 됨.
ⓑ **PRD 와 사용자 의도의 분리** — PRD 는 *과거 어느 시점* 의 의도. 본 하네스가 호출되는 *지금* 의 의도가 같다는 보증은 없다. 사용자가 마음을 바꿨는지, PRD 의 어느 부분이 여전히 유효한지 — 명시 확정만이 답.
ⓒ **확증 회귀 ([`interview.md`](interview.md) §2-2) 가 작동할 수 없음** — PRD 만 보고 진행하면 같은 의도를 다른 표현으로 두 번 묻는 인지 트릭이 자동 생략. 모순 발견 기회 0.
ⓓ **사후 책임 추적 불가** — 자율 결정의 *왜* 가 산출물에 기록되어도, 그 기반인 페이즈 04 답이 PRD 자동 추출이면 사용자가 "내가 그렇게 답한 적 없다" 라 할 수 있음. 명시 확정 timestamp 가 책임 분기점.

## PRD 처리 절차 (페이즈 01 + 04 통합)

### 1. PRD 입력 보존

사용자가 호출 시 PRD 를 첨부하면, 본 하네스는 *원본 그대로* 다음에 보존:

```
.ShipofTheseus/<프로젝트>/intent/00-prd-source.md
```

frontmatter:

```yaml
---
skill_name: theseus-harness
skill_version: 0.2.1
phase: prd-source
project_id: <proj>
project_run: <run>
fingerprint: sha256:<PRD 본문의 핑거프린트>
prev_fingerprint: null
produced_at: <PRD 첨부 시각>
producer_agent: user-supplied
prd_kind: full | partial | reference   # 충실도 자기 신고
---
```

본 산출물은 *입력 자료* — 본 하네스가 절대 수정 안 함. 후속 산출물의 prev_fingerprint 체인의 출발점.

### 2. PRD → 인터뷰 항목 매핑

`intent-extractor` 가 PRD 본문에서 다음 *후보값* 추출 (사용자 답 *대체 아님*):

| 인터뷰 항목 | PRD 추출 후보 위치 (휴리스틱) |
| --------- | -------------------------- |
| Q-G1 그레이드 | "복잡도", "범위", "FE+BE", "결제" 같은 키워드 → G2~G5 추정 |
| 의도 무엇/왜 | PRD 의 "Goal" / "Why" / "Background" 섹션 |
| 비목표 | PRD 의 "Out of scope" / "Non-goals" 섹션 |
| 제약 | PRD 의 "Constraints" / "Requirements" 섹션 |
| NFR (성능/가용성/보안) | PRD 의 "Performance" / "SLA" / "Security" 섹션 |
| 스택 | PRD 의 "Tech stack" / "Architecture" 섹션 |
| Q-D1~Q-D7 사전 위임 | PRD 거의 안 다룸 — 사용자에게 *반드시* 직접 질의 |

추출된 후보값은 `intent/01-intent.md` 의 *후보 표* 에 `prd_extracted: true` 마크와 함께 기록.

### 3. 페이즈 04 의 인터뷰 — PRD 근거 인용 + 비평가 대안 추가 (default 강조 금지)

`clarifier` 가 매 질의를 *세 부분* 으로 구성한다 — PRD 근거 인용 + 본 하네스 비평가의 다른 제안 + 객관식 (default 강조 없음).

```
질의 (Q-D3 천정 도달 시 자동 임계 조정):

[PRD 근거 인용]
PRD §3.2 "비기능 요구사항" 발췌:
> "성능 임계 미달 시 인스턴스 자동 업그레이드 (예산 한도 X 까지)."
이 근거로 옵션 2 (리소스 업그레이드 자동) 가 PRD 와 일치합니다.

[본 하네스 비평가의 다른 제안 — *필요 시 추가*]
critic.md 의 분석:
- 옵션 4 (도메인 단순화) 는 PRD 의 "예산 한도" 와 정합되며 비용 변동 0
  으로 더 보수적. PRD 가 *예산을 더 우선* 했다면 이 안이 더 맞을 수 있음.
- 옵션 1 (권고 임계 자동 조정) 는 가장 안전한 default. 아직 운영 데이터
  부족하면 이 안 권장.

[선택지 — default 강조 없음, 사용자가 근거를 보고 비교 선택]
1. 권고 임계로 자동 조정 — 가장 보수, 비용 변동 0
2. 리소스 업그레이드 자동 (PRD §3.2 매핑)
3. 도메인 단순화 자동 시도
4. 정체 수용 — 게이트 영구 fail
```

사용자가 옵션 N 선택 → `intent/04-answers.md` 에 다음 기록 (모든 필드 의무):

```yaml
- question_id: Q-D3
  prd_evidence_cited: true             # PRD 근거 인용 의무 — 인용 누락 시 fail
  prd_evidence:
    section: "§3.2 비기능 요구사항"
    quote: "성능 임계 미달 시 인스턴스 자동 업그레이드 (예산 한도 X 까지)"
    maps_to_option: "2"
  alternative_proposals_offered: true  # 비평가 대안 추가 의무 — 누락 시 fail
  alternatives:
    - option: "4"
      reason: "PRD 의 '예산 한도' 와 정합, 비용 변동 0"
    - option: "1"
      reason: "운영 데이터 부족 시 가장 안전한 default"
  user_answer: "4"                     # 사용자가 비평가 대안 채택
  user_explicit_confirmation: true
  confirmed_at: 2026-05-01T18:42:33+09:00
  matches_prd_proposal: false          # PRD 와 다른 선택 — drift 마크
  drift_reason: "비평가의 비용 보존 우선 권고를 채택"
```

`drift_reason` 이 채워지면 페이즈 05 비평이 *PRD 의 어느 가정이 흔들리는지* 분석 의무.

### default 강조 금지 — 왜

객관식 보기 중 어느 옵션도 "(default)" / "(권장)" / 색상 강조 / 첫 번째 위치 우선 등의 *심리 가중* 표시 금지. 이유:

ⓐ **무비판 채택 차단** — PRD 가 *충실해 보일수록* 사용자가 무의식적으로 1번을 누를 위험. PRD 도 *과거 시점의 의도* 일 뿐.
ⓑ **비평가 대안의 동등 가시성** — 옵션 위치/번호로 PRD 가 우월하게 보이지 않게. 사용자가 *근거 텍스트* 만 보고 선택.
ⓒ **확증 회귀의 토대** — 사용자가 PRD 와 다른 선택을 할 가능성이 *심리적으로 가능* 해야 drift 검출이 의미 있음.

### 4. 모든 인터뷰 항목 답 의무 — 누락 시 진입 거부

페이즈 05 진입 전 *모든 항목* 의 답 + `user_explicit_confirmation: true` 검증. 누락 시 페이즈 04 로 회귀.

필수 항목:
ⓐ Q-G1 (그레이드) — `intent/04-grade.md`
ⓑ Q-D1 ~ Q-D7 (사전 위임 7) — `intent/04-autonomy.md`
ⓒ NFR 임계 (도메인 매칭된 항목 모두) — `intent/01-intent.md` 의 "성능/스펙" 표
ⓓ 스택 (언어/컴파일러/패키지 매니저) — `intent/04-stack.md`
ⓔ 리소스 프로파일 — `intent/04-resource-profile.md`
ⓕ 일반 명료화 질문 (Q1~Q8 [`interview.md`](interview.md) §2 한도) — `intent/04-answers.md`

각 항목의 답 객체에 `user_explicit_confirmation: true` 필드 강제. self_lint C33 이 검증.

## 확증 회귀가 PRD 위에서도 작동

[`interview.md`](interview.md) §2-2 의 확증 회귀 — 같은 의도를 다른 표현으로 두 번 묻기 — 가 PRD 입력에서도 그대로:

ⓐ 페이즈 01 의 마인드맵 단계에서 PRD 의 의도를 *자기 말로* 재구성 (intent-extractor).
ⓑ 페이즈 04 의 객관식에서 같은 의도를 *다른 표현* 으로 재질의.
ⓒ PRD 추출값과 사용자 명시 답이 *의미상 다르면* drift 마크 — 페이즈 05 의 비평 입력으로 반드시 들어감.

PRD 가 충실해도 확증 회귀는 *의무* — 시간 차이로 사용자 의도가 변했을 가능성을 잡는 유일한 메커니즘.

## 빠른 인터뷰 vs 인터뷰 스킵 — 구분

ⓐ **빠른 인터뷰 (정상)** — PRD 매핑 후보 1번이 default 로 표시, 사용자가 모든 항목에 1번 빠르게 답. 각 항목 1초씩 → 7+5+α 항목 = 1~2 분.
ⓑ **인터뷰 스킵 (금지)** — `intent/04-answers.md` 자체가 비어 있거나 `user_explicit_confirmation: true` 가 없는 항목 존재. self_lint C33 이 fail.

빠른 인터뷰는 본 컨벤션이 권장 — 사용자 부담 최소화. 단 *형식적 의식* 인 명시 확정은 절대 생략 안 됨.

## PRD 가 부분/낡음/모순일 때

ⓐ **partial PRD** (`prd_kind: partial`) — 일부 섹션 누락. 누락 부분은 일반 인터뷰로 채움.
ⓑ **낡은 PRD** — 사용자 답이 PRD 와 *의미상 다름* drift 마크 → 페이즈 05 비평이 "PRD 가 stale" 표시 + 다음 회차 PRD 갱신 권고.
ⓒ **모순 PRD** — PRD 자체가 자기 모순 (예: "p99 < 100ms" 와 "비동기 보상 흐름" 동시) → 페이즈 04 의 명시 확정에서 사용자가 둘 중 하나만 선택. 두 모순이 모두 사용자 답으로 들어오면 [`autonomy.md`](autonomy.md) 의 *유일 예외* (의도 모순) 트리거.

## 안티 패턴

ⓐ **PRD 충실하니까 페이즈 04 생략** — 본 컨벤션의 *가장 큰 위반*. C33 이 fail.
ⓑ **PRD 추출값을 사용자 답으로 *대체*** — 명시 확정 흔적 없음. self_lint fail.
ⓒ **PRD 매핑을 1번에 두고 default 강조** — passive 채택 유도. 본 컨벤션 §3 위반. 옵션 위치/번호/색상 어떤 것도 PRD 우월 표시 금지.
ⓓ **비평가 대안 누락** — `alternative_proposals_offered: true` 가 false 면 fail. PRD 가 명백히 정답이어도 *비평 의무* 는 면제 안 됨 (그래야 사용자가 무비판 채택을 못함).
ⓔ **PRD 근거 인용 누락** — `prd_evidence_cited: true` + `prd_evidence.section` + `prd_evidence.quote` 필수. 인용 없는 매핑은 *근거 없는 자동 추정* 과 같음.
ⓕ **모든 객관식 답이 PRD 매핑 옵션** — 그 자체는 정상이지만, *확증 회귀 drift 0* 이면 사용자가 PRD 를 *읽지 않고* 무비판 채택한 의심 → 비평 페이즈에 "PRD 재독 필요" 권고.
ⓖ **PRD 원본을 산출물로 보존 안 함** — `intent/00-prd-source.md` 누락은 사후 책임 추적 불가. 산출물 자산 손실.
ⓗ **`user_explicit_confirmation` 필드 누락한 답 통과** — 본 컨벤션의 핵심 강제. self_lint C33 이 catch.
