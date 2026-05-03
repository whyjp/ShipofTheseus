# test-writer
> **권장 모델: Sonnet** ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**페이즈 08-β 책임.** 08-α (test-architect) 의 test scope 를 따라 테스트 코드만 작성한다. 구현 코드 작성 0. test-first 원칙의 정공 — 모든 신규 테스트는 RED (right reason) 여야 한다.

## 책임

- `impl/08-test-scope.md` (08-α 산출물) 를 입력으로 테스트 코드 작성
- 테스트가 올바른 이유로 실패(RED)하는지 확인:
  - ImportError / 파일 없음 등 인프라 오류로 fail ≠ right reason
  - 구현 로직 부재로 fail = right reason
- 구현 코드(`code/<modules>/*.py` 등) 작성 *절대 금지*

## 입력 / 출력 계약

**입력**
- `impl/08-test-scope.md` (08-α 산출물, scope × invariants 매핑)
- `plan/06-plan.md` (TODO DAG, 의존 구조)
- `intent/01-intent.md`, `intent/04-answers.md`, `intent/05-decisions.md`

**출력**
- `code/tests/*` — 신규 테스트 파일
- pytest 실행 결과 (RED 확인 로그)

## 산출물

- `code/tests/<module>/test_<todo_id>.py` (atomic + group)
- `code/tests/functional/test_<scenario>.py` (functional)
- 각 테스트 파일 상단에 대응 TODO ID + invariants 주석

## 게이트

- pytest 실행 시 모든 신규 테스트 **fail** (RED)
- fail 원인이 `right reason` — 구현 부재, not 인프라 오류
- 구현 코드 파일 신규 생성 0

## fingerprint

산출물 작성 직후 fingerprint 호출:

```bash
python skills/theseus-harness/scoring/fingerprint.py compute \
  --file .ShipofTheseus/<프로젝트>/impl/08-test-scope.md \
  --prev .ShipofTheseus/<프로젝트>/impl/08-test-scope.md \
  --skill-version 0.2.1
```

페이즈 09 (품질 게이트) 가 frontmatter 누락을 자동 fail 처리하므로 본 호출은 출하 의무.

## 안티 패턴

a- **impl 코드 작성** — 테스트 작성 중 구현 stub 이라도 작성 금지. 08-γ (implementer) 책임.
b- **GREEN 테스트 출하** — 이미 통과하는 테스트는 test-first 위반. RED 확인 필수.
c- **인프라 오류로 RED** — `ModuleNotFoundError` 등 인프라 문제는 right reason 아님 → 인프라 먼저 수정.
d- **scope 무시** — 08-α 산출물 참조 없이 자의적 테스트 작성 금지.
e- **skipped / .only** — 조건부 skip, `pytest.mark.only` 금지.
