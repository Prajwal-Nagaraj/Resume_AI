import asyncio
import os
from typing import List, Optional, Dict
from pathlib import Path
import json # Added for json.dumps
import docx # type: ignore
from pydantic import BaseModel, Field
from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama # Or any other model you prefer, e.g., agno.models.openai.OpenAIChat
# Helper function to load resume text from DOCX
def load_resume_from_docx(file_path: str) -> str:
    """Loads text content from a .docx file."""
    try:
        doc = docx.Document(file_path)
        full_text = [para.text for para in doc.paragraphs]
        return "\\n".join(full_text)
    except Exception as e:
        print(f"Error loading resume from {file_path}: {e}")
        return ""

# Helper function to load resume text from PDF
def load_resume_from_pdf(file_path: str) -> str:
    """Loads text content from a .pdf file."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        full_text = []
        for page in doc:
            full_text.append(page.get_text())
        doc.close()
        return "\\n".join(full_text)
    except Exception as e:
        print(f"Error loading resume from {file_path}: {e}")
        return ""

# Helper function to load resume text from any supported format
def load_resume_text(file_path: str) -> str:
    """Loads text content from supported file formats."""
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.pdf':
        return load_resume_from_pdf(file_path)
    elif file_extension in ['.docx', '.doc']:
        return load_resume_from_docx(file_path)
    else:
        print(f"Unsupported file format: {file_extension}")
        return ""

# Initialize the Agno Agent for Resume Parsing (without strict response model)
resume_parser_agent = Agent(
    model=Ollama("llama3.2:latest"), # Using a recommended Ollama model, adjust if needed. Ensure Ollama is running and the model is pulled.
    description=dedent("""\
        You are ResumeParser-AI, an intelligent agent designed to meticulously parse resumes
        and extract information into a structured JSON format. Your goal is to accurately capture
        all key details from a given resume text.
        """),
    instructions=dedent("""\
        You will be given the raw text extracted from a resume document.
        Your task is to analyze this text and return a well-structured JSON object with ALL the information you find.
        
        CRITICAL JSON-ONLY REQUIREMENT: 
        - Your response must be ONLY a valid JSON object
        - NO explanations, NO markdown formatting, NO additional text
        - NO code blocks, NO backticks, NO ```json``` formatting
        - NO introductory text, NO concluding text
        - ONLY the raw JSON object starting with { and ending with }
        - The first character of your response must be { and the last character must be }
        
        The JSON structure should follow this format (these are just examples - extract ALL actual content):
        {
          "contact_info": {
            "name": "Full name of the candidate",
            "email": "email@example.com",
            "phone": "phone number",
            "linkedin": "LinkedIn profile URL",
            "github": "GitHub profile URL",
            "portfolio": "Portfolio website URL"
          },
          "summary": "Complete professional summary or objective statement",
          "work_experience": [
            {
              "company": "Company Name",
              "title": "Job Title",
              "start_date": "YYYY-MM",
              "end_date": "YYYY-MM or Present",
              "location": "Job location",
              "description": ["ALL responsibilities listed", "ALL achievements mentioned", "ALL key contributions", "ALL bullet points from this job"]
            }
          ],
          "education": [
            {
              "institution": "University Name",
              "degree": "Degree Type",
              "major": "Field of Study",
              "graduation_date": "YYYY-MM",
              "gpa": "GPA if mentioned",
              "location": "Institution location"
            }
          ],
          "skills": {
            "Technical": ["ALL technical skills mentioned"],
            "Programming Languages": ["ALL programming languages"],
            "Frameworks": ["ALL frameworks and libraries"],
            "Tools": ["ALL tools and software"],
            "Databases": ["ALL database systems"],
            "Languages": ["ALL spoken languages"],
            "Soft Skills": ["ALL soft skills mentioned"],
            "Other": ["ANY other skills not categorized above"]
          },
          "projects": [
            {
              "title": "Project Name",
              "description": ["COMPLETE project description", "ALL key features", "ALL outcomes and results", "ALL details mentioned"],
              "url": "Project URL if available",
              "technologies_used": ["ALL technologies, frameworks, and tools used"]
            }
          ],
          "certifications": ["ALL certifications mentioned"],
          "awards_and_honors": ["ALL awards, honors, and recognitions"],
          "languages": ["ALL languages with proficiency levels"]
        }

        CRITICAL EXTRACTION GUIDELINES:
        1. **Extract EVERYTHING**: Do not limit the number of items. If there are 20 skills, extract all 20. If there are 10 bullet points under a job, extract all 10.
        2. **Contact Information**: Extract ALL contact details found (name, email, phone, LinkedIn, GitHub, portfolio, address, etc.).
        3. **Summary/Objective**: Extract the COMPLETE summary or objective statement, not just a portion.
        4. **Work Experience**: For each position, extract ALL responsibilities, achievements, and bullet points mentioned. Do not truncate or summarize.
        5. **Education**: Extract ALL educational institutions, degrees, certifications, coursework, and academic details.
        6. **Skills**: Create comprehensive skill categories and extract EVERY skill mentioned. Include technical skills, programming languages, frameworks, tools, databases, soft skills, etc.
        7. **Projects**: Extract ALL projects with COMPLETE descriptions, features, outcomes, and technologies used.
        8. **Certifications**: List EVERY professional certification, license, or credential mentioned.
        9. **Awards and Honors**: Include ALL awards, honors, recognitions, achievements, and accolades.
        10. **Languages**: List ALL languages with their proficiency levels if mentioned.

        COMPLETENESS IS KEY: Your goal is to extract 100% of the resume content, not just examples or summaries.
        If certain information is not present, use null for optional fields or empty arrays for lists.
        Ensure all descriptions are broken down into comprehensive bullet points (arrays of strings).
        
        ABSOLUTE FINAL REQUIREMENT - JSON ONLY:
        Your response must be ONLY a valid JSON object. Period. No exceptions.
        - Start with { and end with }
        - NO markdown, NO code blocks, NO explanations
        - NO text before or after the JSON
        - Just the pure JSON object and nothing else
        - This is mandatory and non-negotiable
        """),
    # Removed response_model to allow flexible JSON output
    markdown=False, # Disabled markdown to get cleaner JSON output
    show_tool_calls=False,
    # debug_mode=True # Provides more verbose logging from Agno
)

def parse_json_response(response_text: str) -> Optional[Dict]:
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


async def parse_resume_raw_json(resume_file_path: str) -> Optional[Dict]:
    """
    Alternative function that returns raw JSON data without StructuredResume conversion
    """
    print(f"Loading resume from: {resume_file_path}")
    resume_text = load_resume_text(resume_file_path)

    if not resume_text:
        print("Failed to load resume text.")
        return None

    print("Resume text loaded. Sending to ResumeParser-AI for processing...")
    
    prompt = f"""
    Please parse the following resume text and extract the information into the structured JSON format.

    Resume Text:
    ---
    {resume_text}
    ---

    CRITICAL: Return ONLY a valid JSON object with all the extracted resume information. Your response must start with {{ and end with }}. NO other text allowed.
    """
    
    try:
        response = await resume_parser_agent.arun(prompt)
        
        # Extract content from response object
        response_content = response.content if hasattr(response, 'content') else str(response)
        
        json_data = parse_json_response(response_content)
        
        if json_data:
            print("Resume parsed successfully! Returning raw JSON data.")
            return json_data
        else:
            print("Failed to parse JSON from agent response.")
            return None
            
    except Exception as e:
        print(f"An error occurred during resume parsing: {e}")
        return None

async def main():

    resume_path = r"C:\Users\Prajwal\Downloads\Resume-Tailor\Backend\uploads\Prajwal_resume.pdf" # REPLACE WITH YOUR RESUME FILE PATH

    print("Standard parsing failed. Trying raw JSON parsing...")
    
    # Try raw JSON parsing as fallback
    raw_json_data = await parse_resume_raw_json(resume_path)
    
    if raw_json_data:
        output_data = {"resume_latest": raw_json_data}
        output_filename = "struc_resume_latest_raw.json"
        
        try:
            with open(output_filename, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\\\\nSuccessfully saved raw JSON resume data to {output_filename}")
        except Exception as e:
            print(f"\\\\nError saving raw JSON resume data to file: {e}")
    else:
        print("Both parsing methods failed.")

if __name__ == "__main__":
    # Ensure you have 'python-docx' and 'agno' installed:
    # pip install python-docx agno ollama (if using ollama)
    # Also ensure Ollama is running and you have pulled the model specified (e.g., ollama pull qwen3:8b)
    asyncio.run(main()) 