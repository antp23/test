"""Product request model - tracking demand signals from rep interactions."""

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class ProductRequest(Base):
    """Product demand tracking from rep call notes and customer requests."""

    __tablename__ = "product_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_name: Mapped[str] = mapped_column(String(500))
    ndc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    requested_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    request_date: Mapped[date] = mapped_column(Date, default=date.today)
    segment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_currently_available: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<ProductRequest {self.product_name} by={self.requested_by}>"
