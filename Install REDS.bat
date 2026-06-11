@echo off
title Project Updater
echo ==========================================
echo        Checking for latest updates...
echo ==========================================
echo.

:: Check Git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not found in PATH.
    echo Please install Git from https://git-scm.com
    pause
    exit /b 1
)

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not found in PATH.
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

set REPO_URL=https://github.com/Tajmalookcs/REDS.git
set PROJECT_DIR=D:\REDS

:: Clone or Pull
if exist "%PROJECT_DIR%\.git" (
    echo Downloading latest changes...
    echo.
    cd /d "%PROJECT_DIR%"
    git pull %REPO_URL%
) else (
    echo First time setup - Downloading project files...
    echo.
    git clone %REPO_URL% "%PROJECT_DIR%"
    cd /d "%PROJECT_DIR%"
)

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Could not download updates. Contact the developer.
    pause
    exit /b 1
)

:: Always cd into project dir to be safe
cd /d "%PROJECT_DIR%"
echo Working directory: %CD%
echo.

:: Create venv if it does not exist
echo ==========================================
echo   Checking virtual environment...
echo ==========================================

if not exist "%PROJECT_DIR%\venv" (
    echo Creating virtual environment...
    python -m venv "%PROJECT_DIR%\venv"
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo ==========================================
echo   Activating virtual environment...
echo ==========================================
call "%PROJECT_DIR%\venv\Scripts\activate.bat"

if %errorlevel% neq 0 (
    echo ERROR: Could not activate virtual environment.
    pause
    exit /b 1
)
echo Virtual environment activated.

echo.
echo ==========================================
echo   Installing dependencies...
echo ==========================================
pip install -r "%PROJECT_DIR%\requirements.txt"

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   Applying database migrations...
echo ==========================================
python manage.py migrate

echo.
if %errorlevel% equ 0 (
    echo ==========================================
    echo   All done! Project is up to date.
    echo ==========================================
) else (
    echo ==========================================
    echo   Migration failed. Contact the developer.
    echo ==========================================
)

echo.
pause
