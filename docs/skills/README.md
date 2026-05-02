# 스킬 가이드

본 디렉터리는 9 스킬 각각의 *사용자 진입점* 가이드다. 각 스킬의 `SKILL.md` 는 LLM 이 읽는 *기계 진입점* — 본 가이드는 사람이 읽고 "이걸 언제 어떻게 호출하는가" 를 빠르게 파악하기 위한 문서다.

## 스킬 호출 순서 (전체 자동 진행)

```
theseus-orchestrator
   │
   ├─ 1. theseus-intent      ─ 페이즈 00–05 (명명·의도·인터뷰·비평)
   ├─ 2. theseus-plan        ─ 페이즈 06–07 (TODO DAG·재이해)
   ├─ 3. theseus-implement   ─ 페이즈 08    (모듈 구현)
   ├─ 4. theseus-quality     ─ 페이즈 09    (5 게이트)
   ├─ 5. theseus-sprint      ─ 페이즈 10–11 (무한 루프·바이섹트)
   ├─ 6. theseus-webview     ─ 페이즈 12    (bun 웹뷰)
   └─ 7. theseus-handoff     ─ 페이즈 13    (요약·PR)

theseus-harness 는 위 모든 페이즈의 콘텐츠 단일 source of truth.
분해 스킬 없이 단독 호출도 가능.
```

## 가이드 목록

| 스킬 | 가이드 | 페이즈 | 단독 호출 가능 |
| ---- | ----- | ----- | -------------- |
| [`theseus-orchestrator`](theseus-orchestrator.md) | 전체 진행 인덱스 | 00–13 | ✓ |
| [`theseus-intent`](theseus-intent.md) | 명명·의도·인터뷰·비평 | 00–05 | ✓ |
| [`theseus-plan`](theseus-plan.md) | TODO DAG·재이해 | 06–07 | ✓ (intent 산출물 입력) |
| [`theseus-implement`](theseus-implement.md) | 모듈 구현 | 08 | ✓ (plan 산출물 입력) |
| [`theseus-quality`](theseus-quality.md) | 5 게이트 | 09 | ✓ (impl 산출물 입력) |
| [`theseus-sprint`](theseus-sprint.md) | 무한 루프·바이섹트 | 10–11 | ✓ (quality 산출물 입력) |
| [`theseus-webview`](theseus-webview.md) | bun 웹뷰 | 12 | ✓ (모든 페이즈 산출물 입력) |
| [`theseus-handoff`](theseus-handoff.md) | 요약·PR | 13 | ✓ (모든 페이즈 + sprint 결과 입력) |
| [`theseus-harness`](theseus-harness.md) | **플래그십** — 단일 source of truth | 00–13 | ✓ |

## 단독 호출의 입력 계약

각 분해 스킬은 *이전 단계의 frontmatter* 를 검증한 뒤 자기 작업을 시작한다. 검증 실패 시 진입을 거부 — 외부에서 받은 산출물을 무비판으로 받아들이지 않게 하는 안전 장치다. 자세한 frontmatter 스펙은 [`../../skills/theseus-harness/conventions/contracts.md`](../../skills/theseus-harness/conventions/contracts.md).

```bash
# 외부 산출물 검증
python skills/theseus-harness/scoring/fingerprint.py verify --file <산출물>

# 핑거프린트 체인 무결성
python skills/theseus-harness/scoring/fingerprint.py chain --dir .ShipofTheseus/<프로젝트>/
```

## 깊은 콘텐츠는 어디에

본 가이드는 *진입점* 만 다룬다. 다음은 단일 source of truth:

- **컨벤션 (21 개)** — [`../../skills/theseus-harness/conventions/`](../../skills/theseus-harness/conventions/)
- **페이즈 (14 개)** — [`../../skills/theseus-harness/phases/`](../../skills/theseus-harness/phases/)
- **에이전트 (13 개)** — [`../../skills/theseus-harness/agents/`](../../skills/theseus-harness/agents/)
- **채점기** — [`../../skills/theseus-harness/scoring/`](../../skills/theseus-harness/scoring/)
- **템플릿** — [`../../skills/theseus-harness/templates/`](../../skills/theseus-harness/templates/)
