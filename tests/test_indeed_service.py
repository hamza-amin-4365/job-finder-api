import asyncio
from app.models.schemas import JobSearchRequest
from app.services.indeed import fetch_jobs

async def test_indeed_scraper():
    # Create a sample job request with more specific location
    job_request = JobSearchRequest(
        position="Python Developer",
        experience="2 years",
        salary="80000",  # Changed to a more US-appropriate salary
        jobNature="remote",
        location="New York, United States",  # More specific location
        skills="Python, FastAPI, Django"
    )
    
    print("\nFetching Indeed jobs...")
    print(f"Search criteria: {job_request.model_dump_json(indent=2)}\n")
    
    jobs = await fetch_jobs(job_request)
    
    print(f"\nFound {len(jobs)} jobs on Indeed")
    
    # Print details of all jobs
    for i, job in enumerate(jobs, 1):
        print(f"\nJob {i}:")
        print(f"Title: {job.job_title}")
        print(f"Company: {job.company}")
        print(f"Location: {job.location}")
        print(f"Experience: {job.experience}")
        print(f"Salary: {job.salary}")
        print(f"Job Nature: {job.jobNature}")
        print(f"Link: {job.apply_link}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_indeed_scraper())
