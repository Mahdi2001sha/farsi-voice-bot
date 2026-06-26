@echo off
setlocal enabledelayedexpansion

set KMP_DUPLICATE_LIB_OK=TRUE

cd /d "%~dp0"

echo.
echo Starting Farsi Voice Assistant...
echo.

echo [1/2] Starting backend on port 9999...
start "Backend" cmd /k "set KMP_DUPLICATE_LIB_OK=TRUE && cd backend && python -m uvicorn main:app --port 9999"

timeout /t 4

echo [2/2] Starting frontend on port 3000...
start "Frontend" cmd /k "cd frontend && python -m http.server 3000"

timeout /t 2

echo Opening browser...
timeout /t 2

start http://localhost:3000/index.html

echo.
echo Both servers running. Close windows to stop.
echo.

pause
