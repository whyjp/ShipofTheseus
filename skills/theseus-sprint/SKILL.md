---
name: theseus-sprint
version: 0.2.1
description: 무한 스프린트 루프 (임계 0.95~0.99999 그레이드별) + 회귀 바이섹트 + 정체 감지 + 천정 자동 조정 + 멀티버스. theseus-orchestrator 또는 단독 호출. 단일 source of truth 는 ../theseus-harness/. frontmatter (contracts.md) 가 입출력 계약.
---

# theseus-sprint — 페이즈 10–11 분해 stub

## 한 줄 요약
**무한 스프린트 루프 (임계 0.95~0.99999 그레이드별) + 회귀 바이섹트 + 정체 감지 + 천정 자동 조정 + 멀티버스**. 본 stub 은 형태와 인터페이스만 정의 — 콘텐츠는 [`../theseus-harness/`](../theseus-harness/) 단일 source of truth.

## 입력 산출물 (frontmatter 검증)

- `quality 산출물 (quality/09)`

검증 명령:
```bash
python ../theseus-harness/scoring/fingerprint.py verify --file <input>
```

검증 실패 시 본 스킬 진입 거부 ([`../theseus-orchestrator/SKILL.md`](../theseus-orchestrator/SKILL.md) 의 안전 장치).

## 출력 산출물

- `sprints/NN/{report.md`
- `inputs.json`
- `lesson_pack.json`
- `bisect.md?`
- `snapshot/?`
- `unit.json`
- `e2e.json}`
- `multiverse/<id>/{universe-a,b,c}/...`

각 산출물에 [`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md) 의 frontmatter 박음 — 다음 스킬이 입력으로 받음.

## 위임할 페이즈 문서

- [`../theseus-harness/phases/10-test-loop.md`](../theseus-harness/phases/10-test-loop.md)
- [`../theseus-harness/phases/11-regression-bisect.md`](../theseus-harness/phases/11-regression-bisect.md)

## 위임할 에이전트

- [`../theseus-harness/agents/tester.md`](../theseus-harness/agents/tester.md)
- [`../theseus-harness/agents/regression-analyst.md`](../theseus-harness/agents/regression-analyst.md)

## 적용 컨벤션 (그레이드별)

[`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md) 의 매트릭스 따름. 본 스킬이 활성화되는 그레이드는:

G3 (3 sprint cap) / G4 (무한) / G5 (무한 + 빡빡)

## 단독 호출

```bash
/theseus-sprint --from <input_dir>
```

`<input_dir>` 의 frontmatter 가 본 스킬의 *입력 계약* 을 만족하면 진입. 예:

```bash
# 이미 의도 산출물 있음 → 본 스킬부터
/theseus-sprint --from .ShipofTheseus/<프로젝트>/
```

## 본 stub 의 안전 보장

ⓐ **콘텐츠 복제 금지** — 본 SKILL.md 는 위임 + 인터페이스만. 룰 본문은 `../theseus-harness/conventions/` 와 `../theseus-harness/phases/` 의 단일 source.
ⓑ **연동 테스트** — `../theseus-harness/scoring/test_skill_handoff.py` 가 본 스킬 산출물의 frontmatter 가 다음 스킬 입력으로 valid 한지 검증.
ⓒ **self_lint C28** — 본 stub 의 cross-link 무결성.

## 향후 풀 분해 (v0.4.0 후보)

본 stub 의 위임 대상 콘텐츠를 *실제로* 본 디렉터리로 이동 (`phases/`, `agents/` 서브폴더 추가). 단, 단일 source of truth 룰은 깨지면 안 되므로 — 분해 시 `../theseus-harness/` 의 해당 콘텐츠 삭제 + 본 디렉터리에 이동 + 모든 cross-link 갱신. self_lint 가 매 단계 검증.
