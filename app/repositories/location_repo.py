from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import (
    State,
    District,
    Constituency,
    Mandal,
    Panchayat,
    Ward
)


class LocationRepo:

    @staticmethod
    async def get_states(db: AsyncSession):

        result = await db.execute(select(State))
        return result.scalars().all()


    @staticmethod
    async def get_districts(db: AsyncSession, state_id: int):

        result = await db.execute(
            select(District).where(District.state_id == state_id)
        )
        return result.scalars().all()


    @staticmethod
    async def get_constituencies(db: AsyncSession, district_id: int):

        result = await db.execute(
            select(Constituency).where(Constituency.district_id == district_id)
        )
        return result.scalars().all()


    @staticmethod
    async def get_mandals(db: AsyncSession, constituency_id: int):

        result = await db.execute(
            select(Mandal).where(Mandal.constituency_id == constituency_id)
        )
        return result.scalars().all()


  

    @staticmethod
    async def get_panchayats(db: AsyncSession, mandal_id: int):

        result = await db.execute(
            select(Panchayat).where(Panchayat.mandal_id == mandal_id)
        )

        panchayats = result.scalars().all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "mandal_id": p.mandal_id,
                "area_category": p.area_category
            }
            for p in panchayats
        ]


    @staticmethod
    async def get_wards(db: AsyncSession, panchayat_id: int):

        result = await db.execute(
            select(Ward).where(Ward.panchayat_id == panchayat_id)
        )

        wards = result.scalars().all()

        return [
            {
                "id": w.id,
                "name": w.name,
                "panchayat_id": w.panchayat_id
            }
            for w in wards
        ]