"""Scrape run model - execution log for scraper runs."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class ScrapeStatus(str, enum.Enum):
    RUNNING = "Running"
    SUCCESS = "Success"
    FAILED = "Failed"
    PARTIAL = "Partial"


class ScrapeRun(Base):
    """Log of each scraper execution for monitoring and debugging."""

    __tablename__ = "scrape_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    state: Mapped[str] = mapped_column(String(2))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[ScrapeStatus] = mapped_column(
        Enum(ScrapeStatus, name="scrape_status_enum"), default=ScrapeStatus.RUNNING
    )
    records_found: Mapped[int] = mapped_column(Integer, default=0)
    records_new: Mapped[int] = mapped_column(Integer, default=0)
    records_updated: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    pharmacies = relationship("Pharmacy", back_populates="scrape_run")

    def __repr__(self) -> str:
        return f"<ScrapeRun {self.state} status={self.status.value} found={self.records_found}>"
