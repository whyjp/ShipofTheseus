# Phase 00 — 프로젝트/모듈 명명

## 한 줄 요약
**나머지 모든 산출물의 폴더와 식별자가 결정되는 첫 페이즈** — 프로젝트명과 1차 모듈명을 사용자와 함께 확정한다. 의도가 명확하고 다른 의미와 충돌하지 않는 단어만 채택.

## 입력
- 사용자의 원본 요청 (현재 대화의 첫 메시지).
- 현재 레포의 `README.md` 와 명명 충돌 가능성이 있는 디렉터리 목록.

## 동작 (지휘자)

0- **(sprint-36 신규) pre-cold-session bootup** — phase 00 enter *직전* `python skills/theseus-harness/scoring/pre_bootup.py bootstrap --root .ShipofTheseus/<프로젝트명_가확정>` 호출. 3 viewer (lineage / webview / interactive) shell 복사 + 빈 골격 JSON emit + viewer-runtime HTTP server 시작. 사용자에게 viewer URL 출력. 이때부터 cold session 진행이 5초 polling 으로 자동 viewer 반영. [`../conventions/pre-cold-session-bootup.md`](../conventions/pre-cold-session-bootup.md) 정합.
1- 시간 기록 시작 — `.ShipofTheseus/__pending/timing/start.json` 임시 작성 (프로젝트명 확정 후 실제 폴더로 이동).
2- `Agent(subagent_type="general-purpose")` 에 [`../agents/project-namer.md`](../agents/project-namer.md) 프롬프트로 호출 — 후보 3~5 개 생성.
3- 후보 산출물을 받아 `.ShipofTheseus/__pending/naming/00-candidates.md` 로 기록.
4- `AskUserQuestion` 으로 사용자에게 객관식 질의 — [`../conventions/interview.md`](../conventions/interview.md) 컨벤션 준수.
5- 사용자 답을 받아 프로젝트명 확정. 폴더를 `.ShipofTheseus/<프로젝트명>/` 으로 rename, `start.json` 이동.
6- 같은 절차로 1차 모듈명 (be4fe / fe / 그 외) 확정 — 단, 모듈명은 한 번에 묶어 최대 5개 제시.
7- 최종 결과를 `naming/00-naming.md` 로 작성.

## 산출물

`naming/00-candidates.md` — 후보별 의미·기원·다른 의미와의 충돌 여부.
`naming/00-naming.md` — 확정 프로젝트명·모듈명·각 이름의 정당화 한 줄.

## 성공 기준

a- 프로젝트명·모듈명 모두 사용자 명시 선택.
b- 두 이름 다 폴더/패키지/도메인 식별자로 즉시 사용 가능 (소문자·하이픈/언더스코어, 영숫자).
c- 후보 검토에 "충돌 검사" 칸이 비어 있지 않다 — 빈 칸은 검토 누락.

## 사용자 질의 형식 예 (잘못 만들면 reject)

```
질의: 프로젝트명을 골라주세요.

세 후보 모두 의미상 충돌이 없습니다. 단, 3 번은 GitHub에 동명 저장소가 있어 검색 시 혼동 가능성이 약간 있습니다.

선택지:
1. atlas-ledger (지도/원장 — 결제 도메인과 잘 맞음)
2. orpheus-flow (전달/흐름 — 메시지 파이프라인 함의)
3. lattice-store (격자/저장 — 분산 캐시 함의, 동명 OSS 존재)
4. 모두 마음에 들지 않음 (다시 후보 생성)
```

## 흔한 실패

a- 사용자 답 없이 추정으로 진행 — 이후 모든 폴더가 잘못된 이름. 절대 금지.
b- 모듈명을 페이즈 06 (계획) 까지 미루기 — 그러면 06 이전 산출물 폴더가 임시명으로 떠돈다. 여기서 끝낸다.
c- "shipoftheseus" 같이 저장소명을 그대로 차용 — 의도 명확성 부족. 새 단어로.

> **공통 안티 패턴** (조기 추상화 / 분산 모놀리스 / 두괄식 누락 / 객관식 라벨 등) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.
