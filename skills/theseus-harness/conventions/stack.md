# 스택 점검 컨벤션

## 한 줄 요약
**언어·컴파일러·패키지 매니저를 페이즈 04 안에서 사용자와 합의 + 로컬 설치 버전 점검 + 필요 시 자율 업데이트.** 맞지 않는 환경 위에서 시작한 스프린트는 회귀의 첫 번째 원인이 된다 — 미리 잡는다.

## 점검 대상 (사용자 명시 없을 때 기본값)

| 영역 | 기본 | 점검 명령 | 권고 최소 버전 |
| --- | ---- | -------- | ------------ |
| 백엔드 언어 | Go | `go version` | 1.21+ |
| 백엔드 의존 | Go modules | `go env GOMODCACHE` | — |
| FE 런타임 | bun | `bun --version` | 1.0+ |
| FE 빌드 | vite (bun 통합) | — | — |
| E2E | Playwright | `npx playwright --version` | 1.40+ |
| 컨테이너 (선택) | docker | `docker --version` | 24.0+ |
| 셸 스크립트 | bash + bat | `bash --version` (linux/mac), `cmd /c ver` (win) | — |
| 설정 형식 | TOML | `python -c "import tomllib"` (3.11+) 또는 `go-toml` | — |

## 동작 (페이즈 04 의 일부)

1- clarifier 가 위 표를 토대로 점검 질의를 생성.
2- 지휘자가 각 항목을 [`interview.md`](interview.md) 컨벤션으로 사용자에게 묻는다 — 1회 1질의, 객관식 5개 이하.
3- 사용자 답을 받으면 *로컬* 에서 `go version`, `bun --version` 등을 실행해 실제 설치 상태 확인.
4- 권고 버전 미만이면 사용자에게 업데이트 권고 — 자율 권한이 사전 부여됐으면 업데이트 명령 실행, 아니면 사용자 ack.

## 사용자 질의 형식 예

```
질의: 백엔드 언어로 Go 를 가정하고 진행할까요?

도메인이 일반적이라면 Go 가 본 하네스의 기본값입니다. ML inference 처럼 라이브러리가 결정적이면 Python 이 더 자연스럽습니다.

선택지:
1. Go (기본값)
2. Python (ML/스크립팅 무거움)
3. TypeScript / Node (백엔드도 JS 통일)
4. 직접 입력 (자유 응답)
```

후속:

```
질의: Go 1.21 이상 필요. 로컬 `go version` 실행 결과 1.20 입니다. 업데이트할까요?

업데이트 권고. asdf/goenv 사용 중이라면 자동 처리 가능합니다. 시스템 패키지 매니저(brew/apt)면 sudo 동의 필요.

선택지:
1. 자율 업데이트 (asdf/goenv 자동)
2. 사용자가 직접 업데이트 후 진행 — 잠시 정지
3. 1.20 로 진행 (호환성 위험 본인 부담)
4. 다른 언어로 변경 — 백엔드 질의 재시작
```

## 산출물

`intent/04-stack.md` — 합의된 스택, 로컬 버전, 업데이트 이력. 시간 메타 헤더.

```markdown
# 스택 합의

| 영역 | 합의 | 로컬 버전 | 권고 최소 | 상태 |
| --- | ---- | -------- | -------- | ---- |
| 백엔드 언어 | Go | 1.22.1 | 1.21 | OK |
| FE 런타임 | bun | 1.1.30 | 1.0 | OK |
| Playwright | npm | 1.45.0 | 1.40 | OK |

## 업데이트 이력
- 2026-05-01 17:50:12 — Go 1.20.5 → 1.22.1 (asdf 자율, 사용자 사전 동의)
```

## 자율 업데이트 가드

a- **사용자 사전 동의 필요** — `intent/05-decisions.md` 또는 명시 응답.
b- **시스템-와이드 변경 금지** — 가능하면 사용자 홈 디렉터리(asdf/nvm/goenv) 안에서.
c- **롤백 명령 표기** — 업데이트 직후 어떻게 되돌릴지 한 줄로.
d- **운영 시스템에서는 절대 자율 업데이트 안 함** — 개발 환경 한정.

## 빌드/실행 스크립트 (생성 시점)

페이즈 08 (구현) 의 implementer 가 다음을 모듈마다 + 루트에 생성:

a- `scripts/build.sh` (linux/mac) + `scripts/build.bat` (windows) — 빌드 명령.
b- `scripts/test.sh` + `scripts/test.bat` — 테스트 매트릭스 실행.
c- `scripts/dev.sh` + `scripts/dev.bat` — 로컬 개발 모드.
d- `scripts/setup.sh` + `scripts/setup.bat` — 의존 설치 + 환경 점검.
e- 모든 스크립트 첫 줄에 `set -euo pipefail` (sh) 또는 `setlocal enabledelayedexpansion` (bat).

## 설정 파일 정책

a- **TOML 기본** — `config.toml` (실값), `config.toml.example` (예시).
b- **`.env`** 는 비밀값. `.env.example` 항상 동반.
c- `.gitignore` 에 `config.toml`, `.env` 추가.
d- `config.toml.example`, `.env.example` 은 커밋 — 누락 시 페이즈 09 fail.
