import asyncio
import os
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing modules
from jobs_scraper import SpeedyApplyTool
from resume_parser_agent import parse_resume_raw_json
# from resume_tailor_agent import ResumeTailorAgent, JobDescription

# Initialize FastAPI app
app = FastAPI(
    title="ResumeTailor API",
    description="API for job search, resume parsing, and automated resume tailoring",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize tools and agents
job_scraper = SpeedyApplyTool()
# resume_tailor_agent = ResumeTailorAgent()

# Storage directories
UPLOAD_DIR = Path("uploads")
TAILORED_RESUMES_DIR = Path("tailored_resumes")
UPLOAD_DIR.mkdir(exist_ok=True)
TAILORED_RESUMES_DIR.mkdir(exist_ok=True)

# In-memory storage for demo (use database in production)
resume_storage: Dict[str, Dict] = {}
extraction_status: Dict[str, Dict] = {}
tailoring_jobs: Dict[str, Dict] = {}

# Pydantic models for API requests/responses
class JobSearchResponse(BaseModel):
    jobs: List[Dict[str, Any]]
    total_count: int
    search_term: str
    location: str

class UploadResponse(BaseModel):
    resume_id: str
    filename: str
    message: str

class ExtractionStatusResponse(BaseModel):
    resume_id: str
    status: str  # "pending", "processing", "completed", "failed"
    extracted_data: Optional[Dict] = None
    error_message: Optional[str] = None

class TailorRequest(BaseModel):
    resume_id: str
    job_descriptions: List[Dict[str, Any]]  # List of job data from search results

class TailorResponse(BaseModel):
    task_id: str
    message: str
    status: str

class TailorStatusResponse(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    tailored_resumes: Optional[List[Dict]] = None
    download_links: Optional[List[str]] = None
    error_message: Optional[str] = None

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ResumeTailor API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "upload": "/api/upload",
            "extract": "/api/extract/{resume_id}",
            "tailor": "/api/tailor",
            "download": "/api/download/{file_key}"
        }
    }

@app.get("/api/search", response_model=JobSearchResponse)
async def search_jobs(
    query: str = Query(..., description="Job search keywords"),
    location: str = Query(..., description="Job location"),
    limit: int = Query(20, description="Maximum number of results"),
    proxy: Optional[str] = Query(None, description="Proxy URL to use for scraping")
):
    """
    Search for job listings using the job scraper
    """
    try:
        # Use the existing job scraper
        filename = job_scraper.find_and_save_jobs(search_term=query, location=location, proxy_url=proxy)
        
        if not filename:
            raise HTTPException(status_code=404, detail="No jobs found or scraping failed")
        
        # Read the CSV file and convert to JSON
        import pandas as pd
        try:
            jobs_df = pd.read_csv(filename)
            jobs_list = jobs_df.head(limit).to_dict('records')
            
            # Clean up the CSV file after reading
            os.remove(filename)
            
            return JobSearchResponse(
                jobs=jobs_list,
                total_count=len(jobs_list),
                search_term=query,
                location=location
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing job data: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job search failed: {str(e)}")

@app.post("/api/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX)
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.docx', '.doc']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file_extension} not supported. Allowed types: {allowed_extensions}"
        )
    
    # Generate unique resume ID
    resume_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{resume_id}_{file.filename}"
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Store resume metadata
        resume_storage[resume_id] = {
            "filename": file.filename,
            "file_path": str(file_path),
            "upload_time": datetime.now().isoformat(),
            "status": "uploaded"
        }
        
        # Initialize extraction status
        extraction_status[resume_id] = {
            "status": "pending",
            "extracted_data": None,
            "error_message": None
        }
        
        return UploadResponse(
            resume_id=resume_id,
            filename=file.filename,
            message="Resume uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/api/extract/{resume_id}", response_model=ExtractionStatusResponse)
async def extract_resume_data(resume_id: str, background_tasks: BackgroundTasks):
    """
    Start resume data extraction process
    """
    if resume_id not in resume_storage:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if resume_id not in extraction_status:
        extraction_status[resume_id] = {
            "status": "pending",
            "extracted_data": None,
            "error_message": None
        }
    
    # Start background extraction task
    background_tasks.add_task(perform_extraction, resume_id)
    
    # Update status to processing
    extraction_status[resume_id]["status"] = "processing"
    
    return ExtractionStatusResponse(
        resume_id=resume_id,
        status="processing",
        extracted_data=None,
        error_message=None
    )

@app.get("/api/extract/{resume_id}/status", response_model=ExtractionStatusResponse)
async def get_extraction_status(resume_id: str):
    """
    Get the status of resume extraction
    """
    if resume_id not in extraction_status:
        raise HTTPException(status_code=404, detail="Extraction status not found")
    
    status_data = extraction_status[resume_id]
    
    return ExtractionStatusResponse(
        resume_id=resume_id,
        status=status_data["status"],
        extracted_data=status_data["extracted_data"],
        error_message=status_data["error_message"]
    )

@app.post("/api/tailor", response_model=TailorResponse)
async def tailor_resume(request: TailorRequest, background_tasks: BackgroundTasks):
    """
    Submit resume and job descriptions for tailoring
    """
    # Validate resume exists and is extracted
    if request.resume_id not in resume_storage:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    if request.resume_id not in extraction_status:
        raise HTTPException(status_code=400, detail="Resume not extracted yet")
    
    if extraction_status[request.resume_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Resume extraction not completed")
    
    if not extraction_status[request.resume_id]["extracted_data"]:
        raise HTTPException(status_code=400, detail="No extracted resume data available")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Initialize tailoring job
    tailoring_jobs[task_id] = {
        "resume_id": request.resume_id,
        "job_descriptions": request.job_descriptions,
        "status": "pending",
        "tailored_resumes": None,
        "download_links": None,
        "error_message": None,
        "created_at": datetime.now().isoformat()
    }
    
    # Start background tailoring task
    background_tasks.add_task(perform_tailoring, task_id)
    
    return TailorResponse(
        task_id=task_id,
        message="Resume tailoring started",
        status="processing"
    )

@app.get("/api/tailor/{task_id}/status", response_model=TailorStatusResponse)
async def get_tailoring_status(task_id: str):
    """
    Get the status of resume tailoring
    """
    if task_id not in tailoring_jobs:
        raise HTTPException(status_code=404, detail="Tailoring task not found")
    
    job_data = tailoring_jobs[task_id]
    
    return TailorStatusResponse(
        task_id=task_id,
        status=job_data["status"],
        tailored_resumes=job_data["tailored_resumes"],
        download_links=job_data["download_links"],
        error_message=job_data["error_message"]
    )

@app.get("/api/download/{file_key}")
async def download_tailored_resume(file_key: str):
    """
    Download a tailored resume file
    """
    file_path = TAILORED_RESUMES_DIR / file_key
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=file_key,
        media_type='application/octet-stream'
    )

# Background task functions

async def perform_extraction(resume_id: str):
    """
    Background task to extract resume data
    """
    try:
        resume_data = resume_storage[resume_id]
        file_path = resume_data["file_path"]
        
        # Use the existing resume parser
        extracted_data = await parse_resume_raw_json(file_path)
        
        if extracted_data:
            extraction_status[resume_id] = {
                "status": "completed",
                "extracted_data": extracted_data,
                "error_message": None
            }
        else:
            extraction_status[resume_id] = {
                "status": "failed",
                "extracted_data": None,
                "error_message": "Failed to extract resume data"
            }
            
    except Exception as e:
        extraction_status[resume_id] = {
            "status": "failed",
            "extracted_data": None,
            "error_message": str(e)
        }

async def perform_tailoring(task_id: str):
    """
    Background task to tailor resumes for multiple jobs
    """
    try:
        job_data = tailoring_jobs[task_id]
        resume_id = job_data["resume_id"]
        job_descriptions = job_data["job_descriptions"]
        
        # Update status to processing
        tailoring_jobs[task_id]["status"] = "processing"
        
        # Get extracted resume data
        resume_data = extraction_status[resume_id]["extracted_data"]
        
        tailored_resumes = []
        download_links = []
        
        for i, job_desc_data in enumerate(job_descriptions):
            try:
                # Create JobDescription object
                job_desc = JobDescription(
                    title=job_desc_data.get("title", "Unknown Title"),
                    company=job_desc_data.get("company", "Unknown Company"),
                    location=job_desc_data.get("location"),
                    description=job_desc_data.get("description", ""),
                    requirements=job_desc_data.get("requirements", []),
                    preferred_skills=job_desc_data.get("preferred_skills", [])
                )
                
                # Tailor resume for this job
                tailored_content = await resume_tailor_agent.tailor_resume(resume_data, job_desc)
                
                if tailored_content:
                    # Generate filename for tailored resume
                    safe_company = "".join(c for c in job_desc.company if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = "".join(c for c in job_desc.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"{resume_id}_{safe_company}_{safe_title}_{i}.json"
                    
                    # Save tailored resume as JSON
                    file_path = TAILORED_RESUMES_DIR / filename
                    with open(file_path, 'w') as f:
                        json.dump(tailored_content.dict(), f, indent=2)
                    
                    tailored_resumes.append({
                        "job_title": job_desc.title,
                        "company": job_desc.company,
                        "tailored_content": tailored_content.dict(),
                        "filename": filename
                    })
                    
                    download_links.append(f"/api/download/{filename}")
                
            except Exception as e:
                print(f"Error tailoring resume for job {i}: {e}")
                continue
        
        if tailored_resumes:
            tailoring_jobs[task_id].update({
                "status": "completed",
                "tailored_resumes": tailored_resumes,
                "download_links": download_links,
                "error_message": None
            })
        else:
            tailoring_jobs[task_id].update({
                "status": "failed",
                "tailored_resumes": None,
                "download_links": None,
                "error_message": "Failed to tailor any resumes"
            })
            
    except Exception as e:
        tailoring_jobs[task_id].update({
            "status": "failed",
            "tailored_resumes": None,
            "download_links": None,
            "error_message": str(e)
        })

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 