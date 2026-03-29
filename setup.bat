@echo off
echo ============================================
echo  Aldus - First Time Setup
echo ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python from https://python.org
    pause
    exit /b 1
)

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo [1/3] Setting up Python backend...
cd backend
python -m venv venv --system-site-packages
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

echo.
echo [2/3] Installing frontend dependencies...
cd frontend
call npm install
cd ..

echo.
echo [3/3] Done!
echo.
echo Run start.bat to launch Aldus.
echo.
pause
