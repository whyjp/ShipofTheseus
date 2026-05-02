#!/usr/bin/env bash
# self-check — 본 저장소의 lint + score test 일괄.
# 부트스트래핑 자체 평가의 객관 측정 단계.
set -euo pipefail
cd "$(dirname "$0")/.."

# v0.4.0 PR-2 — fresh-user stack 점검 모드
if [[ "${1:-}" == "--check-stack-only" ]]; then
  echo "==> stack-check (fresh-user 환경 진단)"
  for cmd in python3 go bun node pytest; do
    if command -v "$cmd" >/dev/null 2>&1; then
      ver="$($cmd --version 2>&1 | head -1)"
      echo "[stack-check] $cmd: ✓ ($ver)"
    else
      echo "[stack-check] $cmd: ✗ — install via stack.md or asdf/nvm/goenv"
    fi
  done
  exit 0
fi

echo "==> self_lint (컨벤션 / 교차 링크 / 버전 / 컴파일 / 인코딩 가드 — 35 체크)"
python skills/theseus-harness/scoring/self_lint.py

echo
echo "==> pytest (score.py 12 + self_lint 4 = 16 케이스)"
python -m pytest skills/theseus-harness/scoring/ -q

echo
echo "==> sample inputs 채점"
python skills/theseus-harness/scoring/score.py \
  --inputs skills/theseus-harness/templates/sample-inputs.json

echo
echo "==> 자기 평가 점수 (임계 0.99999)"
python skills/theseus-harness/scoring/self_lint.py --score

echo
echo "==> 핑거프린트 체인 무결성 (.ShipofTheseus/theseus-self/)"
python skills/theseus-harness/scoring/fingerprint.py chain \
  --dir .ShipofTheseus/theseus-self/

echo
echo "==> 모두 통과"
