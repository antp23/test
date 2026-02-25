"""Notion Vendor Pipeline database operations.

Manages the vendor/manufacturer evaluation and onboarding pipeline in Notion.
Schema matches the Vendor Pipeline Database spec from section 2.5.
"""

import logging
from typing import Any

from src.config import Settings
from src.notion.client import NotionClient

logger = logging.getLogger(__name__)


def _title(text: str) -> dict:
    return {"title": [{"text": {"content": text or ""}}]}


def _rich_text(text: str) -> dict:
    return {"rich_text": [{"text": {"content": text or ""}}]}


def _select(name: str) -> dict:
    return {"select": {"name": name}} if name else {"select": None}


def _number(val) -> dict:
    try:
        return {"number": float(val)} if val else {"number": None}
    except (ValueError, TypeError):
        return {"number": None}


def _email(email: str) -> dict:
    return {"email": email} if email else {"email": None}


def _phone(phone: str) -> dict:
    return {"phone_number": phone} if phone else {"phone_number": None}


class VendorPipeline:
    """Manages the Vendor Pipeline Notion database."""

    def __init__(self, settings: Settings | None = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self.notion = NotionClient(self.settings)
        self.db_id = self.settings.notion_vendors_db_id

    def create_vendor(self, vendor: dict) -> dict:
        """Create a new vendor entry in the pipeline database."""
        if not self.db_id:
            raise ValueError("NOTION_VENDORS_DB_ID not configured")

        properties = {
            "Vendor Name": _title(vendor.get("vendor_name", "")),
            "Type": _select(vendor.get("vendor_type", "")),
            "Country": _rich_text(vendor.get("country", "")),
            "Products of Interest": _rich_text(vendor.get("products_of_interest", "")),
            "Stage": _select(vendor.get("stage", "Identified")),
            "FDA Registration": _select(vendor.get("fda_registration_status", "Unknown")),
            "cGMP Status": _select(vendor.get("cgmp_status", "Unknown")),
            "Contact Name": _rich_text(vendor.get("contact_name", "")),
            "Contact Email": _email(vendor.get("contact_email", "")),
            "Contact Phone": _phone(vendor.get("contact_phone", "")),
            "Source": _select(vendor.get("source", "")),
            "Est. Product Count": _number(vendor.get("est_product_count")),
            "Est. Annual Revenue": _number(vendor.get("est_annual_revenue")),
            "Priority": _select(vendor.get("priority", "Medium")),
            "Notes": _rich_text(vendor.get("notes", "")),
        }

        page = self.notion.create_page(self.db_id, properties)
        logger.info("Created vendor: %s (page %s)", vendor.get("vendor_name"), page["id"])
        return page

    def update_stage(self, page_id: str, new_stage: str) -> dict:
        """Update a vendor's pipeline stage."""
        return self.notion.update_page(
            page_id, {"Stage": _select(new_stage)}
        )

    def get_vendors_by_stage(self, stage: str) -> list[dict]:
        """Get all vendors at a specific pipeline stage."""
        if not self.db_id:
            return []

        return self.notion.query_database(
            self.db_id,
            filter_obj={
                "property": "Stage",
                "select": {"equals": stage},
            },
        )

    def get_all_vendors(self) -> list[dict]:
        """Get all vendors in the pipeline."""
        if not self.db_id:
            return []
        return self.notion.query_database(self.db_id)
