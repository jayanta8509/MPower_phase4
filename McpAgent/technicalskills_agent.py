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


async def technicalskills_agent(technicalskills_database, resume_technicalskills_list):
    """
    Analyzes resume technical skills list against database technical skill categories
    Returns matching IDs or [0] if no matches found
    
    Args:
        technicalskills_database: Dict with technical skill categories (e.g., {"1": "Artificial Intelligence", "2": "Blockchain Development", ...})
        resume_technicalskills_list: List of technical skills extracted from resume
    """

    # Format the technical skills database for the prompt
    technicalskills_options = "\n".join([f'"{id}": "{skill}"' for id, skill in technicalskills_database.items()])
    
    # Format the resume technical skills list
    resume_skills_formatted = ", ".join(resume_technicalskills_list)

    prompt_template = f"""You are an expert at analyzing technical skills and matching them to predefined categories.

**Your Task:**
Analyze the resume technical skills list and determine which technical skill categories from the database best match the skills presented.

**Technical Skills Database Categories:**
{technicalskills_options}

**Resume Technical Skills:**
{resume_skills_formatted}

**Instructions:**
1. Carefully review each technical skill from the resume
2. Match each skill to the most appropriate category from the database
3. Group similar skills under the same category when appropriate
4. Return the IDs of matching categories as a list of integers
5. If no skills clearly match any database categories, return [0]
6. Only include categories that have clear technical skill matches
7. Avoid duplicating the same category ID multiple times

**Matching Guidelines:**
- AI/ML Skills → Artificial Intelligence (1), Machine Learning (9)
- Programming Languages → Python Programming (43), Java Programming (38), JavaScript (39), C++ Programming (21), PHP Programming (41)
- Cloud Platforms → Cloud Computing (3), AWS (55)
- Databases → Database Management (29), SQL (47)
- Web Technologies → Web Development (13), HTML/CSS (35)
- Mobile → Mobile App Development (7)
- Data Skills → Data Analysis (16), Data Engineering (27), Data Visualization (28)
- Security → Cybersecurity (6)
- UI/UX → UI/UX Design (11)
- APIs → RESTful API (52)
- Version Control → Git, GitHub (54)
- Frameworks → .Net (58), ASP.NET (59)
- DevOps → DevOps (14), CI/CD (57)
- Testing → Testing and validation (15), Automation Testing (19)
- Business Tools → Microsoft Excel (40), CRM (24), Project Management (42)
- Marketing → Digital Marketing (30), SEO/SEM (10), Social Media Management (46)

**Matching Strategy:**
- Look for exact matches first (e.g., "Python" → Python Programming)
- Match related technologies to broader categories (e.g., "TensorFlow" → Machine Learning, "AWS Lambda" → Cloud Computing)
- Group similar skills (e.g., multiple AWS services → AWS category)
- Be inclusive but avoid over-categorization

**Output Format:**
Return a list of integer IDs that match the technical skill categories evidenced in the resume skills.
If no clear matches are found, return [0].

Examples:
- If Python, TensorFlow, scikit-learn are present: [43, 9] (Python Programming, Machine Learning)
- If AWS services are mentioned: [3, 55] (Cloud Computing, AWS)
- If JavaScript, HTML, CSS are present: [39, 35, 13] (JavaScript, HTML/CSS, Web Development)
- If no recognizable technical skills: [0]
"""

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": f"Please analyze these technical skills and return matching category IDs: {resume_skills_formatted}"}
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