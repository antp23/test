"""Application configuration loaded from environment variables."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Root configuration - all settings loaded from .env file."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/safeway_lead_gen"

    # Apollo.io
    apollo_api_key: str = ""
    apollo_rate_limit_per_min: int = 100

    # Google Places
    google_places_api_key: str = ""
    google_rate_limit_per_min: int = 500

    # Notion
    notion_api_key: str = ""
    notion_prospects_db_id: str = ""
    notion_vendors_db_id: str = ""

    # Slack
    slack_webhook_url: str = ""
    slack_channel: str = "#lead-gen-alerts"

    # FDA
    fda_api_key: str = ""

    # Scraper
    scraper_user_agent: str = "SafewayDistributors/1.0"
    scraper_request_delay: float = 2.0
    scraper_max_retries: int = 3

    # Enrichment
    enrichment_batch_size: int = 50

    # Rep assignment
    reps: str = "Colin,Kevin"
    default_rep: str = "Colin"

    # State tiers
    tier_1_states: str = "FL,TX,CA,NY,NJ,PA,OH,GA,NC,AZ"
    tier_2_states: str = "IL,MI,VA,MA,TN,MO,WI,MN,MD,IN"

    # Logging
    log_level: str = "INFO"

    # Paths
    data_dir: Path = Path("data")
    output_dir: Path = Path("output")

    @property
    def rep_list(self) -> list[str]:
        return [r.strip() for r in self.reps.split(",") if r.strip()]

    @property
    def tier_1_state_list(self) -> list[str]:
        return [s.strip() for s in self.tier_1_states.split(",") if s.strip()]

    @property
    def tier_2_state_list(self) -> list[str]:
        return [s.strip() for s in self.tier_2_states.split(",") if s.strip()]

    def get_state_tier(self, state_code: str) -> int:
        code = state_code.upper()
        if code in self.tier_1_state_list:
            return 1
        if code in self.tier_2_state_list:
            return 2
        return 3


def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
