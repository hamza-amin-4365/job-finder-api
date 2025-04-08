from app.models.schemas import JobSearchRequest, JobListing
from typing import List

async def fetch_jobs(request: JobSearchRequest) -> List[JobListing]:
    """
    Fetch job listings from Glassdoor based on the search criteria
    """
    # This will be implemented later
    return []