# Da Capo 결합 인덱스 — AIDE × LLM Wiki 매핑 (얇은 메타 컨벤션)

## 한 줄 요약
**본 컨벤션은 *얇은 인덱스* 다.** Da Capo 의 강제 루프 본문 — "실패 → 해결 → 레슨 → 방어 → 검증 → 무효화 → 재해결" — 의 *각 단계가 어느 컨벤션/도구에 이미 박혀 있는지* 매핑하고, 본 하네스에만 있는 **고유 신규 개념 2종 (방어 테스트 / 모순 감지)** 의 위치를 명시한다. 본문 룰을 여기서 다시 정의하지 않는다 ([`fragmentation.md`](fragmentation.md) §1 DRY).

## 출처 (변경 없음)

a- **AIDE Tree Search** (Weco AI, 2024.01~) — 4 오퍼레이터 (Draft/Improve/Debug/Memory).
b- **LLM Wiki** (Karpathy, 2026.04) — Two Outputs Rule, 모순 감지, Lint, Decision Records.
c- **Da Capo Loop** (사용자 이전 연구, 2026.04 §3.3) — 두 개념의 강제 순차 결합.

## 결합이 어디에 박혀 있는가 — 출처 × 본 하네스 매핑

### AIDE 4 오퍼레이터

| AIDE Operator | 본 하네스의 동치 | 정의 위치 |
| ------------- | --------------- | -------- |
| **Draft** | 빈 루트에서 새 솔루션 — 첫 의도/계획/구현 | [`../phases/01-intent.md`](../phases/01-intent.md) / [`../phases/06-plan.md`](../phases/06-plan.md) / [`../phases/08-implement.md`](../phases/08-implement.md) |
| **Improve** | 기존 노드(체크포인트) 에서 분기 개선 | [`../phases/10-test-loop.md`](../phases/10-test-loop.md) (스프린트 루프) |
| **Debug** | 실패 분석 + 수정 (회귀 바이섹트 + 정체 rewrite) | [`../phases/11-regression-bisect.md`](../phases/11-regression-bisect.md) + [`lessons.md`](lessons.md) `rewrite_module` |
| **Memory** | 과거 시도 요약 주입 — lesson_pack | [`lessons.md`](lessons.md) `lesson_pack` (모든 sprint 첨부) |

### LLM Wiki 4 원칙

| LLM Wiki 원칙 | 본 하네스의 동치 | 정의 위치 |
| ------------ | --------------- | -------- |
| **Two Outputs Rule** | 작업 결과물 + 위키 (lesson_pack/decisions/multiverse verdict) | 본 컨벤션 §"Two Outputs 매핑" (아래) |
| **Contradictions flagged, not overwritten** | 레슨 무효화 시 wiki/contradictions/ 기록 | 본 컨벤션 §"모순 감지" (신규 정의) + [`contracts.md`](contracts.md) 의 wiki/contradictions/ 디렉터리 |
| **Lint** | 산출물·컨벤션 정합성 검사 | [`../scoring/self_lint.py`](../scoring/self_lint.py) (31 체크) + [`../scoring/index_builder.py`](../scoring/index_builder.py) |
| **Decision Records** | 사용자/자율 결정 기록 | `intent/05-decisions.md` + [`autonomy.md`](autonomy.md) §"자율 결정의 사후 리뷰 가능성" + [`indexing.md`](indexing.md) |

### Da Capo 강제 루프 6 단계

각 단계의 *룰 본문* 은 다른 컨벤션이 정의 — 본 컨벤션은 *어디에 있는지* 만 가리킨다:

| 단계 | 정의 위치 |
| --- | -------- |
| 1- 실패 (failure detection) | [`../phases/10-test-loop.md`](../phases/10-test-loop.md) 스프린트 결과 + [`test-invariants.md`](test-invariants.md) Phase V |
| 2- 해결 (fix) | [`../phases/11-regression-bisect.md`](../phases/11-regression-bisect.md) 권고 + [`lessons.md`](lessons.md) rewrite |
| 3- 레슨 추출 (extract) | [`lessons.md`](lessons.md) `lesson_pack` 형식 |
| 4- 방어 테스트 (defense) | 본 컨벤션 §"방어 테스트" (신규 정의) — [`lessons.md`](lessons.md) lesson_pack 의 `defense_test` 필드 확장 |
| 5- 회귀 검증 (regression suite) | [`../phases/10-test-loop.md`](../phases/10-test-loop.md) 의 매 sprint 전체 재실행 |
| 6- 무효화 (invalidation) | 본 컨벤션 §"모순 감지" (신규 정의) — wiki/contradictions/ 기록 |

→ 단계 4-/6- 만 본 컨벤션 *고유 신규*. 나머지 4 단계는 cross-link.

## Two Outputs 매핑 (LLM Wiki 핵심 룰)

본 하네스의 모든 페이즈/스킬 산출은 두 출력을 만든다:

a- **작업 결과물** — `intent/<NN>.md` / `plan/<NN>.md` / `impl/<...>` / 코드 등.
b- **위키 업데이트** — 다음 셋 중 하나 이상:
  b-1 `lesson_pack.json` (sprint NN — [`lessons.md`](lessons.md))
  b-2 `intent/05-decisions.md` (사용자/자율 결정)
  b-3 `multiverse/<branch>/verdict.md` (우승/머지 사유)
  b-4 `wiki/contradictions/<date>-<topic>.md` (모순 — 아래 §모순 감지)

[`indexing.md`](indexing.md) 의 INDEX.md 가 두 출력 모두를 자동 인덱싱.

## 방어 테스트 — 본 하네스 고유 신규 개념

**문제**: 레슨이 *지난 실패가 다시 안 난다* 를 보장하려면 그 레슨을 *시험할 테스트* 가 필요. 단순 lesson_pack 누적만으로는 다음 sprint 가 같은 실패를 일으키는지 *적극 검증* 안 됨.

**해결** — [`lessons.md`](lessons.md) 의 `lesson_pack` 구조에 다음 필드 추가:

```yaml
defense_test:
  test_id: "T-AUTH-DEFENSE-042"
  test_path: "internal/auth/defense_test.go::TestExpiredTokenStillRejectedAfterRefactor"
  reproduces_failure: "lesson 042 의 X 조건 + 그 레슨이 적용된 코드"
  added_to_regression_suite: true
  added_at: "2026-05-01T18:42:11+09:00"
```

**룰**:
a- 모든 정상 등록되는 lesson 은 `defense_test` 필드 의무.
b- 방어 테스트가 *나중에* 깨지면 — 레슨 무효화 (§모순 감지) + 재해결 (Da Capo 사이클 재진입).
c- 회귀 스위트 ([`../phases/10-test-loop.md`](../phases/10-test-loop.md)) 가 매 sprint 모든 방어 테스트 실행.

## 모순 감지 — 본 하네스 고유 신규 개념

**문제**: 새 레슨이 기존 레슨을 반박할 때 — 예: lesson 042 "쓰기 후 즉시 읽기는 일관성 보장" → 나중에 lesson 067 "stale 가능". *덮어쓰기* 는 LLM Wiki 의 핵심 룰 위반.

**해결** — `.ShipofTheseus/<프로젝트>/wiki/contradictions/<date>-<topic>.md` 표준 형식:

```markdown
# 모순 — lesson 042 vs lesson 067

- **lesson 042** (sprint 5): "쓰기 후 즉시 읽기는 일관성 보장" — defense_test_042
- **lesson 067** (sprint 12): "쓰기 후 즉시 읽기는 stale 가능" — defense_test_067

## 해소
lesson 067 채택 — sprint 12 의 부하 조건이 더 현실적 (실 운영 트래픽 모방).
lesson 042 는 invalidated, defense_test_042 는 회귀 스위트에서 비활성화 (삭제 X — git history + 본 모순 기록 보존).

## 후속
- defense_test_067 신규 추가 (회귀 스위트)
- intent/05-decisions.md 에 본 모순 해소 결정 기록
```

**룰**:
a- 레슨 무효화는 *항상* 본 디렉터리에 모순 기록 — 단순 lesson_pack 갱신 금지.
b- 무효화된 lesson 은 *삭제* 안 됨 — `invalidated: true` 마크 + 사유 + 무효 시점 기록.
c- [`indexing.md`](indexing.md) 의 INDEX.md 가 모순 기록을 별도 섹션으로 노출.
d- [`autonomy.md`](autonomy.md) 의 *사후 리뷰 가능성* 에 모순 이력 포함.

## 안티 패턴

a- **본 컨벤션이 본문 룰을 다시 정의** — fragmentation.md DRY 위반. 본문 룰은 lessons/checkpoints/test-invariants/phase 10 만 정의, 본 컨벤션은 *매핑 인덱스 + 신규 2 개념* 만.
b- **방어 테스트 없이 레슨 등록** — 다음 sprint 에서 같은 실패 재발 시 검증 불가. lesson_pack 의 `defense_test` 필드 의무.
c- **레슨 무효화 = 삭제** — LLM Wiki 모순 감지 위반. 항상 `wiki/contradictions/` 기록.
d- **AIDE 4 오퍼레이터 매핑을 페이즈 본문에 복제** — 본 컨벤션의 매핑 표가 단일 source.
