# Phase 05 — 비평·대안

## 한 줄 요약
**계획 작성 전에 *의도 자체* 를 친다** — 미스초이스, 범위 함정, 더 단순한 대안, 이미 존재하는 해법. 비평 에이전트는 명시적으로 적대적이며 동의보다 유용함을 우선.

## 입력
- `intent/01-intent.md`
- `intent/04-answers.md`
- `intent/04-autonomy.md` — Q-D1~Q-D8 사전 위임 답 (8 줄)
- `intent/04-verification.md` — **진입 게이트** (oh-my-ralph Verification Commands 패턴, v0.3.0). frontmatter `entry_blocked: true` 면 본 페이즈 진입 거부 — 사용자가 외부 완료 검증 명령을 제시 안 함. `commands_count > 0 || manual_only == true` 일 때만 진입 허용.
- 레포의 기존 코드 (이미 일부를 풀고 있는 prior art 탐색).

## 진입 가드 (v0.3.0)

비평 에이전트는 본 페이즈 시작 전에 다음 검증:

```python
verification_fm = read_frontmatter("intent/04-verification.md")
if verification_fm.get("entry_blocked", False):
    raise SkillEntryError(
        "Q-D8 Verification Commands 부재 — oh-my-ralph 룰 차용. "
        "intent/04-verification.md 의 bash 블록을 채우거나 manual_only=true 로 표시 후 재시도. "
        "검증 없는 자율 진행은 본 하네스가 거부."
    )
if verification_fm.get("manual_only", False):
    log_warning(
        "manual_only=true — 페이즈 09 의 e2e_pass 차원 cap 0.95 적용. "
        "핸드오프에서 외부 검증 책임 사용자 명시."
    )
```

이 가드가 v0.3.0 의 가장 중요한 외부 정합 게이트.

## 서브에이전트
[`../agents/critic.md`](../agents/critic.md).

## 산출물
`intent/05-critique.md`:

a- **미스초이스** — 합리적으로 보이지만 반복적으로 역효과 나는 패턴 (조기 추상화, 분산 모놀리스, sync-where-async, 자체 인증 등).
b- **범위 위험** — "기왕 하는 김에" 로 슬며시 들어오는 기능.
c- **재사용 가능한 기존 해법** — `path/to/file.go:NN` 또는 잘 알려진 라이브러리.
d- **대안 접근** — 최소 2개, 트레이드오프 명시.
e- **추천 경로** — 비평가의 한 표.
f- **사용자에게 넘겨야 할 트레이드오프** — 비즈니스적 함의가 있어 비평가 단독 결정 부적절.

지휘자는 f- 항목을 [`../conventions/interview.md`](../conventions/interview.md) 컨벤션으로 사용자에게 묻고 답을 `intent/05-decisions.md` 에 기록.

## 성공 기준

a- 미스초이스 1개 이상 명시.
b- 대안 2개 이상 + 트레이드오프.
c- 사용자 트레이드오프 1개 이상이 `05-decisions.md` 로 마무리.

## 백엔드 스택 기본값

사용자가 명시하지 않은 한 백엔드/API/엔진은 **Go**. 비평가는 이 가정을 받아들이되, 도메인이 Go 와 부적합한 강한 이유가 있으면 대안 후보 중 하나로 명시 (예: ML inference 라면 Python 후보).

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).

## v0.9.20 sprint-14 — Directional Simplification 표 의무

### 본문 의무 표 ([`../conventions/directional-simplification.md`](../conventions/directional-simplification.md), bg)

`intent/05-critique.md` 신규 의무 섹션 — 각 introduced simplification 에 대해 *방향성 + 정량 + reason* 1 줄 :

```markdown
## Simplification 방향성·정량 표 (directional-simplification.md bg 의무)

| ID | simplification | direction (↑/↓/?) | magnitude (±%) | reason | impact_dim |
|---|---|---|---|---|---|
| S-1 | (예: "shared lane → independent directions") | ↑ throughput | +5% | "real congestion ramp couples directions" | data_topology |
| S-2 | (예: "warmup=0 in single 480 min shift") | ? | n/a | "first 30 min noise diluted" | conceptual |
```

각 row 의무 :
- **direction** : ↑ / ↓ / ? — 해당 simplification 이 *없을 때* 결과가 어느 방향
- **magnitude** : ±% 또는 `n/a` (정량 추정 불가 시)
- **reason** : 1 줄 mechanism

산출물 frontmatter 에 자동 sync :

```yaml
---
simplifications:
  - {id: S-1, direction: '↑', magnitude_pct: 5, impact_dim: data_topology}
  - {id: S-2, direction: '?', magnitude_pct: null, impact_dim: conceptual}
simplification_count: 2
direction_known_ratio: 0.50
magnitude_known_ratio: 0.50
---
```

self_lint C-DS 가 frontmatter / 본문 / row 정합 검증.

### Contested Decisions Source 산출 ([`../conventions/contested-decision-multiverse.md`](../conventions/contested-decision-multiverse.md), bf)

본 페이즈의 비평 본문 중 *stress-test ⚠* 마크는 페이즈 06 의 contested decisions 추출 source 가 됨. critique 산출물 본문 안티-패턴 table 에 ⚠ severity column 의무 (페이즈 06 의 `extract_contested_decisions()` 가 본 column 을 자동 파싱).
