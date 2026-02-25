"""Vendor model - manufacturer/supplier pipeline tracking."""

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class VendorType(str, enum.Enum):
    API_MANUFACTURER = "API Manufacturer"
    FINISHED_DOSAGE = "Finished Dosage"
    REPACKAGER = "Repackager"
    DISTRIBUTOR = "Distributor"
    RAW_MATERIAL = "Raw Material"


class VendorStage(str, enum.Enum):
    IDENTIFIED = "Identified"
    INITIAL_CONTACT = "Initial Contact"
    EVALUATING = "Evaluating"
    DOC_REVIEW = "Doc Review"
    NEGOTIATION = "Negotiation"
    ONBOARDING = "Onboarding"
    ACTIVE = "Active"
    ON_HOLD = "On Hold"
    REJECTED = "Rejected"


class FDAStatus(str, enum.Enum):
    REGISTERED = "Registered"
    NOT_REGISTERED = "Not Registered"
    UNKNOWN = "Unknown"


class CGMPStatus(str, enum.Enum):
    COMPLIANT = "Compliant"
    WARNING_LETTER = "Warning Letter"
    UNKNOWN = "Unknown"


class VendorPriority(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Vendor(Base):
    """Vendor/manufacturer in the sourcing pipeline."""

    __tablename__ = "vendors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vendor_name: Mapped[str] = mapped_column(String(500))
    vendor_type: Mapped[VendorType] = mapped_column(
        Enum(VendorType, name="vendor_type_enum")
    )
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    products_of_interest: Mapped[str | None] = mapped_column(Text, nullable=True)
    stage: Mapped[VendorStage] = mapped_column(
        Enum(VendorStage, name="vendor_stage_enum"), default=VendorStage.IDENTIFIED
    )
    fda_registration_status: Mapped[FDAStatus] = mapped_column(
        Enum(FDAStatus, name="fda_status_enum"), default=FDAStatus.UNKNOWN
    )
    cgmp_status: Mapped[CGMPStatus] = mapped_column(
        Enum(CGMPStatus, name="cgmp_status_enum"), default=CGMPStatus.UNKNOWN
    )
    contact_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    est_product_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    est_annual_revenue: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    priority: Mapped[VendorPriority] = mapped_column(
        Enum(VendorPriority, name="vendor_priority_enum"), default=VendorPriority.MEDIUM
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    notion_page_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Vendor {self.vendor_name} stage={self.stage.value}>"
