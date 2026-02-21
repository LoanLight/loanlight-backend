from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database.session import db_session
from entities.account_entity import AccountEntity
from services.auth_service import AuthService

bearer = HTTPBearer(auto_error=False)


def get_current_account(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    session: Session = Depends(db_session),
) -> AccountEntity:
    if creds is None or not creds.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token.")

    auth = AuthService(session=session)
    account_id: UUID = auth.decode_token_subject(creds.credentials)
    return auth.get_account_entity_by_id(account_id)