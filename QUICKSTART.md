# Quick Start Guide

Get your SDR Agent running in 5 minutes!

## Prerequisites

- Python 3.9+
- Node.js 18+
- Anthropic API key

## Setup (Windows)

### 1. Clone and Setup

Run the automated setup script:

```bash
setup.bat
```

This will:
- Create Python virtual environment
- Install Python dependencies
- Install Node.js dependencies
- Initialize the database

### 2. Configure API Keys

Create `backend/.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
TAVILY_API_KEY=tvly-optional-tavily-key
DATABASE_URL=sqlite+aiosqlite:///./crm.db
```

**Get your Anthropic API key**: https://console.anthropic.com/

### 3. Start Backend

In one terminal:

```bash
run-backend.bat
```

Or manually:

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

Backend will start at: http://localhost:8000
API docs: http://localhost:8000/docs

### 4. Start Frontend

In another terminal:

```bash
run-frontend.bat
```

Or manually:

```bash
cd frontend
npm run dev
```

Frontend will start at: http://localhost:3000

## Setup (Mac/Linux)

### 1. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

### 2. Configure API Keys

Create `backend/.env` file with your keys (same as Windows above)

### 3. Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 4. Start Frontend

```bash
cd frontend
npm run dev
```

## Using the Agent

1. Open http://localhost:3000
2. Enter a company domain (try "openai.com" or "stripe.com")
3. Click "🚀 Research & Generate Email"
4. Watch the agent:
   - Research the company
   - Save to CRM
   - Generate personalized email
   - Mock-send the email
5. Click "📋 View CRM" to see all leads

## Testing the API Directly

### Research a Company

```bash
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"company_domain": "openai.com"}'
```

### Get All Leads

```bash
curl http://localhost:8000/api/leads
```

### Get All Emails

```bash
curl http://localhost:8000/api/emails
```

## Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError`
**Fix**: Make sure virtual environment is activated and dependencies are installed:
```bash
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**Error**: `pydantic_settings not found`
**Fix**: Install pydantic-settings:
```bash
pip install pydantic-settings
```

### Frontend won't start

**Error**: `Cannot find module`
**Fix**: Install dependencies:
```bash
cd frontend
npm install
```

### Database errors

**Fix**: Reinitialize the database:
```bash
cd backend
venv\Scripts\activate
python init_db.py
```

### CORS errors

**Fix**: Make sure:
- Backend is running on port 8000
- Frontend is running on port 3000
- Both are on localhost

### Anthropic API errors

**Error**: `Invalid API key`
**Fix**: Check your `.env` file has the correct Anthropic key

**Error**: `Rate limit exceeded`
**Fix**: Wait a moment or check your Anthropic plan limits

## Architecture

```
User → Next.js Frontend → FastAPI Backend → LangGraph Agent
                                             ↓
                                    [ResearchTool, CRMTool, EmailTool]
                                             ↓
                                        SQLite CRM
```

## What's Happening Behind the Scenes?

When you submit a company domain:

1. **Frontend** sends POST request to backend
2. **Backend** initializes LangGraph agent
3. **Agent** executes workflow:
   - Calls **ResearchTool** to gather company info
   - Calls **CRMTool** to save lead to database
   - Uses **Claude 3.5 Sonnet** to generate personalized email
   - Calls **EmailTool** to save and "send" email
4. **Results** returned to frontend and displayed

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive
- Check [README.md](README.md) for full documentation
- Review [FILE_STRUCTURE.md](FILE_STRUCTURE.md) for complete file reference
- Explore the code:
  - `backend/agent.py` - LangGraph orchestration
  - `backend/tools.py` - Tool implementations
  - `frontend/src/app/page.tsx` - UI component

## Example Companies to Try

- openai.com
- stripe.com
- anthropic.com
- langchain.com
- vercel.com

The system includes mock data for openai.com and stripe.com, but will work with any domain!

## Support

Issues? Questions?
- Check the API docs: http://localhost:8000/docs
- Review logs in terminal where backend is running
- Ensure all environment variables are set correctly
