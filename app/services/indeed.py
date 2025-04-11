from apify_client import ApifyClient
from typing import List, Optional
import asyncio
from app.models.schemas import JobSearchRequest, JobListing
from app.config import APIFY_API_TOKEN

# Add country name to code mapping
COUNTRY_TO_CODE = {
    "united states": "US",
    "united kingdom": "GB",
    "pakistan": "PK",
    "india": "IN",
    "canada": "CA",
    "australia": "AU",
    # Add more mappings as needed
}

async def fetch_jobs(request: JobSearchRequest) -> List[JobListing]:
    """
    Fetch job listings from Indeed using Apify API
    """
    loop = asyncio.get_event_loop()
    jobs = await loop.run_in_executor(None, lambda: _fetch_from_apify(request))
    return jobs

def _fetch_from_apify(request: JobSearchRequest) -> List[JobListing]:
    """
    Helper function to fetch job listings from Apify
    """
    jobs = []
    
    try:
        client = ApifyClient(APIFY_API_TOKEN)
        
        # Extract location components and convert country to code
        location_parts = request.location.split(',')
        country_name = location_parts[-1].strip().lower() if len(location_parts) > 1 else location_parts[0].strip().lower()
        city = location_parts[0].strip() if len(location_parts) > 1 else ""
        
        # Get country code, default to US if not found
        country_code = COUNTRY_TO_CODE.get(country_name, "US")
        
        run_input = {
            "position": request.position,
            "country": country_code,  # Use the country code
            "location": city if city else country_name,
            "maxItems": 5,
            "parseCompanyDetails": False,
            "saveOnlyUniqueItems": True,
            "followApplyRedirects": False,
        }
        
        print(f"Searching with parameters: {run_input}")  # Debug print
        
        run = client.actor("hMvNSpz3JnHgl5jkh").call(run_input=run_input)
        
        dataset_id = run["defaultDatasetId"]
        items = list(client.dataset(dataset_id).iterate_items())
        
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
        
        
        # print few jobs for debugging purposes
        print("--------Indeed job----------")
        print(f"Job Title: {item.get('positionName', 'Not specified')}")
        print(f"Company: {item.get('company', 'Not specified')}")
        print(f"Location: {item.get('location', 'Not specified')}")
        print(f"Experience: {request.experience}")
        print(f"Salary: {item.get('salary', request.salary or 'Not specified')}")
        print(f"Apply Link: {item.get('url', '')}")
        print("-" * 50)

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
