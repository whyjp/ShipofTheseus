# theseus-quality 가이드

## 한 줄 요약

**페이즈 09 — 5 종 게이트 + Phase V 측정 유효성 점검 + frontmatter 검증.** 구현 산출물이 다음 단계(스프린트 루프) 로 진입할 자격을 검증한다.

## 언제 호출하는가

ⓐ orchestrator 가 자동 위임 (implement 직후).
ⓑ 외부에서 받은 구현물의 게이트 통과 여부만 점검하고 싶을 때 — 단독 호출.

## 호출 형식

```
/theseus-quality <요구사항>
```

단, *impl 산출물* (`impl/08-impl-log.md` + 코드 + 테스트) 이 존재해야 한다. frontmatter 검증 실패 시 진입 거부.

## 5 게이트

| # | 게이트 | 무엇을 검증 | hard fail 룰 |
| - | ----- | ---------- | ------------ |
| 1 | DIP (의존성 역전) | 모듈 간 의존이 추상에 의존하는가, 구현체 직접 import 가 있는가 | 단독 hard cap 0.6 |
| 2 | SoC (관심사 분리) | 단위 테스트가 모듈 경계를 분리하는가 | 5 hard cap 중 하나 |
| 3 | 빌드 스크립트 | sh + bat 모두 존재 + 둘 다 성공하는가 | 누락 시 fail |
| 4 | 설정·환경 | `config.toml.example` + `.env.example` 모두 존재 | 누락 시 fail |
| 5 | NFR | 페이즈 04 에서 확정한 NFR 충족 (성능·가용성·보안·운영) | 충족 미달 시 fail |
| 6 | 도메인 NFR (spec-catalog) | 도메인별 자동 채움 NFR (결제/CRUD/검색 등) | 충족 미달 시 fail |
| 7 | Phase V 측정 유효성 | 측정 프로브 자체가 정상 동작 (오버헤드/베이스라인/편차) | 무효 시 fail |

자세한 채점 룰은 [`../../skills/theseus-harness/scoring/rubric.md`](../../skills/theseus-harness/scoring/rubric.md).

## DIP 가 왜 *단독* hard cap 인가

본 하네스의 핵심 약속은 "테세우스의 배" — 판자를 갈아 끼워도 같은 배라 부를 수 있어야 한다. 그 *판자 교체 가능성* 이 곧 DIP. DIP 가 깨지면 다른 5 차원이 다 만점이어도 본 하네스의 정체성이 무너진다 — 따라서 단독 hard cap 0.6 으로 강제.

## Phase V 측정 유효성

게이트 7 — 측정 자체가 *측정 대상에 영향을 주지 않는지* 점검. 프로브 오버헤드가 측정값을 왜곡하지 않는가, 베이스라인이 안정적인가, 편차가 통계적으로 유의한가. 자세한 룰은 [`../../skills/theseus-harness/conventions/test-invariants.md`](../../skills/theseus-harness/conventions/test-invariants.md).

## 입출력 (단독 호출)

- **입력**: `impl/08-impl-log.md` + 코드 + 테스트 (frontmatter 검증 통과 필수).
- **출력**: `quality/09-quality-gate.md` (게이트 1~7 결과 + remediation TODO). 다음 스킬 (`theseus-sprint`) 이 입력으로 받음.

## remediation TODO

게이트 실패 시 `quality/09-quality-gate.md` 끝에 *remediation TODO 리스트* 가 박힌다 — 페이즈 11 의 회귀 분석가가 이를 입력으로 받아 다음 스프린트 계획을 세운다. 즉 *quality 가 실패해도 스프린트 진입을 막지 않는다* — 스프린트 루프가 보완을 담당.

단, **DIP 단독 hard cap** 만은 예외 — 0.6 미만이면 페이즈 11 의 `re-architect` 트리거 (모듈을 깨고 페이즈 06 부터 재진입).

## 자주 묻는 질문

**Q. 게이트가 모두 통과하면 임계 0.999 도 통과하는가?**
A. 아니다. 게이트는 *필요 조건*, 임계 0.999 는 *충분 조건* (스프린트 루프가 도달). 게이트 통과는 스프린트 진입 자격일 뿐.

**Q. 게이트 6 (도메인 NFR) 은 어떻게 자동으로 알아내는가?**
A. 페이즈 01 (intent) 에서 도메인을 분류하면 [`../../skills/theseus-harness/conventions/spec-catalog.md`](../../skills/theseus-harness/conventions/spec-catalog.md) 의 카탈로그에서 해당 도메인의 NFR 이 자동 채워진다. 페이즈 04 인터뷰에서 사용자가 객관식 1 클릭으로 확정.

**Q. Phase V 측정이 무효라고 판정되면?**
A. 게이트 7 fail — 측정 자체를 다시 설계 (프로브 위치/베이스라인/표본 크기). 자세한 룰은 [`../../skills/theseus-harness/conventions/test-invariants.md`](../../skills/theseus-harness/conventions/test-invariants.md).

## 더 읽을거리

- [`../../skills/theseus-quality/SKILL.md`](../../skills/theseus-quality/SKILL.md) — 기계 진입점.
- [`../../skills/theseus-harness/scoring/rubric.md`](../../skills/theseus-harness/scoring/rubric.md) — 6 차원 채점 + DIP hard cap.
- [`../../skills/theseus-harness/conventions/spec-catalog.md`](../../skills/theseus-harness/conventions/spec-catalog.md) — 도메인별 NFR.
- [`../../skills/theseus-harness/conventions/test-invariants.md`](../../skills/theseus-harness/conventions/test-invariants.md) — Phase V 측정 유효성.
