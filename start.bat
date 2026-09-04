@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title poe-to-openai

REM ---------- 1. Locate a usable Python environment ----------
REM Order: .python-path (written by setup.bat) -> .venv -> conda env -> system python/py
set "PY_BIN="
if exist ".python-path" (
    set /p _p=<".python-path"
    if exist "!_p!" set "PY_BIN=!_p!"
)
if not defined PY_BIN if exist ".venv\Scripts\python.exe" set "PY_BIN=.venv\Scripts\python.exe"
if not defined PY_BIN (
    for %%b in (
        "%USERPROFILE%\miniforge3"
        "%USERPROFILE%\miniconda3"
        "%USERPROFILE%\mambaforge3"
        "%USERPROFILE%\anaconda3"
        "C:\ProgramData\miniforge3"
        "C:\ProgramData\miniconda3"
        "C:\ProgramData\anaconda3"
    ) do (
        if not defined PY_BIN if exist "%%~b\envs\poe-to-openai\python.exe" set "PY_BIN=%%~b\envs\poe-to-openai\python.exe"
    )
)
if not defined PY_BIN (
    where python >nul 2>nul
    if !errorlevel! equ 0 (
        set "PY_BIN=python"
    ) else (
        where py >nul 2>nul
        if !errorlevel! equ 0 set "PY_BIN=py"
    )
)

REM ---------- 2. No environment found -> auto setup ----------
if not defined PY_BIN (
    echo [INFO] No conda / miniforge / python environment detected. Running auto setup...
    echo.
    call setup.bat
    if !errorlevel! neq 0 (
        pause
        exit /b 1
    )
    if exist ".python-path" set /p PY_BIN=<".python-path"
    if not defined PY_BIN (
        echo [ERROR] No usable Python environment after setup. See output above.
        pause
        exit /b 1
    )
)

REM ---------- 3. Dependency check -> auto setup if missing ----------
"%PY_BIN%" -c "import uvicorn, fastapi_poe" >nul 2>nul
if !errorlevel! neq 0 (
    echo [INFO] Dependencies missing or incomplete. Running auto setup...
    echo.
    call setup.bat
    if !errorlevel! neq 0 (
        pause
        exit /b 1
    )
    if exist ".python-path" set /p PY_BIN=<".python-path"
    if not defined PY_BIN (
        echo [ERROR] No usable Python environment after setup. See output above.
        pause
        exit /b 1
    )
)

REM ---------- 4. Run manager.py ----------
"%PY_BIN%" manager.py %*

if "%~1"=="" (
    pause
)
