from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import db_session
from models.account_models import SignupRequest, LoginRequest, TokenResponse, AccountResponse
from services.auth_service import AuthService
from deps.auth_deps import get_current_account

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, session: Session = Depends(db_session)):
    return AuthService(session=session).signup(payload.email, payload.password)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(db_session)):
    return AuthService(session=session).login(payload.email, payload.password)


@router.get("/me", response_model=AccountResponse)
def me(current=Depends(get_current_account)):
    return current.to_response_model()