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

class date(BaseModel):
    dateFrom: str
    dateTo: str

class experience(BaseModel):
    jobTitle: str
    company: str
    currentlyWorking: bool
    industryId: int
    description: str
    date: date

class Step(BaseModel):
    experience: list[experience]


class resume_data(BaseModel):
    steps: list[Step]


async def industry_agent(industry_database, experience_data):
    """
    Analyzes experience data and assigns appropriate industryId to each experience
    
    Args:
        industry_database: Dict with industry categories (e.g., {"1": "Technology", "2": "Healthcare", ...})
        experience_data: List of experience objects or resume_data object with experiences
    
    Returns:
        resume_data: Same structure as input but with industryId populated for each experience
        total_tokens: Token usage count
    """

    # Format the industry database for the prompt
    industry_options = "\n".join([f'"{id}": "{industry}"' for id, industry in industry_database.items()])

    prompt_template = f"""You are an expert at analyzing work experiences and matching them to industry categories.

**Your Task:**
Analyze each work experience (job title, company, description) and assign the most appropriate industryId from the database to each experience.

**Industry Database Options:**
{industry_options}

**Instructions:**
1. For each experience entry, analyze the job title, company name, and job description
2. Determine which industry category best matches that specific work experience
3. Assign the appropriate industryId to each experience
4. Keep all other fields (jobTitle, company, currentlyWorking, description, date) exactly the same
5. If an industry cannot be clearly determined for an experience, assign industryId as 0

**Matching Guidelines:**
- Technology (1): Software development, IT, tech companies, programming, systems engineering, data science, cybersecurity, software engineers, developers, data analysts
- Healthcare (2): Hospitals, medical devices, pharmaceuticals, healthcare services, biotechnology, medical research, doctors, nurses, medical professionals
- Finance (3): Banking, investment, insurance, financial services, accounting, fintech, wealth management, financial analysts, accountants
- Retail (4): Retail stores, e-commerce, consumer sales, merchandising, retail operations, sales associates, retail managers
- Manufacturing (5): Production, industrial manufacturing, automotive, aerospace, chemical, materials, production engineers, factory workers
- Education (6): Schools, universities, training organizations, educational technology, academic research, teachers, professors, trainers
- Government (7): Public sector, government agencies, military, public administration, regulatory bodies, civil servants, government officials
- Real Estate (8): Property development, real estate services, construction, property management, real estate agents, property managers
- Hospitality (9): Hotels, restaurants, tourism, event management, food service, travel, chefs, hotel staff, tour guides
- Transportation (10): Logistics, shipping, aviation, automotive transport, supply chain, delivery services, drivers, logistics coordinators
- Energy (11): Oil & gas, renewable energy, utilities, power generation, energy consulting, energy engineers, utility workers
- Media and Entertainment (12): Publishing, broadcasting, film, gaming, advertising, digital media, marketing, content creators, marketers
- Professional Services (13): Consulting, legal services, accounting firms, business services, HR services, consultants, lawyers, HR professionals
- Consumer Goods (14): Consumer products, FMCG, retail products, brand management, product development, product managers, brand managers
- NonProfit/NGO (15): Non-profit organizations, charitable institutions, social services, advocacy groups, social workers, NGO staff

**Output Format:**
Return the exact same structure as input but with industryId field populated for each experience based on the analysis.

**Important:**
- Preserve all existing data exactly as provided
- Only add/update the industryId field for each experience
- Maintain the exact same structure and format"""

    # Convert experience_data to proper format for analysis
    if isinstance(experience_data, dict):
        # If it's a dict, convert to resume_data format for consistency
        experiences_text = str(experience_data)
    elif hasattr(experience_data, 'steps'):
        # If it's already a resume_data object
        experiences_text = str(experience_data.model_dump())
    else:
        # If it's a list or other format
        experiences_text = str(experience_data)

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"Please analyze these work experiences and assign appropriate industryId to each experience:\n\n{experiences_text}"}
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