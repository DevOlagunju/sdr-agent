from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from database import init_db, get_db, Lead, Email
from agent import run_sdr_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_db()
    print("Database initialized")
    yield
    print("Shutting down")


app = FastAPI(
    title="SDR Agent API",
    description="AI-powered Sales Development Representative with LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ResearchRequest(BaseModel):
    company_domain: str


class ResearchResponse(BaseModel):
    company_domain: str
    research: dict
    lead: dict
    email: dict
    status: str


class LeadResponse(BaseModel):
    id: int
    company_domain: str
    company_name: str
    industry: Optional[str]
    description: Optional[str]
    research_summary: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class EmailResponse(BaseModel):
    id: int
    lead_id: int
    subject: str
    body: str
    status: str
    created_at: str
    sent_at: Optional[str]

    class Config:
        from_attributes = True


# Routes
@app.get("/")
async def root():
    return {
        "message": "SDR Agent API",
        "version": "1.0.0",
        "endpoints": {
            "research": "/api/research",
            "leads": "/api/leads",
            "emails": "/api/emails"
        }
    }


@app.post("/api/research", response_model=ResearchResponse)
async def research_company(request: ResearchRequest):
    """
    Research a company and generate outreach email.
    This endpoint orchestrates the entire SDR workflow:
    1. Research the company
    2. Save to CRM
    3. Generate personalized email
    4. Mock-send the email
    """
    try:
        result = await run_sdr_agent(request.company_domain)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads", response_model=List[LeadResponse])
async def get_leads(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all leads from CRM"""
    result = await db.execute(
        select(Lead).offset(skip).limit(limit).order_by(Lead.created_at.desc())
    )
    leads = result.scalars().all()
    
    return [
        LeadResponse(
            id=lead.id,
            company_domain=lead.company_domain,
            company_name=lead.company_name,
            industry=lead.industry,
            description=lead.description,
            research_summary=lead.research_summary,
            created_at=str(lead.created_at),
            updated_at=str(lead.updated_at)
        )
        for lead in leads
    ]


@app.get("/api/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific lead by ID"""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return LeadResponse(
        id=lead.id,
        company_domain=lead.company_domain,
        company_name=lead.company_name,
        industry=lead.industry,
        description=lead.description,
        research_summary=lead.research_summary,
        created_at=str(lead.created_at),
        updated_at=str(lead.updated_at)
    )


@app.get("/api/emails", response_model=List[EmailResponse])
async def get_emails(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get all emails"""
    result = await db.execute(
        select(Email).offset(skip).limit(limit).order_by(Email.created_at.desc())
    )
    emails = result.scalars().all()
    
    return [
        EmailResponse(
            id=email.id,
            lead_id=email.lead_id,
            subject=email.subject,
            body=email.body,
            status=email.status,
            created_at=str(email.created_at),
            sent_at=str(email.sent_at) if email.sent_at else None
        )
        for email in emails
    ]


@app.get("/api/leads/{lead_id}/emails", response_model=List[EmailResponse])
async def get_lead_emails(lead_id: int, db: AsyncSession = Depends(get_db)):
    """Get all emails for a specific lead"""
    result = await db.execute(
        select(Email).where(Email.lead_id == lead_id).order_by(Email.created_at.desc())
    )
    emails = result.scalars().all()
    
    return [
        EmailResponse(
            id=email.id,
            lead_id=email.lead_id,
            subject=email.subject,
            body=email.body,
            status=email.status,
            created_at=str(email.created_at),
            sent_at=str(email.sent_at) if email.sent_at else None
        )
        for email in emails
    ]


@app.delete("/api/leads/{lead_id}")
async def delete_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a lead"""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    await db.delete(lead)
    await db.commit()
    
    return {"status": "deleted", "lead_id": lead_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
