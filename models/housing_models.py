from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class HousingIn(BaseModel):
    city: str = Field(min_length=1, max_length=128)
    state: str = Field(min_length=2, max_length=2)
    bedroom_count: int = Field(ge=0, le=10)  # 0=studio
    housing_type: str = Field(default="apartment", max_length=64)


class HousingOut(BaseModel):
    id: UUID
    city: str
    state: str
    bedroom_count: int
    housing_type: str
    hud_estimated_rent_monthly: Decimal