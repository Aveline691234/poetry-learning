@echo off
chcp 65001 >nul
title AI Poetry Teacher
echo.
echo ========================================
echo    AI Poetry Teacher - Launcher
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo OK: Python ready

echo.
echo [2/4] Installing dependencies...
pip install flask flask-cors requests -q
echo OK: Dependencies installed

echo.
echo [3/4] Starting backend...
start "Backend-Poetry" cmd /k "python backend.py"
timeout /t 3 /nobreak >nul

echo.
echo [4/4] Starting frontend...
start "Frontend-Poetry" cmd /k "python -m http.server 8888"
timeout /t 2 /nobreak >nul

echo.
echo Opening browser...
start msedge "http://localhost:8888/login.html"

echo.
echo ========================================
echo    AI Poetry Teacher Started!
echo ========================================
echo.
echo    Frontend: http://localhost:8888
echo    Backend:  http://localhost:8000
echo.
echo    Login:    http://localhost:8888/login.html
echo.
echo    Close windows to stop services
echo ========================================
echo.
pause