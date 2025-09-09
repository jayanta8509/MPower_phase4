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
    industry: str
    memberEducationLevel: str
    communication: str
    leadership: str
    metacognition: str
    criticalThinking: str
    collaboration: str
    character: str
    creativity: str
    growthMindset: str
    mindfulness: str
    fortitude: str
    technicalSkill: list[str]






class resume_data(BaseModel):
    steps: list[Step]


async def analyze_resume_array(input_question):

    prompt_template = """ You are an expert resume parser and analyzer. Extract and analyze the following information from the resume data provided:

        **Professional Information:**
        - industry: Identify the primary industry based on work experience, skills, and career focus
        - memberEducationLevel: Determine the highest education level achieved (e.g., "High School", "Bachelor's Degree", "Master's Degree", "PhD", "Professional Certification", etc.)
        
        **Soft Skills Assessment (Provide descriptive assessment - NOT numeric ratings):**
        - communication: Assess communication skills based on resume presentation, writing quality, professional experience, and any communication-related achievements
        - leadership: Evaluate leadership experience and potential based on roles, responsibilities, team management, and leadership achievements
        - metacognition: Assess self-awareness and learning ability from career progression, skill development, and evidence of self-reflection
        - criticalThinking: Evaluate problem-solving and analytical skills from project descriptions, accomplishments, and complex challenges addressed
        - collaboration: Assess teamwork and collaborative experience from work history, cross-functional projects, and team-based achievements
        - character: Evaluate integrity and professional character from career consistency, ethical considerations, and professional achievements
        - creativity: Assess creative and innovative capabilities from projects, solutions, creative problem-solving, and innovative approaches
        - growthMindset: Evaluate learning orientation and adaptability from skill acquisition, career transitions, and continuous development
        - mindfulness: Assess emotional intelligence and self-awareness from professional interactions, work-life balance considerations, and growth mindset
        - fortitude: Evaluate resilience and persistence from career challenges overcome, goal achievement, and demonstrated perseverance
        
        **Technical Skills:**
        - technicalSkill: Extract all technical skills as an array of strings including:
          * Programming languages (e.g., Python, JavaScript, Java)
          * Frameworks and libraries (e.g., React, Django, TensorFlow)
          * Tools and technologies (e.g., Git, Docker, Kubernetes)
          * Databases (e.g., MySQL, PostgreSQL, MongoDB)
          * Cloud platforms (e.g., AWS, Azure, Google Cloud)
          * Certifications (e.g., AWS Certified, PMP, Scrum Master)
          * Domain-specific skills (e.g., Data Analysis, Machine Learning, UI/UX Design)

        **Important Guidelines:**
        - Focus on professional qualifications and skills that can be evidenced from the resume
        - Use "Not specified" or "Unknown" for information that cannot be determined
        - CRITICAL: Do NOT use numeric ratings for any fields - use descriptive text instead
        - All assessments should be based on evidence found in the resume content
        - Provide thoughtful, personalized assessments rather than generic responses
        - For soft skills, provide specific examples or evidence when possible
        - Return the analysis as a single Step object within the steps array
        - Ensure all technical skills are returned as individual string elements in the array

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

