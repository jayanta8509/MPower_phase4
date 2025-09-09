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


async def character_agent(character_database, resume_character_assessment):
    """
    Analyzes resume character assessment against database character traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        character_database: Dict with character traits (e.g., {"1": "Accountability", "2": "Self-Motivation", ...})
        resume_character_assessment: String with character assessment from resume analysis
    """

    # Format the character database for the prompt
    character_options = "\n".join([f'"{id}": "{trait}"' for id, trait in character_database.items()])

    prompt_template = f"""You are an expert at analyzing character traits and matching them to predefined categories.

**Your Task:**
Analyze the resume character assessment and determine which character traits from the database best match the evidence presented.

**Character Database Options:**
{character_options}

**Resume Character Assessment:**
{resume_character_assessment}

**Instructions:**
1. Carefully read the resume character assessment
2. Compare it against each character trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for explicit mentions of the trait or its synonyms
- Consider behaviors and examples that demonstrate the trait
- Professional consistency and achievement patterns that suggest the trait
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the character traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If accountability and reliability are clearly shown: [1, 5]
- If self-motivation is evident: [2]
- If no traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this character assessment and return matching trait IDs: {resume_character_assessment}"}
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

