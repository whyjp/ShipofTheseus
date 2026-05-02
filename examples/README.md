# Examples — 본 하네스 사용 시나리오 (oh-my-ralph 패턴 차용)

3 시나리오로 본 하네스 진입을 안내한다. 각 예제는 페이즈 04 의 사전 위임 8 답 (Q-D1 ~ Q-D8) 과 Q-D8 의 verification commands 답을 *실제 사용자가 입력하는 형태로* 보여준다.

| 시나리오 | 그레이드 | 도메인 정착도 | 권장 진입점 | 가이드 |
| ------- | ------- | ------------ | --------- | ------ |
| `evolving-spec` | G3 | 미정착 — 인터뷰로 의도 좁히기 | `/theseus-orchestrator` | [evolving-spec.md](evolving-spec.md) |
| `frozen-spec` | G4 | 명확 — PRD 또는 명세 첨부 | `/theseus-orchestrator` | [frozen-spec.md](frozen-spec.md) |
| `fix-bug` | G2 | 단일 모듈 버그 수정 | `/theseus-harness` | [fix-bug.md](fix-bug.md) |

## 첫 번째 적용을 위한 진입 절차 (공통)

1. Claude Code 마켓플레이스 등록 + 플러그인 설치 ([INSTALL.md §3](../INSTALL.md))
2. 본인 프로젝트 루트로 이동 (필요 시 `git init` 후 빈 커밋 1 개)
3. `/theseus-orchestrator <요구사항>` 호출 — 페이즈 00 (명명) 부터 자동 진행
4. 페이즈 04 에서 객관식 답 + Q-D8 의 검증 명령 입력 — *유일한 사용자 인터럽트*
5. 페이즈 05 ~ 13 자율 진행 — 핸드오프 도착 시 `webview/` 의 `bun run dev` 실행

## Q-D8 답 패턴 — 3 시나리오 비교

각 예제 공통의 Q-D8 답이 어떻게 다른지:

| 답 | evolving-spec | frozen-spec | fix-bug |
| -: | ------------- | ----------- | ------- |
| 1 (CI 그대로) | ❌ — CI 미정착 | ✅ — `npm test && npm run typecheck` | ✅ — `pytest tests/auth/test_login.py` |
| 2 (새 스니펫) | ✅ — 도메인별 스모크 한 줄부터 | ❌ — 이미 CI 충분 | ❌ — 단일 회귀 케이스 추가만 |
| 3 (manual only) | △ — 디자인 컴포넌트면 manual 비중 큼 | ❌ — 자동화 가능 | ❌ — bash 회귀 가능 |

답 3 (`manual_only: true`) 시 페이즈 09 의 `e2e_pass` 차원 cap 0.95 적용 — 점수 천정 강하의 명시적 트레이드오프. 핸드오프에서 외부 검증 책임이 사용자에게 명시된다.
