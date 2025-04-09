import asyncio
from app.models.schemas import JobSearchRequest, JobListing
from app.services.llm_service import filter_relevant_jobs

async def test_llm_filtering():
    # Create a sample job search request
    request = JobSearchRequest(
        position="Senior Python Developer",
        experience="5 years",
        skills="Python, FastAPI, AWS, Docker, Kubernetes",
        jobNature="remote",
        location="United States",
        salary="150000"
    )
    
    # Create sample job listings - mix of relevant and less relevant jobs
    sample_jobs = [
        JobListing(
            job_title="Senior Python Developer",
            company="Tech Corp",
            experience="5+ years",
            jobNature="Remote",
            location="New York, United States",
            salary="140000-160000",
            apply_link="https://example.com/job1",
            source="Test"
        ),
        JobListing(
            job_title="Junior Python Developer",
            company="Startup Inc",
            experience="1-2 years",
            jobNature="Remote",
            location="United States",
            salary="70000-90000",
            apply_link="https://example.com/job2",
            source="Test"
        ),
        JobListing(
            job_title="Senior Full Stack Developer (Python/React)",
            company="Enterprise Solutions",
            experience="5+ years",
            jobNature="Hybrid",
            location="San Francisco, United States",
            salary="160000-180000",
            apply_link="https://example.com/job3",
            source="Test"
        ),
        JobListing(
            job_title="DevOps Engineer",
            company="Cloud Services Ltd",
            experience="4+ years",
            jobNature="Remote",
            location="United States",
            salary="130000-150000",
            apply_link="https://example.com/job4",
            source="Test"
        )
    ]

    print("\nTesting LLM Job Filtering Service")
    print("-" * 50)
    print(f"Search criteria:")
    print(f"Position: {request.position}")
    print(f"Experience: {request.experience}")
    print(f"Skills: {request.skills}")
    print(f"Job Nature: {request.jobNature}")
    print(f"Location: {request.location}")
    print(f"Salary: {request.salary}")
    print("-" * 50)
    
    print(f"\nTotal jobs before filtering: {len(sample_jobs)}")
    
    # Filter jobs using LLM service
    relevant_jobs = await filter_relevant_jobs(request, sample_jobs)
    
    print(f"Relevant jobs after filtering: {len(relevant_jobs)}")
    
    # Print details of relevant jobs
    print("\nRelevant Jobs Details:")
    print("-" * 50)
    for i, job in enumerate(relevant_jobs, 1):
        print(f"\nJob {i}:")
        print(f"Title: {job.job_title}")
        print(f"Company: {job.company}")
        print(f"Experience: {job.experience}")
        print(f"Job Nature: {job.jobNature}")
        print(f"Location: {job.location}")
        print(f"Salary: {job.salary}")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(test_llm_filtering())