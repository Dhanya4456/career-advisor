@echo off
title PathAI Frontend (port 5173)
cd /d "%~dp0frontend\career-advisor"
if not exist node_modules (
  echo Installing packages...
  call npm install
)
call npm run dev
pause
