@echo off
title REDS — Real Estate Developer System
cd /d "%~dp0"

:: Check venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Please run "Install REDS.bat" first to set up the project.
    pause
    exit /b 1
)

:: Apply any pending migrations silently
venv\Scripts\python.exe manage.py migrate --run-syncdb >nul 2>&1

:: Open browser after short delay (server needs a moment to start)
start "" cmd /c "timeout /t 2 >nul && start http://127.0.0.1:8000"

:: Start server
echo ==========================================
echo   REDS is starting...
echo   Open your browser at http://127.0.0.1:8000
echo   Press Ctrl+C to stop the server.
echo ==========================================
echo.
venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
