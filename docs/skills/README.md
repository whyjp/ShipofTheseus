# 스킬 가이드

본 디렉터리는 v0.9.16 기준 **2 스킬** 각각의 *사용자 진입점* 가이드다. 각 스킬의 `SKILL.md` 는 LLM 이 읽는 *기계 진입점* — 본 가이드는 사람이 읽고 "이걸 언제 어떻게 호출하는가" 를 빠르게 파악하기 위한 문서다.

## 스킬 호출 (전체 자동 진행)

```
사용자 요청
   │
   ▼
theseus-orchestrator (사용자 entry point, HARD-RULE + 그레이드 인덱스)
   │  콘텐츠 source 동반 의존
   ▼
theseus-harness (15 페이즈 + 47 컨벤션 + 18 에이전트 + 채점기 + 2 도메인 어댑터)
   │
   └─ 페이즈 04 인터뷰 1회 후 인터럽트 0
      └─ AIDE multiverse (페이즈 06 plan-tree + 페이즈 02/05/08/11/13 multi-phase 확장)
         └─ Layer 3 결과물 허들 supremacy (메모리/컨벤션 override 불가)
```

> **v0.9.0 sprint-03-b 단순화** — 이전 9 SKILL.md (orchestrator + 7 phase 분해 stub + harness) 에서 7 phase stub 제거. pure delegation 이라 cost > benefit. 사용자 entry namespace `/shipoftheseus:theseus-orchestrator` 동일.

## 가이드 목록

| 스킬 | 가이드 | 페이즈 | 비고 |
| ---- | ----- | ----- | ----- |
| [`theseus-orchestrator`](theseus-orchestrator.md) | 사용자 entry, 자율 driver | 00–14 (15 페이즈) | HARD-RULE 1~9 + 그레이드 매트릭스 |
| [`theseus-harness`](theseus-harness.md) | **콘텐츠 source of truth** | 00–14 (15 페이즈) | 47 컨벤션 + 18 에이전트 + 채점기 + 2 도메인 어댑터 |

## 핸드오프 입력 계약

orchestrator 가 페이즈마다 호출하는 sub-agent 는 *이전 페이즈 산출물의 frontmatter* 를 검증한 뒤 자기 작업을 시작한다. 검증 실패 시 진입을 거부 — fingerprint 체인이 깨진 산출물을 무비판으로 받지 않게 하는 안전 장치다. 자세한 frontmatter 스펙은 [`../../skills/theseus-harness/conventions/contracts.md`](../../skills/theseus-harness/conventions/contracts.md).

```bash
# 외부 산출물 검증
python skills/theseus-harness/scoring/fingerprint.py verify --file <산출물>

# 핑거프린트 체인 무결성
python skills/theseus-harness/scoring/fingerprint.py chain --dir .ShipofTheseus/<프로젝트>/
```

## 깊은 콘텐츠는 어디에

본 가이드는 *진입점* 만 다룬다. 다음은 단일 source of truth:

- **컨벤션 (41 개)** — [`../../skills/theseus-harness/conventions/`](../../skills/theseus-harness/conventions/)
- **도메인 어댑터 (2 개, v0.9.13~)** — [`../../skills/theseus-harness/conventions/domain-adapters/`](../../skills/theseus-harness/conventions/domain-adapters/)
- **페이즈 (15 개)** — [`../../skills/theseus-harness/phases/`](../../skills/theseus-harness/phases/)
- **에이전트 (18 개)** — [`../../skills/theseus-harness/agents/`](../../skills/theseus-harness/agents/)
- **채점기** — [`../../skills/theseus-harness/scoring/`](../../skills/theseus-harness/scoring/)
- **템플릿** — [`../../skills/theseus-harness/templates/`](../../skills/theseus-harness/templates/)
