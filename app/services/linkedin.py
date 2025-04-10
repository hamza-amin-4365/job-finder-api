import httpx
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
from app.models.schemas import JobSearchRequest, JobListing
from app.config import USER_AGENT, REQUEST_TIMEOUT, SCRAPING_DELAY

# LinkedIn search URL
BASE_URL = "https://www.linkedin.com/jobs/search"

async def fetch_linkedin_jobs(request: JobSearchRequest) -> List[JobListing]:
    """
    Fetch job listings from LinkedIn based on the search criteria
    """
    jobs = []
    
    # Prepare search parameters
    params = build_search_params(request)
    
    # Fetch initial page to get total results
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True, cookies={}) as client:
        headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }
        
        try:
            first_response = await client.get(BASE_URL, headers=headers)
            first_response.raise_for_status()
            response = await client.get(BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job listings from the page
            job_cards = extract_job_cards(soup)
            
            # Process each job card
            for job_card in job_cards:
                job = parse_job_card(job_card, request)
                if job:
                    jobs.append(job)
            
            # Get total number of pages (limited to first 2 pages for this implementation)
            max_pages = min(determine_max_pages(soup), 2)
            
            # Fetch additional pages if available
            for page in range(2, max_pages + 1):
                # Respect LinkedIn's rate limiting
                await asyncio.sleep(SCRAPING_DELAY * 2)
                
                # Update page parameter
                page_params = params.copy()
                page_params["start"] = (page - 1) * 25  # LinkedIn uses 25 jobs per page
                
                page_response = await client.get(BASE_URL, params=page_params, headers=headers)
                page_response.raise_for_status()
                
                page_soup = BeautifulSoup(page_response.text, 'html.parser')
                page_job_cards = extract_job_cards(page_soup)
                
                for job_card in page_job_cards:
                    job = parse_job_card(job_card, request)
                    if job:
                        jobs.append(job)
        
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"Error fetching LinkedIn jobs: {e}")
    
    return jobs

def build_search_params(request: JobSearchRequest) -> Dict[str, Any]:
    """Build URL parameters for LinkedIn job search"""
    params = {
        "keywords": request.position,
        "f_WT": "2",  # Default to on-site jobs
        "pageSize": 25
    }
    
    # Add location if provided
    if request.location:
        params["location"] = request.location
    
    # Set job nature (remote, on-site, hybrid)
    if request.jobNature:
        if request.jobNature.lower() == "remote":
            params["f_WT"] = "1"
        elif request.jobNature.lower() == "hybrid":
            params["f_WT"] = "3"
    
    # Add experience level if possible
    if request.experience:
        exp_years = extract_years_of_experience(request.experience)
        if 0 <= exp_years < 1:
            params["f_E"] = "1"  # Internship/Entry level
        elif 1 <= exp_years < 3:
            params["f_E"] = "2"  # Associate level
        elif 3 <= exp_years < 5:
            params["f_E"] = "3"  # Mid-Senior level
        elif exp_years >= 5:
            params["f_E"] = "4"  # Director/Executive level
    
    return params

def extract_years_of_experience(experience_str: str) -> float:
    """Extract years from experience string"""
    # Try to find patterns like "2 years", "2+" etc.
    patterns = [
        r'(\d+)\s*(\+)?\s*years?',
        r'(\d+)\s*(\+)?'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, experience_str.lower())
        if match:
            years = float(match.group(1))
            return years
    
    return 0  # Default to entry level if can't determine

def extract_job_cards(soup: BeautifulSoup) -> List[Any]:
    """Extract job card elements from the page"""
    # LinkedIn typically uses ul with job cards as li elements
    job_container = soup.find('ul', class_='jobs-search__results-list')
    if job_container:
        return job_container.find_all('li')
    return []

def determine_max_pages(soup: BeautifulSoup) -> int:
    """Determine the maximum number of pages in search results"""
    # Look for pagination information
    try:
        # LinkedIn might display pagination info or total jobs count
        pagination = soup.find('ul', class_='artdeco-pagination__pages')
        if pagination:
            pages = pagination.find_all('li')
            if pages:
                return int(pages[-1].text.strip())
        
        # If pagination not found, check for job count
        job_count_element = soup.find('span', class_='results-context-header__job-count')
        if job_count_element:
            job_count = int(job_count_element.text.strip().replace(',', '').replace('+', ''))
            return min(max(1, (job_count // 25) + 1), 5)  # LinkedIn shows 25 jobs per page
        
    except (ValueError, AttributeError) as e:
        print(f"Error determining max pages: {e}")
    
    return 1  # Default to 1 page if can't determine

def parse_job_card(job_card: Any, request: JobSearchRequest) -> JobListing:
    """Parse job card element to extract job details"""
    try:
        # Extract job title
        job_title_element = job_card.find('h3', class_='base-search-card__title')
        job_title = job_title_element.text.strip() if job_title_element else "N/A"
        
        # Extract company name
        company_element = job_card.find('h4', class_='base-search-card__subtitle')
        company = company_element.text.strip() if company_element else "N/A"
        
        # Extract location
        location_element = job_card.find('span', class_='job-search-card__location')
        location = location_element.text.strip() if location_element else "N/A"
        
        # Extract job link
        link_element = job_card.find('a', class_='base-card__full-link')
        apply_link = link_element.get('href') if link_element else None
        
        # Sometimes LinkedIn provides experience level in the job card
        experience = "Not specified"
        criteria_elements = job_card.find_all('li', class_='base-search-card__metadata-item')
        for element in criteria_elements:
            text = element.text.strip().lower()
            if "experience" in text:
                experience = text
        
        # If no specific experience found, use the request's experience
        if experience == "Not specified":
            experience = request.experience
        
        # Extract salary if available (LinkedIn often doesn't display this directly in cards)
        salary = "Not specified"
        salary_element = job_card.find('span', class_='job-search-card__salary-info')
        if salary_element:
            salary = salary_element.text.strip()
        
        # Determine job nature if not specified in the card
        job_nature = request.jobNature if request.jobNature else "Not specified"
        
        # Return job listing if we have the minimum required information
        if job_title != "N/A" and company != "N/A" and apply_link:
            return JobListing(
                job_title=job_title,
                company=company,
                experience=experience,
                jobNature=job_nature,
                location=location,
                salary=salary,
                apply_link=apply_link,
                source="LinkedIn"
            )
    
    except Exception as e:
        print(f"Error parsing job card: {e}")
    
    return None