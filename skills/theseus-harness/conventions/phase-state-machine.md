---
id: phase-state-machine
category: core
applies-to-phases: '[all]'
applies-to-grades: '[all]'
trigger-when: 'phase enter / phase exit'
indexed-in: conventions/INDEX.md
---

# Phase State Machine — runtime 단조성 게이트 (sprint-34 / v0.9.39)

## 한 줄 요약

**orchestrator 가 매 페이즈 enter/exit 시점에 `scoring/phase_state.py` 호출 의무. `state/phase_state.json` 누적 + 단조성 (entered_at strict-monotonic) + 산출물 frontmatter `created_at` cross-check 로 v0.9.22 의 백필/위조 (페이즈 01-06 사후 frontmatter 9-12 분 위조) 를 *runtime* 시점에 차단.** cold session 산출물 정합은 `run_gate.py` 의 `cold.isolation` CheckSpec(meta_audit, 값 기반, 9.f 은퇴) 이 *post-hoc* 검사를 하고, 본 모듈은 *runtime entry-time* gate — 두 layer 가 상보적.

## 1. 결손 진단

기존 자산:
- [`checkpoint.py`](../scoring/checkpoint.py) — failure_kind → 회귀 페이즈 매핑 (사후 회귀)
- `run_gate.py` `cold.isolation` CheckSpec — phase 09 *cold session 정합* 검사 (post-hoc, 값 기반)
- [`phase-lineage-viewer.md`](phase-lineage-viewer.md) (br) — 프로젝트 종료 후 lineage.md mermaid + fingerprint chain
- [`contracts.md`](contracts.md) — frontmatter prev_fingerprint 체인

**갭** — 페이즈 *진입/종료 시점* 에 단조성을 강제하는 runtime gate 부재. v0.9.22 사고 (페이즈 01-06 백필 + frontmatter created_at 9-12 분 위조) 는 :
- artifact 자체는 self_lint 통과 (frontmatter 형식 OK)
- `cold.isolation` CheckSpec 는 *cold session 정합만* 검사
- contracts.md fingerprint chain 은 *값 일치* 만 보지 *시간 단조성* 안 봄

→ 페이즈 단위 enter/exit 시각을 *별도 state 파일* 에 기록하고, 산출물 frontmatter `created_at` 가 그 *진입~종료 윈도* 내인지 cross-check 가 필요.

## 2. state/phase_state.json 스키마

```json
{
  "schema_version": 1,
  "project_id": "synthetic_mine_throughput_001",
  "grade": "G4",
  "started_at": "2026-05-09T13:00:00Z",
  "current_phase": "06",
  "current_status": "in_progress",
  "phases": [
    {
      "phase": "00",
      "status": "completed",
      "entered_at": "2026-05-09T13:00:00Z",
      "exited_at": "2026-05-09T13:02:13Z",
      "duration_seconds": 133,
      "fingerprint": "sha256:7a9c...",
      "producer": "project-namer",
      "outcome": "ok",
      "artifact_path": "naming/00-naming.md",
      "frontmatter_created_at": "2026-05-09T13:01:55Z"
    }
  ]
}
```

`current_status` ∈ {`idle`, `in_progress`}. 동시 진행 페이즈 ≤ 1 — 새 enter 호출 시 직전이 in_progress 면 reject.

## 3. orchestrator 호출 인터페이스

매 페이즈 진입/종료 시점에 의무 호출 :

```bash
# 호출 직후 첫 동작 (HARD-RULE 1 의 timing/start.json 작성과 함께)
python skills/theseus-harness/scoring/phase_state.py init \
    --root .ShipofTheseus/<proj>/ --grade G4 --project-id <id>

# 매 페이즈 진입
python skills/theseus-harness/scoring/phase_state.py enter \
    --root .ShipofTheseus/<proj>/ --phase 00 --producer project-namer

# 매 페이즈 종료 (산출물 frontmatter created_at 자동 cross-check)
python skills/theseus-harness/scoring/phase_state.py exit \
    --root .ShipofTheseus/<proj>/ --phase 00 \
    --fingerprint sha256:7a9c... --outcome ok \
    --artifact-path naming/00-naming.md

# phase 09 진입 직전 (HARD-RULE 9.f cold-session validator 와 함께)
python skills/theseus-harness/scoring/phase_state.py validate \
    --root .ShipofTheseus/<proj>/
# exit 0 = PASS, exit 1 = stderr 위반 목록
```

## 4. 트리거 신호 + abort vs warn

| 신호 | 검출 시점 | 처리 |
|---|---|---|
| 동시 in_progress 페이즈 ≥ 2 | enter 시 | **ABORT** — 직전 페이즈 exit 호출 의무 |
| entered_at ≤ 직전 entered_at/exited_at | enter / validate | **ABORT** — 단조성 위반, `intent/00-violation.md` 기록 |
| exited_at ≤ entered_at | exit / validate | **ABORT** — 시계 역행 (보정 필요) |
| frontmatter created_at ∉ [entered_at, exited_at] | exit / validate | **ABORT** — *forgery 의심* (v0.9.22 패턴) |
| phase_state.json 부재인데 enter/exit 호출 | enter / exit | **ABORT** — init 먼저 |
| current_status=in_progress 인데 phases[-1] 가 in_progress 아님 | validate | WARN — state 파일 손상, 재초기화 후보 |

ABORT 처리 통일 — exit 1 + stderr 명세 + orchestrator 가 `intent/00-violation.md` 박고 페이즈 재진입.

## 5. frontmatter forgery cross-check 정확도

```python
def cross_check(artifact_path: Path, entered_at: str, exited_at: str) -> bool:
    """산출물 frontmatter created_at 이 [entered_at, exited_at] 윈도 안인지."""
    fm_dt = parse_iso(read_frontmatter_field(artifact_path, "created_at"))
    return parse_iso(entered_at) <= fm_dt <= parse_iso(exited_at)
```

v0.9.22 사건 :
- phase 진입 시각 = (사후 백필 시점) 14:30
- 산출물 created_at = (위조) 13:30 (페이즈 01-06 진입 *이전* 9-12 분)
- 본 cross-check → forgery 의심, ABORT.

cross-check 적용 대상은 frontmatter `created_at` 또는 `produced_at` (둘 다 사용됨).

## 6. self_lint C-PSM 룰

```python
def lint_phase_state_machine(skill_root: Path) -> list[str]:
    """본 컨벤션 본문 + scoring/phase_state.py 존재 + 의무 함수 검증."""
    issues = []
    conv = (skill_root / "conventions" / "phase-state-machine.md").read_text(encoding="utf-8")
    py = (skill_root / "scoring" / "phase_state.py")

    # 컨벤션 본문 키워드
    for kw in ["단조성", "frontmatter", "forgery", "phase_state.json", "schema_version"]:
        if kw not in conv:
            issues.append(f"phase-state-machine.md: '{kw}' 키워드 누락")

    # 스크립트 존재 + 의무 함수
    if not py.exists():
        issues.append("scoring/phase_state.py 부재")
        return issues
    src = py.read_text(encoding="utf-8")
    for fn in ["cmd_init", "cmd_enter", "cmd_exit", "cmd_validate", "cmd_status",
               "validate_state", "_read_frontmatter_created_at"]:
        if f"def {fn}" not in src:
            issues.append(f"scoring/phase_state.py: 의무 함수 {fn} 부재")

    # SCHEMA_VERSION 상수
    if "SCHEMA_VERSION" not in src:
        issues.append("scoring/phase_state.py: SCHEMA_VERSION 상수 부재")

    return issues
```

CHECKS 등록 (sprint-34 신규) — `("C-PSM", "phase_state.py runtime monotonic gate (sprint-34 / v0.9.39)", check_phase_state_machine)`.

## 7. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 단조성 = 시간 인과 룰, 도메인 무관.
b- frontmatter created_at cross-check = 산출물 무결성, 도메인 무관.
c- phase 00~14 enter/exit 라이프사이클 = 본 하네스 일반 골격 (`phases/`), 케이스 X.

## 8. 안티 패턴

a- **phase_state.py 미호출** — orchestrator 가 산출물만 박고 state 누적 안 함. self_lint C-PSM fail (post-hoc validate 시 phase_state.json 부재).
b- **수동 phase_state.json 편집** — 사람이 시각을 임의 수정해 단조성 깸. validate 가 검출 (sprint-17 forgery 패턴 차단).
c- **artifact_path 누락** — exit 시 산출물 경로 안 박음 → frontmatter cross-check skip → forgery 회피로. exit 시 `--artifact-path` 의무 (G3+).
d- **created_at 이 ISO8601 비표준** — `2026-05-09 13:00` (T 누락) / `13:00:00+09:00` (timezone 변형). cross-check parse 실패 → 경고만 (현 구현). 후속: ISO8601 strict 강제.
e- **다카포 rerun 시 같은 페이즈 재진입을 단조성 위반으로 reject** — 페이즈 06/08 다카포 loop 는 *같은 phase 번호* 의 재진입이 의도. 본 구현은 시각만 단조이면 OK (phase 번호 중복 OK).

## 9. cold.isolation CheckSpec 와의 layer 분리

| Layer | 컨벤션 | 검증 시점 | 검증 대상 |
|---|---|---|---|
| **runtime entry-time** | **본 컨벤션 (C-PSM)** | 매 페이즈 enter/exit 시점 | phase_state.json 단조성 + frontmatter cross-check |
| **post-hoc artifact** | `run_gate.py` `cold.isolation` CheckSpec (meta_audit, 9.f 은퇴) | phase 09 | cold session 정합 (값 기반 — isolation 관측) |

두 layer 가 *상보적*. runtime 은 시각/순서, post-hoc 은 산출물 내용. 둘 다 통과해야 phase 09 진입.

## 10. 그레이드 활성

- G1 / G2 — 단순 (3~11 산출물). phase_state.json 의무. minimal phases (00 또는 01 + 04 + 06 + 08 + 09 + 14) 만 누적.
- **G3+ — 풀 활성** (00~14 phase 전체).
- G5 — 빡빡 모드 (frontmatter created_at parse 실패 시 ABORT, 현 구현 WARN 보다 강하게).

## 11. 호환성

- [`contracts.md`](contracts.md) — fingerprint chain 무결성 = 본 phase_state.json 의 fingerprint 필드 입력.
- [`phase-lineage-viewer.md`](phase-lineage-viewer.md) (br) — lineage.md fingerprint chain 표 = phase_state.json 변환 view.
- `run_gate.py` `cold.isolation` CheckSpec (9.f 은퇴) — post-hoc layer, 본 컨벤션 = runtime layer (직교).
- [`autonomy.md`](autonomy.md) — ABORT 시 페이즈 재진입 = 자율 (사용자 ack 없음).
