# Phase 11 — 회귀 바이섹트

## 한 줄 요약
**점수가 0.05 이상 하락한 스프린트가 발생하면 *추가 구현 전* 에 원인 판자를 찾는다.** 테세우스의 배에 잘못된 판자가 박혀 있다 — 더 박기 전에 빼낸다. 분석가는 진단만, 코드 수정 금지.

## 트리거

페이즈 10 의 루프가 `score(N) < score(N-1) - 0.05` 일 때 자동 호출. 수동: `score.py --bisect`.

## 입력
- `sprints/N-1/report.md` (마지막 양호)
- `sprints/N/report.md` (회귀)
- 두 체크포인트 사이의 `git diff`
- 스프린트 N 의 실패 테스트 목록 + 에러 메시지

## 서브에이전트
[`../agents/regression-analyst.md`](../agents/regression-analyst.md). **코드 편집 금지** — 진단만.

## 산출물
`sprints/NN/bisect.md` — [`../conventions/timing.md`](../conventions/timing.md) 헤더 + 다음:

a- **무엇이 떨어졌나** — 어떤 sub-score 가 얼마만큼.
b- **무엇이 변했나** — diff 요약 (파일·함수·라인).
c- **주 가설** — 함수/라인 수준에서 단일 후보. 실패 테스트 1개 이상이 이 가설과 정합.
d- **반대 가설** — 최소 1개, 왜 덜 가능성 있는지.
e- **권고** — 다음 셋 중 하나:
  1- `revert <commit-or-file>` — 외과적 되돌림.
  2- `re-architect <module>` — *깊은 품질 위반* 의 증상 → 그 모듈에 대해 페이즈 06 부터 재실행. 트리거 차원: DIP/SOLID · 코드 오류 누적 · 기획-구현 갭 · 성능/NFR 미달 · 의도 표류 · 정체/회귀 누적 6 종 중 *어느 하나라도* 깊이 임계 초과면 충분.
  3- `accept` — 회귀가 실은 의도된 변화 (제약이 중간에 바뀜) — 사용자가 명시 확인.

## 지휘자 후속 — 사전 위임 자동 적용 (인터럽트 없음)

페이즈 04 의 [`../conventions/autonomy.md`](../conventions/autonomy.md) Q-D1 답에 따라 회귀 권고를 *자동 적용*. 인터뷰 종료 후 사용자에게 추가 ack 호출 절대 없음:

a- Q-D1 답 = `1` (모든 권고 자동) → bisect 의 `recommendation` (revert / re-architect / accept) 그대로 자동 적용.
b- Q-D1 답 = `2` (revert 만 자동) → recommendation 이 revert 면 자동, 그 외는 lessons.md 의 정체로 판정해 Q-D4 매핑.
c- Q-D1 답 = `3` (모두 정지) → 본 스킬 의도 위반 — 페이즈 04 에서 비권장으로 표시, 그래도 사용자가 선택했다면 정지.

[`../conventions/timing.md`](../conventions/timing.md) 의 라이브 보고에 한 줄:

```
스프린트 NN 회귀 (점수 0.92 → 0.78) → bisect 권고 revert (path/a.go:42) → Q-D1.1 자동 적용. 누적 1시간 12분.
```

## 왜 필요한가

우로보로스의 두 번째 자기 무는 지점이며, 회귀 직후 추가 구현 차단을 위한 강제 게이트. 없으면 재귀 하네스는 회귀를 더 많은 코드로 "고치려" 하고, 스프린트마다 누적 악화로 들어간다.

## 성공 기준

a- `bisect.md` 가 특정 commit/파일/함수를 명시.
b- 사전 위임 Q-D1 답이 자동 적용되어 다음 스프린트 진행 — 인터럽트 없음 ([`../conventions/autonomy.md`](../conventions/autonomy.md) 의 인터뷰 후 인터럽트 0 룰).
c- **깊은 품질 위반 점검 6 차원** (DIP/코드 오류 누적/스펙 누락/NFR 미달/의도 표류/정체) 모두 명시 (발견 없음도 명시). 어느 차원이라도 임계 초과면 `re-architect` 가 권고.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).

## 회귀 원인 분류 (sprint-05-e Q1)

회귀가 검출되면 본 페이즈 = git bisect 로 commit 식별 후 *원인을 4 분류로 자동 판별* + 권고 페이즈 결정.

### 4 분류

| 분류 | 신호 | 권고 페이즈 |
|----|----|----|
| **plan defect** | 페이즈 06 plan 의 TODO 자체가 잘못 정의 (data 와 충돌, 인터페이스 불일치, 알고리즘 모순) | 페이즈 06 재실행 (re-plan) — universe 재분기 가능 |
| **impl defect** | plan TODO 정확하나 페이즈 08 impl 이 부분 누락 / 잘못 구현 / 분포 실수 | 페이즈 08-γ 재실행 (re-impl) — 같은 plan 유지, 코드만 수정 |
| **data defect** | 입력 데이터 자체 변경/오류 (CSV 컬럼 변동, YAML 스키마 깨짐) | 페이즈 04 Q-D8 재검증 (re-data) + 데이터 수정 |
| **external defect** | 외부 의존 변경 (라이브러리 버전, 환경 변수, OS) | 페이즈 09 게이트 7 재실행 (re-env) |

### 분류 알고리즘

```
1. git bisect 로 회귀 시작 commit C 식별
2. C 의 변경 파일 검사 :
   - plan/ 변경 ? → plan defect 후보
   - code/ 또는 mine_sim/ 변경 ? → impl defect 후보
   - data/ (CSV/YAML) 변경 ? → data defect 후보
   - requirements.txt / pyproject.toml / .env 변경 ? → external defect 후보
3. 페이즈 06 plan 의 TODO DAG 와 페이즈 08 impl-log 의 TODO 매핑 비교 :
   - TODO ID 가 plan 에 있으나 impl-log 에 없음 → impl defect (누락)
   - impl-log 의 모듈명/인터페이스가 plan 의 인터페이스 시그니처와 불일치 → impl defect (drift)
   - plan TODO 의 완료 조건이 *현실 데이터* 와 충돌 → plan defect
4. 분류별 권고 페이즈에 자동 진입 (인터럽트 0, 페이즈 04 외 ack 없음)
```

### 산출물 — `bisect.md` 본문 강화

```markdown
## 회귀 원인 분류
- 분류 : plan defect | impl defect | data defect | external defect
- 신호 : (어떤 파일/어떤 TODO 에서 검출)
- 권고 페이즈 : 06 | 08-γ | 04 Q-D8 | 09 게이트 7
- 자동 진입 : true (인터럽트 0)
```

### sprint-05-c 회고 — 분류 부재 영향

sprint-05-c 의 페이즈 11 비활성 (G3) 이라 분류 안 함. 그러나 페이즈 08 의 sprint narrative 보강 sub-agent 실패 = *impl defect 가 아닌 sub-agent 자체 실패* — 본 분류 5번째 차원 (sub-agent defect) 후보. 후속 sprint 에서 검토.
