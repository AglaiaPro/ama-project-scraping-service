from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.scraping_service import ScrapingService
from services.handle_refresh_company import HandleRefreshCompany
from app.exceptions import SectorNotFound, ScrapingTemplateNotFound, CompanyNotFound

app = FastAPI()
scraping_service = ScrapingService()
handle_refresh_company = HandleRefreshCompany()


class LinkRequest(BaseModel):
    link: str


class RefreshCompanyRequest(BaseModel):
    link: str


# endpoint firstcustomscraping для взаимодействия с custom scraping
@app.post('/firstcustomscraping')
async def custom_scraping(request: LinkRequest):
    try:
        return scraping_service.run(request.link)
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
        return handle_refresh_company.run(request.link)
    except CompanyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SectorNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ScrapingTemplateNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Unexpected error: {e}')




#testLink = 'https://www.finder.fi/search?what=IT+ja+ohjelmistot&sort=TURNOVER_desc'
