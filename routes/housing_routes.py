from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from deps.auth_deps import get_current_account
from models.housing_models import HousingIn, HousingOut
from services.housing_service import HousingService

router = APIRouter(prefix="/housing", tags=["housing"])


@router.post("", response_model=HousingOut)
async def upsert_housing(
    payload: HousingIn,
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return await HousingService(session).upsert(current.id, payload)


@router.get("/current", response_model=HousingOut)
def get_housing(
    session: Session = Depends(db_session),
    current=Depends(get_current_account),
):
    return HousingService(session).get_or_404(current.id)