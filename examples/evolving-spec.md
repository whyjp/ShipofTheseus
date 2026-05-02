# Example — Evolving Spec (도메인 미정착, G3)

## 시나리오

신규 SaaS 서비스의 *피드백 위젯* 을 만든다. 사용자 답이 모호 — "버튼 + 모달 + 백엔드" 같은 큰 그림은 있지만, 알림 채널 / 인증 / 데이터 보존 정책은 *진행 중에 좁혀지는* 도메인. 정확히 oh-my-ralph 의 `evolving-spec.md` 패턴.

## 호출 예시

```
/theseus-orchestrator
"피드백 위젯 — 사용자가 페이지 우하단 버튼으로 텍스트 + 평점 (1~5) 을
보낼 수 있다. Slack 채널로 알림. 운영자 대시보드는 후순위."
```

## 페이즈 04 답 예시 (사용자가 입력하는 부분)

### Q-G1 그레이드 확정

| 항목 | 답 |
| --- | -- |
| `grade_assess.py` 자동 추정 | G3 (다중 모듈, 단일 사이드 — FE 위젯 + BE 알림 라우터) |
| 사용자 확정 | **G3 — Standard** (12 페이즈 / 12 컨벤션 / 임계 0.97) |

### NFR (`spec-catalog.md` 자동 제안 후 사용자 확정)

| NFR | 권고 | 사용자 답 |
| --- | --- | --------- |
| latency p99 | 200ms | 1. 권고 채택 |
| 가용성 | 99.5% | 1. 권고 채택 |
| 동시 사용자 | 50 RPS | 1. 권고 채택 |
| 데이터 보존 | 90 일 | 4. 미확정 (게이트 비활성) — 운영 정책 후속 결정 |

### Q-D1 ~ Q-D7 (사전 위임 카탈로그, autonomy.md)

| 질의 | 답 | 의미 |
| ---- | -- | --- |
| Q-D1 회귀 권고 | 1 | 모든 권고 자동 적용 (revert / re-architect / accept) |
| Q-D2 경쟁 resolve | 1 | 모든 resolve 자동 (Δ ≥ 0.05 SELECT / Δ < 0.02 AUTO_MERGE) |
| Q-D3 천정 도달 | 1 | 권고 임계로 자동 조정 (측정 평균 × 1.05) |
| Q-D4 정체 누적 | 1 | 페이즈 06 (계획) 부터 자동 재시작 |
| Q-D5 패키지 업데이트 | 1 | asdf/nvm/goenv 안에서 자동 (시스템 영향 없음) |
| Q-D6 보고 빈도 | 1 | 매 결정 라이브 보고 (인터럽트 없음) |
| Q-D7 체크포인트 | 1 | 자동 회귀 + 멀티버스 자동 분기 (default) |

### Q-D8 Verification Commands (v0.3.0 신규, oh-my-ralph 차용)

**답: 2 — 새 검증 스니펫 작성**

evolving-spec 시나리오는 CI 가 아직 정착되지 않아 답 1 (CI 그대로) 가 부적합. 사용자가 acceptance criteria 별로 단순 스모크부터 작성하고, 도메인이 좁혀지면서 추가:

```
[SC-1] 위젯 버튼 클릭 시 모달이 5초 안에 열린다 | Verification: pytest tests/widget/test_smoke.py::test_modal_opens_within_5s
[SC-2] 평점 + 텍스트 제출이 Slack 에 도달한다  | Verification: pytest tests/integration/test_slack_delivery.py
[SC-3] 빌드 성공                                 | Verification: bun run build
```

`intent/04-verification.md` 의 `Verification Commands` 블록:

```bash
# Run from repo root.
pytest tests/widget/test_smoke.py -v
pytest tests/integration/test_slack_delivery.py -v
bun run build
```

frontmatter:
```yaml
commands_count: 3
manual_only: false
entry_blocked: false
```

## 예상 진행

1. **페이즈 05 비평** — Slack webhook 직접 호출 vs 메시지 큐 경유 미스초이스 식별 → 90 일 동안 단일 webhook 으로 충분, 그 후 큐 도입 권고를 `intent/05-decisions.md` 에 기록.
2. **페이즈 06 계획** — `widget/` `notifier/` `api/` 3 모듈로 SoC. 시퀀스 다이어그램 자동 생성.
3. **페이즈 08 구현** — 3 모듈 병렬 (RAM 50% 가드 안에서). 위젯 = bun + React, notifier = Go (백엔드 기본값), api = Go.
4. **페이즈 10 스프린트** — 임계 0.97 (G3) 까지 무한 루프. 정체 시 lessons.md 자동 적용.
5. **페이즈 12 웹뷰** — `bun run dev` 로 6 탭 대시보드 (Mermaid 자동 렌더).

## 미니 회로 — Q-D8 답 누락 시

페이즈 04 마지막에 Q-D8 답을 입력 안 하면 `intent/04-verification.md` 의 frontmatter 가 `entry_blocked: true` 로 박혀 페이즈 05 의 [`agents/critic.md`](../skills/theseus-harness/agents/critic.md) 가 `SkillEntryError` 로 거부:

```
SkillEntryError: Q-D8 Verification Commands 부재 — oh-my-ralph 룰 차용.
intent/04-verification.md 의 bash 블록을 채우거나 manual_only=true 로 표시 후 재시도.
검증 없는 자율 진행은 본 하네스가 거부.
```

이 메시지를 받은 사용자는 다시 페이즈 04 로 돌아가 Q-D8 답 입력 — 본 하네스의 *유일한* 인터럽트 지점이 그곳이기 때문.
