from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import json
from tools import ResearchTool, CRMTool, EmailTool
from config import get_settings

settings = get_settings()


# Define the state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    company_domain: str
    research_data: dict
    lead_data: dict
    email_data: dict
    next_step: str


# Initialize tools
research_tool = ResearchTool()
crm_tool = CRMTool()
email_tool = EmailTool()

tools = [research_tool, crm_tool, email_tool]

# Initialize LLM with Claude
llm = ChatAnthropic(
    model="claude-3-haiku-20240307",
    temperature=0.7,
    anthropic_api_key=settings.anthropic_api_key
)
llm_with_tools = llm.bind_tools(tools)


# Define agent nodes
async def research_node(state: AgentState) -> AgentState:
    """Research the company"""
    print(f"🔍 Researching company: {state['company_domain']}")
    
    company_domain = state["company_domain"]
    research_result = await research_tool._arun(company_domain)
    research_data = json.loads(research_result)
    
    state["research_data"] = research_data
    state["messages"].append(
        AIMessage(content=f"Research completed for {company_domain}. Found: {research_data.get('company_name', 'Unknown')}")
    )
    state["next_step"] = "save_to_crm"
    
    return state


async def save_to_crm_node(state: AgentState) -> AgentState:
    """Save lead to CRM"""
    print("💾 Saving lead to CRM")
    
    research_data = state["research_data"]
    
    crm_result = await crm_tool._arun(
        company_domain=state["company_domain"],
        company_name=research_data.get("company_name", ""),
        industry=research_data.get("industry", ""),
        description=research_data.get("description", ""),
        research_summary=json.dumps(research_data)
    )
    
    lead_data = json.loads(crm_result)
    state["lead_data"] = lead_data
    state["messages"].append(
        AIMessage(content=f"Lead saved to CRM with ID: {lead_data.get('lead_id')}")
    )
    state["next_step"] = "generate_email"
    
    return state


async def generate_email_node(state: AgentState) -> AgentState:
    """Generate personalized email using LLM"""
    print("✉️ Generating personalized email")
    
    research_data = state["research_data"]
    company_name = research_data.get("company_name", "the company")
    
    # Create prompt for email generation
    email_prompt = f"""You are Wasiu Ibrahim, writing a professional B2B outreach email about AI/automation solutions based on the research below.

COMPANY RESEARCH:
- Company: {research_data.get('company_name', 'Unknown')}
- Industry: {research_data.get('industry', 'Unknown')}
- Description: {research_data.get('description', 'Unknown')}
- Key Highlights: {', '.join(research_data.get('key_highlights', []))}
- Recent News: {research_data.get('recent_news', 'Unknown')}

INSTRUCTIONS:
Write an exceptionally professional, executive-level B2B outreach email that:

1. SUBJECT LINE: 
   - Must include the company name "{research_data.get('company_name', 'Unknown')}"
   - Executive-level professional (no sales language)
   - Format examples: "Operational Efficiency for [Company]" or "Strategic Partnership - [Company]"
   - Keep it formal and business-focused

2. EMAIL BODY STRUCTURE:
   - Opening: MUST start with "Hi {research_data.get('company_name', 'Unknown')}," (exactly this format)
   - First Paragraph: Show specific knowledge of their business or industry position
   - Second Paragraph: Present clear value proposition focused on business outcomes
   - Third Paragraph: Brief credibility statement (results-oriented, no fluff)
   - Closing: Simple, professional call-to-action
   - Sign-off: "Best regards,\\n\\nWasiu Ibrahim"

3. PROFESSIONAL WRITING STANDARDS:
   - Write in clear, direct business language
   - Use active voice and strong verbs
   - No quotes, no ellipses, no casual language
   - No exclamation marks or promotional language
   - Focus on business value and outcomes
   - Sound like a peer reaching out for collaboration
   - Maintain executive-level tone throughout
   - Do NOT mention any job titles, positions, or company affiliations

4. CONTENT REQUIREMENTS:
   - Mention company name 2-3 times naturally
   - Reference specific industry insights or achievements
   - Focus on strategic benefits, not product features
   - Be concise and respect their time
   
5. LENGTH: 140-180 words (professional brevity)

6. FORMAT: Return ONLY valid JSON with this exact structure:
{{
  "subject": "subject line here",
  "body": "email body here"
}}

CRITICAL FORMATTING:
- MUST start body with: "Hi {research_data.get('company_name', 'Unknown')},"
- Use \\n\\n for paragraph breaks only
- MUST end with: "Best regards,\\n\\nWasiu Ibrahim"
- Write plain text with no quotation marks
- Professional, executive-level tone throughout"""
    
    response = await llm.ainvoke([HumanMessage(content=email_prompt)])
    
    # Parse the email content
    try:
        # Try to extract JSON from the response
        content = response.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        email_content = json.loads(content)
        
        # Ensure proper formatting with full signature
        if "body" in email_content:
            body = email_content["body"].strip()
            
            # Remove any quotes from the body
            body = body.replace('"', '').replace("'", "'")
            
            # Ensure it starts with "Hi [Company],"
            if not body.startswith("Hi "):
                body = f"Hi {company_name},\n\n" + body
            
            # Add full signature if not present
            signature = "Best regards,\n\nWasiu Ibrahim"
            if "Wasiu Ibrahim" not in body and not body.endswith(signature):
                if body.endswith(("Best regards,", "Kind regards,", "Regards,")):
                    # Replace incomplete signature
                    for ending in ["Best regards,", "Kind regards,", "Regards,"]:
                        if body.endswith(ending):
                            body = body[:-len(ending)].strip()
                            break
                body += f"\n\n{signature}"
            
            email_content["body"] = body
        
        # Clean up subject line - remove quotes
        if "subject" in email_content:
            email_content["subject"] = email_content["subject"].replace('"', '').replace("'", "'").strip()
            
    except Exception as e:
        print(f"Error parsing email JSON: {e}")
        # Fallback if JSON parsing fails
        email_content = {
            "subject": f"Strategic Partnership Discussion - {company_name}",
            "body": f"Hi {company_name},\n\nI have been following {company_name}'s progress in the {research_data.get('industry', 'technology')} sector and wanted to reach out regarding potential collaboration opportunities.\n\nWe specialize in implementing AI and automation solutions that help companies achieve measurable improvements in operational efficiency and scalability. Based on {company_name}'s current market position, I believe there may be strategic value in exploring how these capabilities could support your growth objectives.\n\nWould you be available for a brief conversation to discuss this further?\n\nBest regards,\n\nWasiu Ibrahim"
        }
    
    state["email_data"] = email_content
    state["messages"].append(
        AIMessage(content=f"Email generated: {email_content.get('subject')}")
    )
    state["next_step"] = "send_email"
    
    return state


async def send_email_node(state: AgentState) -> AgentState:
    """Save and mock-send the email"""
    print("📤 Sending email")
    
    lead_id = state["lead_data"].get("lead_id")
    email_data = state["email_data"]
    
    email_result = await email_tool._arun(
        lead_id=lead_id,
        subject=email_data.get("subject", ""),
        body=email_data.get("body", "")
    )
    
    email_result_data = json.loads(email_result)
    state["messages"].append(
        AIMessage(content=f"Email sent successfully! Email ID: {email_result_data.get('email_id')}")
    )
    state["next_step"] = "end"
    
    return state


def route_next_step(state: AgentState) -> str:
    """Determine the next step in the workflow"""
    next_step = state.get("next_step", "research")
    
    if next_step == "save_to_crm":
        return "save_to_crm"
    elif next_step == "generate_email":
        return "generate_email"
    elif next_step == "send_email":
        return "send_email"
    elif next_step == "end":
        return "end"
    else:
        return "research"


# Build the graph
def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("save_to_crm", save_to_crm_node)
    workflow.add_node("generate_email", generate_email_node)
    workflow.add_node("send_email", send_email_node)
    
    # Add edges
    workflow.set_entry_point("research")
    workflow.add_conditional_edges(
        "research",
        route_next_step,
        {
            "save_to_crm": "save_to_crm",
            "end": END
        }
    )
    workflow.add_conditional_edges(
        "save_to_crm",
        route_next_step,
        {
            "generate_email": "generate_email",
            "end": END
        }
    )
    workflow.add_conditional_edges(
        "generate_email",
        route_next_step,
        {
            "send_email": "send_email",
            "end": END
        }
    )
    workflow.add_conditional_edges(
        "send_email",
        route_next_step,
        {
            "end": END
        }
    )
    
    return workflow.compile()


# Create the agent
agent_graph = create_agent_graph()


async def run_sdr_agent(company_domain: str) -> dict:
    """Run the SDR agent for a given company domain"""
    initial_state = AgentState(
        messages=[HumanMessage(content=f"Research and create outreach for {company_domain}")],
        company_domain=company_domain,
        research_data={},
        lead_data={},
        email_data={},
        next_step="research"
    )
    
    print(f"🤖 Starting SDR Agent for {company_domain}")
    print("=" * 50)
    
    final_state = await agent_graph.ainvoke(initial_state)
    
    print("=" * 50)
    print("✅ Agent workflow completed!")
    
    return {
        "company_domain": company_domain,
        "research": final_state["research_data"],
        "lead": final_state["lead_data"],
        "email": final_state["email_data"],
        "status": "completed"
    }
