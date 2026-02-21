from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from pwdlib import PasswordHash
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import settings
from entities.account_entity import AccountEntity
from models.account_models import TokenResponse


class AuthService:
    def __init__(self, session: Session):
        self._session = session
        self.password_hash = PasswordHash.recommended()

    def hash_password(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)

    def create_access_token(self, subject: UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRY_DAYS)
        payload = {"sub": str(subject), "exp": expire}
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def decode_token_subject(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            sub = payload.get("sub")
            if not sub:
                raise ValueError("missing sub")
            return UUID(sub)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token.")

    def get_account_entity_by_id(self, account_id: UUID) -> AccountEntity:
        q = select(AccountEntity).where(AccountEntity.id == account_id)
        account = self._session.scalars(q).one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")
        return account

    def signup(self, email: str, password: str) -> TokenResponse:
        email = email.lower().strip()
        q = select(AccountEntity).where(AccountEntity.email == email)
        if self._session.scalars(q).one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered.")

        account = AccountEntity(email=email, hashed_password=self.hash_password(password))
        self._session.add(account)
        self._session.commit()
        self._session.refresh(account)
        return TokenResponse(access_token=self.create_access_token(account.id))

    def login(self, email: str, password: str) -> TokenResponse:
        email = email.lower().strip()
        q = select(AccountEntity).where(AccountEntity.email == email)
        account = self._session.scalars(q).one_or_none()
        if not account or not self.verify_password(password, account.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
        return TokenResponse(access_token=self.create_access_token(account.id))