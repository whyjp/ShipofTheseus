---
id: regression-tdd-gate
category: quality
applies-to-phases: '[08,10,11]'
applies-to-grades: '[all]'
trigger-when: 'every code change / dacapo step F / sprint iteration'
indexed-in: conventions/INDEX.md
---

# Regression TDD Gate — commit-level 재실행 hurdle (sprint-34 / v0.9.39)

## 한 줄 요약

**phase 08 의 매 sub-impl 산출 + dacapo loop step F + sprint loop iteration 시점에 `scoring/regression_check.py run` 의무 호출. test + boot + lint 를 *재실행* 해 회귀를 commit-level 에서 차단.** 페이즈 08 의 5 sub-phase TDD ([`phases/08-implement.md`](../phases/08-implement.md)) 가 *페이즈 단위* 이라면, 본 컨벤션은 *commit 단위* — 두 layer 가 상보적.

## 1. 결손 진단

기존 자산:
- `phases/08-implement.md` — 5 sub-phase TDD (test-architect / test-writer / implementer / runtime-detector / refactorer)
- [`scoring/boot_check.py`](../scoring/boot_check.py) — runtime/healthz 검증 (게이트 7)
- [`scoring/check_cold_session.py`](../scoring/check_cold_session.py) (HARD-RULE 9.f) — phase 09 진입 직전 cold session 검사
- [`dacapo-mandatory-rerun.md`](dacapo-mandatory-rerun.md) (HARD-RULE 9.gg) — phase 06/08 다카포 ≥ 1 회 의무

**갭** — 페이즈 08 *사이* 의 매 sub-impl 산출 + dacapo step F 시점 + sprint iteration 시점에 *test 재실행* 강제 layer 부재. v0.9.22 이후 cold session 들에서 :
- impl universe 중간에 테스트 깨진 채로 다음 sub-impl 진행
- sprint NN 의 baseline measure 가 *직전 sprint 의 known-good 상태* 와 비교 안 됨
- regression-bisect (phase 11) 가 *어디서* 깨졌는지 찾을 수 있는 *append-only 로그* 부재

→ commit/sub-impl 시점마다 test + boot + lint 재실행 + `state/regression_log.json` append-only 누적 + 직전 known-good 대비 회귀 검출 layer 가 필요.

## 2. state/regression_log.json 스키마

```json
{
  "schema_version": 1,
  "entries": [
    {
      "timestamp": "2026-05-09T13:30:00Z",
      "phase": "08",
      "module": "T-001",
      "trigger": "impl",
      "test": {"cmd": "pytest -x", "exit": 0, "stdout_tail": "...", "stderr_tail": ""},
      "boot": {"cmd": "npm start", "exit": 0, "stdout_tail": "...", "stderr_tail": ""},
      "lint": {"cmd": "ruff check .", "exit": 0, "stdout_tail": "", "stderr_tail": ""},
      "outcome": "ok",
      "reason": "all pass"
    }
  ]
}
```

`trigger` ∈ {`impl`, `dacapo-step-f`, `sprint-iter`, `phase-exit`}.

append-only — 항목 삭제/수정 금지. 회귀 발생 시 *새 항목* 으로 fail 누적.

## 3. orchestrator 호출 인터페이스

```bash
# phase 08 의 매 sub-impl 산출 후
python skills/theseus-harness/scoring/regression_check.py run \
    --root .ShipofTheseus/<proj>/ --module T-001 --phase 08 --trigger impl \
    --test-cmd "pytest -x" \
    --boot-cmd "npm start" --boot-timeout 60 \
    --lint-cmd "ruff check ."
# exit 0 = PASS, 1 = FAIL — fail 시 phase 08 step C 재진입

# dacapo step F (sprint-15 / dacapo loop)
python ... regression_check.py run --trigger dacapo-step-f --module rerun-NN ...

# 회귀 검출 (compare 모드)
python ... regression_check.py compare --root .ShipofTheseus/<proj>/
# exit 0 = no regression, 1 = regression detected
```

## 4. 트리거 신호 + abort vs warn

| 신호 | 시점 | 처리 |
|---|---|---|
| test exit ≠ 0 | run | **ABORT** — phase 08 step C (implementer) 재진입, lesson_pack 누적 |
| boot exit ≠ 0 | run | **ABORT** — runtime-prereq 재검증, 환경 결손 시 phase 04 회귀 |
| lint exit ≠ 0 | run | WARN — code 만 reject, lesson 으로 누적 (dacapo step F 보강) |
| compare regression detected | dacapo step F / sprint iter | **ABORT** — phase 11 bisect 트리거 (G4+), 또는 phase 08 sub-impl 재진입 (G3) |
| regression_log.json 부재 | phase 09 진입 직전 | **ABORT** — 본 컨벤션 미이행, phase 08 재진입 |
| `entries` 0 | phase 09 진입 직전 | **ABORT** — sub-impl 한 번도 검증 안 됨 |

ABORT 처리 통일 — exit 1 + `intent/00-violation.md` 기록 + 자율 재진입 (페이즈 04 외 인터럽트 0 정합).

## 5. 회귀 검출 알고리즘

```python
def detect_regression(log):
    entries = log["entries"]
    if len(entries) < 2:
        return {"regressed": False, "reason": "history < 2"}
    latest = entries[-1]
    if latest["outcome"] == "ok":
        return {"regressed": False, "reason": "latest ok"}
    prev_ok = next((e for e in reversed(entries[:-1]) if e["outcome"] == "ok"), None)
    if prev_ok is None:
        return {"regressed": False, "reason": "no prior known-good"}
    return {
        "regressed": True,
        "reason": f"직전 ok ({prev_ok['timestamp']}) → 최신 fail ({latest['reason']})",
        "prev_ok": prev_ok,
        "latest": latest,
    }
```

회귀 = (직전 known-good 존재) AND (최신 fail). 첫 fail 은 baseline 으로 간주 (회귀 X).

phase 11 (regression-bisect) 가 본 함수의 `prev_ok` 와 `latest` 사이 entries 를 binary search 해 *깨진 commit/module* 식별.

## 6. self_lint C-RTG 룰

```python
def lint_regression_tdd_gate(skill_root: Path) -> list[str]:
    issues = []
    conv = (skill_root / "conventions" / "regression-tdd-gate.md").read_text(encoding="utf-8")
    py = (skill_root / "scoring" / "regression_check.py").read_text(encoding="utf-8")

    for kw in ["regression_log.json", "append-only", "commit-level", "회귀 검출",
               "dacapo step F", "sprint iteration"]:
        if kw not in conv:
            issues.append(f"regression-tdd-gate.md: '{kw}' 키워드 누락")

    for fn in ["evaluate_entry", "detect_regression", "cmd_run", "cmd_last", "cmd_compare"]:
        if f"def {fn}" not in py:
            issues.append(f"regression_check.py: 함수 {fn} 부재")

    return issues
```

CHECKS 등록 — `("C-RTG", "regression-tdd-gate.py + 컨벤션 (sprint-34 / v0.9.39)", check_regression_tdd_gate)`.

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- test/boot/lint 3 단계 = 일반 CI gate 골격, 도메인 X.
b- regression detection (직전 known-good 비교) = 일반 SCM/CI 패턴, 도메인 X.
c- append-only 로그 = phase 11 bisect 의 일반 입력, 도메인 X.

## 8. 안티 패턴

a- **regression_check.py 미호출** — phase 08 implementer 가 self-test 만 보고 진행. cold session 에서 빈번 회귀.
b- **regression_log.json 수동 편집** — 사람이 fail 항목 삭제 → bisect 무력화. append-only 의무 (수정/삭제 시 self_lint detect 가능).
c- **trigger 분류 오용** — 모든 항목을 `trigger=impl` 로 통일 → dacapo loop 회귀 vs sprint 회귀 구분 불가. [`phases/08-implement.md`](../phases/08-implement.md), [`phases/10-test-loop.md`](../phases/10-test-loop.md) 진입 시 정확한 trigger 박음.
d- **boot/lint 생략** — `--test-cmd` 만 사용. phase 04 Q-D8 verification commands + Q-D9 runtime-prereq 답에 명시된 boot/lint 누락. phase 04 답안 → trigger 자동 매핑 의무.
e- **timeout 무한** — `--test-timeout` 미지정으로 무한 대기. budget cap (페이즈 04 Q-D2) 위반. default 300s 강제 + 외부 명시 시 budget profile 정합.

## 9. phase 08 5 sub-phase 와의 layer 분리

| Layer | 입자 | 트리거 |
|---|---|---|
| **phase 08 5 sub-TDD** ([`phases/08-implement.md`](../phases/08-implement.md)) | universe 단위 (test-architect → test-writer → implementer → runtime-detector → refactorer) | phase 08 진입 |
| **본 컨벤션 (commit-level)** | sub-impl / dacapo step F / sprint iter | 매 코드 수정 |

phase 08 의 implementer sub-phase 가 *한 universe 의 코드 산출* 을 한 번 끝내면, 그 *직후* 본 컨벤션의 `regression_check.py run` 호출 — *코드 작성 vs 회귀 검증* 의 분리 layer.

## 10. 그레이드 활성

- **G1 — 활성** (test-cmd 만 의무, boot/lint 옵션).
- **G2 — 활성** (test + boot 의무).
- **G3+ — 풀 활성** (test + boot + lint 모두 + dacapo-step-f trigger 의무).
- **G5** — 빡빡 모드 (test 0 fail / boot pass / lint 0 warning 강제).

## 11. 호환성

- [`phases/08-implement.md`](../phases/08-implement.md) — 5 sub-phase TDD (페이즈 단위 layer).
- [`scoring/boot_check.py`](../scoring/boot_check.py) — boot 검증 helper (본 컨벤션 의 `--boot-cmd` 호출 alternative).
- [`scoring/check_cold_session.py`](../scoring/check_cold_session.py) (HARD-RULE 9.f) — phase 09 직전 post-hoc layer.
- [`scoring/phase_state.py`](../scoring/phase_state.py) (sprint-34 #1) — runtime entry-time gate.
- [`phases/11-regression-bisect.md`](../phases/11-regression-bisect.md) — regression_log entries 사이 binary search 로 *깨진 commit/module* 식별 (G4+).
- [`runtime-prereq.md`](runtime-prereq.md) — Q-D9 runtime-prereq 답 → boot-cmd 자동 매핑.
- [`autonomy.md`](autonomy.md) — ABORT 시 자율 재진입 (인터럽트 0).
