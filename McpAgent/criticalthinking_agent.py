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


async def criticalthinking_agent(criticalthinking_database, resume_criticalthinking_assessment):
    """
    Analyzes resume critical thinking assessment against database critical thinking traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        criticalthinking_database: Dict with critical thinking traits (e.g., {"1": "Problem Solving", "2": "Research", ...})
        resume_criticalthinking_assessment: String with critical thinking assessment from resume analysis
    """

    # Format the critical thinking database for the prompt
    criticalthinking_options = "\n".join([f'"{id}": "{trait}"' for id, trait in criticalthinking_database.items()])

    prompt_template = f"""You are an expert at analyzing critical thinking skills and matching them to predefined categories.

**Your Task:**
Analyze the resume critical thinking assessment and determine which critical thinking traits from the database best match the evidence presented.

**Critical Thinking Database Options:**
{criticalthinking_options}

**Resume Critical Thinking Assessment:**
{resume_criticalthinking_assessment}

**Instructions:**
1. Carefully read the resume critical thinking assessment
2. Compare it against each critical thinking trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for explicit mentions of problem-solving, analysis, or logical reasoning
- Evidence of research projects, data analysis, or investigative work
- Complex project descriptions that show analytical thinking
- Prioritization skills demonstrated through project management or decision-making
- Investigation experience through troubleshooting, debugging, or root cause analysis
- Critical thinking demonstrated through strategic planning or complex decision-making
- Intellectual curiosity shown through continuous learning, certifications, or self-directed projects
- Analytical thinking evidenced through data interpretation, metrics analysis, or systematic approaches
- Evidence of methodical approaches to challenges
- Quality assurance or testing experience that requires analytical skills
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the critical thinking traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If problem solving and analytical thinking are clearly shown: [1, 7]
- If research and investigation skills are evident: [2, 4]
- If prioritization and critical thinking experience is mentioned: [3, 5]
- If intellectual curiosity through learning is shown: [6]
- If no critical thinking traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this critical thinking assessment and return matching trait IDs: {resume_criticalthinking_assessment}"}
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

