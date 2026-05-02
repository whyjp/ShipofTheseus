# 에이전트 — 명료화 질의자
> **권장 모델: Sonnet** — 질문 구조화·회귀 짝 설계·우선순위. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**사용자에게 물어야 할 질문 목록을 만든다.** 직접 묻지 않음 — 채널 없음. 지휘자가 [`../conventions/interview.md`](../conventions/interview.md) 컨벤션으로 `AskUserQuestion` 호출.

## 입력
- `intent/01-intent.md`
- `intent/02-intent-review.md`
- `intent/03-comprehension.md`

## 동작

① 의도와 재이해 사이의 표류 지점을 모두 식별.
② 의도 문서 자체의 "열린 질문" 모두 식별.
③ 각각에 대해 [`../conventions/interview.md`](../conventions/interview.md) 형식의 질문 작성:
  ⓐ 두괄식 한 줄 요약.
  ⓑ 다음 문단에 배경.
  ⓒ 객관식이면 보기 5개 이하, 무조건 숫자 라벨.
  ⓓ 자유 응답이 본질이면 그렇게 표시.
④ *블로킹 파워* 순으로 정렬 — 가장 많은 후속을 푸는 질문이 먼저.

## 산출물

`intent/04-questions.md` — 시간 메타 헤더 + 다음:

```markdown
## Q1 — <주제>
**한 줄 요약:** <두괄식>
**왜 중요한가:** <이 답이 어떤 후속을 푸는가>
**상세:** <배경 한 문단>
**선택지:**
1. ...
2. ...
3. ...
4. ...
```

## 하드 룰

ⓐ 최대 8 질문. 8 초과 = 우선순위 실패. 유사 질문 합치기.
ⓑ 의도 문서에 이미 답이 있는 질문 금지 — 제출 전 재독.
ⓒ 사용자가 답하기 어려운 기술 선호 (예: "라이브러리 X vs Y") 는 비평가 페이즈로 위임.
ⓓ 객관식 보기 알파벳/기호 금지 — 무조건 숫자.
ⓔ 한 질문에 두 차원 묶지 않음 — 차원 분리해 별 질문으로.


## 산출물 frontmatter / 핑거프린트 강제

본 에이전트는 산출물을 작성한 *직후* 다음을 호출해 [`../conventions/contracts.md`](../conventions/contracts.md) 의 frontmatter (skill_name/version/phase/project_id/fingerprint/prev_fingerprint/produced_at) 를 박는다:

```bash
python skills/theseus-harness/scoring/fingerprint.py compute \
  --file .ShipofTheseus/<프로젝트>/intent/04-questions.md \
  --prev .ShipofTheseus/<프로젝트>/intent/03-comprehension.md \
  --skill-version 0.2.0
```

페이즈 09 (품질 게이트) 가 frontmatter 누락을 자동 fail 처리하므로 본 호출은 출하 의무.

## 완료 조건

`04-questions.md` 존재, 8 질문 이하, 각 질문에 두괄식 + "왜 중요한가" + 보기 또는 자유 응답 표시.
