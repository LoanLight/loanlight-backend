from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from entities.federal_loan_entity import FederalLoanEntity
from models.federal_loan_models import FederalLoanIn, FederalLoanOut, FederalLoanBulkOut


class FederalLoanService:
    def __init__(self, session: Session):
        self._session = session

    def _estimate_min_payment(self, balance: Decimal) -> Decimal:
        # Hackathon-simple: 1% of balance, min $25
        est = (balance * Decimal("0.01")).quantize(Decimal("0.01"))
        return max(est, Decimal("25.00"))

    def replace_all(self, user_id: UUID, loans: list[FederalLoanIn]) -> FederalLoanBulkOut:
        self._session.execute(delete(FederalLoanEntity).where(FederalLoanEntity.user_id == user_id))

        entities: list[FederalLoanEntity] = []
        for l in loans:
            min_pay = l.min_monthly_payment
            if min_pay is None:
                min_pay = self._estimate_min_payment(l.balance)

            ent = FederalLoanEntity(
                user_id=user_id,
                loan_name=l.loan_name,
                balance=l.balance,
                interest_rate=l.interest_rate,
                min_monthly_payment=min_pay,
            )
            entities.append(ent)
            self._session.add(ent)

        self._session.commit()

        return self.list(user_id)

    def list(self, user_id: UUID) -> FederalLoanBulkOut:
        q = select(FederalLoanEntity).where(FederalLoanEntity.user_id == user_id)
        rows = list(self._session.scalars(q).all())

        outs: list[FederalLoanOut] = [
            FederalLoanOut(
                id=r.id,
                loan_name=r.loan_name,
                balance=r.balance,
                interest_rate=r.interest_rate,
                min_monthly_payment=r.min_monthly_payment,
            )
            for r in rows
        ]

        total_balance = sum((r.balance for r in rows), Decimal("0.00"))
        total_min_payment = sum(((r.min_monthly_payment or Decimal("0.00")) for r in rows), Decimal("0.00"))

        return FederalLoanBulkOut(
            loans=outs,
            total_balance=total_balance.quantize(Decimal("0.01")),
            total_min_payment=total_min_payment.quantize(Decimal("0.01")),
        )