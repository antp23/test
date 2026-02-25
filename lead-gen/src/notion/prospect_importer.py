"""Notion prospect bulk importer with deduplication.

Handles:
- Deduplication check by phone number and business name
- Property mapping from enriched records to Notion schema
- Batch import with progress tracking
- Round-robin rep assignment
"""

import logging
from typing import Any

from src.config import Settings
from src.notion.client import NotionClient

logger = logging.getLogger(__name__)


# Notion property type builders
def _title(text: str) -> dict:
    return {"title": [{"text": {"content": text or ""}}]}


def _rich_text(text: str) -> dict:
    return {"rich_text": [{"text": {"content": text or ""}}]}


def _number(val) -> dict:
    try:
        return {"number": float(val)} if val else {"number": None}
    except (ValueError, TypeError):
        return {"number": None}


def _select(name: str) -> dict:
    return {"select": {"name": name}} if name else {"select": None}


def _checkbox(val) -> dict:
    if isinstance(val, str):
        val = val.lower() in ("true", "1", "yes")
    return {"checkbox": bool(val)}


def _url(url: str) -> dict:
    return {"url": url} if url else {"url": None}


def _phone(phone: str) -> dict:
    return {"phone_number": phone} if phone else {"phone_number": None}


def _email(email: str) -> dict:
    return {"email": email} if email else {"email": None}


def _date(date_str: str) -> dict:
    if date_str:
        return {"date": {"start": date_str}}
    return {"date": None}


class ProspectImporter:
    """Imports scored pharmacy prospects into the Notion Prospects database."""

    def __init__(self, settings: Settings | None = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self.notion = NotionClient(self.settings)
        self.db_id = self.settings.notion_prospects_db_id
        self._rep_index = 0

    def check_duplicates(self, records: list[dict]) -> tuple[list[dict], list[dict]]:
        """Check records against existing Notion database for duplicates.

        Returns (new_records, duplicate_records).
        """
        if not self.db_id:
            logger.warning("NOTION_PROSPECTS_DB_ID not configured, skipping dedup")
            return records, []

        new_records = []
        duplicates = []

        for record in records:
            phone = record.get("phone", "")
            name = record.get("business_name", "")
            is_dup = False

            try:
                # Check by phone first (most reliable)
                if phone:
                    existing = self.notion.search_by_phone(self.db_id, phone)
                    if existing:
                        is_dup = True

                # Check by name if phone didn't match
                if not is_dup and name:
                    existing = self.notion.search_by_name(self.db_id, name)
                    if existing:
                        is_dup = True
            except Exception as e:
                logger.debug("Dedup check failed for %s: %s", name, e)

            if is_dup:
                record["dedup_status"] = "duplicate"
                duplicates.append(record)
            else:
                record["dedup_status"] = "new"
                new_records.append(record)

        logger.info(
            "Dedup check: %d new, %d duplicates out of %d total",
            len(new_records), len(duplicates), len(records),
        )
        return new_records, duplicates

    def import_batch(self, records: list[dict]) -> list[dict]:
        """Import a batch of records into Notion.

        Returns list of successfully imported records (with notion_page_id set).
        """
        if not self.db_id:
            logger.error("NOTION_PROSPECTS_DB_ID not configured")
            return []

        imported = []
        for i, record in enumerate(records, 1):
            try:
                # Assign rep
                record["assigned_rep"] = self._assign_rep()

                # Map to Notion properties
                properties = self._map_to_notion(record)

                # Create page
                page = self.notion.create_page(self.db_id, properties)
                record["notion_page_id"] = page["id"]
                imported.append(record)

                if i % 25 == 0:
                    logger.info("Imported %d/%d records", i, len(records))

            except Exception as e:
                logger.error(
                    "Failed to import %s: %s",
                    record.get("business_name", "unknown"),
                    e,
                )

        logger.info("Successfully imported %d/%d records", len(imported), len(records))
        return imported

    def _map_to_notion(self, record: dict) -> dict[str, Any]:
        """Map an enriched record dict to Notion database properties."""
        return {
            "Business Name": _title(record.get("business_name", "")),
            "License Number": _rich_text(record.get("license_number", "")),
            "License Type": _select(record.get("license_type", "")),
            "Address": _rich_text(record.get("address", "")),
            "City": _rich_text(record.get("city", "")),
            "State": _select(record.get("state", "")),
            "Phone": _phone(record.get("phone", "")),
            "Segment": _select(record.get("segment", "")),
            "Lead Score": _number(record.get("score")),
            "Priority": _select(record.get("priority", "")),
            "Contact Name": _rich_text(record.get("contact_name", "")),
            "Contact Email": _email(record.get("contact_email", "")),
            "Contact Title": _rich_text(record.get("contact_title", "")),
            "Employee Count": _number(record.get("employee_count")),
            "Website": _url(record.get("website", "")),
            "Google Rating": _number(record.get("google_rating")),
            "Review Count": _number(record.get("google_review_count")),
            "503B Registered": _checkbox(record.get("is_503b_registered", False)),
            "PCAB Accredited": _checkbox(record.get("is_pcab_accredited", False)),
            "Assigned Rep": _select(record.get("assigned_rep", "")),
            "Source": _select(record.get("source", "")),
            "Scrape Date": _date(record.get("scrape_date", "")),
        }

    def _assign_rep(self) -> str:
        """Round-robin rep assignment."""
        reps = self.settings.rep_list
        if not reps:
            return self.settings.default_rep

        rep = reps[self._rep_index % len(reps)]
        self._rep_index += 1
        return rep
