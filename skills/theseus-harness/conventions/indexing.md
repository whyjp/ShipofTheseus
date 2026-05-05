---
id: indexing
category: core
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# 산출물 인덱싱 컨벤션 — 산출물 = DB, 비직렬성 트리, 오해 방지 허들

## 한 줄 요약
**`.ShipofTheseus/<프로젝트>/` 트리 자체가 데이터베이스다.** 멀티버스(checkpoints) + 경쟁(competition) + 서브에이전트 재귀(sub-agents) 로 인해 산출물이 *선형 체인이 아닌 트리/그래프* 구조를 갖는 본 하네스의 가장 큰 차별점이자 가장 큰 함정. **인덱스가 곧 허들·장치** — `INDEX.md` 자동 갱신 + frontmatter 비직렬성 메타 + self_lint 무결성 검증으로 사용자/에이전트가 산출물 구조를 *오해 없이* 이해.

## 본 하네스의 산출물이 다른 코딩 작업과 다른 이유

일반 코딩 작업: 산출물 = 코드 + 커밋 (선형 chain).
본 하네스: 산출물 = **선형 페이즈 chain × 멀티버스 분기 × 서브에이전트 재귀** = **3 차원 그래프**.

```
시간 →
페이즈 01 (단일)                                     ← 1차원 (선형 페이즈)
    ↓
페이즈 06 (계획)                                     
    ↓ multiverse 트리거
페이즈 06.a, 06.b, 06.c (3 우주 격리 병렬)            ← 2차원 (우주 분기)
    ↓ 우주 a 채택
페이즈 08 (구현)
    ↓ T-020 LOC > 200, 서브에이전트 재귀
T-020/sub/A.1, A.2, A.3 (3 하위 모듈)                ← 3차원 (서브에이전트 깊이)
    ↓ A.2 회귀 누적 → 깊이 2 분해
T-020/sub/A.2/sub/A.2.x, A.2.y                       ← 깊이 2
```

**이 3 차원이 인덱스 없으면 즉시 미궁** — 사용자도, 다음 페이즈 에이전트도, 외부 스킬도 "현재 어떤 우주에 있는가, 부모는 누구인가" 답 못 함.

## 산출물 = DB 패러다임

각 산출물 마크다운 파일 = **노드**. frontmatter = **메타데이터 행**. 디렉터리 트리 = **테이블 인덱스**. fingerprint = **무결성 검증 컬럼**.

```
산출물 노드
├─ frontmatter (메타데이터)
│   ├─ skill_name, skill_version (출처)
│   ├─ phase, project_id, project_run (분류)
│   ├─ fingerprint, prev_fingerprint (체인)
│   ├─ universe, parent_branch (멀티버스 좌표) ← NEW
│   ├─ parent_module, depth (서브에이전트 좌표) ← NEW
│   ├─ branch_kind (분기 종류) ← NEW
│   └─ produced_at, producer_agent (기록)
└─ 본문 (실 데이터 — 마크다운/json)
```

조회 예 (CLI 또는 INDEX.md):
- "현재 활성 우주의 모든 페이즈 산출물" → `WHERE branch_kind != 'multiverse_loser'`
- "T-020 의 모든 하위 모듈" → `WHERE parent_module = 'T-020'`
- "회귀 누적 3 회 이상" → 체크포인트 트리에서 같은 노드 ≥ 3 회 등장

## frontmatter 비직렬성 메타 (contracts.md 확장)

기존 `contracts.md` 의 frontmatter 스키마에 다음 필드 추가:

```yaml
---
skill_name: theseus-harness
skill_version: 0.2.1
phase: 06-plan
project_id: atlas-ledger
project_run: 20260501-174412
fingerprint: sha256:...
prev_fingerprint: sha256:...
produced_at: 2026-05-01T17:46:30+09:00
producer_agent: planner

# ── 비직렬성 메타 (선형 작업이면 모두 null) ──
universe: a                  # 멀티버스 우주 식별자 (a/b/c). 선형 작업은 null.
parent_branch: 06-plan       # 멀티버스 분기 ID (예: "06-plan" 페이즈에서 분기)
parent_module: T-020         # 서브에이전트 분해의 부모 TODO ID. 일반 모듈은 null.
depth: 1                     # 재귀 깊이 (서브에이전트). 0 = 페이즈 루트.
branch_kind: multiverse_winner | multiverse_loser | sub_parallel | sub_sequential | sub_competition | sequential
                             # null = 일반 선형 페이즈
---
```

각 필드의 *선택성*:

| 필드 | 일반 선형 | 멀티버스 | 서브에이전트 |
| ---- | --------: | -------: | ----------: |
| `universe` | null | `a`/`b`/`c` | null (또는 부모 우주 상속) |
| `parent_branch` | null | 분기 페이즈 ID | null |
| `parent_module` | null | null | 부모 TODO ID |
| `depth` | 0 | 0 (페이즈 단위) | 1~2 |
| `branch_kind` | `sequential` | `multiverse_winner`/`_loser` | `sub_parallel`/`_sequential`/`_competition` |

## INDEX.md — 산출물 트리 자동 인덱스

`.ShipofTheseus/<프로젝트>/INDEX.md` 가 *모든 산출물의 트리 뷰* 를 항상 최신 상태로 유지. 매 페이즈/체크포인트/서브에이전트 산출 시 [`../scoring/index_builder.py`](../scoring/index_builder.py) 가 자동 재생성.

### INDEX.md 구조

```markdown
# 산출물 인덱스 — `<프로젝트>` (run `<project_run>`)

> **시작:** ... · **현재:** ... · **누적 경과:** ...
> **활성 우주:** a · **총 산출물:** 47 · **멀티버스 분기:** 1 · **서브 분해:** 3

## 트리 뷰

```
naming/00-naming.md                                    [ok ✓]
└─ intent/01-intent.md                                 [ok ✓]
   ├─ intent/02-intent-review.md                       [ok ✓]
   ├─ intent/03-comprehension.md                       [ok ✓]
   ├─ intent/04-{questions,answers,autonomy,grade,resource-profile,stack}.md
   └─ intent/05-{critique,decisions}.md                [ok ✓]
      └─ plan/06-plan.md                               [ok ✓]
         ├─ multiverse/06-plan/universe-a/             [WINNER ★]
         │  └─ plan/07-plan-review.md
         │     └─ impl/08-impl-log.md
         │        ├─ T-020/                            [subdivided depth=1, mode=parallel]
         │        │  ├─ sub/A.1/                       [ok ✓]
         │        │  ├─ sub/A.2/                       [DIP violation ✗ → 회귀]
         │        │  └─ sub/A.3/                       [ok ✓]
         │        └─ T-040/                            [single]
         ├─ multiverse/06-plan/universe-b/             [LOSER, score 0.91]
         └─ multiverse/06-plan/universe-c/             [LOSER, score 0.88]
```

## 통계

| 항목 | 값 |
| --- | -: |
| 총 산출물 | 47 |
| 활성 우주 | a (Δ +0.06 vs runner-up b) |
| 패배 우주 (보존) | b (0.91), c (0.88) |
| 서브 분해 트리거 | T-020 (LOC=247, parallel mode) |
| 회귀 누적 | T-020/sub/A.2 (1 회, DIP 위반) |
| 체크포인트 | 12 개 (페이즈 06: 3 / 08: 5 / 10: 4) |

## 무결성

- ✓ fingerprint 체인: 47/47 verify pass
- ✓ universe 일관성: 모든 활성 산출물이 universe=a
- ✓ parent_module 체인: T-020/sub/A.{1,3} → parent=T-020 검증
- ⚠️ depth: 한 케이스 깊이 2 (T-020/sub/A.2/...) — 한도 내

## 회귀 가능 지점

[`checkpoints.md`](../../skills/theseus-harness/conventions/checkpoints.md) 의 회귀 매핑 후보:

- `intent_mismatch` → `intent/01-intent.md` 체크포인트
- `plan_misfit` → `plan/06-plan.md` (현재 활성 우주 a)
- `module_impl_violation` (T-020) → `impl/T-020/` 직전 체크포인트
- `test_regression` → `sprints/N-1/` (가장 최근 정상 sprint)
```

## 인덱스 자동 갱신 의무

a- 매 페이즈 산출물 작성 *직후* `index_builder.py rebuild` 자동 호출.
b- 멀티버스 분기/머지 직후 자동 갱신 — 우주 상태 변화 즉시 반영.
c- 서브에이전트 디스패치/머지 직후 자동 갱신 — 분해 트리 변화 반영.
d- self_lint C30 가 INDEX.md 의 *최신성* 검증 — 가장 최근 산출물의 timestamp ≤ INDEX.md 갱신 시각.

## index.json — 기계 판독용 인덱스

INDEX.md 와 같은 데이터의 *프로그램 친화 형식*:

```json
{
  "project_id": "atlas-ledger",
  "project_run": "20260501-174412",
  "rebuilt_at": "2026-05-01T18:42:11Z",
  "active_universe": "a",
  "total_artifacts": 47,
  "tree": [
    {
      "path": "naming/00-naming.md",
      "fingerprint": "sha256:...",
      "phase": "00-naming",
      "universe": null,
      "parent_module": null,
      "depth": 0,
      "branch_kind": "sequential",
      "children": ["intent/01-intent.md"]
    },
    ...
  ],
  "multiverses": [
    {
      "branch_id": "06-plan",
      "winner": "a",
      "losers": ["b", "c"],
      "scores": {"a": 0.97, "b": 0.91, "c": 0.88}
    }
  ],
  "subdivisions": [
    {
      "parent_module": "T-020",
      "mode": "parallel",
      "depth": 1,
      "sub_modules": ["A.1", "A.2", "A.3"],
      "eliminated": ["A.2"]
    }
  ],
  "integrity": {
    "fingerprint_chain": "ok",
    "universe_consistency": "ok",
    "parent_module_chain": "ok",
    "depth_within_limit": "warn (1 case at depth=2)"
  }
}
```

## 허들로서의 인덱스

본 하네스의 *오해 방지 장치* — 다음 시점에 INDEX.md / index.json 이 사용자/에이전트의 마지막 안전장치:

a- **사용자 핸드오프 시** (페이즈 13) — handoff/13-handoff.md 가 INDEX.md 를 인용해 "어떤 결정이 어디에 기록됐는지" 한 표로 제시.
b- **단독 스킬 호출 시** ([`sub-agents.md`](sub-agents.md) §"단독 호출 input 계약") — 진입 스킬이 INDEX.md 를 먼저 읽고 *현재 어떤 우주의 어떤 산출물이 valid 한가* 판단.
c- **회귀 결정 시** ([`checkpoints.md`](checkpoints.md) `find_regression_target`) — 인덱스 트리에서 회귀 가능 지점을 즉시 식별.
d- **외부 검토 시** — PR 리뷰어가 INDEX.md 한 파일만 봐도 본 회차의 모든 결정이 한눈에.

## 인덱스가 깨지는 상황과 보호

| 깨짐 신호 | 원인 | 보호 |
| -------- | ---- | ---- |
| INDEX.md 와 실제 디렉터리 불일치 | 산출물 작성 후 자동 재생성 누락 | self_lint C30 — INDEX 갱신 시각 ≥ 모든 산출물 timestamp |
| `parent_module` 가 존재하지 않는 모듈 가리킴 | frontmatter 오기재 | C30 — 부모 존재 여부 검증 |
| 활성 우주에 fingerprint 체인 끊김 | tamper 또는 누락 | C30 — fingerprint chain verify 통합 |
| 같은 universe 안에 다중 winner | resolve 알고리즘 오작동 | index_builder 가 multiverse 별 winner 단일성 검증 |
| 깊이 3 이상 서브에이전트 | sub-agents.md 의 깊이 한도 위반 | index_builder warn + checkpoints.md 의 자동 페이즈 06 회귀 |

## 안티 패턴

a- **INDEX.md 수동 작성** — `index_builder.py` 가 자동 재생성 source. 수동 편집은 다음 자동 재생성에서 덮어써짐. *사용자가 수정하고 싶으면 frontmatter / 산출물 본문* 을 고침.
b- **frontmatter 비직렬성 메타 누락** — universe/parent_module/depth/branch_kind 누락은 인덱스 빌더가 *기본값* (선형) 으로 추론하지만 — 실제 멀티버스/서브에이전트 산출물이 누락하면 트리 잘못 그려짐. 산출 에이전트 의무.
c- **자기 갱신 사이클 무시** — 한 페이즈 산출 후 즉시 인덱스 재생성 안 하면, 다음 페이즈가 stale INDEX 로 잘못된 입력 검증. C30 의 timestamp 검사로 차단.
d- **인덱스를 사용자 인터럽트 트리거로 활용** — 인덱스는 *사후 리뷰 도구*. 페이즈 04 외 사용자 인터럽트 0 룰 ([`autonomy.md`](autonomy.md)) 변경 안 됨.
