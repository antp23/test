"""Drug shortage model - FDA shortage database tracking."""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class DrugShortage(Base):
    """FDA drug shortage record for monitoring and alerting."""

    __tablename__ = "drug_shortages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    drug_name: Mapped[str] = mapped_column(String(500))
    ndc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    shortage_status: Mapped[str] = mapped_column(String(100), default="Current")
    fda_shortage_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    first_detected: Mapped[date] = mapped_column(Date, default=date.today)
    last_updated: Mapped[date] = mapped_column(Date, default=date.today)
    matches_catalog: Mapped[bool] = mapped_column(Boolean, default=False)
    matches_compounder_needs: Mapped[bool] = mapped_column(Boolean, default=False)
    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DrugShortage {self.drug_name} status={self.shortage_status}>"
