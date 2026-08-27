@echo off
setlocal
cd /d "%~dp0"
title poe-to-openai Configuration

REM 1. Find python executable
set "PY_BIN="
if exist ".venv\Scripts\python.exe" (
    set "PY_BIN=.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_BIN=python"
    ) else (
        where py >nul 2>nul
        if %errorlevel% equ 0 (
            set "PY_BIN=py"
        )
    )
)

if "%PY_BIN%"=="" (
    echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

REM 2. Run manager.py config
"%PY_BIN%" manager.py config

echo.
pause