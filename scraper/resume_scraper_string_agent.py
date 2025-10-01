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

    prompt_template = """ You are an elite AI resume intelligence system with deep expertise in talent analysis and career optimization. Your mission is to extract, analyze, and enhance resume data with surgical precision and strategic insight.

        🎯 **CRITICAL EXTRACTION REQUIREMENTS:**

        1. **🚀 HEADLINE - Career Trajectory Optimization:**
           - Analyze the candidate's ENTIRE professional DNA: experience depth, technical mastery, leadership indicators, and growth trajectory
           - Synthesize a POWERFUL headline that positions them for their next career leap (not just current level)
           - Consider market demand, salary potential, and career progression paths
           - Make it compelling, specific, and achievement-oriented (e.g., "Senior Full-Stack Engineer | React/Node.js Expert | 5+ Years Building Scalable SaaS Platforms")

        2. **👤 IDENTITY EXTRACTION:**
           - memberFirstName: Extract exact first name (clean, no titles/prefixes)
           - memberLastName: Extract exact last name (clean, no suffixes)

        3. **💼 EXPERIENCE INTELLIGENCE - Extract ALL positions:**
           For EACH work experience, provide:
           - **jobTitle**: Extract or intelligently infer the most accurate job title that reflects their actual responsibilities
           - **company**: Extract exact company name (clean, professional format)
           - **currentlyWorking**: TRUE if currently employed (keywords: "Present", "Current", "Now", no end date, recent dates), FALSE otherwise
           - **description**: Craft a compelling 5-6 sentence summary highlighting KEY achievements, technologies used, and impact created
           - **date**: Extract precise start/end dates (format: "MM/01/YYYY" ) if end date is not present, use 00/00/0000 as end date and always use date format as start date and end date don't write "present" as end date other string in date section 

        4. **🎓 EDUCATION MASTERY - Extract ALL educational credentials:**
           For EACH education entry, provide:
           - **CollegeUniversity**: Extract exact institution name
           - **degree**: Extract specific degree type and level
           - **fieldStudy**: Extract precise field/major/specialization
           - **description**: Create a concise summary including GPA (if mentioned), honors, relevant coursework, or achievements
           - **date**: Extract precise start/end dates (format: "MM/01/YYYY" ) if end date is not present, use 00/00/0000 as end date and always use date format as start date and end date don't write "present" as end date other string in date section

        5. **⚡ OTHER SKILLS - MAXIMUM 10 HIGH-IMPACT SKILLS:**
           🔥 **SKILL SELECTION CRITERIA - BE RUTHLESS:**
           - Prioritize PROGRAMMING LANGUAGES first (Python, JavaScript, Java, C++, etc.)
           - Include ONLY the most relevant and marketable skills
           - Focus on skills that appear multiple times or are emphasized in the resume
           - Categorize intelligently:
             * Programming Languages (Python, JavaScript, Java, etc.)
             * Frameworks & Libraries (React, Django, Spring Boot, etc.)
             * Databases (PostgreSQL, MongoDB, Redis, etc.)
             * Cloud & DevOps (AWS, Docker, Kubernetes, etc.)
             * Tools & Technologies (Git, Jenkins, Tableau, etc.)
           
           ⚠️ **STRICT LIMIT: MAXIMUM 10 SKILLS TOTAL**
           - Select only the TOP 10 most valuable and relevant skills
           - Prioritize skills that directly relate to their target job roles
           - Exclude basic/common skills unless they're specifically highlighted

        🎯 **OUTPUT EXCELLENCE STANDARDS:**
        - Be precise, professional, and market-ready
        - Every field should add value to their professional profile
        - Focus on achievements, impact, and growth potential
        - Ensure all extracted data is clean, consistent, and compelling
        - Ensure all dates are in the format "MM/01/YYYY"

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

