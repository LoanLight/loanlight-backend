from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from entities.housing_profile_entity import HousingProfileEntity
from models.housing_models import HousingIn, HousingOut
from services.hud_service import HudService


class HousingService:
    def __init__(self, session: Session):
        self._session = session

    async def upsert(self, user_id: UUID, payload: HousingIn) -> HousingOut:
        q = select(HousingProfileEntity).where(HousingProfileEntity.user_id == user_id)
        row = self._session.scalars(q).one_or_none()

        hud = HudService()
        rent_result = await hud.get_fmr_rent(payload.city, payload.state, payload.bedroom_count)

        rent_dec = Decimal(str(rent_result.rent)).quantize(Decimal("0.01"))

        if row is None:
            row = HousingProfileEntity(
                user_id=user_id,
                city=payload.city,
                state=payload.state.upper(),
                bedroom_count=payload.bedroom_count,
                housing_type=payload.housing_type,
                hud_estimated_rent_monthly=rent_dec,
            )
            self._session.add(row)
        else:
            row.city = payload.city
            row.state = payload.state.upper()
            row.bedroom_count = payload.bedroom_count
            row.housing_type = payload.housing_type
            row.hud_estimated_rent_monthly = rent_dec

        self._session.commit()
        self._session.refresh(row)

        return HousingOut(
            id=row.id,
            city=row.city,
            state=row.state,
            bedroom_count=row.bedroom_count,
            housing_type=row.housing_type,
            hud_estimated_rent_monthly=row.hud_estimated_rent_monthly,
        )

    def get_or_404(self, user_id: UUID) -> HousingOut:
        q = select(HousingProfileEntity).where(HousingProfileEntity.user_id == user_id)
        row = self._session.scalars(q).one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="Housing profile not found.")

        return HousingOut(
            id=row.id,
            city=row.city,
            state=row.state,
            bedroom_count=row.bedroom_count,
            housing_type=row.housing_type,
            hud_estimated_rent_monthly=row.hud_estimated_rent_monthly,
        )