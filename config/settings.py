import os


def _get_positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        return default

    return value if value > 0 else default


MONGO_URI = os.getenv("MONGO_URI")
MAX_PAGES = _get_positive_int_env("MAX_PAGES", 2)
COMPANY_SCRAPE_CONCURRENCY = _get_positive_int_env("COMPANY_SCRAPE_CONCURRENCY", 3)
