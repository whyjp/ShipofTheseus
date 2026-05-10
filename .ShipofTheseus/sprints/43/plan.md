# Sprint-43 — Orchestrator Runtime Invoke (트랙 7)

> 시작: 2026-05-10 (sprint-42 v0.9.47 마감 + g4-v2 91/100 샌드박스 검증 후)
> 직전: sprint-42 정성 layer (CLI 4 종)
> 외부 검증: g4-v2 회차 = **91/100 (87→91 +4pt)** + **submission 폴더 빈 상태 (10 .pyc 만)** + 9 CLI runtime 미호출
> 우선순위: **orchestrator runtime invoke 본격화** — *declared ≠ invoked* 갭 폐쇄

본 sprint = sprint-41 (정량) + sprint-42 (정성) 의 9 CLI 가 *declared 되어 있어도 invoked 되지 않는* 결손 정정. orchestrator phase 본문에 *literal Bash command line* 박기 + cold session 호출 trace 검증 + post-eval 산출물 잔존 검증.

---

## 0. 배경 — *declared ≠ invoked* 갭의 textbook evidence

### 0-1. g4-v2 91/100 샌드박스 검증 결과

[`docs/reviews/2026-05-10-bench-001-mine-throughput-91-g4-v2-sandbox-verification.md`](../../../docs/reviews/2026-05-10-bench-001-mine-throughput-91-g4-v2-sandbox-verification.md):

| 차원 | 결과 |
|---|---|
| 공식 점수 91/100 정합 | ✅ dashboard md + evaluation_report.json |
| 57/57 자동 + 6/6 behavioural | ✅ 평가 시점 |
| Submission 폴더 산출물 | ❌ **10 .pyc 만 — README/submission.yaml/conceptual_model/run_experiment/outputs/.ShipofTheseus 모두 부재** |
| sprint-41/42 9 CLI runtime 호출 | ❌ 0 — 13 산출물 모두 미생성 |
| `cold_session_artefacts.py` 직접 호출 결과 | ✅ 13/13 missing → exit 1 (CLI 가 정확히 catch) |

**진단**: 9 CLI 가 컨벤션 본문 + HARD-RULE 9.qq~9.xx 에 declared. 그러나 *cold session agent 가 자율 skip*. 본 회차 = sprint-41/42 v0.9.47 push *후* 임에도 enforcement layer *0 활성*.

### 0-2. 사용자 직접 지적 (이전 sprint 들 누적)

> *"이쯤이면 충분해" 자율 종료 / 다카포 universe 감소 / 0.9999 노력 / 컨텍스트 전달 / ouroboros MCP 처럼 CLI 기반 룰베이스 허들*

→ sprint-41/42 가 코드를 박았지만 runtime 호출 안 됨. **컨벤션 본문 + CLI 코드 만으로는 불충분 — orchestrator 가 *literal Bash 명령* 으로 phase 본문에 박혀야** agent 가 *명시 실행*.

### 0-3. 3 결손 axis

| 결손 | sprint-41/42 catch? | sprint-43 신규 |
|---|---|---|
| orchestrator phase 본문에 CLI 호출 step 명시 부재 | ❌ HARD-RULE 9.X 가 *prose 권고* 만 | **PR-E** literal Bash command 박기 |
| cold session 산출물 *호출 trace* 부재 | ❌ self_lint 가 trace 검증 0 | **PR-C** phase_invoke_audit.py |
| 평가 후 산출물 *대량 삭제* 차단 | ❌ post-eval 잔존 검증 0 | **PR-B** submission_completeness.py |
| dashboard ↔ submission disk 일치 | ❌ parity 검증 0 | **PR-D** dashboard_submission_parity.py |

---

## 1. 의도 — 한 줄

orchestrator phase 본문에 *literal Bash command line* 박기 + 3 신규 CLI (post-eval 잔존 / invoke trace / dashboard parity) → *declared ≠ invoked* 갭 폐쇄.

---

## 2. PR 분할안

| PR | scope | 산출 | self_lint |
|---|---|---|---|
| PR-A ★ 본 PR | sprint-43 plan + g4-v2 샌드박스 검증 docs (이미 main 머지됨) | 1 plan | 0 |
| PR-B | **submission_completeness.py** — 평가 *직후* 산출물 disk 잔존 (.pyc-only 차단) + HARD-RULE 9.yy | scoring + test | C-SCM (후속) |
| PR-C | **phase_invoke_audit.py** — orchestrator phase 본문 literal command 검증 + cold session 호출 trace + HARD-RULE 9.zz | scoring + test | C-PIA (후속) |
| PR-D | **dashboard_submission_parity.py** — dashboard md `files:` ↔ submission disk 일치 + HARD-RULE 9.aaa | scoring + test | C-DSP (후속) |
| PR-E | **orchestrator phase walkthrough literal command 본문 박기** — phases/04 ~ phases/14 본문에 9 CLI literal Bash invocation 박힘 | phases/* 본문 + orchestrator SKILL.md walkthrough | C-OWL (후속) |
| PR-F | sprint 마감 v0.9.48 + CHANGELOG | SKILL.md / orchestrator / plugin.json / CHANGELOG | 0 |

self_lint +4 신규 (144 → 148).

---

## 3. 각 PR 상세 명세

### 3.1 PR-B — submission_completeness.py (HARD-RULE 9.yy)

#### 동기

g4-v2 91 회차 = `submissions/.../theseus-orchestrator-g4-v2/` 안에 *10 .pyc 파일만*. 평가 시점에는 산출물 존재 (output_exists_* 모두 pass), 그러나 *현재 0*. 평가 *후* 대량 삭제 / scratch cleanup 패턴 — 재현성 0 + governance trail 0.

#### CLI 명세

```bash
python submission_completeness.py \
    --submission-dir submissions/<id>/ \
    --eval-report results/evaluation_report.json \
    --output results/gate_submission_completeness.json
```

검사 알고리즘:
- evaluation_report.json 의 `automated_checks.checks` 안 `output_exists_*` true 인 모든 파일이 *현재 disk* 에 잔존 검증
- `.pyc` 만 잔존 (cache only) 패턴 detect — `.py` / `.md` / `.json` / `.yaml` 부재 시 fail
- `.ShipofTheseus/` governance trail 부재 시 G3+ 회차 fail
- post-eval 잔존 ratio < 0.5 시 fail (절반 이상 사라지면 불완전)

#### HARD-RULE 9.yy

> phase 14 handoff *직후* + dashboard sync *전* 의무 호출. exit 1 시 산출물 재emit 또는 *재실행* 강제. `.pyc-only` 패턴 차단.

### 3.2 PR-C — phase_invoke_audit.py (HARD-RULE 9.zz)

#### 동기

본 sprint 의 *핵심* CLI. orchestrator 가 phase 본문에 *literal Bash command* 를 박아도, agent 가 *실제로 호출* 했는지 산출물 trace 로 검증 필요.

#### CLI 명세

```bash
python phase_invoke_audit.py \
    --orchestrator-skill skills/theseus-orchestrator/SKILL.md \
    --project-root .ShipofTheseus/<proj>/ \
    --output quality/gate_phase_invoke_audit.json
```

검사 알고리즘:
- orchestrator SKILL.md 본문에서 `python skills/theseus-harness/scoring/<NAME>.py` literal command 추출 (9 CLI 모두)
- 각 CLI 별 *호출 trace* (e.g., `quality/gate_<NAME>.json` 파일 존재 + `evaluated_at` timestamp 가 phase 진입 시각 ≥ 인지) 검증
- 호출 trace 0 → "declared but not invoked" violation

#### 산출물 — `quality/gate_phase_invoke_audit.json`

```json
{
  "schema_version": "0.9.48",
  "orchestrator_declared_clis": [
    "dacapo_threshold", "cold_session_artefacts", "sprint_loop_cap",
    "runtime_guard_chain", "generate_sprint40_artefacts",
    "cross_phase_context_audit", "universe_count_monotonicity",
    "stagnation_breakthrough", "surrender_phrase_grep"
  ],
  "invocation_traces": {
    "cold_session_artefacts": {"trace_path": "quality/gate_cold_session_artefacts.json", "found": true, "evaluated_at": "..."},
    "dacapo_threshold": {"trace_path": "plan/dacapo_threshold.json", "found": false, "violation": "declared but not invoked"},
    ...
  },
  "violations": ["dacapo_threshold", "stagnation_breakthrough", ...],
  "verdict": "pass" if violations 0 else "fail"
}
```

#### HARD-RULE 9.zz

> phase 09 진입 + phase 14 진입 시 orchestrator 가 본 CLI 자동 호출 의무. exit 1 시 미호출 CLI 들 *전체 재호출* + phase 재진입.

### 3.3 PR-D — dashboard_submission_parity.py (HARD-RULE 9.aaa)

#### 동기

g4-v2 회차 — dashboard md `files:` 가 9 source path 명시, 그러나 submission disk 에 0 → *parity 깨짐*. dashboard 가 *과거 상태* 보존, disk 가 *현재 상태*. 두 상태 불일치는 *데이터 무결성* 실패.

#### CLI 명세

```bash
python dashboard_submission_parity.py \
    --submission-dir submissions/<id>/ \
    --dashboard-md dashboard/src/content/submissions/<id>.md \
    --output results/gate_dashboard_parity.json
```

검사 알고리즘:
- dashboard md `files:` 항목 추출 (path + bytes + kind)
- submission/<id>/ 의 실제 disk 파일 list
- 차집합 — dashboard 만 있고 disk 0 → "missing on disk"
- 차집합 — disk 만 있고 dashboard 0 → "untracked on dashboard"

#### HARD-RULE 9.aaa

> dashboard sync *직후* 의무 호출. parity 깨짐 시 *dashboard 재생성* 또는 *disk 복구* 강제.

### 3.4 PR-E — orchestrator phase walkthrough literal command 박기

#### 동기

본 sprint 의 *행동* 차원 변경. HARD-RULE 9.X *prose 권고* → *literal Bash command* 본문 박기.

#### 변경 — phases/* 본문 + orchestrator SKILL.md

각 phase 본문 끝 *§자동 CLI 호출* 절 신규:

```markdown
## §자동 CLI 호출 (sprint-43 PR-E)

본 phase 종료 직전 orchestrator 의무 호출 :

\```bash
# 9.qq — 다카포 임계
python skills/theseus-harness/scoring/dacapo_threshold.py \
    --tournament-md .ShipofTheseus/<proj>/plan/tournament-01.md \
    --output .ShipofTheseus/<proj>/plan/dacapo_threshold.json

# exit 1 시 round N+1 자동 진행
\```
```

orchestrator SKILL.md walkthrough 도 phase 별 *literal command* 박힘 — agent 가 *prose 가 아니라 명령* 으로 받아들임.

#### self_lint C-OWL (orchestrator walkthrough literal command)

phases/04~14 본문에 *최소 1 literal Bash command* (`python skills/.../<NAME>.py` 패턴) 박힘 검증. 부재 phase 발견 시 fail.

### 3.5 PR-F — 마감 v0.9.48

skills/theseus-harness/SKILL.md `version: 0.9.48`, plugin.json, CHANGELOG entry. self_lint 144 → 148.

---

## 4. 구조 가치

| sprint | layer | enforcement |
|---|---|---|
| sprint-40 | 문서 layer | 컨벤션 본문 강화 |
| sprint-41 | 정량 layer | CLI 5 종 |
| sprint-42 | 정성 layer | CLI 4 종 |
| **sprint-43** | **runtime invoke layer** | **CLI 3 종 + orchestrator literal command** |

4 layer 결합 = ouroboros + 정량 + 정성 + *literal invoke* = *진정한* runtime guard.

---

## 5. 검증 — 외부 적용 평가

PR-F 머지 후 v0.9.48 :
1. simulation-bench fresh G4 cold session
2. 평가 *대상* — orchestrator phase 본문에 박힌 *literal Bash command* 가 cold session 에서 *실제 실행* 되어 *invoke trace* 산출되는가?
3. 활성 → *declared = invoked* 정착 입증
4. 부분 미활성 → 어느 phase 의 walkthrough 가 fail 인지 진단, sprint-44 fix
5. 외부 점수 변화는 *결과* / *부산물*

---

## 6. 위험 + 대응

| 위험 | 대응 |
|---|---|
| literal Bash command 가 cold session 환경에서 path 다름 (project_root 변수) | 모든 command 가 `<project_root>` placeholder 사용, orchestrator 가 substitute |
| phase_invoke_audit 가 *trace 없는 phase* 모두 fail → false positive | *trace 의무 phase* 명시 (phase 06 = dacapo_threshold trace, phase 09 = cold_session_artefacts trace, phase 10 = sprint_loop_cap trace 등) |
| dashboard parity 가 *legitimate cleanup* 차단 | scratch cleanup 명시 cases (e.g., `__pycache__/`) override |
| orchestrator walkthrough 본문 비대화 | literal command 는 *말미 §자동 CLI 호출* 절로 분리, 본문 narrative 보존 |

---

## 7. 비고

본 sprint = sprint-41/42 의 *코드 layer* 위에 *invocation layer* 추가. 메모리 [`feedback_hurdle_as_cli_paradigm.md`] *컨벤션 본문 = 명세, CLI = 집행* 패러다임의 *3 단계 강화* — *명세 → 코드 → invocation 강제*. agent 가 컨벤션 *읽고 따름* 만으로 부족 → orchestrator 가 *명령 박음* + audit CLI 가 *실 호출 검증*.
