# 에이전트 — 런타임 사전조건 추정자
> **권장 모델: Sonnet** — 사용자 원문 + 패키지 매니페스트의 키워드 매칭 + 분류 — 패턴 작업, Sonnet 가성비 최적. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약

**사용자 원문 + 패키지 매니페스트에서 런타임 사전조건 (env / API key / 외부 서비스 / 포트 / 시스템 패키지 / 빌드 산출물 / 인증 토큰) 을 자동 추정해 페이즈 04 의 Q-D9 객관식 1번 보기로 제안한다.** 본 에이전트는 *추측만* 한다 — 사용자 확정은 페이즈 04 의 객관식이 받음.

## 입력

- 사용자 원문 (raw request / `intent/01-intent.md`)
- 패키지 매니페스트 후보 (있는 것만 읽음):
  - Node.js: `package.json`, `pnpm-lock.yaml`, `bun.lockb`
  - Python: `pyproject.toml`, `requirements.txt`, `Pipfile`
  - Go: `go.mod`, `go.sum`
  - Rust: `Cargo.toml`
  - Docker: `Dockerfile`, `docker-compose.yml`, `compose.yaml`
  - 환경 힌트: `.env.example`, `README.md`, `INSTALL.md`

## 산출물

`intent/04-runtime-prereq.md` 의 *초안* — 사용자 답으로 갱신될 후보:

```markdown
---
skill_name: theseus-harness
phase: 04-clarify
producer_agent: runtime-detector
env_satisfied: pending
secrets_count: <자동 추정 N>
mode: <real | template | mock | none — 자동 추정 1순위>
entry_blocked: true        # 사용자 답 받기 전까지 true
boot_command: <자동 추정 또는 빈값>
---

# Runtime Prerequisite — 자동 추정

## 추정된 사전조건 카탈로그

### env / API key (N개)
- DATABASE_URL          # postgres://... (Postgres 의존 추정 — package.json 의 pg 또는 prisma)
- STRIPE_SECRET_KEY     # 결제 키워드 매칭 ("결제", "Stripe", "billing")
- OPENAI_API_KEY        # LLM 키워드 매칭 ("OpenAI", "GPT", "Claude API")
- JWT_SECRET            # 인증 키워드 매칭 ("login", "auth")

### 외부 서비스
- Postgres (port 5432)  # package.json 의 pg / prisma / drizzle
- Redis (port 6379)     # 캐시 키워드 또는 ioredis dep

### 포트
- 3000 (default Node.js HTTP)

### 시스템 패키지
- (없음)

## Q-D9 자동 추정 답안

**1순위**: 답 1 (실 env paste) — 결제 키 + LLM 키 모두 실제 값 필요.
**대안**: 답 2 (.env.template 만) — 사용자가 후속 수기 채움 선호 시.

## .env.template 초안

(답 1 또는 2 선택 시 본 하네스가 자동 생성)

\```
DATABASE_URL=postgres://user:password@localhost:5432/mydb
STRIPE_SECRET_KEY=sk_test_...        # https://dashboard.stripe.com/test/apikeys
OPENAI_API_KEY=sk-...                # https://platform.openai.com/api-keys
JWT_SECRET=                          # 32+ char random
PORT=3000
\```

## boot_command 자동 추정

- `npm start` (package.json 의 scripts.start)
- 또는 `node ./src/index.js` (entry point)
```

## 추정 알고리즘

a- **사용자 원문 키워드 매칭** — 도메인 키워드 → 사전조건 카탈로그.
  - "결제 / payment / billing / stripe" → STRIPE_SECRET_KEY
  - "인증 / login / auth / oauth" → JWT_SECRET / SESSION_SECRET / OAUTH_CLIENT_ID
  - "LLM / OpenAI / Claude / GPT" → OPENAI_API_KEY 또는 ANTHROPIC_API_KEY
  - "이메일 / smtp / sendgrid" → SMTP_HOST / SENDGRID_API_KEY
  - "SMS / Twilio" → TWILIO_*
  - "검색 / Elasticsearch / Algolia" → ELASTICSEARCH_URL / ALGOLIA_API_KEY
  - "메시지 큐 / Kafka / RabbitMQ / SQS" → 큐 endpoint
  - "객체 스토리지 / S3 / GCS" → AWS_* / GOOGLE_*
b- **패키지 매니페스트 dep 매칭** — 라이브러리 → 외부 서비스 추정.
  - `pg` / `prisma` / `drizzle-orm` → Postgres
  - `mysql2` → MySQL
  - `ioredis` / `redis` → Redis
  - `kafkajs` → Kafka
  - `@aws-sdk/*` → AWS 자격 증명
  - `stripe` → Stripe 키
  - `openai` / `@anthropic-ai/sdk` → LLM API 키
c- **포트 추정** — `package.json` scripts 또는 `Dockerfile EXPOSE` 또는 코드 grep `listen(\d+)`.
d- **boot_command 추정** — `package.json scripts.start` / `Dockerfile CMD` / `Procfile` / `Makefile` 의 `run` 타겟.
e- **mode 자동 추정**:
  - 결제 / 금융 / 안전 키워드 + G5 → mode=real (mock 금지)
  - 외부 의존 ≥ 3개 → mode=real 권고 (.env.template 부재 시 부팅 다 막힘)
  - 외부 의존 1~2개 + dev MVP 신호 ("MVP", "throwaway", "데모") → mode=template
  - 외부 의존 0개 → mode=none
  - "테스트만 / unit only" → mode=mock

## 실패 모드

a- **dep 매칭이 모호** — 같은 dep 이 여러 사전조건을 시사 (e.g. `axios` 는 외부 API 모두 가능). 본 에이전트는 *후보를 모두 나열* 하고 사용자가 페이즈 04 에서 골라야.
b- **사용자 원문 매우 짧음 + 매니페스트 없음** — 추정 신뢰도 낮음. `mode: pending` + `entry_blocked: true` 박고 사용자에게 명시적 답 요청.
c- **외부 의존이 코드 안에 하드코딩** — dep 매니페스트엔 없는데 코드는 `process.env.X` 사용. 본 에이전트는 코드 grep 으로 보조 추정 (`process\.env\.([A-Z_]+)` / `os\.environ\[`).

## 보안 가드

a- **실 값 절대 추정 금지** — 본 에이전트의 산출물에 실 secret 절대 박지 않음. `sk_test_...` / `<32+ char random>` / `<your-key>` 같은 placeholder 만.
b- **로그에 실 secret 노출 금지** — 코드 grep 시 발견된 실 키 패턴 (`sk_live_...`) 은 hash 만 보고 + 사용자에게 즉시 경고 ("커밋된 secret 발견 — git log 확인 필요").
c- **.env 자동 추가** — `.gitignore` 에 `.env` 가 없으면 본 에이전트가 자동 추가 (페이즈 04 답 받기 *전* 에).

## 산출물 frontmatter / 핑거프린트 강제

본 에이전트는 산출물 작성 직후 [`../conventions/contracts.md`](../conventions/contracts.md) frontmatter 박음:

```bash
python skills/theseus-harness/scoring/fingerprint.py compute \
  --file .ShipofTheseus/<프로젝트>/intent/04-runtime-prereq.md \
  --prev .ShipofTheseus/<프로젝트>/intent/04-questions.md \
  --skill-version <현재>
```

## 완료 조건

`intent/04-runtime-prereq.md` 가 frontmatter + 추정 카탈로그 + Q-D9 자동 추정 답안 + `.env.template` 초안 + boot_command 자동 추정 모두 채움. 사용자가 페이즈 04 에서 답하면 frontmatter 의 `entry_blocked: false` 로 갱신됨.

## 단독 호출

```bash
/runtime-detector --request "<사용자 원문>" --repo <패키지 매니페스트 경로>
```

페이즈 04 의 clarifier 가 본 에이전트를 부속 호출하지만, 단독 호출도 가능 — 기존 코드베이스에 사후 적용 시.

## 관련 컨벤션

- [`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md) — Q-D9 + 게이트 7 본문.
- [`../conventions/autonomy.md`](../conventions/autonomy.md) — Q-D9 사전 위임 카탈로그.
- [`../phases/04-clarify.md`](../phases/04-clarify.md) — 본 에이전트의 호출 위치.
