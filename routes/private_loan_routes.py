from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.private_loan_models import PrivateLoanBulkIn, PrivateLoanBulkOut
from services.private_loan_service import PrivateLoanService

router = APIRouter(prefix="/private-loans", tags=["private_loans"])


@router.post("/bulk", response_model=PrivateLoanBulkOut)
def replace_all_private_loans(
    payload: PrivateLoanBulkIn,
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return PrivateLoanService(session).replace_all(current.id, payload.loans)


@router.get("", response_model=PrivateLoanBulkOut)
def list_private_loans(
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return PrivateLoanService(session).list(current.id)