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


async def collaboration_agent(collaboration_database, resume_collaboration_assessment):
    """
    Analyzes resume collaboration assessment against database collaboration traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        collaboration_database: Dict with collaboration traits (e.g., {"1": "Interpersonal Relationships", "2": "Coordinating", ...})
        resume_collaboration_assessment: String with collaboration assessment from resume analysis
    """

    # Format the collaboration database for the prompt
    collaboration_options = "\n".join([f'"{id}": "{trait}"' for id, trait in collaboration_database.items()])

    prompt_template = f"""You are an expert at analyzing collaboration skills and matching them to predefined categories.

**Your Task:**
Analyze the resume collaboration assessment and determine which collaboration traits from the database best match the evidence presented.

**Collaboration Database Options:**
{collaboration_options}

**Resume Collaboration Assessment:**
{resume_collaboration_assessment}

**Instructions:**
1. Carefully read the resume collaboration assessment
2. Compare it against each collaboration trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for explicit mentions of collaboration, teamwork, or working with others
- Consider project descriptions that show team involvement
- Look for leadership roles that require coordinating with others
- Evidence of remote work or virtual team collaboration
- Examples of interpersonal skills in professional settings
- Scheduling and organizing team activities
- Building relationships and cooperation with colleagues
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the collaboration traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If teamwork and coordination are clearly shown: [3, 2]
- If interpersonal relationships and cooperation are evident: [1, 6]
- If remote team experience is mentioned: [7]
- If no collaboration traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this collaboration assessment and return matching trait IDs: {resume_collaboration_assessment}"}
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

