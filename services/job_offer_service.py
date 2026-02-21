from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.job_offer_entity import JobOfferEntity
from models.job_offer_models import JobOfferIn, JobOfferOut


class JobOfferService:
    def __init__(self, session: Session):
        self._session = session

    def _estimate_take_home_monthly(self, base_salary: Decimal, bonus: Decimal | None, state: str) -> Decimal:
        """
        Hackathon-simple take-home:
          - assume bonus is annual and taxed like income (simplified)
          - federal+fica blended effective rate ~ 28% for many new grads
          - tiny state adjustment placeholder
        """
        gross_annual = base_salary + (bonus or Decimal("0.00"))
        effective = Decimal("0.28")  # simple blended assumption

        # tiny state tweak
        st = state.upper()
        if st in {"TX", "FL", "WA"}:
            effective -= Decimal("0.02")
        elif st in {"CA", "NY", "NJ"}:
            effective += Decimal("0.02")

        net_annual = gross_annual * (Decimal("1.00") - effective)
        net_monthly = (net_annual / Decimal("12")).quantize(Decimal("0.01"))
        return max(net_monthly, Decimal("0.00"))

    def upsert(self, user_id: UUID, payload: JobOfferIn) -> JobOfferOut:
        q = select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)
        row = self._session.scalars(q).one_or_none()

        est_take_home = self._estimate_take_home_monthly(payload.base_salary, payload.bonus, payload.state)

        if row is None:
            row = JobOfferEntity(
                user_id=user_id,
                base_salary=payload.base_salary,
                bonus=payload.bonus,
                state=payload.state.upper(),
                estimated_take_home_monthly=est_take_home,
            )
            self._session.add(row)
        else:
            row.base_salary = payload.base_salary
            row.bonus = payload.bonus
            row.state = payload.state.upper()
            row.estimated_take_home_monthly = est_take_home

        self._session.commit()
        self._session.refresh(row)

        return JobOfferOut(
            id=row.id,
            base_salary=row.base_salary,
            bonus=row.bonus,
            state=row.state,
            estimated_take_home_monthly=row.estimated_take_home_monthly,
        )

    def get_or_404(self, user_id: UUID) -> JobOfferOut:
        q = select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)
        row = self._session.scalars(q).one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="Job offer not found.")

        return JobOfferOut(
            id=row.id,
            base_salary=row.base_salary,
            bonus=row.bonus,
            state=row.state,
            estimated_take_home_monthly=row.estimated_take_home_monthly,
        )