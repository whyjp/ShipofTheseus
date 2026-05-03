# 테스트 목적 보호 — 불변 조건과 Phase V

## 한 줄 요약
**레슨이 테스트의 목적(불변 조건) 을 훼손하면 그건 "해결" 이 아니라 "회피" 다.** 각 테스트는 *불변 조건* (절대 건드리면 안 되는 측정 의미) 과 *가변 조건* (구현 디테일) 을 명시 분리하고, **Phase V — 측정 유효성 점검** 으로 "테스트가 제대로 실행됐는지" 를 *결과 신뢰 전* 에 검증한다.

## 출처

본 컨벤션은 사용자가 이전 연구에서 정형화한 *AIDE × LLM Wiki × Lesson Loop 프레임워크* (2026.04) 의 §5.2~§5.5 (테스트 목적 보호 + Phase V) 를 본 하네스 페이즈 09 (품질 게이트) 와 페이즈 10 (스프린트 루프) 에 흡수한 것이다.

## 위험한 "해결" 의 예

```
T5: Concurrent Read During Write
  목적: 쓰기 부하 하에서 읽기 성능 저하 측정

위험한 레슨: "concurrent writer 를 1개로 줄이면 PASS"
  → 테스트는 통과, 그러나 "concurrent" 조건을 사실상 제거 — 회피.

올바른 레슨: "Python GIL 이 프로브의 실질 병렬성을 제한하므로
            multiprocessing 으로 교체해야 concurrent 조건 성립"
  → 측정 도구를 수정해 테스트 목적(병렬 측정) 을 보존 — 진짜 해결.
```

본 하네스의 [`lessons.md`](lessons.md) 가 `forbidden_strategies` 로 *효과 없는 전략* 은 누적 차단하지만, *불변 조건을 훼손하는 전략* 은 별도 분류로 강제 거부해야 한다.

## 불변 조건 명시 — 페이즈 06 (계획) 의 의무

`plan/06-plan.md` 의 각 테스트 TODO 는 다음 두 항목을 *반드시* 채운다:

```yaml
- T-080 — 동시 부하 하 읽기 latency 측정
  invariants:
    - writer 와 reader 가 실제로 동시 실행 (타임스탬프 오버랩 ≥ 80%)
    - writer 부하가 유의미 (noop 아닌 실제 쓰기 ≥ N 건/초)
    - reader 가 writer 와 같은 데이터 영역 접근
  variables:
    - 프로브 구현 언어/방식
    - batch size, iteration count
    - 타임아웃 값
    - 리소스 할당
```

레슨이 `variables` 를 수정하면 정상 레슨 — `lessons.md` 의 lesson_pack 으로 누적.
레슨이 `invariants` 를 변경하려 하면 **"테스트 재설계 신호"** 로 분리, 다른 절차:

```
레슨 추출 시 (페이즈 11 회귀 분석가 또는 페이즈 10 테스터):
  if 레슨이 invariants 를 변경:
    if 원래 테스트 목적이 잘못됐는가?
      yes → 테스트 재정의 (plan/06-plan.md 수정 + ADR 기록)
      no  → 이 레슨은 "회피" 이지 "해결" 아님 → forbidden_strategies 누적
  else:
    정상 레슨 → lesson_pack
```

## Phase V — 측정 유효성 점검 (페이즈 09 의 게이트 7)

[`../phases/09-quality-gates.md`](../phases/09-quality-gates.md) 에 **게이트 7 — 측정 유효성** 추가:

> 테스트가 fail/pass 판정 *전* 에 "테스트가 *제대로 실행됐는지*" 검증.

체크리스트 (페이즈 09 quality-gate 에이전트 의무):

a- **프로브 오버헤드** — 측정 루프의 CPU/메모리가 측정 대상의 10% 이상이면 SUSPECT (예: Python GIL 이 concurrent 프로브의 실질 병렬성 제한).
b- **불변 조건 충족** — `invariants` 의 모든 조건이 *실제 실행* 에서 만족되는지 (타임스탬프 오버랩, 스레드/프로세스 수, 데이터 영역 일치 등).
c- **베이스라인 sanity** — 알려진 대상에서 같은 프로브가 합리적 결과를 내는지. 안 그러면 프로브 자체 문제.
d- **반복 편차** — 동일 테스트 3 회 결과 편차가 30% 이상이면 SUSPECT (환경 불안정 또는 프로브 비결정성).

판정:
- **VALID** → Phase 2(PASS) 또는 Phase F(FAIL) 로 진행.
- **SUSPECT** → 불변 조건 충족 의심 → 프로브 검증 후 재측정.
- **INVALID** → 테스트 실행조차 안 됨 → Phase F (실패 분석) 가 아니라 *테스트 인프라 수정*. lesson_pack 에 `infrastructure_issue: true` 마크.

## 자기 평가에서의 적용

본 저장소의 self_lint (`scoring/test_score.py`, `test_self_lint.py`, `test_stagnation.py`, `test_resource_ceiling.py`, `test_checkpoint.py`) 자체에도 본 룰 적용:

a- 각 테스트의 *불변 조건* — 예: `test_perfect_inputs_pass_at_999_threshold` 의 불변 = "모든 차원 1.0 이면 self_score 1.0".
b- Phase V 적용 — 단위 테스트 실행 시 환경 의존성 (subprocess, tempfile) 이 결과를 흐리지 않는지 검증 — `test_score.py` 의 `tempfile.NamedTemporaryFile` 변경이 그 결과 (race-free).

## 안티 패턴

a- **불변 조건 명시 없이 테스트 작성** — 실패 시 어떤 변경이 회피인지 판단 불가.
b- **Phase V 건너뛰기** — fail 결과를 바로 신뢰하면 *테스트가 제대로 실행 안 된* 케이스를 잘못된 레슨으로 누적.
c- **불변 조건 무시한 레슨을 정상 lesson_pack 으로** — 본 컨벤션 핵심 위반. forbidden_strategies 분리가 의무.
d- **"테스트가 통과한다" 만으로 만족** — 통과 자체가 목적이 아니라, 테스트 *목적이 측정한* 것이 만족됐는지가 본질.

## RED-GREEN-REFACTOR 루프 (sprint-05-a TDD)

페이즈 08 은 sprint-05-a 부터 RED-GREEN-REFACTOR 3 단계 루프를 강제한다.

**RED** (08-β, test-writer):
- test-first 원칙 — 구현 없이 테스트만 작성
- pytest 실행 시 모든 신규 테스트 fail (right reason)
- right reason = 구현 부재. 인프라 오류로 fail 은 right reason 아님

**GREEN** (08-γ, implementer):
- RED 확인된 테스트를 통과하는 *최소* 구현만 작성
- pytest 모두 GREEN 확인 후 출하
- 과잉 구현 (테스트 없는 기능 추가) 금지

**REFACTOR** (08-δ, refactorer):
- GREEN 유지하면서 DRY / SOLID / docstring / type hint 개선
- 기능 변경 0 — pytest GREEN 유지가 기능 불변의 증거
- REFACTOR 후 새로운 RED 발생 시 즉시 중단 + 롤백

페이즈 08 의 5 서브페이즈 연결: 08-α(scope) → 08-β(RED) → 08-γ(GREEN) → 08-δ(REFACTOR) → 08-ε(log).

자세한 서브페이즈 정의는 [`../phases/08-implement.md`](../phases/08-implement.md) 참조.

## universe 변경 트리거

페이즈 06 (plan-tree) 의 머지 결정이 변경되는 경우 — universe 추가, 제거, 머지 결정 변경 — 페이즈 08 을 **08-α 부터 재실행**한다.

트리거 조건:
- 새 universe 추가 → 기존 test scope (08-α) 가 새 universe 를 포함하지 않음 → scope 무효
- universe 제거 → 해당 universe 대상 테스트 삭제 필요 → scope 재정의
- 머지 결정 변경 → 모듈 경계 변경 → atomic/group scope 재정의

재진입 절차:
1. 현재 08 서브페이즈 중단
2. 08-α (test-architect) 재호출 — 새 plan-tree 기반 scope 재정의
3. 08-β → 08-γ → 08-δ → 08-ε 순서 재실행
4. 이전 `impl/08-test-scope.md` 는 `impl/08-test-scope.prev.md` 로 보존 (감사 추적)

부분 재진입(08-β 만 재실행 등)은 scope 불일치를 유발하므로 **금지**.
