---
skill_name: theseus-harness
skill_version: 0.2.2
phase: 04-clarify
project_id: TEMPLATE
project_run: TEMPLATE
fingerprint: TEMPLATE
prev_fingerprint: TEMPLATE
produced_at: TEMPLATE
producer_agent: clarifier
commands_count: 0
manual_only: false
entry_blocked: true
---

> **프로젝트:** `<project_id>` · **페이즈:** `04-clarify`
> **시작:** `<ISO>` · **현재 시각:** `<ISO>`

# Verification Commands — 외부 완료 검증

> **oh-my-ralph 패턴 차용 (v0.3.0)** — 본 하네스의 6 차원 rubric 가중평균 ≥ 0.999 는 *내부 정합* 측정이다. *외부에서 보아 완료* 인지는 사용자가 정의한 검증 명령으로만 판정 가능. 본 산출물의 frontmatter `entry_blocked: true` 면 페이즈 05 (비평) 진입 거부.

## 답 (Q-D8)

| Q-D8 답 | 의미 | frontmatter |
| ------ | --- | ---------- |
| 1 | CI 명령 그대로 paste | `commands_count > 0`, `manual_only: false`, `entry_blocked: false` |
| 2 | 새 검증 스니펫 자유 응답 | `commands_count > 0`, `manual_only: false`, `entry_blocked: false` |
| 3 | 자동 검증 불가 — 수동만 | `commands_count: 0`, `manual_only: true`, `entry_blocked: false` |
| (미응답) | 진입 차단 | `commands_count: 0`, `manual_only: false`, `entry_blocked: true` |

## Acceptance Criteria

각 항목은 `[SC-N] body | Verification: <command 또는 manual: ...>` 형식. oh-my-ralph 의 RALPH.md 와 정합.

```
[SC-1] 사용자 로그인이 OAuth 토큰을 발급한다 | Verification: pytest tests/auth/test_login.py -v
[SC-2] /healthz 가 200 OK 를 반환한다       | Verification: curl -fsS http://localhost:3000/healthz
[SC-3] 빌드 성공                             | Verification: npm run build
```

## Verification Commands

> 답 1/2 일 때 채움. exit 0 = pass. 답 3 일 때는 빈 블록 + Manual Verification 만.

```bash
# Run from repo root.
pytest tests/auth/ -v
curl -fsS http://localhost:3000/healthz > /dev/null
npm run build
```

## Manual Verification (선택)

bash 로 자동화 불가능한 항목만. 답 3 (`manual_only: true`) 일 때 본 섹션이 *유일한* 검증 절차 — 페이즈 09 의 `e2e_pass` 차원이 cap 0.95 로 강하되고 핸드오프에서 외부 검증 책임이 사용자에게 명시됨.

- 모바일 디바이스에서 라이브 앱 열어 5 초 내 로딩 확인.
- 1 분간 30 명 동시 접속 부하 시 P99 지연 200ms 이하 (외부 측정 필요).

## Decision Trace

- **Q-D8 답:** `<1 | 2 | 3>`
- **사유:** `<왜 이 답을 골랐는지>`
- **commands_count:** `<int>`
- **manual_only:** `<true|false>`
