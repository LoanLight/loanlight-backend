from __future__ import annotations
from decimal import Decimal
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from fastapi import HTTPException

from entities.job_offer_entity import JobOfferEntity
from entities.housing_profile_entity import HousingProfileEntity
from entities.federal_loan_entity import FederalLoanEntity
from entities.private_loan_entity import PrivateLoanEntity
from models.job_offer_models import JobOfferOut
from models.housing_models import HousingOut
from models.federal_loan_models import FederalLoanOut
from models.private_loan_models import PrivateLoanOut
from models.overview_models import (
    ProfileOverviewResponse, LoansSummary, CashflowBaseline, StateResponse,
    ProfileCompletionResponse,
)


class OverviewService:
    def __init__(self, session: Session):
        self._session = session

    def get_completion(self, user_id: UUID) -> ProfileCompletionResponse:
        job = self._session.scalars(select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)).one_or_none()
        housing = self._session.scalars(select(HousingProfileEntity).where(HousingProfileEntity.user_id == user_id)).one_or_none()

        missing: list[str] = []
        if not job:
            missing.append("job_offer")
        if not housing:
            missing.append("housing")

        complete = len(missing) == 0
        message = None
        if not complete:
            parts = []
            if "job_offer" in missing:
                parts.append("job offer")
            if "housing" in missing:
                parts.append("housing profile")
            message = f"Add your {' and '.join(parts)} to continue."

        return ProfileCompletionResponse(complete=complete, missing=missing, message=message)

    def get_state(self, user_id: UUID) -> StateResponse:
        job = self._session.scalars(select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)).one_or_none()
        housing = self._session.scalars(select(HousingProfileEntity).where(HousingProfileEntity.user_id == user_id)).one_or_none()
        fed = list(self._session.scalars(select(FederalLoanEntity).where(FederalLoanEntity.user_id == user_id)).all())
        priv = list(self._session.scalars(select(PrivateLoanEntity).where(PrivateLoanEntity.user_id == user_id)).all())

        job_out = None
        if job:
            job_out = JobOfferOut(
                id=job.id, base_salary=job.base_salary, bonus=job.bonus, state=job.state,
                estimated_take_home_monthly=job.estimated_take_home_monthly,
                tax_source=getattr(job, "tax_source", "fallback"),
                tax_payload=getattr(job, "tax_payload", None),
            )

        housing_out = None
        if housing:
            housing_out = HousingOut(
                id=housing.id, city=housing.city, state=housing.state, bedroom_count=housing.bedroom_count,
                housing_type=housing.housing_type, hud_estimated_rent_monthly=housing.hud_estimated_rent_monthly,
            )

        fed_out = [
            FederalLoanOut(
                id=r.id, loan_name=r.loan_name, balance=r.balance,
                interest_rate=r.interest_rate, min_monthly_payment=r.min_monthly_payment
            )
            for r in fed
        ]

        priv_out = [
            PrivateLoanOut(
                id=r.id, lender_name=r.lender_name, current_balance=r.current_balance,
                interest_rate=r.interest_rate, min_monthly_payment=r.min_monthly_payment
            )
            for r in priv
        ]

        return StateResponse(
            job_offer=job_out,
            housing=housing_out,
            federal_loans=fed_out,
            private_loans=priv_out,
        )

    def get_overview_or_404(self, user_id: UUID) -> ProfileOverviewResponse:
        job = self._session.scalars(select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)).one_or_none()
        housing = self._session.scalars(select(HousingProfileEntity).where(HousingProfileEntity.user_id == user_id)).one_or_none()
        if not job or not housing:
            raise HTTPException(status_code=400, detail="Missing job offer or housing profile.")

        fed = list(self._session.scalars(select(FederalLoanEntity).where(FederalLoanEntity.user_id == user_id)).all())
        priv = list(self._session.scalars(select(PrivateLoanEntity).where(PrivateLoanEntity.user_id == user_id)).all())

        total_debt = sum((r.balance for r in fed), Decimal("0.00")) + sum((r.current_balance for r in priv), Decimal("0.00"))
        total_min = sum(((r.min_monthly_payment or Decimal("0.00")) for r in fed), Decimal("0.00")) + sum((r.min_monthly_payment for r in priv), Decimal("0.00"))

        return ProfileOverviewResponse(
            job_offer=JobOfferOut(
                id=job.id, base_salary=job.base_salary, bonus=job.bonus, state=job.state,
                estimated_take_home_monthly=job.estimated_take_home_monthly,
                tax_source=getattr(job, "tax_source", "fallback"),
                tax_payload=getattr(job, "tax_payload", None),
            ),
            housing=HousingOut(
                id=housing.id, city=housing.city, state=housing.state, bedroom_count=housing.bedroom_count,
                housing_type=housing.housing_type, hud_estimated_rent_monthly=housing.hud_estimated_rent_monthly,
            ),
            loans=LoansSummary(
                total_debt=total_debt.quantize(Decimal("0.01")),
                total_min_payment=total_min.quantize(Decimal("0.01")),
                federal_count=len(fed),
                private_count=len(priv),
            ),
            cashflow_baseline=CashflowBaseline(
                take_home_monthly=job.estimated_take_home_monthly.quantize(Decimal("0.01")),
                rent_monthly=housing.hud_estimated_rent_monthly.quantize(Decimal("0.01")),
            ),
        )