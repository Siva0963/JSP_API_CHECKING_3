from fastapi import Security, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()


def verify_token(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Security(security)
):

    token = credentials.credentials

    if token != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Token")

    print("API HIT FROM IP:", request.client.host)

    return token