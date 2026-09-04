@echo off
echo ===================================================
echo   Starting CutoffGrid AI (Backend + Frontend)
echo ===================================================

echo [1/2] Launching Backend on http://localhost:8000 ...
start "CutoffGrid Backend" cmd /k "cd backend && venv\Scripts\activate && python app.py"

echo [2/2] Launching Frontend on http://localhost:5173 ...
start "CutoffGrid Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers started!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://localhost:8000/docs
echo.
