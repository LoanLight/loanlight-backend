from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.session import db_session
from entities.account_entity import AccountEntity
from models.auth_models import SignupRequest, LoginRequest, TokenResponse
from services.auth_service import AuthService
from core.security import get_current_account

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(payload: SignupRequest, session: Session = Depends(db_session), auth: AuthService = Depends()):
    existing = session.scalars(select(AccountEntity).where(AccountEntity.email == payload.email.lower())).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    entity = AccountEntity(email=payload.email.lower(), hashed_password=auth.hash_password(payload.password))
    session.add(entity)
    session.commit()
    session.refresh(entity)

    token = auth.create_access_token(entity.id)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, auth: AuthService = Depends()):
    account = auth.authenticate_user(payload.email, payload.password)
    token = auth.create_access_token(account.id)
    return TokenResponse(access_token=token)

@router.get("/me")
def me(current_account = Depends(get_current_account)):
    return current_account