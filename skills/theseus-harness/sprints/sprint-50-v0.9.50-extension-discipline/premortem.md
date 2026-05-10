# Sprint-50 — Premortem (망설임 1 회) — v0.9.50

> `premortem-friction.md` 컨벤션 정합. 페이즈 02 / 03 / 07 의 cold reread 정신을 sprint 본 의도에도 적용 — *forward simulation* + *derived improvements* 도출. 멈춤 아니라 *한 번 더 고민*.

---

## 1. 격언 — 동·서 1 개씩

### 동
> **不患寡而患不均** (논어 — 季氏 16-1)
>
> "적음을 걱정하지 말고, 고르지 않음을 걱정하라."
>
> *해석*: 본 sprint 의 본질은 *의도가 적은 게 아니라* — 의도의 *형질이 한 쪽 (프롬프트 충실 이행) 으로 쏠려* 있다는 것. extension 은 *양적* 추가가 아니라 *질적 균형* 회복이다. **만점 = 천정** 이 아니라 **균형 = 만점**. 91 plateau 가 *부족함의 결과* 가 아니라 *치우침의 결과* 임을 직시하면, 본 sprint 의 PR-B (Phase 1.5) 는 단순 추가 단계가 아니라 *이미 무너져 있던 균형* 을 회복하는 단계.

### 서
> **"The greatest enemy of a good plan is the dream of a perfect plan."**
> — *Carl von Clausewitz* (변형, *On War* 의 정신)
>
> *해석*: 본 sprint 의 reach 는 *7 PR 모두 완벽한 enforcement* 가 아니라 *다음 cold session 에서 한 차원이라도 측정 가능하게 움직이는 것*. dogfood 한계 (`feedback_self_eating_dogfood.md`) 정합 — 본 sprint 의 검증은 *본 sprint 자체* 가 아니라 *다음 회차*.
>
> 따라서 본 sprint 의 *기준* = 모든 CLI 가 *완벽한 휴리스틱* 일 필요 없다. *측정 가능 + reproducible* 이면 된다. (특히 `comment_intent_check.py` 같은 NLP-grade 휴리스틱은 *false positive 일부 허용 + sentinel marker `# why:` 명시 escape* 두기.)

---

## 2. Forward Simulation — *3 시나리오*

### 2-1. 낙관 (BEST) — *본 sprint 가 진짜로 천정을 깬다*

| 단계 | 결과 |
|---|---|
| g4-v4 cold session | Phase 1.5 hidden-intent 5+ 항목 emit. 그 중 1 should = "sensitivity sweep on truck inter-arrival" 채택. |
| Phase 06 universe-1/2/3 = modular / event-driven / data-driven (philosophy distinct PASS) | universe-2 가 winner — *기존 modular 가 항상 이기던 패턴* 깨짐. plan tournament 의 진짜 다양성 |
| Phase 08 deep-module — model.py 338 → 분리 (3 모듈) | _choose_loader 의 hidden state realtime queue 검토 → **Code quality 9/10 → 10/10** |
| 외부 Opus 평가 | **94 → 96 또는 97** (Experimental +1 / Conceptual +1 / Code quality +1) |

**Best case: 95 (v0.9.44 역대 최고) 갱신.**

### 2-2. 중도 (LIKELY) — *반쯤 효과*

| 단계 | 결과 |
|---|---|
| Phase 1.5 emit ✅ but extension-trace 가 plan/impl 에 도달하지 않음 (extension_to_artifact_trace.py warn but not fail) | hidden intent 가 도큐먼트 레벨로만 머무름 |
| Phase 06 universe philosophy distinct = 형식적으로 충족 (modular / oop / functional 3 개) but *실제 winner 는 modular 가 또* | tournament 가 사실상 modular 만 깊이 다듬음 |
| Phase 08 deep-module — 모듈 수 동일, interface/internal 비율만 개선 | LOC 거의 동일, 외부 평가 영향 미미 |
| 외부 Opus 평가 | **91 → 92 또는 93** (Experimental +1 / Code quality 동일) |

**Likely case: plateau 1-2pt 상승. 천정 돌파 X. 다음 sprint-51 후속 의제로 design philosophy *winner* 강제 추가 검토.**

### 2-3. 비관 (WORST) — *enforcement 가 작동 안 함*

| 단계 | 결과 |
|---|---|
| Phase 1.5 산출물은 emit 되지만 ≥5 항목이 *프롬프트 paraphrase* — `hidden_intent_originality.py` 가 휴리스틱 fail (token-overlap 임계 ≤ τ 통과 못함) | agent 가 PASS 하기 위해 *겉으로 다른 표현* 만 추가, 의미는 동일 |
| Phase 06 universe philosophy 가 *이름만 다르고 코드는 동일* | universe_philosophy_distinct.py PASS but *실질적 다양성 0* |
| Phase 08 deep-module CLI 가 너무 빡빡 → agent 가 *모든 모듈을 1 파일로 합침* (모듈 0 = vacuously PASS) | 휴리스틱 우회 |
| 외부 Opus 평가 | **91 → 88-90** (regression — agent 가 metric 만 맞추느라 본질 훼손) |

**Worst case: Goodhart's law (when a measure becomes a target, it ceases to be a good measure). 본 sprint 가 metric-gaming 으로 변질.**

---

## 3. Derived Improvements — *worst case 회피 위한 본 sprint 내 보강*

worst case 의 risk = *agent 가 metric 만 맞추고 본질 훼손*. 이건 본 sprint *내부* 에서 미리 막는다:

### 3-1. PR-B `hidden_intent_originality.py` 의 *2 단 휴리스틱*

- 1 단 (token-overlap): hidden intent 항목과 prompt 의 token overlap ≤ τ
- **2 단 (semantic novelty)**: hidden intent 가 *프롬프트의 5 자연 카테고리* (data / topology / scenario / metrics / constraints) 외 카테고리 ≥1 개 다룸 (sentinel grep — e.g. `validation` / `sensitivity` / `non-functional` / `domain-modeling` / `risk` 등 catalog).
- 2 단 둘 다 PASS 일 때만 OK. *paraphrase escape 차단*.

### 3-2. PR-C `universe_philosophy_distinct.py` 의 *코드 비교 강제*

- universe meta.md 의 declared philosophy 만 비교하면 worst case 우회 가능.
- 추가 검사: universe N 의 `06-plan.md` 본문에서 ≥3 architectural 결정 추출 (e.g. 모듈 경계 / 통신 방식 / 상태 관리 / 에러 모델) → universe 간 결정 distinct ≥ ⌈N/2⌉ 의무.
- 이름만 다른 universe ≥2 = fail.

### 3-3. PR-D `deep_module_metric.py` 의 *vacuous PASS 차단*

- 모듈 수 = 1 (전체 1 파일) = automatic fail (vacuous PASS 차단).
- 모듈 수 ≥ ⌈sqrt(LOC/100)⌉ 의무 — LOC 1000 = 모듈 ≥ 4.
- *낮은 모듈 수 + 깊은 모듈* = OK / *낮은 모듈 수 + 단일 모듈 회피* = fail.

### 3-4. PR-E `comment_intent_check.py` 의 *sentinel escape*

- comment 가 *paraphrase* 인지 *WHY* 인지 휴리스틱은 false positive 가능.
- escape: comment 가 `# why:` 또는 `// why:` 또는 한국어 `# 이유:` prefix 면 강제 OK (의도 명시 marker).
- prefix 비율 *cap* — 전체 comment 중 prefix escape 가 ≥80% = "전부 escape 만 사용" → 의심 fail (comment 의 *진짜 의도* 가 아닌 우회 의심).

### 3-5. PR-F refactor-not-rewrite 의 *git-blame 기반 측정*

- *변경* 비율 = sprint loop 동안 modified-but-not-deleted 줄 수 / 신규 추가 줄 수
- 측정 방식: `git diff --stat sprint-loop-start..HEAD` 의 `+` 와 `-` 카운트.
- 임계: `min(modified_lines / added_lines) ≥ 0.3` (즉 변경:추가 ≈ 1:3 이상).
- vacuous PASS 차단: 산출물 0 변경 = automatic fail.

---

## 4. 본 sprint 가 *떠안고* 가는 risk (mitigation 안 함)

`premortem-friction.md` 정합 — *모든* risk 를 mitigation 하지 않는다. 일부는 *명시적으로 떠안고 다음 sprint 에 인계*.

### 4-1. CLI 휴리스틱의 *근본 부정확성*

- `comment_intent_check.py` / `hidden_intent_originality.py` 는 NLP-grade 휴리스틱이 아닌 token-level 휴리스틱.
- false positive ~5–10% 가능.
- mitigation 안 함 (sentinel escape 만 둠). **다음 sprint-51 후속 의제 — embedding-based 휴리스틱 검토.**

### 4-2. universe philosophy 카탈로그의 *완전성 부재*

- 본 sprint 는 7 philosophy (modular / oop / functional / data-driven / event-driven / actor / dsl-first) 만 catalog.
- 도메인 특화 철학 (e.g. *constraint-programming* / *streaming* / *staged-pipeline*) 부재.
- mitigation 안 함. **agent 가 catalog 외 philosophy 사용 시 `--allow-extra` flag 로 declare + 사용자 ack 한 회 = 카탈로그 추가.**

### 4-3. dogfood 검증의 *시간 격차*

- 본 sprint 마감 = 2026-05-10. g4-v4 cold session 검증 = 다음 회차 (사용자 일정 의존).
- 그 사이 본 sprint 는 *unverified* 상태.
- mitigation 안 함. **본 sprint 의 진짜 marker = g4-v4 결과. 그 전엔 *임시 plateau* 로 간주.**

---

## 5. 망설임 1 회 — *본 sprint 진행 OK?*

위 3 시나리오 + derived improvements + 떠안는 risk 까지 고려해도, 진행 결정.

근거:
1. **Likely case 도 plateau 1-2pt 상승** — 91 → 92-93. *우상향 압력*.
2. **Worst case 의 -1-3pt 회귀도 *구조 변경의 일시적 cost*** — `feedback_score_targeting_taboo.md` 정합. *구조 가치 우선*.
3. **Best case 의 95-97** = 1-2pt 갱신 가능성 — 천정 직접 깰 1 회 도전 가치.
4. **본 sprint 미진행 = 91 plateau 영구화** — 이건 사용자 명시 거부 메시지 ("그 이상을 하려면").

---

## 6. 본 premortem 의 자기 정합

본 문서 = 본 sprint 진행 *전* 의 *forward simulation*. 본 sprint 마감 시점 (PR-G report.md) 에서 *세 시나리오 중 어느 것이 실제* 였는지 *back-reference* 의무 (premortem-friction.md 정합 — 격언 + 망설임의 *purpose* = forward simulation + derived_improvements 도출).

PR-G `report.md` 본문 = 본 premortem 의 §2 시나리오 매핑 + §3 derived improvements 의 적용 결과 + §4 떠안은 risk 의 사후 평가.
