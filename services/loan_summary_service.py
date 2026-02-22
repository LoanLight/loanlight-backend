from __future__ import annotations
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.federal_loan_entity import FederalLoanEntity
from entities.private_loan_entity import PrivateLoanEntity
from models.loan_summary_models import LoanSummaryOut


class LoanSummaryService:
    def __init__(self, session: Session):
        self._session = session

    def get_summary(self, user_id: UUID) -> LoanSummaryOut:
        federal = list(
            self._session.scalars(
                select(FederalLoanEntity).where(FederalLoanEntity.user_id == user_id)
            ).all()
        )
        private = list(
            self._session.scalars(
                select(PrivateLoanEntity).where(PrivateLoanEntity.user_id == user_id)
            ).all()
        )

        total_federal_debt = sum((r.balance for r in federal), Decimal("0.00"))
        total_private_debt = sum((r.current_balance for r in private), Decimal("0.00"))

        total_federal_min = sum(
            ((r.min_monthly_payment or Decimal("0.00")) for r in federal), Decimal("0.00")
        )
        total_private_min = sum((r.min_monthly_payment for r in private), Decimal("0.00"))

        total_debt = total_federal_debt + total_private_debt
        total_min_monthly = total_federal_min + total_private_min

        return LoanSummaryOut(
            total_federal_debt=total_federal_debt.quantize(Decimal("0.01")),
            total_private_debt=total_private_debt.quantize(Decimal("0.01")),
            total_debt=total_debt.quantize(Decimal("0.01")),
            total_min_monthly=total_min_monthly.quantize(Decimal("0.01")),
            federal_count=len(federal),
            private_count=len(private),
        )