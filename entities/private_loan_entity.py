from __future__ import annotations

from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from entities.entity_base import EntityBase


class PrivateLoanEntity(EntityBase):
    __tablename__ = "private_loans"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False)

    lender_name: Mapped[str] = mapped_column(String(255), nullable=False)

    current_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    interest_rate: Mapped[Decimal] = mapped_column(
        Numeric(6, 3), nullable=False, default=Decimal("0.000")
    )  # percent

    min_monthly_payment: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))