from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.federal_loan_entity import FederalLoanEntity
from entities.private_loan_entity import PrivateLoanEntity
from entities.job_offer_entity import JobOfferEntity
from entities.housing_profile_entity import HousingProfileEntity
from models.plan_models import (
    PlanCalculateRequest,
    PlanCalculateResponse,
    LimitsOut,
    CashflowOut,
    InvestingOut,
    SeriesPoint,
)


@dataclass
class LoanSim:
    name: str
    balance: Decimal
    apr_pct: Decimal
    min_payment: Decimal


class PlanService:
    def __init__(self, session: Session):
        self._session = session

    def _load_state(self, user_id: UUID) -> tuple[list[LoanSim], Decimal, Decimal, Decimal]:
        # loans
        fed = list(self._session.scalars(select(FederalLoanEntity).where(FederalLoanEntity.user_id == user_id)).all())
        priv = list(self._session.scalars(select(PrivateLoanEntity).where(PrivateLoanEntity.user_id == user_id)).all())

        loans: list[LoanSim] = []
        for r in fed:
            loans.append(
                LoanSim(
                    name=r.loan_name,
                    balance=r.balance,
                    apr_pct=r.interest_rate,
                    min_payment=(r.min_monthly_payment or Decimal("0.00")),
                )
            )
        for r in priv:
            loans.append(
                LoanSim(
                    name=r.lender_name,
                    balance=r.current_balance,
                    apr_pct=r.interest_rate,
                    min_payment=r.min_monthly_payment,
                )
            )

        if not loans:
            raise HTTPException(status_code=400, detail="No loans found. Add loans first.")

        job = self._session.scalars(select(JobOfferEntity).where(JobOfferEntity.user_id == user_id)).one_or_none()
        if not job:
            raise HTTPException(status_code=400, detail="Job offer not found. Add job offer first.")
        take_home = job.estimated_take_home_monthly

        housing = self._session.scalars(select(HousingProfileEntity).where(HousingProfileEntity.user_id == user_id)).one_or_none()
        if not housing:
            raise HTTPException(status_code=400, detail="Housing profile not found. Add housing first.")
        rent = housing.hud_estimated_rent_monthly

        return loans, take_home, rent, Decimal("0.00")

    def _expected_return_annual(self, risk_level: str) -> Decimal:
        # hackathon ETF avg assumptions
        return {
            "low": Decimal("0.05"),
            "moderate": Decimal("0.07"),
            "high": Decimal("0.09"),
        }[risk_level]

    def _invest_split(self, risk_level: str) -> Decimal:
        # portion of EXTRA that goes to investing
        return {
            "low": Decimal("0.20"),
            "moderate": Decimal("0.50"),
            "high": Decimal("0.80"),
        }[risk_level]

    def _order_loans(self, loans: list[LoanSim], strategy: str) -> list[int]:
        idx = list(range(len(loans)))
        if strategy == "avalanche":
            idx.sort(key=lambda i: loans[i].apr_pct, reverse=True)
        elif strategy == "snowball":
            idx.sort(key=lambda i: loans[i].balance)
        else:  # hybrid
            # weighted: apr + balance normalization-ish
            idx.sort(key=lambda i: (loans[i].apr_pct * Decimal("0.7") + loans[i].balance / Decimal("10000") * Decimal("0.3")), reverse=True)
        return idx

    def _simulate(
        self,
        loans: list[LoanSim],
        monthly_commitment: Decimal,
        investing_enabled: bool,
        risk_level: str,
        strategy: str,
        start: date,
        max_months: int = 600,
    ) -> tuple[date, int, Decimal, Decimal, list[SeriesPoint], Decimal]:
        # Make local mutable copies
        balances = [l.balance for l in loans]
        mins = [l.min_payment for l in loans]
        apr = [l.apr_pct for l in loans]

        total_start = sum(balances, Decimal("0.00"))
        order = self._order_loans(loans, strategy)

        invest_bal = Decimal("0.00")
        invest_monthly_rate = self._expected_return_annual(risk_level) / Decimal("12")
        invest_share = self._invest_split(risk_level) if investing_enabled else Decimal("0.0")

        total_interest_paid = Decimal("0.00")
        series: list[SeriesPoint] = []

        def add_months(d: date, n: int) -> date:
            # small hack: approximate month addition by stepping month/year manually
            y = d.year
            m = d.month + n
            y += (m - 1) // 12
            m = (m - 1) % 12 + 1
            return date(y, m, 1)

        for m in range(max_months + 1):
            remaining = sum((b for b in balances if b > 0), Decimal("0.00"))
            paid_pct = Decimal("0.00") if total_start == 0 else (Decimal("1.00") - (remaining / total_start))
            series.append(
                SeriesPoint(
                    month_index=m,
                    date=add_months(start, m),
                    remaining_loan_balance=remaining.quantize(Decimal("0.01")),
                    paid_pct=(paid_pct * Decimal("100")).quantize(Decimal("0.01")),
                    investment_balance=invest_bal.quantize(Decimal("0.01")),
                )
            )
            if remaining <= Decimal("0.005"):
                freedom = add_months(start, m)
                return freedom, m, total_interest_paid.quantize(Decimal("0.01")), invest_bal.quantize(Decimal("0.01")), series, total_start.quantize(Decimal("0.01"))

            # 1) apply monthly interest to loans
            for i in range(len(balances)):
                if balances[i] <= 0:
                    continue
                monthly_rate = (apr[i] / Decimal("100")) / Decimal("12")
                interest = (balances[i] * monthly_rate)
                balances[i] += interest
                total_interest_paid += interest

            # 2) minimum payments first
            min_total = sum((mins[i] for i in range(len(mins)) if balances[i] > 0), Decimal("0.00"))
            pay_pool = monthly_commitment

            # clamp: can't pay less than mins if they exist
            if pay_pool < min_total:
                pay_pool = min_total

            # apply mins
            for i in range(len(balances)):
                if balances[i] <= 0:
                    continue
                p = mins[i]
                if p <= 0:
                    continue
                applied = min(p, balances[i], pay_pool)
                balances[i] -= applied
                pay_pool -= applied

            # 3) extra above mins gets split between investing + extra loan pay
            extra = max(Decimal("0.00"), pay_pool)

            invest_amt = (extra * invest_share).quantize(Decimal("0.01"))
            extra_to_loans = (extra - invest_amt).quantize(Decimal("0.01"))

            # investment grows then receives contribution
            if investing_enabled and invest_amt > 0:
                invest_bal = (invest_bal * (Decimal("1.00") + invest_monthly_rate)) + invest_amt

            # 4) apply extra_to_loans using strategy order
            for i in order:
                if extra_to_loans <= 0:
                    break
                if balances[i] <= 0:
                    continue
                applied = min(extra_to_loans, balances[i])
                balances[i] -= applied
                extra_to_loans -= applied

        # If never paid off within max_months
        freedom = add_months(start, max_months)
        return freedom, max_months, total_interest_paid.quantize(Decimal("0.01")), invest_bal.quantize(Decimal("0.01")), series, total_start.quantize(Decimal("0.01"))

    def _find_commitment_for_target(
        self,
        loans: list[LoanSim],
        min_commitment: Decimal,
        max_commitment: Decimal,
        investing_enabled: bool,
        risk_level: str,
        strategy: str,
        start: date,
        target: date,
    ) -> tuple[Decimal, list[str]]:
        warnings: list[str] = []
        if max_commitment < min_commitment:
            warnings.append("Income/expenses do not cover minimum payments.")
            return min_commitment, warnings

        # Binary search for lowest commitment that reaches target date or earlier
        lo = min_commitment
        hi = max_commitment
        best = hi

        # Convert target -> month horizon
        target_months = (target.year - start.year) * 12 + (target.month - start.month)
        if target_months < 0:
            warnings.append("Target date is in the past. Using minimum commitment.")
            return min_commitment, warnings

        for _ in range(18):
            mid = (lo + hi) / Decimal("2")
            freedom, months, *_ = self._simulate(
                loans=loans,
                monthly_commitment=mid,
                investing_enabled=investing_enabled,
                risk_level=risk_level,
                strategy=strategy,
                start=start,
                max_months=600,
            )
            if months <= target_months:
                best = mid
                hi = mid
            else:
                lo = mid

        # check feasibility at max
        freedom_max, months_max, *_ = self._simulate(
            loans=loans,
            monthly_commitment=max_commitment,
            investing_enabled=investing_enabled,
            risk_level=risk_level,
            strategy=strategy,
            start=start,
            max_months=600,
        )
        if months_max > target_months:
            warnings.append("Target date is not feasible with your current income/expenses. Showing closest possible plan.")

        return best.quantize(Decimal("0.01")), warnings
    
    def calculate(self, user_id: UUID, req: PlanCalculateRequest) -> PlanCalculateResponse:
        loans, take_home, rent, _ = self._load_state(user_id)

        essentials = req.budget_inputs.monthly_non_housing_essentials

        # slider max = discretionary before loans
        discretionary_before_loans = max(Decimal("0.00"), (take_home - rent - essentials))

        # slider min = total minimum loan payments
        min_payments = sum((l.min_payment for l in loans if l.balance > 0), Decimal("0.00"))
        min_commitment = min_payments
        max_commitment = discretionary_before_loans

        warnings: list[str] = []
        if max_commitment < min_commitment:
            warnings.append("Your income after essentials does not cover minimum loan payments.")

        # clamp commitment into [min_commitment, max_commitment] if feasible; else keep at min
        commitment = req.budget_inputs.monthly_commitment
        if max_commitment >= min_commitment:
            commitment = max(min_commitment, min(commitment, max_commitment))
        else:
            commitment = min_commitment

        extra_above_min = max(Decimal("0.00"), commitment - min_payments)
        discretionary_left = max(Decimal("0.00"), discretionary_before_loans - commitment)

        start = date.today().replace(day=1)

        freedom_date, months_to_freedom, total_interest, invest_at_freedom, series, total_start_debt = self._simulate(
            loans=loans,
            monthly_commitment=commitment,
            investing_enabled=req.investing_enabled,
            risk_level=req.risk_level,
            strategy=req.repayment_strategy,
            start=start,
        )

        expected_return = self._expected_return_annual(req.risk_level)
        invest_share = self._invest_split(req.risk_level) if req.investing_enabled else Decimal("0.0")
        monthly_investment = (extra_above_min * invest_share).quantize(Decimal("0.01")) if req.investing_enabled else Decimal("0.00")

        return PlanCalculateResponse(
            freedom_date=freedom_date,
            months_to_freedom=months_to_freedom,
            limits=LimitsOut(
                min_commitment=min_commitment.quantize(Decimal("0.01")),
                max_commitment=max_commitment.quantize(Decimal("0.01")),
            ),
            cashflow=CashflowOut(
                take_home_monthly=take_home.quantize(Decimal("0.01")),
                rent_monthly=rent.quantize(Decimal("0.01")),
                non_rent_essentials=essentials.quantize(Decimal("0.01")),
                discretionary_before_loans=discretionary_before_loans.quantize(Decimal("0.01")),
                minimum_loan_payments=min_payments.quantize(Decimal("0.01")),
                monthly_commitment=commitment.quantize(Decimal("0.01")),
                extra_above_minimum=extra_above_min.quantize(Decimal("0.01")),
                discretionary_left=discretionary_left.quantize(Decimal("0.01")),
            ),
            total_starting_debt=total_start_debt,
            total_interest_paid=total_interest,
            investing=InvestingOut(
                enabled=req.investing_enabled,
                risk_level=req.risk_level,
                expected_return_annual=expected_return,
                monthly_investment=monthly_investment,
                projected_investment_value_at_freedom=invest_at_freedom,
            ),
            series=series,
            warnings=warnings,
        )