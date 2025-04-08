import asyncio
from app.models.schemas import JobSearchRequest
from app.services.linkedin import fetch_jobs

async def test_linkedin_scraper():
    # Create a sample job request
    job_request = JobSearchRequest(
        position="Software Engineer",
        experience="2 years",
        salary="80,000 PKR to 120,000 PKR",
        jobNature="onsite",
        location="Pakistan",
        skills="Python, LLMs, Fine-tuning"
    )
    
    print("Fetching LinkedIn jobs...")
    jobs = await fetch_jobs(job_request)
    
    print(f"Found {len(jobs)} jobs on LinkedIn")
    
    # Print some details of the first few jobs
    for i, job in enumerate(jobs[:5]):  # Show first 5 jobs
        print(f"\nJob {i+1}:")
        print(f"Title: {job.job_title}")
        print(f"Company: {job.company}")
        print(f"Location: {job.location}")
        print(f"Experience: {job.experience}")
        print(f"Link: {job.apply_link}")

if __name__ == "__main__":
    asyncio.run(test_linkedin_scraper())