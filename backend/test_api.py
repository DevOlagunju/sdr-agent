"""
Simple test script to verify the SDR Agent API is working
Run this after starting the backend server
"""
import asyncio
import httpx
import json


API_URL = "http://localhost:8000"


async def test_health():
    """Test if the API is running"""
    print("Testing API health...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/")
            print(f"✅ API is running: {response.status_code}")
            print(f"   Response: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ API not responding: {e}")
            return False


async def test_research():
    """Test the research endpoint"""
    print("\nTesting research endpoint...")
    test_domain = "openai.com"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            print(f"   Researching: {test_domain}")
            response = await client.post(
                f"{API_URL}/api/research",
                json={"company_domain": test_domain}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Research completed!")
                print(f"   Company: {data['research']['company_name']}")
                print(f"   Industry: {data['research']['industry']}")
                print(f"   Lead ID: {data['lead']['lead_id']}")
                print(f"   Email Subject: {data['email']['subject']}")
                print(f"\n   Generated Email Body:")
                print(f"   {data['email']['body'][:200]}...")
                return True
            else:
                print(f"❌ Research failed: {response.status_code}")
                print(f"   {response.text}")
                return False
        except Exception as e:
            print(f"❌ Research error: {e}")
            return False


async def test_get_leads():
    """Test getting leads from CRM"""
    print("\nTesting CRM leads endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/api/leads")
            if response.status_code == 200:
                leads = response.json()
                print(f"✅ Retrieved {len(leads)} leads from CRM")
                if leads:
                    print(f"   Latest lead: {leads[0]['company_name']}")
                return True
            else:
                print(f"❌ Failed to get leads: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error getting leads: {e}")
            return False


async def test_get_emails():
    """Test getting emails"""
    print("\nTesting emails endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/api/emails")
            if response.status_code == 200:
                emails = response.json()
                print(f"✅ Retrieved {len(emails)} emails")
                if emails:
                    print(f"   Latest email subject: {emails[0]['subject']}")
                return True
            else:
                print(f"❌ Failed to get emails: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error getting emails: {e}")
            return False


async def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("SDR Agent API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not await test_health():
        print("\n❌ API is not running. Please start the backend first:")
        print("   cd backend && venv\\Scripts\\activate && uvicorn main:app --reload")
        return
    
    # Test 2: Research endpoint (this takes time due to LLM)
    await test_research()
    
    # Test 3: Get leads
    await test_get_leads()
    
    # Test 4: Get emails
    await test_get_emails()
    
    print("\n" + "=" * 60)
    print("Test suite completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("\n⚠️  Make sure the backend is running before running tests!")
    print("   Start it with: uvicorn main:app --reload\n")
    
    asyncio.run(run_all_tests())
