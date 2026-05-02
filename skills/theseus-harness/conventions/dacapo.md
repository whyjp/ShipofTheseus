# Da Capo 루프 — 자기 강화 회귀 테스트

## 한 줄 요약
**실패 → 해결 → 레슨 → 방어 테스트 → 회귀 검증 → (방어 깨지면) 레슨 무효화 → 다시 해결 — 음악의 "Da Capo (처음부터 다시)" 처럼, 매 반복마다 누적 레슨이 테스트를 더 강하게 만드는 강제 루프.** AIDE tree search + LLM Wiki 의 두 패턴에 이미 내재된 요소들 (백트랙·Memory·Lint·모순 감지) 을 *반드시 해야 하는* 강제 순차로 묶은 것.

## 출처

본 컨벤션은 사용자가 이전 연구에서 정형화한 *AIDE × LLM Wiki × Lesson Loop 프레임워크* (2026.04, §3.3 "Da Capo Loop") 를 본 하네스의 페이즈 10/11 + lessons.md + checkpoints.md 와 통합한 것이다.

ⓐ **AIDE Tree Search** (Weco AI, 2024.01~) — 4 오퍼레이터 (Draft/Improve/Debug/Memory), tree 기반 백트랙.
ⓑ **LLM Wiki** (Karpathy, 2026.04) — Two Outputs Rule, 모순 감지, Lint, Decision Records.
ⓒ **Da Capo** — 두 개념의 강제 순차 루프 결합.

## AIDE 4 오퍼레이터 매핑

본 하네스의 14 페이즈를 AIDE 오퍼레이터로 매핑:

| AIDE Operator | 본 하네스에서의 역할 | 페이즈 |
| ------------- | ------------------ | ----- |
| **Draft** | 빈 루트에서 새 솔루션 생성 — 첫 의도/계획/구현 | 페이즈 01 / 06 / 08 |
| **Improve** | 기존 성공 노드(체크포인트) 에서 분기해 개선 | 페이즈 10 (스프린트 루프) |
| **Debug** | 실패 노드의 에러 분석 + 수정 — 회귀 바이섹트 + 정체 rewrite | 페이즈 11 + lessons.md `rewrite_module` |
| **Memory** | 과거 시도 요약을 다음에 주입 — lesson_pack | lessons.md `lesson_pack` 매 sprint 첨부 |

## 강제 루프 (의사코드)

```
loop:
    test_result = run_test_matrix()                    # AIDE Improve (sprint)

    # Phase V — 측정 유효성 (test-invariants.md)
    validity = check_measurement_validity(test_result)
    if validity == "INVALID":
        fix_test_infrastructure()                       # AIDE Debug (인프라)
        continue

    if test_result.passed:
        # Two Outputs Rule (LLM Wiki) — 결과물 + 위키
        write_artifact(test_result)
        update_wiki(lesson=None)                        # 통과도 wiki 갱신
    else:
        # 실패 분석 + 회귀 결정 (checkpoints.md)
        target = find_regression_target(failure)        # AIDE 백트랙
        regress_to(target)
        lesson = extract_lesson(failure, target)        # AIDE Memory

        # 불변 조건 검사 (test-invariants.md)
        if lesson.violates_invariants:
            forbidden_strategies.append(lesson)         # 회피 분리
            continue

        # 방어 테스트 생성 — 레슨이 *실제로* 방어되는지 검증할 테스트
        defense_test = generate_defense_test(lesson)
        regression_suite.append(defense_test)

        # Da Capo — 회귀 스위트 전체 재실행
        regression_result = run_all_tests(regression_suite)

        if defense_test in regression_result.failed:
            # 레슨 무효화 — 방어가 실제로 작동 안 함
            invalidate_lesson(lesson, reason="defense test failed")
            continue                                    # 다시 해결

        # 정상 등록
        lessons.append(lesson)                          # AIDE Memory 누적
        update_wiki(lesson)                             # LLM Wiki Two Outputs
```

## 방어 테스트 (Defense Test) — 레슨이 실제로 작동하는지 검증

레슨의 핵심: *지난 실패가 다시 나지 않을 것* 을 보장. 이를 검증하려면 레슨 자체를 시험할 *방어 테스트* 가 필요:

ⓐ 레슨 = "X 조건에서 Y 가 깨지면 Z 로 해결" → 방어 테스트 = "X 조건을 다시 만들고 Z 가 적용된 코드가 통과하는지 검증".
ⓑ 방어 테스트는 회귀 스위트 (regression suite) 에 영구 추가 — 이후 매 sprint 마다 실행.
ⓒ 방어 테스트가 *나중에* 깨지면 → 레슨 무효화 + 재해결 (Da Capo).
ⓓ 레슨 무효화는 LLM Wiki 의 *모순 감지* — 덮어쓰지 않고 `wiki/decisions/<date>-invalidated-lesson-N.md` 에 사유 + 무효 시점 기록.

## 자기 평가에서의 적용

본 저장소 (`theseus-self`) 의 self_lint 자체에도 Da Capo 루프 적용:

ⓐ **Draft** — 새 체크 (예: C24) 추가는 Draft.
ⓑ **Improve** — 기존 체크의 정확도 개선 (예: C11 의 `proposed: true` 만 본문 검사 → 매 항목 검사).
ⓒ **Debug** — fail 발견 (예: C12-C18 fail) → 해당 phase/agent 본문 보강.
ⓓ **Memory** — 보강 후 *같은 종류의 갭이 다른 곳에도 있는지* 자동 탐색 (예: C17 이 12 에이전트 모두에 적용된 것).

회차 시계열은 LLM Wiki 의 누적 — `.ShipofTheseus/theseus-self/sprints/NN/quality-gate.md` 가 매 회차 누적.

## Phase V 와 Da Capo 의 결합

```
sprint:
    1. test_result = run()                          # AIDE Improve
    2. validity = phase_v_check(test_result)        # test-invariants.md
       ├─ INVALID → infrastructure fix → sprint 재시작
       └─ VALID → 3
    3. if PASS: wiki update + return
       if FAIL: 4
    4. failure → find_regression_target              # checkpoints.md
                → regress + lesson 추출 (AIDE Memory)
                → invariants violation? → forbidden 분리
                → defense_test 생성
                → regression_suite 전체 재실행 (Da Capo)
                → defense 실패? → 레슨 무효화 → 재해결
                → defense 성공? → wiki 등록 → sprint 종료
```

## Two Outputs Rule — 본 하네스 적용

LLM Wiki 의 핵심 룰 — *모든 작업은 두 출력을 생성*:

ⓐ **작업 결과물** — 코드/문서/측정값.
ⓑ **위키 업데이트** — 무엇을 배웠는지 (lesson_pack), 어떤 결정을 했는지 (decision record), 어떤 모순이 있는지 (contradiction record).

본 하네스에서:
ⓐ 페이즈 산출물 자체 = 작업 결과물.
ⓑ `lesson_pack.json` (페이즈 10) + `intent/05-decisions.md` + `multiverse/<id>/verdict.md` = 위키 업데이트.

## 모순 감지 — 덮어쓰지 않고 기록

새 레슨이 기존 레슨을 반박할 때 (예: "X 조건에서 Y 가 옳다" → 나중에 "X 조건에서 Y 가 틀렸다") 덮어쓰지 않고 *모순으로 기록*:

```
.ShipofTheseus/<프로젝트>/wiki/contradictions/2026-05-01-lesson-042-vs-067.md
  - lesson 042: "쓰기 후 즉시 읽기는 일관성 보장" (sprint 5)
  - lesson 067: "쓰기 후 즉시 읽기는 stale 가능" (sprint 12)
  - resolved: lesson 067 채택 — sprint 12 의 부하 조건이 더 현실적
  - lesson 042 는 invalidated, defense_test_042 비활성화
```

## 안티 패턴

ⓐ **방어 테스트 없이 레슨 등록** — 다음 sprint 에서 같은 실패 재발 시 레슨이 작동했는지 모름.
ⓑ **레슨 무효화 = 삭제** — LLM Wiki 의 모순 감지 위반. 덮어쓰지 말고 invalidated 마크 + 사유 기록.
ⓒ **Phase V 건너뛰고 fail 분석 직행** — INVALID 케이스를 잘못된 레슨으로 누적.
ⓓ **AIDE Debug 만 무한 시도** — Memory + 백트랙 결합 안 하면 같은 실패 반복. lesson_pack + checkpoints.md 회귀로 조합.
