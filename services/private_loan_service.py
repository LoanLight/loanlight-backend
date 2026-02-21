from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from entities.private_loan_entity import PrivateLoanEntity
from models.private_loan_models import PrivateLoanIn, PrivateLoanOut, PrivateLoanBulkOut


class PrivateLoanService:
    def __init__(self, session: Session):
        self._session = session

    def replace_all(self, user_id: UUID, loans: list[PrivateLoanIn]) -> PrivateLoanBulkOut:
        self._session.execute(delete(PrivateLoanEntity).where(PrivateLoanEntity.user_id == user_id))

        for l in loans:
            ent = PrivateLoanEntity(
                user_id=user_id,
                lender_name=l.lender_name,
                current_balance=l.current_balance,
                interest_rate=l.interest_rate,
                min_monthly_payment=l.min_monthly_payment,
            )
            self._session.add(ent)

        self._session.commit()
        return self.list(user_id)

    def list(self, user_id: UUID) -> PrivateLoanBulkOut:
        q = select(PrivateLoanEntity).where(PrivateLoanEntity.user_id == user_id)
        rows = list(self._session.scalars(q).all())

        outs: list[PrivateLoanOut] = [
            PrivateLoanOut(
                id=r.id,
                lender_name=r.lender_name,
                current_balance=r.current_balance,
                interest_rate=r.interest_rate,
                min_monthly_payment=r.min_monthly_payment,
            )
            for r in rows
        ]

        total_balance = sum((r.current_balance for r in rows), Decimal("0.00"))
        total_min_payment = sum((r.min_monthly_payment for r in rows), Decimal("0.00"))

        return PrivateLoanBulkOut(
            loans=outs,
            total_balance=total_balance.quantize(Decimal("0.01")),
            total_min_payment=total_min_payment.quantize(Decimal("0.01")),
        )