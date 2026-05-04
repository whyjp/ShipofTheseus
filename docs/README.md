# docs/

본 디렉터리는 사용자 진입점 가이드 모음이다. 깊은 콘텐츠는 [`skills/theseus-harness/`](../skills/theseus-harness/) 가 단일 source of truth — 본 docs/ 는 *지도와 사용설명서* 로 한정한다.

## 무엇이 어디에

| 위치 | 목적 | 깊이 |
| ---- | ---- | --- |
| [`../README.md`](../README.md) | 저장소 첫인상, 15 페이즈 표, 2 스킬 표, AIDE 멀티버스 컨셉 격상 | 5 분 읽기 |
| [`../INSTALL.md`](../INSTALL.md) | 설치·갱신·트러블슈팅 | 10 분 |
| [`../PHILOSOPHY.md`](../PHILOSOPHY.md) | 신뢰 담보 의미, AIDE 멀티버스 — 진짜 차별 동력, 도자기 장인 비유, 합성 패턴 6 (Ralph/OhMy/우로보로스/AIDE/Wiki/Da Capo) | 30 분 |
| [`../BOOTSTRAP.md`](../BOOTSTRAP.md) | 본 하네스로 본 저장소를 평가하는 부트스트래핑 절차 | 20 분 |
| [`../CHANGELOG.md`](../CHANGELOG.md) | v0.9.0 → v0.9.16 의미 있는 변경 기록 | 10 분 |
| [`skills/`](skills/) | **스킬별 가이드 — 역할, 입출력, FAQ** | 각 5–10 분 |
| [`../skills/theseus-harness/`](../skills/theseus-harness/) | 깊은 콘텐츠 (47 컨벤션 + 15 페이즈 + 18 에이전트 + 2 도메인 어댑터 + 채점기) | 본격 |

## 어떻게 읽는가

ⓐ **처음 사용자** — `../README.md` → `skills/theseus-orchestrator.md` (전체 자동 진행) → `../INSTALL.md` → 실제 호출.
ⓑ **단일 페이즈 재진입** — `skills/theseus-harness.md` → `../skills/theseus-harness/conventions/contracts.md` (frontmatter 입력 계약).
ⓒ **하네스 자체 기여자** — `../BOOTSTRAP.md` → `../skills/theseus-harness/SKILL.md` → 47 컨벤션.
ⓓ **설계 동기 의문** — `../PHILOSOPHY.md` (AIDE 멀티버스 + 도자기 장인).

## 스킬 가이드 인덱스

[`skills/`](skills/) 아래 2 개 가이드 (v0.9.0 sprint-03-b 에서 7 phase 분해 stub 제거 — pure delegation cost > benefit):

- [`theseus-orchestrator`](skills/theseus-orchestrator.md) — 사용자 entry point, 15 페이즈 자율 driver
- [`theseus-harness`](skills/theseus-harness.md) — 콘텐츠 source of truth (47 컨벤션 + 18 에이전트 + 채점기 + 템플릿)
