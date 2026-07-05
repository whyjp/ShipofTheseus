"""pytest 부트 — producer 테스트가 producer/kernel/scoring 모듈을 평면 import 하도록.

measure_submission.py 는 `import parsers`(같은 producers 디렉터리) 와 kernel 의
evidence/checkspec/kernel/meta_audit 을 쓴다. 테스트도 같은 최상위 이름으로 이들을
import 하고 score(집계)도 부른다. 세 디렉터리를 sys.path 에 넣어 스크립트 실행과
pytest 실행 경로를 일치시킨다. (상위 scoring/conftest.py 의 PYTHONIOENCODING 가드는
그대로 상속되며, 여기서도 방어적으로 재설정 — git subprocess 가 한국어 경로/출력을
안전히 디코딩하도록.)
"""
from __future__ import annotations

import os
import sys

_PRODUCERS_DIR = os.path.dirname(os.path.dirname(__file__))
_SCORING_DIR = os.path.dirname(_PRODUCERS_DIR)
_KERNEL_DIR = os.path.join(_SCORING_DIR, "kernel")

for _d in (_PRODUCERS_DIR, _KERNEL_DIR, _SCORING_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
