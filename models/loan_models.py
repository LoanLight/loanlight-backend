from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

class LoanResponse(BaseModel):
    id: UUID
    loan_category: str
    loan_type: str
    interest_rate: Decimal
    principal_balance: Decimal
    status: str
    servicer_name: str | None