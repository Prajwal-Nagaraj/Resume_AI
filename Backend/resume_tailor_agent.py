import os
import json
import asyncio
from typing import Dict, Any, Optional
from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama



def create_resume_tailor_agent(model_name: str = "llama3.2:latest") -> Agent:
    """
    Creates and returns a resume tailor agent using Ollama.
    
    Args:
        model_name (str): The name of the Ollama model to use (e.g., 'llama3.2:latest').
                          This should match the model available in your Ollama installation.
    
    Returns:
        Agent: The configured resume tailor agent.
    """
    return Agent(
        model=Ollama(model_name),
        description=dedent("""\
            You are ResumeTailor-AI, an expert ATS optimization specialist and world-class 
            professional resume writer. Your mission is to meticulously tailor a user's resume 
            for a specific job application with precision, honesty, and focus on highlighting 
            the candidate's true strengths in the most compelling way possible.
            """),
        instructions=dedent("""\
            You will receive a user's resume in JSON format and a job description text. 
            Your goal is to revise the resume to maximize its chances of passing an ATS scan 
            and impressing a human recruiter for this specific job.

            CRITICAL RULES:
            1. NO FABRICATION: You must NEVER invent, exaggerate, or falsify any information. 
               All tailored content must be based on the experience and skills present in the original resume. 
               You are reframing, not inventing.
            2. JSON-IN, JSON-OUT: Your final output must be ONLY the tailored resume in a single, valid JSON object, 
               maintaining the same structure as the input resume. Do not include any explanatory text, markdown, 
               or apologies outside of the JSON block.
            3. ATS & HUMAN OPTIMIZATION: The resume must be rich in keywords from the job description but also 
               well-written, professional, and achievement-oriented for human readers.
            4. PRESERVE STRUCTURE: Keep the same field names and structure as the input resume. If the input has 
               "work_experience", use "work_experience" in output. If it has "skills" as an object with categories, 
               maintain that structure.

            PROCESS TO FOLLOW:

            1. Analyze Job Description:
               First, deeply analyze the job description. Identify the top 5-10 most critical keywords, skills 
               (technical and soft), and qualifications. Understand the core responsibilities of the role.

            2. Analyze User Resume:
               Next, carefully review the resume to understand the candidate's background, skills, and accomplishments.

            3. Execute Section-by-Section Tailoring:
               Revise the resume according to these instructions:

               - Professional Summary/Objective: Rewrite any summary, objective, or about section into a powerful 
                 2-3 sentence paragraph. It must directly address the key requirements of the job description and 
                 immediately signal that the candidate is a strong fit.

               - Experience/Work History: This is the most critical section. For each role, revise the responsibilities/achievements:
                 * Start every bullet point with a strong action verb (e.g., "Orchestrated," "Engineered," "Maximized," "Analyzed").
                 * Quantify results wherever possible using numbers and metrics to demonstrate impact. If the original resume 
                   lacks metrics, rephrase to emphasize the outcome of the action.
                 * Weave the keywords and phrases from the job description into the bullet points where they align with 
                   the user's actual experience.

               - Skills: Review the skills section. Ensure it prominently features the key skills identified from the job 
                 description, provided they are substantiated by the user's experience. Maintain the existing structure 
                 (list or categorized object).

            CRITICAL: Your response must be ONLY a valid JSON object maintaining the exact same structure as the input resume. 
            No explanations, markdown formatting, or additional text.
            """),
        markdown=False,
        show_tool_calls=False,
    )

def parse_json_response(response_text: str) -> Optional[Dict]:
    """
    Parse the agent's response and extract JSON content with improved nested JSON handling
    """
    import re
    
    # Remove any <think> tags and their content
    response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
    response_text = response_text.strip()
    
    try:
        # Try to parse the response directly as JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If direct parsing fails, try to extract JSON from the response
        try:
            # Enhanced markdown JSON block extraction
            # Look for ```json or ``` followed by JSON content
            markdown_patterns = [
                r'```json\s*\n?(.*?)\n?```',
                r'```\s*\n?(.*?)\n?```'
            ]
            
            for pattern in markdown_patterns:
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    json_content = match.group(1).strip()
                    try:
                        return json.loads(json_content)
                    except json.JSONDecodeError:
                        continue
            
            # Find JSON object with proper brace counting
            def extract_json_with_brace_counting(text: str) -> Optional[str]:
                start_idx = text.find('{')
                if start_idx == -1:
                    return None
                
                brace_count = 0
                in_string = False
                escape_next = False
                
                for i, char in enumerate(text[start_idx:], start_idx):
                    if escape_next:
                        escape_next = False
                        continue
                        
                    if char == '\\':
                        escape_next = True
                        continue
                        
                    if char == '"' and not escape_next:
                        in_string = not in_string
                        continue
                        
                    if not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                return text[start_idx:i+1]
                
                return None
            
            json_text = extract_json_with_brace_counting(response_text)
            if json_text:
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: try to find JSON object between the first { and last }
            first_brace = response_text.find('{')
            last_brace = response_text.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_text = response_text[first_brace:last_brace + 1]
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass
                
        except Exception as e:
            print(f"Error during JSON parsing: {e}")
    
    print(f"Failed to parse JSON from response: {response_text[:500]}...")
    return None

async def tailor_resume(resume_data: Dict[str, Any], job_desc: Dict[str, Any], model_name: str = "llama3.2:latest") -> Optional[Dict[str, Any]]:
    """
    Takes resume data and a job description, then returns a tailored resume.

    Args:
        resume_data (Dict[str, Any]): The user's resume data as a dictionary.
        job_desc (Dict[str, Any]): The job description as a dictionary.
        model_name (str): The name of the Ollama model to use.

    Returns:
        Dict[str, Any]: A dictionary containing the tailored resume data, or None if parsing fails.
    """
    
    # Create the agent
    agent = create_resume_tailor_agent(model_name)
    
    # Extract and clean the job description text
    job_description_text = job_desc.get('description', '')
    # Replace newline characters with spaces
    job_description_text = job_description_text.replace('\n', ' ')
    
    # Create the prompt with the resume and job description data
    prompt = f"""
    Please tailor the following resume for the specific job description provided. Follow all the rules and guidelines specified in your instructions.

    User's Resume:
    ---
    {json.dumps(resume_data, indent=2)}
    ---

    Job Description:
    ---
    {job_description_text}
    ---

    Return ONLY a valid JSON object with the tailored resume maintaining the same structure as the input resume.
    """

    try:
        print("Sending resume to ResumeTailor-AI for processing...")
        response = await agent.arun(prompt)
        
        # Extract content from response object
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON from response
        tailored_data = parse_json_response(response_content)
        
        if tailored_data:
            print("Successfully tailored resume!")
            print("Tailored resume:")
            print(tailored_data)
            return tailored_data
        else:
            print("Failed to parse JSON from agent response.")
            return None

    except Exception as e:
        print(f"An unexpected error occurred while contacting the LLM: {e}")
        raise

# Example usage function
async def example_usage():
    """Example of how to use the resume tailor functions"""
    
    # Example job description (flexible structure)
    job = {
        "title": "Senior Python Developer",
        "company": "TechCorp Inc.",
        "location": "San Francisco, CA",
        "description": """
        We are seeking a Senior Python Developer to join our team. The ideal candidate will have:
        - 5+ years of Python development experience
        - Experience with FastAPI, Django, or Flask
        - Knowledge of PostgreSQL and database design
        - Experience with cloud platforms (AWS, GCP)
        - Strong problem-solving skills
        - Experience with agile development methodologies
        """,
        "requirements": ["Python", "FastAPI", "PostgreSQL", "AWS", "5+ years experience"],
        "preferred_skills": ["Django", "Flask", "GCP", "Agile"]
    }
    
    print("Resume tailor functions ready with Ollama!")
    print(f"Ready to tailor resumes for: {job['title']} at {job['company']}")
    print("Ensure Ollama is running and llama3.2:latest model is pulled.")
    
    # Example usage:
    # resume_data = {...}  # Your resume JSON data
    # tailored_resume = await tailor_resume(resume_data, job)
    
    return job

if __name__ == "__main__":
    # Test the resume tailor functions
    # Ensure you have 'agno' installed: pip install agno
    # Also ensure Ollama is running and you have pulled the model: ollama pull llama3.2:latest
    asyncio.run(example_usage())