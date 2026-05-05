# Intent Completeness — 9 sub-criterion 의도 본문 의무

## 한 줄 요약

**페이즈 01 의 `intent/01-intent.md` 본문이 9 sub-criterion (§a~§k) 모두 채워져 있어야 한다.** intent 가 *제목 + 한 줄* 만 박힌 채 plan 으로 넘어가는 회귀 차단. 9 sub 미완 시 페이즈 02 진입 거부 + 페이즈 01 재실행. v0.9.19 부터 intent axis sprint ≥ 2 의무 동행 — 9 sub PASS 라도 *content depth* sprint NN+1 보강.

## v0.9.19 sprint-13 갱신 — intent sprint loop trigger

§k 9 sub 모두 PASS 라도 [`intent-plan-impl-sprint-trinity.md`](intent-plan-impl-sprint-trinity.md) (bd) 의 intent axis sprint ≥ 2 의무 — 첫 sprint = baseline measure, 두 번째 sprint = lesson 적용 후 재측정. axis lesson 후보:
- mindmap richness 추가 노드 (mindmap-richness-default A 등급 도달까지)
- §k limitation / data-derived 분리 강화
- §i derived NFR 추가 + 임계 정량화

본 컨벤션의 9 sub 자기 충분 검증과 *직교* — sub PASS 라도 *content depth* 가 sprint NN+1 에서 보강 의무.

## 한 줄 요약

**페이즈 01 의도 문서가 9 sub-criterion 모두 명시 의무** — system boundary / entities / resources / events / state variables / assumptions / **limitations** / performance measures / **data-derived facts vs introduced assumptions 분리**. v0915-cold01 외부 채점 -2pt (Conceptual 18/20) 의 직접 원인 = limitations 절 + data/introduced 분리 부재.

## 1. 결손 진단

기존 [`../phases/01-intent.md`](../phases/01-intent.md) 의 §a~§j (10 항목) 가 다음을 *명시 의무화 안 함*:

- **§ limitations** — 모델/시스템의 *알려진 한계*. "이 모델이 *못 다루는* 것" 명시 의무. 사용자 의도와 별도.
- **§ data-derived vs introduced 분리** — 의도/모델의 fact 가 *입력 데이터에서 도출* 인지 *분석가가 가정 추가* 인지 명시 분리. 정직성 핵심.
- **§ system boundary** — §a 무엇을 와 직교. *시스템 외부 vs 내부* 명시.
- **§ entities / resources / events / state variables** — 도메인 모델 골격 (의도 단계에서 *추정* OK, 페이즈 06 plan-tree 가 확정).

→ 이 9 sub 부재 = conceptual model 채점 -2~3pt 의 일반 패턴.

## 2. 운영 룰

### Step 1 — 페이즈 01 의도 §k 신규 의무

`intent/01-intent.md` 에 §k 신규:

```markdown
## §k Conceptual model — 9 sub-criterion (intent-completeness)

a- **System boundary**: 시스템 *외부 (out of scope)* vs *내부 (in scope)* 명시.
b- **Entities**: 시스템 안에서 *능동* 으로 행동하는 객체 (트럭 / 사용자 / job / process 등).
c- **Resources**: *공유 / 제약 capacity* 자원 (loader / DB connection / queue / GPU 등).
d- **Events**: 상태 변화 트리거 (load_start / dump_end / request_received 등).
e- **State variables**: 시뮬/시스템의 *동적 상태* (in_queue / processing / idle 등).
f- **Assumptions** — 명시 가정 (homogeneous trucks / Poisson arrival 등).
g- **Limitations** — *알려진 한계* (no breakdowns / no shift change / no error retries 등). 모델이 *못 다루는* 것.
h- **Performance measures** — 외부에서 관찰·계량 가능 메트릭 (throughput / latency / utilization 등).
i- **Data-derived vs introduced** — fact 카탈로그 분리:
   - *Data-derived*: 입력 데이터/스펙에서 도출 (truck capacity = 100t from data/trucks.csv)
   - *Introduced*: 분석가가 *가정 추가* (load time = TruncNormal(mean=3.0, sigma=0.5) — 분석가 가정)
```

### Step 2 — 도메인 비종속

본 9 sub 는 simulation 도메인 종속 X — 모든 *의도 추출* 작업에 적용:
- DES (시뮬레이션) → entities = trucks, resources = loaders, events = load_start
- Web API → entities = users, resources = DB pool, events = request_received
- ML pipeline → entities = samples, resources = GPU, events = batch_step
- Workflow → entities = jobs, resources = workers, events = job_completed

intent-extractor 에이전트가 도메인 추정 후 9 sub 의 도메인-매핑 예시 자동 제시.

### Step 3 — 본문 의무 검증

`scoring/intent_completeness.py` (또는 self_lint 모듈):

```python
def check_intent_completeness(intent_md: Path) -> list[str]:
    body = intent_md.read_text(encoding="utf-8")
    required_subsections = [
        "system boundary", "entities", "resources", "events",
        "state variables", "assumptions", "limitations",
        "performance measures", "data-derived",
    ]
    missing = [s for s in required_subsections if s not in body.lower()]
    return [f"intent missing §k sub: {s}" for s in missing]
```

매 페이즈 01 산출물 작성 시 9 sub 모두 박힘 검증. 누락 시 페이즈 02 진입 거부.

## 3. self_lint 룰

`scoring/self_lint.py` C-IC (신규):

```python
def lint_intent_completeness(skill_root: Path) -> list[str]:
    errors = []
    ic = (skill_root / "conventions" / "intent-completeness.md").read_text(encoding="utf-8")
    p1 = (skill_root / "phases" / "01-intent.md").read_text(encoding="utf-8")
    template = skill_root / "templates" / "intent.template.md"
    # 1. 9 sub 키워드 ic 본문 보유
    required = ["system boundary", "entities", "resources", "events", "state variables",
                "assumptions", "limitations", "performance measures", "data-derived"]
    for kw in required:
        if kw.lower() not in ic.lower():
            errors.append(f"intent-completeness.md: '{kw}' 키워드 누락")
    # 2. phase 01 본문이 §k 또는 intent-completeness 인용
    if "intent-completeness" not in p1 and "9 sub-criterion" not in p1:
        errors.append("phases/01-intent.md: intent-completeness §k 인용 누락")
    return errors
```

## 4. 본 컨벤션이 *케이스 종속이 아닌* 이유

a- 9 sub-criterion = conceptual modeling 의 *generic dimension*, 도메인 X.
b- 도메인 별 매핑은 §2 step 2 의 generic pattern (entities/resources/events).
c- data-derived vs introduced 분리 = *정직성 룰*, 도메인 무관.

## 5. 안티 패턴

a- **§k 통째 누락** — 의도 §a~§i 만 작성하고 §k 없음. self_lint C-IC fail.
b- **§g limitations 절에 "없음" 만** — 한계가 *없는* 모델은 거짓. 최소 1 항목 의무.
c- **§i data-derived/introduced 분리 안 함** — 모든 fact 를 한 표에 섞어 정직성 위반. 두 표 분리.
d- **assumptions == limitations 혼동** — assumptions = *전제로 가정* (load time normal), limitations = *못 다루는 영역* (no breakdowns).

## 6. 자기 검증

본 하네스 자체에 적용 — `intent/01-intent.md` 가 본 하네스의 *system boundary / entities / resources / events / state variables / assumptions / limitations / performance / data-derived* 9 sub 작성 가능. 본 컨벤션 도입 회차 = v0.9.18 sprint-12.
