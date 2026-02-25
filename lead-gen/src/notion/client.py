"""Notion API client wrapper.

Provides rate-limited access to the Notion API for creating and querying
database pages. Rate limit: 3 requests/second average.
"""

import logging
import time
from typing import Any, Optional

from notion_client import Client

from src.config import Settings

logger = logging.getLogger(__name__)


class NotionClient:
    """Wrapper around the Notion SDK with rate limiting and error handling."""

    RATE_LIMIT_DELAY = 0.34  # ~3 req/sec

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Optional[Client] = None
        self._last_request_time = 0.0

    @property
    def client(self) -> Client:
        if self._client is None:
            if not self.settings.notion_api_key:
                raise ValueError("NOTION_API_KEY not configured")
            self._client = Client(auth=self.settings.notion_api_key)
        return self._client

    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        elapsed = time.monotonic() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.monotonic()

    def create_page(self, database_id: str, properties: dict[str, Any]) -> dict:
        """Create a new page in a Notion database.

        Args:
            database_id: The Notion database ID.
            properties: Dict mapping property names to Notion property values.

        Returns:
            The created page object from Notion API.
        """
        self._rate_limit()
        try:
            page = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties,
            )
            return page
        except Exception as e:
            logger.error("Failed to create Notion page: %s", e)
            raise

    def query_database(
        self,
        database_id: str,
        filter_obj: dict | None = None,
        sorts: list[dict] | None = None,
        page_size: int = 100,
    ) -> list[dict]:
        """Query a Notion database with optional filters and sorting.

        Returns all matching pages (handles pagination automatically).
        """
        self._rate_limit()
        all_results = []
        has_more = True
        start_cursor = None

        while has_more:
            kwargs: dict[str, Any] = {
                "database_id": database_id,
                "page_size": page_size,
            }
            if filter_obj:
                kwargs["filter"] = filter_obj
            if sorts:
                kwargs["sorts"] = sorts
            if start_cursor:
                kwargs["start_cursor"] = start_cursor

            response = self.client.databases.query(**kwargs)
            all_results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

            if has_more:
                self._rate_limit()

        return all_results

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict:
        """Update an existing Notion page's properties."""
        self._rate_limit()
        return self.client.pages.update(page_id=page_id, properties=properties)

    def search_by_phone(self, database_id: str, phone: str) -> list[dict]:
        """Search for prospects by phone number."""
        if not phone:
            return []
        return self.query_database(
            database_id,
            filter_obj={
                "property": "Phone",
                "phone_number": {"equals": phone},
            },
        )

    def search_by_name(self, database_id: str, name: str) -> list[dict]:
        """Search for prospects by business name."""
        if not name:
            return []
        return self.query_database(
            database_id,
            filter_obj={
                "property": "Business Name",
                "title": {"equals": name},
            },
        )
