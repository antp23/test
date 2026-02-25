"""State board of pharmacy scraper registry."""

from src.scrapers.base import BaseScraper, PharmacyRecord
from src.scrapers.states.az import ArizonaScraper
from src.scrapers.states.ca import CaliforniaScraper
from src.scrapers.states.fl import FloridaScraper
from src.scrapers.states.ga import GeorgiaScraper
from src.scrapers.states.nc import NorthCarolinaScraper
from src.scrapers.states.nj import NewJerseyScraper
from src.scrapers.states.ny import NewYorkScraper
from src.scrapers.states.oh import OhioScraper
from src.scrapers.states.pa import PennsylvaniaScraper
from src.scrapers.states.tx import TexasScraper

# Registry mapping state codes to scraper classes
SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "FL": FloridaScraper,
    "TX": TexasScraper,
    "CA": CaliforniaScraper,
    "NY": NewYorkScraper,
    "NJ": NewJerseyScraper,
    "PA": PennsylvaniaScraper,
    "OH": OhioScraper,
    "GA": GeorgiaScraper,
    "NC": NorthCarolinaScraper,
    "AZ": ArizonaScraper,
}


def get_scraper(state_code: str) -> BaseScraper:
    """Get a scraper instance for the given state code.

    Raises ValueError if state code is not supported.
    """
    code = state_code.upper()
    scraper_class = SCRAPER_REGISTRY.get(code)
    if scraper_class is None:
        available = ", ".join(sorted(SCRAPER_REGISTRY.keys()))
        raise ValueError(f"No scraper available for state '{code}'. Available: {available}")
    return scraper_class()


def get_all_scrapers() -> dict[str, BaseScraper]:
    """Get scraper instances for all supported states."""
    return {code: cls() for code, cls in SCRAPER_REGISTRY.items()}


__all__ = [
    "BaseScraper",
    "PharmacyRecord",
    "get_scraper",
    "get_all_scrapers",
    "SCRAPER_REGISTRY",
]
