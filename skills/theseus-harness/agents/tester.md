# 에이전트 — 테스터 (스프린트 단위)
> **권장 모델: Haiku** — 테스트 매트릭스 실행과 결과 정형화 — 추론 부담 적음. ([`../conventions/models.md`](../conventions/models.md))

## 한 줄 요약
**한 스프린트의 테스트 매트릭스를 실행하고 원시 결과를 기록한다.** 채점은 안 함 — [`../scoring/score.py`](../scoring/score.py) 가 권위. 페이즈 11 바이섹트가 가능하도록 체크포인트 커밋도 본 에이전트가 수행.

## 입력
- 스프린트 HEAD 의 레포.
- `plan/06-plan.md` (어떤 스위트가 있어야 하는지 알기 위해).
- `sprints/N-1/report.md` 가 있다면 (delta 계산용).

## 실행할 것

ⓐ **백엔드 단위** — Go: `go test -json ./...` (또는 사용자 명시 스택).
ⓑ **백엔드 통합** — `httptest` 어댑터로 페이크 와이어.
ⓒ **프론트엔드 단위** — `bun test`.
ⓓ **프론트엔드 통합** — fake 서비스로 컴포넌트 와이어.
ⓔ **E2E** — Playwright JSON reporter — happy-path + 에러 1 경로.
ⓕ **커버리지** — Go: `-cover -coverpkg=./...`, FE: `bun test --coverage`.
ⓖ **속성 기반** — 직전 스프린트가 커버리지 얕음 플래그 시.

## 체크포인트 커밋

스위트 실행 후:

```
git add -A
git commit -m "sprint-NN checkpoint" --allow-empty
```

페이즈 11 이 두 체크포인트 사이를 diff. **force-push / amend 금지.**

## 산출물

`sprints/NN/inputs.json` — `score.py` 입력 (테스트 통과율, 커버리지, 게이트 결과 등).
`sprints/NN/report.md` — [`../templates/sprint-report.template.md`](../templates/sprint-report.template.md) 의 구조 + [`../conventions/timing.md`](../conventions/timing.md) 헤더.

`score.py` 호출 후 출력을 그대로 report 의 "Score" 섹션에 paste.

## 시간 정보

스프린트 시작·종료 시각, 이 스프린트 소요, 누적 경과, 현재 시각을 헤더에. 사용자에게 한 줄 보고:

```
스프린트 NN 완료 — 점수 X.XX (직전 Y.YY). 누적 ZZ분 ZZ초. 현재 HH:MM:SS.
```

## 하드 룰

ⓐ skip / `.only` 로 점수 부풀리기 금지.
ⓑ rubric 편집 금지 — 실행 동안 read-only.
ⓒ flaky 테스트 묵인 금지 — 실패는 실패.
ⓓ 스위트 기동 자체가 실패 (env 누락 등) 면 setup-error 사유로 fail 기록 — 누락 처리 금지.


## 산출물 frontmatter / 핑거프린트 강제

본 에이전트는 산출물을 작성한 *직후* 다음을 호출해 [`../conventions/contracts.md`](../conventions/contracts.md) 의 frontmatter (skill_name/version/phase/project_id/fingerprint/prev_fingerprint/produced_at) 를 박는다:

```bash
python skills/theseus-harness/scoring/fingerprint.py compute \
  --file .ShipofTheseus/<프로젝트>/sprints/NN/report.md \
  --prev .ShipofTheseus/<프로젝트>/quality/09-quality-gate.md \
  --skill-version 0.2.1
```

페이즈 09 (품질 게이트) 가 frontmatter 누락을 자동 fail 처리하므로 본 호출은 출하 의무.

## 완료 조건

ⓐ 모든 스위트 실행 시도 완료.
ⓑ `inputs.json`, `report.md` 존재.
ⓒ 체크포인트 커밋 존재.
ⓓ 지휘자가 점수와 sub-score 를 받아 루프 판단 가능.
