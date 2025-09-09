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

class JobMatchAnalysis(BaseModel):
    match_explanation: str
    strengths: list[str]
    gaps: list[str] 
    recommendations: list[str]


async def matching_explanation(data):
    """
    Use OpenAI to analyze the job match and provide an explanation
    """
    if not openai_api_key:
        return {"error": "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."}, 0
    
    # Handle both old format (with job_id/member_id) and new format (complete data structure)
    if "data" in data and "member" in data["data"] and "jobpost" in data["data"]:
        # New format: complete data structure provided
        member_data = data["data"]["member"]
        job_data = data["data"]["jobpost"] 
        match_percentage = data["data"].get("Matching_Percentage", 0)
    else:
        # Old format: just job_id and member_id - would need to fetch data
        # For now, return error asking for complete data structure
        return {"error": "Please provide complete data structure with member and jobpost data"}, 0
    
    prompt_template = """You are an AI career advisor analyzing a job match. Based on the provided job posting and member profile data, provide a detailed analysis of the job match."""
    
    user_prompt = f"""
JOB POSTING:
- Title: {job_data.get('JobTitle', 'N/A')}
- Required Skills: {job_data.get('Required_Skills', 'N/A')}
- Preferred Skills: {job_data.get('PreferredSkills', 'N/A')}
- Qualifications: {job_data.get('Qualifications', 'N/A')}
- Responsibilities: {job_data.get('Key_Responsibilities', 'N/A')}
- Industry: {job_data.get('Industry', 'N/A')}
- Role: {job_data.get('Role', 'N/A')}
- Location: {job_data.get('JobLocation', 'N/A')}

YOUR PROFILE:
- Headline: {member_data.get('Headline', 'N/A')}
- Technical Skills: {member_data.get('TechnicalSkillNames', 'N/A')}
- Other Skills: {member_data.get('OtherSkills', 'N/A')}
- Experience: {member_data.get('Experience', 'N/A')}
- Job Titles: {member_data.get('JobTitles', 'N/A')}
- Education: {member_data.get('Education', 'N/A')}
- Communication Skills: {member_data.get('CommunicationNames', 'N/A')}
- Leadership Skills: {member_data.get('LeadershipNames', 'N/A')}
- Critical Thinking: {member_data.get('CriticalThinkingNames', 'N/A')}
- Collaboration: {member_data.get('CollaborationNames', 'N/A')}
- Character: {member_data.get('CharacterNames', 'N/A')}
- Creativity: {member_data.get('CreativityNames', 'N/A')}
- Growth Mindset: {member_data.get('GrowthMindsetNames', 'N/A')}
- Mindfulness: {member_data.get('MindfulnessNames', 'N/A')}
- Fortitude: {member_data.get('FortitudeNames', 'N/A')}
- City: {member_data.get('CityName', 'N/A')}

MATCH RESULT:
- Match Percentage: {match_percentage}%

MATCHING ALGORITHM COMPONENTS:
1. Required Skills (30%): Job's Required Skills matched against your Technical Skills and Soft Skills (Character, Collaboration, Communication, Creativity, Critical Thinking, Fortitude, Growth Mindset, Leadership, Mindfulness) and Other Skills
2. Preferred Skills (15%): Job's Preferred Skills matched against your Technical Skills and Other Skills
3. Other Skills (10%): Job's Required & Preferred Skills matched against your Technical Skills and Other Skills
4. Qualifications (15%): Job's Qualifications matched against your Education and Experience
5. Responsibilities (15%): Job's Key Responsibilities matched against your Experience
6. Industry (5%): Job's Industry matched against your Industry experience
7. Role (5%): Job's Role matched against your Job Titles
8. Location (5%): Job's Location matched against your City

Based on the above information and matching algorithm, provide a detailed explanation of:
1. Why your profile received a {match_percentage}% match score for this job
2. Identify the strongest matching areas between your profile and the job
3. Identify skills or qualifications gaps you should work on to improve your match percentage
4. Provide 3-5 specific, actionable recommendations for how you can improve your match score

Provide your response with these components:
- match_explanation: detailed explanation text of why the profile received this match score
- strengths: list of matching strengths between the profile and job (provide as array of strings)
- gaps: list of skill/qualification gaps that should be addressed (provide as array of strings)  
- recommendations: list of specific, actionable recommendations for improvement (provide as array of strings)

IMPORTANT: strengths, gaps, and recommendations MUST be arrays of strings, not single strings or other formats.
"""

    try:
        # Get the async client
        client = await get_async_client()
        
        completion = await client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_template},
                {"role": "user", "content": user_prompt}
            ],
            response_format=JobMatchAnalysis,
        )

        analysis_response = completion.choices[0].message
        total_tokens = completion.usage.total_tokens
        
        if hasattr(analysis_response, 'refusal') and analysis_response.refusal:
            print(f"Model refused to respond: {analysis_response.refusal}")
            return None, total_tokens
        else:
            parsed_data = analysis_response.parsed
            return parsed_data, total_tokens
            
    except Exception as e:
        return {"error": f"Error analyzing job match: {str(e)}"}, 0


# # Legacy function for backward compatibility
# async def matching_explanation(input_question):
#     """
#     Legacy function - use analyze_job_match instead
#     """
#     return await matching_explanation(input_question)