from __future__ import annotations
from decimal import Decimal
from pydantic import BaseModel

from models.job_offer_models import JobOfferOut
from models.housing_models import HousingOut
from models.federal_loan_models import FederalLoanOut
from models.private_loan_models import PrivateLoanOut


class LoansSummary(BaseModel):
    total_debt: Decimal
    total_min_payment: Decimal
    federal_count: int
    private_count: int


class CashflowBaseline(BaseModel):
    take_home_monthly: Decimal
    rent_monthly: Decimal
    non_rent_essentials_monthly: Decimal | None = None
    discretionary_before_loans: Decimal | None = None
    after_min_payments: Decimal | None = None


class ProfileOverviewResponse(BaseModel):
    job_offer: JobOfferOut
    housing: HousingOut
    loans: LoansSummary
    cashflow_baseline: CashflowBaseline


class StateResponse(BaseModel):
    job_offer: JobOfferOut | None
    housing: HousingOut | None
    federal_loans: list[FederalLoanOut]
    private_loans: list[PrivateLoanOut]


class ProfileCompletionResponse(BaseModel):
    complete: bool
    missing: list[str] = []
    message: str | None = None