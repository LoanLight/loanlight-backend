from pydantic import BaseModel
from datetime import date

class PlanCompareRequest(BaseModel):
    mode: str = "optimize"  # optimize|target_date
    risk_level: str = "moderate"  # low|moderate|high
    strategy: str = "avalanche"  # avalanche|snowball|hybrid
    monthly_essentials: float = 900.0

    # used only if mode == target_date
    target_payoff_date: date | None = None

class PlanCompareResponse(BaseModel):
    freedom_date: date
    feasible: bool
    required_monthly_payment: float
    shortfall_monthly: float

    earliest_possible_payoff: date
    minimum_only_payoff: date

    monthly_breakdown: dict
    series_preview: list[dict]
    assumptions: dict