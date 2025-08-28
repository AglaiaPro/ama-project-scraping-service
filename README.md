# Scraping Service
This microservice is responsible for scraping companies from specified website sectors 
using predefined templates stored in the database.
In addition to collecting new companies, it can also update the data of an existing company by its link.

# Features
- Scrape a list of companies from a sector page.
- Scrape detailed information about each company.
- Save results into MongoDB.
- Run scraping as a background task (via FastAPI BackgroundTasks).
- Update an existing company’s data by URL.
- Fully compatible with the custom-scraping and update-checker microservices.

# Settings
The main configuration is located in config/settings.py

MONGO_URI = "mongodb+srv://<USERNAME>:<PASSWORD>@cluster0.ykuoi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
- Replace <USERNAME> and <PASSWORD> with your MongoDB credentials.
- By default, the service is configured for MongoDB Atlas, but it can be pointed to a local MongoDB instance as well.

MAX_PAGES = 2
- Defines the maximum number of pages to crawl when scraping companies from a sector.
- This limit prevents the service from scraping all available companies (which could be in the thousands).
- Increase this value if you need to collect more companies.

# API Endpoints

## POST /firstcustomscraping 
Starts scraping for a given sector link which is obtained from the custom-scraping service

Request:
{
  "link": "https://example.com/some-sector"
}

Response:
{
  "message": "Scraping started"
}

## POST /refreshcompany
Updates company data for a given company URL which is obtained from the update-checker bot service

Request:
{
  "link": "https://example.com/company/123",
  "id": "64b8f3e4a1b2c3d4e5f6a7b8"
}

Response:
{
  "success": true,
  "message": "Company data updated for: https://example.com/company/123"
}

# MongoDB Collections

This service uses three main collections:

- companies — stores scraped company data
- business_sectors — stores sector links
- scraping_templates — stores scraping templates for sectors
You can check connectivity by pinging MongoDB on startup.

## Installation & Run

### 1. Clone the repository

git clone https://github.com/your-repo/scraping_service.git
cd scraping_service

### 2. Create a virtual environment and install packages
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
pip install -r requirements.txt

### 4. Run service
uvicorn app.main:app --reload --port 8001
Swagger docs: http://127.0.0.1:8001/docs

# Notes
Selenium runs in headless mode with randomized User-Agent, window size, and other parameters to bypass anti-bot measures.
MAX_PAGES prevents scraping too many pages at once; adjust it according to your needs.
All scraping tasks are run safely with exception handling, and errors are logged for debugging.

# Deployment
This service is containerized and runs inside Docker as part of the overall microservices system.
All dependencies are installed automatically within the Docker environment.