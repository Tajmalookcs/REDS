@echo off
cd /d "%~dp0"

netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel% == 0 (
    start "" "http://127.0.0.1:8000/"
    exit
)

start "" /b wscript.exe "%~dp0run_silent.vbs"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000/"
exit
