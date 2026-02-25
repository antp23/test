"""Pennsylvania Board of Pharmacy scraper.

Data source: PA Licensing System (PALS)
URL: https://www.pals.pa.gov/
Method: Web search / bulk download if available
"""

import csv
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

PA_SEARCH_URL = "https://www.pals.pa.gov/api/Search/SearchForPersonOrFacility"


class PennsylvaniaScraper(BaseScraper):
    """Scraper for Pennsylvania Board of Pharmacy via PALS system."""

    @property
    def state_code(self) -> str:
        return "PA"

    @property
    def state_name(self) -> str:
        return "Pennsylvania"

    @property
    def source_url(self) -> str:
        return PA_SEARCH_URL

    def fetch(self, output_dir: Path) -> Path:
        """Fetch PA pharmacy data via PALS API."""
        dest = output_dir / "PA_raw.csv"

        try:
            # PALS has a search API that accepts POST requests
            payload = {
                "Board": "Pharmacy",
                "LicenseType": "Pharmacy Permit",
                "State": "PA",
                "PageSize": 5000,
                "PageNumber": 1,
            }

            records = []
            page = 1
            while True:
                payload["PageNumber"] = page
                response = self.session.post(
                    self.source_url,
                    json=payload,
                    timeout=60,
                )

                if response.status_code != 200:
                    # Fallback to HTML scraping
                    logger.info("PALS API returned %d, trying HTML fallback", response.status_code)
                    return self._fetch_html_fallback(output_dir)

                data = response.json()
                results = data.get("Results", data.get("results", []))
                if not results:
                    break

                for item in results:
                    records.append({
                        "name": item.get("Name", item.get("BusinessName", "")),
                        "license_number": item.get("LicenseNumber", ""),
                        "license_type": item.get("LicenseType", ""),
                        "address": item.get("Address", ""),
                        "city": item.get("City", ""),
                        "zip": item.get("Zip", ""),
                        "phone": item.get("Phone", ""),
                        "status": item.get("Status", ""),
                        "expiration_date": item.get("ExpirationDate", ""),
                    })

                page += 1
                if len(results) < 5000:
                    break

            with open(dest, "w", newline="", encoding="utf-8") as f:
                if records:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)

        except Exception as e:
            logger.error("PA scraper failed: %s", e)
            dest.touch()

        return dest

    def _fetch_html_fallback(self, output_dir: Path) -> Path:
        """Fallback HTML scraping if API is not available."""
        dest = output_dir / "PA_raw.csv"
        dest.touch()
        logger.warning("PA HTML fallback not yet implemented - returning empty file")
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
                            state="PA",
                            zip_code=row.get("zip", ""),
                            phone=row.get("phone", ""),
                            license_status=row.get("status", "Active"),
                            expiration_date=row.get("expiration_date", ""),
                            source="PA_PALS",
                        ))
        except Exception as e:
            logger.error("Failed to parse PA data: %s", e)
        return records
