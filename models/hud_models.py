from pydantic import BaseModel

class HudRentRequest(BaseModel):
    city: str
    state: str
    year: int | None = None

class HudRentResponse(BaseModel):
    metro_name: str
    entity_id: str
    one_bedroom_fmr: int
    year: int