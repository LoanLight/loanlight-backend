from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.limits_models import PlanLimitsResponse
from services.limits_service import LimitsService

router = APIRouter(prefix="/plan", tags=["plan"])


@router.get("/limits", response_model=PlanLimitsResponse)
def plan_limits(
    monthly_non_housing_essentials: Decimal = Query(..., ge=0),
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return LimitsService(session).get_limits(current.id, monthly_non_housing_essentials)