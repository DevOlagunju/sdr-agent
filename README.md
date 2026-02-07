# SDR Agent with LangGraph

An intelligent Sales Development Representative agent that researches companies and manages CRM operations using LangGraph orchestration.

## 🎯 Features

- **🔍 Company Research**: Automatically researches companies using web search
- **✉️ Email Generation**: Creates personalized outreach emails based on research findings
- **💾 CRM Integration**: Saves leads and tracks email campaigns in SQLite database
- **🤖 LangGraph Orchestration**: Intelligent agent workflow with multiple specialized tools
- **🎨 Modern UI**: Beautiful Next.js frontend with Tailwind CSS
- **⚡ Fast API**: High-performance FastAPI backend with async support

## 🏗️ Tech Stack

### Backend
- **Python 3.9+** - Core language
- **FastAPI** - Modern async web framework
- **LangGraph** - Agent orchestration and workflow
- **LangChain** - Tool abstractions and LLM integration
- **Anthropic Claude 3.5 Sonnet** - Email generation and reasoning
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Lightweight CRM database

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API keys
# Copy .env.example to .env and add your keys

# Initialize database
python init_db.py

# Start the backend server
uvicorn main:app --reload
```

Backend runs at: **http://localhost:8000**  
API docs at: **http://localhost:8000/docs**

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Frontend runs at: **http://localhost:3000**

## 🔑 Environment Variables

Create a `.env` file in the `backend` directory:

```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
TAVILY_API_KEY=tvly-optional-tavily-key-for-better-search
DATABASE_URL=sqlite+aiosqlite:///./crm.db
```

**Required:**
- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com/)

**Optional:**
- `TAVILY_API_KEY` - For production-grade web search ([Tavily](https://tavily.com))

## 📖 Usage

1. **Start the Backend** (see setup above)
2. **Start the Frontend** (see setup above)
3. **Open your browser** to http://localhost:3000
4. **Enter a company domain** (e.g., `openai.com`, `stripe.com`)
5. **Click "🚀 Research & Generate Email"**
6. **Watch the magic happen**:
   - Agent researches the company
   - Saves lead to CRM
   - Generates personalized email
   - Mock-sends the email
7. **View CRM** by clicking "📋 View CRM" to see all leads

### Try These Example Domains

- `openai.com` - AI research company (has mock data)
- `stripe.com` - Payment processing (has mock data)
- `anthropic.com` - AI safety company
- Any other `.com` domain!

## 🏛️ Architecture

### LangGraph Agent Workflow

```
User Input (Domain)
      ↓
┌─────────────────┐
│  Research Node  │ ← ResearchTool
└────────┬────────┘
         ↓
┌─────────────────┐
│ Save to CRM Node│ ← CRMTool
└────────┬────────┘
         ↓
┌─────────────────┐
│Generate Email   │ ← GPT-4 LLM
└────────┬────────┘
         ↓
┌─────────────────┐
│  Send Email Node│ ← EmailTool
└────────┬────────┘
         ↓
      Results
```

### Tools

1. **ResearchTool** (`backend/tools.py`)
   - Searches web for company information
   - Returns structured data (name, industry, description, highlights)
   - Mock implementation included; easily extensible with Tavily API

2. **CRMTool** (`backend/tools.py`)
   - Performs CRUD operations on leads
   - Creates or updates lead records
   - Stores research data in SQLite

3. **EmailTool** (`backend/tools.py`)
   - Saves generated emails to database
   - Marks emails as "sent" (mock sending)
   - Tracks email history per lead

### API Endpoints

- `POST /api/research` - Research company and generate email
- `GET /api/leads` - List all leads
- `GET /api/leads/{id}` - Get specific lead
- `GET /api/emails` - List all emails
- `GET /api/leads/{id}/emails` - Get emails for a lead
- `DELETE /api/leads/{id}` - Delete a lead

Full API documentation available at: http://localhost:8000/docs

## 🧪 Testing

### Test the Backend API

```bash
cd backend
python test_api.py
```

This runs automated tests for all endpoints.

### Manual API Testing

```bash
# Research a company
curl -X POST http://localhost:8000/api/research \
  -H "Content-Type: application/json" \
  -d '{"company_domain": "openai.com"}'

# Get all leads
curl http://localhost:8000/api/leads

# Get all emails
curl http://localhost:8000/api/emails
```

## 📁 Project Structure

```
SDR/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── agent.py             # LangGraph agent orchestration
│   ├── tools.py             # Tool implementations
│   ├── database.py          # SQLAlchemy models
│   ├── config.py            # Configuration
│   ├── init_db.py           # Database initialization
│   ├── test_api.py          # API tests
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variables template
│   ├── .env                 # Environment variables (create this)
│   └── crm.db               # SQLite database (created on init)
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx     # Main UI component
│   │       ├── layout.tsx   # Root layout
│   │       └── globals.css  # Global styles
│   ├── package.json         # Node dependencies
│   ├── package-lock.json    # Locked dependencies
│   ├── tsconfig.json        # TypeScript config
│   ├── tailwind.config.ts   # Tailwind config
│   ├── postcss.config.js    # PostCSS config
│   ├── next.config.js       # Next.js config
│   ├── .eslintrc.json       # ESLint config
│   └── .gitignore           # Frontend-specific git ignores
│
├── .gitignore               # Root git ignore
├── README.md                # This file
├── QUICKSTART.md            # Quick start guide
├── ARCHITECTURE.md          # Detailed architecture docs
├── PROJECT_SUMMARY.md       # Project overview
├── SETUP_COMPLETE.md        # Setup completion guide
├── setup.bat                # Windows setup script
├── setup.sh                 # Mac/Linux setup script
├── run-backend.bat          # Windows backend runner
└── run-frontend.bat         # Windows frontend runner
```

## 🎓 Learning Resources

- **LangGraph Documentation**: https://langchain-ai.github.io/langgraph/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs

## 🔧 Customization

### Adding New Tools

See `backend/tools.py` for examples. Each tool extends `BaseTool`:

```python
class YourTool(BaseTool):
    name: str = "your_tool"
    description: str = "What it does"
    args_schema: Type[BaseModel] = YourToolInput
    
    async def _arun(self, **kwargs) -> str:
        # Implementation
        pass
```

### Integrating Real Search

Replace mock search in `ResearchTool` with Tavily:

```python
from tavily import TavilyClient

client = TavilyClient(api_key=settings.tavily_api_key)
results = client.search(query)
```

### Customizing Email Templates

Modify the prompt in `agent.py` → `generate_email_node()`

## 🐛 Troubleshooting

See [QUICKSTART.md](QUICKSTART.md#troubleshooting) for common issues and solutions.

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - Get started in 5 minutes
- [ARCHITECTURE.md](ARCHITECTURE.md) - Deep dive into the system design
- [FILE_STRUCTURE.md](FILE_STRUCTURE.md) - Complete file-by-file reference
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview and summary

## 🚀 Production Considerations

Before deploying to production:

1. **Security**: Add authentication, rate limiting, input validation
2. **Database**: Migrate to PostgreSQL or MySQL
3. **Search**: Integrate Tavily or similar production search API
4. **Email**: Integrate with SendGrid, AWS SES, or similar
5. **Monitoring**: Add logging, error tracking (Sentry)
6. **Caching**: Add Redis for research results
7. **Deployment**: Use Docker, deploy to AWS/GCP/Azure

## 🤝 Contributing

This is a demonstration project showing LangGraph orchestration in action. Feel free to:

- Add more tools
- Improve the UI
- Enhance email generation
- Add new features

## 📝 License

MIT License - feel free to use this for learning or as a starting point for your projects!

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) by LangChain
- Powered by [Anthropic Claude](https://www.anthropic.com/)
- UI inspired by modern SaaS applications
- Created for demonstrating agent orchestration patterns
