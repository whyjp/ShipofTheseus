---
name: theseus-harness
description: 다중 모듈/프론트엔드+백엔드/도메인 미정착 등 의도 모호 + 테스트 부족이 실제 손해를 부르는 비-단순 기능을 위한 재귀 멀티 에이전트 코딩 하네스. 프로젝트 명명 → 의도 추출 → 교차 이해 → 사용자 질의 → 비평 → 계획 → 재계획 → 구현 → 5종 품질 게이트 → 점수 0.9 도달까지 무한 스프린트 루프 → 회귀 바이섹트 → bun 기반 be4fe + fe 웹뷰 자동 생성 → 핸드오프. 모든 사용자 질의는 두괄식·1회 1질의·숫자 객관식 5개 이하 컨벤션을 따르며, 모든 페이즈 산출물 헤더에 시작·종료·누적 경과·현재 시각을 표기한다. 한 줄 수정·기계적 리네임 같은 사소한 작업에는 사용 금지.
---

# 테세우스 하네스

## 한 줄 요약
**한 요구를 처음 의도한 타이틀로 끝까지 부를 자격을 만들기 위한 재귀 코딩 하네스.** 당신(메인 에이전트)은 *지휘자*다. 직접 작업하지 않고, 페이즈마다 정해진 서브 에이전트를 띄워 산출물을 받아 다음 페이즈로 넘긴다.

## 장인의 도자기 — 페이즈 재회귀의 정당화

도자기 장인은 흙을 빚다 마음에 들지 않으면 깨고 다시 빚는다. 본 하네스의 페이즈 재회귀(특히 페이즈 11 의 `re-architect`) 는 그 *깨고 다시 빚기* 의 코드판이다. 회귀가 깊은 SOLID/DIP 위반의 증상이면 모듈을 통째로 페이즈 06(계획) 부터 다시 — 부분 수정으로 덮는 것은 잘못된 형 위에 흙을 더 붙이는 일이다. 자세한 근거는 [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md).

## 가장 중요한 원칙

ⓐ **의존성 역전(DIP) 이 SOLID 중 최우선.** 품질 게이트(페이즈 09)는 DIP 위반 단독 hard fail, 나머지 SOLID 는 부분 감점.
ⓑ **관심사 분리(SoC) 가 단위 테스트 기반.** 설계자는 모듈 경계를 먼저 긋고 기능 TODO 를 그 위에 배치 — "기능부터, 분리는 나중에" 금지.
ⓒ **모든 산출물은 파일로 떨어진다** — 어느 시점으로든 되돌아갈 수 있게.

## 동작 원리 (요약 → 상세)

ⓐ 모든 산출물은 `.ShipofTheseus/<프로젝트명>/` 아래에 카테고리별로 떨어진다.
ⓑ 모든 사용자 질의는 [`conventions/interview.md`](conventions/interview.md) 컨벤션을 강제 준수.
ⓒ 모든 산출물 헤더는 [`conventions/timing.md`](conventions/timing.md) 의 시작·종료·누적·현재 시각을 표기.
ⓓ 스프린트 점수 0.9 미만이면 무한 반복. 0.05 이상 하락하면 즉시 회귀 바이섹트.
ⓔ 최종 산출물에 모듈 구성도·설계 의도·구현 의도·단위/E2E 테스트 탭을 가진 bun 기반 인터랙티브 웹뷰가 항상 포함된다.

## 사전 준비 (1회)

① 최초 프롬프트 수신 즉시 `date +%FT%T%z` 로 시간 기록.
② Phase 00 호출 — 프로젝트명·모듈명을 사용자와 함께 확정.
③ `.ShipofTheseus/<프로젝트명>/` 트리 생성. `timing/start.json` 작성.
④ 본 페이즈 목록을 `TodoWrite` 로 미러링. 각 페이즈는 `in_progress` → 산출물 생성 + 자가 확인 → `completed`.

## 산출물 트리

```
.ShipofTheseus/<프로젝트명>/
├── timing/
│   └── start.json                       # 절대 시작 시각 (불변)
├── naming/
│   ├── 00-candidates.md                 # 후보안 + 충돌 검토
│   └── 00-naming.md                     # 확정된 프로젝트명/모듈명
├── intent/
│   ├── 01-intent.md
│   ├── 02-intent-review.md
│   ├── 03-comprehension.md
│   ├── 04-questions.md
│   ├── 04-answers.md
│   ├── 05-critique.md
│   └── 05-decisions.md
├── plan/
│   ├── 06-plan.md
│   └── 07-plan-review.md
├── impl/
│   └── 08-impl-log.md
├── quality/
│   └── 09-quality-gate.md
├── sprints/
│   ├── 01/
│   │   ├── report.md
│   │   ├── inputs.json
│   │   └── bisect.md                    # 회귀 트리거 시에만
│   ├── 02/...
│   └── ...
├── webview/                             # Phase 12 산출물
│   ├── package.json                     # bun
│   ├── server.ts                        # be4fe (Hono 기반)
│   ├── src/...                          # fe (React)
│   └── README.md
└── handoff/
    └── 13-handoff.md
```

## 페이즈 (14개)

각 페이즈는 [`phases/`](phases/) 의 자기 문서에 입력·서브에이전트·산출물·성공 기준이 정의된다. **호출 직전에 페이즈 문서를 다시 읽어라** — 추측 금지.

| # | 페이즈 | 페이즈 문서 | 서브에이전트 |
| - | ----- | --------- | ----------- |
| 00 | 프로젝트/모듈 명명 | [`phases/00-naming.md`](phases/00-naming.md) | [`agents/project-namer.md`](agents/project-namer.md) |
| 01 | 의도 추출 | [`phases/01-intent.md`](phases/01-intent.md) | [`agents/intent-extractor.md`](agents/intent-extractor.md) |
| 02 | 의도 문서 리뷰 | [`phases/02-document.md`](phases/02-document.md) | [`agents/doc-reviewer.md`](agents/doc-reviewer.md) |
| 03 | 독립 재이해 (콜드) | [`phases/03-independent-comprehension.md`](phases/03-independent-comprehension.md) | [`agents/independent-comprehender.md`](agents/independent-comprehender.md) |
| 04 | 사용자 질의 | [`phases/04-clarify.md`](phases/04-clarify.md) | [`agents/clarifier.md`](agents/clarifier.md) |
| 05 | 비평·대안 | [`phases/05-critique.md`](phases/05-critique.md) | [`agents/critic.md`](agents/critic.md) |
| 06 | 계획 (TODO 형) | [`phases/06-plan.md`](phases/06-plan.md) | [`agents/planner.md`](agents/planner.md) |
| 07 | 계획 재이해 (콜드) | [`phases/07-plan-recursion.md`](phases/07-plan-recursion.md) | [`agents/plan-reviewer.md`](agents/plan-reviewer.md) |
| 08 | 구현 (모듈별) | [`phases/08-implement.md`](phases/08-implement.md) | [`agents/implementer.md`](agents/implementer.md) |
| 09 | 5종 품질 게이트 | [`phases/09-quality-gates.md`](phases/09-quality-gates.md) | [`agents/quality-gate.md`](agents/quality-gate.md) |
| 10 | 무한 스프린트 루프 | [`phases/10-test-loop.md`](phases/10-test-loop.md) | [`agents/tester.md`](agents/tester.md) |
| 11 | 회귀 바이섹트 | [`phases/11-regression-bisect.md`](phases/11-regression-bisect.md) | [`agents/regression-analyst.md`](agents/regression-analyst.md) |
| 12 | be4fe + bun fe 웹뷰 생성 | [`phases/12-webview-assembly.md`](phases/12-webview-assembly.md) | [`agents/webview-builder.md`](agents/webview-builder.md) |
| 13 | 핸드오프 | [`phases/13-handoff.md`](phases/13-handoff.md) | (없음 — 지휘자 직접) |

## 하드 룰

ⓐ **페이즈 생략 불가.** 불필요해 보여도 실행하고 "발견 없음" 으로 기록 — 5분 단축보다 감사 트레일이 중요하다.
ⓑ **페이즈 03 / 07 은 fresh `Agent` 호출** (컨텍스트 공유 금지). 콜드 리딩이 의도 표류를 잡는 메커니즘이다.
ⓒ **페이즈 04 (사용자 질의)** 는 하드 체크포인트. `AskUserQuestion` 사용. 답을 받지 못하면 정지 — 가정 금지.
ⓓ **모든 사용자 질의는 [`conventions/interview.md`](conventions/interview.md)** 컨벤션을 따른다 (두괄식·1질의·숫자 5개 이하).
ⓔ **모든 페이즈 산출물 헤더에 [`conventions/timing.md`](conventions/timing.md)** 의 시간 정보를 표기한다.
ⓕ **모든 구현 모듈은 목 표면을 노출**해야 한다 — 포트가 없으면 게이트 9 fail.
ⓖ **백엔드와 프론트엔드는 별도 채점.** 한쪽만 단단하면 게이트 10 fail.
ⓗ **점수 ≥ 0.9 까지 무한 반복.** 8회 캡 같은 것 없음. 회귀 트리거 시에만 사용자 ack 로 정지/계속을 결정.
ⓘ **점수 0.05 이상 하락 = 즉시 페이즈 11 발동**, 추가 구현 금지, 사용자 ack 필수. 깊은 DIP 위반의 증상이면 `re-architect` 권고 (모듈을 깨고 페이즈 06 부터 다시).
ⓙ **서브에이전트 산출 파일을 지휘자가 손대지 않는다.** 잘못되면 페이즈 재실행. 편집은 출처를 망친다.
ⓚ **사용자 진행 보고에는 누적 경과 시간 1줄을 항상 포함.**

## 스프린트 루프 (페이즈 10 상세)

```
sprint = 1
prev_score = None
while True:
    suite = run_test_matrix()                                   # BE 단위/통합, FE 단위/통합, E2E
    score, sub = score.py(rubric, suite, prior=prev_score)
    write `sprints/{sprint:02d}/report.md` with timing header
    report_to_user(누적_경과, 스프린트_소요, 현재_시각, 점수)

    if score >= 0.9:
        break

    if prev_score is not None and score < prev_score - 0.05:
        run_phase_11(bisect) → `sprints/{sprint:02d}/bisect.md`
        ack = AskUserQuestion(권고: revert | re-architect | accept)
        if ack == 정지요청: halt

    spawn_implementer(failing_tests + sub_score 약점)
    prev_score = score
    sprint += 1
    # 캡 없음 — 사용자가 정지시키지 않는 한 계속
```

## 호출 시점

ⓐ 다중 모듈 기능 (FE+BE, 서비스+DB).
ⓑ 의도 모호함이 의미 있는 재작업을 부를 만한 작업.
ⓒ SOLID 경계를 건드리는 리팩터.
ⓓ 유비쿼터스 언어가 아직 정착하지 않은 새 도메인.

## 호출하지 말아야 할 시점

ⓐ 한 줄 버그 수정. 그냥 고친다.
ⓑ 리네임·기계적 리팩터.
ⓒ 사용자가 명시적으로 "버릴 코드" 라고 말한 스파이크.

## 함께 보기

ⓐ [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — 신뢰 담보 의미와 패턴 합성 근거.
ⓑ [`scoring/rubric.md`](scoring/rubric.md) — 채점 차원과 가중치.
ⓒ [`conventions/`](conventions/) — 인터뷰·시간 컨벤션.
ⓓ [`templates/`](templates/) — 산출물 템플릿과 웹뷰 스캐폴드.
