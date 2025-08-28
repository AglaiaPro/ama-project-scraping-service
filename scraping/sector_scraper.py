# Класс для сбора компаний в секторе
import time
from scraping.base_scraper import BaseScraper


class SectorScraper(BaseScraper):
    def __init__(self, driver, template):
        self.driver = driver
        self.template = template

    def get_companies(self, start_url, max_pages):
        companies = []
        current_url = start_url
        page_count = 0

        while current_url and page_count < max_pages:
            self.driver.get(current_url)
            time.sleep(2)

            fields = self.template['fields']
            company_sel = self.template['company_selector']

            try:
                company_elements = self.driver.find_elements(
                    self.get_by_type(company_sel['type']),
                    company_sel['value']
                )

                for elem in company_elements:
                    # company name
                    name = self.extract_field(elem, fields['name'])

                    # company URL
                    url = self.extract_field(elem, fields['url'])
                    print(f'===   Name {name} and url {url}\n')
                    if name and url:
                        companies.append({
                            "name": name,
                            "url": url
                        })
            except Exception as e:
                print(f"Error parsing company: {e}")
                break

            # Переход на следующую страницу # Pagination
            current_url = self.extract_field(self.driver, fields['next_page_selector'])
            print(f'Текущая ссылка: {current_url}')
            if not current_url:
                print('The following link was not found')
                return companies
            page_count += 1

        return companies
