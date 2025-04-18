import google.generativeai as genai
import asyncio
import json
from typing import List
from app.models.schemas import JobSearchRequest, JobListing
from app.config import GEMINI_API_KEY

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


async def filter_relevant_jobs(
    request: JobSearchRequest, jobs: List[JobListing]
) -> List[JobListing]:
    print("\n=== STARTING LLM FILTERING ===")
    print(f"Received {len(jobs)} jobs to filter")

    if not jobs:
        print("No jobs to filter!")
        return []

    if len(jobs) <= 3:
        print(f"Few jobs ({len(jobs)}), skipping LLM filter")
        return jobs

    try:
        # Build candidate profile
        candidate_profile = {
            "position": request.position,
            "experience": request.experience,
            "skills": request.skills,
            "preferences": {
                "job_nature": request.jobNature or "Any",
                "location": request.location or "Any",
                "salary": request.salary or "Flexible",
            },
        }

        # Prepare job listings
        job_listings = []
        for idx, job in enumerate(jobs, 1):
            job_listings.append(
                {
                    "job_number": idx,
                    "title": job.job_title,
                    "company": job.company,
                    "experience": job.experience,
                    "location": job.location,
                    "job_nature": job.jobNature or "Not specified",
                }
            )

        # Create prompt
        prompt = f"""
        [SYSTEM PROMPT]
        You are a job matching expert. Analyze this candidate profile and job listings.
        Return ONLY a JSON array of relevant job numbers like [1,3,5].

        [CANDIDATE PROFILE]
        {json.dumps(candidate_profile, indent=2)}

        [JOB LISTINGS]
        {json.dumps(job_listings, indent=2)}

        [RULES]
        1. Match position titles and skills
        2. Consider experience level
        3. Location match gets priority
        4. Include partial matches
        5. Select at least 3 jobs
        6. Return ONLY the array
        """

        print("\n=== PROMPT SENT TO LLM ===")
        print(prompt[:2000] + "\n... [truncated]")  # Print first 2000 chars

        # Get LLM response
        print("\nAwaiting LLM response...")
        response = await asyncio.to_thread(model.generate_content, prompt)
        response_text = response.text.strip()

        print("\n=== RAW LLM RESPONSE ===")
        print(response_text)

        # Parse response
        try:
            print("\nAttempting to parse response...")
            start_idx = response_text.find("[")
            end_idx = response_text.find("]")

            if start_idx == -1 or end_idx == -1:
                print("❗ No array found in response")
                raise ValueError("No array found")

            json_text = response_text[start_idx : end_idx + 1]
            print(f"Extracted JSON text: {json_text}")

            relevant_indices = json.loads(json_text)
            print(f"Parsed indices: {relevant_indices}")

            if not isinstance(relevant_indices, list):
                print("❗ Response is not a list")
                raise ValueError("Invalid response format")

            # Convert to 0-based indices
            valid_indices = []
            for idx in relevant_indices:
                if isinstance(idx, int) and 1 <= idx <= len(jobs):
                    valid_indices.append(idx - 1)
                else:
                    print(f"⚠️ Invalid index skipped: {idx}")

            print(f"Valid indices after conversion: {valid_indices}")

            if not valid_indices:
                print("⚠️ No valid indices, using fallback")
                return keyword_matching_fallback(request, jobs)

            filtered_jobs = [jobs[i] for i in valid_indices if i < len(jobs)]
            print(f"\n=== FINAL FILTERED JOBS ({len(filtered_jobs)}) ===")
            for job in filtered_jobs:
                print(f"- {job.job_title} | {job.company}")

            return filtered_jobs

        except Exception as parse_error:
            print(f"\n❗ PARSING ERROR: {str(parse_error)}")
            print("Attempting keyword fallback...")
            return keyword_matching_fallback(request, jobs)

    except Exception as e:
        print(f"\n❗ GENERAL ERROR: {str(e)}")
        return keyword_matching_fallback(request, jobs)


def keyword_matching_fallback(
    request: JobSearchRequest, jobs: List[JobListing]
) -> List[JobListing]:
    print("\n=== KEYWORD FALLBACK ACTIVATED ===")
    if not jobs:
        return []
    
    # Extract keywords
    keywords = set()
    keywords.update(request.position.lower().split())
    keywords.update(kw.strip().lower() for kw in request.skills.split(','))
    
    # Score jobs
    scored = []
    for job in jobs:
        job_text = f"{job.job_title} {job.company} {job.location}".lower()
        score = sum(1 for kw in keywords if kw in job_text)
        
        # Bonus for location match
        if request.location and request.location.lower() in job.location.lower():
            score += 2
            
        scored.append((score, job))
    
    # Sort and return top 50% or min 3 jobs
    scored.sort(reverse=True, key=lambda x: x[0])
    keep = max(3, len(scored) // 2)
    return [job for (score, job) in scored[:keep]]