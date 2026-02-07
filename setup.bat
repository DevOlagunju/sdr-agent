@echo off
echo ========================================
echo SDR Agent Setup Script
echo ========================================
echo.

echo Step 1: Setting up Backend...
echo ----------------------------------------
cd backend

echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo ⚠️  IMPORTANT: Your .env file has been created with your Anthropic API key!
echo   Location: backend\.env
echo   You can add TAVILY_API_KEY if you want production search (optional)
echo.
pause

echo Initializing database...
python init_db.py

cd ..

echo.
echo Step 2: Setting up Frontend...
echo ----------------------------------------
cd frontend

echo Installing Node.js dependencies...
call npm install

cd ..

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start the backend: cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo 2. Start the frontend: cd frontend ^&^& npm run dev
echo 3. Open http://localhost:3000
echo.
echo Your Anthropic API key is already configured!
echo.
pause
