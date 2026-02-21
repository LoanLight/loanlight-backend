from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from entities.entity_base import EntityBase
from models.account_models import AccountResponse


class AccountEntity(EntityBase):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def to_response_model(self) -> AccountResponse:
        return AccountResponse(
            id=self.id,
            email=self.email,
            created_at=self.created_at,
        )