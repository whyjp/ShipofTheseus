# Example — Frozen Spec (도메인 명확, G4)

## 시나리오

성숙한 코드베이스 (예: 100k LOC SaaS) 에 *결제 통합* 을 추가한다. PRD 가 충실히 작성되어 있고 CI 도 정착. 본 하네스가 PRD 처리 룰 ([`interview.md`](../skills/theseus-harness/conventions/interview.md) "PRD/스펙 입력 처리" 절, v0.4.0 PR-13 흡수) 로 인터뷰 스킵 금지를 강제하지만, *답 자체는 PRD 의 1번 보기 1 클릭* 으로 빠르게 통과.

## 호출 예시

```
/theseus-harness
"<docs/PRDs/2026-Q2-payments-prd.md> 첨부. Stripe 통합 + 결제 영수증
이메일 + 환불 처리. 코드베이스: services/billing/. 임계 0.999."
```

## 페이즈 04 답 예시

### Q-G1 그레이드 확정

| 항목 | 답 |
| --- | -- |
| 자동 추정 | G5 (결제 키워드 매칭, mission-critical) |
| 사용자 확정 | **G5 — Mission Critical** (14 페이즈 풀 + 빡빡 모드 / 임계 0.99999) |

> 결제 / 금융 / 안전 시스템은 G5 자동. 사용자가 G4 로 강하 시도 시 `grade_assess.py` 가 경고.

### Q-D1 ~ Q-D7 (PRD 매핑 + 사용자 확정)

| 질의 | PRD 매핑 (1번) | 답 |
| ---- | ------------- | -- |
| Q-D1 회귀 | "회귀 시 즉시 정지 + 인간 검토" | **3** (모두 정지) — G5 도메인은 인간 ack 필수 |
| Q-D2 경쟁 | "단일 안 채택" | 1 (자동) |
| Q-D3 천정 | "리소스 업그레이드 사전 동의 됨" | 2 (자동 변경) |
| Q-D4 정체 | "재시작 자율" | 1 |
| Q-D5 업데이트 | "변경 금지 — production lock" | 3 (현재 버전 유지) |
| Q-D6 보고 | "스프린트마다" | 2 (스프린트 종료 누적) |
| Q-D7 체크포인트 | "자동 회귀만, 멀티버스 명시 시" | 2 |

각 답에 `user_explicit_confirmation: true` + `prd_evidence_cited: true` + `confirmed_at` 박힘.

### Q-D8 Verification Commands

**답: 1 — CI 명령 그대로 사용**

frozen-spec 시나리오는 CI 가 정착되어 그대로 차용:

```
[SC-1] 단위 테스트 통과            | Verification: npm test
[SC-2] 타입 체크 통과              | Verification: npm run typecheck
[SC-3] Stripe 통합 테스트 통과     | Verification: npm run test:integration:stripe
[SC-4] 결제 e2e 통과 (Playwright)  | Verification: npm run test:e2e -- --grep payments
[SC-5] 빌드 성공                   | Verification: npm run build
[SC-6] 보안 스캔 통과              | Verification: npm audit --audit-level=high
```

`intent/04-verification.md`:

```bash
# Run from repo root. Production-grade verification.
npm test
npm run typecheck
npm run test:integration:stripe
npm run test:e2e -- --grep payments
npm run build
npm audit --audit-level=high
```

frontmatter:
```yaml
commands_count: 6
manual_only: false
entry_blocked: false
```

## 예상 진행 (G5 의 빡빡 모드)

1. **페이즈 05 비평** — PRD 의 미스초이스 적극 적대. 예: "결제 retry 큐 부재" → critic 이 대안 추가, `intent/05-decisions.md` 에 기록.
2. **페이즈 06 계획** — TODO DAG 에 보안 검토 별 토글 강제. 시퀀스 다이어그램 의무.
3. **페이즈 08 구현** — DIP 위반 단독 hard cap 0.6 → 어댑터 분리 강제. Stripe SDK 직접 import 금지, port 인터페이스 통한 호출만.
4. **페이즈 09 게이트** — 5 게이트 + Phase V 측정 유효성 모두 통과. 임계 0.99999 미달 시 무한 스프린트.
5. **페이즈 10 ~ 11 스프린트 + 회귀 바이섹트** — 점수 0.05 하락 시 즉시 페이즈 11 발동. Q-D1=3 이라 인간 ack 대기 (인터럽트 허용 — G5 예외).
6. **페이즈 13 핸드오프** — PR 자동 생성 (Q-D6 답에 따라).

## 비교 — oh-my-ralph 의 `frozen-spec.md` 차이

oh-my-ralph 는 frozen-spec 일 때 *루프 시작 후 인간 개입 없음* 을 원칙으로 한다 (autonomy 최대). 본 하네스는 G5 (Mission Critical) 일 때 *오히려* 인간 ack 를 강제 — Q-D1 답 3 으로 회귀 권고 정지를 사용자가 결재. 결제 / 금융 도메인의 사고 비용을 자율성보다 우선.

> 본 하네스의 G2/G3/G4 는 ralph 와 비슷한 max-autonomy 모드. **G5 만 다름**.
