@echo off
REM Unified runner for tests and static checks (cmd)
REM Usage:
REM   scripts\run.cmd --tests
REM   scripts\run.cmd --lint
REM   scripts\run.cmd --security
REM   scripts\run.cmd --all

set RUN_TESTS=false
set RUN_LINT=false
set RUN_SECURITY=false

if "%~1"=="" set RUN_TESTS=true
:parse
if "%~1"=="" goto run
if "%~1"=="--tests" set RUN_TESTS=true
if "%~1"=="--lint" set RUN_LINT=true
if "%~1"=="--security" set RUN_SECURITY=true
if "%~1"=="--all" set RUN_TESTS=true&set RUN_LINT=true
if "%~1"=="--help" goto help
shift
goto parse

:run
if "%RUN_LINT%"=="true" (
  if "%RUN_SECURITY%"=="true" (
    call ci\static-checks.cmd
  ) else (
    call ci\static-checks.cmd --quick
  )
)
if "%RUN_TESTS%"=="true" call ci\run-tests.cmd
exit /b 0

:help
echo Usage: run.cmd [--tests] [--lint] [--security] [--all]
exit /b 0
