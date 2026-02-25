"""Florida Board of Pharmacy scraper.

Data source: FL Department of Health Data Download Portal
URL: https://data-download.mqa.flhealthsource.gov/
Format: Pipe-delimited text files, updated daily
Profession filter: Pharmacy
"""

import csv
import logging
from pathlib import Path

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

# FL DOH data download portal provides pipe-delimited files
FL_DATA_URL = "https://data-download.mqa.flhealthsource.gov/datasets/Pharmacy.txt"
FL_BACKUP_URL = "https://data-download.mqa.flhealthsource.gov/datasets/PharmacyTechnician.txt"


class FloridaScraper(BaseScraper):
    """Scraper for Florida Board of Pharmacy via DOH Data Download Portal.

    Florida provides daily-updated pipe-delimited text files with all licensed
    pharmacy records through the MQA Data Download Portal.
    """

    @property
    def state_code(self) -> str:
        return "FL"

    @property
    def state_name(self) -> str:
        return "Florida"

    @property
    def source_url(self) -> str:
        return FL_DATA_URL

    def fetch(self, output_dir: Path) -> Path:
        """Download the FL pharmacy license data file."""
        dest = output_dir / "FL_raw.txt"
        return self.download_file(self.source_url, dest)

    def parse(self, raw_path: Path) -> list[PharmacyRecord]:
        """Parse pipe-delimited FL pharmacy data.

        Expected columns (pipe-delimited):
        License Number | License Type | Status | First Name | Middle Name |
        Last Name | Suffix | Business Name | Address 1 | Address 2 | City |
        State | Zip | County | Phone | Expiration Date | ...

        Note: Exact column layout may vary. This parser handles the standard
        FL DOH pharmacy establishment export format.
        """
        records = []
        try:
            with open(raw_path, "r", encoding="utf-8", errors="replace") as f:
                # Try pipe-delimited first
                sample = f.read(2048)
                f.seek(0)

                if "|" in sample:
                    delimiter = "|"
                elif "\t" in sample:
                    delimiter = "\t"
                else:
                    delimiter = ","

                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader, None)

                if not header:
                    logger.warning("Empty file: %s", raw_path)
                    return []

                # Normalize header names for flexible column mapping
                header_lower = [h.strip().lower().replace(" ", "_") for h in header]
                col_map = {name: idx for idx, name in enumerate(header_lower)}

                for row_num, row in enumerate(reader, start=2):
                    try:
                        record = self._parse_row(row, col_map)
                        if record:
                            records.append(record)
                    except Exception as e:
                        logger.debug("Skipping row %d: %s", row_num, e)

        except Exception as e:
            logger.error("Failed to parse %s: %s", raw_path, e)

        logger.info("Parsed %d pharmacy records from FL data", len(records))
        return records

    def _parse_row(self, row: list[str], col_map: dict[str, int]) -> PharmacyRecord | None:
        """Parse a single row into a PharmacyRecord."""
        def get(name: str, *alternates: str) -> str:
            for n in (name, *alternates):
                idx = col_map.get(n)
                if idx is not None and idx < len(row):
                    return row[idx].strip()
            return ""

        business_name = get("business_name", "dba_name", "facility_name", "name")
        license_number = get("license_number", "license_no", "lic_number", "license")
        status = get("status", "license_status", "lic_status")

        if not business_name or not license_number:
            return None

        return PharmacyRecord(
            business_name=business_name,
            license_number=license_number,
            license_type=get("license_type", "type", "profession", "category"),
            address=get("address_1", "address", "street_address", "addr1"),
            city=get("city"),
            state="FL",
            zip_code=get("zip", "zip_code", "zipcode", "postal_code"),
            phone=get("phone", "phone_number", "telephone"),
            license_status=status or "Active",
            expiration_date=get("expiration_date", "exp_date", "expdate", "expires"),
            source="FL_DOH",
        )
