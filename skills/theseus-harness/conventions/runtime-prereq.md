# 런타임 사전조건 (Runtime Prerequisite) 컨벤션

## 한 줄 요약

**lint 통과 + 단위 테스트 통과 ≠ 실행 가능.** env / API key / 외부 서비스 의존성이 빠지면 *완성된 코드가 첫 실행에서 부팅 실패.* 본 컨벤션은 페이즈 04 의 Q-D9 로 사전조건을 자백받고, 페이즈 09 의 게이트 7 로 *실 실행 1회 통과* 를 강제해 코드-실행가능 까지를 한 약속에 묶는다. **정직박스 ⓔ 의 단순 lint/test 게이트보다 한 단계 강한 가드.**

## 왜 필요한가

a- LLM 코딩 하네스의 흔한 실패: `pytest` 통과 + `tsc` 통과 + `eslint` 통과인데 `npm start` 가 즉시 죽음 — `STRIPE_SECRET_KEY undefined` / `ECONNREFUSED postgres:5432` / `Missing required env: API_BASE_URL`.
b- 단위 테스트는 콘크리트 의존을 페이크로 대체하므로 *실 환경* 의 부재를 안 잡음.
c- 사용자는 코드 받자마자 "왜 안 돌아가지" 에 시간 소진. 사후 디버깅 비용 >> 사전 자백 비용.
d- 코드 출하 의무는 *실행 가능한 코드* 의무까지를 포함해야 한다 — `Verification Commands` (Q-D8) 가 *어떻게 검증하나* 를 정한다면, 본 컨벤션 (Q-D9) 은 *어떻게 부팅하나* 를 정한다.

## 사전조건 분류

a- **env 변수** — 토큰, 시크릿, 호스트, 포트, 플래그.
b- **API key / 시크릿** — 결제 / 인증 / 이메일 / SMS / LLM API.
c- **외부 서비스** — DB (Postgres / MySQL / Redis), 메시지 큐 (Kafka / RabbitMQ), 객체 스토리지 (S3 / GCS).
d- **포트** — 로컬 dev 가 사용할 인바운드 포트 (3000 / 8080 / 5432).
e- **시스템 패키지** — Docker, ffmpeg, ImageMagick 등 OS 레벨 의존.
f- **빌드 산출물** — wasm, native binding, codegen 결과.
g- **인증 토큰** — gh CLI, gcloud, kubectl 컨텍스트 등 사용자 단위 secret.

각 분류마다 *대체 가능 (mock / fake / disable)* 인지 *진짜 필요 (real-only)* 인지 표기.

## Q-D9 — 페이즈 04 사전 위임 신규 답안 ([`autonomy.md`](autonomy.md))

페이즈 04 의 마지막 9번째 사전 위임 질의:

```
질의: 본 작업의 *런타임 사전조건* 을 어떻게 처리하시겠습니까?

자동 추정: 외부 서비스 키워드 N개 감지 (예: "Stripe", "Postgres", "OpenAI").

선택지 (복수 응답 가능):
1. 실 env 값 paste (gitignored 별도 파일로 즉시 봉인 + 보안 가드)
2. `.env.template` 만 자동 생성 (사용자가 후속 수기 채움, 실행 가드는 키 부재 명시 메시지)
3. 모든 외부 의존을 mock / disable 모드로 부팅 (dev profile, 실 키 부재 OK)
4. 외부 의존 없음 (순수 로컬 / in-memory only)
```

답을 `intent/04-autonomy.md` 의 9번째 줄에 기록 + Q-D9 의 본문은 `intent/04-runtime-prereq.md` 에 기록. **9 답 + runtime-prereq 산출물 모두 valid 해야 페이즈 05 진입.**

### 답별 frontmatter 매핑

| Q-D9 답 | 의미 | frontmatter |
| ------ | --- | ---------- |
| 1 | 실 env paste (즉시 봉인) | `env_satisfied: true`, `secrets_count > 0`, `mode: real`, `entry_blocked: false` |
| 2 | `.env.template` 만 (수기 채움) | `env_satisfied: pending`, `secrets_count > 0`, `mode: template`, `entry_blocked: false` |
| 3 | mock / disable 부팅 | `env_satisfied: true`, `secrets_count: 0`, `mode: mock`, `entry_blocked: false` |
| 4 | 외부 의존 없음 | `env_satisfied: true`, `secrets_count: 0`, `mode: none`, `entry_blocked: false` |
| (미응답) | 진입 차단 | `env_satisfied: false`, `entry_blocked: true` |

답 1 + 2 는 동시 가능 (실 키 + template 둘 다). 답 3·4 는 단독.

## `.env.template` — 자동 생성 + 보안 가드

답 1·2 에서 본 하네스가 자동 생성. 본 파일은 *키 이름 + 형태만* 노출, 실 값은 `.env` (gitignored) 에 수기 입력.

```bash
# .env.template (gitignored 가 아님 — 카탈로그)
# 사용자가 본 파일을 .env 로 복사 후 실 값을 채움
# .env 는 .gitignore 에 의해 자동 제외됨

DATABASE_URL=postgres://user:password@localhost:5432/mydb
STRIPE_SECRET_KEY=sk_test_...                # https://dashboard.stripe.com/test/apikeys
OPENAI_API_KEY=sk-...                        # https://platform.openai.com/api-keys
PORT=3000
LOG_LEVEL=info
```

### 보안 가드 (자동 강제)

a- `.env` 는 `.gitignore` 에 자동 추가 (없으면 신설). self_lint C-RP1 이 검증.
b- `.env.template` 의 *값 자리* 에 실 시크릿 잔존 금지 (예: `sk_live_...`, `prod-token-...`). 정규식 `(sk_live_|prod[-_])` 매칭 시 self_lint 자동 fail.
c- `git status` 에 `.env` 가 untracked 로도 보이면 본 하네스가 마지막 커밋 직전 한 번 더 경고 (정직박스 ⓔ 강화).
d- 답 1 (실 paste) 시 hash 만 frontmatter 에 기록 (`env_hash: sha256:...`). 사후 audit 가능, 평문 잔존 0.

## 페이즈 09 — 게이트 7 신설 (env-satisfied + 실 실행 1회)

기존 6 게이트 (의도 일치 / 범위 규율 / SOLID / 테스트 모양 / FE-BE 패리티 / NFR 일치) 에 게이트 7 추가:

| # | 게이트 | 무엇을 보는가 | fail 신호 |
| - | ------ | ----------- | -------- |
| 7 | **env-satisfied + 실 실행 1회** | a- `intent/04-runtime-prereq.md` 의 `entry_blocked: false` b- 답 1·2 시 `.env.template` 존재 + `.gitignore` 에 `.env` c- 부팅 명령 1회 exit 0 (또는 mock 모드면 mock 부팅 1회 exit 0) | env_satisfied=false / 실 부팅 시 missing env / `:port` 충돌 / DB connect 실패 |

### 부팅 검증 알고리즘

a- Q-D9 답 1·2 → `<.env 또는 .env.template> 로드 → 부팅 명령 (e.g. `npm start` / `go run ./cmd/server`) → 5 초 내 healthz 200 OK → SIGTERM`. 실패하면 missing env / 포트 / DB 사유 산출.
b- Q-D9 답 3 → mock 모드 부팅 명령 (e.g. `BOOT_MODE=mock npm start`) → 동일 healthz check.
c- Q-D9 답 4 → 부팅 무필요. 게이트 7 = `pass (no runtime)`.

검증 명령은 `intent/04-runtime-prereq.md` 의 `boot_command` 필드에 박힘 (Q-D9 답 시 사용자 또는 자동 추정으로 채움).

### 산출물에 박는 증거

`quality/09-quality-gate.md` 의 게이트 7 절:

```markdown
## 게이트 7 — env-satisfied + 실 실행 1회

- 사전조건 답: Q-D9 = 1 (실 env paste)
- env_satisfied: true
- secrets_count: 4 (DATABASE_URL, STRIPE_SECRET_KEY, OPENAI_API_KEY, JWT_SECRET)
- env_hash: sha256:abcd... (audit only, 평문 0)
- boot_command: `npm start` (PORT=3000)
- boot_exit: 0
- healthz_status: 200 OK (3.4s after start)
- 결과: pass
```

## 그레이드별 적용 (matrix)

| Grade | Q-D9 강제 | 게이트 7 강제 | mock 모드 허용 |
| ----- | :-------: | :-----------: | :------------: |
| G1 Trivial | — | — | — |
| G2 Simple | 옵션 | 옵션 | ✅ |
| G3 Standard | ✅ | ✅ | ✅ |
| G4 Complex | ✅ | ✅ | ✅ |
| G5 Critical | ✅ | ✅ + 실 모드 강제 | — (mock 금지) |

G5 는 mock 모드 부팅을 허용 안 함 — 미션 크리티컬에서 *실 환경 부재* 는 곧 게이트 미달.

## verification.md (Q-D8) 와의 관계

| 차원 | Q-D8 (verification) | Q-D9 (runtime-prereq) |
| ---- | ------------------- | --------------------- |
| 무엇을 정함 | *어떻게* 외부 완료 검증 | *어떻게* 부팅 |
| 산출물 | `intent/04-verification.md` | `intent/04-runtime-prereq.md` |
| 게이트 | 페이즈 09 의 acceptance criteria | 페이즈 09 의 게이트 7 |
| frontmatter 키 | `commands_count`, `manual_only`, `entry_blocked` | `env_satisfied`, `secrets_count`, `mode`, `entry_blocked` |
| 임계 | exit 0 = pass | boot_exit 0 + healthz 200 |

두 답 모두 받아야 페이즈 05 진입. 단일 산출물 의무.

## 보안 — 자율 결정의 *유일한* 예외 ([`autonomy.md`](autonomy.md))

a- 실 secret 의 git 커밋은 **자동 차단** — 사용자 ack 없이 자율로 *거부*. 페이즈 04 후 인터럽트 0 룰의 한 케이스 예외.
b- `.env` 의 untracked 잔존이 핸드오프 직전 발견되면 본 하네스가 *한 번* 사용자 ack 호출 (정직박스 ⓔ 강화).
c- frontmatter 의 `env_hash` 는 sha256 만, 평문 0. audit 시 같은 값 입력하면 hash 비교로 일치 검증 가능.
d- 답 1 의 실 env paste 산출물은 `.ShipofTheseus/<프로젝트>/.gitignore` 에 자동 추가됨 — 산출물 디렉터리 밖으로 누출 0.

## 자원 가드

a- 실 모드 부팅 검증은 동시 1 회만. 멀티버스 우주별로 부팅하지 않음 (포트 충돌, DB connect 폭주).
b- mock 모드는 동시 N 회 가능 (외부 의존 0).
c- 부팅 검증 timeout 30 초. 미달 시 `boot_exit: timeout` + 게이트 7 fail.

## 안티 패턴

a- **Q-D9 미응답인데 페이즈 05 진입** — `entry_blocked: true` 가 강제. 우회 시 self_lint C-RP2 fail.
b- **`.env` 를 git 에 커밋** — 자율 차단 + 사용자 ack. 우회 코드 추가 금지.
c- **`.env.template` 의 값 자리에 실 시크릿** — self_lint C-RP3 정규식 fail.
d- **mock 모드 부팅이 mock 모드 코드를 우회** — `BOOT_MODE=mock` 가 코드에서 진짜로 mock 어댑터를 선택해야 게이트 7 통과. 단순 환경변수 paste 만으로 통과 안 함.
e- **부팅 검증 없이 게이트 통과** — 게이트 7 의 `boot_exit` + `healthz_status` 둘 다 산출물에 박혀야 통과. 누락 시 fail.
f- **G5 에서 mock 모드 통과** — 매트릭스 위반. self_lint C-RP4 fail.

## 후속 (sprint-02-e 또는 v0.7.x)

a- `agents/runtime-detector.md` — env / 외부 서비스 자동 추정 에이전트 (사용자 원문 + 패키지 매니페스트에서 키워드 매칭).
b- `scoring/boot_check.py` — 부팅 검증 자동화 헬퍼 (timeout / healthz / SIGTERM).
c- `templates/env.template` — 도메인별 (.env 권고 키 카탈로그 — 결제/인증/저장소/메시지/LLM).
d- self_lint C-RP1~C-RP4 — `.env` gitignore / Q-D9 entry_blocked / `.env.template` 보안 / G5 mock 금지.
e- 페이즈 12 웹뷰의 새 탭 "Runtime" — `boot_exit` / `healthz` / `secrets_count` 라이브 표기.
