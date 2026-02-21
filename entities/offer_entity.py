import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Numeric, String, Date

from database.base import Base

class OfferEntity(Base):
    __tablename__ = "offers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)

    base_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    signing_bonus: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    start_date: Mapped[object | None] = mapped_column(Date, nullable=True)

    retirement_match_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    health_premium_monthly: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    location_city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location_state: Mapped[str | None] = mapped_column(String(50), nullable=True)