@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0\.."

REM v0.4.0 PR-2 — fresh-user stack 점검 모드
if "%~1"=="--check-stack-only" (
  echo ==^> stack-check ^(fresh-user 환경 진단^)
  for %%c in (python3 go bun node pytest) do (
    where /q %%c
    if errorlevel 1 (
      echo [stack-check] %%c: X -- install via stack.md or asdf/nvm/goenv
    ) else (
      echo [stack-check] %%c: OK
    )
  )
  exit /b 0
)

echo ==^> self_lint (35 체크)
python skills\theseus-harness\scoring\self_lint.py || exit /b 1

echo.
echo ==^> pytest 99 케이스
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

REM v0.4.0 PR-9 — sprint 시계열 자동 기록
set SPRINT_DIR=.ShipofTheseus\theseus-self\sprints
if exist "%SPRINT_DIR%" (
  set LATEST_SPRINT=
  for /f "delims=" %%d in ('dir /b /ad /o-n "%SPRINT_DIR%" 2^>nul ^| findstr "^[0-9]"') do (
    if not defined LATEST_SPRINT set LATEST_SPRINT=%SPRINT_DIR%\%%d
  )
  if defined LATEST_SPRINT (
    set REPORT_FILE=%LATEST_SPRINT%\report.md
    for /f "delims=" %%s in ('python skills\theseus-harness\scoring\self_lint.py --score 2^>nul ^| python -c "import sys, json; d=json.load(sys.stdin); print(d.get('self_score', 'N/A'))" 2^>nul') do (
      set SELF_SCORE=%%s
    )
    if not defined SELF_SCORE set SELF_SCORE=N/A
    echo. >> "%REPORT_FILE%"
    echo ## Sprint Run -- %date% %time% >> "%REPORT_FILE%"
    echo - self_score: `%SELF_SCORE%` >> "%REPORT_FILE%"
    echo - 임계: `0.99999` >> "%REPORT_FILE%"
    echo [sprint-timeline] %REPORT_FILE% 갱신 완료 ^(self_score=%SELF_SCORE%^)
  )
)
