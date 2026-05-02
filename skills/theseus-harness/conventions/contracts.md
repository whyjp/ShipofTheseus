# 산출물 계약 컨벤션 (Contracts)

## 한 줄 요약
**페이즈 산출물에 frontmatter (스킬 이름·버전·페이즈·프로젝트·핑거프린트·이전 핑거프린트·생성 시각) 를 박아, 외부에서 그 산출물을 들고 와도 *다음 페이즈부터 재진입* 가능하게 한다.** 이 frontmatter 가 페이즈 간 의존성 계약이다 — 페이즈 N 의 출력 = 페이즈 N+1 의 입력.

## 왜 필요한가

ⓐ **부분 호출** — 사용자가 인터뷰만 먼저 돌리고, 결과 파일을 다른 시점·다른 머신에서 던져 플랜 페이즈만 따로 호출하고 싶다.
ⓑ **단계 재진입** — 회귀 후 "스프린트 3 부터 다시" 같은 정확한 진입점.
ⓒ **모듈 분해 가능성** — 향후 페이즈 그룹별로 별도 스킬로 분해할 때, 산출물 계약만 지키면 스킬 간 결합 없이 통신.
ⓓ **출처 보장** — 산출물이 본 하네스가 만든 것인지 확신 (위·변조·잘못된 입력 거부).

## frontmatter 스키마

모든 페이즈 산출물 마크다운 파일은 다음 frontmatter 로 시작한다.

```yaml
---
skill_name: theseus-harness
skill_version: 0.2.0
phase: 06-plan                       # phases/<id> 와 동일
project_id: atlas-ledger             # naming 페이즈에서 확정한 프로젝트명
project_run: 20260501-174412         # 같은 프로젝트의 별 실행 식별 (timing/start.json 의 epoch)
fingerprint: sha256:7a9c...          # 본 산출물의 핑거프린트
prev_fingerprint: sha256:1f2e...     # 직전 페이즈 산출물의 핑거프린트 (체인)
produced_at: 2026-05-01T17:46:30+09:00
producer_agent: planner              # agents/<name>.md 의 name
---

> **시작:** ... · **종료:** ... · **소요:** ... · **누적 경과:** ... · **현재 시각:** ...
```

frontmatter 다음 줄 부터는 [`timing.md`](timing.md) 의 시간 메타 헤더, 그 다음이 본문.

## 비직렬성 메타 확장 ([`indexing.md`](indexing.md))

본 하네스의 산출물이 *멀티버스 분기 + 서브에이전트 재귀* 로 비선형 트리를 가지므로, [`indexing.md`](indexing.md) 가 정의한 추가 필드를 frontmatter 에 박는다 — 일반 선형 산출물은 모두 null:

```yaml
universe: a | b | c | null            # 멀티버스 우주 식별
parent_branch: 06-plan | null         # 분기 페이즈 ID (멀티버스 트리거된 페이즈)
parent_module: T-020 | null           # 서브에이전트 분해의 부모 TODO ID
depth: 0 | 1 | 2                      # 재귀 깊이 (서브에이전트). 한도 2.
branch_kind: sequential | multiverse_winner | multiverse_loser
           | sub_parallel | sub_sequential | sub_competition | null
```

이 필드들이 [`../scoring/index_builder.py`](../scoring/index_builder.py) 의 입력 — INDEX.md / index.json 자동 생성.

## 핑거프린트 계산

```
fingerprint = "sha256:" + hex(sha256(
    skill_name +
    skill_version_major +              # major 만 (호환 범위)
    phase +
    project_id +
    project_run +
    prev_fingerprint +
    canonical_body                      # 본문에서 시간 메타와 frontmatter 자체를 제외한 정규화 텍스트
))
```

ⓐ `canonical_body` = 본문 전체에서 frontmatter, timing 헤더, 후행 공백, 행 끝 정규화(`\n` 통일) 후의 텍스트.
ⓑ `skill_version_major` 만 사용해 마이너/패치 변경에는 핑거프린트가 흔들리지 않게.
ⓒ `prev_fingerprint` 가 들어가므로 페이즈 간 체인이 형성 — 한 단계 변조되면 그 이후 모두 무효.

## 핑거프린트 헬퍼

[`scoring/fingerprint.py`](../scoring/fingerprint.py) 가 마크다운 파일을 받아 frontmatter 를 파싱·핑거프린트 계산·검증.

```bash
# 새 산출물 생성 시
python scoring/fingerprint.py compute --file plan/06-plan.md --prev intent/05-critique.md

# 외부 산출물 검증
python scoring/fingerprint.py verify --file plan/06-plan.md
```

## 재진입 규칙

지휘자가 호출 시작 시 사용자가 `.ShipofTheseus/<프로젝트>/` 또는 일부 산출물 묶음을 가리키면:

① 모든 마크다운 산출물의 frontmatter 를 파싱.
② 각 파일에 대해:
  ⓐ `skill_name == "theseus-harness"` 확인.
  ⓑ `skill_version` 의 major 가 현재 하네스 major 와 같음 확인.
  ⓒ `project_id`, `project_run` 이 같은 묶음 안에서 일관 확인.
  ⓓ `fingerprint` 재계산해 frontmatter 의 값과 일치 확인.
  ⓔ `prev_fingerprint` 가 직전 페이즈 산출물의 `fingerprint` 와 일치 확인 (체인 무결).
③ 가장 늦은 valid 페이즈 N 식별. 페이즈 N+1 부터 시작.
④ 일관성 깨진 산출물이 있으면 사용자에게 객관식 질의 ([`interview.md`](interview.md) 컨벤션):

```
질의: 던져진 산출물 일부가 검증 실패했습니다. 어떻게 진행할까요?

paths/06-plan.md 의 fingerprint 가 본문과 불일치 — 외부 편집 가능성. 의도부터 다시 시작할 수도 있고, 해당 페이즈만 재실행할 수도 있습니다.

선택지:
1. 페이즈 06 만 재실행 (이전 산출물은 유지)
2. 페이즈 01 부터 전체 재실행
3. 외부 편집 의도였음 — frontmatter 만 갱신하고 진행
4. 정지하고 사람이 검토
```

## 부분 호출 시나리오

ⓐ "**인터뷰만**" — 페이즈 00–05 만 실행, `.ShipofTheseus/<프로젝트>/` 의 `naming/`, `intent/` 만 산출. 이후 종료.
ⓑ "**플랜만**" — 위 산출물을 입력으로, 페이즈 06–07 만 실행 후 `plan/` 산출.
ⓒ "**구현부터 끝까지**" — 위 + plan 산출물을 입력으로, 페이즈 08–13 까지.

CLI 슬래시 명령에 페이즈 범위를 지정할 수 있게 하는 것도 후속 PR 후보 — `/theseus-harness --from 06 --to 07`.

## frontmatter 가 산출물에 박히는 시점

ⓐ 각 페이즈의 서브에이전트가 산출물을 작성할 때 직접 `fingerprint.py compute` 호출해 결과를 frontmatter 에 기입.
ⓑ 또는 산출물을 본문만 작성한 뒤 페이즈 종료 시점에 지휘자가 helper 로 일괄 부착.
ⓒ 어느 방식이든, 지휘자가 페이즈 *완료* 로 표시하기 전에 frontmatter 가 부착되어야 함.

## 안티 패턴

ⓐ frontmatter 없이 산출 — 페이즈 09 게이트에서 자동 fail.
ⓑ frontmatter 의 `fingerprint` 를 손으로 적기 — 검증 실패. 항상 helper 로 계산.
ⓒ `prev_fingerprint` 누락 — 체인 끊김. 페이즈 N=00 (시작 페이즈) 만 `prev_fingerprint: null` 허용.
ⓓ `skill_version` 을 임의 변경해 호환을 위장 — 검증은 본문 + 기록된 버전을 기반으로 하므로 결국 깨진다.

## 버전 정책 (semver)

ⓐ MAJOR — 산출물 형식 / 페이즈 인덱스 / 컨벤션 호환성 깨는 변경.
ⓑ MINOR — 페이즈 추가, 컨벤션 추가, 후방 호환 변경.
ⓒ PATCH — 문서 오타, 에이전트 프롬프트 미세 조정.

같은 MAJOR 내의 산출물은 재진입 호환. 다른 MAJOR 면 거부 (마이그레이션 가이드는 `docs/changes/` 의 ADR 로).

## 향후 모듈 분해 시

본 컨벤션이 그대로 스킬 간 인터페이스가 된다. `skills/theseus-intent` 가 출력한 산출물을 `skills/theseus-plan` 이 frontmatter 만 검증하고 그대로 소비 — 두 스킬은 본문에 대한 약한 결합만 갖는다 (DIP 의 직접 적용).
