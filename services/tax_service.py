from __future__ import annotations

from decimal import Decimal
import httpx
from fastapi import HTTPException

from core.config import settings


class TaxService:
    """
    Free-tier compatible tax calculator.
    Uses API Ninjas only for federal tax.
    Computes FICA + state locally.
    """
    # https://www.irs.gov/newsroom/irs-provides-tax-inflation-adjustments-for-tax-year-2024


    BASE_URL = "https://api.api-ninjas.com/v1/incometaxcalculator"

    async def estimate_take_home_monthly(
        self,
        *,
        salary_annual: Decimal,
        state: str,
        filing_status: str = "single",
    ) -> tuple[Decimal, dict]:

        if not settings.API_NINJAS_KEY:
            raise HTTPException(status_code=500, detail="API_NINJAS_KEY not configured")

        params = {
            "country": "US",
            "region": state.upper(),
            "income": float(salary_annual),
            "filing_status": filing_status,
        }

        headers = {"X-Api-Key": settings.API_NINJAS_KEY}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.BASE_URL, params=params, headers=headers)
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Tax API error: {repr(e)}")

        federal = data.get("federal_taxes_owed")

        if federal is None:
            raise HTTPException(status_code=502, detail="Missing federal_taxes_owed")

        # Convert safely
        federal_dec = Decimal(str(federal))
        gross_dec = Decimal(str(salary_annual))

        # ----------------------
        # Compute FICA locally
        # ----------------------
        ss_rate = Decimal("0.062")
        ss_cap = Decimal("168600")  # 2024 wage base
        medicare_rate = Decimal("0.0145")

        social_security = min(gross_dec, ss_cap) * ss_rate
        medicare = gross_dec * medicare_rate
        fica_total = social_security + medicare

        st = state.upper()

        no_tax_states = {"TX", "FL", "WA", "NV", "TN", "SD", "WY", "AK", "NH"}

        state_effective = {
            "CA": Decimal("0.06"),
            "NY": Decimal("0.06"),
            "NJ": Decimal("0.05"),
            "MA": Decimal("0.05"),
            "NC": Decimal("0.045"),
            "IL": Decimal("0.0495"),
            "PA": Decimal("0.0307"),
        }

        if st in no_tax_states:
            state_tax = Decimal("0.00")
        else:
            state_tax = gross_dec * state_effective.get(st, Decimal("0.04"))
            
        net_annual = gross_dec - federal_dec - fica_total - state_tax
        monthly = (net_annual / Decimal("12")).quantize(Decimal("0.01"))

        breakdown = {
            "gross_income": gross_dec,
            "federal_tax": federal_dec,
            "fica_total": fica_total.quantize(Decimal("0.01")),
            "state_tax": state_tax.quantize(Decimal("0.01")),
            "net_annual": net_annual.quantize(Decimal("0.01")),
        }

        return monthly, breakdown