---
id: intent-optional-disambiguation
category: interview
applies-to-phases: '[01,04]'
applies-to-grades: '[all]'
trigger-when: 'user utterance contains optional marker'
indexed-in: conventions/INDEX.md
---

# Intent Optional Disambiguation — "additional / 해도 좋음" 의도 4-option 강제 (sprint-34 / v0.9.39)

## 한 줄 요약

**사용자 의도에 *옵셔널 마커* (additional / 해도 좋음 / 추가로 / 가능하면 / 선택적 / could be nice / optional 등) 가 검출되면, clarifier agent 는 4 option AskUserQuestion 을 *반드시* 발사해 (1) 포함-필수 (2) 포함-가능시만 (3) 다음 페이즈 deferral (4) 명시 drop 으로 disambiguation 한다.** "해도 좋음" 이 자율 해석으로 "안 해도 좋음" 으로 역해석 (silent drop) 되는 회귀 차단. 결과는 `intent/04-optional-decisions.md` (G2+ 의무 산출물 신규) 에 박힘 — 사후 회수 시 사용자 명시 답변으로 추적 가능.

## 1. 결손 진단

기존 자산:
- [`interview.md`](interview.md) — 두괄식 / 1회 1질의 / Confirmation Recursion (drift/match/contradict)
- [`intent-completeness.md`](intent-completeness.md) — 9 sub criterion (limitations / data-derived 등)
- [`deep-semantic-intent.md`](deep-semantic-intent.md) — 의도 의미 깊이
- [`decision-support-framing.md`](decision-support-framing.md) — handoff 결정 framing

**갭** — 옵셔널 의도 의 *역해석 위험* :

| 사용자 발화 | 표면 의미 | 자율 해석 위험 (silent drop) |
|---|---|---|
| "추가로 X 도 됐으면" | "X 포함 권장" | "X 안 해도 됨" → drop |
| "가능하면 Y 까지" | "Y 까지 가능 시 포함" | "Y 까지 안 해도 됨" → drop |
| "additional Z is nice" | "Z 추가가 좋음" | "Z 는 nice-to-have, drop OK" |
| "옵션으로 W 도" | "W 도 포함 가능" | "W 는 옵션이니 drop" |

interview.md 의 *Confirmation Recursion* 은 *모순 답변* 만 검출 — 옵셔널 의도의 silent drop 은 *답변 자체 부재* 라 검출 안 됨. 본 컨벤션은 *옵셔널 마커 감지* 시점에 *명시 답변 강제* layer.

## 2. 옵셔널 마커 카탈로그

clarifier agent 가 사용자 의도 (페이즈 01 mindmap / 페이즈 04 답변) 에서 다음 정규식 매치 시 본 컨벤션 발동 :

```python
OPTIONAL_MARKERS_KO = [
    r"추가로", r"가능하면", r"선택적", r"옵션", r"해도\s*좋", r"있으면\s*좋",
    r"하면\s*더\s*좋", r"필요\s*시", r"여유\s*되면",
]
OPTIONAL_MARKERS_EN = [
    r"\badditional\b", r"\boptional\b", r"\bif\s+possible\b", r"\bcould\s+be\s+nice\b",
    r"\bnice[\s-]to[\s-]have\b", r"\bif\s+feasible\b", r"\bif\s+time\s+permits\b",
    r"\bbonus\b",
]
```

매치 정확도 : 단어 경계 + space-tolerant. *명시 부정* (예: "추가는 안 해도 됨", "not optional") 은 별도 패턴으로 차감.

## 3. 4-option 강제 형식 ([`interview.md`](interview.md) 정합)

옵셔널 마커 매치 시 clarifier 가 발사하는 객관식 :

```markdown
질의 (Q-OPT-NN): "<원 발화 인용>" — 이 항목을 어떻게 처리할까요?

선택지:
1. 포함 — material (반드시 포함, scope 핵심)
2. 포함 — cheap-only (구현 비용이 낮을 때만 포함, scope creep 시 drop)
3. 다음 페이즈로 defer (현 sprint 미포함, sprint NN+1 검토)
4. drop (명시적으로 scope 외, 본 프로젝트 미포함)
```

**보기 4 개 = `interview.md` §3 의 한도 정합**. 답이 모호하면 §"세분화 절차" 따라 차원 분해.

## 4. 산출물 — `intent/04-optional-decisions.md` (G2+ 신규 의무)

```markdown
---
skill_name: theseus-harness
skill_version: 0.9.39
phase: '04'
artifact_type: optional-decisions
project_id: <proj>
fingerprint: sha256:<hex>
prev_fingerprint: <04-answers.md fingerprint>
created_at: <ISO>
producer_agent: clarifier
---

# Optional Decisions — sprint-34 / v0.9.39

본 페이즈 04 인터뷰에서 *옵셔널 마커* 가 검출된 항목들의 사용자 명시 답변. 자율 해석 0.

## 항목별 결정

### Q-OPT-01 — "추가로 모니터링 대시보드"

- 원 발화: "기본 logging 외에 추가로 모니터링 대시보드도 됐으면"
- 검출 마커: `추가로`, `됐으면` (Q-OPT-NN 발사)
- 사용자 답: **2. 포함 — cheap-only** (1번 클릭 timestamp: 2026-05-09T13:14:22Z)
- 처리 방침:
  - phase 06 plan-tree 의 universe-N 중 *cheap-implementation universe* 에서 evaluate
  - 구현 LOC ≤ 200 시 포함, 그 이상 시 drop + sprint NN+1 시 재검토 후보

### Q-OPT-02 — ...
```

각 항목 frontmatter `confirmed_at` timestamp + 답안 라벨 1~4 의무.

## 5. 트리거 신호 + abort vs warn

| 신호 | 처리 |
|---|---|
| 옵셔널 마커 매치 + Q-OPT-NN 미발사 | **ABORT** — phase 04 재진입, clarifier 가 누락 항목 모두 발사 |
| Q-OPT-NN 답이 1~4 외 | **ABORT** — 사용자에게 1~4 중 명시 클릭 요청 |
| optional-decisions.md 부재 (phase 04 종료 시) | **ABORT** — 마커 검출 ≥ 1 인데 산출 부재 시 |
| 마커 검출 0 + optional-decisions.md 부재 | OK — 본 컨벤션 적용 대상 아님 |
| 답이 *2. cheap-only* 이고 phase 06 plan-tree 가 *cheap universe* 미생성 | WARN — phase 06 재진입, contested-axis 로 cheap vs full universe 분기 |
| 답이 *3. defer* 이고 sprint NN+1 까지 미인용 | WARN — regression §2 sprint loop 가 검출, lesson 누적 |

ABORT 처리 통일 — `intent/00-violation.md` 기록 + 자율 재진입.

## 6. self_lint C-IOD 룰

```python
def lint_intent_optional_disambiguation(skill_root: Path) -> list[str]:
    issues = []
    conv = (skill_root / "conventions" / "intent-optional-disambiguation.md").read_text(encoding="utf-8")
    for kw in ["옵셔널 마커", "Q-OPT", "optional-decisions.md", "cheap-only",
               "추가로", "additional", "역해석", "silent drop"]:
        if kw not in conv:
            issues.append(f"intent-optional-disambiguation.md: '{kw}' 키워드 누락")

    # interview.md cross-link 의무
    if "interview.md" not in conv:
        issues.append("intent-optional-disambiguation.md: interview.md cross-link 누락")

    # phase 04 산출물 4-option 형식 명시
    if "1. 포함" not in conv or "4. drop" not in conv:
        issues.append("intent-optional-disambiguation.md: 4-option 라벨 본문 누락")
    return issues
```

CHECKS 등록 — `("C-IOD", "intent-optional-disambiguation 4-option (sprint-34 / v0.9.39)", check_intent_optional_disambiguation)`.

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 옵셔널 마커 = 자연어 일반 패턴 (한국어/영어), 도메인 X.
b- 4-option (material / cheap / defer / drop) = scope decision 일반 차원, 도메인 X.
c- silent drop 차단 = 정직성 룰 ([`intent-completeness.md`](intent-completeness.md) §i data-derived/introduced 분리와 동계열), 도메인 X.

## 8. 안티 패턴

a- **clarifier 가 마커 무시** — "추가로 X 도" 받고 X 를 자율적으로 drop 또는 include. 사용자 명시 답안 없이 진행 → silent drop 회귀. self_lint C-IOD fail (optional-decisions.md 부재).
b- **답안 *1. material* 이지만 phase 06 plan 에서 누락** — 사용자 명시 *반드시 포함* 인데 plan/06-plan.md 에서 빠짐. self_lint 가 optional-decisions.md vs plan 본문 cross-check (후속 sprint 작업).
c- ***4. drop* 이지만 phase 14 handoff 에서 *향후 작업* 으로 재등장** — 사용자가 *명시 drop* 한 항목을 *암묵적 backlog* 로 부활. drop 답은 *영구 scope-out* 의미.
d- **boundary 모호 — "기본은 X, 추가로 Y"** — `추가로` 만 보고 Y 만 Q-OPT 발사. *X 와 Y 의 boundary* 가 명시되지 않으면 별 Q 로 분리 (X 가 base scope 인지, Y 와 함께 optional 인지).
e- **옵셔널 마커 *검출* 시점 누락** — phase 01 mindmap 작성 시 검출 안 하고 phase 04 답변 시 검출. 두 phase 모두 의무 — phase 01 mindmap 의 *예외/엣지 가지* 도 옵셔널 마커 매치 검사.

## 9. 그레이드 활성

- **G1 — 활성** (마커 검출 시 Q-OPT-NN 발사 + optional-decisions.md 의무).
- **G2+ — 풀 활성** (phase 01 mindmap + phase 04 답변 양쪽 검사).
- **G5** — 빡빡 모드 (cheap-only 답이라도 phase 06 plan-tree 의 contested-axis 로 cheap vs full universe 분기 강제).

## 10. 호환성

- [`interview.md`](interview.md) — 본 컨벤션의 4-option 형식이 interview §3 의 보기 4 개 한도 정합. Q-OPT-NN 도 §2-2 Confirmation Recursion 의 paired_with 메타에 등록.
- [`intent-completeness.md`](intent-completeness.md) — §g limitations + §i data-derived/introduced 와 직교 (옵셔널 vs 한계 vs 가정 별 차원).
- [`deep-semantic-intent.md`](deep-semantic-intent.md) — 옵셔널 마커 검출이 *의미 깊이* 의 한 차원.
- [`contested-decision-multiverse.md`](contested-decision-multiverse.md) — *2. cheap-only* 답이 phase 06 의 *cheap vs full universe* contested axis 자동 발동.
- [`autonomy.md`](autonomy.md) — 본 컨벤션은 페이즈 04 *유일한 인터럽트* 정합 (clarifier 가 답 받음 후 자율).
- [`intent-refresh.md`](intent-refresh.md) — 1차 refresh 산출 (`01-additional.md`) 가 본 컨벤션의 *2./3. defer* 답안 추적 (intent 본문 분리).
