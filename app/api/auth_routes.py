from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth_schema import LoginRequest, VerifyOTPRequest
from app.services.auth_service import send_login_otp_service, verify_otp_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/send-otp")
async def send_otp(request: LoginRequest, db: Session = Depends(get_db)):
    return await send_login_otp_service(db, request.mobile_or_email)


@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    return await verify_otp_service(db, request.mobile_or_email, request.otp)