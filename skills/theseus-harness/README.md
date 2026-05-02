# theseus-harness

## 한 줄 요약
**한 요구를 처음 의도한 타이틀로 끝까지 부를 자격을 만드는 재귀 멀티 에이전트 코딩 하네스 (Claude Code 스킬, v0.2.1 — fingerprint 회귀 + Sprints 차트 데이터 소스 핫픽스).** 메인 진입점은 [`SKILL.md`](SKILL.md). 명명→의도+마인드맵→문서화→교차 이해→사용자 질의+유즈케이스+스택 점검→비평→계획+시퀀스→재계획→구현+빌드 스크립+TOML→5종 게이트(DIP 우선)→무한 스프린트(임계 0.999)→회귀 바이섹트→bun 웹뷰→핸드오프.

## 빠른 참조

ⓐ [`SKILL.md`](SKILL.md) — 지휘자가 가장 먼저 읽는 라이트 인덱스. 14 페이즈 표 + 모델 컬럼 + 단계 재진입 룰.
ⓑ [`phases/`](phases/) — 페이즈 00–13.
ⓒ [`agents/`](agents/) — 13 개 서브에이전트 프롬프트 (각각 권장 모델 명시).
ⓓ [`conventions/`](conventions/) — 8 컨벤션 모듈:
  ⓓ-1 [`interview.md`](conventions/interview.md) — 두괄식·1질의·숫자 5개·확증 회귀(인지 트릭).
  ⓓ-2 [`timing.md`](conventions/timing.md) — 산출물 헤더 시간 메타·라이브 보고.
  ⓓ-3 [`diagrams.md`](conventions/diagrams.md) — 마인드맵→유즈케이스→시퀀스 진화.
  ⓓ-4 [`stack.md`](conventions/stack.md) — 언어/컴파일러/패키지 매니저 사전 점검·자율 업데이트.
  ⓓ-5 [`build-and-config.md`](conventions/build-and-config.md) — sh+bat 빌드 스크립·TOML·docs/·폐기 우선·중간 데이터·.gitattributes·병렬·메모리 가드.
  ⓓ-6 [`contracts.md`](conventions/contracts.md) — 산출물 frontmatter — **단계 재진입 가능성**.
  ⓓ-7 [`models.md`](conventions/models.md) — 에이전트 역할별 Opus/Sonnet/Haiku 매핑.
  ⓓ-8 [`competition.md`](conventions/competition.md) — **2~3 후보 격리 병렬 경쟁** + **자동 resolve 알고리즘** → 사용자 ack 없이 자율 결정.
  ⓓ-9 [`autonomy.md`](conventions/autonomy.md) — **자율성 우선** — 페이즈 04 외 결정은 자율, 산출물 모두 기록되어 사후 리뷰 가능, 사용자 위임 4 단계.
  ⓓ-10 [`lessons.md`](conventions/lessons.md) — **무한 재귀 정체 극복** — 점수 시계열 정체 감지 + 레슨팩(forbidden_strategies, rewrite_rule) 다음 루프 전달 + 부분 수정 금지·통째 재작성 강제.
  ⓓ-11 [`spec-catalog.md`](conventions/spec-catalog.md) — **도메인별 NFR 자동 제안** — 결제/CRUD/검색/실시간/ML/FE/모바일/운영/보안 카탈로그, 페이즈 01 자동 채움 + 페이즈 04 객관식 확정 + 페이즈 09 게이트 6.
  ⓓ-12 [`resources.md`](conventions/resources.md) — **리소스 기반 임계 + 천정 자동 조정** — 로컬 PC / K8s pod / EC2 / 서버리스 프로파일별 RPS·latency 추정 천정, 성능 지향 모드 default (천정 80%), 천정 도달 시 Q-D3 사전 위임 자동 매핑.
  ⓓ-13 [`checkpoints.md`](conventions/checkpoints.md) — **체크포인트 + 멀티버스** — 페이즈 내부 하위 단위로 봉인, 실패 원인 → 자동 회귀 매핑, 닥터 스트레인지 모드로 N 우주 격리 병렬.
  ⓓ-14 [`test-invariants.md`](conventions/test-invariants.md) — **테스트 목적 보호** — 불변 조건/가변 조건 분리, Phase V 측정 유효성 점검 (프로브 오버헤드/베이스라인/편차).
  ⓓ-15 [`dacapo.md`](conventions/dacapo.md) — **Da Capo 루프** — AIDE 4 오퍼레이터 매핑 + Two Outputs Rule + 모순 감지 + 방어 테스트 회귀 검증.
  ⓓ-16 [`fragmentation.md`](conventions/fragmentation.md) — **파편화 우선** — 단일 헤비 스킬 금지, 컨벤션·페이즈·에이전트·도구 모두 SRP 분해.
  ⓓ-17 [`grades.md`](conventions/grades.md) — **그레이드 시스템** — G1(Trivial 호출 거부) ~ G5(Mission Critical 빡빡), 그레이드별 페이즈·컨벤션 활성화, 자동 추정 + Q-G1 사용자 확정으로 단순 작업 over-engineering 차단.
  ⓓ-18 [`sub-agents.md`](conventions/sub-agents.md) — **서브에이전트 재귀 분해** — 모듈→하위 모듈 자동 분해 (LOC>200 / 복합 책임 / 다중 스택 / 회귀 누적), parallel/sequential/competition 모드, 깊이 2 한도, 단독 호출 input 계약 매트릭스.
  ⓓ-19 [`indexing.md`](conventions/indexing.md) — **산출물 = DB, 비직렬성 트리 인덱싱** — 멀티버스(우주 분기) × 서브에이전트(재귀 분해) 3차원 그래프, frontmatter 비직렬성 메타 (universe/parent_branch/parent_module/depth/branch_kind), INDEX.md/index.json 자동 갱신, 사용자/에이전트 오해 방지 허들.
  ⓓ-20 [`resume.md`](conventions/resume.md) — **리줌 (중단/재개)** — 매우 장기간 작업 중 사용자가 webview Progress 탭으로 라이브 관찰, 중단 시 `state.json` 자동 기록, `resume.py next` 가 마지막 valid 페이즈 다음 진입점 자동 결정, 부분 산출물 자동 폐기, 무결성 깨짐 시 사용자 ack 1 회만.
  ⓓ-21 [`prd-handling.md`](conventions/prd-handling.md) — **PRD 처리 허들** — 충실한 PRD 가 입력이어도 페이즈 04 의 모든 인터뷰 항목 (Q-G1+Q-D1~D7+NFR+스택) 생략 금지. PRD 추출값은 객관식 1번 보기로, 사용자 1 클릭 확정 + `user_explicit_confirmation: true` + timestamp 강제. 인터럽트 0 약속의 *전제* 보호.
ⓔ [`scoring/rubric.md`](scoring/rubric.md) + [`scoring/score.py`](scoring/score.py) — 6 차원 채점, **임계 0.999**, **DIP 위반 단독 hard cap 0.6**.
ⓕ [`scoring/fingerprint.py`](scoring/fingerprint.py) — frontmatter 핑거프린트 계산·검증·체인 무결성.
ⓖ [`scoring/self_lint.py`](scoring/self_lint.py) + [`scoring/test_self_lint.py`](scoring/test_self_lint.py) — 본 저장소 자기 평가 19 체크 + `--score` 모드, 임계 **0.99999** (자기 표준).
ⓗ [`templates/`](templates/) — intent / plan / sprint-report / naming 템플릿 + bun 기반 webview 스캐폴드.

## 주요 원칙

ⓐ **의존성 역전(DIP) 이 SOLID 중 최우선** — 위반은 단독 hard fail.
ⓑ **관심사 분리(SoC) 가 단위 테스트 기반** — 모듈 경계를 기능보다 먼저.
ⓒ **장인의 도자기처럼** 깊은 품질 위반 (DIP/SOLID · 코드 오류 누적 · 기획-구현 갭 · 성능/NFR 미달 · 의도 표류 · 정체/회귀 누적) *어느 차원* 이라도 깊이 임계 초과면 모듈을 깨고 페이즈 06 부터 다시 빚는다 (페이즈 11 `re-architect`). 트리거 매핑은 [`conventions/lessons.md`](conventions/lessons.md) + [`conventions/checkpoints.md`](conventions/checkpoints.md) 의 11 분류.
ⓓ **모든 산출물은 파일** — `.ShipofTheseus/<프로젝트>/` 트리에 카테고리별로 떨어진다.
ⓔ **무한 스프린트 루프** — 임계 0.999 까지, 회귀 시에만 사용자 ack 로 정지.
ⓕ **시간 라이브 표시** — 매 산출물 헤더에 시작·소요·누적·현재.
ⓖ **백엔드 기본값 Go** — 사용자 명시 없을 때.
ⓗ **항상 인터랙티브 웹뷰** — 페이즈 12 가 bun 기반 be4fe + fe 6 탭 자동 생성.

## 산출물 트리 (한 프로젝트 실행 결과)

```
.ShipofTheseus/<프로젝트명>/
├── timing/start.json
├── naming/00-naming.md
├── intent/01..05*.md
├── plan/06..07*.md
├── impl/08-impl-log.md
├── quality/09-quality-gate.md
├── sprints/NN/{report.md, inputs.json, bisect.md?, unit.json, e2e.json}
├── webview/                           # bun + hono + react
└── handoff/13-handoff.md
```

## 채점 검증

```bash
python -m pytest scoring/test_score.py -q
# 11 passed
```

## 호출

Claude Code 세션에서:

```
/theseus-harness <요구사항>
```

Claude 가 [`SKILL.md`](SKILL.md) 를 읽고 페이즈 00 부터 시작한다.

## 더 읽을거리

ⓐ [`../../PHILOSOPHY.md`](../../PHILOSOPHY.md) — 신뢰 담보, 도자기 장인 비유, Ralph/OhMy/우로보로스 합성, SOLID/TDD/DDD/Hexagonal/Clean/실용주의 매핑.
ⓑ [`../../INSTALL.md`](../../INSTALL.md) — git clone 기반 설치, 플러그인 매니페스트, 트러블슈팅.
