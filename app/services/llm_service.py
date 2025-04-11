import google.generativeai as genai
import asyncio
import json
from typing import List, Dict, Any
from app.models.schemas import JobSearchRequest, JobListing
from app.config import GEMINI_API_KEY, RELEVANCE_THRESHOLD

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-lite')

async def filter_relevant_jobs(request: JobSearchRequest, jobs: List[JobListing]) -> List[JobListing]:
    """
    Filter jobs by relevance using a single Gemini API call
    """
    if not jobs:
        return []
    
    # If we have 5 or fewer jobs, consider all relevant to avoid API call
    if len(jobs) <= 5:
        print("Small number of jobs found - skipping LLM filtering")
        return jobs
        
    try:
        # Create candidate profile section
        candidate_profile = f"""
        Candidate Profile:
        - Position seeking: {request.position}
        - Experience: {request.experience}
        - Required skills: {request.skills}
        - Preferred job nature: {request.jobNature if request.jobNature else 'Any'}
        - Preferred location: {request.location if request.location else 'Any'}
        - Expected salary: {request.salary if request.salary else 'Not specified'}
        """
        
        # Create job listings section
        job_details = []
        for i, job in enumerate(jobs):
            job_details.append(f"""
            Job #{i+1}:
            - Title: {job.job_title}
            - Company: {job.company}
            - Experience: {job.experience}
            - Job nature: {job.jobNature if job.jobNature else 'Not specified'}
            - Location: {job.location}
            - Salary: {job.salary if job.salary else 'Not specified'}
            """)
        
        job_listings = "\n".join(job_details)
        
        # Complete prompt
        prompt = f"""
        You are an expert job matching assistant. Here's a candidate profile and {len(jobs)} job listings.
        Your task is to identify which jobs are most relevant for this candidate.

        {candidate_profile}

        {job_listings}

        Evaluate each job's relevance to the candidate profile.
        A job is considered relevant if:
        1. The job title matches or is related to the position the candidate is seeking
        2. The experience requirements match the candidate's experience
        3. The skills required overlap with the candidate's skills
        4. The job nature and location match the candidate's preferences (if specified)

        RESPOND WITH A VALID JSON ARRAY containing only the job numbers that are relevant:
        [1, 3, 5] (example showing jobs #1, #3, and #5 are relevant)
        """
        
        # Make a single API call
        print(f"Making a single LLM call to evaluate {len(jobs)} jobs")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Extract JSON array from response
        # First clean up the response to get just the JSON part
        if '```' in response_text:
            # Extract JSON from code block
            json_text = response_text.split('```')[1]
            if json_text.startswith('json'):
                json_text = json_text[4:].strip()
        else:
            # Try to find square brackets for the array
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')
            if start_idx != -1 and end_idx != -1:
                json_text = response_text[start_idx:end_idx+1]
            else:
                json_text = response_text
        
        try:
            # Parse JSON array
            relevant_indices = json.loads(json_text)
            # Convert to 0-based indices and ensure they're in range
            relevant_indices = [idx-1 for idx in relevant_indices if isinstance(idx, int) and 1 <= idx <= len(jobs)]
            
            # Return the relevant jobs
            return [jobs[idx] for idx in relevant_indices]
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text}")
            # Fallback to keyword matching
            return keyword_matching_fallback(request, jobs)
            
    except Exception as e:
        print(f"Error in LLM filtering: {str(e)}")
        # Fallback to simple keyword matching
        return keyword_matching_fallback(request, jobs)

def keyword_matching_fallback(request: JobSearchRequest, jobs: List[JobListing]) -> List[JobListing]:
    """
    Fallback method using basic keyword matching when LLM is unavailable
    """
    print("Using keyword matching fallback")
    relevant_jobs = []
    
    # Extract keywords from request
    keywords = set()
    keywords.update(request.position.lower().split())
    keywords.update(request.skills.lower().split(','))
    keywords = {k.strip() for k in keywords if len(k.strip()) > 2}
    
    for job in jobs:
        # Create a job text combining all fields
        job_text = f"{job.job_title} {job.company} {job.experience} {job.jobNature or ''} {job.location}"
        job_text = job_text.lower()
        
        # Count matching keywords
        matches = sum(1 for keyword in keywords if keyword in job_text)
        
        # Consider relevant if at least 30% of keywords match
        if matches >= max(1, len(keywords) * 0.3):
            relevant_jobs.append(job)
    
    return relevant_jobs