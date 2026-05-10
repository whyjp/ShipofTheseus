# 2026-05-10 — Bench 001 g4-v2 91/100 — 샌드박스 검증 결과 (보고 vs 실재 불일치)

> **회차:** `2026-05-10__001_synthetic_mine_throughput__claude-code__claude-opus-4-7__theseus-orchestrator-g4-v2`
> **공식 점수:** 91 / 100 (dashboard + evaluation_report.json 기록)
> **샌드박스 검증 일시:** 2026-05-10 (sprint-42 v0.9.47 push *후*)
> **검증 도구:** 9 CLI (sprint-41 5 + sprint-42 4)

## 0. TL;DR — 3 결론

1. **공식 점수 91/100 은 dashboard + evaluation_report.json 에 *실재 기록* 됨** — 57/57 자동 + 6/6 behavioural + Opus reviewer 7 차원 채점. 부정 X.
2. **그러나 submission 폴더는 *비어 있음* (10 `.pyc` 파일만)** — 소스 .py / outputs/ / .ShipofTheseus/ / README.md / submission.yaml / token_usage.json / conceptual_model.md 모두 *부재*. 평가 *시점에는 존재* 했으나 (`output_exists_*` 체크 모두 pass) 현재 *증거 0*.
3. **샌드박스 테스트 — sprint-41 PR-C `cold_session_artefacts.py` 가 정확히 catch**. 13/13 산출물 missing → exit 1. **CLI 가 *실제로* runtime 에서 호출되었더라면 phase 09 차단 + agent 가 13 산출물 emit 강제**.

## 1. 점수 분포 — 87 → 91 +4pt 회복

| Category | Max | Score | 0510-1 (synthetic, 90) Δ | 0510-2 (mine, 87) Δ |
|---|---:|---:|---:|---:|
| Conceptual modelling | 20 | **18** | 0 | 0 |
| Data + topology | 15 | **13** | -1 | 0 |
| Simulation correctness | 20 | **18** | 0 | 0 |
| Experimental design | 15 | **14** | +1 | +2 |
| Results + interpretation | 15 | **14** | +1 | +1 |
| Code quality | 10 | **9** | 0 | 0 |
| Traceability | 5 | **5** | 0 | +1 |
| **합계** | **100** | **91** | **+1** | **+4** |

**+4pt 회복은 Experimental + Results + Traceability** 차원. 0510-2 의 자율 종료 자백 (*defer to opus-reviewer / asymptote*) 패턴이 *본 g4-v2 회차 보고에는 부재* — surrender_phrase_grep 0 매치 (검증 §3-3 참조).

## 2. dashboard vs submission 폴더 *불일치*

### 2-1. dashboard 기록 (정합)

`dashboard/src/content/submissions/2026-05-10__...__theseus-orchestrator-g4-v2.md`:

```yaml
totalScore: 91
categoryScores:
  conceptual_modelling: 18
  data_topology: 13
  ...
runtimeSeconds: 4.81683
files:
  - path: "requirements.txt"        bytes: 89
  - path: "results/evaluation_report.json"  bytes: 14550
  - path: "run_experiment.py"       bytes: 6057
  - path: "run_metrics.json"        bytes: 3373
  - path: "src/mine_sim/{__init__,config,experiment,model,routing,summary,topology}.py"
```

`dashboard/public/submissions/.../results/evaluation_report.json`:
- automated_checks.passed = 57/57
- output_exists_conceptual_model.md = `passed: true` (평가 시점에는 존재)
- output_exists_README.md = `passed: true`
- behavioural checks (last 6) = all pass

### 2-2. submissions 폴더 실재 상태

`submissions/2026-05-10__...__theseus-orchestrator-g4-v2/`:
```
src/mine_sim/__pycache__/  (7 .pyc 파일만)
tests/__pycache__/          (3 .pyc 파일만)
```

**총 10 `.pyc` 파일. 그 외 파일 0**.

부재 항목:
- ❌ `README.md`
- ❌ `submission.yaml`
- ❌ `token_usage.json`
- ❌ `conceptual_model.md`
- ❌ `run_experiment.py` (소스)
- ❌ `run_metrics.json`
- ❌ `requirements.txt`
- ❌ `outputs/` (5 의무 출력 + state_log.csv + topology.png)
- ❌ `.ShipofTheseus/mine-throughput/` (45+ governance 산출물 — 사용자 보고 인용)
- ❌ `src/mine_sim/*.py` (소스 — `.pyc` 만 cache)
- ❌ `tests/*.py` (소스 — `.pyc` 만 cache)
- ❌ `results/evaluation_report.json` (dashboard/public/ 에는 사본 존재, submission/ 에는 부재)

### 2-3. 진단 — 평가 후 산출물 *대량 삭제*

evaluation_report.json 의 모든 `output_exists_*` 체크가 `passed: true` 였음 → **평가 시점** 에는 산출물 모두 존재. dashboard 가 file metadata 도 기록 → **dashboard 캡처 시점** 에도 존재. **그러나 *현재* 0**.

가능한 원인:
- ⓐ **scratch 폴더 cleanup** — cold session 이 산출물을 *공유 scratch* 에 작성, dashboard 동기화 후 cleanup 가 submission/ 자체를 삭제
- ⓑ **수동 삭제** — 사용자 또는 다른 process 가 산출물 정리
- ⓒ **분리된 산출물** — submission/ 의 *.pyc 만 동기화되고 본 파일들은 다른 위치 (예: `dashboard/public/`) 로만 푸시

**reproducibility 측면**: V6 cross-process byte-equal 재실행 검증 0 — 산출물 부재 시 재실행 자체 불가.

## 3. 샌드박스 검증 — 9 CLI 직접 호출

### 3-1. submission 폴더 (비어 있음) 대상

| CLI | 결과 | 의의 |
|---|---|---|
| `cold_session_artefacts.py` (9.rr) | **FAIL** — missing 13/13 sprint-40 산출물 | ✅ **정확히 catch.** runtime 호출 시 phase 09 차단 |
| `universe_count_monotonicity.py` (9.vv) | pass — plan/impl 디렉터리 부재로 검사 대상 0 | ⚠ 디렉터리 자체 부재 시 vacuous pass — sprint-43 보강 후보 |
| `surrender_phrase_grep.py` (9.xx) | pass — md/json 파일 0 | (vacuous) |
| `cross_phase_context_audit.py` (9.uu) | pass — phase 산출물 0 → skip | (vacuous) |

**CLI 1 (cold_session_artefacts) 가 단독으로 모든 결손을 detect.** 13 산출물 부재 = sprint-40 enforcement layer 0 활성 = 본 회차가 v0.9.46/47 의 CLI 자동 호출 hook *미실행*.

### 3-2. dashboard/public 사본 대상

같은 결과 — `cold_session_artefacts.py` FAIL 13/13. dashboard 사본도 evaluation_report.json 1 개만 보유.

### 3-3. 사용자 입력 보고 텍스트에 surrender_phrase_grep 직접

```
$ python surrender_phrase_grep.py --input <agent_report>
```

**결과 — 0 매치**. 본 회차 agent 가 *defer to opus-reviewer* / *plateaued* / *asymptote* 류 자백 어휘 사용 0. 0510-2 회차 (87) 와 비교 시 *언어 layer* 회피 패턴 *없음* — 이것이 +4pt 회복의 일부 설명.

## 4. agent 보고된 약점 vs sprint 게이트 매핑

| Agent 보고 약점 | sprint 게이트 | 활성 시 효과 |
|---|---|---|
| `experiment.py:_truck_specs` 가 `trucks.csv` 무시 + 합성 (payload 100, start PARK) | sprint-40 PR-F `modeling-shortcuts.md` 4-tier (heuristic / placeholder) | classification = "placeholder" → phase 08 진입 거부 (placeholder tier 0 의무) |
| `outputs/README.md` Q1 "0.66" vs `summary.json` "0.29" 불일치 | sprint-40 PR-E `gate_readme_summary_consistency.json` (drift ≤ 0.01%) | 0.29 vs 0.66 = 128% drift → phase 09 verdict halt + atomic regen |
| `submission.yaml` / `token_usage.json` 부재 → 리더보드 ? | sprint-41 PR-C `cold_session_artefacts.py` (13 file existence) | 본 회차 13/13 missing → phase 09 차단 |

**3 약점 모두 *기존 게이트로 차단 가능*** — 그러나 *runtime 호출 미실행* 으로 인해 발현. 이는 sprint-42 마감 시점에 이미 진단된 *컨벤션 본문 권고 ↛ runtime guard* 갭.

## 5. sprint-43 후보 — orchestrator runtime invoke 본격화

### 5-1. 진단

본 회차 = sprint-41/42 *컨벤션 + CLI* 가 모두 v0.9.47 에 박힌 후의 회차임에도 *9 CLI 모두 미호출*. 가능한 원인:

ⓐ skill_version 0.9.45 stale frontmatter (이전 회차 패턴) — agent 가 v0.9.47 의 9.qq~9.xx HARD-RULE 본문을 *읽지도 못함*
ⓑ HARD-RULE 9.X 가 *prose 권고* 만 — agent 가 *Bash 호출 의무* 로 받아들이지 않음
ⓒ orchestrator phase invoke step 본문이 *CLI 명시 호출* 을 *literal 명령* 으로 박지 않음 — agent 가 자율 skip

**sprint-43 본격 의제** — orchestrator SKILL.md 의 phase walkthrough 본문에 *literal Bash command line* 박힘 + self_lint 가 phase 본문에 해당 command line 등장 검증 + cold session validator 가 산출물 (`gate_*.json`) 의 *생성 시각 ≥ phase 진입 시각* 검증.

### 5-2. 신규 CLI 후보 (sprint-43)

| CLI | 역할 |
|---|---|
| `submission_completeness.py` | 평가 *직후* 산출물 모두 disk 잔존 검증 (`pyc-only` 패턴 차단) |
| `phase_invoke_audit.py` | orchestrator 본문에서 9 CLI literal command 박힘 검증 + cold session 의 phase 산출물에 *CLI 호출 trace* (예: `9.rr_invoked: true`) 검증 |
| `dashboard_submission_parity.py` | dashboard md `files:` 목록 vs submission/ 디스크 일치 검증 — 본 회차 같은 *대량 삭제* 차단 |

## 6. 결론 — 본 회차 검증 verdict

### ✅ 인정되는 것
- **91/100 점수 정합** (dashboard + evaluation_report.json 정합)
- **57/57 자동 + 6/6 behavioural** (평가 시점)
- **자율 종료 자백 어휘 0** (0510-2 87 회차 대비 개선)

### ❌ 부정되는 것 / 검증 실패
- **submission 산출물 전부 부재** — *.pyc 만 잔존
- **15 phase governance trail 0** (`.ShipofTheseus/mine-throughput/` 전체 부재)
- **sprint-40~42 13 산출물 0 emit** (사용자 직접 지적 *컨벤션 선언 ≠ 런타임* 갭의 직접 발현)
- **9 CLI hook 미호출** — sprint-41/42 enforcement layer *runtime 0 활성*
- **재현성 0** — 산출물 부재로 V6 byte-equal 재실행 불가

### 종합 판정

**91 점은 *결과 점수* 로는 인정** (dashboard 기록), **그러나 *재현성 / governance / runtime guard* 측면에서는 0510 첫 회차 (90) 보다도 *더 약한 evidence*** — 산출물 0. 점수만 더 높지만 *증명 가능성* 더 낮음.

본 sandbox 검증의 단일 핵심 통찰: **9 CLI 가 declared 되어 있어도 *invoked* 되지 않으면 enforcement = 0**. sprint-43 = orchestrator phase 본문에 *literal command line* 박기 + invocation trace 검증 의무.

---

## Appendix — 원자료 위치

- 비어있는 submission: `submissions/2026-05-10__001_synthetic_mine_throughput__...__theseus-orchestrator-g4-v2/` (10 .pyc 만)
- dashboard md (점수 + files 메타): `dashboard/src/content/submissions/...__theseus-orchestrator-g4-v2.md`
- evaluation_report.json (57/57): `dashboard/public/submissions/.../results/evaluation_report.json`
- 0510-2 87 회차 (비교 대상): `submissions/2026-05-10__...__theseus-orchestrator-g4/.ShipofTheseus/mine-throughput/` (45+ 산출물 잔존)
- 본 sandbox CLI: `D:/github/ShipofTheseus/skills/theseus-harness/scoring/{cold_session_artefacts,universe_count_monotonicity,surrender_phrase_grep,cross_phase_context_audit}.py`
- 본 하네스 메모리: [`feedback_pseudocode_to_enforcement.md`], [`feedback_convention_runtime_gap.md`], [`feedback_hurdle_as_cli_paradigm.md`]
