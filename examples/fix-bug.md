# Example — Fix Bug (단일 모듈 버그 수정, G2)

## 시나리오

기존 코드베이스의 *로그인 회귀* 한 건 수정. 이슈 트래커에 재현 절차 + 스택트레이스 있음. G2 미니 모드 — 5 페이즈 / 7 컨벤션 / 임계 0.95 만으로 충분.

## 호출 예시

```
/theseus-harness
"이슈 #842 — OAuth 토큰 갱신 시 401. 재현: 1) 1시간 idle, 2) /api/me 호출.
재현 테스트 tests/auth/test_token_refresh.py::test_refresh_after_idle
는 *현재 fail*. 본 PR 에서 빨간 → 초록 + 회귀 가드."
```

## 페이즈 04 답 예시

### Q-G1 그레이드 확정

| 항목 | 답 |
| --- | -- |
| 자동 추정 | G2 (단일 모듈, ~50 LOC 변경 예상) |
| 사용자 확정 | **G2 — Simple** (5 페이즈 / 7 컨벤션 / 임계 0.95) |

> G1 (Trivial — typo / rename) 답이면 본 하네스 즉시 종료 + 단순 응답 권고. 본 시나리오는 *재현 테스트가 fail* 이라 단순 회귀가 아닌 G2 가 정확.

### Q-D1 ~ Q-D7 (G2 단순 모드 — 사전 위임 최소)

| 질의 | 답 | 의미 |
| ---- | -- | --- |
| Q-D1 회귀 | 1 | 자동 적용 |
| Q-D2 경쟁 | 1 | 자동 (단일 모듈이라 경쟁 트리거 거의 없음) |
| Q-D3 천정 | 1 | 자동 |
| Q-D4 정체 | 2 | 임계 자동 완화 (G2 는 임계 0.95 라 보통 정체 안 옴) |
| Q-D5 업데이트 | 3 | 업데이트 없이 — 버그 수정만 |
| Q-D6 보고 | 3 | 핸드오프에서만 (단일 PR 흐름) |
| Q-D7 체크포인트 | 2 | 자동 회귀만 (멀티버스는 G2 에 과대) |

### Q-D8 Verification Commands

**답: 1 — CI 명령 그대로 + 회귀 케이스 추가**

```
[SC-1] 회귀 케이스 통과 (이번 PR 의 핵심)         | Verification: pytest tests/auth/test_token_refresh.py::test_refresh_after_idle -v
[SC-2] 기존 auth 모듈 회귀 없음                    | Verification: pytest tests/auth/ -v
[SC-3] 전체 단위 테스트 통과                        | Verification: pytest --tb=no -q
[SC-4] 타입 체크 통과                              | Verification: mypy src/auth/
```

`intent/04-verification.md`:

```bash
# Run from repo root. Bug-fix verification.
pytest tests/auth/test_token_refresh.py::test_refresh_after_idle -v
pytest tests/auth/ -v
pytest --tb=no -q
mypy src/auth/
```

frontmatter:
```yaml
commands_count: 4
manual_only: false
entry_blocked: false
```

## 예상 진행 (G2 미니 모드)

1. **페이즈 00 ~ 04** — 명명·의도·인터뷰. PRD 가 *이슈 본문* 으로 입력 → [`prd-handling.md`](../skills/theseus-harness/conventions/prd-handling.md) 의 1 클릭 확정 흐름.
2. **페이즈 05 비평 스킵** — G2 미니 모드는 비평 페이즈 부분 스킵 (단일 모듈 + 명확한 회귀 케이스라 비평이 미스초이스 잡을 표면 좁음). 단 critic 이 *한 줄* 이라도 적대적 의견 출력 — 동의로만 끝나지 않음.
3. **페이즈 06 ~ 07 계획** — TODO 1 ~ 3 개. 시퀀스 다이어그램 의무는 유지.
4. **페이즈 08 구현** — 단일 모듈 패치 + 회귀 가드 테스트.
5. **페이즈 09 게이트 + 페이즈 10 스프린트** — 임계 0.95. 보통 1 스프린트로 통과.
6. **페이즈 12 웹뷰** — G2 미니 모드도 자동 생성 (작은 PR 도 웹뷰 검토 가능).
7. **페이즈 13 핸드오프** — PR 자동 생성 (Q-D6=3 이라 핸드오프 시점 일괄 보고).

## G2 vs G3+ 의 회귀 가드 강도

G2 는 *단일 회귀 케이스* 를 본 PR 의 절대 통과 조건으로. G3+ 는 *다중 회귀 짝* (paired_with) 까지 강제. 둘 다 `interview.md` §2-2 의 confirmation regression 패턴 적용 — 본 시나리오는 단일 짝.

## 흔한 실패 모드

ⓐ **G1 으로 강하 유혹** — "그냥 한 줄 수정인데" 라며 G1 선택 시 본 하네스가 종료. 그러나 *재현 테스트 fail → 빨간 → 초록* 흐름은 G1 이 다룰 수 없는 작업 (단순 응답 권고가 부적합). G2 가 최소 단위.
ⓑ **Q-D8 답 3 (manual only) 선택 유혹** — 버그 수정은 *자동 회귀 가능* 한 도메인이므로 답 3 부적합. 답 1 (CI + 회귀 케이스 추가) 또는 답 2 (회귀 케이스만 신규) 가 정상.
