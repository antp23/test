"""California Board of Pharmacy scraper.

Data source: CA Department of Consumer Affairs (DCA) public data
URL: https://www.dca.ca.gov/consumers/public_info/index.shtml
Format: Tab-delimited flat files, updated monthly
"""

import csv
import logging
from pathlib import Path

from src.scrapers.base import BaseScraper, PharmacyRecord

logger = logging.getLogger(__name__)

CA_DATA_URL = "https://www.dca.ca.gov/consumers/public_info/licensee_file/pharmacy.txt"


class CaliforniaScraper(BaseScraper):
    """Scraper for California Board of Pharmacy via DCA flat file download."""

    @property
    def state_code(self) -> str:
        return "CA"

    @property
    def state_name(self) -> str:
        return "California"

    @property
    def source_url(self) -> str:
        return CA_DATA_URL

    def fetch(self, output_dir: Path) -> Path:
        dest = output_dir / "CA_raw.txt"
        return self.download_file(self.source_url, dest)

    def parse(self, raw_path: Path) -> list[PharmacyRecord]:
        records = []
        try:
            with open(raw_path, "r", encoding="utf-8", errors="replace") as f:
                sample = f.read(2048)
                f.seek(0)
                delimiter = "\t" if "\t" in sample else "|" if "|" in sample else ","

                reader = csv.reader(f, delimiter=delimiter)
                header = next(reader, None)
                if not header:
                    return []

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

        logger.info("Parsed %d pharmacy records from CA data", len(records))
        return records

    def _parse_row(self, row: list[str], col_map: dict[str, int]) -> PharmacyRecord | None:
        def get(name: str, *alts: str) -> str:
            for n in (name, *alts):
                idx = col_map.get(n)
                if idx is not None and idx < len(row):
                    return row[idx].strip()
            return ""

        name = get("business_name", "dba_name", "name", "facility_name")
        lic = get("license_number", "license_no", "license")
        if not name or not lic:
            return None

        return PharmacyRecord(
            business_name=name,
            license_number=lic,
            license_type=get("license_type", "type", "category"),
            address=get("address", "address_1", "street"),
            city=get("city"),
            state="CA",
            zip_code=get("zip", "zip_code", "zipcode"),
            phone=get("phone", "phone_number", "telephone"),
            license_status=get("status", "license_status") or "Active",
            expiration_date=get("expiration_date", "exp_date"),
            source="CA_DCA",
        )
