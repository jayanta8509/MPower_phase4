from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime

class Date(BaseModel):
    dateFrom: Optional[str] = None
    dateTo: Optional[str] = None

class Experience(BaseModel):
    jobTitle: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    date: Optional[Date] = None

class Education(BaseModel):
    CollegeUniversity: Optional[str] = None
    degree: Optional[str] = None
    fieldStudy: Optional[str] = None
    description: Optional[str] = None
    date: Optional[Date] = None

class ProfileData(BaseModel):
    headline: Optional[str] = None
    memberFirstName: Optional[str] = None
    memberLastName: Optional[str] = None
    experience: List[Experience] = []
    education: List[Education] = []
    otherSkillName: List[str] = []
    city: Optional[str] = None
    state: Optional[str] = None
    pronoun: Optional[str] = None
    memberEthnicity: Optional[str] = None
    age: Optional[str] = None
    memberGender: Optional[str] = None
    sexualOrient: Optional[str] = None
    nationality: Optional[str] = None
    personalFamily: Optional[str] = None
    jobLevel: Optional[str] = None
    employmentType: Optional[str] = None
    industry: Optional[str] = None
    memberEducationLevel: Optional[str] = None
    communication: Optional[str] = None
    leadership: Optional[str] = None
    metacognition: Optional[str] = None
    criticalThinking: Optional[str] = None
    collaboration: Optional[str] = None
    character: Optional[str] = None
    creativity: Optional[str] = None
    growthMindset: Optional[str] = None
    mindfulness: Optional[str] = None
    fortitude: Optional[str] = None
    race: Optional[str] = None
    technicalSkill: List[str] = []

def extract_skills_from_text(text: str) -> List[str]:
    """Extract technical skills from text using common programming/tech keywords"""
    if not text:
        return []
    
    # Common technical skills to look for
    tech_skills = [
        'Python', 'C++', 'C', 'Java', 'JavaScript', 'SQL', 'Django', 'Flask',
        'Machine Learning', 'Deep Learning', 'NLP', 'AI', 'Artificial Intelligence',
        'Data Science', 'TensorFlow', 'PyTorch', 'scikit-learn', 'Pandas', 'NumPy',
        'HTML', 'CSS', 'React', 'Node.js', 'MongoDB', 'PostgreSQL', 'MySQL',
        'AWS', 'Docker', 'Kubernetes', 'Git', 'Linux', 'Cloud Computing',
        'Data Structure', 'Algorithm', 'Operating System', 'DBMS', 'Computer Networking'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in tech_skills:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicates

def parse_date_range(start_date: str, end_date: str) -> Date:
    """Parse date range from LinkedIn format"""
    date_from = None
    date_to = None
    
    if start_date:
        try:
            # Handle formats like "Jun 2024", "2020", etc.
            date_from = start_date.strip()
        except:
            date_from = None
    
    if end_date and end_date.lower() != 'present':
        try:
            date_to = end_date.strip()
        except:
            date_to = None
    elif end_date and end_date.lower() == 'present':
        date_to = "Present"
    
    return Date(dateFrom=date_from, dateTo=date_to)

def classify_linkedin_profile(profile_data: dict) -> ProfileData:
    """Classify a single LinkedIn profile into the structured format"""
    
    # Extract basic information
    first_name = profile_data.get('first_name')
    last_name = profile_data.get('last_name')
    headline = profile_data.get('position', profile_data.get('about', ''))
    
    # Extract location information
    city = None
    state = None
    if profile_data.get('city'):
        location_parts = profile_data['city'].split(', ')
        if len(location_parts) >= 2:
            city = location_parts[0]
            state = location_parts[1]
        else:
            city = profile_data['city']
    
    # Process experience
    experiences = []
    if profile_data.get('experience'):
        for exp in profile_data['experience']:
            experience = Experience(
                jobTitle=exp.get('title'),
                company=exp.get('company'),
                description=exp.get('description_html') or exp.get('description'),
                date=parse_date_range(exp.get('start_date'), exp.get('end_date'))
            )
            experiences.append(experience)
    
    # Process education
    educations = []
    if profile_data.get('education'):
        for edu in profile_data['education']:
            education = Education(
                CollegeUniversity=edu.get('title'),
                degree=edu.get('degree'),
                fieldStudy=edu.get('field'),
                description=edu.get('description'),
                date=parse_date_range(edu.get('start_year'), edu.get('end_year'))
            )
            educations.append(education)
    
    # Extract technical skills from various sources
    all_text = ' '.join(filter(None, [
        profile_data.get('about', ''),
        profile_data.get('position', ''),
        ' '.join([edu.get('description', '') or '' for edu in profile_data.get('education', [])]),
        ' '.join([(exp.get('description_html') or exp.get('description') or '') 
                 for exp in profile_data.get('experience', [])])
    ]))
    
    technical_skills = extract_skills_from_text(all_text)
    
    # Extract other skills (non-technical)
    other_skills = []
    if profile_data.get('languages'):
        for lang in profile_data['languages']:
            other_skills.append(lang.get('title', ''))
    
    # Determine education level
    education_level = None
    if educations:
        degrees = [edu.degree for edu in educations if edu.degree]
        if any('master' in deg.lower() or 'mba' in deg.lower() for deg in degrees):
            education_level = "Master's"
        elif any('bachelor' in deg.lower() or 'btech' in deg.lower() or 'be' in deg.lower() for deg in degrees):
            education_level = "Bachelor's"
        elif any('diploma' in deg.lower() for deg in degrees):
            education_level = "Diploma"
    
    # Determine job level and industry from experience
    job_level = None
    industry = None
    if experiences:
        # Try to extract industry from company or job title
        for exp in experiences:
            if exp.jobTitle:
                title_lower = exp.jobTitle.lower()
                if any(word in title_lower for word in ['senior', 'lead', 'principal', 'manager']):
                    job_level = "Senior"
                elif any(word in title_lower for word in ['junior', 'intern', 'entry']):
                    job_level = "Junior"
                elif any(word in title_lower for word in ['director', 'vp', 'head']):
                    job_level = "Executive"
        
        # Simple industry detection based on job titles/companies
        all_exp_text = ' '.join(filter(None, [exp.jobTitle for exp in experiences] + 
                                            [exp.company for exp in experiences]))
        if any(word in all_exp_text.lower() for word in ['software', 'tech', 'developer', 'engineer']):
            industry = "Technology"
        elif any(word in all_exp_text.lower() for word in ['finance', 'bank', 'investment']):
            industry = "Finance"
        elif any(word in all_exp_text.lower() for word in ['health', 'medical', 'hospital']):
            industry = "Healthcare"
    
    return ProfileData(
        headline=headline,
        memberFirstName=first_name,
        memberLastName=last_name,
        experience=experiences,
        education=educations,
        otherSkillName=other_skills,
        city=city,
        state=state,
        technicalSkill=technical_skills,
        memberEducationLevel=education_level,
        # Set defaults for fields not available in LinkedIn data
        pronoun=None,
        memberEthnicity=None,
        age=None,
        memberGender=None,
        sexualOrient=None,
        nationality=None,
        personalFamily=None,
        jobLevel=job_level,
        employmentType=None,
        industry=industry,
        communication=None,
        leadership=None,
        metacognition=None,
        criticalThinking=None,
        collaboration=None,
        character=None,
        creativity=None,
        growthMindset=None,
        mindfulness=None,
        fortitude=None,
        race=None
    )

def process_multiple_profiles(linkedin_data) -> ProfileData:
    """Process LinkedIn profile data - handles both single profiles and lists"""
    if not linkedin_data:
        return None
    
    # If it's a list, process the first profile
    if isinstance(linkedin_data, list):
        if len(linkedin_data) == 0:
            return None
        profile = linkedin_data[0]
    else:
        # If it's a single dict, use it directly
        profile = linkedin_data
    
    try:
        classified_profile = classify_linkedin_profile(profile)
        return classified_profile
    except Exception as e:
        print(f"Error processing profile {profile.get('first_name', 'Unknown')} {profile.get('last_name', '')}: {str(e)}")
        return None

def save_to_json(profiles: List[ProfileData], filename: str = "classified_profiles.json"):
    """Save classified profiles to JSON file"""
    profiles_dict = [profile.dict() for profile in profiles]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(profiles_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(profiles)} profiles to {filename}")
