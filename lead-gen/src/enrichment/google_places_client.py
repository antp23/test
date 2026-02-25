"""Google Places API client for business verification and enrichment.

Uses the Google Places API (New) for:
- Text search to find pharmacy businesses
- Place details for phone, website, reviews, hours
"""

import logging
from typing import Optional

import httpx

from src.config import Settings
from src.utils.rate_limiter import RateLimiter
from src.utils.retry import retry

logger = logging.getLogger(__name__)


class GooglePlacesClient:
    """Client for Google Places API business data enrichment."""

    BASE_URL = "https://places.googleapis.com/v1"

    def __init__(self, settings: Settings):
        self.api_key = settings.google_places_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=settings.google_rate_limit_per_min)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.BASE_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": self.api_key,
                },
                timeout=15.0,
            )
        return self._client

    @retry(max_retries=2, base_delay=1.0, exceptions=(httpx.HTTPError,))
    def search_pharmacy(self, name: str, address: str = "", city: str = "", state: str = "") -> dict:
        """Search for a pharmacy business by name and location.

        Returns dict with: place_id, formatted_address, phone, website,
        rating, review_count, business_status.
        """
        if not self.api_key:
            logger.debug("Google Places API key not configured, skipping")
            return {}

        self.rate_limiter.wait()

        query = name
        if city and state:
            query = f"{name} {city} {state}"
        elif address:
            query = f"{name} {address}"

        payload = {
            "textQuery": query + " pharmacy",
        }

        # Request specific fields to minimize cost
        field_mask = (
            "places.id,places.displayName,places.formattedAddress,"
            "places.nationalPhoneNumber,places.websiteUri,"
            "places.rating,places.userRatingCount,"
            "places.currentOpeningHours,places.businessStatus"
        )

        response = self.client.post(
            "/places:searchText",
            json=payload,
            headers={"X-Goog-FieldMask": field_mask},
        )
        response.raise_for_status()
        data = response.json()

        places = data.get("places", [])
        if not places:
            return {}

        place = places[0]  # Best match
        return {
            "google_place_id": place.get("id", ""),
            "google_address": place.get("formattedAddress", ""),
            "google_phone": place.get("nationalPhoneNumber", ""),
            "google_website": place.get("websiteUri", ""),
            "google_rating": place.get("rating"),
            "google_review_count": place.get("userRatingCount", 0),
            "google_business_status": place.get("businessStatus", ""),
        }

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
