# 파편화 우선 설계 컨벤션

## 한 줄 요약
**본 하네스는 *단일 헤비 스킬* 로 설계되지 않는다.** 모든 룰·도구·정책은 작은 컨벤션 파일로 분해되어 독립 갱신·교체·재사용 가능해야 한다 — Karpathy LLM Wiki 의 "compounding artifact" 패턴과 같이, 작은 문서들의 조합이 누적 가치를 만든다.

## 왜 파편화인가

ⓐ **단일 헤비 스킬의 함정** — SKILL.md 가 비대해지면 (1) 사용자/에이전트의 컨텍스트 부담 증가, (2) 부분 갱신 어려움, (3) 한 룰 변경이 다른 룰을 흔드는 결합 발생.
ⓑ **DIP 의 자기 적용** — 본 하네스가 사용자 프로젝트에 강제하는 SoC/DIP 를 *본 하네스 자체* 에 적용. 컨벤션·페이즈·에이전트·스코어링·템플릿이 *서로 추상* 에 의존, 콘크리트 결합 금지.
ⓒ **회차별 진화** — 자기 평가 회차마다 새 컨벤션이 추가될 수 있어야 함 ([`../../BOOTSTRAP.md`](../../BOOTSTRAP.md)). 단일 파일에 누적하면 매 회차 전체를 다시 읽어야 함.
ⓓ **선택적 사용** — 사용자가 본 하네스의 일부만 채택하고 싶을 때 (예: lessons.md 만, 또는 checkpoints.md 만) 분해되어 있어야 가능.

## 파편화 룰

### 1. SKILL.md 는 라이트 인덱스 — 룰 본문 박지 않음

ⓐ SKILL.md 는 *어떤 컨벤션이 어디 있는지* 가리키는 인덱스 + 14 페이즈 표만.
ⓑ 구체 룰 (예: 인터뷰 형식 / 시간 헤더 형식 / 점수 차원 / 정체 감지 임계) 은 본문 *복제* 금지 — 컨벤션 파일을 링크.
ⓒ 한 줄 요약은 SKILL.md 에 둘 수 있으나, 룰의 상세는 컨벤션에 위임.

### 2. 한 컨벤션 = 한 책임 (SRP)

각 `conventions/*.md` 는 *단일* 책임:
ⓐ `interview.md` — 사용자 질의 형식만.
ⓑ `timing.md` — 시간 헤더만.
ⓒ `diagrams.md` — 마인드맵/유즈케이스/시퀀스 진화만.
ⓓ `stack.md` — 스택 점검만.
ⓔ `build-and-config.md` — sh/bat 스크립트 + TOML + docs + .gitattributes + 병렬 가드 (관련 운영 묶음).
ⓕ `contracts.md` — frontmatter / 핑거프린트 / 단계 재진입.
ⓖ `models.md` — 에이전트 모델 매핑.
ⓗ `competition.md` — 페이즈 단위 경쟁.
ⓘ `autonomy.md` — 사전 위임 카탈로그 + 인터뷰 후 인터럽트 0.
ⓙ `lessons.md` — 정체 감지 + 레슨 전달.
ⓚ `spec-catalog.md` — 도메인별 NFR 카탈로그.
ⓛ `resources.md` — 리소스 프로파일 + 천정 자동 조정.
ⓜ `checkpoints.md` — 체크포인트 회귀 + 멀티버스 (이번 회차).
ⓝ `fragmentation.md` — 본 컨벤션.

같은 책임을 두 파일이 나누면 모순 위험 — self_lint 가 한 파일만 갱신되고 다른 파일이 stale 한 상태를 잡지 못한다.

### 3. 컨벤션 간 cross-link 명시

한 컨벤션이 다른 컨벤션의 룰을 가정하면 *반드시 링크* — `[`other.md`](other.md)`. 자기 책임 외 룰을 본문에 복제 금지. self_lint 가 cross-link 깨짐을 잡는다 (C2/C11).

### 4. 페이즈/에이전트도 파편화

ⓐ 페이즈 14 개를 단일 파일에 모으지 않음 — `phases/00-naming.md` ~ `phases/13-handoff.md` 각 파일.
ⓑ 에이전트 13 개를 단일 카탈로그에 모으지 않음 — `agents/<role>.md` 개별.
ⓒ 각 페이즈/에이전트는 자기 책임 *외* 의 컨벤션을 본문에 복제 금지 — 링크.

### 5. 도구도 파편화

ⓐ `scoring/score.py` — rubric 채점만.
ⓑ `scoring/fingerprint.py` — frontmatter 무결성만.
ⓒ `scoring/self_lint.py` — 본 저장소 자체 lint 만.
ⓓ `scoring/stagnation.py` — 정체 감지만.
ⓔ `scoring/resource_ceiling.py` — 천정 감지만.
ⓕ `scoring/checkpoint.py` — 체크포인트 회귀 + 멀티버스만.

각 도구가 단독 실행 가능 + 단독 테스트 가능 (`test_<도구>.py`) — 한 도구의 변경이 다른 도구를 흔들지 않음.

### 6. 새 룰 = 새 컨벤션 파일 (default)

회차마다 새 룰이 등장할 때 *기존 파일 비대화* 보다 *새 컨벤션 추가* 를 default 로. 단, 같은 책임의 작은 보강은 기존 파일에 추가 (예: `interview.md` 의 확증 회귀는 같은 인터뷰 책임이므로 같은 파일에).

판단 기준:
ⓐ 새 룰이 *기존 책임의 일부* 인가? → 기존 파일 보강.
ⓑ 새 룰이 *독립된 새 책임* 인가? → 새 컨벤션 파일.
ⓒ 의심되면 새 파일 — 비대화보다 분해의 비용이 항상 작다.

### 7. self_lint 가 파편화를 강제

ⓐ SKILL.md 의 본문 길이가 임계 초과 → fail (룰 본문이 누적된 신호).
ⓑ 컨벤션 파일이 임계 초과 → 분해 권고.
ⓒ 같은 룰이 두 파일에 복제됨 → fail (DRY 위반).
ⓓ 신규 컨벤션 파일이 cross-link 안 됨 → fail (고립).

이 항목들은 [`../scoring/self_lint.py`](../scoring/self_lint.py) 의 C26 (파편화 점검) 으로 구현 가능 — 후속 PR 에서 강화.

## LLM Wiki 패턴 — 작은 문서들의 누적 가치

본 컨벤션은 Karpathy 의 *LLM Wiki* (2026.04 gist) 패턴과 정합:

ⓐ **Two Outputs Rule** — 모든 작업은 작업 결과물 + 위키 업데이트 두 출력. 본 하네스에서는 *산출물 + lesson_pack* 매핑.
ⓑ **Contradictions are flagged, not overwritten** — 모순은 덮어쓰지 않고 기록. 본 하네스에서는 자기 평가의 `intent/05-critique.md` 에 갭으로 누적.
ⓒ **Lint** — 주기적 위키 건강 점검. 본 하네스의 `self_lint.py`.
ⓓ **Decision Records** — 선택/포기 이유 기록. 본 하네스의 `intent/05-decisions.md` + `multiverse/<id>/verdict.md`.

## 안티 패턴

ⓐ **SKILL.md 에 룰 본문 복제** — 컨벤션 파일이 곧 truth source. SKILL.md 는 인덱스만.
ⓑ **새 룰을 기존 큰 파일에 무한 추가** — 책임이 흐려지고 self_lint 가 cross-link 깨짐 못 잡음.
ⓒ **컨벤션 간 모순** — 한 룰을 두 파일에서 다르게 정의하면 어느 것이 맞는지 모름. self_lint 의 책임.
ⓓ **단일 테스트 파일에 모든 도구 테스트** — 도구별 `test_<name>.py` 분리. pytest 단일 디렉터리 실행도 OK.
ⓔ **분해 회피의 핑계** — "이건 작은 룰이라 기존 파일에 넣어도 돼" 가 누적되면 결국 비대. 의심되면 새 파일.

## 이 컨벤션의 자기 적용

본 컨벤션 자체도 작은 단일 책임 파일 — *파편화 정책만* 다룬다. 인터뷰·시간·다이어그램·스택 등은 각자 자기 파일. 본 컨벤션이 비대해지면 그 자체가 자기 룰 위반이므로, 분해할 시점.
