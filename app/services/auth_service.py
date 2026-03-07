from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.schemas.auth_schema import LoginRequest, VerifyOTPRequest
from app.repositories import auth_repo
from app.utils.otp_utils import generate_otp
from app.utils.jwt_utils import create_access_token
from app.utils.email_utils import send_otp_email
from app.utils.pytz_utils import get_ist_time


OTP_EXPIRY_MINUTES = 5


# =====================================================
# SEND LOGIN OTP
# =====================================================

async def send_login_otp(data: LoginRequest, db: AsyncSession):

    identifier = data.mobile_or_email

    member = await auth_repo.get_member_by_identifier(db, identifier)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    current_time = get_ist_time()

    # Delete expired OTPs from DB
    await auth_repo.delete_expired_otps(db, current_time)

    # Delete previous OTP of this member (only 1 OTP allowed)
    await auth_repo.delete_member_otps(db, member.id)

    # Generate OTP
    otp_code = generate_otp()

    expires_at = current_time + timedelta(minutes=OTP_EXPIRY_MINUTES)

    # Save OTP
    await auth_repo.create_otp(
        db,
        member.id,
        otp_code,
        expires_at
    )

    # Send OTP email if login using email
    if "@" in identifier:
        send_otp_email(identifier, otp_code)

    return {
        "message": "OTP sent successfully"
    }


# =====================================================
# VERIFY OTP
# =====================================================

async def verify_login_otp(data: VerifyOTPRequest, db: AsyncSession):

    identifier = data.mobile_or_email
    otp = data.otp

    member = await auth_repo.get_member_by_identifier(db, identifier)

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    current_time = get_ist_time()

    otp_obj = await auth_repo.get_valid_otp(
        db,
        member.id,
        otp,
        current_time
    )

    if not otp_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )

    # OTP verified → delete it
    await auth_repo.delete_otp(db, otp_obj)

    # Generate JWT token
    token = create_access_token(
        {"member_id": member.id}
    )

    member_data = {
        "id": member.id,
        "full_name": member.full_name,
        "mobile": member.mobile,
        "email": member.email,
        "address": member.address,
        "is_active": member.is_active,
        "kriya_id": member.kriya_id,
        "state_id": member.state_id,
        "district_id": member.district_id,
        "constituency_id": member.constituency_id,
        "mandal_id": member.mandal_id,
        "panchayat_id": member.panchayat_id,
        "ward_id": member.ward_id
    }

    return {
        "access_token": token,
        "token_type": "bearer",
        "member": member_data
    }