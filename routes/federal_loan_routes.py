from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.federal_loan_models import FederalLoanBulkIn, FederalLoanBulkOut
from services.federal_loan_service import FederalLoanService

router = APIRouter(prefix="/federal-loans", tags=["federal_loans"])


@router.post("/bulk", response_model=FederalLoanBulkOut)
def replace_all_federal_loans(
    payload: FederalLoanBulkIn,
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return FederalLoanService(session).replace_all(current.id, payload.loans)


@router.get("", response_model=FederalLoanBulkOut)
def list_federal_loans(
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return FederalLoanService(session).list(current.id)