from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import time

import httpx
from fastapi import HTTPException

from core.config import settings


@dataclass
class HudRentResult:
    rent: float
    metro_name: str | None = None
    entity_id: str | None = None


class HudService:
    """
    HUD FMR:
      - listMetroAreas -> find entity id
      - data/{entityid} -> get rent by bedroom size
    Cache metro list in memory for hackathon simplicity.
    """

    _metro_cache: dict[str, Any] | None = None
    _metro_cache_ts: float | None = None

    BASE = "https://www.huduser.gov/hudapi/public/fmr"

    def __init__(self):
        self._token = settings.HUD_API_TOKEN

    def _headers(self) -> dict[str, str]:
        if not self._token:
            # You can still run without HUD token by returning placeholder rent
            return {}
        return {"Authorization": f"Bearer {self._token}"}

    async def _get_metros(self) -> list[dict[str, Any]]:
        now = time.time()
        if self._metro_cache and self._metro_cache_ts and (now - self._metro_cache_ts) < 86400:
            return self._metro_cache["metros"]

        url = f"{self.BASE}/listMetroAreas"
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, headers=self._headers())
            if r.status_code != 200:
                raise HTTPException(status_code=502, detail="HUD metro lookup failed.")
            data = r.json()

        if isinstance(data, list):
            metros = data
        else:
            metros = data.get("data", []) if isinstance(data, dict) else []
        self._metro_cache = {"metros": metros}
        self._metro_cache_ts = now
        return metros

    @staticmethod
    def _score(a: str, b: str) -> float:
        a = a.lower().strip()
        b = b.lower().strip()
        if a == b:
            return 1.0
        # super simple similarity
        overlap = sum(1 for ch in a if ch in b) / max(1, len(a))
        return overlap

    async def resolve_entity_id(self, city: str, state: str) -> tuple[str | None, str | None]:
        if not self._token:
            return None, None

        metros = await self._get_metros()
        target = f"{city}, {state}".lower()

        best = None
        best_score = 0.0
        for m in metros:
            name = (m.get("metro_name") or "").lower()
            sc = self._score(target, name)
            if sc > best_score:
                best_score = sc
                best = m

        if not best:
            return None, None

        return best.get("metro_code"), best.get("metro_name")

    async def get_fmr_rent(self, city: str, state: str, bedroom_count: int, year: int | None = None) -> HudRentResult:
        # No token? return placeholder rent for demo
        if not self._token:
            return HudRentResult(rent=1800.0, metro_name="(HUD disabled)", entity_id=None)

        entity_id, metro_name = await self.resolve_entity_id(city, state)
        if not entity_id:
            return HudRentResult(rent=1800.0, metro_name="(metro not found)", entity_id=None)

        url = f"{self.BASE}/data/{entity_id}"
        params = {}
        if year:
            params["year"] = year

        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, headers=self._headers(), params=params)
            if r.status_code != 200:
                raise HTTPException(status_code=502, detail="HUD rent lookup failed.")
            data = r.json()

        # HUD returns keys like "Zero-Bedroom", "One-Bedroom", etc.
        key_map = {
            0: "Zero-Bedroom",
            1: "One-Bedroom",
            2: "Two-Bedroom",
            3: "Three-Bedroom",
            4: "Four-Bedroom",
        }
        bed_key = key_map.get(bedroom_count, "One-Bedroom")

        rent_val = None
        try:
            rent_val = data["data"]["basicdata"][bed_key]
        except Exception:
            rent_val = None

        rent = float(rent_val) if rent_val is not None else 1800.0
        return HudRentResult(rent=rent, metro_name=metro_name, entity_id=entity_id)