---
id: submission-portability
category: quality
applies-to-phases: '[09]'
applies-to-grades: '[all]'
trigger-when: 'entry script'
indexed-in: conventions/INDEX.md
---

# Submission portability — entry script CLI flag + env var fallback (sprint-18, cd, HARD-RULE 9.ff)

## 한 줄 요약

**submissions 의 entry script 는 `--data-dir` CLI flag 의무 + `DATA_DIR` env var fallback. `REPO_ROOT.parent.parent` 같은 path 하드코딩 금지.** 외부 cold session 003 의 `REPO_ROOT.parent.parent` 경로 하드코딩으로 다른 디렉터리 구조에서 실행 불가 회귀 직접 정정.

## 결손 진단

| 결손 | 증거 / 영향 |
|---|---|
| entry script 가 `__file__.parent.parent.parent` 같은 path 추정 | 디렉터리 구조 가정 깨지면 실행 불가 → grader 가 portability 직접 지적 -1pt Code quality |
| CLI flag / env var fallback 부재 | grader 가 다른 환경에서 재현 불가 |

## 트리거

페이즈 09 quality gate. submissions 의 entry script (`run_experiment.py`, `main.py`, `entry.py`, `index.ts` 등).

## 알고리즘

1. entry script grep 패턴 ≥ 1 detect → fail :
   - `Path(__file__).parent.parent`
   - `REPO_ROOT.parent.parent`
   - `os.path.dirname(os.path.dirname(os.path.dirname(...)))` 류 ≥ 2 회 chain
   - 절대 경로 하드코딩 (`/home/`, `C:\`, `D:\`)
2. 의무 패턴 ≥ 1 detect 강제 :
   - `argparse.ArgumentParser` + `--data-dir` flag, OR
   - `click.option('--data-dir', ...)` + `DATA_DIR` env var fallback (`os.environ.get('DATA_DIR', default)`).
3. fallback 순서 : CLI flag > env var > 명시적 default (script 동일 디렉터리).
4. 위반 시 entry script 수정 강제.

## entry script 의무 패턴 (Python)

```python
import argparse, os
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--data-dir', type=Path,
               default=Path(os.environ.get('DATA_DIR', Path(__file__).parent / 'data')))
args = p.parse_args()
DATA_DIR = args.data_dir
```

## frontmatter (09-quality-gate)

```yaml
entry_script_path: "run_experiment.py"
entry_script_data_dir_cli: true
entry_script_env_var_fallback: true
hardcoded_path_violations: 0
```

## self_lint C-SPB

컨벤션 파일 존재 + 페이즈 09 본문 "submission-portability" + "--data-dir" + "CLI flag" + "env var" + 안티 패턴 "REPO_ROOT.parent.parent" 명시.

## 안티 패턴

a- `REPO_ROOT = Path(__file__).parent.parent.parent` — sprint-18 직접 차단 대상.
b- 절대 경로 (`/home/user/...` / `C:\...`) — portability 0.
c- env var 만 (CLI flag 없음) — 사용자 ergonomics 떨어짐.
d- CLI flag 만 (env var fallback 없음) — CI/automation 비편의.
e- "submissions/X/data" 하드코딩 후 다른 위치로 이동 시 깨짐.

## cold session 003 검증

`run_experiment.py`: `REPO_ROOT = Path(__file__).parent.parent.parent` + `DATA_DIR = REPO_ROOT / 'submissions' / '...' / 'data'`.
→ grader -1pt Code quality. sprint-18 게이트 적용 시 grep detect → argparse + DATA_DIR env fallback 변환 강제.
