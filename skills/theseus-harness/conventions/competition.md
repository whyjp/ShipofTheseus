# 경쟁 병렬 컨벤션 (Competitive Parallelism)

## 한 줄 요약
**한 페이즈에서 명확한 단일 정답이 보이지 않으면, 2개 이상의 후보안을 격리 병렬로 동시 생성하고 점수로 경쟁시킨 뒤 우승자를 선택하거나 장점만 골라 머지한다.** 의도의 애매함은 페이즈 04 가 사용자 질의로 해소하지만, 구현·설계의 애매함은 LLM 에이전트의 비결정성 위에 놓인 문제 — 분기·경쟁·합병으로 정공법으로 극복한다.

## 트리거 조건

다음 중 하나라도 성립하면 경쟁 모드 진입:

a- 비평가(페이즈 05) 가 "대안 A·B 의 트레이드오프가 비슷, 사용자 결정도 어려움" 으로 보고.
b- 설계자(페이즈 06) 가 "두 모듈 분할안의 장단점이 길항" 으로 보고.
c- 구현자(페이즈 08) 가 "두 구현 방식이 모두 SOLID/테스트 통과 가능, 미감 차이만 있음" 으로 보고.
d- 플랜 재이해(페이즈 07) 의 콜드 리딩이 두 가지 다른 해석을 동시에 산출.
e- 같은 페이즈를 두 번 호출했는데 LLM 이 의미상 다른 결과를 출력 (비결정성 직접 노출).

## 격리

각 후보는 자기 디렉터리 안에서만 동작:

```
.ShipofTheseus/<프로젝트>/competitions/<phase>-<topic>/
├── meta.md                      # 트리거 사유, 후보 수, 평가 기준
├── a/
│   ├── <페이즈 산출물 동일 구조>
│   └── ...
├── b/
│   └── ...
├── c/                            # 선택적 — 3 후보까지 권고
│   └── ...
└── result.md                     # 점수, 우승자, 머지 내역
```

후보 디렉터리들은 **서로의 산출물을 절대 보지 않는다.** 격리는 정직한 비교의 전제.

## 병렬 디스패치

지휘자가 한 메시지에 다중 `Agent` 호출을 넣어 후보별 서브에이전트를 동시 기동:

```
Agent(model="opus", prompt="...후보 A 컨텍스트...")
Agent(model="opus", prompt="...후보 B 컨텍스트...")
Agent(model="opus", prompt="...후보 C 컨텍스트...")
```

각 에이전트는 같은 입력 (의도 / 비평 / 결정) 을 받지만 자기 산출 디렉터리만 본다. [`build-and-config.md`](build-and-config.md) §7 의 자원 가드 (RAM 50%, 동시 E2E 2개) 를 준수.

## 채점

a- 페이즈 06 (계획) 경쟁이라면 — `agents/plan-reviewer.md` 의 콜드 리딩 4 답을 *후보별 별도 fresh 에이전트* 로 받아 비교. 더 잘 인코딩된 안이 우승.
b- 페이즈 08 (구현) 경쟁이라면 — `quality-gate.md` 5 게이트 + `score.py` rubric 으로 후보별 점수 산출. **DIP 위반은 단독 hard cap 0.6** ([`../scoring/rubric.md`](../scoring/rubric.md)) 가 후보 탈락 기준.
c- 다른 페이즈는 그 페이즈의 자기 성공 기준에 맞춘 *비교 rubric* 을 `meta.md` 에 미리 정의.

## 선택 / 머지 프로토콜

점수 분포에 따라:

| 점수 차 | 행동 |
| ------- | ---- |
| Δ ≥ 0.05 | **선택** — 우승자 채택, 패자 디렉터리는 `competitions/.../losers/` 로 이동 (라이브 전 보존) |
| 0.02 ≤ Δ < 0.05 | **머지 검토** — critic 또는 planner 에이전트가 둘의 장점을 골라 합칠 수 있는지 판단 |
| Δ < 0.02 | **머지 강제** — 사실상 동등. 명시적 머지 산출물 생성 |

머지 산출물 `competitions/.../result.md` 의 본문:

```markdown
# 경쟁 결과 — <phase>-<topic>

## 후보별 점수
| 후보 | 점수 | DIP 위반 | 비고 |
| --- | ---: | -------- | ---- |
| a | 0.987 | 없음 | 모듈 분할 단순 |
| b | 0.972 | 없음 | 어댑터 다양성 우수 |

## 결정: 머지
b 의 어댑터 다양성을 a 의 모듈 분할 위에 얹는다.

## 머지 디테일
- a 의 `internal/auth/` 모듈 구조 채택
- b 의 `JWTAdapter`, `SessionAdapter` 두 어댑터 인터페이스 도입
- 충돌 지점: `AuthService` 인터페이스 시그니처 — a 의 시그니처 채택, b 의 메서드명만 이식
```

## 비결정성 극복의 두 메커니즘

a- **노이즈 분리** — 같은 입력에 LLM 이 표면 차이만 다르게 출력하면 두 후보의 점수가 거의 같다 (Δ < 0.02). 머지로 평균화.
b- **의미 분기 발견** — 의미상 다른 두 해석을 LLM 이 동시 산출하면 점수가 의미 있게 갈린다 (Δ ≥ 0.05). 우승자 채택.

이 두 케이스를 **자동 구분하는 것** 이 경쟁 프로토콜의 가치.

## 자동 resolve 알고리즘 (자율 결정의 핵심)

```python
def resolve_competition(candidates):
    """경쟁 후보를 받아 우승자/머지 안을 자율 결정. autonomy.md 위임 수준 1·2 면 ack 없이 적용."""
    # 1. DIP 위반 후보는 즉시 탈락
    candidates = [c for c in candidates if not c.score.dip_violation]
    if not candidates:
        return Resolution.HALT_AND_ASK_USER

    # 2. 점수 내림차순
    candidates.sort(key=lambda c: c.score.overall, reverse=True)
    top, runner = candidates[0], candidates[1] if len(candidates) > 1 else None
    delta = (top.score.overall - runner.score.overall) if runner else 1.0

    # 3. 단일 또는 압도적 우위 — SELECT
    if runner is None or delta >= 0.05:
        return Resolution.SELECT(winner=top, losers=candidates[1:])

    # 4. 사실상 동등 (< 0.02) — AUTO_MERGE 코드 단순성 우선
    if delta < 0.02:
        return Resolution.AUTO_MERGE(base=top, merge_from=runner,
                                      strategy=_choose_simpler(top, runner))

    # 5. 중간 영역 (0.02 ≤ Δ < 0.05) — 차원별 분석
    dim_winners = {d: max(candidates, key=lambda c: c.score.sub[d])
                   for d in ("correctness", "solid", "coverage", "e2e_pass")}
    if all(w is top for w in dim_winners.values()):
        return Resolution.SELECT(winner=top, losers=[runner])
    return Resolution.MERGE_BY_DIMENSION(winners_per_dim=dim_winners, base=top)
```

자율 결정 룰 (ack 없이 적용 — `autonomy.md` 위임 수준 1·2):

a- **Δ ≥ 0.05** → SELECT (top 채택, 패자는 `losers/`).
b- **0.02 ≤ Δ < 0.05** → 차원별 분석. 한쪽이 모든 차원 우위면 SELECT, 분점이면 MERGE_BY_DIMENSION.
c- **Δ < 0.02** → AUTO_MERGE (코드 단순성 — LOC 적음, 모듈 적음 우선).
d- **모두 DIP 위반** → HALT_AND_ASK_USER (설계 자체 문제).

### 차원별 분석 가중치 (resolve 전용)

| 차원 | 머지 가중 | 사유 |
| --- | -------: | ---- |
| `correctness` | 0.30 | 테스트 통과는 절대 |
| `solid` | 0.25 | DIP 외 SOLID 도 핵심 |
| `e2e_pass` | 0.20 | 사용자 시나리오 직접 |
| `coverage` | 0.15 | 적당 |
| `fe_be_parity` | 0.05 | 보조 |
| `scope_fit` | 0.05 | 보조 |

(rubric 의 *전체 점수* 가중과 다름 — 본 표는 *차원별 우열 비교* 용.)

### 자율 결정 산출물

`competitions/<phase>-<topic>/result.md` 에 다음 모두 기록 ([`autonomy.md`](autonomy.md) 의 사후 리뷰 가능성):

a- 점수 표 (후보별 종합 + 차원별)
b- 적용된 룰 (Δ ≥ 0.05 SELECT / Δ 중간 차원 분석 / Δ < 0.02 AUTO_MERGE)
c- 머지 전략 (코드 단순성 비교 결과 — LOC/모듈 수)
d- 패자 후보 디렉터리 위치 (`losers/`)
e- frontmatter (스킬 버전 / 페이즈 / 핑거프린트)

→ 사용자가 사후에 "이 결정이 왜 그렇게 났지" 확인 시 result.md 한 파일로 답.

## 사용자 ack 시점 — 사전 위임 자동 적용 (인터럽트 없음)

a- 점수 차 < 0.02 의 머지 결정 — 자동 (Q-D2 답 무관).
b- 점수 차 ≥ 0.05 의 우승자 선택 — 자동 (게이트가 객관적).
c- 비평가가 *전략적* 의미 있다 표시한 경쟁 (예: 인증 모드) — [`autonomy.md`](autonomy.md) **Q-D2 사전 위임 답** 자동 적용:
  c-1 Q-D2 답 = `1` (모든 resolve 자동) → 점수 우위 자동 채택.
  c-2 Q-D2 답 = `2` (비즈니스 함의도 자동) → 동일하게 점수 우위 자동.
  c-3 Q-D2 답 = `3` (비즈니스 함의는 정지) → 본 스킬 의도 위반, 페이즈 04 에서 비권장 표시되었으나 사용자가 선택했다면 정지.

[`timing.md`](timing.md) 라이브 보고 한 줄:

```
스프린트 NN 경쟁 (인증 모드: a 0.987 vs b 0.972) → Q-D2.1 자동 적용 (a 채택, b 의 리프레시 흐름은 보류 항목으로 누적).
```

인터뷰 종료 후 사용자에게 별도 ack 호출 절대 없음.

## 적용 페이즈 우선순위

a- **페이즈 06 (계획)** — 가장 큰 가치. 모듈 분할의 애매함을 여기서 해소하면 후속 모든 비용 절감.
b- **페이즈 08 (구현)** — 도메인 코어 같은 복잡 모듈에 한정. 단순 어댑터까지 경쟁시키면 비용 폭발.
c- **페이즈 11 (회귀 바이섹트)** — `revert` vs `re-architect` 권고가 길항할 때.
d- 다른 페이즈는 비용·이득 균형이 안 맞아 보통 적용 안 함.

## 안티 패턴

a- 모든 페이즈에 무조건 경쟁 — 비용 폭발, 가치 없음.
b- 후보 5개 이상 — 비교가 노이즈에 묻힘. 최대 3.
c- 후보 디렉터리끼리 산출물 공유 — 격리 위반, 점수 부정.
d- 점수 차 < 0.02 인데 우승자 강제 선택 — 노이즈를 의미로 오해. 머지 권고 무시 금지.

## 비용 가드

a- 한 페이즈에 경쟁 1회까지. 같은 페이즈에서 두 번 경쟁이 트리거되면 의도/계획 자체가 모호 → 페이즈 04 사용자 질의로 회귀.
b- 경쟁 중인 페이즈는 [`timing.md`](timing.md) 사용자 보고에 "경쟁 N 후보 진행 중" 명시 — 사용자가 비용·시간 사실 인지.
c- 동시 디스패치 후보 수는 [`models.md`](models.md) 의 모델 비용을 고려해 결정 — Opus 후보가 3개면 합리적, Sonnet 은 5개도 가능.
