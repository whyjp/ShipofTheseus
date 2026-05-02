# docs/

본 디렉터리는 사용자 진입점 가이드 모음이다. 깊은 콘텐츠는 [`skills/theseus-harness/`](../skills/theseus-harness/) 가 단일 source of truth — 본 docs/ 는 *지도와 사용설명서* 로 한정한다.

## 무엇이 어디에

| 위치 | 목적 | 깊이 |
| ---- | ---- | --- |
| [`../README.md`](../README.md) | 저장소 첫인상, 14 페이즈 표, 9 스킬 표, 빠른 사용 | 5 분 읽기 |
| [`../INSTALL.md`](../INSTALL.md) | 설치·갱신·트러블슈팅 | 10 분 |
| [`../PHILOSOPHY.md`](../PHILOSOPHY.md) | 신뢰 담보 의미, 도자기 장인 비유, Ralph/우로보로스 합성 | 30 분 |
| [`../BOOTSTRAP.md`](../BOOTSTRAP.md) | 본 하네스로 본 저장소를 평가하는 부트스트래핑 절차 | 20 분 |
| [`skills/`](skills/) | **스킬별 가이드 — 역할, 입출력, 단독 호출 시점, FAQ** | 각 5–10 분 |
| [`../skills/theseus-harness/`](../skills/theseus-harness/) | 깊은 콘텐츠 (21 컨벤션 + 14 페이즈 + 13 에이전트 + 채점기) | 본격 |

## 어떻게 읽는가

ⓐ **처음 사용자** — `../README.md` → `skills/theseus-orchestrator.md` (전체 자동 진행) → `../INSTALL.md` → 실제 호출.
ⓑ **단일 페이즈 재진입** — `skills/theseus-<페이즈>.md` (해당 스킬 가이드) → `../skills/theseus-harness/conventions/contracts.md` (frontmatter 입력 계약).
ⓒ **하네스 자체 기여자** — `../BOOTSTRAP.md` → `../skills/theseus-harness/SKILL.md` → 21 컨벤션.
ⓓ **설계 동기 의문** — `../PHILOSOPHY.md`.

## 스킬 가이드 인덱스

[`skills/`](skills/) 아래 9 개 가이드:

- [`theseus-orchestrator`](skills/theseus-orchestrator.md) — 전체 자동 진행 (가장 흔한 진입점)
- [`theseus-intent`](skills/theseus-intent.md) — 페이즈 00–05
- [`theseus-plan`](skills/theseus-plan.md) — 페이즈 06–07
- [`theseus-implement`](skills/theseus-implement.md) — 페이즈 08
- [`theseus-quality`](skills/theseus-quality.md) — 페이즈 09
- [`theseus-sprint`](skills/theseus-sprint.md) — 페이즈 10–11
- [`theseus-webview`](skills/theseus-webview.md) — 페이즈 12
- [`theseus-handoff`](skills/theseus-handoff.md) — 페이즈 13
- [`theseus-harness`](skills/theseus-harness.md) — 플래그십 (단일 source of truth, 단독 호출 가능)
