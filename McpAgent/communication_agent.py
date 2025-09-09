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


async def communication_agent(communication_database, resume_communication_assessment):
    """
    Analyzes resume communication assessment against database communication traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        communication_database: Dict with communication traits (e.g., {"1": "Verbal Communication", "2": "Written Communication", ...})
        resume_communication_assessment: String with communication assessment from resume analysis
    """

    # Format the communication database for the prompt
    communication_options = "\n".join([f'"{id}": "{trait}"' for id, trait in communication_database.items()])

    prompt_template = f"""You are an expert at analyzing communication skills and matching them to predefined categories.

**Your Task:**
Analyze the resume communication assessment and determine which communication traits from the database best match the evidence presented.

**Communication Database Options:**
{communication_options}

**Resume Communication Assessment:**
{resume_communication_assessment}

**Instructions:**
1. Carefully read the resume communication assessment
2. Compare it against each communication trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for explicit mentions of communication skills, speaking, writing, or presenting
- Consider documentation, reports, or publications that show written communication
- Evidence of presentations, training sessions, or public speaking
- Customer service or client interaction experience
- Remote/hybrid communication experience
- Negotiation skills or conflict resolution
- Social media management or digital communication
- Active listening skills demonstrated through collaboration
- Clear resume writing and professional presentation
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the communication traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If verbal and written communication are clearly shown: [1, 2]
- If presentation and public speaking skills are evident: [5, 9]
- If customer service experience is mentioned: [8]
- If remote communication experience is shown: [4]
- If no communication traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this communication assessment and return matching trait IDs: {resume_communication_assessment}"}
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

