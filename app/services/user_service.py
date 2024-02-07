# services/user_service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.config import settings
from core.security import Token, authenticate_user, create_access_token, hash_password
from models.models import Member, RoleEnum, StatusEnum, GradeEnum
from datetime import datetime, timedelta


async def create_user(user_data, db_session: AsyncSession):
    hashed_pwd = hash_password(user_data.password)
    new_member = Member(
        username=user_data.username,
        nickname=user_data.nickname,
        password=hashed_pwd,
        role=RoleEnum.MEMBER,
        status=StatusEnum.ACTIVATE,
        grade=GradeEnum.FREE,
        register_at=datetime.now()
    )
    db_session.add(new_member)
    await db_session.commit()
    await db_session.refresh(new_member)
    return new_member

async def user_exists(username: str, db_session: AsyncSession) -> bool:
    async with db_session as session:
        result = await session.execute(select(Member).where(Member.username == username))
        member = result.scalars().first()
        return member is not None