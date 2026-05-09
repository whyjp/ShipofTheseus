---
id: reproducibility-doublecheck
category: quality
applies-to-phases: '[09]'
applies-to-grades: '[all]'
trigger-when: 'entry script'
indexed-in: conventions/INDEX.md
---

# Reproducibility doublecheck (`reproducibility-doublecheck`) — 2회 실행 byte-equal (sprint-18, ca, HARD-RULE 9.cc)

## 한 줄 요약

**entry script 를 *2회* 연속 실행 후 summary.json byte-equal assert — 시드 고정에도 불구하고 `hash()` 솔트 / 스레드 race / OS 비결정 path 등으로 출력이 흔들리는 잠복 회귀 차단.** 외부 cold session 003 의 `hash()` 솔트 버그로 reproducibility 깨졌으나 harness 가 잡지 못한 회귀 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| 시드 고정 만으로 충분하다 가정 | Python `hash()` PYTHONHASHSEED 미설정 시 dict 순회 비결정 → seeded run 도 출력 다름 |
| 단일 run 결과 신뢰 | 한 번 실행 후 summary.json 박힘 → 다음 run 결과 다른 줄 모름 |
| determinism evidence 부재 | frontmatter `reproducibility_seed_explicit: true` 만으로 검증 종료 — 실 doublecheck 안 함 |

## 트리거

페이즈 09 게이트 (실 코드가 외부 repo 일 시 phase 09 가 외부 repo 의 entry script 호출).

## 알고리즘

1. 첫 run: `subprocess.run([sys.executable, entry_script, ...], env={**os.environ, "PYTHONHASHSEED": "0"})` 후 `cp summary.json summary.run1.json`.
2. 둘째 run: **별 subprocess 호출** 동일 명령 후 `cp summary.json summary.run2.json`. (sprint-40 강화 — *같은 process 내 두 함수 호출* 로 위장 금지. cross-process 의무.)
3. byte-equal assert :
   ```python
   import hashlib
   sha1 = hashlib.sha256(open('summary.run1.json','rb').read()).hexdigest()
   sha2 = hashlib.sha256(open('summary.run2.json','rb').read()).hexdigest()
   assert sha1 == sha2, f'reproducibility broken: {sha1} != {sha2}'
   ```
4. **anti-pattern grep** ([`cross-process-anti-patterns.md`](cross-process-anti-patterns.md), sprint-40 PR-B 신규) — `SeedSequence([..., hash(scenario_id), ...])` 류 7 패턴 src/ 자동 검사. violations 비어 있어야 통과.
5. 불일치 → fail + 가능한 원인 진단 :
   - PYTHONHASHSEED 미설정 (`os.environ['PYTHONHASHSEED'] = '0'` 의무 — `hash() 솔트` 회귀 직접 차단)
   - `cross-process-anti-patterns.md` 카탈로그 위반 (e.g., `hash(scenario_id)` in SeedSequence — sprint-40 직접 사례)
   - threading / multiprocessing 결과 순서 비결정
   - `os.listdir()` / `glob.glob()` 정렬 안 함
   - timestamp / wall-clock 기반 출력 leak
6. byte-equal + anti-pattern grep 0 위반 후에야 phase 09 통과.
7. **JSON evidence emit 의무 (sprint-40 PR-B 강화)** — `quality/gate_v6_reproducibility.json` 별 산출물 필수 (phase 09-quality-gates.md §V6-Evidence-Bound 본문 참조). 본문 attestation 만으로 통과 불가.

## frontmatter (quality-gate)

```yaml
reproducibility_run1_sha256: "..."
reproducibility_run2_sha256: "..."
reproducibility_byte_equal: true
pythonhashseed: "0"
reproducibility_evidence_json: "quality/gate_v6_reproducibility.json"  # sprint-40 PR-B 신규 — 본 JSON 부재 시 phase 09 진입 거부
cross_process_anti_pattern_violations: 0   # sprint-40 신규 — 7 패턴 grep 0 위반
```

## self_lint C-RDC

컨벤션 파일 존재 + 페이즈 09 게이트 본문에 "doublecheck" + sha256 알고리즘 + "byte-equal" 명시.

## self_lint C-V6X (sprint-40 PR-B 신규)

phase 09 진입 시 :
- `quality/gate_v6_reproducibility.json` 존재 확인
- 본 JSON 의 `verdict == "pass"` + `cross_process.summary_byte_equal == true` + `anti_pattern_grep.violations == []` 모두 만족 확인
- 미달 시 phase 09 진입 거부

본 lint 가 *컨벤션 선언 ≠ 런타임 집행* 갭 (메모리 [`feedback_convention_runtime_gap.md`](../../../memory/feedback_convention_runtime_gap.md)) 의 직접 닫음.

## 안티 패턴

a- 시드만 고정하고 doublecheck skip — sprint-18 차단 대상.
b- diff 가 "타임스탬프뿐" 으로 무시 — 타임스탬프도 출력에 박히면 불일치. summary.json 에 timestamp 포함 금지 (별도 metadata 파일로 분리).
c- PYTHONHASHSEED 미설정 → `hash() 솔트` 회귀 (cold 003 직접 사례).
d- 첫 run 만 grader 에 노출 — 실제는 두 번 다 grader 에게 sha256 evidence 박는 의무.

## cold session 003 검증

`run_experiment.py` 가 dict 순회 결과를 summary.json 에 박음. PYTHONHASHSEED 미설정으로 두 번째 run 의 key 순서 다름 → grader -3pt Reproducibility (Results 와 root cause 공유). sprint-18 doublecheck 적용 시 sha256 mismatch detect → PYTHONHASHSEED=0 강제.

## simulation-bench 001 v0.9.44 g4-v2 검증 (sprint-40 PR-B 직접 대응)

`src/mine_sim/distributions.py::replication_rng` 가 `numpy.random.SeedSequence([base, hash(scenario_id), rep])` — `hash(scenario_id)` 의 *Python salt randomization* 으로 process invocation 마다 다른 시드 생성 → cross-process 출력 다름. **본 컨벤션의 V6 byte-equal assert + sprint-40 PR-B 의 §V6-Evidence-Bound (별 subprocess 의무 + anti-pattern grep) 동시 적용 시 detect**:

1. `subprocess.run` × 2 의 summary.json sha256 mismatch — fail.
2. `cross-process-anti-patterns.md` 의 `SeedSequence\([^)]*hash\(` regex grep — match. fail.
3. 정정 — `hashlib.md5(scenario_id.encode()).digest()[:4]` 류 deterministic hash.

zero-context Opus reviewer 가 README ↔ summary 0.08% drift 를 catch 한 후에야 발견된 회귀를 *본 컨벤션 의 sprint-40 강화* 가 phase 09 진입 단계에서 미리 차단.
