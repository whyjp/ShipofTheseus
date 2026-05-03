---
name: theseus-harness
version: 0.7.1
description: 다중 모듈/FE+BE/도메인 미정착 기능을 위한 재귀 멀티 에이전트 코딩 하네스. 14 페이즈 + 27 컨벤션 + 13 에이전트 + 부트스트래핑 자기 평가. 객관식 보기 4개 이하 (질문 수 무한). 한 줄 수정 같은 사소한 작업에는 사용 금지.
---

# 테세우스 하네스

## 한 줄 요약
**한 요구를 처음 의도한 타이틀로 끝까지 부를 자격을 만들기 위한 재귀 코딩 하네스.** 당신(메인 에이전트)은 *지휘자* — 직접 작업하지 않고, 페이즈마다 정해진 서브 에이전트를 띄워 산출물을 받아 다음 페이즈로 넘긴다. 본 SKILL.md 는 *인덱스* 다 — 상세는 컨벤션·페이즈·에이전트 문서로 위임.

## 가장 먼저 읽을 것 (모두 라이트하게 분리됨)

a- 설계 철학과 도자기 장인 비유: [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md)
b- 사용자 질의 형식: [`conventions/interview.md`](conventions/interview.md)
c- 산출물 헤더 시간 표기: [`conventions/timing.md`](conventions/timing.md)
d- 마인드맵 → 유즈케이스 → 시퀀스 진화: [`conventions/diagrams.md`](conventions/diagrams.md)
e- 언어/컴파일러/패키지 매니저 점검: [`conventions/stack.md`](conventions/stack.md)
f- 빌드 스크립트 / TOML / docs/ / 폐기 / 병렬·메모리: [`conventions/build-and-config.md`](conventions/build-and-config.md)
g- **단계별 의존성 분리·핑거프린트·재진입**: [`conventions/contracts.md`](conventions/contracts.md)
h- **에이전트 역할별 모델(Opus/Sonnet/Haiku) 매핑**: [`conventions/models.md`](conventions/models.md)
i- **2버전 이상 격리 병렬 경쟁 + 머지 (LLM 비결정성 극복)**: [`conventions/competition.md`](conventions/competition.md)
j- **무한 재귀 정체 극복 — 레슨 전달 + 강제 재작성**: [`conventions/lessons.md`](conventions/lessons.md)
k- **도메인별 NFR 자동 제안 카탈로그 (성능·가용성·보안·운영·FE)**: [`conventions/spec-catalog.md`](conventions/spec-catalog.md)
l- **리소스 기반 임계 + 천정 자동 조정 (로컬/K8s/EC2 프로파일)**: [`conventions/resources.md`](conventions/resources.md)
m- **체크포인트 + 멀티버스 (닥터 스트레인지 메타포)**: [`conventions/checkpoints.md`](conventions/checkpoints.md)
n- **테스트 목적 보호 — 불변 조건 + Phase V 측정 유효성**: [`conventions/test-invariants.md`](conventions/test-invariants.md)
o- **Da Capo 루프 (AIDE × LLM Wiki 결합 — 자기 강화 회귀)**: [`conventions/dacapo.md`](conventions/dacapo.md)
p- **파편화 우선 설계 (단일 헤비 스킬 금지)**: [`conventions/fragmentation.md`](conventions/fragmentation.md)
q- **그레이드 시스템 — 작업 복잡도별 내부 모듈레이션 (G1 TBD ~ G5 빡빡 모드)**: [`conventions/grades.md`](conventions/grades.md)
r- **모듈 → 하위 모듈 서브에이전트 재귀 분해 (parallel/sequential/competition)**: [`conventions/sub-agents.md`](conventions/sub-agents.md)
s- **산출물 = DB / 비직렬성 트리 인덱싱 (INDEX.md 자동 갱신)**: [`conventions/indexing.md`](conventions/indexing.md)
t- **리줌 — state.json + 재개 진입점 + FE 라이브 진행 추적**: [`conventions/resume.md`](conventions/resume.md)
u- **AIDE 플랜 트리 — N 우주 격리 + 토너먼트 (회귀+병렬 강점 인코딩)**: [`conventions/plan-tree.md`](conventions/plan-tree.md)
v- **런타임 사전조건 — Q-D9 + 게이트 7 (코드-실행가능 까지 담보)**: [`conventions/runtime-prereq.md`](conventions/runtime-prereq.md)
## 산출물 트리

```
.ShipofTheseus/<프로젝트명>/
├── timing/start.json
├── naming/{00-candidates.md, 00-naming.md}
├── intent/{01-intent.md, 02-..05-decisions.md, 04-stack.md, 04-verification.md, 04-runtime-prereq.md}
├── plan/{06-plan.md, 07-plan-review.md, tournament.md, candidates/universe-N/...}  # G3+ AIDE 트리
├── impl/08-impl-log.md
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, unit.json, e2e.json}
├── webview/                     # bun + hono + react
└── handoff/13-handoff.md
```

## 페이즈 (14)

각 페이즈 산출물은 [`conventions/contracts.md`](conventions/contracts.md) 의 frontmatter (skill_name, skill_version, phase, project_id, fingerprint, prev_fingerprint, produced_at) 를 포함한다.

| # | 페이즈 | 모델 | 페이즈 문서 | 서브에이전트 | 산출 위치 |
| - | ----- | ---- | --------- | ----------- | -------- |
| 00 | 프로젝트/모듈 명명 | Haiku | [`phases/00-naming.md`](phases/00-naming.md) | [`agents/project-namer.md`](agents/project-namer.md) | `naming/` |
| 01 | 의도 + 마인드맵 | **Opus** | [`phases/01-intent.md`](phases/01-intent.md) | [`agents/intent-extractor.md`](agents/intent-extractor.md) | `intent/01-intent.md` |
| 02 | 의도 문서 리뷰 | Sonnet | [`phases/02-document.md`](phases/02-document.md) | [`agents/doc-reviewer.md`](agents/doc-reviewer.md) | `intent/02-intent-review.md` |
| 03 | 독립 재이해 (콜드) | Sonnet | [`phases/03-independent-comprehension.md`](phases/03-independent-comprehension.md) | [`agents/independent-comprehender.md`](agents/independent-comprehender.md) | `intent/03-comprehension.md` |
| 04 | 사용자 질의 + 유즈케이스 + 스택 점검 + 회귀짝 | Sonnet | [`phases/04-clarify.md`](phases/04-clarify.md) | [`agents/clarifier.md`](agents/clarifier.md) | `intent/04-*.md` |
| 05 | 비평·대안 | **Opus** | [`phases/05-critique.md`](phases/05-critique.md) | [`agents/critic.md`](agents/critic.md) | `intent/05-*.md` |
| 06 | 계획 + 시퀀스 | **Opus** | [`phases/06-plan.md`](phases/06-plan.md) | [`agents/planner.md`](agents/planner.md) | `plan/06-plan.md` |
| 07 | 계획 재이해 | Sonnet | [`phases/07-plan-recursion.md`](phases/07-plan-recursion.md) | [`agents/plan-reviewer.md`](agents/plan-reviewer.md) | `plan/07-plan-review.md` |
| 08 | 구현 + 빌드 스크립트 + TOML | Sonnet (필요 시 Opus) | [`phases/08-implement.md`](phases/08-implement.md) | [`agents/implementer.md`](agents/implementer.md) | `impl/08-impl-log.md` |
| 09 | 5종 게이트 (DIP 우선) | Sonnet | [`phases/09-quality-gates.md`](phases/09-quality-gates.md) | [`agents/quality-gate.md`](agents/quality-gate.md) | `quality/09-quality-gate.md` |
| 10 | 무한 스프린트 (임계 0.999) | Haiku | [`phases/10-test-loop.md`](phases/10-test-loop.md) | [`agents/tester.md`](agents/tester.md) | `sprints/NN/` |
| 11 | 회귀 바이섹트 | **Opus** | [`phases/11-regression-bisect.md`](phases/11-regression-bisect.md) | [`agents/regression-analyst.md`](agents/regression-analyst.md) | `sprints/NN/bisect.md` |
| 12 | be4fe + bun fe 웹뷰 | Sonnet | [`phases/12-webview-assembly.md`](phases/12-webview-assembly.md) | [`agents/webview-builder.md`](agents/webview-builder.md) | `webview/` |
| 13 | 핸드오프 | (지휘자) | [`phases/13-handoff.md`](phases/13-handoff.md) | (없음) | `handoff/13-handoff.md` |

## 단계별 진입 (재진입 / 부분 호출)

본 하네스는 처음부터 끝까지 한 호출에 다 도는 게 *기본 모드* 이지만, **각 페이즈 산출물이 다음 페이즈의 입력 계약** 이므로 외부 호출자가 특정 페이즈 산출물을 들고 와서 그 *다음 페이즈부터* 진입할 수 있다.

진입 규칙:

a- 호출 시 사용자가 `.ShipofTheseus/<프로젝트>/` 디렉터리(또는 그 일부 산출물 묶음) 를 가리키면, 지휘자는 그 산출물들의 frontmatter 를 검사한다.
b- 각 산출물은 `skill_name == "theseus-harness"`, `skill_version` 호환 (semver: 같은 major), `fingerprint` 일관성을 가져야 한다.
c- 가장 늦은 페이즈 N 의 산출물이 valid 면, 페이즈 N+1 부터 진입.
d- 호환되지 않는 버전이거나 핑거프린트가 깨진 산출물은 거부 — 사용자에게 객관식 질의 (재실행 / 무시 / 디버깅).

자세한 frontmatter 스키마와 핑거프린트 계산은 [`conventions/contracts.md`](conventions/contracts.md).

## 자기 평가 (부트스트래핑)

본 하네스는 자기 자신에게 자기의 평가 절차를 적용한다 — 우로보로스의 진짜 발현. 자세한 절차는 [`../../BOOTSTRAP.md`](../../BOOTSTRAP.md). 핵심:

a- **임계 0.99999** — 자기 표준은 사용자 프로젝트 임계 0.999 보다 한 단계 빡빡.
b- **`scoring/self_lint.py`** — 35 체크로 컨벤션·교차 링크·버전·frontmatter·경쟁 룰·인코딩 비호환 가드 객관 측정. `--score` 모드.
c- **`scripts/self-check.{sh,bat}`** — lint + 16 pytest + sample + self_score + 핑거프린트 체인 일괄.
d- **회차 누적** — `.ShipofTheseus/theseus-self/sprints/NN/` 점수 시계열로 본 하네스가 더 단단해지는지 객관 측정.

## 자율성 우선 (초기 인터뷰 후 사용자 액션 최소화)

[`conventions/autonomy.md`](conventions/autonomy.md) 에 따라 **페이즈 04 (초기 사용자 질의) 이후에는 가능한 모든 결정을 에이전트가 자율 진행**. 사용자 액션이 *반드시* 필요한 곳은 다음 셋만:

a- 페이즈 04 의 객관식 답 (필수, 침묵 = 정지).
b- 회귀 바이섹트의 권고 ack (사용자가 사전 위임 시 자율).
c- 자율 시스템 업데이트 (스택 점검) — 사전 동의 시 자율.

그 외는 모두 자율, 모든 결정이 산출물에 frontmatter + 본문으로 기록되어 사후 리뷰 가능. 경쟁(competition) 의 머지/우승자 결정도 [`conventions/competition.md`](conventions/competition.md) 의 자동 resolve 알고리즘으로 점수 차 + 차원별 sub-score 비교로 자율 결정.

## 모듈 분해 — 진행 완료 (v0.2.0)

✅ 8 분해 stub 신규 (`skills/theseus-{orchestrator,intent,plan,implement,quality,sprint,webview,handoff}/SKILL.md`).
✅ 단일 source of truth 유지 — 콘텐츠는 본 디렉터리에. stub 은 형태와 인터페이스만.
✅ [`../theseus-orchestrator/SKILL.md`](../theseus-orchestrator/SKILL.md) — **공식 메인 체이닝 진입점**. 8 분해 스킬을 frontmatter 자동 핸드오프로 순차 호출.
✅ 연동 테스트 — [`scoring/test_skill_handoff.py`](scoring/test_skill_handoff.py) 10 케이스 (stub 존재 / source 참조 / 룰 본문 비복제 / fingerprint 체인 / tamper 거부 / 두 진입점 관계).
✅ self_lint C28 — 분해 무결성 매 PR 검증.

본 단계에서는 *형태와 인터페이스* 정착. 실제 콘텐츠 이동(각 stub 안에 자기 페이즈/에이전트 파일 두기) 은 v0.4.0 후보.

본 하네스의 SoC/DIP 철학을 본 하네스 자신에게 적용한 결과:

a- `skills/theseus-orchestrator/` — 인덱스 + 14 페이즈 진행 제어만.
b- `skills/theseus-intent/` — 페이즈 00–05 (명명, 의도, 리뷰, 재이해, 질의, 비평).
c- `skills/theseus-plan/` — 페이즈 06–07 (계획, 재이해).
d- `skills/theseus-implement/` — 페이즈 08 (구현).
e- `skills/theseus-quality/` — 페이즈 09 + 채점 rubric.
f- `skills/theseus-sprint/` — 페이즈 10–11 (스프린트 루프, 회귀 바이섹트).
g- `skills/theseus-webview/` — 페이즈 12.
h- `skills/theseus-handoff/` — 페이즈 13.
i- 공유 자원: 저장소 루트의 `core/{conventions,scoring,templates,agents}` — 모든 스킬이 상대 경로 참조.

각 스킬이 [`conventions/contracts.md`](conventions/contracts.md) 의 frontmatter 계약만 지키면 독립 호출·교체 가능. 본 PR 은 분해 *가능성을 만든* 단계 — 실제 분해는 후속.

<!-- HARD-RULE: 본 절의 a-~l- 항목은 본 하네스 호출 시 *예외 없이* 적용. 위반은 즉시 게이트 fail. -->

## 하드 룰 (요약)

a- 페이즈 생략 불가. 불필요해 보여도 실행하고 "발견 없음" 으로 기록.
b- 페이즈 03/07 은 *fresh* `Agent` 호출 — 컨텍스트 공유 금지.
c- 페이즈 04 는 *유일한* 사용자 인터럽트 지점. 사전 위임 카탈로그(Q-D1~D6) 답 누락 시 페이즈 05 진입 불가. **페이즈 05~13 동안 사용자 인터럽트 절대 없음** — 모든 ack 는 페이즈 04 답 자동 매핑 ([`conventions/autonomy.md`](conventions/autonomy.md)).
d- **임계 점수 0.999** — 임계 미달 시 무한 스프린트, 캡 없음. 회귀 시에만 사용자 ack.
e- **DIP 가 SOLID 중 최우선** — 위반 단독 hard cap 0.6.
e-1 **깨고 다시 빚기 트리거 = 모든 깊은 품질 위반** — DIP 위반만이 아니라 1- 코드 오류 누적 2- 기획-구현 갭 (스펙 누락) 3- 성능/NFR 미달 4- 의도 표류 5- 정체/회귀 누적 중 *어느 차원* 이라도 깊이가 임계를 넘으면 부분 수정 금지 → 페이즈 06 부터 통째 재빚기 (`re-architect`). 차원별 트리거·매핑은 [`conventions/lessons.md`](conventions/lessons.md) + [`conventions/checkpoints.md`](conventions/checkpoints.md).
f- 백엔드 기본 Go, FE 기본 bun + React + TS.
g- 모든 모듈은 sh + bat 스크립트, TOML 설정 + `.example` 동행, `docs/` 폴더.
h- 수정·리팩터링 시 기존 코드 폐기 우선. 라이브 전 중간 산출물 보존.
i- 병렬 서브에이전트 환영 — RAM 50% / 동시 E2E 2개 / 같은 파일 직렬 가드.
i-1 페이즈 06/08/11 에서 명확한 단일안이 보이지 않으면 **2~3 후보 격리 병렬 경쟁** → 점수 비교 → 우승자 또는 머지 ([`conventions/competition.md`](conventions/competition.md)). LLM 비결정성을 분기·경쟁·합병으로 정공법 극복. **resolve 는 점수 차/차원별 분석으로 자율 결정** — 사용자 ack 는 비즈니스 함의가 명시된 경쟁만.
i-2 **자율성 우선** — 페이즈 04 (초기 사용자 질의) 이외의 모든 결정은 자율 진행 ([`conventions/autonomy.md`](conventions/autonomy.md)). 모든 자율 결정은 산출물 frontmatter + 본문 기록 → 사후 리뷰 가능.
j- 사용자 진행 보고에 누적 경과 시간 1줄 항상 포함.
k- **모든 산출물에 frontmatter (skill_name, skill_version, phase, project_id, fingerprint, prev_fingerprint, produced_at) 필수.**
l- 페이즈 산출 파일을 지휘자가 손대지 않는다 — 잘못되면 페이즈 재실행.

## 호출 그레이드 — [`conventions/grades.md`](conventions/grades.md) 의 허들

**호출 직후 첫 동작 = `scoring/grade_assess.py` 자동 추정 + 페이즈 04 의 Q-G1 객관식 확정.** 그레이드별 페이즈/컨벤션 활성화로 단순 작업 over-engineering 차단.

| Grade | 호출 시점 | 본 하네스 동작 |
| ----- | -------- | ------------ |
| **Grade 1** Trivial | 한 줄 수정 / 리네임 / typo / throwaway | **TBD (v0.5.x 후속 정의)** |
| **Grade 2** Simple | 단일 모듈 작은 기능 (~100 LOC) | 미니 (5 페이즈 / 7 컨벤션 / 임계 0.95) |
| **Grade 3** Standard | 다중 모듈 단일 사이드 | 12 페이즈 / 12 컨벤션 / 임계 0.97 |
| **Grade 4** Complex | FE+BE / 새 도메인 / SOLID 리팩터 (default) | 14 페이즈 풀 / 26 컨벤션 / 임계 0.999 |
| **Grade 5** Mission Critical | 결제 / 금융 / 안전 시스템 | 14 풀 + 빡빡 모드 / 임계 0.99999 |

## 안티 패턴 통합 카탈로그 (v0.4.0 — 중복 제거)

페이즈별 "흔한 실패" 절에 분산되어 있던 *공통 안티 패턴* 을 본 절로 통합. 페이즈별 본문에는 *해당 페이즈 고유* 의 실패만 잔존. (superpowers Red Flags 패턴 차용 — 단, 합성 아닌 *내부 중복 제거*. 거울 원칙 정합.)

### A. 설계 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A1 | 조기 추상화 — 단일 사용처에서 *재사용 가능성* 가정 | 06 (계획), 08 (구현) | 사용처 ≥ 2 까지 인라인 유지 |
| A2 | 분산 모놀리스 — 모듈 간 강한 결합 (DIP 위반) | 08 (구현) | 어댑터 분리, 포트 인터페이스 |
| A3 | Sync-where-async — 비동기 도메인에 동기 인터페이스 강제 | 08 (구현) | 큐 / 이벤트 / async 채택 |
| A4 | 자체 인증 / 자체 직렬화 — 표준 라이브러리 회피 | 08 (구현) | oauth2, json, 검증된 SDK |

### B. 인터뷰 / 산출물 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A5 | 두괄식 누락 — 첫 줄 한 줄 요약 없음 | 04 (인터뷰), 모든 산출물 | [`conventions/interview.md`](conventions/interview.md) 의 두괄식 룰 강제 |
| A6 | 객관식 알파벳 라벨 (a/b/c) | 04 (인터뷰) | 숫자 1~5 만 |
| A7 | frontmatter 누락 | 모든 산출물 | quality-gate 자동 fail (C14) |
| A8 | 페이즈 생략 | 모든 페이즈 | "발견 없음" 으로 기록 의무 |

### C. 자율성 안티 패턴

| ID | 안티 패턴 | 트리거 페이즈 | 대안 |
|--|--|--|--|
| A9 | 페이즈 04 외 사용자 ack 호출 | 05~13 | [`conventions/autonomy.md`](conventions/autonomy.md) C23 |
| A10 | 자율 결정의 침묵 (라이브 보고 누락) | 05~13 | [`conventions/timing.md`](conventions/timing.md) 라이브 보고 |

페이즈별 *고유* 안티 패턴은 [`phases/`](phases/) 본문에 잔존 — 본 카탈로그는 *공통* 만. self_lint C40 가 통합 정합 검증.
