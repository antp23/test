"""Enrichment pipeline orchestrator.

Takes raw pharmacy records and enriches them with:
1. Apollo.io - company data + decision-maker contacts
2. Google Places - verified phone, website, reviews
3. FDA 503B - outsourcing facility registration check
4. PCAB/ACHC - accreditation cross-reference
5. Classifier - segment assignment
"""

import logging
from datetime import datetime

from src.config import Settings
from src.enrichment.accreditation import AccreditationClient
from src.enrichment.apollo_client import ApolloClient
from src.enrichment.classifier import classify_pharmacy
from src.enrichment.fda_client import FDA503BClient
from src.enrichment.google_places_client import GooglePlacesClient

logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    """Orchestrates multi-source enrichment of pharmacy records."""

    def __init__(
        self,
        settings: Settings | None = None,
        skip_apollo: bool = False,
        skip_google: bool = False,
    ):
        from src.config import get_settings
        self.settings = settings or get_settings()
        self.skip_apollo = skip_apollo
        self.skip_google = skip_google

        # Initialize API clients
        self.apollo = ApolloClient(self.settings) if not skip_apollo else None
        self.google = GooglePlacesClient(self.settings) if not skip_google else None
        self.fda_503b = FDA503BClient(self.settings)
        self.accreditation = AccreditationClient(self.settings)

    def enrich_batch(self, records: list[dict], batch_size: int = 50) -> list[dict]:
        """Enrich a batch of pharmacy records.

        Processes records in configurable batch sizes to manage API rate limits.
        Returns enriched records with additional fields.
        """
        enriched = []
        total = len(records)

        for i in range(0, total, batch_size):
            batch = records[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size
            logger.info("Enriching batch %d/%d (%d records)", batch_num, total_batches, len(batch))

            for record in batch:
                try:
                    enriched_record = self.enrich_single(record)
                    enriched.append(enriched_record)
                except Exception as e:
                    logger.warning(
                        "Failed to enrich %s: %s",
                        record.get("business_name", "unknown"),
                        e,
                    )
                    # Keep the original record even if enrichment fails
                    record["enrichment_error"] = str(e)
                    enriched.append(record)

        logger.info("Enrichment complete: %d/%d records enriched", len(enriched), total)
        return enriched

    def enrich_single(self, record: dict) -> dict:
        """Enrich a single pharmacy record with all available data sources.

        Graceful degradation: if any source fails, continue with others.
        """
        enriched = dict(record)  # Copy original
        name = record.get("business_name", "")
        address = record.get("address", "")
        city = record.get("city", "")
        state = record.get("state", "")

        # 1. FDA 503B cross-reference
        try:
            is_503b = self.fda_503b.is_503b_facility(name, state)
            enriched["is_503b_registered"] = str(is_503b)
        except Exception as e:
            logger.debug("503B check failed for %s: %s", name, e)
            enriched["is_503b_registered"] = "False"

        # 2. PCAB/ACHC accreditation
        try:
            enriched["is_pcab_accredited"] = str(self.accreditation.is_pcab_accredited(name))
            enriched["is_achc_accredited"] = str(self.accreditation.is_achc_accredited(name))
        except Exception as e:
            logger.debug("Accreditation check failed for %s: %s", name, e)
            enriched["is_pcab_accredited"] = "False"
            enriched["is_achc_accredited"] = "False"

        # 3. Segment classification
        is_503b = enriched.get("is_503b_registered", "False").lower() == "true"
        enriched["segment"] = classify_pharmacy(
            name,
            license_type=record.get("license_type", ""),
            is_503b_registered=is_503b,
        )

        # 4. Sterile license flag
        license_type = record.get("license_type", "").lower()
        enriched["has_sterile_license"] = str("sterile" in license_type)

        # 5. Apollo enrichment (company + contacts)
        if self.apollo:
            try:
                apollo_data = self.apollo.enrich_pharmacy(name, address=f"{address} {city} {state}")
                enriched.update(apollo_data)
            except Exception as e:
                logger.debug("Apollo enrichment failed for %s: %s", name, e)

        # 6. Google Places enrichment
        if self.google:
            try:
                google_data = self.google.search_pharmacy(name, address, city, state)
                enriched.update(google_data)
                # Use Google website if Apollo didn't find one
                if not enriched.get("website") and google_data.get("google_website"):
                    enriched["website"] = google_data["google_website"]
            except Exception as e:
                logger.debug("Google Places failed for %s: %s", name, e)

        enriched["enriched_at"] = datetime.utcnow().isoformat()
        return enriched

    def close(self):
        """Clean up API client connections."""
        if self.apollo:
            self.apollo.close()
        if self.google:
            self.google.close()
