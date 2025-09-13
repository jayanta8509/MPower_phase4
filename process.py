import asyncio
import json

#Scraper imports
from scraper.document_scraper import get_resume_content
from scraper.resume_scraper_string_agent import analyze_resume
from scraper.resume_scraper_array_agent import analyze_resume_array
from scraper.databse_scraper_agent import async_route, fetch_data_async

#McpAgent imports
from McpAgent.character_agent import character_agent
from McpAgent.collaboration_agent import collaboration_agent
from McpAgent.creativity_agent import creativity_agent
from McpAgent.growthmindset_agent import growthmindset_agent
from McpAgent.mindfulness_agent import mindfulness_agent
from McpAgent.technicalskills_agent import technicalskills_agent
from McpAgent.industry_agent import industry_agent
from McpAgent.educationlevel_agent import educationlevel_agent
from McpAgent.communication_agent import communication_agent
from McpAgent.leadership_agent import leadership_agent
from McpAgent.metacognition_agent import metacognition_agent
from McpAgent.criticalthinking_agent import criticalthinking_agent
from McpAgent.fortitude_agent import fortitude_agent

async def main(path):
    resume_data = get_resume_content(path)
    
    # Run all three async functions in parallel
    results = await asyncio.gather(
        analyze_resume_array(resume_data),
        analyze_resume(resume_data),
        fetch_data_async()
    )
    
    # Unpack results
    resume_array, total_tokens1 = results[0]
    string_data, total_tokens2 = results[1]
    databse_data = results[2]
    
    # Extract data for all agents
    resume_step = resume_array.steps[0]
    resume_string_step = string_data.steps[0]
    # Run all MCP agents in parallel
    agent_results = await asyncio.gather(
        character_agent(databse_data['character'], resume_step.character),
        collaboration_agent(databse_data['collaboration'], resume_step.collaboration),
        creativity_agent(databse_data['creativity'], resume_step.creativity),
        growthmindset_agent(databse_data['growthmindset'], resume_step.growthMindset),
        mindfulness_agent(databse_data['mindfulness'], resume_step.mindfulness),
        technicalskills_agent(databse_data['technicalskills'], resume_step.technicalSkill),
        industry_agent(databse_data['industry'], resume_string_step),
        educationlevel_agent(databse_data['educationlevel'], resume_step.memberEducationLevel),
        communication_agent(databse_data['communication'], resume_step.communication),
        leadership_agent(databse_data['leadership'], resume_step.leadership),
        metacognition_agent(databse_data['metacognition'], resume_step.metacognition),
        criticalthinking_agent(databse_data['criticalthinking'], resume_step.criticalThinking),
        fortitude_agent(databse_data['fortitude'], resume_step.fortitude)
    )
    
    # Extract agent results and tokens
    agent_tokens = 0
    processed_results = {}
    agent_names = [
        'character', 'collaboration', 'creativity', 'growthmindset', 
        'mindfulness', 'technicalskills', 'experience', 'educationlevel',
        'communication', 'leadership', 'metacognition', 'criticalthinking', 'fortitude'
    ]
    
    for i, (result, tokens) in enumerate(agent_results):
        # Handle industry_agent differently since it returns experience data
        if agent_names[i] == 'experience':
            # For industry agent, return the complete experience data with industryId populated
            processed_results[agent_names[i]] = result.steps[0].experience if result else []
        else:
            # Store only the matched_ids array (flat structure) for other agents
            processed_results[agent_names[i]] = result.steps[0].id if result else [0]
        agent_tokens += tokens
    
    total_tokens = total_tokens1 + total_tokens2 + agent_tokens
    
    # Remove the "steps" wrapper from string_data and exclude experience data
    clean_string_data = string_data.steps[0] if string_data.steps else {}
    
    # Remove experience from clean_string_data since it's handled by industry_agent
    if hasattr(clean_string_data, 'experience'):
        clean_string_data_dict = clean_string_data.model_dump()
        clean_string_data_dict.pop('experience', None)
    else:
        clean_string_data_dict = clean_string_data
    
    return clean_string_data_dict, processed_results, total_tokens


if __name__ == "__main__":
    path = "Jayanta_Roy_CV.pdf"
    string_data, processed_results, total_tokens = asyncio.run(main(path))
    print("string_data: ", string_data)
    print("processed_results: ", processed_results)
    print("total_tokens: ", total_tokens)

