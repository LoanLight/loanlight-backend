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
from models.limits_models import PlanLimitsResponse
from models.plan_models import LimitsOut


class LimitsService:
    def __init__(self, session: Session):
        self._session = session

    def get_limits(self, user_id: UUID, essentials: Decimal) -> PlanLimitsResponse:
        job = self._session.scalars(select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)).one_or_none()
        housing = self._session.scalars(select(HousingProfileEntity).where(HousingProfileEntity.user_id == user_id)).one_or_none()
        if not job or not housing:
            raise HTTPException(status_code=400, detail="Missing job offer or housing profile.")

        fed = list(self._session.scalars(select(FederalLoanEntity).where(FederalLoanEntity.user_id == user_id)).all())
        priv = list(self._session.scalars(select(PrivateLoanEntity).where(PrivateLoanEntity.user_id == user_id)).all())

        min_payments = (
            sum(((r.min_monthly_payment or Decimal("0.00")) for r in fed), Decimal("0.00"))
            + sum((r.min_monthly_payment for r in priv), Decimal("0.00"))
        )

        take_home = job.estimated_take_home_monthly
        rent = housing.hud_estimated_rent_monthly

        discretionary_before_loans = max(Decimal("0.00"), take_home - rent - essentials)
        after_min_payments = max(Decimal("0.00"), discretionary_before_loans - min_payments)

        warnings = []
        if discretionary_before_loans < min_payments:
            warnings.append("Your income after essentials does not cover minimum loan payments.")

        return PlanLimitsResponse(
            take_home_monthly=take_home.quantize(Decimal("0.01")),
            rent_monthly=rent.quantize(Decimal("0.01")),
            minimum_loan_payments=min_payments.quantize(Decimal("0.01")),
            monthly_non_housing_essentials=essentials.quantize(Decimal("0.01")),
            discretionary_before_loans=discretionary_before_loans.quantize(Decimal("0.01")),
            after_min_payments=after_min_payments.quantize(Decimal("0.01")),
            limits=LimitsOut(
                min_commitment=min_payments.quantize(Decimal("0.01")),
                max_commitment=discretionary_before_loans.quantize(Decimal("0.01")),
            ),
            warnings=warnings,
        )