from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta

from app.schemas.auth_schema import LoginRequest, VerifyOTPRequest
from app.repositories import auth_repo
from app.utils.otp_utils import generate_otp
from app.utils.jwt_utils import create_access_token
from app.utils.email_utils import send_otp_email
from app.utils.pytz_utils import get_ist_time
from app.core.logger import logger

OTP_EXPIRY_MINUTES = 5


# =====================================================
# SEND LOGIN OTP
# =====================================================

async def send_login_otp(data: LoginRequest, db: AsyncSession):

    identifier = data.mobile_or_email

    try:

        member = await auth_repo.get_member_by_identifier(db, identifier)

        if not member:
            logger.warning(f"Login attempt failed. Member not found: {identifier}")

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        current_time = get_ist_time()

        # delete expired OTPs
        await auth_repo.delete_expired_otps(db, current_time)

        # delete previous OTPs
        await auth_repo.delete_member_otps(db, member.id)

        otp_code = generate_otp()

        expires_at = current_time + timedelta(minutes=OTP_EXPIRY_MINUTES)

        await auth_repo.create_otp(
            db,
            member.id,
            otp_code,
            expires_at
        )

        # send email
        if "@" in identifier:
            try:
                send_otp_email(identifier, otp_code)
            except Exception as email_error:
                logger.error(
                    f"Failed to send OTP email to {identifier}: {str(email_error)}"
                )

        logger.info(f"OTP generated for member_id={member.id}")

        return {
            "message": "OTP sent successfully"
        }

    except HTTPException:
        raise

    except SQLAlchemyError as db_error:

        await db.rollback()

        logger.error(
            f"Database error while sending OTP for {identifier}: {str(db_error)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while processing request"
        )

    except ValueError as value_error:

        logger.error(
            f"Invalid data while sending OTP for {identifier}: {str(value_error)}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request data"
        )

    except Exception as e:

        logger.exception(
            f"Unexpected error while sending OTP for {identifier}: {str(e)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# =====================================================
# VERIFY OTP
# =====================================================

async def verify_login_otp(data: VerifyOTPRequest, db: AsyncSession):

    identifier = data.mobile_or_email
    otp = data.otp

    try:

        member = await auth_repo.get_member_by_identifier(db, identifier)

        if not member:

            logger.warning(
                f"OTP verification failed. Member not found: {identifier}"
            )

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

            logger.warning(
                f"Invalid OTP attempt for member_id={member.id}"
            )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )

        # delete OTP after verification
        await auth_repo.delete_otp(db, otp_obj)

        # =====================================================
        # CREATE ACCESS TOKEN
        # =====================================================

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

        try:
            token = create_access_token(token_payload)
        except Exception as token_error:

            logger.error(
                f"JWT creation failed for member_id={member.id}: {str(token_error)}"
            )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation failed"
            )

        logger.info(f"Member logged in successfully: member_id={member.id}")

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

    except HTTPException:
        raise

    except SQLAlchemyError as db_error:

        await db.rollback()

        logger.error(
            f"Database error during OTP verification for {identifier}: {str(db_error)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while verifying OTP"
        )

    except ValueError as value_error:

        logger.error(
            f"Invalid OTP input for {identifier}: {str(value_error)}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP format"
        )

    except Exception as e:

        logger.exception(
            f"Unexpected error verifying OTP for {identifier}: {str(e)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )