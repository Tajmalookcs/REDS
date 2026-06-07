@echo off
cd /d "%~dp0"

echo ================================
echo   REDS Auto Update
echo ================================
echo.

:: Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed!
    pause
    exit
)

:: Check if this is a git repo
if not exist ".git" (
    echo [ERROR] This folder is not a REDS project folder!
    echo Please run this file from inside the REDS folder.
    pause
    exit
)

:: Fetch latest changes from GitHub
echo Checking for updates...
git fetch origin main >nul 2>&1

:: Compare local and remote
git status -uno | findstr "behind" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Your project is already UP TO DATE!
    echo No changes found.
    echo.
    pause
    exit
)

:: Pull latest changes
echo Update found! Downloading...
git pull origin main
if %errorlevel% neq 0 (
    echo [ERROR] Update failed!
    pause
    exit
)

:: Activate venv and install any new requirements
echo.
echo Checking for new requirements...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

:: Run migrations if any new ones
echo Applying any new migrations...
python manage.py migrate

echo.
echo ================================
echo   Update Complete!
echo ================================
echo.
pause
