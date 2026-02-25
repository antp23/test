"""PCAB/ACHC accreditation cross-reference.

Data sources:
- PCAB (Pharmacy Compounding Accreditation Board) - part of ACHC
- ACHC (Accreditation Commission for Health Care)
URL: https://achc.org/find-organizations/

Both are small lists (~68 pharmacies total for ACHC pharmacy accreditation).
We cache locally and refresh weekly.
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

ACHC_SEARCH_URL = "https://achc.org/find-organizations/"


class AccreditationClient:
    """Cross-references pharmacies against PCAB and ACHC accreditation lists."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._pcab_list: Optional[list[dict]] = None
        self._achc_list: Optional[list[dict]] = None
        self._pcab_cache = settings.data_dir / "reference" / "pcab_pharmacies.csv"
        self._achc_cache = settings.data_dir / "reference" / "achc_pharmacies.csv"

    @property
    def pcab_pharmacies(self) -> list[dict]:
        if self._pcab_list is None:
            if self._pcab_cache.exists():
                self._pcab_list = self._load_csv(self._pcab_cache)
            else:
                self._pcab_list = self._fetch_achc_pharmacies("PCAB", self._pcab_cache)
        return self._pcab_list

    @property
    def achc_pharmacies(self) -> list[dict]:
        if self._achc_list is None:
            if self._achc_cache.exists():
                self._achc_list = self._load_csv(self._achc_cache)
            else:
                self._achc_list = self._fetch_achc_pharmacies("ACHC", self._achc_cache)
        return self._achc_list

    @retry(max_retries=2, base_delay=2.0, exceptions=(requests.RequestException,))
    def _fetch_achc_pharmacies(self, accreditation_type: str, cache_path: Path) -> list[dict]:
        """Fetch accredited pharmacy list from ACHC website."""
        logger.info("Fetching %s pharmacy list from ACHC", accreditation_type)

        try:
            response = requests.get(ACHC_SEARCH_URL, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            pharmacies = []

            # Parse the ACHC directory listing
            listings = soup.find_all("div", class_="organization") or soup.find_all("tr")
            for listing in listings:
                name_elem = listing.find("h3") or listing.find("td")
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    address_elem = listing.find("p", class_="address") or listing.find_next("td")
                    address = address_elem.get_text(strip=True) if address_elem else ""

                    pharmacies.append({
                        "name": name,
                        "address": address,
                        "type": accreditation_type,
                    })

            # Cache
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            if pharmacies:
                with open(cache_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["name", "address", "type"])
                    writer.writeheader()
                    writer.writerows(pharmacies)

            logger.info("Cached %d %s pharmacies", len(pharmacies), accreditation_type)
            return pharmacies

        except Exception as e:
            logger.warning("Failed to fetch %s list: %s", accreditation_type, e)
            return []

    def _load_csv(self, path: Path) -> list[dict]:
        with open(path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def is_pcab_accredited(self, business_name: str) -> bool:
        """Check if pharmacy has PCAB accreditation."""
        return self._name_match(business_name, self.pcab_pharmacies)

    def is_achc_accredited(self, business_name: str) -> bool:
        """Check if pharmacy has ACHC accreditation."""
        return self._name_match(business_name, self.achc_pharmacies)

    @staticmethod
    def _name_match(name: str, pharmacy_list: list[dict]) -> bool:
        name_lower = name.lower().strip()
        for pharmacy in pharmacy_list:
            p_name = pharmacy.get("name", "").lower()
            if name_lower in p_name or p_name in name_lower:
                return True
        return False
