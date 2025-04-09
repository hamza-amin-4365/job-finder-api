import google.generativeai as genai
from typing import List
from app.models.schemas import JobSearchRequest, JobListing
from app.config import GEMINI_API_KEY, RELEVANCE_THRESHOLD

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

async def filter_relevant_jobs(request: JobSearchRequest, jobs: List[JobListing]) -> List[JobListing]:
    """
    Filter jobs by relevance using Gemini LLM technology
    """
    if not jobs:
        return []

    relevant_jobs = []
    
    # Create a prompt template for job matching
    base_prompt = f"""
    As a job matching expert, analyze the job requirements and candidate profile below.
    Rate the match on a scale of 0-100 and provide a brief explanation.
    
    Candidate Profile:
    - Position seeking: {request.position}
    - Experience: {request.experience}
    - Required skills: {request.skills}
    - Preferred job nature: {request.jobNature if request.jobNature else 'Any'}
    - Preferred location: {request.location if request.location else 'Any'}
    - Expected salary: {request.salary if request.salary else 'Not specified'}

    Job Details:
    """

    for job in jobs:
        try:
            # Add specific job details to the prompt
            job_prompt = base_prompt + f"""
            - Title: {job.job_title}
            - Company: {job.company}
            - Required experience: {job.experience}
            - Job nature: {job.jobNature if job.jobNature else 'Not specified'}
            - Location: {job.location}
            - Salary: {job.salary if job.salary else 'Not specified'}

            Provide the match score (0-100) and a one-line explanation in the following format:
            Score: [number]
            Explanation: [brief explanation]
            """

            # Get response from Gemini
            response = model.generate_content(job_prompt)
            response_text = response.text

            # Extract score from response
            score = extract_score(response_text)
            
            if score >= RELEVANCE_THRESHOLD:
                relevant_jobs.append(job)

        except Exception as e:
            print(f"Error processing job {job.job_title}: {str(e)}")
            continue

    return relevant_jobs

def extract_score(response_text: str) -> float:
    """
    Extract the numerical score from the LLM response
    """
    try:
        # Look for "Score: " followed by a number
        score_line = [line for line in response_text.split('\n') if 'Score:' in line][0]
        score_str = score_line.split('Score:')[1].strip()
        score = float(score_str.split()[0])  # Get first number after "Score:"
        return min(100, max(0, score))  # Ensure score is between 0 and 100
    except Exception:
        return 0.0
