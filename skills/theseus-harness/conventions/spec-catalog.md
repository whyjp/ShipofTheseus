---
id: spec-catalog
category: quality
applies-to-phases: '[01,09]'
applies-to-grades: '[all]'
trigger-when: 'always'
indexed-in: conventions/INDEX.md
---

# 스펙 카탈로그 — 도메인별 NFR 자동 제안

## 한 줄 요약
**사용자가 "이거 만들어줘" 만 던져도 본 하네스가 도메인을 식별해 일반적 NFR(non-functional requirements) 임계를 자동 제안한다 — 사용자는 채택/조정만 객관식으로 답한다.** "기본값으로 OK" 라는 답도 *기본값이 무엇인지* 명시 기록 → 페이즈 09 게이트가 그 임계까지 검증.

## 왜 이 카탈로그가 필요한가

a- 사용자는 *기능* 은 잘 말하지만 *성능/가용성/보안/운영* 은 묵시적으로 둔다 — "빨라야 함" / "안 되면 곤란함" 수준.
b- 임계가 없으면 페이즈 09 의 게이트가 *정량 검증 불가* — 단순 "테스트 통과" 만 봄.
c- 도메인마다 *통상 임계* 가 있다 — 결제 API 의 p99 와 정적 사이트의 p99 는 두 자릿수 다름. 본 하네스가 그것을 알고 자동 제안하면 사용자 부담이 크게 줄어든다.
d- 임계가 산출물에 박히면 페이즈 10 의 점수 산출에 *NFR 차원* 을 추가할 수 있다 — `nfr_meets_spec` 차원 후보.

## 카탈로그 (도메인 → NFR 임계 휴리스틱)

### 결제 / 금융 / 원장
| 항목 | 권고 임계 (기본값) | 측정 |
| --- | ----------------- | ---- |
| API p99 latency | < 200ms | k6 / Vegeta E2E 부하 |
| API p50 latency | < 50ms | 동일 |
| 가용성 | 99.95% (월 21.9분 다운) | uptime 모니터 |
| 에러율 | < 0.05% | 5xx 응답 비율 |
| Idempotency | 모든 결제 요청 idempotency-key 필수 | 통합 테스트 |
| 감사 로그 | 모든 거래 (성공/실패) 7년 보존 | 로그 export |
| PII 처리 | 카드번호 토큰화, CVV 미저장 | 코드 정적 분석 |
| 트랜잭션 격리 | SERIALIZABLE 또는 명시적 보상 | DB 검증 |
| 백필 | 다운타임 0 (zero-downtime migration) | 배포 절차 |

### 일반 CRUD API
| 항목 | 권고 임계 (기본값) | 측정 |
| --- | ----------------- | ---- |
| API p99 latency | < 500ms | E2E 부하 |
| 가용성 | 99.9% (월 43.8분) | uptime |
| 에러율 | < 0.1% | 5xx 비율 |
| RPS (단일 인스턴스) | ≥ 200 RPS | 부하 테스트 |
| 페이로드 한도 | 요청 1MB / 응답 5MB | 통합 테스트 |
| 인증 | JWT 또는 세션 + CSRF | 보안 게이트 |
| Rate limit | IP당 100 req/min | 통합 테스트 |

### 검색 / 인덱스
| 항목 | 권고 임계 | 측정 |
| --- | -------- | ---- |
| 쿼리 p95 latency | < 300ms | E2E |
| 인덱스 갱신 lag | < 5분 | 모니터 |
| recall@10 | ≥ 0.85 | 평가 데이터셋 |
| 동시 쿼리 | ≥ 1000 QPS | 부하 |

### 실시간 / 메시징 / 알림
| 항목 | 권고 임계 | 측정 |
| --- | -------- | ---- |
| 전송 latency p99 | < 1s | E2E |
| 손실율 | < 0.001% | 메트릭 |
| 순서 보장 | per-key FIFO | 통합 테스트 |
| At-least-once / exactly-once | 명시 | 설계 |
| 백프레셔 | 큐 depth 임계 + drop 정책 | 통합 |

### ML / inference
| 항목 | 권고 임계 | 측정 |
| --- | -------- | ---- |
| inference p99 | < 1s (서빙) / < 100ms (실시간) | 부하 |
| GPU 메모리 ceiling | 모델 크기 × 1.5 | 프로세스 메트릭 |
| 정확도 | 사용자 명시 (도메인별) | 평가 셋 |
| 모델 버전 관리 | semver + 태그 + 롤백 절차 | 배포 |
| Cold start | 첫 요청 < 30s | 모니터 |

### 프론트엔드 (웹)
| 항목 | 권고 임계 | 측정 |
| --- | -------- | ---- |
| LCP (Largest Contentful Paint) | < 2.5s | Lighthouse |
| FID (First Input Delay) | < 100ms | Lighthouse |
| CLS (Cumulative Layout Shift) | < 0.1 | Lighthouse |
| TTI (Time to Interactive) | < 3.5s | Lighthouse |
| 번들 크기 (initial) | < 200KB gzip | 빌드 분석 |
| 접근성 | WCAG 2.1 AA | axe-core / Lighthouse |
| i18n | 텍스트 외부화, 동적 로케일 | 코드 검토 |

### 모바일 (네이티브 / 하이브리드)
| 항목 | 권고 임계 | 측정 |
| --- | -------- | ---- |
| 앱 cold start | < 2s | profiler |
| 화면 전환 | < 200ms | profiler |
| 배터리 영향 | 백그라운드 < 1%/h | 시뮬레이션 |
| 메모리 ceiling | 폰 RAM 의 5% | profiler |
| 오프라인 동작 | 핵심 흐름 70% 가능 | 통합 |

### 운영 (모든 백엔드 공통)
| 항목 | 권고 임계 | 측정 |
| --- | -------- | ---- |
| MTTR (mean time to repair) | < 30분 | 인시던트 기록 |
| RTO (recovery time obj) | < 1시간 | 재해 복구 훈련 |
| RPO (recovery point obj) | < 5분 (백업 주기) | 백업 정책 |
| 옵저버빌리티 — 메트릭 | RED (Rate, Errors, Duration) 기본 | Prometheus 등 |
| 옵저버빌리티 — 로그 | 구조화 (JSON) + 추적 ID | 코드 검토 |
| 옵저버빌리티 — 트레이스 | OpenTelemetry, 5% 샘플링 | 통합 |
| 알람 | error budget 25% 소진 시 | 알람 정책 |
| Error budget | SLO 99.9% 면 월 0.1% (43.8분) | SLO 문서 |
| 시크릿 관리 | 환경 변수 + .env.example, 보관소 (Vault/SSM) | 코드 검토 |
| 키 회전 | 90일 | 운영 절차 |

### 보안 (도메인 무관 공통)
| 항목 | 권고 임계 | 측정 |
| --- | -------- | ---- |
| OWASP Top 10 | 정기 점검 통과 | SAST/DAST |
| 의존성 취약점 | High 0건, Critical 0건 | Snyk/Dependabot |
| 비밀번호 정책 | bcrypt/argon2, salt 자동 | 코드 검토 |
| 세션 만료 | idle 30분, absolute 24h | 인증 모듈 |
| HTTPS only | HSTS preload | 헤더 검증 |
| 감사 로그 | 인증/권한/금융 이벤트 모두 | 로그 검토 |

## 지휘자(메인 에이전트)의 자동 제안 흐름

페이즈 01 (의도 추출) 직후, intent-extractor 가 다음 분석:

1- 사용자 원문에서 도메인 키워드 추출 — "결제", "검색", "알림", "로그인", "관리자", "지도", ...
2- 본 카탈로그에서 매칭되는 도메인 NFR 표 1~3 개 선택 (예: 사용자 요청이 "결제 API + 관리자 웹뷰" 면 결제 + 일반 CRUD + 운영 + 보안 + 프론트엔드 5표).
3- 각 NFR 항목에 대해 *권고 임계* 를 채워 `intent/01-intent.md` 의 "성능/스펙" 표에 기록.
4- 각 항목 옆에 `proposed: true` 마크 — 사용자 확정 전 임시값.

## 페이즈 04 (사용자 질의) 의 NFR 확정

clarifier 가 위 표를 받아, 항목별로 [`interview.md`](interview.md) 컨벤션의 객관식 4 보기 생성:

```
질의: 결제 API 의 p99 latency 임계를 정해주세요.

본 하네스의 결제 도메인 카탈로그 권고는 < 200ms 입니다. 더 빡빡 (예: 100ms) 또는 완화 (예: 500ms) 도 선택 가능. 임계는 페이즈 10 의 성능 게이트에 자동 반영됩니다.

선택지:
1. 카탈로그 권고 채택 (< 200ms)
2. 더 빡빡 (< 100ms — 카드 거절 직후 재시도가 흔한 도메인)
3. 완화 (< 500ms — 비동기 보상 흐름 우선)
4. NFR 미확정 — 페이즈 09 에서 게이트 자동 비활성화
```

답이 **4 (미확정)** 이면 그 NFR 은 게이트 9 의 비교 항목에서 제외 — 단 산출물에 "측정 안 함" 으로 명시 기록.

## 산출물 형식 — `intent/01-spec.md` (또는 01-intent 의 "성능/스펙" 섹션)

```markdown
## 성능 / 스펙 (NFR)

도메인 매칭: 결제 / 일반 CRUD / 운영 / 보안 / 프론트엔드

| 도메인 | 항목 | 임계 | 사용자 확정 | 측정 | 게이트 |
| ----- | ---- | ---- | ---------: | ---- | ------ |
| 결제 | API p99 latency | < 200ms | ✅ (옵션 1, 카탈로그 권고) | k6 부하 | 페이즈 10 |
| 결제 | 가용성 | 99.95% | ✅ (옵션 1) | uptime 모니터 | 운영 |
| 결제 | Idempotency | 필수 | ✅ (옵션 1) | 통합 테스트 | 페이즈 09 |
| 운영 | 옵저버빌리티 메트릭 | RED 기본 | ⏸ (미확정 — 게이트 비활성화) | n/a | n/a |
| FE | LCP | < 2.5s | ✅ (옵션 1) | Lighthouse | 페이즈 10 |
| 보안 | 의존성 High 0 | 0 | ✅ (옵션 1) | Snyk | 페이즈 09 |

## 사용자 결정 이력
- 2026-05-01 18:42:11 — 결제 카탈로그 5/5 항목 채택 (모두 권고)
- 2026-05-01 18:42:55 — 운영 옵저버빌리티 미확정 (사용자: "다음 회차로 이월")
```

## 페이즈 09 (품질 게이트) 통합

`agents/quality-gate.md` 의 5 게이트 외에 **게이트 6 — NFR 일치** 추가 가능:

a- `intent/01-spec.md` 의 ✅ 항목별로 페이즈 10 의 측정 결과 비교.
b- 임계 미달이면 게이트 6 fail.
c- ⏸ (미확정) 항목은 자동 skip.

새 차원 `nfr_meets_spec` 을 [`../scoring/rubric.md`](../scoring/rubric.md) 에 후속 PR 로 추가 가능 — v0.3.0 후보.

## 리소스 기반 임계 조정 (성능 지향 default)

본 카탈로그는 *도메인* 기반 권고 임계만 제공. 실제 NFR 임계는 *그 리소스에서 가능한 천정* 까지 빡빡하게 잡아야 한다 — [`resources.md`](resources.md) 의 프로파일별 추정 천정 표 참조. 본 하네스 default 는 **성능 지향 모드** — 리소스 천정의 80% 를 임계로 자동 권고.

예: 결제 도메인 + AWS EC2 t3.medium (CRUD write 보정 0.6) →
- 카탈로그 권고: p99 < 200ms
- 리소스 추정 천정: 150ms × 0.6 = 90ms... 잠깐, latency 는 보정 X (RPS만 보정). t3.medium 의 p99 천정은 150ms.
- 성능 지향 권고: p99 < 120ms (천정 80%)

페이즈 10 측정 시 천정 90% 이상 도달 + 변동 안정이면 [`resources.md`](resources.md) 의 자동 조정 권고가 사용자에게 객관식 4 보기로 전달 (임계 채택 / 리소스 업그레이드 / 도메인 단순화 / 정체 수용).

## 자동 제안의 신뢰도

a- 카탈로그는 *휴리스틱* — 도메인별 통상값. 모든 프로젝트에 들어맞지 않음.
b- 사용자가 옵션 4 (미확정) 또는 자유 응답으로 다른 임계를 선택할 수 있다.
c- 카탈로그 자체도 시간 흐름에 따라 갱신 — 매 자기 평가 회차에서 *새 도메인이 등장* 하면 추가.
d- 본 카탈로그가 강제 룰이 아닌 *제안* 임을 명시 — 비평가(critic) 가 도메인 부적합 시 다른 임계 제안 가능.

## 카탈로그 갱신 정책

a- 새 도메인 추가는 PR — 본 컨벤션 자체가 deprecation policy 의 대상.
b- 기존 임계 변경 시 changelog (예: `docs/changes/2026-NN-spec-catalog.md`) 에 사유 + 측정 데이터 첨부.
c- 카탈로그 보강 회차는 자기 평가의 한 책임 — `BOOTSTRAP.md` 의 회차 시계열에 카탈로그 변경 흔적 누적.

## 안티 패턴

a- 사용자에게 NFR 임계를 묻지 않고 *암묵 가정* 으로 진행 — 페이즈 09 가 측정할 기준 부재.
b- 카탈로그 임계를 *사용자 동의 없이* 게이트로 적용 — 자율 결정의 범위 초과 (autonomy.md 의 사용자 ack 필요 케이스).
c- 모든 도메인에 일률적 임계 적용 — 결제 API 와 검색 API 의 p99 가 같을 수 없다.
d- NFR 미확정인데도 게이트 6 를 fail 처리 — ⏸ 항목은 skip, fail 아님.

---

## 도메인별 interactive-viewer dashboard 카탈로그 (페이즈 13)

페이즈 13 ([`../phases/13-interactive-viewer.md`](../phases/13-interactive-viewer.md)) 의 interactive-viewer 가 도메인 식별 후 아래 매트릭스에서 default dashboard 를 선택한다. observability 목적 — 프로젝트 결과를 도메인 특성에 맞게 시각화.

| 도메인 | default dashboard |
|---|---|
| DES (시뮬레이션) | scenario throughput bar + bottleneck heatmap + truck cycle gantt |
| 데이터 ETL/스트리밍 | flow diagram + batch progress + record count over time + schema drift |
| ML | metric curves (loss/accuracy) + confusion matrix + feature importance + sample drift |
| 분석 | key metric dashboard + drill-down view + cohort comparison |
| REST API | endpoint latency p50/p95/p99 + error rate + RPS over time + status code distribution |
| Frontend | screen tree + component metric + Lighthouse score + bundle size |
| (도메인 미매칭) | 단순 결과 JSON pretty + 1 summary plot |

### 선택 기준

1- 페이즈 01 의도 추출 시 도메인 키워드 식별 (NFR 카탈로그 도메인 매칭과 동일 흐름).
2- Q-D4 답으로 도메인 확정 — "Skip" 시에도 카탈로그 매칭이 있으면 최소 1 plot 자동 emit.
3- 도메인 완전 미매칭 시 페이즈 13 skip 허용 — handoff(페이즈 14) 에 사유 기록 의무.
4- 도메인 2개 이상 매칭 시 모든 도메인 dashboard 병렬 emit.

### NFR 카탈로그와의 관계

본 절의 dashboard 카탈로그는 *결과 시각화* 용, 위 NFR 카탈로그는 *성능 임계 제안* 용 — 목적이 다르나 도메인 분류 체계는 동기화한다. 새 도메인 추가 시 두 카탈로그 모두 갱신 의무.
