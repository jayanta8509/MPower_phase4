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


async def creativity_agent(creativity_database, resume_creativity_assessment):
    """
    Analyzes resume creativity assessment against database creativity traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        creativity_database: Dict with creativity traits (e.g., {"1": "Innovation", "2": "Creative Thinking", ...})
        resume_creativity_assessment: String with creativity assessment from resume analysis
    """

    # Format the creativity database for the prompt
    creativity_options = "\n".join([f'"{id}": "{trait}"' for id, trait in creativity_database.items()])

    prompt_template = f"""You are an expert at analyzing creativity skills and matching them to predefined categories.

**Your Task:**
Analyze the resume creativity assessment and determine which creativity traits from the database best match the evidence presented.

**Creativity Database Options:**
{creativity_options}

**Resume Creativity Assessment:**
{resume_creativity_assessment}

**Instructions:**
1. Carefully read the resume creativity assessment
2. Compare it against each creativity trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for explicit mentions of innovation, creative problem-solving, or novel approaches
- Evidence of original projects, inventions, or creative solutions
- Brainstorming sessions, ideation processes, or creative workshops
- Experimental approaches or willingness to try new methods
- Visionary thinking demonstrated through strategic planning or future-oriented projects
- Creative thinking in problem-solving or project design
- Development of new processes, products, or solutions
- Artistic or design-related experience that shows creativity
- Entrepreneurial ventures or startup experience
- Patents, publications, or creative works
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the creativity traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If innovation and creative thinking are clearly shown: [1, 2]
- If visionary and ideation skills are evident: [3, 4]
- If experimentation and brainstorming experience is mentioned: [5, 6]
- If innovation in product development is shown: [1]
- If no creativity traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this creativity assessment and return matching trait IDs: {resume_creativity_assessment}"}
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

