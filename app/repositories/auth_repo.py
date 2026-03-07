from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_

from app.models.models import Member, OTP


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


async def get_valid_otp(db: AsyncSession, member_id: int, otp: str):

    result = await db.execute(
        select(OTP).where(
            OTP.member_id == member_id,
            OTP.otp_code == otp,
            OTP.is_used == False
        )
    )

    return result.scalars().first()


async def mark_otp_used(db: AsyncSession, otp_obj: OTP):

    otp_obj.is_used = True
    await db.commit()

async def delete_otp(db, otp_obj):
    await db.delete(otp_obj)
    await db.commit()


async def delete_expired_otps(db, member_id, current_time):
    from sqlalchemy import delete

    await db.execute(
        delete(OTP).where(
            OTP.member_id == member_id,
            OTP.expires_at < current_time
        )
    )
    await db.commit()