from sqlalchemy import select, or_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Member, OTP


# ==========================================
# GET MEMBER BY MOBILE OR EMAIL
# ==========================================

async def get_member_by_identifier(db: AsyncSession, identifier: str):

    result = await db.execute(
        select(Member).where(
            or_(
                Member.mobile == identifier,
                Member.email == identifier
            )
        )
    )

    return result.scalars().first()


# ==========================================
# CREATE OTP
# ==========================================

async def create_otp(db: AsyncSession, member_id: int, otp: str, expires_at):

    otp_obj = OTP(
        member_id=member_id,
        otp_code=otp,
        expires_at=expires_at
    )

    db.add(otp_obj)

    await db.commit()
    await db.refresh(otp_obj)

    return otp_obj


# ==========================================
# GET VALID OTP (CHECK NOT EXPIRED)
# ==========================================

async def get_valid_otp(db: AsyncSession, member_id: int, otp: str, current_time):

    result = await db.execute(
        select(OTP).where(
            OTP.member_id == member_id,
            OTP.otp_code == otp,
            OTP.expires_at > current_time
        )
    )

    return result.scalars().first()


# ==========================================
# DELETE OTP AFTER SUCCESSFUL VERIFICATION
# ==========================================

async def delete_otp(db: AsyncSession, otp_obj: OTP):

    await db.delete(otp_obj)
    await db.commit()


# ==========================================
# DELETE EXPIRED OTPS
# ==========================================

async def delete_expired_otps(db: AsyncSession, member_id: int, current_time):

    await db.execute(
        delete(OTP).where(
            OTP.member_id == member_id,
            OTP.expires_at < current_time
        )
    )

    await db.commit()