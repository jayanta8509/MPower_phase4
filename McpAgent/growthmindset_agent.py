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


async def growthmindset_agent(growthmindset_database, resume_growthmindset_assessment):
    """
    Analyzes resume growth mindset assessment against database growth mindset traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        growthmindset_database: Dict with growth mindset traits (e.g., {"1": "Self-starter", "2": "Proactivity", ...})
        resume_growthmindset_assessment: String with growth mindset assessment from resume analysis
    """

    # Format the growth mindset database for the prompt
    growthmindset_options = "\n".join([f'"{id}": "{trait}"' for id, trait in growthmindset_database.items()])

    prompt_template = f"""You are an expert at analyzing growth mindset and learning orientation skills and matching them to predefined categories.

**Your Task:**
Analyze the resume growth mindset assessment and determine which growth mindset traits from the database best match the evidence presented.

**Growth Mindset Database Options:**
{growthmindset_options}

**Resume Growth Mindset Assessment:**
{resume_growthmindset_assessment}

**Instructions:**
1. Carefully read the resume growth mindset assessment
2. Compare it against each growth mindset trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for evidence of taking initiative without being asked or managed (Self-starter)
- Taking action before being directed, anticipating needs and opportunities (Proactivity)
- Demonstrating interest in learning new things, asking questions, exploring (Curiosity)
- Finding creative solutions with limited resources, making things work (Resourcefulness)
- Starting new ventures, taking business risks, innovative thinking (Entrepreneurship)
- Preference for doing rather than planning, implementation focus (Action-Oriented)
- Focus on achieving outcomes, measuring success, goal achievement (Results Focused)
- Working independently, minimal supervision needed, autonomous work style (Self-Sufficiency)
- Evidence of continuous learning and skill acquisition
- Career progression showing adaptability and learning
- Self-directed projects or professional development
- Taking on new challenges outside comfort zone
- Innovation and improvement initiatives
- Independent problem-solving capabilities
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the growth mindset traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If self-starter and proactivity are clearly shown: [1, 2]
- If curiosity and resourcefulness are evident: [3, 4]
- If entrepreneurship and action-oriented behavior are mentioned: [5, 6]
- If results focused and self-sufficiency are shown: [7, 8]
- If no growth mindset traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this growth mindset assessment and return matching trait IDs: {resume_growthmindset_assessment}"}
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