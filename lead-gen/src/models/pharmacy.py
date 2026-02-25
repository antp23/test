"""Pharmacy model - raw records from state board scrapers."""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Pharmacy(Base):
    """Raw pharmacy record scraped from a state board of pharmacy."""

    __tablename__ = "pharmacies"
    __table_args__ = (
        UniqueConstraint("license_number", "state", name="uq_pharmacy_license_state"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    business_name: Mapped[str] = mapped_column(String(500))
    license_number: Mapped[str] = mapped_column(String(100))
    license_type: Mapped[str] = mapped_column(String(200), default="")
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    city: Mapped[str | None] = mapped_column(String(200), nullable=True)
    state: Mapped[str] = mapped_column(String(2))
    zip_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    license_status: Mapped[str] = mapped_column(String(50), default="Active")
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    scrape_date: Mapped[date] = mapped_column(Date, default=date.today)
    scrape_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scrape_runs.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    scrape_run = relationship("ScrapeRun", back_populates="pharmacies")
    prospect = relationship("Prospect", back_populates="pharmacy", uselist=False)

    def __repr__(self) -> str:
        return f"<Pharmacy {self.business_name} ({self.state} {self.license_number})>"
