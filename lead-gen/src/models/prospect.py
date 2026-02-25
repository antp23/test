"""Prospect model - enriched, scored pharmacy records ready for sales outreach."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Segment(str, enum.Enum):
    COMPOUNDING_503A = "503A"
    OUTSOURCING_503B = "503B"
    MAIL_ORDER = "Mail Order"
    B_AND_M = "B&M"
    SPECIALTY = "Specialty"
    HOSPITAL = "Hospital"
    UNKNOWN = "Unknown"


class Priority(str, enum.Enum):
    HOT = "Hot"
    WARM = "Warm"
    COLD = "Cold"
    WATCH_LIST = "Watch List"


class ProspectStatus(str, enum.Enum):
    NEW = "New"
    IMPORTED = "Imported"
    DUPLICATE = "Duplicate"
    REJECTED = "Rejected"


class Prospect(Base):
    """Enriched and scored pharmacy prospect."""

    __tablename__ = "prospects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pharmacy_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pharmacies.id"), nullable=True
    )

    # Core info
    business_name: Mapped[str] = mapped_column(String(500))
    segment: Mapped[Segment] = mapped_column(
        Enum(Segment, name="segment_type"), default=Segment.UNKNOWN
    )
    priority: Mapped[Priority | None] = mapped_column(
        Enum(Priority, name="priority_level"), nullable=True
    )
    tier: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Location
    state: Mapped[str] = mapped_column(String(2))
    city: Mapped[str | None] = mapped_column(String(200), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    zip_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Apollo enrichment
    contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Google Places enrichment
    google_review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    google_rating: Mapped[float | None] = mapped_column(nullable=True)

    # Flags
    is_503b_registered: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pcab_accredited: Mapped[bool] = mapped_column(Boolean, default=False)
    is_achc_accredited: Mapped[bool] = mapped_column(Boolean, default=False)
    has_sterile_license: Mapped[bool] = mapped_column(Boolean, default=False)

    # Tracking
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notion_page_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    assigned_rep: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[ProspectStatus] = mapped_column(
        Enum(ProspectStatus, name="prospect_status"), default=ProspectStatus.NEW
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    pharmacy = relationship("Pharmacy", back_populates="prospect")

    def __repr__(self) -> str:
        return f"<Prospect {self.business_name} score={self.score} tier={self.tier}>"
