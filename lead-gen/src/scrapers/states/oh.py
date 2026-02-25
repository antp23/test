"""Ohio Board of Pharmacy scraper.

Data source: Ohio eLicense verification
URL: https://elicense.ohio.gov/
Method: Search API / web scraping
"""

import csv
import logging
from pathlib import Path

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

OH_SEARCH_URL = "https://elicense.ohio.gov/api/search"
OH_WEB_URL = "https://elicense.ohio.gov/"


class OhioScraper(BaseScraper):
    """Scraper for Ohio Board of Pharmacy via eLicense system."""

    @property
    def state_code(self) -> str:
        return "OH"

    @property
    def state_name(self) -> str:
        return "Ohio"

    @property
    def source_url(self) -> str:
        return OH_WEB_URL

    def fetch(self, output_dir: Path) -> Path:
        dest = output_dir / "OH_raw.csv"

        try:
            payload = {
                "Board": "Pharmacy",
                "Type": "Terminal Distributor of Dangerous Drugs",
                "Status": "Active",
                "PageSize": 5000,
                "Page": 1,
            }

            records = []
            page = 1
            while True:
                payload["Page"] = page
                response = self.session.post(OH_SEARCH_URL, json=payload, timeout=60)

                if response.status_code != 200:
                    logger.warning("OH API returned %d", response.status_code)
                    break

                data = response.json()
                results = data.get("results", data.get("Results", []))
                if not results:
                    break

                for item in results:
                    records.append({
                        "name": item.get("BusinessName", item.get("Name", "")),
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
                else:
                    f.write("")

        except Exception as e:
            logger.error("OH scraper failed: %s", e)
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
                            license_type=row.get("license_type", "Terminal Distributor"),
                            address=row.get("address", ""),
                            city=row.get("city", ""),
                            state="OH",
                            zip_code=row.get("zip", ""),
                            phone=row.get("phone", ""),
                            license_status=row.get("status", "Active"),
                            expiration_date=row.get("expiration_date", ""),
                            source="OH_BOP",
                        ))
        except Exception as e:
            logger.error("Failed to parse OH data: %s", e)
        return records
