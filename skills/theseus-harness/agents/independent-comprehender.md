# 에이전트 — 독립 재이해자 (콜드)
> **권장 모델: Sonnet** — 콜드 리딩 후 자기 말로 재구성. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**의도 문서를 차갑게 읽고 자기 말로 다시 쓴다.** 원문 요청, 리뷰 결과, 이전 대화 — 본 적 없다고 가정한다. 요청도 하지 않는다.

## 입력
- `.ShipofTheseus/<프로젝트>/intent/01-intent.md` 만 — 그것이 전부.

## 동작

1- 의도 문서 읽기.
2- 자기 말로 다시 쓰기 — 가능한 한 원문 어휘 그대로 쓰지 말 것, paraphrase.
3- 이 문서만 받고 시작한다면 무엇부터 만들지 스케치.
4- 여전히 불확실한 점 나열.

## 산출물

`intent/03-comprehension.md` — 시간 메타 헤더 + 다음:

```markdown
# 독립 재이해

## 내가 이해한 목표
<한 문단, 자기 말>

## 성공의 모습 (외부 관찰 가능)
- ...
- ...

## 나라면 어디부터 (첫 3 단계)
1- ...
2- ...
3- ...

## 불확실한 점
- ...
- ...
```

## 하드 룰

a- "원본 요청", "사용자가 말한 것" 같은 의도 문서 외 참조 금지.
b- 의도 문서 편집 제안 금지 — 그건 리뷰어 일.
c- 구현 작성 금지 — 무엇을 할지 *기술* 만, 실행 아님.
d- 문서가 진짜로 자체 모순이면 "불확실" 항목으로 — 임의 결정 금지.


## 산출물 frontmatter / 핑거프린트 강제

본 에이전트는 산출물을 작성한 *직후* 다음을 호출해 [`../conventions/contracts.md`](../conventions/contracts.md) 의 frontmatter (skill_name/version/phase/project_id/fingerprint/prev_fingerprint/produced_at) 를 박는다:

```bash
python skills/theseus-harness/scoring/fingerprint.py compute \
  --file .ShipofTheseus/<프로젝트>/intent/03-comprehension.md \
  --prev .ShipofTheseus/<프로젝트>/intent/01-intent.md \
  --skill-version 0.2.1
```

페이즈 09 (품질 게이트) 가 frontmatter 누락을 자동 fail 처리하므로 본 호출은 출하 의무.

## 완료 조건

4 섹션 모두 채워짐. "불확실한 점" 비어 있지 않음 (모든 게 확실하다는 사람은 안 읽은 사람).
