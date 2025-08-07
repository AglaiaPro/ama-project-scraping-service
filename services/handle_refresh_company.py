from bson import ObjectId
from scraping.driver_manager import setup_stealth_driver
from database.mongo_connection import get_collections
from app.exceptions import SectorNotFound, ScrapingTemplateNotFound, CompanyNotFound
from scraping.company_scraper import CompanyScraper


class HandleRefreshCompany:
    def __init__(self):
        self.companies_collection, self.sectors_collection, self.templates_collection = get_collections()

    def _find_sector_id(self, company_url: str) -> str:
        company = self.companies_collection.find_one({"url": company_url})
        if not company:
            raise CompanyNotFound(f"No company found with URL: {company_url}")
        sector = self.sectors_collection.find_one({"_id": ObjectId(company["sector_id"])})
        if not sector:
            raise SectorNotFound(f"Can't determine sector for: {company_url}")

        return str(sector["_id"])

    def _get_company_template(self, sector_id: str) -> dict:
        template = self.templates_collection.find_one({"website_id": sector_id})
        if not template or "company_template" not in template:
            raise ScrapingTemplateNotFound(f"No template for sector {sector_id}")
        return template["company_template"]

    def run(self, company_url: str) -> dict:
        driver = None
        try:
            sector_id = self._find_sector_id(company_url)
            company_template = self._get_company_template(sector_id)

            driver = setup_stealth_driver()

            company_scraper = CompanyScraper(company_template, sector_id)
            company_data = company_scraper.scrape_company(company_url)  # одиночный скрапинг

            if company_data:
                self.companies_collection.replace_one(
                    {"website": company_data["website"]}, company_data, upsert=True
                )
                print('The data has been updated successfully')

            return {
                "success": True,
                "message": f"Company data updated for: {company_url}"
            }

        finally:
            if driver:
                driver.quit()
