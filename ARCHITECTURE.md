# SDR Agent Architecture

## Overview

This SDR (Sales Development Representative) Agent is an AI-powered system that automates the process of researching companies, managing leads in a CRM, and generating personalized outreach emails.

## Architecture Diagram

```
┌─────────────────┐         ┌──────────────────────┐
│                 │         │                      │
│  Next.js        │ HTTP    │   FastAPI Backend    │
│  Frontend       ├────────►│                      │
│  (Port 3000)    │         │   (Port 8000)        │
│                 │         │                      │
└─────────────────┘         └──────────┬───────────┘
                                       │
                                       │
                            ┌──────────▼───────────┐
                            │                      │
                            │  LangGraph Agent     │
                            │  Orchestration       │
                            │                      │
                            └──────────┬───────────┘
                                       │
                    ┏──────────────────┼──────────────────┓
                    │                  │                  │
         ┌──────────▼──────┐ ┌────────▼──────┐ ┌────────▼──────┐
         │                 │ │               │ │               │
         │ ResearchTool    │ │   CRMTool     │ │   EmailTool   │
         │                 │ │               │ │               │
         └─────────────────┘ └───────┬───────┘ └───────┬───────┘
                                     │                 │
                                     │                 │
                              ┌──────▼─────────────────▼──┐
                              │                           │
                              │   SQLite Database         │
                              │   (CRM Storage)           │
                              │                           │
                              └───────────────────────────┘
```

## Component Breakdown

### 1. Frontend (Next.js + React + Tailwind)

**Location**: `frontend/`

**Purpose**: Provides a clean, modern UI for interacting with the SDR agent

**Key Features**:
- Company domain input form
- Real-time loading states
- Results display (research, email, CRM status)
- CRM leads viewer
- Responsive design with Tailwind CSS

**Main Files**:
- `src/app/page.tsx` - Main application component
- `src/app/layout.tsx` - Root layout
- `src/app/globals.css` - Global styles with Tailwind

### 2. Backend (FastAPI)

**Location**: `backend/`

**Purpose**: RESTful API that exposes the agent functionality

**Key Endpoints**:
- `POST /api/research` - Trigger the SDR agent workflow
- `GET /api/leads` - List all leads from CRM
- `GET /api/leads/{id}` - Get specific lead
- `GET /api/emails` - List all emails
- `GET /api/leads/{id}/emails` - Get emails for a lead
- `DELETE /api/leads/{id}` - Delete a lead

**Main Files**:
- `main.py` - FastAPI application and routes
- `config.py` - Configuration and environment variables
- `database.py` - SQLAlchemy models and database setup

### 3. LangGraph Agent Orchestration

**Location**: `backend/agent.py`

**Purpose**: Orchestrates the multi-step SDR workflow using LangGraph

**Workflow States**:
```
Entry (research) → save_to_crm → generate_email → send_email → END
```

**State Management**:
The agent maintains state including:
- `messages`: Conversation history
- `company_domain`: Target company
- `research_data`: Research results
- `lead_data`: CRM lead information
- `email_data`: Generated email content
- `next_step`: Current workflow position

**Nodes**:
1. **research_node**: Uses ResearchTool to gather company information
2. **save_to_crm_node**: Uses CRMTool to create/update lead
3. **generate_email_node**: Uses LLM to create personalized email
4. **send_email_node**: Uses EmailTool to save and mock-send email

**Conditional Edges**:
The agent uses `route_next_step()` to determine the next action based on the current state, enabling dynamic workflow control.

### 4. Tools

**Location**: `backend/tools.py`

#### ResearchTool
- **Purpose**: Research companies via web search
- **Input**: Company domain (e.g., "openai.com")
- **Output**: Structured company information (name, industry, description, highlights)
- **Implementation**: Currently uses mock data for demo; easily extendable with Tavily API or similar

#### CRMTool
- **Purpose**: Perform CRUD operations on leads
- **Operations**: Create/update leads in SQLite database
- **Input**: Company details from research
- **Output**: Lead ID and status

#### EmailTool
- **Purpose**: Save and send emails
- **Operations**: Create email records and mark as sent
- **Input**: Lead ID, subject, body
- **Output**: Email ID and sent status

### 5. Database (SQLite)

**Location**: `backend/crm.db` (created on init)

**Schema**:

**Leads Table**:
- `id` (Primary Key)
- `company_domain` (Unique)
- `company_name`
- `industry`
- `description`
- `research_summary`
- `created_at`
- `updated_at`

**Emails Table**:
- `id` (Primary Key)
- `lead_id` (Foreign Key)
- `subject`
- `body`
- `status` (draft/sent/failed)
- `created_at`
- `sent_at`

## Data Flow

### Complete SDR Workflow

1. **User Input**: User enters company domain in frontend
2. **API Request**: Frontend sends POST to `/api/research`
3. **Agent Initialization**: Backend initializes LangGraph agent with domain
4. **Research Phase**:
   - Agent calls ResearchTool
   - Tool searches for company information
   - Returns structured data
5. **CRM Phase**:
   - Agent calls CRMTool with research data
   - Tool creates/updates lead in database
   - Returns lead ID
6. **Email Generation Phase**:
   - Agent uses LLM (Claude 3.5 Sonnet) to generate personalized email
   - Email references specific research findings
   - Returns subject and body
7. **Email Sending Phase**:
   - Agent calls EmailTool
   - Tool saves email to database
   - Marks as "sent" (mock)
8. **Response**: Complete results returned to frontend
9. **Display**: Frontend shows research, CRM status, and generated email

## Key Technologies

### Backend Stack
- **FastAPI**: Modern async Python web framework
- **LangGraph**: Agent orchestration and workflow management
- **LangChain**: Tool abstractions and LLM integration
- **Anthropic Claude 3.5 Sonnet**: Email generation and reasoning
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Lightweight database for CRM

### Frontend Stack
- **Next.js 14**: React framework with App Router
- **React**: UI library
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **Axios**: HTTP client

## Extensibility

### Adding New Tools

To add a new tool to the agent:

1. Create tool class in `tools.py`:
```python
class NewTool(BaseTool):
    name: str = "new_tool_name"
    description: str = "What this tool does"
    args_schema: Type[BaseModel] = NewToolInput
    
    async def _arun(self, **kwargs) -> str:
        # Tool implementation
        pass
```

2. Add to agent in `agent.py`:
```python
new_tool = NewTool()
tools = [research_tool, crm_tool, email_tool, new_tool]
```

3. Create node if needed:
```python
async def new_tool_node(state: AgentState) -> AgentState:
    result = await new_tool._arun(...)
    # Update state
    return state
```

### Integrating Real Search API

Replace the mock search in `ResearchTool` with Tavily:

```python
from tavily import TavilyClient

async def _perform_search(self, domain: str, query: str):
    client = TavilyClient(api_key=settings.tavily_api_key)
    results = client.search(query)
    # Process and return structured data
```

### MCP Integration (Bonus)

The tool pattern used is compatible with Model Context Protocol (MCP). To convert a tool to MCP:

1. Define MCP server endpoint
2. Register tool schema
3. Handle tool invocations via MCP protocol
4. Return results in MCP format

Example structure:
```python
# mcp_server.py
from mcp import Server, Tool

server = Server("sdr-agent")

@server.tool("research_company")
async def research_company(domain: str) -> dict:
    return await research_tool._arun(domain)
```

## Environment Variables

Required in `backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-...  # Required
TAVILY_API_KEY=tvly-...              # Optional (for real search)
DATABASE_URL=sqlite+aiosqlite:///./crm.db
```

## Error Handling

- **API Errors**: FastAPI returns proper HTTP status codes
- **Tool Errors**: Tools return JSON with error field
- **Agent Errors**: Caught and returned to frontend
- **Database Errors**: Handled with try-catch and transactions

## Performance Considerations

- **Async/Await**: All I/O operations are async
- **Connection Pooling**: SQLAlchemy handles DB connections
- **Caching**: Can add Redis for research results
- **Rate Limiting**: Consider adding for production

## Security Notes

- API keys stored in `.env` (never commit)
- CORS configured for local development
- Input validation via Pydantic
- SQL injection prevented by ORM

## Future Enhancements

1. **Authentication**: Add user login and multi-tenancy
2. **Email Sending**: Integrate with SendGrid/AWS SES
3. **Advanced Search**: Use Tavily or Perplexity API
4. **Analytics**: Track email open rates, responses
5. **A/B Testing**: Test different email templates
6. **Scheduling**: Auto-send emails at optimal times
7. **Enrichment**: Integrate with Clearbit/Apollo
8. **Webhooks**: Notify on lead responses
9. **Export**: CSV/Excel export of leads
10. **Multi-agent**: Add specialized agents for different industries

## Additional Documentation

For more details, see:
- [FILE_STRUCTURE.md](FILE_STRUCTURE.md) - Complete file-by-file reference
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview
- [README.md](README.md) - Main documentation
