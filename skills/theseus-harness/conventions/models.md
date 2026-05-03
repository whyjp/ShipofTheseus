# 모델 선택 컨벤션

## 한 줄 요약
**각 서브에이전트는 역할에 맞는 모델(Opus / Sonnet / Haiku) 을 호출한다** — 깊은 추론은 Opus, 일반 구현·리뷰는 Sonnet, 단순 실행·요약은 Haiku. 비용·지연·품질의 균형을 페이즈마다 의도적으로 결정.

## 모델 매핑

| 에이전트 | 페이즈 | 역할 성격 | 권장 모델 | 이유 |
| ------- | ----- | -------- | -------- | ---- |
| `project-namer` | 00 | 후보 명명·충돌 검사 | **Haiku** | 사전 lookup + 짧은 텍스트, 빠름·저렴이 가치 |
| `intent-extractor` | 01 | 의도 해석·마인드맵·엣지 발산 | **Opus** | 창의적 해석과 폭넓은 가지 발산이 핵심 |
| `doc-reviewer` | 02 | 문서 정독·일관성·인용 | **Sonnet** | 꼼꼼한 검토, 비용 대비 적절 |
| `independent-comprehender` | 03 | 콜드 리딩·자기 말로 재구성 | **Sonnet** | 표준적 텍스트 변환 |
| `clarifier` | 04 | 질문 구조화·회귀 짝 설계 | **Sonnet** | 형식·우선순위 판단 |
| `critic` | 05 | 적대적 비평·대안·아키텍처 압력 | **Opus** | 깊은 추론·대안 탐색 필요 |
| `planner` | 06 | TODO DAG·SoC·DIP·시퀀스 다이어그램 | **Opus** | 아키텍처 설계는 모델의 가장 큰 가치 |
| `plan-reviewer` | 07 | 계획 콜드 리딩 | **Sonnet** | 03 와 같은 콜드 리딩 성격 |
| `implementer` | 08 | 코드 + 테스트 + 목 표면 | **Sonnet** (default) / **Opus** (복잡 모듈) | 표준 구현은 Sonnet, 도메인 코어 등 복잡도 높은 모듈만 Opus |
| `quality-gate` | 09 | 5 게이트 감사·인용 | **Sonnet** | 코드 읽고 판정 |
| `tester` | 10 | 테스트 매트릭스 실행·결과 기록 | **Haiku** | 명령 실행과 결과 정형화 — 추론 부담 적음 |
| `regression-analyst` | 11 | 회귀 원인 추적·DIP 위반 식별·반대 가설 | **Opus** | 깊은 분석과 다중 가설 비교 |
| `webview-builder` | 12 | bun + react 스캐폴드 채우기 | **Sonnet** | 표준 프론트 코드 생성 |

## Agent 호출 시점 명시

지휘자가 서브에이전트를 띄울 때:

```
Agent(
  subagent_type="general-purpose",
  model="opus",                      # 위 표 참조
  prompt="<agents/<name>.md 의 내용 + 입력 컨텍스트>"
)
```

Agent 도구 `model` 파라미터의 허용값: `"opus"`, `"sonnet"`, `"haiku"` (생략 시 부모 세션 모델 상속).

## 비용·지연 가드

a- Opus 호출이 한 페이즈에서 3 회 이상 반복되면 (재실행 루프) 사용자에게 비용 사실 한 줄 보고.
b- Haiku 가 출력 품질 부족으로 fail 한 페이즈는 *한 번만* Sonnet 으로 escalate, 그래도 안 되면 사용자 질의.
c- 사용자가 명시적으로 "전부 Sonnet" / "전부 Opus" 지정 시 그 결정을 우선.

## 비고

a- 본 매핑은 휴리스틱 — 실제 작업의 도메인 복잡도에 따라 implementer 처럼 페이즈 안에서 모델을 선택적으로 끌어올릴 수 있음.
b- 모델 명세 변경 시 본 문서를 source of truth 로 — SKILL.md 의 페이즈 표는 본 문서를 참조.
