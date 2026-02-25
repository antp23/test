"""Product demand tracker.

Aggregates product requests from Notion prospect notes and activity logs
to identify the most-requested products for proactive sourcing.

Key output: "Progesterone USP requested 47 times across 23 unique prospects"
"""

import logging
import re
from collections import Counter, defaultdict
from typing import Optional

from src.config import Settings

logger = logging.getLogger(__name__)

# Common pharmaceutical product patterns to look for in notes
PRODUCT_PATTERNS = [
    # APIs (Active Pharmaceutical Ingredients)
    r"\b(progesterone)\b",
    r"\b(estradiol)\b",
    r"\b(testosterone)\b",
    r"\b(levothyroxine)\b",
    r"\b(liothyronine)\b",
    r"\b(hydrocortisone)\b",
    r"\b(dexamethasone)\b",
    r"\b(ketamine)\b",
    r"\b(gabapentin)\b",
    r"\b(baclofen)\b",
    r"\b(omeprazole)\b",
    r"\b(ondansetron)\b",
    r"\b(lidocaine)\b",
    r"\b(bupivacaine)\b",
    r"\b(methylprednisolone)\b",
    r"\b(triamcinolone)\b",
    r"\b(nystatin)\b",
    r"\b(fluconazole)\b",
    r"\b(metformin)\b",
    r"\b(sildenafil)\b",
    r"\b(tadalafil)\b",
    r"\b(oxytocin)\b",
    r"\b(misoprostol)\b",
    r"\b(methotrexate)\b",
    r"\b(fluorouracil)\b",
    # NDC pattern
    r"\b(\d{4,5}-\d{3,4}-\d{1,2})\b",
]


class DemandTracker:
    """Tracks and ranks product demand from prospect interactions."""

    def __init__(self, settings: Settings | None = None):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self._product_counts: Counter = Counter()
        self._product_prospects: defaultdict[str, set] = defaultdict(set)
        self._compiled_patterns = [re.compile(p, re.IGNORECASE) for p in PRODUCT_PATTERNS]

    def scan_prospect_notes(self, prospects: list[dict]) -> dict:
        """Scan prospect records for product mentions.

        Args:
            prospects: List of prospect dicts with 'notes' and 'business_name' fields.

        Returns:
            Dict with scan statistics.
        """
        total_mentions = 0
        for prospect in prospects:
            notes = prospect.get("notes", "")
            name = prospect.get("business_name", "unknown")

            if not notes:
                continue

            # Scan for product mentions
            for pattern in self._compiled_patterns:
                matches = pattern.findall(notes)
                for match in matches:
                    product = match.lower().strip()
                    self._product_counts[product] += 1
                    self._product_prospects[product].add(name)
                    total_mentions += 1

        logger.info(
            "Scanned %d prospects, found %d product mentions across %d unique products",
            len(prospects), total_mentions, len(self._product_counts),
        )

        return {
            "prospects_scanned": len(prospects),
            "total_mentions": total_mentions,
            "unique_products": len(self._product_counts),
        }

    def add_manual_request(self, product_name: str, prospect_name: str):
        """Add a manual product request (from Slack escalation, etc.)."""
        product = product_name.lower().strip()
        self._product_counts[product] += 1
        self._product_prospects[product].add(prospect_name)

    def get_demand_rankings(
        self,
        limit: int = 20,
        min_requests: int = 1,
        available_products: list[str] | None = None,
    ) -> list[dict]:
        """Get ranked list of most-requested products.

        Args:
            limit: Maximum number of products to return.
            min_requests: Minimum request count to include.
            available_products: List of products currently in Safeway catalog.

        Returns:
            List of dicts sorted by request count, descending.
        """
        available_set = set()
        if available_products:
            available_set = {p.lower().strip() for p in available_products}

        rankings = []
        for product, count in self._product_counts.most_common():
            if count < min_requests:
                continue

            rankings.append({
                "product_name": product.title(),
                "request_count": count,
                "unique_prospects": len(self._product_prospects[product]),
                "is_available": product in available_set,
                "sourcing_opportunity": not (product in available_set) and count >= 3,
            })

            if len(rankings) >= limit:
                break

        return rankings

    def get_sourcing_opportunities(self, available_products: list[str]) -> list[dict]:
        """Get products with high demand that Safeway doesn't currently carry.

        These are the highest-priority sourcing targets.
        """
        rankings = self.get_demand_rankings(
            limit=50,
            min_requests=3,
            available_products=available_products,
        )
        return [r for r in rankings if r["sourcing_opportunity"]]

    def reset(self):
        """Clear accumulated demand data."""
        self._product_counts.clear()
        self._product_prospects.clear()
