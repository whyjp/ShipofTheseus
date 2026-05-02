@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

echo ==^> self_lint (18 체크)
python skills\theseus-harness\scoring\self_lint.py || exit /b 1

echo.
echo ==^> pytest 16 케이스
python -m pytest skills\theseus-harness\scoring\ -q || exit /b 1

echo.
echo ==^> sample inputs
python skills\theseus-harness\scoring\score.py --inputs skills\theseus-harness\templates\sample-inputs.json || exit /b 1

echo.
echo ==^> 자기 평가 점수 (임계 0.99999)
python skills\theseus-harness\scoring\self_lint.py --score || exit /b 1

echo.
echo ==^> 핑거프린트 체인
python skills\theseus-harness\scoring\fingerprint.py chain --dir .ShipofTheseus\theseus-self\ || exit /b 1

echo.
echo ==^> 모두 통과
