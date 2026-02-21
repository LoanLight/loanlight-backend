from __future__ import annotations

from uuid import uuid4, UUID
from decimal import Decimal

from sqlalchemy import String, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from entities.entity_base import EntityBase


class HousingProfileEntity(EntityBase):
    __tablename__ = "housing_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=False, unique=True)

    city: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    bedroom_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    housing_type: Mapped[str] = mapped_column(String(64), nullable=False, default="apartment")

    # computed by HUD FMR
    hud_estimated_rent_monthly: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )