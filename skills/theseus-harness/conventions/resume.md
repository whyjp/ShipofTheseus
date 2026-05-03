# 리줌(Resume) 컨벤션 — 중단된 항해의 재개

## 한 줄 요약
**14 페이즈가 몇 시간~며칠 걸리는 본 하네스에서 사용자/시스템 중단은 정상 시나리오다.** `state.json` 이 진행 상태를 누적 기록하고, FE 가 *완료 산출물 + 현재 진행 페이즈* 를 라이브 표시하며, `resume.py` 가 마지막 valid 지점부터 손실 없이 재개. 본 하네스의 *데이터가 곧 resume 의 자산* — 인덱싱(`indexing.md`) + 핑거프린트(`contracts.md`) + 체크포인트(`checkpoints.md`) 셋이 결합되어 resume 무결성을 보장.

## 중단 사유 분류

| 사유 | 예 | resume 가능성 | state.json 자동 기록 |
| --- | -- | ----------: | ----------------: |
| **planned** | 사용자가 의도적으로 정지 (예: 비용 검토) | 100% | ✅ 자발적 |
| **user_signal** | Ctrl+C / 세션 종료 | 90% | ⚠️ 직전 페이즈까지만 |
| **crash** | 에이전트 OOM / 프로세스 죽음 | 70% | ⚠️ 부분 산출물 가능 |
| **external** | 네트워크 / API rate limit / 토큰 소진 | 80% | ⚠️ 직전 호출 결과 미기록 가능 |
| **timeout** | 페이즈 자체 타임아웃 (예: 1 페이즈 > 1시간) | 80% | ⚠️ 부분 진행 |
| **invalid_state** | frontmatter 체인 깨짐 발견 | 50% | ❌ 무결성 회복 필요 |

## state.json — 진행 상태 단일 source

`.ShipofTheseus/<프로젝트>/state.json` 이 *현재 진행 상태* 의 truth. 매 페이즈 시작/종료 + 체크포인트 + 멀티버스 분기 + 서브에이전트 디스패치 시점에 자동 갱신.

```json
{
  "project_id": "atlas-ledger",
  "project_run": "20260501-174412",
  "started_at": "2026-05-01T17:44:12+09:00",
  "last_updated_at": "2026-05-01T19:23:45+09:00",
  "elapsed_seconds": 5973,
  "status": "in_progress",
  "current_phase": "08-implement",
  "current_universe": "a",
  "current_module": "T-020",
  "current_sub_depth": 1,
  "last_completed_phase": "07-plan-recursion",
  "last_completed_artifact": "plan/07-plan-review.md",
  "last_completed_fingerprint": "sha256:c21d...",
  "active_skill": "theseus-implement",
  "active_agent": "implementer",
  "pending_artifacts": [
    "impl/T-020/sub/A.1/code.go (in_progress)",
    "impl/T-020/sub/A.2/code.go (in_progress)"
  ],
  "completed_count": 14,
  "total_estimated": 47,
  "interrupt_reason": null,
  "resume_hint": null
}
```

중단 발생 시 (또는 사용자가 수동 정지 시) 마지막 갱신 시점의 state.json + interrupt_reason 자동 기록:

```json
{
  ...,
  "status": "interrupted",
  "interrupt_reason": "external_rate_limit",
  "interrupt_at": "2026-05-01T19:25:11+09:00",
  "resume_hint": "theseus-implement --from .ShipofTheseus/atlas-ledger/ --resume-from impl/T-020/sub/A.2"
}
```

## 재개 진입점 결정 알고리즘 (`scoring/resume.py`)

```python
def determine_resume_point(state: dict, artifacts: list[Artifact]) -> ResumePlan:
    """
    state.json + 인덱싱된 산출물을 입력으로, 어디서부터 재개할지 결정.
    """
    # 1. 무결성 검증 — fingerprint 체인 + parent_module 체인
    integrity = index_builder.integrity_checks(artifacts)
    if integrity["fingerprint_chain"].startswith("break"):
        return ResumePlan(
            ok=False,
            action="repair_required",
            reason="fingerprint 체인 끊김 — 마지막 valid 지점까지 회수 필요",
            details=integrity,
        )

    # 2. 부분 산출물 처리 (state.pending_artifacts 검사)
    incomplete = []
    for path in state.get("pending_artifacts", []):
        full_path = root / path.split(" ")[0]
        if full_path.exists():
            text = full_path.read_text(encoding="utf-8")
            if not has_valid_frontmatter(text) or "in_progress" in path:
                incomplete.append(path)

    if incomplete:
        # 부분 산출물은 폐기 후 재시도가 default — checkpoints.md 의 회귀와 동일
        return ResumePlan(
            ok=True,
            action="discard_incomplete_then_resume",
            discard_files=incomplete,
            entry_skill=state["active_skill"],
            entry_input=state["last_completed_artifact"],
            reason=f"부분 산출물 {len(incomplete)} 개 폐기 후 {state['active_skill']} 재시작",
        )

    # 3. 모든 산출물 완전 — 마지막 완료 페이즈의 *다음* 페이즈로 진입
    next_phase = _next_phase_after(state["last_completed_phase"])
    next_skill = _phase_to_skill(next_phase)
    return ResumePlan(
        ok=True,
        action="resume_next_phase",
        entry_skill=next_skill,
        entry_input=state["last_completed_artifact"],
        next_phase=next_phase,
        reason=f"마지막 완료 페이즈 {state['last_completed_phase']} → 다음 {next_phase}",
    )
```

## 부분 산출물 처리 룰

페이즈 진행 중 *완료 전 중단* 으로 인한 미완성 파일 처리:

a- **frontmatter 없음** = 부분 산출물 — 자동 폐기 (다음 시도가 새로 작성).
b- **frontmatter 있으나 fingerprint null** = compute 실패 — 자동 폐기 + 재생성.
c- **frontmatter + fingerprint 정상** = 완전 산출물 — 보존, 다음 페이즈 진입.
d- **state.json 의 pending_artifacts 와 디스크 불일치** = 신뢰성 의심 — `repair_required`, 사용자 ack 필요 (인터뷰 후 인터럽트 0 의 *유일한 추가 예외*).

폐기 전 *백업* — `discarded/<timestamp>/<원경로>` 로 이동 (학습 자산 보존, [`checkpoints.md`](checkpoints.md) 의 손녀 패턴과 동일).

## resume 가능 시점

a- **페이즈 경계** — 가장 안전. 마지막 페이즈가 완료된 직후의 frontmatter 가 기준.
b- **체크포인트 경계** — 페이즈 내부의 안정 시점 (`checkpoints/<phase>/<sequence>/state.json`).
c- **서브에이전트 머지 후** — `impl/T-020/sub/.../merge.md` 작성 직후 (한 부모 모듈의 모든 자식 머지 완료).
d- **멀티버스 verdict 후** — `multiverse/<branch>/verdict.md` 작성 직후.

## 페이즈 *진행 중* resume 의 한계

**한 페이즈 내부의 부분 진행은 resume 안 함** — 너무 복잡하고 LLM 출력의 비결정성 때문에 같은 페이즈를 반복 실행해도 결과가 달라짐. 페이즈를 통째 *재실행* 이 default. 비용은 페이즈 단위 (체크포인트 단위 회귀가 비용 최소화).

## FE 라이브 진행 추적 (webview 보강)

[`../templates/webview/`](../templates/webview/) 의 webview 가 다음 추가:

a- **신규 탭 `Progress`** — state.json 라이브 폴링 (5초 간격) + SSE 업데이트:
   - 현재 페이즈 / 우주 / 모듈 / 깊이
   - 경과 시간 (timing 헤더)
   - 완료 vs 예상 (14 / 47 같은 진행률)
   - 활성 스킬 + 에이전트 (어떤 모델이 호출 중)
   - pending artifacts 리스트
   - 자율 결정 라이브 보고 ([`autonomy.md`](autonomy.md) Q-D6 매핑)

b- **신규 컴포넌트 `InterruptControl`** — 사용자가 *외부에서* 정지하고 싶을 때:
   - "안전 정지" 버튼 — 현재 페이즈 종료 후 state.json 에 `status: "user_paused"` 박고 종료
   - "긴급 정지" 버튼 — 즉시 SIGTERM, 부분 산출물 가능
   - 정지 후 "재개" 버튼 — `resume.py determine` 결과 표시 + 사용자 확인

c- **신규 탭 `Resume`** — 중단된 작업의 재개:
   - 마지막 state.json 표시
   - resume_hint 명령 (복사 가능)
   - 무결성 체크 결과 (`index_builder.py verify` 결과)
   - 부분 산출물 목록 (폐기 vs 보존 선택)

## 매우 장기간 작업의 사용자 경험

본 하네스가 14 페이즈 + 무한 스프린트 루프 + 멀티버스 + 서브에이전트로 *몇 시간~며칠* 걸리는 시나리오에서:

a- **초기 인터뷰** (~10 분) — 사용자가 페이즈 04 의 Q-G1/Q-D1~D7 + NFR + 스택 답.
b- **자율 진행** — 사용자는 자기 일을 함. webview 를 *언제든* 열어 진행 상태 관찰 가능.
c- **장시간 후 확인** — 몇 시간 뒤 webview 열기 → Progress 탭에서 "지금 페이즈 10 sprint 5 / 점수 0.987" 한눈에.
d- **중단 필요 시** — InterruptControl 의 "안전 정지" → state.json 에 정지 사유 기록 → 다음에 `resume.py next` 로 재개.
e- **장기 미관찰 후** — 1 일 뒤 webview 확인 → 핸드오프 완료 또는 자율 한계 도달로 정지 (interrupt_reason: `autonomy_threshold_reached`).

## resume 검증 절차

```bash
# 현재 상태 보기
python scoring/resume.py state --root .ShipofTheseus/<프로젝트>/

# 재개 진입점 결정
python scoring/resume.py next --root .ShipofTheseus/<프로젝트>/

# 무결성 + 재개 가능성 검증
python scoring/resume.py validate --root .ShipofTheseus/<프로젝트>/
```

`validate` 가 통과하면:

```bash
# 권고된 진입점으로 단독 스킬 호출
/<recommended_skill> --from .ShipofTheseus/<프로젝트>/
```

[`sub-agents.md`](sub-agents.md) 의 단독 호출 input 계약 매트릭스 + [`contracts.md`](contracts.md) 의 frontmatter 검증이 그대로 적용 — resume 가 단독 호출의 *특수 케이스*.

## state.json 자동 갱신 의무

a- **페이즈 시작/종료 시** — 모든 분해 스킬의 진입/종료 hook.
b- **체크포인트 작성 시** — checkpoint.py 가 state.json 도 함께 갱신.
c- **멀티버스 분기/머지 시** — current_universe 갱신.
d- **서브에이전트 디스패치/머지 시** — current_module / current_sub_depth.
e- **자율 결정 시** — 라이브 보고와 함께 state.json `autonomy_decisions` 누적 (Q-D6 답 따라).

자동 갱신 누락은 `self_lint C31` 가 검출 — 마지막 산출물 timestamp ≤ state.json `last_updated_at`.

## resume 가 안 되는 케이스 (정직)

a- **`.ShipofTheseus/` 디렉터리 자체가 삭제됨** — 데이터가 곧 자산. 데이터 손실 = resume 불가.
b- **frontmatter 체인이 여러 곳에서 깨짐** — 부분 회복 가능하나 사용자 결정 필요.
c- **외부 코드 (resume 시점의 git HEAD) 가 stale** — `git status` 검증 + 사용자 ack.
d- **임계 미달 종료된 작업** — resume 가능하나 *왜 임계 미달이었는지* 의 lesson_pack 이 누적되어 같은 정체 반복 위험. 사용자가 의도/스택을 변경한 뒤 재개하는 게 합리.

## 안티 패턴

a- **state.json 수동 편집** — `resume.py` 의 input. 손으로 고치면 무결성 깨짐.
b- **부분 산출물 보존** — frontmatter 없는 미완성 파일을 그대로 두면 다음 시도가 valid 하다고 착각. 자동 폐기 default.
c- **resume 없이 처음부터 재실행** — 본 하네스 비용 폭발. 항상 `resume.py next` 먼저.
d- **무결성 깨짐 무시 강제 resume** — `validate` 실패는 *수리 필요* 신호. 무시하면 데이터 corruption 누적.
e- **FE Progress 탭 없는 webview** — 사용자가 진행 중 상태 못 봄. *완료 산출물만* 보여주는 webview 는 본 컨벤션 위반.
