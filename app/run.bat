@echo off
setlocal
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" (
  echo Virtual environment missing. Run setup.bat first.
  pause
  exit /b 1
)
if not exist ".env" (
  echo .env missing. Copy .env.example to .env and configure it.
  pause
  exit /b 1
)
call "venv\Scripts\activate.bat"
python app.py
pause
