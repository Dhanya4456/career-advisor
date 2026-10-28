@echo off
setlocal
title PathAI Backend - port 8000
cd /d "%~dp0backend"

rem ---- find a good Python (3.12 / 3.11 / 3.13 preferred) ----
set "PY="
for %%V in (3.12 3.11 3.13 3.10) do (
  if not defined PY (
    py -%%V --version >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY (
  python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo.
  echo Python is not installed or not on PATH.
  echo Install Python 3.12 from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
echo Using: 
%PY% --version

rem ---- virtual environment ----
if not exist ".venv\Scripts\python.exe" (
  echo Creating virtual environment...
  %PY% -m venv .venv
  if errorlevel 1 goto :fail
)
set "VPY=.venv\Scripts\python.exe"

echo Installing requirements - first run takes a few minutes...
"%VPY%" -m pip install --upgrade pip >nul 2>&1
"%VPY%" -m pip install -r requirements.txt
if errorlevel 1 goto :fail

echo.
echo ===== Self-test =====
"%VPY%" diagnose.py

echo ===== Starting server: http://localhost:8000/health =====
"%VPY%" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
echo.
echo The server stopped. Read the messages above for the reason.
pause
exit /b 0

:fail
echo.
echo *** SETUP FAILED - scroll up and read the red error above, or send me a screenshot. ***
pause
exit /b 1
