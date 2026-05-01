# theseus-harness

## 한 줄 요약
**한 요구를 처음 의도한 타이틀로 끝까지 부를 자격을 만드는 재귀 멀티 에이전트 코딩 하네스 (Claude Code 스킬).** 메인 진입점은 [`SKILL.md`](SKILL.md). 의도→명명→문서화→교차 이해→사용자 질의→비평→계획→재계획→구현→5종 게이트→무한 스프린트 루프(임계 0.9)→회귀 바이섹트→bun 웹뷰→핸드오프.

## 빠른 참조

ⓐ [`SKILL.md`](SKILL.md) — 지휘자(메인 에이전트)가 가장 먼저 읽는 파일. 14 페이즈 표.
ⓑ [`phases/`](phases/) — 페이즈 00–13 의 입력·서브에이전트·산출물·성공 기준.
ⓒ [`agents/`](agents/) — 13 개 서브에이전트 프롬프트 (project-namer, intent-extractor, doc-reviewer, independent-comprehender, clarifier, critic, planner, plan-reviewer, implementer, quality-gate, tester, regression-analyst, webview-builder).
ⓓ [`conventions/`](conventions/) — 인터뷰(두괄식·1질의·숫자 5개) + 시간 기록 컨벤션.
ⓔ [`scoring/rubric.md`](scoring/rubric.md) + [`scoring/score.py`](scoring/score.py) — 6 차원 가중 채점, **DIP 위반 단독 hard cap 0.6**.
ⓕ [`templates/`](templates/) — intent / plan / sprint-report / naming 템플릿 + bun 기반 webview 스캐폴드.

## 주요 원칙

ⓐ **의존성 역전(DIP) 이 SOLID 중 최우선** — 위반은 단독 hard fail.
ⓑ **관심사 분리(SoC) 가 단위 테스트 기반** — 모듈 경계를 기능보다 먼저.
ⓒ **장인의 도자기처럼** 깊은 위반은 모듈을 깨고 페이즈 06 부터 다시 빚는다 (페이즈 11 `re-architect`).
ⓓ **모든 산출물은 파일** — `.ShipofTheseus/<프로젝트>/` 트리에 카테고리별로 떨어진다.
ⓔ **무한 스프린트 루프** — 임계 0.9 까지, 회귀 시에만 사용자 ack 로 정지.
ⓕ **시간 라이브 표시** — 매 산출물 헤더에 시작·소요·누적·현재.
ⓖ **백엔드 기본값 Go** — 사용자 명시 없을 때.
ⓗ **항상 인터랙티브 웹뷰** — 페이즈 12 가 bun 기반 be4fe + fe 6 탭 자동 생성.

## 산출물 트리 (한 프로젝트 실행 결과)

```
.ShipofTheseus/<프로젝트명>/
├── timing/start.json
├── naming/00-naming.md
├── intent/01..05*.md
├── plan/06..07*.md
├── impl/08-impl-log.md
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, unit.json, e2e.json}
├── webview/                           # bun + hono + react
└── handoff/13-handoff.md
```

## 채점 검증

```bash
python -m pytest scoring/test_score.py -q
# 11 passed
```

## 호출

Claude Code 세션에서:

```
/theseus-harness <요구사항>
```

Claude 가 [`SKILL.md`](SKILL.md) 를 읽고 페이즈 00 부터 시작한다.

## 더 읽을거리

ⓐ [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — 신뢰 담보, 도자기 장인 비유, Ralph/OhMy/우로보로스 합성, SOLID/TDD/DDD/Hexagonal/Clean/실용주의 매핑.
ⓑ [`../../INSTALL.md`](../../INSTALL.md) — git clone 기반 설치, 플러그인 매니페스트, 트러블슈팅.
