#!/usr/bin/env bash
# viewer-down.sh — sprint-36 viewer 라이프사이클 종료
# 위치: <project root>/viewer-runtime/viewer-down.sh
# 호출: bash viewer-runtime/viewer-down.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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
  echo "[viewer-down] THESEUS_HARNESS_ROOT 미설정 + 자동 탐색 실패." >&2
  exit 1
fi

CLI="$HARNESS_ROOT/scoring/viewer_runtime.py"
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
  PYTHON=python
fi

exec "$PYTHON" "$CLI" down --root "$PROJECT_ROOT"
