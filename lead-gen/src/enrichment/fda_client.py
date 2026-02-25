"""FDA 503B outsourcing facility cross-reference.

Data source: FDA list of registered outsourcing facilities
URL: https://www.fda.gov/drugs/human-drug-compounding/registered-outsourcing-facilities
"""

import csv
import logging
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

from src.config import Settings
from src.utils.retry import retry

logger = logging.getLogger(__name__)

FDA_503B_URL = "https://www.fda.gov/drugs/human-drug-compounding/registered-outsourcing-facilities"


class FDA503BClient:
    """Cross-references pharmacies against FDA 503B registered outsourcing facilities.

    The 503B list is small (~93 facilities) and changes infrequently.
    We fetch and cache it locally, refreshing weekly.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._facilities: Optional[list[dict]] = None
        self._cache_file = settings.data_dir / "reference" / "fda_503b_facilities.csv"

    @property
    def facilities(self) -> list[dict]:
        """Get cached 503B facility list, fetching if needed."""
        if self._facilities is None:
            if self._cache_file.exists():
                self._facilities = self._load_cache()
            else:
                self._facilities = self.refresh_cache()
        return self._facilities

    @retry(max_retries=2, base_delay=2.0, exceptions=(requests.RequestException,))
    def refresh_cache(self) -> list[dict]:
        """Fetch the current 503B facility list from FDA and cache locally."""
        logger.info("Fetching FDA 503B facility list from %s", FDA_503B_URL)

        response = requests.get(FDA_503B_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table")

        facilities = []
        if table:
            rows = table.find_all("tr")[1:]  # Skip header
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 3:
                    facility = {
                        "name": cells[0].get_text(strip=True),
                        "address": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                        "state": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                        "registration_date": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                    }
                    facilities.append(facility)

        # Cache to file
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        if facilities:
            with open(self._cache_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["name", "address", "state", "registration_date"])
                writer.writeheader()
                writer.writerows(facilities)

        logger.info("Cached %d 503B facilities", len(facilities))
        self._facilities = facilities
        return facilities

    def _load_cache(self) -> list[dict]:
        """Load 503B facility list from local cache file."""
        with open(self._cache_file, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def is_503b_facility(self, business_name: str, state: str = "") -> bool:
        """Check if a pharmacy is a registered 503B outsourcing facility.

        Uses fuzzy name matching (case-insensitive, contains check).
        """
        name_lower = business_name.lower().strip()
        state_upper = state.upper().strip()

        for facility in self.facilities:
            facility_name = facility.get("name", "").lower()
            facility_state = facility.get("state", "").upper()

            # Exact or substring match on name
            if name_lower in facility_name or facility_name in name_lower:
                # If state provided, verify it matches
                if state_upper and facility_state and state_upper != facility_state:
                    continue
                return True

        return False
