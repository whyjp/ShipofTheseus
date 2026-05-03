---
name: theseus-orchestrator
version: 0.7.0
description: theseus-harness 의 14 페이즈를 8 분해 스킬로 순차 위임. frontmatter 자동 핸드오프, 페이즈 04 한 번 인터뷰 후 인터럽트 0. 단독 단순 작업에는 사용 금지 — grade-assess 로 먼저 확인.
---

# theseus-orchestrator — 분해 스킬 진행 제어

## 한 줄 요약
**14 페이즈를 8 분해 스킬로 순차 위임하는 인덱스 스킬.** 단일 source of truth 는 [`../theseus-harness/`](../theseus-harness/) — 본 분해는 *형태* 만 만들고 콘텐츠는 한 곳에 둔다. 연동 깨짐 0 가 핵심 약속.

## 분해 스킬 호출 순서

| 순서 | 스킬 | 페이즈 | 입력 | 출력 |
| ---: | ---- | ----- | ---- | ---- |
| 1 | [`theseus-intent`](../theseus-intent/SKILL.md) | 00–05 | 사용자 요청 | `naming/00-naming.md` + `intent/01..05*.md` |
| 2 | [`theseus-plan`](../theseus-plan/SKILL.md) | 06–07 | intent 산출물 | `plan/06-plan.md` + `plan/07-plan-review.md` |
| 3 | [`theseus-implement`](../theseus-implement/SKILL.md) | 08 | plan 산출물 | `impl/08-impl-log.md` + 코드/테스트 |
| 4 | [`theseus-quality`](../theseus-quality/SKILL.md) | 09 | impl 산출물 | `quality/09-quality-gate.md` |
| 5 | [`theseus-sprint`](../theseus-sprint/SKILL.md) | 10–11 | quality 산출물 | `sprints/NN/{report.md, bisect.md?}` (임계 도달까지) |
| 6 | [`theseus-webview`](../theseus-webview/SKILL.md) | 12 | 모든 산출물 | `webview/` (bun + hono + react) |
| 7 | [`theseus-handoff`](../theseus-handoff/SKILL.md) | 13 | 모든 산출물 + sprint 결과 | `handoff/13-handoff.md` |

명명(00) 은 intent 가 책임. 사용자 인터뷰(04) 는 intent 안에서.

## 스킬 간 인터페이스 — frontmatter 계약

**각 스킬은 다음 스킬의 입력 산출물에 박힌 frontmatter** ([`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md)) **를 검증한 뒤 자기 작업 시작.** 검증 실패 시 자기 페이즈 진입 거부. 이게 분해의 안전 장치.

```python
# 모든 분해 스킬의 진입 프롤로그 (의사코드)
def enter_skill(input_artifacts: list[Path]):
    for art in input_artifacts:
        fp_check = subprocess.run([
            "python", "../theseus-harness/scoring/fingerprint.py",
            "verify", "--file", str(art),
        ], check=False)
        if fp_check.returncode != 0:
            raise SkillEntryError(f"frontmatter 검증 실패: {art}")
        # skill_name, skill_version, prev_fingerprint 체인 무결성 확인
    proceed_with_phase()
```

## 단순 source of truth — 콘텐츠 위치

- **컨벤션 (28 개)** — [`../theseus-harness/conventions/`](../theseus-harness/conventions/)
- **페이즈 문서 (14)** — [`../theseus-harness/phases/`](../theseus-harness/phases/)
- **에이전트 프롬프트 (13)** — [`../theseus-harness/agents/`](../theseus-harness/agents/)
- **스코어링 도구 (8)** — [`../theseus-harness/scoring/`](../theseus-harness/scoring/)
- **템플릿** — [`../theseus-harness/templates/`](../theseus-harness/templates/)

각 분해 스킬은 *위임 + 입출력 계약만* 정의. 룰 본문 복제 금지 ([`../theseus-harness/conventions/fragmentation.md`](../theseus-harness/conventions/fragmentation.md) §1).

## 그레이드 처리 (호출 직후 첫 동작)

```
1. grade_assess.py 자동 추정 (사용자 원문)
2. 페이즈 04 의 Q-G1 객관식 → 사용자 그레이드 확정
3. 그레이드별 분해 스킬 호출 (모든 그레이드 진행 — 그레이드는 *내부 모듈레이션만*):
   - Grade 1 (Trivial): mini_harness_tbd 모드 — 최소 페이즈 (v0.5.x 후속에서 모듈레이션 정의)
   - Grade 2 (Simple):  intent + plan + implement + quality (4 스킬)
   - Grade 3 (Standard): intent + plan + implement + quality + sprint(3 cap) + handoff (6)
   - Grade 4 (Complex): 7 스킬 모두 (default)
   - Grade 5 (Critical): 7 스킬 + 빡빡 모드
```

자세한 그레이드 매트릭스는 [`../theseus-harness/conventions/grades.md`](../theseus-harness/conventions/grades.md).

## 단독 호출 가능성 (재진입)

> **단독 호출 시 의존성:** 본 stub 은 *위임 + 인터페이스* 만. 룰 본문은 [`../theseus-harness/`](../theseus-harness/) 단일 source 에 위치. **fresh user 가 본 stub 만 설치하면 본문 점프가 모두 dead link** — 본 저장소 전체 또는 최소 [`../theseus-harness/`](../theseus-harness/) 동반 설치 필요.

```bash
# 반드시 theseus-harness 동반 설치 후
/theseus-orchestrator --from <input_dir>
```

`<input_dir>` 의 frontmatter 가 본 스킬의 *입력 계약* 을 만족하면 진입.

각 분해 스킬도 valid frontmatter 입력만 있으면 재진입 가능 (단, harness 동반 필수):

a- "이미 의도 문서 있음 → 계획부터" → `theseus-plan` 단독 호출.
b- "구현 끝났음 → 게이트만" → `theseus-quality` 단독 호출.
c- "스프린트 점수 시계열 있음 → 회귀 바이섹트만" → `theseus-sprint` 단독 호출.

[`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md) 의 단계 재진입 룰이 이를 보장.

## 본 분해의 안전 보장

a- **연동 테스트** — [`../theseus-harness/scoring/test_skill_handoff.py`](../theseus-harness/scoring/test_skill_handoff.py) 가 각 스킬 산출물의 frontmatter 가 다음 스킬 입력으로 valid 한지 검증.
b- **self_lint C28** — 8 stub 존재 + 단일 source of truth 룰 위반 검사 (콘텐츠가 stub 에 복제되지 않았는지).
c- **fingerprint 체인** — 각 스킬 산출물이 직전 스킬 산출물의 fingerprint 를 prev_fingerprint 로 가짐. 체인 끊기면 다음 스킬이 진입 거부.

## 본 분해 진행 상황

a- ✅ 8 stub 디렉터리 + SKILL.md 신규.
b- ✅ 단일 source of truth 유지 (콘텐츠 = `../theseus-harness/`).
c- ✅ 연동 핸드오프 테스트 — `test_skill_handoff.py`.
d- ✅ self_lint C28 — 분해 무결성 검사.
e- ⏸ 콘텐츠 실제 분해 (각 stub 에 자기 페이즈/에이전트 콘텐츠 이동) — v0.4.0 후보.

## 두 진입점의 관계 — orchestrator vs harness

본 저장소에 *두 진입점* 이 있고, 둘 다 같은 결과를 만든다 — 차이는 *형태* 만:

| 진입점 | 역할 | 사용 시점 |
| ----- | ---- | -------- |
| **`/theseus-orchestrator`** (본 스킬) | **공식 메인 체이닝 진입점** — 8 분해 스킬을 순차 호출 | default — 분해의 가치 (단독 호출, 단계 재진입, 모듈성) 를 활용하고 싶을 때 |
| `/theseus-harness` ([`../theseus-harness/SKILL.md`](../theseus-harness/SKILL.md)) | 콘텐츠 source + 호환 단일 진입점 | 분해 신경 안 쓰고 한 호출로 끝내고 싶을 때 |

self_lint C28 가 두 진입점이 *같은 결과* 를 만드는지 검증 (페이즈 인덱스 일치, 컨벤션 cross-link 일치).

## 메인 체이닝 실행 흐름 (의사코드)

본 스킬이 호출되면 다음 흐름으로 8 분해 스킬을 자동 체이닝:

```python
def orchestrate(user_request: str, project_root: Path):
    """
    공식 메인 체이닝 진입점. 8 분해 스킬을 순차 호출하고 산출물 frontmatter
    로 자동 핸드오프. 인터럽트 0 (페이즈 04 안에서만 사용자 질의).
    """
    # 1. 그레이드 자동 추정 (호출 직후 첫 동작)
    #    grade.md 룰: 그레이드는 *내부 모듈레이션만*. 진행/거부 게이트 아님.
    #    G1 도 mini_harness_tbd 로 진행 (v0.5.0 sprint-02-a).
    grade_report = subprocess.run([
        "python", "../theseus-harness/scoring/grade_assess.py",
        "--request", user_request,
    ])
    # recommendation: tight_mode (G5) / full_or_standard (G3/G4) / mini_harness (G2) / mini_harness_tbd (G1)

    # 2. timing 시작 시각 기록 (timing.md)
    timing_start = write_timing_start(project_root)

    # 3. theseus-intent (페이즈 00–05) — 사용자 인터뷰 포함
    intent_artifacts = invoke_skill(
        "theseus-intent",
        inputs=[user_request, project_root],
        grade=grade_report["primary_grade"],   # 페이즈 04 의 Q-G1 으로 사용자 확정
    )
    verify_handoff(intent_artifacts, next_skill="theseus-plan")

    # 4. 그레이드별 후속 스킬 활성화
    grade = read_user_confirmed_grade(intent_artifacts)
    autonomy_policy = read_autonomy_answers(intent_artifacts)  # Q-D1~D7
    threshold = grade_to_threshold(grade)  # G2=0.95, G3=0.97, G4=0.999, G5=0.99999

    if grade == 1:
        return short_circuit_with_simple_response()

    # 5. theseus-plan (페이즈 06–07)
    plan_artifacts = invoke_skill("theseus-plan", inputs=intent_artifacts)
    verify_handoff(plan_artifacts, next_skill="theseus-implement")

    # 6. theseus-implement (페이즈 08) — TODO DAG 병렬 디스패치
    impl_artifacts = invoke_skill("theseus-implement", inputs=plan_artifacts)
    verify_handoff(impl_artifacts, next_skill="theseus-quality")

    # 7. theseus-quality (페이즈 09)
    quality_artifacts = invoke_skill("theseus-quality", inputs=impl_artifacts)
    verify_handoff(quality_artifacts, next_skill="theseus-sprint")

    # 8. theseus-sprint (페이즈 10–11) — 임계 도달까지 무한 루프
    #    (Grade 3 면 3 sprint cap, Grade 4/5 면 무한)
    sprint_artifacts = invoke_skill(
        "theseus-sprint",
        inputs=quality_artifacts,
        threshold=threshold,
        autonomy=autonomy_policy,   # Q-D1 회귀 / Q-D3 천정 / Q-D4 정체 / Q-D7 체크포인트
        sprint_cap=3 if grade == 3 else None,
    )

    # 9. theseus-webview (페이즈 12) — 항상 생성
    webview_artifacts = invoke_skill("theseus-webview", inputs=all_artifacts())

    # 10. theseus-handoff (페이즈 13)
    handoff = invoke_skill("theseus-handoff", inputs=all_artifacts())

    return handoff


def invoke_skill(skill_name: str, inputs: list, **kwargs):
    """분해 스킬 호출 + 산출물 frontmatter 자동 박음."""
    artifacts = run_skill(skill_name, inputs, **kwargs)
    for art in artifacts:
        subprocess.run([
            "python", "../theseus-harness/scoring/fingerprint.py",
            "compute", "--file", str(art),
            "--prev", str(prev_artifact_for(art)),
            "--skill-version", "0.2.2",
        ])
    return artifacts


def verify_handoff(artifacts: list, next_skill: str):
    """다음 스킬 진입 전 frontmatter 체인 무결성 검증."""
    for art in artifacts:
        result = subprocess.run([
            "python", "../theseus-harness/scoring/fingerprint.py",
            "verify", "--file", str(art),
        ])
        if result.returncode != 0:
            raise SkillHandoffError(
                f"{art} 의 frontmatter 검증 실패 — 다음 스킬({next_skill}) 진입 거부"
            )
    # 추가: 다음 스킬이 기대하는 입력 산출물이 모두 있는지 확인
    expected = required_inputs_for(next_skill)
    missing = [e for e in expected if not any(art.name == e for art in artifacts)]
    if missing:
        raise SkillHandoffError(
            f"다음 스킬 {next_skill} 입력 누락: {missing}"
        )
```

## 자동 핸드오프 — frontmatter 체인이 인터페이스

각 스킬 호출 사이의 핸드오프는 *인간 개입 없이* 자동:

```
theseus-intent → naming/00-naming.md (fingerprint X)
              → intent/01-intent.md  (prev = X, fingerprint Y)
              → ...
              → intent/05-decisions.md (prev = ..., fingerprint Z)

theseus-plan ← Z 검증 ✓ → plan/06-plan.md (prev = Z, fingerprint W)
            → ...

... (체인 계속)
```

체인 끊기면 다음 스킬이 진입 거부 — `SkillHandoffError`. 사용자에게는 timing 라이브 보고만 한 줄.

## 단독 스킬 호출 (재진입)

각 분해 스킬을 *단독* 호출 가능 — 입력 산출물의 frontmatter 가 valid 하면:

```bash
# 의도 산출물만 있을 때 — 계획부터
/theseus-plan --from .ShipofTheseus/<프로젝트>/

# 구현 끝났을 때 — 게이트만
/theseus-quality --from .ShipofTheseus/<프로젝트>/

# 스프린트 결과만 있을 때 — 회귀 바이섹트만
/theseus-sprint --from .ShipofTheseus/<프로젝트>/sprints/
```

[`../theseus-harness/conventions/contracts.md`](../theseus-harness/conventions/contracts.md) 의 단계 재진입 룰이 보장.

## 호출

```
/theseus-orchestrator <요구사항>     # 공식 메인 체이닝 — 8 분해 스킬 자동 순차
/theseus-harness     <요구사항>     # 호환 단일 진입점 — 같은 결과
/theseus-<단일스킬>  --from <dir>    # 단독 재진입
```
