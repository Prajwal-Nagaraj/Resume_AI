import os
import json
import asyncio
from typing import Dict, Any, Optional
from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama



def create_resume_tailor_agent(model_name: str = "gemma3:4b-it-qat") -> Agent:
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
            You are an expert ATS optimization specialist and world-class 
            professional resume writer. Your mission is to meticulously tailor a user's resume 
            for a specific job application with precision, honesty, and focus on highlighting 
            the candidate's true strengths in the most compelling way possible.
            """),
        instructions=dedent("""\
            You will receive focused resume sections (summary, skills, work_experience, projects) and a job description text. 
            Your goal is to tailor these specific sections to maximize their chances of passing an ATS scan 
            and impressing a human recruiter for this specific job. You must only output the JSON object and nothing else.

            CRITICAL RULES:
            1. NO FABRICATION: You must NEVER invent, exaggerate, or falsify any information. 
               All tailored content must be based on the experience and skills present in the original sections. 
               You are reframing, not inventing.
            2. PRESERVE ALL CONTENT: You must NEVER remove, omit, or delete ANY bullet points, responsibilities, 
               or achievements from the original resume. Every single point must be included in the tailored version.
               This is absolutely mandatory - you are enhancing, not reducing content.
            3. MANDATORY JSON-ONLY OUTPUT: Your response must be ONLY a valid JSON object
               - NO markdown formatting, NO code blocks
               - The first character must be { and the last character must be }
               - Maintain the exact same structure as the input sections
            4. ATS & HUMAN OPTIMIZATION: The sections must be rich in keywords from the job description but also 
               well-written, professional, and achievement-oriented for human readers.
            5. PRESERVE STRUCTURE: Keep the same field names and structure as the input sections.

            PROCESS TO FOLLOW:

            1. Analyze Job Description:
               First, deeply analyze the job description. Identify the top 5-10 most critical keywords, skills 
               (technical and soft), and qualifications. Understand the core responsibilities of the role.

            2. Analyze Resume Sections:
               Next, carefully review the provided sections to understand the candidate's background, skills, and accomplishments.

            3. Execute Section-by-Section Tailoring:
               Tailor the sections according to these instructions:

               - Summary: Rewrite the professional summary into a powerful 2-3 sentence paragraph that directly 
                 addresses the key requirements of the job description. It must immediately signal that the candidate 
                 is a strong fit for this specific role. Include relevant keywords from the job description while 
                 maintaining authenticity based on the candidate's actual experience.

               - Skills: Review and reorganize the skills section. Ensure it prominently features the key skills 
                 identified from the job description, provided they are substantiated by the user's experience. 
                 Classify the skills into separate categories that are relevant to the job description.
                 Prioritize the most relevant skills for this specific job.

               - Work Experience: This is the most critical section. PRESERVE ALL work experience entries.
                 For each work experience entry, you must:
                 * MANDATORY: KEEP ALL existing bullet points/responsibilities - do not remove or omit any content whatsoever
                 * Count the original bullet points and ensure the same count appears in your output
                 * ENHANCE each bullet point by starting with a strong action verb (e.g., "Orchestrated," "Engineered," "Maximized," "Analyzed")
                 * Quantify results wherever possible using numbers and metrics to demonstrate impact. If the original resume 
                   lacks metrics, rephrase to emphasize the outcome of the action.
                 * Weave the keywords and phrases from the job description into the bullet points where they align with 
                   the user's actual experience.
                 * ABSOLUTE REQUIREMENT: MAINTAIN the complete work history - every job, every responsibility, every achievement must be included
                 * If the original has 5 bullet points, your output must have 5 bullet points (enhanced, not removed)

               - Projects: Enhance project descriptions to highlight relevant technologies, skills, and outcomes that align 
                 with the job description. For each project:
                 * MANDATORY: KEEP ALL existing projects - do not remove any
                 * MANDATORY: KEEP ALL existing project description points - do not remove or omit any content
                 * Count the original description bullet points and ensure the same count appears in your output
                 * ENHANCE descriptions with relevant keywords from the job description
                 * Emphasize technologies and skills that match the job requirements
                 * Quantify results and impact where possible
                 * If the original project has 3 description points, your output must have 3 description points (enhanced, not removed)

            ABSOLUTE FINAL REQUIREMENT - PURE JSON ONLY:
            Your response must be ONLY a valid JSON object with the tailored sections. This is mandatory and non-negotiable.
            - Begin with { and end with }
            - NO text before the JSON, NO text after the JSON
            - NO markdown, NO code blocks, NO backticks
            - NO explanations, NO apologies, NO comments
            - Just the raw JSON object and absolutely nothing else
            - Maintain the exact same structure as the input sections
            
            FINAL REMINDER: DO NOT REMOVE ANY CONTENT. Every bullet point, responsibility, achievement, and project description 
            from the original resume MUST appear in your tailored output. You are enhancing and optimizing, NOT reducing or summarizing.
            The total number of bullet points in each section should remain exactly the same.
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

async def tailor_resume(resume_data: Dict[str, Any], job_description: str, model_name: str = "llama3.2:latest") -> Optional[Dict[str, Any]]:
    """
    Takes focused resume data and a job description, then returns tailored sections.

    Args:
        resume_data (Dict[str, Any]): The user's focused resume data (skills, work_experience, projects).
        job_description (str): The job description as a string.
        model_name (str): The name of the Ollama model to use.

    Returns:
        Dict[str, Any]: A dictionary containing the tailored resume sections, or None if parsing fails.
    """
    
    # Create the agent
    agent = create_resume_tailor_agent(model_name)
    
    # Clean the job description text
    job_description_text = job_description.replace('\n', ' ')
    
    # Create the prompt with the focused resume sections and job description
    prompt = f"""
    Please tailor the following focused resume sections for the specific job description provided. Follow all the rules and guidelines specified in your instructions.

    Resume Sections to Tailor:
    ---
    {json.dumps(resume_data, indent=2)}
    ---

    Job Description:
    ---
    {job_description_text}
    ---

    CRITICAL REMINDERS:
    1. Return ONLY a valid JSON object with the tailored resume sections. Your response must start with {{ and end with }}. NO other text allowed.
    2. PRESERVE ALL CONTENT: Do not remove any bullet points, responsibilities, or achievements. Enhance them, don't delete them.
    3. Maintain the exact same number of bullet points in each section as the original resume.
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
    
    # Example job description
    job_description = """
    We are seeking a Senior Python Developer to join our team. The ideal candidate will have:
    - 5+ years of Python development experience
    - Experience with FastAPI, Django, or Flask
    - Knowledge of PostgreSQL and database design
    - Experience with cloud platforms (AWS, GCP)
    - Strong problem-solving skills
    - Experience with agile development methodologies
    """
    
    # Example focused resume data (what would be sent to the tailoring agent)
    focused_resume_example = {
        "summary": "Experienced software developer with 3+ years of experience in web development and database management. Skilled in Python, JavaScript, and modern frameworks.",
        "skills": {
            "Technical": ["Python", "JavaScript", "SQL"],
            "Programming Languages": ["Python", "JavaScript", "Java"],
            "Frameworks": ["Django", "React", "Node.js"],
            "Tools": ["Git", "Docker", "Linux"],
            "Databases": ["MySQL", "MongoDB"],
            "Other": ["Problem Solving", "Team Leadership"]
        },
        "work_experience": [
            {
                "company": "Example Corp",
                "title": "Software Developer",
                "start_date": "2020-01",
                "end_date": "Present",
                "description": ["Developed web applications using Python", "Collaborated with cross-functional teams"]
            }
        ],
        "projects": [
            {
                "title": "E-commerce Platform",
                "description": ["Built full-stack web application", "Implemented user authentication"],
                "technologies_used": ["Python", "Django", "PostgreSQL"]
            }
        ]
    }
    
    print("Resume tailor functions ready with Ollama!")
    print("Ready to tailor focused resume sections (summary, skills, work_experience, projects)")
    print("Ensure Ollama is running and llama3.2:latest model is pulled.")
    
    # Example usage:
    # tailored_sections = await tailor_resume(focused_resume_example, job_description)
    
    return {"job_description": job_description, "focused_resume_example": focused_resume_example}

if __name__ == "__main__":
    # Test the resume tailor functions
    # Ensure you have 'agno' installed: pip install agno
    # Also ensure Ollama is running and you have pulled the model: ollama pull llama3.2:latest
    asyncio.run(example_usage())