# theseus-handoff 가이드

## 한 줄 요약

**페이즈 13 — 한 줄 요약 + 점수 시계열 + 자율 결정 이력 + 웹뷰 실행 명령 + (자율 권한 시) PR 생성.**

본 하네스의 *마지막 페이즈*. 사용자에게 결과를 요약 메시지로 돌려주고, 자율 권한이 있으면 PR 까지 자동 생성한다.

## 언제 호출하는가

ⓐ orchestrator 가 자동 위임 (webview 직후).
ⓑ 외부에서 받은 모든 페이즈 + sprint 결과로 *핸드오프만 다시* 만들고 싶을 때 — 단독 호출.

## 호출 형식

```
/theseus-handoff <요구사항>
```

단, *모든 페이즈 산출물 + sprint 결과* 가 존재해야 한다. frontmatter 검증 실패 시 진입 거부.

## 산출물

| 위치 | 내용 |
| ---- | --- |
| `handoff/13-handoff.md` | 한 줄 요약 + 점수 시계열 + 결정 이력 + 웹뷰 실행 명령 |
| 채팅 메시지 | 위 핸드오프의 사용자 진입점 (마지막 LLM 응답) |
| (자율 권한 시) PR | GitHub PR 자동 생성 (제목·본문·체크리스트) |

## 채팅 메시지 형식

```
✓ <project_id> — 임계 0.<NNN> 도달 (스프린트 NN 회 / 누적 시간 H:MM:SS)

한 줄 요약: <intent/01 의 한 줄 요약>

점수 시계열: 0.72 → 0.84 → 0.91 → 0.96 → 0.999

자율 결정 이력 (총 N 건):
  - <결정 1 요약>
  - <결정 2 요약>
  ...

웹뷰: cd webview && bun install && bun dev
PR: <PR URL 또는 "자율 권한 없음 — 사용자 직접 생성">

산출물: .ShipofTheseus/<project_id>/
```

## 자율 PR 생성

페이즈 04 의 자율 권한 매트릭스에 따라 결정:

| 자율 권한 단계 | PR 동작 |
| ------------ | ------- |
| L0 (모든 결정 사용자 ack) | PR 생성 안 함, 핸드오프 메시지에 "사용자 직접 생성" |
| L1 (자율 결정 + 사후 리뷰) | PR draft 로 생성, 본문에 결정 이력 모두 박음 |
| L2 (자율 결정 + 자동 머지 후보) | PR open 으로 생성, 사용자가 머지만 |
| L3 (완전 자율 — 거의 안 씀) | PR 생성 + 자동 머지 (CI 통과 시) |

자세한 매트릭스는 [`../../skills/theseus-harness/conventions/autonomy.md`](../../skills/theseus-harness/conventions/autonomy.md).

## 입출력 (단독 호출)

- **입력**: 모든 페이즈 산출물 + sprint 결과 (frontmatter 검증 통과 필수).
- **출력**: `handoff/13-handoff.md` + 채팅 메시지 + (자율 시) PR.

## 자주 묻는 질문

**Q. 임계에 도달하지 못한 채 페이즈 13 에 진입하면?**
A. orchestrator 가 막는다 — 페이즈 13 은 sprint 임계 도달 또는 명시적 중단 (사용자 ack) 후에만 진입. 단독 호출 시에도 `quality/09-quality-gate.md` 의 `final: true` frontmatter 가 없으면 거부.

**Q. PR 본문에 무엇이 들어가는가?**
A. 한 줄 요약, 점수 시계열, 자율 결정 이력 전체, 웹뷰 실행 명령, 산출물 트리. 리뷰어가 사후 리뷰할 수 있게 *모든 결정 근거가 본문에 들어간다.*

**Q. PR 생성 권한 (GitHub token) 은 어디서?**
A. 본 스킬은 GitHub MCP 도구를 사용 — Claude Code 환경에 GitHub 통합이 설정되어 있어야 한다. 미설정 시 자동으로 L0 로 다운시프트 후 사용자에게 직접 생성 안내.

**Q. 결정 이력이 너무 길면?**
A. 핸드오프 메시지에는 *상위 N 건* 만 (default 10), 전체는 `handoff/13-handoff.md` 본문에. 우선순위는 점수 영향도 + 사용자 영향도.

## 더 읽을거리

- [`../../skills/theseus-handoff/SKILL.md`](../../skills/theseus-handoff/SKILL.md) — 기계 진입점.
- [`../../skills/theseus-harness/conventions/autonomy.md`](../../skills/theseus-harness/conventions/autonomy.md) — 자율 권한 매트릭스.
- [`../../skills/theseus-harness/agents/handoff-writer.md`](../../skills/theseus-harness/agents/handoff-writer.md) — 핸드오프 작성 에이전트.
