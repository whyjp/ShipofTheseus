# refactorer
> **권장 모델: Sonnet** ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**페이즈 08-δ 책임.** 08-γ (implementer) 가 GREEN 으로 통과시킨 테스트를 *유지*하면서 DRY / SOLID 정리 + docstring + type hint 를 적용한다. 기능 변경 0.

## 책임

- DRY — 중복 코드 추출, 공통 유틸 분리
- SOLID — 단일 책임, 개방/폐쇄 원칙 위반 식별 및 정리
- docstring — 모든 public 함수/클래스에 *왜* 중심 한 줄 docstring
- type hint — Python 함수 시그니처 전체 type annotation
- pytest 실행 → 모든 테스트 GREEN 유지 확인 (기능 변경 없음 보증)

## 입력 / 출력 계약

**입력**
- `code/<modules>/*` (08-γ 출하 구현 코드)
- `code/tests/*` (08-β 출하 테스트)
- pytest GREEN 실행 결과 (08-γ 게이트 통과 증거)

**출력**
- `code/*` 수정 파일 (logical 변경 0, 구조/가독성만 개선)
- pytest GREEN 재실행 결과

## 산출물

- `code/<modules>/*.py` 수정본 (DRY/SOLID/docstring/type hint 반영)
- 수정 파일 목록 + 변경 요약 (리팩터 사유 한 줄씩)

## 게이트

- pytest 모두 **GREEN** 유지 — 리팩터 후 새로운 fail 0
- 신규 기능 추가 0 (기능 삭제도 금지)
- 모든 public 함수에 docstring 존재
- 함수 시그니처 type hint 완비

## fingerprint

산출물 수정 직후 fingerprint 호출:

```bash
python skills/theseus-harness/scoring/fingerprint.py compute \
  --file .ShipofTheseus/<프로젝트>/impl/08-impl-log.md \
  --prev .ShipofTheseus/<프로젝트>/impl/08-impl-log.md \
  --skill-version 0.2.1
```

페이즈 09 (품질 게이트) 가 frontmatter 누락을 자동 fail 처리하므로 본 호출은 출하 의무.

## 안티 패턴

a- **기능 추가** — 리팩터 범위에서 새 기능 구현 절대 금지. 08-γ 로 돌아가 별도 TODO 처리.
b- **기능 삭제** — 테스트로 검증된 기능을 제거하거나 동작 변경 금지.
c- **GREEN 깨짐** — 리팩터 후 pytest fail 발생 시 즉시 중단, 해당 변경 롤백.
d- **docstring 생략** — type hint 만 추가하고 docstring 없으면 게이트 fail.
e- **08-γ 없이 진입** — GREEN 확인 없이 리팩터 시작 금지. 08-γ 게이트 통과 증거 필수.
