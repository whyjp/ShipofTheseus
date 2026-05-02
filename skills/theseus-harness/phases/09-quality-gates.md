# Phase 09 — 5종 품질 게이트

## 한 줄 요약
**테스트 실행 전에 다섯 게이트로 *코드 모양* 을 감사한다.** 모양이 어긋나면 다음 스프린트가 잘못된 형태에 시간을 소진한다.

## 5 게이트

| # | 게이트 | 무엇을 보는가 | fail 신호 |
| - | ----- | ------------ | -------- |
| 1 | **의도 일치** | 만든 것이 `01-intent.md` + `04-answers.md` + `05-decisions.md` 와 맞는가 | 요청 안 한 기능 등장, 또는 요청 기능 누락 |
| 2 | **범위 규율** | 계획 외 변경 있는가 | TODO 가 인가하지 않은 파일 변경 |
| 3 | **SOLID** | 모듈별 SRP/OCP/LSP/ISP/DIP | 변경 사유 2개 클래스, 포트 자리에 콘크리트 |
| 4 | **테스트 모양** | 모든 public 표면에 단위, 모든 교차 모듈 경로에 통합, 사용자 시나리오 happy-path E2E | public 함수에 테스트 없음, 모듈에 페이크 없음 |
| 5 | **FE/BE 패리티** | 양쪽 모두 동등한 테스트 깊이 | BE 80% 커버리지 + FE 스냅샷만 |
| 6 | **NFR 일치** | `intent/01-intent.md` 의 ✅ NFR 항목별 페이즈 10 측정 결과가 임계 만족 — [`../conventions/spec-catalog.md`](../conventions/spec-catalog.md) | p99 200ms 약속이 280ms 측정 / 가용성 99.95% 인데 99.8% / LCP 2.5s 인데 3.4s. ⏸ (미확정) 항목은 자동 skip, fail 아님 |

## 입력
- `intent/01-intent.md`, `intent/04-answers.md`, `intent/05-decisions.md`
- `plan/06-plan.md`, `impl/08-impl-log.md`
- 디스크 위 실제 코드 — 에이전트는 로그 믿지 말고 파일 Read.

## 서브에이전트
[`../agents/quality-gate.md`](../agents/quality-gate.md).

## 산출물
`quality/09-quality-gate.md`:

ⓐ 게이트마다 `pass` | `fail` + 증거 (`경로:라인` 인용).
ⓑ fail 마다 remediation TODO (`T-NNN-fix`) — 계획에 폴드백.
ⓒ 종합 판정: `proceed` | `remediate-then-proceed` | `halt`.

## 헤더 시간 정보 검증

각 페이즈 산출물 헤더에 [`../conventions/timing.md`](../conventions/timing.md) 의 시간 메타가 빠지면 자동 fail (게이트 1 의 일부).

## 지휘자 후속

ⓐ `proceed` → 페이즈 10.
ⓑ `remediate-then-proceed` → 페이즈 08 을 fix-TODO 만 재실행 → 페이즈 09 재실행.
ⓒ `halt` → 사용자 질의. 구조적 문제.
