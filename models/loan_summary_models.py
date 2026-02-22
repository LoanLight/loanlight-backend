from __future__ import annotations
from decimal import Decimal
from pydantic import BaseModel


class LoanSummaryOut(BaseModel):
    total_federal_debt: Decimal
    total_private_debt: Decimal
    total_debt: Decimal
    total_min_monthly: Decimal
    federal_count: int
    private_count: int