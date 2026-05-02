#!/usr/bin/env bash
# self-check — 본 저장소의 lint + score test 일괄.
# 부트스트래핑 자체 평가의 객관 측정 단계.
set -euo pipefail
cd "$(dirname "$0")/.."

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
