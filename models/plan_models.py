from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


RepaymentStrategy = Literal["avalanche", "snowball", "hybrid"]
RiskLevel = Literal["low", "moderate", "high"]
BudgetSource = Literal["slider", "plaid", "csv"]


class BudgetInputs(BaseModel):
    monthly_non_housing_essentials: Decimal = Field(ge=0)
    monthly_commitment: Decimal = Field(ge=0)
    source: BudgetSource = "slider"


class PlanCalculateRequest(BaseModel):
    repayment_strategy: RepaymentStrategy = "avalanche"
    risk_level: RiskLevel = "moderate"
    investing_enabled: bool = True
    budget_inputs: BudgetInputs


class LimitsOut(BaseModel):
    min_commitment: Decimal
    max_commitment: Decimal


class CashflowOut(BaseModel):
    take_home_monthly: Decimal
    rent_monthly: Decimal
    non_rent_essentials: Decimal

    discretionary_before_loans: Decimal
    minimum_loan_payments: Decimal

    monthly_commitment: Decimal
    extra_above_minimum: Decimal
    discretionary_left: Decimal


class InvestingOut(BaseModel):
    enabled: bool
    risk_level: RiskLevel
    expected_return_annual: Decimal
    monthly_investment: Decimal
    projected_investment_value_at_freedom: Decimal


class SeriesPoint(BaseModel):
    month_index: int
    date: date
    remaining_loan_balance: Decimal
    paid_pct: Decimal
    investment_balance: Decimal


class PlanCalculateResponse(BaseModel):
    freedom_date: date
    months_to_freedom: int

    limits: LimitsOut
    cashflow: CashflowOut

    total_starting_debt: Decimal
    total_interest_paid: Decimal

    investing: InvestingOut
    series: list[SeriesPoint]

    warnings: list[str] = []