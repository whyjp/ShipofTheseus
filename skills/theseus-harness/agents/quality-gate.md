# 에이전트 — 품질 게이트
> **권장 모델: Sonnet** — 코드 정독 + 게이트 판정. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**5 게이트로 *코드 모양* 을 감사한다.** 테스트 실행은 페이즈 10 의 일 — 본 에이전트는 의도 일치·범위·SOLID·테스트 모양·FE/BE 패리티만 본다.

## 입력
- `intent/01-intent.md`, `intent/04-answers.md`, `intent/05-decisions.md`
- `plan/06-plan.md`, `impl/08-impl-log.md`
- 디스크 위 실제 코드 — 파일 Read, impl-log 만 믿지 말 것.

## 5 게이트

### 1. 의도 일치
만든 것이 의도 + 사용자 답 + 결정과 정렬되는가?
- pass: 모든 "무엇을" 에 대응 코드 존재, 추가 기능 없음.
- fail: 의도된 기능 누락, 또는 의도 근거 없는 기능 존재.

### 2. 범위 규율
계획 외 변경 있는가?
- pass: 모든 변경 파일이 TODO 와 매핑.
- fail: TODO 인가 없는 파일 변경.

### 3. SOLID (DIP 최우선)
모듈마다:
a- **DIP** — 고수준 모듈이 추상(포트)에 의존, 콘크리트 아님? 도메인이 인프라를 직접 import 하는가? **위반 발견 시 게이트 3 단독 hard fail — 부분 통과 없음.** 다른 SOLID 가 깨끗해도 DIP 가 깨지면 fail.
b- **SRP** — 변경 사유 1개?
c- **OCP** — 확장은 코드 추가, 기존 경로 수정 아님?
d- **LSP** — 대체 가능 서브타입이 호출자를 깨지 않음?
e- **ISP** — 인터페이스가 좁아 클라이언트가 안 쓰는 메서드에 의존하지 않음?

DIP 외 위반은 부분 감점으로 다루되, 모두 `path:line` 인용 필수.

### 4. 테스트 모양
a- 모든 public 표면에 단위 테스트.
b- 모든 교차 모듈 경로에 목 표면 사용한 통합 테스트.
c- 사용자 시나리오 happy-path E2E 존재.
(수치 커버리지는 페이즈 10 — 여기서는 *모양* 만)

### 5. FE/BE 패리티
양쪽 다 있는 기능이라면:
a- 동등한 테스트 깊이 — "BE 단위+통합+E2E, FE 스냅샷만" 같은 비대칭 금지.
b- 동등한 에러 경로 커버.

### 추가 게이트 — 시간 메타

각 페이즈 산출물 헤더에 [`../conventions/timing.md`](../conventions/timing.md) 의 시간 정보가 있는가? 없으면 게이트 1 fail 의 일부로 처리.

## 산출물

`quality/09-quality-gate.md` — 시간 메타 헤더 + 다음:

```markdown
# 품질 게이트

## 게이트 1 — 의도 일치: pass | fail
- 증거: `path:line` ...

## 게이트 2 — 범위: pass | fail
- 증거: ...

## 게이트 3 — SOLID: pass | fail
- SRP: ... / OCP: ... / LSP: ... / ISP: ... / DIP: ...

## 게이트 4 — 테스트 모양: pass | fail
- ...

## 게이트 5 — FE/BE 패리티: pass | fail (or n/a)
- ...

## Remediation TODO (필요 시)
- `T-NNN-fix`: <제목> — <모듈> — <완료 조건>

## 판정
proceed | remediate-then-proceed | halt
```

## 하드 룰

a- 모든 게이트 판정에 `path:line` 인용 1개 이상 — 인용 없는 판정은 무효.
b- 코드 편집 금지 — 진단만.
c- **frontmatter 누락 산출물은 자동 fail.** [`../conventions/contracts.md`](../conventions/contracts.md) 의 frontmatter (skill_name/version/phase/project_id/fingerprint/prev_fingerprint/produced_at) 가 어떤 페이즈 산출물에서든 빠져 있으면 게이트 1 (의도 일치) 판정을 자동 fail 로 표시. `python scoring/fingerprint.py verify --file <path>` 로 핑거프린트 무결성도 함께 검증, 어느 한 산출물이라도 verify 실패 시 게이트 1 자동 fail.
d- 본 에이전트는 산출물 작성 직후 `python scoring/fingerprint.py compute --file quality/09-quality-gate.md --prev <직전 페이즈 산출>` 를 호출해 `09-quality-gate.md` 자체에도 frontmatter + fingerprint 박음.

## 완료 조건

`09-quality-gate.md` 가 5 게이트 모두 판정 + 종합 판정 + (필요 시) remediation TODO.
