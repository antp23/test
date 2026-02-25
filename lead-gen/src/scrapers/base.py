"""Abstract base class for state board of pharmacy scrapers."""

import csv
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import requests

from src.config import Settings
from src.utils.phone import normalize_phone

logger = logging.getLogger(__name__)


@dataclass
class PharmacyRecord:
    """Standardized pharmacy record produced by all scrapers."""
    business_name: str
    license_number: str
    license_type: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    phone: str = ""
    license_status: str = "Active"
    expiration_date: str = ""
    scrape_date: str = field(default_factory=lambda: date.today().isoformat())
    source: str = ""

    def to_dict(self) -> dict:
        return {
            "business_name": self.business_name,
            "license_number": self.license_number,
            "license_type": self.license_type,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "phone": normalize_phone(self.phone) or self.phone,
            "license_status": self.license_status,
            "expiration_date": self.expiration_date,
            "scrape_date": self.scrape_date,
            "source": self.source,
        }


class BaseScraper(ABC):
    """Abstract base class for all state board scrapers.

    Subclasses must implement:
        - state_code: 2-letter state abbreviation
        - state_name: Full state name
        - source_url: Primary data source URL
        - fetch(): Download raw data and return path to file
        - parse(path): Parse raw file into PharmacyRecord list
    """

    def __init__(self, settings: Optional[Settings] = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self._session: Optional[requests.Session] = None

    @property
    @abstractmethod
    def state_code(self) -> str:
        """2-letter state code (e.g., 'FL')."""
        ...

    @property
    @abstractmethod
    def state_name(self) -> str:
        """Full state name (e.g., 'Florida')."""
        ...

    @property
    @abstractmethod
    def source_url(self) -> str:
        """Primary URL for data source."""
        ...

    @abstractmethod
    def fetch(self, output_dir: Path) -> Path:
        """Download raw data from the state board.

        Returns the path to the downloaded raw file.
        """
        ...

    @abstractmethod
    def parse(self, raw_path: Path) -> list[PharmacyRecord]:
        """Parse downloaded raw data into standardized PharmacyRecord objects.

        Should filter to Active licenses only.
        """
        ...

    def run(self, output_dir: Optional[Path] = None) -> list[dict]:
        """Execute the full scraper flow: fetch → parse → return dicts.

        Returns a list of record dicts ready for CSV output.
        """
        out_dir = output_dir or self.settings.data_dir / "raw"
        out_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Starting scrape for %s (%s)", self.state_name, self.state_code)
        raw_path = self.fetch(out_dir)
        logger.info("Raw data saved to %s", raw_path)

        records = self.parse(raw_path)
        active = [r for r in records if r.license_status.lower() == "active"]
        logger.info(
            "%s: %d total records, %d active",
            self.state_code, len(records), len(active),
        )

        return [r.to_dict() for r in active]

    @property
    def session(self) -> requests.Session:
        """Lazy-initialized requests session with configured headers."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": self.settings.scraper_user_agent,
            })
        return self._session

    def download_file(self, url: str, dest: Path) -> Path:
        """Download a file from URL to destination path."""
        logger.info("Downloading %s → %s", url, dest)
        response = self.session.get(url, timeout=60, stream=True)
        response.raise_for_status()

        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info("Downloaded %d bytes to %s", dest.stat().st_size, dest)
        return dest

    @staticmethod
    def write_csv(records: list[PharmacyRecord], path: Path):
        """Write pharmacy records to CSV."""
        if not records:
            return
        fieldnames = list(records[0].to_dict().keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in records:
                writer.writerow(r.to_dict())
