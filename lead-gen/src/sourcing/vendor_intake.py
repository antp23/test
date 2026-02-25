"""Vendor intake form processing.

Handles submissions from the "Become a Supplier" web form on the Safeway
or iRemedy website. Auto-creates entries in the Vendor Pipeline Database.
"""

import logging
from datetime import datetime

from src.config import Settings
from src.notion.vendor_pipeline import VendorPipeline

logger = logging.getLogger(__name__)


class VendorIntakeProcessor:
    """Processes vendor intake form submissions."""

    def __init__(self, settings: Settings | None = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self.pipeline = VendorPipeline(self.settings)

    def process_submission(self, form_data: dict) -> dict:
        """Process a vendor intake form submission.

        Expected form fields:
            company_name, company_type, country, products,
            contact_name, contact_email, contact_phone,
            fda_registered (bool), notes

        Returns the created vendor record.
        """
        vendor = {
            "vendor_name": form_data.get("company_name", ""),
            "vendor_type": self._map_vendor_type(form_data.get("company_type", "")),
            "country": form_data.get("country", ""),
            "products_of_interest": form_data.get("products", ""),
            "stage": "Identified",
            "fda_registration_status": (
                "Registered" if form_data.get("fda_registered") else "Unknown"
            ),
            "cgmp_status": "Unknown",
            "contact_name": form_data.get("contact_name", ""),
            "contact_email": form_data.get("contact_email", ""),
            "contact_phone": form_data.get("contact_phone", ""),
            "source": "Website Intake Form",
            "priority": "Medium",
            "notes": f"Submitted via intake form on {datetime.now().strftime('%Y-%m-%d')}. "
                     f"{form_data.get('notes', '')}",
        }

        logger.info("Processing vendor intake: %s", vendor["vendor_name"])

        try:
            page = self.pipeline.create_vendor(vendor)
            vendor["notion_page_id"] = page["id"]
            vendor["status"] = "created"
        except Exception as e:
            logger.error("Failed to create vendor from intake: %s", e)
            vendor["status"] = "error"
            vendor["error"] = str(e)

        return vendor

    @staticmethod
    def _map_vendor_type(raw_type: str) -> str:
        """Map free-text company type to standardized vendor type."""
        raw = raw_type.lower()
        if "api" in raw or "ingredient" in raw or "active" in raw:
            return "API Manufacturer"
        if "finish" in raw or "dosage" in raw or "formul" in raw:
            return "Finished Dosage"
        if "repack" in raw:
            return "Repackager"
        if "distribut" in raw or "wholesal" in raw:
            return "Distributor"
        if "raw" in raw or "excipient" in raw or "chemical" in raw:
            return "Raw Material"
        return "API Manufacturer"  # Default
