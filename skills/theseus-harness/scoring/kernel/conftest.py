"""pytest 부트 — kernel 디렉터리를 sys.path 에 삽입해 평면 import 를 허용.

kernel.py 는 `python kernel.py verify` 스크립트로도, pytest 로도 동일한 최상위
모듈(evidence/checkspec/kernel)로 import 되어야 한다. 스크립트 실행 시엔 sys.path[0]
이 곧 이 디렉터리라 자동 해결되고, pytest 실행 시엔 본 conftest 가 같은 경로를 넣어
양쪽 경로를 일치시킨다. (상위 scoring/conftest.py 의 PYTHONIOENCODING 가드는 그대로
상속된다.)
"""
from __future__ import annotations

import os
import sys

_KERNEL_DIR = os.path.dirname(__file__)
if _KERNEL_DIR not in sys.path:
    sys.path.insert(0, _KERNEL_DIR)
