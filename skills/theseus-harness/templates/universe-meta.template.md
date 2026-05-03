---
universe_id: TEMPLATE                # 예: 1-domain-first / 1-a-by-bounded-context (자식)
seed: TEMPLATE                       # domain-first | adapter-first | minimal-subtraction | tdd-topology | strict-layering
parent: null                         # null = root universe, "<parent universe_id>" = 자식
depth: 1                             # 1 = root, 2 = 자식 (cap 그레이드별 grades.md 매트릭스)
hypothesis: |                        # 본 시드가 본 의도에 맞다 가정한 이유 (planner 가 작성)
  TEMPLATE — 한 단락 자연어. 예:
  "본 의도는 결제 도메인이 핵심이고 인증/세션은 부수적이다 — 따라서 도메인
  boundary 가 모듈 boundary 인 domain-first 시드가 자연스럽다. 어댑터 다양성은
  현 단계에서 단일 PG/Stripe 가정으로 충분."

# 5 차원 점수 (plan-reviewer 가 페이즈 07 콜드 리딩 후 채움)
score:
  cold_recall: 0.0       # 1- 답이 intent/01-intent.md 와 의미상 일치 (< 0.6 즉시 탈락)
  dip_strictness: 0.0    # DIP 위반 TODO 수 역 비례
  simplicity: 0.0        # 모듈 / TODO 수 (적을수록 가산)
  test_topology: 0.0     # leaf TODO 마다 테스트 + E2E cover
  fe_be_parity: 0.0      # FE/BE 의존 짝맞춤 (G4+)
  overall: 0.0           # 가중 합 (auto: tournament.py 가 채움)

status: pending          # pending → winner | runner_up | loser | merged (tournament.py 가 갱신)

# 산출물 (본 우주 디렉터리 안)
artifacts:
  - 06-plan.md           # 본 우주의 플랜 (Mermaid 시퀀스 동봉)
  - 07-cold-read.md      # plan-reviewer 의 4 답 (콜드 리딩)
  - children/            # 깊이 ≥ 2 시 자식 우주 (있을 때만)

# fingerprint chain (contracts.md 의 frontmatter 확장)
skill_name: theseus-harness
skill_version: TEMPLATE
phase: 06-plan
project_id: TEMPLATE
fingerprint: TEMPLATE
prev_fingerprint: TEMPLATE
produced_at: TEMPLATE
producer_agent: planner
---

# Universe `<universe_id>` — `<seed>`

> **시드**: `<seed>` ([`../../conventions/plan-tree.md`](../../conventions/plan-tree.md))
> **부모**: `<parent or null>` · **깊이**: `<depth>`

## 가설 (왜 이 시드가 본 의도에 맞는가)

(`hypothesis` frontmatter 필드 본문화)

## 본 우주의 플랜 요약

(planner 가 작성 — 본 우주가 어떻게 분할했는지 한 단락. 상세는 `06-plan.md`.)

## 토너먼트 결과 (plan-reviewer + tournament.py)

`07-cold-read.md` 의 4 답 + `tournament.py` 가 채운 5 차원 점수 + status.

- 콜드 리딩 1- 답: `<요약>` (의도 일치 여부 평가)
- 종합 점수: `<overall>`
- 자격: `<pass | disqualified (cold_recall < 0.6)>`
- 결정: `<winner | runner_up | loser | merged>` ← `tournament.md` 의 resolve

## 자식 우주 (있을 때만)

깊이 분기 트리거 시 `children/<universe_id-a-...>/` 디렉터리. 자식 시드는 부모 시드 *상속하되 한 차원만* 다르게 (예: `domain-first/by-bounded-context` vs `/by-aggregate-root`).

- (없음 — 본 우주는 leaf)
