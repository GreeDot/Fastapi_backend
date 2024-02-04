from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from typing import Optional
from models.models import Member, RoleEnum, StatusEnum, GradeEnum
from core.security import hash_password, verify_password, create_access_token
from database import get_db
from pydantic import BaseModel

router = APIRouter()


# Pydantic 모델 정의
class RegisterRequest(BaseModel):
    email: str
    nickname: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

# 이메일 중복 확인
async def user_exists(email: str, db_session: AsyncSession) -> bool:
    async with db_session as session:
        result = await session.execute(select(Member).where(Member.email == email))
        member = result.scalars().first()
        return member is not None


## 이메일이 일치한지 확인
async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[Member]:
    async with db as session:
        result = await session.execute(select(Member).where(Member.email == email))
        user = result.scalars().first()
        if user and verify_password(password, user.password):
            return user
    return None


@router.post('/register')
async def register_member(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await user_exists(request.email, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 사용자입니다.")
    if not request.email or not request.nickname or not request.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="모든 필드를 입력해주세요.")

    hashed_pwd = hash_password(request.password)

    new_member = Member(
        email=request.email,
        nickname=request.nickname,
        password=hashed_pwd,
        role=RoleEnum.MEMBER,
        status=StatusEnum.ACTIVATE,
        grade=GradeEnum.FREE,
        register_at=datetime.now()
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    # 회원가입 후에 로그인 처리
    user = new_member
    return {"message": "회원가입이 성공적으로 완료되었습니다.", "user_id": user.id}


##일치하면 토큰 반환, 불일치하면 에러 메세지 반환
@router.post('/login', response_model=Token)
async def login_for_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
