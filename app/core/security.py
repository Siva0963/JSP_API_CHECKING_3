from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):

    token = credentials.credentials

    if token != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Token")

    return token