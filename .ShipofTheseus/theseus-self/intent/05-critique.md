---
skill_name: theseus-harness
skill_version: 0.2.0
phase: 05-critique
project_id: theseus-self
project_run: 20260501-184946
fingerprint: sha256:8b28c3d8165f5bc6276500fbe62a01fa53c3cb82f52a3465bc447deb42364dfe
prev_fingerprint: sha256:db8710ef8f7b07e9b8601af3c660fb53745bd3bf74b695faa1edb6d97cfa4a16
produced_at: 2026-05-01T18:49:46Z
producer_agent: human-bootstrap
---
> **시작:** 2026-05-01T18:50:30Z · **종료:** 2026-05-01T18:53:00Z · **소요:** 2분 30초
> **누적 경과:** 3분 14초 · **현재 시각:** 2026-05-01T18:53:00Z

# 자체 비평 — 1차

## 한 줄 요약
**본 저장소에는 self_lint 가 잡지 못하는 진짜 약점이 9 개** 있다 — 페이즈 문서의 헤더 시간 메타 누락, 에이전트의 "완료 조건" 일관성 부족, contracts.md 의 frontmatter 가 실제 페이즈 산출물에 강제되지 않음, 경쟁 컨벤션이 페이즈 06/08 에 *언급만* 됨, 모듈 분해 로드맵이 추상에 머무름 등.

## 미스초이스

### M1 — frontmatter 가 컨벤션에만 박혀 있고 *실제 페이즈 산출물 작성 시점에 강제* 되지 않음
[`conventions/contracts.md`](../../../skills/theseus-harness/conventions/contracts.md) 가 frontmatter 표준을 정의하지만, 페이즈 01–13 문서나 에이전트 프롬프트에 **"산출물 작성 시 fingerprint.py compute 를 호출하라"** 가 명시되지 않음. 결과: 사용자가 본 하네스를 돌려도 frontmatter 가 빠진 산출물이 나올 가능성. 게이트 9 가 그것을 잡아도 *예방* 이 아닌 *사후 발견*.

### M2 — 페이즈 문서 헤더의 시간 메타가 본 저장소 내부에는 없음
[`conventions/timing.md`](../../../skills/theseus-harness/conventions/timing.md) 가 모든 산출물 헤더에 시간 메타를 강제하지만, *본 저장소의* phase/agent/convention 문서는 그 자체가 산출물이 아니라 *명세* 이므로 시간 메타가 없다. 일관된 정책이 없어 사용자가 헷갈릴 여지. 명세 문서 vs 실행 산출물의 분리가 어디서도 명시 안 됨.

### M3 — 경쟁 컨벤션(competition.md)이 phases/06, 08, 11 안에 *적용 룰* 로 박히지 않음
[`competition.md`](../../../skills/theseus-harness/conventions/competition.md) 가 v0.2.0 에서 추가됐지만, 페이즈 06/08/11 문서 본문에는 "경쟁 모드 트리거 조건" 이 명시되지 않음. 결과: 메인 에이전트가 페이즈 06 진행 중 *애매함이 보였을 때 경쟁을 띄울 의무* 를 잊을 수 있음.

## 범위 위험

### S1 — 모듈 분해 로드맵이 SKILL.md 끝에 *권고* 로만 있음
"`skills/theseus-orchestrator` + `skills/theseus-{naming,intent,plan,...}`" 분해가 후속 PR 후보로만 적혀 있고, 그 이행을 강제하는 lint 또는 test 가 없음. v0.3.0 에서 슬그머니 잊힐 위험.

### S2 — 자기 평가 회차 점수의 시계열 보존 메커니즘 부재
`.ShipofTheseus/theseus-self/sprints/` 가 비어있고, 회차 누적을 어떻게 할지 명시가 없음. 매 회차가 독립적이면 *향상되는지* 측정 불가.

## 재사용 가능한 기존 해법

### R1 — fingerprint.py 의 compute 명령이 이미 in-place 로 frontmatter 갱신
구현자/clarifier 에이전트가 산출물 작성 직후 `fingerprint.py compute --file <path> --prev <prev>` 를 *반드시* 호출하도록 에이전트 프롬프트에 박으면 M1 해소.

### R2 — self_lint.py 가 11 체크에서 끝났으나 확장 가능
phase 문서 시간 메타, agent "완료 조건", competition 적용 룰 박힘 여부 모두 self_lint 의 새 체크로 추가 가능. 비용 거의 없음.

## 대안 접근

### 대안 A — 보강만, 분해 안 함 (보수)
v0.3.0 에서 self_lint 확장 + frontmatter 강제 + 경쟁 룰 phase 박힘만 처리. 모듈 분해는 v1.0.0 까지 보류.
**트레이드오프:** 본 PR 직후 사용자 가치 확실, 분해 가능성 늦어짐.

### 대안 B — 모듈 분해 우선 (적극)
v0.3.0 에서 `skills/theseus-{orchestrator,intent,plan,...}` 분해를 먼저 하고, frontmatter 강제는 분해 후 자연스럽게.
**트레이드오프:** 분해는 큰 작업, 회귀 위험. 한 번에 다하면 PR 비대화.

## 추천 경로
**대안 A** — 본 1차 자체 평가의 부트스트래핑 가치는 보강에서 더 크다. 분해는 자기 평가 회차 2~3회 누적 후 v0.3 또는 v0.4 에서 별도 PR.

## 사용자(메인테이너) 결정이 필요한 트레이드오프
- **CI 강제 수준** — `self-check.sh` 실패 시 PR 자동 차단? 또는 경고만? 1번/2번/3번/4번 보기로.
- **자기 평가 회차 주기** — 매 PR / 매 minor 릴리스 / 매 major 릴리스 / 수동 트리거.
- **분해 시점** — v0.3 / v0.4 / v1.0 / 무기한 보류.

## 추가 발견 — self_lint 가 잡았어야 했지만 못 잡은 9 개

| # | 발견 | 검출 가능성 |
| - | --- | ---------- |
| 1 | phases/06-plan.md 가 시퀀스 다이어그램을 *동봉* 의무로 명시 안 함 — diagrams.md 만 의존 | self_lint C12 추가 가능 |
| 2 | phases/08-implement.md 가 build-and-config.md 의 sh+bat 강제를 본문에 안 박음 | self_lint C13 추가 가능 |
| 3 | quality-gate.md 가 frontmatter 누락을 자동 fail 하라는 룰을 본문에 안 박음 | self_lint C14 추가 가능 |
| 4 | regression-analyst.md 가 경쟁 컨벤션 사용 가능성을 언급 안 함 | self_lint C15 추가 가능 |
| 5 | conventions/competition.md 가 critic 또는 plan-reviewer 에이전트의 트리거 책임을 명시 안 함 | self_lint C16 추가 가능 |
| 6 | webview 스캐폴드의 Mermaid 렌더가 README 에만 권고 — server.ts 가 자동 렌더 미지원 | webview-builder.md 보강 필요 |
| 7 | fingerprint.py 가 frontmatter 의 producer_agent 를 검증 안 함 | fingerprint.py 확장 가능 |
| 8 | sample-inputs.json 이 dip_violation=false 만 보여줌 — true 케이스 샘플 없음 | sample-inputs-dip.json 추가 가능 |
| 9 | INSTALL.md 가 BOOTSTRAP.md 와 self-check 절차를 언급 안 함 | INSTALL 보강 필요 |
