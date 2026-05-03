# 체크포인트·회귀·멀티버스 컨벤션

## 한 줄 요약
**페이즈 *내부* 의 하위 세부 단위를 체크포인트로 관리해 — 실패/잘못된 구현 시 원인을 자동 분석하고 적절한 체크포인트로 자율 회귀, 동시에 여러 후보 우주(멀티버스) 를 병렬 진행해 점수+레슨으로 최적 루트를 선택한다.** 인터럽트 없이 분기·실패·회수가 자동으로 도는 구조 — 사용자는 결과만 받는다.

## 출처 — 사용자가 이전부터 연구해온 루프 방식

본 컨벤션은 사용자(저장소 메인테이너) 가 이전 연구에서 정형화한 *체크포인트 회귀 + 멀티버스 병렬* 루프를 본 하네스의 정식 컨벤션으로 흡수한 것이다. 페이즈 단위 경쟁(`competition.md`) 과 정체 후 rewrite(`lessons.md`) 의 *상위 일반화* — 페이즈 내부의 하위 시도 단위까지 같은 메커니즘을 확장.

## 닥터 스트레인지 메타포

> "I went forward in time, to view alternate futures. To see all the possible outcomes of the coming conflict. ... 14,000,605 ... in only one we win."
>
> *— Doctor Strange, Avengers: Infinity War*

본 하네스는 한 의사결정 지점에서 *N 개 후보 우주* (multiverse_branch) 를 격리 병렬 진행하고, 각 우주의 점수와 레슨을 비교해 최적 루트를 *자동* 선택한다. 채택 안 된 우주는 폐기되지 않고 학습 자산으로 보존 — 다음 멀티버스 시도에서 `forbidden_strategies` 로 누적.

## 체크포인트 정의

체크포인트는 **페이즈 내부의 하위 세부 단계** 에서 산출물·상태·측정값·레슨을 한 번에 봉인한 시점.

a- 페이즈 = 큰 단위 (00 명명 / 01 의도 / ... / 13 핸드오프)
b- 체크포인트 = 페이즈 안의 작은 단위 (예: 페이즈 08 구현 안에서 모듈별 또는 TODO별 체크포인트)
c- 각 체크포인트마다 [`contracts.md`](contracts.md) 의 frontmatter + 부모 체크포인트 fingerprint 체인 + 누적 레슨 ([`lessons.md`](lessons.md))

### 체크포인트 ID 명명

`<phase>.<sequence>` 형식. 예:
- `08.001` — 페이즈 08 의 첫 체크포인트 (스캐폴딩 완료 시점)
- `08.002` — 두 번째 (테스트 인프라 완료)
- `08.012` — 12번째 (모듈 N 구현 완료)
- `10.05.b` — 페이즈 10 의 5번째 스프린트의 b 버전 (멀티버스 분기)

### 체크포인트 산출물 구조

```
.ShipofTheseus/<프로젝트>/checkpoints/<phase>/<sequence>/
├── state.json         # 진행 상태 + frontmatter + 측정값 스냅샷
├── lesson.md          # 이 체크포인트에서 배운 것 (lessons.md 의 lesson_pack 호환)
├── snapshot/          # 작업 트리의 관련 모듈 코드 스냅샷 (회귀용)
└── meta.md            # 부모 체크포인트, 트리거 사유, 다음 후보 분기
```

## 회귀 알고리즘 — 실패 원인 → 회귀 위치 매핑

**모든 깊은 품질 위반이 회귀·재빚기 트리거**: DIP/SOLID 위반만이 아니라 1- 코드 오류 누적 2- 기획-구현 갭 (스펙 누락) 3- 성능/NFR 미달 4- 의도 표류 5- 정체/회귀 누적 6- 테스트 회귀 7- 천정 도달 8- scope creep 모두 동등한 트리거 — 차원만 달라질 뿐 어느 차원이라도 깊이가 임계를 넘으면 부분 수정 금지·해당 모듈 통째 재작성 (`re-architect`).

실패 (테스트 fail / 게이트 fail / 정체 / 천정 / 코드 오류 / 스펙 누락 / 성능 미달 / 의도 표류) 발생 시:

```python
def find_regression_target(
    failure: Failure,
    checkpoint_chain: list[Checkpoint],
) -> Checkpoint:
    """실패 원인을 분석해 회귀할 체크포인트를 결정. 인터럽트 없이 자율 결정."""

    # 분류 1: 의도 어긋남 (문서 vs 측정 결과 의미 차이)
    if failure.kind == "intent_mismatch":
        return find_checkpoint_at_phase(checkpoint_chain, "01")

    # 분류 2: 계획 어긋남 (모듈 분할이 측정과 충돌)
    if failure.kind == "plan_misfit":
        return find_checkpoint_at_phase(checkpoint_chain, "06")

    # 분류 3: 모듈 구현 잘못 (특정 모듈의 SOLID/DIP 위반)
    if failure.kind == "module_impl_violation":
        return find_module_checkpoint(checkpoint_chain, "08", failure.module)

    # 분류 4: 테스트 회귀 (직전 스프린트 대비 점수 하락)
    if failure.kind == "test_regression":
        return find_checkpoint_at_phase(checkpoint_chain, "10", before=failure.sprint)

    # 분류 5: 천정 도달 (resources.md)
    if failure.kind == "resource_ceiling":
        # NFR 임계 체크포인트 (페이즈 04) 로 회귀해 Q-D3 정책 적용
        return find_checkpoint_at_phase(checkpoint_chain, "04", subset="nfr")

    # 분류 6: 정체 누적 (lessons.md)
    if failure.kind == "stagnation":
        # 정체 차원에 책임 있는 모듈의 체크포인트 (08.NNN) 로
        return find_module_checkpoint(checkpoint_chain, "08", failure.module)

    # 분류 7: DIP / SOLID 깊은 위반 (rubric.md hard cap)
    if failure.kind == "dip_violation":
        # DIP 경계가 깨진 모듈 → 페이즈 06 (계획) 부터 모듈 경계 재정의 + rewrite
        return find_checkpoint_at_phase(checkpoint_chain, "06")

    # 분류 8: scope creep (의도 표류 — 페이즈 04 사전 위임 답과 모순 누적)
    if failure.kind == "scope_creep":
        return find_checkpoint_at_phase(checkpoint_chain, "04")

    # 분류 9: 코드 오류 누적 (동일 사상 버그 ≥ 3 모듈 또는 예외 흐름 비일관)
    if failure.kind == "code_error_cascade":
        # 사상의 책임 모듈을 통째 재작성 (lessons.md rewrite_rule.preserve=false)
        return find_module_checkpoint(checkpoint_chain, "08", failure.module)

    # 분류 10: 기획-구현 갭 (스펙 누락 — 의도/계획에 있던 항목이 구현에서 사라짐)
    if failure.kind == "spec_omission":
        # 페이즈 06 계획 부분 재정렬 + 해당 모듈 재작성
        return find_checkpoint_at_phase(checkpoint_chain, "06")

    # 분류 11: 성능 / NFR 미달 (게이트 6 깊은 미달, resources.md 천정 깊은 초과)
    if failure.kind == "nfr_violation":
        # 자료구조·알고리즘 재선정 필요 → 모듈 통째 재작성
        return find_module_checkpoint(checkpoint_chain, "08", failure.module)

    # 분류되지 않은 실패 — 가장 가까운 안정 체크포인트 (last_known_good)
    return last_known_good_checkpoint(checkpoint_chain)
```

회귀 후 **자동 진행**:
a- 회귀 위치의 산출물을 작업 트리로 복원 (`snapshot/` → 모듈 디렉터리).
b- 회귀 사유와 새 lesson_pack 을 다음 시도의 입력에 첨부 (`forbidden_strategies` 누적).
c- 같은 분기를 *3 회 회귀해도* 같은 실패면 멀티버스 분기로 전환 (한 우주의 한계 = 다른 우주 시도 신호).
d- [`autonomy.md`](autonomy.md) Q-D7 사전 위임 답에 따라 자율 적용 — 인터뷰 후 인터럽트 없음.

## 멀티버스 병렬 — 한 의사결정에서 N 우주 동시 분기

`competition.md` 가 한 페이즈 안의 후보 N개를 비교한다면, 멀티버스는 **여러 페이즈에 걸친 전체 경로** 를 N 우주로 분기한다.

### 트리거

a- 같은 의사결정 지점에서 회귀가 3 회 누적 (한 우주가 막혔다는 신호).
b- 비평가가 "두 접근의 *전체 결과* 가 어떻게 다를지 모르겠다" 표시 (페이즈 단위 비교 불가능).
c- 멀티버스를 명시 트리거하는 사용자 사전 위임 (Q-D7).

### 분기 구조

```
.ShipofTheseus/<프로젝트>/multiverse/<branch_id>/
├── universe-a/
│   ├── checkpoints/          # 우주 a 의 자기 체크포인트 체인
│   ├── intent/  plan/  impl/ # 우주 a 의 자기 산출물 (격리)
│   └── score.json            # 최종 점수 + 레슨 요약
├── universe-b/
│   └── ...
├── universe-c/                # 최대 3 우주 (비용 폭발 차단)
│   └── ...
└── verdict.md                # 우승 우주 + 사유 + 패자 보존 위치
```

### 우승 결정 알고리즘

```python
def select_universe(universes: list[Universe]) -> Universe:
    """다중 우주 비교 → 최적 우주 자율 선택 (인터럽트 없음)."""

    # 1. DIP 위반 우주 즉시 탈락 (rubric.md 의 hard cap)
    universes = [u for u in universes if not u.score.dip_violation]
    if not universes:
        # 모두 DIP 위반 = 의도 자체 모순 → autonomy.md 의 유일 예외 case
        return Resolution.HALT_FOR_INTENT_MISMATCH

    # 2. 종합 점수 비교
    universes.sort(key=lambda u: u.score.overall, reverse=True)
    top, runner = universes[0], universes[1] if len(universes) > 1 else None

    # 3. competition.md 의 resolve 알고리즘과 같은 임계 적용
    if runner is None or top.score.overall - runner.score.overall >= 0.05:
        # 압도적 우위 — top 채택, 나머지 우주는 multiverse/<id>/losers/ 로
        return Resolution.SELECT(winner=top, archive=universes[1:])

    # 4. 점수 근접 — 차원별 비교 + 코드 단순성 우선
    return Resolution.MERGE_OR_SIMPLER(...)
```

### 폐기되지 않는 우주 — 학습 자산

채택되지 않은 우주는 **삭제하지 않고** `multiverse/<branch_id>/losers/` 로 이동. 다음 멀티버스 분기 시 `forbidden_strategies` 에 그 우주에서 시도된 접근이 자동 누적되어 *같은 실패 반복 방지*. 닥터 스트레인지가 14,000,604 우주의 패배를 *기억* 해 한 우주를 찾아낸 것과 같은 원리.

## 체크포인트 회귀 + 멀티버스의 결합

```
페이즈 N 진행 중 실패 발생
  ↓
실패 원인 분석 (find_regression_target)
  ↓
회귀 위치 결정 (체크포인트 X.Y)
  ↓
같은 위치 3 회 회귀 누적?
  ├─ 아니오 → 단일 우주에서 lesson_pack 첨부 후 재시도
  └─ 예 → 멀티버스 분기 (2~3 우주 격리 병렬)
            ↓
       각 우주가 자기 체크포인트 체인 누적
            ↓
       모든 우주 임계 도달 또는 막힘
            ↓
       select_universe → 우승자 채택 + 나머지 학습 자산 보존
```

## 체크포인트 도구

[`../scoring/checkpoint.py`](../scoring/checkpoint.py) 가 다음 명령 제공:

a- `checkpoint create --phase NN --sequence MMM --snapshot <dir>` — 새 체크포인트 봉인.
b- `checkpoint list --phase NN` — 페이즈 N 의 모든 체크포인트 ID + 점수 + 시각.
c- `checkpoint regress --to <id>` — 지정 체크포인트로 작업 트리 복원 + lesson_pack 자동 생성.
d- `checkpoint find-target --failure <kind> --module <name>` — 회귀 매핑 자동 결정.
e- `checkpoint multiverse --branch <id> --universes N` — N 우주 분기 디렉터리 생성.

## Q-D7 사전 위임 (autonomy.md 추가)

```
질의: 체크포인트 회귀 정책?

선택지:
1. 자동 회귀 + 멀티버스 자동 분기 (가장 자율적, default — 닥터 스트레인지 모드)
2. 자동 회귀만 (멀티버스는 사용자 명시 시에만)
3. 회귀 없이 항상 fresh 시작 (단순, 학습 누적 없음)
```

## 안티 패턴

a- **체크포인트 없이 페이즈 단위만 봉인** — 실패 시 페이즈 통째 재실행 = 비용 폭발.
b- **회귀 위치를 사람이 매번 결정** — 본 컨벤션의 핵심 위반 (인터뷰 후 인터럽트 0).
c- **멀티버스 우주 5개 이상** — 비용 폭발. 최대 3.
d- **패자 우주 즉시 삭제** — 학습 자산 손실. 항상 `losers/` 로 보존.
e- **같은 위치 3 회 회귀해도 단일 우주 고집** — 정체 신호 무시. 멀티버스 자동 분기 룰.
f- **체크포인트 fingerprint 체인 무시** — `contracts.md` 의 무결성 위반, 페이즈 09 게이트 자동 fail.
g- **DIP 위반에만 rewrite 트리거 한정** — 코드 오류 누적·스펙 누락·NFR 미달·의도 표류 같은 *다른 깊은 위반* 도 동등한 통째 재작성 트리거 ([`lessons.md`](lessons.md) "부분 수정 vs 깨고 다시 작성" 표). 본 컨벤션 11 분류 (`code_error_cascade`/`spec_omission`/`nfr_violation`/`scope_creep`/...) 가 그 일반화.
