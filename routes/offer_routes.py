from fastapi import APIRouter, Depends
from core.security import get_current_account
from models.offer_models import OfferUpsertRequest

router = APIRouter(prefix="/offers", tags=["offers"])

@router.post("/extract-text")
def extract_text(payload: dict, current = Depends(get_current_account)):
    # payload: {"text": "..."}
    # TODO: OfferExtractService
    return {"message": "stub", "extracted": {}}

@router.post("")
def upsert_offer(payload: OfferUpsertRequest, current = Depends(get_current_account)):
    # TODO: save OfferEntity for current user
    return {"message": "stub"}

@router.get("/current")
def get_offer(current = Depends(get_current_account)):
    return {"message": "stub", "offer": None}