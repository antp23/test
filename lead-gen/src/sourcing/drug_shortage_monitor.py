"""FDA Drug Shortage Monitor.

Monitors the FDA Drug Shortage database and cross-references against:
1. Safeway's product catalog (sales opportunity)
2. Common pharmacy purchasing lists (sourcing opportunity)

FDA Drug Shortage API: https://api.fda.gov/drug/drugsfda.json
OpenFDA Shortage endpoint: https://api.fda.gov/drug/shortages.json

Strategic note from spec: Drug shortages are the single biggest leverage point
in pharmaceutical wholesale sales. Being first to know about shortages and
first to offer alternatives is the highest-ROI automation in this system.
"""

import logging
from datetime import date, datetime
from typing import Optional

import httpx

from src.config import Settings
from src.utils.retry import retry

logger = logging.getLogger(__name__)

FDA_SHORTAGES_URL = "https://api.fda.gov/drug/drugsfda.json"

# Common products needed by compounding pharmacies (503A/503B)
COMPOUNDER_COMMON_NEEDS = [
    "progesterone",
    "estradiol",
    "testosterone",
    "thyroid",
    "levothyroxine",
    "hydrocortisone",
    "dexamethasone",
    "ketamine",
    "gabapentin",
    "baclofen",
    "omeprazole",
    "famotidine",
    "ondansetron",
    "methotrexate",
    "fluorouracil",
    "lidocaine",
    "bupivacaine",
    "methylprednisolone",
    "triamcinolone",
    "nystatin",
]


class DrugShortageMonitor:
    """Monitors FDA drug shortages and generates actionable alerts."""

    def __init__(self, settings: Settings | None = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self._catalog: list[str] = []

    def set_catalog(self, products: list[str]):
        """Set Safeway's current product catalog for cross-reference."""
        self._catalog = [p.lower().strip() for p in products]

    @retry(max_retries=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    def fetch_shortages(self, limit: int = 100) -> list[dict]:
        """Fetch current drug shortages from FDA API.

        Returns list of shortage records with standardized fields.
        """
        params = {
            "limit": limit,
        }

        if self.settings.fda_api_key:
            params["api_key"] = self.settings.fda_api_key

        try:
            response = httpx.get(FDA_SHORTAGES_URL, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            shortages = []
            for item in results:
                shortage = self._parse_shortage(item)
                if shortage:
                    shortages.append(shortage)

            logger.info("Fetched %d drug shortage records from FDA", len(shortages))
            return shortages

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.info("No shortage data available from FDA API")
                return []
            raise

    def _parse_shortage(self, item: dict) -> Optional[dict]:
        """Parse an FDA API result into a standardized shortage record."""
        products = item.get("products", [{}])
        product = products[0] if products else {}

        drug_name = (
            product.get("brand_name", "")
            or item.get("application_number", "")
        )
        generic = product.get("active_ingredients", [{}])
        generic_name = generic[0].get("name", "") if generic else ""

        if not drug_name and not generic_name:
            return None

        return {
            "drug_name": generic_name or drug_name,
            "brand_name": drug_name,
            "generic_name": generic_name,
            "dosage_form": product.get("dosage_form", ""),
            "route": product.get("route", ""),
            "status": "Current",
            "ndc": "",
            "first_detected": date.today().isoformat(),
            "last_updated": date.today().isoformat(),
            "matches_catalog": False,
            "matches_compounder_needs": False,
        }

    def check_shortages(self) -> list[dict]:
        """Fetch shortages and cross-reference against catalog and compounder needs.

        Returns enriched shortage records with match flags.
        """
        shortages = self.fetch_shortages()

        for shortage in shortages:
            name_lower = shortage.get("generic_name", "").lower()
            drug_lower = shortage.get("drug_name", "").lower()

            # Cross-reference against Safeway catalog
            for product in self._catalog:
                if product in name_lower or product in drug_lower:
                    shortage["matches_catalog"] = True
                    break

            # Cross-reference against common compounder needs
            for ingredient in COMPOUNDER_COMMON_NEEDS:
                if ingredient in name_lower or ingredient in drug_lower:
                    shortage["matches_compounder_needs"] = True
                    break

        # Sort: catalog matches first, then compounder matches, then others
        shortages.sort(
            key=lambda s: (
                not s.get("matches_catalog"),
                not s.get("matches_compounder_needs"),
                s.get("drug_name", ""),
            )
        )

        catalog_count = sum(1 for s in shortages if s.get("matches_catalog"))
        compounder_count = sum(1 for s in shortages if s.get("matches_compounder_needs"))
        logger.info(
            "Shortage analysis: %d total, %d catalog matches, %d compounder matches",
            len(shortages), catalog_count, compounder_count,
        )

        return shortages
