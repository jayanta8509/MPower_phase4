import os
import re
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path to import shared_client
sys.path.append(str(Path(__file__).parent.parent))
from shared_client import get_async_client

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")



class Step(BaseModel):
    id: list[int]


class resume_data(BaseModel):
    steps: list[Step]


async def industry_agent(industry_database, resume_industry_assessment):
    """
    Analyzes resume industry assessment against database industry categories
    Returns matching IDs or [0] if no matches found
    
    Args:
        industry_database: Dict with industry categories (e.g., {"1": "Technology", "2": "Healthcare", ...})
        resume_industry_assessment: String with industry assessment from resume analysis
    """

    # Format the industry database for the prompt
    industry_options = "\n".join([f'"{id}": "{industry}"' for id, industry in industry_database.items()])

    prompt_template = f"""You are an expert at analyzing industries and matching career backgrounds to predefined industry categories.

**Your Task:**
Analyze the resume industry assessment and determine which industry from the database best matches the candidate's primary industry background.

**Industry Database Options:**
{industry_options}

**Resume Industry Assessment:**
{resume_industry_assessment}

**Instructions:**
1. Carefully read the resume industry assessment
2. Identify the primary industry based on work experience, skills, and career focus
3. Match it to the most appropriate category from the database
4. Return the ID of the matching industry as a list with one integer
5. If no clear industry can be determined, return [0]
6. Choose the single most representative industry based on the majority of experience
7. Consider the most recent and significant work experience

**Matching Guidelines:**
- Technology (1): Software development, IT, tech companies, programming, systems engineering, data science, cybersecurity
- Healthcare (2): Hospitals, medical devices, pharmaceuticals, healthcare services, biotechnology, medical research
- Finance (3): Banking, investment, insurance, financial services, accounting, fintech, wealth management
- Retail (4): Retail stores, e-commerce, consumer sales, merchandising, retail operations
- Manufacturing (5): Production, industrial manufacturing, automotive, aerospace, chemical, materials
- Education (6): Schools, universities, training organizations, educational technology, academic research
- Government (7): Public sector, government agencies, military, public administration, regulatory bodies
- Real Estate (8): Property development, real estate services, construction, property management
- Hospitality (9): Hotels, restaurants, tourism, event management, food service, travel
- Transportation (10): Logistics, shipping, aviation, automotive transport, supply chain, delivery services
- Energy (11): Oil & gas, renewable energy, utilities, power generation, energy consulting
- Media and Entertainment (12): Publishing, broadcasting, film, gaming, advertising, digital media, marketing
- Professional Services (13): Consulting, legal services, accounting firms, business services, HR services
- Consumer Goods (14): Consumer products, FMCG, retail products, brand management, product development
- NonProfit/NGO (15): Non-profit organizations, charitable institutions, social services, advocacy groups

**Output Format:**
Return a list with one integer ID that matches the primary industry evidenced in the resume assessment.
If no clear industry can be determined, return [0].

Examples:
- If primarily software engineering background: [1]
- If working in hospitals or medical field: [2]
- If banking or financial services experience: [3]
- If retail or e-commerce background: [4]
- If manufacturing or production experience: [5]
- If industry cannot be clearly determined: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this industry assessment and return the matching industry ID: {resume_industry_assessment}"}
    ],
    response_format=resume_data,
    )

    analysis_response = completion.choices[0].message
    total_tokens = completion.usage.total_tokens
    if hasattr(analysis_response, 'refusal') and analysis_response.refusal:
        print(f"Model refused to respond: {analysis_response.refusal}")
        return None, total_tokens
    else:
        parsed_data = resume_data(steps=analysis_response.parsed.steps)
        return parsed_data, total_tokens 