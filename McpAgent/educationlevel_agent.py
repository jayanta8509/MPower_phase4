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

class education(BaseModel):
    CollegeUniversity: str
    memberEducationLevelId: int
    degree: str
    fieldStudy: str
    description: str
    date: date

class Step(BaseModel):
    education: list[education]


class resume_data(BaseModel):
    steps: list[Step]


async def educationlevel_agent(educationlevel_database, education_history):
    """
    Analyzes the full education history and appends memberEducationLevelId to each entry
    while preserving all other fields exactly as-is. If no clear level, use 0.
    
    Args:
        educationlevel_database: Dict with education level categories (e.g., {"1": "High School degree", "2": "2 year degree", ...})
        education_history: List of education entries with fields CollegeUniversity, degree, fieldStudy, description, date
    """

    # Format the education level database for the prompt
    educationlevel_options = "\n".join([f'"{id}": "{level}"' for id, level in educationlevel_database.items()])

    prompt_template = f"""You are an expert at analyzing education histories and matching each entry to predefined education level categories.

**Your Task:**
For each education entry, determine the most appropriate education level from the database and add memberEducationLevelId to that entry. Do not change any other fields.

**Education Level Database Options:**
{educationlevel_options}

**Instructions:**
1. Carefully read each education entry (degree, field of study, description, institution, dates)
2. Match that single entry to the most appropriate category from the database
3. Add memberEducationLevelId with the chosen ID for that entry
4. If no clear education level can be determined for an entry, set memberEducationLevelId to 0 for that entry
5. Preserve every other field exactly as provided (CollegeUniversity, degree, fieldStudy, description, date)
6. Do not remove or reorder entries; return the same list with the added IDs

**Matching Guidelines:**
- High School degree (1): High school diploma, GED, or equivalent secondary education
- 2 year degree (2): Associate degree, community college diploma, or 2-year technical programs
- 4 year degree (4): Bachelor's degree, undergraduate degree, or 4-year college programs
- Post graduate degree (5): Master's degree, PhD, doctoral degree, or other advanced graduate degrees
- Certification (6): Professional certifications, industry credentials, or specialized training certificates (when this is the highest level)
- Look for explicit mentions of degree names (Associate, Bachelor, Master, PhD/Doctorate), diplomas, or certifications
- Consider field names that imply level (e.g., MS/M.Sc = Master's, BS/B.Sc/BA = Bachelor's)
- If ambiguous, choose 0

**Output Format:**
Return the exact same structure as the input list of education entries, but with memberEducationLevelId populated for each entry.

"""

    # Get the async client
    client = await get_async_client()
    
    # Convert education_history to text for the prompt while relying on structured parsing for output
    if isinstance(education_history, dict) or isinstance(education_history, list):
        education_text = str(education_history)
    else:
        education_text = str(education_history)

    completion = await client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": f"Please analyze this education history and add memberEducationLevelId to each entry, preserving everything else:\n\n{education_text}"}
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