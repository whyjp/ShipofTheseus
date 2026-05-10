---
id: surrender-phrase-forbid
category: quality
applies-to-phases: '[10,14]'
applies-to-grades: '[all]'
trigger-when: 'cold session 산출물 종료 시점'
indexed-in: conventions/INDEX.md
---

# Surrender Phrase Forbid — agent 자율 종료 자백 어휘 차단 (sprint-42 PR-E 신규)

## 한 줄 요약

**Cold session 산출물 본문에 *agent 가 책임 회피 / 자율 종료 / 외부 위임* 류 어휘 등장 시 phase 차단.** 8 패턴 카탈로그 + override 메커니즘. 본 컨벤션 = ouroboros 보다 *더 깊은* enforcement — 점수 / 산출물 / 단조성 외에 *agent 의 자백 어휘* 자체를 runtime guard.

증거 회피 사례 (0510-2 회차 `sprints/03/report.json:lessons_outbound[1]`):
> "0.97 < 0.999 G4 asymptote; **defer to opus-reviewer scoring as final ground truth**"

위 한 문장 안에 4 surrender 패턴 (*defer to external*, *asymptote*, *final ground truth*, *would only*). 본 컨벤션 + sprint-42 PR-E `surrender_phrase_grep.py` 가 직접 차단.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| agent 가 *명시적* "0.999 미달" 인지 + "외부 reviewer 에 위임" 자율 결정 | 본 하네스 책임 회피 — 단순 *defer to opus-reviewer* 한 줄로 sprint loop 종료 |
| *plateaued* / *asymptote* / *good enough* 류 어휘 = stagnation 정당화 | 노력 의무 회피의 *언어* layer — sprint-41 정량 layer 가 catch 불가 |
| 자율 종료 자백 어휘 grep 메커니즘 부재 | sprint-40/41 모든 게이트가 *수치* 검사 — *언어* 검사 0 |

## 8 패턴 카탈로그

| # | kind | regex | 차단 사유 |
|---|---|---|---|
| 1 | `defer_to_external` | `\bdefer(?:s\|red\|ring)?\s+to\s+(?!self\|the\s+(?:plan\|impl\|test\|code))(?:opus[-_]reviewer\|human\|external\|reviewer\|grader\|judge\|user)\b` | 외부 위임 — 본 하네스 책임 회피 |
| 2 | `plateaued` | `\bplateau(?:ed\|ing)\b` (verb form only, *plateau* 명사 neutral 허용) | 정체 인정 — stagnation 후 노력 종료 신호 |
| 3 | `asymptote` | `\basymptot(?:e\|ic\|ically)\b` | 점근선 인정 — 임계 미달 + 종료 정당화 |
| 4 | `good_enough` | `\bgood\s+enough\b` | "이쯤이면 충분해" 직접 어휘 |
| 5 | `sufficient` | `\b(?:considered\|deemed\|judged\|is)\s+sufficient\b` | 충분함 인정 (context 의존, override 가능) |
| 6 | `fine_tune_narrative` | `\bfine[-_\s]?tune\s+(?:the\s+)?(?:narrative\|wording\|prose\|text)\b` | 서술만 다듬음 — 실 개선 회피 |
| 7 | `would_only` | `\bwould\s+only\s+(?:fine[-_\s]?tune\|polish\|tweak\|adjust)\b` | 더 시도 무의미 — exit 정당화 |
| 8 | `final_ground_truth_external` | `\b(?:final\|definitive)\s+ground\s+truth\b` | 외부에 진실 위임 — 본 하네스 결정 회피 |

## 트리거

- **phase 10 sprint loop 종료** — `surrender_phrase_grep.py --project-root <root>` 호출 의무
- **phase 14 handoff 진입** — handoff 본문에 자백 어휘 등장 차단

## 알고리즘

```python
import re

PATTERNS = [...]  # 8 패턴

def scan(project_root):
    files = list(project_root.rglob('*.md')) + list(project_root.rglob('*.json'))
    violations = []
    for path in files:
        text = path.read_text()
        # frontmatter override 검사
        has_override = bool(re.search(r'^surrender_override:\s*true', text, re.M))
        for kind, pat, why in PATTERNS:
            for m in pat.finditer(text):
                if not has_override:
                    violations.append({'file': path, 'kind': kind, 'match': m.group(0)})
    return violations
```

## Override 메커니즘

산출물 frontmatter 에 다음 두 필드 명시 시 *해당 파일* 의 surrender 매치 허용:

```yaml
surrender_override: true
surrender_override_reason: "사용자 직접 ack — 외부 reviewer 통합 단계 (path-policy 정합)"
```

Override 는:
- **파일 단위** — 다른 파일 매치는 차단
- **사용자 ack 의무** — 메모리 [`feedback_deliverable_path_user_confirm.md`] 정합 (06.f path-policy)
- **남용 차단** — frontmatter 의 `surrender_override: true` 가 *전체 산출물 의 5%* 초과 시 self_lint fail

## 산출물 — `quality/gate_surrender_phrase.json`

```json
{
  "schema_version": "0.9.47",
  "files_scanned": 47,
  "files_with_match": 1,
  "total_violations": 4,
  "overridden_count": 0,
  "patterns_checked": ["defer_to_external", "plateaued", "asymptote", "good_enough", "sufficient", "fine_tune_narrative", "would_only", "final_ground_truth_external"],
  "per_file": [
    {
      "path": "sprints/03/report.json",
      "matches": [
        {"kind": "plateaued", "match": "plateaued", "why": "정체 인정", "overridden": false},
        {"kind": "asymptote", "match": "asymptote", "why": "점근선 인정", "overridden": false},
        {"kind": "defer_to_external", "match": "defer to opus-reviewer", "why": "외부 위임", "overridden": false},
        {"kind": "final_ground_truth_external", "match": "final ground truth", "why": "외부에 진실 위임", "overridden": false}
      ]
    }
  ],
  "verdict": "fail"
}
```

## self_lint C-SPF (sprint-42 PR-E 신규)

phase 10 / 14 진입 시 :
- `quality/gate_surrender_phrase.json` 존재 + `verdict == "pass"` 확인
- override 사용량 ≤ 5% (남용 차단)
- 미달 시 phase 진입 거부

## 안티 패턴

a- **patterns 회피 어휘 변형** (예: "deferred to ..." 대신 "yielded to ...") — 신규 어휘 발견 시 본 카탈로그 *추가* 의무. 카탈로그 외 어휘는 sprint NN 신규 추가.
b- **frontmatter 외 위치에 override 박기** — frontmatter 외 위치는 검출 안 됨. 의도된 design — frontmatter 가 single source of truth.
c- **override reason 빈 문자열** — `surrender_override_reason` 본문 ≥ 5 단어 의무 (단순 "ack" 류 차단 — 후속 self_lint 검증).
d- **Override 남용** — *전체 산출물 의 5%* 초과 시 fail.

## 메모리 정합

- [`feedback_hurdle_as_cli_paradigm.md`](../../../memory/feedback_hurdle_as_cli_paradigm.md) — 컨벤션 본문 = 명세, CLI = 집행. 본 컨벤션 + surrender_phrase_grep.py 1:1 페어.
- [`project_bench_001_v0945_87_deeper.md`](../../../memory/project_bench_001_v0945_87_deeper.md) — 0510-2 회차 lessons_outbound 직접 인용 사례.
- [`feedback_pseudocode_to_enforcement.md`](../../../memory/feedback_pseudocode_to_enforcement.md) — *언어 layer* enforcement 의 본격화.
