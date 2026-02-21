import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Numeric, String, DateTime, func

from database.base import Base

class PlanEntity(Base):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)

    mode: Mapped[str] = mapped_column(String(20), nullable=False, default="optimize")  # optimize|target_date
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="moderate")  # low|moderate|high
    strategy: Mapped[str] = mapped_column(String(20), nullable=False, default="avalanche")  # avalanche|snowball|hybrid

    monthly_essentials: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=900)

    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)