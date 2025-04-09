from apify_client import ApifyClient
from typing import List, Optional
import asyncio
from app.models.schemas import JobSearchRequest, JobListing
from app.config import APIFY_API_TOKEN  # Add this to your config.py

async def fetch_jobs(request: JobSearchRequest) -> List[JobListing]:
    """
    Fetch job listings from Indeed using Apify API
    """
    # Execute the Apify API call in a separate thread to avoid blocking the event loop
    loop = asyncio.get_event_loop()
    jobs = await loop.run_in_executor(None, lambda: _fetch_from_apify(request))
    return jobs

def _fetch_from_apify(request: JobSearchRequest) -> List[JobListing]:
    """
    Helper function to fetch job listings from Apify
    """
    jobs = []
    
    try:
        # Initialize the ApifyClient with your API token
        client = ApifyClient(APIFY_API_TOKEN)
        
        # Extract location components - assuming format like "City, Country"
        location_parts = request.location.split(',')
        country = location_parts[-1].strip() if len(location_parts) > 1 else location_parts[0].strip()
        city = location_parts[0].strip() if len(location_parts) > 1 else ""
        
        # Prepare the Actor input
        run_input = {
            "position": request.position,
            "country": country,
            "location": city if city else country,
            "maxItems": 20,  # Limit to 20 jobs to reduce cost and runtime
            "parseCompanyDetails": False,
            "saveOnlyUniqueItems": True,
            "followApplyRedirects": False,
        }
        
        # Run the Actor and wait for it to finish
        run = client.actor("hMvNSpz3JnHgl5jkh").call(run_input=run_input)
        
        # Retrieve the Actor's dataset items
        dataset_id = run["defaultDatasetId"]
        items = list(client.dataset(dataset_id).iterate_items())
        
        # Convert items to JobListing objects
        for item in items:
            job = _convert_to_job_listing(item, request)
            if job:
                jobs.append(job)
                
        print(f"Successfully fetched {len(jobs)} jobs from Indeed via Apify")
        
    except Exception as e:
        print(f"Error fetching jobs from Apify: {e}")
    
    return jobs

def _convert_to_job_listing(item: dict, request: JobSearchRequest) -> Optional[JobListing]:
    """
    Convert an Apify job item to a JobListing object
    """
    try:
        # Extract job nature from jobType if available
        job_nature = "Not specified"
        job_types = item.get("jobType", [])
        if job_types:
            if any("remote" in job_type.lower() for job_type in job_types):
                job_nature = "Remote"
            elif any("hybrid" in job_type.lower() for job_type in job_types):
                job_nature = "Hybrid"
            elif any(("onsite" in job_type.lower() or "on-site" in job_type.lower()) for job_type in job_types):
                job_nature = "Onsite"
            else:
                job_nature = job_types[0]  # Use the first job type if none of the above
        
        # Use the requested job nature if not found in the data
        if job_nature == "Not specified" and request.jobNature:
            job_nature = request.jobNature
        
        # Map fields to JobListing schema
        return JobListing(
            job_title=item.get("positionName", "Not specified"),
            company=item.get("company", "Not specified"),
            experience=request.experience,  # Use the requested experience
            jobNature=job_nature,
            location=item.get("location", "Not specified"),
            salary=item.get("salary", request.salary or "Not specified"),
            apply_link=item.get("url", ""),
            source="Indeed (via Apify)"
        )
    
    except Exception as e:
        print(f"Error converting job item: {e}")
        return None