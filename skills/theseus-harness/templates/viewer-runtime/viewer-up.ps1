# viewer-up.ps1 — sprint-36 viewer 라이프사이클 시작 (Windows PowerShell)
# 위치: <project root>\viewer-runtime\viewer-up.ps1
# 호출: powershell -File viewer-runtime\viewer-up.ps1 [-Port 18080] [-Host 127.0.0.1]
param(
  [int]$Port = 0,
  [string]$ListenHost = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = (Resolve-Path (Join-Path $ScriptDir "..")).Path

$HarnessRoot = $env:THESEUS_HARNESS_ROOT
if (-not $HarnessRoot) {
  $candidates = @(
    (Join-Path $ProjectRoot "..\..\skills\theseus-harness"),
    (Join-Path $ProjectRoot "..\..\..\skills\theseus-harness"),
    (Join-Path $ProjectRoot "..\..\..\..\skills\theseus-harness")
  )
  foreach ($c in $candidates) {
    $cli = Join-Path $c "scoring\viewer_runtime.py"
    if (Test-Path $cli) {
      $HarnessRoot = (Resolve-Path $c).Path
      break
    }
  }
}

if (-not $HarnessRoot) {
  Write-Error "[viewer-up] THESEUS_HARNESS_ROOT 미설정 + 자동 탐색 실패. 환경변수 설정 후 재실행."
  exit 1
}

$Cli = Join-Path $HarnessRoot "scoring\viewer_runtime.py"
if (-not (Test-Path $Cli)) {
  Write-Error "[viewer-up] viewer_runtime.py 부재: $Cli"
  exit 1
}

$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

$args = @("up", "--root", $ProjectRoot)
if ($Port -gt 0)        { $args += @("--port", $Port) }
if ($ListenHost -ne "") { $args += @("--host", $ListenHost) }

& $Python $Cli @args
exit $LASTEXITCODE
