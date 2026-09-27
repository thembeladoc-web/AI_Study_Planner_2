@echo off
echo ==========================================
echo Timetable Planner - Setup Script
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    exit /b 1
)

echo [1/6] Creating Python virtual environment...
cd backend
python -m venv .venv

echo [2/6] Activating virtual environment...
call .venv\Scripts\activate

echo [3/6] Installing Python dependencies...
pip install -r requirements.txt

echo [4/6] Running database migrations...
python manage.py migrate

echo [5/6] Installing frontend dependencies...
cd ..\frontend
npm install

echo [6/6] Setup complete!
echo.
echo To start the application:
echo   1. Start backend: cd backend ^&^& .venv\Scripts\activate ^&^& python manage.py runserver
echo   2. Start frontend: cd frontend ^&^& npm start
echo.
pause
