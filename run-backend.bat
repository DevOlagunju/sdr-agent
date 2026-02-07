@echo off
echo Starting SDR Agent Backend...
echo ========================================
cd backend
call venv\Scripts\activate
echo Backend running at http://localhost:8000
echo API docs at http://localhost:8000/docs
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
