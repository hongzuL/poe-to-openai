@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title poe-to-openai Setup

set "ENV_NAME=poe-to-openai"
set "PY_VER=3.11"
set "MARKER=.python-path"

echo ==================================================
echo  poe-to-openai environment setup
echo ==================================================
echo.

REM ---------- 0. Reuse existing ready environment ----------
if exist "%MARKER%" (
    set /p _p=<"%MARKER%"
    if exist "!_p!" (
        "!_p!" -c "import uvicorn, fastapi_poe" >nul 2>nul
        if !errorlevel! equ 0 (
            echo [OK] Environment already configured: !_p!
            goto :done
        )
    )
)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import uvicorn, fastapi_poe" >nul 2>nul
    if !errorlevel! equ 0 (
        echo [OK] Environment already configured: .venv
        echo %CD%\.venv\Scripts\python.exe>"%MARKER%"
        goto :done
    )
)

REM ---------- 1. Detect conda / miniforge ----------
set "CONDA_BASE="
for %%p in (
    "%USERPROFILE%\miniforge3"
    "%USERPROFILE%\miniconda3"
    "%USERPROFILE%\mambaforge3"
    "%USERPROFILE%\anaconda3"
    "%LOCALAPPDATA%\miniforge3"
    "%LOCALAPPDATA%\miniconda3"
    "C:\ProgramData\miniforge3"
    "C:\ProgramData\miniconda3"
    "C:\ProgramData\anaconda3"
) do (
    if not defined CONDA_BASE if exist "%%~p\Scripts\conda.exe" set "CONDA_BASE=%%~p"
)

REM conda on PATH (condabin\conda.bat or Scripts\conda.exe)
if not defined CONDA_BASE (
    for /f "delims=" %%i in ('where conda 2^>nul') do (
        if not defined CONDA_BASE (
            set "_cdir=%%~dpi"
            set "_cdir=!_cdir:~0,-1!"
            for %%d in ("!_cdir!") do set "_cname=%%~nxd"
            if /i "!_cname!"=="condabin" (
                for %%d in ("!_cdir!\..") do (
                    if exist "%%~fd\Scripts\conda.exe" set "CONDA_BASE=%%~fd"
                )
            )
            if /i "!_cname!"=="Scripts" (
                for %%d in ("!_cdir!\..") do (
                    if exist "%%~fd\Scripts\conda.exe" set "CONDA_BASE=%%~fd"
                )
            )
        )
    )
)

if defined CONDA_BASE (
    echo [1/3] Found Conda/Miniforge: !CONDA_BASE!
    set "ENV_PY=!CONDA_BASE!\envs\%ENV_NAME%\python.exe"
    if exist "!ENV_PY!" (
        echo [2/3] Conda env "%ENV_NAME%" already exists, skipping creation
    ) else (
        echo [2/3] Creating conda env "%ENV_NAME%" (Python %PY_VER%^), first run may take a few minutes...
        "!CONDA_BASE!\Scripts\conda.exe" create -n %ENV_NAME% python=%PY_VER% -y
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to create conda env. Check network and retry.
            pause
            exit /b 1
        )
    )
    echo [3/3] Installing dependencies...
    "!ENV_PY!" -m pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies. Check network and retry.
        pause
        exit /b 1
    )
    echo !ENV_PY!>"%MARKER%"
    goto :done
)

REM ---------- 2. No conda: fall back to system Python + .venv ----------
set "SYS_PY="
where python >nul 2>nul
if !errorlevel! equ 0 set "SYS_PY=python"
if not defined SYS_PY (
    where py >nul 2>nul
    if !errorlevel! equ 0 set "SYS_PY=py"
)

if defined SYS_PY (
    set "_okv="
    set "_ver="
    for /f "delims=" %%v in ('!SYS_PY! -c "import sys;print('%%d.%%d'%%sys.version_info[:2])" 2^>nul') do set "_ver=%%v"
    if defined _ver (
        for /f "tokens=1,2 delims=." %%a in ("!_ver!") do (
            if %%a geq 3 if %%b geq 10 set "_okv=1"
        )
    )
    if not defined _okv (
        echo [WARN] System Python !_ver! is too old ^(need 3.10+^), skipped.
    ) else (
        echo [1/2] Creating virtual environment .venv with system Python...
        !SYS_PY! -m venv .venv
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to create virtual environment.
            pause
            exit /b 1
        )
        echo [2/2] Installing dependencies...
        ".venv\Scripts\python.exe" -m pip install --upgrade pip
        ".venv\Scripts\python.exe" -m pip install -r requirements.txt
        if !errorlevel! neq 0 (
            echo [ERROR] Failed to install dependencies. Check network and retry.
            pause
            exit /b 1
        )
        echo %CD%\.venv\Scripts\python.exe>"%MARKER%"
        goto :done
    )
)

REM ---------- 3. Nothing found ----------
echo.
echo [ERROR] No conda / miniforge / python environment detected.
echo.
echo Please install ONE of the following, then run this script again:
echo   1. Miniforge (recommended): https://github.com/conda-forge/miniforge
echo   2. Miniconda:               https://docs.conda.io/projects/miniconda
echo   3. Python 3.10+:            https://www.python.org/downloads/
echo      (check "Add Python to PATH" during installation)
echo.
pause
exit /b 1

:done
echo.
echo ==================================================
echo  Setup complete. Run start.bat to launch the server.
echo ==================================================
exit /b 0
