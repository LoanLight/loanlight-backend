from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class JobOfferIn(BaseModel):
    base_salary: Decimal = Field(ge=0)
    bonus: Decimal | None = Field(default=None, ge=0)
    state: str = Field(min_length=2, max_length=2)


class JobOfferOut(BaseModel):
    id: UUID
    base_salary: Decimal
    bonus: Decimal | None
    state: str
    estimated_take_home_monthly: Decimal