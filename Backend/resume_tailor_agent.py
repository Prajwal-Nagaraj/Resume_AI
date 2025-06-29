import os
import json
import asyncio
from pydantic import BaseModel, ValidationError
from typing import List, Dict, Any, Optional
from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama

# --- Pydantic Models for Data Structure ---
# These models ensure that the data passed to and received from the agent is well-structured.

class JobDescription(BaseModel):
    """
    A Pydantic model to structure the job description data.
    This is used as input for the tailoring agent.
    """
    title: str
    company: str
    location: Optional[str] = None
    description: str
    requirements: List[str] = []
    preferred_skills: List[str] = []

class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str
    linkedin_url: Optional[str] = None
    location: Optional[str] = None

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: str
    end_date: str
    responsibilities: List[str]

class Education(BaseModel):
    institution: str
    degree: str
    graduation_date: str

class Resume(BaseModel):
    """
    The canonical structure for a resume within the application.
    The agent will receive and output data in this format.
    """
    contact_info: ContactInfo
    summary: str
    experience: List[Experience]
    education: List[Education]
    skills: List[str]

# --- Master Prompt for the Resume Tailoring Agent ---

MASTER_PROMPT = """
You are an expert ATS optimization specialist and a world-class professional resume writer. Your mission is to meticulously tailor a user's resume for a specific job application. You must operate with precision, honesty, and a focus on highlighting the candidate's true strengths in the most compelling way possible.

**Your Task:**
You will receive a user's resume and a job description, both in JSON format. Your goal is to revise the resume to maximize its chances of passing an ATS scan and impressing a human recruiter for this specific job.

**CRITICAL RULES:**
1.  **NO FABRICATION:** You must NEVER invent, exaggerate, or falsify any information. All tailored content must be based on the experience and skills present in the original resume. You are reframing, not inventing.
2.  **JSON-IN, JSON-OUT:** Your final output must be ONLY the tailored resume in a single, valid JSON object, adhering strictly to the input resume's structure. Do not include any explanatory text, markdown, or apologies outside of the JSON block.
3.  **ATS & HUMAN OPTIMIZATION:** The resume must be rich in keywords from the job description but also well-written, professional, and achievement-oriented for human readers.

**Here is the process you must follow:**

1.  **Analyze Job Description:**
   First, deeply analyze the `job_description_json`. Identify the top 5-10 most critical keywords, skills (technical and soft), and qualifications. Understand the core responsibilities of the role.

2.  **Analyze User Resume:**
   Next, carefully review the `resume_json` to understand the candidate's background, skills, and accomplishments.

3.  **Execute Section-by-Section Tailoring:**
   Revise the resume according to these instructions:

   - **`summary`:** Rewrite the professional summary into a powerful 2-3 sentence paragraph. It must directly address the key requirements of the job description and immediately signal that the candidate is a strong fit.

   - **`experience`:** This is the most critical section. For each role, revise the bulleted `responsibilities`:
     - Start every bullet point with a strong action verb (e.g., "Orchestrated," "Engineered," "Maximized," "Analyzed").
     - Quantify results wherever possible using numbers and metrics to demonstrate impact. If the original resume lacks metrics, rephrase to emphasize the outcome of the action.
     - Weave the keywords and phrases from the job description into the bullet points where they align with the user's actual experience. For example, if the job requires "data analysis" and the user has a bullet about creating reports, rephrase it to "Analyzed user data to generate key insights for quarterly reports, improving decision accuracy."

   - **`skills`:** Review the `skills` list. Ensure it prominently features the key skills identified from the job description, provided they are substantiated by the user's experience. You may add skills to this section if they are mentioned in the user's experience but missing from the skills list. Group skills logically (e.g., 'Programming Languages', 'Cloud Technologies', 'Project Management Tools').

**INPUTS:**

**User's Resume:**
```
{resume_json}
```

**Job Description:**
```
{job_description_json}
```

**OUTPUT (Must be only the valid JSON object below):**
"""

class ResumeTailorAgent:
    """
    An agent that uses Ollama to tailor a resume for a specific job description.
    This class encapsulates the logic for prompt construction, API interaction, and data validation.
    """
    def __init__(self, model_name: str = "llama3.2:latest"):
        """
        Initializes the agent with Ollama.
        
        Args:
            model_name (str): The name of the Ollama model to use (e.g., 'llama3.2:latest').
                              This should match the model available in your Ollama installation.
        
        Note:
        This agent is configured to work with Ollama. Ensure Ollama is running and 
        the specified model is pulled (e.g., `ollama pull llama3.2:latest`).
        """
        self.agent = Agent(
            model=Ollama(model_name),
            description=dedent("""\
                You are ResumeTailor-AI, an expert ATS optimization specialist and world-class 
                professional resume writer. Your mission is to meticulously tailor a user's resume 
                for a specific job application with precision, honesty, and focus on highlighting 
                the candidate's true strengths.
                """),
            instructions=dedent("""\
                You will receive a user's resume and a job description, both in JSON format. 
                Your goal is to revise the resume to maximize its chances of passing an ATS scan 
                and impressing a human recruiter for this specific job.

                CRITICAL RULES:
                1. NO FABRICATION: Never invent, exaggerate, or falsify any information. 
                   All tailored content must be based on the original resume.
                2. JSON-ONLY OUTPUT: Return ONLY a valid JSON object matching the input resume structure.
                3. ATS & HUMAN OPTIMIZATION: Rich in keywords but professional and achievement-oriented.

                Your response must be ONLY a valid JSON object. No explanations, markdown, or additional text.
                """),
            markdown=False,
            show_tool_calls=False,
        )

    def parse_json_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse the agent's response and extract JSON content
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
                # Try to find JSON block in markdown format
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(1))
                
                # Try to find the largest JSON object in the text
                json_matches = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text, re.DOTALL)
                for match in sorted(json_matches, key=len, reverse=True):
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue
                
                # Try to find JSON object between the first { and last }
                first_brace = response_text.find('{')
                last_brace = response_text.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_text = response_text[first_brace:last_brace + 1]
                    return json.loads(json_text)
                    
            except json.JSONDecodeError:
                pass
        
        print(f"Failed to parse JSON from response: {response_text[:200]}...")
        return None

    async def tailor_resume(self, resume_data: Dict[str, Any], job_desc: JobDescription) -> Optional[Resume]:
        """
        Takes resume data and a job description, then returns a tailored resume.

        Args:
            resume_data (Dict[str, Any]): The user's resume data as a dictionary.
            job_desc (JobDescription): The job description Pydantic object.

        Returns:
            Resume: A Pydantic object containing the tailored resume data, or None if parsing fails.
        
        Raises:
            ValueError: If the input resume data structure is invalid.
        """
        # Validate input resume data structure
        try:
            validated_resume = Resume.parse_obj(resume_data)
        except ValidationError as e:
            print(f"Input resume data failed validation: {e}")
            raise ValueError("Invalid input resume data structure.") from e

        # Format the prompt with the JSON data
        prompt = MASTER_PROMPT.format(
            resume_json=json.dumps(validated_resume.dict(), indent=2),
            job_description_json=json.dumps(job_desc.dict(), indent=2)
        )

        try:
            print("Sending resume to ResumeTailor-AI for processing...")
            response = await self.agent.arun(prompt)
            
            # Extract content from response object
            response_content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON from response
            tailored_data = self.parse_json_response(response_content)
            
            if tailored_data:
                # Validate the output against the Resume Pydantic model
                try:
                    return Resume.parse_obj(tailored_data)
                except ValidationError as e:
                    print(f"Error: LLM output failed validation. Errors:\n{e}")
                    return None
            else:
                print("Failed to parse JSON from agent response.")
                return None

        except Exception as e:
            print(f"An unexpected error occurred while contacting the LLM: {e}")
            raise

# Example usage function
async def example_usage():
    """Example of how to use the ResumeTailorAgent"""
    
    # Initialize the agent with Ollama
    tailor_agent = ResumeTailorAgent()
    
    # Example job description
    job = JobDescription(
        title="Senior Python Developer",
        company="TechCorp Inc.",
        location="San Francisco, CA",
        description="""
        We are seeking a Senior Python Developer to join our team. The ideal candidate will have:
        - 5+ years of Python development experience
        - Experience with FastAPI, Django, or Flask
        - Knowledge of PostgreSQL and database design
        - Experience with cloud platforms (AWS, GCP)
        - Strong problem-solving skills
        - Experience with agile development methodologies
        """,
        requirements=["Python", "FastAPI", "PostgreSQL", "AWS", "5+ years experience"],
        preferred_skills=["Django", "Flask", "GCP", "Agile"]
    )
    
    # Note: In real usage, you would load this from the resume parser
    # For now, this is just an example structure
    print("ResumeTailorAgent initialized successfully with Ollama!")
    print(f"Ready to tailor resumes for: {job.title} at {job.company}")
    print("Ensure Ollama is running and llama3.2:latest model is pulled.")
    
    return tailor_agent

if __name__ == "__main__":
    # Test the agent initialization
    # Ensure you have 'agno' installed: pip install agno
    # Also ensure Ollama is running and you have pulled the model: ollama pull llama3.2:latest
    asyncio.run(example_usage()) 