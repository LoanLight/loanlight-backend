from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pwdlib import PasswordHash
import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.config import ACCESS_TOKEN_EXPIRY_DAYS, JWT_SECRET, JWT_ALGORITHM
from database.session import db_session
from entities.account_entity import AccountEntity
from models.account_models import AccountResponse


class AuthService:
    def __init__(self, session: Session = Depends(db_session)):
        self._session = session
        self.password_hash = PasswordHash.recommended()

    def hash_password(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)

    def create_access_token(self, subject: UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRY_DAYS)
        payload = {"sub": str(subject), "exp": expire}
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_token_subject(self, token: str) -> UUID:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(status_code=401, detail="Invalid or expired token.")
            return UUID(sub)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid or expired token.")

    def authenticate_user(self, email: str, password: str) -> AccountResponse:
        email_norm = email.strip().lower()
        query = select(AccountEntity).where(AccountEntity.email == email_norm)
        account = self._session.scalars(query).one_or_none()

        if not account or not self.verify_password(password, account.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        return account.to_response_model()

    def get_account_entity_by_id(self, account_id: UUID) -> AccountEntity:
        query = select(AccountEntity).where(AccountEntity.id == account_id)
        account = self._session.scalars(query).one_or_none()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found.")

        return account