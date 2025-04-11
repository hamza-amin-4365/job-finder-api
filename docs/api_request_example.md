## API Request Example

### Request to `/search-jobs` endpoint

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

### Response from API

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

## Job Matching Algorithm Flow

1. **Data Collection**: Jobs are collected from multiple sources (LinkedIn, Indeed, Glassdoor)
2. **AI Filtering**: Gemini AI analyzes job listings against your profile
3. **Relevance Ranking**: Jobs are ranked based on relevance to your skills and preferences
4. **Fallback Mechanism**: If AI filtering fails, a keyword-based matching algorithm is used
