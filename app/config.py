import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys and configurations
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  


RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "70.0"))  # Minimum score to consider a job relevant

# Scraping configurations
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 30  # seconds
SCRAPING_DELAY = 2  # seconds between requests

# Source URLs
LINKEDIN_JOBS_URL = "https://www.linkedin.com/jobs/search"
INDEED_JOBS_URL = "https://www.indeed.com/jobs"
GLASSDOOR_JOBS_URL = "https://www.glassdoor.com/Job/jobs.htm"