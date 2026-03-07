from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import verify_token
from app.repositories.location_repo import LocationRepo
from app.core.logger import logger

router = APIRouter()


@router.get("/states")
async def get_states(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):

    logger.info("States API Hit")

    return await LocationRepo.get_states(db)


@router.get("/districts")
async def get_districts(
    state_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):

    logger.info(f"District API Hit state_id={state_id}")

    return await LocationRepo.get_districts(db, state_id)


@router.get("/constituencies")
async def get_constituencies(
    district_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):

    logger.info(f"Constituencies API Hit district_id={district_id}")

    return await LocationRepo.get_constituencies(db, district_id)


@router.get("/mandals")
async def get_mandals(
    constituency_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):

    logger.info(f"Mandals API Hit constituency_id={constituency_id}")

    return await LocationRepo.get_mandals(db, constituency_id)


@router.get("/panchayats")
async def get_panchayats(
    mandal_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):

    logger.info(f"Panchayats API Hit mandal_id={mandal_id}")

    return await LocationRepo.get_panchayats(db, mandal_id)


@router.get("/wards")
async def get_wards(
    panchayat_id: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(verify_token)
):

    logger.info(f"Wards API Hit panchayat_id={panchayat_id}")

    return await LocationRepo.get_wards(db, panchayat_id)