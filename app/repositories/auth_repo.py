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
# DELETE ALL OTPs OF MEMBER
# (Ensures only 1 OTP exists)
# ==========================================

async def delete_member_otps(db: AsyncSession, member_id: int):

    await db.execute(
        delete(OTP).where(
            OTP.member_id == member_id
        )
    )

    await db.commit()


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
# GET VALID OTP
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
# DELETE OTP AFTER VERIFICATION
# ==========================================

async def delete_otp(db: AsyncSession, otp_obj: OTP):

    await db.delete(otp_obj)
    await db.commit()


# ==========================================
# DELETE EXPIRED OTPs
# ==========================================

async def delete_expired_otps(db: AsyncSession, current_time):

    await db.execute(
        delete(OTP).where(
            OTP.expires_at < current_time
        )
    )

    await db.commit()


from sqlalchemy import select, or_
from app.models.models import Member


async def get_member_by_identifier(db, identifier: str):

    identifier = identifier.strip()

    # Normalize mobile numbers
    mobile_plain = identifier.replace("+91", "")

    query = select(Member).where(
        or_(
            Member.email == identifier,
            Member.mobile == identifier,
            Member.mobile == mobile_plain
        )
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()