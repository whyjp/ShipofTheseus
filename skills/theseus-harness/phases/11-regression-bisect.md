# Phase 11 — 회귀 바이섹트

## 한 줄 요약
**점수가 0.05 이상 하락한 스프린트가 발생하면 *추가 구현 전* 에 원인 판자를 찾는다.** 테세우스의 배에 잘못된 판자가 박혀 있다 — 더 박기 전에 빼낸다. 분석가는 진단만, 코드 수정 금지.

> **v0.9.16 sprint-10 — 자기 강화 메커니즘 (`regression` §3 lint autogen, sprint-37 PR-AE 통합)**: 4 분류 (plan/impl/data/external defect) 정정 commit 시 *동일 차원 회귀 차단 self_lint 룰 신규* 의무. 회귀 정정이 일회성이 아니라 *영구 자산화* — 본 하네스가 회차마다 더 단단해지는 우로보로스 메커니즘. 자세한 룰은 [`../conventions/regression.md`](../conventions/regression.md) §3.

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

## 병렬 회의론자 진단 (B2 — `regression.parallel_diagnosis` 게이트)

> **커널 게이트 배선**: 회귀(`score_delta < -0.05`)가 검출되면 진단은 단일 분석가의 서술이 아니라 *여러 독립 회의론자의 corroborated 병렬 판단* 이어야 한다. [`../scoring/producers/measure_regression_diagnosis.py`](../scoring/producers/measure_regression_diagnosis.py) 가 산출물을 디스크에서 세어 커널 게이트 `regression.parallel_diagnosis`(G4/G5) 를 먹인다. 진단 병렬화가 모델재량이 아니라 코드가 소유하는 조건.

### 1. K 회의론자 병렬 dispatch (evidence-axis framing)

`K = manifest.regression_diagnosis.min_hypotheses[grade]` (G4=3, G5=4) 명의 *fresh, zero-shared-context* 회의론자를 **동시에** dispatch 한다. 각 회의론자는 서로의 결론을 보지 않는다(공유 컨텍스트 0). 프레이밍은 *defect-class 별 옹호자* 가 아니라 **관측 축(evidence-axis)** 별이다 — 결론이 아니라 *무엇을 읽을지* 를 나눠 dispatch 편향을 줄인다:

| 회의론자 축 | 읽는 것 |
|----|----|
| **diff-reader** | 회귀 시작 commit 의 diff (파일·함수·라인) |
| **failing-test-trace-reader** | 실패 테스트의 스택/assert 메시지 트레이스 |
| **data-schema-reader** | 입력 데이터 스키마 변동 (CSV 컬럼/YAML 키) |
| **env-dependency-reader** | 외부 의존 변경 (requirements/pyproject/.env/OS) |

각 회의론자는 자기 축에서 관측한 것만으로 `defect_class` 를 *독립* 판정하고 `sprints/NN/hypotheses/hypothesis-<k>.json` 을 쓴다:

```json
{
  "agent_call_id": "<이 dispatch 고유 ID>",
  "defect_class": "plan_defect | impl_defect | data_defect | external_defect",
  "suspect_file_or_commit": "internal/auth/token.go:42 | <commit-sha>",
  "failing_test": "internal/auth/token_test.go::TestExpiredRejected",
  "alternative_class": "impl_defect",
  "alternative_reason": "왜 이 대안이 덜 가능성 있는지 — 단독 가설은 과신"
}
```

동시에 각 회의론자는 자기 dispatch 를 `state/review_dispatch_log.json` 에 append 한다(순도 교차 대조용, `review.context_minimality` 게이트 생태계 보강):

```json
{"agent_call_id": "<위와 동일>", "prior_context_token_count": 0, "loaded_artifacts": ["<자기 축 파일들>"]}
```

- `defect_class` 는 유효 4-class([`../scoring/checkpoint.py`](../scoring/checkpoint.py) `BISECT_DEFECT_CLASSES`) 밖이면 `invalid_class_votes` FAIL.
- `agent_call_id` 재사용(중복)은 zero-shared-context 병렬성 위조 → `duplicate_call_ids` FAIL.
- 비어있지 않은 `alternative_class` 없는 가설은 `hypotheses_without_alternative` FAIL(반대 가설 의무).

### 2. 회귀 분석가 = MERGE 역할

병렬 회의론자 뒤, [`../agents/regression-analyst.md`](../agents/regression-analyst.md) 는 옹호가 아니라 **병합(merge)** 을 수행한다 — 코드가 소유하는 argmax:

- `regression_class` := 회의론자 표결의 **argmax** `defect_class` (최다 득표). 같은 class 합의가 `corroboration_min`(=2) 미만이면 `corroboration_count` FAIL(미수렴 → 추가 구현 차단).
- `fix_target_phase` := `FAILURE_TO_PHASE[regression_class]` ([`../scoring/checkpoint.py`](../scoring/checkpoint.py) 단일 소스 — `plan_defect→06 / impl_defect→08 / data_defect→04 / external_defect→09`). 이 라우팅 테이블과 어긋나면 `routing_matches_class` FAIL.
- 회귀 이벤트 binding: `bisect.md` frontmatter 에 `gate_history_ref`(회귀가 기록된 `state/gate_history/<NN>` dir 이름) + `prior_score` + `current_score`(그 이벤트의 evidence score 와 일치) 를 쓴다. 일치하는 bound 진단이 없는 회귀 이벤트는 `undiagnosed_events` FAIL.

```yaml
# sprints/NN/bisect.md frontmatter 추가 키 (기존 regression_class/fix_target_phase 위)
gate_history_ref: "07"        # 회귀 이벤트가 기록된 gate_history dir
prior_score: 0.92             # 그 이벤트의 prior_score 와 일치
current_score: 0.78           # 그 이벤트의 current_score 와 일치
```

## 지휘자 후속 — 사전 위임 자동 적용 (인터럽트 없음)

페이즈 04 의 [`../conventions/autonomy.md`](../conventions/autonomy.md) Q-D1 답에 따라 회귀 권고를 *자동 적용*. 인터뷰 종료 후 사용자에게 추가 ack 호출 절대 없음:

a- Q-D1 답 = `1` (모든 권고 자동) → bisect 의 `recommendation` (revert / re-architect / accept) 그대로 자동 적용.
b- Q-D1 답 = `2` (revert 만 자동) → recommendation 이 revert 면 자동, 그 외는 sprint-narrative.md §4 의 정체로 판정해 Q-D4 매핑.
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

> **라우팅 단일 소스 (P2 통합)**: 위 4 분류 → 페이즈 매핑의 *코드 권위* 는 [`../scoring/checkpoint.py`](../scoring/checkpoint.py) 의 `FAILURE_TO_PHASE` 단일 테이블이다 (`plan_defect→06 / impl_defect→08 / data_defect→04 / external_defect→09`). 본 표는 *설명* 이고 실제 라우팅은 그 테이블이 낸다 — 런타임 신호 계열(`stagnation`/`dip_violation` 등)과 bisect 4 분류가 한 테이블로 통합되어 이원화가 제거됐다. 본 표와 `FAILURE_TO_PHASE` 가 어긋나면 `test_checkpoint` 의 drift 가드가 FAIL.

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
