# Phase 04 — 사용자 질의

## 한 줄 요약
**의도 문서의 모호함을 사용자와 직접 해소하는 유일한 페이즈.** [`../conventions/interview.md`](../conventions/interview.md) 컨벤션을 예외 없이 따른다 — 두괄식·1회 1질의·객관식 *보기* 4개 이하 (`AskUserQuestion` 옵션 한도). **누적 질문 *수* 는 무한** — 4 는 옵션 수 한도지 질문 갯수 한도가 아니다 (의도 모호하면 자유롭게 추가 질의).

## 입력
- `intent/01-intent.md`
- `intent/03-comprehension.md` (재이해에서 표류한 지점)

## 서브에이전트
[`../agents/clarifier.md`](../agents/clarifier.md). 이 에이전트는 *질의 목록만 작성* 한다 — 사용자에게 직접 묻지 않음. 묻는 사람은 지휘자.

## 산출물

a- `intent/04-questions.md` — 질의 리스트. 각 항목: 질문 텍스트, 왜 중요한지, 보기 후보(객관식이면).
b- `intent/04-answers.md` — 사용자 답을 시각과 함께 기록.
c- `intent/04-resource-profile.md` — 리소스 프로파일 합의 + 추정 천정. [`../conventions/resources.md`](../conventions/resources.md).
d- `intent/04-stack.md` — 언어/컴파일러/패키지 매니저 합의. [`../conventions/stack.md`](../conventions/stack.md).
e- NFR 임계 확정값은 `intent/01-intent.md` 의 "성능/스펙" 표를 in-place 갱신 (`proposed: true` → 사용자 답).
f- `intent/04-autonomy.md` — [`../conventions/autonomy.md`](../conventions/autonomy.md) 의 사전 위임 카탈로그 Q-D1 ~ Q-D9 답 9 줄. **이게 페이즈 05 진입 조건** — 답이 빠지면 페이즈 05 시작 불가.
g- `intent/04-verification.md` — Q-D8 답에 따른 *외부 완료 검증* 산출물 (oh-my-ralph Verification Commands 패턴). bash 검증 스니펫 + acceptance criteria `[SC-N]` 매핑 + 선택적 manual 절차. **답이 1/2 면 `Verification Commands` 블록 비어있으면 페이즈 05 진입 거부**, 답이 3 (`manual_only: true`) 이면 페이즈 09 게이트의 `e2e_pass` 차원 cap 0.95 + 핸드오프 경고.
h- `intent/04-runtime-prereq.md` — Q-D9 답에 따른 *실행 가능 사전조건* 산출물 ([`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md), v0.7.0). env / API key / 외부 서비스 분류 + `.env.template` (답 1·2) 또는 mock/none 모드 선언 (답 3·4). **답 1·2 인데 `.env.template` 비어있으면 `entry_blocked: true`** — 페이즈 09 게이트 7 (env-satisfied + 실 실행 1회) 가 본 답을 입력으로 부팅 검증.

## 지휘자 동작 (강제)

각 질문마다:

1- 두괄식 한 줄 요약을 먼저 출력.
2- 다음 문단에 배경·트레이드오프.
3- 객관식이면 숫자 보기 4개 이하 — `AskUserQuestion` 의 `options` 배열에 라벨 `"1"` … `"4"` (도구 한도). 5번째 옵션이 필요하면 별도 자유 응답 후속으로 분리.
4- 자유 응답이 본질이면 도구 없이 평문으로 질의.
5- 답을 받기 전에는 다음 질문으로 넘어가지 않는다 — 사용자가 답할 때까지 다른 페이즈 호출 금지.
6- **질문 *수* 는 한도 없음** — 4 는 *한 질문의 옵션 수* 한도. 페이즈 04 의 NFR 항목별 / Q-G1 / Q-D1~D8 / 의도 모호 해소 / 회귀 짝까지 누적 *수십 질문* 이 정상. 사용자가 *질문 적게 만들려고* 의도 추출을 단축 금지 ([`../conventions/interview.md`](../conventions/interview.md) §3 정합).

## NFR-derived 후속 질의 ([`../conventions/nfr-derivation.md`](../conventions/nfr-derivation.md), v0.9.6)

**페이즈 01 의 §i "Derived NFRs" 의 각 항목마다 후속 질의 1건.** 사용자 답으로 verification method 와 fail 처리 정책 (auto-fix vs truthful record) 확정. NFR 갯수만큼 질의 수 증가 — [`../conventions/interview.md`](../conventions/interview.md) §3 의 *옵션 4 한도 ≠ 질문 갯수 한도* 룰 정합.

각 NFR 후속 질의 (Q-N{nfr_id}-V) 는 페이즈 04 의 *Q-G1 + Q-D1~D9 사이* 위치 — 사전 위임 (Q-D1~D9) 이 *전체 자율 정책*, NFR-V 는 *NFR 별 verification 정책*.

```
질의 (Q-N2-V, NFR=Q2 reproducibility):
재현 가능성 검증 방법은?

자동 추정 : 옵션 2 (byte-hash SHA256 매치)
선택지:
1. seed 로그 + per-rep RNG 분리
2. byte-hash SHA256 매치 across 2회 실행  ← 자동 추정
3. pinned dep version + lockfile 봉인
4. N/A — 본 NFR 은 본 작업에선 비활성
```

답을 `intent/04-nfr-verifications.md` (NFR 갯수만큼 행) 에 기록 → 페이즈 09 의 derived gate 생성 입력.

페이즈 01 의 §i 가 "functional-only" 면 본 절 skip — derived 질의 0.

## 첫 질의 — Q-G1 그레이드 확정 ([`../conventions/grades.md`](../conventions/grades.md))

본 페이즈의 **가장 첫 질의**. `scoring/grade_assess.py` 가 페이즈 01 의 `intent/01-grade-signals.json` + `intent/01-mindmap-signals.json` (페이즈 01 §j) 을 입력으로 그레이드 추정 — **default = G4** (v0.9.17 sprint-11, 키워드 매칭 폐기). 두괄식으로 추정 결과 (escalation triggers 매칭 / 단순함 증명 차원) 를 보여주고 5 보기 객관식으로 사용자 확정. Grade 1 (Trivial) 답이어도 본 하네스 진행 (그레이드는 내부 모듈레이션만).

**Q-G1 의 두괄식 본문**:
- *추정 grade + reason* (default G4 / G3 단순 증명 / G5 mission-critical 등)
- *escalation triggers 매칭 list* (external evaluator / measured value / multi-scenario / domain adapter / FE+BE)
- *단순함 증명 차원* (G3 추정 시 — 12 차원 중 satisfied list)
- *G3·G2 하향 선택 시 사용자 ack 의무 명시* — "G3 작업은 본 하네스 없이도 진행 가능, 부분만 가치"

## PRD 입력 처리 — 인터뷰 스킵 금지 ([`../conventions/interview.md`](../conventions/interview.md) "PRD/스펙 입력 처리" 절)

사용자가 PRD/스펙 문서를 첨부했어도 본 페이즈의 *모든 인터뷰 항목* 은 생략 안 됨. PRD 추출값은 객관식의 1번 보기로 제안되고, 사용자가 빠르게 1 클릭 확정. 각 답에 `user_explicit_confirmation: true` + `confirmed_at` timestamp 필수. self_lint C33 이 누락된 항목 자동 검출 → 페이즈 05 진입 거부.

## 사전 위임 카탈로그 (페이즈 04 의 마지막 9 질의)

본 페이즈가 *유일한* 사용자 인터럽트 지점이므로, 후속 페이즈(05~13) 의 모든 자율 결정 정책을 *여기서* 한 번에 결정한다. [`../conventions/autonomy.md`](../conventions/autonomy.md) 의 Q-D1 ~ Q-D9 9 질의를 Q-G1 + 일반 질의 *뒤에* 차례로 진행:

a- Q-D1 — 회귀 권고 자동 적용 정책 (페이즈 11)
b- Q-D2 — 경쟁 resolve 자동 적용 정책 (competition.md)
c- Q-D3 — 천정 도달 시 자동 임계 조정 정책 (resources.md)
d- Q-D4 — 정체 누적 시 정책 (lessons.md)
e- Q-D5 — 자율 패키지 업데이트 정책 (stack.md)
f- Q-D6 — 자율 결정 보고 빈도
g- Q-D7 — 체크포인트 회귀 + 멀티버스 정책 (checkpoints.md)
h- **Q-D8 — Verification Commands** (oh-my-ralph 차용, v0.3.0). 사용자가 *외부 완료 검증* 명령을 제시해야 페이즈 05 진입. 답이 1/2 면 `intent/04-verification.md` 의 bash 블록 채움, 답이 3 (`manual_only: true`) 이면 페이즈 09 의 `e2e_pass` 차원 cap 0.95 + 핸드오프 경고.
i- **Q-D9 — Runtime Prerequisite** (v0.7.0 신규, [`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md)). 실 부팅 사전조건 (env / API key / 외부 서비스 / 포트 / 시스템 패키지) 처리 정책. 답 1: 실 env paste + sha256 봉인 / 답 2: `.env.template` 만 / 답 3: mock 부팅 / 답 4: 외부 의존 없음. 답 1·2 인데 `.env.template` 비어있으면 `entry_blocked: true`. 페이즈 09 게이트 7 이 본 답을 입력으로 *실 부팅 1회* 검증 — 코드-실행가능 까지 담보.

답을 `intent/04-autonomy.md` (9 줄 표) + Q-D8 의 verification 본문은 `intent/04-verification.md`, Q-D9 의 runtime-prereq 본문은 `intent/04-runtime-prereq.md` 에 기록. **9 답 + verification 산출물 + runtime-prereq 산출물 모두 valid 해야 페이즈 05 진입** — 페이즈 04 가 마지막 인터럽트이므로 사전 위임 + 검증 명령 + 실행 사전조건 부재 시 후속 자율 진행이 정의 안 된다.

## 성공 기준

a- `04-answers.md` 가 `04-questions.md` 의 모든 항목을 커버. `TBD` 또는 `?` 표시 없음.
b- "사용자가 결정 보류" 같은 응답도 명시적으로 기록 (페이즈 05 비평이 이를 다시 다룸).

## 흔한 실패

a- 질문 6개 이상 — 차원이 섞임. clarifier 재실행해 차원별로 재구성.
b- 객관식인데 알파벳 라벨 — 컨벤션 위반. 수정 후 재질의.
c- 두괄식 누락 — 사용자가 끝까지 읽어야 핵심이 나오는 질문은 무효.

> **공통 안티 패턴** (조기 추상화 / 분산 모놀리스 / 두괄식 누락 / 객관식 라벨 등) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조.
