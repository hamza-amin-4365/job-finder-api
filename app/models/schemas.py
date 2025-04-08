from pydantic import BaseModel, Field
from typing import List, Optional

class JobSearchRequest(BaseModel):
    position: str
    experience: str
    salary: Optional[str] = None
    jobNature: Optional[str] = None
    location: Optional[str] = None
    skills: str

class JobListing(BaseModel):
    job_title: str
    company: str
    experience: str
    jobNature: Optional[str] = None
    location: str
    salary: Optional[str] = None
    apply_link: str
    source: str = Field(..., description="Source of job listing (LinkedIn, Indeed, etc.)")

class JobSearchResponse(BaseModel):
    relevant_jobs: List[JobListing]