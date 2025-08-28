from config.settings import MAX_PAGES
from scraping.driver_manager import setup_stealth_driver
from database.mongo_connection import get_collections
from app.exceptions import SectorNotFound, ScrapingTemplateNotFound
from scraping.sector_scraper import SectorScraper
from scraping.company_scraper import CompanyScraper


class ScrapingService:
    def __init__(self):
        # Получаем коллекции из MongoDB
        self.companies_collection, self.sectors_collection, self.templates_collection = get_collections()

    def _search_link(self, link: str):
        sector = self.sectors_collection.find_one({"linkki": link})
        if not sector:
            raise SectorNotFound(f"The link {link} was not found in the database")

        sector_id = str(sector["_id"])
        return sector_id

    def _get_templates(self, sector_id: str):
        template = self.templates_collection.find_one({"website_id": sector_id})
        if not template:
            raise ScrapingTemplateNotFound(f"No scraping template found for sector_id {sector_id}")
        return template['page_companies_template'], template['company_template']

    def run(self, link: str):
        driver = None
        try:
            sector_id = self._search_link(link)
            page_companies_temp, company_template = self._get_templates(sector_id)

            driver = setup_stealth_driver()

            sector_scraper = SectorScraper(driver, page_companies_temp)
            companies = sector_scraper.get_companies(link, MAX_PAGES)
            print(f'Найдено компаний {len(companies)}')

            company_scraper = CompanyScraper(company_template, sector_id)
            results = company_scraper.scrape_companies(companies)

            if results:
                self.companies_collection.insert_many(results)
                print('Successfully saved all data in the database.')

        finally:
            if driver:
                driver.quit()
