from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import JobSearchRequest, JobSearchResponse
from app.services import linkedin, indeed, glassdoor
from app.services.llm_service import filter_relevant_jobs

app = FastAPI(
    title="Job Finder API",
    description="API that fetches and filters relevant job listings from multiple sources",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #NOTE: adjust in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Job Finder API"}

@app.post("/search-jobs", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest):
    try:
        # Fetch jobs from different sources
        linkedin_jobs = await linkedin.fetch_linkedin_jobs(request)
        #NOTE: The apify api takes too much time to respond that's why it has been commented out but the code is functional and properly working.
        # indeed_jobs = await indeed.fetch_jobs(request)
        glassdoor_jobs = await glassdoor.fetch_glassdoor_jobs(request)

        # Combine all job listings
        all_jobs = linkedin_jobs + glassdoor_jobs  # add indeed_jobs here
        print(all_jobs)
        print(f"Total jobs from all sources before filtering: {len(all_jobs)}")

        # Filter jobs by relevance using LLM
        relevant_jobs = await filter_relevant_jobs(request, all_jobs)
        
        return JobSearchResponse(relevant_jobs=relevant_jobs)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)