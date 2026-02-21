from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class PrivateLoanIn(BaseModel):
    lender_name: str
    current_balance: Decimal = Field(ge=0)
    interest_rate: Decimal = Field(ge=0)  # percent
    min_monthly_payment: Decimal = Field(ge=0)


class PrivateLoanOut(BaseModel):
    id: UUID
    lender_name: str
    current_balance: Decimal
    interest_rate: Decimal
    min_monthly_payment: Decimal


class PrivateLoanBulkIn(BaseModel):
    loans: list[PrivateLoanIn]


class PrivateLoanBulkOut(BaseModel):
    loans: list[PrivateLoanOut]
    total_balance: Decimal
    total_min_payment: Decimal