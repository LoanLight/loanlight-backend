from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.plan_models import PlanCalculateRequest, PlanCalculateResponse
from services.plan_service import PlanService

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post("/calculate", response_model=PlanCalculateResponse)
def calculate_plan(
    payload: PlanCalculateRequest,
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return PlanService(session).calculate(current.id, payload)