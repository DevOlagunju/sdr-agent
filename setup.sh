#!/bin/bash

echo "========================================"
echo "SDR Agent Setup Script"
echo "========================================"
echo ""

echo "Step 1: Setting up Backend..."
echo "----------------------------------------"
cd backend

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✅  Your .env file has been created with your Anthropic API key!"
echo "   Location: backend/.env"
echo "   You can add TAVILY_API_KEY if you want production search (optional)"
echo ""
read -p "Press enter to continue..."

echo "Initializing database..."
python init_db.py

cd ..

echo ""
echo "Step 2: Setting up Frontend..."
echo "----------------------------------------"
cd frontend

echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Start the backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Open http://localhost:3000"
echo ""
echo "✅ Your Anthropic API key is already configured!"
echo ""
