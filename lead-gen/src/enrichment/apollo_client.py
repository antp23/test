"""Apollo.io API client for company and contact enrichment.

Apollo API docs: https://apolloio.github.io/apollo-api-docs/
Endpoints used:
  - POST /v1/organizations/enrich (company enrichment)
  - POST /v1/people/match (contact enrichment)
"""

import logging
from typing import Optional

import httpx

from src.config import Settings
from src.utils.rate_limiter import RateLimiter
from src.utils.retry import retry

logger = logging.getLogger(__name__)


class ApolloClient:
    """Client for Apollo.io enrichment API."""

    BASE_URL = "https://api.apollo.io/api/v1"

    def __init__(self, settings: Settings):
        self.api_key = settings.apollo_api_key
        self.rate_limiter = RateLimiter(requests_per_minute=settings.apollo_rate_limit_per_min)
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.BASE_URL,
                headers={
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache",
                },
                timeout=30.0,
            )
        return self._client

    @retry(max_retries=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    def enrich_organization(
        self, name: str, domain: str = "", address: str = ""
    ) -> dict:
        """Enrich a company/organization by name and optional domain/address.

        Returns dict with keys: name, website, linkedin_url, phone, employee_count,
        industry, city, state, country, etc.
        """
        if not self.api_key:
            logger.debug("Apollo API key not configured, skipping enrichment")
            return {}

        self.rate_limiter.wait()

        payload = {
            "api_key": self.api_key,
            "name": name,
        }
        if domain:
            payload["domain"] = domain
        if address:
            payload["address"] = address

        response = self.client.post("/organizations/enrich", json=payload)
        response.raise_for_status()
        data = response.json()

        org = data.get("organization", {})
        if not org:
            return {}

        return {
            "apollo_org_name": org.get("name", ""),
            "website": org.get("website_url", ""),
            "linkedin_url": org.get("linkedin_url", ""),
            "apollo_phone": org.get("phone", ""),
            "employee_count": org.get("estimated_num_employees"),
            "industry": org.get("industry", ""),
            "annual_revenue": org.get("annual_revenue_printed", ""),
        }

    @retry(max_retries=3, base_delay=2.0, exceptions=(httpx.HTTPError,))
    def find_decision_maker(
        self, organization_name: str, titles: list[str] | None = None
    ) -> dict:
        """Find a decision-maker contact at the organization.

        Default title search: Owner, Pharmacist-in-Charge, Director of Pharmacy,
        Purchasing Manager, General Manager.

        Returns dict with keys: name, title, email, phone, linkedin_url.
        """
        if not self.api_key:
            return {}

        self.rate_limiter.wait()

        search_titles = titles or [
            "Owner",
            "Pharmacist in Charge",
            "Director of Pharmacy",
            "Purchasing Manager",
            "General Manager",
        ]

        payload = {
            "api_key": self.api_key,
            "q_organization_name": organization_name,
            "person_titles": search_titles,
            "per_page": 1,
        }

        response = self.client.post("/mixed_people/search", json=payload)
        response.raise_for_status()
        data = response.json()

        people = data.get("people", [])
        if not people:
            return {}

        person = people[0]
        return {
            "contact_name": person.get("name", ""),
            "contact_title": person.get("title", ""),
            "contact_email": person.get("email", ""),
            "contact_phone": person.get("phone_numbers", [{}])[0].get("sanitized_number", "")
            if person.get("phone_numbers")
            else "",
            "contact_linkedin": person.get("linkedin_url", ""),
        }

    def enrich_pharmacy(self, name: str, address: str = "", domain: str = "") -> dict:
        """Full enrichment: org data + decision-maker contact.

        Returns combined dict of org enrichment and contact data.
        """
        result = {}

        # Org enrichment
        org_data = self.enrich_organization(name, domain=domain, address=address)
        result.update(org_data)

        # Contact enrichment
        contact_data = self.find_decision_maker(name)
        result.update(contact_data)

        return result

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
