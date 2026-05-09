---
id: tournament-blind-rerun
category: tournament
applies-to-phases: '[06,08,11]'
applies-to-grades: '[G3,G4,G5]'
trigger-when: '임계 미달'
indexed-in: conventions/INDEX.md
---

# Tournament Blind Rerun — 토너먼트 미달 시 blind champion-injection 재경합

## 한 줄 요약

**페이즈 06 또는 multi-phase AIDE-tree 의 tournament 결과가 임계 미달 시, *previous winner 를 anonymize* 후 N+1 universe 로 재경합.** *blind* 진행 — 새 agent 는 *어떤 candidate 가 previous champion 인지 모름*. 이중 검증 :  (a) previous winner 가 다시 우승하면 *진짜 강함* / (b) 새 fresh winner 가 우승하면 *previous 가 운*. 또는 *algorithmic union* candidate 로 대체 가능.

## 1. 결손 진단

기존 [`competition.md`](competition.md) + [`regression.md`](regression.md) §2 sprint loop (sprint-37 PR-AE 통합) :

- competition.md = single tournament 후 winner 선정.
- regression.md §2 sprint loop = sprint-level 임계 미달 시 *project-wide* lesson 적용.

→ **phase-level tournament 의 임계 미달 시 *그 페이즈만* 재경합** 메커니즘 부재. winner 가 임계 미달이어도 phase 14 진입 또는 sprint loop 의 weakest dim 보강. winner 자체가 *우연한 1등* 이었을 가능성 미검증.

## 2. 운영 룰

### Step 1 — tournament 결과 → 임계 비교

페이즈 06 (또는 다른 AIDE-tree 페이즈) 의 tournament merge 후 winner 의 *self-estimate sub-score* 계산 :

- threshold (G3=0.97 / G4=0.999) 이상 → CONVERGED, phase 07 진입
- threshold 미달 → REGRESS, **블라인드 재경합** 트리거

### Step 2 — anonymize previous winner

previous winner 의 산출물 (`plan/candidates/universe-W/06-plan.md` 등) 을 *anonymize copy* :

a- frontmatter 제거 / scrub (skill_name / version / fingerprint 모두).
b- 본문에서 universe ID 자기 인용 제거 (`이 universe 는 ...` → `이 후보는 ...`).
c- 파일명 변경 — `universe-W-anonymous-{rand_id}` 처럼 *식별 불가* 이름.

### Step 3 — fresh N + 1 (blind) 재경합

- 새 N planner sub-agent 호출 (페이즈 06 와 동일 룰, 다른 seed).
- 새 agents 에 *anonymized previous winner* 도 *equal candidate* 로 입력. 어느 것이 anonymized 인지 *모름*.
- tournament merge 재실행 (자동 — competition.md 알고리즘 동일).

### Step 4 — 결과 분석

| 결과 | 의미 | 다음 |
|---|---|---|
| anonymized previous winner 가 다시 우승 | *진짜 강함* — fresh agents 의 새 candidates 모두 못 이김 | CONVERGED, phase 07 진입. (단 임계 여전 미달 시 algorithmic union 옵션) |
| 새 fresh winner 가 우승 | previous winner 가 *운* 또는 *지엽적 강점* — 새 winner 가 better | new winner 채택, phase 07 진입 |
| 동률 | universe diff 가 substantive 안 함 — *재경합 의미 약* | 두 winner ensemble (algorithmic union) |

## 3. Algorithmic Union 옵션

blind 재경합 대신 또는 추가로 :

`plan/candidates/universe-union-{revision}` 신규 생성 — N previous candidates 의 algorithmic union :

a- 각 universe 의 *strongest sub-component* 만 추출 (예: U1 의 dispatcher 알고리즘 + U2 의 resource 모델 + U3 의 router).
b- merge 충돌 (둘 다 dispatcher 정의) → competition.md 의 차원별 sub-score 로 자동 resolve.
c- Union candidate 가 *기존 winner 와 동급* 이면 union 채택 (covers more strengths).

## 4. v0.9.10 페이즈 내 활성

| 페이즈 | tournament 활성 | blind rerun 활성 |
|---|:-:|:-:|
| 06 plan-tree | ✅ default | ✅ G4+ |
| 02 doc-review (multi-reviewer) | ⚠️ aide-tree §2 (multi-phase) 활성 시 | ✅ |
| 05 critique (multi-critic) | ⚠️ aide-tree §2 (multi-phase) 활성 시 | ✅ |
| 08 impl strategy | ⚠️ aide-tree §2 (multi-phase) 활성 시 | ✅ |
| 11 regression bisect (multi-hypothesis) | ⚠️ aide-tree §2 (multi-phase) 활성 시 | ✅ |

## 5. 안티 패턴

a- **anonymize 미완** — previous winner 의 frontmatter 일부 잔존 → fresh agents 가 식별 가능. self_lint C-TBR-ANON 강제.
b- **infinite blind rerun** — 매 sprint 마다 blind rerun → budget 소진. *budget cap* 또는 *임계 가까이 도달* 시 종료 룰.
c- **anonymize 후 의미 변형** — universe-W 의 본문 의미가 anonymize 과정에서 *바뀌면* fair test 위반. 의미 보존 검증 의무.
d- **union 의 cherry-picking** — strongest sub-component 만 픽 → union 이 항상 우승 → competition 우회. self_lint C-TBR-UNION 가 union 의 *origin 분포* (각 universe contribution 비율) ≥ 0.2 each 검증.

## 6. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- anonymize = 텍스트 처리 (frontmatter scrub + universe ID 제거), 도메인 X.
b- blind rerun = 일반 tournament 재실행, 도메인 X.
c- union = competition.md 의 차원별 sub-score 룰 재사용, 도메인 X.

## 7. 자기 검증 (메타)

본 컨벤션 자체에 적용 가능 : 본 conventions/tournament-blind-rerun.md 가 작성된 후, 임계 미달 (예: section count < expected) 발견 시 본 문서 자체를 anonymize → fresh agents 가 다시 작성 → 비교. 본 회차 에서는 미적용 (single-shot).
