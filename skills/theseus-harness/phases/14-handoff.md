# 페이즈 14 — 핸드오프

## 한 줄 요약
**한 줄 요약 + 점수 + 누적 시간 + 웹뷰 실행 명령** 을 사용자에게 전달하고 종료. 지휘자가 직접 작성 — 서브에이전트 없음.

## 입력
- `.ShipofTheseus/<프로젝트명>/` 의 모든 산출물.

## 산출물
`handoff/14-handoff.md` 와 채팅 메시지.

## 핸드오프 문서 구조

[`../conventions/timing.md`](../conventions/timing.md) 헤더 + 다음:

a- **무엇이 만들어졌는가** — 한 문단, 외부 관찰 표현 (`01-intent.md` 의 "무엇을" 과 미러).
b- **최종 점수** — 차원별 sub-score 와 함께.
c- **스프린트 수** — 몇 회로 도달했는가.
d- **결정 이력** — 페이즈 04, 05 에서 사용자가 한 모든 선택의 bullet 목록.
e- **알려진 갭** — rubric 이 1.0 미만 ≥ 0.9 로 매긴 항목과 한 줄 사유.
f- **추천 후속** — 비평가가 deferred 한 항목 + 범위 외이지만 가치 있는 후속.
g- **회귀 이력** — 페이즈 11 트리거된 스프린트들과 한 줄 해소.
**g-2 — Knowledge Portfolio refresh** (sprint-50, HARD-RULE 9.iii) — 본 회차에서 *학습한 통찰* ≥ 3 항목 의무. 각 §-level header (keyword: `lesson` / `learned` / `insight` / `finding` / `takeaway` / `observation` / `discovery` / `학습` / `교훈` / `발견` / `관찰` / `통찰`) + 본문 ≥80 chars. distinct topic ≥ 3. 단순 산출물 list 가 아니라 *insight*. 격언: Hunt & Thomas, Pragmatic Programmer Ch.1 — *"Treat your knowledge as an investment portfolio."* CLI: `scoring/knowledge_portfolio_check.py`.
h- **시간 요약** — 최초 프롬프트 → 핸드오프 총 경과, 페이즈별 누적 (텍스트 막대 표).
i- **웹뷰 실행 방법 (viewer 를 산출한 경우)** — prebuilt shell + viewer-runtime 이 옵션(advisory, §8 동결 B2-F3). phase 00 pre-bootup 으로 떠 있는 경우 종료 시 `bash .ShipofTheseus/<프로젝트>/viewer-runtime/viewer-down.sh`(또는 `viewer-down.ps1`) 호출 — PID 누수 차단(조건부 의무, 부팅한 경우만). dev mode 옵션 `cd webview && bun install && bun run dev`. URL 은 `viewer-runtime/viewer.lock.json` 의 `viewers[].url`.

i-3- **Viewer teardown (부팅한 경우 조건부 의무)** — 부팅했다면 phase 14 종료 시 `python skills/theseus-harness/scoring/pre_bootup.py teardown --root .ShipofTheseus/<프로젝트>` 호출. lock 의 PID 종료 + lock 정리 — 부팅하지 않은 run 은 해당 없음.
i-2- **Phase lineage viewer cross-link** ([`../conventions/phase-lineage-viewer.md`](../conventions/phase-lineage-viewer.md), br v0.9.22) — 본 핸드오프 본문에 `.ShipofTheseus/<프로젝트>/lineage.md` cross-link 의무 (G3+). lineage.md 가 phase 00 → 14 전체 흐름 + dacapo 요약 + fingerprint chain 단일 view. 본 페이즈 종료 시점에 orchestrator 가 final_outcome=HANDOFF 박고 fingerprint chain 무결성 최종 검증.
j- **Decision-support framing** ([`../conventions/decision-support-framing.md`](../conventions/decision-support-framing.md), v0.9.18) — 결정 질문 (Q1~QN) 마다 다음 3 항목 본문 의무 :
  - **Operational implications** — 결과가 운영에 의미하는 것 (1-2 문단)
  - **Trade-off framing** — 대안 비교 표 (≥3 차원, 예: 비용 / throughput / latency)
  - **Opportunity-cost** — 선택 시 *포기하는* 것 (명시 옵션)
  Q 답이 *수치 + bottleneck 결론* 만 있으면 self_lint C-DSF fail. handoff frontmatter `evidence_decision_support` 매핑 (Q 별 3 항목 보유 boolean).

## 채팅 메시지 (사용자에게)

세 문장 + 웹뷰 실행 한 줄.

예시:
```
"<프로젝트명>" 출하 완료. 점수 0.93, 스프린트 4회, 총 1시간 23분. 산출물은 .ShipofTheseus/<프로젝트명>/, 회귀 1건은 스프린트 3 에서 세션 쿠키 변경 revert 로 해소.
웹뷰: cd .ShipofTheseus/<프로젝트명>/webview && bun install && bun run dev
어느 산출물부터 살펴볼까요?
```

## 자율 git 작업 (사용자 사전 승인 시)

사용자가 자율 커밋·푸시·PR 생성을 사전에 허용한 경우 ([CLAUDE.md](../../CLAUDE.md) 또는 슬래시 인자 명시):

1- 변경 사항을 커밋 — 메시지에 프로젝트명·최종 점수·스프린트 수 포함.
2- 작업 브랜치에 푸시.
3- PR 생성 — 본문에 핸드오프 문서 요약 + 웹뷰 실행 명령 + 산출물 트리.

사전 승인 없으면 사용자에게 묻고 답을 받은 뒤 진행.

## 성공 기준

a- 핸드오프 파일 존재.
b- 채팅 요약이 사용자 화면에 스크롤 없이 들어감.
c- 웹뷰가 실제로 기동 가능한 상태.
d- 자율 권한이 있다면 PR URL 까지 사용자에게 제공.

## 흔한 실패

> **공통 안티 패턴** (A1~A10) 은 [`../SKILL.md`](../SKILL.md) "안티 패턴 통합 카탈로그" 참조. 본 페이즈 고유 실패는 (현재 발견 없음 — 후속 회차에서 추가).


## §canonical 산출물 룰 (sprint-37 PR-AH inline, prev: canonical-not-stub.md)

`handoff/14-handoff.md` (canonical) 도 phase 06 §canonical 룰 동등 적용 — winner inline ≥80% 또는 shared schema 3 섹션 의무. asof_fingerprint frontmatter 의무. "80%", "shared schema", "asof_fingerprint" 키워드 본문 박힘 강제 (self_lint C-CNS).


## §timing 핸드오프 요약 (sprint-37 PR-AI inline, prev: timing.md)

**최종 핸드오프 문서에는 다음을 표시한다** :

a- 최초 프롬프트 시각
b- 핸드오프 시각
c- 총 소요 (사람이 읽는 단위 — `1시간 23분`)
d- 페이즈별 누적 시간 막대 (텍스트 표)
e- 스프린트별 소요 표

§timing 본 룰의 전체 정의 (시작 시각 기록, 페이즈 산출물 헤더, 스프린트 보고서 헤더, 도구 사용, 강제 사항) 는 [`./00-naming.md`](./00-naming.md) §timing 참조.

## §자동 CLI 호출 (sprint-43 PR-E)

phase 14 handoff *직후* + dashboard sync *전후* orchestrator 의무 호출 :

```bash
# HARD-RULE 9.xx — handoff 본문에 surrender 어휘 차단
python skills/theseus-harness/scoring/surrender_phrase_grep.py \
    --project-root .ShipofTheseus/<proj>/ \
    --output .ShipofTheseus/<proj>/quality/gate_surrender_phrase_handoff.json

# HARD-RULE 9.uu — handoff 본문에 phase 09/10/11 인용 검증
python skills/theseus-harness/scoring/cross_phase_context_audit.py \
    --project-root .ShipofTheseus/<proj>/ --phase 14 \
    --output .ShipofTheseus/<proj>/quality/gate_cross_phase_context_14.json

# HARD-RULE 9.zz — phase invoke audit 최종 (모든 declared CLI invoked 검증)
python skills/theseus-harness/scoring/phase_invoke_audit.py \
    --orchestrator-skill skills/theseus-orchestrator/SKILL.md \
    --project-root .ShipofTheseus/<proj>/ \
    --output .ShipofTheseus/<proj>/quality/gate_phase_invoke_audit_final.json

# HARD-RULE 9.yy — submission 산출물 disk 잔존 (.pyc-only 차단)
python skills/theseus-harness/scoring/submission_completeness.py \
    --submission-dir submissions/<id>/ \
    --eval-report submissions/<id>/results/evaluation_report.json \
    --grade <G> \
    --output submissions/<id>/results/gate_submission_completeness.json

# HARD-RULE 9.aaa — dashboard sync 직후, dashboard ↔ disk parity
python skills/theseus-harness/scoring/dashboard_submission_parity.py \
    --submission-dir submissions/<id>/ \
    --dashboard-md dashboard/src/content/submissions/<id>.md \
    --output submissions/<id>/results/gate_dashboard_parity.json
```

본 §은 sprint-43 의 *literal Bash command* 박힘. handoff 후 *대량 삭제* / *dashboard mismatch* 차단.

## sprint-50 — Knowledge Portfolio refresh CLI 의무 호출 (HARD-RULE 9.iii)

phase 14 산출 *직후* 의무 호출:

```bash
python skills/theseus-harness/scoring/knowledge_portfolio_check.py \
    --project-root .ShipofTheseus/<프로젝트>/ \
    --min-insights 3 \
    --json-out .ShipofTheseus/<프로젝트>/handoff/knowledge_portfolio.json
```

- exit 0 → handoff 종료
- exit 1 → handoff §g-2 본문에 insight ≥3 보강 후 재진입.

격언: Hunt & Thomas, *Pragmatic Programmer*, Ch.1 — *"Your Knowledge Portfolio."*

## sprint-52 — Viewer Finalization Closure (HARD-RULE 9.nnn / 9.ppp, 조건부 존치 — B2-F3)

**생산 의무는 §8 동결로 해제됐다** — viewer(lineage.json/webview.json/dashboard.json) 를 산출한 경우에 *한해* 조건부 진실성 의무가 남는다: `pre_bootup.py` 가 phase 00 직전 박은 *빈 골격*(`mermaid_flowchart="cold session 미시작"`, `fingerprint_chain=[]`, `project_run="pending"` 등)을 실 데이터로 refresh 하지 않으면 viewer 가 거짓 placeholder 상태로 마감된다 — 이건 만든 산출물의 진실성 문제이지 산출 자체의 의무가 아니다. **viewer 산출물이 존재하지 않는 run 은 아래 호출 해당 없음.**

viewer 산출물이 존재하는 경우, phase 14 산출 직후 호출 (3 종 CLI literal Bash):

```bash
# HARD-RULE 9.nnn — phase 14 finalize CLI invoke 의무 (Viewer Finalization Closure)
# .ShipofTheseus/ 재귀 스캔 → fingerprint chain / mermaid / project_run / winner 실값 refresh
# + dashboard.json + webview/data/webview.json 동시 정정
python skills/theseus-harness/scoring/lineage_finalize.py refresh \
    --root .ShipofTheseus/<프로젝트>/ \
    --strict

# fingerprint chain 무결성 최종 검증 (handoff 본문 §i-2 의 의무 검증)
python skills/theseus-harness/scoring/fingerprint.py chain \
    --dir .ShipofTheseus/<프로젝트>/

# HARD-RULE 9.ppp — viewer JSON placeholder 잔존 차단 (sprint-51 placeholder_grep 의 viewer 확장)
python skills/theseus-harness/scoring/placeholder_grep.py \
    --target-root .ShipofTheseus/<프로젝트>/ \
    --include-viewer-json \
    --max-violation-count 0
```

- viewer 산출물 존재 시: exit 0 (3 종 모두) → handoff 종료 / exit 1(어느 하나) → 보강 후 재진입
- viewer 미산출 run: 위 3 종 호출 해당 없음(§8 동결 — 강제 아님)
- **(B1 §5.2)** `quality/gate_meta_audit.json` 존재 + `verdict == "pass"` 확인은 별개로 존치
  — 부재 시 phase 09 run_gate.py 미호출 신호, phase 09 재진입 강제.

viewer 를 산출하는 경우, pre_bootup 의 *emit-skeleton* 과 본 §의 refresh 가 대칭을 이룬다(cold session 시작 시 빈 골격 emit ↔ 종료 시 실 데이터 refresh).

격언: declared = invoked (sprint-43) — 본 §은 그 패턴의 viewer 차원 적용.
