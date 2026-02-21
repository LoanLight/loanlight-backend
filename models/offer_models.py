from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from uuid import UUID

class OfferUpsertRequest(BaseModel):
    base_salary: Decimal
    signing_bonus: Decimal | None = None
    start_date: date | None = None
    retirement_match_pct: Decimal | None = None
    health_premium_monthly: Decimal | None = None
    location_city: str | None = None
    location_state: str | None = None

class OfferResponse(OfferUpsertRequest):
    id: UUID