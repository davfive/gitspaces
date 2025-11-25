param(
  [string] $versionsStr = ""
)

$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Split-Path -Parent $ScriptDir)

# Find python (prefer 'python', fallback to 'py -3')
if (Get-Command python -ErrorAction SilentlyContinue) {
  $pyCmd = 'python'
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
  $pyCmd = 'py -3'
} else {
  Write-Error 'No python found on PATH.'
  exit 1
}

if ($versionsStr) {
  & $pyCmd "$ScriptDir\run-tests.py" $versionsStr
} else {
  & $pyCmd "$ScriptDir\run-tests.py"
}

exit $LASTEXITCODE