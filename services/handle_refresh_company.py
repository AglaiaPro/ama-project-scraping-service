from bson import ObjectId
from database.mongo_connection import get_collections
from app.exceptions import SectorNotFound, ScrapingTemplateNotFound, CompanyNotFound
from scraping.company_scraper import CompanyScraper


class HandleRefreshCompany:
    def __init__(self):
        self.companies_collection, self.sectors_collection, self.templates_collection = get_collections()

    def _find_sector_id(self, company_url: str, company_id: ObjectId) -> tuple:
        company = self.companies_collection.find_one({
            "url": company_url,
            "_id": company_id
        })
        if not company:
            raise CompanyNotFound(f"No company found with URL: {company_url} and ID: {company_id}")
        sector = self.sectors_collection.find_one({"_id": ObjectId(company["sector_id"])})
        if not sector:
            raise SectorNotFound(f"Can't determine sector for: {company_url}")

        return str(sector["_id"]), company

    def _get_company_template(self, sector_id: str) -> dict:
        template = self.templates_collection.find_one({"website_id": sector_id})
        if not template or "company_template" not in template:
            raise ScrapingTemplateNotFound(f"No template for sector {sector_id}")
        return template["company_template"]

    def run(self, company_url: str, company_id: ObjectId) -> dict:
        try:
            sector_id, company = self._find_sector_id(company_url, company_id)
            company_template = self._get_company_template(sector_id)

            company_scraper = CompanyScraper(company_template, sector_id)
            company_data = company_scraper.scrape_company(company_url)  # одиночный скрапинг
            if not company_data:
                raise CompanyNotFound(f"Failed to scrape company data for {company_url}")

            if company_data:
                self.companies_collection.update_one(
                    {"_id": company["_id"]},
                    {"$set": company_data},
                    upsert=False
                )

                print('The data has been updated successfully')

            return {
                "success": True,
                "message": f"Company data updated for: {company_url}"
            }
        except Exception as e:
            print(f"Scraping failed for {company_url}: {e}")
            raise
