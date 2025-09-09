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


async def educationlevel_agent(educationlevel_database, resume_educationlevel_assessment):
    """
    Analyzes resume education level assessment against database education level categories
    Returns matching IDs or [0] if no matches found
    
    Args:
        educationlevel_database: Dict with education level categories (e.g., {"1": "High School degree", "2": "2 year degree", ...})
        resume_educationlevel_assessment: String with education level assessment from resume analysis
    """

    # Format the education level database for the prompt
    educationlevel_options = "\n".join([f'"{id}": "{level}"' for id, level in educationlevel_database.items()])

    prompt_template = f"""You are an expert at analyzing education levels and matching them to predefined categories.

**Your Task:**
Analyze the resume education level assessment and determine which education level from the database best matches the highest education achieved.

**Education Level Database Options:**
{educationlevel_options}

**Resume Education Level Assessment:**
{resume_educationlevel_assessment}

**Instructions:**
1. Carefully read the resume education level assessment
2. Identify the highest level of education mentioned or achieved
3. Match it to the most appropriate category from the database
4. Return the ID of the matching education level as a list with one integer
5. If no clear education level can be determined, return [0]
6. Only select the highest level of education achieved
7. Consider both formal degrees and professional certifications

**Matching Guidelines:**
- High School degree (1): High school diploma, GED, or equivalent secondary education
- 2 year degree (2): Associate degree, community college diploma, or 2-year technical programs
- 4 year degree (4): Bachelor's degree, undergraduate degree, or 4-year college programs
- Post graduate degree (5): Master's degree, PhD, doctoral degree, or other advanced graduate degrees
- Certification (6): Professional certifications, industry credentials, or specialized training certificates (when this is the highest level)
- Look for explicit mentions of degrees, diplomas, or educational institutions
- Consider graduation dates and degree names
- Professional certifications should only be selected if no formal degree is mentioned
- Choose the single highest level achieved

**Output Format:**
Return a list with one integer ID that matches the highest education level evidenced in the resume assessment.
If no clear education level can be determined, return [0].

Examples:
- If Bachelor's degree is mentioned: [4]
- If Master's degree is the highest: [5]
- If only high school is mentioned: [1]
- If Associate degree is the highest: [2]
- If PhD or doctoral degree: [5]
- If only professional certifications (no formal degree): [6]
- If education level cannot be determined: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this education level assessment and return the matching education level ID: {resume_educationlevel_assessment}"}
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