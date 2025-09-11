# Класс для детального сбора данных о компании
import hashlib
import random
import re
import time
from bs4 import BeautifulSoup

from scraping.base_scraper import BaseScraper
from scraping.driver_manager import setup_stealth_driver


class CompanyScraper(BaseScraper):
    def __init__(self, template, sector_id=None):
        self.template = template
        self.sector_id = sector_id

    def scrape_company(self, company_url):
        driver = None
        try:
            driver = setup_stealth_driver()
            driver.get(company_url)
            time.sleep(random.uniform(1, 5))

            fields = self.template.get('fields', {})
            details = self.parse_fields(driver, fields)

            details['sector_id'] = self.sector_id
            details['url'] = company_url

            html_page = driver.page_source
            details['hash'] = self.clean_html_and_hash(html_page)
            print(f'--- {company_url}')
            # print(f"[OK] {details['name']} — hash: {details['hash']}")
            return details

        except Exception as e:
            print(f"[ERROR] Failed to scrape company {company_url}: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def scrape_companies(self, companies):
        results = []
        for company in companies:
            url = company.get('url')
            if url:
                details = self.scrape_company(url)
                if details:
                    results.append(details)
        return results

    def parse_fields(self, driver, fields):
        result = {}
        for key, field in fields.items():
            if isinstance(field, dict):
                if field.get('type') == 'table':
                    result[key] = self.parse_table(driver, field)

                elif all(k in field for k in ("type", "value", "attribute")):
                    result[key] = self.extract_field(driver, field)

                else:
                    result[key] = self.parse_fields(driver, field)
            else:
                print(f"Unknown field structure for key: {key}")
                continue
        return result

    def parse_table(self, driver, field):
        subfields = field.get('fields', {})

        # сбор данных по каждому столбцу
        columns = {
            name: self.extract_field(driver, fdata)
            for name, fdata in subfields.items()
        }
        # Определим максимальное количество строк по длине самого длинного столбца
        max_len = max((len(col) for col in columns.values() if isinstance(col, list)), default=0)

        rows = []
        for i in range(max_len):
            row = {
                col_name: col_values[i] if isinstance(col_values, list) and i < len(col_values) else None
                for col_name, col_values in columns.items()
            }
            rows.append(row)
        return rows

    @staticmethod
    def clean_html_and_hash(html):
        soup = BeautifulSoup(html, 'html.parser')

        # 1. Удаляем всё, что точно не влияет на данные
        for tag in soup(['script', 'style', 'meta', 'noscript', 'link']):
            tag.decompose()

        # 2. Удаляем или очищаем потенциально нестабильные атрибуты
        for tag in soup.find_all(True):
            # Удаляем динамические/нестабильные атрибуты
            for attr in list(tag.attrs):
                if attr in ['id', 'class', 'style', 'data-reactid', 'aria-hidden', 'tabindex']:
                    del tag.attrs[attr]
                elif attr.startswith('data-'):
                    del tag.attrs[attr]

        # 3. Убираем лишние пробелы и пустые строки

        clean_text = soup.body.get_text(separator=' ', strip=True) if soup.body else soup.get_text(separator=' ', strip=True)
        clean_text = re.sub(r'\s+', ' ', clean_text)

        return hashlib.md5(clean_text.encode('utf-8')).hexdigest()
