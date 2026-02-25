"""Arizona Board of Pharmacy scraper.

Data source: AZ Board of Pharmacy license verification
URL: https://pharmacy.az.gov/
Method: Web search / data export
"""

import csv
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

AZ_SEARCH_URL = "https://pharmacy.az.gov/licensee-search"


class ArizonaScraper(BaseScraper):
    """Scraper for Arizona Board of Pharmacy."""

    @property
    def state_code(self) -> str:
        return "AZ"

    @property
    def state_name(self) -> str:
        return "Arizona"

    @property
    def source_url(self) -> str:
        return AZ_SEARCH_URL

    def fetch(self, output_dir: Path) -> Path:
        dest = output_dir / "AZ_raw.csv"

        try:
            # AZ Board of Pharmacy has a license search that may expose an API
            params = {
                "type": "pharmacy",
                "status": "active",
            }

            records = []
            response = self.session.get(self.source_url, params=params, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", class_="views-table") or soup.find("table")

            if table:
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        records.append({
                            "name": cells[0].get_text(strip=True),
                            "license_number": cells[1].get_text(strip=True),
                            "license_type": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                            "address": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                            "city": cells[4].get_text(strip=True) if len(cells) > 4 else "",
                            "zip": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                            "status": cells[6].get_text(strip=True) if len(cells) > 6 else "Active",
                        })

            with open(dest, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["name", "license_number", "license_type", "address", "city", "zip", "status"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

        except Exception as e:
            logger.error("AZ scraper failed: %s", e)
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
                            license_type=row.get("license_type", "Pharmacy"),
                            address=row.get("address", ""),
                            city=row.get("city", ""),
                            state="AZ",
                            zip_code=row.get("zip", ""),
                            license_status=row.get("status", "Active"),
                            source="AZ_BOP",
                        ))
        except Exception as e:
            logger.error("Failed to parse AZ data: %s", e)
        return records
