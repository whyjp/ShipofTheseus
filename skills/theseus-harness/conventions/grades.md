# 그레이드 시스템 — 작업 복잡도별 허들 구조

## 한 줄 요약
**14 페이즈 + 26 컨벤션 풀세트는 *복잡 작업* 의 비용을 정당화하지만, *단순 작업* 에는 over-engineering.** 본 하네스 호출 직후 그레이드를 자동 추정 + 사용자 객관식 확정해 그레이드별 페이즈/컨벤션을 활성화한다. **그레이드는 본 하네스의 내부 동작 (복잡도 / 페이즈 수 / 컨벤션 / 임계 / 멀티버스 / 모델 라우팅) 만 모듈레이션. 진행/거부에는 관여하지 않는다.**

## 5 그레이드

| Grade | 별칭 | 작업 예 | 페이즈 | 컨벤션 | 멀티버스 | 임계 |
| ----- | ---- | ------ | ------ | -----: | -------- | ---: |
| **1** | Trivial | 한 줄 수정, 리네임, 기계적 리팩터, throwaway | **TBD (v0.5.x 후속)** | 0 | X | TBD |
| **2** | Simple | 단일 모듈 작은 기능 (~100 LOC), 명확한 스펙 | 01+04+06+08+09 (5) | 7 (interview/timing/contracts/models/build-and-config/lessons/fragmentation) | X | 0.95 |
| **3** | Standard | 도메인 정착 + 단일 sprint 충분 + *외부 evaluator 없음* (내부 작업 한정). v0.9.8: external-evaluator (벤치/채점/리더보드) 작업 → 자동 G4 escalation | 00-09 + 10(3 sprint cap) + 13 (12) | 12 (Grade 2 + diagrams/stack/spec-catalog/resources/checkpoints) | X | 0.97 |
| **4** | Complex | FE+BE / 새 도메인 / SOLID 경계 리팩터 / **외부 evaluator 작업** (벤치마크 / 채점 / 외부 PR 등) (v0.9.8 default for non-trivial) | 14 풀 + sprint regression loop 의무 | 28 (전부 + sprint-regression-loop + parallel-cold-review) | 옵션 (Q-D7=1 시) | 0.999 |
| **5** | Mission Critical | 결제/금융/안전 시스템 / 회복 불가 변경 | 14 풀 + 빡빡 모드 | 26 + 추가 가드 | 강제 | 0.99999 |

### 빡빡 모드 (Grade 5 추가 가드)

a- DIP cap 0.6 → 0.4 (위반 시 더 큰 패널티).
b- 회귀 임계 0.05 → 0.02 (작은 회귀도 즉시 페이즈 11 트리거).
c- Q-D 답 옵션 1 (모두 자동) → 옵션 2 (회귀만 자동) 강제.
d- 멀티버스 우주 수 2~3 → 3~5.
e- 페이즈 11 회귀 바이섹트도 자율 적용 — 본 하네스의 핵심 원칙 (페이즈 04 외 인터럽트 0). G5 빡빡 모드라도 ack 강제 안 함, multiverse + bisect 가 자율 정정 인프라.

## 그레이드 자동 추정 알고리즘 (`scoring/grade_assess.py`)

원문 키워드 + 도메인 매칭 + 모듈 수 추정으로 그레이드 후보 산출:

```python
def assess_grade(request_text: str, repo_context: dict) -> GradeReport:
    """
    원문에서 다음 신호 추출:
      - 도메인 키워드 (결제/금융/안전 → Grade 5 후보)
      - 모듈/사이드 키워드 (FE+BE / 다중 모듈 → Grade 4 후보)
      - 단순 동사 (rename/typo/oneline → Grade 1)
      - 모호 신호 → Grade 3 default
    """
    triggers_g5 = ["결제", "금융", "payment", "billing", "안전", "safety", "의료", "medical"]
    triggers_g4 = ["FE+BE", "프론트엔드", "백엔드", "frontend", "backend", "신규 도메인", "새 도메인", "리팩터", "refactor",
                   # v0.9.8: external-evaluator 작업 자동 G4 escalation
                   "벤치마크", "benchmark", "leaderboard", "리더보드", "외부 채점", "external eval",
                   "PR 제출", "submission", "심사", "review process", "competition"]
    triggers_g2 = ["단일 모듈", "single module", "작은 기능", "small feature", "추가", "add"]
    triggers_g1 = ["한 줄", "oneline", "one line", "rename", "리네임", "typo", "오타", "버그 수정", "throwaway"]

    text_lower = request_text.lower()
    candidates = []

    if any(t in text_lower or t in request_text for t in triggers_g5):
        candidates.append((5, "도메인 키워드 일치 (결제/금융/안전 등)"))
    if any(t in text_lower or t in request_text for t in triggers_g4):
        candidates.append((4, "FE+BE 또는 신규 도메인 키워드"))
    if any(t in text_lower or t in request_text for t in triggers_g2):
        candidates.append((2, "단일 모듈 작은 기능 키워드"))
    if any(t in text_lower or t in request_text for t in triggers_g1):
        candidates.append((1, "Trivial 키워드 — TBD (v0.5.x 후속)"))

    if not candidates:
        candidates.append((3, "키워드 매칭 없음 — Standard default"))

    # 가장 높은 그레이드를 기본 후보로 (보수적)
    candidates.sort(key=lambda x: -x[0])
    primary = candidates[0]
    return GradeReport(
        primary_grade=primary[0],
        primary_reason=primary[1],
        all_candidates=candidates,
        require_user_confirmation=True,  # 항상 페이즈 04 의 Q-G1 으로 확정
    )
```

## Q-G1 — 페이즈 04 의 첫 질의 (모든 그레이드 공통)

```
질의: 본 작업의 그레이드를 확정해주세요.

자동 추정: Grade 4 (FE+BE 키워드 일치).
페이즈 수와 컨벤션 적용 범위가 그레이드에 따라 달라집니다.

선택지:
1. Grade 1 (Trivial) — TBD (v0.5.x 후속, 현재는 진행 가능)
2. Grade 2 (Simple) — 5 페이즈 / 7 컨벤션 / 임계 0.95
3. Grade 3 (Standard) — 12 페이즈 / 12 컨벤션 / 임계 0.97
4. Grade 4 (Complex) — 14 페이즈 풀 / 26 컨벤션 / 임계 0.999 (자동 추정)
5. Grade 5 (Mission Critical) — Grade 4 + 빡빡 모드 / 임계 0.99999
```

답을 `intent/04-grade.md` 에 기록. 이후 모든 페이즈가 본 답을 입력으로.

## 그레이드의 역할 — 내부 모듈레이션만

a- 그레이드는 *내부 동작 모듈레이션* 만 한다 — 페이즈 수, 컨벤션 적용, 임계, 멀티버스 분기 수, 모델 라우팅 (haiku/sonnet/opus).
b- **진행/거부 결정에는 관여하지 않는다.** 본 하네스는 호출되면 *항상* 진행한다. G1 (Trivial) 도 진행 (단, v0.5.x 후속 PR 에서 G1 의 모듈레이션을 가장 가볍게 정의 예정).
c- self_lint C-GS 룰: grade 단어가 entry/blocked/reject/거부/종료 와 결합된 표현 검출 시 fail.

## 그레이드별 컨벤션 적용 매트릭스

| 컨벤션 | G2 Simple | G3 Standard | G4 Complex | G5 Critical |
| ------ | :------: | :--------: | :--------: | :---------: |
| interview.md | ✅ | ✅ | ✅ | ✅ |
| timing.md | ✅ | ✅ | ✅ | ✅ |
| contracts.md (frontmatter) | ✅ | ✅ | ✅ | ✅ |
| models.md (Opus/Sonnet/Haiku) | ✅ | ✅ | ✅ | ✅ |
| build-and-config.md | ✅ | ✅ | ✅ | ✅ |
| lessons.md | ✅ | ✅ | ✅ | ✅ |
| fragmentation.md | ✅ | ✅ | ✅ | ✅ |
| diagrams.md | ⚠️ 마인드맵만 | ✅ | ✅ | ✅ |
| stack.md | — | ✅ | ✅ | ✅ |
| spec-catalog.md | — | ✅ | ✅ | ✅ |
| resources.md | — | ✅ | ✅ | ✅ |
| autonomy.md | ⚠️ Q-G1만 | ✅ Q-D1-D6 | ✅ Q-D1-D7 | ✅ |
| competition.md | — | — | 옵션 | ✅ 강제 |
| plan-tree.md | — | ✅ (폭 2 / 깊이 1) | ✅ (폭 3 / 깊이 1, 옵션 2) | ✅ 강제 (폭 5 / 깊이 2) |
| runtime-prereq.md (Q-D9) | 옵션 | ✅ | ✅ | ✅ + 실 모드 강제 (mock 금지) |
| checkpoints.md | — | — | 옵션 | ✅ 강제 |
| test-invariants.md | — | ✅ | ✅ | ✅ |
| dacapo.md | — | — | ✅ | ✅ |
| spec-catalog (NFR 게이트 6) | — | ⚠️ 일부 | ✅ | ✅ |

## 그레이드별 페이즈 활성화

| 페이즈 | G2 | G3 | G4 | G5 |
| ----- | :-: | :-: | :-: | :-: |
| 00 명명 | — | ✅ | ✅ | ✅ |
| 01 의도 + 마인드맵 | ✅ | ✅ | ✅ | ✅ |
| 02 의도 리뷰 | — | ✅ | ✅ | ✅ |
| 03 콜드 재이해 | — | ✅ | ✅ | ✅ |
| 04 사용자 질의 + Q-G1/Q-D | ✅ | ✅ | ✅ | ✅ |
| 05 비평 | — | ✅ | ✅ | ✅ |
| 06 계획 | ✅ | ✅ | ✅ | ✅ |
| 07 계획 재이해 | — | — | ✅ | ✅ |
| 08 구현 | ✅ | ✅ | ✅ | ✅ |
| 09 게이트 | ✅ | ✅ | ✅ | ✅ |
| 10 스프린트 루프 | — | ⚠️ 3 sprint cap | ✅ 무한 | ✅ 무한 |
| 11 회귀 바이섹트 | — | — | ✅ | ✅ |
| 12 웹뷰 자동 생성 | — | ⚠️ 단순 | ✅ | ✅ |
| 13 핸드오프 | ✅ | ✅ | ✅ | ✅ |

## 그레이드 다운그레이드 권고 (자율)

자동 추정 < 사용자 답 (예: 자동 G2, 사용자 G4) → 본 하네스가 *다운그레이드 권고* :

```
[자율 결정] 자동 추정은 Grade 2 (단일 모듈) 인데 Grade 4 로 진행 선택. 비용 ~5배.
정말 진행하시겠습니까? (페이즈 05 진입 전 마지막 확인)

선택지:
1. 그대로 Grade 4 진행 (사용자 책임)
2. Grade 2 로 다운그레이드
3. Grade 3 절충
```

자동 추정 > 사용자 답 (예: 자동 G4, 사용자 G2) → 본 하네스가 *업그레이드 권고* (위험 명시):

```
[자율 결정] 자동 추정은 Grade 4 (FE+BE) 인데 Grade 2 로 진행 선택. 위험: 다중 모듈
의존이 미검증, FE/BE 패리티 게이트 비활성, 임계 0.95 로 완화.

선택지:
1. 그대로 Grade 2 진행 (위험 본인 부담)
2. Grade 4 로 업그레이드 (자동 추정 채택)
3. Grade 3 절충
```

## 안티 패턴

a- **Grade 판정 없이 풀 14 페이즈 진행** — 단순 작업에 over-engineering. 본 컨벤션 핵심 위반.
b- **Grade 를 진행/거부 게이트로 사용** — 그레이드는 내부 모듈레이션만. G1 답이어도 진행한다.
c- **자동 추정만 믿고 사용자 확정 생략** — Q-G1 은 *모든 그레이드 공통* 의무 질의. 자동 추정은 *후보* 일 뿐.
d- **그레이드 중간 변경** — 페이즈 04 답이 source of truth. 페이즈 05 이후 그레이드 변경은 페이즈 04 재진입 의미.
e- **빡빡 모드 (G5) 인데 Q-D 답이 옵션 1 (최대 자율)** — G5 는 보수적 옵션 강제. 페이즈 04 에서 자동 보정 + 사용자 알림.

## 자기 평가에서의 적용

본 저장소 (`theseus-self`) 의 자기 평가 그레이드 = **Grade 5 (Mission Critical)** — 본 하네스 자체는 *다른 모든 프로젝트의 신뢰 담보 도구* 이므로 가장 빡빡한 표준 적용.

a- 임계 0.99999 (G5 표준).
b- 모든 26 컨벤션 적용.
c- 멀티버스 강제 (회차마다 분기 가능).
d- DIP cap 0.4 (현재 0.6 보다 빡빡).
e- 회귀 임계 0.02 (현재 0.05 보다 빡빡).

위 강화는 v0.3.0 의 BOOTSTRAP.md 갱신 후보.

## 멀티버스 폭 확장 (sprint-05-b)

본 하네스의 강점 = *다차원 동시진행* (plan-tree N universe + 경쟁 + 머지). 폭이 좁으면 디자인 다양성 부족 — *동급 외부 스킬 (plan-mode 96 / ouroboros 97)* 을 능가하려면 폭 확장 필수.

| Grade | sprint-05-a 까지 (default) | sprint-05-b 후 (확장 default) | 사유 |
|----|:-:|:-:|----|
| G3 Standard | 폭 2 / 깊이 1 | **폭 3 / 깊이 1** | 단일 사이드 작업도 3 디자인 후보 비교 → process/data/sync 등 ≥3 axis |
| G4 Complex | 폭 3 / 깊이 1 | **폭 4 / 깊이 1** | FE+BE 의 본질적 다차원 (frontend stance × backend stance) 표현 |
| G5 Critical | 폭 5 / 깊이 2 | **폭 6 / 깊이 2** | 미션 크리티컬은 6 후보 head-to-head 비교 + 깊이 2 의 자식 분기 |

폭 확장 트레이드오프 :
a- **비용** : 폭 N → planner sub-agent N 회 호출. wall-clock = max(N) (병렬). 토큰 = sum(N).
b- **메모리** : N 병렬 sub-agent 의 메모리 합 → [`resources.md`](resources.md) 의 universe N 병렬 budget profile (sprint-05-b) 가 가드.
c- **머지 복잡도** : 후보 ↑ → tournament resolve 알고리즘 부담 ↑. [`competition.md`](competition.md) 의 자동 머지 알고리즘 (sprint-05-b) 강화로 흡수.

폭 축소 옵션 — 사용자 시간/비용 압박 시 Q-D3 답으로 폭 축소 가능 (G3 폭 2 / G4 폭 3 등). default 만 확장.
