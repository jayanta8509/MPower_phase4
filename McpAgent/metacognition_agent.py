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


async def metacognition_agent(metacognition_database, resume_metacognition_assessment):
    """
    Analyzes resume metacognition assessment against database metacognition traits
    Returns matching IDs or [0] if no matches found
    
    Args:
        metacognition_database: Dict with metacognition traits (e.g., {"1": "Detail Oriented", "2": "Planning", ...})
        resume_metacognition_assessment: String with metacognition assessment from resume analysis
    """

    # Format the metacognition database for the prompt
    metacognition_options = "\n".join([f'"{id}": "{trait}"' for id, trait in metacognition_database.items()])

    prompt_template = f"""You are an expert at analyzing metacognition and self-awareness skills and matching them to predefined categories.

**Your Task:**
Analyze the resume metacognition assessment and determine which metacognition traits from the database best match the evidence presented.

**Metacognition Database Options:**
{metacognition_options}

**Resume Metacognition Assessment:**
{resume_metacognition_assessment}

**Instructions:**
1. Carefully read the resume metacognition assessment
2. Compare it against each metacognition trait in the database
3. Identify which traits are clearly evidenced or strongly suggested by the resume assessment
4. Return the IDs of matching traits as a list of integers
5. If no traits clearly match the evidence in the resume, return [0]
6. Only include traits that have clear evidence or strong indication in the assessment
7. Be selective - only choose traits that are well-supported by the resume content

**Matching Guidelines:**
- Look for evidence of attention to accuracy, precision, and thoroughness (Detail Oriented)
- Evidence of strategic thinking, project planning, and systematic approaches (Planning)
- Experience in training others, knowledge transfer, or educational activities (Teaching)
- Demonstrated ability to structure work, manage complexity, and maintain order (Organizational Skills)
- Evidence of meeting deadlines, managing schedules, and efficient work processes (Time Management)
- Career transitions, learning new skills, or adjusting to changing environments (Adaptability)
- Setting and achieving objectives, career progression planning, or milestone tracking (Goal Setting)
- Experience giving or receiving feedback, performance reviews, or improvement processes (Constructive Feedback)
- Evidence of self-reflection and self-awareness in career development
- Systematic approaches to problem-solving and learning
- Process improvement and optimization initiatives
- Quality assurance and attention to standards
- Documentation and knowledge management practices
- Continuous improvement mindset
- Self-directed learning and skill development
- Avoid assumptions - only match what is clearly supported by evidence

**Output Format:**
Return a list of integer IDs that match the metacognition traits evidenced in the resume assessment.
If no clear matches are found, return [0].

Examples:
- If detail oriented and organizational skills are clearly shown: [1, 4]
- If planning and time management are evident: [2, 5]
- If teaching and constructive feedback are mentioned: [3, 8]
- If adaptability and goal setting are shown: [6, 7]
- If no metacognition traits are clearly evidenced: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze this metacognition assessment and return matching trait IDs: {resume_metacognition_assessment}"}
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