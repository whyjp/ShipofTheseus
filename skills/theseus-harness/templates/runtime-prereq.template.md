---
skill_name: theseus-harness
skill_version: TEMPLATE
phase: 04-clarify
project_id: TEMPLATE
project_run: TEMPLATE
fingerprint: TEMPLATE
prev_fingerprint: TEMPLATE
produced_at: TEMPLATE
producer_agent: clarifier            # 또는 runtime-detector (부속 호출 시)

# Q-D9 답에 따라 채워짐
env_satisfied: pending               # true | pending (답 2 = .env.template 만) | false (entry_blocked)
secrets_count: 0                     # 사전조건 카탈로그의 env / API key 갯수
mode: pending                        # real | template | mock | none | pending
boot_command: ""                     # 예: "npm start" / "go run ./cmd/server"
healthz_url: ""                      # 예: http://localhost:3000/healthz
env_hash: ""                         # sha256:... (mode=real 시, 평문 0)
entry_blocked: true                  # 답 받기 전까지 true → 페이즈 05 진입 거부
---

> **프로젝트:** `<project_id>` · **페이즈:** `04-clarify`
> **시작:** `<ISO>` · **현재 시각:** `<ISO>`

# Runtime Prerequisite — 실행 가능 사전조건 (Q-D9)

> **v0.7.0 신규 — [`../conventions/runtime-prereq.md`](../conventions/runtime-prereq.md)**
> lint + 단위 테스트 통과 ≠ 실행 가능. env / API key / 외부 서비스가 빠지면 부팅 즉시 죽음.
> Q-D8 (Verification Commands) 이 *어떻게 검증하나* 라면 Q-D9 는 *어떻게 부팅하나*.

## 답 (Q-D9)

| Q-D9 답 | 의미 | frontmatter |
| ------ | --- | ---------- |
| 1 | 실 env 값 paste (gitignored 봉인 + sha256 hash audit) | `mode: real`, `secrets_count > 0`, `entry_blocked: false` |
| 2 | `.env.template` 만 (사용자 후속 수기) | `mode: template`, `secrets_count > 0`, `entry_blocked: false` |
| 3 | mock / disable 부팅 (dev profile) | `mode: mock`, `secrets_count: 0`, `entry_blocked: false` |
| 4 | 외부 의존 없음 (순수 로컬) | `mode: none`, `secrets_count: 0`, `entry_blocked: false` |
| (미응답) | 진입 차단 | `entry_blocked: true` |

답 1 + 2 동시 가능 (실 키 + template 둘 다). 답 3·4 단독.

## 추정된 사전조건 카탈로그 (runtime-detector 또는 사용자 직접)

### env / API key (N개)

```
DATABASE_URL          # postgres://user:password@localhost:5432/<db>
STRIPE_SECRET_KEY     # 결제 — https://dashboard.stripe.com/test/apikeys
OPENAI_API_KEY        # LLM — https://platform.openai.com/api-keys
JWT_SECRET            # 인증 — 32+ char random
```

### 외부 서비스

- Postgres (port 5432) — `pg` / `prisma` / `drizzle-orm` dep
- Redis (port 6379) — `ioredis` dep (선택)

### 포트

- 3000 (Node.js HTTP, 또는 사용자 답)

### 시스템 패키지

- (없음 또는 사용자 답)

## .env.template (답 1·2 시 자동 생성)

> 본 파일은 카탈로그 — 실제 값은 `.env` (gitignored) 에 수기 입력.

```bash
# .env.template — copy to .env and fill real values
DATABASE_URL=postgres://user:password@localhost:5432/mydb
STRIPE_SECRET_KEY=sk_test_...
OPENAI_API_KEY=sk-...
JWT_SECRET=
PORT=3000
LOG_LEVEL=info
```

## 부팅 검증 (페이즈 09 게이트 7)

| 필드 | 값 |
| --- | --- |
| `boot_command` | `<예: npm start>` |
| `healthz_url` | `<예: http://localhost:3000/healthz>` |
| 임계 | 5 초 내 200 OK (default 30 초 timeout — `boot_check.py`) |

답 3 (mock) 시 `BOOT_MODE=mock npm start` 자동 추가. 답 4 (none) 시 부팅 skip — 게이트 7 = `pass (no runtime)`.

## 보안 가드

- `.env` 자동 `.gitignore` 추가 (없으면 신설).
- `.env.template` 의 값 자리에 실 시크릿 (`sk_live_*`, `prod-*`) 잔존 금지 — self_lint C-RP RP3.
- 답 1 (실 paste) 시 frontmatter 의 `env_hash` 에 sha256 만 박힘 — 평문 0, audit 가능.
- 실 secret 의 git 커밋 감지 시 자율 차단 + `.gitignore` 자동 추가 + handoff/13 사후 보고 (ack 없음).

## Decision Trace

- **Q-D9 답:** `<1 | 2 | 3 | 4>`
- **사유:** `<왜 이 답을 골랐는지>`
- **mode:** `<real | template | mock | none>`
- **secrets_count:** `<N>`
- **boot_command:** `<command>`
- **결정 시각:** `<ISO>`
