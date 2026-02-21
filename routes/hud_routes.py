from fastapi import APIRouter, Depends
from core.security import get_current_account
from models.hud_models import HudRentRequest

router = APIRouter(prefix="/hud", tags=["hud"])

@router.post("/rent")
def rent(payload: HudRentRequest, current = Depends(get_current_account)):
    # TODO: HudService -> listMetroAreas + fuzzy match + fmr/data/entityid
    return {"message": "stub", "city": payload.city, "state": payload.state}