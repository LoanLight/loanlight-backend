from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class FederalLoanIn(BaseModel):
    loan_name: str
    balance: Decimal = Field(ge=0)
    interest_rate: Decimal = Field(ge=0)  # percent e.g. 6.8
    min_monthly_payment: Decimal | None = Field(default=None, ge=0)


class FederalLoanOut(BaseModel):
    id: UUID
    loan_name: str
    balance: Decimal
    interest_rate: Decimal
    min_monthly_payment: Decimal | None


class FederalLoanBulkIn(BaseModel):
    loans: list[FederalLoanIn]


class FederalLoanBulkOut(BaseModel):
    loans: list[FederalLoanOut]
    total_balance: Decimal
    total_min_payment: Decimal