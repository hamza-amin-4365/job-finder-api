import httpx
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import quote_plus

# Import your configuration and models
from app.config import SCRAPERAPI_API_KEY
try:
    from app.models.schemas import JobSearchRequest, JobListing
except ModuleNotFoundError:
    # Allow running the script directly for testing
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from app.models.schemas import JobSearchRequest, JobListing


# Constants
SCRAPERAPI_URL = "http://api.scraperapi.com"
# *** IMPORTANT: Glassdoor URL structure needs verification ***
# This is a GUESS based on common patterns for glassdoor.com (adjust if needed)
GLASSDOOR_SEARCH_URL_TEMPLATE = "https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}&locT=N&locId={location_query}&fromAge=-1&minSalary=0&includeNoSalaryJobs=true&radius=100"

# Define standard headers (ScraperAPI might override some, but good practice)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

async def fetch_glassdoor_jobs(request: JobSearchRequest, max_jobs: int = 10) -> List[JobListing]:
    """
    Fetches job listings from Glassdoor.com via ScraperAPI.

    Args:
        request: JobSearchRequest containing position, location, etc.
        max_jobs: The maximum number of job listings to return.

    Returns:
        A list of JobListing objects.

    Requires a valid SCRAPERAPI_API_KEY in config.
    NOTE: Glassdoor selectors are highly volatile and likely need frequent updates.
          The URL structure also needs verification.
    """
    print(f"--- Starting Glassdoor scrape via ScraperAPI for: Position='{request.position}', Location='{request.location}' ---")
    scraped_jobs: List[JobListing] = []

    if not SCRAPERAPI_API_KEY:
        print("Error: SCRAPERAPI_API_KEY is not set in config/environment variables.")
        return []

    # --- Prepare Search Terms ---
    # Basic URL encoding for keywords
    query = quote_plus(request.position.strip())
    # Location might need specific formatting or IDs for Glassdoor (this is a simple guess)
    location_query = quote_plus(request.location.strip() if request.location else "")
    print(f"(Using query: '{query}', location_query: '{location_query}')")

    # Limit to 1-2 pages approx (Glassdoor shows up to 30 jobs/page)
    max_pages = 2 # Adjust as needed
    jobs_found_count = 0

    async with httpx.AsyncClient(headers=HEADERS, timeout=45.0, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            if jobs_found_count >= max_jobs:
                print(f"Reached max_jobs limit ({max_jobs}). Stopping pagination.")
                break

            print(f"\n--- Requesting Glassdoor Page {page} via ScraperAPI ---")
            try:
                # *** Construct the target Glassdoor URL (NEEDS VERIFICATION/ADJUSTMENT) ***
                # Adding `&p={page}` is a common pattern, but verify with Glassdoor's actual URL
                target_url = GLASSDOOR_SEARCH_URL_TEMPLATE.format(query=query, location_query=location_query) + f"&p={page}"
                print(f"Target Glassdoor URL: {target_url}")

                # Construct ScraperAPI request URL
                scraper_api_request_url = f"{SCRAPERAPI_URL}?api_key={SCRAPERAPI_API_KEY}&url={quote_plus(target_url)}"
                # Optional: Add parameters for JS rendering or premium proxies if needed
                # scraper_api_request_url += "&render=true" # Example if JS rendering is needed

                response = await client.get(scraper_api_request_url)

                print(f"ScraperAPI response status: {response.status_code}")
                response.raise_for_status() # Check for HTTP errors

                soup = BeautifulSoup(response.text, 'lxml') # Use lxml

                # *** SELECTORS NEED VERIFICATION - These are based on the user's script & common patterns ***
                # Main job listing card selector
                all_jobs_on_page = soup.select('li[data-test="jobListing"], article[data-test="jobListing"]') # Common tags
                print(f"Found {len(all_jobs_on_page)} potential job cards on page {page}.")

                if not all_jobs_on_page:
                    print("No job listings found on this page (selectors might be wrong or page empty).")
                    # Consider breaking if a page is empty, maybe after the first page
                    if page > 1:
                       break
                    else:
                       continue


                for job_element in all_jobs_on_page:
                    if jobs_found_count >= max_jobs:
                        break

                    try:
                        # --- Extract data using selectors (NEEDS VERIFICATION) ---
                        # Title often in a link within specific divs/headings
                        title_element = job_element.select_one('a[data-test="job-link"]') or \
                                        job_element.select_one('div[id^="job-title"]') # IDs often start with job-title

                        # Company often in a div near the title
                        company_element = job_element.select_one('div[data-test="employer-name"]') or \
                                          job_element.select_one('div[class*="employer"] span') # Look for employer class

                        # Location often in a div/span with class containing 'location'
                        location_element = job_element.select_one('div[data-test="location"]') or \
                                           job_element.select_one('div[class*="location"]')


                        job_title = title_element.text.strip() if title_element else "N/A"
                        apply_link_relative = title_element['href'].strip() if title_element and title_element.has_attr('href') else None
                        company = company_element.text.strip() if company_element else "N/A"
                        location = location_element.text.strip() if location_element else "N/A"

                        if not apply_link_relative:
                             print("  Skipping card - missing apply link.")
                             continue

                        # Make link absolute (Glassdoor links are usually relative)
                        apply_link = f"https://www.glassdoor.com{apply_link_relative}"

                        print(f"  Extracted: Title='{job_title}', Company='{company}', Location='{location}'")

                        # Create JobListing object
                        job_listing = JobListing(
                            job_title=job_title,
                            company=company,
                            # Experience/Salary/JobNature usually require visiting the detail page
                            # or might sometimes be in snippets on the search page (need specific selectors)
                            experience="Not specified",
                            jobNature=None,
                            location=location,
                            salary=None,
                            apply_link=apply_link,
                            source="Glassdoor"
                        )
                        scraped_jobs.append(job_listing)
                        jobs_found_count += 1
                        print(f"  ++ Added Job Listing ({jobs_found_count}/{max_jobs}) ++")

                    except Exception as e:
                        print(f"  Error parsing a Glassdoor job card: {e}")
                        # *** DEBUG: Uncomment to see card HTML if parsing fails ***
                        # print(job_element.prettify())

            except httpx.RequestError as exc:
                print(f"An error occurred while requesting via ScraperAPI {exc.request.url!r}: {exc}")
                break # Stop if connection fails
            except httpx.HTTPStatusError as exc:
                print(f"ScraperAPI Error response {exc.response.status_code} while requesting {exc.request.url!r}. Check API key and target URL.")
                # Optionally log response body for debugging API errors
                # print(f"Response body: {exc.response.text[:500]}")
                break # Stop if API returns error
            except Exception as e:
                print(f"An unexpected error occurred during Glassdoor scraping: {e}")
                break # Stop on other errors

    print(f"--- Finished Glassdoor scrape. Found {len(scraped_jobs)} jobs. ---")
    return scraped_jobs