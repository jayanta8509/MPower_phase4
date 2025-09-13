from multiprocessing import current_process
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

class date(BaseModel):
    dateFrom: str
    dateTo: str

class experience(BaseModel):
    jobTitle: str
    company: str
    currentlyWorking: bool
    description: str
    date: date
    
class education(BaseModel):
    CollegeUniversity: str
    degree: str
    fieldStudy: str
    description: str
    date: date

class Step(BaseModel):
    headline: str
    memberFirstName: str
    memberLastName: str
    experience: list[experience]
    education: list[education]
    otherSkillName: list[str]





class resume_data(BaseModel):
    steps: list[Step]


async def analyze_resume(input_question):

    prompt_template = """ You are an expert resume parser. Extract the following information from the resume and structure it according to the specified format:
        1. **headline**
           - Based on the candidate's work experience, education, and technical skill set, suggest the most suitable job role they are likely to be both qualified for and interested in
           - The suggested role should align with the candidate's career progression, domain expertise, and strengths demonstrated in their resume
           - Ensure the recommendation reflects realistic career advancement and industry relevance

        2. **Member FirstName and Member LastName:**
           - Candidate's first name
           - Candidate's last name

        3. **Member FirstName and Member LastName:**
           - Candidate's first name
           - Candidate's last name
           


        4. **experience Job Title:**
           - analyze the candidate's work experience and suggest the most suitable job title
           
        5. **experience Company:**
           - analyze the candidate's work experience and suggest the most suitable company

        6. **experience Currently Working:**
           - Set to true if the candidate is currently working at this company (indicated by phrases like "Present", "Current", "ongoing", or no end date)
           - Set to false if the candidate is no longer working at this company (has a specific end date)

        7. **experience Description:**
           - analyze the candidate's work experience and suggest the most suitable job description

        8. **education School:**
           - analyze the candidate's education and suggest the most suitable school

        9. **education Degree:**
           - analyze the candidate's education and suggest the most suitable degree

        10. **education Field Study:**
           - analyze the candidate's education and suggest the most suitable field of study

        11. **education Description:**
           - analyze the candidate's education and suggest the most suitable education description

        12. **other Skill Name:**
          - analyze the candidate's technical skill set and suggest the most suitable other skill name
           - Frameworks & Libraries
           - Databases
           - Tools & Technologies
           - Domain Expertise
           (Create appropriate categories based on the resume content)

        """

    # Get the async client
    client = await get_async_client()
    
    completion = await client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": prompt_template},
        {"role": "user", "content": input_question}
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

