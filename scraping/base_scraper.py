# Общие классы и интерфейсы
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By


class BaseScraper:
    @staticmethod
    def get_by_type(selector_type):
        if selector_type == "css":
            return By.CSS_SELECTOR
        elif selector_type == "xpath":
            return By.XPATH
        else:
            raise ValueError(f"Unsupported selector type: {selector_type}")

    def extract_field(self, driver_or_elem, field):
        field_type = field.get('type')
        value = field['value']
        attribute = field['attribute']
        multiple = field.get("multiple", False)

        try:
            by = self.get_by_type(field_type)
            if multiple:
                elements = driver_or_elem.find_elements(by, value)
                if attribute is None:
                    return [elem.text.strip() for elem in elements if elem.text]
                else:
                    return [elem.get_attribute(attribute).strip() for elem in elements if elem.get_attribute(attribute)]
            else:
                # Один элемент
                element = driver_or_elem.find_element(by, value)
                if attribute is None:
                    return element.text.strip() if element.text else None
                else:
                    return element.get_attribute(attribute).strip() if element.get_attribute(attribute) else None

        except NoSuchElementException:
            return None
        except Exception as e:
            print(f'Error extracting value for selector {field}: {e}')
            return None
