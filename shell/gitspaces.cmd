@echo off
REM GitSpaces shell wrapper for Windows CMD
REM This wrapper enables cd behavior after gitspaces commands
REM
REM Installation:
REM   Add the shell directory to your PATH, or copy this file to a directory in your PATH
REM
REM Usage:
REM   gs [command] [args...]

setlocal enabledelayedexpansion

REM Run gitspaces
gitspaces %*
set EXIT_CODE=%ERRORLEVEL%

REM Check for shell target file
set "PID_FILE=%USERPROFILE%\.gitspaces\pid-%~dp0"
REM Use a simpler approach - check for any pid file for this session
for /f "tokens=2 delims==" %%i in ('wmic process where "ProcessId=%%" get ParentProcessId /value 2^>nul ^| find "="') do set PPID=%%i

set "PID_FILE=%USERPROFILE%\.gitspaces\pid-cmd"
if exist "%PID_FILE%" (
    set /p TARGET_DIR=<"%PID_FILE%"
    del "%PID_FILE%" 2>nul
    
    if exist "!TARGET_DIR!" (
        cd /d "!TARGET_DIR!"
    )
)

endlocal & cd /d "%TARGET_DIR%" 2>nul
exit /b %EXIT_CODE%
