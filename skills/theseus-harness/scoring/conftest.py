"""pytest 세션 부트 — Windows 인코딩 호환 가드.

테스트 다수가 `subprocess.run([sys.executable, ...])` 로 자식 Python 프로세스를
띄워 한국어가 포함된 JSON 을 stdout 으로 반환받는다. Windows 의 콘솔 기본 코덱은
cp949 라서 자식의 sys.stdout 이 cp949 로 인코딩되고, 부모가 utf-8 로 디코딩하면
한국어 바이트 일부가 누락되어 JSON 파싱이 깨진다 — *작동하다 깨진 회귀가 아니라
v0.2.0 부터 Windows 에서 한 번도 작동한 적 없는 잠재 버그*. v0.2.1 까지의
"self_score=1.0 통과" 수치는 Linux/Mac 한정에서만 참이었다.

PYTHONIOENCODING=utf-8 을 부모 환경에 박으면 subprocess 가 자동 상속해 자식의
sys.stdout 도 utf-8 로 강제된다. 본 파일은 pytest 가 자동 로드 — 수동 import
불필요. 단일 변경으로 자식 Python 프로세스 모두에 전파.
"""
from __future__ import annotations

import os

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
