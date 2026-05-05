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

1. 첫 run: `python run_experiment.py` (또는 entry script) 후 `cp summary.json summary.run1.json`.
2. 둘째 run: 동일 명령 후 `cp summary.json summary.run2.json`.
3. byte-equal assert :
   ```python
   import hashlib
   sha1 = hashlib.sha256(open('summary.run1.json','rb').read()).hexdigest()
   sha2 = hashlib.sha256(open('summary.run2.json','rb').read()).hexdigest()
   assert sha1 == sha2, f'reproducibility broken: {sha1} != {sha2}'
   ```
4. 불일치 → fail + 가능한 원인 진단 :
   - PYTHONHASHSEED 미설정 (`os.environ['PYTHONHASHSEED'] = '0'` 의무 — `hash() 솔트` 회귀 직접 차단)
   - threading / multiprocessing 결과 순서 비결정
   - `os.listdir()` / `glob.glob()` 정렬 안 함
   - timestamp / wall-clock 기반 출력 leak
5. byte-equal 후에야 phase 09 통과.

## frontmatter (quality-gate)

```yaml
reproducibility_run1_sha256: "..."
reproducibility_run2_sha256: "..."
reproducibility_byte_equal: true
pythonhashseed: "0"
```

## self_lint C-RDC

컨벤션 파일 존재 + 페이즈 09 게이트 본문에 "doublecheck" + sha256 알고리즘 + "byte-equal" 명시.

## 안티 패턴

a- 시드만 고정하고 doublecheck skip — sprint-18 차단 대상.
b- diff 가 "타임스탬프뿐" 으로 무시 — 타임스탬프도 출력에 박히면 불일치. summary.json 에 timestamp 포함 금지 (별도 metadata 파일로 분리).
c- PYTHONHASHSEED 미설정 → `hash() 솔트` 회귀 (cold 003 직접 사례).
d- 첫 run 만 grader 에 노출 — 실제는 두 번 다 grader 에게 sha256 evidence 박는 의무.

## cold session 003 검증

`run_experiment.py` 가 dict 순회 결과를 summary.json 에 박음. PYTHONHASHSEED 미설정으로 두 번째 run 의 key 순서 다름 → grader -3pt Reproducibility (Results 와 root cause 공유). sprint-18 doublecheck 적용 시 sha256 mismatch detect → PYTHONHASHSEED=0 강제.
