from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.job_offer_models import JobOfferIn, JobOfferOut
from services.job_offer_service import JobOfferService

router = APIRouter(prefix="/job-offer", tags=["job-offer"])


@router.post("", response_model=JobOfferOut)
async def upsert_job_offer(
    payload: JobOfferIn,
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return await JobOfferService(session).upsert(current.id, payload)


@router.get("/current", response_model=JobOfferOut)
def get_job_offer(
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return JobOfferService(session).get_or_404(current.id)