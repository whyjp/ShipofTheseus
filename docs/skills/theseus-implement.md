# theseus-implement 가이드

## 한 줄 요약

**페이즈 08 — TODO 별 모듈 단위 구현 (코드 + 테스트 + 목 표면 + 빌드 스크립트 + TOML + docs/ 한 호출에).**

## 언제 호출하는가

ⓐ orchestrator 가 자동 위임 (plan 직후).
ⓑ 외부에서 받은 plan 산출물로 *구현부터 다시 시작* 하고 싶을 때 — 단독 호출.
ⓒ 한 모듈만 다시 구현하고 싶을 때 (TODO 단위 부분 호출).

## 호출 형식

```
/theseus-implement <요구사항>
```

단, *plan 산출물* (`plan/06-plan.md`, `plan/07-plan-review.md`) 이 존재해야 한다. frontmatter 검증 실패 시 진입 거부.

## 페이즈별 산출물

| 페이즈 | 파일 | 내용 |
| ----- | ---- | --- |
| 08 | `impl/08-impl-log.md` | TODO 별 구현 로그 + 테스트 + 빌드 스크립트 + 설정 + 문서 |
| 08 | (코드) | 실제 모듈 코드 |
| 08 | (테스트) | 단위·통합 테스트 (TDD 우선) |
| 08 | `build.sh` + `build.bat` | 크로스 플랫폼 빌드 스크립트 (의무) |
| 08 | `config.toml.example` | TOML 설정 예시 |
| 08 | `.env.example` | 환경 변수 예시 |
| 08 | `docs/` | 모듈 docs (사용자 진입점) |

## 한 모듈 = 한 호출에 무엇이 다 들어가는가

본 스킬은 *모듈 한 단위* 를 한 LLM 호출에 코드 + 테스트 + 목 + 빌드 + 설정 + docs 까지 다 만든다. 분리 호출 금지 — 분리 시 *목 표면이 코드와 어긋나는* 회귀가 자주 발생.

자세한 컨벤션은 [`../../skills/theseus-harness/conventions/build-and-config.md`](../../skills/theseus-harness/conventions/build-and-config.md).

## 빌드 스크립트 (sh + bat 의무)

self_lint C13 이 강제: 페이즈 08 산출물에 `build.sh` 와 `build.bat` 모두 포함되어야 한다 — 크로스 플랫폼 운영을 *기본값* 으로.

## 입출력 (단독 호출)

- **입력**: `plan/06-plan.md` + `plan/07-plan-review.md` (frontmatter 검증 통과 필수).
- **출력**: `impl/08-impl-log.md` + 코드/테스트/빌드 스크립트/설정/docs. 다음 스킬 (`theseus-quality`) 이 입력으로 받음.

## 정체 극복 (lessons.md)

페이즈 08 가 같은 모듈에서 같은 류의 실패를 반복하면 (점수 시계열 정체 감지), `lesson_pack.json` 이 다음 루프에 전달된다:

```json
{
  "forbidden_strategies": ["DI 컨테이너 직접 import"],
  "rewrite_rule": "기존 모듈 통째 폐기 후 페이즈 06 부터 재진입",
  "stagnation_trigger": "score Δ < 0.005 for 3 sprints"
}
```

자세한 절차는 [`../../skills/theseus-harness/conventions/lessons.md`](../../skills/theseus-harness/conventions/lessons.md).

## 자주 묻는 질문

**Q. TDD 가 강제인가?**
A. 추천이지만 강제는 아니다. 단, 테스트가 코드와 *같은 호출* 에 같이 만들어져야 한다 (목 표면 일관성). 후속 페이즈 09 의 게이트가 테스트 커버리지를 검증.

**Q. 모듈 분해는 어떤 기준으로?**
A. plan/06 의 TODO DAG 가 모듈 경계. 한 모듈이 LOC>200 / 복합 책임이면 서브 에이전트로 재귀 분해 ([`../../skills/theseus-harness/conventions/sub-agents.md`](../../skills/theseus-harness/conventions/sub-agents.md)).

**Q. 한 모듈 호출에 토큰 한도를 넘으면?**
A. 모듈을 더 작게 분해해 다시 시도. 호출 분리는 마지막 수단 — 분리 시 목 표면 일관성을 별도 검증해야 함.

## 더 읽을거리

- [`../../skills/theseus-implement/SKILL.md`](../../skills/theseus-implement/SKILL.md) — 기계 진입점.
- [`../../skills/theseus-harness/conventions/build-and-config.md`](../../skills/theseus-harness/conventions/build-and-config.md) — 빌드·TOML·docs 컨벤션.
- [`../../skills/theseus-harness/conventions/lessons.md`](../../skills/theseus-harness/conventions/lessons.md) — 정체 극복.
- [`../../skills/theseus-harness/conventions/sub-agents.md`](../../skills/theseus-harness/conventions/sub-agents.md) — 재귀 분해.
