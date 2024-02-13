# services/user_service.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import hash_password
from app.models.models import Member, RoleEnum, StatusEnum, GradeEnum
from datetime import datetime


async def create_user(user_data, db_session: AsyncSession):
    # username, nickname, password의 빈 값 검사
    if not user_data.username or not user_data.nickname or not user_data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username, nickname, and password cannot be empty.")
    
    if user_data.username == '' or user_data.nickname == '' or user_data.password == '':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username, nickname, and password cannot be empty.")

    # 같은 username으로 이미 존재하는 유저가 있는지 확인
    if await user_exists(user_data.username, db_session):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username is already in use.")

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
    result = await db_session.execute(select(Member).where(Member.username == username))
    member = result.scalars().first()
    return member is not None
