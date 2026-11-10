@echo off
setlocal
cd /d "%~dp0"
echo ===============================================
echo   MS College Events - First-time Setup
echo ===============================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher not found. Install Python 3.12 from python.org and enable PATH.
  pause
  exit /b 1
)
if not exist "venv\Scripts\python.exe" (
  py -3.12 -m venv venv
  if errorlevel 1 (
    echo Python 3.12 was not found. Install Python 3.12, then rerun setup.bat.
    pause
    exit /b 1
  )
)
call "venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist ".env" copy ".env.example" ".env"
echo.
echo Setup complete.
echo 1. Start MySQL in XAMPP.
echo 2. Review your .env database settings.
echo 3. Run run.bat.
pause
