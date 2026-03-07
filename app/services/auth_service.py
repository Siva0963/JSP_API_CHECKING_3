from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.auth_repo import (
    get_member_by_identifier,
    create_otp,
    get_valid_otp,
    delete_otp,
    delete_expired_otps
)

from app.utils.otp_utils import generate_otp
from app.utils.jwt_utils import create_access_token
from app.utils.pytz_utils import get_ist_time


# =========================================================
# SEND OTP SERVICE
# =========================================================

async def send_login_otp_service(db: AsyncSession, mobile_or_email: str):

    if not mobile_or_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number or email is required"
        )

    try:

        current_time = get_ist_time()

        # Fetch member
        member = await get_member_by_identifier(db, mobile_or_email)

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        if not member.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Member account is inactive"
            )

        # Remove expired OTPs (single DB call)
        await delete_expired_otps(db, member.id, current_time)

        # Generate OTP
        otp = generate_otp()
        expires_at = current_time + timedelta(minutes=5)

        # Store OTP
        await create_otp(db, member.id, otp, expires_at)

        # Send OTP (Replace with SMS/Email service later)
        if member.mobile == mobile_or_email:
            print(f"OTP {otp} sent to mobile {member.mobile}")
        else:
            print(f"OTP {otp} sent to email {member.email}")

        return {"message": "OTP sent successfully"}

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while generating OTP"
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error"
        )


# =========================================================
# VERIFY OTP SERVICE
# =========================================================

async def verify_otp_service(db: AsyncSession, mobile_or_email: str, otp: str):

    if not mobile_or_email or not otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile/email and OTP are required"
        )

    try:

        current_time = get_ist_time()

        # Fetch member
        member = await get_member_by_identifier(db, mobile_or_email)

        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        if not member.is_active:
            raise HTTPException(status_code=403, detail="Member account is inactive")

        # Fetch OTP
        otp_obj = await get_valid_otp(db, member.id, otp)

        if not otp_obj:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # Check expiry
        if otp_obj.expires_at < current_time:
            await delete_otp(db, otp_obj)
            raise HTTPException(status_code=400, detail="OTP expired")

        # Delete OTP after success
        await delete_otp(db, otp_obj)

        # Create JWT token
        token = create_access_token({"member_id": member.id})

        return {
            "access_token": token,
            "token_type": "bearer",
            "member": {
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
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred while verifying OTP"
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected server error"
        )