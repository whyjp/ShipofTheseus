#!/usr/bin/env bash
# viewer-up.sh — sprint-36 viewer 라이프사이클 시작
#
# 본 스크립트는 .ShipofTheseus/<proj>/viewer-runtime/ 에 복사된 후 실행.
# 위치: <project root>/viewer-runtime/viewer-up.sh
# 호출: bash viewer-runtime/viewer-up.sh [--port 18080] [--host 127.0.0.1]
#
# 동작:
#   1. python skills/theseus-harness/scoring/viewer_runtime.py up --root <project root>
#   2. lock file: viewer-runtime/viewer.lock.json
#   3. log file:  viewer-runtime/server.log
#
# 종료: viewer-down.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 하네스 위치 추적 — env var 우선, 없으면 상대 경로 추정
HARNESS_ROOT="${THESEUS_HARNESS_ROOT:-}"
if [ -z "$HARNESS_ROOT" ]; then
  for candidate in \
      "$PROJECT_ROOT/../../skills/theseus-harness" \
      "$PROJECT_ROOT/../../../skills/theseus-harness" \
      "$PROJECT_ROOT/../../../../skills/theseus-harness" ; do
    if [ -f "$candidate/scoring/viewer_runtime.py" ]; then
      HARNESS_ROOT="$(cd "$candidate" && pwd)"
      break
    fi
  done
fi

if [ -z "$HARNESS_ROOT" ]; then
  echo "[viewer-up] THESEUS_HARNESS_ROOT 미설정 + 자동 탐색 실패." >&2
  echo "  THESEUS_HARNESS_ROOT=<harness root> 로 환경변수 설정 후 재실행." >&2
  exit 1
fi

CLI="$HARNESS_ROOT/scoring/viewer_runtime.py"
if [ ! -f "$CLI" ]; then
  echo "[viewer-up] viewer_runtime.py 부재: $CLI" >&2
  exit 1
fi

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  PYTHON=python
fi

exec "$PYTHON" "$CLI" up --root "$PROJECT_ROOT" "$@"
