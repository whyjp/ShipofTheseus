# theseus-webview 가이드

## 한 줄 요약

**페이즈 12 — bun + hono + react 기반 인터랙티브 웹뷰 자동 생성 (6 탭 + Mermaid 자동 렌더 + TimingHeader 라이브).**

스프린트 결과를 사람이 *시각적으로* 확인할 수 있도록 웹뷰를 항상 같이 만든다 — 텍스트 산출물만으로는 점수 시계열·다이어그램·라이브 상태를 따라가기 어렵기 때문.

## 언제 호출하는가

ⓐ orchestrator 가 자동 위임 (sprint 임계 도달 후).
ⓑ 외부에서 받은 모든 페이즈 산출물로 *웹뷰만 다시 빌드* 하고 싶을 때 — 단독 호출.

## 호출 형식

```
/theseus-webview <요구사항>
```

단, *모든 페이즈 산출물* (intent ~ sprints) 이 존재해야 한다. frontmatter 검증 실패 시 진입 거부.

## 산출물

| 위치 | 내용 |
| ---- | --- |
| `webview/package.json` | bun + hono + react + Mermaid 의존 |
| `webview/server.ts` | hono 백엔드, `/api/sprints` `/api/intent` 등 |
| `webview/src/App.tsx` | 6 탭 라우팅 |
| `webview/src/tabs/Intent.tsx` | 의도·인터뷰·결정 |
| `webview/src/tabs/Plan.tsx` | TODO DAG·시퀀스 다이어그램 (Mermaid 자동 렌더) |
| `webview/src/tabs/Impl.tsx` | 구현 로그·코드 트리·테스트 |
| `webview/src/tabs/Quality.tsx` | 5 게이트 결과·remediation TODO |
| `webview/src/tabs/Sprints.tsx` | 점수 시계열 차트·바이섹트 |
| `webview/src/tabs/Progress.tsx` | TimingHeader 라이브·resume 상태 |

## 실행

```bash
cd webview
bun install
bun dev
# http://localhost:3000
```

자세한 의존은 [`../../INSTALL.md`](../../INSTALL.md) 의 §5.

## Mermaid 자동 렌더 (의무)

페이즈 06 의 시퀀스 다이어그램, 페이즈 01 의 마인드맵 등이 *Mermaid 텍스트* 로 산출된다. 웹뷰는 모든 Mermaid 블록을 자동으로 SVG 로 렌더 — 사용자가 별도 작업 없이 시각적으로 확인 가능. self_lint C18 이 강제.

## TimingHeader 라이브

각 산출물 헤더의 timing 정보 (`**시작:** / **종료:** / **누적 경과:** / **현재 시각:** / **이 스프린트 소요:** / **소요:**`) 가 Progress 탭에 라이브로 표시. 장기간 작업 시 사용자가 진행 상황을 *세션 밖에서* 따라갈 수 있다 — 자세한 룰은 [`../../skills/theseus-harness/conventions/timing.md`](../../skills/theseus-harness/conventions/timing.md).

## 입출력 (단독 호출)

- **입력**: 모든 페이즈 산출물 (frontmatter 검증 통과 필수).
- **출력**: `webview/` 디렉터리 (bun 프로젝트). 다음 스킬 (`theseus-handoff`) 이 입력으로 받음.

## 자주 묻는 질문

**Q. 웹뷰가 항상 만들어지는가?**
A. 그렇다. G2 미니 모드에서도 축약된 형태(3 탭) 의 웹뷰가 같이 만들어진다 — *visual feedback 없이 14 페이즈 진행은 사용자가 따라가기 어렵다* 가 본 하네스의 핵심 가설.

**Q. bun 외 다른 런타임으로 바꿀 수 있는가?**
A. v0.2.x 에서는 bun 고정. v0.3.x 에서 Node fallback 검토 예정.

**Q. 차트가 비어 있다면?**
A. v0.2.1 핫픽스 이전 버전이라면 `inputs.json` 만 로드해 비어 있을 수 있음. 현재 버전은 `score.json` 도 로드 — 이전 산출물이라면 `python skills/theseus-harness/scoring/score.py --inputs <inputs.json> --out <score.json>` 으로 score.json 을 생성하고 다시 로드.

**Q. 라이브 갱신은?**
A. SSE (server-sent events) 로 산출물 변화를 push. 새 sprint 가 추가되거나 timing 헤더가 갱신되면 즉시 반영.

## 더 읽을거리

- [`../../skills/theseus-webview/SKILL.md`](../../skills/theseus-webview/SKILL.md) — 기계 진입점.
- [`../../skills/theseus-harness/conventions/timing.md`](../../skills/theseus-harness/conventions/timing.md) — TimingHeader 룰.
- [`../../skills/theseus-harness/agents/webview-builder.md`](../../skills/theseus-harness/agents/webview-builder.md) — 웹뷰 빌더 에이전트.
