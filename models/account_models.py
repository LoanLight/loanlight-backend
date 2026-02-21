from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class AccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime