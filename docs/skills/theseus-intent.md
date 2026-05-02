# theseus-intent 가이드

## 한 줄 요약

**페이즈 00–05 — 명명 + 의도 추출 + 마인드맵 + 콜드 재이해 + 사용자 인터뷰 + 비평·대안.** 본 하네스의 *모든 후속 페이즈가 의존하는 단 하나의 인터럽트 지점*.

## 언제 호출하는가

ⓐ 새 요청에서 의도 명세를 처음 만들 때 (orchestrator 가 자동 위임).
ⓑ 외부에서 명명/의도 산출물을 받지 못해 처음부터 시작해야 할 때.
ⓒ 기존 의도 산출물이 시간이 지나 콜드 재이해가 필요할 때 — 같은 입력으로 다시 호출하면 새 frontmatter 로 재생성.

## 호출 형식

```
/theseus-intent <요구사항>
```

## 페이즈별 산출물

| 페이즈 | 파일 | 내용 |
| ----- | ---- | --- |
| 00 | `naming/00-naming.md` | `project_id`, 한 줄 요약, 별칭 |
| 01 | `intent/01-intent.md` | 사용자 의도 + 도메인별 NFR 카탈로그 자동 채움 |
| 02 | `intent/02-intent-review.md` | 의도 자체 비평 (의도 표류 가능성) |
| 03 | `intent/03-comprehension.md` | 콜드 재이해 (다른 에이전트가 처음 보는 것처럼) |
| 04 | `intent/04-{questions,answers,autonomy,grade,resource-profile,stack}.md` | 사용자 인터뷰 + 자율 권한 + 그레이드 + 리소스 + 스택 |
| 05 | `intent/05-{critique,decisions}.md` | 비평·대안 + 결정 기록 |

## 사용자 인터뷰 (페이즈 04)

본 하네스의 인터럽트가 발생하는 *유일한 지점.* 컨벤션:

ⓐ **두괄식** — 결론 먼저, 근거 뒤에.
ⓑ **1 회 1 질의** — 멀티 질문 금지, 한 번에 한 결정.
ⓒ **숫자 객관식 5 개 이하** — 자유 입력 강제 금지.
ⓓ **확증 회귀** — 사용자 답변이 모순될 때 자동 회귀 질의.
ⓔ **PRD 처리 허들** — 충실한 PRD 가 입력이어도 인터뷰 항목 생략 금지. PRD 추출값은 객관식 1 번 보기로 제시.

자세한 컨벤션은 [`../../skills/theseus-harness/conventions/interview.md`](../../skills/theseus-harness/conventions/interview.md) (PRD 처리는 같은 파일의 "PRD/스펙 입력 처리" 절 — v0.4.0 PR-13 prd-handling 흡수).

## 인터뷰 항목

| 코드 | 주제 |
| ---- | ---- |
| Q-G1 | 그레이드 확정 (G1 거부 ~ G5 빡빡) |
| Q-D1 | 도메인 (결제/CRUD/검색/실시간/ML/FE/모바일) |
| Q-D2 | 백엔드 스택 (Go default) |
| Q-D3 | 성능 천정 (RPS·latency, 리소스 프로파일 자동 매핑) |
| Q-D4 | 운영 환경 (로컬/K8s/EC2/서버리스) |
| Q-D5 | 자율 권한 (4 단계) |
| Q-D6 | 멀티버스 사용 여부 (격리 병렬 우주) |
| Q-D7 | 체크포인트 봉인 단위 |
| NFR | 성능·가용성·보안·운영·FE NFR 확정 |

## 입출력 (단독 호출)

- **입력**: 사용자 원본 요청 + 레포 컨텍스트.
- **출력**: 위 표의 산출물 모두. 다음 스킬 (`theseus-plan`) 이 입력으로 받음.

frontmatter 는 [`../../skills/theseus-harness/scoring/fingerprint.py`](../../skills/theseus-harness/scoring/fingerprint.py) 가 박는다.

## 자주 묻는 질문

**Q. 사용자가 빠른 처리를 원해 인터뷰를 스킵하라고 요구하면?**
A. **거부.** PRD 처리 허들이 그것을 막는다. PRD 가 충실해도 객관식 1 번 보기로 1 클릭 확정만 받는다 — `user_explicit_confirmation: true` + timestamp 가 필수. 인터럽트 0 약속의 *전제* 보호.

**Q. 그레이드가 G1 으로 판정되면?**
A. orchestrator 와 본 스킬이 즉시 호출을 거부 — "본 하네스 대상이 아닙니다, 직접 편집하시거나 일반 Claude Code 슬래시 명령을 사용하십시오" 안내.

**Q. 페이즈 04 답변이 04 의 다른 항목과 모순되면?**
A. 확증 회귀 — 모순된 두 답변을 표시하고 사용자에게 어느 쪽을 채택할지 다시 묻는다 (1 회 한정).

## 더 읽을거리

- [`../../skills/theseus-intent/SKILL.md`](../../skills/theseus-intent/SKILL.md) — 기계 진입점.
- [`../../skills/theseus-harness/conventions/interview.md`](../../skills/theseus-harness/conventions/interview.md) — 인터뷰 컨벤션.
- [`../../skills/theseus-harness/conventions/spec-catalog.md`](../../skills/theseus-harness/conventions/spec-catalog.md) — 도메인별 NFR 카탈로그.
- [`../../skills/theseus-harness/conventions/grades.md`](../../skills/theseus-harness/conventions/grades.md) — 그레이드 시스템.
- [`../../skills/theseus-harness/conventions/interview.md`](../../skills/theseus-harness/conventions/interview.md) "PRD/스펙 입력 처리" 절 — PRD 처리 허들 (v0.4.0 PR-13 흡수).
