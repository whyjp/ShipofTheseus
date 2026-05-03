---
name: theseus-intent
version: 0.7.7
description: 페이즈 00–05 분해 — 명명/의도/마인드맵/콜드 재이해/사용자 질의/비평. 단일 source 는 ../theseus-harness/. frontmatter 가 입출력 계약.
---

# theseus-intent — 페이즈 00–05 분해 stub

## 한 줄 요약
**프로젝트 명명 + 의도 추출 + 마인드맵 + 의도 리뷰 + 콜드 재이해 + 사용자 질의(Q-G1+Q-D1~D7+NFR) + 비평·대안**. 본 stub 은 형태와 인터페이스만 정의 — 콘텐츠는 [`../theseus-harness/`](../theseus-harness/) 단일 source of truth.

## 입력 산출물 (frontmatter 검증)

- `사용자 원본 요청 + 레포 컨텍스트`

검증 명령:
```bash
python ../theseus-harness/scoring/fingerprint.py verify --file <input>
```

검증 실패 시 본 스킬 진입 거부 ([`../theseus-orchestrator/SKILL.md`](../theseus-orchestrator/SKILL.md) 의 안전 장치).

## 출력 산출물

- `naming/00-naming.md`
- `intent/01-intent.md`
- `intent/02-intent-review.md`
- `intent/03-comprehension.md`
- `intent/04-{questions,answers,autonomy,grade,resource-profile,stack}.md`
- `intent/05-{critique,decisions}.md`

각 산출물에 [`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md) 의 frontmatter 박음 — 다음 스킬이 입력으로 받음.

## 위임할 페이즈 문서

- [`../theseus-harness/phases/00-naming.md`](../theseus-harness/phases/00-naming.md)
- [`../theseus-harness/phases/01-intent.md`](../theseus-harness/phases/01-intent.md)
- [`../theseus-harness/phases/02-document.md`](../theseus-harness/phases/02-document.md)
- [`../theseus-harness/phases/03-independent-comprehension.md`](../theseus-harness/phases/03-independent-comprehension.md)
- [`../theseus-harness/phases/04-clarify.md`](../theseus-harness/phases/04-clarify.md)
- [`../theseus-harness/phases/05-critique.md`](../theseus-harness/phases/05-critique.md)

## 위임할 에이전트

- [`../theseus-harness/agents/project-namer.md`](../theseus-harness/agents/project-namer.md)
- [`../theseus-harness/agents/intent-extractor.md`](../theseus-harness/agents/intent-extractor.md)
- [`../theseus-harness/agents/doc-reviewer.md`](../theseus-harness/agents/doc-reviewer.md)
- [`../theseus-harness/agents/independent-comprehender.md`](../theseus-harness/agents/independent-comprehender.md)
- [`../theseus-harness/agents/clarifier.md`](../theseus-harness/agents/clarifier.md)
- [`../theseus-harness/agents/critic.md`](../theseus-harness/agents/critic.md)

## 적용 컨벤션 (그레이드별)

[`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md) 의 매트릭스 따름. 본 스킬이 활성화되는 그레이드는:

G2 (질의 일부) / G3+ (전체)

## 단독 호출 (재진입)

> **단독 호출 시 의존성:** 본 stub 은 *위임 + 인터페이스* 만. 룰 본문은 [`../theseus-harness/`](../theseus-harness/) 단일 source 에 위치. **fresh user 가 본 stub 만 설치하면 본문 점프가 모두 dead link** — 본 저장소 전체 또는 최소 [`../theseus-harness/`](../theseus-harness/) 동반 설치 필요.

```bash
# 반드시 theseus-harness 동반 설치 후
/theseus-intent --from <input_dir>
```

`<input_dir>` 의 frontmatter 가 본 스킬의 *입력 계약* 을 만족하면 진입.

## 본 stub 의 안전 보장

a- **콘텐츠 복제 금지** — 본 SKILL.md 는 위임 + 인터페이스만. 룰 본문은 `../theseus-harness/conventions/` 와 `../theseus-harness/phases/` 의 단일 source.
b- **연동 테스트** — `../theseus-harness/scoring/test_skill_handoff.py` 가 본 스킬 산출물의 frontmatter 가 다음 스킬 입력으로 valid 한지 검증.
c- **self_lint C28** — 본 stub 의 cross-link 무결성.

## 향후 풀 분해 (v0.4.0 후보)

본 stub 의 위임 대상 콘텐츠를 *실제로* 본 디렉터리로 이동 (`phases/`, `agents/` 서브폴더 추가). 단, 단일 source of truth 룰은 깨지면 안 되므로 — 분해 시 `../theseus-harness/` 의 해당 콘텐츠 삭제 + 본 디렉터리에 이동 + 모든 cross-link 갱신. self_lint 가 매 단계 검증.
