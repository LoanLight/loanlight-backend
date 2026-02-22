from __future__ import annotations
from decimal import Decimal
from pydantic import BaseModel

from models.plan_models import LimitsOut


class PlanLimitsResponse(BaseModel):
    take_home_monthly: Decimal
    rent_monthly: Decimal
    minimum_loan_payments: Decimal
    monthly_non_housing_essentials: Decimal

    discretionary_before_loans: Decimal
    after_min_payments: Decimal

    limits: LimitsOut
    warnings: list[str] = []