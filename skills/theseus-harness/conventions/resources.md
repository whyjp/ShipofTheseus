---
id: resources
category: core
applies-to-phases: '[10]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# 리소스 기반 NFR 임계 — 천정 감지와 자동 조정

## 한 줄 요약
**임계는 추상적 "빨라야 함" 이 아니라 *그 리소스에서 가능한 천정* 기준으로 정해진다.** 본 하네스는 로컬 PC / K8s pod / AWS EC2 인스턴스 별 NFR 추정치 표를 가지고, 사용자 환경에 맞춰 빡빡한 성능 지향 임계를 자동 제안한다. 시도 과정에서 측정값이 추정 천정의 90% 이상에 도달하면 더 개선 불가능 신호로 판단해 임계를 자동 조정하고 사용자에게 사유와 함께 알린다.

## 왜 이 컨벤션이 필요한가

a- **추상 임계의 함정** — `p99 200ms` 라는 약속이 t3.micro 에서는 불가능, c5.xlarge 에서는 너무 느슨. 리소스 명시 없으면 의미 없음.
b- **성능 포기 방지** — 처음부터 성능 지향으로 가도, 천정에 닿으면 *합리적으로* 완화해야 무한 정체 막을 수 있다 ([`lessons.md`](lessons.md)).
c- **자율 조정** — 사용자가 매번 "이 임계 안 되네 좀 풀어줘" 할 필요 없이, 본 하네스가 측정값과 추정 천정을 비교해 *자동으로* 권고.

## 리소스 프로파일별 NFR 추정치 (Go API 기준)

다음 표는 **단순 read-heavy CRUD API** (DB 한 번 조회, JSON 응답) 의 추정치. 도메인 무거움 (예: ML inference, 결제 검증) 은 추정치를 절반 이하로 보정.

### 로컬 PC (개발 환경)

| 프로파일 | CPU | RAM | 추정 RPS 천정 | p99 latency 천정 | p50 latency 천정 |
| ------- | --- | --- | -----------: | --------------: | --------------: |
| 저사양 노트북 (4코어 / 8GB) | 4 vCPU | 8GB | 800 RPS | 80ms | 15ms |
| 표준 데스크톱 (8코어 / 16GB) | 8 vCPU | 16GB | 2500 RPS | 50ms | 8ms |
| 고사양 워크스테이션 (16코어 / 32GB) | 16 vCPU | 32GB | 6000 RPS | 30ms | 5ms |
| Apple Silicon M2/M3 (8코어 / 16GB) | 8 vCPU | 16GB | 4000 RPS | 35ms | 6ms |

### K8s Pod (단일 인스턴스)

| 프로파일 | CPU request | RAM request | 추정 RPS 천정 | p99 천정 |
| ------- | ----------: | ----------: | -----------: | -------: |
| small | 250m | 256Mi | 300 RPS | 150ms |
| medium | 500m | 512Mi | 700 RPS | 100ms |
| large | 1000m | 1Gi | 1500 RPS | 70ms |
| xlarge | 2000m | 2Gi | 3000 RPS | 50ms |

### AWS EC2 (단일 인스턴스, gp3 SSD, 같은 AZ DB)

| 프로파일 | vCPU | RAM | 추정 RPS 천정 | p99 천정 | 시간당 비용 (us-east-1, 2026) |
| ------- | ---: | --: | -----------: | -------: | ----------------------------: |
| t3.micro | 2 | 1GB | 200 RPS | 250ms | $0.0104 |
| t3.small | 2 | 2GB | 400 RPS | 200ms | $0.0208 |
| t3.medium | 2 | 4GB | 700 RPS | 150ms | $0.0416 |
| t3.large | 2 | 8GB | 1200 RPS | 120ms | $0.0832 |
| c5.large | 2 | 4GB | 1500 RPS | 80ms | $0.085 |
| c5.xlarge | 4 | 8GB | 3500 RPS | 50ms | $0.17 |
| c5.2xlarge | 8 | 16GB | 7500 RPS | 35ms | $0.34 |
| m5.large | 2 | 8GB | 1300 RPS | 90ms | $0.096 |
| m5.xlarge | 4 | 16GB | 3000 RPS | 60ms | $0.192 |

### 클라우드 컨테이너 (Lambda / Cloud Run / Fargate)

| 프로파일 | 메모리 | 추정 RPS 천정 | p99 천정 | cold start |
| ------- | ----: | -----------: | -------: | ---------: |
| Lambda 256MB | 256MB | 200 RPS (provisioned 1k) | 200ms | 800ms |
| Lambda 1024MB | 1024MB | 800 RPS | 80ms | 600ms |
| Cloud Run 1vCPU/512MB | 1 | 600 RPS | 100ms | 500ms |
| Fargate 0.5vCPU/1GB | 0.5 | 300 RPS | 150ms | n/a (warm) |

## 성능 지향 모드 (default ON)

[`spec-catalog.md`](spec-catalog.md) 의 도메인별 권고 임계 위에 **본 표의 RPS/latency 천정의 80%** 를 *목표 임계* 로 자동 제안. 즉 t3.medium 에서 CRUD API 면:

a- 카탈로그 권고: p99 < 500ms.
b- 리소스 천정: 150ms.
c- 성능 지향 권고 (천정 80%): **p99 < 120ms**.

사용자가 페이즈 04 에서 4개 객관식 중 선택:

```
질의: t3.medium 의 추정 p99 천정 150ms. 임계를 어디에 둘까요?

성능 지향 모드는 천정의 80% (120ms) 를 권고합니다. 카탈로그 권고는 도메인 안전치 (500ms) 입니다. 빡빡한 임계는 회귀 감지를 빠르게 하지만 천정에 가까울수록 변동에 취약.

선택지:
1. 성능 지향 (120ms — 천정 80%, 본 하네스 default)
2. 카탈로그 권고 (500ms — 도메인 일반)
3. 천정에 더 가깝게 (140ms — 천정 93%, 측정 변동에 취약)
4. 직접 입력
```

## 천정 감지 알고리즘

```python
def detect_ceiling(
    measurements: list[float],     # 직전 N 스프린트의 측정값
    threshold: float,               # 현재 임계
    estimated_ceiling: float,       # 리소스 프로파일 기반 추정 천정
    window: int = 3,
    ceiling_pct: float = 0.90,
    spread_eps: float = 0.05,
) -> CeilingReport:
    """
    천정 도달 신호:
      - 직전 N 측정값이 추정 천정의 ceiling_pct 이상
      - 측정값 분산이 spread_eps 이내 (이미 안정됨)
      - 임계 미달 (그렇지 않으면 조정 불필요)
    """
    if len(measurements) < window:
        return CeilingReport(near_ceiling=False)
    recent = measurements[-window:]
    avg = sum(recent) / window
    spread = max(recent) - min(recent)

    near = (
        avg >= estimated_ceiling * ceiling_pct
        and spread / avg < spread_eps
        and avg > threshold              # 임계 미달 시에만 조정 검토
    )

    if not near:
        return CeilingReport(near_ceiling=False, avg=avg)

    # 권고 임계 = 안정 측정값의 105% (5% 안전 여유)
    recommended = round(avg * 1.05, 2)
    return CeilingReport(
        near_ceiling=True,
        avg=avg,
        spread=spread,
        ceiling_pct_actual=avg / estimated_ceiling,
        recommended_threshold=recommended,
        reason=(
            f"3 스프린트 평균 측정 {avg:.0f}ms 가 추정 천정 "
            f"{estimated_ceiling}ms 의 {avg/estimated_ceiling*100:.0f}% — "
            f"개선 불가능 신호. 임계 → {recommended}ms (안전 여유 5%) 권고."
        ),
    )
```

## 자동 임계 조정 흐름 (페이즈 10 통합)

```
sprint = 1
while True:
    measurements = run_perf_test()
    if measurement_passes_threshold:
        continue_to_next_sprint()
        continue

    # lessons.md 의 정체 감지
    if stagnation.detect(...):
        # 천정 검토 (resources.md)
        ceiling = detect_ceiling(
            measurements_history[dim],
            threshold=current_threshold,
            estimated_ceiling=resource_profile_ceiling[dim],
        )
        if ceiling.near_ceiling:
            # 자동 적용 — autonomy.md 의 Q-D3 사전 위임 답 매핑
            policy = autonomy_policy["Q-D3"]   # intent/04-autonomy.md 의 답
            if policy == "1":
                # 권고 임계로 자동 조정 (default)
                set_threshold(ceiling.recommended_threshold)
                report_live("천정 도달 → 임계 자동 조정")
            elif policy == "2":
                # 리소스 업그레이드 자동 (사용자 결제 사전 동의 시)
                upgrade_resource_profile()
            elif policy == "3":
                # 도메인 단순화 자동 시도
                spawn_implementer_with_simplification_directive()
            elif policy == "4":
                # 정체 수용 — 게이트 영구 fail, 다음 페이즈 진행
                disable_gate(dim)
            # 모든 경우 인터럽트 없음 — 사전 위임 답이 곧 답
        else:
            # 천정 아님 → lessons.md 의 rewrite 트리거 (Q-D4 매핑)
            spawn_implementer_with_rewrite_rule()
```

## 도메인 무거움 보정

본 표는 *단순 CRUD* 기준. 도메인이 무거우면 추정치를 보정:

| 도메인 | 보정 계수 | 사유 |
| ------ | -------: | ---- |
| 단순 CRUD (read) | 1.0 | 기준 |
| CRUD (write + 트랜잭션) | 0.6 | DB 잠금 |
| 결제 (외부 PG 호출) | 0.3 | 외부 latency 종속 |
| 검색 (Elasticsearch) | 0.5 | 인덱스 hit 분산 |
| ML inference (CPU) | 0.1 | 모델 추론 무거움 |
| ML inference (GPU) | 0.4 | GPU 가용 시 |
| 실시간 메시징 | 0.7 | 큐잉 오버헤드 |
| 정적 + 캐시 hit | 5.0 | 메모리만 — 천정 더 높음 |

예: t3.medium 의 단순 CRUD 천정이 700 RPS 라면 결제 도메인 추정 천정은 **210 RPS** (0.3 보정).

## 리소스 프로파일 결정 (페이즈 04)

[`interview.md`](interview.md) 컨벤션으로 사용자에게 객관식:

```
질의: 본 프로젝트의 *주 운영 환경* 은 어디입니까?

성능 임계가 이 답에 따라 자동 조정됩니다. 개발 환경과 운영 환경이 다르면 운영 환경 기준.

선택지:
1. 로컬 PC / 워크스테이션 (CPU 코어 수와 RAM 알려주세요)
2. AWS EC2 (인스턴스 타입 알려주세요)
3. K8s 클러스터 (pod CPU/RAM request 알려주세요)
4. 서버리스 (Lambda / Cloud Run / Fargate)
5. 다른 클라우드 (Azure / GCP) — 카탈로그에 없는 경우 직접 입력
```

답을 `intent/04-resource-profile.md` 에 기록. 후속 페이즈가 본 프로파일을 입력으로 받음.

## 산출물 — `intent/04-resource-profile.md`

```markdown
# 리소스 프로파일 — 합의

| 항목 | 값 | 비고 |
| --- | -- | ---- |
| 환경 | AWS EC2 | 페이즈 04 답 옵션 2 |
| 인스턴스 | t3.medium | vCPU 2, RAM 4GB |
| DB | RDS PostgreSQL t3.small | 같은 AZ |
| 도메인 보정 | 0.6 (CRUD write 위주) | 자동 |
| **추정 RPS 천정** | **420 RPS** | 700 × 0.6 |
| **추정 p99 천정** | **150ms** | 표준 |
| **성능 지향 임계 (천정 80%)** | **RPS ≥ 336, p99 < 120ms** | default |

## 사용자 결정 이력
- 2026-05-01 18:50:11 — t3.medium 채택 (옵션 2)
- 2026-05-01 18:50:33 — 성능 지향 모드 ON (옵션 1, default)
```

## 안티 패턴

a- 리소스 명시 없이 임계 약속 — 측정 시점에 의미 없음.
b- 성능 지향 임계인데 *천정의 95% 이상* 으로 잡음 — 변동에 즉시 fail, 빡빡함이 고통이 됨. 권고는 80%.
c- 천정 도달 후 *임계 조정 없이* 무한 시도 — 본 컨벤션 위반, [`lessons.md`](lessons.md) 의 정체와 같이 자동 조정 권고로 빠져나가야.
d- 인터뷰 종료 후 임계 변경에 사용자 ack 호출 — [`autonomy.md`](autonomy.md) 의 핵심 룰 위반 (인터뷰 후 인터럽트 0). 임계 변경은 페이즈 04 의 Q-D3 사전 위임 답에 따라 자율 적용.
e- 도메인 보정 무시 — ML inference 에 단순 CRUD 천정 적용하면 너무 빡빡.

## Opt-In 보조 천정 — wall-clock + token + bounded iteration (v0.4.0 신규)

> **거울 원칙 차용** — ralph (`.ralph/run.sh` wall-clock cap) + autoresearch (`Iterations: N`) 의 *직교 차원* 차용. 본 하네스는 `stop_policy`(설계 B2 §2.2 — 게이트 pass AND 무회귀 AND (plateau OR budget≥95%)) 신호가 있는 동안 스프린트를 계속하는 것이 기본이지만, *외부 운영 환경* (CI 시간 한도 / API 토큰 budget / 자동화 회차 cap) 에서 *기본 활성* 은 컨셉 충돌이므로 **기본 비활성 + opt-in** 으로 차용.

### 컨셉 충돌 명시

본 하네스는 *도자기 장인의 깨고 다시 빚기* 메타포 — 시간이 다 됐다고 *부족한 품질로 정지* 하는 건 본 하네스의 핵심 정신과 정반대. 따라서 본 절의 보조 천정 활성은 *외부 환경 강제* 일 때만 정당.

### 활성 조건 (모두 만족 시 활성)

a- Q-D3 (천정 도달) 답이 sub-option `1-aux` 또는 `2-aux` ([`autonomy.md`](autonomy.md)).
b- `.ShipofTheseus/<프로젝트>/config.toml` 에 다음 키가 *명시* 존재:

```toml
[supplementary_ceiling]
enabled = true                # 기본 false — 명시 true 만 활성
max_wall_clock_minutes = 90   # 권고 60~90, 0 이면 비활성
max_total_tokens = 1000000    # 권고 100k~10M, 0 이면 비활성
max_sprint_iterations = 10    # 권고 5~20, 0 이면 비활성
on_breach = "checkpoint"      # checkpoint | abort | ack-and-continue
```

c- 본 하네스 호출 직전 사용자가 위 config 를 *생성/편집* — 호출 도중 변경은 무시.

### 천정 도달 시 동작 (`on_breach`)

| 값 | 동작 |
|--|--|
| `checkpoint` (default) | 현 sprint 완료 시 [`checkpoints.md`](checkpoints.md) 의 `partial-completion` 체크포인트 자동 생성 + 핸드오프 진입 |
| `abort` | 즉시 종료 (Phase 13 핸드오프 직행) |
| `ack-and-continue` | autonomy 위배라 *비권장* — Q-D6 답이 1 (라이브 보고) 일 때만 허용 |

### 본 컨벤션의 자기 가드

a- self_lint C39 — 본 절의 *기본 비활성* 명시 + *컨셉 충돌* 명시 + Q-D3 sub-option 흡수 명시 일관성 검증.
b- 본 보조 천정은 *stop_policy 의 대체 아님* — plateau/게이트 미충족 + 시간 도달 시 `partial-completion` 으로 마킹되어 *후속 회차의 입력* 으로만 사용.

## universe N 병렬 budget profile (sprint-05-b → sprint-13 v0.9.19 격상)

플랜-트리 폭 확장 (G3 폭 5 / G4 폭 7 / G5 폭 9, 옵션 default G3=10/G4=12/G5=16) → 동시 N planner sub-agent + N implementer sub-agent. 본 절은 *병렬 universe 메모리 가드* 와 *wall-clock budget* 을 정의해 OS OOM / 타임아웃 자율 회피.

### 병렬 universe 메모리 가드

| Grade | 동시 universe 수 (폭 default) | universe parallel cap (옵션 default) | 메모리 가드 | 회피 동작 |
|----|:-:|:-:|----|----|
| G3 | 5 (← 3) | 10 | 합 ≤ machine RAM × 40% | 초과 시 sequential fallback (1 universe 씩) + `fallback_reason` |
| G4 | 7 (← 4) | 12 | 합 ≤ machine RAM × 50% | 초과 시 폭 축소 (7→5→4) + lessons 기록 + `fallback_reason` |
| G5 | 9 (← 6) | 16 | 합 ≤ machine RAM × 60% | 초과 시 폭 축소 (9→7→5) + checkpoint + `fallback_reason` |

폭 default 격상 사유 — [`multiverse-width-default-bump.md`](multiverse-width-default-bump.md) (bc) sprint-13 spread default. budget-aware-fallback 의 fallback_reason frontmatter 의무.

측정 명령 (페이즈 06 진입 직전 자동 실행) :
```bash
python scoring/resource_ceiling.py --check-multiverse-memory --universe-count 3 --grade G3
```

### wall-clock budget per universe

| Grade | 폭 default | 페이즈 06 (planner) budget per universe | 페이즈 08 (implementer) budget per universe |
|----|:-:|----|----|
| G3 | 5 | 4 분 (← 5) | 12 분 (← 15) |
| G4 | 7 | 6 분 (← 8) | 16 분 (← 20) |
| G5 | 9 | 8 분 (← 10) | 20 분 (← 25) |

폭 ↑ 시 per-universe 시간 ↓ (병렬 wall-clock 보존). 각 universe 의 budget 초과 시 부분 산출물 + `<!-- budget-truncated -->` 태그.

전체 wall-clock = max(per-universe) (병렬) + tournament resolve overhead (~3 분). 토큰 = sum(per-universe).

### budget 초과 시 자율 처리

a- per-universe budget 초과 → 해당 universe 의 부분 산출물 + `<!-- budget-truncated -->` 태그, 다른 universe 는 진행. tournament resolve 시 부분 universe 는 weight 절반.
b- 전체 wall-clock budget 초과 → 가장 빠른 N-1 universe 결과로 머지, 마지막 universe drop. handoff/14 에 기록.

### a 케이스 retro

simulation-bench 베이스라인 (G3 폭 2, sprint-05-a 직전 default) → 폭 2 × 평균 5분 = 10분, 8 트럭 simulation 4.9s × 180 reps = 15분. wall-clock 총 ~25분 (45 분 budget 안전). 폭 3 으로 확장 (sprint-05-b default) → 총 ~30 분 추정 (여전히 45분 cap 안).
