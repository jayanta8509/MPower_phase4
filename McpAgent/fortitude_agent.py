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


async def fortitude_agent(fortitude_database, resume_fortitude_assessment):
    """
    Analyzes resume fortitude assessment against database fortitude traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        fortitude_database: Dict with fortitude traits (e.g., {"1": "Resilience", "2": "Motivational Skills", ...})
        resume_fortitude_assessment: String with fortitude assessment from resume analysis
    """

    # Format the fortitude database for the prompt
    fortitude_options = "\n".join([f'"{id}": "{trait}"' for id, trait in fortitude_database.items()])

    prompt_template = f"""You are an expert at analyzing fortitude and resilience skills and matching them to predefined categories.

**Your Task:**
Analyze the resume fortitude assessment and determine which fortitude traits from the database best match the evidence presented.

**Fortitude Database Options:**
{fortitude_options}

**Resume Fortitude Assessment:**
{resume_fortitude_assessment}

**Instructions:**
1. Carefully read the resume fortitude assessment
2. Compare it against each fortitude trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for evidence of overcoming challenges, setbacks, or difficult situations (Resilience)
- Ability to motivate others or self-motivation in challenging circumstances (Motivational Skills)
- Positive outlook and maintaining morale during difficulties (Optimism)
- Persistence in pursuing goals despite obstacles (Tenacity)
- Taking initiative and standing up for decisions or beliefs (Assertiveness)
- Evidence of self-control, organization, and consistent work habits (Self-Discipline)
- Performance under tight deadlines, stress, or high-pressure situations (Calmness Under Pressure)
- Confidence in abilities and decision-making (Self-Confident)
- Career transitions showing adaptability and courage
- Leadership during crisis or challenging periods
- Long-term commitment to goals or projects
- Evidence of bouncing back from failures or setbacks
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the fortitude traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If resilience and tenacity are clearly shown: [1, 4]
- If self-discipline and calmness under pressure are evident: [6, 7]
- If motivational skills and optimism are mentioned: [2, 3]
- If self-confidence and assertiveness are shown: [8, 5]
- If no fortitude traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this fortitude assessment and return matching trait IDs: {resume_fortitude_assessment}"}
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