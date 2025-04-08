from app.models.schemas import JobSearchRequest, JobListing
from typing import List
from app.config import OPENAI_API_KEY, RELEVANCE_THRESHOLD

async def filter_relevant_jobs(request: JobSearchRequest, jobs: List[JobListing]) -> List[JobListing]:
    """
    Filter jobs by relevance using LLM technology
    """
    # This will be implemented later with actual LLM integration
    return jobs  # For now, return all jobs