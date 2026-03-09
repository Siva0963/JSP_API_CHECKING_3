from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta

from app.schemas.auth_schema import LoginRequest, VerifyOTPRequest
from app.repositories import auth_repo
from app.utils.otp_utils import generate_otp
from app.utils.jwt_utils import create_access_token
from app.utils.email_utils import send_otp_email
from app.utils.fast2sms_service11 import SMSService
from app.utils.pytz_utils import get_ist_time
from app.core.logger import logger


OTP_EXPIRY_MINUTES = 5


# =====================================================
# SEND LOGIN OTP
# =====================================================

async def send_login_otp(data: LoginRequest, db: AsyncSession):

    identifier = data.mobile_or_email.strip()

    try:
        # -------------------------------------------------
        # FIND MEMBER
        # -------------------------------------------------
        member = await auth_repo.get_member_by_identifier(db, identifier)

        if not member:
            logger.warning(f"Login attempt failed. Member not found: {identifier}")

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        current_time = get_ist_time()

        # -------------------------------------------------
        # CLEAN OLD OTPs
        # -------------------------------------------------
        await auth_repo.delete_expired_otps(db, current_time)
        await auth_repo.delete_member_otps(db, member.id)

        # -------------------------------------------------
        # GENERATE OTP
        # -------------------------------------------------
        otp_code = generate_otp()
        expires_at = current_time + timedelta(minutes=OTP_EXPIRY_MINUTES)

        await auth_repo.create_otp(
            db=db,
            member_id=member.id,
            otp=otp_code,
            expires_at=expires_at
        )

        # -------------------------------------------------
        # SEND OTP
        # -------------------------------------------------
        if "@" in identifier:

            await send_otp_email(identifier, otp_code)

            logger.info(f"OTP email sent to {identifier}")

        else:
            mobile_number = format_mobile_number(identifier)

            await SMSService.send_otp(mobile_number, otp_code)

            logger.info(f"OTP SMS sent to {mobile_number}")

        return {
            "success": True,
            "message": "OTP sent successfully"
        }

    # -------------------------------------------------
    # ERROR HANDLING
    # -------------------------------------------------

    except HTTPException:
        raise

    except SQLAlchemyError as db_error:
        await db.rollback()

        logger.error(f"Database error while sending OTP: {str(db_error)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while processing request"
        )

    except Exception as e:
        logger.exception(f"Unexpected error sending OTP: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# =====================================================
# VERIFY LOGIN OTP
# =====================================================

async def verify_login_otp(data: VerifyOTPRequest, db: AsyncSession):

    identifier = data.mobile_or_email.strip()
    otp = data.otp.strip()

    try:
        # -------------------------------------------------
        # FIND MEMBER
        # -------------------------------------------------
        member = await auth_repo.get_member_by_identifier(db, identifier)

        if not member:
            logger.warning(f"OTP verification failed. Member not found: {identifier}")

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        current_time = get_ist_time()

        # -------------------------------------------------
        # VALIDATE OTP
        # -------------------------------------------------
        otp_obj = await auth_repo.get_valid_otp(
            db=db,
            member_id=member.id,
            otp=otp,
            current_time=current_time
        )

        if not otp_obj:
            logger.warning(f"Invalid OTP attempt for member_id={member.id}")

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )

        # -------------------------------------------------
        # DELETE OTP AFTER SUCCESS
        # -------------------------------------------------
        await auth_repo.delete_otp(db, otp_obj)

        # -------------------------------------------------
        # GENERATE ACCESS TOKEN
        # -------------------------------------------------
        token_payload = {
            "member_id": member.id,
            "kriya_id": member.kriya_id,
            "full_name": member.full_name,
            "state_id": member.state_id,
            "district_id": member.district_id,
            "constituency_id": member.constituency_id,
            "mandal_id": member.mandal_id,
            "panchayat_id": member.panchayat_id,
            "ward_id": member.ward_id
        }

        token = create_access_token(token_payload)

        logger.info(f"Member login successful: member_id={member.id}")

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

    # -------------------------------------------------
    # ERROR HANDLING
    # -------------------------------------------------

    except HTTPException:
        raise

    except SQLAlchemyError as db_error:
        await db.rollback()

        logger.error(f"Database error verifying OTP: {str(db_error)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while verifying OTP"
        )

    except Exception as e:
        logger.exception(f"Unexpected error verifying OTP: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# =====================================================
# HELPER FUNCTION
# =====================================================

def format_mobile_number(number: str) -> str:
    """
    Convert mobile number to E.164 format required by SMS providers
    """

    number = number.strip()

    if number.startswith("+"):
        return number

    if number.startswith("91"):
        return f"+{number}"

    return f"+91{number}"