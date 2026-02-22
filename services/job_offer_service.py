from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from entities.job_offer_entity import JobOfferEntity
from models.job_offer_models import JobOfferIn, JobOfferOut
from services.tax_service import TaxService


class JobOfferService:
    """
    Stores one current job offer per user (upsert).
    Caches take-home + tax breakdown in DB so plan calcs don't re-hit tax API.
    """

    def __init__(self, session: Session):
        self._session = session

    async def _compute_take_home_with_source(
        self,
        base_salary: Decimal,
        bonus: Decimal | None,
        state: str,
    ) -> tuple[Decimal, str, dict | None]:
        """
        Returns: (estimated_take_home_monthly, tax_source, tax_payload)
        tax_source: "api_ninjas_free" | "fallback"
        """
        gross_annual = base_salary + (bonus or Decimal("0.00"))
        st = state.upper()

        # No key => fallback only
        if not getattr(settings, "API_NINJAS_KEY", None):
            monthly = self._estimate_take_home_monthly(base_salary, bonus, st)
            payload = {
                "gross_income_annual": str(gross_annual),
                "note": "API_NINJAS_KEY missing; used fallback estimate",
            }
            return monthly, "fallback", payload

        try:
            # FREE-TIER tax service:
            # returns (monthly_take_home, breakdown_dict)
            tax = TaxService()
            monthly, breakdown = await tax.estimate_take_home_monthly(
                salary_annual=gross_annual,
                state=st,
                filing_status="single",
            )

            payload_small = {
                "gross_income_annual": str(breakdown.get("gross_income")),
                "federal_tax_annual": str(breakdown.get("federal_tax")),
                "fica_total_annual": str(breakdown.get("fica_total")),
                "state_tax_annual": str(breakdown.get("state_tax")),
                "net_annual": str(breakdown.get("net_annual")),
                "method": "api_ninjas_free_federal + local_fica + local_state",
            }

            return monthly, "api_ninjas_free", payload_small

        except Exception as e:
            # Never crash the app because tax API failed
            print("Tax computation failed -> fallback:", repr(e))
            monthly = self._estimate_take_home_monthly(base_salary, bonus, st)
            payload = {
                "gross_income_annual": str(gross_annual),
                "note": "Tax API failed; used fallback estimate",
                "error": repr(e),
            }
            return monthly, "fallback", payload

    async def upsert(self, user_id: UUID, payload: JobOfferIn) -> JobOfferOut:
        q = select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)
        row = self._session.scalars(q).one_or_none()

        est_take_home, tax_source, tax_payload = await self._compute_take_home_with_source(
            payload.base_salary,
            payload.bonus,
            payload.state,
        )

        if row is None:
            row = JobOfferEntity(
                user_id=user_id,
                base_salary=payload.base_salary,
                bonus=payload.bonus,
                state=payload.state.upper(),
                estimated_take_home_monthly=est_take_home,
                tax_source=tax_source,
                tax_payload=tax_payload,
            )
            self._session.add(row)
        else:
            row.base_salary = payload.base_salary
            row.bonus = payload.bonus
            row.state = payload.state.upper()
            row.estimated_take_home_monthly = est_take_home
            row.tax_source = tax_source
            row.tax_payload = tax_payload

        self._session.commit()
        self._session.refresh(row)

        return JobOfferOut(
            id=row.id,
            base_salary=row.base_salary,
            bonus=row.bonus,
            state=row.state,
            estimated_take_home_monthly=row.estimated_take_home_monthly,
            tax_source=row.tax_source,
            tax_payload=row.tax_payload,
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
            tax_source=getattr(row, "tax_source", "fallback"),
            tax_payload=getattr(row, "tax_payload", None),
        )

    def _estimate_take_home_monthly(self, base_salary: Decimal, bonus: Decimal | None, state: str) -> Decimal:
        gross_annual = base_salary + (bonus or Decimal("0.00"))
        effective = Decimal("0.28")

        st = state.upper()
        if st in {"TX", "FL", "WA"}:
            effective -= Decimal("0.02")
        elif st in {"CA", "NY", "NJ"}:
            effective += Decimal("0.02")

        net_annual = gross_annual * (Decimal("1.00") - effective)
        return max((net_annual / Decimal("12")).quantize(Decimal("0.01")), Decimal("0.00"))