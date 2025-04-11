# Job Finder API Documentation

![Job Finder API](https://img.shields.io/badge/Job%20Finder-API-blue)

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [API Endpoints](#api-endpoints)
4. [Job Matching Algorithm](#job-matching-algorithm)
5. [Setup and Configuration](#setup-and-configuration)
6. [Example Usage](#example-usage)
7. [Troubleshooting](#troubleshooting)

## Introduction

Job Finder API is an intelligent job aggregation service that fetches job listings from multiple sources (LinkedIn, Indeed, Glassdoor) and uses AI to filter the most relevant opportunities based on your skills and preferences.

The API is built with FastAPI and leverages Google's Gemini AI to provide intelligent job matching capabilities. It's designed to help job seekers find the most relevant job opportunities without having to manually search through multiple job boards.

### Key Features

- **Multi-source Job Aggregation**: Collects job listings from LinkedIn, Indeed, and Glassdoor
- **AI-Powered Relevance Filtering**: Uses Google's Gemini AI to match jobs to your profile
- **Customizable Search**: Filter by position, experience, salary, job type, location, and skills
- **RESTful API**: Simple and consistent API endpoints with FastAPI
- **Fallback Mechanisms**: Keyword-based matching when AI filtering is unavailable

### Demo

[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/8EXp9Vge4_Q)    

*Click the logo above to watch the demo video*

## System Architecture

The Job Finder API follows a modular architecture that separates concerns and makes the system easy to maintain and extend.

### Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Client Request │────▶│  FastAPI Server │────▶│  Job Scrapers   │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └────────┬────────┘
                                 │                       │
                                 │                       │
                                 │                       ▼
                        ┌────────▼────────┐     ┌─────────────────┐
                        │                 │     │                 │
                        │  Job Filtering  │◀────│  Job Sources    │
                        │  (Gemini AI)    │     │  (LinkedIn,     │
                        │                 │     │   Indeed,       │
                        └────────┬────────┘     │   Glassdoor)    │
                                 │              │                 │
                                 │              └─────────────────┘
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │  API Response   │
                        │  (Filtered Jobs)│
                        │                 │
                        └─────────────────┘
```

### Component Overview

1. **FastAPI Server**: Handles HTTP requests and responses
2. **Job Scrapers**: Modules for fetching job listings from different sources
3. **Gemini AI Integration**: Filters jobs based on relevance to user profile
4. **Fallback Mechanism**: Keyword-based matching when AI is unavailable

## API Endpoints

The Job Finder API provides the following endpoints:

### GET /

**Description**: Welcome message to confirm the API is running.

**Response**:
```json
{
  "message": "Welcome to the Job Finder API"
}
```

### POST /search-jobs

**Description**: Search for jobs based on your criteria and get AI-filtered relevant results.

**Request Body**:
```json
{
  "position": "Frontend Developer",
  "experience": "2 years",
  "salary": "150000",
  "jobNature": "onsite",
  "location": "Lahore, Pakistan",
  "skills": "ReactJS, HTML, CSS"
}
```

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| position | string | Yes | Job title or position you're looking for |
| experience | string | Yes | Years of experience |
| salary | string | No | Expected salary |
| jobNature | string | No | Job type (onsite, remote, hybrid) |
| location | string | No | Job location |
| skills | string | Yes | Comma-separated list of skills |

**Response**:
```json
{
  "relevant_jobs": [
    {
      "job_title": "Senior Frontend Developer",
      "company": "Tech Solutions Inc.",
      "experience": "2 years",
      "jobNature": "onsite",
      "location": "Lahore, Pakistan",
      "salary": "150000",
      "apply_link": "https://example.com/apply",
      "source": "LinkedIn"
    },
    {
      "job_title": "Frontend Engineer",
      "company": "Digital Innovations",
      "experience": "2 years",
      "jobNature": "remote",
      "location": "Lahore, Pakistan",
      "salary": "140000",
      "apply_link": "https://example.com/apply2",
      "source": "Indeed"
    }
  ]
}
```

## Job Matching Algorithm

The Job Finder API uses a sophisticated job matching algorithm powered by Google's Gemini AI to find the most relevant job listings based on your profile and preferences.

### Algorithm Flow

1. **Data Collection**: Jobs are collected from multiple sources (LinkedIn, Indeed, Glassdoor)
2. **AI Filtering**: Gemini AI analyzes job listings against your profile
3. **Relevance Ranking**: Jobs are ranked based on relevance to your skills and preferences
4. **Fallback Mechanism**: If AI filtering fails, a keyword-based matching algorithm is used

### AI Matching Process

The AI matching process involves the following steps:

1. **Profile Analysis**: Your profile (position, experience, skills, preferences) is analyzed
2. **Job Analysis**: Each job listing is analyzed for relevance to your profile
3. **Matching**: The AI matches your profile with job listings based on:
   - Position title match
   - Skills match
   - Experience level match
   - Location preference
   - Job nature preference (remote, onsite, hybrid)
   - Salary expectations

### Fallback Mechanism

If the AI filtering fails for any reason, the system falls back to a keyword-based matching algorithm:

1. **Keyword Extraction**: Keywords are extracted from your position and skills
2. **Scoring**: Each job is scored based on the presence of these keywords
3. **Location Bonus**: Jobs matching your preferred location get a bonus score
4. **Ranking**: Jobs are ranked by score and the top results are returned

### Example AI Prompt

```
[SYSTEM PROMPT]
You are a job matching expert. Analyze this candidate profile and job listings.
Return ONLY a JSON array of relevant job numbers like [1,3,5].

[CANDIDATE PROFILE]
{
  "position": "Frontend Developer",
  "experience": "2 years",
  "skills": "ReactJS, HTML, CSS",
  "preferences": {
    "job_nature": "onsite",
    "location": "Lahore, Pakistan",
    "salary": "150000"
  }
}

[JOB LISTINGS]
[
  {
    "job_number": 1,
    "title": "Senior Frontend Developer",
    "company": "Tech Solutions Inc.",
    "experience": "2 years",
    "location": "Lahore, Pakistan",
    "job_nature": "onsite"
  },
  {
    "job_number": 2,
    "title": "Backend Developer",
    "company": "Digital Innovations",
    "experience": "3 years",
    "location": "Karachi, Pakistan",
    "job_nature": "remote"
  }
]

[RULES]
1. Match position titles and skills
2. Consider experience level
3. Location match gets priority
4. Include partial matches
5. Select at least 3 jobs
6. Return ONLY the array
```

## Setup and Configuration

### Prerequisites

- Python 3.8+
- API keys for external services:
  - Apify API Token (for Indeed scraping)
  - Google Gemini API Key (for AI job matching)
  - ScraperAPI Key (for Glassdoor scraping)

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/job-finder-api.git
cd job-finder-api
```

2. **Create a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the root directory with the following variables:

```
APIFY_API_TOKEN=your_apify_token
GEMINI_API_KEY=your_gemini_api_key
SCRAPERAPI_API_KEY=your_scraperapi_key
```

5. **Run the server**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation UI

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

### Example 1: Search for Frontend Developer Jobs

**Request**:
```bash
curl -X 'POST' \
  'http://localhost:8000/search-jobs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "position": "Frontend Developer",
  "experience": "2 years",
  "salary": "150000",
  "jobNature": "onsite",
  "location": "Lahore, Pakistan",
  "skills": "ReactJS, HTML, CSS"
}'
```

**Response**:
```json
{
  "relevant_jobs": [
    {
      "job_title": "Senior Frontend Developer",
      "company": "Tech Solutions Inc.",
      "experience": "2 years",
      "jobNature": "onsite",
      "location": "Lahore, Pakistan",
      "salary": "150000",
      "apply_link": "https://example.com/apply",
      "source": "LinkedIn"
    },
    {
      "job_title": "Frontend Engineer",
      "company": "Digital Innovations",
      "experience": "2 years",
      "jobNature": "remote",
      "location": "Lahore, Pakistan",
      "salary": "140000",
      "apply_link": "https://example.com/apply2",
      "source": "Indeed"
    }
  ]
}
```

### Example 2: Search for Data Scientist Jobs

**Request**:
```bash
curl -X 'POST' \
  'http://localhost:8000/search-jobs' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "position": "Data Scientist",
  "experience": "3 years",
  "salary": "180000",
  "jobNature": "remote",
  "location": "United States",
  "skills": "Python, Machine Learning, SQL, TensorFlow"
}'
```

**Response**:
```json
{
  "relevant_jobs": [
    {
      "job_title": "Senior Data Scientist",
      "company": "AI Solutions",
      "experience": "3 years",
      "jobNature": "remote",
      "location": "New York, United States",
      "salary": "180000",
      "apply_link": "https://example.com/apply3",
      "source": "LinkedIn"
    },
    {
      "job_title": "Machine Learning Engineer",
      "company": "Tech Innovations",
      "experience": "3 years",
      "jobNature": "remote",
      "location": "San Francisco, United States",
      "salary": "190000",
      "apply_link": "https://example.com/apply4",
      "source": "Indeed"
    }
  ]
}
```

## Troubleshooting

### Common Issues and Solutions

#### API Keys Not Working

**Issue**: The API returns errors related to external services.

**Solution**: 
- Verify that your API keys are correctly set in the `.env` file
- Check if your API keys have expired or reached usage limits
- Ensure you have the correct permissions for the API keys

#### No Jobs Found

**Issue**: The API returns an empty list of jobs.

**Solution**:
- Try broadening your search criteria (e.g., less specific position, more general location)
- Check if the job sources are accessible (LinkedIn, Indeed, Glassdoor)
- Verify that your search parameters are valid

#### AI Filtering Not Working

**Issue**: The API falls back to keyword matching instead of using AI filtering.

**Solution**:
- Check your Gemini API key and quota
- Ensure that the job listings contain enough information for AI filtering
- Try providing more detailed information in your search request

### Logging

The API logs detailed information about the job search process. Check the console output for:

- Job scraping status from each source
- Number of jobs found before filtering
- AI filtering process and results
- Fallback to keyword matching (if applicable)

### Getting Help

If you encounter issues not covered in this documentation, please:

1. Check the GitHub repository for known issues
2. Open a new issue with detailed information about your problem
3. Contact the maintainers for support

---

## Conclusion

The Job Finder API provides a powerful way to aggregate and filter job listings from multiple sources. By leveraging AI technology, it helps job seekers find the most relevant opportunities based on their skills and preferences.

This documentation covers the basic usage and configuration of the API. For more advanced usage or customization, refer to the source code and comments.

---

*Documentation created for Job Finder API - Version 1.0.0*
