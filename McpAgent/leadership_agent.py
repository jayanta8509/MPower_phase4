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


async def leadership_agent(leadership_database, resume_leadership_assessment):
    """
    Analyzes resume leadership assessment against database leadership traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        leadership_database: Dict with leadership traits (e.g., {"1": "Management", "2": "Leadership", ...})
        resume_leadership_assessment: String with leadership assessment from resume analysis
    """

    # Format the leadership database for the prompt
    leadership_options = "\n".join([f'"{id}": "{trait}"' for id, trait in leadership_database.items()])

    prompt_template = f"""You are an expert at analyzing leadership skills and matching them to predefined categories.

**Your Task:**
Analyze the resume leadership assessment and determine which leadership traits from the database best match the evidence presented.

**Leadership Database Options:**
{leadership_options}

**Resume Leadership Assessment:**
{resume_leadership_assessment}

**Instructions:**
1. Carefully read the resume leadership assessment
2. Compare it against each leadership trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for evidence of managing teams, departments, or organizations (Management)
- Demonstrated ability to lead and inspire others, vision setting (Leadership)
- Experience teaching, training, or developing others professionally (Mentorship)
- Evidence of making important decisions, strategic choices, or critical judgments (Decision Making)
- Managing projects, timelines, resources, and coordinating deliverables (Project Management)
- Representing interests, championing causes, or speaking up for others (Advocacy)
- Identifying, assessing, and mitigating risks in projects or operations (Risk Management)
- Industry recognition, speaking engagements, thought pieces, or innovation leadership (Thought Leadership)
- Evidence of people management responsibilities
- Leading cross-functional teams or initiatives
- Strategic planning and execution
- Change management and organizational transformation
- Conflict resolution and problem-solving at leadership level
- Budget and resource management
- Performance management of team members
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the leadership traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If management and project management are clearly shown: [1, 5]
- If leadership and mentorship are evident: [2, 3]
- If decision making and risk management are mentioned: [4, 7]
- If thought leadership and advocacy are shown: [8, 6]
- If no leadership traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this leadership assessment and return matching trait IDs: {resume_leadership_assessment}"}
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