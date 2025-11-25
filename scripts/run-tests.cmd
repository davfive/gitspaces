@echo off
REM Tiny cmd wrapper that invokes the Python orchestrator so tests actually run on Windows but orchestration uses Python.
REM Usage: scripts\run-tests.cmd "3.9,3.10"  (or omit arg for default)
setlocal
set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPTS=%SCRIPT_DIR%run-tests.py"
set "VERSIONS=%~1"

REM Try to find a Python interpreter (prefer py launcher)
where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo ERROR: No python interpreter found on PATH.
    endlocal & exit /b 1
  ) else (
    set "PY_CMD=py -3"
  )
) else (
  set "PY_CMD=python"
)

if "%VERSIONS%"=="" (
  %PY_CMD% "%PY_SCRIPTS%"
) else (
  %PY_CMD% "%PY_SCRIPTS%" "%VERSIONS%"
)

endlocal
exit /b %ERRORLEVEL%