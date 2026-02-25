"""Texas State Board of Pharmacy scraper.

Data source: Texas TSBP bulk CSV download
URL: https://www.pharmacy.texas.gov/dbsearch/downloads.asp
Format: CSV files, updated daily
Files: phydsk.csv (pharmacies), phtdsk.csv (pharmacists)
"""

import csv
import logging
from pathlib import Path

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

TX_PHARMACY_URL = "https://www.pharmacy.texas.gov/downloads/phydsk.csv"


class TexasScraper(BaseScraper):
    """Scraper for Texas State Board of Pharmacy.

    Texas provides direct CSV download of all licensed pharmacy establishments.
    This is the simplest scraper - pure download + CSV parse.
    """

    @property
    def state_code(self) -> str:
        return "TX"

    @property
    def state_name(self) -> str:
        return "Texas"

    @property
    def source_url(self) -> str:
        return TX_PHARMACY_URL

    def fetch(self, output_dir: Path) -> Path:
        """Download the TX pharmacy CSV file."""
        dest = output_dir / "TX_raw.csv"
        return self.download_file(self.source_url, dest)

    def parse(self, raw_path: Path) -> list[PharmacyRecord]:
        """Parse TX pharmacy CSV data.

        Expected CSV columns:
        Permit Number, Class, DBA Name, Address, City, State, Zip,
        Phone, Status, Expiration Date, ...
        """
        records = []
        try:
            with open(raw_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.DictReader(f)
                for row_num, row in enumerate(reader, start=2):
                    try:
                        record = self._parse_row(row)
                        if record:
                            records.append(record)
                    except Exception as e:
                        logger.debug("Skipping row %d: %s", row_num, e)

        except Exception as e:
            logger.error("Failed to parse %s: %s", raw_path, e)

        logger.info("Parsed %d pharmacy records from TX data", len(records))
        return records

    def _parse_row(self, row: dict[str, str]) -> PharmacyRecord | None:
        """Parse a single CSV row into a PharmacyRecord."""
        def get(key: str, *alternates: str) -> str:
            for k in (key, *alternates):
                val = row.get(k, "").strip()
                if val:
                    return val
            return ""

        name = get("DBA Name", "DBA_Name", "Business Name", "Name", "Pharmacy Name")
        permit = get("Permit Number", "Permit_Number", "License Number", "License", "Permit")

        if not name or not permit:
            return None

        return PharmacyRecord(
            business_name=name,
            license_number=permit,
            license_type=get("Class", "License Type", "Type", "Category"),
            address=get("Address", "Street Address", "Address1"),
            city=get("City"),
            state="TX",
            zip_code=get("Zip", "Zip Code", "ZipCode"),
            phone=get("Phone", "Phone Number", "Telephone"),
            license_status=get("Status", "License Status") or "Active",
            expiration_date=get("Expiration Date", "Exp Date", "Expiration"),
            source="TX_TSBP",
        )
