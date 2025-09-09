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


async def mindfulness_agent(mindfulness_database, resume_mindfulness_assessment):
    """
    Analyzes resume mindfulness assessment against database mindfulness traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        mindfulness_database: Dict with mindfulness traits (e.g., {"1": "Hospitality", "2": "Compassion", ...})
        resume_mindfulness_assessment: String with mindfulness assessment from resume analysis
    """

    # Format the mindfulness database for the prompt
    mindfulness_options = "\n".join([f'"{id}": "{trait}"' for id, trait in mindfulness_database.items()])

    prompt_template = f"""You are an expert at analyzing mindfulness and emotional intelligence skills and matching them to predefined categories.

**Your Task:**
Analyze the resume mindfulness assessment and determine which mindfulness traits from the database best match the evidence presented.

**Mindfulness Database Options:**
{mindfulness_options}

**Resume Mindfulness Assessment:**
{resume_mindfulness_assessment}

**Instructions:**
1. Carefully read the resume mindfulness assessment
2. Compare it against each mindfulness trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for evidence of service-oriented roles, welcoming behavior, or guest relations (Hospitality)
- Demonstrated care for others, volunteer work, or helping colleagues (Compassion)
- Understanding others' perspectives, relating to diverse backgrounds, or emotional awareness (Empathy)
- Working through long-term projects, dealing with difficult situations calmly (Patience)
- Evidence of good communication skills, understanding others, or collaborative listening (Active Listening)
- Managing relationships well, understanding team dynamics, or interpersonal skills (Emotional Intelligence)
- Willingness to learn from others, acknowledging mistakes, or accepting feedback gracefully (Humility)
- Working with diverse teams, international experience, or cross-cultural awareness (Cultural Sensitivity)
- Evidence of self-awareness and emotional regulation
- Conflict resolution and mediation experience
- Customer service or client relations roles
- Team harmony and positive workplace culture contributions
- Mentoring or supporting colleagues through challenges
- Adapting communication style to different audiences
- Stress management and maintaining composure
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the mindfulness traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If hospitality and compassion are clearly shown: [1, 2]
- If empathy and active listening are evident: [3, 5]
- If emotional intelligence and cultural sensitivity are mentioned: [6, 8]
- If patience and humility are shown: [4, 7]
- If no mindfulness traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this mindfulness assessment and return matching trait IDs: {resume_mindfulness_assessment}"}
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