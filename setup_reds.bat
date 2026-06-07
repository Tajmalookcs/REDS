@echo off
cd /d "%~dp0"

echo ================================
echo   REDS Project Setup
echo ================================
echo.

:: Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed! Please install Git first.
    pause
    exit
)

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed! Please install Python first.
    pause
    exit
)

:: Clone the repository
echo [1/6] Cloning repository...
git clone https://github.com/Tajmalookcs/REDS.git
if %errorlevel% neq 0 (
    echo [ERROR] Failed to clone repository!
    pause
    exit
)
cd REDS

:: Create virtual environment
echo [2/6] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment!
    pause
    exit
)

:: Activate virtual environment
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat

:: Install requirements
echo [4/6] Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements!
    pause
    exit
)

:: Run migrations
echo [5/6] Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Migration failed!
    pause
    exit
)

:: Seed accounts
echo [6/6] Seeding accounts...
python manage.py seed_accounts
if %errorlevel% neq 0 (
    echo [WARNING] seed_accounts failed. Continuing...
)

echo.
echo ================================
echo   Setup Complete!
echo ================================
echo.
echo Now create superuser:
echo.
python manage.py createsuperuser

echo.
echo Setup done! Run start_reds.bat to launch the app.
echo.
pause
