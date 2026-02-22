from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.loan_summary_models import LoanSummaryOut
from services.loan_summary_service import LoanSummaryService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("/summary", response_model=LoanSummaryOut)
def get_loan_summary(
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return LoanSummaryService(session).get_summary(current.id)