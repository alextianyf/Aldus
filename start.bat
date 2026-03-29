@echo off
echo Starting Aldus...

:: Start backend in a separate window
start "Aldus Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000"

:: Wait for backend to boot
timeout /t 3 /nobreak >nul

:: Open browser
start http://localhost:5173

:: Start frontend (this window stays open — closing it stops the frontend)
cd /d %~dp0frontend
call npm run dev
