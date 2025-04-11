# Job Finder API

#### FastAPI service that aggregates job postings from well-known sources and returns them in JSON format.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload

```

## API Endpoints

- `GET /jobs` - Get all jobs
- `GET /jobs/search` - Search jobs with filters

## License

Apache License 2.0

## Test the api
```
{
  "position": "Frontend Developer",
  "experience": "2 years",
  "salary": "150000",
  "jobNature": "onsite",
  "location": "Lahore, Pakistan",
  "skills": "ReactJS< HTML, CSS"
}
```