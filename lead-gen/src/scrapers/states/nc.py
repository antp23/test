"""North Carolina Board of Pharmacy scraper.

Data source: NC Board of Pharmacy permit search
URL: https://www.ncbop.org/
Method: Web search with BeautifulSoup
"""

import csv
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

NC_SEARCH_URL = "https://www.ncbop.org/pharmacysearch.asp"


class NorthCarolinaScraper(BaseScraper):
    """Scraper for North Carolina Board of Pharmacy."""

    @property
    def state_code(self) -> str:
        return "NC"

    @property
    def state_name(self) -> str:
        return "North Carolina"

    @property
    def source_url(self) -> str:
        return NC_SEARCH_URL

    def fetch(self, output_dir: Path) -> Path:
        dest = output_dir / "NC_raw.csv"

        try:
            payload = {
                "SearchType": "Pharmacy",
                "Status": "Active",
                "State": "NC",
            }

            records = []
            response = self.session.post(self.source_url, data=payload, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table", {"id": "results"}) or soup.find("table", class_="data")

            if table:
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 3:
                        records.append({
                            "name": cells[0].get_text(strip=True),
                            "license_number": cells[1].get_text(strip=True),
                            "address": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                            "city": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                            "status": cells[4].get_text(strip=True) if len(cells) > 4 else "Active",
                            "phone": cells[5].get_text(strip=True) if len(cells) > 5 else "",
                        })

            with open(dest, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["name", "license_number", "address", "city", "status", "phone"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)

        except Exception as e:
            logger.error("NC scraper failed: %s", e)
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
                            address=row.get("address", ""),
                            city=row.get("city", ""),
                            state="NC",
                            phone=row.get("phone", ""),
                            license_status=row.get("status", "Active"),
                            source="NC_BOP",
                        ))
        except Exception as e:
            logger.error("Failed to parse NC data: %s", e)
        return records
