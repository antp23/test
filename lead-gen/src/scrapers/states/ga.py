"""Georgia Board of Pharmacy scraper.

Data source: Georgia Secretary of State license search
URL: https://sos.ga.gov/cgi-bin/plbsearch.asp
Method: Web search / data download
"""

import csv
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

GA_SEARCH_URL = "https://sos.ga.gov/cgi-bin/plbsearch.asp"


class GeorgiaScraper(BaseScraper):
    """Scraper for Georgia Board of Pharmacy."""

    @property
    def state_code(self) -> str:
        return "GA"

    @property
    def state_name(self) -> str:
        return "Georgia"

    @property
    def source_url(self) -> str:
        return GA_SEARCH_URL

    def fetch(self, output_dir: Path) -> Path:
        dest = output_dir / "GA_raw.csv"

        try:
            # GA uses a simple form POST for license searches
            payload = {
                "Board": "260",  # Board of Pharmacy
                "Category": "01",  # Pharmacy
                "LastName": "",
                "FirstName": "",
                "LicenseNumber": "",
                "City": "",
                "State": "GA",
                "Status": "Active",
            }

            records = []
            response = self.session.post(self.source_url, data=payload, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", class_="results") or soup.find("table")

            if table:
                rows = table.find_all("tr")[1:]  # Skip header
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 4:
                        records.append({
                            "name": cells[0].get_text(strip=True),
                            "license_number": cells[1].get_text(strip=True),
                            "status": cells[2].get_text(strip=True),
                            "city": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                            "expiration_date": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                        })

            with open(dest, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["name", "license_number", "status", "city", "expiration_date"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

        except Exception as e:
            logger.error("GA scraper failed: %s", e)
            dest.touch()

        return dest

    def parse(self, raw_path: Path) -> list[PharmacyRecord]:
        records = []
        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    name = row.get("name", "").strip()
                    lic = row.get("license_number", "").strip()
                    if name and lic:
                        records.append(PharmacyRecord(
                            business_name=name,
                            license_number=lic,
                            license_type="Pharmacy",
                            city=row.get("city", ""),
                            state="GA",
                            license_status=row.get("status", "Active"),
                            expiration_date=row.get("expiration_date", ""),
                            source="GA_SOS",
                        ))
        except Exception as e:
            logger.error("Failed to parse GA data: %s", e)
        return records
