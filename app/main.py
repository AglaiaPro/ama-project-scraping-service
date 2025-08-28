from bson import ObjectId
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from services.scraping_service import ScrapingService
from services.handle_refresh_company import HandleRefreshCompany
from app.exceptions import SectorNotFound, ScrapingTemplateNotFound, CompanyNotFound

app = FastAPI()


class LinkRequest(BaseModel):
    link: str


class RefreshCompanyRequest(BaseModel):
    link: str
    id: str


# endpoint firstcustomscraping для взаимодействия с custom scraping
@app.post('/firstcustomscraping')
async def custom_scraping(request: LinkRequest, background_tasks: BackgroundTasks):
    try:
        scraping_service = ScrapingService()
        background_tasks.add_task(scraping_service.run, request.link)
        return {
            "message": "Scraping started"
        }
    except SectorNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ScrapingTemplateNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unexpected error: {e}')


# endpoint refreshcompany для взаимодействия с update-checker bot
@app.post('/refreshcompany')
async def update_checker_bot(request: RefreshCompanyRequest):
    try:
        handle_refresh_company = HandleRefreshCompany()
        return handle_refresh_company.run(company_url=request.link, company_id=ObjectId(request.id))
    except CompanyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SectorNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ScrapingTemplateNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unexpected error: {e}')
