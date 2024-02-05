from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models import models
from schemas.user import UserUpdate


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Member).filter(models.Member.id == user_id))
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Member).offset(skip).limit(limit))
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user: UserUpdate):
    db_user = await get_user(db, user_id)
    if db_user:
        user_data = user.dict(exclude_unset=True)
        for key, value in user_data.items():
            setattr(db_user, key, value)
        await db.commit()
        await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user
