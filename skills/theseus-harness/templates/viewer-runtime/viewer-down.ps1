# viewer-down.ps1 — sprint-36 viewer 라이프사이클 종료 (Windows PowerShell)
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
  Write-Error "[viewer-down] THESEUS_HARNESS_ROOT 미설정 + 자동 탐색 실패."
  exit 1
}

$Cli = Join-Path $HarnessRoot "scoring\viewer_runtime.py"
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }

& $Python $Cli down --root $ProjectRoot
exit $LASTEXITCODE
