import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Numeric, String

from database.base import Base

class LoanEntity(Base):
    __tablename__ = "loans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)

    loan_category: Mapped[str] = mapped_column(String(20), nullable=False, default="federal")  # federal|private
    loan_type: Mapped[str] = mapped_column(String(120), nullable=False)
    interest_rate: Mapped[float] = mapped_column(Numeric(6, 3), nullable=False)
    principal_balance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="in_repayment")
    servicer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)