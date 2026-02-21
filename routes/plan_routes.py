from fastapi import APIRouter, Depends
from core.security import get_current_account
from models.plan_models import PlanCompareRequest, PlanCompareResponse
from datetime import date

router = APIRouter(prefix="/plans", tags=["plans"])

@router.post("/compare", response_model=PlanCompareResponse)
def compare(payload: PlanCompareRequest, current = Depends(get_current_account)):
    # TODO: RepaymentPlanService + InvestmentProjectionService + OfferAnalysisService + HudService
    # Returning dummy shape so iOS can build UI immediately.
    today = date.today()
    return PlanCompareResponse(
        freedom_date=today,
        feasible=True,
        required_monthly_payment=0.0,
        shortfall_monthly=0.0,
        earliest_possible_payoff=today,
        minimum_only_payoff=today,
        monthly_breakdown={
            "take_home": 0,
            "rent": 0,
            "essentials": payload.monthly_essentials,
            "min_loan": 0,
            "extra_loan": 0,
            "invest": 0
        },
        series_preview=[],
        assumptions={"risk_level": payload.risk_level, "strategy": payload.strategy}
    )