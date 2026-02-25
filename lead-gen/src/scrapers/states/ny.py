"""New York Board of Pharmacy scraper.

Data source: NYSED Office of the Professions verification search
URL: https://eservices.nysed.gov/professions/verification-search
Method: Selenium (no bulk download available)

NOTE: NY does not provide bulk downloads. This scraper uses Selenium to
drive the verification search interface and paginate through results.
Consider filing a FOIL request for bulk data as an alternative.
"""

import csv
import logging
import time
from pathlib import Path

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

NY_SEARCH_URL = "https://eservices.nysed.gov/professions/verification-search"


class NewYorkScraper(BaseScraper):
    """Scraper for New York Board of Pharmacy via NYSED search.

    Uses Selenium to automate the search form since NY does not provide
    bulk data downloads. This is the most complex Tier 1 scraper.
    """

    @property
    def state_code(self) -> str:
        return "NY"

    @property
    def state_name(self) -> str:
        return "New York"

    @property
    def source_url(self) -> str:
        return NY_SEARCH_URL

    def fetch(self, output_dir: Path) -> Path:
        """Fetch NY pharmacy data using Selenium browser automation."""
        dest = output_dir / "NY_raw.csv"

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.support.ui import WebDriverWait, Select

            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 30)

            try:
                driver.get(self.source_url)
                time.sleep(2)

                # Select Pharmacy profession
                profession_select = wait.until(
                    EC.presence_of_element_located((By.ID, "professionId"))
                )
                Select(profession_select).select_by_visible_text("Pharmacy")
                time.sleep(1)

                # Search for all pharmacy establishments
                search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_btn.click()
                time.sleep(3)

                # Extract results from all pages
                records = []
                page = 1
                while True:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 4:
                            records.append({
                                "name": cells[0].text.strip(),
                                "license_number": cells[1].text.strip(),
                                "status": cells[2].text.strip(),
                                "address": cells[3].text.strip() if len(cells) > 3 else "",
                            })

                    # Try next page
                    try:
                        next_btn = driver.find_element(By.CSS_SELECTOR, "a.next-page, .pagination .next a")
                        if "disabled" in next_btn.get_attribute("class"):
                            break
                        next_btn.click()
                        page += 1
                        time.sleep(self.settings.scraper_request_delay)
                    except Exception:
                        break

                logger.info("Fetched %d records across %d pages from NY", len(records), page)

                # Write raw data to CSV
                with open(dest, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["name", "license_number", "status", "address"])
                    writer.writeheader()
                    writer.writerows(records)

            finally:
                driver.quit()

        except ImportError:
            logger.error("Selenium not installed. Install with: pip install selenium")
            # Create empty file as fallback
            dest.touch()
        except Exception as e:
            logger.error("NY Selenium scraper failed: %s", e)
            dest.touch()

        return dest

    def parse(self, raw_path: Path) -> list[PharmacyRecord]:
        records = []
        try:
            with open(raw_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("name", "").strip()
                    lic = row.get("license_number", "").strip()
                    if not name or not lic:
                        continue

                    # Parse address into components
                    address_parts = row.get("address", "").split(",")
                    city = address_parts[-2].strip() if len(address_parts) >= 2 else ""
                    street = address_parts[0].strip() if address_parts else ""

                    records.append(PharmacyRecord(
                        business_name=name,
                        license_number=lic,
                        license_type="Pharmacy",
                        address=street,
                        city=city,
                        state="NY",
                        phone="",
                        license_status=row.get("status", "Active"),
                        source="NY_NYSED",
                    ))
        except Exception as e:
            logger.error("Failed to parse NY data: %s", e)

        logger.info("Parsed %d pharmacy records from NY data", len(records))
        return records
