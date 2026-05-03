# `.env.template` — 도메인별 카탈로그

> [`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md) Q-D9 답 1·2 시 본 카탈로그에서 도메인별 키를 골라 `.env.template` 자동 생성.
> 실 값은 `.env` (gitignored) 에 수기 입력. 본 카탈로그의 값 자리는 항상 placeholder (`sk_test_*` / `<your-key>`).

## 결제 (Stripe / Toss / KakaoPay / PortOne)

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_...        # https://dashboard.stripe.com/test/apikeys
STRIPE_WEBHOOK_SECRET=whsec_...

# Toss Payments
TOSS_CLIENT_KEY=test_ck_...
TOSS_SECRET_KEY=test_sk_...

# PortOne (구 아임포트)
PORTONE_IMP_KEY=imp_...
PORTONE_IMP_SECRET=...
```

## 인증 / 세션

```bash
# JWT
JWT_SECRET=                          # 32+ char random — `openssl rand -hex 32`
JWT_EXPIRES_IN=24h

# OAuth (Google)
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Session
SESSION_SECRET=                      # 32+ char random
COOKIE_DOMAIN=localhost
```

## DB (Postgres / MySQL / SQLite / Redis)

```bash
# Postgres
DATABASE_URL=postgres://user:password@localhost:5432/mydb

# MySQL
DATABASE_URL=mysql://user:password@localhost:3306/mydb

# SQLite (로컬 dev)
DATABASE_URL=file:./dev.db

# Redis
REDIS_URL=redis://localhost:6379
```

## 객체 스토리지 (S3 / GCS / Azure Blob)

```bash
# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-2
S3_BUCKET=mybucket

# Google Cloud Storage
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCS_BUCKET=mybucket
```

## 메시지 큐 (Kafka / RabbitMQ / SQS)

```bash
# Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_CLIENT_ID=myapp

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672

# AWS SQS
AWS_SQS_QUEUE_URL=https://sqs.ap-northeast-2.amazonaws.com/<account>/<queue>
```

## LLM API

```bash
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...                # 선택

# Google Gemini
GOOGLE_API_KEY=...
```

## 이메일 / SMS

```bash
# SendGrid
SENDGRID_API_KEY=SG....

# AWS SES
AWS_SES_REGION=ap-northeast-2

# Twilio (SMS)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+82-10-...
```

## 검색 (Elasticsearch / Algolia / Meilisearch)

```bash
# Elasticsearch
ELASTICSEARCH_URL=http://localhost:9200

# Algolia
ALGOLIA_APP_ID=...
ALGOLIA_API_KEY=...
ALGOLIA_INDEX=myindex

# Meilisearch
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=...
```

## 모니터링 / 로깅

```bash
# Sentry
SENTRY_DSN=https://....@sentry.io/...

# DataDog
DATADOG_API_KEY=...

# Logtail / BetterStack
LOGTAIL_SOURCE_TOKEN=...
```

## 공통 (모든 프로젝트)

```bash
# 앱 메타
NODE_ENV=development                 # development | production | test
PORT=3000
LOG_LEVEL=info                       # debug | info | warn | error

# 외부 베이스 URL (CORS / OAuth redirect 등에 사용)
APP_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:3001
```

## 보안 가드 (자동)

- 본 카탈로그의 모든 값은 placeholder. 실 값 (`sk_live_*`, `prod-*`) 잔존 시 self_lint C-RP RP3 fail.
- `.env` 는 `.gitignore` 에 자동 추가.
- 답 1 (실 paste) 시 `intent/04-runtime-prereq.md` 의 frontmatter 에 sha256 hash 만 박힘.

## 사용 흐름

a- runtime-detector 에이전트가 사용자 원문 + 패키지 매니페스트에서 *필요한 도메인* 추정.
b- 본 카탈로그의 해당 절을 발췌해 `.env.template` 자동 생성.
c- 사용자가 답 1 선택 시 실 값 입력 → `.env` 로 봉인. 답 2 면 `.env.template` 만 출하.
d- 페이즈 09 게이트 7 의 `boot_check.py` 가 `.env` 로드 → 부팅 → healthz 검증.
