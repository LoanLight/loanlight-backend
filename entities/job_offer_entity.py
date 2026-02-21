from __future__ import annotations

from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from entities.entity_base import EntityBase


class JobOfferEntity(EntityBase):
    __tablename__ = "job_offers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False, unique=True)

    base_salary: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    bonus: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    state: Mapped[str] = mapped_column(String(2), nullable=False)  # e.g. "MA"

    # computed by backend
    estimated_take_home_monthly: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )