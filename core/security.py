from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.auth_service import AuthService

bearer = HTTPBearer()

def get_current_account(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    auth: AuthService = Depends(),
):
    token = creds.credentials
    account_id = auth.decode_token_subject(token)
    entity = auth.get_account_entity_by_id(account_id)
    return entity.to_response_model()