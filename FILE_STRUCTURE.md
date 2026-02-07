# SDR Agent - Complete File Structure

This document provides a comprehensive overview of every file in the project and its purpose.

## Project Root: `SDR/`

```
SDR/
├── backend/                 # Python FastAPI backend
├── frontend/                # Next.js React frontend
├── .gitignore              # Git ignore rules
├── README.md               # Main project documentation
├── QUICKSTART.md           # 5-minute quick start guide
├── ARCHITECTURE.md         # Technical architecture details
├── PROJECT_SUMMARY.md      # Project overview and summary
├── SETUP_COMPLETE.md       # Setup completion guide
├── FILE_STRUCTURE.md       # This file
├── setup.bat               # Windows automated setup script
├── setup.sh                # Mac/Linux automated setup script
├── run-backend.bat         # Windows backend launcher
└── run-frontend.bat        # Windows frontend launcher
```

---

## Backend Directory: `backend/`

### Core Application Files

#### `main.py` - FastAPI Application
**Purpose**: Main FastAPI application with all API endpoints

**Key Features**:
- REST API endpoints for research, leads, emails
- CORS configuration for frontend communication
- Database session management
- Error handling and validation

**Endpoints**:
- `GET /` - API info and health check
- `POST /api/research` - Trigger SDR agent workflow
- `GET /api/leads` - List all leads
- `GET /api/leads/{id}` - Get specific lead details
- `DELETE /api/leads/{id}` - Delete a lead
- `GET /api/emails` - List all sent emails
- `GET /api/leads/{id}/emails` - Get emails for specific lead

**Dependencies**: FastAPI, SQLAlchemy, agent.py, database.py

---

#### `agent.py` - LangGraph Agent Orchestration
**Purpose**: Implements the LangGraph state machine for SDR workflow

**Key Components**:
- `AgentState` - TypedDict defining agent state structure
- `research_node()` - Executes company research
- `save_to_crm_node()` - Saves lead to database
- `generate_email_node()` - Generates email using Claude
- `send_email_node()` - Saves and mock-sends email
- `route_next_step()` - Conditional routing logic
- `create_agent_graph()` - Builds and compiles StateGraph
- `run_agent()` - Main entry point to execute agent

**Workflow**:
```
START → research → save_to_crm → generate_email → send_email → END
```

**Dependencies**: LangGraph, LangChain, Anthropic Claude, tools.py

---

#### `tools.py` - Tool Implementations
**Purpose**: Defines all tools used by the LangGraph agent

**Tools**:

1. **ResearchTool**
   - Input: Company domain (e.g., "openai.com")
   - Action: Web search for company information
   - Output: JSON with name, industry, description, highlights
   - Current: Mock implementation with sample data
   - Extensible: Can integrate Tavily API

2. **CRMTool**
   - Input: Company details from research
   - Action: Create or update lead in SQLite database
   - Output: Lead ID and creation/update status
   - Operations: Upsert (create if new, update if exists)

3. **EmailTool**
   - Input: Lead ID, email subject, email body
   - Action: Save email to database, mark as "sent"
   - Output: Email ID and sent status
   - Current: Mock sending (no actual email sent)
   - Extensible: Can integrate SendGrid, AWS SES

**Base Class**: All tools extend `BaseTool` from LangChain

**Dependencies**: LangChain, Pydantic, database.py

---

#### `database.py` - SQLAlchemy Models
**Purpose**: Database schema and ORM models

**Models**:

1. **Lead**
   - `id`: Integer, Primary Key
   - `company_domain`: String, Unique, Indexed
   - `company_name`: String
   - `industry`: String, Nullable
   - `description`: Text, Nullable
   - `research_summary`: Text, Nullable
   - `created_at`: DateTime
   - `updated_at`: DateTime
   - Relationship: One-to-many with Email

2. **Email**
   - `id`: Integer, Primary Key
   - `lead_id`: Integer, Foreign Key to Lead
   - `subject`: String
   - `body`: Text
   - `status`: String (draft/sent/failed)
   - `created_at`: DateTime
   - `sent_at`: DateTime, Nullable
   - Relationship: Many-to-one with Lead

**Functions**:
- `get_db()` - Async context manager for database sessions
- `init_db()` - Creates all tables

**Database**: SQLite with async support (aiosqlite)

**Dependencies**: SQLAlchemy, aiosqlite

---

#### `config.py` - Configuration Management
**Purpose**: Environment variables and application configuration

**Settings** (via Pydantic BaseSettings):
- `anthropic_api_key`: Required for Claude API
- `tavily_api_key`: Optional for web search
- `database_url`: SQLite database connection string

**Environment File**: Loads from `backend/.env`

**Dependencies**: pydantic-settings

---

#### `init_db.py` - Database Initialization
**Purpose**: Script to create database tables

**Usage**:
```bash
cd backend
python init_db.py
```

**Action**: Creates `crm.db` with Lead and Email tables

**Dependencies**: asyncio, database.py

---

#### `test_api.py` - API Test Suite
**Purpose**: Automated tests for all API endpoints

**Tests**:
- API health check
- Research endpoint (full workflow)
- Lead retrieval
- Email retrieval

**Usage**:
```bash
cd backend
python test_api.py
```

**Dependencies**: requests, json

---

### Configuration Files

#### `requirements.txt` - Python Dependencies
**Purpose**: List of all Python packages required

**Key Packages**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `langchain` - LLM framework
- `langchain-anthropic` - Anthropic integration
- `langgraph` - Agent orchestration
- `anthropic` - Claude API client
- `sqlalchemy` - ORM
- `aiosqlite` - Async SQLite driver
- `pydantic-settings` - Config management
- `python-dotenv` - Environment variables

---

#### `.env.example` - Environment Template
**Purpose**: Template for environment variables

**Contents**:
```env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
TAVILY_API_KEY=tvly-optional-tavily-key
DATABASE_URL=sqlite+aiosqlite:///./crm.db
```

**Note**: Copy to `.env` and add actual keys

---

#### `.env` - Environment Variables (User Created)
**Purpose**: Stores sensitive API keys and configuration

**Security**: 
- Never commit to git (.gitignore includes this)
- Required for application to run

---

### Generated Files

#### `crm.db` - SQLite Database
**Purpose**: Stores all leads and emails

**Created By**: `init_db.py`

**Tables**: leads, emails

**Location**: `backend/crm.db`

---

#### `venv/` - Python Virtual Environment
**Purpose**: Isolated Python environment for dependencies

**Created By**: `python -m venv venv` or setup script

**Platform-Specific**:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

---

## Frontend Directory: `frontend/`

### Source Code: `src/app/`

#### `page.tsx` - Main Application Component
**Purpose**: Primary UI for SDR agent interaction

**Features**:
- Company domain input form
- Research & generate button
- Real-time loading states
- Research results display
- Generated email preview
- CRM leads viewer
- Responsive design
- Error handling

**Key Functions**:
- `handleResearch()` - Calls backend research endpoint
- `fetchLeads()` - Retrieves all leads from CRM
- State management with React hooks

**Tech**: React, TypeScript, Tailwind CSS

---

#### `layout.tsx` - Root Layout
**Purpose**: Root layout component for Next.js App Router

**Includes**:
- HTML document structure
- Metadata configuration
- Font optimization (Inter)
- Global styles import
- Child component wrapper

**Tech**: Next.js 14 App Router

---

#### `globals.css` - Global Styles
**Purpose**: Global CSS with Tailwind directives

**Includes**:
- Tailwind base styles
- Tailwind components
- Tailwind utilities
- Custom CSS (if any)

**Tech**: CSS, Tailwind CSS

---

### Configuration Files

#### `package.json` - Node Dependencies
**Purpose**: NPM package configuration and scripts

**Scripts**:
- `dev` - Start development server
- `build` - Build for production
- `start` - Start production server
- `lint` - Run ESLint

**Dependencies**:
- `next` - React framework
- `react` - UI library
- `react-dom` - React DOM renderer
- `typescript` - Type checking
- `axios` - HTTP client

**Dev Dependencies**:
- `@types/node` - Node.js types
- `@types/react` - React types
- `tailwindcss` - Utility-first CSS
- `postcss` - CSS processing
- `eslint` - Code linting
- `autoprefixer` - CSS vendor prefixes

---

#### `package-lock.json` - Locked Dependencies
**Purpose**: Locks exact versions of all dependencies

**Generated By**: `npm install`

**Use**: Ensures consistent installs across environments

---

#### `tsconfig.json` - TypeScript Configuration
**Purpose**: TypeScript compiler options

**Key Settings**:
- Target: ES5+
- Module: ESNext
- JSX: preserve (for React)
- Strict type checking
- Path aliases (`@/*`)

---

#### `next.config.js` - Next.js Configuration
**Purpose**: Next.js framework configuration

**Potential Settings**:
- API routes
- Rewrites/redirects
- Image optimization
- Environment variables

---

#### `tailwind.config.ts` - Tailwind Configuration
**Purpose**: Tailwind CSS customization

**Includes**:
- Content paths for purging
- Theme extensions
- Custom colors/fonts
- Plugin configuration

---

#### `postcss.config.js` - PostCSS Configuration
**Purpose**: PostCSS plugin configuration

**Plugins**:
- `tailwindcss` - Processes Tailwind
- `autoprefixer` - Adds vendor prefixes

---

#### `.eslintrc.json` - ESLint Configuration
**Purpose**: JavaScript/TypeScript linting rules

**Extends**: `next/core-web-vitals`

**Enforces**: Next.js best practices

---

#### `.gitignore` - Frontend Git Ignore
**Purpose**: Specifies untracked files for frontend

**Ignores**:
- `node_modules/`
- `.next/`
- `out/`
- `*.log`
- `.env*.local`

---

## Root Configuration Files

### `.gitignore` - Root Git Ignore
**Purpose**: Specifies untracked files for entire project

**Ignores**:
- Python: `venv/`, `__pycache__/`, `*.pyc`, `*.db`
- Node: `node_modules/`, `.next/`
- Environment: `.env`
- IDE: `.vscode/`, `.idea/`
- OS: `.DS_Store`, `Thumbs.db`

---

## Documentation Files

### `README.md` - Main Documentation
**Purpose**: Comprehensive project overview

**Sections**:
- Features and tech stack
- Quick start guide
- Installation instructions
- Usage examples
- API endpoints
- Architecture overview
- File structure
- Testing guide
- Customization tips
- Troubleshooting
- Production considerations

**Audience**: Developers and users

---

### `QUICKSTART.md` - Quick Start Guide
**Purpose**: Get up and running in 5 minutes

**Sections**:
- Prerequisites
- Setup steps (Windows/Mac/Linux)
- Configuration
- Starting servers
- First test
- Troubleshooting

**Audience**: New users

---

### `ARCHITECTURE.md` - Technical Architecture
**Purpose**: Deep dive into system design

**Sections**:
- Architecture diagram
- Component breakdown
- Data flow
- Technology stack
- Extensibility guide
- MCP integration notes
- Performance considerations
- Security notes
- Future enhancements

**Audience**: Technical developers

---

### `PROJECT_SUMMARY.md` - Project Overview
**Purpose**: High-level project summary

**Sections**:
- What was built
- Requirements checklist
- Key features
- File inventory
- Demo flow
- Testing guide
- Customization examples
- Database schema
- Learning points
- Production readiness

**Audience**: Stakeholders, reviewers

---

### `SETUP_COMPLETE.md` - Setup Guide
**Purpose**: Post-setup instructions

**Sections**:
- What's configured
- Next steps
- Quick test
- Why Claude?
- Troubleshooting

**Audience**: Users who just configured API keys

---

### `FILE_STRUCTURE.md` - This Document
**Purpose**: Complete file reference guide

**Sections**:
- Directory structure
- File-by-file explanations
- Purpose and dependencies
- Usage instructions

**Audience**: Developers exploring the codebase

---

## Setup Scripts

### `setup.bat` - Windows Setup
**Purpose**: Automated setup for Windows

**Actions**:
1. Creates Python virtual environment
2. Activates venv
3. Installs Python dependencies
4. Initializes database
5. Installs Node.js dependencies

**Usage**: Double-click or run `setup.bat`

---

### `setup.sh` - Mac/Linux Setup
**Purpose**: Automated setup for Mac/Linux

**Actions**: Same as setup.bat but for Unix systems

**Usage**: 
```bash
chmod +x setup.sh
./setup.sh
```

---

### `run-backend.bat` - Windows Backend Launcher
**Purpose**: Quick backend startup for Windows

**Actions**:
1. Navigates to backend directory
2. Activates virtual environment
3. Starts uvicorn server

**Usage**: Double-click or run `run-backend.bat`

---

### `run-frontend.bat` - Windows Frontend Launcher
**Purpose**: Quick frontend startup for Windows

**Actions**:
1. Navigates to frontend directory
2. Starts Next.js dev server

**Usage**: Double-click or run `run-frontend.bat`

---

## File Count Summary

**Total Files**: 30+ core files

**By Category**:
- Backend Python: 8 files
- Frontend TypeScript/JavaScript: 3 source files
- Configuration: 12 files
- Documentation: 6 files
- Scripts: 4 files

**By Type**:
- Python (`.py`): 8
- TypeScript/React (`.tsx`, `.ts`): 3
- JavaScript (`.js`): 3
- JSON (`.json`): 4
- Markdown (`.md`): 6
- CSS (`.css`): 1
- Text (`.txt`): 1
- Batch/Shell (`.bat`, `.sh`): 4
- Environment (`.env*`): 2

---

## Dependencies Graph

```
Frontend (Next.js)
    ↓ HTTP Requests
Backend (FastAPI)
    ↓ Calls
LangGraph Agent
    ↓ Uses
Tools (Research, CRM, Email)
    ↓ Reads/Writes
SQLite Database (crm.db)
```

---

## Key File Relationships

1. **Agent Workflow**:
   - `main.py` → calls → `agent.py`
   - `agent.py` → uses → `tools.py`
   - `tools.py` → accesses → `database.py`

2. **Configuration**:
   - `config.py` → reads → `.env`
   - `agent.py` → imports → `config.py`
   - `tools.py` → imports → `config.py`

3. **Database**:
   - `database.py` → defines → models
   - `init_db.py` → creates → `crm.db`
   - `main.py` → queries → `crm.db`

4. **Frontend-Backend**:
   - `page.tsx` → fetches → `main.py` endpoints
   - `layout.tsx` → wraps → `page.tsx`
   - `globals.css` → styles → all components

---

## Entry Points

**Backend**:
- Start: `uvicorn main:app --reload`
- Entry: `main.py`
- Port: 8000

**Frontend**:
- Start: `npm run dev`
- Entry: `src/app/page.tsx`
- Port: 3000

**Database**:
- Initialize: `python init_db.py`
- File: `crm.db`

**Tests**:
- Run: `python test_api.py`
- Entry: `test_api.py`

---

## Generated/Ignored Files

These files are created during setup/runtime and not committed to git:

**Backend**:
- `venv/` - Virtual environment
- `crm.db` - Database file
- `.env` - API keys
- `__pycache__/` - Python bytecode
- `*.pyc` - Compiled Python

**Frontend**:
- `node_modules/` - NPM packages
- `.next/` - Next.js build cache
- `out/` - Production build
- `*.log` - Log files

---

## Quick Reference

**Want to...**

- **Understand the agent workflow?** → Read `agent.py`
- **Add a new tool?** → Edit `tools.py`
- **Change database schema?** → Modify `database.py`
- **Add API endpoint?** → Update `main.py`
- **Customize UI?** → Edit `page.tsx`
- **Change styling?** → Modify `globals.css` or `tailwind.config.ts`
- **Configure environment?** → Edit `.env`
- **Run tests?** → Execute `test_api.py`

---

## Version Control

**Tracked** (committed to git):
- All source code files
- Configuration templates (`.env.example`)
- Documentation
- Setup scripts

**Untracked** (in .gitignore):
- Dependencies (`venv/`, `node_modules/`)
- Generated files (`.db`, build artifacts)
- Secrets (`.env`)
- IDE/OS files

---

This file structure enables a clean separation of concerns with:
- **Backend**: API and agent logic
- **Frontend**: User interface
- **Documentation**: Comprehensive guides
- **Scripts**: Easy setup and running

Each file has a single, clear responsibility, making the codebase easy to understand and extend.
