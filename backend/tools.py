from langchain.tools import BaseTool
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel, Field
import httpx
import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import Lead, Email, async_session


# Research Tool Schema
class ResearchToolInput(BaseModel):
    company_domain: str = Field(description="The company domain to research (e.g., openai.com)")


class ResearchTool(BaseTool):
    name: str = "research_company"
    description: str = """
    Research a company by its domain. This tool searches the web for information about the company
    including its name, industry, products, recent news, and key highlights.
    Returns a structured summary of findings.
    """
    args_schema: Type[BaseModel] = ResearchToolInput
    
    async def _arun(self, company_domain: str) -> str:
        """Research a company using web search"""
        try:
            # Use a simple web search (in production, use Tavily or similar)
            search_query = f"{company_domain} company about products services"
            
            # Mock search results for demonstration
            # In production, integrate with Tavily API or similar
            research_data = await self._perform_search(company_domain, search_query)
            
            return json.dumps(research_data, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _run(self, company_domain: str) -> str:
        """Sync version (not used in async context)"""
        raise NotImplementedError("Use async version")
    
    async def _perform_search(self, domain: str, query: str) -> Dict[str, Any]:
        """Perform actual web search - this is a mock implementation"""
        # Mock implementation - in production, use real search API
        mock_data = {
            "openai.com": {
                "company_name": "OpenAI",
                "industry": "Artificial Intelligence",
                "description": "OpenAI is an AI research and deployment company focused on ensuring artificial general intelligence benefits all of humanity.",
                "products": ["ChatGPT", "GPT-4", "DALL-E", "Whisper"],
                "recent_news": "Leading advancements in AI with GPT-4 and ChatGPT",
                "key_highlights": [
                    "Pioneer in large language models",
                    "ChatGPT reached 100M users in 2 months",
                    "Partnership with Microsoft"
                ]
            },
            "stripe.com": {
                "company_name": "Stripe",
                "industry": "Financial Technology",
                "description": "Stripe is a technology company that builds economic infrastructure for the internet.",
                "products": ["Payment Processing", "Stripe Connect", "Stripe Atlas"],
                "recent_news": "Expanding global payment solutions",
                "key_highlights": [
                    "Processes billions in payments annually",
                    "Used by millions of businesses",
                    "Valued at $50B+"
                ]
            }
        }
        
        # Check if we have mock data for this domain
        if domain in mock_data:
            return mock_data[domain]
        
        # For unknown domains, try to extract company name from domain
        company_name = domain.replace('.com', '').replace('.io', '').replace('.ai', '').title()
        
        return {
            "company_name": company_name,
            "industry": "Technology",
            "description": f"{company_name} is a company operating in the technology sector.",
            "products": ["Product information not available"],
            "recent_news": "Limited information available",
            "key_highlights": [
                f"Domain: {domain}",
                "Further research recommended"
            ]
        }


# CRM Tool Schemas
class CRMCreateLeadInput(BaseModel):
    company_domain: str = Field(description="Company domain")
    company_name: str = Field(description="Company name")
    industry: str = Field(default="", description="Industry")
    description: str = Field(default="", description="Company description")
    research_summary: str = Field(default="", description="Research summary")


class CRMGetLeadInput(BaseModel):
    company_domain: str = Field(description="Company domain to look up")


class CRMTool(BaseTool):
    name: str = "crm_operations"
    description: str = """
    Perform CRM operations including creating, reading, updating leads.
    Operations:
    - create_lead: Save a new lead to the CRM with research data
    - get_lead: Retrieve an existing lead by company domain
    - update_lead: Update lead information
    """
    args_schema: Type[BaseModel] = CRMCreateLeadInput
    
    async def _arun(self, **kwargs) -> str:
        """Execute CRM operation"""
        try:
            async with async_session() as session:
                # Create or update lead
                result = await self._create_or_update_lead(session, kwargs)
                await session.commit()
                return json.dumps(result, default=str)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _run(self, **kwargs) -> str:
        """Sync version (not used)"""
        raise NotImplementedError("Use async version")
    
    async def _create_or_update_lead(self, session: AsyncSession, data: dict) -> dict:
        """Create or update a lead in the database"""
        company_domain = data.get("company_domain")
        
        # Check if lead exists
        result = await session.execute(
            select(Lead).where(Lead.company_domain == company_domain)
        )
        existing_lead = result.scalar_one_or_none()
        
        if existing_lead:
            # Update existing lead
            existing_lead.company_name = data.get("company_name", existing_lead.company_name)
            existing_lead.industry = data.get("industry", existing_lead.industry)
            existing_lead.description = data.get("description", existing_lead.description)
            existing_lead.research_summary = data.get("research_summary", existing_lead.research_summary)
            existing_lead.updated_at = datetime.utcnow()
            
            return {
                "status": "updated",
                "lead_id": existing_lead.id,
                "company_domain": existing_lead.company_domain,
                "company_name": existing_lead.company_name
            }
        else:
            # Create new lead
            new_lead = Lead(
                company_domain=company_domain,
                company_name=data.get("company_name", ""),
                industry=data.get("industry", ""),
                description=data.get("description", ""),
                research_summary=data.get("research_summary", "")
            )
            session.add(new_lead)
            await session.flush()
            
            return {
                "status": "created",
                "lead_id": new_lead.id,
                "company_domain": new_lead.company_domain,
                "company_name": new_lead.company_name
            }


class EmailToolInput(BaseModel):
    lead_id: int = Field(description="Lead ID to create email for")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body content")


class EmailTool(BaseTool):
    name: str = "email_operations"
    description: str = """
    Save and send emails for leads. Operations:
    - save_email: Save a drafted email to the CRM
    - send_email: Mock-send an email (marks as sent)
    """
    args_schema: Type[BaseModel] = EmailToolInput
    
    async def _arun(self, lead_id: int, subject: str, body: str) -> str:
        """Save email to CRM"""
        try:
            async with async_session() as session:
                email = Email(
                    lead_id=lead_id,
                    subject=subject,
                    body=body,
                    status="sent",
                    sent_at=datetime.utcnow()
                )
                session.add(email)
                await session.commit()
                
                return json.dumps({
                    "status": "success",
                    "email_id": email.id,
                    "lead_id": lead_id,
                    "sent_at": str(email.sent_at)
                })
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _run(self, lead_id: int, subject: str, body: str) -> str:
        """Sync version (not used)"""
        raise NotImplementedError("Use async version")
