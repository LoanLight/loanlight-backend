from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.overview_models import ProfileOverviewResponse, StateResponse, ProfileCompletionResponse
from services.overview_service import OverviewService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/overview", response_model=ProfileOverviewResponse)
def overview(session: Session = Depends(db_session), current=Depends(get_current_account)):
    return OverviewService(session).get_overview_or_404(current.id)


@router.get("/state", response_model=StateResponse)
def state(session: Session = Depends(db_session), current=Depends(get_current_account)):
    return OverviewService(session).get_state(current.id)


@router.get("/complete", response_model=ProfileCompletionResponse)
def complete(session: Session = Depends(db_session), current=Depends(get_current_account)):
    return OverviewService(session).get_completion(current.id)