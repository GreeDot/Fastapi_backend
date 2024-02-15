from typing import List

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Gree as GreeModel
from app.schemas.gree import GreeUpdate, Gree

async def crud_update_gree(db: AsyncSession, gree_id: int, gree_update: GreeUpdate) -> GreeModel:
    async with db as session:
        query = select(GreeModel).filter(GreeModel.id == gree_id)
        result = await session.execute(query)
        gree = result.scalar()
        if gree:
            update_data = gree_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(gree, key, value)
            await session.commit()
            return gree
        return None


async def crud_get_grees(db: AsyncSession, user_id: int) -> List[GreeModel]:
    async with db as session:
        query = select(GreeModel).filter(GreeModel.member_id == user_id, GreeModel.status == "activate")
        result = await session.execute(query)
        grees = result.scalars().all()
        return grees


async def crud_get_gree_by_id(db: AsyncSession, gree_id: int, user_id: int) -> GreeModel:
    async with db as session:
        query = select(GreeModel).filter(GreeModel.id == gree_id, GreeModel.member_id == user_id, GreeModel.status == "activate")
        result = await session.execute(query)
        gree = result.scalar()
        return gree


async def crud_update_gree_status(db: AsyncSession, gree_id: int, user_id: int, new_status: str) -> None:
    async with db as session:
        query = select(GreeModel).filter(GreeModel.id == gree_id, GreeModel.member_id == user_id)
        result = await session.execute(query)
        gree = result.scalar()
        gree.status = new_status
        await session.commit()
