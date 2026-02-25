"""New Jersey Board of Pharmacy scraper.

Data source: NJ Division of Consumer Affairs license verification
URL: https://newjersey.mylicense.com/verification/
Method: Web scraping (search form with results)
"""

import csv
import logging
import time
from pathlib import Path

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

NJ_SEARCH_URL = "https://newjersey.mylicense.com/verification/Search.aspx"


class NewJerseyScraper(BaseScraper):
    """Scraper for New Jersey Board of Pharmacy."""

    @property
    def state_code(self) -> str:
        return "NJ"

    @property
    def state_name(self) -> str:
        return "New Jersey"

    @property
    def source_url(self) -> str:
        return NJ_SEARCH_URL

    def fetch(self, output_dir: Path) -> Path:
        """Fetch NJ pharmacy data via web scraping."""
        dest = output_dir / "NJ_raw.csv"

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
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

                # Select Pharmacy board and search
                board_select = wait.until(
                    EC.presence_of_element_located((By.ID, "t_web_lookup__board_id"))
                )
                Select(board_select).select_by_visible_text("Board of Pharmacy")
                time.sleep(1)

                # Select license type
                type_select = driver.find_element(By.ID, "t_web_lookup__license_type_id")
                Select(type_select).select_by_visible_text("Pharmacy Permit")
                time.sleep(1)

                search_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                search_btn.click()
                time.sleep(3)

                records = []
                rows = driver.find_elements(By.CSS_SELECTOR, "table.datagrid tbody tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 3:
                        records.append({
                            "name": cells[0].text.strip(),
                            "license_number": cells[1].text.strip(),
                            "status": cells[2].text.strip(),
                            "city": cells[3].text.strip() if len(cells) > 3 else "",
                        })

                with open(dest, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["name", "license_number", "status", "city"])
                    writer.writeheader()
                    writer.writerows(records)

            finally:
                driver.quit()

        except ImportError:
            logger.error("Selenium required for NJ scraper")
            dest.touch()
        except Exception as e:
            logger.error("NJ scraper failed: %s", e)
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
                            license_type="Pharmacy Permit",
                            city=row.get("city", ""),
                            state="NJ",
                            license_status=row.get("status", "Active"),
                            source="NJ_DCA",
                        ))
        except Exception as e:
            logger.error("Failed to parse NJ data: %s", e)
        return records
