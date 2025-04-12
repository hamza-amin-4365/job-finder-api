from typing import List, Optional
from app.models.schemas import JobListing, JobSearchRequest
from bs4 import BeautifulSoup
import requests
import time
import random
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import asyncio

class LinkedInScraper:
    def __init__(self):
        self.session = self._setup_session()
        self.BASE_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        self.JOBS_PER_PAGE = 25
        self.MIN_DELAY = 2
        self.MAX_DELAY = 5
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
            "Cache-Control": "no-cache",
        }

    def _setup_session(self) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        return session

    def _build_search_url(self, position: str, location: str, start: int = 0) -> str:
        params = {
            "keywords": position,
            "location": location,
            "start": start,
        }
        return f"{self.BASE_URL}?{'&'.join(f'{k}={quote(str(v))}' for k, v in params.items())}"

    def _clean_job_url(self, url: str) -> str:
        return url.split("?")[0] if "?" in url else url

    def _extract_job_data(self, job_card: BeautifulSoup, request: JobSearchRequest) -> Optional[JobListing]:
        try:
            title = job_card.find("h3", class_="base-search-card__title").text.strip()
            company = job_card.find("h4", class_="base-search-card__subtitle").text.strip()
            location = job_card.find("span", class_="job-search-card__location").text.strip()
            job_link = self._clean_job_url(
                job_card.find("a", class_="base-card__full-link")["href"]
            )
            
            return JobListing(
                job_title=title,
                company=company,
                experience=request.experience,  # Using requested experience
                jobNature=request.jobNature or "Not specified",
                location=location,
                salary=request.salary or "Not specified",
                apply_link=job_link,
                source="LinkedIn"
            )
        except Exception as e:
            print(f"Failed to extract job data: {str(e)}")
            return None

    def _fetch_job_page(self, url: str) -> BeautifulSoup:
        try:
            response = self.session.get(url, headers=self.HEADERS)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed: {str(e)}")

    def _scrape_jobs_sync(self, request: JobSearchRequest) -> List[JobListing]:
        all_jobs = []
        start = 0
        max_jobs = 10  # Default limit

        while len(all_jobs) < max_jobs:
            try:
                url = self._build_search_url(request.position, request.location or "", start)
                soup = self._fetch_job_page(url)
                job_cards = soup.find_all("div", class_="base-card")

                if not job_cards:
                    break

                for card in job_cards:
                    job_data = self._extract_job_data(card, request)
                    if job_data:
                        all_jobs.append(job_data)
                        if len(all_jobs) >= max_jobs:
                            break

                print(f"Scraped {len(all_jobs)} jobs from LinkedIn...")
                start += self.JOBS_PER_PAGE
                time.sleep(random.uniform(self.MIN_DELAY, self.MAX_DELAY))
                
            except Exception as e:
                print(f"LinkedIn scraping error: {str(e)}")
                break

        return all_jobs[:max_jobs]

async def fetch_linkedin_jobs(request: JobSearchRequest) -> List[JobListing]:
    scraper = LinkedInScraper()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, scraper._scrape_jobs_sync, request)