from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import hash_password
from app.models.models import Member
from app.schemas.user import UserUpdate


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Member).filter(Member.id == user_id))
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Member).offset(skip).limit(limit))
    return result.scalars().all()


async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    db_user = await get_user(db, user_id)
    if db_user:
        user_data = user_update.dict(exclude_unset=True)

        # 비밀번호가 제공되었다면 해싱 처리
        if 'password' in user_data:
            hashed_password = hash_password(user_data['password'])
            db_user.password = hashed_password
            del user_data['password']

        for key, value in user_data.items():
            setattr(db_user, key, value)

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user(db, user_id)
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user
