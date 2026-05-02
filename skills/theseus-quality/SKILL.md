---
name: theseus-quality
version: 0.2.0
description: 5 게이트 + Phase V 측정 유효성 + frontmatter 검증. theseus-orchestrator 또는 단독 호출. 단일 source of truth 는 ../theseus-harness/. frontmatter (contracts.md) 가 입출력 계약.
---

# theseus-quality — 페이즈 09 분해 stub

## 한 줄 요약
**5 게이트 + Phase V 측정 유효성 + frontmatter 검증**. 본 stub 은 형태와 인터페이스만 정의 — 콘텐츠는 [`../theseus-harness/`](../theseus-harness/) 단일 source of truth.

## 입력 산출물 (frontmatter 검증)

- `impl 산출물 (impl/08)`

검증 명령:
```bash
python ../theseus-harness/scoring/fingerprint.py verify --file <input>
```

검증 실패 시 본 스킬 진입 거부 ([`../theseus-orchestrator/SKILL.md`](../theseus-orchestrator/SKILL.md) 의 안전 장치).

## 출력 산출물

- `quality/09-quality-gate.md (게이트 1~7 결과 + remediation TODO)`

각 산출물에 [`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md) 의 frontmatter 박음 — 다음 스킬이 입력으로 받음.

## 위임할 페이즈 문서

- [`../theseus-harness/phases/09-quality-gates.md`](../theseus-harness/phases/09-quality-gates.md)

## 위임할 에이전트

- [`../theseus-harness/agents/quality-gate.md`](../theseus-harness/agents/quality-gate.md)

## 적용 컨벤션 (그레이드별)

[`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md) 의 매트릭스 따름. 본 스킬이 활성화되는 그레이드는:

G2~G5 모두

## 단독 호출

```bash
/theseus-quality --from <input_dir>
```

`<input_dir>` 의 frontmatter 가 본 스킬의 *입력 계약* 을 만족하면 진입. 예:

```bash
# 이미 의도 산출물 있음 → 본 스킬부터
/theseus-quality --from .ShipofTheseus/<프로젝트>/
```

## 본 stub 의 안전 보장

ⓐ **콘텐츠 복제 금지** — 본 SKILL.md 는 위임 + 인터페이스만. 룰 본문은 `../theseus-harness/conventions/` 와 `../theseus-harness/phases/` 의 단일 source.
ⓑ **연동 테스트** — `../theseus-harness/scoring/test_skill_handoff.py` 가 본 스킬 산출물의 frontmatter 가 다음 스킬 입력으로 valid 한지 검증.
ⓒ **self_lint C28** — 본 stub 의 cross-link 무결성.

## 향후 풀 분해 (v0.4.0 후보)

본 stub 의 위임 대상 콘텐츠를 *실제로* 본 디렉터리로 이동 (`phases/`, `agents/` 서브폴더 추가). 단, 단일 source of truth 룰은 깨지면 안 되므로 — 분해 시 `../theseus-harness/` 의 해당 콘텐츠 삭제 + 본 디렉터리에 이동 + 모든 cross-link 갱신. self_lint 가 매 단계 검증.
