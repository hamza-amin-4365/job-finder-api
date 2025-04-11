# Job Finder API 🔍

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0%2B-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

## Overview

Job Finder API is an intelligent job aggregation service that fetches job listings from multiple sources (LinkedIn, Indeed, Glassdoor) and uses AI to filter the most relevant opportunities based on your skills and preferences.

## ✨ Features

- **Multi-source Job Aggregation**: Collects job listings from LinkedIn Indeed and Glassdoor
- **AI-Powered Relevance Filtering**: Uses Google's Gemini AI to match jobs to your profile
- **Customizable Search**: Filter by position, experience, salary, job type, location, and skills
- **RESTful API**: Simple and consistent API endpoints with FastAPI
- **Fallback Mechanisms**: Keyword-based matching when AI filtering is unavailable

## 🚀 Installation

### Prerequisites

- Python 3.8+
- API keys for external services (Apify, Google Gemini)

### Setup

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
```

5. **Run the server**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### GET /

Welcome message to confirm the API is running.

#### POST /search-jobs

Search for jobs based on your criteria and get AI-filtered relevant results.

**Request Body:**

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

**Response:**

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
    // More job listings...
  ]
}
```


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.