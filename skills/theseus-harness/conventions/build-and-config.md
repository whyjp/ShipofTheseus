# 빌드·설정·문서화 컨벤션

## 한 줄 요약
**모든 모듈 + 루트는 sh/bat 스크립트로 빌드·테스트·실행이 재현 가능해야 하고, 설정은 TOML 기본, `.example` 파일이 항상 동행, `docs/` 폴더가 누락 없이 단계별 변경을 기록한다.** 문서뿐 아니라 코드로서 환경 구성이 학습·실행 가능해야 함.

> **v0.9.16 sprint-10 — `polyglot-code-quality` 격상**: 본 문서의 §8 ruff 통합 절은 v0.9.16 [`polyglot-code-quality.md`](polyglot-code-quality.md) 의 *언어 카탈로그 1번* 으로 격하됨. 외부 사용자가 Go / TS / Rust / Java / Ruby 등 비-Python 프로젝트 시 페이즈 09 게이트 3 가 발현되도록 polyglot-code-quality 가 master.

## 1. 빌드/실행 스크립트 — 모듈마다 + 루트

a- 위치: 모듈마다 `<모듈>/scripts/`, 루트는 `scripts/`.
b- 셋트:

| 스크립트 | 용도 | linux/mac | windows |
| ------- | ---- | --------- | ------- |
| 빌드 | 컴파일·번들 | `build.sh` | `build.bat` |
| 테스트 | 단위+통합+E2E | `test.sh` | `test.bat` |
| 개발 모드 | 핫리로드 기동 | `dev.sh` | `dev.bat` |
| 셋업 | 의존 설치 + 환경 점검 | `setup.sh` | `setup.bat` |

c- sh 첫 줄: `#!/usr/bin/env bash` 다음 줄 `set -euo pipefail`.
d- bat 첫 줄: `@echo off` 다음 줄 `setlocal enabledelayedexpansion`.
e- 두 형식이 동등한 동작 — 한쪽만 작동하면 게이트 fail.

### 예시 — `scripts/test.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Go 단위 테스트"
go test -race -coverpkg=./... -coverprofile=coverage.out ./...

echo "==> FE 단위"
( cd fe && bun test --coverage )

echo "==> E2E"
bunx playwright test
```

### 예시 — `scripts/test.bat`

```bat
@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

echo ==^> Go 단위 테스트
go test -race -coverpkg=./... -coverprofile=coverage.out ./... || exit /b 1

echo ==^> FE 단위
pushd fe && bun test --coverage && popd || exit /b 1

echo ==^> E2E
bunx playwright test || exit /b 1
```

## 2. 설정 파일 — TOML 기본

a- 실값 파일: `config.toml`, `.env` — `.gitignore` 에 추가.
b- 예시 파일: `config.toml.example`, `.env.example` — **항상 커밋, 누락 시 페이즈 09 fail.**
c- TOML 파서: Go 는 `pelletier/go-toml/v2` 또는 `BurntSushi/toml`, Node 는 `@iarna/toml`.
d- JSON/YAML 사용은 외부 시스템 호환 필요 시만 — 그 외는 TOML 통일.

### 예시 `config.toml.example`

```toml
[server]
host = "0.0.0.0"
port = 8080

[database]
driver = "postgres"
dsn = "postgres://user:pass@localhost/dbname"   # 실값은 .env 에 분리

[logging]
level = "info"
format = "json"
```

### 예시 `.env.example`

```
DATABASE_PASSWORD=
JWT_SECRET=
SENTRY_DSN=
```

## 3. 문서화 — 모듈별 docs/

a- 위치: 루트 `docs/`, 모듈마다 `<모듈>/docs/`.
b- 단계별 변경마다 문서 갱신 — 누락 시 게이트 fail.
c- 변경으로 deprecated 된 항목은 **삭제하지 않고** `> [!WARNING] DEPRECATED — <시점>·<대체 항목>` 마크다운 어드모니션으로 표시.
d- 새 결정·정정은 `docs/changes/YYYY-MM-DD-<주제>.md` 에 ADR(Architecture Decision Record) 형식으로 누적.

### docs/ 폴더 표준

```
docs/
├── README.md            # 전체 문서 인덱스
├── architecture.md      # 모듈 구성도 + 시퀀스 다이어그램
├── api.md               # 외부 노출 API
├── ops.md               # 배포·롤백·모니터링
├── changes/             # ADR 누적
│   ├── 2026-05-01-initial-design.md
│   └── 2026-05-03-switched-from-jwt-to-session.md
└── glossary.md          # 유비쿼터스 언어
```

## 4. 코드 폐기 정책

a- **수정·개선·리팩터링 시 기존 코드는 가급적 폐기** — 주석으로 남기지 말고 삭제.
b- deprecated 된 함수/모듈은 즉시 제거. 외부 노출 API 라 호환 필요하면 `docs/changes/` 에 ADR + 코드 내 DEPRECATED 주석 + 한 마이너 버전 후 제거 일정.
c- "혹시 모르니" 보존 코드 금지 — git history 가 보존소.

## 5. 중간 과정 데이터 보존

a- 프로젝트가 **완전 완료 + 라이브** 되기 *전* 까지는 `.ShipofTheseus/<프로젝트>/` 의 모든 페이즈/스프린트 산출물을 보존.
b- 라이브 후에는 `.ShipofTheseus/` 를 아카이브 디렉터리로 이동 가능 (사용자 명시 동의).
c- 중간 과정 데이터는 **혼란이 아닌 추적 자산** — 회귀 바이섹트와 향후 유사 작업의 reference.

## 6. .gitattributes — 플랫폼 이식

저장소 루트에 `.gitattributes` 강제. 핵심 룰:

```
* text=auto eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
*.sh text eol=lf
*.png binary
*.jpg binary
*.gif binary
*.ico binary
*.pdf binary
go.sum -diff
bun.lockb binary
```

## 7. 병렬·자원 가드 (서브에이전트)

a- 가급적 병렬 디스패치 — 의존 없는 TODO 는 한 메시지에 다중 `Agent` 호출.
b- 단, 동시 실행 에이전트 수 N 의 상한은 다음 가드:
  b-1 노드/Go 프로세스 메모리 합이 머신 RAM 의 50% 를 넘지 않을 것.
  b-2 동시 E2E (Playwright) 인스턴스는 최대 2 개 — 헤드리스 브라우저는 무겁다.
  b-3 같은 파일을 수정하는 TODO 는 절대 병렬 금지 — 직렬화.
c- 메모리/CPU 과사용으로 OS 가 프로세스를 죽이는 일이 발생하면, 다음 스프린트는 병렬도를 절반으로 줄여 재시도.
d- 측정 명령: `top -b -n1 | head -20`, `free -m` (linux), `ps -A -o %mem= | sort -rn | head` 활용.

## 8. 코드 lint/format — ruff 통합 (sprint-05-a)

a- **모든 Python 모듈** 은 `ruff` 를 lint + format 도구로 사용 (default 채택). 외부 도구지만 *본 하네스가 코드 micro 품질 게이트를 자체 정의하지 않고 표준 도구 호출* 하는 거울 원칙 정합 — 메모리 `feedback_borrow_discipline.md` 정합.
b- 빌드/테스트 스크립트에 `ruff check` + `ruff format --check` 호출 의무. 페이즈 09 게이트 3 (SOLID DIP) 에 *ruff 통과* 가 부속 게이트로 박힘.
c- 설정 파일 — 모듈 루트의 `pyproject.toml` 의 `[tool.ruff]` 절에 룰 셋 명시. 권장 룰 셋 = `select = ["E", "F", "I", "B", "UP"]` (PEP8 + pyflakes + isort + bugbear + pyupgrade).
d- 페이즈 08-δ refactor 서브페이즈가 `ruff check --fix` + `ruff format` 으로 자동 정리 (test GREEN 유지하며).

### 예시 — `scripts/lint.sh` / `lint.bat`

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> ruff check (lint)"
ruff check .

echo "==> ruff format --check (formatting)"
ruff format --check .
```

```bat
@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

echo ==^> ruff check
ruff check . || exit /b 1

echo ==^> ruff format --check
ruff format --check . || exit /b 1
```

e- 비-Python 모듈 (Go, TS, Rust 등) 은 각 언어의 표준 lint/format 도구 사용 — Go: `go vet` + `gofmt -l`, TS: `biome check`, Rust: `cargo clippy` + `cargo fmt --check`. ruff 룰의 *정신* (외부 표준 도구 통합) 을 따름.

## 강제 시점

a- 페이즈 06 (계획) — planner 가 위 룰을 계획 산출물에 반영.
b- 페이즈 08 (구현) — implementer 가 스크립트/설정 예시/docs 동행 출하. 페이즈 08-δ refactor 가 `ruff check --fix` + `ruff format` 자동 호출.
c- 페이즈 09 (게이트) — quality-gate 가 누락 검사: `config.toml.example`, `.env.example`, `.gitattributes`, 모듈별 sh+bat, 모듈별 `docs/`, **`pyproject.toml [tool.ruff]` (Python 모듈 시)**, **ruff check + ruff format --check 통과** 가 없으면 fail.
